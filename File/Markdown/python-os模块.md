# Python os 模块完整使用指南


## 📖 适用人群

- Python 初学者 / 中级开发者
- 系统管理员 / 运维工程师
- 自动化脚本开发者
- 需要深入理解文件系统操作的开发者

## 目录

- 第一部分：概述与导入
  - 第一章：os 模块概述
  - 第二章：导入方式与命名空间
  - 第三章：os 模块的核心子模块
- 第二部分：文件与目录操作
  - 第四章：当前工作目录
  - 第五章：目录的创建与删除
  - 第六章：文件的删除与重命名
  - 第七章：列出目录内容
  - 第八章：遍历目录树 os.walk
- 第三部分：路径操作 os.path
  - 第九章：路径拼接与拆分
  - 第十章：路径判断与存在性检查
  - 第十一章：路径转换与规范化
  - 第十二章：文件信息获取
- 第四部分：环境变量与进程信息
  - 第十三章：环境变量操作
  - 第十四章：进程与用户信息
  - 第十五章：系统信息获取
- 第五部分：文件描述符与底层 I/O
  - 第十六章：文件描述符基础
  - 第十七章：os.open 与 os.close
  - 第十八章：文件描述符的复制与重定向
  - 第十九章：os.fdopen 与文件对象转换
- 第六部分：权限、属性与执行
  - 第二十章：文件权限管理
  - 第二十一章：文件属性与时间戳
  - 第二十二章：执行系统命令
  - 第二十三章：进程管理
- 第七部分：跨平台与最佳实践
  - 第二十四章：os 与 pathlib 对比
  - 第二十五章：跨平台注意事项
  - 第二十六章：常见陷阱与安全建议
  - 第二十七章：速查小抄
- 参考资料


# 第一部分：概述与导入

## 第一章：os 模块概述

`os` 模块是 Python 标准库的核心模块之一，提供了一种**可移植**的方式来使用与操作系统相关的功能。其设计遵循一个核心原则：只要不同操作系统上某一功能可用，就使用相同的接口。例如，`os.stat(path)` 在所有平台上都以相同格式返回文件状态信息。

### 1.1 os 模块的核心能力

| 能力领域 | 代表函数 | 说明 |
|---------|---------|------|
| 文件与目录操作 | `os.mkdir()`、`os.remove()`、`os.rename()` | 创建、删除、重命名 |
| 路径操作 | `os.path.join()`、`os.path.exists()` | 跨平台路径处理 |
| 环境变量 | `os.environ`、`os.getenv()` | 读写系统环境变量 |
| 进程管理 | `os.fork()`、`os.exec()`、`os.system()` | 创建和执行进程 |
| 系统信息 | `os.uname()`、`os.getpid()` | 获取系统和进程信息 |
| 文件描述符 | `os.open()`、`os.read()`、`os.write()` | 底层 I/O 操作 |
| 权限管理 | `os.chmod()`、`os.chown()` | 文件权限与所有者 |

### 1.2 什么时候用 os，什么时候用其他模块

根据官方文档的建议：

- 只想读写文件 → 使用内置 `open()`
- 只想操作路径 → 使用 `os.path` 模块
- 创建临时文件和目录 → 使用 `tempfile` 模块
- 高级文件和目录处理（复制、移动） → 使用 `shutil` 模块
- 读取命令行参数 → 使用 `argparse` 模块
- 面向对象的路径操作 → 使用 `pathlib` 模块

### 1.3 异常处理

os 模块的所有函数在遇到无效或无法访问的文件名、路径，或其他操作系统不接受的参数时，都会抛出 `OSError`（或其子类）。

```python
import os

try:
    os.remove("/path/to/nonexistent")
except OSError as e:
    print(f"错误代码: {e.errno}")      # 错误编号
    print(f"错误信息: {e.strerror}")   # 错误描述
    print(f"错误文件: {e.filename}")   # 相关文件
```

`os.error` 是内置 `OSError` 异常的别名。

```python
# os.error 和 OSError 是同一个东西
assert os.error is OSError  # True
```

### 1.4 os.name：操作系统标识

```python
import os

print(os.name)  # 'posix'（Linux/macOS）或 'nt'（Windows）或 'java'
```

已注册的名称：`'posix'`、`'nt'`、`'java'`。如需更细粒度的平台信息，使用 `sys.platform` 或 `platform` 模块。


## 第二章：导入方式与命名空间

### 2.1 推荐导入方式

```python
# 推荐：导入整个模块
import os
os.getcwd()
os.path.join("dir", "file.txt")
```

### 2.2 为什么不推荐 from os import *

`os` 模块定义了一个名为 `open` 的函数（即底层文件打开），如果使用 `from os import *`，会覆盖内置的 `open()` 函数，导致后续代码出现难以排查的错误。

```python
# ❌ 千万不要这样做
from os import *  # 会覆盖内置 open()

# ✅ 正确做法
import os
# 或按需导入
from os import getcwd, listdir
from os.path import join, exists
```

### 2.3 探索模块内容

