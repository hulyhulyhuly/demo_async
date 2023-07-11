"""
# `yield`的 3 種用法
即: Generator 的 3  種應用模式
"""

"""
## 概念澄清

基於生成器的協程
> `Generator-based Coroutines`
> Deprecated since version 3.8, will be removed in version 3.11: Use `async def` instead.

按照Python文檔的描述, 所謂的「基於生成器的協程」指的是用`yield from`創建的生成器, 並且還要搭配`asyncio.coroutine`裝飾器來使用
"""

"""
## 這個到底算不算`Coroutine`?
```python
# 例子最初來源: https://mail.python.org/pipermail/python-ideas/2009-April/003841.html
# 《流暢的 Python》中有一個改寫的版本; 這同時借鑒了兩者的寫法

def coro_averager():
    ''' 計算移動平均值 '''
    count = 0
    total = 0
    avg = None
    while True:
        try:
            val = yield avg
        except GeneratorExit:
            return total, count, avg
        else:
            total += val
            count += 1
            avg = total / count
```
"""

"""
## 生成器的 3 種模式
> 來自「仁慈的獨裁者」的權威解釋

Python之父 Guido 在一封郵件裡總結道, 生成器有 3 種模式:
> There's t

he tranditional "pull" style (iterator). "push" style (like the averaging example). and then there are "tasks"
-- Guido van Rossum <討論`yield from`的郵件>

+ pull: 特點在於能不斷向外產出資料, 也就是迭代器
+ push: 特點在於能不斷向內 發送資料, 比如上一章中的計算移動平均值的例子, 是非常早期的協程概念
+ task: 任務式 (是 AsyncIO 裡的協程)
"""

"""
+ pull式, 也就是生成器的資料流
    > for-loop <- Iterator <- Iterator <- ... <- Iterator <- Iterator <- Iterable

+ push式, 也就是經典的協程資料流
    + push式 資料流-1
    > Source of Data -> Coroutine -> Coroutine -> ... -> Coroutine -> Coroutine -> ...

    + push式 資料流-2
    >                 -> Coroutine ->
    > Source of Data --> Coroutine --> Coroutine
    >                 -> Coroutine ->
"""

"""
## push vs task
# 例子最初來源: https://mail.python.org/pipermail/python-ideas/2009-April/003841.html
# 《流暢的 Python》中有一個改寫的版本; 這同時借鑒了兩者的寫法

+ 這是 push式生成器
    ```python
    def coro_averager():
        ''' 計算移動平均值 '''
        count = 0
        total = 0
        avg = None
        while True:
            try:
                val = yield avg
            except GeneratorExit:
                return total, count, avg
            else:
                total += val
                count += 1
                avg = total / count
    ```

+ 這是任務式生成器的偽程式碼
    ```python
    def core_some_task(n):
        print('doing step 1.')
        yield "1秒鐘後回來"     # 出棧前能夠傳出去的最後訊息
        # 1秒鐘時間到, 繼續
        print('doing step 2)
        data = yield "data 可以用了再叫我"
        # data 準備好了, 繼續吧
        return 'done'
    ```
"""

"""
## data vs event

一句話解釋:
    + pull/push 都是受**資料驅動**的
    + task是受**事件驅動**的

'''python    
# pull風格 生成器偽程式碼
def pull_style():
    while still_have_data:
        yield data

# push風格 生成器偽程式碼
def push_style():
    while still_have_data:
        input_data = yield output_data


# task風格 生成器偽程式碼
def task_style():
    ??? = yield ???
'''
"""

"""
## 什麼是「event」?

> 事件(event)是一個抽象的概念, 就是指一件事情發生了.

+ 例如:
    + 要休息 3 秒鐘後繼續執行, 滴答.. 滴答.. 滴答.. 3秒時間到, 這就是一個事件.

+ 再例如:
    + 要讀取網路資料
    ```python
    socket.recv(1024)
    ```
如果 socket 還沒接收資料, 此時這個調用就會阻塞在這裡, 直到有資料可讀.
**socket 變得可讀**, 這就是一個事件.
"""

# %%
"""
## event 是如何運作的?

> 事件通常都是通過`回調函數(callback)`來處理的.
"""

## 設置回調的函數大概是下面這樣子

# 3 秒後調用 func
call_later(3, func)

# 當 socket 可讀時調用 read
register(sock, selectors.EVENT_READ, read)

"""
## 靈魂發問

+ 為什麼要 **讓出** (`yield`)執行權 (也就是出棧)?
    + 遇到什麼樣的事件需要`yield`?
    + 在出棧前該如何設置事件(callback)?

+ 憑什麼能恢復執行 (也就是入棧)?
    + 是誰促成了事件的發生?
    + 是誰 (感知到了事件的發生) 讓出棧的協程再次入棧(也就是說, 誰來調用`send`)?

> PS: 大家不都說有了協程不用寫回調函數了嗎, 這又是怎麼回事?
"""