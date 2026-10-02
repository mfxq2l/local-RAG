"""生成式 LLM provider 工厂。

支持的 provider：

    llama_cpp   本机用 llama-server 跑 gguf（默认）
    openai      任意 OpenAI 兼容端点（Ollama / LM Studio / vLLM / 云端）

用法：

    from src.llm import get_llm

    llm = get_llm()
    ok, reason = llm.available()
    if ok:
        reply = llm.chat([ChatMessage("user", "你好")])
"""

from __future__ import annotations

import threading

from src.config import LLM_CONFIG, LlmConfig
from src.llm.base import (
    ChatDelta,
    ChatMessage,
    ChatProvider,
    ChatReply,
    ChatUsage,
    LLMError,
    LLMUnavailable,
)
from src.llm.llama_cpp import LlamaCppChat
from src.llm.openai_compat import OpenAICompatChat

# provider 别名 → 规范名
_ALIASES = {
    "llama_cpp": "llama_cpp",
    "llamacpp": "llama_cpp",
    "llama": "llama_cpp",
    "local": "llama_cpp",

    "openai": "openai",
    "openai_compat": "openai",
    "openai-compatible": "openai",
    "remote": "openai",
    "api": "openai",
}

# Ollama 的 OpenAI 兼容端口
_DEFAULT_OPENAI_BASE_URL = "http://127.0.0.1:11434/v1"

_instances: dict[str, object] = {}
_lock = threading.Lock()


def canonical_provider(name: str | None = None) -> str:
    """归一化 provider 名称。"""
    key = (name or LLM_CONFIG.provider or "llama_cpp").strip().lower()

    if key not in _ALIASES:
        raise ValueError(
            f"未知的 LLM provider: {key!r}，"
            f"可选: {sorted(set(_ALIASES))}"
        )

    return _ALIASES[key]


def _cache_key(provider: str, model: str | None) -> str:
    return f"{provider}:{(model or '').strip().lower()}"


def get_llm(
    provider: str | None = None,
    model: str | None = None,
    config: LlmConfig | None = None,
) -> object:
    """返回 provider 单例。

    Args:
        provider: ``llama_cpp``（本地离线）/ ``openai``（云端 API）。
            ``None`` 时用当前生效的方式（``data/llm_selection.json``）。
        model: 仅对 ``llama_cpp`` 有效，显式指定模型
            （文件名片段 / 清单序号 / 完整路径）。
    """
    from src.llm.cloud import active_provider, load_cloud

    config = config or LLM_CONFIG
    key = canonical_provider(provider if provider is not None else active_provider())
    ck = _cache_key(key, model)

    with _lock:
        existing = _instances.get(ck)
        if existing is not None:
            return existing

        if key == "llama_cpp":
            instance: object = LlamaCppChat(config, model=model)

        elif key == "openai":
            cloud = load_cloud()

            # 环境变量优先于持久配置，便于临时覆盖
            base_url = config.base_url or cloud.base_url or _DEFAULT_OPENAI_BASE_URL
            api_key = config.api_key or cloud.api_key
            model_name = config.model_name or cloud.model or "default"

            instance = OpenAICompatChat(
                base_url=base_url,
                model=model_name,
                api_key=api_key,
                timeout=cloud.timeout or config.request_timeout,
                label=model_name,
            )

        else:  # pragma: no cover - canonical_provider 已保证
            raise ValueError(f"未实现的 provider: {key}")

        _instances[ck] = instance

    return instance


# ----------------------------------------------------------------------
# 模型清单与切换
# ----------------------------------------------------------------------


def active_vision_endpoint() -> tuple[str, str] | None:
    """若当前对话服务已带 mmproj 就绪，返回 ``(base_url, model)``。

    供 :class:`src.vision.VisionCaptioner` 复用 —— 同一个模型没必要
    为了读图再加载一份（8GB 显卡上那是约 3GB 的浪费）。
    """
    with _lock:
        instances = list(_instances.values())

    for instance in instances:
        getter = getattr(instance, "vision_endpoint", None)
        if not callable(getter):
            continue
        try:
            endpoint = getter()
        except Exception:  # noqa: BLE001
            continue
        if endpoint:
            return endpoint

    return None


def available_models(include_auxiliary: bool = True) -> list[dict]:
    """返回可选的本地模型清单（含分类与显存估算）。"""
    from src.llm.catalog import build_catalog

    try:
        entries = build_catalog()
    except Exception:  # noqa: BLE001
        return []

    if not include_auxiliary:
        entries = [e for e in entries if e.is_chat_capable]

    return [e.to_dict() for e in entries]


