import time
from time import sleep
import random
import threading

import collections
import heapq
import itertools

class EventLoop:
    def __init__(self):
        self._ready = collections.deque()
        self._scheduled = []
        self._stopping = False

    def call_soon(self, callback, *args):        
        self._ready.append((callback, args))

    def call_later(self, delay, callback, *args):
        t = time.time() + delay
        heapq.heappush(self._scheduled, (t, callback, args))

    def stop(self):
        self._stopping = True

    def run_forever(self):
        while True:
            self.run_once()
            if self._stopping:
                break

    def run_once(self):
        now = time.time()
        if self._scheduled:
            if self._scheduled[0][0] < now:
                _, cb, args = heapq.heappop(self._scheduled)
                self._ready.append((cb, args))

        num = len(self._ready)
        for i in range(num):
            cb, args = self._ready.popleft()
            cb(*args)

        # self.stop()

class Future:
    def __init__(self):
        global loop
        self._loop = loop
        self._result = None
        self._done = False
        self._callbacks = []

    def set_result(self, result):
        if self._done:
            raise RuntimeError('future alreadt done.')
        self._result = result
        self._done = True

        for cb in self._callbacks:
            self._loop.call_soon(cb)

    def result(self):
        if self._done:
            return self._result
        else:
            raise RuntimeError('future is not done.')

    def add_done_callback(self, callback):
        self._callbacks.append(callback)

    def __await__(self):
        yield self
        return self.result()

task_id_counter = itertools.count(1)

class Task(Future):
    def __init__(self, coro):
        super().__init__()
        self.coro = coro
        # self._result = None
        # self._done = False
        self._id = f'Task-{next(task_id_counter)}'
        self._loop.call_soon(self.run)
        self._start_time = time.time()

    def run(self):
        print(f'-----{self._id}-----')
        if not self._done:
            try:
                x = self.coro.send(None)
            except StopIteration as e:
                self.set_result(e.value)
                global total_block_time
                total_block_time += time.time() - self._start_time
            else:
                # 我什麼時候能恢復執行?
                x.add_done_callback(self.run)
        else:
            print('task is done.')
        print(f'-----{self._id}-----')

async def small_step():
    global loop
    fut = Future()
    # 指派一個目標來執行 set_result
    fake_io_read(fut)
    result = await fut
    return result

def fake_io_read(future):
    def read():
        sleep(random.random())  # IO 阻塞
        future.set_result(random.randint(1, 100))
    threading.Thread(target=read).start()

async def one_task():
    print('begin task')
    ... # 其他步驟
    print('  begin big step')
    big_result = await big_step()
    print(f'  end big step with {big_result}')
    ... # 其他步驟
    print('end task')

async def big_step():
    ... # 其他小步驟
    print('    begin small step')
    small_result = await small_step()
    print(f'    end small step with {small_result}')
    ... # 其他步驟
    return small_result * 1000

def until_all_done(tasks):
    tasks = [t for t in tasks if not t._done]
    if tasks:
        loop.call_soon(until_all_done, tasks)
    else:
        loop.stop()

if __name__ == '__main__':
    loop = EventLoop()
    total_block_time = 0
    start_time = time.time()
    all_tasks = [Task(one_task()) for i in range(2000)]
    # loop.call_later(1, loop.stop)
    loop.call_later(0.9, until_all_done, all_tasks)
    loop.run_forever()
    print(total_block_time, time.time() - start_time)