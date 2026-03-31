from scrax import SpiderBase
from scrax.core.decorators import check_request_return
from scrax.http import Request

class BaiduSpider(SpiderBase):
    # start_url = 'https://www.baidu.com'
    # 会有多个 URL 的
    start_urls = ['https://www.baidu.com', 'https://www.qq.com']

    @check_request_return
    def start_requests(self):
        # 业务类不需要做具体的事情，只暴露下载的 URL 即可
        return [Request(url=url) for url in self.start_urls]

