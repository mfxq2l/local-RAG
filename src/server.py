"""RAG Web Server（FastAPI）。

接口总览
--------
基础
    GET  /                      服务信息
    GET  /api/health            健康检查（含索引与 LLM 状态）
    GET  /api/config            当前配置

知识库
    GET  /api/documents                      Markdown 文件列表
    GET  /api/documents/{path}               单文件信息
    POST /api/chunks/preview                 切块预览
    GET  /api/chunks/stats                   全库切块统计

检索与问答
    POST /api/search         混合检索（Dense + BM25 + RRF + Rerank）
    POST /api/ask            检索 + 生成式问答
    POST /api/ask/stream     同上，SSE 流式（含思考过程与引用）
    GET  /api/llm/status     生成式模型状态

索引
    GET  /api/index/status   索引状态
    POST /api/index          构建 / 重建索引

UI
    GET  /ui                 内置 Web 界面

实现约定
--------
* **重活一律用同步 def**：FastAPI 会把同步路由丢进线程池，避免阻塞事件循环。
  早期版本用 ``async def`` 直接跑 embedding / 检索，导致建索引期间整个服务卡死。
* **生命周期**：lifespan 退出时统一关闭 Qdrant 客户端与 llama-server 子进程。
"""

from __future__ import annotations

import json
import mimetypes
import sys
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import quote

# ============================================================================
# 确保从项目根目录运行时可以找到 src
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================================
# 第三方依赖
# ============================================================================

try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import (
        FileResponse,
        HTMLResponse,
        Response,
        StreamingResponse,
    )
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "缺少 FastAPI 依赖。\n"
        "请安装：\n"
        "    pip install fastapi uvicorn pydantic\n"
    ) from exc


# ============================================================================
# 项目内部模块
# ============================================================================

from src.config import (
    ACTIVE_EMBEDDING,
    CHUNK_CONFIG,
    CONTEXT_CONFIG,
    EMBEDDING_CONFIG,
    EMBEDDING_MODELS,
    IMAGE_DIR,
    LLM_CONFIG,
    LOGGING_CONFIG,
    MARKDOWN_DIR,
    PDF_DIR,
    QDRANT_CONFIG,
    RETRIEVAL_CONFIG,
    SERVER_CONFIG,
    TEXT_DIR,
    VISION_CONFIG,
)

from src.database.vector_db import close_all as close_vector_dbs
from src.database.vector_db import get_vector_db
from src.embedding import model_key
from src.ids import chunk_point_id
from src.ingest.chunker import load_markdown_directory, markdown_to_chunks
from src.ingest.pipeline import ingest_all
from src.llm import close_all as close_llms
from src.llm import get_llm
from src.llama_server import stop_all as stop_llama_servers
from src.rag.answer import RAGAnswerer
from src.rag.modes import mode_catalog
from src.rag.search import search_rag
from src.retrieval.bm25 import bm25_index_path


# ============================================================================
# 全局状态
# ============================================================================

# 建索引是重操作，同一时刻只允许一个
_index_lock = threading.Lock()
_index_state: dict[str, Any] = {
    "running": False,
    "started_at": 0.0,
    "last_result": None,
    "last_error": None,
}


# ============================================================================
# Lifespan
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[server] 启动完成")
    print(f"[server] Web UI : http://{SERVER_CONFIG.host}:{SERVER_CONFIG.port}/ui")

    try:
        yield
    finally:
        print("[server] 正在关闭资源…")
        close_llms()
        stop_llama_servers()
        close_vector_dbs()
        print("[server] 已释放 LLM 与向量库资源")


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Local RAG API",
    description="本地部署 RAG 服务：混合检索 + 生成式问答。",
    version="0.2.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(SERVER_CONFIG.allow_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_WEB_DIR = PROJECT_ROOT / "web"

if _WEB_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(_WEB_DIR)),
        name="static",
    )


# ============================================================================
# Pydantic 模型
# ============================================================================


class ChunkPreviewRequest(BaseModel):
    """Chunk 预览请求。"""

    file: str = Field(
        ...,
        description="相对于 File/Markdown 的 Markdown 文件路径",
        examples=["python知识点.md"],
    )
    limit: int = Field(default=10, ge=1, le=100, description="返回多少个 Chunk")


class SearchRequest(BaseModel):
    """检索请求。"""

    query: str = Field(..., min_length=1, max_length=5000, description="用户查询")
    top_k: int = Field(default=5, ge=1, le=50, description="最终返回数量")
    use_bm25: bool = Field(default=RETRIEVAL_CONFIG.enable_bm25)
    use_reranker: bool = Field(default=RETRIEVAL_CONFIG.enable_reranker)
    include_images: bool = Field(
        default=True,
        description=(
            "是否把图片纳入检索结果。图片描述与文本共处同一向量空间，"
            "因此文字查询可以直接命中相关图片。"
        ),
    )
    use_web: bool | None = Field(
        default=None,
        description=(
            "是否联网搜索。None 表示用设置里的默认值。"
            "联网结果会追加在本地结果之后，引用里带 url 与 source_type=web。"
        ),
    )
    web_limit: int | None = Field(
        default=None, ge=1, le=15, description="联网取几条结果"
    )
    web_fetch_pages: bool | None = Field(
        default=None, description="是否抓取网页正文（关闭则只用搜索摘要，更快）"
    )


def resolve_web_options(request: "SearchRequest") -> dict[str, Any]:
    """把请求里的联网参数与设置默认值合并。

    请求里传了就以请求为准，没传就取设置里的默认值 —— 这样前端只需在
    用户显式切换时发送字段。
    """
    from src.web import get_web_config

    cfg = get_web_config().get()

    use_web = cfg.enabled if request.use_web is None else request.use_web

    return {
        "use_web": bool(use_web),
        "web_limit": (
            request.web_limit
            if request.web_limit is not None
            else cfg.max_results
        ),
        "web_fetch_pages": (
            cfg.fetch_pages
            if request.web_fetch_pages is None
            else request.web_fetch_pages
        ),
    }


