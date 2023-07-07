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