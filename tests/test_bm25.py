"""BM25 索引测试（jieba 分词 + rank_bm25）。"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from src.retrieval.bm25 import BM25Index, tokenize


CORPUS = [
    {
        "chunk_id": "nmap::001",
        "content": "nmap 的 -sS 参数执行 TCP SYN 扫描，速度快且隐蔽。",
        "doc_id": "nmap",
    },
    {
        "chunk_id": "burp::001",
        "content": "Burp Suite 是 Web 应用安全测试工具，可用于拦截 HTTP 请求。",
        "doc_id": "burp",
    },
    {
        "chunk_id": "python::001",
        "content": "Python 的 os 模块提供操作系统接口，os.path 处理路径。",
        "doc_id": "python",
    },
]


class TestTokenize(unittest.TestCase):
    def test_chinese_tokens(self) -> None:
        tokens = tokenize("端口扫描")
        self.assertTrue(tokens)
        self.assertTrue(all(isinstance(t, str) for t in tokens))

    def test_ascii_lowercased_and_kept_whole(self) -> None:
        tokens = tokenize("NMAP -sS")
        self.assertIn("nmap", tokens)

    def test_numbers_preserved(self) -> None:
        tokens = tokenize("HTTP/2 8080")
        self.assertIn("8080", tokens)

    def test_mixed_text(self) -> None:
        tokens = tokenize("用 nmap 做端口扫描")
        self.assertIn("nmap", tokens)
        self.assertTrue(any("端口" in t for t in tokens))

    def test_empty_string(self) -> None:
        self.assertEqual(tokenize(""), [])


class TestBM25Index(unittest.TestCase):
    def test_build_and_len(self) -> None:
        index = BM25Index(name="test")
        index.build(CORPUS)
        self.assertEqual(len(index), 3)

    def test_search_ranks_relevant_first(self) -> None:
        index = BM25Index(name="test")
        index.build(CORPUS)

        results = index.search("nmap SYN 扫描", top_k=3)

        self.assertTrue(results)
        self.assertEqual(results[0]["id"], "nmap::001")
        self.assertEqual(results[0]["source"], "bm25")

    def test_search_chinese_query(self) -> None:
        index = BM25Index(name="test")
        index.build(CORPUS)

        results = index.search("Web 安全测试", top_k=3)

        self.assertTrue(results)
        self.assertEqual(results[0]["id"], "burp::001")

    def test_search_empty_index(self) -> None:
        index = BM25Index(name="test")
        index.build([])
        self.assertEqual(index.search("任意查询"), [])

    def test_search_no_token_match(self) -> None:
        index = BM25Index(name="test")
        index.build(CORPUS)
        self.assertEqual(index.search("zzzzqqqq"), [])

    def test_scores_are_positive(self) -> None:
        index = BM25Index(name="test")
        index.build(CORPUS)

        for item in index.search("Python os 模块", top_k=3):
            self.assertGreater(item["score"], 0.0)

    def test_save_load_roundtrip(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="rag_bm25_test_"))
        try:
            path = tmp / "bm25.pkl"

            original = BM25Index(name="test")
            original.build(CORPUS)
            original.save(path)

            self.assertTrue(path.exists())
            self.assertGreater(path.stat().st_size, 0)

            restored = BM25Index(name="restored")
            restored.load(path)

            self.assertEqual(len(restored), 3)
            self.assertEqual(
                [r["id"] for r in restored.search("nmap SYN", top_k=1)],
                ["nmap::001"],
            )
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_load_or_build_appends_new_chunks(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="rag_bm25_test_"))
        try:
            path = tmp / "bm25.pkl"

            first = BM25Index(name="test")
            first.build(CORPUS[:1])
            first.save(path)

            extra = CORPUS[1:]
            merged = BM25Index(name="test")
            merged.load_or_build(path, extra)

            self.assertEqual(len(merged), 3)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_load_or_build_falls_back_when_missing(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="rag_bm25_test_"))
        try:
            path = tmp / "missing.pkl"
            index = BM25Index(name="test")
            index.load_or_build(path, CORPUS)
            self.assertEqual(len(index), 3)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