class AskRequest(SearchRequest):
    """问答请求。"""

    mode: str | None = Field(
        default=None,
        description="问答档位：fast（关闭思考，快）| precise（开启思考，准）。"
        "None 用配置默认值。",
        examples=["fast", "precise"],
    )
    temperature: float | None = Field(
        default=None, ge=0.0, le=2.0, description="采样温度，None 用档位默认值"
    )
    max_tokens: int | None = Field(
        default=None, ge=16, le=8192, description="最大生成 token 数，None 用档位默认值"
    )
    provider: str | None = Field(
        default=None, description="生成模型 provider：llama_cpp | openai"
    )


class IndexRequest(BaseModel):
    """建索引请求。"""

    rebuild: bool = Field(default=False, description="是否清空后重建")
    prune: bool = Field(default=True, description="是否清理已失效文档的残留 chunk")
    include_images: bool = Field(
        default=True,
        description=(
            "是否用视觉模型描述 File/image 下的图片并一起索引。"
            "图片描述与文本共用同一个向量库，因此一次查询可同时召回两者。"
        ),
    )


# ============================================================================
# 辅助函数
# ============================================================================


def path_to_safe_relative(base_dir: Path, user_path: str) -> Path:
    """把用户提供的相对路径转为安全路径，防止 ``../../`` 逃逸。"""
    if not user_path:
        raise ValueError("文件路径不能为空")

    user_path = user_path.replace("\\", "/")

    candidate = Path(user_path)

    if candidate.is_absolute():
        raise ValueError("只允许使用知识库目录下的相对路径")

    target = (base_dir / candidate).resolve()
    base = base_dir.resolve()

    try:
        target.relative_to(base)
    except ValueError as exc:
        raise ValueError(
            "非法文件路径：目标文件必须位于知识库目录内部"
        ) from exc

    return target


def get_markdown_files() -> list[Path]:
    """列出全部 Markdown 文件。"""
    if not MARKDOWN_DIR.exists():
        return []

    return sorted(
        (
            path
            for path in MARKDOWN_DIR.rglob("*")
            if path.is_file() and path.suffix.lower() in {".md", ".markdown"}
        ),
        key=lambda p: str(p).lower(),
    )


def relative_markdown_path(path: Path) -> str:
    """转成相对于 File/Markdown 的路径。"""
    try:
        return str(
            path.resolve().relative_to(MARKDOWN_DIR.resolve())
        ).replace("\\", "/")
    except ValueError:
        return path.name


def serialize_chunk(chunk: Any) -> dict[str, Any]:
    """Chunk → JSON 可序列化字典。"""
    if hasattr(chunk, "to_dict"):
        return chunk.to_dict()

    return {
        "chunk_id": getattr(chunk, "chunk_id", ""),
        "doc_id": getattr(chunk, "doc_id", ""),
        "title": getattr(chunk, "title", ""),
        "section": getattr(chunk, "section", ""),
        "content": getattr(chunk, "content", ""),
        "source": getattr(chunk, "source", ""),
        "chunk_index": getattr(chunk, "chunk_index", 0),
        "heading_level": getattr(chunk, "heading_level", 0),
        "metadata": getattr(chunk, "metadata", {}),
    }


def indexed_count() -> int:
    """当前 collection 的向量数量（失败返回 0）。"""
    try:
        return get_vector_db().count()
    except Exception:  # noqa: BLE001
        return 0


def _indexed_doc_ids() -> set[str]:
    """已进入索引的文档标识集合。

    图片的 ``doc_id`` 形如 ``image::sub/pic.png``，这里统一剥掉前缀，
    与文件相对路径对齐，便于逐个文件比对「是否已索引」。

    取不到时返回空集合（界面会显示为未索引，属保守但安全的退化）。
    """
    try:
        raw = get_vector_db().payload_values("doc_id")
    except Exception:  # noqa: BLE001
        return set()

    result: set[str] = set()

    for doc_id in raw:
        if doc_id.startswith("image::"):
            result.add(doc_id[len("image::"):])
        else:
            result.add(doc_id)

    return result


def image_count() -> int:
    """已索引的图片数量（按 ``metadata.modality == image`` 统计）。"""
    try:
        from src.retrieval.vector import VectorRetriever

        return VectorRetriever().count_images()
    except Exception:  # noqa: BLE001
        return 0


def llm_status() -> dict[str, Any]:
    """生成式模型状态（含当前方式、生效模型与可选数量）。"""
    from src.llm.cloud import active_provider, load_cloud

    provider = "unknown"
    try:
        provider = active_provider()
    except Exception:  # noqa: BLE001
        pass

    try:
        from src.llm import active_model, chat_models

        active = active_model()
        choices = len(chat_models())
    except Exception:  # noqa: BLE001
        active = {}
        choices = 0

    try:
        llm = get_llm()
    except Exception as exc:  # noqa: BLE001
        return {
            "available": False,
            "reason": str(exc),
            "provider": provider,
            "active": active,
            "choices": choices,
        }

    status_fn = getattr(llm, "status", None)

    if callable(status_fn):
        try:
            payload = dict(status_fn())
        except Exception as exc:  # noqa: BLE001
            payload = {"available": False, "reason": str(exc)}
    else:
        available, reason = llm.available()  # type: ignore[attr-defined]
        payload = {
            "available": available,
            "reason": reason,
            "provider": provider,
            "model": getattr(llm, "name", ""),
        }

    payload["provider"] = provider

    if provider == "openai":
        cloud = load_cloud()
        # 只暴露掩码，绝不回传明文 Key
        payload["cloud"] = cloud.to_public_dict()

    payload["active"] = active
    payload["choices"] = choices

    return payload


