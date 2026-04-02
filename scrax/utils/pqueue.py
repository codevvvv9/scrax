"""
对优先队列的二次封装
"""
import asyncio
from asyncio import PriorityQueue
from asyncio.exceptions import TimeoutError

class SpiderPriorityQueue(PriorityQueue):
    def __init__(self, maxsize=0):
        super().__init__(maxsize)
    # 重写 get方法 
    async def get(self):
        get_coro = super().get()
        try:
            # 任务超时控制，通过暴露错误让 crawl 函数有时机处理请求
            request = await asyncio.wait_for(get_coro, timeout=0.1)
        except TimeoutError:
            return None
        return request