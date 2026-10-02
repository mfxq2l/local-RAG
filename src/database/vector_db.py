"""Qdrant 向量数据库封装（本地 embedded 模式）。

设计要点
--------
1. **每个 embedding 模型一个 collection**：不同模型的向量维度不同，必须隔离。

       rag_knowledge_qwen3   (2560 维)
       rag_knowledge_wemm    (2048 维)

2. **point id 使用 UUID**：Qdrant 的 string id 必须是 UUID，因此 ingest 侧用
   :func:`src.ids.chunk_point_id` 做了确定性映射；可读的 ``chunk_id`` 保存在
   payload 里。

3. **线程安全**：FastAPI 会把同步接口丢进线程池并发执行，而嵌入式
   QdrantClient 并不保证线程安全，因此所有客户端操作都由一把可重入锁串行化。

4. **检索使用 query_points**：qdrant-client 1.19 已移除 ``QdrantClient.search``，
   必须改用 ``query_points``。
"""

from __future__ import annotations

import atexit
import shutil
import threading
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient, models

from src.config import (
    EMBEDDING_MODELS,
    QDRANT_CONFIG,
)
from src.embedding import model_key


# 距离算法名 → qdrant 枚举
_DISTANCE_MAP: dict[str, models.Distance] = {
    "cosine": models.Distance.COSINE,
    "dot": models.Distance.DOT,
    "euclid": models.Distance.EUCLID,
    "manhattan": models.Distance.MANHATTAN,
}


# collection key → VectorDB 单例
_db_cache: dict[str, "VectorDB"] = {}


