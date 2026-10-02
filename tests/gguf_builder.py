"""测试用：生成合法的最小 GGUF 文件。

为什么需要
----------
旧测试用 ``path.write_bytes(b"x" * 1024)`` 造假模型文件。在「读取真实 GGUF
元数据」的实现下，这种文件会被正确识别为无效而跳过，因此测试必须构造
**结构合法**的 GGUF 头部。

这里只写 KV 区（``tensor_count = 0``），不写张量数据 —— 足以覆盖元数据解析、
分类、显存估算与挑选逻辑，而文件体积只有几百字节。
"""

from __future__ import annotations

import struct
from pathlib import Path

# 与 src/llm/gguf.py 保持一致的类型枚举
STRING = 8
UINT32 = 4
INT32 = 5
BOOL = 7
ARRAY = 9


def _enc_string(text: str) -> bytes:
    data = text.encode("utf-8")
    return struct.pack("<Q", len(data)) + data


def _value_type(value) -> int:
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, str):
        return STRING
    if isinstance(value, int):
        return INT32 if value < 0 else UINT32
    if isinstance(value, (list, tuple)):
        return ARRAY
    raise TypeError(f"不支持的元数据类型: {type(value)!r}")


def _enc_value(value) -> bytes:
    if isinstance(value, bool):
        return struct.pack("<?", value)
    if isinstance(value, str):
        return _enc_string(value)
    if isinstance(value, int):
        return struct.pack("<i" if value < 0 else "<I", value)
    if isinstance(value, (list, tuple)):
        items = list(value)
        if not items:
            return struct.pack("<I", STRING) + struct.pack("<Q", 0)
        elem_type = _value_type(items[0])
        out = struct.pack("<I", elem_type) + struct.pack("<Q", len(items))
        for item in items:
            out += _enc_value(item)
        return out
    raise TypeError(f"不支持的元数据值: {value!r}")


def write_gguf(
    path: Path,
    metadata: dict,
    *,
    version: int = 3,
    tensor_count: int = 0,
    magic: bytes = b"GGUF",
) -> Path:
    """写一个只含 KV 区的合法 GGUF 文件。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    out = bytearray()
    out += magic
    out += struct.pack("<I", version)
    out += struct.pack("<Q", tensor_count)
    out += struct.pack("<Q", len(metadata))

    for key, value in metadata.items():
        out += _enc_string(key)
        out += struct.pack("<I", _value_type(value))
        out += _enc_value(value)

    path.write_bytes(bytes(out))
    return path


CHAT_TEMPLATE = (
    "{% for message in messages %}"
    "{{ message['role'] }}: {{ message['content'] }}\n"
    "{% endfor %}"
)


def chat_metadata(
    *,
    arch: str = "llama",
    name: str = "Test-Chat-Model",
    size_label: str = "7B",
    context_length: int = 8192,
    block_count: int = 32,
    embedding_length: int = 4096,
    head_count: int = 32,
    head_count_kv: int = 8,
    chat_template: str | None = CHAT_TEMPLATE,
    tags: list[str] | None = None,
    **extra,
) -> dict:
    """构造一个「通用对话模型」的元数据。

    架构相关键使用 ``<arch>.xxx`` 前缀，与真实文件一致 —— 这正好覆盖
    「带架构前缀的键必须被识别」这条曾经出过 bug 的路径。
    """
    meta: dict = {
        "general.architecture": arch,
        "general.name": name,
        "general.size_label": size_label,
        f"{arch}.context_length": context_length,
        f"{arch}.block_count": block_count,
        f"{arch}.embedding_length": embedding_length,
        f"{arch}.attention.head_count": head_count,
        f"{arch}.attention.head_count_kv": head_count_kv,
    }

    if chat_template is not None:
        meta["tokenizer.chat_template"] = chat_template

    if tags is not None:
        meta["general.tags"] = list(tags)

    meta.update(extra)
    return meta


__all__ = [
    "ARRAY",
    "BOOL",
    "CHAT_TEMPLATE",
    "INT32",
    "STRING",
    "UINT32",
    "chat_metadata",
    "write_gguf",
]
