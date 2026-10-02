"""
Markdown 文档切块器

功能：
    1. 读取 Markdown 文件
    2. 识别 # / ## / ### ... 标题层级
    3. 为每个 Chunk 保留标题上下文
    4. 过长 Section 自动二次切块
    5. 尽量保持代码块、表格的完整性
    6. 支持 Chunk Overlap
    7. 生成适合后续 Embedding / RAG 使用的结构化 Chunk

输出结构示例：

Chunk(
    chunk_id="nmap知识点::端口扫描::001",
    doc_id="nmap知识点",
    title="Nmap 知识点",
    section="端口扫描 > -sS",
    content="...",
    source="File/Markdown/nmap知识点.md",
    metadata={
        "file_name": "nmap知识点.md",
        "extension": ".md",
        "heading_level": 3,
        "chunk_index": 1,
    }
)
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# 导入引导
#
# 既要支持 `python -m src.ingest.chunker`，也要支持直接 `python src/ingest/chunker.py`。
# 后者的 sys.path[0] 是 src/ingest，找不到顶层 src 包，因此这里显式把项目根
# 目录塞进 sys.path。旧的 try/except ImportError 兜底是坏的（会去 import 一个
# 并不存在的顶层 config 模块）。
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.config import CHUNK_CONFIG, MARKDOWN_DIR  # noqa: E402


# ============================================================================
# 数据结构
# ============================================================================


@dataclass
class Chunk:
    """
    RAG Chunk。

    这个对象会在后续阶段被：
        Chunk
          ↓
        Embedding
          ↓
        Vector DB
    """

    chunk_id: str

    # 文档 ID
    doc_id: str

    # 文档标题
    title: str

    # Markdown 章节路径
    # 例如：
    #   网络扫描 > TCP 扫描 > SYN 扫描
    section: str

    # 实际进入 embedding 的文本
    content: str

    # 原始文件
    source: str

    # 额外元数据
    metadata: dict[str, object] = field(default_factory=dict)

    # 当前 chunk 在文档中的顺序
    chunk_index: int = 0

    # 原始 heading 层级
    heading_level: int = 0

    def to_dict(self) -> dict[str, object]:
        """
        转为普通 dict，方便后续 JSON / Qdrant payload 使用。
        """

        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "title": self.title,
            "section": self.section,
            "content": self.content,
            "source": self.source,
            "chunk_index": self.chunk_index,
            "heading_level": self.heading_level,
            "metadata": self.metadata,
        }


# ============================================================================
# Markdown Section
# ============================================================================


@dataclass
class MarkdownSection:
    """
    Markdown 的一个逻辑 Section。

    例如：

    ## Python
    内容……

    ### os 模块
    内容……

    最终会保存：
        heading = "os 模块"
        level = 3
        hierarchy = ["Python", "os 模块"]
    """

    heading: str

    level: int

    hierarchy: list[str]

    lines: list[str] = field(default_factory=list)

    def text(self) -> str:
        return "\n".join(self.lines).strip()


# ============================================================================
# Markdown 标题
# ============================================================================


_HEADING_RE = re.compile(
    r"^( {0,3})(#{1,6})[ \t]+(.+?)\s*$"
)


def parse_heading(line: str) -> tuple[int, str] | None:
    """
    识别 Markdown ATX 标题。

    支持：

        # 标题
        ## 标题
        ### 标题

    不识别代码块内部的 # 标记。
    """

    match = _HEADING_RE.match(line)

    if not match:
        return None

    level = len(match.group(2))
    heading = match.group(3).strip()

    # 去除标题末尾可能存在的关闭 #
    # 例如：
    # ## Python ##
    heading = re.sub(r"\s+#+\s*$", "", heading).strip()

    return level, heading


# ============================================================================
# Markdown 解析
# ============================================================================


def parse_markdown(text: str) -> tuple[str, list[MarkdownSection]]:
    """
    将 Markdown 文本解析成：

        document_title
        sections

    注意：
        解析过程会避免将代码块内部的内容识别成标题。
    """

    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    document_title = ""

    sections: list[MarkdownSection] = []

    # 当前标题层级栈
    #
    # [(level, title), ...]
    heading_stack: list[tuple[int, str]] = []

    current_section: MarkdownSection | None = None

    in_code_block = False
    code_fence = ""

    for line in lines:
        stripped = line.strip()

        # ---------------------------------------------------------------
        # fenced code block
        # ---------------------------------------------------------------
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]

            if not in_code_block:
                in_code_block = True
                code_fence = fence
            elif fence == code_fence:
                in_code_block = False

            if current_section is None:
                current_section = MarkdownSection(
                    heading="",
                    level=0,
                    hierarchy=[],
                )

            current_section.lines.append(line)
            continue

        # ---------------------------------------------------------------
        # 代码块内部：
        # 绝对不能识别 Markdown 标题
        # ---------------------------------------------------------------
        if in_code_block:
            if current_section is None:
                current_section = MarkdownSection(
                    heading="",
                    level=0,
                    hierarchy=[],
                )

            current_section.lines.append(line)
            continue

        # ---------------------------------------------------------------
        # Markdown 标题
        # ---------------------------------------------------------------
        heading = parse_heading(line)

        if heading is not None:
            level, title = heading

            # 第一层 # 标题，同时作为 document title
            if level == 1 and not document_title:
                document_title = title

            # 找到当前标题对应的位置
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()

            heading_stack.append((level, title))

            hierarchy = [item[1] for item in heading_stack]

            # 创建新 Section
            current_section = MarkdownSection(
                heading=title,
                level=level,
                hierarchy=hierarchy,
            )

            sections.append(current_section)
            continue

        # ---------------------------------------------------------------
        # 普通文本
        # ---------------------------------------------------------------
        if current_section is None:
            current_section = MarkdownSection(
                heading="",
                level=0,
                hierarchy=[],
            )
            sections.append(current_section)

        current_section.lines.append(line)

    # 如果文档没有 # 标题：
    # 使用文件名作为 title 的 fallback 在外层处理。
    return document_title, sections


# ============================================================================
# 文本清理
# ============================================================================


def normalize_text(text: str) -> str:
    """
    对 Markdown 文本做轻度清理。

    注意：
        不做激进清洗。
        因为代码、命令、表格格式可能对 RAG 很重要。
    """

    # 统一空白行
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 连续 3 个以上空行压缩成 2 个
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 清理每行末尾多余空格
    lines = [line.rstrip() for line in text.split("\n")]

    # 去掉文档首尾空白
    return "\n".join(lines).strip()


# ============================================================================
# 特殊结构识别
# ============================================================================


def is_code_fence_start(line: str) -> bool:
    """
    判断是否为 fenced code block 开始。
    """

    stripped = line.strip()
    return stripped.startswith("```") or stripped.startswith("~~~")


def is_table_line(line: str) -> bool:
    """
    简单判断 Markdown 表格行。

    例如：
        | 参数 | 说明 |
        |------|------|
        | -sS  | SYN  |

    注意：
        这是一个轻量判断，不试图完整实现 Markdown parser。
    """

    stripped = line.strip()

    return (
        stripped.startswith("|")
        and stripped.endswith("|")
    )


def is_table_separator(line: str) -> bool:
    """
    判断 Markdown 表格的分隔线。
    """

    stripped = line.strip()

    if not is_table_line(stripped):
        return False

    cells = [
        cell.strip()
        for cell in stripped.strip("|").split("|")
    ]

    if not cells:
        return False

    return all(
        bool(re.fullmatch(r":?-{3,}:?", cell))
        for cell in cells
    )


# ============================================================================
# 逻辑块
# ============================================================================


def split_into_blocks(lines: list[str]) -> list[list[str]]:
    """
    将 Section 内部拆成逻辑块。

    一般情况下：
        空行 → 新块

    但：
        代码块不能被拆散
        表格尽量保持完整
    """

    blocks: list[list[str]] = []
    current: list[str] = []

    in_code = False
    code_fence = ""

    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ---------------------------------------------------------------
        # 代码块
        # ---------------------------------------------------------------
        if is_code_fence_start(line):
            fence = stripped[:3]

            if not in_code:
                # 开启代码块
                in_code = True
                code_fence = fence
            elif fence == code_fence:
                # 关闭代码块（必须与开启时的围栏符号一致）
                in_code = False

            current.append(line)

            i += 1
            continue

        if in_code:
            current.append(line)
            i += 1
            continue

        # ---------------------------------------------------------------
        # 表格
        # ---------------------------------------------------------------
        if is_table_line(line):
            current.append(line)

            i += 1

            # 表格连续行全部放进同一个 block
            while i < len(lines) and is_table_line(lines[i]):
                current.append(lines[i])
                i += 1

            continue

        # ---------------------------------------------------------------
        # 普通空行
        # ---------------------------------------------------------------
        if not stripped:
            if current:
                blocks.append(current)
                current = []

            i += 1
            continue

        current.append(line)

        i += 1

    if current:
        blocks.append(current)

    return blocks


# ============================================================================
# 长文本切割
# ============================================================================


def split_long_block(
    lines: list[str],
    max_chars: int,
) -> list[str]:
    """
    将一个过长逻辑块拆成多个文本块。

    优先按行切分。

    如果某一行本身就非常长：
        再按字符进行切割。
    """

    if max_chars <= 0:
        raise ValueError("max_chars 必须大于 0")

    result: list[str] = []

    current: list[str] = []
    current_length = 0

    for line in lines:
        line_length = len(line)

        # 当前已经有内容，并且加入这一行后明显超限
        if current and current_length + line_length + 1 > max_chars:
            result.append("\n".join(current).strip())

            current = []
            current_length = 0

        # ---------------------------------------------------------------
        # 单行本身超过最大长度
        # ---------------------------------------------------------------
        if line_length > max_chars:
            # 先把已有内容落盘
            if current:
                result.append("\n".join(current).strip())
                current = []
                current_length = 0

            for start in range(0, line_length, max_chars):
                piece = line[start:start + max_chars]

                if piece.strip():
                    result.append(piece.strip())

            continue

        current.append(line)
        current_length += line_length + 1

    if current:
        result.append("\n".join(current).strip())

    return [
        item
        for item in result
        if item.strip()
    ]


# ============================================================================
# 添加标题上下文
# ============================================================================


def build_context_prefix(
    document_title: str,
    hierarchy: list[str],
) -> str:
    """
    构造用于 embedding 的标题上下文。

    例如：

        文档：Python 知识点
        路径：文件操作 > os.path

    输出：

        文档：Python 知识点
        章节：文件操作 > os.path
    """

    parts: list[str] = []

    if document_title:
        parts.append(f"文档：{document_title}")

    if hierarchy:
        parts.append(
            "章节：" + " > ".join(hierarchy)
        )

    if not parts:
        return ""

    return "\n".join(parts) + "\n\n"


# ============================================================================
# Section → Chunk
# ============================================================================


def section_to_chunks(
    section: MarkdownSection,
    *,
    document_title: str,
    doc_id: str,
    source: str,
) -> list[Chunk]:
    """
    将一个 Markdown Section 转成多个 Chunk。
    """

    raw_text = normalize_text(section.text())

    if not raw_text:
        return []

    blocks = split_into_blocks(section.lines)

    if not blocks:
        return []

    max_size = CHUNK_CONFIG.max_chunk_size
    target_size = CHUNK_CONFIG.chunk_size
    overlap = CHUNK_CONFIG.chunk_overlap
    min_size = CHUNK_CONFIG.min_chunk_size

    # ---------------------------------------------------------------
    # 首先把超长 block 拆开
    # ---------------------------------------------------------------

    normalized_blocks: list[str] = []

    for block in blocks:
        # block 是 list[str]（多行文本），需先合并成字符串再清理
        block = normalize_text("\n".join(block))

        if not block:
            continue

        if len(block) <= max_size:
            normalized_blocks.append(block)
        else:
            pieces = split_long_block(
                block.split("\n"),
                max_size,
            )

            normalized_blocks.extend(pieces)

    # ---------------------------------------------------------------
    # 打包成目标 Chunk
    # ---------------------------------------------------------------

    chunk_texts: list[str] = []

    current_blocks: list[str] = []
    current_length = 0

    for block in normalized_blocks:
        block_length = len(block)

        if (
            current_blocks
            and current_length + block_length + 2 > target_size
        ):
            chunk_texts.append(
                "\n\n".join(current_blocks).strip()
            )

            current_blocks = []
            current_length = 0

        current_blocks.append(block)
        current_length += block_length + 2

    if current_blocks:
        chunk_texts.append(
            "\n\n".join(current_blocks).strip()
        )

    # ---------------------------------------------------------------
    # 合并过小 Chunk
    # ---------------------------------------------------------------

    merged: list[str] = []

    for text in chunk_texts:
        if (
            merged
            and len(text) < min_size
            and len(merged[-1]) + len(text) + 2 <= max_size
        ):
            merged[-1] = (
                merged[-1]
                + "\n\n"
                + text
            )
        else:
            merged.append(text)

    chunk_texts = merged

    # ---------------------------------------------------------------
    # 生成标题上下文
    # ---------------------------------------------------------------

    prefix = build_context_prefix(
        document_title=document_title,
        hierarchy=section.hierarchy,
    )

    result: list[Chunk] = []

    for local_index, text in enumerate(chunk_texts):
        final_content = text

        if CHUNK_CONFIG.include_document_title or CHUNK_CONFIG.include_section_title:
            final_content = prefix + text

        # -----------------------------------------------------------
        # Chunk ID
        #
        # 用 section hierarchy + index 构造稳定 ID
        # -----------------------------------------------------------

        section_id = (
            "::".join(section.hierarchy)
            if section.hierarchy
            else "root"
        )

        chunk_id = (
            f"{doc_id}::{section_id}::{local_index + 1:03d}"
        )

        metadata = {
            "file_name": Path(source).name,
            "extension": Path(source).suffix.lower(),
            "heading_level": section.level,
            "section_path": section.hierarchy.copy(),
            "content_length": len(final_content),
        }

        result.append(
            Chunk(
                chunk_id=chunk_id,
                doc_id=doc_id,
                title=document_title,
                section=" > ".join(section.hierarchy),
                content=final_content,
                source=source,
                metadata=metadata,
                chunk_index=local_index,
                heading_level=section.level,
            )
        )

    # ---------------------------------------------------------------
    # Overlap
    #
    # 注意：
    # 这里使用前一个 Chunk 的尾部文本作为下一个 Chunk 的上下文。
    #
    # 对 Markdown / 中文知识库而言，比生硬地切字符更实用。
    # ---------------------------------------------------------------

    if overlap > 0 and len(result) > 1:
        for i in range(1, len(result)):
            previous = result[i - 1].content

            # 取前一个 chunk 的最后 overlap 个字符
            overlap_text = previous[-overlap:].strip()

            if not overlap_text:
                continue

            result[i].content = (
                overlap_text
                + "\n\n"
                + result[i].content
            )

            result[i].metadata["overlap_chars"] = len(
                overlap_text
            )

    return result


# ============================================================================
# 文档处理
# ============================================================================


def markdown_to_chunks(
    file_path: str | Path,
) -> list[Chunk]:
    """
    将一个 Markdown 文件转换成 Chunk 列表。
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Markdown 文件不存在：{path}"
        )

    if path.suffix.lower() not in {".md", ".markdown"}:
        raise ValueError(
            f"不是 Markdown 文件：{path}"
        )

    # ---------------------------------------------------------------
    # UTF-8-sig 可以自动处理带 BOM 的 UTF-8 文件
    # ---------------------------------------------------------------

    text = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    document_title, sections = parse_markdown(text)

    # 如果 Markdown 没有一级标题：
    # 使用文件名作为 title。
    if not document_title:
        document_title = path.stem

    doc_id = path.stem

    result: list[Chunk] = []

    for section in sections:
        chunks = section_to_chunks(
            section,
            document_title=document_title,
            doc_id=doc_id,
            source=str(path),
        )

        result.extend(chunks)

    # ---------------------------------------------------------------
    # 重新编号
    # ---------------------------------------------------------------

    for index, chunk in enumerate(result):
        chunk.chunk_index = index

    return result


