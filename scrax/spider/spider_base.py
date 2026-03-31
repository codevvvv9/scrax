# from typing import Optional, Generator # 旧版本的引入 typing
from collections.abc import Iterable
from scrax.http import Request
from abc import ABCMeta, abstractmethod, ABC
from scrax.core.decorators import check_request_return

# ======================
# 🔥 框架核心：自动绑定装饰器的元类
# ======================
# 🔥 关键：自定义元类 继承 ABCMeta
# 同时拥有：抽象类能力 + 自动装饰器能力
# ======================
# ======================
class SpiderMeta(ABCMeta):
    """爬虫元类：自动为所有子类的 start_requests 方法添加校验装饰器"""
    def __new__(cls, name, bases, attrs):
        # 自动给 start_requests 方法套上装饰器
        if 'start_requests' in attrs:
            attrs['start_requests'] = check_request_return(attrs['start_requests'])
        return super().__new__(cls, name, bases, attrs)

# 抽象基类，不可以被实例化
# ======================
# 🔥 基类继承元类 → 全子类自动生效
# 这样写所有子类的重写方法会检查到错误了，不用再手写装饰器了
# 基类：既是 抽象基类，又有元类约束
# ======================
# noinspection PyAbstractClass
class SpiderBase(metaclass=SpiderMeta):
    """
    爬虫基类
    爬虫业务系统都继承它
    """
    def __init__(self):
        # 初始化时先判断属性
        if not hasattr(self, 'start_urls'):
            self.start_urls = []

    @abstractmethod
    def parse(self, response):
        pass

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