def vision_status() -> dict[str, Any]:
    """视觉模型（图片理解）状态。"""
    try:
        from src.vision import VisionCaptioner

        return VisionCaptioner().status()
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": str(exc)}


def sse(event: dict[str, Any]) -> str:
    """把事件字典编码成 SSE 帧。"""
    return f"data: {json.dumps(event, ensure_ascii=False, default=str)}\n\n"


# ============================================================================
# 基础 API
# ============================================================================


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "name": "Local RAG API",
        "version": "0.2.0",
        "status": "running",
        "ui": "/ui",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/api/health")
async def health() -> dict[str, Any]:
    """健康检查（不触发 embedding 模型加载）。"""
    chunks = indexed_count()

    bm25_exists = False
    try:
        bm25_exists = bm25_index_path().exists()
    except Exception:  # noqa: BLE001
        pass

    status = llm_status()
    vision = vision_status()

    return {
        "status": "ok",
        "version": "0.2.0",
        "timestamp": time.time(),
        "project_root": str(PROJECT_ROOT),
        "embedding_model": EMBEDDING_CONFIG.name,
        "embedding_model_exists": EMBEDDING_CONFIG.model_path.exists(),
        "markdown_directory_exists": MARKDOWN_DIR.exists(),
        "qdrant_directory_exists": QDRANT_CONFIG.path.exists(),
        "indexed_chunks": chunks,
        "image_chunks": image_count(),
        "bm25_index_exists": bm25_exists,
        "llm_available": bool(status.get("available")),
        "llm_model": status.get("model", ""),
        "llm_reason": status.get("reason", ""),
        "vision_available": bool(vision.get("available")),
        "vision_model": vision.get("model", ""),
        "vision_reason": vision.get("reason", ""),
        "indexing": _index_state["running"],
    }


@app.get("/api/config")
async def get_config() -> dict[str, Any]:
    """返回当前配置（不含任何密钥）。"""
    return {
        "project": {"root": str(PROJECT_ROOT)},
        "embedding": {
            "active": ACTIVE_EMBEDDING,
            "model_path": str(EMBEDDING_CONFIG.model_path),
            "dimension": EMBEDDING_CONFIG.dimension,
            "max_tokens": EMBEDDING_CONFIG.max_tokens,
            "multimodal": EMBEDDING_CONFIG.multimodal,
            "available_models": {
                name: {
                    "name": config.name,
                    "dimension": config.dimension,
                    "multimodal": config.multimodal,
                    "model_path": str(config.model_path),
                }
                for name, config in EMBEDDING_MODELS.items()
            },
        },
        "chunk": {
            "chunk_size": CHUNK_CONFIG.chunk_size,
            "chunk_overlap": CHUNK_CONFIG.chunk_overlap,
            "min_chunk_size": CHUNK_CONFIG.min_chunk_size,
            "max_chunk_size": CHUNK_CONFIG.max_chunk_size,
            "preserve_headings": CHUNK_CONFIG.preserve_headings,
        },
        "retrieval": {
            "dense_top_k": RETRIEVAL_CONFIG.dense_top_k,
            "bm25_top_k": RETRIEVAL_CONFIG.bm25_top_k,
            "candidate_top_k": RETRIEVAL_CONFIG.candidate_top_k,
            "rerank_top_k": RETRIEVAL_CONFIG.rerank_top_k,
            "context_top_k": RETRIEVAL_CONFIG.context_top_k,
            "enable_bm25": RETRIEVAL_CONFIG.enable_bm25,
            "enable_reranker": RETRIEVAL_CONFIG.enable_reranker,
        },
        "context": {
            "max_chunk_chars": CONTEXT_CONFIG.max_chunk_chars,
            "max_context_chars": CONTEXT_CONFIG.max_context_chars,
        },
        "qdrant": {
            "mode": QDRANT_CONFIG.mode,
            "path": str(QDRANT_CONFIG.path),
            "collection": QDRANT_CONFIG.collection_name,
            "distance": QDRANT_CONFIG.distance,
        },
        "llm": {
            "provider": LLM_CONFIG.provider,
            "context_size": LLM_CONFIG.context_size,
            "max_tokens": LLM_CONFIG.max_tokens,
            "temperature": LLM_CONFIG.temperature,
            "reasoning": LLM_CONFIG.reasoning,
            "default_mode": LLM_CONFIG.default_mode,
        },
        "modes": mode_catalog(),
    }


# ============================================================================
# 知识库文件 API
# ============================================================================


