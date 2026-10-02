"""联网搜索。

    from src.web import search_web

    outcome = search_web("nmap SYN 扫描", limit=5)
    for item in outcome.raw:
        print(item.title, item.url)

设计要点见各子模块：

* :mod:`src.web.fetch` —— 代理处理（绕开 httpx 的 ``NO_PROXY`` 崩溃）、
  HTML 取正文、受限抓取
* :mod:`src.web.providers` —— 搜索后端（默认 Bing，免密钥）
* :mod:`src.web.search` —— 编排与结果结构转换
* :mod:`src.web.config` —— 设置持久化（Key 只出掩码）
"""

from src.web.config import (
    WebConfigStore,
    WebSettings,
    get_web_config,
    mask_key,
)
from src.web.fetch import build_client, fetch_page, strip_html
from src.web.providers import (
    DEFAULT_PROVIDER,
    PROVIDERS,
    WebProvider,
    WebResult,
    get_provider,
    provider_catalog,
)
from src.web.search import (
    WebSearchOutcome,
    WebSearcher,
    search_web,
    to_result_dict,
)

__all__ = [
    "DEFAULT_PROVIDER",
    "PROVIDERS",
    "WebConfigStore",
    "WebProvider",
    "WebResult",
    "WebSearchOutcome",
    "WebSearcher",
    "WebSettings",
    "build_client",
    "fetch_page",
    "get_provider",
    "get_web_config",
    "mask_key",
    "provider_catalog",
    "search_web",
    "strip_html",
    "to_result_dict",
]
