"""生成式模型清单（catalog）。

解决的问题
----------
模型目录里往往混着好几种东西：通用对话模型、翻译专用模型、embedding 模型、
视觉投影器（mmproj）、多 token 预测头（mtp）。仅凭文件名挑选很容易出错，
历史上就出现过「兜底取体积最大的 gguf」从而选中 30B 模型（显存装不下）
的情况。

本模块基于 :mod:`src.llm.gguf` 读出的**真实元数据**：

1. **分类**：chat / translation / embedding / vision / base / unknown
2. **显存估算**：权重 + KV cache + 预留（embedding 模型常驻）
3. **排序与挑选**：项目自带目录优先 → 偏好关键字 → 显存可容纳 → 体积
4. **持久化选择**：``run.py models --set <名字>`` 写入 ``data/llm_selection.json``

只依赖标准库，不做任何模型加载。
"""

from __future__ import annotations

import json
import re
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path

from src.config import DATA_DIR, LLM_CONFIG, LlmConfig
from src.llm.gguf import GgufMeta, read_gguf, scan_directory


# ----------------------------------------------------------------------
# 分类
# ----------------------------------------------------------------------

KIND_CHAT = "chat"                # 通用对话（instruct）
KIND_TRANSLATION = "translation"  # 翻译专用
KIND_EMBEDDING = "embedding"      # 向量模型
KIND_VISION = "vision"            # 视觉投影器 mmproj / clip
KIND_BASE = "base"                # 无对话模板的基座模型
KIND_UNKNOWN = "unknown"

KIND_LABELS = {
    KIND_CHAT: "对话",
    KIND_TRANSLATION: "翻译",
    KIND_EMBEDDING: "向量",
    KIND_VISION: "视觉投影",
    KIND_BASE: "基座",
    KIND_UNKNOWN: "未知",
}

# 只有这些类型能用于问答
CHAT_CAPABLE_KINDS = {KIND_CHAT, KIND_TRANSLATION}

# 这些架构**只是投影器/编码器**，不能独立生成文本
_PROJECTOR_ARCHS = {"clip", "mtmd", "siglip", "whisper"}

# 这些架构是 embedding 模型，不能做生成
_EMBEDDING_ARCHS = {
    "bert", "nomic-bert", "nomic-bert-moe", "jina-bert-v2",
    "jina-bert-v3", "bge", "bge-m3", "gte", "qwen3-embedding",
}

# 注意：qwen2vl / llava / omni 这类**多模态对话模型**不在此列。
# 它们虽然也吃图片，但本身是能对话的主模型，只要带 chat template
# 就应当归为 chat，否则会被错误地从问答候选里剔除。
_AUX_PREFIXES = ("mmproj-", "mtp-")

# 形如 719b5158bed2e3f88829e1d1509a036fe7edac7d 的“名字”其实是提交哈希
_HASH_NAME_RE = re.compile(r"[0-9a-f]{32,}", re.IGNORECASE)


# ----------------------------------------------------------------------
# 条目
# ----------------------------------------------------------------------


@dataclass
class ModelEntry:
    """清单中的一个模型。"""

    path: str
    file_name: str
    size_gb: float

    architecture: str
    name: str
    size_label: str
    quantization: str

    # 模型**自身支持**的最大上下文
    context_length: int = 0
    # 实际按配置运行使用的上下文（用于显存估算）
    effective_context: int = 0

    block_count: int = 0
    embedding_length: int = 0
    head_count: int = 0
    head_count_kv: int = 0
    has_chat_template: bool = False
    tags: list[str] = field(default_factory=list)
    base_organization: str = ""
    base_name: str = ""

    kind: str = KIND_UNKNOWN
    directory_priority: int = 99

    # 被 RAG_LLM_EXCLUDE 排除（不会出现在可选列表里）
    excluded: bool = False
    excluded_reason: str = ""

    # 显存估算（GB）
    weights_gb: float = 0.0
    kv_cache_gb: float = 0.0
    total_gb: float = 0.0
    fits_vram: bool = True

    @property
    def display_name(self) -> str:
        """展示名。

        个别模型的 ``general.name`` 是一串提交哈希（打包时没写名字），
        这种直接用文件名主干更易读。
        """
        raw = (self.name or "").strip()

        if raw and not _HASH_NAME_RE.fullmatch(raw):
            return raw

        return Path(self.file_name).stem

    @property
    def label(self) -> str:
        """人类可读的一行标识。"""
        parts = [self.display_name]
        if self.size_label:
            parts.append(self.size_label)
        if self.quantization and self.quantization != "?":
            parts.append(self.quantization)
        return " · ".join(parts)

    @property
    def is_chat_capable(self) -> bool:
        return self.kind in CHAT_CAPABLE_KINDS and not self.excluded

    def to_dict(self) -> dict:
        data = asdict(self)
        data["label"] = self.label
        data["kind_label"] = KIND_LABELS.get(self.kind, self.kind)
        data["is_chat_capable"] = self.is_chat_capable
        return data