@app.get("/api/documents")
def documents() -> dict[str, Any]:
    """知识库文件清单，**按类型分组**。

    分组：Markdown / PDF / 图片 / 文本。图片额外给出缩略图与原图地址，
    并标注**是否已进入索引** —— 新放进来的图片在重建索引之前不会被检索到，
    这一点必须在界面上看得见。
    """
    indexed = _indexed_doc_ids()

    groups: list[dict[str, Any]] = []

    # ---- Markdown ----------------------------------------------------
    markdown_docs = []
    for path in get_markdown_files():
        try:
            stat = path.stat()
        except OSError:
            continue

        rel = relative_markdown_path(path)

        markdown_docs.append(
            {
                "file": rel,
                "name": path.name,
                "size": stat.st_size,
                "modified_at": stat.st_mtime,
                "kind": "markdown",
                "indexed": path.stem in indexed,
            }
        )

    # ---- PDF ---------------------------------------------------------
    pdf_docs = []
    if PDF_DIR.is_dir():
        for path in sorted(PDF_DIR.rglob("*.pdf")):
            if not path.is_file():
                continue
            try:
                stat = path.stat()
            except OSError:
                continue

            pdf_docs.append(
                {
                    "file": str(path.relative_to(PDF_DIR)).replace("\\", "/"),
                    "name": path.name,
                    "size": stat.st_size,
                    "modified_at": stat.st_mtime,
                    "kind": "pdf",
                    "indexed": path.stem in indexed,
                }
            )

    # ---- 图片 ---------------------------------------------------------
    image_docs = []
    if IMAGE_DIR.is_dir():
        from src.ingest.image import iter_image_files

        for path in iter_image_files(IMAGE_DIR):
            try:
                stat = path.stat()
            except OSError:
                continue

            rel = str(
                path.resolve().relative_to(IMAGE_DIR.resolve())
            ).replace("\\", "/")

            encoded = "/".join(quote(seg) for seg in rel.split("/"))

            image_docs.append(
                {
                    "file": rel,
                    "name": path.name,
                    "size": stat.st_size,
                    "modified_at": stat.st_mtime,
                    "kind": "image",
                    "indexed": rel in indexed,
                    "url": f"/api/images/{encoded}",
                    "thumb_url": f"/api/images/{encoded}?w=96",
                }
            )

    # ---- 纯文本 -------------------------------------------------------
    text_docs = []
    if TEXT_DIR.is_dir():
        for path in sorted(TEXT_DIR.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".txt", ".text"}:
                continue
            try:
                stat = path.stat()
            except OSError:
                continue

            text_docs.append(
                {
                    "file": str(path.relative_to(TEXT_DIR)).replace("\\", "/"),
                    "name": path.name,
                    "size": stat.st_size,
                    "modified_at": stat.st_mtime,
                    "kind": "text",
                    "indexed": path.stem in indexed,
                }
            )

    for kind, label, items in (
        ("markdown", "Markdown", markdown_docs),
        ("pdf", "PDF", pdf_docs),
        ("image", "图片", image_docs),
        ("text", "文本", text_docs),
    ):
        groups.append(
            {
                "kind": kind,
                "label": label,
                "count": len(items),
                "indexed": sum(1 for d in items if d.get("indexed")),
                "documents": items,
            }
        )

    total = sum(g["count"] for g in groups)
    pending = sum(
        g["count"] - g["indexed"] for g in groups
    )

    return {
        # 向后兼容：旧的 frontend / 脚本仍可读 documents（仅 Markdown）
        "count": len(markdown_docs),
        "documents": markdown_docs,
        # 新结构：按类型分组
        "total": total,
        "pending_index": pending,
        "groups": groups,
    }


@app.get("/api/documents/{file_path:path}")
def document_info(file_path: str) -> dict[str, Any]:
    """单个 Markdown 文件信息 + chunk 概览。"""
    try:
        path = path_to_safe_relative(MARKDOWN_DIR, file_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")

    if not path.is_file():
        raise HTTPException(status_code=400, detail="目标不是文件")

    if path.suffix.lower() not in {".md", ".markdown"}:
        raise HTTPException(status_code=400, detail="目前只支持 Markdown 文件")

    try:
        chunks = markdown_to_chunks(path)
        stat = path.stat()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"解析 Markdown 失败：{exc}"
        ) from exc

    return {
        "file": relative_markdown_path(path),
        "name": path.name,
        "size": stat.st_size,
        "modified_at": stat.st_mtime,
        "chunk_count": len(chunks),
        "chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "point_id": chunk_point_id(chunk.chunk_id),
                "section": chunk.section,
                "length": len(chunk.content),
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ],
    }


# ============================================================================
# Chunk API
# ============================================================================


@app.post("/api/chunks/preview")
def chunk_preview(request: ChunkPreviewRequest) -> dict[str, Any]:
    """预览某个 Markdown 文件被切成了什么样。"""
    try:
        path = path_to_safe_relative(MARKDOWN_DIR, request.file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not path.exists():
        raise HTTPException(
            status_code=404, detail=f"文件不存在：{request.file}"
        )

    if not path.is_file():
        raise HTTPException(status_code=400, detail="目标不是文件")

    if path.suffix.lower() not in {".md", ".markdown"}:
        raise HTTPException(status_code=400, detail="目前只支持 Markdown 文件")

    start = time.perf_counter()

    try:
        chunks = markdown_to_chunks(path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"Chunk 解析失败：{exc}"
        ) from exc

    elapsed = time.perf_counter() - start

    return {
        "file": relative_markdown_path(path),
        "total_chunks": len(chunks),
        "returned_chunks": min(request.limit, len(chunks)),
        "elapsed_ms": round(elapsed * 1000, 2),
        "chunks": [
            serialize_chunk(chunk) for chunk in chunks[: request.limit]
        ],
    }


@app.get("/api/chunks/stats")
def chunk_stats() -> dict[str, Any]:
    """全库切块统计。"""
    start = time.perf_counter()
    chunks = load_markdown_directory()
    elapsed = time.perf_counter() - start

    total_chars = sum(len(chunk.content) for chunk in chunks)

    return {
        "documents": len({chunk.doc_id for chunk in chunks}),
        "chunks": len(chunks),
        "total_chars": total_chars,
        "average_chunk_length": (
            round(total_chars / len(chunks), 2) if chunks else 0
        ),
        "elapsed_ms": round(elapsed * 1000, 2),
    }


# ============================================================================
# 图片服务（多模态检索结果里的图片展示）
# ============================================================================


@app.get("/api/images/{image_path:path}")
def serve_image(
    image_path: str,
    w: int | None = Query(
        default=None, ge=32, le=2048,
        description="按宽度等比缩放，用于缩略图；不传则返回原图",
    ),
):
    """提供知识库目录下的图片。

    路径相对于 ``File/image``，并限制在目录内部（防路径逃逸）。
    """
    try:
        path = path_to_safe_relative(IMAGE_DIR, image_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not path.is_file():
        raise HTTPException(status_code=404, detail="图片不存在")

    if w is None:
        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return FileResponse(path, media_type=media_type)

    # 等比缩放作为缩略图
    try:
        import io

        from PIL import Image

        with Image.open(path) as img:
            img = img.convert("RGB")
            ratio = w / max(1, img.width)
            height = max(1, int(img.height * ratio))
            img = img.resize((w, height), Image.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="PNG", optimize=True)

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Cache-Control": "public, max-age=3600"},
        )

    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"生成缩略图失败：{exc}"
        ) from exc


