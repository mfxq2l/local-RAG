"""GGUF 文件头解析。

为什么需要
----------
仅凭文件名无法可靠判断一个 gguf 到底是什么：量化方式、参数量、上下文长度、
是否支持对话模板、是否是多模态投影器，都写在文件头的元数据里。本模块直接读
GGUF 头部，得到**可信**的模型身份。

实现要点
--------
* GGUF 的 KV 区里可能包含巨大的数组（例如 25 万条 tokenizer 词表）。
  这里对数组做**按字节跳过**，不逐条解码，因此解析很快。
* 结果按 ``(路径, 大小, mtime)`` 缓存到 ``data/models_cache.json``，
  重复扫描近乎零成本。
* 解析失败一律返回 ``None``，绝不因为一个坏文件中断整个扫描。
"""

from __future__ import annotations

import json
import re
import struct
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.config import DATA_DIR


# GGUF 元数据类型枚举
(
    _U8, _I8, _U16, _I16, _U32, _I32, _F32, _BOOL,
    _STRING, _ARRAY, _U64, _I64, _F64,
) = range(13)

_FIXED_FMT: dict[int, str] = {
    _U8: "<B", _I8: "<b", _U16: "<H", _I16: "<h",
    _U32: "<I", _I32: "<i", _F32: "<f", _BOOL: "<?",
    _U64: "<Q", _I64: "<q", _F64: "<d",
}

_FIXED_SIZE: dict[int, int] = {
    t: struct.calcsize(f) for t, f in _FIXED_FMT.items()
}

# 我们关心的元数据键（精确匹配）
_INTERESTING = {
    "general.architecture",
    "general.name",
    "general.basename",
    "general.size_label",
    "general.file_type",
    "general.quantized_by",
    "general.license",
    "general.tags",
    "general.type",
    "general.base_model.0.name",
    "general.base_model.0.organization",
    "general.base_model.0.repo_url",
    "tokenizer.chat_template",
    "tokenizer.ggml.model",
    "tokenizer.ggml.bos_token_id",
    "tokenizer.ggml.eos_token_id",
}

# 架构相关参数使用**后缀**匹配，因为键名带架构前缀，例如：
#   gemma4.context_length
#   qwen35.block_count
#   hunyuan-dense.attention.head_count
#
# 注意顺序无关紧要，但 head_count 与 head_count_kv 必须区分：
# "...attention.head_count_kv" 不会命中 ".attention.head_count"。
_INTERESTING_SUFFIXES = (
    ".context_length",
    ".block_count",
    ".embedding_length",
    ".attention.head_count",
    ".attention.head_count_kv",
    ".attention.key_length",
    ".attention.value_length",
)


def _is_interesting(key: str) -> bool:
    """判断某个元数据键是否是我们需要的。"""
    if key in _INTERESTING:
        return True
    return key.endswith(_INTERESTING_SUFFIXES)

# 文件名里常见的量化标记
_QUANT_RE = re.compile(
    r"(UD-)?"
    r"(I?Q\d+(?:_[A-Z0-9]+)*"
    r"|BF16|F16|FP16|F32|FP32|Q8_0)",
    re.IGNORECASE,
)

# 缓存版本：解析逻辑变更时必须递增，否则会命中字段不全的旧缓存
_VERSION = 2
_CACHE_PATH = DATA_DIR / "models_cache.json"
_cache_lock = threading.Lock()


