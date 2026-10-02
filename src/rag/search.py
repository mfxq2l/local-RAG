"""RAG 检索主流程。

流程：
    Query
      ↓
    Dense (Qdrant)   BM25
      ↓                ↓
        RRF Fusion
              ↓
           Reranker
              ↓
           Top-K
              ↓
           Context
"""

from __future__ import annotations

from typing import Any

from src.config import RETRIEVAL_CONFIG
from src.embedding import model_key
from src.rag.context import build_citations, build_context
from src.retrieval.bm25 import BM25Index, bm25_index_path, load_cached
from src.settings_store import relevance_floor
from src.retrieval.rerank import EmbeddingReranker
from src.retrieval.vector import VectorRetriever
from src.web import WebSearcher


def _rrf_fusion(
    dense: list[dict[str, Any]],
    bm25: list[dict[str, Any]],
    k: int = 60,
) -> list[dict[str, Any]]:
    """Reciprocal Rank Fusion。"""
    scores: dict[str, float] = {}
    store: dict[str, dict[str, Any]] = {}

    for rank, item in enumerate(dense):
        key = item["id"]
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
        store.setdefault(key, item)

    for rank, item in enumerate(bm25):
        key = item["id"]
        scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank + 1)
        store.setdefault(key, item)

    ordered = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

    fused: list[dict[str, Any]] = []
    for key, score in ordered:
        item = dict(store[key])
        item["fusion_score"] = score
        fused.append(item)

    return fused


def _is_image(item: dict[str, Any]) -> bool:
    """判断检索结果是否为图片。"""
    payload = item.get("payload") or {}
    metadata = payload.get("metadata")
    if not isinstance(metadata, dict):
        return False
    return metadata.get("modality") == "image"


