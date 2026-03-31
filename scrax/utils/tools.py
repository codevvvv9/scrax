from collections.abc import AsyncIterable
from inspect import isgenerator, isasyncgen
from typing import Any

from scrax.exceptions import TransformTypeError


async def transform(func_result) -> AsyncIterable[Any]:
    """
    转换回调函数结果为异步生成器
    :param func_result: 回调函数返回的任意类型结果
    :return: AsyncGenerator[Request, None]: 异步生成器，产出 Request 对象
    """
    if isgenerator(func_result):
        for r in func_result:
            yield r  # 异步生成器
    elif isasyncgen(func_result):
        async for r in func_result:
            yield r  # 异步生成器
    else:
        raise TransformTypeError('callback return values must be generator or async generator')