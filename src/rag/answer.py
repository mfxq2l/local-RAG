"""RAG 问答编排。

完整链路：

    Query
      ↓
    Hybrid Retrieval（Dense + BM25 + RRF + Rerank）   ← src.rag.search
      ↓
    Context（带 [n] 编号）                            ← src.rag.context
      ↓
    Prompt                                            ← src.rag.prompt
      ↓
    LLM（本地 llama.cpp 或 OpenAI 兼容端点）           ← src.llm
      ↓
    Answer + 引用列表
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Iterator

from src.llm import ChatMessage, LLMUnavailable, get_llm
from src.rag.context import build_citations
from src.rag.modes import AnswerMode, resolve_mode
from src.rag.prompt import (
    DIRECT_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    build_rag_prompt,
)
from src.rag.search import RAGSearch
from src.usage import record_usage


@dataclass
class AnswerResult:
    """一次完整问答的结果。"""

    query: str
    answer: str
    reasoning: str = ""

    results: list[dict[str, Any]] = field(default_factory=list)
    citations: list[dict[str, Any]] = field(default_factory=list)

    context: str = ""
    stats: dict[str, Any] = field(default_factory=dict)

    model: str = ""
    mode: str = ""
    elapsed_ms: float = 0.0
    usage: dict[str, int] = field(default_factory=dict)
    finish_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "reasoning": self.reasoning,
            "results": self.results,
            "citations": self.citations,
            "context": self.context,
            "stats": self.stats,
            "model": self.model,
            "mode": self.mode,
            "elapsed_ms": self.elapsed_ms,
            "usage": self.usage,
            "finish_reason": self.finish_reason,
        }


class RAGAnswerer:
    """检索增强问答。"""

    def __init__(
        self,
        name: str | None = None,
        provider: str | None = None,
        llm_model: str | None = None,
    ) -> None:
        self.searcher = RAGSearch(name)
        self.llm = get_llm(provider, model=llm_model)

    # ------------------------------------------------------------------
    # 状态
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """LLM 可用性。"""
        try:
            ok, reason = self.llm.available()  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            return {"available": False, "reason": str(exc)}

        return {"available": ok, "reason": reason}

    def _model_name(self) -> str:
        return getattr(self.llm, "name", "unknown")

    # ------------------------------------------------------------------
    # 内部：构造 messages
    # ------------------------------------------------------------------

    @staticmethod
    def _build_messages(query: str, context: str) -> list[ChatMessage]:
        return [
            ChatMessage("system", SYSTEM_PROMPT),
            ChatMessage("user", build_rag_prompt(query, context)),
        ]

    # ------------------------------------------------------------------
    # 非流式
    # ------------------------------------------------------------------

    def answer(
        self,
        query: str,
        top_k: int = 5,
        use_bm25: bool | None = None,
        use_reranker: bool | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        mode: str | None = None,
        include_images: bool = True,
        use_web: bool | None = None,
        web_limit: int | None = None,
        web_fetch_pages: bool | None = None,
    ) -> AnswerResult:
        """检索 + 生成，返回完整答案。

        Args:
            mode: 问答档位 ``fast`` / ``precise``，None 用配置默认值。
            temperature / max_tokens: 显式指定时覆盖档位的默认值。
            include_images: 是否把图片纳入检索结果。

        Raises:
            LLMUnavailable: 没有可用的生成模型。调用方应降级为纯检索。
        """
        started = time.perf_counter()

        answer_mode: AnswerMode = resolve_mode(mode)

        retrieved = self.searcher.search(
            query=query,
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

        available, reason = self.llm.available()  # type: ignore[attr-defined]
        if not available:
            raise LLMUnavailable(reason)

        if not results:
            # 没有相关资料 —— 不硬拒答，改为当普通问题直接回答
            try:
                direct = self.llm.chat(  # type: ignore[attr-defined]
                    [
                        ChatMessage("system", DIRECT_SYSTEM_PROMPT),
                        ChatMessage("user", query),
                    ],
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
                answer = direct.content
            except Exception:  # noqa: BLE001
                answer = "没有检索到相关资料，我也无法直接回答这个问题。"

            return AnswerResult(
                query=query,
                answer=answer,
                results=[],
                citations=[],
                context="",
                stats=retrieved["stats"],
                model=self._model_name(),
                mode=answer_mode.name,
                elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
            )

        reply = self.llm.chat(  # type: ignore[attr-defined]
            self._build_messages(query, context),
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

        if getattr(reply, "usage", None):
            record_usage(
                reply.usage.to_dict(),
                model=getattr(reply, "model", "") or self._model_name(),
                kind="ask",
            )

        return AnswerResult(
            query=query,
            answer=reply.content,
            reasoning=getattr(reply, "reasoning", "") or "",
            results=results,
            citations=build_citations(results),
            context=context,
            stats=retrieved["stats"],
            model=getattr(reply, "model", "") or self._model_name(),
            mode=answer_mode.name,
            elapsed_ms=round((time.perf_counter() - started) * 1000, 2),
            usage=reply.usage.to_dict() if getattr(reply, "usage", None) else {},
            finish_reason=getattr(reply, "finish_reason", None),
        )

    # ------------------------------------------------------------------
    # 流式
    # ------------------------------------------------------------------
    def stream(
        self,
        query: str,
        top_k: int = 5,
        use_bm25: bool | None = None,
        use_reranker: bool | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        mode: str | None = None,
        include_images: bool = True,
        use_web: bool | None = None,
        web_limit: int | None = None,
        web_fetch_pages: bool | None = None,
    ) -> Iterator[dict[str, Any]]:
        """流式问答，逐个产出事件字典。

        事件类型：

            {"type": "status",    "stage": ..., "message": ...}
            {"type": "citations", "citations": [...], "stats": {...}}
            {"type": "reasoning", "text": "..."}
            {"type": "token",     "text": "..."}
            {"type": "done",      "elapsed_ms": ..., "usage": {...}}
            {"type": "error",     "message": ...}
        """
        started = time.perf_counter()

        try:
            answer_mode: AnswerMode = resolve_mode(mode)
        except ValueError as exc:
            yield {"type": "error", "message": str(exc)}
            return

        yield {
            "type": "status",
            "stage": "retrieval",
            "message": "正在检索知识库…",
            "mode": answer_mode.name,
        }

        try:
            retrieved = self.searcher.search(
                query=query,
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

        yield {
            "type": "citations",
            "citations": build_citations(results),
            "stats": retrieved["stats"],
            "context": retrieved["context"],
            "mode": answer_mode.name,
        }

        available, reason = self.llm.available()  # type: ignore[attr-defined]
        if not available:
            yield {"type": "error", "message": reason, "degraded": True}
            return

        if not results:
            # 没有相关资料 —— 流式地当普通问题直接回答
            yield {
                "type": "status",
                "stage": "generation",
                "message": "没有相关资料，直接回答…",
            }

            direct_usage: dict[str, int] = {}

            try:
                for delta in self.llm.stream(  # type: ignore[attr-defined]
                    [
                        ChatMessage("system", DIRECT_SYSTEM_PROMPT),
                        ChatMessage("user", query),
                    ],
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
                        direct_usage = delta.usage.to_dict()
                    if delta.content:
                        yield {"type": "token", "text": delta.content}
            except Exception as exc:  # noqa: BLE001
                yield {"type": "error", "message": f"生成失败：{exc}"}
                return

            if direct_usage:
                record_usage(
                    direct_usage, model=self._model_name(), kind="ask"
                )

            yield {
                "type": "done",
                "elapsed_ms": round(
                    (time.perf_counter() - started) * 1000, 2
                ),
                "usage": direct_usage,
                "used_retrieval": False,
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
            "mode": answer_mode.name,
        }

        stream_usage: dict[str, int] = {}

        try:
            for delta in self.llm.stream(  # type: ignore[attr-defined]
                self._build_messages(query, retrieved["context"]),
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
                    yield {"type": "reasoning", "text": delta.reasoning}
                if delta.content:
                    yield {"type": "token", "text": delta.content}

        except Exception as exc:  # noqa: BLE001
            yield {"type": "error", "message": f"生成失败：{exc}"}
            return

        if stream_usage:
            record_usage(stream_usage, model=self._model_name(), kind="ask")

        yield {
            "type": "done",
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            "usage": stream_usage,
            "model": self._model_name(),
            "mode": answer_mode.name,
        }


def answer_rag(
    query: str,
    top_k: int = 5,
    use_bm25: bool | None = None,
    use_reranker: bool | None = None,
    name: str | None = None,
    provider: str | None = None,
    mode: str | None = None,
    llm_model: str | None = None,
    include_images: bool = True,
) -> dict[str, Any]:
    """给 server / CLI 用的顶层函数。"""
    return RAGAnswerer(name, provider, llm_model).answer(
        query=query,
        top_k=top_k,
        use_bm25=use_bm25,
        use_reranker=use_reranker,
        mode=mode,
        include_images=include_images,
    ).to_dict()


__all__ = ["AnswerResult", "RAGAnswerer", "answer_rag"]
