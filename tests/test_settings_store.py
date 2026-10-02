"""WebUI 设置持久化测试。

重点：非法值必须被**忽略并保留原值**，而不是把设置写坏。
"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.settings_store import SettingsStore


class TestSettingsDefaults(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_settings_test_"))
        self.store = SettingsStore(self.tmp / "ui_settings.json")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ------------------------------------------------------------------

    def test_all_sections_present(self) -> None:
        data = self.store.all()
        self.assertEqual(
            set(data.keys()), {"general", "retrieval", "chat"}
        )

    def test_general_defaults(self) -> None:
        general = self.store.all()["general"]
        self.assertEqual(general["language"], "zh")
        self.assertEqual(general["theme"], "dark")
        self.assertEqual(general["font_size"], 14)

    def test_returns_copy_not_internal_state(self) -> None:
        data = self.store.all()
        data["general"]["theme"] = "hacked"

        self.assertEqual(self.store.all()["general"]["theme"], "dark")

    def test_get_single_value(self) -> None:
        self.assertEqual(self.store.get("general", "language"), "zh")
        self.assertIsNone(self.store.get("general", "nope"))
        self.assertEqual(self.store.get("general", "nope", "fb"), "fb")


class TestSettingsUpdate(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_settings_test_"))
        self.path = self.tmp / "ui_settings.json"
        self.store = SettingsStore(self.path)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_update_single_field(self) -> None:
        result = self.store.update({"general": {"theme": "light"}})

        self.assertEqual(result["general"]["theme"], "light")
        # 其他字段不受影响
        self.assertEqual(result["general"]["language"], "zh")
        self.assertEqual(result["general"]["font_size"], 14)

    def test_partial_section_update(self) -> None:
        self.store.update({"chat": {"condense": False}})

        data = self.store.all()
        self.assertFalse(data["chat"]["condense"])
        self.assertEqual(data["chat"]["mode"], data["chat"]["mode"])

    def test_unknown_section_ignored(self) -> None:
        self.store.update({"nope": {"a": 1}})
        self.assertNotIn("nope", self.store.all())

    def test_unknown_key_ignored(self) -> None:
        self.store.update({"general": {"unknown": "x"}})
        self.assertNotIn("unknown", self.store.all()["general"])

    def test_enum_rejects_bad_value(self) -> None:
        """实测过的关键行为：非法主题不能被写入。"""
        self.store.update({"general": {"theme": "rainbow"}})
        self.assertEqual(self.store.all()["general"]["theme"], "dark")

        self.store.update({"general": {"language": "fr"}})
        self.assertEqual(self.store.all()["general"]["language"], "zh")

        self.store.update({"chat": {"mode": "turbo"}})
        self.assertNotEqual(self.store.all()["chat"]["mode"], "turbo")

    def test_enum_accepts_good_values(self) -> None:
        for theme in ("dark", "light", "system"):
            self.store.update({"general": {"theme": theme}})
            self.assertEqual(self.store.all()["general"]["theme"], theme)

        for language in ("zh", "en"):
            self.store.update({"general": {"language": language}})
            self.assertEqual(self.store.all()["general"]["language"], language)

    def test_bool_type_enforced(self) -> None:
        self.store.update({"retrieval": {"use_bm25": False}})
        self.assertFalse(self.store.all()["retrieval"]["use_bm25"])

        # 字符串不是布尔，应被忽略
        self.store.update({"retrieval": {"use_bm25": "yes"}})
        self.assertFalse(self.store.all()["retrieval"]["use_bm25"])

    def test_number_is_clamped(self) -> None:
        self.store.update({"general": {"font_size": 99999}})
        self.assertLessEqual(self.store.all()["general"]["font_size"], 100)

        self.store.update({"general": {"font_size": -50}})
        self.assertGreaterEqual(self.store.all()["general"]["font_size"], 0)

    def test_number_rejects_non_numeric(self) -> None:
        self.store.update({"retrieval": {"top_k": 7}})
        self.store.update({"retrieval": {"top_k": "abc"}})
        self.assertEqual(self.store.all()["retrieval"]["top_k"], 7)

    def test_float_setting(self) -> None:
        self.store.update({"retrieval": {"min_relevance": 0.3}})
        self.assertAlmostEqual(
            self.store.all()["retrieval"]["min_relevance"], 0.3
        )

    def test_bool_not_accepted_as_int(self) -> None:
        """True 是 int 的子类，不应被当成数字写入。"""
        self.store.update({"retrieval": {"top_k": True}})
        self.assertEqual(self.store.all()["retrieval"]["top_k"], 5)

    def test_empty_patch_is_safe(self) -> None:
        before = self.store.all()
        self.store.update({})
        self.assertEqual(self.store.all(), before)

    def test_non_dict_section_is_ignored(self) -> None:
        self.store.update({"general": "not a dict"})  # type: ignore[dict-item]
        self.assertEqual(self.store.all()["general"]["theme"], "dark")


class TestSettingsPersistence(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_settings_test_"))
        self.path = self.tmp / "ui_settings.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_update_persists_to_disk(self) -> None:
        SettingsStore(self.path).update(
            {"general": {"theme": "light", "language": "en"}}
        )

        self.assertTrue(self.path.exists())

        reloaded = SettingsStore(self.path).all()
        self.assertEqual(reloaded["general"]["theme"], "light")
        self.assertEqual(reloaded["general"]["language"], "en")

    def test_no_write_when_nothing_changed(self) -> None:
        store = SettingsStore(self.path)
        store.update({"general": {"theme": "dark"}})  # 与默认相同
        self.assertFalse(self.path.exists())

    def test_corrupt_file_falls_back_to_defaults(self) -> None:
        self.path.write_text("{broken", encoding="utf-8")

        store = SettingsStore(self.path)

        self.assertEqual(store.all()["general"]["theme"], "dark")

    def test_reset_restores_defaults(self) -> None:
        store = SettingsStore(self.path)
        store.update({"general": {"theme": "light"}, "chat": {"condense": False}})

        result = store.reset()

        self.assertEqual(result["general"]["theme"], "dark")
        self.assertTrue(result["chat"]["condense"])
        # 也应落盘
        self.assertEqual(
            SettingsStore(self.path).all()["general"]["theme"], "dark"
        )

    def test_unwritable_path_does_not_raise(self) -> None:
        store = SettingsStore(Path("Z:/nope/ui_settings.json"))
        result = store.update({"general": {"theme": "light"}})
        self.assertEqual(result["general"]["theme"], "light")

    def test_file_is_valid_json(self) -> None:
        store = SettingsStore(self.path)
        store.update({"general": {"font_size": 16}})

        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data["general"]["font_size"], 16)


class TestRelevanceFloor(unittest.TestCase):
    """相关性下限必须真的在检索时生效。

    踩过的坑：`RetrievalConfig` 是 `@dataclass(frozen=True)`，直接赋值会抛
    `FrozenInstanceError`，而异常被 `except Exception: pass` 吞掉 —— 设置
    看起来保存成功，实际检索完全不受影响。
    """

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_floor_test_"))

        import src.settings_store as store_module

        self.module = store_module
        self.original = store_module._store
        store_module._store = store_module.SettingsStore(
            self.tmp / "ui_settings.json"
        )

    def tearDown(self) -> None:
        self.module._store = self.original
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_returns_setting_value(self) -> None:
        self.module.get_settings().update(
            {"retrieval": {"min_relevance": 0.2}}
        )

        self.assertAlmostEqual(self.module.relevance_floor(0.45), 0.2)

    def test_falls_back_when_settings_unavailable(self) -> None:
        self.module._store = None
        # 没有已加载的设置实例时，应退回调用方给的默认值
        self.assertAlmostEqual(self.module.relevance_floor(0.45), 0.45)

    def test_reset_restores_default(self) -> None:
        settings = self.module.get_settings()
        settings.update({"retrieval": {"min_relevance": 0.1}})
        settings.reset()

        self.assertAlmostEqual(self.module.relevance_floor(0.45), 0.45)

    def test_zero_disables_filter(self) -> None:
        """设为 0 表示关闭过滤，不能因为 falsy 就退回默认值。"""
        self.module.get_settings().update({"retrieval": {"min_relevance": 0}})

        self.assertAlmostEqual(self.module.relevance_floor(0.45), 0.0)

    def test_frozen_config_is_never_mutated(self) -> None:
        from src.config import RETRIEVAL_CONFIG

        before = RETRIEVAL_CONFIG.min_relevance_score

        self.module.get_settings().update(
            {"retrieval": {"min_relevance": 0.99}}
        )
        self.module.relevance_floor(before)

        self.assertEqual(RETRIEVAL_CONFIG.min_relevance_score, before)


if __name__ == "__main__":
    unittest.main()
