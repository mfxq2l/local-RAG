"""本地 llama.cpp 生成式模型 provider。

拉起一个 ``llama-server.exe`` 作为 chat 服务，然后复用
:class:`src.llm.openai_compat.OpenAICompatChat` 调用它的 OpenAI 兼容接口。

显存自适应
----------
RTX 3070 只有 8GB，而 embedding 模型常驻约 2.4GB。若 chat 模型按 ``-ngl -1``
全量 offload 时显存不足，llama-server 会启动失败。这里捕获该情况并自动退回
CPU 推理（``-ngl 0``），保证功能可用而不是直接报错。
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from src.config import (
    LLAMA_CONFIG,
    LLM_CONFIG,
    LlmConfig,
    discover_llm_model,
)
from src.llama_server import LlamaServerProcess
from src.llm.base import (
    ChatDelta,
    ChatMessage,
    ChatReply,
    LLMError,
    LLMUnavailable,
)
from src.llm.openai_compat import OpenAICompatChat


class LlamaCppChat:
    """在本机运行 gguf 模型的 chat provider。"""

    def __init__(
        self,
        config: LlmConfig | None = None,
        model: str | None = None,
    ) -> None:
        """
        Args:
            config: LLM 配置。
            model: 显式指定模型（文件名片段 / 清单序号 / 完整路径）。
                ``None`` 时按配置自动发现（含 ``data/llm_selection.json``
                里的持久选择）。
        """
        self.config = config or LLM_CONFIG
        self.model_query = model

        # 解析失败不直接抛，交由 available() 汇报，
        # 这样 /api/llm/status 能给出可读原因而不是 500
        self._resolve_error: str | None = None

        try:
            self.model_path: Path | None = self._resolve_model(model, self.config)
        except LLMUnavailable as exc:
            self.model_path = None
            self._resolve_error = str(exc)

        self._server: LlamaServerProcess | None = None
        self._client: OpenAICompatChat | None = None

        # 该模型配对的视觉投影器（mmproj）。挂了它之后同一个服务
        # 既能对话又能读图，不必再为视觉单独加载一份模型。
        self.mmproj_path: Path | None = self._resolve_projector()

        # 显存不足退回 CPU 后置为 True，仅用于展示
        self._cpu_fallback = False

    def _resolve_projector(self) -> Path | None:
        """查找并校验配对的 mmproj。"""
        if not self.config.load_mmproj or self.model_path is None:
            return None

        try:
            from src.llm.catalog import projector_for

            projector = projector_for(self.model_path)
        except Exception:  # noqa: BLE001
            return None

        if projector is not None and projector.exists():
            return projector

        return None

    @property
    def vision_enabled(self) -> bool:
        """该对话服务是否同时具备看图能力。"""
        return self.mmproj_path is not None and self._client is not None

    def vision_endpoint(self) -> tuple[str, str] | None:
        """若已就绪且带 mmproj，返回 ``(base_url, model)`` 供视觉复用。"""
        if not self.vision_enabled or self._server is None:
            return None

        assert self.model_path is not None

        return self._server.base_url, str(self.model_path)

    @staticmethod
    def _resolve_model(model: str | None, config: LlmConfig) -> Path | None:
        """解析模型路径。

        显式指定时走清单查找（因此受 ``RAG_LLM_EXCLUDE`` 约束，
        被排除的模型即使写名字也找不到）。
        """
        if not model:
            return discover_llm_model(config)

        # 延迟导入，避免 config / llm 之间的循环依赖
        from src.llm.catalog import find_model

        entry = find_model(model)

        if entry is None:
            raise LLMUnavailable(
                f"找不到模型 {model!r}。"
                f"用 `run.py models` 查看可用清单；"
                f"若该模型被 RAG_LLM_EXCLUDE 排除，则不会被选中。"
            )

        return Path(entry.path)

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        if self.model_path is None:
            return "llama.cpp(未配置模型)"
        if self._cpu_fallback:
            return f"{self.model_path.stem}(CPU)"
        return self.model_path.stem

    @property
    def model_file(self) -> str:
        return self.model_path.name if self.model_path else ""

    def available(self) -> tuple[bool, str]:
        if not self.config.enabled:
            return False, "生成式问答已在配置中禁用（RAG_LLM_ENABLED=false）"

        if self._resolve_error:
            return False, self._resolve_error

        if self.model_path is None:
            searched = ", ".join(str(d) for d in self.config.model_dirs)
            return (
                False,
                "未找到可用的 gguf chat 模型。请把模型放到 "
                f"models/LLM/ 或这些目录之一：{searched}，"
                "或设置环境变量 RAG_LLM_MODEL 指向模型文件。",
            )

        if not self.model_path.exists():
            return False, f"模型文件不存在: {self.model_path}"

        return True, "ok"

    def status(self) -> dict:
        """供 /api/config、/api/health 展示的状态。"""
        ok, reason = self.available()
        return {
            "provider": "llama_cpp",
            "available": ok,
            "reason": reason,
            "model": self.model_file,
            "model_path": str(self.model_path) if self.model_path else "",
            "port": self.config.port,
            "context_size": self.config.context_size,
            "gpu_layers": self.config.gpu_layers,
            "reasoning": self.config.reasoning,
            "mode": self.config.default_mode,
            "vision": self.mmproj_path.name if self.mmproj_path else "",
            "cpu_fallback": self._cpu_fallback,
            "started": self._client is not None,
        }

    # ------------------------------------------------------------------
    # 启动
    # ------------------------------------------------------------------

    def _build_args(self, gpu_layers: int) -> list[str]:
        cfg = self.config

        assert self.model_path is not None

        args = [
            "-m", str(self.model_path),
            "--host", "127.0.0.1",
            "--port", str(cfg.port),
            "-c", str(cfg.context_size),
            "-ngl", str(gpu_layers),
            "-t", str(cfg.threads),
            "-b", str(cfg.batch_size),
            # 单槽位：避免为并发槽位预留多份 KV cache，省显存
            "-np", "1",
            # 让思考内容进入 message.reasoning_content，而不是混进正文
            "--reasoning-format", "deepseek",
            "--reasoning", cfg.reasoning,
        ]

        if LLAMA_CONFIG.flash_attention:
            args += ["--flash-attn", "on"]

        # 挂上视觉投影器：同一个服务既能对话又能读图
        if self.mmproj_path is not None:
            args += ["--mmproj", str(self.mmproj_path)]

        return args

    def _launch(self, gpu_layers: int, name_suffix: str = "") -> OpenAICompatChat:
        assert self.model_path is not None

        server = LlamaServerProcess(
            name=f"{self.model_path.stem}{name_suffix}",
            port=self.config.port,
            model_path=self.model_path,
            extra_args=self._build_args(gpu_layers),
            request_timeout=self.config.request_timeout,
        )

        server.start()

        self._server = server

        return OpenAICompatChat(
            base_url=server.base_url,
            model=str(self.model_path),
            api_key=self.config.api_key,
            timeout=self.config.request_timeout,
            label=self.model_path.stem,
        )

    def _ensure_client(self) -> OpenAICompatChat:
        """确保 chat 服务已就绪，返回客户端。"""
        if self._client is not None:
            return self._client

        ok, reason = self.available()
        if not ok:
            raise LLMUnavailable(reason)

        try:
            self._client = self._launch(self.config.gpu_layers)
        except Exception as exc:  # noqa: BLE001
            # GPU 显存不足（或 CUDA 不可用）时退回 CPU
            if self.config.gpu_layers != 0:
                print(
                    f"[llm] GPU 启动失败，尝试退回 CPU 推理：{exc}"
                )
                self._cpu_fallback = True
                self._client = self._launch(0, name_suffix="-cpu")
            else:
                raise LLMError(f"启动本地 LLM 失败: {exc}") from exc

        return self._client

    # ------------------------------------------------------------------
    # 生成
    # ------------------------------------------------------------------

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        thinking: bool | None = None,
    ) -> ChatReply:
        client = self._ensure_client()

        return client.chat(
            messages,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=(
                self.config.temperature if temperature is None else temperature
            ),
            top_p=self.config.top_p if top_p is None else top_p,
            repeat_penalty=self.config.repeat_penalty,
            thinking=thinking,
        )

    def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        thinking: bool | None = None,
    ) -> Iterator[ChatDelta]:
        client = self._ensure_client()

        yield from client.stream(
            messages,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=(
                self.config.temperature if temperature is None else temperature
            ),
            top_p=self.config.top_p if top_p is None else top_p,
            repeat_penalty=self.config.repeat_penalty,
            thinking=thinking,
        )

    # ------------------------------------------------------------------
    # 资源
    # ------------------------------------------------------------------

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

        if self._server is not None:
            self._server.stop()
            self._server = None

        self._cpu_fallback = False


__all__ = ["LlamaCppChat"]
