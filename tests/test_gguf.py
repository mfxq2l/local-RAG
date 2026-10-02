"""GGUF 元数据解析测试。

重点回归：架构相关的键带前缀（``gemma4.context_length`` / ``qwen35.block_count``），
解析器必须用**后缀匹配**而不是精确匹配，否则读出来全是 0 —— 这个 bug 曾真实
导致了「上下文长度、层数、KV 头数全为 0」。
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from src.llm.gguf import GgufMeta, read_gguf, scan_directory

from tests.gguf_builder import CHAT_TEMPLATE, chat_metadata, write_gguf


class TestReadGguf(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_gguf_test_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, name: str, metadata: dict) -> Path:
        return write_gguf(self.tmp / name, metadata)

    # ------------------------------------------------------------------
    # 基本解析
    # ------------------------------------------------------------------

    def test_reads_general_fields(self) -> None:
        path = self._write(
            "m.gguf",
            chat_metadata(name="My Model", size_label="8B"),
        )

        meta = read_gguf(path)

        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertEqual(meta.architecture, "llama")
        self.assertEqual(meta.name, "My Model")
        self.assertEqual(meta.size_label, "8B")

    def test_reads_architecture_prefixed_keys(self) -> None:
        """核心回归：带架构前缀的参数键必须被识别。"""
        path = self._write(
            "gemma.gguf",
            chat_metadata(
                arch="gemma4",
                context_length=131072,
                block_count=42,
                embedding_length=2560,
                head_count=8,
                head_count_kv=2,
            ),
        )

        meta = read_gguf(path)

        assert meta is not None
        self.assertEqual(meta.context_length, 131072)
        self.assertEqual(meta.block_count, 42)
        self.assertEqual(meta.embedding_length, 2560)
        self.assertEqual(meta.head_count, 8)
        self.assertEqual(meta.head_count_kv, 2)

    def test_detects_chat_template(self) -> None:
        with_template = self._write("chat.gguf", chat_metadata())
        without = self._write(
            "base.gguf", chat_metadata(chat_template=None)
        )

        self.assertTrue(read_gguf(with_template).has_chat_template)  # type: ignore[union-attr]
        self.assertFalse(read_gguf(without).has_chat_template)  # type: ignore[union-attr]

    def test_reads_string_array_tags(self) -> None:
        path = self._write(
            "tagged.gguf",
            chat_metadata(tags=["translation", "unsloth"]),
        )

        meta = read_gguf(path)

        assert meta is not None
        self.assertEqual(meta.tags, ["translation", "unsloth"])

    def test_large_string_array_is_skipped(self) -> None:
        """大数组（如 20 万条词表）必须能安全跳过。"""
        big_vocab = [f"tok{i}" for i in range(20000)]
        metadata = chat_metadata()
        metadata["tokenizer.ggml.tokens"] = big_vocab
        metadata["general.name"] = "After-Vocab"

        path = self._write("vocab.gguf", metadata)

        meta = read_gguf(path)

        assert meta is not None
        # 词表之后的键仍要能读到
        self.assertEqual(meta.name, "After-Vocab")
        self.assertEqual(meta.context_length, 8192)

    # ------------------------------------------------------------------
    # 异常与边界
    # ------------------------------------------------------------------

    def test_bad_magic_returns_none(self) -> None:
        path = self._write("bad.gguf", chat_metadata())
        data = bytearray(path.read_bytes())
        data[0:4] = b"XXXX"
        path.write_bytes(bytes(data))

        self.assertIsNone(read_gguf(path))

    def test_garbage_file_returns_none(self) -> None:
        path = self.tmp / "garbage.gguf"
        path.write_bytes(b"x" * 1024)
        self.assertIsNone(read_gguf(path))

    def test_missing_file_returns_none(self) -> None:
        self.assertIsNone(read_gguf(self.tmp / "nope.gguf"))

    def test_old_version_rejected(self) -> None:
        path = write_gguf(
            self.tmp / "v1.gguf", chat_metadata(), version=1
        )
        self.assertIsNone(read_gguf(path))

    def test_empty_metadata_file_is_invalid(self) -> None:
        """没有 general.architecture 的文件无法估算任何东西，视为无效。"""
        path = write_gguf(self.tmp / "empty.gguf", {})
        self.assertIsNone(read_gguf(path))

    def test_architecture_only(self) -> None:
        """只要有 architecture 就算有效，其余字段可以为空。"""
        path = write_gguf(
            self.tmp / "bare.gguf", {"general.architecture": "llama"}
        )
        meta = read_gguf(path)
        self.assertIsNotNone(meta)
        assert meta is not None
        self.assertEqual(meta.architecture, "llama")
        self.assertEqual(meta.context_length, 0)
        self.assertFalse(meta.has_chat_template)

    # ------------------------------------------------------------------
    # 派生属性
    # ------------------------------------------------------------------

    def test_quantization_from_file_name(self) -> None:
        cases = {
            "Qwen3.8-4B-Q4_K_M.gguf": "Q4_K_M",
            "gemma-4-E2B-it-UD-Q4_K_XL.gguf": "UD-Q4_K_XL",
            "mmproj-x-BF16.gguf": "BF16",
            "model-F16.gguf": "F16",
            "unknown.gguf": "?",
        }
        for file_name, expected in cases.items():
            meta = GgufMeta(path=str(self.tmp / file_name), size_bytes=1)
            self.assertEqual(
                meta.quantization, expected, f"{file_name} 量化识别错误"
            )

    def test_parameter_count_parsed(self) -> None:
        meta = GgufMeta(path="x", size_bytes=1, size_label="80B-A3B")
        self.assertEqual(meta.parameter_count_b, 80.0)

    def test_parameter_count_missing(self) -> None:
        meta = GgufMeta(path="x", size_bytes=1, size_label="Mini")
        self.assertIsNone(meta.parameter_count_b)

    def test_roundtrip_dict(self) -> None:
        path = self._write("rt.gguf", chat_metadata(name="RT"))
        meta = read_gguf(path)
        assert meta is not None

        restored = GgufMeta.from_dict(meta.to_dict())

        self.assertEqual(restored.architecture, meta.architecture)
        self.assertEqual(restored.context_length, meta.context_length)
        self.assertEqual(restored.path, meta.path)


class TestScanDirectory(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_scan_test_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_finds_gguf_recursively(self) -> None:
        write_gguf(self.tmp / "a.gguf", chat_metadata(name="A"))
        write_gguf(self.tmp / "sub" / "b.gguf", chat_metadata(name="B"))
        (self.tmp / "note.txt").write_text("x", encoding="utf-8")

        metas = scan_directory(self.tmp, use_cache=False)

        self.assertEqual({m.name for m in metas}, {"A", "B"})

    def test_missing_directory_returns_empty(self) -> None:
        self.assertEqual(
            scan_directory(self.tmp / "nope", use_cache=False), []
        )

    def test_sorted_by_size_desc(self) -> None:
        write_gguf(self.tmp / "small.gguf", chat_metadata(name="S"))
        big = write_gguf(self.tmp / "big.gguf", chat_metadata(name="B"))
        big.write_bytes(big.read_bytes() + b"\x00" * 4096)

        metas = scan_directory(self.tmp, use_cache=False)

        self.assertEqual(metas[0].name, "B")


if __name__ == "__main__":
    unittest.main()