# ============================================================================
# 检索
# ============================================================================


@app.post("/api/search")
def search(request: SearchRequest) -> dict[str, Any]:
    """混合检索：Dense + BM25 → RRF → Rerank → Context。"""
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="查询不能为空")

    if indexed_count() == 0:
        return {
            "status": "empty",
            "message": (
                "知识库尚未建索引。请先调用 POST /api/index 构建索引后再搜索。"
            ),
            "query": query,
            "results": [],
            "citations": [],
            "context": "",
            "stats": {
                "dense_hits": 0,
                "bm25_hits": 0,
                "candidates": 0,
                "final": 0,
                "use_bm25": request.use_bm25,
                "use_reranker": request.use_reranker,
            },
        }

    try:
        result = search_rag(
            query=query,
            top_k=request.top_k,
            use_bm25=request.use_bm25,
            use_reranker=request.use_reranker,
            include_images=request.include_images,
            **resolve_web_options(request),
        )
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"搜索失败：{exc}"
        ) from exc

    return {
        "status": "ok",
        "query": result["query"],
        "results": result["results"],
        "citations": result.get("citations", []),
        "context": result["context"],
        "stats": result["stats"],
        # 联网搜索摘要（前端据此显示「本地 N 条 · 网页 M 条」与失败原因）
        "web": result.get("web", {"enabled": False}),
    }


# ============================================================================
# 多轮对话
# ============================================================================


class ChatRequest(SearchRequest):
    """对话请求。"""

    conversation_id: str | None = Field(
        default=None,
        description="会话 ID。为空或不存在时自动新建会话",
    )
    mode: str | None = Field(
        default=None,
        description="问答档位：fast | precise，None 用配置默认值",
    )
    condense: bool = Field(
        default=True,
        description=(
            "是否用 LLM 把追问改写成独立可检索的查询。"
            "关闭后「那第二点呢」这类追问将检索不到内容"
        ),
    )
    image: str | None = Field(
        default=None,
        description=(
            "可选的图片：相对 File/image 的路径，或 data URL。"
            "需要对话服务已加载 mmproj（默认开启），否则服务端会拒绝"
        ),
    )
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=16, le=8192)
    provider: str | None = Field(default=None, description="llama_cpp | openai")


def _turn_to_dict(turn: Any) -> dict[str, Any]:
    """Turn → JSON 可序列化字典。"""
    from dataclasses import asdict

    return asdict(turn)


@app.get("/api/conversations")
def list_conversations(limit: int = 50) -> dict[str, Any]:
    """会话列表（按最近更新排序，不含轮次明细）。"""
    from src.rag.conversation import get_store

    items = get_store().list(limit=limit)

    return {"count": len(items), "conversations": items}


@app.post("/api/conversations")
def create_conversation() -> dict[str, Any]:
    """新建一个空会话。"""
    from src.rag.conversation import get_store

    conversation = get_store().create()

    return {"status": "ok", "conversation": conversation.to_dict(include_turns=True)}


@app.get("/api/conversations/{conversation_id}")
def get_conversation(conversation_id: str) -> dict[str, Any]:
    """会话详情（含全部轮次）。"""
    from src.rag.conversation import get_store

    conversation = get_store().get(conversation_id)

    if conversation is None:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"status": "ok", "conversation": conversation.to_dict(include_turns=True)}


@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(conversation_id: str) -> dict[str, Any]:
    """删除会话。"""
    from src.rag.conversation import get_store

    removed = get_store().delete(conversation_id)

    if not removed:
        raise HTTPException(status_code=404, detail="会话不存在")

    return {"status": "ok", "message": "会话已删除"}


def resolve_chat_image(image: str | None) -> str | None:
    """把请求里的 image 参数解析成视觉模型可用的形式。

    * ``data:`` 开头 → 原样返回
    * 否则视为相对 ``File/image`` 的路径，并做路径逃逸检查
    """
    if not image:
        return None

    value = image.strip()
    if not value:
        return None

    if value.startswith("data:"):
        return value

    try:
        path = path_to_safe_relative(IMAGE_DIR, value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"图片不存在：{value}")

    return str(path)


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    """多轮对话（非流式）。

    与 ``/api/ask`` 的区别：会带上会话历史，并先把追问改写成独立查询再检索。
    """
    from src.llm import LLMUnavailable
    from src.rag.chat import RAGChat
    from src.rag.conversation import get_store

    question = request.query.strip()

    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    if indexed_count() == 0:
        return {
            "status": "empty",
            "message": "知识库尚未建索引。请先调用 POST /api/index 构建索引。",
        }

    store = get_store()
    conversation = store.get_or_create(request.conversation_id)

    chat_engine = RAGChat(provider=request.provider)
    image_path = resolve_chat_image(request.image)

    try:
        turn = chat_engine.chat(
            conversation,
            question,
            top_k=request.top_k,
            use_bm25=request.use_bm25,
            use_reranker=request.use_reranker,
            include_images=request.include_images,
            **resolve_web_options(request),
            mode=request.mode,
            condense=request.condense,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            image=image_path,
        )
    except LLMUnavailable as exc:
        raise HTTPException(
            status_code=503,
            detail={"message": str(exc), "degraded": True},
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"对话失败：{exc}"
        ) from exc

    store.append_turn(conversation, turn)

    return {
        "status": "ok",
        "conversation_id": conversation.id,
        "title": conversation.title,
        "turn": _turn_to_dict(turn),
    }


