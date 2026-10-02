"""Dense 向量检索。"""

from __future__ import annotations

from typing import Any

from qdrant_client import models

from src.config import RETRIEVAL_CONFIG
from src.database.vector_db import get_vector_db
from src.embedding import get_embedder, model_key
from src.ids import chunk_point_id


def _text_only_filter() -> models.Filter:
    """只返回非图片结果的 Qdrant 过滤器。"""
    return models.Filter(
        must_not=[
            models.FieldCondition(
                key="metadata.modality",
                match=models.MatchValue(value="image"),
            )
        ]
    )


class VectorRetriever:
    def __init__(self, name: str | None = None) -> None:
        self.key = model_key(name)
        self.embedder = get_embedder(name)
        self.db = get_vector_db(name)

        # 最近一次检索使用的 query 向量，供 rerank 复用，避免重复 embedding
        self.last_query_vector: list[float] | None = None

    def search(
        self,
        query: str,
        top_k: int | None = None,
        score_threshold: float | None = None,
        include_images: bool = True,
    ) -> list[dict[str, Any]]:
        top_k = top_k or RETRIEVAL_CONFIG.dense_top_k
        score_threshold = (
            score_threshold
            if score_threshold is not None
            else RETRIEVAL_CONFIG.similarity_threshold
        )

        q_vec = self.embedder.embed_one(query)
        self.last_query_vector = q_vec

        hits = self.db.search(
            query_vector=q_vec,
            top_k=top_k,
            score_threshold=score_threshold,
            query_filter=None if include_images else _text_only_filter(),
        )

        results: list[dict[str, Any]] = []
        for hit in hits:
            payload = hit["payload"]
            results.append(
                {
                    "id": payload.get("chunk_id", hit["id"]),
                    "score": hit["score"],
                    "payload": payload,
                    "source": "vector",
                }
            )
        return results

    def vectors_for(
        self,
        chunk_ids: list[str],
    ) -> dict[str, list[float]]:
        """按 ``chunk_id`` 取回已存储的文档向量。

        ``chunk_id`` → point id 是确定性 UUIDv5 映射（见 :mod:`src.ids`），
        因此可以直接反查。
        """
        if not chunk_ids:
            return {}

        mapping: dict[str, str] = {}
        for chunk_id in chunk_ids:
            try:
                mapping[chunk_point_id(chunk_id)] = chunk_id
            except ValueError:
                continue

        stored = self.db.get_vectors(list(mapping))

        return {
            mapping[point_id]: vector
            for point_id, vector in stored.items()
            if point_id in mapping
        }

    def count(self) -> int:
        return self.db.count()

    def count_images(self) -> int:
        """已索引的图片数量。"""
        return self.db.count_where("metadata.modality", "image")

    def count_text(self) -> int:
        """已索引的文本 chunk 数量（总数 - 图片数）。"""
        return max(0, self.count() - self.count_images())


__all__ = ["VectorRetriever"]
