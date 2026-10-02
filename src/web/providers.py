"""搜索后端适配层。

后端分两类：

* **免密钥（抓网页）** —— ``bing`` / ``baidu`` / ``duckduckgo`` / ``searxng``
* **API 型（需 key）** —— ``tavily`` / ``serper`` / ``brave``

默认用 ``bing``：免密钥、国内可达、HTML 结构稳定（实测 10 条结果全部
解析出标题+链接+摘要）。``duckduckgo`` 在部分代理下会因证书问题失败，
因此不作为默认。
"""

from __future__ import annotations

import base64
import binascii
import json
import re
from dataclasses import asdict, dataclass, field
from html import unescape
from typing import Any
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import httpx

from src.web.fetch import build_client, strip_html


@dataclass
class WebResult:
    """一条网页搜索结果。"""

    title: str = ""
    url: str = ""
    snippet: str = ""
    content: str = ""
    engine: str = ""
    rank: int = 0
    published: str = ""

    @property
    def domain(self) -> str:
        try:
            return (urlparse(self.url).hostname or "").lower()
        except Exception:  # noqa: BLE001
            return ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["domain"] = self.domain
        return data


# ----------------------------------------------------------------------
# 链接解码
# ----------------------------------------------------------------------

_BING_CK = re.compile(r"bing\.com/ck/a\?", re.I)
_DDG_L = re.compile(r"duckduckgo\.com/l/\?")


def decode_bing_redirect(url: str) -> str:
    """解 ``bing.com/ck/a?...&u=a1<base64>&...`` 这类跳转链接。"""
    if not _BING_CK.search(url):
        return url

    try:
        params = parse_qs(urlparse(url).query)
        raw = (params.get("u") or [""])[0]
    except Exception:  # noqa: BLE001
        return url

    if not raw:
        return url

    # u 的值形如 a1aHR0cHM6Ly8...，去掉前两位再 base64 解
    payload = raw[2:] if raw.startswith("a1") else raw
    padding = "=" * (-len(payload) % 4)

    try:
        decoded = base64.urlsafe_b64decode(payload + padding).decode(
            "utf-8", errors="replace"
        )
    except (binascii.Error, ValueError):
        return url

    return decoded if decoded.startswith("http") else url


def decode_ddg_redirect(url: str) -> str:
    """解 DuckDuckGo 的 ``/l/?uddg=<urlencoded>`` 跳转。"""
    if not _DDG_L.search(url) and "uddg=" not in url:
        return url

    try:
        params = parse_qs(urlparse(url).query)
        target = (params.get("uddg") or [""])[0]
    except Exception:  # noqa: BLE001
        return url

    return unquote(target) if target.startswith("http") else url


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", strip_html(text or "")).strip()


# ----------------------------------------------------------------------
# 基类
# ----------------------------------------------------------------------


class WebProvider:
    """搜索后端基类。"""

    id: str = ""
    label: str = ""
    needs_key: bool = False
    needs_url: bool = False   # 如 SearXNG 需要实例地址

    def search(
        self,
        query: str,
        *,
        limit: int = 5,
        client: httpx.Client | None = None,
        api_key: str = "",
        base_url: str = "",
        timeout: float = 15.0,
        use_proxy: bool = True,
    ) -> list[WebResult]:
        raise NotImplementedError

    def _client(
        self, client: httpx.Client | None, timeout: float, use_proxy: bool
    ) -> tuple[httpx.Client, bool]:
        """返回 (client, 是否由我创建)。"""
        if client is not None:
            return client, False
        return build_client(timeout=timeout, use_proxy=use_proxy), True

    def available(self, api_key: str = "", base_url: str = "") -> tuple[bool, str]:
        """该后端在给定配置下是否可用。"""
        if self.needs_key and not api_key:
            return False, f"{self.label} 需要 API Key"
        if self.needs_url and not base_url:
            return False, f"{self.label} 需要实例地址"
        return True, ""


# ----------------------------------------------------------------------
# 免密钥：抓 HTML
# ----------------------------------------------------------------------


class BingProvider(WebProvider):
    """Bing（默认）。免密钥，国内可达。"""

    id = "bing"
    label = "Bing"

    _ITEM = re.compile(r'(?is)<li class="b_algo".*?</li>')
    _TITLE = re.compile(
        r'(?is)<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
    )
    _SNIPPET = re.compile(r"(?is)<p[^>]*>(.*?)</p>")

    def search(self, query, *, limit=5, client=None, api_key="",
               base_url="", timeout=15.0, use_proxy=True):
        cli, owned = self._client(client, timeout, use_proxy)

        try:
            response = cli.get(
                "https://www.bing.com/search",
                params={"q": query, "setlang": "zh-CN", "count": max(limit, 10)},
            )
            response.raise_for_status()
            html = response.text
        finally:
            if owned:
                cli.close()

        results: list[WebResult] = []

        for rank, block in enumerate(self._ITEM.findall(html)):
            match = self._TITLE.search(block)
            if not match:
                continue

            url = decode_bing_redirect(unescape(match.group(1)))
            title = _clean(match.group(2))

            if not url.startswith("http"):
                continue

            snippet = ""
            snip = self._SNIPPET.search(block)
            if snip:
                snippet = _clean(snip.group(1))

            results.append(
                WebResult(
                    title=title or url,
                    url=url,
                    snippet=snippet,
                    engine=self.id,
                    rank=rank,
                )
            )

            if len(results) >= limit:
                break

        return results


