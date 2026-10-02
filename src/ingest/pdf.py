"""PDF 摄取：PyMuPDF 提取文本，按页切块，可选提取图片。

当前阶段：
    PDF 文本 → 普通 chunk → 用 Qwen3 embedding
    PDF 图片 → 保存到 File/image/，由 image.py 处理
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from src.config import (
    CHUNK_CONFIG,
    IMAGE_DIR,
    PDF_DIR,
)
from src.ingest.chunker import Chunk

try:
    # PyMuPDF >= 1.24 推荐使用 `pymupdf` 作为模块名，
    # 旧的 `fitz` 别名会打印弃用警告。
    import pymupdf as fitz  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    import fitz  # type: ignore[no-redef]


def _split_text(text: str, max_chars: int, overlap: int) -> list[str]:
    """按字符切分，保留段落边界。"""
    text = text.strip()
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    pieces: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))

        # 尽量在换行处切开
        if end < len(text):
            nl = text.rfind("\n", start, end)
            if nl > start + max_chars // 2:
                end = nl

        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return pieces


def pdf_to_chunks(
    file_path: str | Path,
    extract_images: bool = False,
) -> list[Chunk]:
    """把 PDF 转成 Chunk 列表。

    每个 chunk 携带 page / source 元数据。
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF 不存在: {path}")

    doc = fitz.open(path)

    doc_id = path.stem
    chunks: list[Chunk] = []

    max_chars = CHUNK_CONFIG.max_chunk_size
    overlap = CHUNK_CONFIG.chunk_overlap

    for page_index in range(len(doc)):
        page = doc[page_index]
        page_number = page_index + 1

        text = page.get_text("text") or ""
        text = text.strip()

        if not text:
            continue

        # 去掉页眉页脚常见形式：单独的数字行
        lines = [
            line for line in text.split("\n")
            if line.strip() and not line.strip().isdigit()
        ]
        text = "\n".join(lines)

        pieces = _split_text(text, max_chars, overlap)

        for local_index, piece in enumerate(pieces):
            chunk_id = f"{doc_id}::p{page_number:04d}::{local_index + 1:03d}"

            content = (
                f"文档：{doc_id}\n"
                f"页码：第 {page_number} 页\n\n"
                f"{piece}"
            )

            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    doc_id=doc_id,
                    title=doc_id,
                    section=f"第 {page_number} 页",
                    content=content,
                    source=str(path),
                    metadata={
                        "file_name": path.name,
                        "extension": ".pdf",
                        "page": page_number,
                        "total_pages": len(doc),
                        "content_length": len(content),
                    },
                    chunk_index=local_index,
                    heading_level=0,
                )
            )

        if extract_images:
            _extract_page_images(doc, page, doc_id, page_number)

    doc.close()

    # 重新编号
    for i, chunk in enumerate(chunks):
        chunk.chunk_index = i

    return chunks


def _extract_page_images(doc, page, doc_id: str, page_number: int) -> None:
    """把 PDF 页面里的图片保存到 File/image/。"""
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    try:
        images = page.get_images(full=True)
    except Exception:  # noqa: BLE001
        return

    for img_index, img in enumerate(images):
        xref = img[0]
        try:
            pix = fitz.Pixmap(doc, xref)
            if pix.n - pix.alpha >= 4:  # CMYK
                pix = fitz.Pixmap(fitz.csRGB, pix)

            raw = pix.tobytes("png")
            digest = hashlib.md5(raw).hexdigest()[:10]

            out = IMAGE_DIR / (
                f"{doc_id}_p{page_number:04d}_{img_index}_{digest}.png"
            )

            if not out.exists():
                out.write_bytes(raw)

            pix = None

        except Exception:  # noqa: BLE001
            continue


def iter_pdf_files(directory: str | Path = PDF_DIR):
    directory = Path(directory)
    if not directory.exists():
        return
    for path in directory.rglob("*.pdf"):
        if path.is_file():
            yield path


def ingest_pdf(
    recreate: bool = False,
    embedder_name: str | None = None,
    directory: str | Path | None = None,
    extract_images: bool = False,
) -> dict:
    """扫描 PDF 目录并写入索引。"""
    from src.database.vector_db import get_vector_db
    from src.embedding import get_embedder, model_key
    from src.ingest.markdown import chunk_to_id, chunk_to_payload
    from src.retrieval.bm25 import BM25Index, bm25_index_path

    directory = Path(directory or PDF_DIR)

    all_chunks: list[Chunk] = []
    for pdf in iter_pdf_files(directory):
        try:
            all_chunks.extend(
                pdf_to_chunks(pdf, extract_images=extract_images)
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[pdf] 处理失败: {pdf}\n  原因: {exc}")

    if not all_chunks:
        return {"chunks": 0, "indexed": 0}

    embedder = get_embedder(embedder_name)
    db = get_vector_db(embedder_name, recreate=recreate)

    vectors = embedder.embed([c.content for c in all_chunks])
    ids = [chunk_to_id(c) for c in all_chunks]
    payloads = [chunk_to_payload(c) for c in all_chunks]

    written = db.upsert(ids, vectors, payloads)

    # 追加到 BM25
    bm25 = BM25Index(name=model_key(embedder_name))
    bm25.load_or_build(bm25_index_path(embedder_name), [
        c.to_dict() for c in all_chunks
    ])
    bm25.save(bm25_index_path(embedder_name))

    return {
        "chunks": len(all_chunks),
        "indexed": written,
        "collection": db.collection_name,
    }


__all__ = [
    "pdf_to_chunks",
    "ingest_pdf",
    "iter_pdf_files",
]