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

    async def parse(self, response):
        """ 爬虫系统的 callback """
        # 拿到响应后，可能又发起了新的请求
        print(f'parse {response}')
        for i in range(10):
            url = 'https://www.baidu.com'
            request = Request(url=url, callback=self.parse_page)
            yield request# 一个带回调的新请求

        # 这个 callback 可能返回 coroutine对象、 异步生成器、生成器

        # return '协程的返回值' # 未处理有返回值的协程对象

    async def parse_page(self, response):
        print(f'parse page {response}')
        for i in range(10):
            url = 'https://www.baidu.com'
            request = Request(url=url, callback=self.parse_detail)
            yield request  # 一个带回调的新请求

    def parse_detail(self, response):
        print(f'parse detail {response}')