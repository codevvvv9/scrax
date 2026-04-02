scrax是一个通用的爬虫框架，简化版的 scrapy，API 设计类似，可以无缝衔接使用，具备以下特点
1. 分层设计，清晰的职责划分 
2. 支持多线程，提高爬取效率
3. 提供丰富的解析规则，支持正则表达式和XPath 
4. 简单易用，上手快

##  1. 基础架构
start_url -->  requests --> response --> parse --> data

对应到架构上就是有个应用层的爬虫系统 --> scrax引擎 --> 下载器处理响应

core 层是核心，分为：

1. scrax 引擎，只是串联爬虫系统和其他系统的中转中心，内部做各种转发
2. downloader 下载器处理响应处理
3. scheduler 调度器，使用队列处理响应


***
注意 WARNING：
1. spider 基类，处理爬虫系统的通用操作，他的返回类型是生成器（不用事先遍历大量数据，生成列表占用内存）
- **按需生成**: 只有在调用 next() 或迭代时才生成下一个值
- **可暂停执行**: 生成器可以在 yield 处暂停，保留当前状态
- **内存友好**: 一次只处理一个元素，不占用大量内存
注意：spider 基类返回生成器类型，具有以下优势：
- **内存高效**: 惰性求值，按需生成 Request 对象，避免一次性创建大量对象
- **延迟计算**: 只有在需要下一个请求时才执行生成逻辑
- **流式处理**: 支持处理大量 URL 而不会内存溢出
- **可暂停执行**: 生成器可在 yield 处暂停，保持执行状态

2. engine 内 crawl设计循环获取，而不是固定长度（因为后续任务可能会继续往队列中添加，队列长度不固定，无法使用队列的长度来控制）
而且并发处理是复杂的，要确保不会遗漏任务
同时有多个任务在运行
- 队列可能暂时为空，但任务正在处理中
- 处理中的任务可能会生成新请求
- 需要等待所有任务完成才能退出

3. 协程函数中为啥不能用普通的 time.sleep
- time.sleep(): 阻塞整个线程，所有协程都会暂停
- await asyncio.sleep(): 让出控制权，事件循环可以运行其他任务
- 性能影响: 使用 time.sleep() 会完全破坏异步程序的性能优势
最佳实践: 在协程中始终使用异步版本的函数，事件循环像是一个单线程的任务调度器，不断地切换协程，给人一种并发的效果
4. crawl的主逻辑，循环开始为啥先消费队列，这是最佳实践，最好是先消费，防止队列任务堆积，影响性能。
更严重的问题是：如果你简单的入队操作这样写：
```python
while True:
    if (request := await self._get_next_request()):
        pass # 你期望有数据就消费，处理逻辑，就会导致 队列get卡死的问题
```
同时因为如果你先消费队列，去 get的话，会导致阻塞住，因为队列的 get 会一直等有数据，如果一直无法入队，就一直卡主，所以 get处理不能直接 await，用异步任务超时控制
```python
# 调度器中队列出队操作
async def _next_request(self): 
    coro = self.spider_queue.get()
        try:
            request = await asyncio.wait_for(coro, timeout=0.1)
        except TimeoutError:
            return None
        return request
```
通过超时控制，显式的抛出 None给 Engine 的就能控制：如果没有请求，就先入队，下次再进循环，就能先消费了
```python
        while self.is_running:
            # 出队操作，何时出队很关键
            if (request := await self._get_next_request()) is not None:
                pass
            else:
                # 入队操作
```
***
### 调度器的细节
问题在于调度器的 方法会**阻塞等待**，导致整个流程卡住：

## 问题分析

### 1. **调度器阻塞**
```python
# Bad: 如果取不到值就卡住了
request = self.spider_queue.get()  # 这里会一直等待，直到队列有数据
return request
```

### 2. **Engine 循环逻辑**
```python
if (request := await self._get_next_request()) is not None:
    # 如果能拿到请求就去下载请求
    await self._crawl(request)  # 一直执行这里
else:
    # 拿不到就去入队  # 这行永远不会执行
```

## 根本原因

- `PriorityQueue.get()` 是**阻塞操作**
- 当队列为空时，它会一直等待直到有数据
- 所以 `request` 永远不会是 `None`
- `else` 分支永远不会执行，无法入队新数据

## 解决方案

恢复带超时的写法：

```python
async def next_request(self):
    """
    调度下一个请求
    :return: 下一个请求
    """
    # 防止卡住，使用超时
    try:
        request = await asyncio.wait_for(self.spider_queue.get(), timeout=0.1)
        return request
    except asyncio.TimeoutError:
        return None
```

## 工作流程

1. **第一次循环**: 队列为空 →  返回 `None` → 执行 `else` 分支 → 入队URL
2. **后续循环**: 队列有数据 →  返回URL → 执行 [_crawl()] → 下载请求

这样就能正常在"出队下载"和"入队新URL"之间切换了。

## 2. 抽象请求类
使用Request来请求，并且增加请求方法的元类装饰器，校验返回参数。、
使用元类装饰器的细节要重点掌握

## 3. 异步核心流程改造

这部分的改造是：为了让爬虫业务系统拿到下载器的结果，因为架构设计上彼此是解耦的
原来engine 核心的start_spider函数中：
```python
# 2. 去执行爬虫
await self.crawl()
# 明显会阻塞后面的代码，所以进一步抽象成协程函数，实现异步操作
```
改成：
```python
async def _open_spider(self):
    # 创建一个异步任务，不影响代码执行
    crawling = asyncio.create_task(self.crawl())
    # print('1111') # 这里可以写其他实现
    await crawling

# 将执行主逻辑的_crawl改造
async def _crawl(self, request: Request):
    # todo 实现真正的并发
    outputs = await self._fetch(request)
    # 处理 outputs
    # 异步迭代
    if outputs:
        async for result in outputs:
            print(result)
```
_fetch 方法主要是：
1. 获取到响应
2. 响应交给 Request 或者 spider业务系统的回调函数, 回调函数内部交给了爬虫业务系统
3. 判断output 类型并返回给真正的 _crawl函数
```python
# _fetch方法的核心逻辑
async def _success(_response):
    _callback: Callable = request.callback or self.spider.parse
    if _callback:
        # 2. 响应交给回调函数, 回调函数内部交给了爬虫业务系统
        _outputs = _callback(_response)
        # !!! 判断这里的响应类型是啥
        if _outputs:
            if iscoroutine(_outputs):
                await _outputs
            else:
                # 进行转换
                return transform(_outputs)
        return None
```
### 3.1 高并发优化
crawl的逻辑目前是不支持高并发的，讲其封装成 Task，使用任务管理器进行统一管理
注意：原来 crawl 的主逻辑是通过异常来结束 while 循环的，这会导致新的请求还没加入到队列中，就被终止掉了
产生bug: 爬虫的回调中的再请求来不及执行！！！

crawl的退出逻辑应该：用显式变量is_running做标志位，控制是否退出循环。
这个标志位重置需要三个条件：
1. 调度器队列为空
2. 下载器集合中没有要下载的任务了
3. 正在执行的任务队列没有未完成的任务了
通过函数判断来重置is_running
 
最后通过 asyncio.Semaphore 控制并发量