"""Context 拼接与引用生成测试。

重点回归：``payload.get("metadata", {})`` 在 metadata 为 ``None`` 时
会抛 AttributeError。
"""

from __future__ import annotations

import unittest

from src.rag.context import build_citations, build_context, citation_of


def make_result(
    content: str = "正文内容",
    *,
    chunk_id: str = "doc::sec::001",
    section: str = "章节 A",
    source: str = "doc.md",
    metadata=None,
    score: float = 0.5,
) -> dict:
    return {
        "id": chunk_id,
        "score": score,
        "payload": {
            "chunk_id": chunk_id,
            "title": "文档标题",
            "section": section,
            "content": content,
            "source": source,
            "metadata": metadata,
        },
    }


class TestBuildContext(unittest.TestCase):
    def test_adds_numbered_prefix(self) -> None:
        context = build_context([make_result("A"), make_result("B")])

        self.assertIn("[1]", context)
        self.assertIn("[2]", context)
        self.assertLess(context.index("[1]"), context.index("[2]"))

    def test_numbering_can_be_disabled(self) -> None:
        context = build_context([make_result("A")], numbered=False)
        self.assertNotIn("[1]", context)
        self.assertIn("A", context)

    def test_metadata_none_does_not_crash(self) -> None:
        """核心回归：metadata 为 None。"""
        context = build_context([make_result("A", metadata=None)])
        self.assertIn("A", context)

    def test_metadata_missing_key(self) -> None:
        context = build_context([make_result("A", metadata={})])
        self.assertIn("doc.md", context)

    def test_payload_none_does_not_crash(self) -> None:
        context = build_context([{"id": "x", "payload": None}])
        self.assertIsInstance(context, str)

    def test_empty_results(self) -> None:
        self.assertEqual(build_context([]), "")

    def test_truncates_long_chunk(self) -> None:
        context = build_context([make_result("x" * 100000)])
        self.assertLess(len(context), 20000)

    def test_respects_max_chars(self) -> None:
        results = [make_result("y" * 400) for _ in range(20)]
        context = build_context(results, max_chars=1000)
        # 至少保留第一块，且不会把所有块都塞进去
        self.assertLess(len(context), 4000)

    def test_page_included_when_present(self) -> None:
        context = build_context([make_result("A", metadata={"page": 7})])
        self.assertIn("第 7 页", context)

    def test_source_and_section_included(self) -> None:
        context = build_context(
            [make_result("A", section="端口扫描 > -sS", metadata={"file_name": "nmap.md"})]
        )
        self.assertIn("nmap.md", context)
        self.assertIn("端口扫描 > -sS", context)


class TestCitations(unittest.TestCase):
    def test_citation_fields(self) -> None:
        citation = citation_of(make_result(score=0.88), 3)

        self.assertEqual(citation["index"], 3)
        self.assertEqual(citation["chunk_id"], "doc::sec::001")
        self.assertEqual(citation["section"], "章节 A")
        self.assertEqual(citation["score"], 0.88)

    def test_citation_uses_file_name_from_metadata(self) -> None:
        citation = citation_of(
            make_result(metadata={"file_name": "nmap知识点.md"}), 1
        )
        self.assertEqual(citation["file_name"], "nmap知识点.md")

    def test_citation_falls_back_to_source(self) -> None:
        citation = citation_of(make_result(source="File/Markdown/x.md"), 1)
        self.assertEqual(citation["file_name"], "File/Markdown/x.md")

    def test_citations_numbering_matches_context(self) -> None:
        results = [make_result("A"), make_result("B")]
        context = build_context(results)
        citations = build_citations(results)

        self.assertEqual([c["index"] for c in citations], [1, 2])
        self.assertIn("[1]", context)
        self.assertIn("[2]", context)

    def test_preview_is_truncated(self) -> None:
        citation = citation_of(make_result("z" * 5000), 1)
        self.assertLessEqual(len(citation["preview"]), 200)

    # ------------------------------------------------------------------
    # 多模态：引用需携带图片信息
    #
    # 流式问答的 citations 事件不带完整 results，因此 citation 本身必须能
    # 判断「这是不是图片」以及「图在哪」。
    # ------------------------------------------------------------------

    def test_text_citation_defaults(self) -> None:
        citation = citation_of(make_result(), 1)
        self.assertEqual(citation["modality"], "text")
        self.assertFalse(citation["is_image"])
        self.assertEqual(citation["image_path"], "")

    def test_image_citation_carries_path(self) -> None:
        result = make_result(
            "图片：pic.png\n一张示意图",
            chunk_id="pic::image::001",
            metadata={
                "modality": "image",
                "image_path": "sub/pic.png",
                "file_name": "pic.png",
            },
        )

        citation = citation_of(result, 1)

        self.assertEqual(citation["modality"], "image")
        self.assertTrue(citation["is_image"])
        self.assertEqual(citation["image_path"], "sub/pic.png")

    def test_image_citation_survives_missing_metadata(self) -> None:
        citation = citation_of(make_result(metadata=None), 1)
        self.assertEqual(citation["modality"], "text")
        self.assertFalse(citation["is_image"])

    def test_citations_list_marks_images(self) -> None:
        text = make_result("文本", chunk_id="a::001")
        image = make_result(
            "图片：p.png",
            chunk_id="p::image::001",
            metadata={"modality": "image", "image_path": "p.png"},
        )

        citations = build_citations([text, image])

        self.assertFalse(citations[0]["is_image"])
        self.assertTrue(citations[1]["is_image"])
        self.assertEqual(citations[1]["image_path"], "p.png")


if __name__ == "__main__":
    unittest.main()
