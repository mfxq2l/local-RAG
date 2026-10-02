"""
RAG 项目全局配置

职责：
    1. 管理项目目录
    2. 管理 Embedding 模型配置
    3. 管理文档 / Chunk 配置
    4. 管理 Qdrant 配置
    5. 管理检索参数
    6. 管理本地推理参数

注意：
    本文件只保存配置，不执行模型加载、数据库初始化等操作。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


# ============================================================================
# 项目目录
# ============================================================================

# 当前文件：
#   RAG/src/config.py
#
# 因此：
#   parents[0] = RAG/src
#   parents[1] = RAG
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 原始文档目录
FILE_DIR = PROJECT_ROOT / "File"

MARKDOWN_DIR = FILE_DIR / "Markdown"
PDF_DIR = FILE_DIR / "PDF"
IMAGE_DIR = FILE_DIR / "image"
TEXT_DIR = FILE_DIR / "text"

# 模型目录
MODELS_DIR = PROJECT_ROOT / "models"

QWEN_MODEL_DIR = MODELS_DIR / "qwen3"
WEMM_MODEL_DIR = MODELS_DIR / "WeMM"

# 运行时
RUNTIME_DIR = PROJECT_ROOT / "runtime"

LLAMA_CPP_DIR = RUNTIME_DIR / "llama.cpp"
PYTHON_DIR = RUNTIME_DIR / "python3.12"

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"

CHUNKS_DIR = DATA_DIR / "chunks"
INDEX_DIR = DATA_DIR / "index"
METADATA_DIR = DATA_DIR / "metadata"

# Qdrant 本地数据库
QDRANT_DIR = DATA_DIR / "qdrant"

# Web
WEB_DIR = PROJECT_ROOT / "web"


# ============================================================================
# 自动创建数据目录
# ============================================================================

for directory in (
    DATA_DIR,
    CHUNKS_DIR,
    INDEX_DIR,
    METADATA_DIR,
    QDRANT_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Embedding 模型
# ============================================================================

@dataclass(frozen=True)
class EmbeddingConfig:
    """
    Embedding 模型配置。
    """

    # 模型名称，仅用于程序内部识别
    name: str

    # GGUF 主模型
    model_path: Path

    # 多模态模型可能需要的 mmproj
    mmproj_path: Path | None

    # 向量维度
    dimension: int

    # 最大输入长度
    max_tokens: int

    # 是否为多模态模型
    multimodal: bool

    # llama.cpp GPU offload 层数
    gpu_layers: int

    # CPU 线程数
    threads: int

    # **客户端**每次 HTTP 请求提交多少条文本
    # （注意：这不是 llama.cpp 的 -b 逻辑批大小）
    batch_size: int


# ---------------------------------------------------------------------------
# Qwen3-Embedding-4B
#
# 当前项目中的模型：
# models/qwen3/Qwen3-Embedding-4B-Q4_K_M.gguf
# ---------------------------------------------------------------------------

QWEN3_EMBEDDING = EmbeddingConfig(
    name="Qwen3-Embedding-4B",
    model_path=QWEN_MODEL_DIR / "Qwen3-Embedding-4B-Q4_K_M.gguf",
    mmproj_path=None,

    # Qwen3-Embedding-4B 使用 2560 维输出配置
    dimension=2560,

    # 模型上下文上限
    max_tokens=32768,

    multimodal=False,

    # -1 = 尽可能全部 offload 到 GPU
    gpu_layers=-1,

    # 根据机器情况调整
    threads=max(1, (os.cpu_count() or 8) // 2),

    batch_size=32,
)


# ---------------------------------------------------------------------------
# WeMM-Embedding-2B
#
# 当前项目中的模型：
# models/WeMM/
#   WeMM-Embedding-2B-Q4_K_M.gguf
#   mmproj-WeMM-Embedding-2B-BF16.gguf
# ---------------------------------------------------------------------------

WEMM_EMBEDDING = EmbeddingConfig(
    name="WeMM-Embedding-2B",
    model_path=WEMM_MODEL_DIR / "WeMM-Embedding-2B-Q4_K_M.gguf",
    mmproj_path=WEMM_MODEL_DIR / "mmproj-WeMM-Embedding-2B-BF16.gguf",

    # 第一阶段建议统一使用 2048 维。
    #
    # 后续如果需要节省向量数据库空间，可以进一步测试更低维度。
    dimension=2048,

    max_tokens=32768,

    multimodal=True,

    gpu_layers=-1,

    threads=max(1, (os.cpu_count() or 8) // 2),

    batch_size=8,
)


# ============================================================================
# 当前 Embedding 模型
# ============================================================================

# 第一阶段：
#   Markdown / TXT
#       ↓
#   Qwen3-Embedding-4B
#
# 第二阶段：
#   PDF / Image / Visual Document
#       ↓
#   WeMM-Embedding-2B

ACTIVE_EMBEDDING = os.getenv(
    "RAG_EMBEDDING_MODEL",
    "qwen3",
).lower()


EMBEDDING_MODELS: dict[str, EmbeddingConfig] = {
    "qwen3": QWEN3_EMBEDDING,
    "qwen": QWEN3_EMBEDDING,

    "wemm": WEMM_EMBEDDING,
}


if ACTIVE_EMBEDDING not in EMBEDDING_MODELS:
    raise ValueError(
        f"未知的 Embedding 模型: {ACTIVE_EMBEDDING!r}\n"
        f"可选值: {', '.join(EMBEDDING_MODELS.keys())}"
    )


EMBEDDING_CONFIG = EMBEDDING_MODELS[ACTIVE_EMBEDDING]


# ============================================================================
# 文档处理
# ============================================================================

@dataclass(frozen=True)
class ChunkConfig:
    """
    文档切块配置。

    对 Markdown 来说：
        优先按标题层级切分，
        再对过大的 section 进行二次切块。
    """

    # 每个 Chunk 目标大小
    chunk_size: int = 800

    # Chunk overlap
    chunk_overlap: int = 120

    # 最小 chunk 大小
    min_chunk_size: int = 80

    # 最大 chunk 大小
    max_chunk_size: int = 1500

    # 是否保留 Markdown 标题层级
    preserve_headings: bool = True

    # 是否将文档标题写入 chunk
    include_document_title: bool = True

    # 是否将 section 标题写入 chunk
    include_section_title: bool = True


CHUNK_CONFIG = ChunkConfig()


# ============================================================================
# 文档扫描
# ============================================================================

SUPPORTED_TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
}

SUPPORTED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
}

SUPPORTED_DOCUMENT_EXTENSIONS = {
    ".pdf",
}


# ============================================================================
# Qdrant
# ============================================================================

@dataclass(frozen=True)
class QdrantConfig:
    """
    Qdrant 向量数据库配置。
    """

    # 本地模式
    mode: str = "local"

    # 本地数据库目录
    path: Path = QDRANT_DIR

    # 如果以后切换到 Qdrant Server，可以启用下面的配置
    host: str = "127.0.0.1"
    port: int = 6333

    # Collection 名称
    collection_name: str = "rag_knowledge"

    # 距离算法
    #
    # 对标准 normalized embedding：
    # cosine 是最常见的选择。
    distance: str = "cosine"

    # HNSW 参数
    hnsw_m: int = 16
    hnsw_ef_construct: int = 100


QDRANT_CONFIG = QdrantConfig()


# ============================================================================
# 检索
# ============================================================================

@dataclass(frozen=True)
class RetrievalConfig:
    """
    RAG 检索参数。

    推荐流程：

        Dense Search
              +
           BM25
              ↓
        Candidate Pool
              ↓
          Reranker
              ↓
          最终 Top-K
    """

    # Dense 向量检索返回多少条
    dense_top_k: int = 20

    # BM25 返回多少条
    bm25_top_k: int = 20

    # 混合检索后的候选数量
    candidate_top_k: int = 30

    # 最终送给 Reranker 的数量
    rerank_top_k: int = 10

    # 最终交给 LLM 的 Context 数量
    context_top_k: int = 5

    # Cosine similarity 最低阈值
    similarity_threshold: float = 0.20

    # 相关性下限：重排后低于此分数的结果视为「与问题无关」而被丢弃。
    #
    # 实测分得很开：
    #   闲聊（你好呀 / 谢谢 / 今天天气）  最高 0.32 ~ 0.39
    #   真实问题（nmap -sS / 图片检索）   最高 0.58 ~ 0.63
    # 因此 0.45 能干净地区分两者。结果为空时，问答会走
    # 「没有相关资料 → 自然回答」而不是硬套不相干的资料答非所问。
    #
    # 设为 0 即关闭该过滤。
    min_relevance_score: float = 0.45

    # 是否启用 BM25
    enable_bm25: bool = True

    # 是否启用 Reranker
    enable_reranker: bool = True


def _retrieval_score_floor() -> float:
    """相关性下限，可用 ``RAG_MIN_RELEVANCE`` 覆盖。

    这里不用模块后方的 ``_env_float`` —— 它在检索配置之后才定义。
    """
    raw = os.getenv("RAG_MIN_RELEVANCE")
    if not raw:
        return 0.45
    try:
        return float(raw)
    except ValueError:
        return 0.45


RETRIEVAL_CONFIG = RetrievalConfig(
    min_relevance_score=_retrieval_score_floor(),
)


# ============================================================================
# RAG Context
# ============================================================================

@dataclass(frozen=True)
class ContextConfig:
    """
    LLM 最终上下文配置。
    """

    # 单个 chunk 允许进入 Context 的最大字符数
    max_chunk_chars: int = 5000

    # 整体 Context 最大字符数
    max_context_chars: int = 24000

    # 是否在 Context 中显示来源
    include_source: bool = True

    # 是否显示章节
    include_section: bool = True

    # 是否显示页码
    include_page: bool = True

    # 不同 chunk 之间的分隔符
    separator: str = "\n\n---\n\n"


CONTEXT_CONFIG = ContextConfig()


# ============================================================================
# 本地推理 / llama.cpp
# ============================================================================

@dataclass(frozen=True)
class LlamaCppConfig:
    """
    llama.cpp 通用运行配置。
    """

    # llama-server / llama-cli 所在目录
    executable_dir: Path = LLAMA_CPP_DIR

    # GPU offload
    gpu_layers: int = -1

    # CPU threads
    threads: int = max(1, (os.cpu_count() or 8) // 2)

    # llama.cpp 逻辑批大小（-b），即 prompt 处理的粒度。
    #
    # 注意：这个值**必须足够大**，否则 prompt 会被切成很多小批次，
    # 吞吐会急剧下降。曾经误用 embedding 的「客户端请求批大小」(32)
    # 作为 -b，导致 RTX 3070 上吞吐只有 ~54 tok/s（正常应为数百）。
    batch_size: int = 2048

    # 微批大小（-ub）
    micro_batch_size: int = 512

    # embedding 服务的上下文长度（llama-server 的 -c）
    #
    # 注意：**不要**直接用模型上限（Qwen3-Embedding 是 32768）。llama.cpp
    # 会按上下文长度分配 prompt cache，配上默认的多 slot 会造出一个巨大且
    # 不断颠簸的缓存 —— 实测日志里出现 3200 次
    # "making room for prompt cache entry, removing oldest entry"。
    #
    # 本项目的 chunk 最大 1500 字符（约 800~1500 token），8192 绰绰有余。
    embedding_context_size: int = 8192

    # embedding 服务的 slot 数（-np）。
    # 单进程顺序批处理，1 个 slot 就够，能显著减小 KV/prompt cache 占用。
    embedding_slots: int = 1

    # embedding 的客户端请求批大小
    embedding_batch_size: int = 32

    # 是否使用 flash attention
    flash_attention: bool = True

    # 是否使用 mmap
    use_mmap: bool = True

    # 是否锁定模型到 RAM
    use_mlock: bool = False


LLAMA_CONFIG = LlamaCppConfig()


# ============================================================================
# 生成式 LLM（RAG 问答）
# ============================================================================

def _env_str(key: str, default: str) -> str:
    value = os.getenv(key)
    return value if value not in (None, "") else default


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw in (None, ""):
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw in (None, ""):
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw in (None, ""):
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "y"}


# 项目内放置 LLM 的目录（把 gguf 拷进来即可自动发现）
LLM_MODEL_DIR = MODELS_DIR / "llm"


@dataclass(frozen=True)
class LlmConfig:
    """生成式 LLM 配置。

    两种 provider：

        llama_cpp  本机拉起 llama-server.exe 跑 gguf（默认）
        openai     任意 OpenAI 兼容端点（Ollama / LM Studio / vLLM / 云端）

    所有字段都可以用环境变量覆盖，见下方 ``LLM_CONFIG``。
    """

    enabled: bool = True

    # llama_cpp | openai
    provider: str = "llama_cpp"

    # 显式指定的模型路径；None 表示自动发现
    model_path: Path | None = None

    # 自动发现的候选目录（按顺序）
    model_dirs: tuple[Path, ...] = (LLM_MODEL_DIR,)

    # 候选文件名关键字（按优先级从高到低匹配）
    preferred_models: tuple[str, ...] = ()

    # 排除列表：命中关键字的模型不会出现在可选清单里，
    # 也不能被 --llm / Web 界面选中（大小写不敏感的子串匹配）
    excluded_models: tuple[str, ...] = ()

    # openai provider 使用
    base_url: str | None = None
    api_key: str = ""
    model_name: str = ""

    # llama_cpp provider 使用
    port: int = 8082
    context_size: int = 8192
    gpu_layers: int = -1
    threads: int = max(1, (os.cpu_count() or 8) // 2)
    # llama.cpp 逻辑批（prompt 处理粒度）；RAG 的 context 很长，给大一些
    batch_size: int = 1024

    # 默认问答档位：fast（关闭思考，约 7.8x 快）| precise（开启思考）
    # 具体参数见 src/rag/modes.py
    default_mode: str = "precise"

    # 服务端级思考开关：on | off | auto
    # 传给 llama-server 的 --reasoning。留 auto 让请求级档位自己决定。
    reasoning: str = "auto"

    # 对话服务是否同时加载配对的视觉投影器（mmproj）。
    #
    # 开启后：同一个 llama-server 既能对话又能读图 —— 省下一份 2.97GB 的
    # 模型副本（8GB 显卡上很关键），视觉描述也直接复用它而不必另起服务。
    load_mmproj: bool = True

    # 采样参数
    max_tokens: int = 1024
    temperature: float = 0.2
    top_p: float = 0.9
    repeat_penalty: float = 1.1

    # 自适应检索（先判断需不需要查知识库）。
    #
    # **默认关闭** —— 经验上「永远检索一次」更可靠。
    # 开启路由后曾出现「带有 GitHub 图标的照片是哪张」被判为不需要检索，
    # 而知识库里明明有那张图，模型反而回答「请您上传图片」。
    # 判断失误的代价远大于多查一次的代价。
    #
    # 需要时可用 RAG_ROUTER_ENABLED=1 打开。
    router_enabled: bool = False

    # 超时
    request_timeout: float = 300.0

    # ---- 显存预算（用于挑选模型，见 src/llm/catalog.py）----------------
    #
    # 显卡总显存。LLM 需要放得下：权重 + KV cache + 下面这份预留。
    vram_budget_gb: float = 8.0

    # 留给 embedding 模型常驻 + 计算缓冲的显存
    vram_reserve_gb: float = 3.0


# ---------------------------------------------------------------------------
# 自动发现：默认候选模型
#
# **只使用项目自带的 models/LLM 目录**（用户明确要求：除该目录外，任何其他
# LLM 都不得使用，包括外部磁盘上的模型库）。
#
# 需要临时引入外部模型时，显式设置 RAG_LLM_MODEL_DIRS 覆盖即可。
#
# 用户明确要求不使用 gemma-4-E4B，故已列入排除规则。
# ---------------------------------------------------------------------------

_DEFAULT_MODEL_DIRS = (
    LLM_MODEL_DIR,
)

_DEFAULT_PREFERRED_MODELS = (
    # 项目内置的通用对话模型（非 gemma 系列）
    "Qwen3.8-4B",
    "Qwen3",
    # gemma-4-E2B 仍可用，但排在 Qwen 之后，且不是默认
    "gemma-4-E2B",
)

_env_model_path = os.getenv("RAG_LLM_MODEL")

LLM_CONFIG = LlmConfig(
    enabled=_env_bool("RAG_LLM_ENABLED", True),

    provider=_env_str("RAG_LLM_PROVIDER", "llama_cpp").lower(),

    model_path=(
        Path(_env_model_path) if _env_model_path else None
    ),

    model_dirs=tuple(
        Path(p)
        for p in _env_str(
            "RAG_LLM_MODEL_DIRS",
            os.pathsep.join(str(p) for p in _DEFAULT_MODEL_DIRS),
        ).split(os.pathsep)
        if p.strip()
    ),

    preferred_models=tuple(
        m.strip()
        for m in _env_str(
            "RAG_LLM_PREFERRED",
            ",".join(_DEFAULT_PREFERRED_MODELS),
        ).split(",")
        if m.strip()
    ),

    # 用户明确要求不使用 gemma-4-E4B，故默认排除。
    # 需要时可改环境变量 RAG_LLM_EXCLUDE（留空即不排除任何模型）。
    excluded_models=tuple(
        m.strip()
        for m in _env_str(
            "RAG_LLM_EXCLUDE",
            "gemma-4-E4B",
        ).split(",")
        if m.strip()
    ),

    base_url=os.getenv("RAG_LLM_BASE_URL") or None,
    api_key=_env_str("RAG_LLM_API_KEY", ""),
    model_name=_env_str("RAG_LLM_NAME", ""),

    port=_env_int("RAG_LLM_PORT", 8082),
    context_size=_env_int("RAG_LLM_CTX", 8192),
    gpu_layers=_env_int("RAG_LLM_GPU_LAYERS", -1),
    threads=_env_int(
        "RAG_LLM_THREADS",
        max(1, (os.cpu_count() or 8) // 2),
    ),
    batch_size=_env_int("RAG_LLM_BATCH", 1024),
    default_mode=_env_str("RAG_LLM_MODE", "precise").lower(),
    reasoning=_env_str("RAG_LLM_REASONING", "auto").lower(),
    load_mmproj=_env_bool("RAG_LLM_LOAD_MMPROJ", True),

    max_tokens=_env_int("RAG_LLM_MAX_TOKENS", 1024),
    temperature=_env_float("RAG_LLM_TEMPERATURE", 0.2),
    top_p=_env_float("RAG_LLM_TOP_P", 0.9),
    repeat_penalty=_env_float("RAG_LLM_REPEAT_PENALTY", 1.1),

    request_timeout=_env_float("RAG_LLM_TIMEOUT", 300.0),
    router_enabled=_env_bool("RAG_ROUTER_ENABLED", False),

    vram_budget_gb=_env_float("RAG_LLM_VRAM_GB", 8.0),
    vram_reserve_gb=_env_float("RAG_LLM_VRAM_RESERVE_GB", 3.0),
)


def discover_llm_model(config: LlmConfig | None = None) -> Path | None:
    """按优先级自动发现一个可用的**对话**模型。

    顺序：

        1. ``RAG_LLM_MODEL`` 显式路径
        2. ``data/llm_selection.json`` 中的持久选择
           （由 ``run.py models --set <名字>`` 或 Web 界面写入）
        3. 模型清单排序后的第一个可对话模型
           （项目自带 ``models/LLM`` 优先，其次外部目录）

    与旧实现的两个关键差异：

    * **不再有「取体积最大的 gguf」兜底**。模型库很大时，那会选中 30B/80B
      这类显存根本装不下的模型。
    * **不再把 mmproj / mtp / 翻译 / 向量模型当作对话模型**，分类见
      :func:`src.llm.catalog.classify`。

    Returns:
        模型路径；找不到可用的对话模型时返回 ``None``。
    """
    config = config or LLM_CONFIG

    if config.model_path is not None:
        return config.model_path if config.model_path.exists() else None

    # 延迟导入：config 与 catalog 互相引用，放在函数内可避免循环导入
    from src.llm.catalog import build_catalog, find_model, load_selection

    try:
        entries = build_catalog(config)
    except Exception:  # noqa: BLE001
        return None

    selected = load_selection()
    if selected:
        entry = find_model(selected, entries)
        if entry is not None and Path(entry.path).exists():
            return Path(entry.path)

    for entry in entries:
        if entry.is_chat_capable:
            path = Path(entry.path)
            if path.exists():
                return path

    return None


# ============================================================================
# 多模态：视觉模型（图片理解 / 描述生成）
# ============================================================================

# 视觉模型端口（embedding 8080、WeMM 8081、对话 LLM 8082）
VISION_PORT = 8083


@dataclass(frozen=True)
class VisionConfig:
    """视觉语言模型配置。

    用途：给图片生成**语义描述**，再交给文本 embedding 入库。

    为什么需要这一步：llama.cpp 的 ``/v1/embeddings`` 只接受文本，
    图片输入会被**静默忽略**（实测：换一张图向量完全不变）。因此真正的
    多模态检索必须经由「视觉模型读懂图片 → 文本描述 → 向量化」这条路。
    """

    enabled: bool = True

    # 显式指定；None 表示自动配对（见 catalog.vision_pairs）
    model_path: Path | None = None
    mmproj_path: Path | None = None

    port: int = VISION_PORT
    context_size: int = 4096
    gpu_layers: int = -1
    threads: int = max(1, (os.cpu_count() or 8) // 2)
    batch_size: int = 1024

    # 描述生成的采样参数
    max_tokens: int = 512
    temperature: float = 0.1

    # 描述时使用的提示词
    prompt: str = (
        "请用简体中文详细描述这张图片，用于后续的检索匹配。要求："
        "1) 逐字列出图片中出现的所有文字（保留原文大小写与符号）；"
        "2) 描述图形、界面元素、布局与颜色；"
        "3) 概括图片的主题与它可能涉及的技术领域。"
        "只输出描述内容本身，不要加前言。"
    )

    # 是否在索引时把描述也写入 BM25（便于关键词命中图片）
    index_caption_in_bm25: bool = True

    request_timeout: float = 300.0


_env_vision_model = os.getenv("RAG_VISION_MODEL")
_env_vision_mmproj = os.getenv("RAG_VISION_MMPROJ")

VISION_CONFIG = VisionConfig(
    enabled=_env_bool("RAG_VISION_ENABLED", True),

    model_path=Path(_env_vision_model) if _env_vision_model else None,
    mmproj_path=Path(_env_vision_mmproj) if _env_vision_mmproj else None,

    port=_env_int("RAG_VISION_PORT", VISION_PORT),
    context_size=_env_int("RAG_VISION_CTX", 4096),
    gpu_layers=_env_int("RAG_VISION_GPU_LAYERS", -1),
    threads=_env_int(
        "RAG_VISION_THREADS",
        max(1, (os.cpu_count() or 8) // 2),
    ),
    batch_size=_env_int("RAG_VISION_BATCH", 1024),

    max_tokens=_env_int("RAG_VISION_MAX_TOKENS", 512),
    temperature=_env_float("RAG_VISION_TEMPERATURE", 0.1),

    prompt=_env_str(
        "RAG_VISION_PROMPT",
        VisionConfig.prompt,
    ),

    index_caption_in_bm25=_env_bool("RAG_VISION_BM25", True),
    request_timeout=_env_float("RAG_VISION_TIMEOUT", 300.0),
)


# ============================================================================
# API / Web Server
# ============================================================================

@dataclass(frozen=True)
class ServerConfig:
    """
    Web API 配置。

    host / port 可用 ``RAG_WEB_HOST`` / ``RAG_WEB_PORT`` 覆盖，
    便于在同一台机器上并行跑多个实例（例如换端口做验证而不打扰正在使用的服务）。
    """

    host: str = "127.0.0.1"
    port: int = 8000

    # 开发环境下开启
    debug: bool = True

    # API 前缀
    api_prefix: str = "/api"

    # CORS
    allow_origins: tuple[str, ...] = (
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    )


SERVER_CONFIG = ServerConfig(
    host=_env_str("RAG_WEB_HOST", "127.0.0.1"),
    port=_env_int("RAG_WEB_PORT", 8000),
    allow_origins=tuple(
        origin
        for origin in (
            f"http://127.0.0.1:{_env_int('RAG_WEB_PORT', 8000)}",
            f"http://localhost:{_env_int('RAG_WEB_PORT', 8000)}",
        )
    ),
)


# ============================================================================
# 日志
# ============================================================================

@dataclass(frozen=True)
class LoggingConfig:
    """
    日志配置。
    """

    level: str = "INFO"

    # 是否显示详细检索信息
    verbose_retrieval: bool = True

    # 是否显示 embedding 计时
    show_embedding_timing: bool = True

    # 是否显示数据库搜索耗时
    show_search_timing: bool = True


LOGGING_CONFIG = LoggingConfig()


# ============================================================================
# 全局配置检查
# ============================================================================

def validate_config() -> None:
    """
    启动前检查关键配置。

    这里只检查配置是否合理，不检查 Python 包、
    CUDA 或模型内部是否真的能够加载。
    """

    if not PROJECT_ROOT.exists():
        raise RuntimeError(
            f"项目根目录不存在: {PROJECT_ROOT}"
        )

    if not EMBEDDING_CONFIG.model_path.exists():
        raise FileNotFoundError(
            "Embedding 模型不存在:\n"
            f"  {EMBEDDING_CONFIG.model_path}"
        )

    if EMBEDDING_CONFIG.multimodal:
        if (
            EMBEDDING_CONFIG.mmproj_path is not None
            and not EMBEDDING_CONFIG.mmproj_path.exists()
        ):
            raise FileNotFoundError(
                "多模态 mmproj 文件不存在:\n"
                f"  {EMBEDDING_CONFIG.mmproj_path}"
            )

    if CHUNK_CONFIG.chunk_overlap >= CHUNK_CONFIG.chunk_size:
        raise ValueError(
            "chunk_overlap 必须小于 chunk_size"
        )

    if CHUNK_CONFIG.min_chunk_size >= CHUNK_CONFIG.max_chunk_size:
        raise ValueError(
            "min_chunk_size 必须小于 max_chunk_size"
        )

    if RETRIEVAL_CONFIG.context_top_k > RETRIEVAL_CONFIG.rerank_top_k:
        raise ValueError(
            "context_top_k 不应大于 rerank_top_k"
        )


# ============================================================================
# 调试输出
# ============================================================================

def print_config() -> None:
    """
    打印当前配置。

    方便第一次运行 RAG 时确认路径和模型是否正确。
    """

    print("=" * 70)
    print("RAG Configuration")
    print("=" * 70)

    print(f"Project Root : {PROJECT_ROOT}")
    print()

    print("Embedding")
    print(f"  Model      : {EMBEDDING_CONFIG.name}")
    print(f"  Path       : {EMBEDDING_CONFIG.model_path}")
    print(f"  Dimension  : {EMBEDDING_CONFIG.dimension}")
    print(f"  Max Tokens : {EMBEDDING_CONFIG.max_tokens}")
    print(f"  Multimodal : {EMBEDDING_CONFIG.multimodal}")
    print()

    if EMBEDDING_CONFIG.mmproj_path is not None:
        print(f"  mmproj     : {EMBEDDING_CONFIG.mmproj_path}")
        print()

    print("Documents")
    print(f"  Markdown   : {MARKDOWN_DIR}")
    print(f"  PDF        : {PDF_DIR}")
    print(f"  Image      : {IMAGE_DIR}")
    print(f"  Text       : {TEXT_DIR}")
    print()

    print("Database")
    print(f"  Qdrant     : {QDRANT_CONFIG.path}")
    print(f"  Collection : {QDRANT_CONFIG.collection_name}")
    print(f"  Distance   : {QDRANT_CONFIG.distance}")
    print()

    print("Chunk")
    print(f"  Size       : {CHUNK_CONFIG.chunk_size}")
    print(f"  Overlap    : {CHUNK_CONFIG.chunk_overlap}")
    print()

    print("Retrieval")
    print(f"  Dense TopK : {RETRIEVAL_CONFIG.dense_top_k}")
    print(f"  BM25 TopK  : {RETRIEVAL_CONFIG.bm25_top_k}")
    print(f"  Candidate  : {RETRIEVAL_CONFIG.candidate_top_k}")
    print(f"  Rerank TopK: {RETRIEVAL_CONFIG.rerank_top_k}")
    print(f"  Context TopK: {RETRIEVAL_CONFIG.context_top_k}")

    print("=" * 70)


# ============================================================================
# 直接执行 config.py 时
# ============================================================================

if __name__ == "__main__":
    validate_config()
    print_config()