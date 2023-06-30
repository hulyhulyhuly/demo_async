# %%
""" 常見可迭代物件 """
iterables = [
    "123",              # string
    [1, 2, 3],          # list
    (1, 2, 3),          # tuple
    { 1: 'a', 2:'b' },  # dict
    {1, 2, 3}           # set
]

for iterable in iterables:
    print(type(iterable))
    print(", ".join(str(i) for i in iterable))
    print()

# %%
def common_attr(*objs):
    """ 提取物件之間的共同屬性 """
    assert(len(objs) > 0)
    attrs = set(dir(objs[0]))
    for obj in objs:
        attrs &= set(dir(obj))      # 取交集
    attrs -= set(dir(object))       # 剔除基礎物件的屬性
    return attrs

# %%
""" 計算可迭代物件的共同屬性 """
iterable_common_attrs = common_attr(*iterables)
print(iterable_common_attrs)

# %%
""" 文件物件也是可迭代物件 """
f = open('example_01.py', 'r')

# 加入到可迭代物件的列表中
iterables.append(f)

# 繼續求一次交集
iterable_common_attrs &= set(dir(f))
print(iterable_common_attrs)

""" 「可迭代物件」唯一的共同屬性：__iter__ """
""" __iter__方法，對應的調用方法就是內置函數`iter()` """ 

# %%
for iterable in iterables:
    print(iter(iterable))

# 由可迭代物件列表得到相應的迭代器列表
iterators = [iter(iterable) for iterable in iterables]

# 故技重施，計算迭代器的共同屬性
iterator_common_attrs = common_attr(*iterators)
print(iterator_common_attrs)

""" 「迭代器」有兩個屬性：__iter__、__next__ """

# %%
actions = ['點讚', '投幣', '收藏']    # 可迭代物件
action_iterator = iter(actions)     # 第 1 步：構建迭代器

# 第 2 步：多次迭代
for _ in range(len(actions)):
    action = next(action_iterator)  # 運行 3 次
    print(action)

# %%
# 第 3 步：迭代結束
action = next(action_iterator)  # 運行 3 次
print(action)

# %%
""" 
迭代的三個關鍵步驟
+ 調用 iter(iterable) 構建迭代器
+ (多次) 調用 next(iterator) 獲取值
+ 最後捕獲`StopIteration`異常來判斷迭代結束
"""

# %%
""" 用 while 循環模擬 for 循環迭代 """

# 創建迭代器
iterator = iter(actions) # 對應 可迭代物件的 __iter__ 方法
while True:
    try:
        # 通過迭代器獲取下一個值
        print(next(iterator))   # 對應 迭代器的 __next__ 方法
    except StopIteration:       # 捕獲異常來判斷結束
        # print('迭代結束')
        break

""" 迭代器的 __iter__ 方法作用在哪裡? """
# %%
"""
# 自定義迭代器
## 設計一個迭代器
### 迭代器基本功能：
+ 初始化時要傳入可迭代物件，這樣才能知道去哪獲取資料
+ 要初始化迭代進度
+ 每次迭代時，即每次調用 __next__()方法時：
    + 如果仍有元素可供迭代，返回本次迭代的元素，同時更新當前迭代進度
    + 如果已無元素可供返回，則迭代結束，拋出 `StopIteration` 異常
---
### 再添加一些額外的邏輯：
+ 設置一名黑名單，如果當前元素在黑名單內，則跳過
+ 將某些符合條件的資料 `*2` 之後再返回
"""

BLACK_LIST = ['白嫖', '取消關注']

class DemoIterator:
    def __init__(self, actions) -> None:
        self.actions = actions
        self.index = 0          # 初始化索引位置
    
    def __next__(self):
        while self.index < len(self.actions):
            action = self.actions[self.index]
            self.index += 1 # 更新索引位置

            if action in BLACK_LIST:
                continue
            elif '幣' in action:
                return action * 2
            else:
                return action
        
        raise StopIteration

actions = ['點讚', '投幣', '取消關注']
demo_iterator = DemoIterator(actions)

while True:
    try:
        print(next(demo_iterator))
    except StopIteration:
        break

# %%
""" for-loop 需要的是「可迭代物件」，而不是「迭代器」 """
for x in DemoIterator(actions):
    print(x)

# %%
""" 一個沒有存在意義的可迭代物件 """
class DemoActions:
    def __init__(self, actions):
        self.actions = actions
    def __iter__(self):
        return DemoIterator(self.actions)

for x in DemoActions(actions):
    print(x)

# %%
class DemoIterator:
    def __init__(self, actions) -> None:
        self.actions = actions
        self.index = 0          # 初始化索引位置
    
    def __next__(self):
        while self.index < len(self.actions):
            action = self.actions[self.index]
            self.index += 1 # 更新索引位置

            if action in BLACK_LIST:
                continue
            elif '幣' in action:
                return action * 2
            else:
                return action
        
        raise StopIteration
    
    """
    `__iter__`
    我要返回一個迭代器
    我已經在迭代器裡面了 (我自己就是迭代器)
    所以直接返回我自己就可以了
    """
    def __iter__(self):
        return self

