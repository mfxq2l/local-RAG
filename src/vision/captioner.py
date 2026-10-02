"""视觉模型：把图片转成**语义描述**。

为什么必须有这一步
------------------
实测结论（见 README「多模态」一节）：

* llama.cpp 的 ``/v1/embeddings`` **不接受图片**。传入图片字段会被
  **静默忽略** —— 请求返回 200 和一个正常的文本向量，换一张图向量完全不变。
  也就是说 WeMM 的 mmproj 无法用于生成图片向量。
* 环境里没有 PyTorch / CLIP，无法绕过 llama.cpp 直接跑原始权重。

因此真实可行的多模态路径是：

    图片 → 视觉模型读懂（OCR + 图形 + 主题）→ 文本描述 → 文本 embedding

本模块负责其中的「视觉模型读懂」环节，产出**富含语义**的中文描述。
这比旧实现的「文件名 + 尺寸 + 色彩模式」是质变：旧描述里没有任何
可供检索的语义内容。
"""

from __future__ import annotations

import base64
import io
import threading
import time
from pathlib import Path

from src.config import (
    LLAMA_CONFIG,
    VISION_CONFIG,
    VisionConfig,
)
from src.llama_server import LlamaServerProcess
from src.llm.base import ChatMessage, LLMError, LLMUnavailable
from src.llm.openai_compat import OpenAICompatChat


# 送入视觉模型前的最长边（像素）。
# 图片过大会产生大量 image token，既慢又可能超出上下文。
_MAX_EDGE = 1024


def prepare_data_url(
    source: str | Path | bytes,
    *,
    max_edge: int = _MAX_EDGE,
) -> str:
    """把图片读成 ``data:image/png;base64,...``。

    会自动按最长边缩放，避免超大图撑爆上下文。

    Raises:
        ValueError: 图片无法识别。
    """
    if isinstance(source, bytes):
        raw = source
    else:
        raw = Path(source).read_bytes()

    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise LLMError("缺少 Pillow，无法处理图片") from exc

    try:
        with Image.open(io.BytesIO(raw)) as img:
            img = img.convert("RGB")

            width, height = img.size
            longest = max(width, height)

            if longest > max_edge:
                scale = max_edge / longest
                img = img.resize(
                    (max(1, int(width * scale)), max(1, int(height * scale))),
                    Image.LANCZOS,
                )

            buffer = io.BytesIO()
            img.save(buffer, format="PNG", optimize=True)
            encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"无法识别图片: {exc}") from exc

    return f"data:image/png;base64,{encoded}"


