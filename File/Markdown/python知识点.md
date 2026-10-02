# Python 完整知识点速查卡（基础 + 进阶 + 工程化）


## 目录

- 第一部分：语言基础
  - [一、输出与输入](#一输出与输入)
  - [二、变量与数据类型](#二变量与数据类型)
  - [三、可变与不可变类型](#三可变与不可变类型核心概念)
  - [四、运算符](#四运算符)
  - [五、字符串操作](#五字符串操作详细)
  - [六、列表操作](#六列表list详细操作)
  - [七、元组](#七元组tuple不可变的列表)
  - [八、集合](#八集合set无序不重复)
  - [九、字典](#九字典dict详细操作)
  - [十、条件判断](#十条件判断if-elif-else)
  - [十一、循环](#十一循环)
- 第二部分：函数与进阶特性
  - [十二、函数](#十二函数详细)
  - [十三、生成器 yield](#十三生成器-yield内存优化神器)
  - [十四、迭代器协议](#十四迭代器协议)
  - [十五、闭包与作用域](#十五闭包与作用域)
  - [十六、装饰器](#十六装饰器-decoratorpython-灵魂特性)
- 第三部分：面向对象
  - [十七、类与对象](#十七类与对象oop-基础)
  - [十八、高级 OOP](#十八高级-oopmro描述符元类)
  - [十九、枚举 enum](#十九枚举-enum)
  - [二十、数据类 dataclass](#二十数据类-dataclass)
- 第四部分：异常与文件
  - [二十一、异常处理](#二十一异常处理tryexcept)
  - [二十二、文件操作](#二十二文件操作)
  - [二十三、上下文管理器](#二十三上下文管理器with-语句原理)
- 第五部分：模块、包与工程化
  - [二十四、模块与包](#二十四模块与包)
  - [二十五、pip 包管理 + 虚拟环境](#二十五pip-包管理--虚拟环境)
  - [二十六、工程化：uv / poetry / pyproject.toml](#二十六工程化uv--poetry--pyprojecttoml)
  - [二十七、打包与发布 PyPI](#二十七打包与发布-pypi)
- 第六部分：标准库与生态
  - [二十八、常用内置函数](#二十八常用内置函数)
  - [二十九、匿名函数 lambda](#二十九匿名函数lambda)
  - [三十、常用内置模块速查](#三十常用内置模块速查)
  - [三十一、标准库补全](#三十一标准库补全)
  - [三十二、序列化与配置](#三十二序列化与配置)
  - [三十三、网络请求](#三十三网络请求)
  - [三十四、数据库](#三十四数据库)
  - [三十五、安全与危险函数](#三十五安全与危险函数)
- 第七部分：并发与异步
  - [三十六、多线程 threading](#三十六多线程-threading)
  - [三十七、多进程 multiprocessing](#三十七多进程-multiprocessing绕过-gil)
  - [三十八、异步 asyncio](#三十八异步-asyncioasyncawait)
  - [三十九、异步进阶](#三十九异步进阶)
  - [四十、并发模型选择](#四十并发模型选择)
- 第八部分：类型系统
  - [四十一、类型注解 Type Hints](#四十一类型注解-type-hints)
  - [四十二、类型注解进阶](#四十二类型注解进阶)
- 第九部分：测试与质量
  - [四十三、测试](#四十三测试unittestpytestmockcoverage)
  - [四十四、代码质量工具](#四十四代码质量工具ruffblackisortmypypre-commit)
- 第十部分：性能与调试
  - [四十五、性能优化技巧](#四十五性能优化技巧)
  - [四十六、性能分析工具](#四十六性能分析工具)
- 第十一部分：其他
  - [四十七、深拷贝 vs 浅拷贝](#四十七深拷贝-vs-浅拷贝)
  - [四十八、正则表达式 re](#四十八正则表达式-re详细)
  - [四十九、Python 版本与新特性](#四十九python-版本与新特性)
  - [五十、常见 Python 陷阱与坑](#五十常见-python-陷阱与坑)
  - [五十一、常见错误与解决办法](#五十一常见错误与解决办法)
  - [五十二、综合小项目](#五十二综合小项目)
  - [五十三、速查小抄](#五十三速查小抄)

---

# 第一部分：语言基础

## 一、输出与输入

```python
# print() 输出
print("你好")
print("我" + "你")
print(3 + 5)
print("=" * 30)
print("a", "b", "c", sep="-")   # a-b-c
print("hello", end="")          # 不换行

# 输出到文件（务必关闭）
with open("log.txt", "w", encoding="utf-8") as f:
    print("你好", file=f)

# input() 输入
name = input("请输入你的名字：")
age = int(input("年龄："))        # input 返回字符串，需转换

# Python 3.8+ 海象运算符（赋值表达式）
while (line := input("输入（q 退出）：")) != "q":
    print(f"收到：{line}")
```

## 二、变量与数据类型

```python
# 基本类型
name = "小明"                    # str
age = 13                         # int
score = 95.5                     # float
is_student = True                # bool
nothing = None                   # NoneType
complex_num = 1 + 2j             # complex
bytes_data = b"hello"            # bytes
byte_array = bytearray(b"hi")    # bytearray（可变）

# 查看类型
print(type(name))
print(isinstance(age, int))      # True

# 类型转换
int("123"); str(123); float("3.14")
bool(0)                          # False
list("abc"); tuple([1,2,3]); set([1,2,2,3])
dict([("a",1), ("b",2)])

# f-string（推荐）
print(f"我叫{name}，今年{age}岁")

# f-string 高级用法（Python 3.6+）
x = 3.14159
print(f"{x:.2f}")                # 3.14
print(f"{x:>10.2f}")             # 右对齐
print(f"{x=}")                   # x=3.14159（调试用）
print(f"{age:03d}")              # 013
print(f"{255:#x}")               # 0xff
n = 1234567
print(f"{n:,}")                  # 1,234,567

# format() / % 格式化
print("我叫{}，今年{}岁".format(name, age))
print("我叫%s，今年%d岁" % (name, age))
```

## 三、可变与不可变类型（核心概念）

```python
# 不可变：int, float, str, bool, tuple, frozenset, bytes
# 可变：list, dict, set, bytearray

# 函数参数传递
def modify(x, lst):
    x += 1           # 不可变，不影响外部
    lst.append(4)    # 可变，影响外部

num = 10
my_list = [1, 2, 3]
modify(num, my_list)
print(num)           # 10
print(my_list)       # [1, 2, 3, 4]

# 默认参数陷阱（巨坑！）
def bad_func(lst=[]):    # 危险
    lst.append(1)
    return lst

print(bad_func())    # [1]
print(bad_func())    # [1, 1] ← 共享同一列表

def good_func(lst=None):
    if lst is None:
        lst = []
    lst.append(1)
    return lst

# 小整数缓存与 is 陷阱
a = 256; b = 256
print(a is b)        # True（-5~256 缓存）
a = 257; b = 257
print(a is b)        # 可能 False，也可能是 True，取决于实现
# 结论：值比较永远用 ==，is 只用于 None / True / False / 单例判断
```

## 四、运算符

```python
# 算术
10 + 3; 10 - 3; 10 * 3
10 / 3      # 3.333...
10 // 3     # 3
10 % 3      # 1
10 ** 3     # 1000

# 比较：== != > < >= <=
# 逻辑：and or not
# 赋值：= += -= *= /= //= %= **= 以及海象 :=

# 身份：is / is not（只用于 None 和单例判断）
# 成员：in / not in

# 位运算
5 & 3       # 1
5 | 3       # 7
5 ^ 3       # 6
~5          # -6
5 << 1      # 10
5 >> 1      # 2

# 优先级（高→低）：
# ** → 正负号 → * / // % → + - → << >> → & → ^ → | → 比较 → not → and → or

# 链式比较（Python 特有）
if 18 <= age <= 60:
    print("工作年龄")
```

## 五、字符串操作（详细）

```python
s = "Hello World"

len(s); s[0]; s[-1]
s[0:5]; s[6:]; s[:5]; s[::2]; s[::-1]

s.lower(); s.upper(); s.capitalize(); s.title(); s.swapcase()
s.split(); s.split(','); s.rsplit()
s.replace('World', 'Python')
s.strip(); s.lstrip(); s.rstrip()
s.startswith('He'); s.endswith('ld')
s.find('o'); s.rfind('o'); s.index('o')
s.count('l')
s.isdigit(); s.isalpha(); s.isalnum(); s.isspace()
','.join(['a', 'b', 'c'])

# 字符串格式化
f"Hello {name}"
"Hello {}".format(name)
"Hello %s" % name

# 转义字符
'\n'; '\t'; '\\'; '\''; '\"'; '\r'; '\b'

# 多行字符串
text = """
第一行
第二行
"""

# 原始字符串（不转义）
path = r"C:\Users\name"

# 编码与解码
s = "中文"
s.encode("utf-8")           # b'\xe4\xb8\xad\xe6\x96\x87'
b = b'\xe4\xb8\xad\xe6\x96\x87'
b.decode("utf-8")           # '中文'
```

## 六、列表（List）详细操作

```python
fruits = ["苹果", "香蕉", "橙子"]
nums = list(range(5))
empty = []
mixed = [1, "hello", 3.14, True]

# 访问与修改
fruits[0]; fruits[-1]; fruits[0] = "葡萄"
fruits[1:3]; fruits[1:3] = ["芒果", "西瓜"]

# 添加
fruits.append("西瓜"); fruits.insert(1, "芒果"); fruits.extend(["草莓"])

# 删除
fruits.remove("香蕉"); fruits.pop(); fruits.pop(1)
del fruits[0]; del fruits[1:3]; fruits.clear()

# 查找与统计
fruits.index("橙子"); fruits.count("苹果"); len(fruits)
"苹果" in fruits

# 排序
nums = [3, 1, 4, 1, 5]
nums.sort()                     # 原地升序
nums.sort(reverse=True)         # 原地降序
nums.sort(key=lambda x: abs(x))
sorted(nums)                    # 返回新列表

# 多级排序
students = [("小明", 90, 18), ("小红", 90, 17), ("小刚", 85, 19)]
students.sort(key=lambda x: (-x[1], x[2]))  # 按分数降序、年龄升序

# 复制（浅拷贝）
new_list = fruits.copy()
new_list = fruits[:]
new_list = list(fruits)

# 推导式
squares = [x**2 for x in range(5)]
evens = [x for x in range(10) if x % 2 == 0]
matrix = [[0 for _ in range(3)] for _ in range(3)]
[x if x % 2 == 0 else 'odd' for x in range(5)]
[(x, y) for x in range(3) for y in range(2)]

# 常用
max(nums); min(nums); sum(nums); any(nums); all(nums)
```

## 七、元组（Tuple）——不可变的列表

```python
t = (1, 2, 3)
t = 1, 2, 3                     # 不加括号也可以
single = (1,)                   # 单元素必须有逗号
empty = ()
from_list = tuple([1, 2, 3])

# 访问
t[0]; t[1:3]; len(t)

# 解包
a, b, c = (1, 2, 3)
a, *rest = (1, 2, 3, 4)         # a=1, rest=[2,3,4]
*init, last = (1, 2, 3, 4)      # init=[1,2,3], last=4

# 命名元组
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
p.x; p.y                        # 10, 20

# 字典键
d = {(1, 2): "坐标"}

# 交换变量
a, b = b, a
```

## 八、集合（Set）——无序、不重复

```python
s = {1, 2, 3}
s = set([1, 2, 2, 3])           # 去重
empty = set()                   # 注意 {} 是空字典

# 添加删除
s.add(4); s.remove(2); s.discard(5); s.pop(); s.clear()

# 集合运算
a = {1, 2, 3}; b = {2, 3, 4}
a | b    # 并集
a & b    # 交集
a - b    # 差集
a ^ b    # 对称差
a.issubset(b); a.issuperset(b); a.isdisjoint(b)

# 冻结集合（不可变，可作字典键）
fs = frozenset([1, 2, 3])

# 推导式
{x for x in [1, 2, 2, 3]}       # {1, 2, 3}
```

## 九、字典（Dict）详细操作

```python
person = {"name": "小明", "age": 18}
person = dict(name="小明", age=18)
person = dict([("name", "小明"), ("age", 18)])

# 访问
person["name"]                  # 键不存在会报错
person.get("name")              # 安全访问
person.get("height", 170)       # 默认值
person.setdefault("city", "北京")

# 修改
person["age"] = 19
person["city"] = "北京"

# 删除
del person["age"]
age = person.pop("age")
item = person.popitem()
person.clear()

# 遍历
for key in person: ...
for key, value in person.items(): ...
for value in person.values(): ...

# 合并
d1 = {"a": 1}; d2 = {"b": 2}
d1.update(d2)
d3 = {**d1, **d2}               # Python 3.5+
d4 = d1 | d2                    # Python 3.9+

# 推导式
{x: x**2 for x in range(5)}

# 视图
person.keys(); person.values(); person.items()

# 有序性（Python 3.7+ 保证插入顺序）
# 统计
from collections import Counter
Counter("hello")                # {'h':1, 'e':1, 'l':2, 'o':1}

# 分组
from collections import defaultdict
groups = defaultdict(list)
for name, dept in [("小明","A"), ("小红","B"), ("小刚","A")]:
    groups[dept].append(name)
```

## 十、条件判断（if-elif-else）

```python
age = 13
if age < 12:
    print("小朋友")
elif age > 14:
    print("大朋友")
else:
    print("刚刚好")

# 三元表达式
result = "成年" if age >= 18 else "未成年"

# 多条件
if age >= 18 and age <= 60: ...
if age < 12 or age > 65: ...
if not is_student: ...

# 链式比较
if 18 <= age <= 60: ...

# 假值判断
# False, None, 0, 0.0, "", [], (), {}, set(), range(0)
if not some_list:
    print("列表为空")

# match-case（Python 3.10+）
status = 200
match status:
    case 200: print("成功")
    case 404: print("未找到")
    case 500: print("服务器错误")
    case _: print("未知")

# match-case 模式匹配（更高级用法）
point = (0, 5)
match point:
    case (0, 0):
        print("原点")
    case (0, y):
        print(f"Y轴上 y={y}")
    case (x, 0):
        print(f"X轴上 x={x}")
    case (x, y):
        print(f"点 ({x}, {y})")

# 守卫
match point:
    case (x, y) if x == y:
        print("对角线")

# 类模式
class Point:
    __match_args__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y

match Point(1, 2):
    case Point(x=0, y=0): print("原点")
    case Point(x=x, y=y): print(f"{x}, {y}")
```

## 十一、循环

```python
# for
for i in range(5): ...
for i in range(1, 6): ...
for i in range(0, 10, 2): ...
for fruit in fruits: ...

# 带索引
for i, fruit in enumerate(fruits): ...

# 字典
for key, value in person.items(): ...

# while
count = 0
while count < 5:
    count += 1

# 无限循环
while True:
    if input("输入 q 退出：") == 'q':
        break

# break / continue
for i in range(10):
    if i == 3: continue
    if i == 7: break
    print(i)

# for-else（循环正常结束时执行）
for i in range(3):
    print(i)
else:
    print("正常结束")   # break 时不执行

# zip
for name, age in zip(names, ages): ...

# zip 严格模式（Python 3.10+）
for a, b in zip([1,2], [3,4], strict=True): ...

# itertools 迭代工具
from itertools import product, permutations, combinations, chain, groupby, islice
product([1,2], ['a','b'])       # 笛卡尔积
permutations([1,2,3], 2)        # 排列
combinations([1,2,3], 2)        # 组合
chain([1,2], [3,4])             # 拼接
groupby("AAABBBCC")             # 分组
islice(range(10), 2, 5)         # 切片
```

---

# 第二部分：函数与进阶特性

## 十二、函数（详细）

```python
def say_hello():
    print("你好！")

def greet(name):
    print(f"你好，{name}！")

def add(a, b):
    return a + b

# 默认参数（不要用可变对象！）
def greet(name="世界"):
    print(f"你好，{name}")

# 关键字参数
greet(name="小红")

# 可变位置参数
def sum_all(*args):
    return sum(args)

# 可变关键字参数
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

# 参数顺序：必选 → 默认 → *args → **kwargs
def func(a, b=1, *args, **kwargs):
    pass

# 仅位置参数（Python 3.8+）
def f(a, b, /, c):
    # a, b 只能位置传参；c 位置或关键字
    pass

# 仅关键字参数
def f(a, *, b):
    # b 必须关键字传参
    pass

# 返回多个值（本质元组）
def get_name_and_age():
    return "小明", 18

name, age = get_name_and_age()

# 解包调用
def add(a, b, c): return a + b + c
nums = [1, 2, 3]
add(*nums)              # 6
info = {"a": 1, "b": 2, "c": 3}
add(**info)             # 6

# 类型注解
def greet(name: str) -> str:
    return f"Hello, {name}"

# global / nonlocal
x = 10
def f1():
    global x
    x = 20

def outer():
    y = 1
    def inner():
        nonlocal y
        y = 2
    inner()
    return y    # 2

# 闭包
def outer(x):
    def inner(y):
        return x + y
    return inner

add_five = outer(5)
add_five(3)             # 8

# 函数作为一等公民
def apply(func, x):
    return func(x)

apply(lambda x: x**2, 5)  # 25

# 函数属性
f.__name__; f.__doc__; f.__annotations__
```

## 十三、生成器 yield（内存优化神器）

```python
# 生成器函数
def generator_demo(n):
    for i in range(n):
        yield i

gen = generator_demo(5)
next(gen)               # 0
next(gen)               # 1
for x in gen:           # 2, 3, 4
    print(x)

# 无限生成器
def infinite_counter():
    n = 0
    while True:
        yield n
        n += 1

# 斐波那契
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# 生成器表达式（惰性求值）
gen_expr = (x**2 for x in range(1_000_000))   # 几乎不占内存

# send() 双向通信
def gen_with_send():
    value = yield "等待输入"
    print(f"收到: {value}")
    yield "结束"

g = gen_with_send()
print(next(g))          # 等待输入
print(g.send("hello"))  # 收到: hello → 结束

# throw() / close()
g.throw(ValueError)
g.close()

# yield from（委托给子生成器）
def chain_gen(*iterables):
    for it in iterables:
        yield from it

list(chain_gen([1,2], [3,4], [5]))  # [1,2,3,4,5]

# 生成器 return 值（通过 StopIteration.value）
def sub():
    yield 1
    return "done"

def main_gen():
    result = yield from sub()
    print(result)       # done

list(main_gen())

# 异步生成器（async for）
async def async_gen():
    for i in range(3):
        yield i

async def consume():
    async for x in async_gen():
        print(x)
```

## 十四、迭代器协议

```python
# 可迭代对象（Iterable）：实现 __iter__
# 迭代器（Iterator）：实现 __iter__ 和 __next__

class CountDown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

for x in CountDown(3):
    print(x)    # 3, 2, 1

# 判断
from collections.abc import Iterable, Iterator
isinstance([1,2,3], Iterable)     # True
isinstance(iter([1,2,3]), Iterator)  # True
isinstance([1,2,3], Iterator)     # False

# iter() 和 next()
it = iter([1, 2, 3])
next(it)    # 1
next(it)    # 2
next(it, "默认值")  # 3

# 无限迭代器
from itertools import count, cycle, repeat
count(10)               # 10, 11, 12, ...
cycle([1,2,3])          # 1,2,3,1,2,3,...
repeat("x", 3)          # 'x','x','x'
```

## 十五、闭包与作用域

```python
# LEGB 规则：Local → Enclosing → Global → Built-in

x = "global"
def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)        # local
    inner()
    print(x)            # enclosing

# nonlocal 修改外层非全局变量
def counter():
    count = 0
    def inc():
        nonlocal count
        count += 1
        return count
    return inc

c = counter()
c(); c()                # 1, 2

# global 修改全局变量
y = 0
def bump():
    global y
    y += 1

# 闭包延迟绑定陷阱
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]    # [2, 2, 2] ← 全部返回 2

# 正确做法
funcs = [lambda i=i: i for i in range(3)]
[f() for f in funcs]    # [0, 1, 2]

# __closure__
def outer2():
    x = 10
    def inner():
        return x
    return inner

f = outer2()
print(f.__closure__[0].cell_contents)  # 10
```

## 十六、装饰器 @decorator（Python 灵魂特性）

```python
from functools import wraps

# 1. 基础装饰器
def my_decorator(func):
    def wrapper():
        print("执行前...")
        func()
        print("执行后...")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

# 2. 通用装饰器（保留元信息）
def timer(func):
    import time
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} 耗时：{time.time()-start:.4f}s")
        return result
    return wrapper

# 3. 带参数的装饰器（装饰器工厂）
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}")

# 4. 类作为装饰器
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"调用次数：{self.count}")
        return self.func(*args, **kwargs)

# 5. 多个装饰器叠加（从下往上执行）
@timer
@repeat(3)
def my_func():
    pass

# 6. 带参数类装饰器
class Retry:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(self.max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if i == self.max_retries - 1:
                        raise
        return wrapper

# 7. 内置常用装饰器
@staticmethod       # 静态方法
@classmethod        # 类方法
@property           # 属性方法
@functools.lru_cache(maxsize=None)  # 缓存
@functools.cached_property          # 缓存属性
@dataclasses.dataclass              # 数据类
@contextlib.contextmanager          # 上下文管理器
@functools.singledispatch           # 单分派泛型函数

# 8. functools.singledispatch（根据类型分发）
from functools import singledispatch

@singledispatch
def process(x):
    print(f"默认：{x}")

@process.register
def _(x: int):
    print(f"整数：{x}")

@process.register
def _(x: str):
    print(f"字符串：{x}")

process(1)      # 整数：1
process("a")    # 字符串：a
```

---

# 第三部分：面向对象

## 十七、类与对象（OOP 基础）

```python
class Dog:
    species = "犬科"        # 类属性
    count = 0

    def __init__(self, name, age):
        self.name = name    # 实例属性
        self.age = age
        Dog.count += 1

    def bark(self):
        print(f"{self.name} 在汪汪叫！")

    @classmethod
    def get_count(cls):
        return cls.count

    @staticmethod
    def is_dog(animal):
        return animal.species == "犬科"

my_dog = Dog("旺财", 3)
my_dog.bark()

# 魔术方法
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"Person({self.name}, {self.age})"

    def __repr__(self):
        return f"Person('{self.name}', {self.age})"

    def __eq__(self, other):
        return isinstance(other, Person) and self.name == other.name

    def __lt__(self, other):
        return self.age < other.age

    def __hash__(self):
        return hash((self.name, self.age))

    def __add__(self, other):
        return Person(self.name + other.name, self.age + other.age)

    def __len__(self):
        return len(self.name)

    def __call__(self):
        print(f"调用 {self.name}")

    def __getattr__(self, name):
        return f"属性 {name} 不存在"

    def __setattr__(self, name, value):
        if name == "age" and value < 0:
            raise ValueError("年龄不能为负")
        super().__setattr__(name, value)

    def __bool__(self):
        return self.age > 0

    def __contains__(self, item):
        return item in self.name

    def __iter__(self):
        return iter(self.name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# 继承
class Cat(Dog):
    def __init__(self, name, age, color):
        super().__init__(name, age)
        self.color = color

    def meow(self):
        print(f"{self.name} 喵喵叫")

    def bark(self):
        print(f"{self.name} 不会汪汪叫")

# 多重继承
class Flyable:
    def fly(self): print("飞行")

class Swimmable:
    def swim(self): print("游泳")

class Duck(Flyable, Swimmable):
    pass

# 抽象类
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def make_sound(self): ...
    @abstractmethod
    def move(self): ...

class Bird(Animal):
    def make_sound(self): print("啾啾")
    def move(self): print("飞")

# property
class Student:
    def __init__(self, name, score):
        self._name = name
        self._score = score

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        if not 0 <= value <= 100:
            raise ValueError("分数必须在0-100")
        self._score = value

    @property
    def is_passing(self):
        return self._score >= 60

# 运算符重载
class Vector:
    def __init__(self, x, y):
        self.x = x; self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

# __slots__ 节省内存
class Point:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x; self.y = y

# 私有属性（名称改写，非真正私有）
class Account:
    def __init__(self):
        self.__balance = 0     # 实际为 _Account__balance
        self._internal = 1     # 约定私有

# 单例
class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## 十八、高级 OOP：MRO、描述符、元类

```python
# MRO 方法解析顺序（C3 线性化）
class A: 
    def who(self): print("A")
class B(A): 
    def who(self): print("B")
class C(A): 
    def who(self): print("C")
class D(B, C): pass

D().who()                       # B
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
print(D.mro())                  # 同 __mro__

# super() 本质是按 MRO 找下一个类
class Base:
    def __init__(self):
        print("Base")

class Mixin1(Base):
    def __init__(self):
        super().__init__()
        print("Mixin1")

class Mixin2(Base):
    def __init__(self):
        super().__init__()
        print("Mixin2")

class Child(Mixin1, Mixin2):
    def __init__(self):
        super().__init__()
        print("Child")

Child()
# Base → Mixin2 → Mixin1 → Child

# __new__ vs __init__
# __new__ 创建实例（返回实例），__init__ 初始化实例

class ImmutableStr(str):
    def __new__(cls, value):
        return super().__new__(cls, value)

class Meta(type):
    pass

# 描述符协议
class Descriptor:
    def __get__(self, obj, objtype=None):
        print("get")
        return 42

    def __set__(self, obj, value):
        print("set")
        obj.__dict__["_value"] = value

    def __delete__(self, obj):
        print("delete")

class MyClass:
    attr = Descriptor()

m = MyClass()
print(m.attr)      # get → 42
m.attr = 100       # set

# property 本质就是描述符
class Prop:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.fget(obj)

class Circle:
    def __init__(self, r):
        self.r = r

    @Prop
    def area(self):
        return 3.14 * self.r ** 2

# 元类
class Meta(type):
    def __new__(mcs, name, bases, namespace):
        print(f"创建类 {name}")
        namespace["created_by_meta"] = True
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=Meta):
    pass

print(MyClass.created_by_meta)  # True

# 动态创建类
MyNewClass = type("MyNewClass", (object,), {"x": 1, "y": 2})
obj = MyNewClass()
print(obj.x, obj.y)             # 1 2

# __init_subclass__
class Base:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        print(f"子类 {cls.__name__} 被创建")

class Sub(Base):    # 打印：子类 Sub 被创建
    pass

# 属性查找顺序
# 实例属性 → 类属性 → 父类属性 → __getattr__
```

## 十九、枚举 enum

```python
from enum import Enum, IntEnum, StrEnum, Flag, IntFlag, auto, unique

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

Color.RED.name          # 'RED'
Color.RED.value         # 1
Color(1)                # Color.RED

class Status(Enum):
    PENDING = auto()
    RUNNING = auto()
    DONE = auto()

@unique
class UniqueEnum(Enum):
    A = 1
    B = 2

# IntEnum（可与整数比较）
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

Priority.HIGH > Priority.LOW    # True
Priority.HIGH == 3              # True

# StrEnum（Python 3.11+，可与字符串比较）
class Str(StrEnum):
    A = "a"
    B = "b"

# Flag 位标志
class Perm(Flag):
    R = auto()
    W = auto()
    X = auto()

Perm.R | Perm.W         # Perm.R|W
Perm.R in (Perm.R | Perm.W)  # True

# 遍历
list(Color)              # [Color.RED, Color.GREEN, Color.BLUE]
for c in Color: ...

# 实际应用
class OrderStatus(Enum):
    PENDING = "待支付"
    PAID = "已支付"
    SHIPPED = "已发货"

def display(s: OrderStatus) -> str:
    return s.value
```

## 二十、数据类 dataclass

```python
from dataclasses import dataclass, field, asdict, astuple, replace, InitVar
from datetime import datetime
from typing import List, Optional

# 基础用法
@dataclass
class Person:
    name: str
    age: int
    city: str = "北京"

p1 = Person("小明", 18)
print(p1)   # Person(name='小明', age=18, city='北京')

# 可变默认值
@dataclass
class Student:
    name: str
    scores: List[int] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

# 不可变
@dataclass(frozen=True)
class Point:
    x: int
    y: int

# 字段配置
@dataclass
class Product:
    name: str
    price: float
    _id: int = field(repr=False)
    tags: List[str] = field(default_factory=list, compare=False)
    description: Optional[str] = None

# __post_init__
@dataclass
class User:
    first_name: str
    last_name: str
    full_name: str = field(init=False)

    def __post_init__(self):
        self.full_name = f"{self.first_name} {self.last_name}"

# 继承
@dataclass
class Admin(Person):
    permissions: List[str] = field(default_factory=list)

# 转换
p = Person("小明", 18)
asdict(p)               # {'name': '小明', 'age': 18, 'city': '北京'}
astuple(p)              # ('小明', 18, '北京')

# 复制并修改
p2 = replace(p, age=19)

# 排序
@dataclass(order=True)
class Item:
    sort_index: float = field(init=False, repr=False, compare=False)
    name: str
    price: float

    def __post_init__(self):
        self.sort_index = self.price

# slots=True（Python 3.10+，更省内存）
@dataclass(slots=True)
class Point3D:
    x: int
    y: int
    z: int

# kw_only=True（Python 3.10+，强制关键字传参）
@dataclass(kw_only=True)
class Config:
    host: str
    port: int = 8080

# Pydantic（运行时验证，推荐 v2）
from pydantic import BaseModel, Field, field_validator

class UserModel(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    email: Optional[str] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('名字不能为空')
        return v

user = UserModel(name="小明", age=18)
```

---

# 第四部分：异常与文件

## 二十一、异常处理（try/except）

```python
try:
    num = int(input("请输入数字："))
    result = 10 / num
except ValueError:
    print("请输入有效的数字！")
except ZeroDivisionError:
    print("不能除以零！")
except Exception as e:
    print(f"出错了：{e}")
else:
    print(f"结果：{result}")   # 无异常时执行
finally:
    print("总会执行")

# 主动抛出
raise ValueError("这是一个错误")

# 自定义异常
class MyCustomError(Exception):
    pass

class ValidationError(MyCustomError):
    def __init__(self, field, message):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

# 断言（调试用）
assert x > 0, "x 必须大于 0"

# 异常链
try:
    1 / 0
except ZeroDivisionError as e:
    raise RuntimeError("计算失败") from e

# 抑制异常链
raise RuntimeError("错误") from None

# 捕获多个异常
try:
    risky()
except (ValueError, TypeError) as e:
    print(f"输入错误：{e}")

# ExceptionGroup（Python 3.11+）
try:
    raise ExceptionGroup("多个错误", [
        ValueError("值错误"),
        TypeError("类型错误"),
    ])
except* ValueError as eg:
    print(f"捕获 ValueError 组：{eg.exceptions}")
except* TypeError as eg:
    print(f"捕获 TypeError 组：{eg.exceptions}")

# 异常信息
import traceback
try:
    risky()
except Exception:
    traceback.print_exc()
    # 或
    print(traceback.format_exc())
```

## 二十二、文件操作

```python
# 读文件
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 逐行读取（大文件推荐）
with open("big.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())

# 读所有行
with open("data.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 写文件
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("Hello\n")
    f.writelines(["行1\n", "行2\n"])

# 追加
with open("out.txt", "a", encoding="utf-8") as f:
    f.write("\n追加")

# 二进制
with open("image.jpg", "rb") as f:
    data = f.read()
with open("copy.jpg", "wb") as f:
    f.write(data)

# 文件模式
# 'r' 只读（默认）  'w' 覆盖  'a' 追加  'x' 独占创建
# 'b' 二进制         't' 文本（默认）  '+' 读写

# 文件指针
with open("f.txt", "r") as f:
    f.seek(10)
    f.tell()
    f.read(5)

# pathlib（推荐）
from pathlib import Path

p = Path("folder/sub/file.txt")
p.exists(); p.is_file(); p.is_dir()
p.parent                # folder/sub
p.name                  # file.txt
p.stem                  # file
p.suffix                # .txt
p.with_suffix(".md")    # folder/sub/file.md
p.mkdir(parents=True, exist_ok=True)
p.unlink()
p.rename("new.txt")
list(Path(".").glob("*.py"))
list(Path(".").rglob("*.txt"))

# 读文本/字节（pathlib 便捷方法）
Path("f.txt").read_text(encoding="utf-8")
Path("f.txt").write_text("内容", encoding="utf-8")
Path("f.bin").read_bytes()
Path("f.bin").write_bytes(b"data")

# 临时文件/目录
import tempfile
with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
    f.write("临时内容")
    print(f.name)

with tempfile.TemporaryDirectory() as tmpdir:
    print(tmpdir)

# 内存文件（IO 操作）
from io import StringIO, BytesIO
f = StringIO()
f.write("hello")
f.seek(0)
print(f.read())

bf = BytesIO()
bf.write(b"hello")
bf.seek(0)
print(bf.read())

# 文件锁（Unix）
import fcntl
with open("f.txt", "r") as f:
    fcntl.flock(f, fcntl.LOCK_EX)
```

## 二十三、上下文管理器（with 语句原理）

```python
# 文件操作
with open('file.txt', 'w') as f:
    f.write('hello')

# 类方式
class MyContext:
    def __enter__(self):
        print("进入")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("退出")
        return True    # 返回 True 表示异常已处理

with MyContext() as ctx:
    raise ValueError("异常")

# contextlib 方式
from contextlib import contextmanager

@contextmanager
def my_context():
    print("进入")
    try:
        yield "返回值"
    finally:
        print("退出")

with my_context() as value:
    print(value)

# 计时器
import time
@contextmanager
def timer(name="操作"):
    start = time.time()
    try:
        yield
    finally:
        print(f"{name} 耗时：{time.time()-start:.4f}s")

with timer("计算"):
    sum(i**2 for i in range(1_000_000))

# 多个上下文
with open("in.txt", "r") as fin, open("out.txt", "w") as fout:
    fout.write(fin.read())

# ExitStack
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(f"{i}.txt", "w")) for i in range(5)]

# 忽略特定异常
from contextlib import suppress
with suppress(FileNotFoundError):
    open("不存在的文件").read()

# 重定向 stdout
import sys, io
with contextlib.redirect_stdout(io.StringIO()) as buf:
    print("会被捕获")
print(buf.getvalue())

# 异步上下文管理器
class AsyncContext:
    async def __aenter__(self):
        print("进入")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("退出")

async def use_async_context():
    async with AsyncContext() as ctx:
        print("使用中")
```

---

# 第五部分：模块、包与工程化

## 二十四、模块与包

```python
# 导入整个模块
import random
random.randint(1, 10)

# 导入指定函数
from random import randint

# 别名
import datetime as dt

# 相对导入（包内）
# from . import module1
# from .. import module2

# 包结构
# mypackage/
#   __init__.py
#   module1.py
#   subpackage/
#       __init__.py
#       module3.py

# __init__.py 控制包的导入
# __all__ 控制 from pkg import * 的行为

# if __name__ == "__main__"
if __name__ == "__main__":
    main()

# 模块搜索路径
import sys
sys.path.append("/custom/path")

# 动态导入
import importlib
mod = importlib.import_module("math")
mod.sqrt(16)

# 重新加载
importlib.reload(mod)

# 元数据
__name__; __file__; __doc__; __package__; __all__; __version__
```

## 二十五、pip 包管理 + 虚拟环境

```bash
# 安装
pip install 包名
pip install 包名==1.2.3
pip install 包名>=1.2.0
pip install -r requirements.txt

# 升级/卸载
pip install --upgrade 包名
pip uninstall 包名

# 查看
pip list
pip list --outdated
pip show 包名
pip freeze > requirements.txt

# 镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple 包名
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 虚拟环境
python -m venv myenv
# Windows
myenv\Scripts\activate
# Mac/Linux
source myenv/bin/activate
deactivate
```

## 二十六、工程化：uv / poetry / pyproject.toml

现代 Python 项目推荐使用 **uv**（极快）或 **poetry**。

### 26.1 uv（推荐）

```bash
# 安装
pip install uv
# 或
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建项目
uv init myproject
cd myproject

# 添加依赖
uv add requests
uv add --dev pytest ruff

# 运行
uv run python main.py
uv run pytest

# 同步环境
uv sync

# 锁定依赖
uv lock

# 导出 requirements.txt
uv export --format requirements-txt > requirements.txt
```

### 26.2 poetry

```bash
pip install poetry

poetry new myproject
cd myproject

poetry add requests
poetry add --group dev pytest

poetry shell
poetry run python main.py

poetry build
poetry publish
```

### 26.3 pyproject.toml 示例

```toml
[project]
name = "myproject"
version = "0.1.0"
description = "示例项目"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "you@example.com" }]
dependencies = [
    "requests>=2.31",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "ruff>=0.5",
    "mypy>=1.10",
]

[project.scripts]
myproject = "myproject.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q"
```

### 26.4 推荐项目结构

```
myproject/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── cli.py
│       ├── core.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── conftest.py
└── docs/
```

## 二十七、打包与发布 PyPI

```bash
# 安装构建工具
pip install build twine

# 构建
python -m build
# 生成 dist/myproject-0.1.0.tar.gz 和 dist/myproject-0.1.0-py3-none-any.whl

# 本地测试安装
pip install dist/myproject-0.1.0-py3-none-any.whl

# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 上传到 PyPI
twine upload dist/*

# 使用 .pypirc 配置
# ~/.pypirc
# [pypi]
# username = __token__
# password = pypi-xxxxx
```

版本号规范（语义化版本）：

- `MAJOR.MINOR.PATCH`（如 `1.2.3`）
- MAJOR：不兼容变更
- MINOR：向后兼容的新功能
- PATCH：向后兼容的 bug 修复

---

# 第六部分：标准库与生态

## 二十八、常用内置函数

```python
# 数学
abs(-5); max(1,2,3); min(1,2,3); sum([1,2,3])
round(3.14159, 2); pow(2, 3); divmod(10, 3)

# 序列
len([1,2,3]); sorted([3,1,2]); reversed([1,2,3])
enumerate(['a','b']); zip([1,2], ['a','b']); range(5)

# 类型
type(123); isinstance(123, int)
int("123"); str(123); list("abc"); tuple([1]); dict(); set()
bool(0); float("3.14"); complex(1, 2); bytes("hi", "utf-8")
ord('A'); chr(65); hex(255); bin(255); oct(8)
bytearray(b"hi")

# 输入输出
print("hi"); input("提示："); open("f.txt")

# 内省
help(print); dir(list); globals(); locals(); vars(obj)
id(obj); hash("x"); callable(f); repr(obj)
hasattr(obj, "x"); getattr(obj, "x", None); setattr(obj, "x", 1); delattr(obj, "x")

# 迭代
iter(obj); next(it); map(f, xs); filter(f, xs)
any([True, False]); all([True, True])

# 格式化
format(3.14, ".2f")

# 其他
eval("1+1")             # 危险，慎用
exec("x=1")             # 危险，慎用
compile("1+1", "<s>", "eval")
__import__("math")
```

## 二十九、匿名函数 lambda

```python
square = lambda x: x ** 2
add = lambda a, b: a + b
(lambda x: x ** 2)(5)

# sorted
sorted([-3, 1, -2], key=lambda x: abs(x))
sorted(["apple", "pear"], key=len)

# filter / map / reduce
list(filter(lambda x: x % 2 == 0, [1,2,3,4]))
list(map(lambda x: x ** 2, [1,2,3]))
from functools import reduce
reduce(lambda x, y: x + y, [1,2,3,4])

# 字典排序
students = [("小明", 90), ("小红", 85)]
sorted(students, key=lambda x: x[1], reverse=True)

# 多级排序
sorted(students, key=lambda x: (-x[1], x[0]))
```

## 三十、常用内置模块速查

```python
# random
import random
random.randint(1, 10); random.random(); random.choice([1,2,3])
random.choices([1,2,3], k=2); random.sample([1,2,3,4,5], 2)
random.shuffle(lst); random.seed(42)

# time
import time
time.sleep(2); time.time(); time.perf_counter()
time.strftime("%Y-%m-%d %H:%M:%S")

# datetime
from datetime import datetime, date, time as dtime, timedelta
datetime.now(); date.today()
datetime.strptime("2024-01-01", "%Y-%m-%d")
datetime.now() + timedelta(days=7)

# 时区（Python 3.9+ zoneinfo）
from zoneinfo import ZoneInfo
dt = datetime.now(ZoneInfo("Asia/Shanghai"))

# os
import os
os.getcwd(); os.chdir("/path"); os.listdir(".")
os.mkdir("f"); os.makedirs("a/b/c", exist_ok=True)
os.remove("f.txt"); os.rename("a", "b")
os.environ.get("PATH")

# math
import math
math.sqrt(16); math.pi; math.e
math.ceil(3.2); math.floor(3.9); math.gcd(12, 18); math.factorial(5)

# collections
from collections import Counter, defaultdict, deque, OrderedDict, namedtuple
Counter("hello")
defaultdict(int)
deque([1,2,3])
Point = namedtuple('Point', ['x', 'y'])

# itertools / functools
# 见循环和 lambda 章节

# logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("信息")

# subprocess（避免 shell=True 命令注入）
import subprocess
result = subprocess.run(["ls", "-l"], capture_output=True, text=True)
print(result.stdout)

# 安全执行 shell=True（不要拼接用户输入）
# subprocess.run("ls -l", shell=True)  # 危险

# warnings
import warnings
warnings.warn("这是一个警告", DeprecationWarning)

# inspect
import inspect
inspect.signature(func)
inspect.getsource(func)
inspect.isfunction(func)

# traceback
import traceback
try:
    ...
except Exception:
    traceback.print_exc()

# sys
import sys
sys.argv; sys.path; sys.version; sys.platform; sys.exit(0)
sys.stdout; sys.stderr; sys.stdin
```

## 三十一、标准库补全

```python
# argparse：命令行参数
import argparse
parser = argparse.ArgumentParser(description="示例")
parser.add_argument("name", help="姓名")
parser.add_argument("-a", "--age", type=int, default=18)
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("--mode", choices=["dev", "prod"], default="dev")
args = parser.parse_args()
# 使用：python script.py 小明 --age 20 -v

# csv
import csv
with open("data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])
    writer.writerows([["小明", 18], ["小红", 19]])

with open("data.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["age"])

# sqlite3
import sqlite3
conn = sqlite3.connect("test.db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INT)")
cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("小明", 18))  # 参数化防注入
conn.commit()
cur.execute("SELECT * FROM users WHERE age > ?", (10,))
for row in cur.fetchall():
    print(row)
conn.close()

# 使用上下文管理器自动提交/回滚
with sqlite3.connect("test.db") as conn:
    conn.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("小红", 19))

# pickle（⚠️ 反序列化不可信数据极危险）
import pickle
data = {"a": 1}
with open("data.pkl", "wb") as f:
    pickle.dump(data, f)
with open("data.pkl", "rb") as f:
    loaded = pickle.load(f)

# hashlib
import hashlib
hashlib.md5(b"hello").hexdigest()
hashlib.sha256(b"hello").hexdigest()
# 加盐
salt = b"random_salt"
hashlib.pbkdf2_hmac("sha256", b"password", salt, 100_000)

# hmac
import hmac
hmac.new(b"key", b"msg", hashlib.sha256).hexdigest()

# secrets（安全随机，用于令牌、密码）
import secrets
secrets.token_hex(16)
secrets.token_urlsafe(32)
secrets.randbelow(100)
secrets.choice(["a", "b", "c"])

# uuid
import uuid
uuid.uuid4()             # 随机 UUID
uuid.uuid1()             # 基于时间
str(uuid.uuid4())

# base64
import base64
base64.b64encode(b"hello").decode()
base64.b64decode("aGVsbG8=")

# struct（二进制打包/解包）
import struct
packed = struct.pack("i4s", 42, b"test")
struct.unpack("i4s", packed)

# glob / fnmatch
import glob, fnmatch
glob.glob("*.py")
glob.glob("**/*.py", recursive=True)
fnmatch.fnmatch("file.txt", "*.txt")

# io
from io import StringIO, BytesIO

# socket
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(("example.com", 80))

# urllib
from urllib.request import urlopen
from urllib.parse import urlencode, quote, unquote

# configparser
import configparser
cfg = configparser.ConfigParser()
cfg.read("config.ini")
cfg["DEFAULT"]["key"]

# tomllib（Python 3.11+）
import tomllib
with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

# zipfile / tarfile / gzip
import zipfile, tarfile, gzip
with zipfile.ZipFile("a.zip", "w") as z:
    z.write("f.txt")
with zipfile.ZipFile("a.zip", "r") as z:
    z.extractall("out/")

with gzip.open("f.gz", "wt", encoding="utf-8") as f:
    f.write("hello")

# platform
import platform
platform.system(); platform.python_version(); platform.machine()
```

## 三十二、序列化与配置

```python
# JSON
import json
json.dumps({"a": 1}, ensure_ascii=False, indent=2)
json.loads('{"a": 1}')
with open("d.json", "w", encoding="utf-8") as f:
    json.dump({"a": 1}, f, ensure_ascii=False, indent=2)
with open("d.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 自定义对象序列化
from dataclasses import asdict
class User:
    def __init__(self, name): self.name = name
json.dumps(User("小明").__dict__)

# CSV（见标准库补全）

# YAML（第三方）
# pip install pyyaml
import yaml
yaml.safe_load("a: 1\nb: 2")
yaml.safe_dump({"a": 1}, allow_unicode=True)

# TOML
# 读取：tomllib（3.11+ 内置）
# 写入：tomli-w（第三方）
# pip install tomli-w
import tomli_w
tomli_w.dumps({"a": 1})

# configparser
import configparser
cfg = configparser.ConfigParser()
cfg["DEFAULT"] = {"host": "localhost", "port": "8080"}
cfg["dev"] = {"host": "dev.local"}
with open("config.ini", "w") as f:
    cfg.write(f)

# dotenv（第三方）
# pip install python-dotenv
from dotenv import load_dotenv
import os
load_dotenv()
os.environ.get("API_KEY")

# 环境变量（内置）
import os
os.environ["MY_VAR"] = "value"
os.getenv("MY_VAR", "default")
```

## 三十三、网络请求

```python
# requests（同步，最常用）
# pip install requests
import requests

resp = requests.get("https://api.example.com/users", timeout=10)
resp.status_code
resp.json()
resp.text
resp.headers

# POST
resp = requests.post(
    "https://api.example.com/users",
    json={"name": "小明"},
    headers={"Authorization": "Bearer token"},
    timeout=10,
)

# 会话（保持 cookie）
with requests.Session() as s:
    s.headers.update({"User-Agent": "myapp"})
    s.get("https://example.com")

# 重试
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

# 代理
requests.get("https://example.com", proxies={"https": "http://proxy:8080"})

# 流式下载
with requests.get("https://example.com/big.zip", stream=True) as r:
    for chunk in r.iter_content(chunk_size=8192):
        ...

# httpx（支持同步/异步）
# pip install httpx
import httpx

with httpx.Client(timeout=10) as client:
    r = client.get("https://example.com")
    r.json()

async with httpx.AsyncClient() as client:
    r = await client.get("https://example.com")

# aiohttp（纯异步）
# pip install aiohttp
import aiohttp
async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()

# urllib（标准库）
from urllib.request import urlopen, Request
from urllib.parse import urlencode

with urlopen("https://example.com", timeout=10) as resp:
    body = resp.read().decode("utf-8")

params = urlencode({"q": "python"})
req = Request(f"https://api.example.com/search?{params}")
```

## 三十四、数据库

```python
# SQLite（内置）
import sqlite3

conn = sqlite3.connect("app.db")
conn.row_factory = sqlite3.Row   # 行可当字典访问
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER
    )
""")

# 参数化查询（防 SQL 注入）
cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", ("小明", 18))
conn.commit()

cur.execute("SELECT * FROM users WHERE age > ?", (10,))
for row in cur.fetchall():
    print(row["id"], row["name"], row["age"])

# 事务
try:
    with conn:  # 自动 commit / rollback
        conn.execute("UPDATE users SET age = age + 1 WHERE name = ?", ("小明",))
except sqlite3.Error as e:
    print(e)

conn.close()

# SQLAlchemy（ORM）
# pip install sqlalchemy
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)

engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)

with Session(engine) as session:
    user = User(name="小明", age=18)
    session.add(user)
    session.commit()
    users = session.query(User).filter(User.age > 10).all()

# Redis / MongoDB / PostgreSQL 等：
# pip install redis pymongo psycopg[binary] asyncpg
```

## 三十五、安全与危险函数

```python
# ⚠️ eval / exec 危险（可执行任意代码）
eval("1 + 1")            # 慎用，绝不用于处理用户输入
exec("x = 1")            # 慎用

# 安全替代：使用 ast.literal_eval 解析字面量
import ast
ast.literal_eval("[1, 2, 3]")        # 安全
ast.literal_eval("{'a': 1}")         # 安全
# ast.literal_eval("__import__('os').system('rm -rf /')")  # 抛异常

# ⚠️ pickle 反序列化不可信数据 = 任意代码执行
# 永远不要 pickle.load 来自不可信来源的数据
# 使用 json / msgpack / pydantic 替代

# ⚠️ subprocess shell=True 命令注入
# 危险
# subprocess.run(f"ls {user_input}", shell=True)

# 安全：使用列表参数，不使用 shell=True
import subprocess
subprocess.run(["ls", user_input], check=True)

# ⚠️ SQL 注入
# 危险
# cur.execute(f"SELECT * FROM users WHERE name = '{name}'")
# 安全：参数化
cur.execute("SELECT * FROM users WHERE name = ?", (name,))

# ⚠️ 路径穿越
from pathlib import Path
def safe_join(base: Path, user_path: str) -> Path:
    target = (base / user_path).resolve()
    if not target.is_relative_to(base.resolve()):
        raise ValueError("非法路径")
    return target

# ⚠️ random 不适用于安全场景
import random, secrets
random.random()          # ❌ 密码、令牌
secrets.token_hex(32)    # ✅ 安全随机

# 密码哈希（推荐 bcrypt / argon2）
# pip install bcrypt
import bcrypt
hashed = bcrypt.hashpw(b"password", bcrypt.gensalt())
bcrypt.checkpw(b"password", hashed)

# 或 argon2-cffi
# pip install argon2-cffi
from argon2 import PasswordHasher
ph = PasswordHasher()
hash_ = ph.hash("password")
ph.verify(hash_, "password")

# 敏感信息不要硬编码
# ❌ API_KEY = "sk-xxxx"
# ✅ 从环境变量读取
import os
api_key = os.environ["API_KEY"]

# YAML 不安全加载
# yaml.load(data)              # ❌ 危险
yaml.safe_load(data)           # ✅ 安全
```

---

# 第七部分：并发与异步

## 三十六、多线程 threading

```python
import threading
import time

def worker(name, delay):
    for i in range(3):
        print(f"{name}: 第{i+1}次")
        time.sleep(delay)

t1 = threading.Thread(target=worker, args=("线程A", 0.5))
t2 = threading.Thread(target=worker, args=("线程B", 0.8))
t1.start(); t2.start()
t1.join(); t2.join()

# 加锁
counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100_000):
        with lock:
            counter += 1

# RLock（可重入）
rlock = threading.RLock()

# 死锁示例（避免）
def deadlock(a, b):
    with a:
        time.sleep(0.1)
        with b:
            pass

# 线程池
from concurrent.futures import ThreadPoolExecutor

def square(n): return n * n

with ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(square, range(10)))
    future = ex.submit(square, 5)
    print(future.result())

# 队列（线程安全）
from queue import Queue
q = Queue()
q.put(1); q.put(2)
q.get(); q.get(timeout=1)

# Event / Semaphore / Barrier
event = threading.Event()
sem = threading.Semaphore(3)
barrier = threading.Barrier(3)

# ThreadPoolExecutor vs Thread
# 优先使用 ThreadPoolExecutor（更高层抽象）
```

## 三十七、多进程 multiprocessing（绕过 GIL）

```python
import multiprocessing as mp

def cpu_bound(n):
    return sum(i ** 2 for i in range(n))

if __name__ == "__main__":    # Windows 必须
    # 进程池
    with mp.Pool(processes=4) as pool:
        results = pool.map(cpu_bound, [1_000_000] * 4)
        print(results)

    # apply_async
    with mp.Pool(4) as pool:
        async_results = [pool.apply_async(cpu_bound, (1_000_000,)) for _ in range(4)]
        results = [r.get() for r in async_results]

    # 共享内存
    shared_value = mp.Value('i', 0)
    shared_array = mp.Array('d', [0.0, 0.0, 0.0])

    # 队列 / 管道
    q = mp.Queue()
    q.put("数据")
    print(q.get())

    parent_conn, child_conn = mp.Pipe()
    child_conn.send("hello")
    print(parent_conn.recv())

    # Manager（更高级共享对象）
    with mp.Manager() as manager:
        shared_list = manager.list([1, 2, 3])
        shared_dict = manager.dict()

# concurrent.futures.ProcessPoolExecutor（推荐）
from concurrent.futures import ProcessPoolExecutor

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(cpu_bound, [1_000_000] * 4))
```

## 三十八、异步 asyncio（async/await）

```python
import asyncio

# 基础
async def say_hello():
    print("开始")
    await asyncio.sleep(1)
    print("结束")
    return "Hello"

async def main():
    result = await say_hello()
    print(result)

asyncio.run(main())

# 并发执行
async def fetch(id, delay):
    await asyncio.sleep(delay)
    return f"数据{id}"

async def concurrent():
    results = await asyncio.gather(
        fetch(1, 2), fetch(2, 1), fetch(3, 3)
    )
    print(results)

# 超时
async def timeout_demo():
    try:
        await asyncio.wait_for(slow(), timeout=2)
    except asyncio.TimeoutError:
        print("超时")

# TaskGroup（Python 3.11+）
async def task_group_demo():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch(1, 2))
        t2 = tg.create_task(fetch(2, 1))
    print(t1.result(), t2.result())

# 异步上下文管理器
class AsyncCtx:
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass

# 异步迭代器
class AsyncCounter:
    def __init__(self, n): self.n = n; self.i = 0
    def __aiter__(self): return self
    async def __anext__(self):
        if self.i >= self.n: raise StopAsyncIteration
        await asyncio.sleep(0.1)
        self.i += 1
        return self.i

async def use_async_iter():
    async for i in AsyncCounter(3):
        print(i)

# 异步队列
async def queue_demo():
    q = asyncio.Queue()
    await q.put("数据")
    print(await q.get())

# 信号量
async def sem_demo():
    sem = asyncio.Semaphore(3)
    async def task(i):
        async with sem:
            await asyncio.sleep(1)
    await asyncio.gather(*[task(i) for i in range(10)])

# 同步代码中调用异步
def sync_call():
    return asyncio.run(main())

# 异步中调用同步（线程池）
async def call_sync():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, time.sleep, 1)
```

## 三十九、异步进阶

```python
import asyncio

# 事件循环（低层 API，通常不需要直接用）
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(main())
finally:
    loop.close()

# 获取当前循环
asyncio.get_running_loop()    # 在协程内
asyncio.get_event_loop()      # 已弃用，慎用

# create_task（立即调度）
async def demo():
    task = asyncio.create_task(fetch(1, 1))
    await asyncio.sleep(0.5)
    result = await task

# wait（等待多个任务，返回 (done, pending)）
async def wait_demo():
    tasks = [asyncio.create_task(fetch(i, 1)) for i in range(3)]
    done, pending = await asyncio.wait(tasks, timeout=5)

# as_completed（按完成顺序返回）
async def as_completed_demo():
    tasks = [asyncio.create_task(fetch(i, i)) for i in range(1, 4)]
    for coro in asyncio.as_completed(tasks):
        print(await coro)

# shield（保护任务不被取消）
async def shield_demo():
    task = asyncio.create_task(fetch(1, 5))
    try:
        await asyncio.wait_for(asyncio.shield(task), timeout=1)
    except asyncio.TimeoutError:
        print("超时，但任务继续")
    print(await task)

# 取消
async def cancel_demo():
    task = asyncio.create_task(fetch(1, 10))
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("任务被取消")

# 异步锁
lock = asyncio.Lock()
async def with_lock():
    async with lock:
        ...

# 异步事件
event = asyncio.Event()
await event.wait()
event.set()

# 异步条件变量
cond = asyncio.Condition()

# 异步生成器
async def async_gen():
    for i in range(3):
        await asyncio.sleep(0.1)
        yield i

async def consume():
    async for x in async_gen():
        print(x)

# 异步推导式（Python 3.6+）
async def async_comp():
    result = [x async for x in async_gen()]
    result = {x async for x in async_gen()}

# anyio / trio（更现代的异步框架）
# pip install anyio
import anyio
async def anyio_demo():
    async with anyio.create_task_group() as tg:
        tg.start_soon(fetch, 1, 1)
        tg.start_soon(fetch, 2, 1)

# uvloop（加速事件循环）
# pip install uvloop
# import uvloop
# uvloop.install()
# asyncio.run(main())

# ExceptionGroup（Python 3.11+）
async def eg_demo():
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(fetch(1, 1))
            tg.create_task(raises())
    except* ValueError as eg:
        print(eg.exceptions)
```

## 四十、并发模型选择

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| CPU 密集型 | 多进程 / ProcessPoolExecutor | 绕过 GIL |
| CPU 密集型（可用 numpy/numba） | 向量化 | 避免 Python 循环 |
| I/O 密集型（阻塞库） | 多线程 / ThreadPoolExecutor | 等待 I/O 时释放 GIL |
| I/O 密集型（异步库） | asyncio | 单线程高并发 |
| 高并发网络服务 | asyncio + aiohttp / httpx / FastAPI | 事件驱动 |
| 简单并行任务 | concurrent.futures | 高层抽象 |
| 大量小任务 | asyncio.gather | 调度开销小 |
| 需要共享状态 | 多线程 + Lock | 共享内存 |
| 需隔离 | 多进程 | 独立内存空间 |

GIL（全局解释器锁）：

- CPython 中同一时刻只有一个线程执行 Python 字节码
- 多线程适合 I/O 密集（I/O 期间释放 GIL）
- 多进程可绕过 GIL
- Python 3.13 起有实验性 free-threaded 版本（无 GIL）

---

# 第八部分：类型系统

## 四十一、类型注解 Type Hints

```python
from typing import (
    List, Dict, Tuple, Optional, Union, Any, Callable,
    Iterable, Iterator, Generator, TypeVar, Generic,
    NewType, Literal, TypedDict, Protocol, Final, ClassVar,
)

# 基础
name: str = "小明"
scores: List[int] = [90, 85]
person: Dict[str, str] = {"name": "小明"}
point: Tuple[int, int] = (10, 20)
mixed: Union[int, str] = 42
nullable: Optional[str] = None

# 现代写法（Python 3.9+）
scores: list[int] = [90]
person: dict[str, str] = {}
point: tuple[int, int] = (1, 2)
mixed: int | str = 42
nullable: str | None = None

# 函数注解
def add(a: int, b: int) -> int:
    return a + b

def log(msg: str) -> None:
    print(msg)

def sum_all(*args: int) -> int:
    return sum(args)

def print_info(**kwargs: str) -> None:
    ...

# 可调用
def apply(func: Callable[[int, int], int], x: int, y: int) -> int:
    return func(x, y)

# 迭代器 / 生成器
def count_up(n: int) -> Iterator[int]:
    yield from range(n)

def gen() -> Generator[int, None, str]:
    yield 1
    return "done"

# 类型别名
UserId = int
UserInfo = tuple[UserId, str]

# 泛型
T = TypeVar('T')
def first(items: list[T]) -> T:
    return items[0]

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
    def push(self, item: T) -> None:
        self._items.append(item)
    def pop(self) -> T:
        return self._items.pop()

# NewType
UserId = NewType('UserId', int)

# Literal
def set_mode(mode: Literal['read', 'write', 'append']) -> None:
    ...

# TypedDict
class UserDict(TypedDict):
    name: str
    age: int
    email: str | None

# Protocol（结构化子类型）
class SupportsStr(Protocol):
    def __str__(self) -> str: ...

def stringify(obj: SupportsStr) -> str:
    return str(obj)

# Final / ClassVar
MAX_SIZE: Final = 100

class C:
    count: ClassVar[int] = 0

# Self（Python 3.11+）
from typing import Self

class Builder:
    def set_x(self, x: int) -> Self:
        self.x = x
        return self
```

## 四十二、类型注解进阶

```python
from typing import (
    overload, TypeVar, ParamSpec, Concatenate,
    TypeAlias, TYPE_CHECKING, Self, Never,
    Required, NotRequired, Unpack,
)

# overload（重载声明，运行时仍需单一实现）
from typing import overload

@overload
def process(x: int) -> int: ...
@overload
def process(x: str) -> str: ...
def process(x):
    return x

# ParamSpec（保留参数签名）
P = ParamSpec("P")
R = TypeVar("R")

def logged(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

# Concatenate（在前面追加参数）
from typing import Concatenate

def with_retry(func: Callable[Concatenate[int, P], R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        for _ in range(3):
            try:
                return func(3, *args, **kwargs)
            except Exception:
                pass
        raise
    return wrapper

# TypeAlias
StrOrInt: TypeAlias = str | int

# TYPE_CHECKING（避免循环导入）
if TYPE_CHECKING:
    from mymodule import MyClass

def f(x: "MyClass") -> None: ...

# Self（3.11+）
from typing import Self
class Builder:
    def set(self, v: int) -> Self:
        self.v = v
        return self

# Never
from typing import Never
def fail() -> Never:
    raise RuntimeError

# Required / NotRequired（TypedDict 可选键）
class User(TypedDict):
    name: str
    age: Required[int]
    email: NotRequired[str]

# Unpack（**kwargs 类型）
class Config(TypedDict):
    host: str
    port: int

def setup(**kwargs: Unpack[Config]) -> None: ...

# Python 3.12 新 type 语句
# type Point = tuple[float, float]
# type StrOrInt = str | int

# 运行时检查（Python 3.10+ 无内置 typeguard，可用 beartype）
# pip install beartype
# from beartype import beartype
# @beartype
# def f(x: int) -> int: return x

# mypy 使用
# pip install mypy
# mypy script.py
# mypy --strict script.py

# pyright
# npm install -g pyright
# pyright script.py

# py.typed 标记（让包被 mypy 检查）
# 在包根目录添加空文件 py.typed

# 常见 mypy 配置（pyproject.toml）
# [tool.mypy]
# python_version = "3.10"
# strict = true
# warn_unused_ignores = true
# disallow_untyped_defs = true
```

---

# 第九部分：测试与质量

## 四十三、测试：unittest、pytest、mock、coverage

```python
# unittest（标准库）
import unittest

class TestMath(unittest.TestCase):
    def setUp(self):
        self.data = [1, 2, 3]

    def tearDown(self):
        pass

    def test_sum(self):
        self.assertEqual(sum(self.data), 6)

    def test_empty(self):
        self.assertRaises(ValueError, lambda: int("abc"))

    def test_in(self):
        self.assertIn(1, self.data)

if __name__ == "__main__":
    unittest.main()
```

```python
# pytest（推荐）
# pip install pytest

# test_math.py
def test_sum():
    assert sum([1, 2, 3]) == 6

def test_empty():
    with pytest.raises(ValueError):
        int("abc")

# fixture
import pytest

@pytest.fixture
def sample_data():
    return [1, 2, 3]

def test_with_fixture(sample_data):
    assert sum(sample_data) == 6

# fixture 作用域
@pytest.fixture(scope="module")
def db():
    conn = create_conn()
    yield conn
    conn.close()

# 参数化
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert a + b == expected

# 标记
@pytest.mark.slow
def test_slow():
    ...

@pytest.mark.skip(reason="未实现")
def test_todo():
    ...

@pytest.mark.xfail
def test_expected_fail():
    assert False

# 临时目录
def test_write(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    assert f.read_text() == "hello"

# 捕获输出
def test_output(capsys):
    print("hello")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"

# monkeypatch
def test_monkey(monkeypatch):
    monkeypatch.setenv("API_KEY", "test")
    monkeypatch.setattr("os.getcwd", lambda: "/fake")

# conftest.py（共享 fixture）
# tests/conftest.py
# 放在 tests 目录下，自动被所有测试发现

# 运行
# pytest
# pytest -v
# pytest -k "test_sum"
# pytest -m "not slow"
# pytest --cov=myproject  （需 pytest-cov）
```

```python
# mock（模拟对象）
from unittest.mock import Mock, MagicMock, patch, AsyncMock

# 基础 Mock
m = Mock()
m.method(1, 2)
m.method.assert_called_once_with(1, 2)
m.method.return_value = 42
assert m.method() == 42

# patch 装饰器
@patch("mymodule.requests.get")
def test_fetch(mock_get):
    mock_get.return_value.json.return_value = {"a": 1}
    from mymodule import fetch
    assert fetch() == {"a": 1}

# patch 上下文
with patch("mymodule.open") as mock_open:
    mock_open.return_value.read.return_value = "data"
    ...

# 异步 Mock
am = AsyncMock()
await am()

# side_effect
m = Mock(side_effect=[1, 2, 3])
m(); m(); m()   # 1, 2, 3

m = Mock(side_effect=ValueError("boom"))
m()             # 抛异常

# coverage
# pip install coverage pytest-cov
# coverage run -m pytest
# coverage report
# coverage html
# pytest --cov=myproject --cov-report=html

# 测试金字塔
#         /\
#        /E2E\        少量
#       /-----\
#      /集成测试\      适量
#     /---------\
#    /  单元测试  \    大量
#   /-------------\
```

## 四十四、代码质量工具：ruff、black、isort、mypy、pre-commit

```bash
# ruff（现代，极快，替代 flake8 + isort + 部分 black 功能）
pip install ruff

ruff check .              # 检查
ruff check --fix .        # 自动修复
ruff format .             # 格式化

# 配置（pyproject.toml）
# [tool.ruff]
# line-length = 100
# target-version = "py310"
#
# [tool.ruff.lint]
# select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
# ignore = ["E501"]

# black（格式化）
pip install black
black .
black --check .

# isort（导入排序）
pip install isort
isort .
isort --check-only .

# mypy（静态类型检查）
pip install mypy
mypy .
mypy --strict .

# pyright（更快的类型检查）
npm install -g pyright
pyright

# pre-commit（提交前自动检查）
pip install pre-commit

# .pre-commit-config.yaml
# repos:
#   - repo: https://github.com/astral-sh/ruff-pre-commit
#     rev: v0.5.0
#     hooks:
#       - id: ruff
#         args: [--fix]
#       - id: ruff-format
#   - repo: https://github.com/pre-commit/mirrors-mypy
#     rev: v1.10.0
#     hooks:
#       - id: mypy

pre-commit install
pre-commit run --all-files

# CI 示例（GitHub Actions）
# .github/workflows/ci.yml
# name: CI
# on: [push, pull_request]
# jobs:
#   test:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - uses: actions/setup-python@v5
#         with:
#           python-version: "3.11"
#       - run: pip install -e ".[dev]"
#       - run: ruff check .
#       - run: mypy .
#       - run: pytest --cov=myproject
```

---

# 第十部分：性能与调试

## 四十五、性能优化技巧

```python
# 1. 用 join 而不是 + 拼接字符串
s = "".join(str(i) for i in range(1000))

# 2. 列表推导式代替 for 循环
squares = [i**2 for i in range(1000)]

# 3. 生成器代替列表（大数量时）
sum(i**2 for i in range(10_000_000))

# 4. set/dict 成员检查 O(1)
if x in {1, 2, 3}: ...

# 5. 局部变量加速
def fast():
    sqrt = math.sqrt
    return [sqrt(i) for i in range(1000)]

# 6. lru_cache 缓存
from functools import lru_cache

@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)

# 7. array 模块
from array import array
numbers = array('i', [1, 2, 3])

# 8. __slots__ 节省内存
class Point:
    __slots__ = ('x', 'y')

# 9. functools.partial
from functools import partial
square = partial(pow, exp=2)    # 错误示例，pow 无 exp 参数
square = partial(pow, 2)

# 10. 内置函数
sum(lst); max(lst); min(lst); any(lst); all(lst)

# 11. 集合运算
result = list(set(a) & set(b))

# 12. deque 做队列
from collections import deque
dq = deque()
dq.appendleft(1)
dq.popleft()

# 13. numpy 向量化（大数量数值计算）
# pip install numpy
import numpy as np
arr = np.arange(1_000_000)
result = arr ** 2 + 1     # 远快于 Python 循环

# 14. numba JIT
# pip install numba
from numba import jit

@jit(nopython=True)
def fast_sum(n):
    total = 0
    for i in range(n):
        total += i
    return total

# 15. Cython
# pip install cython
# 编译 .pyx 文件为 C 扩展

# 16. multiprocessing 并行 CPU 任务
from concurrent.futures import ProcessPoolExecutor

# 17. 避免重复属性查找
# 慢
for i in range(10_000_000):
    self.value += 1
# 快
v = self.value
for i in range(10_000_000):
    v += 1
self.value = v

# 18. 减少函数调用开销
# 内联热点函数、使用内置函数

# 19. 懒加载
def lazy_property(fn):
    name = "_lazy_" + fn.__name__
    @property
    def wrapper(self):
        if not hasattr(self, name):
            setattr(self, name, fn(self))
        return getattr(self, name)
    return wrapper

# 20. 使用 __slots__ + dataclass(slots=True)
```

## 四十六、性能分析工具

```python
# cProfile（内置）
import cProfile
cProfile.run("my_function()")
# 命令行
# python -m cProfile -s cumulative script.py

# profile 装饰器
import cProfile, pstats, io
pr = cProfile.Profile()
pr.enable()
my_function()
pr.disable()
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
ps.print_stats(20)
print(s.getvalue())

# timeit
import timeit
timeit.timeit("sum(range(1000))", number=10_000)

# 在脚本中计时
t = timeit.timeit(lambda: my_func(), number=1000)

# tracemalloc（内存追踪）
import tracemalloc
tracemalloc.start()
my_function()
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics("lineno")[:10]:
    print(stat)
tracemalloc.stop()

# memory_profiler
# pip install memory_profiler
# from memory_profiler import profile
# @profile
# def f(): ...

# line_profiler（逐行分析）
# pip install line_profiler
# @profile 装饰器 + kernprof -l -v script.py

# py-spy（采样分析器，不需要改代码）
# pip install py-spy
# py-spy top -- python script.py
# py-spy record -o profile.svg -- python script.py

# scalene（CPU + 内存 + GPU 分析）
# pip install scalene
# scalene script.py

# 性能分析建议
# 1. 先测量再优化（不要凭直觉）
# 2. 找到瓶颈（80/20 法则）
# 3. 优先算法优化，再微观优化
# 4. 用实际数据规模测试
```

---

# 第十一部分：其他

## 四十七、深拷贝 vs 浅拷贝

```python
import copy

# 浅拷贝：只拷贝第一层
original = [[1, 2], [3, 4]]
shallow = copy.copy(original)
shallow[0][0] = 99
print(original)     # [[99, 2], [3, 4]]

# 深拷贝：递归独立
original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)
deep[0][0] = 99
print(original)     # [[1, 2], [3, 4]]

# 切片、dict.copy()、list() 都是浅拷贝
lst = [1, 2, [3, 4]]
lst2 = lst[:]
lst2[2][0] = 99
print(lst)          # [1, 2, [99, 4]]

# 自定义 __deepcopy__
class MyClass:
    def __init__(self, data):
        self.data = data

    def __deepcopy__(self, memo):
        return MyClass(copy.deepcopy(self.data, memo))
```

## 四十八、正则表达式 re（详细）

```python
import re

text = "我的电话是13812345678，邮箱是test@example.com"

# search / findall / finditer
m = re.search(r'\d{11}', text)
m.group(); m.start(); m.end(); m.span()

re.findall(r'\d{11}', text)
for m in re.finditer(r'\d{11}', text):
    print(m.group())

# 分组
pattern = r'姓名：(\w+)，年龄：(\d+)'
m = re.search(pattern, "姓名：小明，年龄：18")
m.group(1); m.groups()

# 命名分组
pattern = r'姓名：(?P<name>\w+)'
m.group('name')

# 替换
re.sub(r'apple', 'orange', 'apple banana')

# 替换函数
def double(match):
    return str(int(match.group()) * 2)
re.sub(r'\d+', double, '1 2 3')

# 反向引用
re.sub(r'(\d+)-(\d+)-(\d+)', r'\3-\2-\1', '2024-01-15')

# 分割
re.split(r'[,; ]+', 'a,b;c d')

# 编译
pattern = re.compile(r'\d{11}')

# 标志
re.IGNORECASE      # re.I
re.MULTILINE       # re.M
re.DOTALL          # re.S
re.VERBOSE         # re.X

# 贪婪 vs 非贪婪
text = "<div>内容1</div><div>内容2</div>"
re.findall(r'<div>.*</div>', text)     # 贪婪
re.findall(r'<div>.*?</div>', text)    # 非贪婪

# 前瞻 / 后顾
text = "abc123def456"
re.findall(r'(?<=abc)\d+', text)       # ['123']
re.findall(r'\d+(?=def)', text)        # ['123']
# ⚠️ 否定前瞻位置敏感，容易回溯
# re.findall(r'\d+(?!def)', text)      # 结果可能是 ['12', '456']，不是 ['456']

# 更稳健的写法
re.findall(r'\d+(?=\D|$)', text)       # 后面是非数字或结尾

# 常用正则
# 手机号：r'1[3-9]\d{9}'
# 邮箱：r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
# 身份证：r'\d{17}[\dXx]'
# IP：r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
# 中文：r'[\u4e00-\u9fff]+'
# URL：r'https?://[^\s]+'
# 日期：r'\d{4}-\d{2}-\d{2}'
# HTML 标签：r'<[^>]+>'
```

## 四十九、Python 版本与新特性

```python
# Python 3.6
# - f-string
# - 数字下划线：1_000_000
# - 变量注解：x: int = 1
# - dict 保持插入顺序（实现细节）

# Python 3.7
# - dataclasses
# - dict 顺序保证（语言规范）
# - async/await 成为关键字
# - breakpoint()

# Python 3.8
# - 海象运算符 :=
# - 仅位置参数 /
# - f-string 支持 =
# - typing.Protocol
# - math.prod

# Python 3.9
# - dict 合并 | 和 |=
# - 内置泛型 list[int]、dict[str, int]
# - str.removeprefix() / removesuffix()
# - zoneinfo

# Python 3.10
# - match-case
# - 联合类型 X | Y
# - dataclass(slots=True, kw_only=True)
# - zip(strict=True)
# - 更好的错误消息

# Python 3.11
# - ExceptionGroup / except*
# - asyncio.TaskGroup
# - tomllib
# - StrEnum
# - typing.Self、LiteralString、Never、Required、NotRequired
# - 显著性能提升（10%-60%）
# - 更精确的错误定位

# Python 3.12
# - type 语句（类型别名）
# - 泛型新语法 class Stack[T]
# - f-string 改进（嵌套引号、多行）
# - 每个解释器独立 GIL（实验性）
# - pathlib 增强

# Python 3.13
# - 实验性 free-threaded 构建（无 GIL）
# - 实验性 JIT
# - 更好的 REPL
# - typing 增强

# Python 3.14
# - 延迟注解求值（PEP 649）
# - 模板字符串 t-string（PEP 750）
# - 多解释器（PEP 734）
```

## 五十、常见 Python 陷阱与坑

```python
# 1. 默认参数陷阱
def bad(lst=[]):
    lst.append(1)
    return lst

# 2. 浮点精度
0.1 + 0.2                       # 0.30000000000000004
from decimal import Decimal
Decimal('0.1') + Decimal('0.2') # 0.3

# 3. 循环中修改列表
# ❌
for x in lst:
    if x % 2 == 0:
        lst.remove(x)
# ✅
lst = [x for x in lst if x % 2 != 0]

# 4. is vs ==
a = 257; b = 257
a is b      # 不确定（不要依赖）
a == b      # True
# 值比较用 ==，is 只用于 None / True / False

# 5. 闭包延迟绑定
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]            # [2, 2, 2]
funcs = [lambda i=i: i for i in range(3)]
[f() for f in funcs]            # [0, 1, 2]

# 6. 类属性可变对象
class Dog:
    tricks = []                 # 所有实例共享
# ✅
class Dog:
    def __init__(self):
        self.tricks = []

# 7. 浅拷贝陷阱
original = [[1, 2]]
shallow = original.copy()
shallow[0][0] = 99
print(original)                 # [[99, 2]]

# 8. 异常捕获过宽
try:
    ...
except:                          # ❌ 连 KeyboardInterrupt 都吞
    pass
try:
    ...
except Exception:                # ✅
    pass

# 9. None 比较
if x is None: ...                # ✅
if x == None: ...                # ❌

# 10. 字符串拼接性能
# ❌
s = ""
for i in range(10000):
    s += str(i)
# ✅
s = "".join(str(i) for i in range(10000))

# 11. 字典迭代时修改
for k in list(d.keys()):
    if k == 'b':
        del d[k]

# 12. 字符串驻留
a = "hello"
b = "hello"
a is b                          # 可能 True，不要依赖

# 13. 参数顺序陷阱
def f(a, b=1, *args, **kwargs): ...

# 14. 列表乘法陷阱
lst = [[]] * 3                  # ❌ 三个引用同一列表
lst[0].append(1)
print(lst)                      # [[1], [1], [1]]
# ✅
lst = [[] for _ in range(3)]

# 15. 整数除法
5 / 2                           # 2.5
5 // 2                          # 2
-5 // 2                         # -3（向下取整）

# 16. 变量作用域
x = 10
def f():
    print(x)                    # 读全局 OK
    x = 20                      # ❌ UnboundLocalError
# 需要 global x 或改参数名

# 17. try/except 中 return 与 finally
def f():
    try:
        return 1
    finally:
        return 2                # 覆盖 try 的 return
f()                             # 2

# 18. 类方法中的 self 拼写错误
class A:
    def method(sefl):           # ❌ 拼写错误，调用时才报错
        pass

# 19. 字符串 in 性能
'a' in 'abc'                    # O(n)
'a' in {'a', 'b'}               # O(1)

# 20. 迭代器只能消费一次
it = iter([1, 2, 3])
list(it)                        # [1, 2, 3]
list(it)                        # []
```

## 五十一、常见错误与解决办法

| 错误 | 说明 | 解决办法 |
|------|------|---------|
| `SyntaxError` | 语法错误 | 检查括号、冒号、缩进 |
| `IndentationError` | 缩进错误 | 统一 Tab/空格，4 空格缩进 |
| `NameError` | 变量未定义 | 检查拼写与作用域 |
| `TypeError` | 类型错误 | 检查操作数类型 |
| `ValueError` | 值错误 | 检查值格式 |
| `IndexError` | 索引越界 | 检查 `0 <= i < len` |
| `KeyError` | 字典键不存在 | 用 `dict.get()` |
| `AttributeError` | 属性不存在 | `hasattr()` / `getattr()` |
| `ZeroDivisionError` | 除以零 | 检查除数 |
| `FileNotFoundError` | 文件不存在 | 检查路径 / `Path.exists()` |
| `ImportError` / `ModuleNotFoundError` | 导入失败 | 检查安装 / 路径 |
| `StopIteration` | 迭代结束 | 检查迭代器 |
| `MemoryError` | 内存不足 | 用生成器、分批处理 |
| `RecursionError` | 递归过深 | 加终止条件 / 改迭代 |
| `UnboundLocalError` | 局部变量未赋值 | 用 `global` / `nonlocal` |
| `RuntimeError` | 运行时错误 | 查看具体信息 |
| `TimeoutError` | 超时 | 增大超时 / 检查网络 |
| `PermissionError` | 权限不足 | 检查文件权限 |

### 调试方法

```python
# print / f-string 调试
print(f"{x=}, {y=}")

# assert
assert x > 0, "x 必须 > 0"

# logging
import logging
logging.basicConfig(level=logging.DEBUG)

# pdb 断点
breakpoint()                    # Python 3.7+
# 命令：n(下一步) s(进入) c(继续) p 变量 l(代码) q(退出) w(堆栈)

# IDE 调试（VSCode / PyCharm）

# traceback
import traceback
try:
    ...
except Exception:
    traceback.print_exc()
```

## 五十二、综合小项目

### 猜数字游戏

```python
import random

secret = random.randint(1, 100)
attempts = 0
while attempts < 7:
    try:
        guess = int(input("输入猜测："))
    except ValueError:
        print("请输入有效数字")
        continue
    attempts += 1
    if guess < secret:
        print("太小")
    elif guess > secret:
        print("太大")
    else:
        print(f"猜对！用了 {attempts} 次")
        break
else:
    print(f"游戏结束，答案是 {secret}")
```

### 通讯录管理

```python
contacts = {}
while True:
    choice = input("\n1.添加 2.查询 3.删除 4.列出 5.退出：")
    if choice == '1':
        contacts[input("姓名：")] = input("电话：")
    elif choice == '2':
        print(contacts.get(input("姓名："), "未找到"))
    elif choice == '3':
        print("已删除" if contacts.pop(input("姓名："), None) else "未找到")
    elif choice == '4':
        for name, phone in contacts.items():
            print(f"{name}: {phone}")
    elif choice == '5':
        break
```

### 文件搜索工具

```python
from pathlib import Path

def search_files(directory, pattern, search_by="name"):
    results = []
    for p in Path(directory).rglob("*"):
        if not p.is_file():
            continue
        if search_by == "name" and pattern.lower() in p.name.lower():
            results.append(p)
        elif search_by == "content":
            try:
                if pattern in p.read_text(encoding="utf-8", errors="ignore"):
                    results.append(p)
            except Exception:
                pass
    return results
```

### FastAPI 简单服务

```python
# pip install fastapi uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

items = {}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in items:
        raise HTTPException(404, "未找到")
    return items[item_id]

@app.post("/items/{item_id}")
def create_item(item_id: int, item: Item):
    items[item_id] = item
    return item

# 运行：uvicorn main:app --reload
```

### CLI 工具（argparse）

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="文件统计")
    parser.add_argument("path", help="文件路径")
    parser.add_argument("-n", "--lines", action="store_true")
    args = parser.parse_args()

    text = open(args.path, encoding="utf-8").read()
    if args.lines:
        print(len(text.splitlines()))
    else:
        print(len(text))

if __name__ == "__main__":
    main()
```

## 五十三、速查小抄

### 最常用

```python
print(); input(); len(); range(); type()
```

### 容器

| 容器 | 说明 |
|------|------|
| `[]` 列表 | 有序、可修改 |
| `()` 元组 | 有序、不可修改 |
| `{}` 集合 | 无序、不重复 |
| `{}` 字典 | 键值对 |
| `set()` | 空集合 |

### 可变/不可变

| 不可变 | 可变 |
|--------|------|
| `int` `str` `tuple` `frozenset` `bytes` `float` `bool` | `list` `dict` `set` `bytearray` |

### 拷贝

```python
import copy
copy.copy()      # 浅拷贝
copy.deepcopy()  # 深拷贝
```

### 推导式

```python
[x for x in list if cond]
{x: y for x, y in dict.items()}
{x for x in set}
(x for x in range(10))          # 生成器表达式
```

### 装饰器模板

```python
from functools import wraps

def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 前处理
        result = func(*args, **kwargs)
        # 后处理
        return result
    return wrapper
```

### 上下文管理器模板

```python
from contextlib import contextmanager

@contextmanager
def ctx():
    try:
        yield value
    finally:
        cleanup()
```

### 异步模板

```python
import asyncio

async def fetch():
    await asyncio.sleep(1)
    return data

async def main():
    results = await asyncio.gather(fetch(), fetch())
    print(results)

asyncio.run(main())
```

### 正则常用

| 函数 | 说明 |
|------|------|
| `re.search()` | 找第一个匹配 |
| `re.findall()` | 找所有匹配 |
| `re.sub()` | 替换 |
| `re.compile()` | 编译 |
| `re.split()` | 分割 |

### 命令行

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 现代工具链（推荐）

```bash
# 使用 uv
uv init
uv add requests
uv add --dev pytest ruff mypy
uv run pytest
```

### 循环枚举

```python
for i in range(n): ...
for i, x in enumerate(xs): ...
for x in iterable: ...
while cond: ...
```

### 文件操作模板

```python
with open("文件", "r", encoding="utf-8") as f:
    content = f.read()
```

### 异常处理模板

```python
try:
    ...
except ValueError as e:
    ...
except Exception as e:
    ...
else:
    ...
finally:
    ...
```

### 测试模板（pytest）

```python
import pytest

@pytest.fixture
def data():
    return [1, 2, 3]

def test_sum(data):
    assert sum(data) == 6
```

### 类型注解速查

```python
def f(x: int, y: str = "a") -> list[int]:
    return [x]

# 现代写法（3.10+）
def f(x: int | None) -> dict[str, int]:
    return {}
```

---
