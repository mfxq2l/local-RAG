"""Qdrant 封装测试（本地 embedded 模式，使用临时目录）。

覆盖两个曾经致命的缺陷：

1. **point id 必须是 UUID** —— 用原始 ``chunk_id`` 写入会抛
   ``ValueError: Point id ... is not a valid UUID``。
2. **``QdrantClient.search`` 在 qdrant-client 1.19 已被移除** ——
   必须走 ``query_points``，否则检索直接 AttributeError。
"""

from __future__ import annotations

import shutil
import tempfile
import unittest

from src.database.vector_db import VectorDB
from src.ids import chunk_point_id


def vec(*values: float) -> list[float]:
    return list(values)


class TestVectorDB(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="rag_qdrant_test_")
        self.db = VectorDB(
            collection_name="test_collection",
            dimension=4,
            path=self.tmp,
        )

    def tearDown(self) -> None:
        self.db.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------

    def test_upsert_with_uuid_ids(self) -> None:
        ids = [
            chunk_point_id("doc::a::001"),
            chunk_point_id("doc::a::002"),
        ]
        written = self.db.upsert(
            ids,
            [vec(1, 0, 0, 0), vec(0, 1, 0, 0)],
            [{"doc_id": "doc", "chunk_id": "doc::a::001"},
             {"doc_id": "doc", "chunk_id": "doc::a::002"}],
        )

        self.assertEqual(written, 2)
        self.assertEqual(self.db.count(), 2)

    def test_upsert_with_raw_chunk_id_fails(self) -> None:
        """证明为什么必须做 UUID 映射（记录原始缺陷）。"""
        with self.assertRaises(Exception) as ctx:
            self.db.upsert(
                ["Burp Suite sqlmap 速查卡::Burp Suite & sqlmap 速查卡::001"],
                [vec(1, 0, 0, 0)],
                [{"doc_id": "x"}],
            )

        self.assertIn("UUID", str(ctx.exception))

    def test_upsert_is_idempotent(self) -> None:
        point_id = chunk_point_id("doc::a::001")
        payload = {"doc_id": "doc", "chunk_id": "doc::a::001"}

        self.db.upsert([point_id], [vec(1, 0, 0, 0)], [payload])
        self.db.upsert([point_id], [vec(0, 1, 0, 0)], [payload])

        self.assertEqual(self.db.count(), 1, "相同 point id 不应产生重复点")

    def test_upsert_length_mismatch_raises(self) -> None:
        with self.assertRaises(ValueError):
            self.db.upsert(
                [chunk_point_id("a")],
                [vec(1, 0, 0, 0), vec(0, 1, 0, 0)],
                [{"doc_id": "d"}],
            )

    def test_upsert_empty_returns_zero(self) -> None:
        self.assertEqual(self.db.upsert([], [], []), 0)

    # ------------------------------------------------------------------
    # 检索（query_points 回归）
    # ------------------------------------------------------------------

    def test_search_uses_query_points(self) -> None:
        self.db.upsert(
            [
                chunk_point_id("doc::x::001"),
                chunk_point_id("doc::x::002"),
            ],
            [vec(1, 0, 0, 0), vec(0, 1, 0, 0)],
            [
                {"doc_id": "doc", "chunk_id": "doc::x::001", "content": "close"},
                {"doc_id": "doc", "chunk_id": "doc::x::002", "content": "far"},
            ],
        )

        hits = self.db.search(vec(1, 0, 0, 0), top_k=2)

        self.assertEqual(len(hits), 2)
        self.assertEqual(hits[0]["payload"]["content"], "close")
        self.assertGreater(hits[0]["score"], hits[1]["score"])
        self.assertIn("id", hits[0])

    def test_search_on_missing_collection_returns_empty(self) -> None:
        # 注意：QdrantLocal 不允许同一存储目录被两个 client 同时打开，
        # 因此这里复用同一个实例，先 drop 掉 collection 再检索。
        self.db.drop()
        self.assertEqual(self.db.search(vec(1, 0, 0, 0)), [])

    def test_search_respects_score_threshold(self) -> None:
        self.db.upsert(
            [chunk_point_id("doc::y::001")],
            [vec(1, 0, 0, 0)],
            [{"doc_id": "doc", "chunk_id": "doc::y::001"}],
        )

        # 正交向量余弦相似度为 0，阈值 0.5 应过滤掉
        self.assertEqual(
            self.db.search(vec(0, 1, 0, 0), score_threshold=0.5), []
        )

    # ------------------------------------------------------------------
    # 删除 / 清理
    # ------------------------------------------------------------------

    def test_doc_ids(self) -> None:
        self.db.upsert(
            [
                chunk_point_id("a::001"),
                chunk_point_id("a::002"),
                chunk_point_id("b::001"),
            ],
            [vec(1, 0, 0, 0), vec(0, 1, 0, 0), vec(0, 0, 1, 0)],
            [
                {"doc_id": "a", "chunk_id": "a::001"},
                {"doc_id": "a", "chunk_id": "a::002"},
                {"doc_id": "b", "chunk_id": "b::001"},
            ],
        )

        self.assertEqual(self.db.doc_ids(), {"a", "b"})

    def test_delete_by_doc_ids(self) -> None:
        self.db.upsert(
            [
                chunk_point_id("a::001"),
                chunk_point_id("a::002"),
                chunk_point_id("b::001"),
            ],
            [vec(1, 0, 0, 0), vec(0, 1, 0, 0), vec(0, 0, 1, 0)],
            [
                {"doc_id": "a", "chunk_id": "a::001"},
                {"doc_id": "a", "chunk_id": "a::002"},
                {"doc_id": "b", "chunk_id": "b::001"},
            ],
        )

        removed = self.db.delete_by_doc_ids(["a"])

        self.assertEqual(removed, 2)
        self.assertEqual(self.db.count(), 1)
        self.assertEqual(self.db.doc_ids(), {"b"})

    def test_delete_by_doc_ids_empty_is_noop(self) -> None:
        self.assertEqual(self.db.delete_by_doc_ids([]), 0)

    # ------------------------------------------------------------------
    # Collection 生命周期
    # ------------------------------------------------------------------

    def test_recreate_clears_collection(self) -> None:
        """早期缺陷：recreate 只在建单例时生效，重建清不掉旧数据。

        更深一层：QdrantLocal 的 delete_collection + create_collection
        会让旧 shard 复活，所以必须走「空 Filter 删除全部 point」。
        """
        self.db.upsert(
            [chunk_point_id("a::001")],
            [vec(1, 0, 0, 0)],
            [{"doc_id": "a", "chunk_id": "a::001"}],
        )
        self.assertEqual(self.db.count(), 1)

        self.db.ensure_collection(recreate=True)

        self.assertEqual(self.db.count(), 0)

    def test_clear_empties_collection(self) -> None:
        self.db.upsert(
            [
                chunk_point_id("a::001"),
                chunk_point_id("b::001"),
            ],
            [vec(1, 0, 0, 0), vec(0, 1, 0, 0)],
            [
                {"doc_id": "a", "chunk_id": "a::001"},
                {"doc_id": "b", "chunk_id": "b::001"},
            ],
        )

        removed = self.db.clear()

        self.assertEqual(removed, 2)
        self.assertEqual(self.db.count(), 0)
        # collection 本身仍然存在
        self.assertTrue(self.db.exists())

    def test_clear_on_empty_collection_returns_zero(self) -> None:
        self.db.ensure_collection()
        self.assertEqual(self.db.clear(), 0)

    def test_drop_then_recreate_resurrects_data(self) -> None:
        """记录 QdrantLocal 的「数据复活」行为。

        客户端仍打开时磁盘上的 ``storage.sqlite`` 被占用（Windows 下无法删除），
        因此 ``delete_collection`` + ``create_collection`` 会让旧 shard 重新挂载，
        旧数据复活。这正是 ``ensure_collection(recreate=True)`` 必须走
        :meth:`VectorDB.clear` 而不是 drop+create 的原因。
        """
        self.db.upsert(
            [chunk_point_id("a::001")],
            [vec(1, 0, 0, 0)],
            [{"doc_id": "a", "chunk_id": "a::001"}],
        )

        self.db.drop()
        self.db.ensure_collection()

        # 旧数据确实回来了（QdrantLocal 的已知行为）
        self.assertEqual(
            self.db.count(),
            1,
            "QdrantLocal 在客户端未关闭时会复活旧 shard",
        )

        # 而 clear() 才是真正可用的清空手段
        self.assertEqual(self.db.clear(), 1)
        self.assertEqual(self.db.count(), 0)

    def test_existing_dimension(self) -> None:
        self.db.ensure_collection()
        self.assertEqual(self.db.existing_dimension(), 4)

    def test_delete_by_chunk_ids(self) -> None:
        """重建时靠它精确清理旧 chunk（按 payload 的 chunk_id 值）。"""
        ids = [
            chunk_point_id("a::001"),
            chunk_point_id("a::002"),
            chunk_point_id("pic::image::001"),
        ]
        self.db.upsert(
            ids,
            [vec(1, 0, 0, 0), vec(0, 1, 0, 0), vec(0, 0, 1, 0)],
            [
                {"doc_id": "a", "chunk_id": "a::001"},
                {"doc_id": "a", "chunk_id": "a::002"},
                {"doc_id": "image::pic.png", "chunk_id": "pic::image::001"},
            ],
        )

        removed = self.db.delete_by_chunk_ids(["a::002"])

        self.assertEqual(removed, 1)
        self.assertEqual(self.db.count(), 2)
        self.assertEqual(
            self.db.payload_values("chunk_id"),
            {"a::001", "pic::image::001"},
        )

    def test_delete_by_chunk_ids_empty(self) -> None:
        self.assertEqual(self.db.delete_by_chunk_ids([]), 0)

    def test_delete_by_chunk_ids_on_missing_collection(self) -> None:
        self.db.drop()
        self.assertEqual(self.db.delete_by_chunk_ids(["a::001"]), 0)

    def test_payload_values_distinct(self) -> None:
        """分组文档清单靠它判断「哪些文件已索引」。"""
        self.db.upsert(
            [
                chunk_point_id("a::001"),
                chunk_point_id("a::002"),
                chunk_point_id("b::001"),
            ],
            [vec(1, 0, 0, 0), vec(0, 1, 0, 0), vec(0, 0, 1, 0)],
            [
                {"doc_id": "a", "chunk_id": "a::001"},
                {"doc_id": "a", "chunk_id": "a::002"},
                {"doc_id": "b", "chunk_id": "b::001"},
            ],
        )

        self.assertEqual(self.db.payload_values("doc_id"), {"a", "b"})

    def test_payload_values_missing_key(self) -> None:
        self.db.upsert(
            [chunk_point_id("a::001")],
            [vec(1, 0, 0, 0)],
            [{"doc_id": "a", "chunk_id": "a::001"}],
        )
        self.assertEqual(self.db.payload_values("no_such_key"), set())

    def test_payload_values_empty_input_collection(self) -> None:
        self.db.ensure_collection()
        self.assertEqual(self.db.payload_values("doc_id"), set())

    def test_payload_values_on_missing_collection(self) -> None:
        self.db.drop()
        self.assertEqual(self.db.payload_values("doc_id"), set())

    def test_get_vectors_roundtrip(self) -> None:
        """按 point id 取回已存向量（rerank 复用依赖此接口）。"""
        ids = [
            chunk_point_id("doc::a::001"),
            chunk_point_id("doc::a::002"),
        ]
        self.db.upsert(
            ids,
            [vec(1, 0, 0, 0), vec(0, 1, 0, 0)],
            [
                {"doc_id": "doc", "chunk_id": "doc::a::001"},
                {"doc_id": "doc", "chunk_id": "doc::a::002"},
            ],
        )

        found = self.db.get_vectors(ids)

        self.assertEqual(set(found), set(ids))
        self.assertEqual(found[ids[0]], [1.0, 0.0, 0.0, 0.0])
        self.assertEqual(found[ids[1]], [0.0, 1.0, 0.0, 0.0])

    def test_get_vectors_missing_ids_are_skipped(self) -> None:
        present = chunk_point_id("doc::a::001")
        self.db.upsert(
            [present],
            [vec(1, 0, 0, 0)],
            [{"doc_id": "doc", "chunk_id": "doc::a::001"}],
        )

        found = self.db.get_vectors(
            [present, chunk_point_id("doc::nope::999")]
        )

        self.assertEqual(set(found), {present})

    def test_get_vectors_empty_input(self) -> None:
        self.assertEqual(self.db.get_vectors([]), {})

    def test_get_vectors_on_missing_collection(self) -> None:
        self.db.drop()
        self.assertEqual(self.db.get_vectors([chunk_point_id("a")]), {})

    def test_ensure_collection_is_idempotent(self) -> None:
        self.db.ensure_collection()
        self.db.ensure_collection()
        self.assertEqual(self.db.count(), 0)

    def test_drop(self) -> None:
        self.db.upsert(
            [chunk_point_id("a::001")],
            [vec(1, 0, 0, 0)],
            [{"doc_id": "a", "chunk_id": "a::001"}],
        )
        self.db.drop()
        self.assertEqual(self.db.count(), 0)
        self.assertFalse(self.db.exists())

    def test_close_is_idempotent(self) -> None:
        self.db.close()
        self.db.close()
        self.assertEqual(self.db.count(), 0)


if __name__ == "__main__":
    unittest.main()
