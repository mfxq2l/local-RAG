"""检索路由器：判断一次提问**是否需要**查询知识库。

为什么需要
----------
RAG 流程会强制模型「只依据参考资料回答」。对「你好呀」「谢谢」这类输入，
知识库里当然没有对应内容，模型只能回一句「根据现有资料无法回答」——
这既不自然，也不是用户想要的。

自适应检索（adaptive retrieval）分两步：

    1. 路由：判断这次是否需要检索
        需要   → 走完整的 RAG 流程
        不需要 → 当普通助手直接回答
    2. 兜底：万一检索确实没命中，也要自然地回答，而不是生硬拒绝

路由策略
--------
先用**规则**处理一眼可判的情况（寒暄、致谢、纯符号），省掉一次模型调用；
其余交给轻量 LLM 分类。任何一步失败都**保守地判定为「需要检索」**——
宁可多查一次，也不要把本该查资料的问题当闲聊答了。
"""

from __future__ import annotations

import re
from typing import Any

from src.llm import ChatMessage


# ----------------------------------------------------------------------
# 规则快判
# ----------------------------------------------------------------------

# 一眼就知道不需要查知识库的输入
_SMALL_TALK = {
    "你好", "您好", "hi", "hello", "hey", "哈喽", "嗨",
    "早", "早上好", "晚上好", "下午好", "在吗", "在么",
    "谢谢", "多谢", "感谢", "thanks", "thank you", "thx",
    "再见", "拜拜", "bye", "goodbye", "晚安",
    "好的", "好", "嗯", "行", "可以", "收到", "明白", "知道了",
    "ok", "okay", "yes", "no",
}

# 与对话本身相关（元问题），也不需要查知识库
_META_PATTERNS = (
    r"你是谁",
    r"你(能|会|可以)(做|干)什么",
    r"你叫什么",
    r"介绍一下你自己",
    r"刚才(说|讲|问)了?什么",
    r"你(是|用)什么(模型|大模型)",
)

_GREETING_RE = re.compile(r"^[\s,!。,.!?？!！~～、;；:：…·]*$")

# 上下文追问的特征。
#
# 孤立地看「那它需要什么权限？」确实不像技术查询，但它在追问上文时
# 几乎必然应该查知识库 —— 实测这类问题曾被误判为「直接回答」，
# 答案因此完全没用到资料。有历史时命中这些模式就强制走检索。
_FOLLOWUP_PATTERNS = (
    r"^\s*(那|这|它|他|她|该|此)",
    r"(刚才|上面|之前|前面|前面提|上述)(说|讲|提|聊)的",
    r"第[一二三四五六七八九十百\d]+(点|个|条|种|步|项|部分|章)",
    r"再(详细|具体|多|展开)?(说|讲|介绍|解释)",
    r"^\s*(继续|接着|然后呢|还有呢|还有其他)",
    r"(它的|这个的|那个的|其)",
    r"(什么意思|什么意思呀|为啥|为什么呢)\s*$",
)

_FOLLOWUP_RES = tuple(re.compile(p) for p in _FOLLOWUP_PATTERNS)


def looks_like_followup(question: str) -> bool:
    """判断是否像是「依赖上文的追问」。"""
    text = (question or "").strip()

    if not text:
        return False

    return any(pattern.search(text) for pattern in _FOLLOWUP_RES)


def _normalize(text: str) -> str:
    """去掉空白与常见语气标点，便于与寒暄词表比对。"""
    cleaned = re.sub(r"[\s!！。.?,，~～、;；:：…]+", "", text or "")
    return cleaned.lower()


def quick_route(question: str) -> bool | None:
    """规则快判。

    Returns:
        ``True`` 需要检索 / ``False`` 不需要 / ``None`` 无法判定
    """
    text = (question or "").strip()

    if not text:
        return False

    # 纯标点或表情
    if _GREETING_RE.fullmatch(text):
        return False

    normalized = _normalize(text)

    # 很短且命中寒暄词表
    if normalized in _SMALL_TALK:
        return False

    # 「你好呀」「谢谢啦」这类带语气词的
    if len(normalized) <= 8:
        for word in _SMALL_TALK:
            if word and normalized.startswith(word) and len(normalized) <= len(word) + 3:
                return False

    for pattern in _META_PATTERNS:
        if re.search(pattern, text):
            return False

    return None