@app.post("/api/chat/stream")
def chat_stream(request: ChatRequest) -> StreamingResponse:
    """多轮对话（SSE 流式）。"""
    from src.rag.chat import RAGChat
    from src.rag.conversation import get_store

    question = request.query.strip()

    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    def event_source() -> Iterator[str]:
        if indexed_count() == 0:
            yield sse(
                {"type": "error", "message": "知识库尚未建索引，请先构建索引。"}
            )
            return

        store = get_store()
        conversation = store.get_or_create(request.conversation_id)

        engine = RAGChat(provider=request.provider)

        try:
            image_path = resolve_chat_image(request.image)
        except HTTPException as exc:
            yield sse({"type": "error", "message": str(exc.detail)})
            return

        try:
            for event in engine.stream_chat(
                conversation,
                question,
                top_k=request.top_k,
                use_bm25=request.use_bm25,
                use_reranker=request.use_reranker,
                include_images=request.include_images,
                **resolve_web_options(request),
                mode=request.mode,
                condense=request.condense,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                image=image_path,
            ):
                # 生成结束后把这一轮落盘（turn 数据由后端自己产出，
                # 不依赖前端回传，避免中途断流导致历史丢失）
                if event.get("type") == "done" and event.get("turn"):
                    from src.rag.conversation import Turn

                    payload = event["turn"]
                    turn = Turn(
                        index=len(conversation.turns),
                        **{
                            k: v
                            for k, v in payload.items()
                            if k in Turn.__dataclass_fields__ and k != "index"
                        },
                    )
                    store.append_turn(conversation, turn)

                    event = dict(event)
                    event["conversation_id"] = conversation.id
                    event["title"] = conversation.title

                yield sse(event)

        except Exception as exc:  # noqa: BLE001
            yield sse({"type": "error", "message": f"对话失败：{exc}"})

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================================
# 设置与用量统计
# ============================================================================


class SettingsPatch(BaseModel):
    """设置修改。只提交要改的字段即可，其余保持不变。"""

    general: dict[str, Any] | None = None
    retrieval: dict[str, Any] | None = None
    chat: dict[str, Any] | None = None


@app.get("/api/settings")
def get_ui_settings() -> dict[str, Any]:
    """读取 WebUI 设置（含默认值，便于前端还原）。"""
    from src.settings_store import get_settings

    store = get_settings()

    return {
        "status": "ok",
        "settings": store.all(),
        "defaults": store.defaults(),
    }


@app.patch("/api/settings")
def patch_ui_settings(patch: SettingsPatch) -> dict[str, Any]:
    """更新设置。非法值会被忽略并保留原值。"""
    from src.settings_store import get_settings

    payload = patch.model_dump(exclude_none=True)
    settings = get_settings().update(payload)

    return {"status": "ok", "settings": settings}


@app.post("/api/settings/reset")
def reset_ui_settings() -> dict[str, Any]:
    """恢复默认设置。"""
    from src.settings_store import get_settings

    return {"status": "ok", "settings": get_settings().reset()}


@app.get("/api/usage")
def get_usage(recent_days: int = 14) -> dict[str, Any]:
    """累计 token 用量统计。"""
    from src.usage import get_tracker

    return {
        "status": "ok",
        "usage": get_tracker().summary(recent_days=recent_days),
    }


@app.post("/api/usage/reset")
def reset_usage() -> dict[str, Any]:
    """清零累计用量。"""
    from src.usage import get_tracker

    tracker = get_tracker()
    tracker.reset()

    return {"status": "ok", "usage": tracker.summary()}


# ============================================================================
# 联网搜索
# ============================================================================


@app.get("/api/web/config")
def get_web_search_config() -> dict[str, Any]:
    """联网搜索配置（**API Key 只返回掩码**）+ 可用后端清单。"""
    from src.web import get_web_config, provider_catalog

    return {
        "status": "ok",
        "config": get_web_config().public(),
        "providers": provider_catalog(),
    }


@app.patch("/api/web/config")
def patch_web_search_config(patch: dict[str, Any]) -> dict[str, Any]:
    """更新联网搜索配置。

    ``api_key`` 传空串表示**保持不变** —— 前端回显的是掩码，
    直接提交会把真 Key 冲掉。
    """
    from src.web import get_web_config

    store = get_web_config()
    store.update(patch)

    return {"status": "ok", "config": store.public()}


@app.post("/api/web/config/clear")
def clear_web_search_config() -> dict[str, Any]:
    """清空联网搜索配置（含 API Key），恢复默认。"""
    from src.web import get_web_config

    store = get_web_config()
    store.clear()

    return {"status": "ok", "config": store.public()}


@app.post("/api/web/test")
def test_web_search() -> dict[str, Any]:
    """连通性测试：真的搜一次，回报后端、条数与耗时。"""
    from src.web import WebSearcher

    try:
        result = WebSearcher().test()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"联网搜索测试失败：{exc}"
        ) from exc

    return {"status": "ok", "result": result}


@app.post("/api/web/search")
def web_search_only(request: SearchRequest) -> dict[str, Any]:
    """只走联网搜索，不查本地知识库（便于单独调试）。"""
    from src.rag.context import build_citations, build_context
    from src.web import WebSearcher

    outcome = WebSearcher().search(
        request.query,
        limit=request.web_limit,
        fetch_pages=request.web_fetch_pages,
    )

    return {
        "status": "ok" if outcome.ok else "error",
        "query": request.query,
        "results": outcome.results,
        "citations": build_citations(outcome.results),
        "context": build_context(outcome.results),
        "web": outcome.summary(),
    }


# ============================================================================
# 生成式问答
# ============================================================================


@app.get("/api/llm/status")
def api_llm_status() -> dict[str, Any]:
    """生成式模型状态。"""
    return llm_status()


@app.get("/api/llm/models")
def api_llm_models() -> dict[str, Any]:
    """可选模型清单 + 当前生效模型。

    前端用这个接口渲染模型下拉框。
    """
    from src.llm import active_model, available_models, chat_models

    try:
        usable = chat_models()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"读取模型清单失败：{exc}"
        ) from exc

    try:
        everything = available_models()
    except Exception:  # noqa: BLE001
        everything = usable

    return {
        "models": usable,
        "all": everything,
        "active": active_model(),
        "count": len(usable),
    }