class VectorDB:
    """单个 collection 的读写封装。"""

    def __init__(
        self,
        collection_name: str,
        dimension: int,
        path: str | None = None,
    ) -> None:
        self.collection_name = collection_name
        self.dimension = dimension
        self.path = Path(path or str(QDRANT_CONFIG.path))

        # 嵌入式客户端不是线程安全的，用可重入锁串行化所有访问。
        self._lock = threading.RLock()
        self._closed = False

        self.client = QdrantClient(path=str(self.path))

    # ------------------------------------------------------------------
    # Collection 生命周期
    # ------------------------------------------------------------------

    def exists(self) -> bool:
        """collection 是否存在。"""
        with self._lock:
            return bool(self.client.collection_exists(self.collection_name))

    def clear(self) -> int:
        """清空 collection 中的**全部 point**，保留 collection 本身。

        为什么不用 ``delete_collection`` + ``create_collection``：
        QdrantLocal 的 ``delete_collection`` 只从 ``meta.json`` 摘除条目，
        磁盘上的 ``collection/<name>/storage.sqlite`` 仍然保留；随后
        ``create_collection`` 同名 collection 时会**把旧 shard 重新挂载**，
        于是「重建」变成了「数据复活」。

        实测：drop → count 0 → create → count 恢复为原值。
        而用空 ``Filter`` 删除所有 point，可以真正清零。

        Returns:
            被清掉的 point 数量。
        """
        with self._lock:
            if not self.client.collection_exists(self.collection_name):
                return 0

            before = int(self.client.count(self.collection_name).count)

            if before == 0:
                return 0

            self.client.delete(
                collection_name=self.collection_name,
                # 空 Filter 匹配所有 point
                points_selector=models.FilterSelector(
                    filter=models.Filter()
                ),
                wait=True,
            )

            after = int(self.client.count(self.collection_name).count)

            return max(0, before - after)

    def existing_dimension(self) -> int | None:
        """读取已存在 collection 的向量维度（读不到返回 None）。"""
        with self._lock:
            if not self.client.collection_exists(self.collection_name):
                return None

            try:
                info = self.client.get_collection(self.collection_name)
                params = info.config.params.vectors
            except Exception:  # noqa: BLE001
                return None

            size = getattr(params, "size", None)
            return int(size) if size else None

    def _remove_shard_directory(self) -> bool:
        """删除 collection 在磁盘上的分片目录。

        QdrantLocal 的存储布局是 ``<path>/collection/<name>/``。
        这是 qdrant-client 的实现细节，因此整体做了防御性处理：
        取不到或删不掉都不致命，只是无法完成「维度变更」这类硬重置。
        """
        shard_dir = self.path / "collection" / self.collection_name

        try:
            if shard_dir.is_dir():
                shutil.rmtree(shard_dir)
                return True
        except OSError:
            return False

        return False

    def ensure_collection(self, recreate: bool = False) -> None:
        """确保 collection 存在且可用。

        Args:
            recreate: 为 True 时清空已有数据后重建。

                维度一致 → 用 :meth:`clear` 清空（可靠）
                维度不一致 → 删除分片目录后重建（硬重置）

        Raises:
            RuntimeError: 维度不一致且无法完成硬重置。
        """
        with self._lock:
            exists = self.client.collection_exists(self.collection_name)

            if exists and recreate:
                current = self.existing_dimension()

                if current is not None and current != self.dimension:
                    # 维度变了，必须真正重建
                    self.client.delete_collection(self.collection_name)
                    removed = self._remove_shard_directory()

                    if not removed and (
                        self.path / "collection" / self.collection_name
                    ).exists():
                        raise RuntimeError(
                            f"collection {self.collection_name} 的向量维度为 "
                            f"{current}，与当前配置 {self.dimension} 不一致，"
                            f"且无法自动清理磁盘分片。请手动删除 "
                            f"{self.path / 'collection' / self.collection_name}"
                        )
                else:
                    self.clear()

                exists = self.client.collection_exists(self.collection_name)

            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=self.dimension,
                        distance=_DISTANCE_MAP.get(
                            QDRANT_CONFIG.distance.lower(),
                            models.Distance.COSINE,
                        ),
                    ),
                    hnsw_config=models.HnswConfigDiff(
                        m=QDRANT_CONFIG.hnsw_m,
                        ef_construct=QDRANT_CONFIG.hnsw_ef_construct,
                    ),
                )

    def drop(self) -> None:
        """从 Qdrant 元数据中删除 collection。

        重要：QdrantLocal 下 ``delete_collection`` **不会**删除磁盘上的
        ``collection/<name>/storage.sqlite``。客户端还开着时该文件被占用
        （Windows 上无法删除），所以随后同名 ``create_collection`` 会把旧
        shard 重新挂载，**旧数据复活**。

        因此：

        * 想「清空数据」→ 用 :meth:`clear`，不要用 drop + create；
        * 想「物理清除」→ 关闭所有客户端后手动删除 ``data/qdrant``。

        这里仍然尽力尝试删除分片目录（客户端已关闭时有效）。
        """
        with self._lock:
            if self.client.collection_exists(self.collection_name):
                self.client.delete_collection(self.collection_name)

            self._remove_shard_directory()

    def count(self) -> int:
        """当前 collection 中的 point 数量。"""
        with self._lock:
            if self._closed:
                return 0
            if not self.client.collection_exists(self.collection_name):
                return 0
            return int(self.client.count(self.collection_name).count)

    def close(self) -> None:
        """释放底层客户端（会释放 data/qdrant 的锁文件）。幂等。"""
        with self._lock:
            if self._closed:
                return
            self._closed = True

            try:
                self.client.close()
            except Exception:  # noqa: BLE001
                pass

    # ------------------------------------------------------------------
    # 写入
    # ------------------------------------------------------------------

    def upsert(
        self,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
        batch_size: int = 64,
    ) -> int:
        """批量写入 / 更新向量。

        Args:
            ids: point id（必须是 UUID 字符串）。
            vectors: 与 ids 等长的向量列表。
            payloads: 与 ids 等长的 payload。
            batch_size: 单次请求的批量大小。

        Returns:
            写入成功的 point 数。

        Raises:
            ValueError: 三个序列长度不一致。
        """
        if not (len(ids) == len(vectors) == len(payloads)):
            raise ValueError(
                "ids / vectors / payloads 长度必须一致："
                f"{len(ids)} vs {len(vectors)} vs {len(payloads)}"
            )

        if not ids:
            return 0

        self.ensure_collection()

        total = 0
        with self._lock:
            for i in range(0, len(ids), batch_size):
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=models.Batch(
                        ids=ids[i : i + batch_size],
                        vectors=vectors[i : i + batch_size],
                        payloads=payloads[i : i + batch_size],
                    ),
                    wait=True,
                )
                total += len(ids[i : i + batch_size])

        return total

    # ------------------------------------------------------------------
    # 删除 / 清理
    # ------------------------------------------------------------------

    def doc_ids(self) -> set[str]:
        """扫描 payload，返回库中出现过的全部 ``doc_id``。"""
        with self._lock:
            if not self.client.collection_exists(self.collection_name):
                return set()

            found: set[str] = set()
            offset: Any = None

            while True:
                records, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=512,
                    offset=offset,
                    with_payload=["doc_id"],
                    with_vectors=False,
                )

                for record in records:
                    payload = record.payload or {}
                    doc_id = payload.get("doc_id")
                    if doc_id:
                        found.add(str(doc_id))

                if offset is None:
                    break

            return found

    def delete_by_doc_ids(self, doc_ids: list[str]) -> int:
        """删除指定文档的全部 point，返回删除条数。"""
        if not doc_ids:
            return 0

        return self._delete_by_field("doc_id", doc_ids)

    def delete_by_chunk_ids(self, chunk_ids: list[str]) -> int:
        """按 ``chunk_id`` 精确删除 point。

        用于「重建」时的收敛：point id 是 ``chunk_id`` 的确定性 UUIDv5，
        因此重建只需全量 upsert + 删除不在本次结果中的旧 chunk，
        **无需先清空 collection** —— 这样中途崩溃也不会丢失索引。
        """
        if not chunk_ids:
            return 0

        return self._delete_by_field("chunk_id", chunk_ids)

    def _delete_by_field(self, key: str, values: list[str]) -> int:
        """按 payload 字段的值集合批量删除，返回删除条数。"""
        with self._lock:
            if self.client is None or self._closed:
                return 0

            if not self.client.collection_exists(self.collection_name):
                return 0

            before = self.count()

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key=key,
                                match=models.MatchAny(any=list(values)),
                            )
                        ]
                    )
                ),
                wait=True,
            )

            after = self.count()

        return max(0, before - after)

    # ------------------------------------------------------------------
    # 检索
    # ------------------------------------------------------------------

    def payload_values(self, key: str) -> set[str]:
        """扫描 payload，返回某个字段的全部取值（去重）。

        用于回答「哪些文档已经被索引了」。局部 sqlite 下 1700 条只需毫秒级。
        """
        values: set[str] = set()

        with self._lock:
            if self._closed:
                return values
            if not self.client.collection_exists(self.collection_name):
                return values

            offset: Any = None

            while True:
                records, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=512,
                    offset=offset,
                    with_payload=[key],
                    with_vectors=False,
                )

                for record in records:
                    payload = record.payload or {}
                    value = payload.get(key)
                    if value:
                        values.add(str(value))

                if offset is None:
                    break

        return values

    def count_where(self, key: str, value: str) -> int:
        """按 payload 字段计数（支持 ``a.b`` 形式的嵌套键）。"""
        with self._lock:
            if self._closed:
                return 0
            if not self.client.collection_exists(self.collection_name):
                return 0

            try:
                result = self.client.count(
                    collection_name=self.collection_name,
                    count_filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key=key,
                                match=models.MatchValue(value=value),
                            )
                        ]
                    ),
                )
                return int(result.count)
            except Exception:  # noqa: BLE001
                return 0

    def get_vectors(
        self,
        point_ids: list[str],
    ) -> dict[str, list[float]]:
        """按 point id 批量取回**已存储的向量**。

        用途：重排（rerank）需要「query 与候选文档」的余弦相似度。候选文档
        的向量在建索引时就已经算过并存在 Qdrant 里了，用同一模型、同一段
        文本算出的向量与重新 embedding 完全一致，因此直接取回即可，
        无需重复推理。

        实测收益：rerank 从 **4.52s 降到毫秒级**。

        Returns:
            ``{point_id: vector}``；取不到的 id 不会出现在结果中。
        """
        if not point_ids:
            return {}

        with self._lock:
            if self._closed:
                return {}

            if not self.client.collection_exists(self.collection_name):
                return {}

            found: dict[str, list[float]] = {}

            # 分批，避免一次请求过大
            batch_size = 128
            for start in range(0, len(point_ids), batch_size):
                batch = point_ids[start : start + batch_size]

                try:
                    records = self.client.retrieve(
                        collection_name=self.collection_name,
                        ids=batch,
                        with_payload=False,
                        with_vectors=True,
                    )
                except Exception:  # noqa: BLE001
                    continue

                for record in records:
                    vector = record.vector
                    if isinstance(vector, dict):
                        # 命名向量：这里只用了单个匿名向量
                        vector = next(iter(vector.values()), None)
                    if vector is not None:
                        found[str(record.id)] = list(vector)

            return found

    def search(
        self,
        query_vector: list[float],
        top_k: int = 20,
        score_threshold: float | None = None,
        query_filter: models.Filter | None = None,
    ) -> list[dict[str, Any]]:
        """向量相似度检索。

        使用 ``query_points``（qdrant-client >= 1.19 已移除 ``search``）。

        Returns:
            ``[{"id", "score", "payload"}, ...]``，按相似度降序。
        """
        with self._lock:
            if not self.client.collection_exists(self.collection_name):
                return []

            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter,
                with_payload=True,
                with_vectors=False,
            )

        results: list[dict[str, Any]] = []
        for hit in response.points:
            payload = dict(hit.payload or {})
            results.append(
                {
                    "id": str(hit.id),
                    "score": float(hit.score),
                    "payload": payload,
                }
            )

        return results


