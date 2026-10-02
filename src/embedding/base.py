"""llama.cpp embedding server 封装。

通过 ``llama-server.exe --embedding`` 拉起一个独立的 HTTP 进程，
用 ``/v1/embeddings`` 做文本向量化。

进程生命周期委托给 :class:`src.llama_server.LlamaServerProcess`。
"""

from __future__ import annotations

import time

from src.config import (
    LLAMA_CONFIG,
    EmbeddingConfig,
)
from src.llama_server import LlamaServerProcess


class LlamaEmbeddingServer:
    """管理一个 llama-server embedding 子进程，提供 embed() 方法。"""

    def __init__(
        self,
        config: EmbeddingConfig,
        port: int,
        pooling: str = "last",
    ) -> None:
        self.config = config
        self.port = port
        self.pooling = pooling

        self._server = LlamaServerProcess(
            name=f"{config.name}-embed",
            port=port,
            model_path=config.model_path,
            extra_args=self._build_args(),
            request_timeout=180.0,
        )

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def base_url(self) -> str:
        return self._server.base_url

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def dimension(self) -> int:
        return self.config.dimension

    @property
    def ready(self) -> bool:
        return self._server.ready

    def _build_args(self) -> list[str]:
        """构造 llama-server 参数（不含可执行文件本身）。"""
        cfg = self.config

        args = [
            "-m", str(cfg.model_path),
            "--embedding",
            "--pooling", self.pooling,
            # 用**收敛后的**上下文长度，而不是模型上限：
            # 32768 会让 llama.cpp 分配一个巨大且不断颠簸的 prompt cache
            # （实测 3200 次缓存驱逐）。chunk 最大 1500 字符，8192 足够。
            "-c", str(LLAMA_CONFIG.embedding_context_size),
            "-ngl", str(cfg.gpu_layers),
            "-t", str(cfg.threads),
            # -b 是 llama.cpp 的**逻辑批**（prompt 处理粒度），不是请求批大小。
            # 用 LLAMA_CONFIG.batch_size（2048）；误用 32 会让吞吐掉一个数量级。
            "-b", str(LLAMA_CONFIG.batch_size),
            "-ub", str(LLAMA_CONFIG.micro_batch_size),
            # 单 slot：顺序批处理不需要多 slot，能大幅缩小缓存占用
            "-np", str(LLAMA_CONFIG.embedding_slots),
            "--host", "127.0.0.1",
            "--port", str(self.port),
        ]

        if cfg.mmproj_path is not None:
            args += ["--mmproj", str(cfg.mmproj_path)]

        if LLAMA_CONFIG.flash_attention:
            # 较新版本 llama.cpp 中 --flash-attn 需要显式取值
            args += ["--flash-attn", "on"]

        if LLAMA_CONFIG.use_mlock:
            args += ["--mlock"]

        return args

    # ------------------------------------------------------------------
    # 启动 / 停止
    # ------------------------------------------------------------------

    def start(self, timeout: float = 600.0) -> None:
        self._server.start(timeout=timeout)

    def stop(self) -> None:
        self._server.stop()

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    def embed(
        self,
        texts: list[str],
        batch_size: int | None = None,
    ) -> list[list[float]]:
        """返回与输入等长的向量列表。"""
        if not texts:
            return []

        self.start()

        # 客户端每请求提交多少条（与 llama.cpp 的 -b 无关）
        size = batch_size or self.config.batch_size or LLAMA_CONFIG.embedding_batch_size
        vectors: list[list[float]] = []

        for start_index in range(0, len(texts), size):
            batch = texts[start_index : start_index + size]

            data = self._embed_batch(batch, batch_index=start_index)
            data.sort(key=lambda item: item.get("index", 0))

            for item in data:
                vectors.append(list(item["embedding"]))

        if vectors and len(vectors[0]) != self.config.dimension:
            print(
                f"[embedding] 警告：{self.name} 实际输出维度 "
                f"{len(vectors[0])}，config 声明 {self.config.dimension}。"
                f"请更新 config.py。"
            )

        return vectors

    def _embed_batch(
        self,
        batch: list[str],
        batch_index: int = 0,
    ) -> list[dict]:
        """发送单个 batch，带瞬时错误重试与诊断信息。"""
        client = self._server.client
        last_error: Exception | None = None

        for attempt in range(3):
            try:
                response = client.post(
                    f"{self.base_url}/v1/embeddings",
                    json={"input": batch, "model": self.name},
                )

                if response.status_code == 200:
                    return response.json()["data"]

                # 服务端瞬时过载 / 排队：退避重试
                if response.status_code >= 500 and attempt < 2:
                    time.sleep(1.0 * (attempt + 1))
                    last_error = RuntimeError(
                        f"HTTP {response.status_code} "
                        f"(batch={batch_index}, attempt={attempt + 1})"
                    )
                    continue

                body = response.text[:800]
                raise RuntimeError(
                    f"embedding 请求失败 HTTP {response.status_code} "
                    f"(batch={batch_index}): {body}"
                )

            except RuntimeError:
                raise
            except Exception as exc:  # noqa: BLE001
                if attempt >= 2:
                    raise
                last_error = exc
                time.sleep(1.0 * (attempt + 1))

        raise last_error or RuntimeError("embedding 请求失败")

    def embed_one(self, text: str) -> list[float]:
        """单条文本向量化。"""
        return self.embed([text])[0]


__all__ = ["LlamaEmbeddingServer"]