# ----------------------------------------------------------------------
# 估算与分类
# ----------------------------------------------------------------------


def estimate_kv_cache_gb(
    meta: GgufMeta,
    context_length: int,
    bytes_per_element: int = 2,
) -> float:
    """估算 KV cache 占用（GB）。

    KV = 2（K 与 V）× 层数 × KV 头数 × 每头维度 × 上下文长度 × 元素字节数

    每头维度优先取元数据里的 ``attention.key_length``，
    否则回退到 ``embedding_length / head_count``。
    """
    if not (meta.block_count and meta.head_count_kv and context_length):
        return 0.0

    head_dim = meta.key_length
    if not head_dim and meta.head_count:
        head_dim = max(1, meta.embedding_length // meta.head_count)

    if not head_dim:
        return 0.0

    total_bytes = (
        2
        * meta.block_count
        * meta.head_count_kv
        * head_dim
        * context_length
        * bytes_per_element
    )

    return total_bytes / 1024**3


def classify(meta: GgufMeta) -> str:
    """判断模型类型。"""
    name = meta.file_name.lower()
    arch = (meta.architecture or "").lower()
    tags = {t.lower() for t in meta.tags}

    # 投影器 / 辅助文件优先判断
    if name.startswith(_AUX_PREFIXES) or arch in _PROJECTOR_ARCHS:
        return KIND_VISION

    if arch in _EMBEDDING_ARCHS or "embedding" in tags:
        return KIND_EMBEDDING

    if "translation" in tags:
        return KIND_TRANSLATION

    # 带对话模板的主模型（含多模态对话模型）→ 可用于问答
    if meta.has_chat_template:
        return KIND_CHAT

    # 没有对话模板：多半是基座模型，不能直接用于问答
    return KIND_BASE


def is_excluded(meta: GgufMeta, patterns: tuple[str, ...]) -> str:
    """判断是否命中排除列表，返回命中的关键字（未命中返回空串）。"""
    haystack = f"{meta.file_name} {meta.name} {meta.base_name}".lower()

    for pattern in patterns:
        pattern = pattern.strip()
        if pattern and pattern.lower() in haystack:
            return pattern

    return ""


def build_entry(
    meta: GgufMeta,
    *,
    directory_priority: int = 99,
    context_length: int | None = None,
    reserve_gb: float = 0.0,
    vram_budget_gb: float = 8.0,
    exclude_patterns: tuple[str, ...] = (),
) -> ModelEntry:
    """把 GGUF 元数据转成清单条目（含显存估算）。"""
    capability = meta.context_length or 8192
    effective = context_length or min(capability, LLM_CONFIG.context_size)

    kv_gb = estimate_kv_cache_gb(meta, effective)
    weights_gb = meta.size_gb

    matched = is_excluded(meta, exclude_patterns)

    entry = ModelEntry(
        path=meta.path,
        file_name=meta.file_name,
        size_gb=meta.size_gb,
        architecture=meta.architecture,
        name=meta.name or meta.base_name or Path(meta.file_name).stem,
        size_label=meta.size_label,
        quantization=meta.quantization,
        context_length=capability,
        effective_context=effective,
        block_count=meta.block_count,
        embedding_length=meta.embedding_length,
        head_count=meta.head_count,
        head_count_kv=meta.head_count_kv,
        has_chat_template=meta.has_chat_template,
        tags=list(meta.tags),
        base_organization=meta.base_organization,
        base_name=meta.base_name,
        kind=classify(meta),
        directory_priority=directory_priority,
        excluded=bool(matched),
        excluded_reason=(
            f"命中排除规则 RAG_LLM_EXCLUDE={matched}" if matched else ""
        ),
    )

    entry.weights_gb = round(weights_gb, 2)
    entry.kv_cache_gb = round(kv_gb, 2)
    entry.total_gb = round(weights_gb + kv_gb, 2)
    entry.fits_vram = entry.total_gb + reserve_gb <= vram_budget_gb

    return entry


# ----------------------------------------------------------------------
# 扫描
# ----------------------------------------------------------------------

_catalog_lock = threading.Lock()
_catalog_cache: dict[str, list[ModelEntry]] = {}


def build_catalog(
    config: LlmConfig | None = None,
    *,
    force: bool = False,
    use_gguf_cache: bool = True,
) -> list[ModelEntry]:
    """扫描全部配置目录，返回模型清单。

    结果按 ``(目录优先级, 是否可对话, 显存是否够, 偏好关键字, 体积)`` 排序，
    因此 ``catalog[0]`` 就是「最应该用」的那个。

    两处后处理：

    * **去重**：同一模型可能同时存在于项目目录与外部模型库（文件同名同大小），
      只保留优先级最高的那一份，避免列表里重复出现。
    * **排除**：命中 ``RAG_LLM_EXCLUDE`` 的模型标记 ``excluded=True``，
      :func:`chat_models` 与默认选择都会跳过它们。
    """
    config = config or LLM_CONFIG

    cache_key = (
        "|".join(str(d) for d in config.model_dirs)
        + f"|ctx={config.context_size}"
        + f"|pref={','.join(config.preferred_models)}"
        + f"|excl={','.join(config.excluded_models)}"
        + f"|vram={config.vram_budget_gb}-{config.vram_reserve_gb}"
    )

    if not force:
        with _catalog_lock:
            cached = _catalog_cache.get(cache_key)
        if cached is not None:
            return list(cached)

    entries: list[ModelEntry] = []

    for priority, directory in enumerate(config.model_dirs):
        metas = scan_directory(directory, use_cache=use_gguf_cache)

        for meta in metas:
            entries.append(
                build_entry(
                    meta,
                    directory_priority=priority,
                    context_length=min(
                        config.context_size,
                        meta.context_length or config.context_size,
                    ),
                    reserve_gb=config.vram_reserve_gb,
                    vram_budget_gb=config.vram_budget_gb,
                    exclude_patterns=config.excluded_models,
                )
            )

    preferred = config.preferred_models
    entries.sort(key=lambda e: _ranking_key(e, preferred))

    # 去重：同名同大小视为同一模型，保留排序靠前（目录优先级更高）的那份
    deduped: list[ModelEntry] = []
    seen: set[tuple[str, int]] = set()

    for entry in entries:
        fingerprint = (entry.file_name.lower(), int(entry.size_gb * 1024))
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        deduped.append(entry)

    with _catalog_lock:
        _catalog_cache[cache_key] = list(deduped)

    return deduped


def _preference_rank(entry: ModelEntry, preferred: tuple[str, ...]) -> int:
    """越小越优先；未命中返回一个大值。"""
    haystack = f"{entry.file_name} {entry.name}".lower()

    for index, keyword in enumerate(preferred):
        if keyword.lower() in haystack:
            return index

    return len(preferred) + 1


def _ranking_key(entry: ModelEntry, preferred: tuple[str, ...]):
    """排序键：项目自带目录 → **纯对话优先** → 显存可容纳 → 偏好关键字 → 体积。

    注意这里**不使用**全局 LLM_CONFIG，而是用调用方传入的 preferred，
    这样 ``build_catalog(custom_config)`` 的结果对自定义配置也是自洽的。

    ``kind`` 的排序是必要的：翻译模型（Hy-MT2）同样带 chat template、
    同样"可对话"，但它不是通用助手。若不加区分，它可能被自动选为默认模型，
    从而给出很差的问答结果。
    """
    kind_rank = {
        KIND_CHAT: 0,
        KIND_TRANSLATION: 1,
    }.get(entry.kind, 2)

    return (
        entry.directory_priority,          # 项目自带目录优先
        kind_rank,                          # 纯对话 > 翻译 > 其它
        0 if entry.fits_vram else 1,        # 显存装得下的优先
        _preference_rank(entry, preferred),
        -entry.size_gb,                     # 同类里大的通常更强
    )


def chat_models(entries: list[ModelEntry] | None = None) -> list[ModelEntry]:
    """可用于问答的模型。"""
    entries = entries if entries is not None else build_catalog()
    return [e for e in entries if e.is_chat_capable]


# ----------------------------------------------------------------------
# 视觉模型配对
# ----------------------------------------------------------------------

# 投影器文件名末尾的量化标记，配对时需要剥掉
_MMPROJ_QUANT_RE = re.compile(
    r"-(BF16|F16|FP16|F32|FP32|Q8_0|Q4_[A-Z0-9_]+|Q5_[A-Z0-9_]+)$",
    re.IGNORECASE,
)


def projector_for(model_path: str | Path) -> Path | None:
    """返回某个模型配对的视觉投影器（mmproj）路径；没有则 ``None``。"""
    try:
        target = Path(model_path).resolve()
    except Exception:  # noqa: BLE001
        return None

    for main, projector in vision_pairs():
        try:
            if Path(main.path).resolve() == target:
                return Path(projector.path)
        except Exception:  # noqa: BLE001
            continue

    return None


def _projector_key(entry: ModelEntry) -> str:
    """从 mmproj 文件名提取主模型关键字。

    ``mmproj-gemma-4-E2B-it-BF16.gguf`` -> ``gemma-4-e2b-it``
    """
    stem = Path(entry.file_name).stem

    if stem.lower().startswith("mmproj-"):
        stem = stem[len("mmproj-"):]

    return _MMPROJ_QUANT_RE.sub("", stem).lower()


def vision_pairs(
    entries: list[ModelEntry] | None = None,
) -> list[tuple[ModelEntry, ModelEntry]]:
    """把视觉投影器（mmproj）与它对应的主模型配对。

    约定：``mmproj-<主模型名>-<量化>.gguf`` 配 ``<主模型名>-...gguf``。

    Returns:
        ``[(主模型, 投影器), ...]``，按主模型的可对话程度与体积排序。
    """
    entries = entries if entries is not None else build_catalog()

    projectors = [
        e
        for e in entries
        if e.file_name.lower().startswith("mmproj-")
    ]

    candidates = [
        e for e in entries
        if not e.file_name.lower().startswith(("mmproj-", "mtp-"))
        and not e.excluded
    ]

    pairs: list[tuple[ModelEntry, ModelEntry]] = []

    for projector in projectors:
        key = _projector_key(projector)
        if not key:
            continue

        matched = [
            c for c in candidates
            if Path(c.file_name).stem.lower().startswith(key)
        ]

        if not matched:
            continue

        # 优先纯对话模型，其次按体积
        matched.sort(
            key=lambda e: (
                0 if e.kind == KIND_CHAT else 1,
                -e.size_gb,
            )
        )

        pairs.append((matched[0], projector))

    return pairs


# ----------------------------------------------------------------------
# 查找
# ----------------------------------------------------------------------


def find_model(
    query: str,
    entries: list[ModelEntry] | None = None,
) -> ModelEntry | None:
    """按序号 / 文件名 / 名称 / 路径查找模型。

    支持：
        ``"1"``              清单序号（从 1 开始，仅限可对话模型）
        ``"Qwen3.8-4B"``     名称或文件名片段（不区分大小写）
        ``"D:\\x\\y.gguf"``  完整路径
    """
    query = (query or "").strip()
    if not query:
        return None

    # 路径
    as_path = Path(query)
    if as_path.exists() and as_path.is_file():
        resolved = str(as_path.resolve())
        for entry in entries or build_catalog():
            if entry.path == resolved:
                return entry

        meta = GgufMeta(path=resolved, size_bytes=as_path.stat().st_size)

        read = read_gguf(as_path)
        if read is not None:
            meta = read
        return build_entry(meta)

    entries = entries if entries is not None else build_catalog()

    # 被排除的模型一律不可选，避免绕过 RAG_LLM_EXCLUDE
    entries = [e for e in entries if not e.excluded]

    # 序号（仅针对可对话模型，与 models 命令的展示顺序一致）
    if query.isdigit():
        usable = chat_models(entries)
        index = int(query) - 1
        if 0 <= index < len(usable):
            return usable[index]
        return None

    lowered = query.lower()

    # 精确文件名
    for entry in entries:
        if entry.file_name.lower() == lowered:
            return entry

    # 名称精确
    for entry in entries:
        if entry.display_name.lower() == lowered:
            return entry

    # 子串（优先可对话模型、优先文件名）
    candidates = [e for e in entries if lowered in e.file_name.lower()]
    if not candidates:
        candidates = [e for e in entries if lowered in e.display_name.lower()]
    if not candidates:
        candidates = [e for e in entries if lowered in e.path.lower()]

    if not candidates:
        return None

    chat = [c for c in candidates if c.is_chat_capable]
    pool = chat or candidates
    pool.sort(key=lambda e: _ranking_key(e, LLM_CONFIG.preferred_models))

    return pool[0]


# ----------------------------------------------------------------------
# 持久化选择
#
# 实际存储由 src/llm/state.py 负责（同一文件里还保存当前的 provider，
# 用于区分「本地离线」与「云端 API」两种方式）。
# ----------------------------------------------------------------------


def load_selection() -> str | None:
    """读取用户持久选择的**本地模型**（文件名）。"""
    from src.llm.state import load_state

    value = load_state().get("model")
    return str(value) if value else None


def save_selection(model: str | None) -> None:
    """写入 / 清除本地模型的持久选择。"""
    from src.llm.state import save_state

    save_state(model=model)

    # 选择变了，清单排序也要重算
    invalidate()


def invalidate() -> None:
    """清空内存中的清单缓存。"""
    with _catalog_lock:
        _catalog_cache.clear()


__all__ = [
    "CHAT_CAPABLE_KINDS",
    "KIND_BASE",
    "KIND_CHAT",
    "KIND_EMBEDDING",
    "KIND_LABELS",
    "KIND_TRANSLATION",
    "KIND_UNKNOWN",
    "KIND_VISION",
    "ModelEntry",
    "build_catalog",
    "build_entry",
    "chat_models",
    "classify",
    "estimate_kv_cache_gb",
    "find_model",
    "invalidate",
    "load_selection",
    "projector_for",
    "save_selection",
    "vision_pairs",
]
