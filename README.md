scrax是一个通用的爬虫框架，简化版的 scrapy，API 设计类似，可以无缝衔接使用，具备以下特点
1. 分层设计，清晰的职责划分 
2. 支持多线程，提高爬取效率
3. 提供丰富的解析规则，支持正则表达式和XPath 
4. 简单易用，上手快

## 基础架构
start_url -->  requests --> response --> parse --> data

对应到架构上就是有个应用层的爬虫系统 --> scrax引擎 --> 下载器处理响应

core 层是核心，分为：

1. scrax 引擎，只是串联爬虫系统和其他系统的中转中心，内部做各种转发
2. downloader 下载器处理响应处理
3. scheduler 调度器，使用队列处理响应


spider 基类，处理爬虫系统的通用操作

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