# %%
""" 「迭代器」也是「可迭代物件」 """
for x in DemoIterator(actions):
    print(x)

# %%
"""
## 迭代器協議 Iterator Protocal
在 Python 文檔中明確指出了，迭代器必須同時實現`__next__`和`__iter__` 兩個方法，這稱之為「迭代器協議」。
根據這個協議，迭代器必須是可迭代的，換言之，「迭代器」是一種「可迭代物件」。

缺少了`__iter__`方法的迭代器是不完整的，不符合迭代器協議的要求。
所有迭代器的`__iter__`方法都只要千篇一律的`return self`即可。
"""

# %%
"""
## 淺層的意義
+ 統一通過 `next()`方法獲取資料，可以屏蔽底層不同的資料讀取方式，簡化程式碼
+ 容器類的資料結構只關心資料的靜態儲存，每一次迭代都需要額外的迭代器對物件專門負責記錄迭代過程的狀態訊息

按照這個思路，我們很容易形成這樣的認知：
> 迭代器就是為了讓資料結構能夠快速地遍歷而定義的輔助物件
"""
for iterable in iterables:
    print(iter(iterable))

""" 但是別忘了，如果只是在`for`循環中使用，是無需用到迭代器的`__iter__`方法 """

# %%
"""
## 深層的意義
為什麼說迭代器的`__iter__`方法是點睛之筆!

### 現在有兩種可迭代物件：
+ 容器類型 Container Type
    + list, tuple, dict...
    + `__iter__` attr only
    + static data
    + support by extra iterator required

+ 迭代器類型 Iterator Type
    + file, StringIO...
    + 同時實現`__iter__`和`__next__`
    + dynamic
    + iter once only


### 針對可迭代物件的循環
```python
for x in iterable:  # 背後操作：「可迭代物件」->「迭代器」
    ...
```
> 此種期況下，只有可迭代物件在前台露臉。
> 而迭代器是在背後使用默認的方式"悄悄"構建的，沒有存在感，並且生命週期是和循環操作本身綁定在一起的。

而一旦迭代器實現了`__iter__`方法

### 針對迭代器的循環
```python
iterator = iter(iterable)   # 迭代器的購艦過程遠離循環而存在

for x in iterator:  # 背後操作：「迭代器」->「迭代器」(self)
    ...
```
> 現在整個迭代過程只需要迭代器就夠了
> 迭代器不光是從後台走向了前台，而且直接讓可迭代物件遠離了循環

現在，迭代器的構建是在明面上單獨完成的，和當前循環操作解耦了
於是乎：
+ 一個可迭代物件可以構建出任意多個不同的迭代器
+ 一種迭代器可以應用於任意多個可迭代物件 (包含其他迭代器)
"""

# %%
"""
## 資料管道 Data Pipeline
如果迭代器不可迭代：
「for循環」<-「迭代器(隱藏)」<-「可迭代物件」

現在，迭代器可以任意的嵌套連接
「for循環」<-「迭代器」<-「迭代器」<-...<-「迭代器」<-「迭代器」<-「可迭代物件」
---
+ 很多個迭代器串聯起來，形成一個`處理資料的管道`，或稱為`資料流`
+ 在這個管道中，每次只通過一份資料，避免了一次性加載所有資料
+ 迭代器也不僅僅只是按順序返回資料那麼簡單了，他開始承擔`處理資料`的責任
    + 例如，`DemoIterator`實際上實現了部分過濾器和放大器的功能。
+ 當通過迭代器獲取資料的時候，遠離了資料儲存，漸漸地開始`不關心資料到底是怎儲存的`。
"""

# %%
from random import random

class Random:
    def __iter__(self):
        return self
    
    def __next__(self):
        return random()
    
"""
這個迭代器不但不需要儲存資料，甚至連`StopIteration`都不用管。
它可以無窮無盡地迭代下去，每次資料都是實時產生的，並不占用記憶體空間。

有經驗的應該就能看出來，這就是「生成器」

雖然該迭代器是名符其實的`資料生成器`，但是`生成器(Generator)`在 Python 中特指包含`yield`的函數物件，這是下一張的內容。
"""

# %%
"""
# 附錄：沒有定義`__iter__`的可迭代物件
並不是所有的可迭代物件都必須定義有`__iter__`方法
如果一個物件沒有`__iter__`方法，但是定義了`__getitem__`方法，同樣是可以迭代的。
"""

class DumbList:
    def __getitem__(self, index):
        if index > 5:
            raise StopIteration
        return index * 2
    
dl = DumbList()
for x in dl:
    print(x)

"""
因此，不能通過檢查`__iter__`方法來判斷一個物件是否是可迭代的，
而是應該直接使用`iter()`函數，如果不可迭代，則會拋出`TypeError`異常。
"""

class NoIterable:
    ...

ni = NoIterable()
it = iter(ni)
# %%