```python
import os

# 查看所有可用属性和方法
dir(os)

# 查看某个函数的帮助
help(os.listdir)

# 查看 os.path 子模块
dir(os.path)
help(os.path.join)

# 查看 os.path 的详细文档
import os.path
help(os.path)
```


## 第三章：os 模块的核心子模块

### 3.1 子模块概览

| 子模块 | 导入方式 | 主要功能 |
|--------|---------|----------|
| `os.path` | `import os.path` 或 `os.path` | 路径操作 |
| `os.environ` | `os.environ` | 环境变量字典 |
| `os.stat_result` | `os.stat()` 返回值 | 文件状态信息 |
| `os.terminal_size` | `os.get_terminal_size()` 返回值 | 终端尺寸 |

### 3.2 平台专属扩展

特定操作系统的扩展也可通过 os 模块使用，但会威胁可移植性。例如：

- Unix 专属：`os.fork()`、`os.getuid()`、`os.uname()`
- Windows 专属：`os.startfile()`、`os.path.islink()`（行为不同）
- WebAssembly / Android / iOS：大量 os 模块函数不可用

```python
import os

# 检查函数是否可用
if hasattr(os, "fork"):
    print("支持 fork")
else:
    print("不支持 fork（Windows 不支持）")

# 检查平台
if os.name == "posix":
    print("Unix-like 系统")
elif os.name == "nt":
    print("Windows 系统")
```


# 第二部分：文件与目录操作

## 第四章：当前工作目录

### 4.1 获取当前工作目录

```python
import os

current_dir = os.getcwd()
print(current_dir)  # 例如 /home/user/project
```

`os.getcwd()` 返回当前工作目录的绝对路径字符串。

### 4.2 切换工作目录

```python
# 切换到指定目录
os.chdir("/path/to/directory")

# 切换到上级目录
os.chdir("..")

# 切换到家目录
os.chdir(os.path.expanduser("~"))

# 使用上下文管理器临时切换（Python 3.11+）
from contextlib import chdir

with chdir("/tmp"):
    print(os.getcwd())  # /tmp
# 退出后自动恢复
print(os.getcwd())  # 原来的目录
```

### 4.3 常用目录常量

```python
# 使用 os.path.expanduser 获取家目录
home = os.path.expanduser("~")

# 使用 os.environ 获取常见目录
home = os.environ.get("HOME")        # Unix
userprofile = os.environ.get("USERPROFILE")  # Windows

# 跨平台方式
from pathlib import Path
home = Path.home()
```


## 第五章：目录的创建与删除

### 5.1 创建目录

```python
# 创建单个目录（父目录必须存在）
os.mkdir("new_dir")

# 递归创建多级目录（父目录自动创建）
os.makedirs("a/b/c/d")

# 递归创建，如果已存在不报错
os.makedirs("a/b/c", exist_ok=True)
```

| 函数 | 行为 | 父目录不存在时 |
|------|------|---------------|
| `os.mkdir(path)` | 创建单级目录 | 报错 `FileNotFoundError` |
| `os.makedirs(path)` | 递归创建 | 自动创建 |
| `os.makedirs(path, exist_ok=True)` | 递归创建，已存在不报错 | 自动创建 |

### 5.2 删除目录

```python
# 删除空目录（目录必须为空）
os.rmdir("empty_dir")

# 递归删除目录树（包括所有内容）
import shutil
shutil.rmtree("dir_with_contents")  # 慎用！

# os.removedirs：递归删除空目录
os.removedirs("a/b/c")  # 从最深层开始，删除所有空的父目录
```

> ⚠️ `os.removedirs()` 会尝试删除指定路径及其所有空父目录，直到遇到非空目录为止。如果 `a/b/c` 为空但 `a/b` 不为空，则只删除 `a/b/c`。


## 第六章：文件的删除与重命名

### 6.1 删除文件

```python
# 删除单个文件
os.remove("file.txt")
# 或
os.unlink("file.txt")  # 与 remove 功能相同

# 删除前检查
if os.path.exists("file.txt"):
    os.remove("file.txt")
```

### 6.2 重命名

```python
# 重命名文件或目录
os.rename("old_name.txt", "new_name.txt")
os.rename("old_dir", "new_dir")
```

| 函数 | 行为 |
|------|------|
| `os.rename(src, dst)` | 重命名；如果 dst 已存在，在 Windows 上报错，在 Unix 上覆盖 |
| `os.replace(src, dst)` | 重命名；如果 dst 已存在，始终覆盖（跨平台一致） |

```python
# 推荐使用 os.replace 以获得跨平台一致行为
os.replace("old.txt", "new.txt")
```


## 第七章：列出目录内容

### 7.1 os.listdir

```python
# 列出目录下的文件和子目录名称（不包含路径）
entries = os.listdir(".")
# 返回 ['file1.txt', 'file2.py', 'subdir', ...]

# 过滤文件
files = [f for f in os.listdir(".") if os.path.isfile(f)]
dirs = [f for f in os.listdir(".") if os.path.isdir(f)]

# 配合 os.path.join 获取完整路径
for entry in os.listdir("."):
    full_path = os.path.join(".", entry)
    print(full_path)
```

### 7.2 os.scandir（推荐，更高效）