class LlmProviderRequest(BaseModel):
    """切换 LLM 使用方式。"""

    provider: str = Field(
        ...,
        description="llama_cpp（本地离线）| openai（云端 API）",
        examples=["llama_cpp", "openai"],
    )


@app.get("/api/llm/providers")
def api_llm_providers() -> dict[str, Any]:
    """两种使用方式的状态（本地离线 / 云端 API）。"""
    from src.llm import providers_status

    try:
        return providers_status()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"读取方式状态失败：{exc}"
        ) from exc


@app.post("/api/llm/provider")
def api_llm_set_provider(request: LlmProviderRequest) -> dict[str, Any]:
    """切换使用方式。"""
    from src.llm.cloud import set_provider

    try:
        provider = set_provider(request.provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    label = "本地离线" if provider == "llama_cpp" else "云端 API"

    return {
        "status": "ok",
        "provider": provider,
        "message": f"已切换到「{label}」。",
    }


@app.get("/api/llm/cloud")
def api_llm_cloud_get() -> dict[str, Any]:
    """当前云端配置（**API Key 只返回掩码**）。"""
    from src.llm.cloud import KNOWN_ENDPOINTS, load_cloud

    payload = load_cloud().to_public_dict()
    payload["known_endpoints"] = KNOWN_ENDPOINTS
    return payload


class CloudConfigRequest(BaseModel):
    """云端配置请求。"""

    base_url: str | None = Field(default=None, description="OpenAI 兼容端点")
    model: str | None = Field(default=None, description="模型名")
    api_key: str | None = Field(
        default=None,
        description="API Key。传空字符串表示保持原有 Key 不变",
    )
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, ge=1, le=32768)


@app.post("/api/llm/cloud")
def api_llm_cloud_set(request: CloudConfigRequest) -> dict[str, Any]:
    """保存云端配置。"""
    from src.llm.cloud import update_cloud

    try:
        settings = update_cloud(
            base_url=request.base_url,
            model=request.model,
            api_key=request.api_key,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=400, detail=f"保存云端配置失败：{exc}"
        ) from exc

    return {"status": "ok", **settings.to_public_dict()}


@app.post("/api/llm/cloud/clear")
def api_llm_cloud_clear() -> dict[str, Any]:
    """删除云端配置（含 API Key）。"""
    from src.llm.cloud import clear_cloud, load_cloud

    clear_cloud()

    return {
        "status": "ok",
        "message": "已删除云端配置与 API Key。",
        **load_cloud().to_public_dict(),
    }


@app.post("/api/llm/cloud/test")
def api_llm_cloud_test(request: CloudConfigRequest) -> dict[str, Any]:
    """测试云端端点连通性（不落盘）。"""
    from src.llm.cloud import load_cloud, test_connection

    stored = load_cloud()

    # 未传 key 时用已保存的，方便「只改地址后测试」
    api_key = request.api_key if request.api_key else stored.api_key
    base_url = request.base_url or stored.base_url
    model = request.model or stored.model

    ok, message, models = test_connection(base_url, api_key, model)

    return {
        "ok": ok,
        "message": message,
        "models": models[:100],
    }


class LlmSelectRequest(BaseModel):
    """切换本地模型请求。"""

    model: str = Field(
        ...,
        min_length=1,
        description="模型标识：文件名片段 / 清单序号 / 完整路径",
        examples=["Qwen3.8-4B", "2"],
    )


@app.post("/api/llm/select")
def api_llm_select(request: LlmSelectRequest) -> dict[str, Any]:
    """切换活动模型。

    会停掉当前 llama-server 并释放显存；新模型在下次问答时懒加载
    （首次约需 8~10 秒）。
    """
    from src.llm import active_model, switch_model

    try:
        entry = switch_model(request.model)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"切换模型失败：{exc}"
        ) from exc

    return {
        "status": "ok",
        "model": entry,
        "active": active_model(),
        "message": (
            f"已切换到 {entry['file_name']}。"
            "新模型将在下次提问时加载（首次约 8~10 秒）。"
        ),
    }


@app.post("/api/ask")
def ask(request: AskRequest) -> dict[str, Any]:
    """检索 + 生成式问答（非流式）。

    生成模型不可用时返回 **503**，并在 ``degraded`` 中带上检索结果，
    让前端可以降级展示。
    """
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="查询不能为空")

    if indexed_count() == 0:
        return {
            "status": "empty",
            "message": "知识库尚未建索引。请先调用 POST /api/index 构建索引。",
            "query": query,
            "answer": "",
            "results": [],
            "citations": [],
        }

    answerer = RAGAnswerer(provider=request.provider)

    ok, reason = answerer.llm.available()  # type: ignore[attr-defined]

    if not ok:
        # 降级：至少把检索结果返回给前端
        degraded = search_rag(
            query=query,
            top_k=request.top_k,
            use_bm25=request.use_bm25,
            use_reranker=request.use_reranker,
            include_images=request.include_images,
            **resolve_web_options(request),
        )

        raise HTTPException(
            status_code=503,
            detail={
                "message": f"生成式问答不可用：{reason}",
                "degraded": True,
                "results": degraded["results"],
                "citations": degraded.get("citations", []),
                "context": degraded["context"],
                "stats": degraded["stats"],
            },
        )

    try:
        result = answerer.answer(
            query=query,
            top_k=request.top_k,
            use_bm25=request.use_bm25,
            use_reranker=request.use_reranker,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            mode=request.mode,
            include_images=request.include_images,
            **resolve_web_options(request),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=500, detail=f"问答失败：{exc}"
        ) from exc

    return {"status": "ok", **result.to_dict()}


