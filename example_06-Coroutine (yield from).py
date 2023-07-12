"""
# 協程 (yield from 版本)
"""



"""
## `yield from`語法介紹

### `yield from`的入門例子
...
"""

# %%
"""
### `yield from`語法的具體實現
"""
## yield from 的用法很簡單
RESULT = yield from EXPR

# %%
## 以下程式碼是 RESULT = yield from EXPR
## 的等價寫法
## 來自: https://peps.python.org/pep-0380

_i = iter(EXPR)
try:
    _y = next(_i)
except StopIteration as _e:
    _r = _e.value
else:
    while 1:
        try:
            _s = yield _y
        except GeneratorExit as _e:
            try:
                _m = _i.close
            except AttributeError:
                ...
            else:
                _m()
            raise _e
        except BaseException as _e:
            _x = sys.exc_info()
            try:
                _m = _i.throw
            except AttributeError:
                raise _e
            else:
                try:
                    _y = _m(*_x)
                except StopIteration as _e:
                    _r = _e.value
                    break
        else:
            try:
                if _s is None:
                    _y = next(_i)
                else:
                    _y = _i.send(_s)
            except StopIteration as _e:
                _r = _e.value
                break
RESULT = _r

# %%
## 部分簡化後的結果

_i = iter(EXPR) # __iter__ -> __await__
try:
    _y = _i.send(None)  # prime
except StopIteration as _e:     # 直接就結束了, 一次 yield 都沒遇上
    _r = _e.value
else:
    while 1:    # 不遇到 StopIteration 不算完
        try:
            _s = yield _y   # 照原樣 yield 出去, 並接受 send 傳入的值
        except GeneratorExit as _e:     # 處理 close
            _i.close()
            raise _e
        except BaseException as _e:     # 處理其他異常
            _x = sys.exc_info()
            try:
                _y = _i.throw(*_x)
            except StopIteration as _e:
                _r = _e.value
                break
        else:
            try:
                _y = _i.send(_s)    # 接收到的值原樣再 sned 下去
            except StopIteration as _e:
                _r = _e.value
                break
RESULT = _r     # StopIteration 帶出來的值就是結果

# %%
## 已知總是會 send(None). 繼續簡化後的結果

_i = iter(EXPR)     # __iter__

while 1:    # 不遇到 StopIteration 不算完
    try:
        _y = _i.send(None)      # 總是 None, 也就無所謂 prime
    except StopIteration as _e:
        _r = _e.value
        break
    else:
        try:
            yield _y    # 照原樣 yield 出去, 不再接收 sned 傳入的值, 因為總是 None
        except GeneratorExit as _e:     # 處理 close
            _i.close()
            raise _e
        except BaseException as _e:     # 處理其他異常
            _x = sys.exc_info()
            try:
                _y = _i.throw(*_x)
            except StopIteration as _e:
                _r = _e.value
                break
RESULT = _r     # StopIteration 帶出來的值就是結果

# %%
## 已知總是會 send(None)
## 再去掉異常處理部分程式碼

_i = iter(EXPR)     # __iter__

while 1:    # 不遇到 StopIteraton 不算完
    try:
        _y = _i.send(None)  # 總是 None, 也就無所謂 prime
    except StopIteration as _e:
        _r = _e.value
        break
    else:
        yield _y    # 照原樣 yield 出去, 不再接收 sned 傳入的值, 因為總是 None
RESULT = _r     # StopIteration 帶出來的值就是結果

# %%
"""
## 定義一個任務

### 一個同步模式的簡單任務
"""

def one_task():
    """ 一個任務 """
    print(f'begin task')
    ... # 其他步驟
    print(f'  begin big_step:')

    big_result = big_step() # <---

    print(f'  end big_step with {big_result}')
    ... # 其他步驟

    print(f'end task')

def big_step():
    ... # 其他小步驟
    print(f'    begin small_step:')

    small_result = small_step() # <---

    print(f'    end small_step with {small_result}')
    ... # 其他小步驟
    return small_result * 1000

def small_step():
    print('      努力工作中...')
    return 123  # 完成了

# 執行任務
one_task()

# %%
""" 遇到阻塞 """
from time import sleep

def small_step():
    print('      休息一下, 馬上回來')
    sleep(2)
    print('      努力工作中...')
    return 123  # 完成了

one_task()

# %%
""" 聽說用 `yield` 變協程可以不阻塞 """
from time import sleep

def small_step():
    print('      休息一下, 馬上回來')
    yield sleep(2)
    print('      努力工作中...')
    return 123  # 完成了

one_task()

# %%
""" `yield` 有「傳染性」  """

def big_step():
    ... # 其他小步驟
    print(f'    sbegin small_step:')

    # small_result = small_step()
    small_coro = small_step()
    while True:
        try:
            x = small_coro.send(None)
        except StopIteration as e:
            small_result = e.value
            break
        else:
            ...

    print(f'    end small_step with {small_result}')
    ... # 其他小步驟
    return small_result * 1000

one_task()

# %%
""" 將阻塞從下游傳到上游 """
import time
from time import sleep

def small_step():
    print('      休息一下, 馬上回來')
    t1 = time.time()
    yield sleep, 2
    assert((time.time() - t1) > 2, '睡眠時間不足!')
    print('      努力工作中...')
    return 123  # 完成了

one_task()