```python
# os.scandir 返回一个迭代器，每个条目包含文件类型信息
with os.scandir(".") as entries:
    for entry in entries:
        print(entry.name)           # 文件名
        print(entry.path)           # 完整路径
        print(entry.is_file())      # 是否是文件
        print(entry.is_dir())       # 是否是目录
        print(entry.stat())         # 文件状态
```

> 💡 `os.scandir()` 比 `os.listdir()` + `os.path.isfile()` 更快，因为它直接从目录读取文件类型信息，无需额外的系统调用。

### 7.3 列出目录对比

| 函数 | 返回类型 | 是否包含路径 | 性能 | 推荐场景 |
|------|---------|-------------|------|----------|
| `os.listdir()` | 列表 | 否 | 中 | 简单列出文件名 |
| `os.scandir()` | 迭代器 | 是（通过 `entry.path`） | 高 | 需要文件类型信息 |
| `os.walk()` | 生成器 | 是 | 中 | 递归遍历目录树 |


## 第八章：遍历目录树 os.walk

### 8.1 基本用法

`os.walk()` 是遍历目录树的标准方式，返回一个生成器，每次迭代产生一个三元组 `(dirpath, dirnames, filenames)`。

```python
import os

for dirpath, dirnames, filenames in os.walk("/project"):
    print(f"当前目录: {dirpath}")
    print(f"子目录: {dirnames}")
    print(f"文件: {filenames}")
    print("---")
```

| 变量 | 含义 |
|------|------|
| `dirpath` | 当前遍历到的目录路径字符串 |
| `dirnames` | 当前目录下的子目录名列表 |
| `filenames` | 当前目录下的文件名列表（不含子目录） |

### 8.2 控制遍历深度

```python
# 自顶向下（默认）：先访问父目录，再访问子目录
for dirpath, dirnames, filenames in os.walk("/project"):
    # 修改 dirnames 可以控制遍历哪些子目录
    # 跳过 node_modules
    if "node_modules" in dirnames:
        dirnames.remove("node_modules")
    print(dirpath)

# 自底向上：先访问子目录，再访问父目录
for dirpath, dirnames, filenames in os.walk("/project", topdown=False):
    print(dirpath)
```

### 8.3 实战：查找特定文件

```python
import os

def find_python_files(root_dir):
    """递归查找所有 .py 文件"""
    results = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                full_path = os.path.join(dirpath, filename)
                results.append(full_path)
    return results
```

### 8.4 实战：计算目录大小

```python
import os

def get_dir_size(root_dir):
    """计算目录总大小"""
    total = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total
```


# 第三部分：路径操作 os.path

## 第九章：路径拼接与拆分

### 9.1 路径拼接

```python
import os.path

# 拼接路径（自动处理分隔符）
path = os.path.join("folder", "subfolder", "file.txt")
# Unix: 'folder/subfolder/file.txt'
# Windows: 'folder\\subfolder\\file.txt'

# 拼接绝对路径
abs_path = os.path.join("/home", "user", "file.txt")
# '/home/user/file.txt'

# 如果某个参数是绝对路径，之前的部分会被丢弃
os.path.join("/home", "/etc", "passwd")  # '/etc/passwd'
```

### 9.2 路径拆分

```python
path = "/home/user/project/main.py"

# 获取目录部分
os.path.dirname(path)   # '/home/user/project'

# 获取文件名部分
os.path.basename(path)  # 'main.py'

# 同时获取目录和文件名
os.path.split(path)     # ('/home/user/project', 'main.py')

# 获取扩展名
os.path.splitext(path)  # ('/home/user/project/main', '.py')

# 获取文件驱动器和路径（Windows 专用）
os.path.splitdrive("C:\\Users\\file.txt")  # ('C:', '\\Users\\file.txt')
```

### 9.3 路径拆分函数对比

| 函数 | 输入 | 输出 |
|------|------|------|
| `os.path.dirname()` | `/a/b/c.txt` | `/a/b` |
| `os.path.basename()` | `/a/b/c.txt` | `c.txt` |
| `os.path.split()` | `/a/b/c.txt` | `('/a/b', 'c.txt')` |
| `os.path.splitext()` | `/a/b/c.txt` | `('/a/b/c', '.txt')` |


## 第十章：路径判断与存在性检查

### 10.1 存在性检查

```python
# 路径是否存在
os.path.exists("/path/to/anything")      # 文件或目录都返回 True

# 是否是文件
os.path.isfile("/path/to/file.txt")

# 是否是目录
os.path.isdir("/path/to/directory")

# 是否是符号链接
os.path.islink("/path/to/symlink")

# 路径是否可访问（权限检查）
os.access("/path/to/file", os.R_OK)  # 可读
os.access("/path/to/file", os.W_OK)  # 可写
os.access("/path/to/file", os.X_OK)  # 可执行
```

### 10.2 路径判断函数对比

| 函数 | 判断条件 | 符号链接行为 |
|------|---------|-------------|
| `os.path.exists()` | 路径存在 | 跟随链接 |
| `os.path.lexists()` | 路径存在 | 不跟随链接（检查链接本身） |
| `os.path.isfile()` | 是普通文件 | 跟随链接 |
| `os.path.isdir()` | 是目录 | 跟随链接 |
| `os.path.islink()` | 是符号链接 | 检查链接本身 |


