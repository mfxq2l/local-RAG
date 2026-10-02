"""chunk_id → Qdrant point id 的稳定性测试。

这是本项目最关键的回归点：Qdrant 本地模式要求 string id 必须是 UUID，
早期实现直接使用 ``chunk_id`` 导致 1707 个 chunk 全部写入失败。
"""

from __future__ import annotations

import unittest
import uuid

from src.ids import RAG_NAMESPACE, chunk_point_id, is_uuid


class TestChunkPointId(unittest.TestCase):
    def test_returns_valid_uuid(self) -> None:
        point_id = chunk_point_id("doc::section::001")
        self.assertTrue(is_uuid(point_id))
        self.assertEqual(len(point_id), 36)

    def test_parses_as_uuid_object(self) -> None:
        uuid.UUID(chunk_point_id("任意中文::章节::001"))

    def test_deterministic(self) -> None:
        raw = "Burp Suite sqlmap 速查卡::Burp Suite & sqlmap 速查卡::001"
        self.assertEqual(chunk_point_id(raw), chunk_point_id(raw))

    def test_distinct_ids_produce_distinct_uuids(self) -> None:
        a = chunk_point_id("doc::a::001")
        b = chunk_point_id("doc::a::002")
        self.assertNotEqual(a, b)

    def test_matches_uuid5_spec(self) -> None:
        raw = "doc::a::001"
        self.assertEqual(
            chunk_point_id(raw),
            str(uuid.uuid5(RAG_NAMESPACE, raw)),
        )

    def test_survives_non_ascii_and_symbols(self) -> None:
        for raw in [
            "nmap知识点::端口扫描::-sS",
            "C速查卡::指针与数组::001",
            "a" * 500,
            "包含 emoji 🚀 的标题::001",
        ]:
            self.assertTrue(is_uuid(chunk_point_id(raw)))

    def test_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            chunk_point_id("")
        with self.assertRaises(ValueError):
            chunk_point_id("   ")

    def test_is_uuid_rejects_bad_values(self) -> None:
        self.assertFalse(is_uuid("not-a-uuid"))
        self.assertFalse(is_uuid(None))
        self.assertFalse(is_uuid(123))
        self.assertFalse(is_uuid("doc::section::001"))


if __name__ == "__main__":
    unittest.main()
