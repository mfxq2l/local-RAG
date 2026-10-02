"""模型清单（catalog）测试：分类、显存估算、排除、排序与查找。"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from src.config import LlmConfig
from src.llm.catalog import (
    KIND_BASE,
    KIND_CHAT,
    KIND_EMBEDDING,
    KIND_TRANSLATION,
    KIND_VISION,
    build_catalog,
    build_entry,
    chat_models,
    classify,
    estimate_kv_cache_gb,
    find_model,
    is_excluded,
)
from src.llm.gguf import GgufMeta

from tests.gguf_builder import chat_metadata, write_gguf


def meta(**overrides) -> GgufMeta:
    base = {
        "path": "C:/models/x.gguf",
        "size_bytes": int(2.5 * 1024**3),
        "architecture": "llama",
        "name": "Test",
        "size_label": "4B",
        "context_length": 8192,
        "block_count": 32,
        "embedding_length": 2048,
        "head_count": 16,
        "head_count_kv": 4,
        "has_chat_template": True,
    }
    base.update(overrides)
    return GgufMeta(**base)


class TestClassify(unittest.TestCase):
    def test_plain_chat_model(self) -> None:
        self.assertEqual(classify(meta()), KIND_CHAT)

    def test_vision_projector_by_file_name(self) -> None:
        self.assertEqual(
            classify(meta(has_chat_template=False, path="x/mmproj-a-BF16.gguf")),
            KIND_VISION,
        )

    def test_vision_projector_by_architecture(self) -> None:
        self.assertEqual(
            classify(meta(architecture="clip", has_chat_template=False)),
            KIND_VISION,
        )

    def test_mtp_is_vision_kind(self) -> None:
        self.assertEqual(
            classify(meta(path="x/mtp-model.gguf")), KIND_VISION
        )

    def test_translation_by_tag(self) -> None:
        self.assertEqual(
            classify(meta(tags=["translation"])), KIND_TRANSLATION
        )

    def test_embedding_by_architecture(self) -> None:
        self.assertEqual(
            classify(meta(architecture="bert", has_chat_template=False)),
            KIND_EMBEDDING,
        )

    def test_base_model_without_template(self) -> None:
        self.assertEqual(
            classify(meta(has_chat_template=False)), KIND_BASE
        )

    def test_multimodal_chat_model_is_chat(self) -> None:
        """回归：Qwen2.5-Omni 这类多模态**对话**模型不能被当成投影器。"""
        for arch in ("qwen2vl", "llava", "qwen2.5-omni"):
            self.assertEqual(
                classify(meta(architecture=arch, has_chat_template=True)),
                KIND_CHAT,
                f"{arch} 应判为对话模型",
            )

    def test_embedding_tag_wins(self) -> None:
        self.assertEqual(
            classify(meta(tags=["embedding"])), KIND_EMBEDDING
        )


class TestKvCacheEstimate(unittest.TestCase):
    def test_formula(self) -> None:
        """KV = 2 × 层 × kv头 × 头维 × ctx × 2字节。"""
        m = meta(
            block_count=32, head_count=16, head_count_kv=4,
            embedding_length=2048, context_length=8192,
        )
        # head_dim = 2048 / 16 = 128
        expected = 2 * 32 * 4 * 128 * 8192 * 2 / 1024**3
        self.assertAlmostEqual(
            estimate_kv_cache_gb(m, 8192), expected, places=6
        )

    def test_scales_with_context(self) -> None:
        m = meta()
        small = estimate_kv_cache_gb(m, 8192)
        large = estimate_kv_cache_gb(m, 32768)
        self.assertAlmostEqual(large / small, 4.0, places=6)

    def test_zero_when_metadata_missing(self) -> None:
        self.assertEqual(
            estimate_kv_cache_gb(meta(block_count=0), 8192), 0.0
        )
        self.assertEqual(
            estimate_kv_cache_gb(meta(head_count_kv=0), 8192), 0.0
        )

    def test_zero_context(self) -> None:
        self.assertEqual(estimate_kv_cache_gb(meta(), 0), 0.0)

    def test_uses_key_length_when_present(self) -> None:
        with_key = estimate_kv_cache_gb(meta(key_length=256), 8192)
        without = estimate_kv_cache_gb(meta(), 8192)
        self.assertGreater(with_key, without)


class TestBuildEntry(unittest.TestCase):
    def test_carries_capability_and_effective_context(self) -> None:
        entry = build_entry(
            meta(context_length=262144),
            context_length=8192,
            reserve_gb=3.0,
            vram_budget_gb=8.0,
        )
        self.assertEqual(entry.context_length, 262144)   # 模型上限
        self.assertEqual(entry.effective_context, 8192)  # 实际使用

    def test_fits_vram_within_budget(self) -> None:
        entry = build_entry(
            meta(), context_length=8192,
            reserve_gb=3.0, vram_budget_gb=8.0,
        )
        # 2.5GB 权重 + KV + 3GB 预留
        self.assertTrue(entry.fits_vram)

    def test_does_not_fit_when_too_big(self) -> None:
        entry = build_entry(
            meta(size_bytes=int(7 * 1024**3)),
            context_length=8192,
            reserve_gb=3.0,
            vram_budget_gb=8.0,
        )
        self.assertFalse(entry.fits_vram)

    def test_exclusion_flag(self) -> None:
        entry = build_entry(
            meta(path="C:/m/gemma-4-E4B-it.gguf", name="Gemma-4-E4B-It"),
            exclude_patterns=("gemma-4-E4B",),
        )
        self.assertTrue(entry.excluded)
        self.assertFalse(entry.is_chat_capable)
        self.assertIn("RAG_LLM_EXCLUDE", entry.excluded_reason)

    def test_hash_name_falls_back_to_file_stem(self) -> None:
        entry = build_entry(
            meta(
                path="C:/m/Qwen3.5-9B-DeepSeek-V4-Flash-Q4_K_M.gguf",
                name="719b5158bed2e3f88829e1d1509a036fe7edac7d",
            )
        )
        self.assertEqual(
            entry.display_name, "Qwen3.5-9B-DeepSeek-V4-Flash-Q4_K_M"
        )


class TestIsExcluded(unittest.TestCase):
    def test_matches_file_name(self) -> None:
        self.assertEqual(
            is_excluded(meta(path="x/gemma-4-E4B-it.gguf"), ("gemma-4-E4B",)),
            "gemma-4-E4B",
        )

    def test_case_insensitive(self) -> None:
        self.assertTrue(
            is_excluded(meta(path="x/GEMMA-4-e4b.gguf"), ("gemma-4-E4B",))
        )

    def test_no_match(self) -> None:
        self.assertEqual(
            is_excluded(meta(path="x/Qwen3.8-4B.gguf"), ("gemma-4-E4B",)),
            "",
        )

    def test_empty_patterns(self) -> None:
        self.assertEqual(is_excluded(meta(), ()), "")


class TestBuildCatalog(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_catalog_test_"))
        self.project = self.tmp / "project"
        self.external = self.tmp / "external"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, directory: Path, file_name: str, **kwargs) -> Path:
        return write_gguf(directory / file_name, chat_metadata(**kwargs))

    def _config(self, **overrides) -> LlmConfig:
        base = {
            "model_path": None,
            "model_dirs": (self.project, self.external),
            "preferred_models": (),
            "excluded_models": (),
            "context_size": 8192,
            "vram_budget_gb": 8.0,
            "vram_reserve_gb": 3.0,
        }
        base.update(overrides)
        return LlmConfig(**base)

    def test_project_directory_wins(self) -> None:
        """项目自带目录里的模型要排在外部目录之前。"""
        self._write(self.external, "ext.gguf", name="External")
        self._write(self.project, "proj.gguf", name="Project")

        entries = build_catalog(self._config(), force=True)

        self.assertEqual(entries[0].name, "Project")
        self.assertEqual(entries[0].directory_priority, 0)

    def test_dedupe_same_name_and_size(self) -> None:
        """同名同大小的副本只保留优先级最高的那份。"""
        self._write(self.project, "same.gguf", name="Same")
        self._write(self.external, "same.gguf", name="Same")

        entries = build_catalog(self._config(), force=True)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].directory_priority, 0)

    def test_excluded_models_are_flagged_and_skipped(self) -> None:
        self._write(self.project, "good.gguf", name="Good")
        self._write(self.project, "gemma-4-E4B-it-UD-Q4_K_XL.gguf", name="Bad")

        cfg = self._config(excluded_models=("gemma-4-E4B",))
        entries = build_catalog(cfg, force=True)

        bad = [e for e in entries if "E4B" in e.file_name]
        self.assertTrue(bad and bad[0].excluded)
        self.assertNotIn(
            "Bad", [e.name for e in chat_models(entries)]
        )

    def test_preferred_keyword_ranks_first(self) -> None:
        self._write(self.project, "aaa.gguf", name="AAA")
        self._write(self.project, "bbb.gguf", name="BBB")

        cfg = self._config(preferred_models=("bbb",), excluded_models=())
        entries = build_catalog(cfg, force=True)

        usable = chat_models(entries)
        self.assertEqual(usable[0].name, "BBB")

    def test_auxiliary_files_not_chat_capable(self) -> None:
        self._write(self.project, "main.gguf", name="Main")
        self._write(
            self.project, "mmproj-main-BF16.gguf",
            name="Proj", arch="clip", chat_template=None,
        )

        entries = build_catalog(self._config(), force=True)
        chat_names = [e.name for e in chat_models(entries)]

        self.assertIn("Main", chat_names)
        self.assertNotIn("Proj", chat_names)

    def test_empty_directories(self) -> None:
        self.assertEqual(build_catalog(self._config(), force=True), [])


class TestFindModel(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_find_test_"))
        write_gguf(
            self.tmp / "Qwen3.8-4B-Q4_K_M.gguf",
            chat_metadata(name="Qwen3.8 4B", size_label="4B"),
        )
        write_gguf(
            self.tmp / "gemma-4-E4B-it.gguf",
            chat_metadata(name="Gemma-4-E4B", size_label="7.5B"),
        )
        write_gguf(
            self.tmp / "mmproj-x.gguf",
            chat_metadata(name="Proj", arch="clip", chat_template=None),
        )
        self.cfg = LlmConfig(
            model_path=None,
            model_dirs=(self.tmp,),
            preferred_models=(),
            excluded_models=("gemma-4-E4B",),
            context_size=8192,
        )
        self.entries = build_catalog(self.cfg, force=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_find_by_name_fragment(self) -> None:
        entry = find_model("Qwen3.8", self.entries)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.file_name, "Qwen3.8-4B-Q4_K_M.gguf")  # type: ignore[union-attr]

    def test_find_by_exact_file_name(self) -> None:
        entry = find_model("Qwen3.8-4B-Q4_K_M.gguf", self.entries)
        self.assertIsNotNone(entry)

    def test_find_by_index(self) -> None:
        entry = find_model("1", self.entries)
        self.assertIsNotNone(entry)
        self.assertTrue(entry.is_chat_capable)  # type: ignore[union-attr]

    def test_index_out_of_range(self) -> None:
        self.assertIsNone(find_model("99", self.entries))

    def test_excluded_model_cannot_be_found(self) -> None:
        """核心：被排除的模型即使写名字也选不到。"""
        self.assertIsNone(find_model("gemma-4-E4B", self.entries))

    def test_auxiliary_not_preferred(self) -> None:
        entry = find_model("mmproj", self.entries)
        # 能匹配到，但不应被当成可对话模型
        if entry is not None:
            self.assertFalse(entry.is_chat_capable)

    def test_unknown_query(self) -> None:
        self.assertIsNone(find_model("nothing-like-this", self.entries))

    def test_empty_query(self) -> None:
        self.assertIsNone(find_model("", self.entries))
        self.assertIsNone(find_model("   ", self.entries))


if __name__ == "__main__":
    unittest.main()