# ============================================================================
# 批量处理 Markdown
# ============================================================================


def iter_markdown_files(
    directory: str | Path,
) -> Iterable[Path]:
    """
    递归遍历 Markdown 文件。

    支持：
        .md
        .markdown
    """

    directory = Path(directory)

    if not directory.exists():
        return

    for path in directory.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() in {
            ".md",
            ".markdown",
        }:
            yield path


def load_markdown_directory(
    directory: str | Path = MARKDOWN_DIR,
) -> list[Chunk]:
    """
    扫描整个 Markdown 目录并生成 Chunk。
    """

    all_chunks: list[Chunk] = []

    for file_path in iter_markdown_files(directory):
        try:
            chunks = markdown_to_chunks(file_path)

        except Exception as exc:
            print(
                f"[WARN] 处理失败：{file_path}\n"
                f"       原因：{exc}"
            )
            continue

        all_chunks.extend(chunks)

    return all_chunks


# ============================================================================
# 简单导出
# ============================================================================


def save_chunks_json(
    chunks: list[Chunk],
    output_path: str | Path,
) -> None:
    """
    将 Chunk 保存为 JSON。

    这个函数主要用于调试。
    后面正式进入 Qdrant 时，可以直接使用 Chunk 对象，
    不一定需要经过 JSON。
    """

    import json

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = [
        chunk.to_dict()
        for chunk in chunks
    ]

    output_path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