class BaiduProvider(WebProvider):
    """百度。免密钥，国内可达。

    注意：返回的链接是 ``baidu.com/link?url=...`` 跳转地址，
    真实地址要跟随重定向才能拿到 —— 抓正文时会自然解析出来。
    """

    id = "baidu"
    label = "百度"

    _ITEM = re.compile(
        r'(?is)<div[^>]+class="result[^"]*".*?<h3.*?</h3>.*?(?:</div>\s*){1,3}'
    )
    _TITLE = re.compile(r'(?is)<h3[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>')

    def search(self, query, *, limit=5, client=None, api_key="",
               base_url="", timeout=15.0, use_proxy=True):
        cli, owned = self._client(client, timeout, use_proxy)

        try:
            response = cli.get(
                "https://www.baidu.com/s",
                params={"wd": query, "rn": max(limit * 2, 10)},
            )
            response.raise_for_status()
            html = response.text
        finally:
            if owned:
                cli.close()

        results: list[WebResult] = []

        for rank, block in enumerate(self._ITEM.findall(html)):
            match = self._TITLE.search(block)
            if not match:
                continue

            url = unescape(match.group(1))
            title = _clean(match.group(2))

            if not url.startswith("http"):
                continue

            results.append(
                WebResult(
                    title=title or url,
                    url=url,
                    snippet="",
                    engine=self.id,
                    rank=rank,
                )
            )

            if len(results) >= limit:
                break

        return results


class DuckDuckGoProvider(WebProvider):
    """DuckDuckGo（免密钥）。

    在部分代理环境下会因证书校验失败 —— 那些网络下请改用 bing。
    """

    id = "duckduckgo"
    label = "DuckDuckGo"

    _ITEM = re.compile(r'(?is)<div class="result[^"]*".*?</div>\s*</div>')
    _TITLE = re.compile(
        r'(?is)<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
    )
    _SNIPPET = re.compile(
        r'(?is)class="result__snippet"[^>]*>(.*?)</a>'
    )

    def search(self, query, *, limit=5, client=None, api_key="",
               base_url="", timeout=15.0, use_proxy=True):
        cli, owned = self._client(client, timeout, use_proxy)

        try:
            response = cli.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query, "kl": "cn-zh"},
            )
            response.raise_for_status()
            html = response.text
        finally:
            if owned:
                cli.close()

        results: list[WebResult] = []

        for rank, block in enumerate(self._ITEM.findall(html)):
            match = self._TITLE.search(block)
            if not match:
                continue

            url = decode_ddg_redirect(unescape(match.group(1)))
            title = _clean(match.group(2))

            if not url.startswith("http"):
                continue

            snippet = ""
            snip = self._SNIPPET.search(block)
            if snip:
                snippet = _clean(snip.group(1))

            results.append(
                WebResult(
                    title=title or url,
                    url=url,
                    snippet=snippet,
                    engine=self.id,
                    rank=rank,
                )
            )

            if len(results) >= limit:
                break

        return results


class SearxngProvider(WebProvider):
    """自建 / 公共 SearXNG 实例（JSON API）。"""

    id = "searxng"
    label = "SearXNG"
    needs_url = True

    def search(self, query, *, limit=5, client=None, api_key="",
               base_url="", timeout=15.0, use_proxy=True):
        if not base_url:
            return []

        cli, owned = self._client(client, timeout, use_proxy)

        try:
            response = cli.get(
                base_url.rstrip("/") + "/search",
                params={"q": query, "format": "json", "language": "zh-CN"},
            )
            response.raise_for_status()
            data = response.json()
        finally:
            if owned:
                cli.close()

        results: list[WebResult] = []

        for rank, item in enumerate((data or {}).get("results") or []):
            url = str(item.get("url") or "")
            if not url.startswith("http"):
                continue

            results.append(
                WebResult(
                    title=_clean(str(item.get("title") or url)),
                    url=url,
                    snippet=_clean(str(item.get("content") or "")),
                    engine=self.id,
                    rank=rank,
                    published=str(item.get("publishedDate") or ""),
                )
            )

            if len(results) >= limit:
                break

        return results


