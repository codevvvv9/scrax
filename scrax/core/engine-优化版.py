import asyncio

from scrax import Request
from scrax.core.downloader import Downloader
from typing import Optional, Generator, Iterable, Any
from collections.abc import Callable, AsyncIterable
from inspect import iscoroutine
from scrax.core.scheduler import Scheduler
from scrax.exceptions import OutputError
from scrax.spider.spider_base import SpiderBase
from scrax.task_manager import TaskManager
from scrax.utils.tools import transform


class Engine:
    def __init__(self):
        # 通过类型注解 各种变量类型声明，延迟初始化
        self.downloader: Optional[Downloader] = None
        # 2. 初始化请求地址
        self.start_requests: Optional[Iterable[Generator]] = None
        self.start_requests_exhausted = False # 代表初始化请求耗尽了
        # 3. 初始化调度器
        self.scheduler: Optional[Scheduler] = None
        # 4. 声明爬虫
        self.spider: Optional[SpiderBase] = None
        # 5. 设置退出循环的标志
        self.is_running = False
        # 6. 初始化任务管理器
        self.task_manager: Optional[TaskManager] = None

    async def start_spider(self, spider: SpiderBase):
        """
        爬虫启动
        :param spider: 爬虫系统实例
        :return:
        """
        # 真正的初始化
        self.is_running = True
        self.task_manager = TaskManager(total_concurrency=10)
        self.spider = spider
        self.scheduler = Scheduler()
        if hasattr(self.scheduler, 'open'):
            self.scheduler.open() # 打开调度器

        self.downloader = Downloader()
        # 1. 获取请求地址
        # 处理成迭代器，防止有的子类重写了start_requests，返回值不是生成器了
        self.start_requests = iter(spider.start_requests())
        self.start_requests_exhausted = False
        # 2. 去执行爬虫
        await self._open_spider()

    async def _open_spider(self):
        # 创建一个异步任务，不影响代码执行
        crawling = asyncio.create_task(self.crawl())
        # print('1111') # 这里可以写其他实现
        await crawling

    async def crawl(self):
        """
        爬取的主逻辑
        :return:
        """
        while self.is_running:
            request = await self._get_next_request()
            if request is not None:
                # 优先消费队列里的请求，避免 start_requests 持续压入导致队列压力过大。
                await self._crawl(request)
                continue

            start_request = self._next_start_request()
            if start_request is not None:
                await self.enqueue_request(start_request)
                continue

            if await self.should_exit():
                self.is_running = False

    def _next_start_request(self):
        if self.start_requests_exhausted or self.start_requests is None:
            return None

        try:
            return next(self.start_requests)
        except StopIteration:
            self.start_requests = None
            self.start_requests_exhausted = True
            return None


    async def enqueue_request(self, request):
        await self._schedule_request(request)

    async def _schedule_request(self, request):
        # todo 去重
        """
        单独拆分一个方法，是因为这里会有去重逻辑，进行解耦
        :param request:
        :return:
        """
        await self.scheduler.enqueue_request(request)

    async def _get_next_request(self):
        """
        出队
        :return:
        """
        return await self.scheduler.next_request()

    async def _crawl(self, request: Request):
        # 实现真正的并发，包装成一个任务，并用信号量控制
        async def crawl_task():
            outputs = await self._fetch(request)
            # 处理 outputs
            # 异步迭代
            if outputs:
                await self._handle_spider_output(outputs)
        # asyncio.create_task(crawl_task()) # 这里不能用 await，否则就不是并发了，又是阻塞了
        # 没添加一次任务，信号获取一次
        await self.task_manager.semaphore.acquire()
        self.task_manager.create_task(crawl_task())

    async def _handle_spider_output(self, outputs: AsyncIterable):
        async for spider_out in outputs:
            # 判断类型
            if isinstance(spider_out, Request):
                # 如果继续拿到 Request，继续入队
                # print(spider_out)
                await self.enqueue_request(spider_out)
            # todo 处理数据data 为 Item 的情况，假设data类型是 Item
            else:
                raise OutputError(f'{type(spider_out)} must return `Request` or `Item`')

    async def _fetch(self, request: Request) -> AsyncIterable[Any]:
        # 1. 拿到响应
        # 只有成功的 fetch才有响应
        async def _success(_response):
            _callback: Callable = request.callback or self.spider.parse
            if _callback:
                # 2. 响应交给回调函数, 回调函数内部交给了爬虫业务系统
                _outputs = _callback(_response)
                # !!! 判断这里的响应类型是啥
                # 判断outputs类别，需要异步迭代，不能简单的 await
                # await self._transform(outputs) # Error Use
                # 或者直接返回
                if _outputs:
                    if iscoroutine(_outputs):
                        await _outputs
                    else:
                        # 进行转换
                        return transform(_outputs)
                return None
            else:
                raise RuntimeError(f'no callback！！！')

        _response = await self.downloader.fetch(request)
        # 2. 返回爬虫业务返回的输出
        outputs = await _success(_response)
        return outputs

    async def should_exit(self):
        return (
            self.start_requests_exhausted
            and self.scheduler.is_idle()
            and self.downloader.is_idle()
            and self.task_manager.all_done()
        )
