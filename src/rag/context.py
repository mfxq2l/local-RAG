"""把检索结果拼成 LLM 可读的 Context，并生成引用列表。

Context 形如：

    [1]【来源：nmap知识点.md | 章节：端口扫描 > -sS】
    ...正文...

    ---

    [2]【来源：...】
    ...正文...

编号 ``[n]`` 的作用是让 LLM 在回答里可以直接写 ``[1]`` ``[2]`` 来标注出处，
前端再把编号渲染成可点击的引用卡片。
"""

from __future__ import annotations

from typing import Any

from src.config import CONTEXT_CONFIG


def _payload(item: dict[str, Any]) -> dict[str, Any]:
    """安全取出 payload（可能为 None）。"""
    payload = item.get("payload")
    return payload if isinstance(payload, dict) else {}


def _metadata(item: dict[str, Any]) -> dict[str, Any]:
    """安全取出 metadata（可能为 None 或非 dict）。"""
    metadata = _payload(item).get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def citation_of(item: dict[str, Any], index: int) -> dict[str, Any]:
    """把一条检索结果转成结构化引用信息。

    带上 ``modality`` 与 ``image_path``，这样前端在**流式**场景下也能精确
    渲染图片缩略图（流式的 citations 事件不携带完整 results，只能靠引用
    本身的信息）。

    联网结果额外带 ``source_type`` / ``url`` / ``domain``，
    前端据此把本地文档与网页渲染成不同样式（网页是可点的外链）。
    """
    payload = _payload(item)
    metadata = _metadata(item)

    source = payload.get("source") or ""
    file_name = metadata.get("file_name") or source

    modality = metadata.get("modality") or "text"
    source_type = metadata.get("source_type") or "local"
    url = metadata.get("url") or ""

    # 网页结果没抓到正文时，用摘要兜底，避免引用卡片空白
    preview_text = payload.get("content") or metadata.get("snippet") or ""

    return {
        "index": index,
        "chunk_id": payload.get("chunk_id") or item.get("id") or "",
        "file_name": file_name,
        "source": source,
        "title": payload.get("title") or metadata.get("title") or "",
        "section": payload.get("section") or "",
        "page": metadata.get("page"),
        "modality": modality,
        "image_path": metadata.get("image_path") or "",
        "is_image": modality == "image",
        # 联网搜索相关
        "source_type": source_type,
        "is_web": source_type == "web",
        "url": url,
        "domain": metadata.get("domain") or "",
        "engine": metadata.get("engine") or "",
        "score": item.get("rerank_score", item.get("score")),
        "preview": preview_text[:200],
    }


def _format_header(item: dict[str, Any], index: int | None) -> str:
    payload = _payload(item)
    metadata = _metadata(item)

    parts: list[str] = []

    # 网页结果：显示标题与链接，让模型知道这是外部来源
    if (metadata.get("source_type") or "local") == "web":
        url = metadata.get("url") or ""
        title = metadata.get("file_name") or metadata.get("domain") or url

        if CONTEXT_CONFIG.include_source and title:
            parts.append(f"网页：{title}")
        if url:
            parts.append(f"链接：{url}")
    else:
        if CONTEXT_CONFIG.include_source:
            source = payload.get("source") or ""
            file_name = metadata.get("file_name") or source
            if file_name:
                parts.append(f"来源：{file_name}")

        if CONTEXT_CONFIG.include_section:
            section = payload.get("section") or ""
            if section:
                parts.append(f"章节：{section}")

        if CONTEXT_CONFIG.include_page:
            page = metadata.get("page")
            if page:
                parts.append(f"页码：第 {page} 页")

    label = f"[{index}]" if index is not None else ""

    if not parts:
        return f"{label}\n" if label else ""

    return f"{label}【" + " | ".join(parts) + "】\n"


def build_context(
    results: list[dict[str, Any]],
    max_chars: int | None = None,
    numbered: bool = True,
) -> str:
    """把多个检索结果拼成一个字符串。

    Args:
        results: 检索结果列表。
        max_chars: 整体最大字符数，默认取配置。
        numbered: 是否加上 ``[n]`` 编号前缀。
    """
    max_chars = max_chars or CONTEXT_CONFIG.max_context_chars

    blocks: list[str] = []
    total = 0

    for position, item in enumerate(results, start=1):
        payload = _payload(item)
        content = payload.get("content") or ""

        if len(content) > CONTEXT_CONFIG.max_chunk_chars:
            content = content[: CONTEXT_CONFIG.max_chunk_chars] + "……"

        block = _format_header(item, position if numbered else None) + content

        # 至少保留第一个 block，避免 max_chars 过小导致 context 全空
        if blocks and total + len(block) > max_chars:
            break

        blocks.append(block)
        total += len(block)

    return CONTEXT_CONFIG.separator.join(blocks)


def build_citations(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """生成与 :func:`build_context` 编号一致的引用列表。"""
    return [
        citation_of(item, position)
        for position, item in enumerate(results, start=1)
    ]


__all__ = [
    "build_context",
    "build_citations",
    "citation_of",
]
