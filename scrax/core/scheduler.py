from typing import Optional
from scrax.utils.pqueue import SpiderPriorityQueue

class Scheduler:
    """
    调度器，调度请求
    请求不是来一条就处理一条，是先入队，交给调度器统一处理
    """

    def __init__(self):
        self.spider_queue: Optional[SpiderPriorityQueue] = None

    def open(self):
        """
        打开调度器
        :return:
        """
        self.spider_queue = SpiderPriorityQueue()


    async def next_request(self):
        """
        调度下一个请求
        :return: 下一个请求
        """
        # Bad: 如果娶不到值就卡住了
        # request = self.spider_queue.get() # 异步阻塞方法，必须使用 await
        # return request
        # request = await self.spider_queue.get() # 但是这样加上，就是一直等待有数据，卡死了就
        # return request

        # Good: 防止卡住，正确使用协程的超时方法
        # future_item = self.spider_queue.get()
        # try:
        #     request = await asyncio.wait_for(future_item, timeout=0.1)
        # except TimeoutError:
        #     return None
        # return request
        request = await self.spider_queue.get()
        return request

    async def enqueue_request(self, request):
        """
        请求入队
        :return:
        """
        await self.spider_queue.put(request)

