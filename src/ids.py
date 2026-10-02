"""稳定的 Qdrant point id 生成。

背景
----
Qdrant 在本地（embedded）模式下要求 string 类型的 point id **必须是合法
UUID**，否则写入时会直接抛错：

    ValueError: Point id Burp Suite sqlmap 速查卡::...::001 is not a valid UUID

而本项目 chunker 产出的 ``chunk_id`` 形如 ``"nmap知识点::端口扫描::001"``，
是可读的自然语言标识，无法直接作为 point id。

方案
----
用 **UUIDv5**（基于 SHA-1 的确定性命名空间 UUID）把 ``chunk_id`` 映射成稳定
UUID：

    chunk_id "nmap知识点::端口扫描::001"
        ↓  uuid5(RAG_NAMESPACE, chunk_id)
    point_id "0b0f9a0e-...."

这样做的收益：

1. 满足 Qdrant 的 UUID 约束；
2. **确定性** —— 同一个 chunk_id 永远得到同一个 UUID，因此重复建索引是
   幂等 upsert，不会产生重复点；
3. 原始可读的 ``chunk_id`` 仍然完整保存在 payload 中，检索结果、RRF 融合
   和前端展示都继续使用它。

注意：RRF 融合依赖 dense 与 BM25 两侧使用**同一个** key，本模块同时被
ingest 与 retrieval 复用，保证两侧一致。
"""

from __future__ import annotations

import uuid

__all__ = [
    "RAG_NAMESPACE",
    "chunk_point_id",
    "is_uuid",
]


# 项目命名空间：由 URL 派生，保证跨机器/跨会话稳定。
RAG_NAMESPACE = uuid.uuid5(
    uuid.NAMESPACE_URL,
    "https://local.rag/chunk",
)


def chunk_point_id(chunk_id: str) -> str:
    """把可读的 ``chunk_id`` 转成确定性的 UUID 字符串。

    Args:
        chunk_id: chunker 生成的原始 chunk 标识。

    Returns:
        标准 36 字符 UUID 字符串。

    Raises:
        ValueError: ``chunk_id`` 为空。
    """

    if not chunk_id or not chunk_id.strip():
        raise ValueError("chunk_id 不能为空")

    return str(uuid.uuid5(RAG_NAMESPACE, chunk_id))


def is_uuid(value: object) -> bool:
    """判断给定值是否为合法的 UUID 字符串。"""

    if not isinstance(value, str):
        return False

    try:
        uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False

    return True
