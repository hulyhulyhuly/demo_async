"""
# 生成器為什麼可以變成協程
+ 生成器函數和普通函數之間的區別
+ 生成器物件和生成器函數之間的關係
+ 生成器函數可以「暫停」執行的秘密 
"""

# %%
"""
## 函數的運行機制
### 函數物件和程式碼物件
每當定義了一個函數之後，就得到了一個「函數物件」：
"""

def func():
    x = 1
    print(x)

print(func)

""" 函數中的程式碼是保存在「程式碼物件 (Code object)」中的 """
print(func.__code__)

"""
程式碼物件會隨著函數物件一起創建，是函數物件的一個重要屬性
> Code objects represent byte-compiled executable Python code, or bytecode.
程式碼物件重要的屬性以`co_`開頭：
"""
func_code = func.__code__

for attr in dir(func_code):
    if attr.startswith('co_'):
        print(f'{attr}\t: {getattr(func_code, attr)}')

# %%
"""
## 函數運行幀
函數物件和程式碼物件保存了函數的基本訊息，當函數運行的時候，還需要一個物件來保存運行時的狀態。
這個物件就是「幀物件 (Frame object)」。
> Frame objec ts represent execution frames.
每一次調用函數，都會自動創建一個幀物件，紀錄當前運行的狀態。
"""

import inspect
from objgraph import show_backrefs

def foo():
    # 獲取到函數的運行幀並返回
    return inspect.currentframe()

f1 = foo()  # 由於被變數所引用，所以幀不會被垃圾回收

f2 = foo()  # 再調用一次，得到另一個幀

## 函件物件、程式碼物件和幀物件之間的關係
show_backrefs(foo.__code__)

# %%
"""
幀物件中重要的屬性以`f_`開頭：
+ `f_code`：執行程式碼的程式碼物件
+ `f_back`：指向上一個幀，也就是調用者的幀
+ `f_locals`：局部變數
+ `f_globals`：全局變數
+ `f_lineno`：當前對應的行數
"""

"""
## 函數運行棧
當一個函數中調用了另一個函數，此時前一個函數還沒有結束，所以這兩個函數的幀物件是同時存在的。

比如，我們的程式一般都始於一個`main`函數，然後又調用了其他函數，以此類推。
因此，一個程式的運行期，同時存在很多個幀物件。

函數之間的調用關係是**先執行的後退出**，所以幀物件之間的關係也是**先入後出**，正好以`棧 Stack`的形式保存。
因此，函數的運行幀又稱為棧幀。

注意：一個線程只有一個函數運行棧。
(https://pythontutor.com/)
"""

# %%
import inspect

# 展示發生函數調用時的棧 
def foo():
    return inspect.currentframe()

def bar():
    return foo()
    # 返回 foo 函數運行時的幀對象

# %%
from objgraph import show_refs

f1 = bar()
show_refs(f1)

# %%
"""
## 生成器函數有何不同
> 生成器函數仍是函數物件，當然也包括了程式碼物件
"""

import inspect

def gen_foo():
    for _ in range(10):
        yield inspect.currentframe()    # 每次迭代都返回當前帧

# %%
"""
調用生成器函數不會直接運行
> (也就是說, 不像普通函數那樣創建幀物件並且壓入函數幀)
而是得到一個生成器物件

那麼秘密自然是藏在生成器物件裡:
"""

gf = gen_foo()
show_refs(gf)

"""
生成器物件
有一個特殊的屬性`gi_frame`
它保留了一個幀物件的一個屬性
這個幀物件和普通函數的幀物件是一樣的
它保留了對我們的程式碼物件的引用

>當每次使用`next()`對生成器進行迭代的時候, 都用這個幀物件(`gi_frame`)來保存狀態:
"""

# %%
## 演示目的: 展示生成器物件迭代的過程中都是同一個幀物件
gf = gen_foo()

# 存為變數, 不然迭代結束後該屬性會清空
gi_frame = gf.gi_frame

# 保存所有迭代的結果
frames = list(gf)

print(gf.gi_frame)  # None

for f in frames:
    print(f is gi_frame)

# %%
""" 在生成器運行的過程中, 觀察運行棧的關係圖 """
def gen_frame_graph():
    for _ in range(10):
        # 在運行時把圖形生成
        graph = show_refs(inspect.currentframe())
        yield graph

# %%
from objgraph import show_refs

gfg = gen_frame_graph()

# 定義兩個不同名的函數是為了方便觀察棧的變化
def func_a(g):
    return next(g)

def func_b(g):
    return next(g)

# %%
func_a(gfg)

# %%
func_b(gfg)


# %%
"""
## 總結
+ 生成器函數並不直接運行, 而是借助於生成器物件來間接運行
+ 創建生成器物件的同時創建了幀物件, 並且由生成器物件保持引用
+ 每次使用`next()`調用生成器時, 就是將生成器引用的幀物件入幀
+ 當`next()`返回時, 也就是程式碼遇到`yield`暫停的時候, 就是將幀出棧
+ 直到迭代結束, 幀最後一次出棧, 並且被銷毀
"""

"""
## 同步和非同步

**普通函數:**
+ 調用函數: 構建幀物件並入棧
+ 函數執行結束: 幀物件出棧並銷毀
"""