"""BM25 检索。

使用 jieba 中文分词 + rank_bm25。
索引持久化到 data/index/bm25_{model}.pkl。
"""

from __future__ import annotations

import pickle
import re
import threading
from pathlib import Path
from typing import Any

import numpy as np

from src.config import INDEX_DIR
from src.embedding import model_key

try:
    import jieba
except ImportError as exc:  # noqa: BLE001
    raise RuntimeError(
        "缺少 jieba。请运行: pip install jieba"
    ) from exc

try:
    from rank_bm25 import BM25Okapi
except ImportError as exc:  # noqa: BLE001
    raise RuntimeError(
        "缺少 rank-bm25。请运行: pip install rank-bm25"
    ) from exc


# 关闭 jieba 的冗余日志
jieba.setLogLevel(20)


_ASCII_RE = re.compile(r"[A-Za-z0-9_]+")


def tokenize(text: str) -> list[str]:
    """中英文混合分词。"""
    tokens: list[str] = []

    # 英文 / 数字
    for m in _ASCII_RE.finditer(text):
        tokens.append(m.group(0).lower())

    # 中文
    for tok in jieba.cut_for_search(text):
        tok = tok.strip()
        if not tok:
            continue
        if _ASCII_RE.fullmatch(tok):
            continue  # 上面已经处理过
        tokens.append(tok.lower())

    return tokens


def bm25_index_path(name: str | None = None) -> Path:
    key = model_key(name)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    return INDEX_DIR / f"bm25_{key}.pkl"


# ----------------------------------------------------------------------
# 索引缓存
#
# 每次检索都会构造 RAGSearch，而它每次都要从磁盘 unpickle 整个 BM25 索引
# （1710 篇文档约 68ms）。索引内容只在重新建索引时变化，因此按
# 「路径 + mtime + 大小」缓存起来，跨请求复用。
#
# 写入方（摄取管线）在保存新索引后必须调用 invalidate_cache()，
# 否则会继续用旧索引。
# ----------------------------------------------------------------------

_cache_lock = threading.RLock()
_index_cache: dict[str, tuple[float, int, "BM25Index"]] = {}


def load_cached(path: Path) -> "BM25Index | None":
    """从缓存加载 BM25 索引（按 mtime/size 失效）。失败返回 None。"""
    try:
        stat = path.stat()
    except OSError:
        return None

    key = str(path)

    with _cache_lock:
        cached = _index_cache.get(key)
        if cached is not None:
            mtime, size, index = cached
            if mtime == stat.st_mtime and size == stat.st_size:
                return index

    index = BM25Index(name=path.stem)

    try:
        index.load(path)
    except Exception:  # noqa: BLE001
        return None

    with _cache_lock:
        _index_cache[key] = (stat.st_mtime, stat.st_size, index)

    return index


def invalidate_cache(path: Path | None = None) -> None:
    """清空 BM25 索引缓存。写入新索引后必须调用。"""
    with _cache_lock:
        if path is None:
            _index_cache.clear()
        else:
            _index_cache.pop(str(path), None)


class BM25Index:
    def __init__(self, name: str = "default") -> None:
        self.name = name
        self.chunks: list[dict[str, Any]] = []
        self.corpus_tokens: list[list[str]] = []
        self.bm25: BM25Okapi | None = None

    # ------------------------------------------------------------------
    # 构建
    # ------------------------------------------------------------------

    def build(self, chunks: list[dict[str, Any]]) -> None:
        self.chunks = list(chunks)
        self.corpus_tokens = [tokenize(c.get("content", "")) for c in self.chunks]
        self.bm25 = BM25Okapi(self.corpus_tokens) if self.corpus_tokens else None

    def load_or_build(
        self,
        path: Path,
        chunks: list[dict[str, Any]],
    ) -> None:
        """优先从磁盘加载，加载失败或为空则新建。"""
        if path.exists() and path.stat().st_size > 0:
            try:
                self.load(path)
                if self.chunks:
                    # 追加新的 chunk
                    known = {c.get("chunk_id") for c in self.chunks}
                    new = [c for c in chunks if c.get("chunk_id") not in known]
                    if new:
                        self.build(self.chunks + new)
                    return
            except Exception:  # noqa: BLE001
                pass

        self.build(chunks)

    # ------------------------------------------------------------------
    # 持久化
    # ------------------------------------------------------------------

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as f:
            pickle.dump(
                {
                    "name": self.name,
                    "chunks": self.chunks,
                    "corpus_tokens": self.corpus_tokens,
                },
                f,
            )

    def load(self, path: Path) -> None:
        with path.open("rb") as f:
            data = pickle.load(f)

        self.name = data.get("name", self.name)
        self.chunks = data.get("chunks", [])
        self.corpus_tokens = data.get("corpus_tokens", [])
        self.bm25 = BM25Okapi(self.corpus_tokens) if self.corpus_tokens else None

    # ------------------------------------------------------------------
    # 检索
    # ------------------------------------------------------------------

    def search(self, query: str, top_k: int = 20) -> list[dict[str, Any]]:
        if self.bm25 is None or not self.chunks:
            return []

        q_tokens = tokenize(query)
        if not q_tokens:
            return []

        scores = self.bm25.get_scores(q_tokens)
        if len(scores) == 0:
            return []

        top_k = min(top_k, len(scores))
        idx = np.argsort(scores)[::-1][:top_k]

        results: list[dict[str, Any]] = []
        for i in idx:
            score = float(scores[i])
            if score <= 0:
                continue

            chunk = self.chunks[int(i)]
            results.append(
                {
                    "id": chunk.get("chunk_id", ""),
                    "score": score,
                    "payload": chunk,
                    "source": "bm25",
                }
            )

        return results

    def __len__(self) -> int:
        return len(self.chunks)


__all__ = [
    "BM25Index",
    "bm25_index_path",
    "invalidate_cache",
    "load_cached",
    "tokenize",
]