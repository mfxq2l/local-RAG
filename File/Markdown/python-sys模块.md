# Python sys 模块完整使用指南

## 📖 适用人群

- Python 初学者 / 中级开发者
- 系统管理员 / 运维工程师
- 需要深入理解 Python 解释器交互的开发者
- 命令行工具与脚本开发者

## ⚠️ 说明

sys 模块是 Python 标准库中最基础、最核心的模块之一，它始终可用。除非显式说明例外情况，**所有变量都是只读的**。

## 目录

- 第一部分：概述与核心变量
  - [第一章：sys 模块概述](#第一章sys-模块概述)
  - [第二章：命令行参数 sys.argv](#第二章命令行参数-sysargv)
  - [第三章：模块搜索路径 sys.path](#第三章模块搜索路径-syspath)
- 第二部分：标准流与 I/O
  - [第四章：标准输入输出流](#第四章标准输入输出流)
  - [第五章：I/O 重定向与流替换](#第五章io-重定向与流替换)
- 第三部分：系统与解释器信息
  - [第六章：平台与版本信息](#第六章平台与版本信息)
  - [第七章：解释器配置与路径](#第七章解释器配置与路径)
  - [第八章：系统限制与常量](#第八章系统限制与常量)
- 第四部分：内存与对象管理
  - [第九章：内存与对象大小](#第九章内存与对象大小)
  - [第十章：引用计数与垃圾回收](#第十章引用计数与垃圾回收)
- 第五部分：调试与性能分析
  - [第十一章：调试钩子](#第十一章调试钩子)
  - [第十二章：性能分析钩子](#第十二章性能分析钩子)
  - [第十三章：跟踪与帧对象](#第十三章跟踪与帧对象)
  - [第十四章：sys.monitoring（3.12+）](#第十四章sysmonitoring312)
- 第六部分：异常处理与安全
  - [第十五章：异常处理](#第十五章异常处理)
  - [第十六章：审计钩子](#第十六章审计钩子)
  - [第十七章：安全相关](#第十七章安全相关)
- 第七部分：进阶与跨平台
  - [第十八章：字符串驻留](#第十八章字符串驻留)
  - [第十九章：跨平台注意事项](#第十九章跨平台注意事项)
  - [第二十章：版本演进与新特性](#第二十章版本演进与新特性)
  - [第二十一章：常见陷阱与最佳实践](#第二十一章常见陷阱与最佳实践)
  - [第二十二章：速查小抄](#第二十二章速查小抄)
- 参考资料


# 第一部分：概述与核心变量

## 第一章：sys 模块概述

### 1.1 sys 模块是什么

sys 模块提供了一些由解释器使用或维护的变量，以及与解释器高强度交互的函数。它将始终可用。

与 os 模块的区别：

| 维度 | sys | os |
|------|-----|-----|
| 交互对象 | Python 解释器本身 | 操作系统 |
| 关注点 | 解释器行为、运行时环境 | 文件、进程、环境变量 |
| 典型用途 | 命令行参数、路径管理、流控制 | 文件操作、进程管理 |

### 1.2 导入方式

```python
import sys

# 查看版本
print(sys.version)
print(sys.version_info)

# 查看平台
print(sys.platform)
```

### 1.3 模块内省

```python
import sys

# 查看所有属性
dir(sys)

# 查看帮助
help(sys)

# 查看模块文档
print(sys.__doc__)
```

### 1.4 核心功能概览

| 功能领域 | 代表变量/函数 |
|---------|-------------|
| 命令行参数 | `sys.argv` |
| 模块搜索路径 | `sys.path`、`sys.prefix`、`sys.exec_prefix` |
| 标准流 | `sys.stdin`、`sys.stdout`、`sys.stderr` |
| 系统信息 | `sys.version`、`sys.platform`、`sys.byteorder` |
| 内存管理 | `sys.getsizeof()`、`sys.getrefcount()` |
| 调试 | `sys.settrace()`、`sys.setprofile()`、`sys.breakpointhook()` |
| 异常 | `sys.exc_info()`、`sys.excepthook()` |
| 审计 | `sys.audit()`、`sys.addaudithook()` |
| 退出 | `sys.exit()` |


## 第二章：命令行参数 sys.argv

### 2.1 基本用法

`sys.argv` 是一个列表，包含传递给 Python 脚本的命令行参数。`argv[0]` 为脚本的名称（是否是完整的路径名取决于操作系统）。

```python
# script.py
import sys

print(sys.argv)
```

```bash
python script.py arg1 arg2 arg3
# 输出: ['script.py', 'arg1', 'arg2', 'arg3']
```

### 2.2 不同调用方式下 argv[0] 的值

| 调用方式 | argv[0] 的值 |
|---------|-------------|
| `python script.py` | `'script.py'` |
| `python -c "..."` | `'-c'` |
| `python -m module` | 模块文件的完整路径 |

使用 `-c` 时，`sys.argv` 的首个元素为 `"-c"`，并会把当前目录加入至 `sys.path` 开头。

### 2.3 参数解析实战

```python
import sys

def main():
    if len(sys.argv) < 2:
        print("用法: python script.py <命令> [参数]")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "greet":
        name = args[0] if args else "World"
        print(f"Hello, {name}!")
    elif command == "sum":
        numbers = [int(x) for x in args]
        print(sum(numbers))
    else:
        print(f"未知命令: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 2.4 推荐：使用 argparse 替代

```python
import argparse

parser = argparse.ArgumentParser(description="示例程序")
parser.add_argument("name", help="你的名字")
parser.add_argument("-a", "--age", type=int, default=18)
args = parser.parse_args()

print(f"{args.name}, {args.age} 岁")
# 自动处理 --help、错误提示、类型转换
```


## 第三章：模块搜索路径 sys.path

### 3.1 sys.path 是什么

`sys.path` 是一个字符串列表，指定了模块搜索路径。Python 在导入模块时按顺序搜索这些目录。

### 3.2 初始化顺序

模块搜索路径的第一个条目是包含输入脚本的目录（如果存在）。否则，第一个条目是当前目录（执行交互式 shell、`-c` 命令或 `-m` 模块时）。

完整初始化顺序：

1. **脚本所在目录**（或当前目录）
2. **PYTHONPATH 环境变量**指定的目录
3. **标准库目录**（平台无关模块）
4. **扩展模块目录**（平台相关模块，`.pyd` 或 `.so` 文件）
5. **site-packages 目录**（第三方库）

### 3.3 查看和修改

```python
import sys

# 查看搜索路径
for p in sys.path:
    print(p)

# 添加自定义路径
sys.path.append("/my/custom/path")    # 追加到末尾
sys.path.insert(0, "/my/custom/path") # 插入到开头（优先级更高）

# 删除路径
sys.path.remove("/my/custom/path")
```

### 3.4 环境变量 PYTHONPATH

```bash
# Unix / macOS
export PYTHONPATH="/my/modules:$PYTHONPATH"

# Windows
set PYTHONPATH=C:\my\modules;%PYTHONPATH%

# 注意：PYTHONPATH 会影响所有已安装的 Python 版本/环境
# 谨慎在 shell profile 或全局环境变量中设置
```

### 3.5 推荐方案

| 方案 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| `sys.path.append()` | 临时调试 | 简单直接 | 运行时修改，不可持久化 |
| `PYTHONPATH` | 全局配置 | 持久化 | 影响所有 Python 环境 |
| `sitecustomize` / `usercustomize` | 用户级定制 | 精细控制 | 需要配置 |
| `._pth` 文件 | 完全覆盖 sys.path | 完全控制 | 仅 Windows |

```python
# 不推荐：硬编码路径
sys.path.append("/home/user/project/src")

# 推荐：使用相对路径
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 更推荐：使用包和 pip install -e
# pip install -e .  （开发模式安装）
```


# 第二部分：标准流与 I/O

## 第四章：标准输入输出流

### 4.1 三个标准流

| 流 | 属性 | 文件描述符 | 用途 |
|----|------|-----------|------|
| 标准输入 | `sys.stdin` | 0 | 读取输入 |
| 标准输出 | `sys.stdout` | 1 | 正常输出 |
| 标准错误 | `sys.stderr` | 2 | 错误输出 |

```python
import sys

# 读取输入
line = sys.stdin.readline()
all_input = sys.stdin.read()

# 输出
sys.stdout.write("Hello\n")
print("Hello")  # 等价于 sys.stdout.write("Hello\n")

# 错误输出
sys.stderr.write("Error!\n")
```

### 4.2 stdin 常用操作

```python
import sys

# 逐行读取
for line in sys.stdin:
    print(line.strip())

# 读取所有输入
data = sys.stdin.read()

# 交互式输入
name = input("请输入名字: ")  # 等价于 sys.stdout.write(prompt) + sys.stdin.readline()
```

### 4.3 stdout 与 stderr 的区别

```python
import sys

# stdout：程序正常输出，可被管道和重定向捕获
print("正常信息")

# stderr：错误信息，不会被管道捕获（默认）
print("错误信息", file=sys.stderr)

# 实战：进度条用 stderr，数据用 stdout
def process(data):
    print("处理中...", file=sys.stderr)
    print(data)  # 数据输出到 stdout
```

### 4.4 流重定向

```bash
# 命令行重定向
python script.py > output.txt          # stdout 到文件
python script.py 2> error.txt          # stderr 到文件
python script.py > all.txt 2>&1        # 合并到同一文件
python script.py >> append.txt         # 追加模式

# 管道
python script.py | grep "keyword"
python script.py 2>/dev/null           # 丢弃 stderr
```


## 第五章：I/O 重定向与流替换

### 5.1 在代码中重定向

```python
import sys
from io import StringIO

# 保存原始 stdout
original_stdout = sys.stdout

# 重定向到 StringIO
sys.stdout = StringIO()
print("这行被捕获")
captured = sys.stdout.getvalue()

# 恢复
sys.stdout = original_stdout
print(captured)  # 这行被捕获
```

### 5.2 同时输出到屏幕和文件

```python
import sys

class Tee:
    """同时输出到多个流"""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()

    def flush(self):
        for s in self.streams:
            s.flush()

# 使用
log_file = open("output.log", "w")
sys.stdout = Tee(sys.__stdout__, log_file)

print("这行同时输出到屏幕和文件")

sys.stdout = sys.__stdout__  # 恢复
log_file.close()
```

### 5.3 原始标准流

| 属性 | 说明 |
|------|------|
| `sys.__stdin__` | 原始 stdin，无论 stdin 是否被重定向 |
| `sys.__stdout__` | 原始 stdout |
| `sys.__stderr__` | 原始 stderr |

这些对象在程序结束前都可以使用，且在需要向实际的标准流打印内容时很有用，无论 `sys.std*` 对象是否已重定向。


# 第三部分：系统与解释器信息

## 第六章：平台与版本信息

### 6.1 版本信息

```python
import sys

# 完整版本字符串
print(sys.version)        # '3.12.0 (main, Oct  2 2023, ...)'

# 版本信息元组
print(sys.version_info)   # sys.version_info(major=3, minor=12, micro=0, ...)
print(sys.version_info.major)   # 3
print(sys.version_info.minor)   # 12
print(sys.version_info.micro)   # 0
print(sys.version_info.releaselevel)  # 'final'
print(sys.version_info.serial)        # 0

# 版本比较（推荐）
if sys.version_info >= (3, 10):
    print("支持 match-case")
```

### 6.2 平台信息

```python
import sys

print(sys.platform)       # 'linux' / 'darwin' / 'win32' / 'cygwin'
print(sys.byteorder)      # 'little' / 'big'
print(sys.maxsize)        # 最大整数（2**63-1 或 2**31-1）
print(sys.maxunicode)     # 最大 Unicode 码点
```

### 6.3 跨平台判断

```python
import sys

if sys.platform.startswith("linux"):
    print("Linux")
elif sys.platform == "darwin":
    print("macOS")
elif sys.platform == "win32":
    print("Windows")

# 推荐：使用 os.name 判断大类
import os
if os.name == "posix":
    print("Unix-like")
elif os.name == "nt":
    print("Windows")
```


## 第七章：解释器配置与路径

### 7.1 路径变量

| 变量 | 说明 |
|------|------|
| `sys.prefix` | Python 安装的基础目录 |
| `sys.exec_prefix` | 平台相关文件的安装目录 |
| `sys.base_prefix` | 基础安装目录（虚拟环境中指向原始 Python） |
| `sys.base_exec_prefix` | 基础执行前缀 |
| `sys.executable` | Python 解释器的绝对路径 |
| `sys.platlibdir` | 平台库目录名（通常为 `lib` 或 `lib64`） |

```python
import sys

print(sys.executable)      # '/usr/bin/python3'
print(sys.prefix)          # '/usr'
print(sys.base_prefix)     # '/usr'（虚拟环境中可能不同）
print(sys.platlibdir)      # 'lib'
```

### 7.2 虚拟环境检测

```python
import sys

def in_venv():
    return sys.prefix != sys.base_prefix

if in_venv():
    print("运行在虚拟环境中")
else:
    print("运行在系统 Python 中")
```

### 7.3 解释器选项

```python
import sys

# 命令行标志
print(sys.flags)
print(sys.flags.debug)      # 是否开启调试模式
print(sys.flags.optimize)   # 优化级别（-O 为 1，-OO 为 2）
print(sys.flags.verbose)    # 详细模式
print(sys.flags.quiet)      # 安静模式（-q）

# 字节序
print(sys.byteorder)        # 'little' 或 'big'
```

### 7.4 默认编码

```python
import sys

print(sys.getdefaultencoding())    # 'utf-8'
print(sys.getfilesystemencoding()) # 'utf-8'（文件系统编码）
print(sys.getfilesystemencodeerrors())  # 'surrogateescape'
```


## 第八章：系统限制与常量

### 8.1 递归限制

```python
import sys

# 查看默认递归限制（默认 1000）
print(sys.getrecursionlimit())

# 修改递归限制
sys.setrecursionlimit(5000)

# ⚠️ 注意事项：
# - 增加限制可能导致 C 栈溢出，使 Python 崩溃
# - 最高限制取决于平台
# - 增加限制不会增加 C 栈空间
# - 进程可能在 10⁴-10⁵ 帧时发生段错误
```

### 8.2 整数限制

```python
import sys

# 最大整数值（取决于平台）
print(sys.maxsize)       # 9223372036854775807（64位）
print(-sys.maxsize - 1)  # 最小整数值
```

### 8.3 路径长度限制

```python
import sys

print(sys.getwindowsversion())  # Windows 版本信息（仅 Windows）
# Unix 上使用 os.pathconf() 获取路径长度限制
```

### 8.4 浮点数信息

```python
import sys

print(sys.float_info)
# sys.float_info(max=1.7976931348623157e+308, max_exp=1024,
#               max_10_exp=308, min=2.2250738585072014e-308,
#               min_exp=-1021, min_10_exp=-307, dig=15,
#               mant_dig=53, epsilon=2.220446049250313e-16,
#               radix=2, rounds=1)

print(sys.float_info.epsilon)  # 2.220446049250313e-16
print(sys.float_info.dig)      # 15（十进制有效位数）
```


# 第四部分：内存与对象管理

## 第九章：内存与对象大小

### 9.1 sys.getsizeof

返回对象的字节大小。只计算直接占用的内存，不计算对象内所引用对象的内存。

```python
import sys

# 基本类型
print(sys.getsizeof(1))       # 28
print(sys.getsizeof(""))      # 49
print(sys.getsizeof([]))      # 56
print(sys.getsizeof({}))      # 64

# 容器：只计算容器本身
data = [1, 2, 3, 4, 5]
print(sys.getsizeof(data))    # 只算列表结构，不含元素

# 计算实际总大小（递归）
def deep_getsizeof(obj, seen=None):
    """递归计算对象的实际内存占用"""
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_getsizeof(k, seen) + deep_getsizeof(v, seen)
                    for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(deep_getsizeof(i, seen) for i in obj)
    return size
```

### 9.2 sys.getallocatedblocks

```python
import sys

# 返回当前已分配的内存块数量
before = sys.getallocatedblocks()
data = [i for i in range(10000)]
after = sys.getallocatedblocks()
print(f"分配了 {after - before} 个内存块")
```


## 第十章：引用计数与垃圾回收

### 10.1 sys.getrefcount

返回对象的引用计数。由于调用函数本身会创建一个临时引用，返回的计数值比实际值大 1。

```python
import sys

a = [1, 2, 3]
print(sys.getrefcount(a))  # 2（一个来自 a，一个来自 getrefcount 参数）

b = a
print(sys.getrefcount(a))  # 3

del b
print(sys.getrefcount(a))  # 2
```

### 10.2 sys._clear_type_cache

```python
import sys

# 清除内部类型缓存（主要用于调试和性能测试）
sys._clear_type_cache()
```

### 10.3 垃圾回收信息

```python
import sys
import gc

# 设置垃圾回收调试标志
gc.set_debug(gc.DEBUG_SAVEALL)

# 查看回收统计
print(gc.get_stats())
```


# 第五部分：调试与性能分析

## 第十一章：调试钩子

### 11.1 sys.breakpointhook

`breakpoint()` 函数调用 `sys.breakpointhook()`，默认进入 `pdb` 调试器。

```python
import sys

# 默认行为：进入 pdb
breakpoint()

# 自定义断点行为
def my_breakpoint(*args, **kwargs):
    print("自定义断点！")
    # 可以启动自己的调试器

sys.breakpointhook = my_breakpoint
breakpoint()  # 输出: 自定义断点！

# 禁用断点
sys.breakpointhook = lambda *x: None

# 环境变量控制
# PYTHONBREAKPOINT=0  # 禁用断点
# PYTHONBREAKPOINT=module.function  # 指定自定义函数
```

### 11.2 sys.excepthook

自定义未捕获异常的处理方式。

```python
import sys

def custom_excepthook(exc_type, exc_value, exc_traceback):
    """自定义异常处理"""
    print(f"发生错误: {exc_type.__name__}: {exc_value}", file=sys.stderr)
    # 可以记录日志、发送告警等

sys.excepthook = custom_excepthook

# 触发未捕获异常
1 / 0  # 输出: 发生错误: ZeroDivisionError: division by zero
```

### 11.3 sys.displayhook

自定义交互式解释器中表达式的显示方式。

```python
import sys

def custom_displayhook(value):
    if value is not None:
        sys.__stdout__.write(f"结果: {repr(value)}\n")

sys.displayhook = custom_displayhook
# 在交互式解释器中：
# >>> 1 + 1
# 结果: 2
```


## 第十二章：性能分析钩子

### 12.1 sys.setprofile

安装性能分析函数。与 settrace 相比，setprofile 只看到函数调用和返回，性能更好。返回值为 None。

```python
import sys
import time

def profiler(frame, event, arg):
    if event == "call":
        print(f"调用: {frame.f_code.co_name}")
    elif event == "return":
        print(f"返回: {frame.f_code.co_name}")

sys.setprofile(profiler)

def foo():
    return 42

foo()

sys.setprofile(None)  # 移除钩子
```

### 12.2 sys.settrace

安装跟踪函数。比 setprofile 更精细，可以获取行事件和异常事件。

```python
import sys

def tracer(frame, event, arg):
    if event == "line":
        print(f"行 {frame.f_lineno}: {frame.f_code.co_filename}")
    elif event == "exception":
        print(f"异常: {arg[0].__name__}")
    return tracer  # 必须返回 tracer 本身以继续跟踪

sys.settrace(tracer)

def example():
    x = 1
    y = 2
    return x + y

example()

sys.settrace(None)
```

### 12.3 setprofile vs settrace 对比

| 特性 | setprofile | settrace |
|------|-----------|----------|
| 事件类型 | call、return、c_call、c_return | call、line、return、exception |
| 精细度 | 函数级 | 行级 |
| 性能开销 | 较低 | 较高 |
| 适用场景 | 性能分析 | 调试 |


## 第十三章：跟踪与帧对象

### 13.1 sys._getframe

```python
import sys

def get_caller_info():
    frame = sys._getframe(1)  # 1 = 调用者的帧
    return frame.f_code.co_name, frame.f_lineno

def caller():
    name, line = get_caller_info()
    print(f"被 {name} 在第 {line} 行调用")

caller()  # 被 caller 在第 11 行调用
```

### 13.2 sys._current_frames

返回一个字典，映射每个线程的 ID 到该线程当前的帧对象。对于调试死锁很有用。

```python
import sys
import traceback
import threading

def dump_all_stacks():
    """打印所有线程的调用栈"""
    for thread_id, frame in sys._current_frames().items():
        print(f"\n=== 线程 {thread_id} ===")
        traceback.print_stack(frame)

# 使用
dump_all_stacks()
```


## 第十四章：sys.monitoring（3.12+）

### 14.1 概述

`sys.monitoring` 是 Python 3.12 引入的执行事件监测模块（PEP 669）。它是一个命名空间，位于 sys 模块内，无需单独导入。

### 14.2 与 settrace 的区别

| 特性 | sys.settrace | sys.monitoring |
|------|-------------|----------------|
| 引入版本 | Python 2 | Python 3.12 |
| 性能 | 高开销 | 低开销 |
| 事件类型 | call/line/return/exception | 更多事件类型 |
| 用途 | 传统调试 | 现代性能分析 |

### 14.3 基本用法

```python
import sys

# 使用工具 ID（0-5 预留给标准工具）
TOOL_ID = sys.monitoring.DEBUGGER_ID

# 注册回调
def on_line(code, line_number):
    print(f"执行 {code.co_name} 的第 {line_number} 行")

# 设置监测
sys.monitoring.use_tool_id(TOOL_ID, "my_tool")
sys.monitoring.register_callback(TOOL_ID, sys.monitoring.events.LINE, on_line)
sys.monitoring.set_events(TOOL_ID, sys.monitoring.events.LINE)

# 执行代码
def example():
    x = 1
    return x

example()

# 清理
sys.monitoring.set_events(TOOL_ID, 0)
sys.monitoring.free_tool_id(TOOL_ID)
```


# 第六部分：异常处理与安全

## 第十五章：异常处理

### 15.1 sys.exc_info

返回当前正在处理的异常信息，是一个三元组（异常类型、异常实例、traceback 对象）。

```python
import sys

try:
    1 / 0
except ZeroDivisionError:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print(f"类型: {exc_type.__name__}")    # ZeroDivisionError
    print(f"值: {exc_value}")              # division by zero
    print(f"Traceback: {exc_traceback}")
```

### 15.2 sys.last_type / last_value / last_traceback

```python
import sys

try:
    1 / 0
except:
    pass

# 这些属性保存了最后一次未捕获异常的信息（交互模式下可用）
print(sys.last_type)       # <class 'ZeroDivisionError'>
print(sys.last_value)      # division by zero
print(sys.last_traceback)  # <traceback object>
```

### 15.3 sys.last_exc（3.12+）

Python 3.12 新增 `sys.last_exc`，直接保存最后一个未捕获异常实例。

```python
import sys

try:
    1 / 0
except:
    pass

# Python 3.12+
print(sys.last_exc)  # ZeroDivisionError('division by zero')
```

**3.12 变更**：`sys._current_exceptions()` 返回的字典中，每个值现在是单个异常实例，而不是 `sys.exc_info()` 返回的 3 元组。


## 第十六章：审计钩子

### 16.1 概述

审计钩子机制由 PEP 578 引入（Python 3.8+），用于监测 Python 解释器的内部操作。

### 16.2 sys.audit

```python
import sys

# 触发审计事件
sys.audit("my_custom_event", "arg1", "arg2")
```

### 16.3 sys.addaudithook

```python
import sys

def my_audit_hook(event, args):
    """审计钩子"""
    print(f"事件: {event}, 参数: {args}")

sys.addaudithook(my_audit_hook)

# 触发事件
sys.audit("custom.event", "hello")

# 内置事件（自动触发）
import os
os.system("echo hello")  # 触发 os.system 审计事件
```

### 16.4 重要说明

- 审计钩子主要用于收集内部或不可观察操作的信息，**不适合实现“沙盒”**
- 恶意代码可以轻易禁用或绕过使用此函数添加的钩子
- 安全敏感的钩子必须使用 C API `PySys_AddAuditHook()` 在初始化运行时之前添加
- 调用 `sys.addaudithook()` 时自身会引发一个名为 `sys.addaudithook` 的审计事件


## 第十七章：安全相关

### 17.1 sys.audit 事件表

Python 内置了大量审计事件，常用的包括：

| 事件名称 | 触发条件 |
|---------|----------|
| `os.system` | 调用 `os.system()` |
| `subprocess.Popen` | 创建子进程 |
| `open` | 打开文件 |
| `exec` | 执行代码 |
| `import` | 导入模块 |
| `socket.connect` | 建立网络连接 |
| `sys.addaudithook` | 添加审计钩子 |

完整事件表参考官方文档的审计事件表。

### 17.2 安全退出

```python
import sys

# 正常退出
sys.exit(0)    # 成功
sys.exit(1)    # 通用错误

# 自定义退出码
sys.exit(2)    # 用法错误

# 带消息退出
sys.exit("错误: 参数无效")  # 打印消息到 stderr 并以 1 退出

# ⚠️ sys.exit() 本质是抛出 SystemExit 异常
try:
    sys.exit(0)
except SystemExit as e:
    print(f"退出码: {e.code}")
```

### 17.3 sys.exit 与 os._exit 的区别

| 特性 | sys.exit() | os._exit() |
|------|-----------|-----------|
| 异常 | 抛出 SystemExit | 不抛异常 |
| 清理 | 执行 finally 和 atexit | 不执行任何清理 |
| 适用场景 | 正常退出 | 子进程强制退出 |


# 第七部分：进阶与跨平台

## 第十八章：字符串驻留

### 18.1 sys.intern

将字符串加入驻留表，返回驻留后的字符串。对于频繁使用的字符串（如字典键），可以加速比较操作。

```python
import sys

a = sys.intern("hello_world")
b = sys.intern("hello_world")
print(a is b)  # True（同一对象）

# 未驻留的字符串
c = "hello_world_" + "test"
d = "hello_world_" + "test"
print(c is d)  # False（可能）

# 驻留后
c = sys.intern(c)
d = sys.intern(d)
print(c is d)  # True
```

### 18.2 自动驻留

Python 自动驻留的字符串包括：

- 短字符串（由编译器决定）
- 标识符
- 模块、类、实例属性名

```python
import sys

# 检查字符串是否已被驻留
# sys.intern(s) is s 返回 True 表示已驻留
s = "hello"
print(sys.intern(s) is s)  # True（字面量通常已驻留）
```


## 第十九章：跨平台注意事项

### 19.1 sys.platform 的差异

```python
import sys

# Linux：始终返回 'linux'（不包含主版本号）
# macOS：'darwin'
# Windows：'win32'（即使是 64 位）
# Cygwin：'cygwin'

# 推荐判断方式
if sys.platform.startswith("linux"):
    ...
elif sys.platform == "darwin":
    ...
elif sys.platform == "win32":
    ...
```

### 19.2 命令行参数的编码

在 Unix 上，命令行参数由操作系统以字节传递。Python 使用文件系统编码和 `surrogateescape` 错误处理器来解码它们。

### 19.3 I/O 编码

```python
import sys

# Python 默认使用 UTF-8，但重定向到管道/文件时可能不同
# 设置 PYTHONIOENCODING 环境变量控制 I/O 编码
# export PYTHONIOENCODING=utf-8
```


## 第二十章：版本演进与新特性

### 20.1 各版本重要变更

| 版本 | 变更 |
|------|------|
| 3.2 | 添加 `sys.abiflags` |
| 3.8 | 添加 `sys.addaudithook()`、`sys.audit()`；默认 ABI flags 变为空字符串 |
| 3.10 | `sys.orig_argv`（命令行原始参数） |
| 3.11 | 优化解释器性能；`sys.exception()` 替代 `sys.exc_info()` |
| 3.12 | 添加 `sys.monitoring`、`sys.last_exc`；`sys._current_exceptions()` 返回异常实例 |
| 3.13 | 实验性自由线程（无 GIL） |
| 3.15 | 添加 `sys.abi_info`（ABI 信息对象） |

### 20.2 sys.monitoring（3.12+）

基于 PEP 669 的低开销监测系统，提供比 `sys.settrace` 更高效的事件监测能力。

### 20.3 sys.abi_info（3.15+）

包含当前 Python 解释器 ABI 信息的对象，包括 `pointer_bits`、`free_threaded`、`debug`、`byteorder` 等属性。


## 第二十一章：常见陷阱与最佳实践

### 21.1 修改 sys.path 的隐患

```python
# ❌ 不推荐：硬编码绝对路径
sys.path.append("/home/user/myproject/src")

# ❌ 不推荐：使用 sys.path.insert(0, ...) 可能覆盖标准库
sys.path.insert(0, "/my/path")  # 可能意外覆盖标准库模块

# ✅ 推荐：使用相对路径
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ✅ 更推荐：使用包管理
# pip install -e .
```

### 21.2 sys.exit 在 try/finally 中的行为

```python
import sys

try:
    sys.exit(0)
finally:
    print("会执行")  # sys.exit() 抛出 SystemExit，finally 仍会执行
```

### 21.3 递归限制设置过高

```python
import sys

# ❌ 危险：设置过高的递归限制
sys.setrecursionlimit(100000)  # 可能导致 C 栈溢出，程序崩溃

# ✅ 安全：将递归改为迭代
def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

### 21.4 重定向 stdout 后忘记恢复

```python
import sys

# ❌ 危险：没有恢复
sys.stdout = open("log.txt", "w")
print("这行写入文件")

# ✅ 安全：使用 try/finally
original = sys.stdout
try:
    sys.stdout = open("log.txt", "w")
    print("这行写入文件")
finally:
    sys.stdout = original
```

### 21.5 最佳实践总结

| 场景 | 推荐做法 |
|------|----------|
| 命令行参数 | 使用 `argparse`，而非直接解析 `sys.argv` |
| 路径管理 | 使用 `pathlib`，而非硬编码路径 |
| 模块导入 | 使用包和 `pip install -e`，而非修改 `sys.path` |
| 调试 | 使用 `breakpoint()`，可通过环境变量控制 |
| 异常处理 | 使用 `try/except`，`sys.exc_info()` 仅用于特殊场景 |
| 退出程序 | 使用 `sys.exit()`，子进程中使用 `os._exit()` |
| I/O 编码 | 显式指定编码，设置 `PYTHONIOENCODING` |


## 第二十二章：速查小抄

### 命令行参数

```python
sys.argv                 # 命令行参数列表
sys.orig_argv            # 原始命令行参数（3.10+）
```

### 模块路径

```python
sys.path                 # 模块搜索路径
sys.prefix               # Python 安装目录
sys.exec_prefix          # 平台相关文件目录
sys.base_prefix          # 基础安装目录
sys.executable           # Python 解释器路径
sys.platlibdir           # 平台库目录
```

### 标准流

```python
sys.stdin                # 标准输入
sys.stdout               # 标准输出
sys.stderr               # 标准错误
sys.__stdin__            # 原始 stdin
sys.__stdout__           # 原始 stdout
sys.__stderr__           # 原始 stderr
```

### 系统信息

```python
sys.version              # 版本字符串
sys.version_info         # 版本信息元组
sys.platform             # 平台标识
sys.byteorder            # 字节序
sys.maxsize              # 最大整数
sys.flags                # 命令行标志
sys.getdefaultencoding() # 默认编码
sys.getfilesystemencoding()  # 文件系统编码
```

### 内存管理

```python
sys.getsizeof(obj)       # 对象大小（字节）
sys.getrefcount(obj)     # 引用计数
sys.getallocatedblocks() # 已分配内存块数
```

### 调试

```python
sys.settrace(func)       # 安装跟踪函数
sys.setprofile(func)     # 安装性能分析函数
sys.breakpointhook       # 断点钩子
sys.excepthook           # 异常钩子
sys.displayhook          # 显示钩子
sys.monitoring           # 执行事件监测（3.12+）
```

### 异常处理

```python
sys.exc_info()           # 当前异常信息
sys.last_type            # 最后异常类型
sys.last_value           # 最后异常值
sys.last_traceback       # 最后异常 traceback
sys.last_exc             # 最后异常实例（3.12+）
```

### 安全与审计

```python
sys.audit(event, *args)  # 触发审计事件
sys.addaudithook(hook)   # 添加审计钩子
```

### 其他

```python
sys.exit(code)           # 退出程序
sys.getrecursionlimit()  # 获取递归限制
sys.setrecursionlimit(n) # 设置递归限制
sys.intern(s)            # 字符串驻留
sys._getframe(n)         # 获取帧对象
sys._current_frames()    # 所有线程的帧
```


## 参考资料

- **官方文档（中文）**: https://docs.python.org/zh-cn/3/library/sys.html
- **官方文档（英文）**: https://docs.python.org/3/library/sys.html
- **命令行与环境**: https://docs.python.org/zh-cn/3/using/cmdline.html
- **sys.path 初始化**: https://docs.python.org/3/library/sys_path_init.html
- **sys.monitoring 文档**: https://docs.python.org/3/library/sys.monitoring.html
- **审计事件表**: https://docs.python.org/3/library/audit_events.html
- **PEP 578（审计钩子）**: https://peps.python.org/pep-0578/
- **PEP 669（低开销监测）**: https://peps.python.org/pep-0669/