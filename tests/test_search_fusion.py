"""RRF 融合与检索编排测试（不触网、不加载模型）。"""

from __future__ import annotations

import unittest

from src.rag.search import _rrf_fusion


def hit(item_id: str, score: float = 1.0, content: str = "") -> dict:
    return {
        "id": item_id,
        "score": score,
        "source": "vector",
        "payload": {"chunk_id": item_id, "content": content or item_id},
    }


class TestRRFFusion(unittest.TestCase):
    def test_merges_both_lists(self) -> None:
        dense = [hit("a"), hit("b")]
        bm25 = [hit("c")]

        fused = _rrf_fusion(dense, bm25)

        self.assertEqual({item["id"] for item in fused}, {"a", "b", "c"})

    def test_item_in_both_lists_ranks_highest(self) -> None:
        dense = [hit("a"), hit("b")]
        bm25 = [hit("b"), hit("c")]

        fused = _rrf_fusion(dense, bm25)

        self.assertEqual(fused[0]["id"], "b", "同时命中两路的条目应排第一")

    def test_scores_are_reciprocal_rank_sums(self) -> None:
        dense = [hit("a")]
        bm25 = [hit("a")]

        fused = _rrf_fusion(dense, bm25, k=60)

        # 1/(60+0+1) * 2
        self.assertAlmostEqual(fused[0]["fusion_score"], 2 / 61, places=6)

    def test_empty_dense(self) -> None:
        fused = _rrf_fusion([], [hit("a"), hit("b")])
        self.assertEqual([item["id"] for item in fused], ["a", "b"])

    def test_empty_bm25(self) -> None:
        fused = _rrf_fusion([hit("a"), hit("b")], [])
        self.assertEqual([item["id"] for item in fused], ["a", "b"])

    def test_both_empty(self) -> None:
        self.assertEqual(_rrf_fusion([], []), [])

    def test_ordering_follows_rank_not_raw_score(self) -> None:
        """RRF 只看排名，不看原始分数。"""
        dense = [hit("a", score=0.1), hit("b", score=0.9)]
        bm25 = []

        fused = _rrf_fusion(dense, bm25)

        self.assertEqual(fused[0]["id"], "a")

    def test_preserves_payload(self) -> None:
        fused = _rrf_fusion([hit("a", content="hello")], [])
        self.assertEqual(fused[0]["payload"]["content"], "hello")

    def test_output_is_sorted_descending(self) -> None:
        dense = [hit("a"), hit("b"), hit("c")]
        bm25 = [hit("c"), hit("a")]

        fused = _rrf_fusion(dense, bm25)
        scores = [item["fusion_score"] for item in fused]

        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
