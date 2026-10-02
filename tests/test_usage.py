"""Token 用量统计测试。"""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src import usage as usage_module
from src.usage import UsageTotals, UsageTracker, record_usage


class TestUsageTotals(unittest.TestCase):
    def test_add_accumulates(self) -> None:
        totals = UsageTotals()
        totals.add(10, 20, 30)
        totals.add(1, 2, 3)

        self.assertEqual(totals.calls, 2)
        self.assertEqual(totals.prompt_tokens, 11)
        self.assertEqual(totals.completion_tokens, 22)
        self.assertEqual(totals.total_tokens, 33)

    def test_total_inferred_when_missing(self) -> None:
        """有些服务端不给 total_tokens，应由 prompt+completion 推出。"""
        totals = UsageTotals()
        totals.add(prompt_tokens=7, completion_tokens=5)

        self.assertEqual(totals.total_tokens, 12)

    def test_none_values_are_safe(self) -> None:
        totals = UsageTotals()
        totals.add(None, None, None)  # type: ignore[arg-type]

        self.assertEqual(totals.calls, 1)
        self.assertEqual(totals.total_tokens, 0)

    def test_to_dict(self) -> None:
        totals = UsageTotals()
        totals.add(1, 2, 3)

        self.assertEqual(
            totals.to_dict(),
            {
                "calls": 1,
                "prompt_tokens": 1,
                "completion_tokens": 2,
                "total_tokens": 3,
            },
        )


class TestUsageTracker(unittest.TestCase):
    def test_record_updates_all_buckets(self) -> None:
        tracker = UsageTracker()
        tracker.record(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            model="m1",
            kind="chat",
        )

        summary = tracker.summary()

        self.assertEqual(summary["totals"]["total_tokens"], 150)
        self.assertEqual(summary["by_model"]["m1"]["total_tokens"], 150)
        self.assertEqual(summary["by_kind"]["chat"]["total_tokens"], 150)
        self.assertEqual(len(summary["by_day"]), 1)

    def test_record_accumulates_across_calls(self) -> None:
        tracker = UsageTracker()
        for _ in range(3):
            tracker.record(prompt_tokens=10, completion_tokens=5, total_tokens=15, model="m", kind="ask")

        self.assertEqual(tracker.summary()["totals"]["calls"], 3)
        self.assertEqual(tracker.summary()["totals"]["total_tokens"], 45)

    def test_unknown_model_and_kind_get_placeholders(self) -> None:
        tracker = UsageTracker()
        tracker.record(prompt_tokens=1, completion_tokens=1, total_tokens=2)

        summary = tracker.summary()

        self.assertIn("未知", summary["by_model"])
        self.assertIn("ask", summary["by_kind"])

    def test_by_model_sorted_by_tokens(self) -> None:
        tracker = UsageTracker()
        tracker.record(prompt_tokens=10, completion_tokens=0, total_tokens=10, model="small")
        tracker.record(prompt_tokens=1000, completion_tokens=0, total_tokens=1000, model="big")

        self.assertEqual(
            list(tracker.summary()["by_model"].keys()), ["big", "small"]
        )

    def test_reset_clears_everything(self) -> None:
        tracker = UsageTracker()
        tracker.record(prompt_tokens=100, completion_tokens=50, total_tokens=150, model="m", kind="chat")
        tracker.reset()

        summary = tracker.summary()

        self.assertEqual(summary["totals"]["calls"], 0)
        self.assertEqual(summary["totals"]["total_tokens"], 0)
        self.assertEqual(summary["by_model"], {})
        self.assertEqual(summary["by_kind"], {})

    def test_by_day_limited_by_recent_days(self) -> None:
        tracker = UsageTracker()

        with tracker._lock:
            for day in range(20):
                tracker.by_day[f"2026-01-{day + 1:02d}"] = UsageTotals()

        self.assertLessEqual(len(tracker.summary(recent_days=5)["by_day"]), 5)

    def test_summary_is_json_serializable(self) -> None:
        tracker = UsageTracker()
        tracker.record(prompt_tokens=1, completion_tokens=2, total_tokens=3, model="m", kind="chat")

        json.dumps(tracker.summary())  # 不应抛异常


