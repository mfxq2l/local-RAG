"""RAG 检索与对话编排层。"""

from src.rag.answer import AnswerResult, RAGAnswerer, answer_rag
from src.rag.chat import RAGChat, condense_query
from src.rag.context import build_citations, build_context, citation_of
from src.rag.conversation import (
    Conversation,
    ConversationStore,
    Turn,
    get_store,
)
from src.rag.modes import (
    FAST,
    MODES,
    PRECISE,
    AnswerMode,
    mode_catalog,
    resolve_mode,
)
from src.rag.prompt import (
    CONDENSE_PROMPT,
    SYSTEM_PROMPT,
    build_followup_prompt,
    build_messages,
    build_rag_prompt,
)
from src.rag.search import RAGSearch, search_rag

__all__ = [
    "AnswerMode",
    "AnswerResult",
    "CONDENSE_PROMPT",
    "Conversation",
    "ConversationStore",
    "FAST",
    "MODES",
    "PRECISE",
    "RAGAnswerer",
    "RAGChat",
    "RAGSearch",
    "Turn",
    "answer_rag",
    "build_citations",
    "build_context",
    "build_followup_prompt",
    "build_messages",
    "build_rag_prompt",
    "citation_of",
    "condense_query",
    "get_store",
    "mode_catalog",
    "resolve_mode",
    "SYSTEM_PROMPT",
    "search_rag",
]
