"""多轮对话的会话模型与存储。

为什么需要它
------------
单轮问答（``/api/ask``）问完即忘。真正可用的对话必须解决两件事：

1. **记住上下文** —— 把历史消息一并交给生成模型，才能理解「那第二点呢」
2. **让追问可检索** —— 这是更关键的一点：向量检索只看当前 query 的字面内容，
   而「再详细说说」这种追问**本身没有任何可检索的语义**。因此需要先用
   对话历史把它改写成独立的问题（见 :mod:`src.rag.chat` 的 condense 步骤）。

存储
----
内存中保留最近使用的会话，同时把每个会话落盘到
``data/conversations/<id>.json``，重启服务后仍可继续。
"""

from __future__ import annotations

import json
import re
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from src.config import DATA_DIR


CONVERSATION_DIR = DATA_DIR / "conversations"

# 会话 id 只允许这些字符。它来自 URL，必须严格校验 ——
# 用「清洗后拼接」会把 "../<id>" 静默别名到 "<id>"，行为不可预测；
# 直接拒绝非法 id 更清晰，也彻底杜绝路径逃逸。
_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def is_valid_id(conversation_id: str | None) -> bool:
    """判断会话 id 是否合法。"""
    return bool(conversation_id and _ID_PATTERN.fullmatch(conversation_id))

# 内存中保留的会话数上限（超出后按最近使用淘汰，磁盘上仍保留）
_MAX_IN_MEMORY = 50

# 送给生成模型的历史轮数上限
DEFAULT_HISTORY_TURNS = 6

# 历史消息的字符预算（超出则从最旧的开始丢弃）
DEFAULT_HISTORY_CHARS = 6000


@dataclass
class Turn:
    """一轮对话。"""

    index: int
    question: str = ""
    answer: str = ""

    # 追问改写后的、真正用于检索的 query
    retrieval_query: str = ""

    reasoning: str = ""
    citations: list[dict[str, Any]] = field(default_factory=list)
    results: list[dict[str, Any]] = field(default_factory=list)
    context: str = ""

    mode: str = ""
    model: str = ""
    elapsed_ms: float = 0.0
    usage: dict[str, int] = field(default_factory=dict)
    error: str = ""
    created_at: float = field(default_factory=time.time)

    # 本轮是否走了知识库检索（False = 当普通对话直接回答）
    used_retrieval: bool = True
    # 路由判定依据，便于排查「为什么这次没查资料」
    route_reason: str = ""

    @property
    def is_rewritten(self) -> bool:
        """检索用的 query 是否与原始问题不同（即发生过改写）。"""
        return bool(
            self.retrieval_query
            and self.retrieval_query.strip() != self.question.strip()
        )


@dataclass
class Conversation:
    """一个会话。"""

    id: str
    title: str = "新对话"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    turns: list[Turn] = field(default_factory=list)

    # ------------------------------------------------------------------
    # 便捷属性
    # ------------------------------------------------------------------

    @property
    def turn_count(self) -> int:
        return len(self.turns)

    @property
    def last_question(self) -> str:
        return self.turns[-1].question if self.turns else ""

    def preview(self, limit: int = 60) -> str:
        """用于会话列表的摘要。"""
        for turn in self.turns:
            if turn.question:
                text = turn.question.strip().replace("\n", " ")
                return text if len(text) <= limit else text[:limit] + "…"
        return "（空会话）"

    def to_dict(self, include_turns: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "turn_count": self.turn_count,
            "preview": self.preview(),
            "last_question": self.last_question,
        }
        if include_turns:
            data["turns"] = [asdict(t) for t in self.turns]
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Conversation":
        turns = [
            Turn(**{k: v for k, v in t.items() if k in Turn.__dataclass_fields__})
            for t in (data.get("turns") or [])
        ]
        return cls(
            id=str(data.get("id") or uuid.uuid4().hex),
            title=str(data.get("title") or "新对话"),
            created_at=float(data.get("created_at") or time.time()),
            updated_at=float(data.get("updated_at") or time.time()),
            turns=turns,
        )

    # ------------------------------------------------------------------
    # 历史
    # ------------------------------------------------------------------

    def history(
        self,
        max_turns: int = DEFAULT_HISTORY_TURNS,
        max_chars: int = DEFAULT_HISTORY_CHARS,
    ) -> list[dict[str, str]]:
        """返回可放入 prompt 的历史消息（``role`` / ``content``）。

        从最近的轮次往回取，直到达到轮数或字符预算 —— 保证最近的内容一定
        在里面，而久远的先被丢掉。
        """
        if not self.turns or max_turns <= 0:
            return []

        messages: list[dict[str, str]] = []
        budget = max_chars

        for turn in reversed(self.turns[-max_turns:]):
            if not turn.answer:
                continue

            pair = [
                {"role": "user", "content": turn.question},
                {"role": "assistant", "content": turn.answer},
            ]
            cost = len(turn.question) + len(turn.answer)

            if cost > budget and messages:
                break

            budget -= cost
            messages = pair + messages

        return messages


