"""Markdown 切块器测试。

重点回归：``split_into_blocks`` 的代码围栏关闭条件曾写反
（``stripped != fence``），导致 ``` 永远关不掉，代码块之后的整节内容
被并进同一个 block。
"""

from __future__ import annotations

import unittest

from src.ingest.chunker import (
    build_context_prefix,
    normalize_text,
    parse_heading,
    parse_markdown,
    split_into_blocks,
    split_long_block,
)


class TestParseHeading(unittest.TestCase):
    def test_basic_levels(self) -> None:
        self.assertEqual(parse_heading("# 标题"), (1, "标题"))
        self.assertEqual(parse_heading("### 三级"), (3, "三级"))

    def test_strips_trailing_hashes(self) -> None:
        self.assertEqual(parse_heading("## Python ##"), (2, "Python"))

    def test_rejects_non_heading(self) -> None:
        self.assertIsNone(parse_heading("普通文本"))
        self.assertIsNone(parse_heading("#没有空格"))


class TestParseMarkdown(unittest.TestCase):
    def test_document_title_and_hierarchy(self) -> None:
        text = (
            "# 文档标题\n\n"
            "## Python\n\n"
            "内容 A\n\n"
            "### os 模块\n\n"
            "内容 B\n"
        )
        title, sections = parse_markdown(text)

        self.assertEqual(title, "文档标题")

        hierarchies = [s.hierarchy for s in sections]
        self.assertIn(["文档标题", "Python"], hierarchies)
        self.assertIn(["文档标题", "Python", "os 模块"], hierarchies)

    def test_headings_inside_code_block_ignored(self) -> None:
        text = (
            "# 标题\n\n"
            "## 代码\n\n"
            "```python\n"
            "# 这不是标题\n"
            "## 这也不是\n"
            "```\n"
        )
        _title, sections = parse_markdown(text)

        for section in sections:
            self.assertNotIn("这不是标题", section.hierarchy)
            self.assertNotIn("这也不是", section.hierarchy)


class TestSplitIntoBlocks(unittest.TestCase):
    def test_plain_paragraphs_split_on_blank_line(self) -> None:
        blocks = split_into_blocks(["第一段", "", "第二段"])
        self.assertEqual(blocks, [["第一段"], ["第二段"]])

    def test_code_fence_closes_properly(self) -> None:
        """核心回归：围栏必须能关闭，之后的文本要独立成块。"""
        lines = [
            "```bash",
            "nmap -sS 192.168.1.1",
            "```",
            "",
            "这段文字必须在代码块之外",
        ]
        blocks = split_into_blocks(lines)

        self.assertEqual(len(blocks), 2, f"期望 2 个 block，实际: {blocks}")

        code_block, text_block = blocks
        self.assertIn("```bash", code_block)
        self.assertIn("nmap -sS 192.168.1.1", code_block)
        self.assertEqual(text_block, ["这段文字必须在代码块之外"])

    def test_text_after_two_code_blocks(self) -> None:
        lines = [
            "```",
            "code1",
            "```",
            "",
            "中间文字",
            "",
            "```",
            "code2",
            "```",
            "",
            "结尾文字",
        ]
        blocks = split_into_blocks(lines)
        flat = ["\n".join(b) for b in blocks]

        self.assertIn("中间文字", flat)
        self.assertIn("结尾文字", flat)
        self.assertIn("code1", flat[0])
        self.assertIn("code2", flat[2])

    def test_tilde_fence(self) -> None:
        lines = ["~~~", "code", "~~~", "", "之后"]
        blocks = split_into_blocks(lines)
        self.assertEqual(len(blocks), 2)

    def test_table_kept_together(self) -> None:
        lines = [
            "| 参数 | 说明 |",
            "|------|------|",
            "| -sS  | SYN  |",
        ]
        blocks = split_into_blocks(lines)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(len(blocks[0]), 3)

    def test_unclosed_fence_swallows_rest(self) -> None:
        """围栏未闭合时，后续内容确实都属于代码块（正确行为）。"""
        lines = ["```", "code", "没有闭合"]
        blocks = split_into_blocks(lines)
        self.assertEqual(len(blocks), 1)


class TestNormalizeText(unittest.TestCase):
    def test_collapses_blank_lines(self) -> None:
        self.assertEqual(normalize_text("a\n\n\n\nb"), "a\n\nb")

    def test_strips_trailing_whitespace(self) -> None:
        self.assertEqual(normalize_text("a   \nb\t"), "a\nb")

    def test_normalizes_crlf(self) -> None:
        self.assertEqual(normalize_text("a\r\nb"), "a\nb")


class TestSplitLongBlock(unittest.TestCase):
    def test_splits_on_lines(self) -> None:
        pieces = split_long_block(["a" * 10, "b" * 10, "c" * 10], max_chars=15)
        self.assertGreater(len(pieces), 1)

    def test_splits_very_long_single_line(self) -> None:
        pieces = split_long_block(["x" * 100], max_chars=30)
        self.assertEqual(len(pieces), 4)

    def test_rejects_zero_max_chars(self) -> None:
        with self.assertRaises(ValueError):
            split_long_block(["a"], max_chars=0)


class TestContextPrefix(unittest.TestCase):
    def test_includes_document_and_section(self) -> None:
        prefix = build_context_prefix("Python 知识点", ["文件操作", "os.path"])
        self.assertIn("文档：Python 知识点", prefix)
        self.assertIn("章节：文件操作 > os.path", prefix)

    def test_empty_when_nothing(self) -> None:
        self.assertEqual(build_context_prefix("", []), "")


if __name__ == "__main__":
    unittest.main()
