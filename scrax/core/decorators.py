# # 这里是自定义的装饰器
from functools import wraps
from collections.abc import Iterable, Generator
from scrax.http import Request


def check_request_return(func):
    """
    爬虫框架强约束装饰器
    1. 强制返回 Iterable 类型（生成器/列表/元组）
    2. 强制所有元素必须是 Request 实例
    3. 生成器惰性检查，不消耗原始数据
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 1. 执行方法，获取返回值
        result = func(*args, **kwargs)

        # 2. 基础校验：必须是可迭代对象
        if not isinstance(result, Iterable):
            raise TypeError(
                f"❌ 方法 {func.__name__} 必须返回 Iterable[Request]\n"
                f"当前返回类型: {type(result)}\n"
                f"支持: 生成器(yield) / list / tuple"
            )

        # 3. 惰性校验包装：保证迭代时每个元素都是 Request
        # 处理生成器（只能迭代一次，必须包装）
        if isinstance(result, Generator):
            def wrapped_generator():
                for item in result:
                    if not isinstance(item, Request):
                        raise TypeError(
                            f"❌ 迭代元素类型错误！\n"
                            f"必须是 Request 对象，当前类型: {type(item)}\n"
                            f"错误值: {item}"
                        )
                    yield item
            return wrapped_generator()

        # 处理普通可迭代对象(list/tuple)，检查第一个元素（高性能）
        try:
            first_item = next(iter(result))
            if not isinstance(first_item, Request):
                raise TypeError(
                    f"❌ 可迭代对象元素必须是 Request 对象\n"
                    f"当前首个元素类型: {type(first_item)}"
                )
        except StopIteration:
            # 空可迭代对象，允许通过
            pass

        return result

    return wrapper