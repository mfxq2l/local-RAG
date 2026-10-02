"""Embedding 工厂：按名字返回单例 embedder。"""

from __future__ import annotations

from src.config import ACTIVE_EMBEDDING
from src.embedding.qwen import QwenEmbedder
from src.embedding.wemm import WeMMEmbedder

_instances: dict[str, object] = {}

# 端口分配：Qwen 8080，WeMM 8081
_MODEL_TABLE = {
    "qwen":  ("qwen3", QwenEmbedder, 8080),
    "qwen3": ("qwen3", QwenEmbedder, 8080),
    "wemm":  ("wemm",  WeMMEmbedder, 8081),
}


def get_embedder(name: str | None = None):
    """返回单例 embedder。name 为 None 时使用 config 的 ACTIVE_EMBEDDING。"""
    key = (name or ACTIVE_EMBEDDING).lower()
    if key not in _MODEL_TABLE:
        raise ValueError(
            f"未知 embedding 模型: {key!r}，可选: {list(_MODEL_TABLE)}"
        )

    canonical, cls, port = _MODEL_TABLE[key]

    if canonical not in _instances:
        _instances[canonical] = cls(port=port)

    return _instances[canonical]


def model_key(name: str | None = None) -> str:
    """把别名归一化到 canonical key（qwen3 / wemm）。"""
    key = (name or ACTIVE_EMBEDDING).lower()
    if key not in _MODEL_TABLE:
        raise ValueError(f"未知 embedding 模型: {key!r}")
    return _MODEL_TABLE[key][0]


__all__ = ["get_embedder", "model_key", "QwenEmbedder", "WeMMEmbedder"]