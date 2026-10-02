"""多轮对话编排。

与单轮问答（:mod:`src.rag.answer`）的关键差别
--------------------------------------------
单轮只做「检索 → 生成」。多轮多了一步，而且这一步是**成败关键**：

    用户追问「那第二点呢」
        ↓  condense（用历史把它改写成独立问题）
    「Nmap -sT 全连接扫描的特点是什么」
        ↓  用改写后的 query 去检索
    ...

为什么必须改写：向量检索与 BM25 都只看 query 的字面内容。
「那第二点呢」「再详细说说」这类追问**本身不含任何可检索语义**，
直接拿去检索只会召回无关内容。改写后才有意义。

生成阶段则把历史消息一并交给模型，它才能理解上下文。
"""

from __future__ import annotations

import time
from typing import Any, Iterator

from src.llm import ChatMessage, LLMUnavailable, get_llm
from src.rag.context import build_citations
from src.rag.conversation import Conversation, Turn
from src.rag.modes import AnswerMode, resolve_mode
from src.rag.prompt import (
    CONDENSE_PROMPT,
    DIRECT_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_direct_prompt,
    build_followup_prompt,
    build_image_prompt,
)
from src.rag.router import needs_retrieval
from src.rag.search import RAGSearch
from src.usage import record_usage


def sanitize_text(text: str) -> str:
    """去掉无法再编码的孤立代理字符。

    来源：Windows 下从管道/控制台读入非 UTF-8 字节时，Python 可能产生
    ``\\udcXX`` 这类孤立代理码位。它们无法编码成 UTF-8，会让后续的 JSON
    请求（发给 embedding / LLM 服务）直接抛 UnicodeEncodeError，
    把整轮对话打断。这里在入口处统一清理。
    """
    if not text:
        return text

    try:
        return text.encode("utf-8", "replace").decode("utf-8")
    except Exception:  # noqa: BLE001
        return "".join(ch for ch in text if not (0xD800 <= ord(ch) <= 0xDFFF))


def condense_query(
    question: str,
    history: list[dict[str, str]],
    llm,
    *,
    enabled: bool = True,
) -> tuple[str, bool]:
    """把追问改写成独立可检索的查询。

    Args:
        question: 用户本轮原始问题。
        history: 历史消息（``role`` / ``content``）。
        llm: 生成模型 provider。
        enabled: 为 False 或没有历史时直接返回原问题。

    Returns:
        ``(用于检索的 query, 是否真的改写成了不同内容)``
        任何失败都退回原问题，绝不因为改写失败而中断对话。
    """
    original = sanitize_text((question or "").strip())

    if not enabled or not history or not original:
        return original, False

    # 只把历史里的「人话」给改写器，避免把长篇资料塞进去
    lines: list[str] = []
    for message in history[-6:]:
        role = "用户" if message.get("role") == "user" else "助手"
        content = (message.get("content") or "").strip().replace("\n", " ")
        if len(content) > 300:
            content = content[:300] + "…"
        lines.append(f"{role}：{content}")

    transcript = "\n".join(lines)

    try:
        reply = llm.chat(  # type: ignore[attr-defined]
            [
                ChatMessage("system", CONDENSE_PROMPT),
                ChatMessage(
                    "user",
                    f"【对话历史】\n{transcript}\n\n【最新问题】\n{original}\n\n"
                    f"请输出改写后的检索查询：",
                ),
            ],
            max_tokens=128,
            temperature=0.0,
            # 改写是纯转换任务，关掉思考能快很多
            thinking=False,
        )
        rewritten = (reply.content or "").strip()

        # 清理模型可能的客套或引号
        rewritten = rewritten.strip().strip("「」\"'“”").strip()
        rewritten = rewritten.splitlines()[0].strip() if rewritten else ""

        # 计入累计用量
        usage = getattr(reply, "usage", None)
        if usage is not None:
            record_usage(
                usage.to_dict(),
                model=getattr(llm, "name", ""),
                kind="condense",
            )

    except Exception:  # noqa: BLE001
        return original, False

    if not rewritten or len(rewritten) > 300:
        return original, False

    # 改写结果与原文几乎一致时，视为未改写
    if rewritten == original:
        return original, False

    return rewritten, True


