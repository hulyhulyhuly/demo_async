# %%
"""
# 基於`Generator`的`Coroutine`

> `Generator-based Coroutines`
> Deprecated since version 3.8, will be removed in version 3.11: Use `async def` instead.
"""

"""
## 對比`generator`和`coroutine`
"""

def generator_func():
    yield

gen = generator_func()

print(gen)

print(sorted(set(dir(gen)) - set(dir(object))))

# %%
async def coroutine_func():
    await coroutine_func()

coro = coroutine_func()

print(coro)

print(sorted(set(dir(coro)) - set(dir(object))))
# %%
gen_attr = set(dir(gen)) - set(dir(object))
cor_attr = set(dir(coro)) - set(dir(object))

print(sorted(gen_attr & cor_attr))
print(sorted(gen_attr - cor_attr))
print(sorted(cor_attr - gen_attr))

# %%
"""
Coroutine 發展時間線
1. Python 2.5
    + [[PEP 342 增強型生成器]]
    > `yield`
2. Python 3.3
    + [[PEP 380 委託子生成器]]
    > `yield from`
3. Python 3.4
    + [[PEP 3156 重啟對非同步IO的支持]]
    > `asyncio`
4. Python 3.5
    + [[PEP 492 增強型生成器]]
    > `async/await`
5. Python 3.6
    + [[PEP 525 非同步生成器]]
    + [[PEP 530 非同步列表解析]]
"""

"""
## 生成器的增強點
+ `yield`語句
    + [[PEP 252 Simple Generators]]
    + Python 2.2
+ `yield`表達式
    + [[PEP 342 Coroutines vis Enhanced Generators]]
    + Python 2.5
"""


# %%
"""
`yield`表達式
> [[PEP 342 Coroutines vis Enhanced Generators]] 把`yield`關鍵字升級成了表達式.
> 所謂表達式(Expression), 意味著它可以被解析成一個**值**.
"""

# 賦值給變數
x = yield

# 計算後賦值給變數
y = yield + 1

# yield 可以作為函數參數, 但是需要使用()括起來
print((yield))  # 需要加括號

# %%
"""
## `yield 表達式`如何獲取到值?
"""

def show_yield_value():
    x = yield
    print(f'x is {x}')

g = show_yield_value()
next(g) # 第 1 次
next(g) # 第 2 次

"""
使用`next()`函數來驅動生成器的時候, `yield`表達式的值總是為`None`.
"""

# %%
"""
為生成器新增一個`send()`方法, 該方法可以接收一個參數.
`send`方法顧名思義, 將該參數發送給生成器, 使生成器恢復運行的同時, 將該參數作為`yield 表達式的值`
"""

def show_yield_value():
    print('開始')
    x = yield
    print(f'x is {x}')

g = show_yield_value()

# 第 1 次, 只能是`None`或是使用`next(g)`
# g.send('hello') 
# TypeError: can't send non-None value to a just-started generator

g.send(None)

# %%
g.send('hello')

# %%
"""
## 關於`prime` (啟動, 激活, 把它叫醒)
對於剛創建好的生成器, 總是需要在第一次的時候`send(None)`值, 
使其運行到`yield`的地方暫停, 這個步驟術語稱為`prime`.

> 這裡`prime`做動詞解釋的意思: 
PREPARE SOMEBODY to prepare someone for a situation so that they know what to do
**使其準備好[應付某個狀況ㄓ]**
"""

# %%
""" `yield`表達式的優先級 """
def add_yield_value():
    x = yield + 1   # bug!?
    print(f'x is {x}')

# %%
g = add_yield_value()
g.send(None)    # prime

# %%
g.send(1)
# 原本預期的結果 1 + 1 = 2
# 但是print出來的結果是 1

"""
x = yield + 1
    vvvvvvvvv
x = (yield +1)
    vvvvvvv
x = (yield 1)
"""
# %%
def add_yield_value():
    x = (yield) + 1   # bug!?
    print(f'x is {x}')

