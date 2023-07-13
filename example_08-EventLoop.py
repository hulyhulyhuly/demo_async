import time
from time import sleep
import random

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

class Awaitable:
    def __init__(self, obj):
        self.value = obj

    def __await__(self):
        yield self

task_id_counter = itertools.count(1)

class Task():
    def __init__(self, coro):
        self.coro = coro
        self._done = False
        self._result = None
        self._id = f'Task-{next(task_id_counter)}'

    def run(self):
        print(f'-----{self._id}-----')
        if not self._done:
            try:
                x = self.coro.send(None)
            except StopIteration as e:
                self._result = e.value
                self._done = True
            else:
                loop.call_later(x.value, self.run)
        else:
            print('task is done.')
        print(f'-----{self._id}-----')

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

async def small_step():
    t1 = time.time()
    sleep_time = random.random()
    await Awaitable(sleep_time)
    # assert(time.time() - t1 > sleep_time, '睡眠時間不足!')    
    return sleep_time  # 完成了

if __name__ == '__main__':
    loop = EventLoop()
    for i in range(10):
        t = Task(one_task())
        loop.call_soon(t.run)
    loop.call_later(1, loop.stop)
    loop.run_forever()