# ----------------------------------------------------------------------
# LLM 路由
# ----------------------------------------------------------------------

ROUTER_PROMPT = """你是一个检索路由器，负责判断用户的问题是否需要查询**本地技术知识库**。

【需要检索】—— 内容很可能收录在本地技术文档里：
- 具体技术细节、原理、参数含义
- 命令 / 工具的用法、选项、示例
- 配置步骤、操作流程、排错方法
- 某个概念在本领域内的定义与对比

【不需要检索】—— 直接回答即可：
- 寒暄、致谢、告别、确认类回应
- 与对话本身相关的问题（你是谁、你能做什么、我刚才问了什么）
- 对**已经给出**的内容做变换：翻译、改写、总结、整理格式
- 通用常识、闲聊、与本地文档无关的开放提问

【特别注意】
如果用户是在**追问上文**（用「它」「那第二点」「再详细说说」这类指代），
而上文讨论的是技术内容，那么答案应当来自知识库 —— 判为 NEED。

只输出一个词：NEED 或 NO。不要解释，不要标点。"""


def _parse_verdict(text: str) -> bool | None:
    """解析模型输出。"""
    cleaned = (text or "").strip().upper()

    # 取第一个词，容忍模型多写了内容
    token = re.split(r"[\s,.。，、:：]+", cleaned)[0] if cleaned else ""

    if token.startswith("NEED") or token == "YES":
        return True
    if token.startswith("NO") or token == "NOT":
        return False

    # 兜底：在整段里找关键词
    if "NEED" in cleaned:
        return True
    if "NO" in cleaned:
        return False

    return None


def needs_retrieval(
    question: str,
    history: list[dict[str, str]] | None,
    llm: Any,
    *,
    enabled: bool = True,
) -> tuple[bool, str]:
    """判断是否需要检索。

    Args:
        question: 用户本轮输入。
        history: 对话历史（可作为判断依据）。
        llm: 生成模型 provider。
        enabled: 为 False 时直接返回「需要」（即关闭自适应，行为同旧版）。

    Returns:
        ``(是否需要检索, 判定依据)``
    """
    if not enabled:
        return True, "自适应检索已关闭"

    # 1) 规则快判
    quick = quick_route(question)
    if quick is not None:
        return quick, "规则判定"

    # 2) 上下文追问：有历史时优先走检索
    #
    # 这一步很关键。「那它需要什么权限？」单独看不像技术查询，但它八成
    # 在追问上文，而答案就在知识库里。实测缺了这一步会被误判为闲聊，
    # 导致答案完全不引用资料。
    if history and looks_like_followup(question):
        return True, "上下文追问"

    # 3) 交给模型判断
    try:
        context_hint = ""
        if history:
            recent = history[-4:]
            lines = []
            for message in recent:
                role = "用户" if message.get("role") == "user" else "助手"
                content = (message.get("content") or "").strip().replace("\n", " ")
                lines.append(f"{role}：{content[:120]}")
            context_hint = "【最近的对话】\n" + "\n".join(lines) + "\n\n"

        reply = llm.chat(  # type: ignore[attr-defined]
            [
                ChatMessage("system", ROUTER_PROMPT),
                ChatMessage(
                    "user",
                    f"{context_hint}【本次输入】\n{question}\n\n"
                    f"请只回答 NEED 或 NO：",
                ),
            ],
            max_tokens=8,
            temperature=0.0,
            thinking=False,
        )

        verdict = _parse_verdict(getattr(reply, "content", "") or "")

        if verdict is not None:
            return verdict, "模型判定"

    except Exception:  # noqa: BLE001
        # 判断失败时保守处理：宁可多查一次
        return True, "路由失败，保守走检索"

    return True, "无法判定，保守走检索"


def should_answer_directly(
    question: str,
    history: list[dict[str, str]] | None,
    llm: Any,
    *,
    enabled: bool = True,
) -> bool:
    """便捷封装：是否需要**跳过**检索直接回答。"""
    need, _ = needs_retrieval(question, history, llm, enabled=enabled)
    return not need


__all__ = [
    "ROUTER_PROMPT",
    "looks_like_followup",
    "needs_retrieval",
    "quick_route",
    "should_answer_directly",
]
