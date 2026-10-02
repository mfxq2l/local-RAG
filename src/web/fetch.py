"""联网搜索的 HTTP 层：代理感知的 client、HTML 取正文、受限抓取。

两个必须说清楚的坑
------------------
**1. 代理要显式传，不能让 httpx 读环境。**

项目里其他 httpx client 都用 ``trust_env=False``（为了不被系统代理拦截
到 127.0.0.1 的请求）。但联网搜索**需要**代理 —— 国内直连拿不到
DuckDuckGo / Google 这类站点。

不能简单改成 ``trust_env=True``：httpx 0.28 解析 ``NO_PROXY`` 时，遇到
形如 ``[::1]`` 的方括号 IPv6 条目会抛 ``Invalid port: ':1]'``，
**建 client 就失败**，和搜索后端毫无关系，极难排查。

所以：``trust_env=False`` + 自己从环境变量读代理 + 显式传 ``proxy=``。

**2. 抓回来的 HTML 必须限流。**

搜索结果的页面可能很大（实测某教程页 95 万字符）。无脑 ``.text`` 会
把内存和上下文都撑爆，所以按字节流式读取并设上限。
"""

from __future__ import annotations

import ipaddress
import os
import re
from html import unescape
from socket import gaierror
from typing import Any
from urllib.parse import urlparse

import httpx


DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)

# 只抓这些类型
_TEXTUAL = (
    "text/html",
    "text/plain",
    "application/xhtml+xml",
)

_MAX_BYTES = 2 * 1024 * 1024  # 单页最多读 2MB


# ----------------------------------------------------------------------
# 代理
# ----------------------------------------------------------------------


def proxy_from_env() -> str | None:
    """从环境变量取代理地址（优先 https）。取不到返回 None。"""
    for key in (
        "HTTPS_PROXY", "https_proxy",
        "HTTP_PROXY", "http_proxy",
        "ALL_PROXY", "all_proxy",
    ):
        value = (os.environ.get(key) or "").strip()
        if value:
            return value
    return None


def build_client(
    timeout: float = 15.0,
    use_proxy: bool = True,
    **kwargs: Any,
) -> httpx.Client:
    """建一个联网用的 client。

    Args:
        timeout: 请求超时（秒）。
        use_proxy: 是否使用环境变量里的代理。
        **kwargs: 透传给 ``httpx.Client``。

    Note:
        始终 ``trust_env=False`` —— 见模块文档里对 ``NO_PROXY`` 崩溃的说明。
    """
    proxy = proxy_from_env() if use_proxy else None

    headers = {
        "User-Agent": DEFAULT_UA,
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8",
    }
    headers.update(kwargs.pop("headers", None) or {})

    return httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        trust_env=False,
        proxy=proxy,
        headers=headers,
        **kwargs,
    )


# ----------------------------------------------------------------------
# 安全
# ----------------------------------------------------------------------


def is_safe_url(url: str) -> bool:
    """拒绝非 http(s) 以及指向内网的地址。

    搜索结果理论上可能指向 ``http://127.0.0.1:8082/...`` 这类本机服务。
    本应用只在本机跑，被抓一下危害有限，但没有理由去抓。
    """
    try:
        parsed = urlparse(url)
    except Exception:  # noqa: BLE001
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    host = (parsed.hostname or "").strip().lower()
    if not host:
        return False

    if host in ("localhost", "localhost.localdomain"):
        return False

    # 字面量 IP 时检查是否内网
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        # 不是 IP 字面量：域名放行（解析后的地址不再校验，够用）
        return True

    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
    )


# ----------------------------------------------------------------------
# HTML → 正文
# ----------------------------------------------------------------------

_DROP_BLOCKS = re.compile(
    r"(?is)<(script|style|noscript|svg|canvas|head|iframe|template|form)"
    r"\b[^>]*>.*?</\1\s*>"
)
_BLOCK_BREAK = re.compile(
    r"(?is)<(?:br|hr)\s*/?>|</(?:p|div|li|tr|h[1-6]|section|article|blockquote"
    r"|header|footer|nav|pre|table|ul|ol|dd|dt)\s*>"
)
_ANY_TAG = re.compile(r"(?s)<[^>]+>")
_WS_RUN = re.compile(r"[ \t\u00a0\u3000]+")
_NL_RUN = re.compile(r"\n\s*\n\s*\n+")

# 优先取这些容器，取不到再退到整页
_MAIN_CANDIDATES = (
    re.compile(r"(?is)<article\b[^>]*>(.*?)</article\s*>"),
    re.compile(r"(?is)<main\b[^>]*>(.*?)</main\s*>"),
    re.compile(r'(?is)<div[^>]+(?:id|class)="[^"]*(?:content|article|post|main)[^"]*"[^>]*>(.*?)</div\s*>'),
)