@app.post("/api/ask/stream")
def ask_stream(request: AskRequest) -> StreamingResponse:
    """检索 + 流式问答（SSE）。

    事件类型见 :meth:`src.rag.answer.RAGAnswerer.stream`。
    """
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="查询不能为空")

    def event_source() -> Iterator[str]:
        if indexed_count() == 0:
            yield sse(
                {
                    "type": "error",
                    "message": "知识库尚未建索引，请先构建索引。",
                }
            )
            return

        answerer = RAGAnswerer(provider=request.provider)

        try:
            for event in answerer.stream(
                query=query,
                top_k=request.top_k,
                use_bm25=request.use_bm25,
                use_reranker=request.use_reranker,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                mode=request.mode,
                include_images=request.include_images,
                **resolve_web_options(request),
            ):
                yield sse(event)

        except Exception as exc:  # noqa: BLE001
            yield sse({"type": "error", "message": f"流式问答失败：{exc}"})

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # 关闭 Nginx 之类反代的缓冲，保证逐字到达
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================================
# 索引
# ============================================================================


@app.get("/api/index/status")
def index_status() -> dict[str, Any]:
    """索引状态（不触发 embedding 加载）。"""
    collection = f"{QDRANT_CONFIG.collection_name}_{model_key()}"

    chunks = 0
    error: str | None = None

    try:
        chunks = get_vector_db().count()
    except Exception as exc:  # noqa: BLE001
        error = str(exc)

    bm25_exists = False
    try:
        bm25_exists = bm25_index_path().exists()
    except Exception:  # noqa: BLE001
        pass

    payload: dict[str, Any] = {
        "status": "error" if error else "ok",
        "indexed_chunks": chunks,
        "bm25_index_exists": bm25_exists,
        "collection": collection,
        "indexing": _index_state["running"],
        "last_result": _index_state["last_result"],
        "last_error": _index_state["last_error"],
    }

    if error:
        payload["message"] = f"读取索引状态失败：{error}"

    return payload


@app.post("/api/index")
def build_index(request: IndexRequest) -> dict[str, Any]:
    """构建 / 重建索引。

    使用非阻塞锁：已有任务在跑时返回 **409**，而不是排队堆积。
    """
    if not _index_lock.acquire(blocking=False):
        raise HTTPException(
            status_code=409,
            detail="已有索引任务正在执行，请等待其完成。",
        )

    _index_state.update(
        {"running": True, "started_at": time.time(), "last_error": None}
    )

    start = time.perf_counter()

    try:
        # --------------------------------------------------------------
        # 腾出显存：建索引要加载 embedding 模型，而 8GB 显卡上
        # 「对话模型 + 视觉模型 + embedding」三者同时驻留会超出预算。
        # 这里先停掉对话与视觉服务（它们都是懒加载的，下次问答会自动重启）。
        # --------------------------------------------------------------
        try:
            close_llms()
            stop_llama_servers()
            _index_state["freed_vram"] = True
        except Exception:  # noqa: BLE001
            _index_state["freed_vram"] = False

        result = ingest_all(
            recreate=request.rebuild,
            include_images=request.include_images,
            prune=request.prune,
        )

    except Exception as exc:  # noqa: BLE001
        _index_state["last_error"] = str(exc)
        raise HTTPException(
            status_code=500, detail=f"索引构建失败：{exc}"
        ) from exc

    finally:
        _index_state["running"] = False
        _index_lock.release()

    elapsed = time.perf_counter() - start

    payload = {
        "status": "ok",
        "elapsed_ms": round(elapsed * 1000, 2),
        "rebuild": request.rebuild,
        "prune": request.prune,
        **result,
    }

    _index_state["last_result"] = payload

    return payload


# ============================================================================
# Web UI
# ============================================================================


@app.get("/ui")
async def web_ui() -> Any:
    """返回内置 Web UI。"""
    index_file = _WEB_DIR / "index.html"

    if index_file.exists() and index_file.stat().st_size > 0:
        return FileResponse(index_file, media_type="text/html")

    return HTMLResponse(
        content=(
            "<!DOCTYPE html><html lang='zh-CN'><head>"
            "<meta charset='UTF-8'><title>Local RAG</title></head>"
            "<body style='font-family:sans-serif;padding:40px'>"
            "<h1>Local RAG</h1>"
            "<p>API 已启动，但 web/index.html 缺失或为空。</p>"
            "<p><a href='/docs'>API 文档</a> · "
            "<a href='/api/health'>健康检查</a></p>"
            "</body></html>"
        )
    )


# ============================================================================
# 启动
# ============================================================================


def run_server() -> None:
    """启动 Uvicorn。"""
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "缺少 uvicorn。\n请安装：\n    pip install uvicorn\n"
        ) from exc

    uvicorn.run(
        app,
        host=SERVER_CONFIG.host,
        port=SERVER_CONFIG.port,
        reload=False,
        log_level=LOGGING_CONFIG.level.lower(),
    )


def main() -> None:
    print("=" * 70)
    print("Local RAG Server v0.2.0")
    print("=" * 70)
    print(f"项目      : {PROJECT_ROOT}")
    print(f"监听      : {SERVER_CONFIG.host}:{SERVER_CONFIG.port}")
    print(f"Embedding : {EMBEDDING_CONFIG.name} (dim={EMBEDDING_CONFIG.dimension})")
    print(f"LLM       : {LLM_CONFIG.provider}")

    status = llm_status()
    if status.get("available"):
        print(f"            {status.get('model', '')}")
    else:
        print(f"            不可用 —— {status.get('reason', '')}")

    print(f"Markdown  : {MARKDOWN_DIR}")
    print(f"Qdrant    : {QDRANT_CONFIG.path}")
    print()
    print(f"Web UI    : http://{SERVER_CONFIG.host}:{SERVER_CONFIG.port}/ui")
    print(f"API Docs  : http://{SERVER_CONFIG.host}:{SERVER_CONFIG.port}/docs")
    print("=" * 70)

    run_server()


if __name__ == "__main__":
    main()
