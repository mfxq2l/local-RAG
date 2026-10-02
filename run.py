"""项目统一入口。

为什么需要这个文件
------------------
本项目自带的是 **embedded Python**（``runtime/python3.12``），其
``python312._pth`` 显式固定了 ``sys.path``，导致两个常见用法都失效：

* ``python -m src.cli``  → ModuleNotFoundError: No module named 'src'
* ``set PYTHONPATH=...`` → 被 ``._pth`` 直接忽略

只有「以脚本方式运行」时 ``sys.path[0]`` 才等于脚本所在目录。
因此把入口收敛到本文件（位于项目根目录），所有子命令都从这里分发：

    runtime\\python3.12\\python.exe run.py serve
    runtime\\python3.12\\python.exe run.py index --rebuild
    runtime\\python3.12\\python.exe run.py ask "nmap -sS 是什么"
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# ---------------------------------------------------------------------------
# 控制台编码
#
# Windows 控制台默认是 GBK(936)，直接输出中文会乱码。
# 这里统一把标准流切到 UTF-8；配套的 .bat 会先 `chcp 65001`。
#
# stdin 也必须处理：从管道（例如 `... | python run.py chat`）读入非 UTF-8
# 字节时，Python 曾产生**孤立代理字符**（\udcXX），后续 json 编码会直接抛
# UnicodeEncodeError 把对话打断。errors="replace" 可避免崩溃。
# ---------------------------------------------------------------------------

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

try:
    sys.stdin.reconfigure(errors="replace")  # type: ignore[union-attr]
except (AttributeError, ValueError):
    pass


from src.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
