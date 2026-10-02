"""Token 用量统计。

为什么要单独做
--------------
每次问答其实都拿到了 ``usage``（prompt / completion tokens），但**用完就丢**，
用户看不到累计消耗。这里把它按时间累积下来并持久化。

流式的特殊处理
--------------
OpenAI 兼容的流式接口默认**不返回 usage**。需要显式请求：::

    {"stream": true, "stream_options": {"include_usage": true}}

服务端会在最后补一个只含 ``usage``、``choices`` 为空的 chunk。
:mod:`src.llm.openai_compat` 已经做了这件事，本模块负责收集。
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from src.config import DATA_DIR


USAGE_PATH = DATA_DIR / "usage_stats.json"

# 落盘节流：每次记录都写磁盘太浪费，最多每 3 秒落一次
_FLUSH_INTERVAL = 3.0


@dataclass
class UsageTotals:
    """一组累计量。"""

    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def add(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
    ) -> None:
        self.calls += 1
        self.prompt_tokens += int(prompt_tokens or 0)
        self.completion_tokens += int(completion_tokens or 0)
        self.total_tokens += int(
            total_tokens or (prompt_tokens or 0) + (completion_tokens or 0)
        )

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass
class UsageTracker:
    """内存中累积，节流落盘。"""

    totals: UsageTotals = field(default_factory=UsageTotals)
    by_model: dict[str, UsageTotals] = field(default_factory=dict)
    by_kind: dict[str, UsageTotals] = field(default_factory=dict)
    by_day: dict[str, UsageTotals] = field(default_factory=dict)

    started_at: float = field(default_factory=time.time)
    last_used_at: float = 0.0

    _lock: threading.RLock = field(
        default_factory=threading.RLock, repr=False
    )
    _dirty: bool = field(default=False, repr=False)
    _last_flush: float = field(default=0.0, repr=False)

    # ------------------------------------------------------------------
    # 记录
    # ------------------------------------------------------------------

    def record(
        self,
        *,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        model: str = "",
        kind: str = "ask",
    ) -> None:
        """记录一次调用的用量。

        ``kind`` 用于区分来源：``ask`` / ``chat`` / ``condense`` 等。
        """
        with self._lock:
            day = time.strftime("%Y-%m-%d")

            for bucket, key in (
                (self.totals, None),
                (self.by_model, model or "未知"),
                (self.by_kind, kind or "ask"),
                (self.by_day, day),
            ):
                if key is None:
                    bucket.add(prompt_tokens, completion_tokens, total_tokens)
                else:
                    bucket.setdefault(key, UsageTotals()).add(
                        prompt_tokens, completion_tokens, total_tokens
                    )

            self.last_used_at = time.time()
            self._dirty = True

            if time.time() - self._last_flush >= _FLUSH_INTERVAL:
                self._flush_locked()

    # ------------------------------------------------------------------
    # 落盘 / 载入
    # ------------------------------------------------------------------

    def _flush_locked(self) -> None:
        try:
            payload = {
                "version": 1,
                "started_at": self.started_at,
                "last_used_at": self.last_used_at,
                "totals": self.totals.to_dict(),
                "by_model": {k: v.to_dict() for k, v in self.by_model.items()},
                "by_kind": {k: v.to_dict() for k, v in self.by_kind.items()},
                "by_day": {k: v.to_dict() for k, v in self.by_day.items()},
            }

            USAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            USAGE_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            self._dirty = False
            self._last_flush = time.time()

        except Exception:  # noqa: BLE001
            # 统计失败绝不影响问答本身
            pass

    def flush(self) -> None:
        """强制落盘（退出时调用）。"""
        with self._lock:
            if self._dirty:
                self._flush_locked()

    def reset(self) -> None:
        """清零并落盘。"""
        with self._lock:
            self.totals = UsageTotals()
            self.by_model = {}
            self.by_kind = {}
            self.by_day = {}
            self.started_at = time.time()
            self.last_used_at = 0.0
            self._dirty = True
            self._flush_locked()

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------

    def summary(self, recent_days: int = 14) -> dict[str, Any]:
        """给设置面板用的汇总。"""
        with self._lock:
            days = sorted(self.by_day.items(), reverse=True)[:recent_days]

            return {
                "totals": self.totals.to_dict(),
                "by_model": {
                    k: v.to_dict()
                    for k, v in sorted(
                        self.by_model.items(),
                        key=lambda kv: -kv[1].total_tokens,
                    )
                },
                "by_kind": {
                    k: v.to_dict() for k, v in self.by_kind.items()
                },
                "by_day": {k: v.to_dict() for k, v in days},
                "started_at": self.started_at,
                "last_used_at": self.last_used_at,
            }


# ----------------------------------------------------------------------
# 单例
# ----------------------------------------------------------------------

_tracker: UsageTracker | None = None
_tracker_lock = threading.Lock()


def _load_from_disk() -> UsageTracker:
    """从磁盘恢复累计量。"""
    tracker = UsageTracker()

    try:
        if not USAGE_PATH.exists():
            return tracker

        data = json.loads(USAGE_PATH.read_text(encoding="utf-8"))

        tracker.started_at = float(data.get("started_at") or time.time())
        tracker.last_used_at = float(data.get("last_used_at") or 0.0)

        def load_totals(raw: dict) -> UsageTotals:
            allowed = set(UsageTotals.__dataclass_fields__)
            return UsageTotals(
                **{k: int(v) for k, v in (raw or {}).items() if k in allowed}
            )

        tracker.totals = load_totals(data.get("totals") or {})
        tracker.by_model = {
            k: load_totals(v) for k, v in (data.get("by_model") or {}).items()
        }
        tracker.by_kind = {
            k: load_totals(v) for k, v in (data.get("by_kind") or {}).items()
        }
        tracker.by_day = {
            k: load_totals(v) for k, v in (data.get("by_day") or {}).items()
        }

    except Exception:  # noqa: BLE001
        pass

    return tracker


def get_tracker() -> UsageTracker:
    """返回全局用量统计器。"""
    global _tracker

    with _tracker_lock:
        if _tracker is None:
            _tracker = _load_from_disk()
            import atexit

            atexit.register(_tracker.flush)

        return _tracker


def record_usage(
    usage: dict[str, Any] | None,
    *,
    model: str = "",
    kind: str = "ask",
) -> None:
    """便捷入口：直接吃 ``usage`` 字典（形如 ``{prompt_tokens, ...}``）。"""
    if not usage:
        return

    try:
        get_tracker().record(
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            total_tokens=int(usage.get("total_tokens") or 0),
            model=model,
            kind=kind,
        )
    except Exception:  # noqa: BLE001
        pass


__all__ = [
    "USAGE_PATH",
    "UsageTotals",
    "UsageTracker",
    "get_tracker",
    "record_usage",
]
