"""生成式 LLM 的公共类型与接口定义。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator, Protocol, runtime_checkable


@dataclass
class ChatMessage:
    """一条对话消息。

    ``content`` 既可以是纯文本，也可以是 OpenAI 风格的内容片段数组：

        [{"type": "text", "text": "描述这张图"},
         {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}]

    后者用于多模态（视觉）模型的图片输入。
    """

    role: str       # system | user | assistant
    content: str | list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {"role": self.role, "content": self.content}

    @property
    def text(self) -> str:
        """取出纯文本部分（多模态时拼接所有 text 片段）。"""
        if isinstance(self.content, str):
            return self.content

        return "".join(
            part.get("text", "")
            for part in self.content
            if isinstance(part, dict) and part.get("type") == "text"
        )


@dataclass
class ChatDelta:
    """流式生成的一个增量片段。

    thinking 模型（如 gemma-4 / Qwen3.5 / GLM-4.7）会先吐出 ``reasoning``
    再吐 ``content``。两者必须分开，否则前端会把思维链当成答案显示。
    """

    content: str = ""
    reasoning: str = ""
    finished: bool = False
    finish_reason: str | None = None

    # 流式响应的 usage 通常在最后一个 chunk 才给（且需要显式请求
    # stream_options.include_usage）。放在这里随流一起返回，
    # 调用方就能把用量累积下来，而不是用完即丢。
    usage: "ChatUsage | None" = None

    @property
    def is_empty(self) -> bool:
        return (
            not self.content
            and not self.reasoning
            and not self.finished
            and self.usage is None
        )


@dataclass
class ChatUsage:
    """token 用量。"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass
class ChatReply:
    """一次完整（非流式）生成的结果。"""

    content: str = ""
    reasoning: str = ""
    usage: ChatUsage = field(default_factory=ChatUsage)
    model: str = ""
    finish_reason: str | None = None

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "reasoning": self.reasoning,
            "usage": self.usage.to_dict(),
            "model": self.model,
            "finish_reason": self.finish_reason,
        }


class LLMError(RuntimeError):
    """LLM 调用相关的统一异常。"""


class LLMUnavailable(LLMError):
    """没有可用的生成模型 / 服务，问答应降级为纯检索。"""


@runtime_checkable
class ChatProvider(Protocol):
    """生成式模型提供方接口。"""

    @property
    def name(self) -> str:
        """用于展示的模型标识。"""

    def available(self) -> tuple[bool, str]:
        """返回 ``(是否可用, 原因说明)``。"""

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> ChatReply:
        """非流式生成。"""

    def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> Iterator[ChatDelta]:
        """流式生成。"""

    def close(self) -> None:
        """释放资源。"""


__all__ = [
    "ChatMessage",
    "ChatDelta",
    "ChatUsage",
    "ChatReply",
    "ChatProvider",
    "LLMError",
    "LLMUnavailable",
]
