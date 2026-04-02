import asyncio
import random
import time
from scrax.http import Request
import requests

class Downloader:
    def __init__(self):
        # 记录当前正在下载的任务
        self._active_downloads = set()


    async def fetch(self, request: Request):
        """返回响应内容"""
        # 获取时，记录到正在下载
        self._active_downloads.add(request)
        result = await self.download(request)
        # try:
        #     # 获取到结果后，从正在下载中移除
        #     self._active_downloads.remove(request)
        # except KeyError as e:
        #     print(f'KeyError is {e}')

        self._active_downloads.remove(request)
        return result

        # try:
        #     result = await self.download(request)
        #     return result
        # finally:
        #     self._active_downloads.discard(request)  # 没有的时候，不移除，就不会报错

    async def download(self, request: Request):

        """
        下载器的核心功能：下载请求
        :param request: 请求对象
        :return:
        """
        # 下载器的核心功能：下载请求
        # response = requests.get(request.url)
        # print(response)
        # 假数据模拟
        await asyncio.sleep(random.random()) # 随机数 [0.0, 1.0)
        return 'result'

    def is_idle(self) -> bool:
        return len(self) == 0

    def __len__(self):
        return len(self._active_downloads)