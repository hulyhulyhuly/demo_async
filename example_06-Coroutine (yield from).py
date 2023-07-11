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
    print(f'    begin big_step:')

    big_result = big_step() # <---

    print(f'    end big_step with {big_result}')
    ... # 其他步驟

    print(f'end task')

def big_step():
    ... # 其他小步驟
    print(f'        begin small_step:')

    small_result = small_step() # <---

    print(f'        end small_step with {small_result}')
    ... # 其他小步驟
    return small_result * 1000

def small_step():
    print('           努力工作中...')
    return 123  # 完成了

# 執行任務
one_task()

""" 遇到阻塞 """
# one_task()

# %%