@dataclass
class GgufMeta:
    """从一个 GGUF 文件读出的关键元数据。"""

    path: str
    size_bytes: int

    architecture: str = ""
    name: str = ""
    basename: str = ""
    size_label: str = ""

    context_length: int = 0
    block_count: int = 0
    embedding_length: int = 0
    head_count: int = 0
    head_count_kv: int = 0
    key_length: int = 0
    value_length: int = 0

    has_chat_template: bool = False
    chat_template_chars: int = 0

    base_name: str = ""
    base_organization: str = ""
    quantized_by: str = ""
    license: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def path_obj(self) -> Path:
        return Path(self.path)

    @property
    def file_name(self) -> str:
        return Path(self.path).name

    @property
    def size_gb(self) -> float:
        return self.size_bytes / 1024**3

    @property
    def quantization(self) -> str:
        """从文件名推断量化方式（文件名通常比 file_type 更直观）。"""
        match = _QUANT_RE.search(self.file_name)
        return match.group(0).upper() if match else "?"

    @property
    def parameter_count_b(self) -> float | None:
        """从 size_label 解析参数量（亿/十亿）。"""
        text = (self.size_label or "").upper().strip()
        match = re.search(r"([\d.]+)\s*B", text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    def to_dict(self) -> dict:
        data = asdict(self)
        data["quantization"] = self.quantization
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "GgufMeta":
        allowed = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in data.items() if k in allowed})


# ----------------------------------------------------------------------
# 底层读取
# ----------------------------------------------------------------------


class _Reader:
    """带跳过能力的读取器。"""

    def __init__(self, fh) -> None:
        self.fh = fh

    def raw(self, n: int) -> bytes:
        data = self.fh.read(n)
        if len(data) != n:
            raise EOFError("GGUF 文件提前结束")
        return data

    def scalar(self, fmt: str):
        return struct.unpack(fmt, self.raw(struct.calcsize(fmt)))[0]

    def string(self) -> str:
        length = self.scalar("<Q")
        return self.raw(length).decode("utf-8", errors="replace")

    def skip_string(self) -> None:
        length = self.scalar("<Q")
        self.fh.seek(length, 1)

    def skip_value(self, vtype: int, depth: int = 0) -> None:
        """按字节跳过某个值，不解码。"""
        if vtype == _STRING:
            self.skip_string()
            return

        if vtype == _ARRAY:
            if depth > 3:
                raise ValueError("数组嵌套过深")
            elem_type = self.scalar("<I")
            count = self.scalar("<Q")

            fixed = _FIXED_SIZE.get(elem_type)
            if fixed is not None:
                self.fh.seek(fixed * count, 1)
                return

            if elem_type == _STRING:
                for _ in range(count):
                    self.skip_string()
                return

            # 元素本身是数组：只能逐个跳过
            for _ in range(count):
                self.skip_value(elem_type, depth + 1)
            return

        fixed = _FIXED_SIZE.get(vtype)
        if fixed is None:
            raise ValueError(f"未知的 GGUF 值类型: {vtype}")
        self.fh.seek(fixed, 1)

    def read_value(self, vtype: int, depth: int = 0):
        """读取值；数组只保留前若干项以控制内存。"""
        if vtype == _STRING:
            return self.string()

        if vtype == _ARRAY:
            elem_type = self.scalar("<I")
            count = self.scalar("<Q")

            keep = 8
            items = []
            for index in range(count):
                if index < keep:
                    items.append(self.read_value(elem_type, depth + 1))
                else:
                    self.skip_value(elem_type, depth + 1)

            if elem_type == _STRING:
                return items  # tags 之类
            return items

        fmt = _FIXED_FMT.get(vtype)
        if fmt is None:
            raise ValueError(f"未知的 GGUF 值类型: {vtype}")
        return self.scalar(fmt)


def read_gguf(path: str | Path) -> GgufMeta | None:
    """读取单个 GGUF 文件的元数据。失败返回 ``None``。"""
    path = Path(path)

    try:
        stat = path.stat()
    except OSError:
        return None

    meta = GgufMeta(path=str(path), size_bytes=stat.st_size)

    try:
        with path.open("rb") as fh:
            reader = _Reader(fh)

            if reader.raw(4) != b"GGUF":
                return None

            version = reader.scalar("<I")
            if version < 2:
                return None

            reader.scalar("<Q")  # tensor_count
            kv_count = reader.scalar("<Q")

            for _ in range(kv_count):
                key = reader.string()
                value_type = reader.scalar("<I")

                if not _is_interesting(key):
                    reader.skip_value(value_type)
                    continue

                value = reader.read_value(value_type)
                _apply(meta, key, value)

    except Exception:  # noqa: BLE001
        # 坏文件不应中断整个扫描
        return None

    # 没有 general.architecture 的文件无法用于任何估算，视为无效
    return meta if meta.architecture else None


