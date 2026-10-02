"""检索路由器测试：判断一次提问是否需要查知识库。

重要回归：「那它需要什么权限？」这类**上下文追问**曾被误判为闲聊，
答案因此完全不引用资料。有历史时命中追问特征必须走检索。
"""

from __future__ import annotations

import unittest

from src.llm.base import ChatMessage
from src.rag.router import (
    looks_like_followup,
    needs_retrieval,
    quick_route,
    should_answer_directly,
)


class FakeLlm:
    """可控的假模型。"""

    def __init__(self, output: str = "NEED", fail: bool = False) -> None:
        self.output = output
        self.fail = fail
        self.calls: list[list] = []

    def chat(self, messages, **kwargs):
        self.calls.append(messages)

        if self.fail:
            raise RuntimeError("模拟路由失败")

        class Reply:
            content = self.output

        return Reply()


HISTORY = [
    {"role": "user", "content": "nmap 的 -sS 参数是什么"},
    {"role": "assistant", "content": "SYN 半开扫描…"},
]


class TestQuickRoute(unittest.TestCase):
    def test_greetings_skip_retrieval(self) -> None:
        for text in ("你好", "你好呀", "您好", "hi", "Hello", "哈喽", "在吗"):
            self.assertIs(quick_route(text), False, f"{text} 应跳过检索")

    def test_thanks_skip_retrieval(self) -> None:
        for text in ("谢谢", "多谢", "感谢", "thanks", "好的", "嗯", "收到"):
            self.assertIs(quick_route(text), False, f"{text} 应跳过检索")

    def test_meta_questions_skip_retrieval(self) -> None:
        for text in ("你是谁", "你能做什么", "你叫什么", "我刚才问了什么"):
            self.assertIs(quick_route(text), False, f"{text} 应跳过检索")

    def test_punctuation_only(self) -> None:
        for text in ("。。。", "？！", "~"):
            self.assertIs(quick_route(text), False)

    def test_empty(self) -> None:
        self.assertIs(quick_route(""), False)

    def test_technical_questions_are_undecided(self) -> None:
        for text in (
            "nmap 的 -sS 参数是什么",
            "怎么配置 Qdrant",
            "Burp Suite 如何拦截请求",
        ):
            self.assertIsNone(quick_route(text), f"{text} 应交由模型判断")

    def test_greeting_with_trailing_punctuation(self) -> None:
        self.assertIs(quick_route("你好！！！"), False)


class TestLooksLikeFollowup(unittest.TestCase):
    def test_pronoun_reference(self) -> None:
        for text in ("那它需要什么权限？", "这个怎么用", "它是什么"):
            self.assertTrue(looks_like_followup(text), text)

    def test_ordinal_reference(self) -> None:
        for text in ("第二种扫描方式呢？", "第二点呢", "第3步是什么"):
            self.assertTrue(looks_like_followup(text), text)

    def test_elaboration_request(self) -> None:
        for text in ("再详细说说", "再讲讲原理", "继续", "还有呢"):
            self.assertTrue(looks_like_followup(text), text)

    def test_standalone_question_is_not_followup(self) -> None:
        for text in ("nmap 的 -sS 参数是什么", "怎么配置数据库"):
            self.assertFalse(looks_like_followup(text), text)

    def test_empty(self) -> None:
        self.assertFalse(looks_like_followup(""))


class TestNeedsRetrieval(unittest.TestCase):
    def test_disabled_always_retrieves(self) -> None:
        need, reason = needs_retrieval("你好", None, FakeLlm(), enabled=False)
        self.assertTrue(need)
        self.assertIn("关闭", reason)

    def test_rules_win_over_model(self) -> None:
        llm = FakeLlm("NEED")
        need, reason = needs_retrieval("你好", None, llm)

        self.assertFalse(need)
        self.assertIn("规则", reason)
        self.assertEqual(llm.calls, [], "规则能判定时不应调用模型")

    def test_followup_with_history_retrieves(self) -> None:
        """核心回归：追问必须走检索，不能被判成闲聊。"""
        llm = FakeLlm("NO")  # 即使模型说不需要

        need, reason = needs_retrieval("那它需要什么权限？", HISTORY, llm)

        self.assertTrue(need, "有历史时的追问应强制走检索")
        self.assertIn("追问", reason)
        self.assertEqual(llm.calls, [], "追问规则应优先于模型判断")

    def test_followup_without_history_defers_to_model(self) -> None:
        llm = FakeLlm("NEED")
        need, _ = needs_retrieval("那它需要什么权限？", [], llm)
        self.assertTrue(need)
        self.assertEqual(len(llm.calls), 1)

    def test_model_says_no(self) -> None:
        llm = FakeLlm("NO")
        need, reason = needs_retrieval("今天天气怎么样", None, llm)
        self.assertFalse(need)
        self.assertIn("模型", reason)

    def test_parses_various_outputs(self) -> None:
        for raw, expected in (
            ("NEED", True), ("need", True), ("NEED.", True),
            ("NO", False), ("no", False), ("NO.", False),
            ("NEED\n", True), ("NO 不需要", False),
        ):
            need, _ = needs_retrieval("某个问题", None, FakeLlm(raw))
            self.assertEqual(need, expected, f"{raw!r} 解析错误")

    def test_unparseable_output_is_conservative(self) -> None:
        """看不懂就保守走检索 —— 宁可多查一次。"""
        need, reason = needs_retrieval("某个问题", None, FakeLlm("???"))
        self.assertTrue(need)
        self.assertIn("保守", reason)

    def test_model_failure_is_conservative(self) -> None:
        need, reason = needs_retrieval("某个问题", None, FakeLlm(fail=True))
        self.assertTrue(need)
        self.assertIn("保守", reason)

    def test_history_is_passed_to_model(self) -> None:
        llm = FakeLlm("NEED")
        needs_retrieval("某个技术问题", HISTORY, llm)

        payload = " ".join(
            m.text if isinstance(m, ChatMessage) else str(m)
            for m in llm.calls[0]
        )
        self.assertIn("nmap", payload, "历史应作为判断依据传给模型")

    def test_should_answer_directly_helper(self) -> None:
        self.assertTrue(should_answer_directly("你好", None, FakeLlm()))
        self.assertFalse(
            should_answer_directly("那它呢", HISTORY, FakeLlm("NEED"))
        )


if __name__ == "__main__":
    unittest.main()
