"""云端 LLM（OpenAI 兼容 API + API KEY）。

提供两种使用方式之一：**本地离线**（llama.cpp 跑 gguf）或**云端**（HTTP API）。

安全约定
--------
* API Key 存放在 ``data/llm_cloud.json``（``data/`` 已被 .gitignore 忽略），
  **不写进代码、不写进环境变量之外的地方**。
* 对外接口（``/api/llm/cloud``、``/api/llm/status``）**只返回掩码**，
  绝不回传明文 key。
* 日志里也不打印 key。

支持任意 OpenAI 兼容端点：OpenAI、DeepSeek、Moonshot、通义、Ollama、
LM Studio、vLLM 等 —— 只要能提供 ``/v1/chat/completions``。
"""

from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass
from pathlib import Path

from src.config import DATA_DIR
from src.llm.state import load_state, save_state

CLOUD_PATH = DATA_DIR / "llm_cloud.json"
_lock = threading.RLock()

# 常见端点，仅用于前端 placeholder 提示
KNOWN_ENDPOINTS = {
    "OpenAI": "https://api.openai.com/v1",
    "DeepSeek": "https://api.deepseek.com/v1",
    "Moonshot": "https://api.moonshot.cn/v1",
    "通义千问": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "智谱 GLM": "https://open.bigmodel.cn/api/paas/v4",
    "本地 Ollama": "http://127.0.0.1:11434/v1",
    "本地 LM Studio": "http://127.0.0.1:1234/v1",
}


@dataclass
class CloudSettings:
    """云端模型配置。"""

    base_url: str = ""
    model: str = ""
    api_key: str = ""
    temperature: float = 0.2
    max_tokens: int = 1024
    timeout: float = 120.0

    @property
    def configured(self) -> bool:
        """是否已具备可用配置（地址 + 模型 + key）。"""
        return bool(self.base_url and self.model and self.api_key)

    def to_public_dict(self) -> dict:
        """对外暴露的字段，**不含明文 key**。"""
        return {
            "configured": self.configured,
            "base_url": self.base_url,
            "model": self.model,
            "has_api_key": bool(self.api_key),
            "api_key_masked": mask_key(self.api_key),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }

    def to_dict(self) -> dict:
        """完整字段（含 key），仅用于落盘。"""
        return asdict(self)


def mask_key(key: str) -> str:
    """把 API Key 掩码成 ``sk-…a1b2`` 形式。"""
    if not key:
        return ""

    if len(key) <= 8:
        return "•" * len(key)

    return f"{key[:3]}…{key[-4:]}"


def load_cloud() -> CloudSettings:
    """读取云端配置。"""
    with _lock:
        try:
            if CLOUD_PATH.exists():
                data = json.loads(CLOUD_PATH.read_text(encoding="utf-8"))
                allowed = set(CloudSettings.__dataclass_fields__)
                return CloudSettings(
                    **{k: v for k, v in data.items() if k in allowed}
                )
        except Exception:  # noqa: BLE001
            pass

    return CloudSettings()


def save_cloud(settings: CloudSettings) -> None:
    """写入云端配置。"""
    with _lock:
        CLOUD_PATH.parent.mkdir(parents=True, exist_ok=True)
        CLOUD_PATH.write_text(
            json.dumps(settings.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def clear_cloud() -> None:
    """删除云端配置（含 key）。"""
    with _lock:
        if CLOUD_PATH.exists():
            CLOUD_PATH.unlink()


def update_cloud(
    *,
    base_url: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    timeout: float | None = None,
) -> CloudSettings:
    """增量更新云端配置。

    ``api_key`` 传**空字符串**表示「保持原有 key 不变」——
    这样用户只想改地址或模型时不必重新输入密钥。
    """
    current = load_cloud()

    if base_url is not None:
        current.base_url = base_url.strip().rstrip("/")
    if model is not None:
        current.model = model.strip()
    if api_key:  # 空串 = 不改
        current.api_key = api_key.strip()
    if temperature is not None:
        current.temperature = float(temperature)
    if max_tokens is not None:
        current.max_tokens = int(max_tokens)
    if timeout is not None:
        current.timeout = float(timeout)

    save_cloud(current)
    return current


# ----------------------------------------------------------------------
# 当前 provider
# ----------------------------------------------------------------------


def active_provider() -> str:
    """当前使用的 LLM 方式：``llama_cpp`` 或 ``openai``。"""
    stored = str(load_state().get("provider") or "").strip().lower()

    if stored in {"llama_cpp", "openai"}:
        return stored

    # 环境变量优先于默认值
    from src.config import LLM_CONFIG

    return "openai" if LLM_CONFIG.provider == "openai" else "llama_cpp"


def set_provider(provider: str) -> str:
    """切换方式并持久化。"""
    key = (provider or "").strip().lower()

    if key not in {"llama_cpp", "openai"}:
        raise ValueError(
            f"未知的 LLM 方式: {provider!r}，可选: llama_cpp, openai"
        )

    if key == "openai":
        settings = load_cloud()
        if not settings.configured:
            raise ValueError(
                "云端 API 尚未配置完整（需要 Base URL、模型名与 API Key）。"
                "请先在「云端 API → 配置」中填写并测试连接。"
            )

    save_state(provider=key)
    return key


# ----------------------------------------------------------------------
# 连接测试
# ----------------------------------------------------------------------


def test_connection(
    base_url: str,
    api_key: str,
    model: str = "",
    timeout: float = 20.0,
) -> tuple[bool, str, list[str]]:
    """测试端点连通性与可用模型。

    Returns:
        ``(是否成功, 说明, 可用模型列表)``
    """
    import httpx

    base_url = (base_url or "").strip().rstrip("/")

    if not base_url:
        return False, "Base URL 不能为空", []

    url = f"{base_url}/models"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        with httpx.Client(timeout=timeout, trust_env=False) as client:
            response = client.get(url, headers=headers)

        if response.status_code == 401:
            return False, "认证失败（401）：API Key 无效或已过期", []
        if response.status_code == 403:
            return False, "拒绝访问（403）：Key 无权访问该端点", []
        if response.status_code == 404:
            return (
                False,
                f"端点不存在（404）：{url}。请确认 Base URL 是否需要以 /v1 结尾",
                [],
            )
        if response.status_code != 200:
            return (
                False,
                f"HTTP {response.status_code}: {response.text[:200]}",
                [],
            )

        try:
            data = response.json()
            models = [
                str(item.get("id", ""))
                for item in (data.get("data") or [])
                if item.get("id")
            ]
        except Exception:  # noqa: BLE001
            models = []

        message = "连接成功"
        if models:
            message += f"，发现 {len(models)} 个模型"
            if model and model not in models:
                message += f"（未在列表中看到 {model}，服务端可能仍会接受）"

        return True, message, models

    except Exception as exc:  # noqa: BLE001
        return False, f"无法连接 {base_url}: {type(exc).__name__}: {exc}", []


__all__ = [
    "CLOUD_PATH",
    "KNOWN_ENDPOINTS",
    "CloudSettings",
    "active_provider",
    "clear_cloud",
    "load_cloud",
    "mask_key",
    "save_cloud",
    "set_provider",
    "test_connection",
    "update_cloud",
]
