"""多轮对话测试：会话模型、历史裁剪、持久化、追问改写。"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from src.rag.chat import condense_query, sanitize_text
from src.rag.conversation import (
    Conversation,
    ConversationStore,
    Turn,
)


def make_turn(index: int, question: str, answer: str = "") -> Turn:
    return Turn(
        index=index,
        question=question,
        answer=answer or f"回答{index}",
        citations=[{"index": 1, "file_name": "doc.md", "section": "章节"}],
    )


class TestTurn(unittest.TestCase):
    def test_rewrite_detection(self) -> None:
        turn = Turn(index=0, question="那它呢", retrieval_query="nmap -sS 是什么")
        self.assertTrue(turn.is_rewritten)

    def test_not_rewritten_when_same(self) -> None:
        turn = Turn(
            index=0, question="nmap -sS", retrieval_query="nmap -sS"
        )
        self.assertFalse(turn.is_rewritten)

    def test_not_rewritten_when_empty_query(self) -> None:
        turn = Turn(index=0, question="nmap -sS")
        self.assertFalse(turn.is_rewritten)

    def test_whitespace_only_difference_is_not_rewrite(self) -> None:
        turn = Turn(
            index=0, question="nmap  -sS", retrieval_query="nmap  -sS "
        )
        self.assertFalse(turn.is_rewritten)


class TestConversationHistory(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(Conversation(id="x").history(), [])

    def test_pairs_in_order(self) -> None:
        c = Conversation(id="x")
        c.turns = [make_turn(0, "Q1"), make_turn(1, "Q2")]

        history = c.history()

        self.assertEqual(len(history), 4)
        self.assertEqual(history[0], {"role": "user", "content": "Q1"})
        self.assertEqual(history[1], {"role": "assistant", "content": "回答0"})
        self.assertEqual(history[2]["content"], "Q2")

    def test_limits_turn_count(self) -> None:
        c = Conversation(id="x")
        c.turns = [make_turn(i, f"Q{i}") for i in range(10)]

        history = c.history(max_turns=3)

        # 只保留最近 3 轮
        self.assertEqual(len(history), 6)
        self.assertIn("Q9", history[-2]["content"])

    def test_char_budget_drops_oldest(self) -> None:
        c = Conversation(id="x")
        for i in range(6):
            c.turns.append(
                Turn(index=i, question=f"Q{i}", answer="A" * 400)
            )

        history = c.history(max_turns=10, max_chars=1000)

        # 最近的轮次必须在，最旧的应被丢掉
        contents = [m["content"] for m in history]
        self.assertTrue(any("Q5" in c for c in contents))
        self.assertFalse(any(m["content"] == "Q0" for m in history))

    def test_skips_turns_without_answer(self) -> None:
        c = Conversation(id="x")
        c.turns = [
            Turn(index=0, question="Q1", answer=""),
            make_turn(1, "Q2"),
        ]

        history = c.history()

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "Q2")

    def test_zero_turns_returns_empty(self) -> None:
        c = Conversation(id="x")
        c.turns = [make_turn(0, "Q1")]
        self.assertEqual(c.history(max_turns=0), [])


class TestConversationMeta(unittest.TestCase):
    def test_preview_uses_first_question(self) -> None:
        c = Conversation(id="x")
        c.turns = [make_turn(0, "第一个问题"), make_turn(1, "第二个问题")]
        self.assertEqual(c.preview(), "第一个问题")

    def test_preview_truncates(self) -> None:
        c = Conversation(id="x")
        c.turns = [make_turn(0, "问" * 200)]
        self.assertLessEqual(len(c.preview(limit=10)), 11)

    def test_preview_empty(self) -> None:
        self.assertEqual(Conversation(id="x").preview(), "（空会话）")

    def test_roundtrip_dict(self) -> None:
        c = Conversation(id="abc", title="标题")
        c.turns = [make_turn(0, "Q1")]

        restored = Conversation.from_dict(c.to_dict())

        self.assertEqual(restored.id, "abc")
        self.assertEqual(restored.title, "标题")
        self.assertEqual(len(restored.turns), 1)
        self.assertEqual(restored.turns[0].question, "Q1")

    def test_to_dict_without_turns(self) -> None:
        c = Conversation(id="abc")
        c.turns = [make_turn(0, "Q1")]

        data = c.to_dict(include_turns=False)

        self.assertNotIn("turns", data)
        self.assertEqual(data["turn_count"], 1)

    def test_from_dict_tolerates_missing_fields(self) -> None:
        restored = Conversation.from_dict({"id": "z"})
        self.assertEqual(restored.id, "z")
        self.assertEqual(restored.turns, [])

    def test_from_dict_ignores_unknown_turn_fields(self) -> None:
        restored = Conversation.from_dict(
            {
                "id": "z",
                "turns": [{"index": 0, "question": "Q", "unknown_field": 1}],
            }
        )
        self.assertEqual(restored.turns[0].question, "Q")


class TestConversationStore(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rag_conv_test_"))
        self.store = ConversationStore(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_create_and_get(self) -> None:
        c = self.store.create()
        self.assertTrue(c.id)
        self.assertIsNotNone(self.store.get(c.id))

    def test_get_unknown_returns_none(self) -> None:
        self.assertIsNone(self.store.get("nope"))
        self.assertIsNone(self.store.get(""))

    def test_get_or_create_reuses_existing(self) -> None:
        c = self.store.create()
        again = self.store.get_or_create(c.id)
        self.assertEqual(again.id, c.id)

    def test_get_or_create_makes_new(self) -> None:
        created = self.store.get_or_create("does-not-exist")
        self.assertTrue(created.id)
        self.assertNotEqual(created.id, "does-not-exist")

    def test_append_turn_persists(self) -> None:
        c = self.store.create()
        self.store.append_turn(c, make_turn(0, "Q1"))

        # 清掉内存缓存后应从磁盘读回
        self.store._cache.clear()
        reloaded = self.store.get(c.id)

        self.assertIsNotNone(reloaded)
        self.assertEqual(len(reloaded.turns), 1)  # type: ignore[union-attr]

    def test_first_turn_sets_title(self) -> None:
        c = self.store.create()
        self.assertEqual(c.title, "新对话")

        self.store.append_turn(c, make_turn(0, "nmap 的 -sS 参数是什么"))

        self.assertIn("nmap", c.title)
        self.assertNotEqual(c.title, "新对话")

    def test_long_title_truncated(self) -> None:
        c = self.store.create()
        self.store.append_turn(c, make_turn(0, "问" * 100))
        self.assertLessEqual(len(c.title), 31)

    def test_list_sorted_by_updated(self) -> None:
        first = self.store.create()
        self.store.append_turn(first, make_turn(0, "Q1"))

        second = self.store.create()
        self.store.append_turn(second, make_turn(0, "Q2"))

        items = self.store.list()
        ids = [i["id"] for i in items]

        self.assertEqual(len(items), 2)
        self.assertIn(first.id, ids)
        self.assertIn(second.id, ids)
        # 列表项不含明细
        self.assertNotIn("turns", items[0])

    def test_delete(self) -> None:
        c = self.store.create()
        self.assertTrue(self.store.delete(c.id))
        self.assertIsNone(self.store.get(c.id))
        self.assertFalse(self.store.delete(c.id))

    def test_id_path_escape_is_blocked(self) -> None:
        """会话 id 来自 URL，必须严格校验而不是「清洗后别名」。"""
        from src.rag.conversation import is_valid_id

        c = self.store.create()

        self.assertIsNone(self.store.get("../" + c.id))
        self.assertIsNone(self.store.get("..\\" + c.id))
        self.assertIsNone(self.store.get("a/b"))
        self.assertIsNone(self.store.get("a.b"))
        self.assertFalse(self.store.delete("../" + c.id))

        self.assertTrue(is_valid_id(c.id))
        self.assertFalse(is_valid_id("../x"))
        self.assertFalse(is_valid_id(""))
        self.assertFalse(is_valid_id(None))  # type: ignore[arg-type]
        self.assertFalse(is_valid_id("x" * 100))

    def test_nothing_is_creatable_outside_directory(self) -> None:
        self.store.create()
        files = list(self.tmp.glob("*.json"))
        self.assertTrue(files)
        for path in files:
            self.assertEqual(path.parent, self.tmp)

    def test_corrupt_file_returns_none(self) -> None:
        path = self.tmp / "broken.json"
        path.write_text("{not json", encoding="utf-8")
        self.assertIsNone(self.store.get("broken"))

    def test_save_survives_unwritable(self) -> None:
        """落盘失败不应影响对话本身。"""
        c = self.store.create()
        self.store.directory = Path("Z:/definitely/not/here")
        self.store.append_turn(c, make_turn(0, "Q"))
        self.assertEqual(len(c.turns), 1)


class FakeLlm:
    """可控的假生成模型。"""

    def __init__(self, output: str = "", fail: bool = False) -> None:
        self.output = output
        self.fail = fail
        self.calls: list[list] = []

    def chat(self, messages, **kwargs):
        self.calls.append(messages)

        if self.fail:
            raise RuntimeError("模拟失败")

        class Reply:
            content = self.output

        return Reply()


class TestCondenseQuery(unittest.TestCase):
    def test_no_history_is_noop(self) -> None:
        llm = FakeLlm("改写结果")
        query, rewritten = condense_query("nmap -sS", [], llm)

        self.assertEqual(query, "nmap -sS")
        self.assertFalse(rewritten)
        self.assertEqual(llm.calls, [], "没有历史时不应调用模型")

    def test_disabled_is_noop(self) -> None:
        llm = FakeLlm("改写结果")
        history = [{"role": "user", "content": "Q"}]

        query, rewritten = condense_query(
            "那它呢", history, llm, enabled=False
        )

        self.assertEqual(query, "那它呢")
        self.assertFalse(rewritten)
        self.assertEqual(llm.calls, [])

    def test_rewrites_with_history(self) -> None:
        llm = FakeLlm("nmap -sS 需要什么权限")
        history = [
            {"role": "user", "content": "nmap 的 -sS 是什么"},
            {"role": "assistant", "content": "SYN 半开扫描"},
        ]

        query, rewritten = condense_query("那它需要什么权限", history, llm)

        self.assertEqual(query, "nmap -sS 需要什么权限")
        self.assertTrue(rewritten)
        self.assertEqual(len(llm.calls), 1)

    def test_strips_quotes_and_preamble(self) -> None:
        for raw in ["「nmap -sS 权限」", '"nmap -sS 权限"', "nmap -sS 权限\n补充"]:
            llm = FakeLlm(raw)
            query, _ = condense_query(
                "那它呢", [{"role": "user", "content": "Q"}], llm
            )
            self.assertNotIn("「", query)
            self.assertNotIn('"', query)
            self.assertNotIn("\n", query)

    def test_empty_model_output_falls_back(self) -> None:
        llm = FakeLlm("   ")
        query, rewritten = condense_query(
            "原问题", [{"role": "user", "content": "Q"}], llm
        )
        self.assertEqual(query, "原问题")
        self.assertFalse(rewritten)

    def test_overlong_output_falls_back(self) -> None:
        llm = FakeLlm("长" * 500)
        query, rewritten = condense_query(
            "原问题", [{"role": "user", "content": "Q"}], llm
        )
        self.assertEqual(query, "原问题")
        self.assertFalse(rewritten)

    def test_model_failure_falls_back(self) -> None:
        """改写失败绝不能中断对话。"""
        llm = FakeLlm(fail=True)
        query, rewritten = condense_query(
            "原问题", [{"role": "user", "content": "Q"}], llm
        )
        self.assertEqual(query, "原问题")
        self.assertFalse(rewritten)

    def test_identical_output_counts_as_not_rewritten(self) -> None:
        llm = FakeLlm("那它呢")
        query, rewritten = condense_query(
            "那它呢", [{"role": "user", "content": "Q"}], llm
        )
        self.assertEqual(query, "那它呢")
        self.assertFalse(rewritten)

    def test_empty_question(self) -> None:
        llm = FakeLlm("x")
        query, rewritten = condense_query(
            "", [{"role": "user", "content": "Q"}], llm
        )
        self.assertEqual(query, "")
        self.assertFalse(rewritten)


class TestSanitizeText(unittest.TestCase):
    def test_removes_lone_surrogates(self) -> None:
        """Windows 管道输入可能产生 \\udcXX，不清理会让 JSON 请求崩掉。"""
        fixed = sanitize_text("nmap \udc84\udc80 参数")

        self.assertNotIn("\udc84", fixed)
        self.assertIn("nmap", fixed)
        # 清理后必须能正常编码
        fixed.encode("utf-8")

    def test_preserves_normal_text(self) -> None:
        text = "正常的中文 English 123"
        self.assertEqual(sanitize_text(text), text)

    def test_empty(self) -> None:
        self.assertEqual(sanitize_text(""), "")

    def test_none_like(self) -> None:
        self.assertEqual(sanitize_text(None), None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
