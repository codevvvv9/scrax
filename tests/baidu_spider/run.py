# 具体的爬虫业务系统的启动入口
import asyncio

from baidu import BaiduSpider
from scrax.core.engine import Engine

async def run():
    baidu_spider = BaiduSpider()
    engine = Engine()
    await engine.start_spider(baidu_spider)

if __name__ == '__main__':
    asyncio.run(run())