class TestUsagePersistence(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_usage_test_"))
        self.original = usage_module.USAGE_PATH
        usage_module.USAGE_PATH = self.tmp / "usage_stats.json"

    def tearDown(self) -> None:
        usage_module.USAGE_PATH = self.original
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_restores_totals(self) -> None:
        payload = {
            "version": 1,
            "started_at": 100.0,
            "last_used_at": 200.0,
            "totals": {"calls": 5, "prompt_tokens": 50,
                       "completion_tokens": 25, "total_tokens": 75},
            "by_model": {"m": {"calls": 5, "prompt_tokens": 50,
                               "completion_tokens": 25, "total_tokens": 75}},
            "by_kind": {"chat": {"calls": 5, "prompt_tokens": 50,
                                 "completion_tokens": 25, "total_tokens": 75}},
            "by_day": {},
        }
        usage_module.USAGE_PATH.write_text(
            json.dumps(payload), encoding="utf-8"
        )

        tracker = usage_module._load_from_disk()

        self.assertEqual(tracker.totals.calls, 5)
        self.assertEqual(tracker.totals.total_tokens, 75)
        self.assertEqual(tracker.by_model["m"].total_tokens, 75)
        self.assertEqual(tracker.started_at, 100.0)

    def test_missing_file_gives_zero(self) -> None:
        tracker = usage_module._load_from_disk()
        self.assertEqual(tracker.totals.calls, 0)

    def test_corrupt_file_does_not_raise(self) -> None:
        usage_module.USAGE_PATH.write_text("{bad json", encoding="utf-8")
        tracker = usage_module._load_from_disk()
        self.assertEqual(tracker.totals.calls, 0)

    def test_flush_writes_file(self) -> None:
        tracker = UsageTracker()
        tracker.record(prompt_tokens=10, completion_tokens=5, total_tokens=15, model="m", kind="chat")
        tracker.flush()

        self.assertTrue(usage_module.USAGE_PATH.exists())

        data = json.loads(usage_module.USAGE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data["totals"]["total_tokens"], 15)

    def test_flush_is_noop_when_clean(self) -> None:
        tracker = UsageTracker()
        tracker.flush()  # 不应创建文件
        self.assertFalse(usage_module.USAGE_PATH.exists())

    def test_unwritable_path_does_not_raise(self) -> None:
        """统计落盘失败绝不能影响问答本身。"""
        usage_module.USAGE_PATH = Path("Z:/nope/usage.json")
        tracker = UsageTracker()
        tracker.record(prompt_tokens=1, completion_tokens=2, total_tokens=3, model="m", kind="chat")
        tracker.flush()

        self.assertEqual(tracker.totals.total_tokens, 3)


class TestRecordUsageHelper(unittest.TestCase):
    def setUp(self) -> None:
        self.tracker = usage_module.get_tracker()
        self.tracker.reset()

    def tearDown(self) -> None:
        self.tracker.reset()

    def test_none_is_ignored(self) -> None:
        record_usage(None, model="m", kind="chat")
        self.assertEqual(self.tracker.summary()["totals"]["calls"], 0)

    def test_empty_dict_is_ignored(self) -> None:
        record_usage({}, model="m", kind="chat")
        self.assertEqual(self.tracker.summary()["totals"]["calls"], 0)

    def test_records_real_usage(self) -> None:
        record_usage(
            {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            model="gemma",
            kind="chat",
        )

        summary = self.tracker.summary()

        self.assertEqual(summary["totals"]["total_tokens"], 30)
        self.assertEqual(summary["by_model"]["gemma"]["total_tokens"], 30)

    def test_partial_usage_dict(self) -> None:
        record_usage({"prompt_tokens": 10}, model="m", kind="chat")
        self.assertEqual(self.tracker.summary()["totals"]["total_tokens"], 10)

    def test_bad_values_do_not_raise(self) -> None:
        record_usage(
            {"prompt_tokens": "abc", "completion_tokens": None},
            model="m",
            kind="chat",
        )


if __name__ == "__main__":
    unittest.main()
