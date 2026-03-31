# from typing import Optional, Generator # 旧版本的引入 typing
from collections.abc import Iterable
from scrax.http import Request
from abc import ABC
from scrax.core.decorators import check_request_return

# 抽象基类，不可以被实例化
class SpiderBase(ABC):
    """
    爬虫基类
    爬虫业务系统都继承它
    """
    def __init__(self):
        # 初始化时先判断属性
        if not hasattr(self, 'start_urls'):
            self.start_urls = []

    @check_request_return
    def start_requests(self) -> Iterable[Request]:
        """
        请求方法，所有爬虫应用类的兜底请求方法
        :return: 一个生成器
        """
        if self.start_urls:
            for url in self.start_urls:
                yield Request(url=url)
        else:
            if hasattr(self, 'start_url') and isinstance(getattr(self, 'start_url'), str):
                yield Request(url=getattr(self, 'start_url'))