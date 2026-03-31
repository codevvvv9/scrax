from typing import (
    Dict,
    Optional,
)
from dataclasses import dataclass
from collections.abc import Callable

@dataclass
class Request:
    headers: Optional[Dict[str, str]] = None
    url: str = None
    priority: int = 0 # 0 最低优先级，然后从 1 开始越小优先级越高
    cookies: Optional[Dict[str, str]] = None
    method: str = 'GET'
    callback: Callable = None

# 加注解的打印是优化版：Request(headers=None, url='https://www.baidu.com', priority=0, cookies=None, method='GET', callback=None)
# class Request:
#     def __init__(self, headers=None, url=None, priority=0, cookies=None, method='GET', callback=None):
#         self.headers = headers
#         self.url = url
#         self.priority = priority
#         self.cookies = cookies
#         self.method = method
#         self.callback = callback
# 传统写法的打印Request 实例：<scrax.http.request.Request object at 0x103b7de70>