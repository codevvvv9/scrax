from scrax import SpiderBase
from scrax.http import Request

class BaiduSpider(SpiderBase):
    # start_url = 'https://www.baidu.com'
    # 会有多个 URL 的
    start_urls = ['https://www.baidu.com', 'https://www.qq.com']

    def start_requests(self):
        # 业务类不需要做具体的事情，只暴露下载的 URL 即可
        return [Request(url=url) for url in self.start_urls]
        # return self.start_urls # 这样写爬虫基类的元类的装饰器就会检查到错误了，不用再手写装饰器了