## 第十一章：路径转换与规范化

### 11.1 绝对路径与相对路径

```python
# 转换为绝对路径
os.path.abspath("file.txt")          # 当前目录下的绝对路径
os.path.abspath("../other/file.txt") # 规范化后的绝对路径

# 获取相对路径
os.path.relpath("/home/user/file.txt", "/home/user/project")
# '../file.txt'

# 规范化路径（去除 .. 和 .）
os.path.normpath("/home/user/../user/./file.txt")
# '/home/user/file.txt'
```

### 11.2 获取路径各部分

```python
path = "/home/user/project/main.py"

# 获取绝对路径
os.path.abspath(path)                # '/home/user/project/main.py'

# 获取真实路径（解析符号链接）
os.path.realpath("/usr/bin/python")  # 实际路径

# 获取文件大小（字节）
os.path.getsize("/path/to/file")

# 获取时间戳
os.path.getatime("/path/to/file")    # 最后访问时间
os.path.getmtime("/path/to/file")    # 最后修改时间
os.path.getctime("/path/to/file")    # 创建时间（Unix 上是 inode 变更时间）

# 获取公共前缀
os.path.commonprefix(["/usr/lib", "/usr/local", "/usr/bin"])
# '/usr/l'

# 获取公共路径（更准确）
os.path.commonpath(["/usr/lib", "/usr/local"])  # '/usr'
```


## 第十二章：文件信息获取

### 12.1 os.stat

```python
import os
import time

stat_info = os.stat("/path/to/file")

# 文件大小（字节）
print(stat_info.st_size)

# 权限模式
print(oct(stat_info.st_mode))       # 例如 0o100644

# 所有者 UID 和 GID
print(stat_info.st_uid)
print(stat_info.st_gid)

# 时间戳
print(stat_info.st_atime)           # 最后访问
print(stat_info.st_mtime)           # 最后修改
print(stat_info.st_ctime)           # 创建/变更

# 转换为可读时间
print(time.ctime(stat_info.st_mtime))
```

### 12.2 os.path 便捷函数

```python
# 这些函数内部调用 os.stat，但更简洁
os.path.getsize("/path/to/file")      # 文件大小
os.path.getmtime("/path/to/file")     # 修改时间戳
os.path.getatime("/path/to/file")     # 访问时间戳
os.path.getctime("/path/to/file")     # 创建时间戳
```

### 12.3 os.stat_result 常用属性

| 属性 | 说明 |
|------|------|
| `st_mode` | 文件类型和权限 |
| `st_ino` | inode 号 |
| `st_dev` | 设备号 |
| `st_nlink` | 硬链接数 |
| `st_uid` | 所有者用户 ID |
| `st_gid` | 所有者组 ID |
| `st_size` | 文件大小（字节） |
| `st_atime` | 最后访问时间 |
| `st_mtime` | 最后修改时间 |
| `st_ctime` | 创建/状态变更时间 |


# 第四部分：环境变量与进程信息

## 第十三章：环境变量操作

### 13.1 os.environ 字典

`os.environ` 是一个映射对象，包含当前进程的所有环境变量。

```python
import os

# 获取环境变量（键不存在会报错 KeyError）
home = os.environ["HOME"]

# 安全获取（键不存在返回 None 或默认值）
api_key = os.environ.get("API_KEY")
db_host = os.environ.get("DB_HOST", "localhost")

# 设置环境变量（仅当前进程有效）
os.environ["MY_VAR"] = "value"

# 删除环境变量
del os.environ["MY_VAR"]

# 检查是否存在
if "PATH" in os.environ:
    print("PATH 已设置")

# 遍历所有环境变量
for key, value in os.environ.items():
    print(f"{key}={value}")
```

### 13.2 os.getenv 和 os.putenv

```python
# os.getenv 是 os.environ.get 的便捷方式
value = os.getenv("HOME")
value = os.getenv("NOT_EXIST", "default")

# os.putenv 直接调用 C 库的 putenv
# ⚠️ 不推荐使用，因为不会更新 os.environ
# 推荐使用 os.environ[key] = value
```

### 13.3 实战：配置分离

```python
import os

# 从环境变量读取配置，提供默认值
config = {
    "db_host": os.environ.get("DB_HOST", "localhost"),
    "db_port": int(os.environ.get("DB_PORT", "5432")),
    "api_key": os.environ.get("API_KEY"),
    "debug": os.environ.get("DEBUG", "false").lower() == "true",
}

# 检查必需的环境变量
required = ["API_KEY", "SECRET_KEY"]
missing = [k for k in required if not os.environ.get(k)]
if missing:
    raise EnvironmentError(f"缺少环境变量: {', '.join(missing)}")
```


## 第十四章：进程与用户信息

### 14.1 进程标识

```python
import os

# 当前进程 ID
print(os.getpid())

# 父进程 ID
print(os.getppid())

# 进程组 ID（Unix）
print(os.getpgrp())

# 会话 ID（Unix）
print(os.getsid())
```

