"""WeMM-Embedding-2B 多模态 embedding。

说明：
    llama.cpp 的 /v1/embeddings 端点只接受文本输入。
    因此这里对图片采用「图片→文本描述→文本 embedding」的降级方案，
    图片描述由 Pillow 提取元数据 + 可选 OCR（见 ingest/image.py）。

    如果后续 llama.cpp 支持多模态 embedding 输入，
    只需替换 embed_images() 的实现。
"""

from __future__ import annotations

from pathlib import Path

from src.config import WEMM_EMBEDDING
from src.embedding.base import LlamaEmbeddingServer


class WeMMEmbedder(LlamaEmbeddingServer):
    def __init__(self, port: int = 8081) -> None:
        super().__init__(
            config=WEMM_EMBEDDING,
            port=port,
            pooling="mean",
        )

    # ------------------------------------------------------------------
    # 多模态（降级）
    # ------------------------------------------------------------------

    def embed_images(
        self,
        image_paths: list[str | Path],
        descriptions: list[str] | None = None,
    ) -> list[list[float]]:
        """图片 embedding。

        descriptions 为 None 时使用 ingest.image.describe_image() 生成。
        """
        if not image_paths:
            return []

        if descriptions is None:
            from src.ingest.image import describe_image

            descriptions = [
                describe_image(Path(p)) for p in image_paths
            ]

        return self.embed(descriptions)


__all__ = ["WeMMEmbedder"]