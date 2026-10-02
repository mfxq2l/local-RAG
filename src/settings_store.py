"""WebUI 设置的服务端持久化。

为什么放服务端而不是 localStorage
--------------------------------
放浏览器里换台机器就没了，而且「检索默认参数」这类设置本来就该由后端
解析。这里保存为 ``data/ui_settings.json``，前端启动时拉取一次。

写入采用**深合并 + 白名单校验**：前端只提交要改的字段，非法值一律忽略
并保留原值，避免一个坏请求把设置写坏。
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from src.config import DATA_DIR, LLM_CONFIG, RETRIEVAL_CONFIG


SETTINGS_PATH = DATA_DIR / "ui_settings.json"


def _defaults() -> dict[str, Any]:
    return {
        "general": {
            "language": "zh",       # zh | en
            "theme": "dark",        # dark | light | system
            "font_size": 14,
        },
        "retrieval": {
            "top_k": RETRIEVAL_CONFIG.context_top_k,
            "use_bm25": RETRIEVAL_CONFIG.enable_bm25,
            "use_reranker": RETRIEVAL_CONFIG.enable_reranker,
            "include_images": True,
            "min_relevance": RETRIEVAL_CONFIG.min_relevance_score,
        },
        "chat": {
            "mode": LLM_CONFIG.default_mode,
            "condense": True,
            "stream": True,
        },
    }


def _coerce(value: Any, current: Any) -> Any:
    """按当前值的类型做校验转换；不合法返回 ``None`` 表示忽略。"""
    if isinstance(current, bool):
        return bool(value) if isinstance(value, bool) else None

    if isinstance(current, int):
        if isinstance(value, bool):
            return None
        try:
            number = int(value)
        except (TypeError, ValueError):
            return None
        # 数值型设置的合法区间
        return max(0, min(number, 100))

    if isinstance(current, float):
        if isinstance(value, bool):
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    if isinstance(current, str):
        return value if isinstance(value, str) else None

    if isinstance(current, dict):
        if not isinstance(value, dict):
            return None
        merged = dict(current)
        for key, sub in value.items():
            if key not in current:
                continue
            coerced = _coerce(sub, current[key])
            if coerced is not None:
                merged[key] = coerced
        return merged

    return None


# 枚举型设置只接受固定取值
_ENUMS = {
    ("general", "language"): {"zh", "en"},
    ("general", "theme"): {"dark", "light", "system"},
    ("chat", "mode"): {"fast", "precise"},
}


def relevance_floor(fallback: float) -> float:
    """相关性下限的**运行时取值**。

    为什么不直接改 ``RETRIEVAL_CONFIG``：它是 ``@dataclass(frozen=True)``，
    赋值会抛 ``FrozenInstanceError``。而且 ``RETRIEVAL_CONFIG`` 被别的模块
    以 ``from src.config import RETRIEVAL_CONFIG`` 按值导入，重新绑定模块属性
    也影响不到那些引用。

    所以检索侧在使用点通过这个函数取当前设置，取不到就退回配置默认值。
    """
    try:
        value = get_settings().get("retrieval", "min_relevance")
        if value is not None:
            return float(value)
    except Exception:  # noqa: BLE001
        pass

    return fallback


class SettingsStore:
    """设置的读写。"""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path or SETTINGS_PATH)
        self._lock = threading.RLock()
        self._data: dict[str, Any] = _defaults()
        self._load()

    # ------------------------------------------------------------------

    def _load(self) -> None:
        try:
            if self.path.exists():
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self._data = _coerce(raw, _defaults()) or _defaults()

        except Exception:  # noqa: BLE001
            self._data = _defaults()

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------

    def all(self) -> dict[str, Any]:
        with self._lock:
            return json.loads(json.dumps(self._data))

    def defaults(self) -> dict[str, Any]:
        return _defaults()

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        with self._lock:
            return self._data.get(section, {}).get(key, fallback)

    def update(self, patch: dict[str, Any]) -> dict[str, Any]:
        """深合并一份修改，返回更新后的完整设置。"""
        with self._lock:
            current = self._data
            changed = False

            for section, values in (patch or {}).items():
                if section not in current or not isinstance(values, dict):
                    continue

                for key, value in values.items():
                    if key not in current[section]:
                        continue

                    allowed = _ENUMS.get((section, key))
                    if allowed is not None and value not in allowed:
                        continue

                    coerced = _coerce(value, current[section][key])
                    if coerced is None or coerced == current[section][key]:
                        continue

                    current[section][key] = coerced
                    changed = True

            if changed:
                self._save()

            return json.loads(json.dumps(current))

    def reset(self) -> dict[str, Any]:
        with self._lock:
            self._data = _defaults()
            self._save()
            return self.all()


_store: SettingsStore | None = None
_store_lock = threading.Lock()


def get_settings() -> SettingsStore:
    global _store

    with _store_lock:
        if _store is None:
            _store = SettingsStore()
        return _store


__all__ = [
    "SETTINGS_PATH",
    "SettingsStore",
    "get_settings",
    "relevance_floor",
]
