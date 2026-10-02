"""联网搜索编排：搜索 → 可选抓正文 → 转成与本地检索一致的结构。

为什么要转成**和本地结果一样的形状**
------------------------------------
这样 ``build_context`` / ``build_citations`` 不用为网页写第二套逻辑，
编号、截断、引用渲染全部复用。区分只体现在
``metadata.source_type = "web"`` 和 ``metadata.url`` 上。
"""

from __future__ import annotations

import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

from src.web.config import WebSettings, get_web_config
from src.web.fetch import build_client, fetch_page
from src.web.providers import WebProvider, WebResult, get_provider


@dataclass
class WebSearchOutcome:
    """一次联网搜索的结果。"""

    results: list[dict[str, Any]] = field(default_factory=list)
    raw: list[WebResult] = field(default_factory=list)
    provider: str = ""
    elapsed_ms: float = 0.0
    fetched: int = 0
    error: str = ""

    @property
    def ok(self) -> bool:
        return bool(self.results)

    def summary(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "count": len(self.results),
            "fetched_pages": self.fetched,
            "elapsed_ms": round(self.elapsed_ms, 1),
            "error": self.error,
        }


def _stable_id(url: str, rank: int) -> str:
    digest = hashlib.sha1(f"{url}#{rank}".encode("utf-8")).hexdigest()[:12]
    return f"web::{digest}"


def to_result_dict(item: WebResult, rank: int) -> dict[str, Any]:
    """把网页结果转成与本地检索结果一致的 dict 形状。"""
    content = (item.content or item.snippet or "").strip()
    chunk_id = _stable_id(item.url, rank)

    return {
        "id": chunk_id,
        "score": round(max(0.0, 1.0 - rank * 0.05), 4),
        # 网页结果不参与本地重排，显式留空
        "rerank_score": None,
        "payload": {
            "chunk_id": chunk_id,
            "doc_id": f"web::{item.domain}",
            "source": item.url,
            "content": content,
            "section": "",
            "title": item.title,
            "metadata": {
                "source_type": "web",
                "file_name": item.title or item.url,
                "url": item.url,
                "domain": item.domain,
                "engine": item.engine,
                "rank": rank,
                "published": item.published,
                "snippet": item.snippet,
                "modality": "text",
            },
        },
    }


class WebSearcher:
    """联网搜索器。"""

    def __init__(self, settings: WebSettings | None = None) -> None:
        self.settings = settings or get_web_config().get()

    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        limit: int | None = None,
        provider: WebProvider | None = None,
        fetch_pages: bool | None = None,
        settings: WebSettings | None = None,
    ) -> WebSearchOutcome:
        """执行一次联网搜索。

        任何失败都返回带 ``error`` 的空结果，**不抛异常** ——
        联网失败不该让整个问答失败。
        """
        cfg = settings or self.settings
        started = time.perf_counter()

        query = (query or "").strip()
        if not query:
            return WebSearchOutcome(error="查询为空")

        engine = provider or get_provider(cfg.provider)

        ok, reason = engine.available(cfg.api_key, cfg.searxng_url)
        if not ok:
            return WebSearchOutcome(
                provider=engine.id,
                error=reason,
                elapsed_ms=(time.perf_counter() - started) * 1000,
            )

        want = limit if limit is not None else cfg.max_results
        do_fetch = cfg.fetch_pages if fetch_pages is None else fetch_pages

        try:
            with build_client(
                timeout=cfg.timeout, use_proxy=cfg.use_proxy
            ) as client:
                raw = engine.search(
                    query,
                    limit=want,
                    client=client,
                    api_key=cfg.api_key,
                    base_url=cfg.searxng_url,
                    timeout=cfg.timeout,
                    use_proxy=cfg.use_proxy,
                )

                # 防御后端超量返回：limit 是我们对外的承诺，
                # 不能指望每个后端都老实照做（测试里的假后端就没照做）
                raw = list(raw or [])[:want]

                fetched = 0
                if do_fetch and raw and cfg.fetch_top_n > 0:
                    fetched = self._fetch_bodies(client, raw, cfg)

        except Exception as exc:  # noqa: BLE001
            return WebSearchOutcome(
                provider=engine.id,
                error=f"{type(exc).__name__}: {exc}",
                elapsed_ms=(time.perf_counter() - started) * 1000,
            )

        results = [
            to_result_dict(item, rank) for rank, item in enumerate(raw, start=1)
        ]

        return WebSearchOutcome(
            results=results,
            raw=raw,
            provider=engine.id,
            fetched=fetched,
            elapsed_ms=(time.perf_counter() - started) * 1000,
        )

    # ------------------------------------------------------------------

    def _fetch_bodies(
        self,
        client: Any,
        raw: list[WebResult],
        cfg: WebSettings,
    ) -> int:
        """并行抓取前 N 条的正文。返回成功条数。

        并行是必要的：串行抓 3 页 ≈ 2~4 秒，并行只要 ~1 秒，
        而问答的整体延迟对体感影响很大。
        """
        targets = [
            item for item in raw[: cfg.fetch_top_n] if item.url.startswith("http")
        ]
        if not targets:
            return 0

        fetched = 0

        with ThreadPoolExecutor(max_workers=min(4, len(targets))) as pool:
            futures = {
                pool.submit(
                    fetch_page,
                    client,
                    item.url,
                    max_chars=cfg.max_page_chars,
                ): item
                for item in targets
            }

            for future in as_completed(futures):
                item = futures[future]

                try:
                    page = future.result()
                except Exception:  # noqa: BLE001
                    continue

                if not page.get("ok"):
                    continue

                item.content = page.get("text") or ""

                # 百度给的是跳转链接，这里顺便换成真实地址
                final_url = page.get("final_url") or ""
                if final_url.startswith("http") and final_url != item.url:
                    item.url = final_url

                if not item.title:
                    item.title = page.get("title") or item.url

                fetched += 1

        return fetched

    # ------------------------------------------------------------------

    def test(self) -> dict[str, Any]:
        """连通性测试：搜一个固定词，回报后端与耗时。"""
        outcome = self.search("hello world", limit=3, fetch_pages=False)

        return {
            "ok": outcome.ok,
            "provider": outcome.provider,
            "count": len(outcome.results),
            "elapsed_ms": round(outcome.elapsed_ms, 1),
            "error": outcome.error,
            "samples": [
                {"title": r.title, "url": r.url, "domain": r.domain}
                for r in outcome.raw[:3]
            ],
        }


def search_web(
    query: str,
    *,
    limit: int | None = None,
    fetch_pages: bool | None = None,
    settings: WebSettings | None = None,
) -> WebSearchOutcome:
    """便捷入口。"""
    return WebSearcher(settings).search(
        query, limit=limit, fetch_pages=fetch_pages, settings=settings
    )


__all__ = [
    "WebSearchOutcome",
    "WebSearcher",
    "search_web",
    "to_result_dict",
]
