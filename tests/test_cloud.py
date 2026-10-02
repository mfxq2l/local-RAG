"""云端 LLM 配置与状态持久化测试。

重点：**明文 API Key 绝不能出现在任何对外结构中**。
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.llm import cloud, state


class CloudTestBase(unittest.TestCase):
    """把落盘路径重定向到临时目录，避免污染真实配置。"""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_cloud_test_"))
        self.cloud_path = self.tmp / "llm_cloud.json"
        self.state_path = self.tmp / "llm_selection.json"

        self._p1 = mock.patch.object(cloud, "CLOUD_PATH", self.cloud_path)
        self._p2 = mock.patch.object(state, "STATE_PATH", self.state_path)
        self._p1.start()
        self._p2.start()

        cloud.clear_cloud()
        state.clear_state()

    def tearDown(self) -> None:
        self._p1.stop()
        self._p2.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestMaskKey(unittest.TestCase):
    def test_masks_middle(self) -> None:
        masked = cloud.mask_key("sk-abcdefghijklmnop")
        self.assertTrue(masked.startswith("sk-"))
        self.assertTrue(masked.endswith("mnop"))
        self.assertNotIn("abcdefghijkl", masked)

    def test_empty(self) -> None:
        self.assertEqual(cloud.mask_key(""), "")

    def test_short_key_fully_hidden(self) -> None:
        self.assertNotIn("abc", cloud.mask_key("abcxyz"))


class TestCloudSettings(CloudTestBase):
    def test_not_configured_by_default(self) -> None:
        self.assertFalse(cloud.load_cloud().configured)

    def test_configured_requires_all_three(self) -> None:
        settings = cloud.CloudSettings(base_url="https://x/v1", model="m")
        self.assertFalse(settings.configured, "缺 API Key 不应算已配置")

        settings.api_key = "sk-1"
        self.assertTrue(settings.configured)

    def test_public_dict_never_leaks_key(self) -> None:
        """核心安全断言。"""
        secret = "sk-super-secret-value-1234"
        settings = cloud.CloudSettings(
            base_url="https://api.example.com/v1",
            model="gpt-x",
            api_key=secret,
        )

        public = settings.to_public_dict()
        dumped = json.dumps(public, ensure_ascii=False)

        self.assertNotIn(secret, dumped)
        self.assertTrue(public["has_api_key"])
        self.assertNotEqual(public["api_key_masked"], secret)

    def test_save_and_load_roundtrip(self) -> None:
        cloud.update_cloud(
            base_url="https://api.example.com/v1",
            model="m1",
            api_key="sk-abc",
        )

        loaded = cloud.load_cloud()

        self.assertEqual(loaded.base_url, "https://api.example.com/v1")
        self.assertEqual(loaded.model, "m1")
        self.assertEqual(loaded.api_key, "sk-abc")

    def test_base_url_trailing_slash_stripped(self) -> None:
        cloud.update_cloud(base_url="https://api.example.com/v1/")
        self.assertEqual(
            cloud.load_cloud().base_url, "https://api.example.com/v1"
        )

    def test_empty_api_key_preserves_existing(self) -> None:
        """用户只改地址时不该被迫重输 Key。"""
        cloud.update_cloud(base_url="https://a/v1", model="m", api_key="sk-old")
        cloud.update_cloud(base_url="https://b/v1", api_key="")

        loaded = cloud.load_cloud()

        self.assertEqual(loaded.base_url, "https://b/v1")
        self.assertEqual(loaded.api_key, "sk-old", "空字符串应保留原 Key")

    def test_update_params(self) -> None:
        cloud.update_cloud(
            base_url="https://a/v1", model="m", api_key="k",
            temperature=0.7, max_tokens=2048,
        )

        loaded = cloud.load_cloud()

        self.assertAlmostEqual(loaded.temperature, 0.7)
        self.assertEqual(loaded.max_tokens, 2048)

    def test_clear_removes_everything(self) -> None:
        cloud.update_cloud(base_url="https://a/v1", model="m", api_key="k")
        self.assertTrue(self.cloud_path.exists())

        cloud.clear_cloud()

        self.assertFalse(self.cloud_path.exists())
        self.assertFalse(cloud.load_cloud().configured)

    def test_corrupt_file_is_tolerated(self) -> None:
        self.cloud_path.write_text("{not json", encoding="utf-8")
        self.assertFalse(cloud.load_cloud().configured)


class TestProviderSwitch(CloudTestBase):
    def test_default_is_llama_cpp(self) -> None:
        self.assertEqual(cloud.active_provider(), "llama_cpp")

    def test_switch_to_local(self) -> None:
        self.assertEqual(cloud.set_provider("llama_cpp"), "llama_cpp")
        self.assertEqual(cloud.active_provider(), "llama_cpp")

    def test_cloud_requires_configuration(self) -> None:
        """未配置就切云端应被拒绝，而不是等到问答时才炸。"""
        with self.assertRaises(ValueError) as ctx:
            cloud.set_provider("openai")
        self.assertIn("尚未配置", str(ctx.exception))

    def test_switch_to_cloud_when_configured(self) -> None:
        cloud.update_cloud(
            base_url="https://a/v1", model="m", api_key="sk-1"
        )

        self.assertEqual(cloud.set_provider("openai"), "openai")
        self.assertEqual(cloud.active_provider(), "openai")

    def test_unknown_provider_rejected(self) -> None:
        with self.assertRaises(ValueError):
            cloud.set_provider("gemini")

    def test_provider_persists_alongside_model(self) -> None:
        cloud.update_cloud(base_url="https://a/v1", model="m", api_key="k")
        cloud.set_provider("openai")

        state.save_state(model="Qwen3.8-4B-Q4_K_M.gguf")

        self.assertEqual(state.load_state()["provider"], "openai")
        self.assertEqual(
            state.load_state()["model"], "Qwen3.8-4B-Q4_K_M.gguf"
        )


class TestStatePersistence(CloudTestBase):
    def test_load_empty(self) -> None:
        self.assertEqual(state.load_state(), {})

    def test_save_and_load(self) -> None:
        state.save_state(provider="llama_cpp", model="m.gguf")
        self.assertEqual(
            state.load_state(), {"provider": "llama_cpp", "model": "m.gguf"}
        )

    def test_none_removes_field(self) -> None:
        state.save_state(provider="openai", model="m.gguf")
        state.save_state(model=None)

        self.assertNotIn("model", state.load_state())
        self.assertEqual(state.load_state()["provider"], "openai")

    def test_clear(self) -> None:
        state.save_state(provider="openai")
        state.clear_state()
        self.assertEqual(state.load_state(), {})

    def test_corrupt_file(self) -> None:
        self.state_path.write_text("nonsense", encoding="utf-8")
        self.assertEqual(state.load_state(), {})


class TestConnection(unittest.TestCase):
    def test_empty_base_url(self) -> None:
        ok, message, models = cloud.test_connection("", "sk-1")
        self.assertFalse(ok)
        self.assertIn("不能为空", message)
        self.assertEqual(models, [])

    def test_unreachable_host(self) -> None:
        ok, message, _ = cloud.test_connection(
            "http://127.0.0.1:1/v1", "sk-1", timeout=2.0
        )
        self.assertFalse(ok)
        self.assertTrue(message)


if __name__ == "__main__":
    unittest.main()