def _apply(meta: GgufMeta, key: str, value) -> None:
    """把元数据写进 :class:`GgufMeta`。"""
    if key == "general.architecture":
        meta.architecture = str(value)
    elif key == "general.name":
        meta.name = str(value)
    elif key == "general.basename":
        meta.basename = str(value)
    elif key == "general.size_label":
        meta.size_label = str(value)
    elif key == "general.quantized_by":
        meta.quantized_by = str(value)
    elif key == "general.license":
        meta.license = str(value)
    elif key == "general.tags":
        meta.tags = [str(v) for v in value] if isinstance(value, list) else []
    elif key == "general.base_model.0.name":
        meta.base_name = str(value)
    elif key == "general.base_model.0.organization":
        meta.base_organization = str(value)
    elif key == "tokenizer.chat_template":
        text = str(value)
        meta.has_chat_template = bool(text.strip())
        meta.chat_template_chars = len(text)
    elif key.endswith(".context_length"):
        meta.context_length = int(value)
    elif key.endswith(".block_count"):
        meta.block_count = int(value)
    elif key.endswith(".embedding_length"):
        meta.embedding_length = int(value)
    elif key.endswith(".attention.head_count"):
        meta.head_count = int(value)
    elif key.endswith(".attention.head_count_kv"):
        meta.head_count_kv = int(value)
    elif key.endswith(".attention.key_length"):
        meta.key_length = int(value)
    elif key.endswith(".attention.value_length"):
        meta.value_length = int(value)


# ----------------------------------------------------------------------
# 带缓存的批量扫描
# ----------------------------------------------------------------------


def _cache_key(path: Path, stat) -> str:
    return f"{path.resolve()}|{stat.st_size}|{int(stat.st_mtime)}"


def _load_cache() -> dict:
    try:
        if _CACHE_PATH.exists():
            data = json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
            if data.get("version") == _VERSION:
                return data.get("entries", {})
    except Exception:  # noqa: BLE001
        pass
    return {}


def _save_cache(entries: dict) -> None:
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(
            json.dumps(
                {"version": _VERSION, "entries": entries},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except Exception:  # noqa: BLE001
        pass


def scan_directory(
    directory: str | Path,
    *,
    recursive: bool = True,
    use_cache: bool = True,
) -> list[GgufMeta]:
    """扫描目录下的全部 GGUF 文件并读取元数据。

    Args:
        directory: 目录。
        recursive: 是否递归子目录。
        use_cache: 是否使用磁盘缓存（按 mtime/size 失效）。
    """
    directory = Path(directory)

    if not directory.is_dir():
        return []

    pattern = "**/*.gguf" if recursive else "*.gguf"
    files = sorted(
        (p for p in directory.glob(pattern) if p.is_file()),
        key=lambda p: -p.stat().st_size if p.exists() else 0,
    )

    cache = _load_cache() if use_cache else {}
    new_cache: dict = {}
    results: list[GgufMeta] = []

    for path in files:
        try:
            stat = path.stat()
        except OSError:
            continue

        key = _cache_key(path, stat)

        cached = cache.get(key)
        if cached is not None:
            meta = GgufMeta.from_dict(cached)
            results.append(meta)
            new_cache[key] = cached
            continue

        meta = read_gguf(path)
        if meta is not None:
            results.append(meta)
            new_cache[key] = meta.to_dict()

    if use_cache:
        with _cache_lock:
            _save_cache(new_cache)

    return results


__all__ = ["GgufMeta", "read_gguf", "scan_directory"]
