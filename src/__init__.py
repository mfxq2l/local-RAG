"""
RAG 项目源码包。

子模块：
    config      全局配置
    server      FastAPI Web 服务
    embedding   Embedding 模型（Qwen3 / WeMM）
    database    Qdrant 向量库封装
    ingest      文档摄取（Markdown / PDF / Image）
    retrieval   检索（Dense / BM25 / Rerank）
    rag         检索编排、Context、Prompt
"""