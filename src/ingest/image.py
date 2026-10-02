"""图片摄取：视觉模型生成语义描述 → 文本 embedding → 与文本共用一个向量库。

为什么是「描述」而不是「图片向量」
----------------------------------
实测（10 种请求形态）：llama.cpp 的 ``/v1/embeddings`` **不接受图片**，
传入图片字段会被静默忽略 —— 换一张图返回的向量完全相同。环境里也没有
PyTorch / CLIP 可以绕过。因此图片必须先由视觉模型转成**文本描述**，
再走文本向量化。

为什么和文本放在同一个 collection
---------------------------------
描述本身就是文本，用同一个 embedding 模型编码后与文本 chunk 处于同一向量
空间。好处：

* 一次查询天然同时召回文字与图片，无需跨库融合（不同模型的分数不可比）
* 只需一个 embedding 服务，省下约 1.4GB 显存

代价是图片向量由「描述」而非像素决定 —— 这正是当前环境的约束。
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Callable, Iterable

from src.config import DATA_DIR, IMAGE_DIR, VISION_CONFIG
from src.ingest.chunker import Chunk


_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}

# 图片 chunk 的标识约定：<doc_id>::image::001
# 其他模块（如摄取管线的清理逻辑）靠它识别图片 chunk，避免误删。
IMAGE_CHUNK_MARKER = "::image::"

# 描述缓存：视觉模型每张图约 1 秒，重复建索引时不应重算
_CAPTION_CACHE_PATH = DATA_DIR / "captions_cache.json"
_CAPTION_CACHE_VERSION = 1
_caption_lock = threading.Lock()


def _caption_cache_key(path: Path) -> str:
    """按「路径 + 大小 + mtime」失效。"""
    try:
        stat = path.stat()
    except OSError:
        return ""
    return f"{path.resolve()}|{stat.st_size}|{int(stat.st_mtime)}"


def load_caption_cache() -> dict:
    try:
        if _CAPTION_CACHE_PATH.exists():
            data = json.loads(_CAPTION_CACHE_PATH.read_text(encoding="utf-8"))
            if data.get("version") == _CAPTION_CACHE_VERSION:
                return data.get("entries", {})
    except Exception:  # noqa: BLE001
        pass
    return {}


def save_caption_cache(entries: dict) -> None:
    try:
        _CAPTION_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CAPTION_CACHE_PATH.write_text(
            json.dumps(
                {"version": _CAPTION_CACHE_VERSION, "entries": entries},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except Exception:  # noqa: BLE001
        pass


def iter_image_files(directory: str | Path = IMAGE_DIR) -> Iterable[Path]:
    """递归遍历图片文件。"""
    directory = Path(directory)

    if not directory.is_dir():
        return

    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in _IMAGE_EXTENSIONS:
            yield path


def describe_image_basic(path: str | Path) -> str:
    """**降级**描述：仅从图片元数据生成。

    视觉模型不可用时使用。注意这种描述**几乎没有可检索的语义内容**，
    只能靠文件名匹配，效果远不如视觉模型生成的描述。
    """
    path = Path(path)

    if not path.exists():
        return f"图片文件（不存在）: {path.name}"

    try:
        from PIL import Image

        with Image.open(path) as img:
            width, height = img.size
            fmt = img.format or path.suffix.lstrip(".").upper()
            mode = img.mode

        return (
            f"图片：{path.name}\n"
            f"格式：{fmt}\n"
            f"尺寸：{width}x{height}\n"
            f"色彩模式：{mode}\n"
        )
    except Exception as exc:  # noqa: BLE001
        return f"图片：{path.name}（读取失败: {exc}）"


def _image_dimensions(path: Path) -> tuple[int, int]:
    try:
        from PIL import Image

        with Image.open(path) as img:
            return img.size
    except Exception:  # noqa: BLE001
        return (0, 0)


def image_to_chunk(
    path: str | Path,
    *,
    description: str | None = None,
    relative_to: Path | None = None,
) -> Chunk:
    """单张图片 → 一个 Chunk。

    Args:
        path: 图片路径。
        description: 已生成的语义描述；``None`` 时使用降级描述。
        relative_to: 用于生成相对路径的基准目录（便于 API 提供图片）。
    """
    path = Path(path)
    doc_id = path.stem

    caption = description if description is not None else describe_image_basic(path)
    width, height = _image_dimensions(path)

    content = f"图片：{path.name}\n{caption.strip()}"

    try:
        base = relative_to or IMAGE_DIR
        rel_path = str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except Exception:  # noqa: BLE001
        rel_path = path.name

    source_kind = "vlm" if description is not None else "metadata"

    return Chunk(
        chunk_id=f"{doc_id}::image::001",
        doc_id=f"image::{rel_path}",
        title=path.name,
        section="图片",
        content=content,
        source=str(path),
        metadata={
            "file_name": path.name,
            "extension": path.suffix.lower(),
            "modality": "image",
            "image_path": rel_path,
            "width": width,
            "height": height,
            "caption_source": source_kind,
            "content_length": len(content),
        },
        chunk_index=0,
        heading_level=0,
    )


def collect_image_chunks(
    directory: str | Path | None = None,
    *,
    captioner=None,
    progress: Callable[[str], None] | None = None,
    describe: bool = True,
) -> list[Chunk]:
    """扫描图片目录并生成 chunk（需要时调用视觉模型）。

    Args:
        directory: 图片目录，默认 ``File/image``。
        captioner: :class:`src.vision.VisionCaptioner`；``None`` 时自动创建。
        progress: 进度回调。
        describe: 是否使用视觉模型生成描述；``False`` 时用降级描述。

    Returns:
        图片 chunk 列表。视觉模型不可用时会自动降级并给出提示。
    """
    directory = Path(directory or IMAGE_DIR)

    if not directory.is_dir():
        return []

    files = list(iter_image_files(directory))

    if not files:
        return []

    def log(message: str) -> None:
        if progress is not None:
            progress(message)
        else:
            print(message)

    log(f"[image] 发现 {len(files)} 张图片")

    reusable = captioner

    if describe and reusable is None:
        try:
            from src.vision import VisionCaptioner

            reusable = VisionCaptioner()
        except Exception as exc:  # noqa: BLE001
            log(f"[image] 视觉模型初始化失败，改用手工描述: {exc}")
            reusable = None

    if describe and reusable is not None:
        ok, reason = reusable.available()
        if not ok:
            log(f"[image] 视觉模型不可用（{reason}），改用手工描述")
            reusable = None

    chunks: list[Chunk] = []

    if reusable is not None:
        cache = load_caption_cache()

        keys = {path: _caption_cache_key(path) for path in files}
        pending = [
            path for path in files
            if not (keys[path] and cache.get(keys[path], {}).get("text"))
        ]
        cached_hits = len(files) - len(pending)

        if cached_hits:
            log(f"[image] {cached_hits} 张图命中描述缓存，无需重新识别")

        fresh: dict[str, str] = {}

        if pending:
            log(f"[image] 使用视觉模型生成描述：{reusable.model_path.name}")

            descriptions = reusable.caption_many(
                pending,
                on_progress=lambda i, n, name, text, elapsed: log(
                    f"[image] ({i}/{n}) {name} {elapsed:.1f}s "
                    f"{text[:60].strip()}{'…' if len(text) > 60 else ''}"
                ),
            )

            for path, desc in zip(pending, descriptions):
                if desc.strip():
                    fresh[keys[path]] = {
                        "text": desc,
                        "file": path.name,
                    }

        cache.update(fresh)

        with _caption_lock:
            save_caption_cache(cache)

        for path in files:
            key = keys[path]
            desc = ""
            if key:
                desc = (fresh.get(key) or cache.get(key) or {}).get("text", "")

            chunks.append(
                image_to_chunk(
                    path,
                    # 描述为空（识别失败且无缓存）时退回降级描述，
                    # 保证图片仍能被文件名检索到
                    description=desc if desc.strip() else None,
                    relative_to=directory,
                )
            )
    else:
        for path in files:
            chunks.append(
                image_to_chunk(path, description=None, relative_to=directory)
            )

    return chunks


def ingest_image(
    recreate: bool = False,
    embedder_name: str | None = None,
    directory: str | Path | None = None,
    progress: Callable[[str], None] | None = None,
) -> dict:
    """单独索引图片目录（写入与文本相同的 collection）。"""
    from src.database.vector_db import get_vector_db
    from src.embedding import get_embedder
    from src.ingest.markdown import chunk_to_id, chunk_to_payload
    from src.retrieval.bm25 import BM25Index, bm25_index_path
    from src.embedding import model_key

    def log(message: str) -> None:
        if progress is not None:
            progress(message)
        else:
            print(message)

    chunks = collect_image_chunks(directory, progress=progress)

    if not chunks:
        log("[image] 没有可索引的图片")
        return {"chunks": 0, "indexed": 0}

    embedder = get_embedder(embedder_name)
    db = get_vector_db(embedder_name, recreate=recreate)

    log(f"[image] 向量化 {len(chunks)} 条描述（{embedder.name}）")
    vectors = embedder.embed([c.content for c in chunks])

    written = db.upsert(
        [chunk_to_id(c) for c in chunks],
        vectors,
        [chunk_to_payload(c) for c in chunks],
    )

    # 把图片描述并入 BM25，使关键词也能命中图片
    if VISION_CONFIG.index_caption_in_bm25:
        bm25 = BM25Index(name=model_key(embedder_name))
        bm25.load_or_build(
            bm25_index_path(embedder_name),
            [c.to_dict() for c in chunks],
        )
        bm25.save(bm25_index_path(embedder_name))
        log("[image] 已并入 BM25 索引")

    return {
        "chunks": len(chunks),
        "indexed": written,
        "collection": db.collection_name,
    }


__all__ = [
    "collect_image_chunks",
    "describe_image_basic",
    "image_to_chunk",
    "ingest_image",
    "iter_image_files",
]
