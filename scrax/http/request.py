from typing import (
    Dict,
    Optional,
    Callable
)
from dataclasses import dataclass

@dataclass
class Request:
    headers: Optional[Dict[str, str]] = None
    url: str = None
    priority: int = 0 # 0 最低优先级，然后从 1 开始越小优先级越高
    cookies: Optional[Dict[str, str]] = None
    method: str = 'GET'
    callback: Callable = None


