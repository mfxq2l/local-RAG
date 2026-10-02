"""Qwen3-Embedding-4B 文本 embedding。

使用 llama-server /v1/embeddings 接口。
Qwen3 系列使用 last-token pooling。
"""

from __future__ import annotations

from src.config import QWEN3_EMBEDDING
from src.embedding.base import LlamaEmbeddingServer


class QwenEmbedder(LlamaEmbeddingServer):
    def __init__(self, port: int = 8080) -> None:
        super().__init__(
            config=QWEN3_EMBEDDING,
            port=port,
            pooling="last",
        )


__all__ = ["QwenEmbedder"]