### 14.2 用户和组信息

```python
import os

# 当前用户 ID（Unix）
print(os.getuid())       # 真实用户 ID
print(os.geteuid())      # 有效用户 ID（用于权限检查）

# 当前组 ID（Unix）
print(os.getgid())       # 真实组 ID
print(os.getegid())      # 有效组 ID

# 当前用户所属的所有组（Unix）
print(os.getgroups())

# 当前登录用户名（跨平台）
print(os.getlogin())

# 用户名（Unix 推荐方式）
import getpass
print(getpass.getuser())
```


## 第十五章：系统信息获取

### 15.1 os.uname（Unix）

`os.uname()` 返回当前操作系统的识别信息，返回值包含五个属性。

```python
import os

info = os.uname()
print(info.sysname)    # 操作系统名（如 'Linux'）
print(info.nodename)   # 机器在网络上的名称
print(info.release)    # 操作系统发行信息（如 '5.15.0-91-generic'）
print(info.version)    # 操作系统版本信息
print(info.machine)    # 硬件标识符（如 'x86_64'）
```

> ⚠️ `os.uname()` 在 Windows 上不可用。跨平台方案：使用 `platform` 模块。

### 15.2 os.name 和 sys.platform

```python
import os
import sys

print(os.name)        # 'posix' / 'nt' / 'java'
print(sys.platform)   # 'linux' / 'darwin' / 'win32' / 'cygwin'

# 更详细的平台信息
import platform
print(platform.system())      # 'Linux' / 'Darwin' / 'Windows'
print(platform.release())     # 内核版本
print(platform.machine())     # 架构
print(platform.python_version())
```

### 15.3 终端尺寸

```python
import os

size = os.get_terminal_size()
print(size.columns)  # 终端列数
print(size.lines)    # 终端行数

# 指定文件描述符
size = os.get_terminal_size(0)  # stdin
```


# 第五部分：文件描述符与底层 I/O

## 第十六章：文件描述符基础

### 16.1 什么是文件描述符

文件描述符（File Descriptor）是一个由操作系统分配的非负整数，用于指代某个 I/O 通道（文件、管道、套接字等）。每个进程启动时，默认打开三个文件描述符：

| 描述符 | 名称 | 对应 |
|--------|------|------|
| 0 | stdin | 标准输入 |
| 1 | stdout | 标准输出 |
| 2 | stderr | 标准错误 |

```python
import os

# 获取文件对象的描述符
with open("file.txt", "r") as f:
    fd = f.fileno()
    print(fd)  # 通常从 3 开始

# 使用 os 模块直接操作描述符
os.write(1, b"Hello via stdout\n")   # 直接写入标准输出
os.write(2, b"Error message\n")      # 直接写入标准错误
```


## 第十七章：os.open 与 os.close

### 17.1 os.open

`os.open()` 打开文件并返回文件描述符，提供比内置 `open()` 更底层的控制。

```python
import os

# 基本打开（只读）
fd = os.open("file.txt", os.O_RDONLY)

# 打开并创建（读写）
fd = os.open("file.txt", os.O_RDWR | os.O_CREAT)

# 打开并追加
fd = os.open("file.txt", os.O_WRONLY | os.O_APPEND)

# 打开并截断
fd = os.open("file.txt", os.O_WRONLY | os.O_TRUNC)

# 关闭描述符
os.close(fd)
```

### 17.2 常用打开标志

| 标志 | 含义 |
|------|------|
| `os.O_RDONLY` | 只读 |
| `os.O_WRONLY` | 只写 |
| `os.O_RDWR` | 读写 |
| `os.O_CREAT` | 不存在则创建 |
| `os.O_EXCL` | 与 O_CREAT 同用，文件存在则失败 |
| `os.O_TRUNC` | 截断为 0 字节 |
| `os.O_APPEND` | 追加模式 |
| `os.O_NONBLOCK` | 非阻塞模式 |
| `os.O_SYNC` | 同步写入 |
| `os.O_DIRECTORY` | 必须为目录 |


## 第十八章：文件描述符的复制与重定向

### 18.1 os.dup 和 os.dup2

```python
import os

fd = os.open("file.txt", os.O_RDONLY)

# 复制描述符（新描述符与旧的共享文件偏移）
new_fd = os.dup(fd)

# 重定向描述符（将 new_fd 指向 fd 的目标）
os.dup2(fd, 1)  # 将标准输出重定向到 file.txt

# 关闭
os.close(fd)
os.close(new_fd)
```

### 18.2 实战：重定向标准输出到文件

```python
import os
import sys

# 保存原始 stdout
original_stdout_fd = os.dup(1)

# 打开文件并重定向
fd = os.open("output.log", os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
os.dup2(fd, 1)
os.close(fd)

print("这行会写入文件而不是终端")

# 恢复原始 stdout
os.dup2(original_stdout_fd, 1)
os.close(original_stdout_fd)

print("这行回到终端")
```


## 第十九章：os.fdopen 与文件对象转换

### 19.1 从描述符创建文件对象