def strip_html(html: str, prefer_main: bool = True) -> str:
    """把 HTML 变成可读纯文本。

    没有 lxml / bs4（这个环境里都没装），所以用标准库级别的正则处理。
    先尝试抽 ``<article>`` / ``<main>`` / 常见正文容器，能明显减少导航栏
    与页脚的噪声。
    """
    if not html:
        return ""

    body = html

    if prefer_main:
        for pattern in _MAIN_CANDIDATES:
            match = pattern.search(html)
            if match and len(match.group(1)) > 400:
                body = match.group(1)
                break

    body = _DROP_BLOCKS.sub(" ", body)
    body = _BLOCK_BREAK.sub("\n", body)
    body = _ANY_TAG.sub(" ", body)
    body = unescape(body)

    body = _WS_RUN.sub(" ", body)
    body = "\n".join(line.strip() for line in body.splitlines())
    body = _NL_RUN.sub("\n\n", body)

    return body.strip()


_CJK = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7af]")


def _weight(line: str) -> int:
    """行的「信息量」：中文字符按 2 计。

    单纯用字符数无法同时适配中英文 —— 英文导航项 ``Reference Guide`` 有
    15 字符，而中文一个完整句子才 20 多个字符。加权后两者的量级才对得上。
    """
    return len(line) + len(_CJK.findall(line))


def drop_leading_nav(text: str, min_weight: int = 48, scan: int = 45) -> str:
    """去掉开头的导航菜单。

    很多页面没有 ``<article>`` / ``<main>`` 容器（实测 nmap.org 首页就是），
    于是整段导航会被当成正文：

        Download
        Reference Guide
        Book
        Docs
        Zenmap GUI
        ...

    导航的特征是**开头一连串短行**，而真正的正文段落通常较长。
    这里找到第一个「信息量」达标的行，从它开始保留（不回退 —— 回退会把
    最后一个导航项也留下，实测 "Zenmap GUI" 就是这么漏进来的）。

    长短按 :func:`_weight` 加权判断，中文字符算双倍，这样中英文页面用
    同一个阈值都成立。

    只在前面**确实全是短行**时才裁剪，避免误伤本来就很干净的正文。
    """
    lines = [line for line in text.split("\n")]

    for index, line in enumerate(lines[:scan]):
        if _weight(line) >= min_weight:
            # 前面若已经有达标行，说明这不是导航区，别动
            if any(_weight(x) >= min_weight for x in lines[:index]):
                return text
            if index <= 1:
                return text
            return "\n".join(lines[index:])

    return text


def trim_text(text: str, limit: int) -> str:
    """按字符数截断，尽量断在句子边界。"""
    if limit <= 0 or len(text) <= limit:
        return text

    head = text[:limit]
    for mark in ("。", "！", "？", ". ", "\n"):
        pos = head.rfind(mark)
        if pos > limit * 0.6:
            return head[: pos + len(mark)].rstrip()

    return head.rstrip() + "…"


# ----------------------------------------------------------------------
# 抓取
# ----------------------------------------------------------------------


def fetch_page(
    client: httpx.Client,
    url: str,
    *,
    max_bytes: int = _MAX_BYTES,
    max_chars: int = 4000,
) -> dict[str, Any]:
    """抓一个网页并提取正文。

    **流式读取并限流** —— 页面可能极大，无脑 ``.text`` 会撑爆内存与上下文。

    Returns:
        ``{"ok": bool, "url": str, "final_url": str, "status": int,
           "title": str, "text": str, "error": str}``
        任何失败都返回 ``ok=False`` 而不是抛异常 —— 单页失败不该毁掉整次搜索。
    """
    result: dict[str, Any] = {
        "ok": False,
        "url": url,
        "final_url": url,
        "status": 0,
        "title": "",
        "text": "",
        "error": "",
    }

    if not is_safe_url(url):
        result["error"] = "不安全的地址"
        return result

    chunks: list[bytes] = []
    size = 0

    try:
        with client.stream("GET", url) as response:
            result["status"] = response.status_code
            result["final_url"] = str(response.url)

            if response.status_code >= 400:
                result["error"] = f"HTTP {response.status_code}"
                return result

            ctype = (response.headers.get("content-type") or "").lower()
            if ctype and not any(t in ctype for t in _TEXTUAL):
                result["error"] = f"非文本类型：{ctype.split(';')[0]}"
                return result

            for chunk in response.iter_bytes():
                chunks.append(chunk)
                size += len(chunk)
                if size >= max_bytes:
                    break

    except httpx.TimeoutException:
        result["error"] = "请求超时"
        return result
    except (gaierror, OSError) as exc:
        result["error"] = f"网络错误：{exc}"
        return result
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result

    try:
        raw = b"".join(chunks).decode("utf-8", errors="replace")
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"解码失败：{exc}"
        return result

    title_match = re.search(r"(?is)<title[^>]*>(.*?)</title\s*>", raw)
    if title_match:
        result["title"] = unescape(_ANY_TAG.sub("", title_match.group(1))).strip()

    text = drop_leading_nav(strip_html(raw))
    result["ok"] = bool(text)
    result["text"] = trim_text(text, max_chars)

    return result


__all__ = [
    "DEFAULT_UA",
    "build_client",
    "drop_leading_nav",
    "fetch_page",
    "is_safe_url",
    "proxy_from_env",
    "strip_html",
    "trim_text",
]
