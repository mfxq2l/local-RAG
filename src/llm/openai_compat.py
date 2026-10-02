"""OpenAI 兼容的 /v1/chat/completions 客户端。

llama-server、Ollama、LM Studio、vLLM 以及云端 API 都暴露这套接口，
因此本模块同时服务于「本地 llama.cpp」和「外部端点」两种 provider。

两个必须处理的现实细节：

1. **thinking 模型**：gemma-4 / Qwen3.5 / GLM-4.7 等会先输出
   ``reasoning_content`` 再输出 ``content``。必须分开收集，否则思维链会被
   当作答案展示。

2. **``chat_template_kwargs`` 兼容性**：这是唯一有效的**请求级**思考开关
   （``{"enable_thinking": false}``）。实测同题：开启思考 5.70s / 1363 字符，
   关闭后 **0.73s / 0 字符且答案依然正确**（约 7.8 倍加速）。

   注意 ``reasoning_budget`` 无论放在顶层还是 chat_template_kwargs 里
   都**不会生效**（实测仍产生 1500+ 字符思考），不要用它。

   部分服务端可能不认识该字段并返回 400，因此首次 400 时自动去掉重试。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import httpx

from src.llm.base import (
    ChatDelta,
    ChatMessage,
    ChatReply,
    ChatUsage,
    LLMError,
)


class OpenAICompatChat:
    """任意 OpenAI 兼容 chat 端点的客户端。"""

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        api_key: str = "",
        timeout: float = 300.0,
        label: str | None = None,
        unavailable_reason: str = "",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self._label = label or model

        # 已知不可用的原因（例如云端配置不完整）。
        # 设置后 available() 直接返回它，避免去连接一个用户并未选择的地址。
        self._unavailable_reason = unavailable_reason

        self._client = httpx.Client(timeout=timeout, trust_env=False)

        # 服务端是否接受 chat_template_kwargs（首次 400 后置为 False）
        self._thinking_kwarg_ok = True

    # ------------------------------------------------------------------
    # 基础
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._label

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _build_payload(
        self,
        messages: list[ChatMessage],
        *,
        stream: bool,
        max_tokens: int | None,
        temperature: float | None,
        top_p: float | None,
        repeat_penalty: float | None = None,
        thinking: bool | None = None,
        use_thinking_kwarg: bool = True,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": stream,
        }

        # 流式默认不返回 usage，必须显式请求。
        # 服务端会在最后补一个 choices 为空、只含 usage 的 chunk。
        if stream:
            payload["stream_options"] = {"include_usage": True}

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if repeat_penalty is not None:
            payload["repeat_penalty"] = repeat_penalty

        # 请求级思考开关（thinking 为 None 时交给服务端按 --reasoning 决定）
        if thinking is not None and use_thinking_kwarg:
            payload["chat_template_kwargs"] = {
                "enable_thinking": bool(thinking)
            }

        return payload

    def available(self) -> tuple[bool, str]:
        """探测端点与模型是否可用。"""
        if self._unavailable_reason:
            return False, self._unavailable_reason

        try:
            response = self._client.get(self._url("/v1/models"))
        except Exception as exc:  # noqa: BLE001
            return False, f"无法连接 {self.base_url}: {exc}"

        if response.status_code != 200:
            return False, f"HTTP {response.status_code} @ /v1/models"

        try:
            data = response.json().get("data") or []
        except Exception:  # noqa: BLE001
            return True, "ok"

        if not data:
            return True, "ok"

        ids = {str(item.get("id", "")) for item in data}

        # llama-server 返回的 id 是模型文件路径，做一次宽松匹配
        if self.model in ids:
            return True, "ok"

        for candidate in ids:
            if self.model and (
                self.model in candidate or candidate in self.model
            ):
                return True, "ok"

        return True, f"端点可用（模型列表中未见 {self.model}，将由服务端自行解析）"

    # ------------------------------------------------------------------
    # 非流式
    # ------------------------------------------------------------------

    def chat(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        repeat_penalty: float | None = None,
        thinking: bool | None = None,
    ) -> ChatReply:
        use_kwarg = thinking is not None and self._thinking_kwarg_ok

        response = self._post(
            payload=self._build_payload(
                messages,
                stream=False,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                repeat_penalty=repeat_penalty,
                thinking=thinking,
                use_thinking_kwarg=use_kwarg,
            ),
            allow_kwarg_retry=use_kwarg,
        )

        try:
            data = response.json()
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"响应不是合法 JSON: {response.text[:400]}") from exc

        choices = data.get("choices") or []
        if not choices:
            raise LLMError(f"响应中没有 choices: {json.dumps(data)[:400]}")

        message = choices[0].get("message") or {}
        content = message.get("content") or ""
        reasoning = message.get("reasoning_content") or ""

        # 思考没结束就截断时 content 可能为空，退回思维链以免界面空白
        if not content and reasoning:
            content = reasoning

        usage_raw = data.get("usage") or {}

        return ChatReply(
            content=content,
            reasoning=reasoning,
            usage=ChatUsage(
                prompt_tokens=int(usage_raw.get("prompt_tokens") or 0),
                completion_tokens=int(usage_raw.get("completion_tokens") or 0),
                total_tokens=int(usage_raw.get("total_tokens") or 0),
            ),
            model=self._display_model(data.get("model")),
            finish_reason=choices[0].get("finish_reason"),
        )

    def _display_model(self, raw: Any) -> str:
        """规范化展示用的模型名。

        llama-server 会把模型**文件路径**作为 ``model`` 返回，
        直接展示给用户很难看，这里截成文件名。
        """
        name = str(raw or self.model)

        if "/" in name or "\\" in name:
            return Path(name).name

        return name

    # ------------------------------------------------------------------
    # 流式
    # ------------------------------------------------------------------

    def stream(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        repeat_penalty: float | None = None,
        thinking: bool | None = None,
    ) -> Iterator[ChatDelta]:
        use_kwarg = thinking is not None and self._thinking_kwarg_ok

        payload = self._build_payload(
            messages,
            stream=True,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            thinking=thinking,
            use_thinking_kwarg=use_kwarg,
        )

        try:
            with self._client.stream(
                "POST",
                self._url("/v1/chat/completions"),
                json=payload,
                headers=self._headers(),
            ) as response:
                if response.status_code == 400 and use_kwarg:
                    # 服务端不认识 chat_template_kwargs，去掉后重试
                    self._thinking_kwarg_ok = False
                    response.read()
                    yield from self.stream(
                        messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                        repeat_penalty=repeat_penalty,
                        thinking=thinking,
                    )
                    return

                if response.status_code != 200:
                    body = response.read().decode("utf-8", errors="replace")
                    raise LLMError(
                        f"流式请求失败 HTTP {response.status_code}: {body[:400]}"
                    )

                yield from self._iter_sse(response)

        except LLMError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"流式请求异常: {exc}") from exc

    def _iter_sse(self, response: httpx.Response) -> Iterator[ChatDelta]:
        """解析 OpenAI 风格的 SSE 流。"""
        for line in response.iter_lines():
            if not line:
                continue

            line = line.strip()

            if not line.startswith("data:"):
                continue

            data = line[len("data:") :].strip()

            if data == "[DONE]":
                yield ChatDelta(finished=True)
                return

            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                continue

            choices = chunk.get("choices") or []

            # usage 通常出现在最后一个 chunk —— 那个 chunk 的 choices 是空的。
            # 旧实现在这里 `if not choices: continue`，正好把用量丢掉了。
            usage_raw = chunk.get("usage")
            if usage_raw:
                yield ChatDelta(
                    finished=not choices,
                    usage=ChatUsage(
                        prompt_tokens=int(
                            usage_raw.get("prompt_tokens") or 0
                        ),
                        completion_tokens=int(
                            usage_raw.get("completion_tokens") or 0
                        ),
                        total_tokens=int(usage_raw.get("total_tokens") or 0),
                    ),
                )

            if not choices:
                continue

            choice = choices[0]
            delta = choice.get("delta") or {}

            content = delta.get("content") or ""
            reasoning = delta.get("reasoning_content") or ""
            finish_reason = choice.get("finish_reason")

            if content or reasoning or finish_reason:
                yield ChatDelta(
                    content=content,
                    reasoning=reasoning,
                    finish_reason=finish_reason,
                )

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    def _post(
        self,
        payload: dict[str, Any],
        *,
        allow_kwarg_retry: bool,
    ) -> httpx.Response:
        """发送请求；若不支持 chat_template_kwargs 则去掉后重试一次。"""
        response = self._client.post(
            self._url("/v1/chat/completions"),
            json=payload,
            headers=self._headers(),
        )

        if response.status_code == 400 and allow_kwarg_retry:
            self._thinking_kwarg_ok = False
            payload = {
                k: v for k, v in payload.items() if k != "chat_template_kwargs"
            }
            response = self._client.post(
                self._url("/v1/chat/completions"),
                json=payload,
                headers=self._headers(),
            )

        if response.status_code != 200:
            raise LLMError(
                f"请求失败 HTTP {response.status_code}: {response.text[:400]}"
            )

        return response

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:  # noqa: BLE001
            pass


__all__ = ["OpenAICompatChat"]
