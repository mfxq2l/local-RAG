# 本地中文 RAG 知识库问答系统

一个本地运行、离线可用的中文 RAG（Retrieval-Augmented Generation，检索增强生成）知识库问答系统。知识库位于 `File/`，当前包含 `File/Markdown/` 下的 27 份中文技术速查卡，以及 `File/image/` 下的示例图片。

切块、嵌入、向量检索、稀疏检索、融合、重排、生成等环节均在本机执行，不依赖云端 API。
当然,你可以往File文件夹里添加文件,比如说图片就放到File/image,以此类推

# 国内开发者如果无法访问huggingface,可以去隔壁的魔搭看看[https://modelscope.cn/models]

# 此项目使用deepseek制作,感谢deepseek
---

## 模型下载

运行项目前，请先下载必需的模型文件，并放入对应的目录中：

| 模型 | 文件名 | 目标目录 | 下载链接 |
| --- | --- | --- | --- |
| WeMM Embedding | `WeMM-Embedding-2B-Q4_K_M.gguf` | `models/WeMM/` | [下载](https://huggingface.co/DreamBlooms/WeMM-Embedding-2B-GGUF/resolve/main/WeMM-Embedding-2B-Q4_K_M.gguf?download=true) |
| WeMM mmproj | `mmproj-WeMM-Embedding-2B-BF16.gguf` | `models/WeMM/` | [下载](https://huggingface.co/DreamBlooms/WeMM-Embedding-2B-GGUF/resolve/main/mmproj-WeMM-Embedding-2B-BF16.gguf?download=true) |
| Qwen3 Embedding | `Qwen3-Embedding-4B-Q4_K_M.gguf` | `models/qwen3/` | [下载](https://huggingface.co/Qwen/Qwen3-Embedding-4B-GGUF/resolve/main/Qwen3-Embedding-4B-Q4_K_M.gguf?download=true) |
| Gemma Chat | `gemma-4-E2B-it-UD-Q4_K_XL.gguf` | `models/LLM/` | [下载](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q4_K_XL.gguf?download=true)还有它的mmproj(https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/mmproj-BF16.gguf?download=true) |

> **注意：** `models/` 目录已被 `.gitignore` 忽略，你只需要下载自己实际使用的模型即可。

## 功能概览

| 环节 | 实现 |
| --- | --- |
| Embedding | `Qwen3-Embedding-4B-Q4_K_M.gguf`，2560 维，通过 `llama-server.exe --embedding` 提供 OpenAI 兼容的 `/v1/embeddings` |
| 备用 Embedding | `WeMM-Embedding-2B`，2048 维，可用于多模态相关实验 |
| 向量库 | Qdrant 本地 embedded 模式，数据目录 `data/qdrant`；不同 embedding 模型使用不同 collection，如 `rag_knowledge_qwen3`、`rag_knowledge_wemm` |
| 稀疏检索 | jieba 分词 + rank_bm25，索引持久化到 `data/index/bm25_<model>.pkl` |
| 融合 | RRF（Reciprocal Rank Fusion，k=60） |
| 重排 | bi-encoder 余弦相似度重排 |
| 生成 | 本地 llama.cpp + gguf instruct 模型，或任意 OpenAI 兼容端点 |
| Web | FastAPI + 原生 HTML/JS 前端，无需 npm 构建 |

其他能力：

- 生成式问答：检索、拼装 context、生成带引用编号的回答
- SSE 流式输出：状态、引用、思考过程、token 逐块返回
- thinking 模型支持：思考过程与正文分离
- 引用列表：答案中的 `[1] [2]` 对应到具体文件与章节
- 索引并发保护：同一时刻只允许一个建索引任务
- 失效文档清理：删除或改名后的文档，其残留 chunk 会在索引时清理
- 多轮对话：会话持久化、历史注入、追问改写
- 联网搜索：本地结果之外可追加网页结果
- 云端 API：可切换本地 llama.cpp 或 OpenAI 兼容云端端点
- 设置与用量：服务端持久化设置，累计 token 用量

---

## 运行方式（embedded Python）

项目自带 embedded Python，位于 `runtime/python3.12`。embedded 发行版的 `python312._pth` 会固定 `sys.path`，因此以下方式不可用：

```bat
:: 不可用
runtime\python3.12\python.exe -m src.cli serve

:: 不可用，PYTHONPATH 会被 ._pth 忽略
set PYTHONPATH=C:\Users\mfxq2\Desktop\RAG
runtime\python3.12\python.exe -m src.cli serve
```

正确方式是通过项目根目录的 `run.py` 运行：

```bat
runtime\python3.12\python.exe run.py <子命令>
```

`run.py` 位于项目根目录，脚本方式运行时会将项目根目录加入 `sys.path`，并将标准输出切换为 UTF-8，避免 Windows 控制台中文乱码。

---

## 快速开始

以下命令均在项目根目录执行。

### 1. 环境自检

```bat
cd C:\Users\mfxq2\Desktop\RAG
runtime\python3.12\python.exe run.py check
```

检查项包括：Python 运行时、`llama-server.exe`、embedding 模型文件、Markdown 文档数、Qdrant collection、已索引 chunk 数、BM25 索引、可用的生成式 LLM 模型。

### 2. 建索引

```bat
runtime\python3.12\python.exe run.py index --rebuild
```

索引会写入 Qdrant，并生成 BM25 索引文件。

### 3. 提问

```bat
:: 纯检索，不调用生成模型
runtime\python3.12\python.exe run.py search "nmap -sS 是什么"

:: 检索 + 生成式问答
runtime\python3.12\python.exe run.py ask "nmap -sS 是什么"
```

### 4. Web 界面

```bat
runtime\python3.12\python.exe run.py serve
```

打开 <http://127.0.0.1:8000/ui>。

---

## 命令行用法

统一入口为 `run.py`。

```bat
cd C:\Users\mfxq2\Desktop\RAG

runtime\python3.12\python.exe run.py check
runtime\python3.12\python.exe run.py config
runtime\python3.12\python.exe run.py index --rebuild
runtime\python3.12\python.exe run.py stats
runtime\python3.12\python.exe run.py search "nmap -sS 是什么"
runtime\python3.12\python.exe run.py ask "nmap -sS 是什么"
runtime\python3.12\python.exe run.py ask "..." --show-thinking
runtime\python3.12\python.exe run.py ask "..." --fast
runtime\python3.12\python.exe run.py ask "..." --precise
runtime\python3.12\python.exe run.py ask "..." --llm 2
runtime\python3.12\python.exe run.py models
runtime\python3.12\python.exe run.py models --use Qwen3.8-4B
runtime\python3.12\python.exe run.py models --detail Qwen
runtime\python3.12\python.exe run.py models --all
runtime\python3.12\python.exe run.py llm --prompt "你好"
runtime\python3.12\python.exe run.py serve
runtime\python3.12\python.exe run.py test
runtime\python3.12\python.exe run.py test -v
```

### 子命令说明

| 子命令 | 作用 | 常用参数 |
| --- | --- | --- |
| `check` | 环境自检 | — |
| `config` | 打印当前生效配置并校验 | `--skip-validate` |
| `index` | 构建 / 重建索引 | `--rebuild`、`--no-prune`、`--model`、`--pdf`、`--pdf-images`、`--images` |
| `stats` | 全库切块统计 | `--json` |
| `search` | 纯检索 | `--top-k`、`--no-bm25`、`--no-rerank`、`--model`、`--context`、`--json`、`--web` |
| `ask` | 检索 + 生成式问答 | `--top-k`、`--model`、`--provider`、`--llm`、`--mode fast\|precise`、`--fast`、`--precise`、`--no-stream`、`--show-thinking`、`--json`、`--web` |
| `models` | 模型清单 / 详情 / 切换 | `--use`、`--clear`、`--detail`、`--all`、`--json` |
| `llm` | 查看生成模型状态或试跑 prompt | `--provider`、`--prompt` |
| `serve` | 启动 FastAPI Web 服务 | — |
| `chat` | 终端交互式多轮对话 | `--top-k`、`--llm`、`--provider`、`--mode`、`--show-thinking`、`--no-images`、`--web` |
| `cloud` | 配置 / 测试 / 切换云端 LLM | `--base-url`、`--model`、`--api-key`、`--test`、`--use`、`--clear` |
| `test` | 运行单元测试 | `--pattern`、`-v` |

`ask` 在生成模型不可用时会打印 `[error]` 并以退出码 `2` 结束，同时提示可改用 `run.py search`。

---

## 问答档位：快速 / 精确

`ask`、`/api/ask`、`/api/ask/stream` 与 Web 界面均支持切换档位。

| 档位 | 思考过程 | `max_tokens` | `temperature` |
| --- | --- | --- | --- |
| `fast` | 关闭 | 512 | 0.1 |
| `precise` | 开启 | 1024 | 0.2 |

默认档位由 `RAG_LLM_MODE` 决定，默认 `precise`。

档位控制通过请求级参数实现：

```json
{"chat_template_kwargs": {"enable_thinking": false}}
```

`fast` 关闭思考过程，`precise` 开启思考过程。`reasoning_budget` 在当前实现中不用于控制思考过程。

---

## 模型管理

将 gguf 放入 `models/LLM/` 即会被自动发现。也可以通过 `RAG_LLM_MODEL_DIRS` 指定其他搜索目录。

当前 `models/LLM/` 下包含：

| 文件 | 作用 |
| --- | --- |
| `gemma-4-E2B-it-UD-Q4_K_XL.gguf` | 对话模型，同时可配合视觉投影器读图 |
| `mmproj-gemma-4-E2B-it-BF16.gguf` | 视觉投影器 |

### 模型类型识别

`run.py models` 会读取 GGUF 头部元数据，区分：

| 类型 | 判断依据 | 能否问答 |
| --- | --- | --- |
| `chat` 对话 | 有 `tokenizer.chat_template` 的主模型 | 是 |
| `translation` 翻译 | `general.tags` 含 `translation` | 是，但不设为默认 |
| `embedding` 向量 | 架构属于 bert/bge/gte 等 | 否 |
| `vision` 投影器 | 文件名 `mmproj-`/`mtp-`，或架构为 `clip` | 否 |
| `base` 基座 | 没有对话模板 | 否 |

多模态对话模型仍归为 `chat`，纯投影器归为 `vision`。

### 显存估算与挑选顺序

```
权重体积 + KV cache + 预留（默认 3GB，给常驻 embedding 模型） ≤ 显存预算
```

KV cache 估算：

```
2 × 层数 × KV头数 × 每头维度 × 上下文长度 × 2字节
```

挑选顺序：

1. 项目自带目录优先
2. 可对话
3. 显存装得下
4. 偏好关键字
5. 体积

装不下的模型会标记，仍可手动选择，但会自动退回 CPU 推理。

### 切换模型

```bat
runtime\python3.12\python.exe run.py models --use Qwen3.8-4B
```

也可以在 Web 界面顶栏下拉框中切换。切换时会：

1. 停掉当前 llama-server 并释放显存
2. 写入 `data/llm_selection.json`
3. 新模型在下次提问时懒加载

同一时刻只驻留一个对话模型。

### 排除模型

`RAG_LLM_EXCLUDE` 命中的模型不会出现在清单里，也无法通过名字、序号或界面选中。

### 模型搜索目录

默认只扫描 `models/LLM`。需要临时引入外部模型时显式覆盖：

```bat
set RAG_LLM_MODEL_DIRS=models\LLM;D:\other\models
```

---

## 多模态检索（图片）

### 当前模型配置

`models/LLM/` 下包含一个对话模型和一个视觉投影器：

| 文件 | 作用 |
| --- | --- |
| `gemma-4-E2B-it-UD-Q4_K_XL.gguf` | 对话 + 读图 |
| `mmproj-gemma-4-E2B-it-BF16.gguf` | 视觉投影器 |

对话服务会自动挂上配对的 mmproj。同一个 llama-server 既能对话又能读图，视觉描述器在需要时复用该服务。

### 直接问图片

因为对话服务带 mmproj，可以直接对图片提问：

```bat
runtime\python3.12\python.exe run.py chat
你> /image 7869275C8C80EC713F001C54309B788D.jpg
已附加图片：7869275C8C80EC713F001C54309B788D.jpg
你> 这张图里有什么？用一句话说明
```

HTTP API 同样支持：`POST /api/chat` 的 `image` 字段可传相对 `File/image` 的路径或 `data:` URL。

附图时使用单独的提示词，不沿用纯 RAG 模板。

### 图片向量化方案

llama.cpp 的 `/v1/embeddings` 不支持图片输入。因此采用以下方案：

```
图片 → 视觉模型生成文本描述
     → 文本 embedding
     → 写入与文本相同的向量库
```

图片描述会按「路径 + 大小 + mtime」缓存在 `data/captions_cache.json`，重复建索引不会重算。

### 使用

```bat
:: 索引时默认处理 File/image 下的图片
runtime\python3.12\python.exe run.py index --rebuild

:: 跳过图片
runtime\python3.12\python.exe run.py index --rebuild --no-images
```

检索 / 问答请求中的 `include_images` 控制是否把图片纳入结果。

### 换用 WeMM 做向量化

```bat
set RAG_EMBEDDING_MODEL=wemm
runtime\python3.12\python.exe run.py index --rebuild
```

WeMM 是 2048 维，Qwen3 是 2560 维，因此会写入不同 collection。

---

## 两种使用方式：本地离线 / 云端 API

生成式问答支持两种方式，可在 CLI 或 Web 界面切换。

### 1. 本地离线

llama.cpp 在本机运行 gguf，完全离线。

### 2. 云端 API

支持任意 OpenAI 兼容端点，例如 OpenAI、DeepSeek、Moonshot、通义千问、智谱 GLM、本地 Ollama / LM Studio / vLLM 等。

```bat
:: 配置，api_key 留空表示保持原有 Key 不变
runtime\python3.12\python.exe run.py cloud ^
    --base-url https://api.deepseek.com/v1 ^
    --model deepseek-chat ^
    --api-key sk-xxxxxxxx

runtime\python3.12\python.exe run.py cloud --test
runtime\python3.12\python.exe run.py cloud --use openai
runtime\python3.12\python.exe run.py cloud --use llama_cpp
runtime\python3.12\python.exe run.py cloud --clear
```

常用端点：

| 服务 | Base URL |
| --- | --- |
| OpenAI | `https://api.openai.com/v1` |
| DeepSeek | `https://api.deepseek.com/v1` |
| Moonshot | `https://api.moonshot.cn/v1` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` |
| 本地 Ollama | `http://127.0.0.1:11434/v1` |

### API Key 约定

- Key 存放在 `data/llm_cloud.json`，`data/` 已被 `.gitignore` 忽略
- 对外接口只返回掩码，不返回明文
- 日志中不打印 Key
- 未配置完整时切换云端会被拒绝，返回 400

---

## 联网搜索

本地知识库只覆盖 `File/` 下的文档。开启联网后，搜索结果会追加在本地结果之后，一起进入 Context。引用中带 `url` 与 `source_type=web`，前端渲染为可点击外链。

### 后端选择

默认使用 Bing。

| 后端 | 需要密钥 | 说明 |
| --- | --- | --- |
| `bing` | 否 | 默认后端，免密钥，结构稳定 |
| `baidu` | 否 | 免密钥，返回跳转链接 |
| `duckduckgo` | 否 | 部分代理环境下可能因证书校验失败 |
| `searxng` | 否 | 需填实例地址 |
| `tavily` / `serper` / `brave` | 是 | API 型，需要 Key |

### 使用

```bat
:: 命令行
runtime\python3.12\python.exe run.py search "问题" --web
runtime\python3.12\python.exe run.py ask "问题" --web --web-limit 5
runtime\python3.12\python.exe run.py chat --web

:: 或使用 WebUI 左下角「设置」→「联网搜索」
```

HTTP 接口在 `/api/search`、`/api/ask`、`/api/chat` 的 body 里加 `use_web` / `web_limit` / `web_fetch_pages`。

### 抓正文与摘要

`fetch_pages` 开启时会并行抓取前 N 条网页正文，默认 3 条。单页正文会截断到 `max_page_chars`，默认 3000。

### 实现说明

- 代理需要显式传入，避免 httpx 读取环境变量时解析 `NO_PROXY` 中的 IPv6 方括号条目失败。
- HTML 取正文未依赖 lxml / bs4，使用标准库级别的正则处理，并优先抽取 `<article>` / `<main>` / 常见正文容器，再去掉开头导航菜单。
- 抓取前会校验目标地址，拒绝非 http(s) 与内网地址。

---

## 设置与用量统计

### 设置持久化

WebUI 设置保存在服务端 `data/ui_settings.json`，不是 localStorage。三组设置：

| 分组 | 内容 |
| --- | --- |
| `general` | `language`(zh/en)、`theme`(dark/light/system)、`font_size` |
| `retrieval` | `top_k`、`use_bm25`、`use_reranker`、`include_images`、`min_relevance` |
| `chat` | `mode`(fast/precise)、`condense`、`stream` |

写入采用深合并 + 白名单校验：只提交要改的字段，未知分组 / 字段忽略，枚举值只接受固定取值，数值会被夹到合法区间。

### Token 用量统计

每次调用的 `usage` 会按时间累积并持久化到 `data/usage_stats.json`，可按模型、按用途（`chat` / `ask` / `condense`）、按天查看。

流式响应的用量需要显式请求：

```json
{"stream": true, "stream_options": {"include_usage": true}}
```

服务端会在最后补一个 `choices` 为空、只含 `usage` 的 chunk。

---

## 多轮对话

单轮问答问完即忘。对话功能解决两件事：

1. 记住上下文：历史消息一并交给生成模型
2. 让追问可检索：每轮开始前先用 LLM 将追问改写为独立可检索的问题

向量检索与 BM25 只看 query 的字面内容。类似「那第二点呢」「再详细说说」「它需要什么权限？」的追问本身不含可检索语义，直接检索会召回无关内容。因此每轮开始前会先做 condense，再用改写后的 query 检索。

改写失败、输出为空、输出过长、或与原文相同，都会退回原问题，不中断对话。关闭 `condense` 可以省掉这次调用。

### 使用

```bat
:: 终端交互式对话
runtime\python3.12\python.exe run.py chat

:: 会话内命令
/new         开新会话
/history     查看本会话的问题
/citations   显示上一次回答的引用
/mode fast   切换档位
/quit        退出
```

Web 界面有独立的「对话」标签页，支持会话列表、切换、删除与流式输出。

会话持久化在 `data/conversations/<id>.json`，重启服务后可继续。会话 id 来自 URL，使用严格白名单校验。

---

## 相关性下限与检索策略

当前策略是：任何输入一律检索一次，重排后按相关性下限过滤。

```
任何输入
   ↓
一律检索一次
   ↓
重排后按相关性下限 0.45 过滤
   ├─ 有结果 → 走 RAG，标注引用
   └─ 无结果 → 当普通问题自然回答
```

默认相关性下限由 `RAG_MIN_RELEVANCE` 控制，默认 `0.45`。设为 `0` 可关闭过滤。

旧的「先判断要不要检索」路由可通过 `RAG_ROUTER_ENABLED=1` 启用，默认关闭。

---

## 检索与生成流程

```
用户提问
   │
   ├─► Dense 检索   Qwen3-Embedding-4B (2560d) ──► Qdrant query_points
   │
   ├─► 稀疏检索     jieba 分词 ──► rank_bm25（data/index/bm25_<model>.pkl）
   │
   ├─► 融合         RRF (k=60)
   │
   ├─► 重排         EmbeddingReranker（bi-encoder 余弦相似度）
   │
   ├─► 上下文拼装   context.py（带引用编号）
   │
   └─► 生成         llama.cpp（gguf instruct 模型）/ OpenAI 兼容端点
                     └─► 答案 + 引用列表（thinking 过程单独返回）
```

---

## Web 界面

```bat
runtime\python3.12\python.exe run.py serve
```

- Web 界面：<http://127.0.0.1:8000/ui>
- API 文档（Swagger）：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>

前端是 `web/index.html` + `web/index.css`，原生 HTML/JS，零依赖，不需要 npm 构建。

左侧栏「知识库」按类型分组展示：Markdown / PDF / 图片 / 文本，并标注是否已索引。

### 设置面板

左下角「设置」按钮打开模态框：

| 分类 | 内容 |
| --- | --- |
| 通用 | 语言、外观、字号 |
| 模型 | 当前生效模型与切换、云端 API 配置 |
| 检索 | TopK、BM25、Rerank、包含图片、相关性下限 |
| 对话 | 默认档位、追问改写、流式输出 |
| 用量 | token 累计统计与重置 |
| 关于 | 版本、索引 chunk 数、当前模型、项目路径 |

设置存在服务端 `data/ui_settings.json`，改动即时生效并 `PATCH /api/settings` 持久化。

主题支持深色 / 浅色 / 跟随系统。语言支持中英文切换，用 `data-i18n` 属性 + 字典实现。

后端代码改动后需要重启服务。Qdrant 本地模式对 `data/qdrant` 加文件锁，同一时刻只能有一个进程访问。服务运行时不要再在另一个终端跑 `run.py index`。

---

## HTTP API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/health` | 健康检查，含 `llm_available` / `indexed_chunks` / `indexing` |
| `GET` | `/api/config` | 当前配置 |
| `GET` | `/api/documents` | 知识库清单，按类型分组，并标注是否已索引 |
| `GET` | `/api/documents/{path}` | 单文档信息 |
| `POST` | `/api/chunks/preview` | 切块预览 |
| `GET` | `/api/chunks/stats` | 全库切块统计 |
| `POST` | `/api/search` | 混合检索，`include_images` 控制是否含图片 |
| `GET` | `/api/images/{path}` | 知识库图片，`?w=` 等比缩放作缩略图 |
| `POST` | `/api/ask` | 检索 + 生成问答，`mode` 可选 `fast` / `precise` |
| `POST` | `/api/ask/stream` | SSE 流式问答 |
| `POST` | `/api/chat` | 多轮对话 |
| `POST` | `/api/chat/stream` | 多轮对话 SSE 流式 |
| `GET` | `/api/conversations` | 会话列表 |
| `POST` | `/api/conversations` | 新建会话 |
| `GET` | `/api/conversations/{id}` | 会话详情 |
| `DELETE` | `/api/conversations/{id}` | 删除会话 |
| `GET` | `/api/llm/status` | 生成模型状态 |
| `GET` | `/api/llm/models` | 可选本地模型清单 |
| `POST` | `/api/llm/select` | 切换本地模型 |
| `GET` | `/api/llm/providers` | 本地离线 / 云端 API 状态 |
| `POST` | `/api/llm/provider` | 切换使用方式 |
| `GET` | `/api/llm/cloud` | 云端配置，只返回掩码 Key |
| `POST` | `/api/llm/cloud` | 保存云端配置 |
| `POST` | `/api/llm/cloud/test` | 测试云端端点连通性 |
| `POST` | `/api/llm/cloud/clear` | 删除云端配置与 API Key |
| `GET` | `/api/settings` | WebUI 设置 |
| `PATCH` | `/api/settings` | 更新设置 |
| `POST` | `/api/settings/reset` | 恢复默认设置 |
| `GET` | `/api/usage` | 累计 token 用量 |
| `POST` | `/api/usage/reset` | 清零累计用量 |
| `GET` | `/api/web/config` | 联网搜索配置 |
| `PATCH` | `/api/web/config` | 更新联网配置 |
| `POST` | `/api/web/config/clear` | 清空联网配置 |
| `POST` | `/api/web/test` | 联网连通性测试 |
| `POST` | `/api/web/search` | 只走联网搜索 |
| `GET` | `/api/index/status` | 索引状态 |
| `POST` | `/api/index` | 触发建索引，已有任务在跑时返回 409 |
| `GET` | `/ui` | Web 界面 |

### SSE 事件类型（`/api/ask/stream`）

| 事件 | 含义 |
| --- | --- |
| `status` | 阶段提示 |
| `citations` | 命中的参考资料列表 |
| `reasoning` | thinking 模型的思考过程增量 |
| `token` | 回答正文增量 |
| `done` | 结束，含耗时、模型名 |
| `error` | 出错 |

---

## 环境变量

以下为主要环境变量，均有默认值。更细粒度配置见 `src/config.py`。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `RAG_EMBEDDING_MODEL` | `qwen3` | embedding 模型：`qwen3` \| `wemm` |
| `RAG_VISION_ENABLED` | `true` | 是否启用视觉模型 |
| `RAG_VISION_MODEL` / `RAG_VISION_MMPROJ` | 自动配对 | 显式指定视觉主模型与投影器 |
| `RAG_VISION_PORT` | `8083` | 视觉模型端口 |
| `RAG_VISION_PROMPT` | 内置 | 生成图片描述用的提示词 |
| `RAG_VISION_MAX_TOKENS` | `512` | 单张图片描述最大长度 |
| `RAG_VISION_BM25` | `true` | 图片描述是否并入 BM25 |
| `RAG_LLM_LOAD_MMPROJ` | `true` | 对话服务是否加载配对的视觉投影器 |
| `RAG_MIN_RELEVANCE` | `0.45` | 相关性下限，0 表示关闭 |
| `RAG_ROUTER_ENABLED` | `false` | 是否启用旧的先判断再检索路由 |
| `RAG_WEB_HOST` | `127.0.0.1` | Web 服务监听地址 |
| `RAG_WEB_PORT` | `8000` | Web 服务端口 |
| `RAG_LLM_ENABLED` | `true` | 是否启用生成式问答 |
| `RAG_LLM_PROVIDER` | `llama_cpp` | `llama_cpp` \| `openai` |
| `RAG_LLM_MODEL` | 空 | 显式指定 gguf 模型路径 |
| `RAG_LLM_MODEL_DIRS` | `models\LLM` | 自动发现的搜索目录，`;` 分隔 |
| `RAG_LLM_PREFERRED` | 见 `src/config.py` | 按关键字优先匹配的模型名，`,` 分隔 |
| `RAG_LLM_BASE_URL` | 空 | OpenAI 兼容端点地址 |
| `RAG_LLM_API_KEY` | 空 | 端点密钥 |
| `RAG_LLM_NAME` | 空 | 请求时上报的模型名 |
| `RAG_LLM_PORT` | `8082` | llama-server 端口 |
| `RAG_LLM_CTX` | `8192` | 上下文长度 |
| `RAG_LLM_GPU_LAYERS` | `-1` | 卸载到 GPU 的层数，`-1` 表示全部 |
| `RAG_LLM_THREADS` | CPU 核数 / 2 | 线程数 |
| `RAG_LLM_MAX_TOKENS` | `1024` | 单次生成最大 token 数 |
| `RAG_LLM_TEMPERATURE` | `0.2` | 采样温度 |
| `RAG_LLM_REASONING` | `auto` | 服务端级思考：`on` \| `off` \| `auto` |
| `RAG_LLM_MODE` | `precise` | 默认问答档位：`fast` \| `precise` |
| `RAG_LLM_EXCLUDE` | 见 `src/config.py` | 排除的模型，逗号分隔子串 |
| `RAG_LLM_VRAM_GB` | `8.0` | 显存预算，用于挑选模型 |
| `RAG_LLM_VRAM_RESERVE_GB` | `3.0` | 预留给 embedding 模型的显存 |
| `RAG_LLM_TIMEOUT` | `300.0` | 请求超时，秒 |

代码中还支持：`RAG_LLM_BATCH`、`RAG_LLM_TOP_P`、`RAG_LLM_REPEAT_PENALTY` 等。

### 端口分配

| 服务 | 端口 |
| --- | --- |
| Embedding（Qwen3） | `8080` |
| WeMM Embedding | `8081` |
| 生成式 LLM | `8082` |
| Web 服务 | `8000` |

端口由 `llama-server` 子进程管理模块拉起与回收，正常退出时会统一关闭。

---

## 目录结构

```
RAG/
├── run.py
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── run_webui.bat
├── run_index.bat
├── run_ask.bat
├── run_check.bat
├── tests/
│   ├── gguf_builder.py
│   ├── test_bm25.py
│   ├── test_catalog.py
│   ├── test_chunker.py
│   ├── test_cloud.py
│   ├── test_config.py
│   ├── test_context.py
│   ├── test_conversation.py
│   ├── test_gguf.py
│   ├── test_ids.py
│   ├── test_modes.py
│   ├── test_rerank.py
│   ├── test_router.py
│   ├── test_search_fusion.py
│   ├── test_settings_store.py
│   ├── test_usage.py
│   ├── test_vector_db.py
│   ├── test_vision.py
│   ├── test_web.py
│   └── __init__.py
├── File/
│   ├── Markdown/            # 27 份 .md 知识库文档
│   ├── image/               # 示例图片
│   ├── PDF/                 # 当前为空
│   └── text/                # 当前为空
├── models/
│   ├── LLM/
│   │   ├── gemma-4-E2B-it-UD-Q4_K_XL.gguf
│   │   └── mmproj-gemma-4-E2B-it-BF16.gguf
│   ├── qwen3/
│   │   └── Qwen3-Embedding-4B-Q4_K_M.gguf
│   └── WeMM/
│       ├── WeMM-Embedding-2B-Q4_K_M.gguf
│       └── mmproj-WeMM-Embedding-2B-BF16.gguf
├── runtime/
│   ├── python3.12/
│   └── llama.cpp/
├── data/
│   ├── qdrant/
│   ├── index/
│   ├── logs/
│   ├── conversations/
│   ├── captions_cache.json
│   ├── llm_selection.json
│   ├── models_cache.json
│   ├── ui_settings.json
│   ├── usage_stats.json
│   └── web_search.json
├── src/
│   ├── config.py
│   ├── ids.py
│   ├── llama_server.py
│   ├── cli.py
│   ├── server.py
│   ├── settings_store.py
│   ├── usage.py
│   ├── database/
│   │   └── vector_db.py
│   ├── embedding/
│   │   ├── base.py
│   │   ├── qwen.py
│   │   ├── wemm.py
│   │   └── __init__.py
│   ├── ingest/
│   │   ├── chunker.py
│   │   ├── image.py
│   │   ├── markdown.py
│   │   ├── pdf.py
│   │   ├── pipeline.py
│   │   └── __init__.py
│   ├── retrieval/
│   │   ├── bm25.py
│   │   ├── rerank.py
│   │   ├── vector.py
│   │   └── __init__.py
│   ├── vision/
│   │   ├── captioner.py
│   │   └── __init__.py
│   ├── llm/
│   │   ├── base.py
│   │   ├── catalog.py
│   │   ├── cloud.py
│   │   ├── gguf.py
│   │   ├── llama_cpp.py
│   │   ├── openai_compat.py
│   │   ├── state.py
│   │   └── __init__.py
│   ├── rag/
│   │   ├── answer.py
│   │   ├── chat.py
│   │   ├── context.py
│   │   ├── conversation.py
│   │   ├── modes.py
│   │   ├── prompt.py
│   │   ├── router.py
│   │   ├── search.py
│   │   └── __init__.py
│   └── web/
│       ├── config.py
│       ├── fetch.py
│       ├── providers.py
│       ├── search.py
│       └── __init__.py
└── web/
    ├── index.html
    ├── index.css
    └── backups/
```

`data/`、`models/`、`runtime/` 已在 `.gitignore` 中忽略。`File/Markdown/` 是知识库本体，应纳入版本库。

---

## 常见问题 / 排错

### 1. `ModuleNotFoundError: No module named 'src'`

原因：使用了 `-m`，或试图通过 `PYTHONPATH` 解决。embedded Python 下这两种方式无效。

解决：改用 `run.py`，并确保当前目录是项目根目录。

```bat
cd C:\Users\mfxq2\Desktop\RAG
runtime\python3.12\python.exe run.py serve
```

### 2. 模型找不到或问答降级为纯检索

现象：`run.py check` 中「生成式 LLM 模型」为 `FAIL`，或 `ask` 报生成式问答不可用。

解决：用 `RAG_LLM_MODEL` 显式指定路径：

```bat
set RAG_LLM_MODEL=D:\GGUF_models\gemma-4-E4B-it-UD-Q4_K_XL.gguf
runtime\python3.12\python.exe run.py check
```

也可以把 gguf 放到 `models\LLM\`，或把所在目录加进 `RAG_LLM_MODEL_DIRS`。

### 3. 显存不足

可尝试：

- 不要同时常驻多个大模型
- 减小 `RAG_LLM_GPU_LAYERS`，例如 `set RAG_LLM_GPU_LAYERS=20`，或设 `0` 纯 CPU
- 降低 `RAG_LLM_CTX`，如 `4096`
- 换更小的模型

显存不足时，`LlamaCppChat` 会自动以 `-ngl 0` 回退 CPU 推理，模型名后会出现 `(CPU)` 标记。

### 4. llama-server 端口被占用

默认端口：embedding `8080`、WeMM `8081`、LLM `8082`。

```bat
netstat -ano | findstr :8082
taskkill /PID <PID> /F

:: 或换端口
set RAG_LLM_PORT=8092
runtime\python3.12\python.exe run.py serve
```

### 5. Qdrant 目录被占用

Qdrant 本地 embedded 模式同一时刻只允许一个进程打开。关闭所有正在使用 `data/qdrant` 的进程，确认没有残留的 `python.exe` / `llama-server.exe`，必要时删除 `.lock` 文件后重新建索引。

不要同时开多个 `run.py serve`，也不要在服务运行时另开终端跑 `run.py index`。API 层的 `/api/index` 已做并发保护，重复触发返回 409。

### 6. 控制台中文乱码

`run.py` 已将标准流切到 UTF-8，`.bat` 会先执行 `chcp 65001`。若仍有乱码，请确认在 `cmd.exe` 中运行。

### 7. 检索没有结果

先确认索引存在：`run.py check` 查看「已索引 chunk」是否大于 0。若为 0，执行：

```bat
runtime\python3.12\python.exe run.py index --rebuild
```

### 8. 索引里的旧文档还在

文档删除或改名后，其 chunk 默认会在下次 `index` 时被清理。若使用过 `--no-prune`，再跑一次不带该参数的 `index`。

---

## 开发

### 依赖

运行期依赖见 `requirements.txt`：fastapi、uvicorn、pydantic、httpx、qdrant-client、numpy、rank-bm25、jieba、PyMuPDF、Pillow。

开发依赖见 `requirements-dev.txt`：

```bat
runtime\python3.12\python.exe -m pip install -r requirements-dev.txt
```

正式运行本项目只需要 `requirements.txt`。

### 代码约定

- 源码保持与 `run.py` 入口兼容，不要在文档中引导使用 `python -m src.xxx`
- 新增 embedding 模型时，需要同步注册到 `src/config.py` 的 `EMBEDDING_MODELS`，并确保 collection 名遵循 `rag_knowledge_<model>` 格式
- 前端为原生 HTML/JS/CSS，修改后无需构建，但后端代码改动后需要重启服务
