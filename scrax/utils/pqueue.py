"""
对优先队列的二次封装
"""
import asyncio
from asyncio import TimeoutError, PriorityQueue
from typing import (
    Optional,
    Coroutine,
)

class SpiderPriorityQueue(PriorityQueue):
    def __init__(self, maxsize=0):
        super().__init__(maxsize)

    async def get(self):
        future_item = super().get()
        try:
            request = await asyncio.wait_for(future_item, timeout=0.1)
        except TimeoutError:
            return None
        return request