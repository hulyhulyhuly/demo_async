# %%
"""
# 什麼是生成器 (Generator) ?

## `yield` 很特別
+ 只能用在函數內
+ 在函數內任何地方出現`yield`關鍵字，哪怕永遠無法被執行到，函數都會發生變異。
"""

def gen():
    print('hello')
    if 0:
        yield

g = gen()
print(g)

"""
調用`gen()`沒有像普通函數那樣執行其中的程式碼
，而是返回了一個`generator`物件
"""

# %%
print(type(gen))
print(type(g))
# %%
import inspect

# 是一般函數，也是生成器函數
print(inspect.isfunction(gen))          # True
print(inspect.isgeneratorfunction(gen)) # True

# 生成器函數不是 `generator`
print(inspect.isgenerator(gen)) # False
print(inspect.isgenerator(g))   # True

# %%
"""
## <術語概念澄清>
含有`yield`的函數稱之為「生成器函數 `generator funciton`」
調用`生成器函數`返回的結果稱為「生成器 `generator`」

```
但是根據 Python 官方文檔：
generator 生成器
A function which returns a generator iterator. ...
一個返回生成器迭代器的函數

Usually refers to a generator function, but may refer to a generator iterator in some contexts.
In cases where the intended meaning isn't clear, using the full terms avoids ambiguity.
通常指的是生成器函數，但是在一定的語境下也可以指代生成器迭代器。為了避免歧義，推薦使用完整的術語。
```

在不會產生歧義的情況下，提到「生成器」可能指的是函數，也可能是函數生成的物件，具體需要根據上下文判斷。
為了區分，這裡一般將「生成器函數 `generator funciton`」的返回結果稱為「生成器物件 `generator object`」。
"""

# %%
"""
## 生成器是迭代器
`generator iterator` 這個名字非常拗口, 實際很少這麼說, 但是它卻指出了:
`「生成器物件」是迭代器`
(生成器是迭代器的一種特殊形式)

既然是迭代器, 那麼肯定要滿足「迭代器協議」:
    + `__iter__`, 返回迭代器物件本身
    + `__next__`, 每次返回一個迭代資料, 如果沒有資料, 則要拋出`StopIteration`異常 
"""

print(hasattr(g, '__next__') and hasattr(g, '__iter__'))
print(g is iter(g))

# %%
""" 
## yield 關鍵字

### 語句 or 表達式 ?

+ `yield` 語句
    + PEP 255 Simple Generator
    + Python 2.2

+ `yield` 表達式
    + PEP 342 Coroutines via Enhanced Generators
    + Python 2.5
"""

# %%
"""
## `yield` 對函數做了什麼

`yield` 最根本的作用是改變了函數的性質:
    1. 調用生成器函數不是直接執行其中的程式碼, 而是返回一個物件
    2. 生成器函數內的程式碼. 需要通過生成器物件來執行

從這一點上說, 生成器函數的作用和類(class)是差不多的
"""

# %%
"""
生成器物件就是迭代器, 所以它的運作方式和迭代器是一樣的:
    + 通過`next()`函數來調用
    + 每次`next()`都會在遇到`yield`後返回結果(作為`next()`的返回值)
    + 如果函數運行結束(即遇到`return`)則拋出`StopIteration`異常
"""

# %%
# 簡單範例 1
# 定義一個生成器函數
def gen_777(meet_yield):
    print('hello')
    if meet_yield:  # 是否遇到 yield 由參數控制
        print('yield!')
        yield 777
        print('back!')
    print('bye')
    return 'result'

# %%
g1 = gen_777(False) # 不會碰到 yield

# %%
x1 = next(g1)
print(x1)

# %%
g2 = gen_777(True)

# %%
x2 = next(g2)

# %%
print(x2)

# %%
print(next(g2))

# %%
"""
## 在循環中使用 `yield`

只遭遇一次`yield`語句的生成器就是只能迭代一次的迭代器, 通常沒什麼實用價值.
要想能迭代多次, 可以在函數內多次使用`yield`語句:
"""

def gen_func():
    print('--- yield 1 ---')
    yield 1
    print('--- yield 2 ---')
    yield 2
    print('--- yield 3 ---')
    yield 3

for x in gen_func():
    print(x)

# %%
""" 
> 相對應地, `yield`一般也是搭配循環使用的:

"""

# itertools.count 示例
def count(start=0, step=1):
    # count(10) -> 10 11 12 13 14 ...
    # count(2.5, 0.5) -> 2.5 3.0 3.5 ...
    n = start
    while True:
        yield n
        n += step

# %%
c = 0
for n in count(10):
    if c == 10:
        break
    print(n)
    c += 1

# %%
"""
## 生成器的 4 個狀態
+ 當調用生成器函數得到生成器物件時
    + 此時的生成器物件可以理解為處於**初始**狀態

+ 通過`next()`調用生成器物件, 對應的生成器函數程式碼開始運行
    + 此時生成器物件處於**運行中**狀態

+ 如果遇到`yield`語句, `next()`返回時
    + `yield`語句右邊的物件作為`next()`的返回值
    + 生成器在`yield`語句所在的位置**暫停**, 當再次使用`next()`時繼續從該位置繼續執行

+ 如果執行到函數結束, 則拋出`StopIteration`異常
    + 不管是使用`return`語句顯式地返回, 或著默認返回`None`值, 返回值都只能作為異常的值一並拋出
    + 此時生成器物件處於**結束**的狀態
    + 對於已經結束得生成器物件再次調用`next()`, 則拋出`StopIteration`異常, 並且不包含返回值
"""

# %%
""" 
## 用`yield`重構迭代器

> 和`class`定義的迭代器進行對比

「action」               「Iterator impled by Class」              「yield Generator」
-------------------------------------------------------------------------------------
define Iterator         class Iterator:                        def iter_fun(*args):
                            def __init__(self, *args):             ...
-------------------------------------------------------------------------------------
build Iterator          Iterator(args)                          iter_fun(args)
-------------------------------------------------------------------------------------
next(Iterator)          def __next__(self): return value        yield value
-------------------------------------------------------------------------------------
StopIteration           raise StopIteration                     return
-------------------------------------------------------------------------------------
iter(Iterator)          def __iter__(self): return self         AUTO implement
"""

# %%
"""
## 生成器的三種應用場景:
    + 定義一個容器類的可迭代物件, 為該物件實現`__iter__`
    + 定義一個處理其他可迭代物件的迭代器
    + 定義一個不依賴資料儲存的資料生成器
"""