"""RAG 命令行入口。

用法（**必须从项目根目录运行**）::

    runtime\\python3.12\\python.exe run.py serve
    runtime\\python3.12\\python.exe run.py index --rebuild
    runtime\\python3.12\\python.exe run.py search "nmap -sS 是什么"
    runtime\\python3.12\\python.exe run.py ask "nmap -sS 是什么"
    runtime\\python3.12\\python.exe run.py check

注意：本项目自带的是 **embedded Python** 发行版，其 ``python312._pth``
固定了 ``sys.path``，导致 ``python -m src.xxx`` 和 ``PYTHONPATH`` 都失效。
因此所有入口都必须经由 ``run.py``（脚本方式，sys.path[0] 即项目根目录）。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# 允许直接 `python src/cli.py` 时也能找到 src 包
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


# ============================================================================
# 输出辅助
# ============================================================================


def _print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


def _rule(title: str = "") -> None:
    print("=" * 72)
    if title:
        print(title)
        print("=" * 72)


def _display_width(text: str) -> int:
    """终端显示宽度：CJK 全角字符占 2 列。"""
    import unicodedata

    return sum(
        2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        for ch in text
    )


def _fit(text: str, width: int, align: str = "left") -> str:
    """按显示宽度截断并填充，保证表格对齐。"""
    text = str(text)

    # 先按显示宽度截断
    if _display_width(text) > width:
        kept = ""
        used = 0
        for ch in text:
            w = 2 if __import__("unicodedata").east_asian_width(ch) in ("W", "F") else 1
            if used + w > width - 1:
                break
            kept += ch
            used += w
        text = kept + "…"

    padding = max(0, width - _display_width(text))

    if align == "right":
        return " " * padding + text
    return text + " " * padding


# ============================================================================
# 子命令实现
# ============================================================================


def cmd_config(args: argparse.Namespace) -> int:
    from src.config import print_config, validate_config

    if not args.skip_validate:
        try:
            validate_config()
            print("[ok] 配置校验通过\n")
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] 配置校验未通过: {exc}\n")

    print_config()
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """环境自检：把「会静默失败的东西」一次性列清楚。"""
    from src.config import (
        ACTIVE_EMBEDDING,
        DATA_DIR,
        EMBEDDING_CONFIG,
        LLAMA_CPP_DIR,
        LLM_CONFIG,
        MARKDOWN_DIR,
        PYTHON_DIR,
        QDRANT_CONFIG,
        discover_llm_model,
    )

    rows: list[tuple[str, bool, str]] = []

    def add(label: str, ok: bool, detail: str = "") -> None:
        rows.append((label, ok, detail))

    python_exe = PYTHON_DIR / "python.exe"
    add("Python 运行时", python_exe.exists(), str(python_exe))

    llama_server = LLAMA_CPP_DIR / "llama-server.exe"
    add("llama-server.exe", llama_server.exists(), str(llama_server))

    add(
        f"Embedding 模型（{EMBEDDING_CONFIG.name}）",
        EMBEDDING_CONFIG.model_path.exists(),
        str(EMBEDDING_CONFIG.model_path),
    )

    if EMBEDDING_CONFIG.mmproj_path is not None:
        add(
            "Embedding mmproj",
            EMBEDDING_CONFIG.mmproj_path.exists(),
            str(EMBEDDING_CONFIG.mmproj_path),
        )

    add("Markdown 目录", MARKDOWN_DIR.is_dir(), str(MARKDOWN_DIR))

    md_count = (
        len(list(MARKDOWN_DIR.rglob("*.md"))) if MARKDOWN_DIR.is_dir() else 0
    )
    add("Markdown 文档数", md_count > 0, f"{md_count} 个")

    add("数据目录", DATA_DIR.is_dir(), str(DATA_DIR))

    # ---- 索引状态 -----------------------------------------------------
    indexed = 0
    try:
        from src.database.vector_db import get_vector_db

        indexed = get_vector_db().count()
        add("Qdrant collection", True, f"{QDRANT_CONFIG.collection_name}_{ACTIVE_EMBEDDING}")
    except Exception as exc:  # noqa: BLE001
        add("Qdrant collection", False, f"打开失败: {exc}")

    add("已索引 chunk", indexed > 0, f"{indexed} 条")

    bm25_ok = False
    bm25_detail = ""
    try:
        from src.retrieval.bm25 import bm25_index_path

        path = bm25_index_path()
        bm25_ok = path.exists()
        bm25_detail = str(path)
    except Exception as exc:  # noqa: BLE001
        bm25_detail = str(exc)
    add("BM25 索引", bm25_ok, bm25_detail)

    # ---- 生成式 LLM ---------------------------------------------------
    model_path = discover_llm_model(LLM_CONFIG)
    add(
        "生成式 LLM 模型",
        model_path is not None,
        str(model_path) if model_path else "未找到（问答将降级为纯检索）",
    )

    # ---- 视觉模型（多模态图片理解）-------------------------------------
    try:
        from src.vision import VisionCaptioner

        vision = VisionCaptioner()
        vision_ok, vision_reason = vision.available()
        add(
            "视觉模型（图片理解）",
            vision_ok,
            vision_reason if not vision_ok else (
                f"{vision.model_path.name if vision.model_path else ''}"
                f" + {vision.mmproj_path.name if vision.mmproj_path else ''}"
            ),
        )
    except Exception as exc:  # noqa: BLE001
        add("视觉模型（图片理解）", False, str(exc))

    # ---- 图片索引情况 --------------------------------------------------
    try:
        from src.ingest.image import iter_image_files

        images = list(iter_image_files())
        add("File/image 图片数", True, f"{len(images)} 张")
    except Exception as exc:  # noqa: BLE001
        add("File/image 图片数", False, str(exc))

    # ---- 输出 ---------------------------------------------------------
    _rule("环境自检")

    width = max(len(label) for label, _, _ in rows)
    failed = 0

    for label, ok, detail in rows:
        mark = "OK  " if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{mark}] {label.ljust(width)}  {detail}")

    print("=" * 72)

    if failed:
        print(f"\n{failed} 项检查未通过。")
    else:
        print("\n全部检查通过。")

    return 1 if failed else 0



def _web_options(args: argparse.Namespace) -> dict:
    """把 CLI 的联网开关转成检索参数。

    ``--web`` 显式开启；不传则返回 ``use_web=None``，由设置里的默认值决定
    （与服务端行为一致）。
    """
    if not getattr(args, "web", False):
        return {"use_web": None}

    return {
        "use_web": True,
        "web_limit": getattr(args, "web_limit", None),
        "web_fetch_pages": not getattr(args, "no_web_fetch", False),
    }

def cmd_index(args: argparse.Namespace) -> int:
    from src.ingest.pipeline import ingest_all

    started = time.perf_counter()

    result = ingest_all(
        recreate=args.rebuild,
        embedder_name=args.model,
        include_images=not args.no_images,
        prune=not args.no_prune,
        progress=lambda message: print(message, flush=True),
    )

    elapsed = time.perf_counter() - started

    _rule()
    print(f"耗时      : {elapsed:.1f}s")
    print(f"文本 chunk: {result.get('text_chunks')}")
    print(f"图片 chunk: {result.get('image_chunks')}")
    print(f"合计 chunk: {result.get('chunks')}")
    print(f"已写入    : {result.get('indexed')}")
    print(f"已清理    : {result.get('pruned', 0)}")
    print(f"collection: {result.get('collection')}")
    print(f"embedding : {result.get('embedding')}")
    if result.get("image_note"):
        print(f"图片说明  : {result['image_note']}")

    if args.pdf:
        from src.ingest.pdf import ingest_pdf

        print()
        print("[index] 继续处理 PDF ...")
        pdf_result = ingest_pdf(
            recreate=False,
            embedder_name=args.model,
            extract_images=args.pdf_images,
        )
        print(f"[index] PDF: {pdf_result}")

    return 0


def cmd_search(args: argparse.Namespace) -> int:
    from src.rag.search import search_rag

    result = search_rag(
        query=args.query,
        top_k=args.top_k,
        use_bm25=not args.no_bm25,
        use_reranker=not args.no_rerank,
        name=args.model,
        **_web_options(args),
    )

    if args.json:
        _print_json(result)
        return 0

    stats = result["stats"]
    _rule(f"检索：{args.query}")
    print(
        f"dense={stats['dense_hits']}  bm25={stats['bm25_hits']}  "
        f"candidates={stats['candidates']}  final={stats['final']}"
        + (
            f"  （本地 {stats.get('local', '?')} + 网页 {stats.get('web', 0)}）"
            if stats.get("use_web")
            else ""
        )
    )

    web_info = result.get("web") or {}
    if web_info.get("enabled"):
        if web_info.get("error"):
            print(f"[web]  联网搜索失败：{web_info['error']}")
        else:
            print(
                f"[web]  {web_info.get('provider')} 返回 {web_info.get('count', 0)} 条"
                f"，抓正文 {web_info.get('fetched_pages', 0)} 页"
                f"，耗时 {web_info.get('elapsed_ms', 0):.0f}ms"
            )

    print()

    if not result["results"]:
        print("没有检索到结果。若尚未建索引，请先运行：run.py index")
        return 0

    for item in result["results"]:
        payload = item.get("payload") or {}
        metadata = payload.get("metadata") or {}

        is_web = metadata.get("source_type") == "web"
        score = item.get("rerank_score", item.get("score"))

        if is_web:
            # 网页结果没有本地重排分数，别显示成 0
            print(
                f"[网页  ] {metadata.get('domain', '')}  "
                f"{metadata.get('file_name', '')}"
            )
            print(f"          {metadata.get('url', '')}")
        else:
            score_text = f"{score:.4f}" if isinstance(score, (int, float)) else "  -   "
            print(
                f"[{item.get('source', '?'):6}] score={score_text}  "
                f"{metadata.get('file_name', '')}"
            )
            print(f"          章节：{payload.get('section', '')}")

        content = (payload.get("content") or "").replace("\n", " ")
        print(f"          {content[:180]}...")
        print()

    if args.context:
        _rule("Context")
        print(result["context"])

    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    from src.llm import LLMUnavailable
    from src.rag.answer import RAGAnswerer
    from src.rag.modes import resolve_mode

    # --fast / --precise 是 --mode 的快捷方式
    mode = args.mode
    if args.fast:
        mode = "fast"
    elif args.precise:
        mode = "precise"

    try:
        answer_mode = resolve_mode(mode)
    except ValueError as exc:
        print(f"[error] {exc}")
        return 2

    answerer = RAGAnswerer(
        name=args.model, provider=args.provider, llm_model=args.llm
    )

    ok, reason = answerer.llm.available()  # type: ignore[attr-defined]
    if not ok:
        print(f"[error] 生成式问答不可用：{reason}")
        print("提示：用 `run.py search` 仍可做纯检索。")
        return 2

    if args.stream:
        _rule(f"问答：{args.query}   [{answer_mode.label}模式]")
        print()

        for event in answerer.stream(
            query=args.query, top_k=args.top_k, mode=answer_mode.name
        ):
            kind = event.get("type")

            if kind == "status":
                print(f"… {event.get('message')}", flush=True)

            elif kind == "citations":
                citations = event.get("citations") or []
                if citations:
                    print(f"… 命中 {len(citations)} 段参考资料", flush=True)

            elif kind == "reasoning":
                if args.show_thinking:
                    print(event.get("text", ""), end="", flush=True)

            elif kind == "token":
                print(event.get("text", ""), end="", flush=True)

            elif kind == "error":
                print(f"\n[error] {event.get('message')}", file=sys.stderr)
                return 1

            elif kind == "done":
                print()
                print()
                print(
                    f"— 用时 {event.get('elapsed_ms')} ms，"
                    f"模型 {event.get('model')}，档位 {event.get('mode')}"
                )

        return 0

    try:
        result = answerer.answer(
            query=args.query,
            top_k=args.top_k,
            mode=answer_mode.name,
            **_web_options(args),
        )
    except LLMUnavailable as exc:
        print(f"[error] {exc}")
        return 2

    if args.json:
        _print_json(result.to_dict())
        return 0

    _rule(f"问答：{args.query}   [{answer_mode.label}模式]")
    print(result.answer)
    print()

    if args.show_thinking and result.reasoning:
        _rule("思考过程")
        print(result.reasoning)
        print()

    if result.citations:
        _rule("引用来源")
        for citation in result.citations:
            print(
                f"[{citation['index']}] {citation['file_name']}"
                f"  ›  {citation['section']}"
            )

    print()
    print(
        f"用时 {result.elapsed_ms} ms  模型 {result.model}  档位 {result.mode}  "
        f"tokens {result.usage.get('completion_tokens', 0)}"
    )

    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    from src.ingest.chunker import load_markdown_directory

    started = time.perf_counter()
    chunks = load_markdown_directory()
    elapsed = time.perf_counter() - started

    if args.json:
        _print_json(
            {
                "chunks": len(chunks),
                "elapsed_ms": round(elapsed * 1000, 2),
                "average_length": (
                    round(sum(len(c.content) for c in chunks) / len(chunks), 2)
                    if chunks
                    else 0
                ),
            }
        )
        return 0

    lengths = [len(c.content) for c in chunks]

    _rule("切块统计")
    print(f"文档数   : {len({c.doc_id for c in chunks})}")
    print(f"chunk 数 : {len(chunks)}")
    print(f"总字符   : {sum(lengths)}")

    if lengths:
        print(f"平均长度 : {sum(lengths) / len(lengths):.1f}")
        print(f"最长     : {max(lengths)}")
        print(f"最短     : {min(lengths)}")

    print(f"解析耗时 : {elapsed * 1000:.0f} ms")

    return 0


def cmd_llm(args: argparse.Namespace) -> int:
    from src.config import LLM_CONFIG
    from src.llm import get_llm

    llm = get_llm(args.provider)

    ok, reason = llm.available()  # type: ignore[attr-defined]

    _print_json(
        {
            "provider": LLM_CONFIG.provider,
            "available": ok,
            "reason": reason,
            "name": llm.name,  # type: ignore[attr-defined]
        }
    )

    if not ok:
        return 2

    if args.prompt:
        from src.llm import ChatMessage

        print()
        print("--- 试跑 ---")
        reply = llm.chat(  # type: ignore[attr-defined]
            [ChatMessage("user", args.prompt)],
            max_tokens=128,
        )
        print(reply.content)

    return 0


def cmd_test(args: argparse.Namespace) -> int:
    """运行单元测试。

    为什么不用 ``python -m unittest``：本项目是 embedded Python，
    ``._pth`` 固定了 sys.path，``-m`` 无法引入项目内的 ``src`` 包。
    因此这里显式加载 ``tests/`` 下的用例。
    """
    import unittest

    tests_dir = Path(__file__).resolve().parents[1] / "tests"

    if not tests_dir.is_dir():
        print(f"[error] 找不到测试目录: {tests_dir}")
        return 1

    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(tests_dir),
        pattern=args.pattern,
        top_level_dir=str(_PROJECT_ROOT),
    )

    runner = unittest.TextTestRunner(
        verbosity=2 if args.verbose else 1,
        buffer=not args.no_buffer,
    )
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


def cmd_models(args: argparse.Namespace) -> int:
    """列出可用模型 / 查看详情 / 切换默认模型。"""
    from src.llm import active_model, available_models, chat_models, switch_model
    from src.llm.catalog import KIND_LABELS

    # ---- 切换 --------------------------------------------------------
    if args.use is not None:
        try:
            entry = switch_model(args.use)
        except ValueError as exc:
            print(f"[error] {exc}")
            return 2

        print(f"[ok] 已切换默认模型 -> {entry['file_name']}")
        print(f"     {entry['label']}")
        print(f"     显存估算 {entry['total_gb']:.2f} GB "
              f"（{'可容纳' if entry['fits_vram'] else '超出预算'}）")
        print("     新模型将在下次问答时加载（首次约 8~10 秒）。")
        return 0

    if args.clear:
        from src.llm.catalog import save_selection

        save_selection(None)
        print("[ok] 已清除持久选择，恢复自动挑选。")
        return 0

    entries = available_models()

    if args.json:
        _print_json(
            {
                "active": active_model(),
                "chat_models": chat_models(),
                "all": entries,
            }
        )
        return 0

    active = active_model()
    active_file = active.get("file_name", "")

    # ---- 可对话模型 --------------------------------------------------
    usable = [e for e in entries if e.get("is_chat_capable")]

    _rule("可用于问答的模型")
    print(
        f"{'#':>3}  {'':2} {_fit('模型', 40)} {_fit('类型', 6)} "
        f"{'大小':>7} {'KV':>6} {'合计':>7} {'显存':4}"
    )
    print("-" * 88)

    for index, entry in enumerate(usable, 1):
        mark = "*" if entry["file_name"] == active_file else " "
        fit = "OK" if entry["fits_vram"] else "NO"
        kind = KIND_LABELS.get(entry["kind"], entry["kind"])

        print(
            f"{index:>3}  {mark:2} {_fit(entry['label'], 40)} "
            f"{_fit(kind, 6)} "
            f"{entry['size_gb']:>6.2f}G {entry['kv_cache_gb']:>5.2f}G "
            f"{entry['total_gb']:>6.2f}G {fit:4}"
        )

    print()
    print(f"  * = 当前生效   共 {len(usable)} 个；"
          f"标注 NO 的模型在小显存上会退回 CPU 推理")

    # ---- 其他文件 ----------------------------------------------------
    others = [e for e in entries if not e.get("is_chat_capable")]

    if others and args.all:
        print()
        _rule("其他文件（不可用于问答）")
        for entry in others:
            kind = KIND_LABELS.get(entry["kind"], entry["kind"])
            note = f"  <- {entry['excluded_reason']}" if entry.get("excluded") else ""
            print(f"      [{_fit(kind, 6)}] "
                  f"{_fit(entry['file_name'], 52)} "
                  f"{entry['size_gb']:>6.2f}G{note}")

    if args.detail:
        target = args.detail
        matched = next(
            (e for e in entries if target.lower() in e["file_name"].lower()),
            None,
        )
        if matched is None:
            print(f"\n[error] 找不到匹配 {target!r} 的模型")
            return 2

        print()
        _rule(f"详情：{matched['file_name']}")
        for key in (
            "label", "kind", "architecture", "size_label", "quantization",
            "context_length", "effective_context", "block_count",
            "embedding_length", "head_count", "head_count_kv",
            "has_chat_template", "tags", "base_organization",
            "size_gb", "weights_gb", "kv_cache_gb", "total_gb",
            "fits_vram", "excluded", "excluded_reason", "path",
        ):
            print(f"  {key:20} : {matched.get(key)}")

    print()
    print(f"当前生效: {active.get('label') or '(未找到可用模型)'}")
    if active.get("selection_file_value"):
        print(f"来源    : 持久选择 ({active['selection_file_value']})")
    else:
        print("来源    : 自动挑选")

    return 0


def cmd_cloud(args: argparse.Namespace) -> int:
    """配置 / 测试 / 切换云端 LLM（OpenAI 兼容 + API KEY）。"""
    from src.llm.cloud import (
        KNOWN_ENDPOINTS,
        clear_cloud,
        load_cloud,
        set_provider,
        test_connection,
        update_cloud,
    )

    # ---- 清空 --------------------------------------------------------
    if args.clear:
        clear_cloud()
        print("[ok] 已删除云端配置与 API Key。")
        return 0

    # ---- 测试连接 ----------------------------------------------------
    if args.test:
        stored = load_cloud()
        base_url = args.base_url or stored.base_url
        api_key = args.api_key or stored.api_key
        model = args.model or stored.model

        print(f"测试 {base_url} …")
        ok, message, models = test_connection(base_url, api_key, model)

        print(f"  {'[ok]' if ok else '[失败]'} {message}")
        if models:
            print(f"  可用模型（前 20）: {', '.join(models[:20])}")

        return 0 if ok else 1

    # ---- 保存 --------------------------------------------------------
    if args.base_url or args.model or args.api_key:
        settings = update_cloud(
            base_url=args.base_url,
            model=args.model,
            api_key=args.api_key,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        print("[ok] 云端配置已保存")
        _print_json(settings.to_public_dict())
        return 0

    # ---- 切换方式 ----------------------------------------------------
    if args.use:
        try:
            set_provider(args.use)
        except ValueError as exc:
            print(f"[error] {exc}")
            return 2
        print(f"[ok] 已切换到 {args.use}")
        return 0

    # ---- 查看 --------------------------------------------------------
    from src.llm.cloud import active_provider

    settings = load_cloud()

    _rule("云端 LLM（OpenAI 兼容 + API Key）")
    _print_json(
        {
            "active_provider": active_provider(),
            **settings.to_public_dict(),
        }
    )
    print()
    print("常用端点:")
    for name, url in KNOWN_ENDPOINTS.items():
        print(f"  {name:12} {url}")
    print()
    print("示例:")
    print('  run.py cloud --base-url https://api.deepseek.com/v1 \\')
    print('               --model deepseek-chat --api-key sk-xxxx')
    print("  run.py cloud --test          # 测试连接")
    print("  run.py cloud --use openai    # 切换到云端")
    print("  run.py cloud --use llama_cpp # 切回本地")
    print("  run.py cloud --clear         # 删除配置与 Key")

    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    """交互式多轮对话（终端内）。"""
    from src.config import IMAGE_DIR
    from src.llm import LLMUnavailable
    from src.rag.chat import RAGChat
    from src.rag.conversation import Conversation
    from src.rag.modes import resolve_mode

    answerer = RAGChat(name=args.model, provider=args.provider, llm_model=args.llm)

    ok, reason = answerer.llm.available()  # type: ignore[attr-defined]
    if not ok:
        print(f"[error] 生成式问答不可用：{reason}")
        print("提示：用 `run.py search` 仍可做纯检索。")
        return 2

    conversation = Conversation(id="cli")
    mode = args.mode or "fast"

    _rule("多轮对话")
    print("输入问题开始对话。命令：")
    print("  /new            开新会话")
    print("  /history        查看本轮会话的问题")
    print("  /mode fast|precise  切换档位")
    print("  /citations      显示上一次回答的引用来源")
    print("  /image <路径>   附加一张图片，下一个问题会带着它一起问（多模态）")
    print("  /image          清除已附加的图片")
    print("  /quit 或 /exit  退出（也可按 Ctrl+C）")
    print(f"当前档位：{mode}")
    print("=" * 72)

    last_turn = None
    pending_image: str | None = None

    while True:
        try:
            question = input("\n你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见。")
            return 0

        if not question:
            continue

        # ---- 内置命令 ------------------------------------------------
        if question in ("/quit", "/exit", "/q"):
            print("再见。")
            return 0

        if question == "/new":
            conversation = Conversation(id="cli")
            last_turn = None
            print("已开启新会话。")
            continue

        if question == "/history":
            if not conversation.turns:
                print("（本会话还没有内容）")
            for turn in conversation.turns:
                print(f"  {turn.index + 1}. {turn.question}")
            continue

        if question == "/citations":
            if last_turn is None or not last_turn.citations:
                print("（没有可显示的来源）")
                continue
            for citation in last_turn.citations:
                print(f"  [{citation['index']}] {citation['file_name']}"
                      f"  ›  {citation['section']}")
            continue

        if question.startswith("/mode"):
            parts = question.split()
            if len(parts) == 2:
                try:
                    mode = resolve_mode(parts[1]).name
                    print(f"已切换到 {mode} 档。")
                except ValueError as exc:
                    print(f"[error] {exc}")
            else:
                print(f"当前档位：{mode}")
            continue

        if question.startswith("/image"):
            parts = question.split(maxsplit=1)

            if len(parts) == 1:
                pending_image = None
                print("已清除附加的图片。")
                continue

            candidate = Path(parts[1].strip().strip('"'))

            if not candidate.is_absolute():
                candidate = IMAGE_DIR / candidate

            if not candidate.is_file():
                print(f"[error] 找不到图片：{candidate}")
                continue

            pending_image = str(candidate)
            print(f"已附加图片：{candidate.name}（下一个问题会带着它）")
            continue

        if question == "/help":
            print("命令：/new /history /citations /image <路径> "
                  "/mode fast|precise /quit")
            continue

        # ---- 正常提问 ------------------------------------------------
        try:
            turn = answerer.chat(
                conversation,
                question,
                top_k=args.top_k,
                mode=mode,
                include_images=not args.no_images,
                image=pending_image,
                **_web_options(args),
            )
        except LLMUnavailable as exc:
            print(f"[error] {exc}")
            continue
        except Exception as exc:  # noqa: BLE001
            print(f"[error] 对话失败：{exc}")
            continue

        if pending_image:
            print(f"  （已附图片 {Path(pending_image).name}）")
            pending_image = None

        conversation.turns.append(turn)
        last_turn = turn

        # 追问改写提示 —— 让用户看到追问是怎么被理解的
        if turn.is_rewritten:
            print(f"  ↳ 结合上下文改写为「{turn.retrieval_query}」")

        if turn.reasoning and args.show_thinking:
            print()
            print("  ── 思考过程 ──")
            for line in turn.reasoning.strip().splitlines():
                print(f"  {line}")

        print()
        print(turn.answer.strip())

        if turn.citations:
            print()
            for citation in turn.citations:
                print(f"  [{citation['index']}] {citation['file_name']}"
                      f"  ›  {citation['section']}")

        print()
        print(f"  （{turn.elapsed_ms / 1000:.1f}s · {turn.mode} · "
              f"{turn.usage.get('completion_tokens', 0)} tokens）")


def cmd_serve(args: argparse.Namespace) -> int:
    from src.server import main as server_main

    server_main()
    return 0


# ============================================================================
# 参数解析
# ============================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="本地 RAG 工具链（检索 / 问答 / 建索引 / Web 服务）",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ---- config ----
    p_config = sub.add_parser("config", help="打印当前配置")
    p_config.add_argument(
        "--skip-validate", action="store_true", help="跳过配置校验"
    )
    p_config.set_defaults(func=cmd_config)

    # ---- check ----
    p_check = sub.add_parser("check", help="环境自检")
    p_check.set_defaults(func=cmd_check)

    # ---- index ----
    p_index = sub.add_parser("index", help="构建 / 重建索引")
    p_index.add_argument(
        "--rebuild", action="store_true", help="清空 collection 后重建"
    )
    p_index.add_argument(
        "--no-prune", action="store_true", help="不清理已失效文档的残留 chunk"
    )
    p_index.add_argument("--model", default=None, help="embedding 模型名")
    p_index.add_argument("--pdf", action="store_true", help="同时索引 PDF 目录")
    p_index.add_argument(
        "--pdf-images", action="store_true", help="索引 PDF 时同时导出图片"
    )
    p_index.add_argument(
        "--no-images",
        action="store_true",
        help="跳过图片（默认会用视觉模型描述 File/image 下的图片并一起索引）",
    )
    p_index.set_defaults(func=cmd_index)

    # ---- search ----
    p_search = sub.add_parser("search", help="纯检索（不生成）")
    p_search.add_argument("query", help="查询文本")
    p_search.add_argument("--top-k", type=int, default=5)
    p_search.add_argument(
        "--web", action="store_true",
        help="联网搜索（结果追加在本地检索之后）",
    )
    p_search.add_argument(
        "--web-limit", type=int, default=None, help="联网取几条，默认取设置"
    )
    p_search.add_argument(
        "--no-web-fetch", action="store_true",
        help="联网时不抓网页正文（更快）",
    )
    p_search.add_argument("--no-bm25", action="store_true")
    p_search.add_argument("--no-rerank", action="store_true")
    p_search.add_argument("--model", default=None)
    p_search.add_argument("--context", action="store_true", help="同时打印 Context")
    p_search.add_argument("--json", action="store_true")
    p_search.set_defaults(func=cmd_search)

    # ---- ask ----
    p_ask = sub.add_parser("ask", help="检索 + 生成式问答")
    p_ask.add_argument("query", help="问题")
    p_ask.add_argument("--top-k", type=int, default=5)
    p_ask.add_argument(
        "--web", action="store_true",
        help="联网搜索（结果追加在本地检索之后）",
    )
    p_ask.add_argument(
        "--web-limit", type=int, default=None, help="联网取几条，默认取设置"
    )
    p_ask.add_argument(
        "--no-web-fetch", action="store_true",
        help="联网时不抓网页正文（更快）",
    )
    p_ask.add_argument("--model", default=None, help="embedding 模型名")
    p_ask.add_argument("--provider", default=None, help="llama_cpp | openai")
    p_ask.add_argument(
        "--llm", default=None, metavar="模型",
        help="指定对话模型（文件名片段 / 序号 / 完整路径）；默认取当前生效模型",
    )
    p_ask.add_argument(
        "--mode",
        default=None,
        choices=["fast", "precise"],
        help="问答档位：fast=关闭思考（快）| precise=开启思考（准）",
    )
    p_ask.add_argument(
        "--fast", action="store_true", help="等价于 --mode fast"
    )
    p_ask.add_argument(
        "--precise", action="store_true", help="等价于 --mode precise"
    )
    p_ask.add_argument(
        "--no-stream", dest="stream", action="store_false", help="关闭流式输出"
    )
    p_ask.add_argument(
        "--show-thinking", action="store_true", help="显示思考过程"
    )
    p_ask.add_argument("--json", action="store_true")
    p_ask.set_defaults(func=cmd_ask, stream=True)

    # ---- stats ----
    p_stats = sub.add_parser("stats", help="切块统计")
    p_stats.add_argument("--json", action="store_true")
    p_stats.set_defaults(func=cmd_stats)

    # ---- llm ----
    p_llm = sub.add_parser("llm", help="生成式模型状态 / 试跑")
    p_llm.add_argument("--provider", default=None)
    p_llm.add_argument("--prompt", default=None, help="试跑一句 prompt")
    p_llm.set_defaults(func=cmd_llm)

    # ---- models ----
    p_models = sub.add_parser("models", help="列出可用模型 / 切换默认模型")
    p_models.add_argument(
        "--use", default=None, metavar="模型",
        help="切换默认模型（文件名片段 / 序号 / 完整路径）",
    )
    p_models.add_argument(
        "--clear", action="store_true", help="清除持久选择，恢复自动挑选"
    )
    p_models.add_argument(
        "--all", action="store_true", help="同时列出不可用于问答的文件"
    )
    p_models.add_argument(
        "--detail", default=None, metavar="模型", help="查看某模型详情"
    )
    p_models.add_argument("--json", action="store_true")
    p_models.set_defaults(func=cmd_models)

    # ---- serve ----
    p_serve = sub.add_parser("serve", help="启动 Web 服务")
    p_serve.set_defaults(func=cmd_serve)

    # ---- chat ----
    p_chat = sub.add_parser("chat", help="交互式多轮对话（终端内）")
    p_chat.add_argument("--top-k", type=int, default=5)
    p_chat.add_argument("--model", default=None, help="embedding 模型名")
    p_chat.add_argument("--llm", default=None, help="对话模型（文件名/序号/路径）")
    p_chat.add_argument("--provider", default=None, help="llama_cpp | openai")
    p_chat.add_argument(
        "--mode", default="fast", choices=["fast", "precise"],
        help="初始档位，默认 fast",
    )
    p_chat.add_argument(
        "--show-thinking", action="store_true", help="显示思考过程"
    )
    p_chat.add_argument(
        "--no-images", action="store_true", help="检索时不包含图片"
    )

    p_chat.add_argument(
        "--web", action="store_true", help="联网搜索（结果追加在本地检索之后）"
    )
    p_chat.add_argument("--web-limit", type=int, default=None, help="联网取几条，默认取设置")
    p_chat.add_argument(
        "--no-web-fetch", action="store_true", help="联网时不抓网页正文（更快）"
    )
    p_chat.set_defaults(func=cmd_chat)

    # ---- cloud ----
    p_cloud = sub.add_parser(
        "cloud", help="配置云端 LLM（OpenAI 兼容 + API KEY）"
    )
    p_cloud.add_argument("--base-url", default=None, help="OpenAI 兼容端点")
    p_cloud.add_argument("--model", default=None, help="模型名")
    p_cloud.add_argument(
        "--api-key", default=None, help="API Key（留空则保持原有）"
    )
    p_cloud.add_argument("--temperature", type=float, default=None)
    p_cloud.add_argument("--max-tokens", type=int, default=None)
    p_cloud.add_argument("--test", action="store_true", help="测试连接")
    p_cloud.add_argument("--clear", action="store_true", help="删除配置与 Key")
    p_cloud.add_argument(
        "--use", default=None, choices=["openai", "llama_cpp"],
        help="切换使用方式：云端 / 本地离线",
    )
    p_cloud.set_defaults(func=cmd_cloud)

    # ---- test ----
    p_test = sub.add_parser("test", help="运行单元测试")
    p_test.add_argument(
        "--pattern", default="test_*.py", help="测试文件匹配模式"
    )
    p_test.add_argument(
        "-v", "--verbose", action="store_true", help="显示每个用例"
    )
    p_test.add_argument(
        "--no-buffer", action="store_true", help="显示测试内的 print 输出"
    )
    p_test.set_defaults(func=cmd_test)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("\n已中断。")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
