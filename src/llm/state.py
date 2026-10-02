"""LLM 运行状态的持久化。

保存在 ``data/llm_selection.json``：

    {
      "provider": "llama_cpp",        # llama_cpp | openai
      "model": "Qwen3.8-4B-Q4_K_M.gguf"
    }

``provider`` 决定用本地离线模型还是云端 API；``model`` 是本地模型的文件名。
云端凭据单独存放（见 :mod:`src.llm.cloud`），避免混在一起。
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

from src.config import DATA_DIR


STATE_PATH = DATA_DIR / "llm_selection.json"
_lock = threading.RLock()


def load_state() -> dict:
    """读取状态；文件不存在或损坏时返回空字典。"""
    with _lock:
        try:
            if STATE_PATH.exists():
                data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:  # noqa: BLE001
            pass
    return {}


def save_state(**fields) -> None:
    """合并写入状态字段；值为 ``None`` 的字段会被删除。"""
    with _lock:
        data = load_state()

        for key, value in fields.items():
            if value is None:
                data.pop(key, None)
            else:
                data[key] = value

        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

        if data:
            STATE_PATH.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        elif STATE_PATH.exists():
            STATE_PATH.unlink()


def clear_state() -> None:
    """清空状态。"""
    with _lock:
        if STATE_PATH.exists():
            STATE_PATH.unlink()


__all__ = ["STATE_PATH", "clear_state", "load_state", "save_state"]