class VisionCaptioner:
    """用本地视觉模型（主模型 + mmproj）为图片生成描述。"""

    _lock = threading.Lock()

    def __init__(self, config: VisionConfig | None = None) -> None:
        self.config = config or VISION_CONFIG

        self._server: LlamaServerProcess | None = None
        self._client: OpenAICompatChat | None = None
        self._resolve_error: str | None = None

        # 为 True 表示复用了对话服务，close() 时不应把它停掉
        self._reused_chat_server = False

        self.model_path, self.mmproj_path = self._resolve_paths()

    # ------------------------------------------------------------------
    # 模型解析
    # ------------------------------------------------------------------

    def _resolve_paths(self) -> tuple[Path | None, Path | None]:
        """确定视觉模型与投影器路径。

        配置显式指定优先；否则在模型清单里自动配对
        （``mmproj-<主模型>-<量化>.gguf`` ↔ ``<主模型>-...gguf``）。
        """
        if self.config.model_path and self.config.mmproj_path:
            return self.config.model_path, self.config.mmproj_path

        try:
            from src.llm.catalog import vision_pairs

            pairs = vision_pairs()

            if pairs:
                main, projector = pairs[0]

                return (
                    self.config.model_path or Path(main.path),
                    self.config.mmproj_path or Path(projector.path),
                )
        except Exception as exc:  # noqa: BLE001
            self._resolve_error = f"自动配对视觉模型失败: {exc}"

        return self.config.model_path, self.config.mmproj_path

    # ------------------------------------------------------------------
    # 状态
    # ------------------------------------------------------------------

    def available(self) -> tuple[bool, str]:
        if not self.config.enabled:
            return False, "视觉模型已禁用（RAG_VISION_ENABLED=false）"

        if self._resolve_error:
            return False, self._resolve_error

        if self.model_path is None:
            return (
                False,
                "未找到视觉模型。请把「主模型 + 对应 mmproj」放进 "
                "models/LLM/，或设置 RAG_VISION_MODEL / RAG_VISION_MMPROJ。",
            )

        if not self.model_path.exists():
            return False, f"视觉模型不存在: {self.model_path}"

        if self.mmproj_path is None:
            return (
                False,
                "缺少视觉投影器（mmproj）。图片理解必须要有它。",
            )

        if not self.mmproj_path.exists():
            return False, f"投影器不存在: {self.mmproj_path}"

        return True, "ok"

    def status(self) -> dict:
        ok, reason = self.available()

        return {
            "available": ok,
            "reason": reason,
            "model": self.model_path.name if self.model_path else "",
            "model_path": str(self.model_path) if self.model_path else "",
            "mmproj": self.mmproj_path.name if self.mmproj_path else "",
            "mmproj_path": str(self.mmproj_path) if self.mmproj_path else "",
            "port": self.config.port,
            "started": self._client is not None,
            "reused_chat_server": self._reused_chat_server,
        }

    # ------------------------------------------------------------------
    # 启动
    # ------------------------------------------------------------------

    def _build_args(self) -> list[str]:
        cfg = self.config

        assert self.model_path is not None
        assert self.mmproj_path is not None

        args = [
            "-m", str(self.model_path),
            "--mmproj", str(self.mmproj_path),
            "--host", "127.0.0.1",
            "--port", str(cfg.port),
            "-c", str(cfg.context_size),
            "-ngl", str(cfg.gpu_layers),
            "-t", str(cfg.threads),
            "-b", str(cfg.batch_size),
            "-np", "1",
            "--reasoning-format", "deepseek",
        ]

        if LLAMA_CONFIG.flash_attention:
            args += ["--flash-attn", "on"]

        return args

    def _ensure_client(self) -> OpenAICompatChat:
        if self._client is not None:
            return self._client

        # --------------------------------------------------------------
        # 优先复用已就绪的对话服务
        #
        # gemma-4-E2B 同时是对话模型和视觉模型，如果对话服务已经带着
        # mmproj 起了，就没必要再为读图加载第二份（约 3GB 显存）。
        # --------------------------------------------------------------
        reused = self._try_reuse_chat_server()

        if reused is not None:
            self._client = reused
            return reused

        ok, reason = self.available()
        if not ok:
            raise LLMUnavailable(reason)

        assert self.model_path is not None

        server = LlamaServerProcess(
            name=f"{self.model_path.stem}-vision",
            port=self.config.port,
            model_path=self.model_path,
            extra_args=self._build_args(),
            request_timeout=self.config.request_timeout,
        )

        server.start()
        self._server = server

        self._client = OpenAICompatChat(
            base_url=server.base_url,
            model=str(self.model_path),
            timeout=self.config.request_timeout,
            label=self.model_path.stem,
        )

        return self._client

    def _try_reuse_chat_server(self) -> OpenAICompatChat | None:
        """若对话服务已带 mmproj 就绪且模型一致，直接复用。"""
        try:
            from src.llm import active_vision_endpoint

            endpoint = active_vision_endpoint()
        except Exception:  # noqa: BLE001
            return None

        if endpoint is None:
            return None

        base_url, model = endpoint

        # 必须是同一个模型 —— 不同模型的 mmproj 不通用
        if self.model_path is None:
            return None

        try:
            if Path(model).resolve() != Path(self.model_path).resolve():
                return None
        except Exception:  # noqa: BLE001
            return None

        self._reused_chat_server = True

        return OpenAICompatChat(
            base_url=base_url,
            model=str(self.model_path),
            timeout=self.config.request_timeout,
            label=f"{self.model_path.stem}(复用对话服务)",
        )

    # ------------------------------------------------------------------
    # 描述生成
    # ------------------------------------------------------------------

    def caption(
        self,
        source: str | Path | bytes,
        prompt: str | None = None,
        *,
        max_tokens: int | None = None,
    ) -> str:
        """为一张图片生成语义描述。

        Args:
            source: 图片路径或原始字节。
            prompt: 覆盖默认提示词。
            max_tokens: 覆盖默认生成长度。

        Raises:
            LLMUnavailable: 视觉模型不可用。
            LLMError: 调用失败。
        """
        data_url = prepare_data_url(source)
        client = self._ensure_client()

        message = ChatMessage(
            role="user",
            content=[
                {"type": "text", "text": prompt or self.config.prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        )

        reply = client.chat(
            [message],
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=self.config.temperature,
            # 描述任务不需要思考过程，关掉可显著提速
            thinking=False,
        )

        text = (reply.content or "").strip()

        if not text:
            raise LLMError("视觉模型返回了空描述")

        return text

    def caption_many(
        self,
        sources: list[str | Path],
        *,
        prompt: str | None = None,
        on_progress=None,
    ) -> list[str]:
        """批量描述，返回与输入等长的列表（失败项为空字符串）。"""
        results: list[str] = []

        for index, source in enumerate(sources, 1):
            name = (
                Path(source).name
                if not isinstance(source, bytes)
                else f"bytes[{len(source)}]"
            )

            started = time.perf_counter()

            try:
                text = self.caption(source, prompt=prompt)
                elapsed = time.perf_counter() - started

                if on_progress is not None:
                    on_progress(index, len(sources), name, text, elapsed)

                results.append(text)

            except Exception as exc:  # noqa: BLE001
                if on_progress is not None:
                    on_progress(
                        index, len(sources), name, f"[失败] {exc}",
                        time.perf_counter() - started,
                    )
                results.append("")

        return results

    # ------------------------------------------------------------------
    # 资源
    # ------------------------------------------------------------------

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

        # 复用对话服务时只断开客户端，**不要**停掉那个服务
        if self._server is not None and not self._reused_chat_server:
            self._server.stop()
            self._server = None

        self._server = None
        self._reused_chat_server = False


__all__ = ["VisionCaptioner", "prepare_data_url"]
