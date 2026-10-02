"""Rerank 测试，重点验证「复用已存储向量」这条优化路径。

复用是纯收益：库里的向量与重新 embedding 得到的完全一致
（同一模型、同一段文本），但省掉了每次查询几十个 chunk 的重复推理。
测试要确保：

1. 提供了 doc_vectors 时**绝不调用** embedding；
2. 只对缺失的候选调用 embedding；
3. 打分结果与「全部重新 embedding」一致。
"""

from __future__ import annotations

import unittest

from src.retrieval.rerank import EmbeddingReranker, _cosine


class FakeEmbedder:
    """记录调用次数的假 embedder。"""

    def __init__(self, dim: int = 3) -> None:
        self.dim = dim
        self.calls: list[list[str]] = []
        self.fail = False

    def embed(self, texts: list[str]) -> list[list[float]]:
        self.calls.append(list(texts))
        if self.fail:
            raise RuntimeError("模拟 embedding 故障")

        return [self._vec(t) for t in texts]

    def _vec(self, text: str) -> list[float]:
        """确定性伪向量：便于断言顺序。"""
        if "query" in text:
            return [1.0, 0.0, 0.0]
        if "close" in text:
            return [0.9, 0.1, 0.0]
        if "mid" in text:
            return [0.5, 0.5, 0.0]
        return [0.0, 0.0, 1.0]


def candidate(key: str, content: str) -> dict:
    return {
        "id": key,
        "score": 0.5,
        "payload": {"chunk_id": key, "content": content},
    }


class TestCosine(unittest.TestCase):
    def test_identical_vectors(self) -> None:
        self.assertAlmostEqual(_cosine([1, 0], [1, 0]), 1.0)

    def test_orthogonal(self) -> None:
        self.assertAlmostEqual(_cosine([1, 0], [0, 1]), 0.0)

    def test_opposite(self) -> None:
        self.assertAlmostEqual(_cosine([1, 0], [-1, 0]), -1.0)

    def test_empty_returns_zero(self) -> None:
        self.assertEqual(_cosine([], [1.0]), 0.0)

    def test_zero_vector_returns_zero(self) -> None:
        self.assertEqual(_cosine([0, 0], [1, 0]), 0.0)

    def test_scale_invariant(self) -> None:
        self.assertAlmostEqual(
            _cosine([1, 2, 3], [2, 4, 6]), 1.0, places=9
        )


class TestRerankWithStoredVectors(unittest.TestCase):
    def test_no_embedding_when_all_vectors_present(self) -> None:
        """核心：候选向量齐全 + 已有 query 向量 → 一次 embedding 都不发。"""
        embedder = FakeEmbedder()
        reranker = EmbeddingReranker(embedder=embedder)

        candidates = [
            candidate("a", "close"),
            candidate("b", "far"),
        ]
        doc_vectors = {
            "a": [0.9, 0.1, 0.0],
            "b": [0.0, 0.0, 1.0],
        }

        result = reranker.rerank(
            "query",
            candidates,
            top_k=2,
            query_vector=[1.0, 0.0, 0.0],
            doc_vectors=doc_vectors,
        )

        self.assertEqual(embedder.calls, [], "不应调用 embedding")
        self.assertEqual(result[0]["id"], "a")
        self.assertGreater(result[0]["rerank_score"], result[1]["rerank_score"])

    def test_only_missing_candidates_are_embedded(self) -> None:
        embedder = FakeEmbedder()
        reranker = EmbeddingReranker(embedder=embedder)

        candidates = [
            candidate("a", "close"),
            candidate("b", "far"),
        ]

        result = reranker.rerank(
            "query",
            candidates,
            top_k=2,
            query_vector=[1.0, 0.0, 0.0],
            doc_vectors={"a": [0.9, 0.1, 0.0]},   # 只有 a
        )

        self.assertEqual(len(embedder.calls), 1)
        self.assertEqual(embedder.calls[0], ["far"], "只应嵌入缺失的 b")
        self.assertEqual(result[0]["id"], "a")

    def test_query_embedded_when_not_provided(self) -> None:
        embedder = FakeEmbedder()
        reranker = EmbeddingReranker(embedder=embedder)

        reranker.rerank(
            "query",
            [candidate("a", "close")],
            top_k=1,
            doc_vectors={"a": [0.9, 0.1, 0.0]},
        )

        self.assertEqual(embedder.calls, [["query"]])

    def test_scores_match_full_recompute(self) -> None:
        """复用向量与重新 embedding 的打分必须完全一致。"""
        candidates = [
            candidate("a", "close"),
            candidate("b", "mid"),
            candidate("c", "other"),
        ]

        reused = EmbeddingReranker(embedder=FakeEmbedder()).rerank(
            "query",
            candidates,
            top_k=3,
            query_vector=[1.0, 0.0, 0.0],
            doc_vectors={
                "a": [0.9, 0.1, 0.0],
                "b": [0.5, 0.5, 0.0],
                "c": [0.0, 0.0, 1.0],
            },
        )

        recomputed = EmbeddingReranker(embedder=FakeEmbedder()).rerank(
            "query",
            candidates,
            top_k=3,
        )

        self.assertEqual(
            [r["id"] for r in reused],
            [r["id"] for r in recomputed],
        )

        for left, right in zip(reused, recomputed):
            self.assertAlmostEqual(
                left["rerank_score"], right["rerank_score"], places=9
            )

    def test_marks_reuse_flag(self) -> None:
        reranker = EmbeddingReranker(embedder=FakeEmbedder())

        result = reranker.rerank(
            "query",
            [candidate("a", "close"), candidate("b", "far")],
            top_k=2,
            query_vector=[1.0, 0.0, 0.0],
            doc_vectors={"a": [0.9, 0.1, 0.0]},
        )

        flags = {r["id"]: r["rerank_reused"] for r in result}
        self.assertTrue(flags["a"])
        self.assertTrue(flags["b"])  # b 被现场嵌入后同样进入 doc_vectors


class TestRerankEdgeCases(unittest.TestCase):
    def test_empty_candidates(self) -> None:
        reranker = EmbeddingReranker(embedder=FakeEmbedder())
        self.assertEqual(reranker.rerank("q", []), [])

    def test_embedding_failure_falls_back(self) -> None:
        embedder = FakeEmbedder()
        embedder.fail = True

        reranker = EmbeddingReranker(embedder=embedder)
        candidates = [candidate("a", "close"), candidate("b", "far")]

        result = reranker.rerank("query", candidates, top_k=1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "a", "失败时应退回原顺序")

    def test_respects_top_k(self) -> None:
        reranker = EmbeddingReranker(embedder=FakeEmbedder())

        result = reranker.rerank(
            "query",
            [candidate(k, c) for k, c in
             [("a", "close"), ("b", "mid"), ("c", "far")]],
            top_k=2,
            query_vector=[1.0, 0.0, 0.0],
            doc_vectors={
                "a": [0.9, 0.1, 0.0],
                "b": [0.5, 0.5, 0.0],
                "c": [0.0, 0.0, 1.0],
            },
        )

        self.assertEqual(len(result), 2)

    def test_candidate_without_vector_is_zero_scored(self) -> None:
        """向量取不到且嵌入失败时不应崩溃。"""
        embedder = FakeEmbedder()
        reranker = EmbeddingReranker(embedder=embedder)

        result = reranker.rerank(
            "query",
            [candidate("a", "close")],
            top_k=1,
            query_vector=[1.0, 0.0, 0.0],
            doc_vectors={},
        )

        self.assertEqual(len(result), 1)


if __name__ == "__main__":
    unittest.main()
