"""Markdown 摄取：切块 → embedding → 写入 Qdrant + BM25 索引。"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from src.config import MARKDOWN_DIR
from src.database.vector_db import get_vector_db
from src.embedding import get_embedder, model_key
from src.ids import chunk_point_id
from src.ingest.chunker import (
    Chunk,
    load_markdown_directory,
    markdown_to_chunks,
)
from src.retrieval.bm25 import BM25Index, bm25_index_path


def chunk_to_payload(chunk: Chunk) -> dict:
    """Chunk → Qdrant payload。

    注意：``chunk_id`` 保存在 payload 中，是检索阶段对外暴露的可读标识；
    真正的 Qdrant point id 由 :func:`chunk_to_id` 生成（UUID）。
    """
    payload = chunk.to_dict()
    # Qdrant payload 中不能放 list of list 之类的复杂结构，
    # section_path 已经是 list[str]，可以保留。
    return payload


def chunk_to_id(chunk: Chunk) -> str:
    """Chunk → Qdrant point id。

    Qdrant 要求 string 类型的 point id 必须是 UUID，因此这里把可读的
    ``chunk_id`` 确定性地映射为 UUIDv5。同一个 chunk 重复写入会命中同一个
    id，从而保证 upsert 幂等。
    """
    return chunk_point_id(chunk.chunk_id)


def ingest_markdown(
    recreate: bool = False,
    embedder_name: str | None = None,
    directory: str | Path | None = None,
    prune: bool = True,
    progress: "Callable[[str], None] | None" = None,
) -> dict:
    """扫描 Markdown 目录，切块、嵌入、写库。

    Args:
        recreate: 是否清空 collection 后重建。
        embedder_name: 使用哪个 embedding 模型。
        directory: 默认 File/Markdown。
        prune: 是否删除「磁盘上已不存在」的文档在库中残留的点。
        progress: 可选的进度回调，用于 CLI / Web 展示。

    Returns:
        含 chunks / indexed / pruned / collection / embedding 的统计字典。
    """

    def log(message: str) -> None:
        # 有进度回调时由回调负责输出，避免重复打印
        if progress is not None:
            progress(message)
        else:
            print(message)

    directory = Path(directory or MARKDOWN_DIR)

    if not directory.exists():
        raise FileNotFoundError(f"Markdown 目录不存在: {directory}")

    log(f"[ingest] 扫描 {directory}")
    chunks = load_markdown_directory(directory)
    log(f"[ingest] 生成 {len(chunks)} 个 chunk")

    embedder = get_embedder(embedder_name)
    db = get_vector_db(embedder_name, recreate=recreate)

    if not chunks:
        log("[ingest] 没有可索引的内容")
        return {
            "chunks": 0,
            "indexed": 0,
            "pruned": 0,
            "collection": db.collection_name,
            "embedding": embedder.name,
        }

    texts = [c.content for c in chunks]
    log(f"[ingest] 开始 embedding（{embedder.name}）...")
    vectors = embedder.embed(texts)

    ids = [chunk_to_id(c) for c in chunks]
    payloads = [chunk_to_payload(c) for c in chunks]

    log(f"[ingest] 写入 Qdrant collection={db.collection_name}")
    written = db.upsert(ids, vectors, payloads)

    # ------------------------------------------------------------------
    # 清理：磁盘上已删除 / 重命名过的文档，其旧 chunk 不应继续留在库中
    # ------------------------------------------------------------------

    pruned = 0
    if prune and not recreate:
        current_doc_ids = {c.doc_id for c in chunks}
        stale = db.doc_ids() - current_doc_ids

        if stale:
            log(f"[ingest] 清理 {len(stale)} 个已失效文档")
            pruned = db.delete_by_doc_ids(sorted(stale))

    # ------------------------------------------------------------------
    # BM25 索引：全量重建，保证与 Qdrant 内容一致
    # ------------------------------------------------------------------

    bm25 = BM25Index(name=model_key(embedder_name))
    bm25.build([c.to_dict() for c in chunks])
    bm25.save(bm25_index_path(embedder_name))

    log(f"[ingest] 完成，写入 {written} 条，清理 {pruned} 条")

    return {
        "chunks": len(chunks),
        "indexed": written,
        "pruned": pruned,
        "collection": db.collection_name,
        "embedding": embedder.name,
    }


def ingest_markdown_file(
    file_path: str | Path,
    embedder_name: str | None = None,
) -> dict:
    """只摄取单个 Markdown 文件（增量更新）。

    会先删除该文档在库中的旧 chunk，再写入新 chunk。
    这样文件被改写、章节减少时不会残留孤儿数据。
    """
    path = Path(file_path)
    chunks = markdown_to_chunks(path)

    if not chunks:
        return {"chunks": 0, "indexed": 0, "removed": 0}

    embedder = get_embedder(embedder_name)
    db = get_vector_db(embedder_name)

    # 先清掉这个文档的旧版本
    removed = db.delete_by_doc_ids([chunks[0].doc_id])

    vectors = embedder.embed([c.content for c in chunks])
    ids = [chunk_to_id(c) for c in chunks]
    payloads = [chunk_to_payload(c) for c in chunks]

    written = db.upsert(ids, vectors, payloads)

    return {
        "file": str(path),
        "chunks": len(chunks),
        "indexed": written,
        "removed": removed,
    }


__all__ = [
    "ingest_markdown",
    "ingest_markdown_file",
    "chunk_to_payload",
    "chunk_to_id",
]