# ============================================================================
# 调试打印
# ============================================================================


def print_chunk_preview(
    chunks: list[Chunk],
    limit: int = 10,
) -> None:
    """
    打印前几个 Chunk，用来检查切块是否符合预期。
    """

    print("=" * 80)
    print(f"Chunk 数量：{len(chunks)}")
    print("=" * 80)

    for index, chunk in enumerate(chunks[:limit], start=1):
        print()
        print(f"[Chunk {index}]")
        print(f"ID      : {chunk.chunk_id}")
        print(f"文档    : {chunk.title}")
        print(f"章节    : {chunk.section}")
        print(f"来源    : {chunk.source}")
        print(f"长度    : {len(chunk.content)}")
        print("-" * 80)
        print(chunk.content[:1500])

        if len(chunk.content) > 1500:
            print("...")


# ============================================================================
# CLI
# ============================================================================


def main() -> None:
    """
    直接运行本文件时：

        python -m src.ingest.chunker

    会：
        1. 扫描 File/Markdown
        2. 生成 Chunk
        3. 打印前几个 Chunk
        4. 输出调试 JSON
    """

    print()
    print("=" * 80)
    print("RAG Markdown Chunker")
    print("=" * 80)

    print(f"Markdown 目录：{MARKDOWN_DIR}")
    print(
        f"Chunk Size    ：{CHUNK_CONFIG.chunk_size}"
    )
    print(
        f"Chunk Overlap ：{CHUNK_CONFIG.chunk_overlap}"
    )
    print(
        f"Chunk Max     ：{CHUNK_CONFIG.max_chunk_size}"
    )
    print()

    chunks = load_markdown_directory()

    print_chunk_preview(
        chunks,
        limit=8,
    )

    output_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "chunks"
        / "chunks_debug.json"
    )

    save_chunks_json(
        chunks,
        output_path,
    )

    print()
    print("=" * 80)
    print(
        f"调试 JSON 已保存：{output_path}"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()