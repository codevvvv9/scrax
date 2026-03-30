import asyncio
import time

import requests

class Downloader:
    def __init__(self):
        pass # 暂时不知道初始化什么

    async def download(self, url):

        """
        下载器的核心功能：下载请求
        :param url: 请求地址
        :return:
        """
        # 下载器的核心功能：下载请求
        # response = requests.get(url)
        # print(response)
        # 假数据模拟
        await asyncio.sleep(1)
        print('result 了')