def build_image_content(
    question: str,
    image: str | bytes | None,
) -> str | list[dict[str, Any]]:
    """构造用户消息内容；有图片时返回多模态片段数组。

    Args:
        question: 用户问题。
        image: 图片路径、原始字节，或已经是 ``data:`` URL 的字符串。
    """
    if not image:
        return question

    try:
        from src.vision import prepare_data_url

        if isinstance(image, str) and image.startswith("data:"):
            data_url = image
        else:
            data_url = prepare_data_url(image)
    except Exception:  # noqa: BLE001
        # 图片处理失败时退回纯文本，至少不中断对话
        return question

    return [
        {"type": "text", "text": question},
        {"type": "image_url", "image_url": {"url": data_url}},
    ]


class RAGChat:
    """多轮检索增强对话。"""

    def __init__(
        self,
        name: str | None = None,
        provider: str | None = None,
        llm_model: str | None = None,
        router: bool | None = None,
    ) -> None:
        from src.config import LLM_CONFIG

        self.searcher = RAGSearch(name)
        self.llm = get_llm(provider, model=llm_model)

        # 自适应检索：为 None 时取配置默认值
        self.router_enabled = (
            LLM_CONFIG.router_enabled if router is None else router
        )

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------

    def _model_name(self) -> str:
        return getattr(self.llm, "name", "unknown")

    def _build_messages(
        self,
        question: str,
        context: str,
        history: list[dict[str, str]],
        image: str | bytes | None = None,
        direct: bool = False,
    ) -> list[ChatMessage]:
        """拼装多轮消息：system → 历史 → 当前问题。

        Args:
            direct: 为 True 时**不注入参考资料**，当普通对话回答。
        """
        system = DIRECT_SYSTEM_PROMPT if direct else SYSTEM_PROMPT
        messages = [ChatMessage("system", system)]

        for message in history:
            role = str(message.get("role") or "user")
            content = str(message.get("content") or "")
            if role in ("user", "assistant") and content:
                messages.append(ChatMessage(role, content))

        if direct:
            prompt = build_direct_prompt(question)
        elif image:
            prompt = build_image_prompt(question, context)
        else:
            prompt = build_followup_prompt(question, context)

        messages.append(
            ChatMessage("user", build_image_content(prompt, image))
        )

        return messages

    # ------------------------------------------------------------------
    # 非流式
    # ------------------------------------------------------------------

    def chat(
        self,
        conversation: Conversation,
        question: str,
        *,
        top_k: int = 5,
        use_bm25: bool | None = None,
        use_reranker: bool | None = None,
        include_images: bool = True,
        use_web: bool | None = None,
        web_limit: int | None = None,
        web_fetch_pages: bool | None = None,
        mode: str | None = None,
        condense: bool = True,
        max_tokens: int | None = None,
        temperature: float | None = None,
        image: str | bytes | None = None,
    ) -> Turn:
        """完成一轮对话并返回该轮记录（调用方负责 append 到会话）。

        Args:
            image: 可选的图片（路径 / 字节 / data URL）。对话服务需已加载
                mmproj 才能读图；否则模型会把图片当成无关内容。
        """
        question = sanitize_text(question)
        started = time.perf_counter()
        answer_mode: AnswerMode = resolve_mode(mode)

        history = conversation.history()

        available, reason = self.llm.available()  # type: ignore[attr-defined]
        if not available:
            raise LLMUnavailable(reason)

        # 0) 自适应检索：先判断这次要不要查知识库
        need, route_reason = needs_retrieval(
            question, history, self.llm, enabled=self.router_enabled
        )

        if not need:
            # 普通对话，不检索
            reply = self.llm.chat(  # type: ignore[attr-defined]
                self._build_messages(
                    question, "", history, image=image, direct=True
                ),
                max_tokens=(
                    max_tokens
                    if max_tokens is not None
                    else answer_mode.max_tokens
                ),
                temperature=(
                    temperature
                    if temperature is not None
                    else answer_mode.temperature
                ),
                thinking=answer_mode.thinking,
            )

            if getattr(reply, "usage", None):
                record_usage(
                    reply.usage.to_dict(),
                    model=self._model_name(),
                    kind="chat",
                )

            return Turn(
                index=len(conversation.turns),
                question=question,
                answer=reply.content,
                reasoning=getattr(reply, "reasoning", "") or "",
                retrieval_query="",
                citations=[],
                results=[],
                context="",
                mode=answer_mode.name,
                model=getattr(reply, "model", "") or self._model_name(),
                usage=(
                    reply.usage.to_dict()
                    if getattr(reply, "usage", None)
                    else {}
                ),
                elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
                used_retrieval=False,
                route_reason=route_reason,
            )

        # 1) 追问改写（无历史时是空操作）
        retrieval_query, rewritten = condense_query(
            question, history, self.llm, enabled=condense
        )

        # 2) 检索
        retrieved = self.searcher.search(
            query=retrieval_query,
            top_k=top_k,
            use_bm25=use_bm25,
            use_reranker=use_reranker,
            include_images=include_images,
            use_web=use_web,
            web_limit=web_limit,
            web_fetch_pages=web_fetch_pages,
        )

        results = retrieved["results"]
        context = retrieved["context"]

        turn = Turn(
            index=len(conversation.turns),
            question=question,
            retrieval_query=retrieval_query,
            citations=build_citations(results),
            results=results,
            context=context,
            mode=answer_mode.name,
            model=self._model_name(),
            used_retrieval=True,
            route_reason=route_reason,
        )

        # 3) 生成
        if not results:
            # 检索没命中 —— 不硬拒答，改为直接回答（更自然，也更有用）
            try:
                reply = self.llm.chat(  # type: ignore[attr-defined]
                    self._build_messages(
                        question, "", history, image=image, direct=True
                    ),
                    max_tokens=(
                        max_tokens
                        if max_tokens is not None
                        else answer_mode.max_tokens
                    ),
                    temperature=(
                        temperature
                        if temperature is not None
                        else answer_mode.temperature
                    ),
                    thinking=answer_mode.thinking,
                )
                turn.answer = reply.content
                turn.reasoning = getattr(reply, "reasoning", "") or ""
                turn.usage = (
                    reply.usage.to_dict()
                    if getattr(reply, "usage", None)
                    else {}
                )
                if turn.usage:
                    record_usage(
                        turn.usage,
                        model=self._model_name(),
                        kind="chat",
                    )
            except Exception:  # noqa: BLE001
                turn.answer = "知识库中没有检索到相关内容，我也无法直接回答这个问题。"

            turn.used_retrieval = False
            turn.route_reason = "检索无命中，改为直接回答"
            turn.elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            return turn

        reply = self.llm.chat(  # type: ignore[attr-defined]
            self._build_messages(question, context, history, image=image),
            max_tokens=(
                max_tokens if max_tokens is not None else answer_mode.max_tokens
            ),
            temperature=(
                temperature
                if temperature is not None
                else answer_mode.temperature
            ),
            thinking=answer_mode.thinking,
        )

        turn.answer = reply.content
        turn.reasoning = getattr(reply, "reasoning", "") or ""
        turn.model = getattr(reply, "model", "") or self._model_name()
        turn.usage = reply.usage.to_dict() if getattr(reply, "usage", None) else {}
        turn.elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

        if turn.usage:
            record_usage(
                turn.usage, model=turn.model or self._model_name(), kind="chat"
            )

        if rewritten:
            turn.retrieval_query = retrieval_query

        return turn

    # ------------------------------------------------------------------
    # 流式
    # ------------------------------------------------------------------

    def stream_chat(
        self,
        conversation: Conversation,
        question: str,
        *,
        top_k: int = 5,
        use_bm25: bool | None = None,
        use_reranker: bool | None = None,
        include_images: bool = True,
        use_web: bool | None = None,
        web_limit: int | None = None,
        web_fetch_pages: bool | None = None,
        mode: str | None = None,
        condense: bool = True,
        max_tokens: int | None = None,
        temperature: float | None = None,
        image: str | bytes | None = None,
    ) -> Iterator[dict[str, Any]]:
        """流式完成一轮对话。

        事件类型与单轮问答一致，另外新增：

            {"type": "conversation", "conversation_id": ..., "turn": n}
            {"type": "condensed", "query": ..., "original": ...}

        调用方需要在收到 ``done`` 时把返回的内容写入会话 ——
        为此 ``done`` 事件里带上了完整的 ``turn`` 数据。
        """
        question = sanitize_text(question)
        started = time.perf_counter()

        try:
            answer_mode: AnswerMode = resolve_mode(mode)
        except ValueError as exc:
            yield {"type": "error", "message": str(exc)}
            return

        yield {
            "type": "conversation",
            "conversation_id": conversation.id,
            "turn": len(conversation.turns),
            "mode": answer_mode.name,
        }

        history = conversation.history()

        available, reason = self.llm.available()  # type: ignore[attr-defined]
        if not available:
            yield {"type": "error", "message": reason, "degraded": True}
            return

        # 0) 自适应检索
        if self.router_enabled:
            yield {
                "type": "status",
                "stage": "routing",
                "message": "正在判断是否需要查询知识库…",
            }

        need, route_reason = needs_retrieval(
            question, history, self.llm, enabled=self.router_enabled
        )

        yield {
            "type": "route",
            "needs_retrieval": need,
            "reason": route_reason,
        }

        if not need:
            yield {
                "type": "status",
                "stage": "generation",
                "message": "这是普通对话，直接回答…",
            }

            answer_parts: list[str] = []
            reasoning_parts: list[str] = []

            try:
                for delta in self.llm.stream(  # type: ignore[attr-defined]
                    self._build_messages(
                        question, "", history, image=image, direct=True
                    ),
                    max_tokens=(
                        max_tokens
                        if max_tokens is not None
                        else answer_mode.max_tokens
                    ),
                    temperature=(
                        temperature
                        if temperature is not None
                        else answer_mode.temperature
                    ),
                    thinking=answer_mode.thinking,
                ):
                    if delta.reasoning:
                        reasoning_parts.append(delta.reasoning)
                        yield {"type": "reasoning", "text": delta.reasoning}
                    if delta.content:
                        answer_parts.append(delta.content)
                        yield {"type": "token", "text": delta.content}

            except Exception as exc:  # noqa: BLE001
                yield {"type": "error", "message": f"生成失败：{exc}"}
                return

            yield {
                "type": "done",
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                "model": self._model_name(),
                "mode": answer_mode.name,
                "used_retrieval": False,
                "route_reason": route_reason,
                "turn": {
                    "question": question,
                    "answer": "".join(answer_parts),
                    "reasoning": "".join(reasoning_parts),
                    "retrieval_query": "",
                    "citations": [],
                    "results": [],
                    "context": "",
                    "mode": answer_mode.name,
                    "model": self._model_name(),
                    "elapsed_ms": round(
                        (time.perf_counter() - started) * 1000, 2
                    ),
                    "used_retrieval": False,
                    "route_reason": route_reason,
                },
            }
            return

        # 1) 追问改写
        if history and condense:
            yield {
                "type": "status",
                "stage": "condense",
                "message": "正在结合上下文理解问题…",
            }

        retrieval_query, rewritten = condense_query(
            question, history, self.llm, enabled=condense
        )

        if rewritten:
            yield {
                "type": "condensed",
                "original": question,
                "query": retrieval_query,
            }

        # 2) 检索
        yield {
            "type": "status",
            "stage": "retrieval",
            "message": "正在检索知识库…",
        }

        try:
            retrieved = self.searcher.search(
                query=retrieval_query,
                top_k=top_k,
                use_bm25=use_bm25,
                use_reranker=use_reranker,
                include_images=include_images,
            use_web=use_web,
            web_limit=web_limit,
            web_fetch_pages=web_fetch_pages,
            )
        except Exception as exc:  # noqa: BLE001
            yield {"type": "error", "message": f"检索失败：{exc}"}
            return

        results = retrieved["results"]
        citations = build_citations(results)

        yield {
            "type": "citations",
            "citations": citations,
            "stats": retrieved["stats"],
            "context": retrieved["context"],
            "retrieval_query": retrieval_query,
            "mode": answer_mode.name,
        }

        # 3) 生成
        if not results:
            # 检索没命中 —— 不硬拒答，改为直接回答
            yield {
                "type": "status",
                "stage": "generation",
                "message": "知识库没有命中，改为直接回答…",
            }

            fallback_parts: list[str] = []
            fallback_usage: dict[str, int] = {}

            try:
                for delta in self.llm.stream(  # type: ignore[attr-defined]
                    self._build_messages(
                        question, "", history, image=image, direct=True
                    ),
                    max_tokens=(
                        max_tokens
                        if max_tokens is not None
                        else answer_mode.max_tokens
                    ),
                    temperature=(
                        temperature
                        if temperature is not None
                        else answer_mode.temperature
                    ),
                    thinking=answer_mode.thinking,
                ):
                    if delta.usage is not None:
                        fallback_usage = delta.usage.to_dict()
                    if delta.content:
                        fallback_parts.append(delta.content)
                        yield {"type": "token", "text": delta.content}
            except Exception as exc:  # noqa: BLE001
                yield {"type": "error", "message": f"生成失败：{exc}"}
                return

            if fallback_usage:
                record_usage(
                    fallback_usage, model=self._model_name(), kind="chat"
                )

            yield {
                "type": "done",
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                "model": self._model_name(),
                "mode": answer_mode.name,
                "used_retrieval": False,
                "route_reason": "检索无命中，改为直接回答",
                "usage": fallback_usage,
                "turn": {
                    "question": question,
                    "answer": "".join(fallback_parts),
                    "retrieval_query": retrieval_query,
                    "citations": [],
                    "results": [],
                    "context": "",
                    "mode": answer_mode.name,
                    "model": self._model_name(),
                    "usage": fallback_usage,
                    "elapsed_ms": round(
                        (time.perf_counter() - started) * 1000, 2
                    ),
                    "used_retrieval": False,
                    "route_reason": "检索无命中，改为直接回答",
                },
            }
            return

        yield {
            "type": "status",
            "stage": "generation",
            "message": (
                "正在生成回答…"
                if answer_mode.thinking
                else "正在生成回答（快速模式，已跳过思考）…"
            ),
        }

        answer_parts: list[str] = []
        reasoning_parts: list[str] = []
        # 流式响应的 usage 在最后一个 chunk 才出现，边收边存
        stream_usage: dict[str, int] = {}

        try:
            for delta in self.llm.stream(  # type: ignore[attr-defined]
                self._build_messages(
                    question, retrieved["context"], history, image=image
                ),
                max_tokens=(
                    max_tokens
                    if max_tokens is not None
                    else answer_mode.max_tokens
                ),
                temperature=(
                    temperature
                    if temperature is not None
                    else answer_mode.temperature
                ),
                thinking=answer_mode.thinking,
            ):
                if delta.usage is not None:
                    stream_usage = delta.usage.to_dict()
                if delta.reasoning:
                    reasoning_parts.append(delta.reasoning)
                    yield {"type": "reasoning", "text": delta.reasoning}
                if delta.content:
                    answer_parts.append(delta.content)
                    yield {"type": "token", "text": delta.content}

        except Exception as exc:  # noqa: BLE001
            yield {"type": "error", "message": f"生成失败：{exc}"}
            return

        if stream_usage:
            record_usage(
                stream_usage, model=self._model_name(), kind="chat"
            )

        yield {
            "type": "done",
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            "model": self._model_name(),
            "mode": answer_mode.name,
            "usage": stream_usage,
            # 供服务端直接落盘，避免前端再回传一遍
            "turn": {
                "question": question,
                "answer": "".join(answer_parts),
                "reasoning": "".join(reasoning_parts),
                "retrieval_query": retrieval_query,
                "citations": citations,
                "results": results,
                "context": retrieved["context"],
                "mode": answer_mode.name,
                "model": self._model_name(),
                "usage": stream_usage,
                "elapsed_ms": round(
                    (time.perf_counter() - started) * 1000, 2
                ),
            },
        }


__all__ = [
    "RAGChat",
    "build_image_content",
    "condense_query",
    "sanitize_text",
]
