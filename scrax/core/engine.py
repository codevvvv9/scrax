from scrax.core.downloader import Downloader
from typing import Optional, Generator

from scrax.core.scheduler import Scheduler
from scrax.spider.spider_base import SpiderBase


class Engine:
    def __init__(self):
        # 通过类型注解 各种变量类型声明，延迟初始化
        self.downloader: Optional[Downloader] = None
        # 2. 初始化请求地址
        self.request_urls: Optional[Generator] = None
        # 3. 初始化调度器
        self.scheduler: Optional[Scheduler] = None

    async def start_spider(self, spider: SpiderBase):
        """
        爬虫启动
        :param spider: 爬虫系统实例
        :return:
        """
        # 真正的初始化
        self.scheduler = Scheduler()
        if hasattr(self.scheduler, 'open'):
            self.scheduler.open() # 打开调度器

        self.downloader = Downloader()
        # 1. 获取请求地址
        # 处理成迭代器，防止有的子类重写了start_requests，返回值不是生成器了
        self.request_urls = iter(spider.start_requests())
        # 2. 去执行爬虫
        await self.crawl()

    async def crawl(self):
        """
        爬取的主逻辑
        :return:
        """
        while True:
            # 出队操作，何时出队很关键
            if (request := await self._get_next_request()) is not None:
                # 如果能拿到请求就去下载请求，拿不到就去入队
                await self._crawl(request)
            else:
                try:
                    # 挨个去请求地址,
                    if self.request_urls:
                        request_url = next(self.request_urls)
                    else:
                        break
                    # print(f'请求地址是{request_url}')
                    # Bad: 直接处理请求
                    # self.downloader.download(url=request_url)
                    # Good: 通过调度器来处理请求，前去入队
                except StopIteration:
                    # # 取完地址了
                    # print('所有请求处理完了')
                    # Bad：遍历完报错，就 break 不是显示退出
                    # break
                    # Good：显式退出，再次引发next(None)报错，下一个 except 处理 break
                    self.request_urls = None
                # except Exception: # 可以不写，在上面的 if else中处理
                #     break
                else:
                    # 入队操作
                    # 如果到这里没有异常，就说明这个获取的请求该入队了
                    await self.enqueue_request(request_url)


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

    async def _crawl(self, request):
        await self.downloader.download(request)