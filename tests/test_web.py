"""联网搜索测试（全部离线，不发真实请求）。"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import httpx

from src.web.config import (
    MAX_RESULTS,
    WebConfigStore,
    WebSettings,
    mask_key,
    normalize,
)
from src.web.fetch import (
    build_client,
    drop_leading_nav,
    is_safe_url,
    proxy_from_env,
    strip_html,
    trim_text,
)
from src.web.providers import (
    DEFAULT_PROVIDER,
    PROVIDERS,
    WebResult,
    decode_bing_redirect,
    decode_ddg_redirect,
    get_provider,
    provider_catalog,
)
from src.web.search import WebSearcher, to_result_dict


# ----------------------------------------------------------------------
# HTML → 文本
# ----------------------------------------------------------------------


class TestStripHtml(unittest.TestCase):
    def test_removes_script_and_style(self) -> None:
        html = "<p>正文</p><script>var a=1;</script><style>.x{}</style>"
        text = strip_html(html)
        self.assertIn("正文", text)
        self.assertNotIn("var a", text)
        self.assertNotIn(".x", text)

    def test_block_tags_become_newlines(self) -> None:
        text = strip_html("<div>一</div><div>二</div><p>三</p>")
        self.assertEqual(text.split("\n"), ["一", "二", "三"])

    def test_decodes_entities(self) -> None:
        self.assertIn("A & B", strip_html("<p>A &amp; B</p>"))
        self.assertIn("<标签>", strip_html("<p>&lt;标签&gt;</p>"))
        self.assertIn("\u00a0".replace("\u00a0", " "), strip_html("<p>a&nbsp;b</p>"))

    def test_collapses_whitespace(self) -> None:
        text = strip_html("<p>a     b\n\n\n\nc</p>")
        self.assertNotIn("  ", text)
        self.assertIn("a b", text)

    def test_prefers_article_container(self) -> None:
        html = (
            "<nav>导航项目一大堆文字很多很多</nav>"
            "<article><p>" + "正文内容。" * 100 + "</p></article>"
            "<footer>页脚</footer>"
        )
        text = strip_html(html)
        self.assertIn("正文内容", text)
        self.assertNotIn("导航项目", text)

    def test_ignores_short_article(self) -> None:
        """article 太短就不采信，退到整页。"""
        html = "<article>短</article><p>" + "真正的内容。" * 100 + "</p>"
        self.assertIn("真正的内容", strip_html(html))

    def test_empty_input(self) -> None:
        self.assertEqual(strip_html(""), "")

    def test_br_becomes_newline(self) -> None:
        self.assertEqual(len(strip_html("a<br>b").split("\n")), 2)


class TestDropLeadingNav(unittest.TestCase):
    def test_drops_english_nav_blocks(self) -> None:
        text = "\n".join(
            ["Download", "Reference Guide", "Book", "Docs", "Zenmap GUI"]
            + ["This is a sufficiently long paragraph of real content."] * 2
        )
        out = drop_leading_nav(text)
        self.assertNotIn("Zenmap GUI", out)
        self.assertIn("real content", out)

    def test_drops_chinese_nav_blocks(self) -> None:
        """中文信息密度高，阈值必须对中文也成立。"""
        text = "\n".join(
            ["首页", "文档", "下载", "关于我们"]
            + ["这是一段足够长的正文，讲述真正的内容，应该被完整保留下来。"] * 2
        )
        out = drop_leading_nav(text)
        self.assertNotIn("关于我们", out)
        self.assertIn("真正的内容", out)

    def test_keeps_clean_text(self) -> None:
        text = "这是一段足够长的正文，讲述真正的内容，应该被完整保留下来。" * 2
        self.assertEqual(drop_leading_nav(text), text)

    def test_keeps_when_long_line_early(self) -> None:
        text = "开头就是很长的正文段落，长度显然超过阈值。" + "\n短\n短"
        self.assertEqual(drop_leading_nav(text), text)

    def test_all_short_lines_unchanged(self) -> None:
        text = "短\n短\n短"
        self.assertEqual(drop_leading_nav(text), text)

    def test_content_line_not_trimmed_away(self) -> None:
        """裁剪后必须保留正文，不能把内容也切掉。"""
        text = "导航一\n导航二\n中文正文段落，足够长，应该保留下来。" * 1
        out = drop_leading_nav(text)
        self.assertIn("中文正文段落", out)


class TestTrimText(unittest.TestCase):
    def test_no_trim_when_short(self) -> None:
        self.assertEqual(trim_text("abc", 10), "abc")

    def test_trim_at_sentence_boundary(self) -> None:
        text = "第一句话。" + "填充" * 100
        out = trim_text(text, 30)
        self.assertTrue(out.endswith("。") or out.endswith("…"))
        self.assertLessEqual(len(out), 31)

    def test_limit_zero_returns_whole(self) -> None:
        self.assertEqual(trim_text("abc", 0), "abc")


# ----------------------------------------------------------------------
# 安全
# ----------------------------------------------------------------------


class TestIsSafeUrl(unittest.TestCase):
    def test_allows_public_http(self) -> None:
        self.assertTrue(is_safe_url("https://nmap.org/"))
        self.assertTrue(is_safe_url("http://example.com/a?b=1"))

    def test_blocks_localhost(self) -> None:
        for url in (
            "http://127.0.0.1:8082/",
            "http://localhost/admin",
            "http://[::1]/",
            "http://192.168.1.1/",
            "http://10.0.0.1/",
            "http://172.16.5.5/",
            "http://169.254.1.1/",
        ):
            self.assertFalse(is_safe_url(url), url)

    def test_blocks_non_http_scheme(self) -> None:
        for url in ("file:///etc/passwd", "ftp://x/", "javascript:alert(1)", ""):
            self.assertFalse(is_safe_url(url), url)

    def test_blocks_malformed(self) -> None:
        self.assertFalse(is_safe_url("http://"))


# ----------------------------------------------------------------------
# 代理
# ----------------------------------------------------------------------


class TestProxyHandling(unittest.TestCase):
    def test_reads_env_proxy(self) -> None:
        original = dict(os.environ)
        try:
            os.environ["HTTPS_PROXY"] = "http://127.0.0.1:9999"
            self.assertEqual(proxy_from_env(), "http://127.0.0.1:9999")
        finally:
            os.environ.clear()
            os.environ.update(original)

    def test_none_when_unset(self) -> None:
        original = dict(os.environ)
        try:
            for key in (
                "HTTPS_PROXY", "https_proxy", "HTTP_PROXY",
                "http_proxy", "ALL_PROXY", "all_proxy",
            ):
                os.environ.pop(key, None)
            self.assertIsNone(proxy_from_env())
        finally:
            os.environ.clear()
            os.environ.update(original)

    def test_client_builds_with_hostile_no_proxy(self) -> None:
        """**核心回归**：NO_PROXY 里的 ``[::1]`` 曾让 httpx 抛 Invalid port。

        本项目其余 httpx client 用 trust_env=False 规避；联网搜索也需要
        代理，所以自己解析代理并显式传入，绝不走 httpx 的 env 解析。
        """
        original = dict(os.environ)
        try:
            os.environ["HTTP_PROXY"] = "http://127.0.0.1:31180/"
            os.environ["HTTPS_PROXY"] = "http://127.0.0.1:31181/"
            os.environ["NO_PROXY"] = "localhost,127.0.0.1,::1,[::1]"

            client = build_client(timeout=5)
            client.close()  # 不应抛异常
        finally:
            os.environ.clear()
            os.environ.update(original)

    def test_no_proxy_still_builds(self) -> None:
        client = build_client(timeout=5, use_proxy=False)
        client.close()

    def test_default_client_is_trust_env_false(self) -> None:
        client = build_client(timeout=5, use_proxy=False)
        try:
            self.assertFalse(client.trust_env)
        finally:
            client.close()


# ----------------------------------------------------------------------
# 链接解码
# ----------------------------------------------------------------------


class TestRedirectDecoding(unittest.TestCase):
    def test_bing_passthrough_when_normal(self) -> None:
        url = "https://nmap.org/"
        self.assertEqual(decode_bing_redirect(url), url)

    def test_bing_decodes_base64(self) -> None:
        import base64

        target = "https://example.com/page"
        payload = base64.urlsafe_b64encode(target.encode()).decode().rstrip("=")
        url = f"https://www.bing.com/ck/a?u=a1{payload}&x=1"
        self.assertEqual(decode_bing_redirect(url), target)

    def test_bing_bad_base64_keeps_original(self) -> None:
        url = "https://www.bing.com/ck/a?u=a1!!!notbase64!!!"
        self.assertEqual(decode_bing_redirect(url), url)

    def test_ddg_decodes_uddg(self) -> None:
        url = "https://duckduckgo.com/l/?uddg=https%3A%2F%2Fnmap.org%2F"
        self.assertEqual(decode_ddg_redirect(url), "https://nmap.org/")

    def test_ddg_passthrough(self) -> None:
        url = "https://nmap.org/"
        self.assertEqual(decode_ddg_redirect(url), url)


# ----------------------------------------------------------------------
# 配置
# ----------------------------------------------------------------------


class TestNormalize(unittest.TestCase):
    def test_defaults(self) -> None:
        cfg = normalize(None)
        self.assertEqual(cfg.provider, DEFAULT_PROVIDER)
        self.assertFalse(cfg.enabled)

    def test_unknown_provider_falls_back(self) -> None:
        self.assertEqual(normalize({"provider": "nope"}).provider, DEFAULT_PROVIDER)

    def test_known_provider_kept(self) -> None:
        self.assertEqual(normalize({"provider": "baidu"}).provider, "baidu")

    def test_max_results_clamped(self) -> None:
        self.assertLessEqual(normalize({"max_results": 999}).max_results, MAX_RESULTS)
        self.assertGreaterEqual(normalize({"max_results": -5}).max_results, 1)

    def test_timeout_clamped(self) -> None:
        self.assertLessEqual(normalize({"timeout": 999}).timeout, 60.0)
        self.assertGreaterEqual(normalize({"timeout": 0}).timeout, 3.0)

    def test_bad_types_fall_back(self) -> None:
        cfg = normalize({"max_results": "abc", "timeout": "xyz", "enabled": "yes"})
        self.assertEqual(cfg.max_results, 5)
        self.assertEqual(cfg.timeout, 15.0)
        self.assertFalse(cfg.enabled)

    def test_bools_enforced(self) -> None:
        self.assertTrue(normalize({"fetch_pages": True}).fetch_pages)
        self.assertTrue(normalize({"use_proxy": True}).use_proxy)

    def test_unknown_keys_ignored(self) -> None:
        cfg = normalize({"nope": 1})
        self.assertEqual(cfg.provider, DEFAULT_PROVIDER)


class TestMaskKey(unittest.TestCase):
    def test_masks_long_key(self) -> None:
        masked = mask_key("tvly-abcdefghijklmnop")
        self.assertTrue(masked.startswith("tvly"))
        self.assertIn("…", masked)
        self.assertNotIn("efghijkl", masked)

    def test_empty(self) -> None:
        self.assertEqual(mask_key(""), "")
        self.assertEqual(mask_key(None), "")  # type: ignore[arg-type]


class TestWebConfigStore(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_web_test_"))
        self.path = self.tmp / "web_search.json"
        self.store = WebConfigStore(self.path)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_defaults(self) -> None:
        cfg = self.store.get()
        self.assertEqual(cfg.provider, DEFAULT_PROVIDER)
        self.assertFalse(cfg.enabled)

    def test_update_persists(self) -> None:
        self.store.update({"provider": "baidu", "enabled": True})

        reloaded = WebConfigStore(self.path).get()
        self.assertEqual(reloaded.provider, "baidu")
        self.assertTrue(reloaded.enabled)

    def test_public_masks_key(self) -> None:
        self.store.update({"api_key": "tvly-secret-key-1234"})

        public = self.store.public()
        self.assertNotIn("secret", public["api_key"])
        self.assertTrue(public["has_key"])

    def test_empty_api_key_preserves_existing(self) -> None:
        """前端回显的是掩码，提交空 Key 不能把真 Key 冲掉。"""
        self.store.update({"api_key": "tvly-real-key-9999"})
        self.store.update({"api_key": ""})

        self.assertEqual(self.store.get().api_key, "tvly-real-key-9999")

    def test_clear_removes_key(self) -> None:
        self.store.update({"api_key": "secret", "provider": "baidu"})
        self.store.clear()

        cfg = self.store.get()
        self.assertEqual(cfg.api_key, "")
        self.assertEqual(cfg.provider, DEFAULT_PROVIDER)

    def test_invalid_value_ignored_keeps_current(self) -> None:
        """非法枚举要**保留原值**，而不是重置为默认。

        ``normalize`` 是读文件时的兜底，它分不清「用户刚发来的非法值」和
        「文件本来就坏」。所以 update 层要先校验。
        """
        self.store.update({"provider": "baidu"})
        self.store.update({"provider": "not-a-provider"})

        self.assertEqual(self.store.get().provider, "baidu")

    def test_corrupt_provider_in_file_falls_back(self) -> None:
        """但文件里本来就是坏值时，读出来要回退到默认。"""
        self.path.write_text(
            json.dumps({"provider": "garbage"}), encoding="utf-8"
        )
        self.assertEqual(
            WebConfigStore(self.path).get().provider, DEFAULT_PROVIDER
        )

    def test_corrupt_file_falls_back(self) -> None:
        self.path.write_text("{broken", encoding="utf-8")
        self.assertEqual(WebConfigStore(self.path).get().provider, DEFAULT_PROVIDER)

    def test_unwritable_path_does_not_raise(self) -> None:
        store = WebConfigStore(Path("Z:/nope/web.json"))
        store.update({"provider": "baidu"})
        self.assertEqual(store.get().provider, "baidu")

    def test_file_is_valid_json(self) -> None:
        self.store.update({"provider": "baidu"})
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data["provider"], "baidu")


# ----------------------------------------------------------------------
# 后端注册表与结果结构
# ----------------------------------------------------------------------


class TestProviders(unittest.TestCase):
    def test_default_exists(self) -> None:
        self.assertIn(DEFAULT_PROVIDER, PROVIDERS)

    def test_get_unknown_returns_default(self) -> None:
        self.assertEqual(get_provider("nope").id, DEFAULT_PROVIDER)
        self.assertEqual(get_provider(None).id, DEFAULT_PROVIDER)

    def test_catalog_marks_default(self) -> None:
        catalog = provider_catalog()
        defaults = [p for p in catalog if p["default"]]
        self.assertEqual(len(defaults), 1)
        self.assertEqual(defaults[0]["id"], DEFAULT_PROVIDER)

    def test_api_providers_declare_needs_key(self) -> None:
        for pid in ("tavily", "serper", "brave"):
            self.assertTrue(PROVIDERS[pid].needs_key, pid)
            ok, reason = PROVIDERS[pid].available("")
            self.assertFalse(ok)
            self.assertIn("Key", reason)

    def test_keyless_providers_available(self) -> None:
        for pid in ("bing", "baidu", "duckduckgo"):
            ok, _ = PROVIDERS[pid].available("")
            self.assertTrue(ok, pid)

    def test_searxng_needs_url(self) -> None:
        ok, reason = PROVIDERS["searxng"].available("", "")
        self.assertFalse(ok)
        self.assertIn("地址", reason)


class TestToResultDict(unittest.TestCase):
    def test_shape_matches_local_results(self) -> None:
        item = WebResult(
            title="标题",
            url="https://example.com/a",
            snippet="摘要",
            content="正文",
            engine="bing",
            rank=0,
        )
        result = to_result_dict(item, 1)

        payload = result["payload"]
        metadata = payload["metadata"]

        self.assertEqual(payload["content"], "正文")
        self.assertEqual(metadata["source_type"], "web")
        self.assertEqual(metadata["url"], "https://example.com/a")
        self.assertEqual(metadata["domain"], "example.com")
        self.assertTrue(payload["chunk_id"].startswith("web::"))

    def test_falls_back_to_snippet(self) -> None:
        item = WebResult(title="t", url="https://e.com", snippet="只有摘要")
        result = to_result_dict(item, 1)
        self.assertEqual(result["payload"]["content"], "只有摘要")

    def test_stable_id(self) -> None:
        item = WebResult(title="t", url="https://e.com/x")
        self.assertEqual(
            to_result_dict(item, 1)["id"], to_result_dict(item, 1)["id"]
        )


# ----------------------------------------------------------------------
# 编排（用假后端，不发网络请求）
# ----------------------------------------------------------------------


class FakeProvider:
    id = "fake"
    label = "Fake"
    needs_key = False
    needs_url = False

    def __init__(self, results=None, error=None):
        self._results = results or []
        self._error = error
        self.calls = 0

    def search(self, query, **kwargs):
        self.calls += 1
        if self._error:
            raise self._error
        return list(self._results)

    def available(self, api_key="", base_url=""):
        return True, ""


class TestWebSearcher(unittest.TestCase):
    def _settings(self, **kwargs) -> WebSettings:
        base = dict(
            enabled=True, provider="bing", max_results=3,
            fetch_pages=False, fetch_top_n=0, use_proxy=False,
        )
        base.update(kwargs)
        return WebSettings(**base)

    def test_empty_query(self) -> None:
        outcome = WebSearcher().search("   ", settings=self._settings())
        self.assertFalse(outcome.ok)
        self.assertIn("空", outcome.error)

    def test_search_returns_converted_results(self) -> None:
        provider = FakeProvider([
            WebResult(title="A", url="https://a.com", snippet="sa"),
            WebResult(title="B", url="https://b.com", snippet="sb"),
        ])
        outcome = WebSearcher().search(
            "查询", provider=provider, settings=self._settings()
        )

        self.assertTrue(outcome.ok)
        self.assertEqual(len(outcome.results), 2)
        self.assertEqual(outcome.results[0]["payload"]["metadata"]["source_type"], "web")

    def test_limit_respected(self) -> None:
        provider = FakeProvider([
            WebResult(title=str(i), url=f"https://e{i}.com") for i in range(10)
        ])
        outcome = WebSearcher().search(
            "查询", limit=2, provider=provider, settings=self._settings()
        )
        self.assertEqual(len(outcome.results), 2)

    def test_provider_exception_becomes_error_not_raise(self) -> None:
        """联网失败绝不能把整个问答带崩。"""
        provider = FakeProvider(error=RuntimeError("网络炸了"))
        outcome = WebSearcher().search(
            "查询", provider=provider, settings=self._settings()
        )

        self.assertFalse(outcome.ok)
        self.assertIn("网络炸了", outcome.error)
        self.assertEqual(outcome.results, [])

    def test_missing_key_reports_error(self) -> None:
        outcome = WebSearcher().search(
            "查询",
            settings=self._settings(provider="tavily"),
        )
        self.assertFalse(outcome.ok)
        self.assertIn("Key", outcome.error)

    def test_summary_fields(self) -> None:
        provider = FakeProvider([WebResult(title="A", url="https://a.com")])
        outcome = WebSearcher().search(
            "查询", provider=provider, settings=self._settings()
        )
        summary = outcome.summary()

        for key in ("provider", "count", "fetched_pages", "elapsed_ms", "error"):
            self.assertIn(key, summary)


if __name__ == "__main__":
    unittest.main()
