"""配置与模型自动发现测试。"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import config as cfg

from tests.gguf_builder import chat_metadata, write_gguf


class TestConfigInvariants(unittest.TestCase):
    def test_validate_config_passes(self) -> None:
        cfg.validate_config()

    def test_probe_root_is_project_root(self) -> None:
        self.assertEqual(cfg.PROJECT_ROOT.name, "RAG")
        self.assertTrue((cfg.PROJECT_ROOT / "src").is_dir())

    def test_directories_created(self) -> None:
        for directory in (
            cfg.DATA_DIR,
            cfg.CHUNKS_DIR,
            cfg.INDEX_DIR,
            cfg.METADATA_DIR,
            cfg.QDRANT_DIR,
        ):
            self.assertTrue(directory.is_dir(), f"目录未创建: {directory}")

    def test_chunk_config_consistent(self) -> None:
        self.assertLess(cfg.CHUNK_CONFIG.chunk_overlap, cfg.CHUNK_CONFIG.chunk_size)
        self.assertLess(cfg.CHUNK_CONFIG.min_chunk_size, cfg.CHUNK_CONFIG.max_chunk_size)

    def test_retrieval_topk_ordering(self) -> None:
        self.assertLessEqual(
            cfg.RETRIEVAL_CONFIG.context_top_k,
            cfg.RETRIEVAL_CONFIG.rerank_top_k,
        )

    def test_active_embedding_known(self) -> None:
        self.assertIn(cfg.ACTIVE_EMBEDDING, cfg.EMBEDDING_MODELS)

    def test_qwen_dimension_matches_model(self) -> None:
        self.assertEqual(cfg.QWEN3_EMBEDDING.dimension, 2560)
        self.assertFalse(cfg.QWEN3_EMBEDDING.multimodal)

    def test_wemm_is_multimodal_with_mmproj(self) -> None:
        self.assertTrue(cfg.WEMM_EMBEDDING.multimodal)
        self.assertIsNotNone(cfg.WEMM_EMBEDDING.mmproj_path)

    def test_llm_port_does_not_clash(self) -> None:
        """LLM 端口不能和 embedding / WeMM 的端口撞车。"""
        self.assertNotIn(cfg.LLM_CONFIG.port, {8080, 8081})


class TestDiscoverLlmModel(unittest.TestCase):
    """自动挑选模型。

    注意：这里必须写**结构合法**的 GGUF 文件。旧版本用 ``b"x" * n`` 造假，
    在「读取真实元数据」的实现下会被正确跳过，因此那套断言已不再成立。
    """

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_llm_discover_"))
        # 隔离：避免受 data/llm_selection.json 里的真实选择影响
        self._selection = mock.patch(
            "src.llm.catalog.load_selection", return_value=None
        )
        self._selection.start()

    def tearDown(self) -> None:
        self._selection.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _touch(
        self,
        name: str,
        *,
        size_label: str = "4B",
        padding: int = 0,
        **kwargs,
    ) -> Path:
        """写一个合法 GGUF；padding 用于撑大文件体积。"""
        path = write_gguf(
            self.tmp / name,
            chat_metadata(name=name, size_label=size_label, **kwargs),
        )
        if padding:
            with path.open("ab") as handle:
                handle.write(b"\x00" * padding)
        return path

    def _config(self, **overrides) -> cfg.LlmConfig:
        base = {
            "model_path": None,
            "model_dirs": (self.tmp,),
            "preferred_models": (),
            "excluded_models": (),
            "context_size": 8192,
            "vram_budget_gb": 8.0,
            "vram_reserve_gb": 3.0,
        }
        base.update(overrides)
        return cfg.LlmConfig(**base)

    def test_returns_none_when_directory_empty(self) -> None:
        self.assertIsNone(cfg.discover_llm_model(self._config()))

    def test_returns_none_for_non_gguf_files(self) -> None:
        (self.tmp / "readme.txt").write_text("x", encoding="utf-8")
        self.assertIsNone(cfg.discover_llm_model(self._config()))

    def test_prefers_keyword_match(self) -> None:
        self._touch("big-model-Q4.gguf", padding=4096)
        wanted = self._touch("wanted-instruct-Q4.gguf")

        found = cfg.discover_llm_model(
            self._config(preferred_models=("wanted",))
        )

        self.assertEqual(found, wanted)

    def test_prefers_model_that_fits_vram(self) -> None:
        """回归：旧实现会「取体积最大的」，从而选中显存装不下的大模型。"""
        small = self._touch("small-Q4.gguf")
        self._touch("huge-Q4.gguf", padding=9 * 1024**3)

        found = cfg.discover_llm_model(self._config())

        self.assertEqual(found, small)

    def test_ignores_auxiliary_gguf(self) -> None:
        self._touch("mmproj-vision-BF16.gguf", arch="clip", chat_template=None)
        self._touch("mtp-head.gguf", arch="clip", chat_template=None)
        main = self._touch("main-model.gguf")

        self.assertEqual(cfg.discover_llm_model(self._config()), main)

    def test_ignores_base_model_without_chat_template(self) -> None:
        self._touch("base-model.gguf", chat_template=None, size_label="70B")
        chat = self._touch("chat-model.gguf")

        self.assertEqual(cfg.discover_llm_model(self._config()), chat)

    def test_excluded_model_is_never_selected(self) -> None:
        """用户明确要求不使用的模型，即使它是唯一候选也不能选中。"""
        self._touch("gemma-4-E4B-it-UD-Q4_K_XL.gguf")

        found = cfg.discover_llm_model(
            self._config(excluded_models=("gemma-4-E4B",))
        )

        self.assertIsNone(found)

    def test_excluded_is_skipped_in_favour_of_others(self) -> None:
        self._touch("gemma-4-E4B-it.gguf")
        good = self._touch("Qwen3.8-4B-Q4_K_M.gguf")

        found = cfg.discover_llm_model(
            self._config(
                preferred_models=("gemma-4-E4B",),   # 即便它更“受偏好”
                excluded_models=("gemma-4-E4B",),
            )
        )

        self.assertEqual(found, good)

    def test_explicit_path_wins(self) -> None:
        explicit = self._touch("explicit.gguf")
        self._touch("other.gguf", size_label="30B")

        found = cfg.discover_llm_model(
            self._config(model_path=explicit, preferred_models=("other",))
        )

        self.assertEqual(found, explicit)

    def test_missing_explicit_path_returns_none(self) -> None:
        found = cfg.discover_llm_model(
            self._config(model_path=self.tmp / "nope.gguf")
        )
        self.assertIsNone(found)

    def test_missing_directory_is_tolerated(self) -> None:
        found = cfg.discover_llm_model(
            self._config(model_dirs=(self.tmp / "not-there",))
        )
        self.assertIsNone(found)

    def test_persisted_selection_is_honoured(self) -> None:
        self._touch("first.gguf")
        second = self._touch("second.gguf")

        with mock.patch(
            "src.llm.catalog.load_selection",
            return_value="second.gguf",
        ):
            found = cfg.discover_llm_model(self._config())

        self.assertEqual(found, second)

    def test_stale_persisted_selection_falls_back(self) -> None:
        present = self._touch("present.gguf")

        with mock.patch(
            "src.llm.catalog.load_selection",
            return_value="deleted-model.gguf",
        ):
            found = cfg.discover_llm_model(self._config())

        self.assertEqual(found, present)


class TestEnvironmentOverrides(unittest.TestCase):
    def test_env_helpers_fall_back(self) -> None:
        self.assertEqual(cfg._env_str("RAG_TEST_UNSET_VAR", "d"), "d")
        self.assertEqual(cfg._env_int("RAG_TEST_UNSET_VAR", 7), 7)
        self.assertEqual(cfg._env_float("RAG_TEST_UNSET_VAR", 1.5), 1.5)
        self.assertTrue(cfg._env_bool("RAG_TEST_UNSET_VAR", True))

    def test_env_int_invalid_falls_back(self) -> None:
        self.assertEqual(cfg._env_int("PATH", 42), 42)


if __name__ == "__main__":
    unittest.main()