# ----------------------------------------------------------------------
# 存储
# ----------------------------------------------------------------------


class ConversationStore:
    """会话存储：内存 + 磁盘。"""

    def __init__(self, directory: Path | None = None) -> None:
        self.directory = Path(directory or CONVERSATION_DIR)
        self.directory.mkdir(parents=True, exist_ok=True)

        self._lock = threading.RLock()
        self._cache: dict[str, Conversation] = {}

    # ------------------------------------------------------------------
    # 增删查
    # ------------------------------------------------------------------

    def create(self, title: str = "新对话") -> Conversation:
        conversation = Conversation(id=uuid.uuid4().hex[:16], title=title)
        with self._lock:
            self._cache[conversation.id] = conversation
            self._evict()
        self._save(conversation)
        return conversation

    def get(self, conversation_id: str) -> Conversation | None:
        """按 id 取会话；内存没有就从磁盘加载。id 非法时返回 ``None``。"""
        if not is_valid_id(conversation_id):
            return None

        with self._lock:
            cached = self._cache.get(conversation_id)
            if cached is not None:
                return cached

        path = self._path(conversation_id)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            conversation = Conversation.from_dict(data)
        except Exception:  # noqa: BLE001
            return None

        with self._lock:
            self._cache[conversation.id] = conversation
            self._evict()

        return conversation

    def get_or_create(
        self,
        conversation_id: str | None = None,
        title: str = "新对话",
    ) -> Conversation:
        """取已有会话；id 为空或不存在时新建。"""
        if conversation_id:
            existing = self.get(conversation_id)
            if existing is not None:
                return existing

        return self.create(title)

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        """列出会话（按最近更新排序）。"""
        items: list[Conversation] = []

        for path in self.directory.glob("*.json"):
            conversation = self.get(path.stem)
            if conversation is not None:
                items.append(conversation)

        items.sort(key=lambda c: c.updated_at, reverse=True)

        return [c.to_dict(include_turns=False) for c in items[:limit]]

    def delete(self, conversation_id: str) -> bool:
        if not is_valid_id(conversation_id):
            return False

        with self._lock:
            self._cache.pop(conversation_id, None)

        path = self._path(conversation_id)
        if path.exists():
            try:
                path.unlink()
                return True
            except OSError:
                return False

        return False

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------

    def append_turn(self, conversation: Conversation, turn: Turn) -> None:
        """追加一轮并落盘。"""
        with self._lock:
            conversation.turns.append(turn)
            conversation.updated_at = time.time()

            # 首轮时用问题作为标题
            if conversation.title in ("", "新对话") and turn.question:
                text = turn.question.strip().replace("\n", " ")
                conversation.title = text[:30] + ("…" if len(text) > 30 else "")

        self._save(conversation)

    def save(self, conversation: Conversation) -> None:
        self._save(conversation)

    def _save(self, conversation: Conversation) -> None:
        path = self._path(conversation.id)

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(
                    conversation.to_dict(include_turns=True),
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
        except Exception:  # noqa: BLE001
            # 落盘失败不应影响对话本身
            pass

    def _path(self, conversation_id: str) -> Path:
        return self.directory / f"{conversation_id}.json"

    def _evict(self) -> None:
        """内存缓存超限时淘汰最久未使用的。"""
        while len(self._cache) > _MAX_IN_MEMORY:
            oldest = min(
                self._cache.values(),
                key=lambda c: c.updated_at,
            )
            self._cache.pop(oldest.id, None)


# 全局单例
_store: ConversationStore | None = None
_store_lock = threading.Lock()


def get_store() -> ConversationStore:
    """返回全局会话存储。"""
    global _store

    with _store_lock:
        if _store is None:
            _store = ConversationStore()
        return _store


__all__ = [
    "CONVERSATION_DIR",
    "DEFAULT_HISTORY_CHARS",
    "DEFAULT_HISTORY_TURNS",
    "Conversation",
    "ConversationStore",
    "Turn",
    "get_store",
    "is_valid_id",
]
