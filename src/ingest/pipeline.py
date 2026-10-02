"""统一摄取管线：文本与图片一起切块、向量化、入同一个向量库。

设计要点
--------
* **一次 embedding 调用**：文本 chunk 与图片描述拼成一个列表一起向量化，
  避免重复加载与多次往返。
* **一个 collection**：图片描述也是文本，与文本 chunk 处于同一向量空间，
  因此一次查询即可同时召回两者。
* **BM25 覆盖两者**：图片描述同样进入 BM25，关键词也能命中图片。
* **清理失效文档**：磁盘上已删除的文档（含图片）在库中的残留点会被删除。
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from src.config import MARKDOWN_DIR
from src.database.vector_db import get_vector_db
from src.embedding import get_embedder, model_key
from src.ingest.chunker import Chunk, load_markdown_directory
from src.ingest.image import IMAGE_CHUNK_MARKER
from src.ingest.markdown import chunk_to_id, chunk_to_payload
from src.retrieval.bm25 import BM25Index, bm25_index_path, invalidate_cache


def ingest_all(
    recreate: bool = False,
    embedder_name: str | None = None,
    include_images: bool = True,
    directory: str | Path | None = None,
    image_dir: str | Path | None = None,
    prune: bool = True,
    progress: Callable[[str], None] | None = None,
) -> dict:
    """索引 Markdown（可选含图片），写入同一个 collection。

    Args:
        recreate: 是否清空后重建。
        embedder_name: embedding 模型名。
        include_images: 是否把图片也用视觉模型描述后一起索引。
        directory: Markdown 目录，默认 ``File/Markdown``。
        image_dir: 图片目录，默认 ``File/image``。
        prune: 是否清理磁盘上已不存在的文档所残留的向量。
        progress: 进度回调。

    Returns:
        统计字典，含 text_chunks / image_chunks / indexed / pruned 等。
    """

    def log(message: str) -> None:
        if progress is not None:
            progress(message)
        else:
            print(message)

    directory = Path(directory or MARKDOWN_DIR)

    if not directory.exists():
        raise FileNotFoundError(f"Markdown 目录不存在: {directory}")

    # ------------------------------------------------------------------
    # 1) 文本
    # ------------------------------------------------------------------
    log(f"[ingest] 扫描文本 {directory}")
    text_chunks = load_markdown_directory(directory)
    log(f"[ingest] 文本 chunk: {len(text_chunks)}")

    # ------------------------------------------------------------------
    # 2) 图片
    # ------------------------------------------------------------------
    image_chunks: list[Chunk] = []
    image_note = ""

    if include_images:
        from src.ingest.image import collect_image_chunks

        try:
            image_chunks = collect_image_chunks(
                image_dir, progress=progress
            )
            image_note = f"图片描述已生成（{len(image_chunks)} 张）"
        except Exception as exc:  # noqa: BLE001
            image_note = f"图片处理失败，已跳过: {exc}"
            log(f"[ingest] {image_note}")
            image_chunks = []
    else:
        image_note = "本次未包含图片"

    log(f"[ingest] 图片 chunk: {len(image_chunks)}")

    chunks = text_chunks + image_chunks

    # ------------------------------------------------------------------
    # 3) 向量化 —— **先算完，再动数据库**
    #
    # 顺序很重要：重建时若先清空再 embedding，一旦中途进程退出（被 kill、
    # 崩溃、断电），旧索引就永久丢失，而新的还没算出来。
    # 因此这里先把所有向量算出来，确认成功后才清空并写入。
    # ------------------------------------------------------------------
    embedder = get_embedder(embedder_name)

    # 注意：这里**不带 recreate**，只确保 collection 存在，
    # 真正的清空推迟到向量全部就绪之后。
    db = get_vector_db(embedder_name)

    vectors: list[list[float]] = []

    if chunks:
        log(f"[ingest] 向量化 {len(chunks)} 条（{embedder.name}）")
        vectors = embedder.embed([c.content for c in chunks])

        if len(vectors) != len(chunks):
            raise RuntimeError(
                f"向量数量与 chunk 数量不一致：{len(vectors)} vs {len(chunks)}"
            )

    # 向量已全部就绪，此时才动数据库。
    #
    # 重建不再「先清空」：point id 是 chunk_id 的确定性 UUIDv5，相同内容
    # 会命中相同 id，因此「全量 upsert + 清理不在本次结果中的旧 chunk」
    # 与「清空后重建」结果等价，却**没有破坏性窗口** —— 中途崩溃只会留下
    # 一个超集，下次成功运行即自愈。
    #
    # 唯一必须真正重置的情况是**向量维度变了**（换了 embedding 模型但
    # collection 名没变），那时清空不可避免。
    if recreate:
        current_dim = db.existing_dimension()
        if current_dim is not None and current_dim != db.dimension:
            log(
                f"[ingest] 向量维度变化 {current_dim} -> {db.dimension}，"
                f"需要重建 collection"
            )
            db.ensure_collection(recreate=True)
        else:
            db.ensure_collection()

    written = 0

    if chunks:
        log(f"[ingest] 写入 Qdrant collection={db.collection_name}")
        written = db.upsert(
            [chunk_to_id(c) for c in chunks],
            vectors,
            [chunk_to_payload(c) for c in chunks],
        )

    # ------------------------------------------------------------------
    # 4) 清理
    # ------------------------------------------------------------------
    pruned = 0

    if chunks:
        if recreate:
            # 精确重建：删掉所有不在本次结果中的旧 chunk。
            # 注意 delete_by_chunk_ids 按 payload 里的 chunk_id 值过滤，
            # 因此传的是可读 chunk_id，而不是 UUID point id。
            stored_chunk_ids = db.payload_values("chunk_id")
            stale_chunk_ids = stored_chunk_ids - {c.chunk_id for c in chunks}

            # 同 prune 分支：本次没扫图片就不要删图片索引
            if not include_images:
                skipped = {
                    cid for cid in stale_chunk_ids
                    if IMAGE_CHUNK_MARKER in cid
                }
                if skipped:
                    log(
                        f"[ingest] 本次未处理图片，保留已有 "
                        f"{len(skipped)} 个图片 chunk"
                    )
                stale_chunk_ids = {
                    cid for cid in stale_chunk_ids
                    if IMAGE_CHUNK_MARKER not in cid
                }

            if stale_chunk_ids:
                log(f"[ingest] 清理 {len(stale_chunk_ids)} 个已不存在的 chunk")
                pruned = db.delete_by_chunk_ids(sorted(stale_chunk_ids))
        elif prune:
            current_doc_ids = {c.doc_id for c in chunks}
            stale_docs = db.doc_ids() - current_doc_ids

            # 「本次没扫描图片」不等于「要删掉图片索引」。
            # 否则用户只要用 include_images=false 建一次索引，
            # 之前索引好的图片就被静默清空了。
            if not include_images:
                skipped = sorted(d for d in stale_docs if d.startswith("image::"))
                if skipped:
                    log(
                        f"[ingest] 本次未处理图片，保留已有 {len(skipped)} 个图片索引"
                    )
                stale_docs = {
                    d for d in stale_docs if not d.startswith("image::")
                }

            if stale_docs:
                log(f"[ingest] 清理 {len(stale_docs)} 个已失效文档")
                pruned = db.delete_by_doc_ids(sorted(stale_docs))

    # ------------------------------------------------------------------
    # 5) BM25（覆盖文本 + 图片描述）
    # ------------------------------------------------------------------
    if chunks:
        bm25 = BM25Index(name=model_key(embedder_name))
        bm25.build([c.to_dict() for c in chunks])
        bm25.save(bm25_index_path(embedder_name))

        # 索引内容变了，必须让检索侧的缓存失效
        invalidate_cache(bm25_index_path(embedder_name))

        log("[ingest] BM25 索引已重建")

    log(f"[ingest] 完成，写入 {written} 条，清理 {pruned} 条")

    return {
        "chunks": len(chunks),
        "text_chunks": len(text_chunks),
        "image_chunks": len(image_chunks),
        "indexed": written,
        "pruned": pruned,
        "collection": db.collection_name,
        "embedding": embedder.name,
        "image_note": image_note,
    }

__all__ = ["ingest_all"]