# ----------------------------------------------------------------------
# 工厂 / 生命周期
# ----------------------------------------------------------------------


def get_vector_db(
    name: str | None = None,
    recreate: bool = False,
) -> VectorDB:
    """按 embedding 模型返回对应的 VectorDB 单例。

    注意：``recreate`` **每次调用都会生效**（旧实现只在首次创建单例时判断，
    导致服务运行期间「重建索引」无法真正清空 collection）。
    """
    key = model_key(name)

    db = _db_cache.get(key)

    if db is None:
        cfg = EMBEDDING_MODELS[key]
        db = VectorDB(
            collection_name=f"{QDRANT_CONFIG.collection_name}_{key}",
            dimension=cfg.dimension,
        )
        _db_cache[key] = db

    db.ensure_collection(recreate=recreate)

    return db


def close_all() -> None:
    """关闭所有已打开的 collection 客户端。

    在应用退出（FastAPI lifespan / atexit）时调用，
    用于释放 data/qdrant 目录的锁并避免解释器关闭期的噪音报错。
    """
    for db in list(_db_cache.values()):
        db.close()
    _db_cache.clear()


# 解释器退出时主动关闭客户端。
# 否则 QdrantClient.__del__ 会在 Python 关闭后期被调用，抛出
# "ImportError: sys.meta_path is None, Python is likely shutting down"。
atexit.register(close_all)


__all__ = [
    "VectorDB",
    "get_vector_db",
    "close_all",
]
