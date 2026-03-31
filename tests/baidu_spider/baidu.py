from scrax import SpiderBase
from scrax.http import Request

class BaiduSpider(SpiderBase):
    # start_url = 'https://www.baidu.com'
    # 会有多个 URL 的
    start_urls = ['https://www.baidu.com', 'https://www.baidu.com']

    # def start_requests(self):
    #     # 业务类不需要做具体的事情，只暴露下载的 URL 即可
    #     return [Request(url=url) for url in self.start_urls]
    #     # return self.start_urls # Error 这样写爬虫基类的元类的装饰器就会检查到错误了，不用再手写装饰器了

    def parse(self, response):
        """ 爬虫系统的 callback """
        # print(f'response is == {response}')
        # 拿到响应后，可能又发起了新的请求
        for i in range(5):
            url = 'https://www.baidu.com'
            yield Request(url=url)

        # 这个 callback 可能返回 coroutine对象、 异步生成器、生成器