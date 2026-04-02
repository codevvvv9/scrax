# 具体的爬虫业务系统的启动入口
import asyncio
import time

from baidu import BaiduSpider
from scrax.core.engine import Engine

async def run():
    baidu_spider = BaiduSpider()
    engine = Engine()
    await engine.start_spider(baidu_spider)

if __name__ == '__main__':
    start_time = time.perf_counter()
    asyncio.run(run())
    end_time = time.perf_counter()
    print(f'爬虫运行时间: {end_time - start_time} 秒')
