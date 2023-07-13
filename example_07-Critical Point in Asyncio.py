# %%
from time import sleep

class Awaitable:
    def __init__(self, obj):
        self.value = obj

    def __await__(self):
        yield self

class Task():
    def __init__(self, coro):
        self.coro = coro

    def run(self):
        print('----------')
        while True:
            try:
                x = self.coro.send(None)
            except StopIteration as e:
                result = e.value
                break
            else:
                func, arg = x.value
                func(arg)
        print('----------')

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
    print('      休息一下, 馬上回來')

    await Awaitable((sleep, 2))
    
    print('      努力工作中...')
    
    return 123  # 完成了

t = Task(one_task())
t.run()

# %%
"""
`yield from` (也就是`await`)
它的作用相當於是一個鏈條或者說一個管道
它把這些協程串起來, 它自己是沒有(主動)出棧的能力.

也就是說 await 自己是沒有 yield
或者說 是沒有主動性 yield 這樣的一個功能
"""

class Task():
    def __init__(self, coro):
        self.coro = coro
        self._done = False
        self._result = None

    def run(self):
        print('----------')
        if not self._done:
            try:
                x = self.coro.send(None)
            except StopIteration as e:
                self._result = e.value
                self._done = True
            else:
                func, arg = x.value
                func(arg)
        else:
            print('task is done.')
        print('----------')

if __name__ == '__main__':
    t = Task(one_task())
    t.run()

    # 等待 2 秒
    for _ in range(10):
        print('doing something ...')
        sleep(0.2)

    t.run()