def chat_models() -> list[dict]:
    """仅返回可用于问答的模型。"""
    from src.llm.catalog import build_catalog, chat_models as _chat

    try:
        return [e.to_dict() for e in _chat(build_catalog())]
    except Exception:  # noqa: BLE001
        return []


def active_model() -> dict:
    """当前生效的本地模型信息。"""
    from src.llm.catalog import build_catalog, find_model, load_selection

    selected = load_selection()
    entry = None

    try:
        if selected:
            entry = find_model(selected, build_catalog())
    except Exception:  # noqa: BLE001
        entry = None

    if entry is None:
        try:
            for candidate in build_catalog():
                if candidate.is_chat_capable:
                    entry = candidate
                    break
        except Exception:  # noqa: BLE001
            entry = None

    info: dict = {
        "selected_by": "persisted" if selected else "auto",
        "selection_file_value": selected or "",
    }

    if entry is not None:
        info["file_name"] = entry.file_name
        info["label"] = entry.label
        info["path"] = entry.path
        info["fits_vram"] = entry.fits_vram
        info["total_gb"] = entry.total_gb

    return info


def switch_model(query: str) -> dict:
    """切换**本地**模型。

    会**停掉当前的 llama-server 并释放显存**，然后写入持久选择，
    同时把使用方式切回「本地离线」。

    之所以不做「按请求切换模型」：那会让多个 llama-server 同时驻留，
    8GB 显存无法承受。

    Raises:
        ValueError: 找不到该模型（含被 ``RAG_LLM_EXCLUDE`` 排除的情况）。
    """
    from src.llm.catalog import build_catalog, find_model, invalidate
    from src.llm.state import save_state

    entries = build_catalog()
    entry = find_model(query, entries)

    if entry is None:
        usable = [e.file_name for e in entries if e.is_chat_capable]
        raise ValueError(
            f"找不到可用的模型: {query!r}。"
            f"可选: {', '.join(usable) if usable else '(无)'}"
        )

    if not entry.is_chat_capable:
        raise ValueError(
            f"{entry.file_name} 的类型是「{entry.kind}」，不能用于问答。"
        )

    # 先停掉旧服务，避免两个模型同时占用显存
    close_all()
    save_state(provider="llama_cpp", model=entry.file_name)
    invalidate()

    return entry.to_dict()


def providers_status() -> dict:
    """两种使用方式的状态（本地离线 / 云端 API）。"""
    from src.llm.cloud import active_provider, load_cloud

    active = active_provider()

    # ---- 本地离线 ----------------------------------------------------
    local_available = False
    local_reason = ""
    local_detail = ""

    try:
        local = get_llm("llama_cpp")
        local_available, local_reason = local.available()  # type: ignore[attr-defined]
        local_detail = getattr(local, "model_file", "") or ""
    except Exception as exc:  # noqa: BLE001
        local_reason = str(exc)

    # ---- 云端 API ----------------------------------------------------
    cloud = load_cloud()

    if cloud.configured:
        cloud_available = True
        cloud_reason = "ok"
        cloud_detail = f"{cloud.model} @ {cloud.base_url}"
    else:
        cloud_available = False
        cloud_reason = (
            "尚未配置。需要 Base URL、模型名与 API Key；"
            "填好后可先点「测试连接」。"
        )
        cloud_detail = ""

    return {
        "active": active,
        "providers": [
            {
                "id": "llama_cpp",
                "label": "本地离线",
                "available": local_available,
                "reason": local_reason,
                "detail": local_detail,
                "description": "本机 llama.cpp 运行 gguf，完全离线",
            },
            {
                "id": "openai",
                "label": "云端 API",
                "available": cloud_available,
                "reason": cloud_reason,
                "detail": cloud_detail,
                "description": "任意 OpenAI 兼容端点 + API Key",
            },
        ],
    }


def close_all() -> None:
    """关闭所有 provider（应用退出时调用）。"""
    with _lock:
        instances = list(_instances.values())
        _instances.clear()

    for instance in instances:
        close = getattr(instance, "close", None)
        if callable(close):
            try:
                close()
            except Exception:  # noqa: BLE001
                pass


__all__ = [
    "ChatDelta",
    "ChatMessage",
    "ChatProvider",
    "ChatReply",
    "ChatUsage",
    "LLMError",
    "LLMUnavailable",
    "LlamaCppChat",
    "OpenAICompatChat",
    "activate_model",
    "active_model",
    "active_vision_endpoint",
    "available_models",
    "canonical_provider",
    "chat_models",
    "close_all",
    "get_llm",
    "providers_status",
    "switch_model",
]

# switch_model 的别名，语义更直观
activate_model = switch_model
