from typing import Optional, Generator


class SpiderBase:
    """
    爬虫基类
    爬虫业务系统都继承它
    """
    def __init__(self):
        # 初始化时先判断属性
        if not hasattr(self, 'start_urls'):
            self.start_urls = []

    def start_requests(self) -> Generator:
        """
        请求方法，所有爬虫应用类的兜底请求方法
        :return: 一个生成器
        """
        if self.start_urls:
            for url in self.start_urls:
                yield url
        else:
            if hasattr(self, 'start_url') and isinstance(getattr(self, 'start_url'), str):
                yield getattr(self, 'start_url')