`os.fdopen()` 从现有的文件描述符创建一个 Python 文件对象，在底层描述符上提供更高级的文件操作。

```python
import os

# 创建描述符
fd = os.open("example.txt", os.O_RDWR | os.O_CREAT)

# 转换为文件对象
with os.fdopen(fd, "r+") as f:
    f.write("Hello World\n")
    f.seek(0)
    print(f.read())
# with 退出时自动关闭文件对象和描述符
```

### 19.2 保留描述符

```python
# closefd=False：关闭文件对象时不关闭底层描述符
fd = os.open("data.txt", os.O_RDWR | os.O_CREAT)
f = os.fdopen(fd, "r+", closefd=False)
f.write("data\n")
f.close()  # 描述符仍然有效
os.write(fd, b"more data\n")
os.close(fd)  # 需要手动关闭
```

### 19.3 读写文件描述符

```python
import os

fd = os.open("file.txt", os.O_RDWR | os.O_CREAT)

# 写入
os.write(fd, b"Hello, World!\n")

# 移动偏移
os.lseek(fd, 0, os.SEEK_SET)  # 回到开头

# 读取
data = os.read(fd, 1024)
print(data)  # b'Hello, World!\n'

# 获取当前偏移
pos = os.lseek(fd, 0, os.SEEK_CUR)
print(pos)

os.close(fd)
```


# 第六部分：权限、属性与执行

## 第二十章：文件权限管理

### 20.1 os.chmod

```python
import os
import stat

# 使用八进制设置权限
os.chmod("file.txt", 0o755)   # rwxr-xr-x
os.chmod("file.txt", 0o644)   # rw-r--r--
os.chmod("file.txt", 0o600)   # rw-------

# 使用 stat 模块常量
os.chmod("file.txt", stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
# 等价于 0o700

# 递归修改目录权限
os.chmod("dir", 0o755)
for root, dirs, files in os.walk("dir"):
    for d in dirs:
        os.chmod(os.path.join(root, d), 0o755)
    for f in files:
        os.chmod(os.path.join(root, f), 0o644)
```

### 20.2 os.chown（Unix）

```python
import os

# 修改所有者和组（需要 root 权限）
os.chown("file.txt", uid=1000, gid=1000)

# 只改所有者
os.chown("file.txt", uid=1000, gid=-1)  # -1 表示不改

# 只改组
os.chown("file.txt", uid=-1, gid=1000)
```

### 20.3 os.umask

```python
import os

# 查看当前 umask
old_umask = os.umask(0)  # 临时设为 0，返回旧值
os.umask(old_umask)      # 恢复
print(oct(old_umask))    # 例如 0o022

# 设置 umask
os.umask(0o027)  # 新文件权限：666 - 027 = 640
```


## 第二十一章：文件属性与时间戳

### 21.1 os.utime

```python
import os
import time

# 设置访问和修改时间
now = time.time()
os.utime("file.txt", (now, now))

# 只设置修改时间
os.utime("file.txt", (os.path.getatime("file.txt"), now))

# 使用纳秒精度（Python 3.3+）
os.utime("file.txt", ns=(atime_ns, mtime_ns))
```

### 21.2 os.link 和 os.symlink

```python
import os

# 创建硬链接
os.link("source.txt", "hardlink.txt")

# 创建符号链接
os.symlink("target.txt", "symlink.txt")

# 读取符号链接的目标
target = os.readlink("symlink.txt")

# 判断是否是符号链接
os.path.islink("symlink.txt")
```

### 21.3 os.truncate

```python
import os

# 截断文件到指定大小
os.truncate("file.txt", 100)  # 保留前 100 字节
```


## 第二十二章：执行系统命令

### 22.1 os.system

```python
import os

# 执行系统命令（返回值是退出码）
exit_code = os.system("ls -la")
# ⚠️ 命令的输出直接打印到终端，无法捕获

# 检查是否成功
if os.system("ping -c 1 google.com") == 0:
    print("网络可达")
```

> ⚠️ `os.system()` 存在命令注入风险，不要拼接用户输入。推荐使用 `subprocess` 模块。

### 22.2 os.popen

```python
import os

# 执行命令并获取输出（返回文件对象）
with os.popen("ls -la") as f:
    output = f.read()
print(output)

# ⚠️ os.popen 同样有安全风险，且已被 subprocess 取代
```

### 22.3 推荐替代：subprocess

```python
import subprocess

# 安全执行命令（列表参数，不经过 shell）
result = subprocess.run(
    ["ls", "-la"],
    capture_output=True,
    text=True,
)
print(result.stdout)
print(result.returncode)

# 检查命令是否成功
subprocess.run(["ls", "-la"], check=True)
```


## 第二十三章：进程管理

### 23.1 os.fork（Unix）

```python
import os

pid = os.fork()

if pid == 0:
    # 子进程
    print(f"子进程 PID: {os.getpid()}, 父进程 PID: {os.getppid()}")
    os._exit(0)  # 子进程退出
else:
    # 父进程
    print(f"父进程 PID: {os.getpid()}, 子进程 PID: {pid}")
    os.waitpid(pid, 0)  # 等待子进程结束
```