# ----------------------------------------------------------------------
# API 型
# ----------------------------------------------------------------------


class TavilyProvider(WebProvider):
    """Tavily —— 专为 LLM 设计的搜索 API，直接返回正文。"""

    id = "tavily"
    label = "Tavily"
    needs_key = True

    def search(self, query, *, limit=5, client=None, api_key="",
               base_url="", timeout=15.0, use_proxy=True):
        cli, owned = self._client(client, timeout, use_proxy)

        try:
            response = cli.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "max_results": limit,
                    "search_depth": "basic",
                    "include_answer": False,
                },
            )
            response.raise_for_status()
            data = response.json()
        finally:
            if owned:
                cli.close()

        results: list[WebResult] = []

        for rank, item in enumerate((data or {}).get("results") or []):
            url = str(item.get("url") or "")
            if not url.startswith("http"):
                continue

            results.append(
                WebResult(
                    title=_clean(str(item.get("title") or url)),
                    url=url,
                    snippet=_clean(str(item.get("content") or ""))[:400],
                    content=str(item.get("content") or ""),
                    engine=self.id,
                    rank=rank,
                )
            )

        return results


class SerperProvider(WebProvider):
    """Serper（Google 结果代理）。"""

    id = "serper"
    label = "Serper"
    needs_key = True

    def search(self, query, *, limit=5, client=None, api_key="",
               base_url="", timeout=15.0, use_proxy=True):
        cli, owned = self._client(client, timeout, use_proxy)

        try:
            response = cli.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
                json={"q": query, "num": limit, "gl": "cn", "hl": "zh-cn"},
            )
            response.raise_for_status()
            data = response.json()
        finally:
            if owned:
                cli.close()

        results: list[WebResult] = []

        for rank, item in enumerate((data or {}).get("organic") or []):
            url = str(item.get("link") or "")
            if not url.startswith("http"):
                continue

            results.append(
                WebResult(
                    title=_clean(str(item.get("title") or url)),
                    url=url,
                    snippet=_clean(str(item.get("snippet") or "")),
                    engine=self.id,
                    rank=rank,
                )
            )

            if len(results) >= limit:
                break

        return results


class BraveProvider(WebProvider):
    """Brave Search API。"""

    id = "brave"
    label = "Brave"
    needs_key = True

    def search(self, query, *, limit=5, client=None, api_key="",
               base_url="", timeout=15.0, use_proxy=True):
        cli, owned = self._client(client, timeout, use_proxy)

        try:
            response = cli.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": api_key, "Accept": "application/json"},
                params={"q": query, "count": limit},
            )
            response.raise_for_status()
            data = response.json()
        finally:
            if owned:
                cli.close()

        results: list[WebResult] = []

        web = ((data or {}).get("web") or {}).get("results") or []

        for rank, item in enumerate(web):
            url = str(item.get("url") or "")
            if not url.startswith("http"):
                continue

            results.append(
                WebResult(
                    title=_clean(str(item.get("title") or url)),
                    url=url,
                    snippet=_clean(str(item.get("description") or "")),
                    engine=self.id,
                    rank=rank,
                    published=str(item.get("age") or ""),
                )
            )

            if len(results) >= limit:
                break

        return results


# ----------------------------------------------------------------------
# 注册表
# ----------------------------------------------------------------------

PROVIDERS: dict[str, WebProvider] = {
    p.id: p
    for p in (
        BingProvider(),
        BaiduProvider(),
        DuckDuckGoProvider(),
        SearxngProvider(),
        TavilyProvider(),
        SerperProvider(),
        BraveProvider(),
    )
}

DEFAULT_PROVIDER = "bing"


def get_provider(provider_id: str | None) -> WebProvider:
    """按 id 取后端；未知 id 返回默认后端。"""
    return PROVIDERS.get((provider_id or "").strip().lower()) or PROVIDERS[
        DEFAULT_PROVIDER
    ]


def provider_catalog() -> list[dict[str, Any]]:
    """给设置面板用的后端清单。"""
    return [
        {
            "id": p.id,
            "label": p.label,
            "needs_key": p.needs_key,
            "needs_url": p.needs_url,
            "default": p.id == DEFAULT_PROVIDER,
        }
        for p in PROVIDERS.values()
    ]


__all__ = [
    "DEFAULT_PROVIDER",
    "PROVIDERS",
    "BaiduProvider",
    "BingProvider",
    "BraveProvider",
    "DuckDuckGoProvider",
    "SearxngProvider",
    "SerperProvider",
    "TavilyProvider",
    "WebProvider",
    "WebResult",
    "decode_bing_redirect",
    "decode_ddg_redirect",
    "get_provider",
    "provider_catalog",
]