class RAGSearch:
    def __init__(self, name: str | None = None) -> None:
        self.key = model_key(name)
        self.vector = VectorRetriever(name)
        self.reranker = EmbeddingReranker(name)
        self._bm25: BM25Index | None = None
        # 联网搜索器（每次调用时才真正发请求）
        self.web = WebSearcher()

    # ------------------------------------------------------------------
    # BM25 懒加载
    # ------------------------------------------------------------------

    @property
    def bm25(self) -> BM25Index:
        if self._bm25 is None:
            # 走带缓存的加载：同一进程内跨请求复用，
            # 避免每次检索都重新 unpickle 整个索引（约 68ms）
            path = bm25_index_path(self.key)

            index = load_cached(path)

            if index is None:
                index = BM25Index(name=self.key)

            self._bm25 = index

        return self._bm25

    # ------------------------------------------------------------------
    # 主流程
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int | None = None,
        use_bm25: bool | None = None,
        use_reranker: bool | None = None,
        include_images: bool = True,
        use_web: bool | None = None,
        web_limit: int | None = None,
        web_fetch_pages: bool | None = None,
    ) -> dict[str, Any]:
        top_k = top_k or RETRIEVAL_CONFIG.context_top_k
        use_bm25 = (
            RETRIEVAL_CONFIG.enable_bm25
            if use_bm25 is None
            else use_bm25
        )
        use_reranker = (
            RETRIEVAL_CONFIG.enable_reranker
            if use_reranker is None
            else use_reranker
        )

        # 1) Dense
        dense_hits = self.vector.search(
            query,
            top_k=RETRIEVAL_CONFIG.dense_top_k,
            include_images=include_images,
        )

        # 2) BM25
        bm25_hits: list[dict[str, Any]] = []
        if use_bm25 and len(self.bm25) > 0:
            bm25_hits = self.bm25.search(
                query,
                top_k=RETRIEVAL_CONFIG.bm25_top_k,
            )

            # BM25 是纯词法匹配，图片描述也在索引里，需要在这里过滤
            if not include_images:
                bm25_hits = [h for h in bm25_hits if not _is_image(h)]

        # 3) Fusion
        if bm25_hits:
            candidates = _rrf_fusion(dense_hits, bm25_hits)
        else:
            candidates = list(dense_hits)

        candidates = candidates[: RETRIEVAL_CONFIG.candidate_top_k]

        # 4) Rerank
        #
        # 候选文档的向量建索引时已存在 Qdrant 中，这里直接取回复用，
        # 避免每次都重新 embedding 几十个 chunk（实测 4.52s -> 毫秒级）。
        rerank_reused = 0

        if use_reranker and candidates:
            candidate_keys = [
                str(
                    c.get("id")
                    or (c.get("payload") or {}).get("chunk_id")
                    or ""
                )
                for c in candidates
            ]

            doc_vectors: dict[str, list[float]] = {}
            try:
                doc_vectors = self.vector.vectors_for(
                    [k for k in candidate_keys if k]
                )
                rerank_reused = len(doc_vectors)
            except Exception as exc:  # noqa: BLE001
                print(f"[search] 取回已存向量失败，将重新 embedding: {exc}")

            try:
                final = self.reranker.rerank(
                    query,
                    candidates,
                    top_k=RETRIEVAL_CONFIG.rerank_top_k,
                    query_vector=self.vector.last_query_vector,
                    doc_vectors=doc_vectors,
                )
            except Exception as exc:  # noqa: BLE001
                print(f"[search] rerank 失败: {exc}")
                final = candidates[: RETRIEVAL_CONFIG.rerank_top_k]
        else:
            final = candidates[: RETRIEVAL_CONFIG.rerank_top_k]

        # 5) 相关性过滤 + 截取最终 context
        #
        # 低于下限的结果视为「与问题无关」。实测闲聊类输入的最高分在
        # 0.32~0.39，真实问题在 0.58 以上，用 0.45 能干净分开。
        # 全部低于下限时结果为空 —— 调用方据此走「自然回答」而不是
        # 硬套不相干的资料答非所问。
        floor = relevance_floor(RETRIEVAL_CONFIG.min_relevance_score)
        dropped = 0

        if floor > 0 and use_reranker and final:
            kept = [
                item for item in final
                if item.get("rerank_score", 0.0) >= floor
            ]
            dropped = len(final) - len(kept)
            final = kept

        final = final[:top_k]

        # 6) 联网搜索
        #
        # 本地结果先截断再追加网页结果 —— 这样 top_k 只约束本地文档，
        # 网页不会被本地结果挤掉。
        #
        # 网页结果**不参与**本地的相关性下限过滤：那是为「向量相似度」
        # 定的阈值，而搜索引擎的排名是另一套标准，硬套会误杀。
        web_summary: dict[str, Any] = {"enabled": False}
        web_results: list[dict[str, Any]] = []

        if use_web:
            outcome = self.web.search(
                query, limit=web_limit, fetch_pages=web_fetch_pages
            )

            web_results = outcome.results
            final = final + web_results

            web_summary = {
                "enabled": True,
                **outcome.summary(),
            }

        # 7) Context
        context = build_context(final)

        return {
            "query": query,
            "results": final,
            "citations": build_citations(final),
            "context": context,
            "web": web_summary,
            "stats": {
                "dense_hits": len(dense_hits),
                "bm25_hits": len(bm25_hits),
                "candidates": len(candidates),
                "final": len(final),
                "local": len(final) - len(web_results),
                "web": len(web_results),
                "dropped_low_relevance": dropped,
                "min_relevance": floor,
                "rerank_reused_vectors": rerank_reused,
                "use_bm25": use_bm25,
                "use_reranker": use_reranker,
                "use_web": bool(use_web),
            },
        }


def search_rag(
    query: str,
    top_k: int = 5,
    use_bm25: bool | None = None,
    use_reranker: bool | None = None,
    name: str | None = None,
    include_images: bool = True,
    use_web: bool | None = None,
    web_limit: int | None = None,
    web_fetch_pages: bool | None = None,
) -> dict[str, Any]:
    """给 server.py 用的顶层函数。"""
    return RAGSearch(name).search(
        query=query,
        top_k=top_k,
        use_bm25=use_bm25,
        use_reranker=use_reranker,
        include_images=include_images,
        use_web=use_web,
        web_limit=web_limit,
        web_fetch_pages=web_fetch_pages,
    )


__all__ = ["RAGSearch", "search_rag"]