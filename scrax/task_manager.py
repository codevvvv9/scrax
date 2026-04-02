import asyncio
from typing import Set, Final
from asyncio import Task, Semaphore

class TaskManager:
    def __init__(self, total_concurrency: int = 10):
        self.current_tasks: Final[Set] = set()
        self.semaphore: Semaphore = Semaphore(total_concurrency)

    def create_task(self, coroutine):
        task = asyncio.create_task(coroutine)
        self.current_tasks.add(task)

        # 什么时候移除呢？任务完成了，通过设置回调，删除
        def done_callback(_task: Task):
            self.current_tasks.remove(task)
            self.semaphore.release() # 任务完成同时也要释放信号，同步方法

        task.add_done_callback(done_callback)

    def all_done(self):
        return len(self.current_tasks) == 0