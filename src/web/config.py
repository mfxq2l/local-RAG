"""联网搜索配置。

落盘到 ``data/web_search.json``，与 ``llm_cloud.json`` 同一套思路：
API Key 存明文（本机文件），但**对外只返回掩码**。
"""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from src.config import DATA_DIR
from src.web.providers import DEFAULT_PROVIDER, PROVIDERS


WEB_CONFIG_PATH = DATA_DIR / "web_search.json"

# 结果数与抓取量的硬边界
MIN_RESULTS = 1
MAX_RESULTS = 15
MAX_FETCH_TOP = 8
MIN_TIMEOUT = 3.0
MAX_TIMEOUT = 60.0


@dataclass
class WebSettings:
    """联网搜索设置。"""

    # 是否默认开启（每次请求仍可单独覆盖）
    enabled: bool = False

    provider: str = DEFAULT_PROVIDER

    # 仅 API 型后端需要
    api_key: str = ""

    # 仅 SearXNG 需要
    searxng_url: str = ""

    # 取几条搜索结果
    max_results: int = 5

    # 是否抓取网页正文（关闭则只用搜索摘要，更快）
    fetch_pages: bool = True
    fetch_top_n: int = 3

    # 单页正文最多保留多少字符
    max_page_chars: int = 3000

    timeout: float = 15.0

    # 是否走系统代理（国内直连拿不到部分站点）
    use_proxy: bool = True


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize(data: dict[str, Any] | None) -> WebSettings:
    """把任意字典收敛成合法设置。非法值一律退回默认。"""
    data = data or {}
    defaults = WebSettings()

    provider = str(data.get("provider") or defaults.provider).strip().lower()
    if provider not in PROVIDERS:
        provider = defaults.provider

    def as_bool(key: str) -> bool:
        value = data.get(key, getattr(defaults, key))
        return bool(value) if isinstance(value, bool) else getattr(defaults, key)

    def as_int(key: str, low: int, high: int) -> int:
        value = data.get(key, getattr(defaults, key))
        try:
            return int(_clamp(int(value), low, high))
        except (TypeError, ValueError):
            return getattr(defaults, key)

    try:
        timeout = float(
            _clamp(
                float(data.get("timeout", defaults.timeout)),
                MIN_TIMEOUT,
                MAX_TIMEOUT,
            )
        )
    except (TypeError, ValueError):
        timeout = defaults.timeout

    return WebSettings(
        enabled=as_bool("enabled"),
        provider=provider,
        api_key=str(data.get("api_key") or ""),
        searxng_url=str(data.get("searxng_url") or "").strip(),
        max_results=as_int("max_results", MIN_RESULTS, MAX_RESULTS),
        fetch_pages=as_bool("fetch_pages"),
        fetch_top_n=as_int("fetch_top_n", 0, MAX_FETCH_TOP),
        max_page_chars=as_int("max_page_chars", 200, 8000),
        timeout=timeout,
        use_proxy=as_bool("use_proxy"),
    )


def mask_key(key: str) -> str:
    """把 Key 变成 ``sk-abc…xyz`` 形式，用于展示。"""
    key = (key or "").strip()
    if not key:
        return ""
    if len(key) <= 8:
        return key[0] + "…" + key[-1] if len(key) > 2 else "…"
    return f"{key[:4]}…{key[-4:]}"


class WebConfigStore:
    """配置读写。"""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path or WEB_CONFIG_PATH)
        self._lock = threading.RLock()
        self._data: WebSettings = WebSettings()
        self._load()

    # ------------------------------------------------------------------

    def _load(self) -> None:
        try:
            if self.path.exists():
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    self._data = normalize(raw)
        except Exception:  # noqa: BLE001
            self._data = WebSettings()

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(asdict(self._data), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------

    def get(self) -> WebSettings:
        with self._lock:
            return WebSettings(**asdict(self._data))

    def public(self) -> dict[str, Any]:
        """给前端的版本：Key 只出掩码。"""
        data = asdict(self.get())
        data["api_key"] = mask_key(data["api_key"])
        data["has_key"] = bool(self.get().api_key)
        return data

    def update(self, patch: dict[str, Any]) -> WebSettings:
        """局部更新；``api_key`` 传空串表示保持不变。

        非法值**忽略并保留原值**（而不是重置为默认）—— 前端可能只改了
        一个字段，不该因为某个值不认识就把用户已有的配置清掉。
        ``provider`` 这种枚举型尤其需要注意：``normalize`` 是给「读文件」
        兜底的，它认不出「用户刚发来的非法值」和「文件里本来就是坏的」，
        所以校验要在这一层先做。
        """
        with self._lock:
            current = asdict(self._data)

            for key, value in (patch or {}).items():
                if key not in current:
                    continue
                # Key 的空值 = 不改动（避免前端回显掩码时把真 Key 冲掉）
                if key == "api_key" and not str(value or "").strip():
                    continue
                # 枚举型：不认识的值直接丢弃，保留原值
                if key == "provider":
                    if str(value or "").strip().lower() not in PROVIDERS:
                        continue
                current[key] = value

            self._data = normalize(current)
            self._save()
            return self.get()

    def clear(self) -> WebSettings:
        """清空配置（含 Key）。"""
        with self._lock:
            self._data = WebSettings()
            self._save()
            return self.get()


_store: WebConfigStore | None = None
_store_lock = threading.Lock()


def get_web_config() -> WebConfigStore:
    global _store

    with _store_lock:
        if _store is None:
            _store = WebConfigStore()
        return _store


__all__ = [
    "WEB_CONFIG_PATH",
    "WebConfigStore",
    "WebSettings",
    "get_web_config",
    "mask_key",
    "normalize",
]
