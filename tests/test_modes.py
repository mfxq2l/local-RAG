"""问答档位（快速 / 精确）测试。"""

from __future__ import annotations

import unittest

from src.config import LLM_CONFIG
from src.rag.modes import (
    FAST,
    MODES,
    PRECISE,
    mode_catalog,
    resolve_mode,
)


class TestResolveMode(unittest.TestCase):
    def test_explicit_names(self) -> None:
        self.assertIs(resolve_mode("fast"), FAST)
        self.assertIs(resolve_mode("precise"), PRECISE)

    def test_case_insensitive(self) -> None:
        self.assertIs(resolve_mode("FAST"), FAST)
        self.assertIs(resolve_mode("  Precise  "), PRECISE)

    def test_aliases(self) -> None:
        self.assertIs(resolve_mode("quick"), FAST)
        self.assertIs(resolve_mode("speed"), FAST)
        self.assertIs(resolve_mode("thinking"), PRECISE)
        self.assertIs(resolve_mode("accurate"), PRECISE)

    def test_none_uses_config_default(self) -> None:
        expected = MODES.get(LLM_CONFIG.default_mode, PRECISE)
        self.assertIs(resolve_mode(None), expected)

    def test_unknown_raises(self) -> None:
        with self.assertRaises(ValueError):
            resolve_mode("turbo")

    def test_error_message_lists_options(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            resolve_mode("nope")
        self.assertIn("fast", str(ctx.exception))
        self.assertIn("precise", str(ctx.exception))


class TestModeSemantics(unittest.TestCase):
    def test_fast_disables_thinking(self) -> None:
        self.assertIs(FAST.thinking, False)

    def test_precise_enables_thinking(self) -> None:
        self.assertIs(PRECISE.thinking, True)

    def test_fast_is_cheaper(self) -> None:
        self.assertLess(FAST.max_tokens, PRECISE.max_tokens)
        self.assertLessEqual(FAST.temperature, PRECISE.temperature)

    def test_distinct_names(self) -> None:
        self.assertNotEqual(FAST.name, PRECISE.name)

    def test_modes_registry_covers_both(self) -> None:
        self.assertEqual(set(MODES), {"fast", "precise"})


class TestModeCatalog(unittest.TestCase):
    def test_catalog_shape(self) -> None:
        catalog = mode_catalog()
        self.assertEqual(len(catalog), 2)

        for entry in catalog:
            for key in (
                "name", "label", "description",
                "thinking", "max_tokens", "temperature", "default",
            ):
                self.assertIn(key, entry)

    def test_exactly_one_default(self) -> None:
        defaults = [e for e in mode_catalog() if e["default"]]
        self.assertEqual(len(defaults), 1)

    def test_default_matches_config(self) -> None:
        default_name = next(e["name"] for e in mode_catalog() if e["default"])
        self.assertEqual(default_name, LLM_CONFIG.default_mode)


if __name__ == "__main__":
    unittest.main()
