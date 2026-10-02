"""问答档位：**快速** / **精确**。

背景
----
默认的生成模型（gemma-4-E4B）是 thinking 模型，回答前会先输出一大段
``reasoning_content``。实测同一道题：

    精确（开启思考）  5.70s，思考 1363 字符
    快速（关闭思考）  0.73s，思考    0 字符，答案依然正确

即 **约 7.8 倍加速**，代价是复杂问题上的推理质量略有下降。

控制手段是**请求级**的 ``chat_template_kwargs: {"enable_thinking": false}``。
（``reasoning_budget`` 无论放在顶层还是 chat_template_kwargs 都无效，实测被忽略。）
"""

from __future__ import annotations

from dataclasses import dataclass

from src.config import LLM_CONFIG


@dataclass(frozen=True)
class AnswerMode:
    """一个问答档位的完整采样参数。"""

    name: str
    label: str
    description: str

    # None = 交给服务端按 --reasoning 决定
    thinking: bool | None

    max_tokens: int
    temperature: float


FAST = AnswerMode(
    name="fast",
    label="快速",
    description=(
        "关闭思考过程，生成阶段约 1 秒；含检索端到端约 7 秒。"
        "适合简单查询与速查"
    ),
    thinking=False,
    max_tokens=512,
    temperature=0.1,
)

PRECISE = AnswerMode(
    name="precise",
    label="精确",
    description=(
        "开启思考过程，答案更严谨；含检索端到端约 17 秒。"
        "适合比较、推理类问题"
    ),
    thinking=True,
    max_tokens=1024,
    temperature=0.2,
)


MODES: dict[str, AnswerMode] = {
    FAST.name: FAST,
    PRECISE.name: PRECISE,
}

# 别名
_ALIASES = {
    "quick": "fast",
    "speed": "fast",
    "thinking": "precise",
    "accurate": "precise",
    "accuracy": "precise",
}


def resolve_mode(name: str | None = None) -> AnswerMode:
    """把档位名解析成 :class:`AnswerMode`。

    ``None`` 时使用配置的默认档位（``RAG_LLM_MODE``，默认 precise）。

    Raises:
        ValueError: 档位名未知。
    """
    key = (name or LLM_CONFIG.default_mode or PRECISE.name).strip().lower()
    key = _ALIASES.get(key, key)

    if key not in MODES:
        raise ValueError(
            f"未知的问答档位: {key!r}，可选: {sorted(MODES)}"
        )

    return MODES[key]


def mode_catalog() -> list[dict]:
    """给 API / 前端用的档位清单。"""
    return [
        {
            "name": mode.name,
            "label": mode.label,
            "description": mode.description,
            "thinking": mode.thinking,
            "max_tokens": mode.max_tokens,
            "temperature": mode.temperature,
            "default": mode.name == resolve_mode().name,
        }
        for mode in MODES.values()
    ]


__all__ = [
    "AnswerMode",
    "FAST",
    "PRECISE",
    "MODES",
    "mode_catalog",
    "resolve_mode",
]