> ⚠️ `os.fork()` 在 Windows 上不可用。跨平台方案：使用 `multiprocessing` 模块或 `subprocess`。

### 23.2 os.exec 系列

```python
import os

# 用新程序替换当前进程
os.execlp("ls", "ls", "-la")        # 在 PATH 中查找
os.execvp("python", ["python", "-c", "print('hi')"])
os.execle("/bin/ls", "ls", "-la", {"PATH": "/usr/bin"})

# 注意：exec 成功后不会返回，原进程被完全替换
```

### 23.3 os.spawn 系列

```python
import os

# 创建新进程（不替换当前进程）
pid = os.spawnlp(os.P_WAIT, "ls", "ls", "-la")
pid = os.spawnv(os.P_NOWAIT, "/bin/ls", ["ls", "-la"])
```

### 23.4 os.kill 和信号

```python
import os
import signal

# 发送信号给进程
os.kill(pid, signal.SIGTERM)   # 优雅终止
os.kill(pid, signal.SIGKILL)   # 强制终止

# 发送信号给进程组
os.killpg(pgid, signal.SIGTERM)

# 信号处理
def handler(signum, frame):
    print(f"收到信号 {signum}")

signal.signal(signal.SIGINT, handler)
```


# 第七部分：跨平台与最佳实践

## 第二十四章：os 与 pathlib 对比

### 24.1 核心差异

| 维度 | os.path | pathlib |
|------|---------|---------|
| 风格 | 过程式（函数） | 面向对象（类） |
| 路径表示 | 字符串 | Path 对象 |
| 拼接 | `os.path.join("a", "b")` | `Path("a") / "b"` |
| 跨平台 | 自动处理分隔符 | 自动处理分隔符 |
| 可读性 | 一般 | 更高 |
| 引入版本 | Python 2 | Python 3.4+ |

### 24.2 功能对照表

| os.path | pathlib |
|---------|---------|
| `os.path.join("a", "b")` | `Path("a") / "b"` |
| `os.path.abspath(p)` | `Path(p).resolve()` |
| `os.path.exists(p)` | `Path(p).exists()` |
| `os.path.isfile(p)` | `Path(p).is_file()` |
| `os.path.isdir(p)` | `Path(p).is_dir()` |
| `os.path.basename(p)` | `Path(p).name` |
| `os.path.dirname(p)` | `Path(p).parent` |
| `os.path.splitext(p)` | `Path(p).suffix` |
| `os.path.getsize(p)` | `Path(p).stat().st_size` |
| `os.listdir(d)` | `Path(d).iterdir()` |
| `os.mkdir(d)` | `Path(d).mkdir()` |
| `os.makedirs(d)` | `Path(d).mkdir(parents=True)` |
| `os.remove(f)` | `Path(f).unlink()` |
| `os.rmdir(d)` | `Path(d).rmdir()` |

### 24.3 选择建议

- **新项目**：优先使用 `pathlib`，代码更简洁、更易读
- **旧代码兼容**：保留 `os.path`
- **os 模块仍然需要**：环境变量、进程管理、文件描述符、权限设置等 pathlib 不覆盖的功能
- **性能敏感场景**：`os.path` 略快（pathlib 有对象创建开销）


## 第二十五章：跨平台注意事项

### 25.1 路径分隔符

```python
import os

# ✅ 正确：使用 os.path.join 或 pathlib
path = os.path.join("folder", "file.txt")

# ✅ 正确：使用 os.sep
path = f"folder{os.sep}file.txt"

# ❌ 错误：硬编码分隔符
path = "folder/file.txt"     # Windows 上可能出问题
path = "folder\\file.txt"    # Unix 上会出问题
```

### 25.2 平台专属函数

| 函数 | 可用平台 | 跨平台替代 |
|------|---------|-----------|
| `os.fork()` | Unix | `multiprocessing` / `subprocess` |
| `os.getuid()` | Unix | `getpass.getuser()` |
| `os.uname()` | Unix | `platform` 模块 |
| `os.startfile()` | Windows | `subprocess` + 系统命令 |
| `os.chown()` | Unix | 无直接替代 |
| `os.killpg()` | Unix | 无直接替代 |

### 25.3 换行符差异

```python
# 文本模式自动处理换行符
with open("file.txt", "r") as f:      # 自动转换 \r\n → \n
    content = f.read()

with open("file.txt", "w") as f:      # 自动转换 \n → \r\n（Windows）
    f.write("line\n")

# 二进制模式不转换
with open("file.txt", "rb") as f:
    content = f.read()  # 保留原始字节
```


## 第二十六章：常见陷阱与安全建议

### 26.1 from os import * 覆盖内置函数

```python
# ❌ 危险：覆盖内置 open
from os import *
f = open("file.txt")  # 这是 os.open，不是内置 open！

# ✅ 安全
import os
with open("file.txt") as f:  # 内置 open
    pass
```

### 26.2 os.system 命令注入

```python
import os

# ❌ 危险：用户输入直接拼接
user_input = "file.txt; rm -rf /"
os.system(f"cat {user_input}")  # 灾难性后果

# ✅ 安全：使用 subprocess + 列表参数
import subprocess
subprocess.run(["cat", user_input], check=True)
```