# %%
""" 繼續拋給上游 """
def big_step():
    ... # 其他小步驟
    print(f'    sbegin small_step:')

    # small_result = small_step()
    small_coro = small_step()
    while True:
        try:
            x = small_coro.send(None)
        except StopIteration as e:
            small_result = e.value
            break
        else:
            yield x

    print(f'    end small_step with {small_result}')
    ... # 其他小步驟
    return small_result * 1000

one_task()

# %%
""" 上游處理爛攤子 """
def one_task():
    """ 一個任務 """
    print(f'begin task')
    ... # 其他步驟
    print(f'  begin big_step:')

    # big_result = big_step()
    big_coro = big_step()
    while True:
        try:
            x = big_coro.send(None)
        except StopIteration as e:
            big_result = e.value
            break
        else:
            func, arg = x
            func(arg)

    print(f'  end big_step with {big_result}')
    ... # 其他步驟

    print(f'end task')

one_task()

# %%
"""
階段總結 1  

+ 協程自己並不能消除阻塞
+ 協程具有傳染性
+ 協程通過 yield 把換個方式傳遞給了上游
+ 最終阻塞仍然需要被解決


1. one_task (normal func) -> big_step (normal func) -> small_step (normal func)
2. one_task (normal func) -> big_step (normal func) <-> small_step (ACTIVE - blocked / coroutine)
3. one_task (normal func) -> big_step (PASITIVE - generator) <-> small_step (ACTIVE - blocked / coroutine)
"""

# %%
"""
## `yield from` 來幫忙
"""

def big_step():
    ... # 其他小步驟
    print(f'    sbegin small_step:')

    # small_result = small_step()

    small_result = yield from small_step()

    # small_coro = small_step()
    # while True:
    #     try:
    #         x = small_coro.send(None)
    #     except StopIteration as e:
    #         small_result = e.value
    #         break
    #     else:
    #         yield x

    print(f'    end small_step with {small_result}')
    ... # 其他小步驟
    return small_result * 1000

one_task()
# %%
"""
## 階段總結 2

為了方便討論:

我們將<最末端的遇到阻塞而不得不主動`yield`的協程>稱之為「主動協程」
<中間接收到下游的傳導而不得不跟隨著`yield`的協程>稱之為「被動協程」

+ 「主動協程」是最先出棧的位置
+ 「被動協程」可能有很多層
+ `yield from` 大大簡化了「被動協程」的程式碼
"""

# %%
"""
## `yield from` 一統江湖
"""

import time
from time import sleep

def small_step():
    print('      休息一下, 馬上回來')
    t1 = time.time()

    # yield sleep, 2
    yield from YieldFromable((sleep, 2))

    assert(time.time() - t1, '睡眠時間不足')
    print('      努力工作中...')
    return 123  # 完成了

class YieldFromable: 
    def __init__(self, obj):
        self.value = obj
    def __iter__(self):
        yield self.value

one_task( )
# %%
"""
## 階段總結 3

> 通過一個`YieldFromable`物件, 將最末端的`yield`進行封裝, 把協程得調用方式統一成了`yield from`.
"""

# %%
"""
## 將任務徹底協程化
"""
def one_task():
    """ 一個任務 """
    print(f'begin task')
    ... # 其他步驟
    print(f'  begin big_step:')

    # big_result = big_step() 

    big_result = yield from big_step()      

    # big_coro = big_step()
    # while True:
    #     try:
    #         x = big_coro.send(None)
    #     except StopIteration as e:
    #         big_result = e.value
    #         break
    #     else:
    #         func, arg = x
    #         func(arg)

    print(f'  end big_step with {big_result}')
    ... # 其他步驟

    print(f'end task')

# 現在該如何來驅動這個任務呢?
one_task()

# %%
"""
# 一個通用的任務驅動器
"""

class YieldFromable: 
    def __init__(self, obj):
        self.value = obj
    def __iter__(self):
        yield self

class Task:
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
                assert(isinstance(x, YieldFromable), "It is not `YieldFromable` class.")
                print(type(x), x)
                func, arg = x.value
                func(arg)
        print('----------')

t = Task(one_task())
t.run()


# %%
"""
## 完成了整個任務的協程化改造
"""

from time import sleep

class YieldFromable: 
    def __init__(self, obj):
        self.value = obj
    def __iter__(self):
        yield self

class Task:
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

def one_task():
    """ 一個任務 """
    print(f'begin task')
    ... # 其他步驟
    print(f'  begin big_step:')

    big_result = yield from big_step()      

    print(f'  end big_step with {big_result}')
    ... # 其他步驟

    print(f'end task')

def big_step():
    ... # 其他小步驟
    print(f'    sbegin small_step:')

    small_result = yield from small_step()

    print(f'    end small_step with {small_result}')
    ... # 其他小步驟
    return small_result * 1000

def small_step():
    print('      休息一下, 馬上回來')

    yield from YieldFromable((sleep, 2))

    print('      努力工作中...')
    return 123  # 完成了

# %%
t = Task(one_task())
t.run()

# %%
"""
## 階段總結 4

通過在首尾兩端分別添加一個通用的組件, 完成了整個任務的協程化更新.
可以看到在`yield from`的幫助下, 被動協程的部分程式碼幾乎不用改變.
只有在最末端要主動`yield`的地方變化比較大.
"""