# %%
g = add_yield_value()
g.send(None)    # prime

# %%
g.send(1) # x is 2

# %%
"""
`send()`用法總結

+ `send`是生成器物件的方法
+ 對於生成器物件`g`, `next(g)`等價於`g.send(None)`
+ 只有當生成器處在「暫停」狀態時, 才能傳入非None的值
+ `send`方法是為了 Coroutine 而增加的 API, 所以:
    + 如果將 Generator 視作 Coroutine, 就應該只用`send`方法
    + 如果視作 Iterator, 就仍用`next`

> 所以, 後面統一都使用`g.send(None)`的方法, 而不再採用`next(g)`的方法. 
"""

# %%
"""
一個極簡的 echo
"""

def gen_echo():
    while True:
        print((yield))

# %%
echo = gen_echo()
echo.send(None)
echo.send(123)
echo.send('456')

# %%
echo.send(StopIteration('stop'))    # 試著結束這個 Generator

# %%
"""
## 使用 `close()`結束生成器
當 Generator 作為 Iterator 來用的時候, 它的生命週期取決於有多少元素可以迭代.
而當作 Coroutine 來用的時候, 通常可以視作是在執行一個任務, 我們希望任務的終止能夠變得可控.
新增的`close`方法就是用來結束一個 Coroutine:
"""

echo.close()
echo.send('hi')

# %%
"""
由於 echo Coroutine 的內容非常簡單, 所以可以直接結束.
如果 Coroutine 的程式碼比較複雜, 它可能需要在結束的時候做一些善後處理, 比如釋放資源...
類似於`StopIteration`的實現機制, 結束 Coroutine 也是靠異常實現的:
"""

def gen_echo_v2():
    while True:
        try:
            x = yield
        except GeneratorExit:
            print('exit. bye!')
            return # 必須要結束
        else:
            print(x)
"""
> 如果`GeneratorExit`異常處理沒有 return, 程序還會繼續進行, Generator 可以繼續 send
"""

# %%
echo = gen_echo_v2()
echo.send(None)

# %%
echo.send('123123123')
echo.close()

# %%
"""
> 除了顯式地調用`close`方法, 如果生成器物件被垃圾回收, 也會自動調用`close`:
"""

echo_v2 = gen_echo_v2()
echo_v2.send(None)  # 需要激活才能捕獲到異常

# del echo_v2
echo_v2 = 123

# %%
"""
## 使用`throw()`將異常拋給`yield`
"""

def gen_echo_v3():
    while True:
        try:
            x = yield
        except GeneratorExit:
            print('exit. bye!')
            return
        except KeyboardInterrupt:
            print('按下了 Ctrl-C')
        else:
            print(x)

# %%
echo_v3 = gen_echo_v3()
echo_v3.send(None)

# %%
echo_v3.throw(KeyboardInterrupt)
echo_v3.send(2)
echo_v3.close()

# %%
echo_v3 = gen_echo_v3()
echo_v3.send(None)

# %%
"""
> 如果出現了沒有處理的異常, 也會導致 Generator 終止
"""
echo_v3.throw(RuntimeError)
echo_v3.send(2)
echo_v3.close()

# %%
"""
## 總結 Coroutine 的幾個功能點
"""

# 例子最初來源: https://mail.python.org/pipermail/python-ideas/2009-April/003841.html
# 《流暢的 Python》中有一個改寫的版本; 這同時借鑒了兩者的寫法

def coro_averager():
    """ 計算移動平均值 """
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

"""
1. 在`yield`的地方產出資料
2. 在`yield`的地方暫停
3. 在`yield`的地方恢復, 並接受新的參數
4. 在`yield`的地方傳入結束信號
5. 在`yield`的地方傳入其他異常 
"""
# %%
coro = coro_averager()
coro.send(None)
# %%
coro.send(10)
# %%
coro.send(20)
# %%
coro.send(0)

# %%
coro.close()