### 26.3 文件操作竞态条件

```python
import os

# ❌ 危险：检查和使用之间存在竞态
if os.path.exists("file.txt"):
    # 另一个进程可能在这里删除了文件
    with open("file.txt") as f:
        pass

# ✅ 安全：直接操作，捕获异常
try:
    with open("file.txt") as f:
        pass
except FileNotFoundError:
    print("文件不存在")
```

### 26.4 路径拼接不要用字符串拼接

```python
import os

# ❌ 错误
path = "folder" + "/" + "file.txt"

# ✅ 正确
path = os.path.join("folder", "file.txt")
from pathlib import Path
path = Path("folder") / "file.txt"
```

### 26.5 os.walk 中修改 dirnames 的影响

```python
for dirpath, dirnames, filenames in os.walk("/project"):
    # 这会阻止 os.walk 进入 .git 目录
    if ".git" in dirnames:
        dirnames.remove(".git")
    # 注意：修改 dirnames 只影响遍历，不修改磁盘
```

### 26.6 编码问题

```python
import os

# 获取系统默认编码
print(os.devnull)  # '/dev/null'（Unix）或 'nul'（Windows）

# 文件系统编码
import sys
print(sys.getfilesystemencoding())  # 通常 'utf-8'
print(sys.getdefaultencoding())     # 'utf-8'
```


## 第二十七章：速查小抄

### 文件与目录

```python
os.getcwd()                    # 当前工作目录
os.chdir(path)                 # 切换目录
os.mkdir(path)                 # 创建单级目录
os.makedirs(path, exist_ok=True)  # 递归创建目录
os.rmdir(path)                 # 删除空目录
os.remove(path)                # 删除文件
os.rename(src, dst)            # 重命名
os.replace(src, dst)           # 重命名（覆盖）
os.listdir(path)               # 列出目录内容
os.scandir(path)               # 高效列出目录
os.walk(path)                  # 递归遍历目录树
```

### 路径操作

```python
os.path.join(a, b, c)          # 拼接路径
os.path.abspath(path)          # 绝对路径
os.path.dirname(path)          # 目录部分
os.path.basename(path)         # 文件名部分
os.path.split(path)            # 拆分目录和文件名
os.path.splitext(path)         # 拆分扩展名
os.path.exists(path)           # 是否存在
os.path.isfile(path)           # 是否是文件
os.path.isdir(path)            # 是否是目录
os.path.getsize(path)          # 文件大小
os.path.getmtime(path)         # 修改时间
```

### 环境变量

```python
os.environ["KEY"]              # 获取（不存在报错）
os.environ.get("KEY", default) # 安全获取
os.environ["KEY"] = "value"    # 设置
del os.environ["KEY"]          # 删除
os.getenv("KEY")               # 获取
```

### 进程与系统

```python
os.getpid()                    # 当前进程 ID
os.getppid()                   # 父进程 ID
os.uname()                     # 系统信息（Unix）
os.name                        # 'posix' / 'nt'
os.getlogin()                  # 当前用户名
os.get_terminal_size()         # 终端尺寸
```

### 文件描述符

```python
os.open(path, flags)           # 打开（返回 fd）
os.close(fd)                   # 关闭
os.read(fd, n)                 # 读取 n 字节
os.write(fd, data)             # 写入
os.lseek(fd, pos, whence)      # 移动偏移
os.dup(fd)                     # 复制 fd
os.dup2(old, new)              # 重定向 fd
os.fdopen(fd, mode)            # fd → 文件对象
```

### 权限与属性

```python
os.chmod(path, mode)           # 修改权限
os.chown(path, uid, gid)       # 修改所有者（Unix）
os.umask(mask)                 # 设置 umask
os.stat(path)                  # 获取状态
os.utime(path, times)          # 修改时间戳
os.link(src, dst)              # 硬链接
os.symlink(src, dst)           # 符号链接
os.readlink(path)              # 读取链接目标
```

### 执行命令

```python
os.system("command")           # 执行命令（不推荐）
os.popen("command")            # 执行并获取输出（不推荐）
# 推荐使用 subprocess 模块
```

### 跨平台判断

```python
os.name == "posix"             # Unix-like
os.name == "nt"                # Windows
import sys
sys.platform == "linux"        # Linux
sys.platform == "darwin"       # macOS
sys.platform == "win32"        # Windows
```


## 参考资料

- **官方文档（英文）**: https://docs.python.org/3/library/os.html
- **官方文档（中文）**: https://docs.python.org/zh-cn/3/library/os.html
- **os.path 文档**: https://docs.python.org/3/library/os.path.html
- **pathlib 文档**: https://docs.python.org/3/library/pathlib.html
- **shutil 文档**: https://docs.python.org/3/library/shutil.html
- **tempfile 文档**: https://docs.python.org/3/library/tempfile.html
- **subprocess 文档**: https://docs.python.org/3/library/subprocess.html
- **Real Python os 教程**: https://realpython.com/python-os-module/
- **Codecademy os 模块**: https://www.codecademy.com/resources/docs/python/os-module