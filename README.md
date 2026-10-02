# Local Chinese RAG Knowledge Base Q&A System

A locally run, offline-capable Chinese RAG (Retrieval-Augmented Generation) knowledge base Q&A system. The knowledge base is located in `File/`, currently containing 27 Chinese technical cheat sheets under `File/Markdown/`, and sample images under `File/image/`.

Chunking, embedding, vector retrieval, sparse retrieval, fusion, reranking, generation, and other stages are all executed locally and do not depend on cloud APIs.
Of course, you can add files to the File folder. For example, put images in File/image, and so on.

# This project was created using DeepSeek. Thanks to DeepSeek.
---

## Model Download

Before running the project, please download the required model files and place them in the corresponding directories:

| Model | File Name | Target Directory | Download Link |
| --- | --- | --- | --- |
| WeMM Embedding | `WeMM-Embedding-2B-Q4_K_M.gguf` | `models/WeMM/` | [Download](https://huggingface.co/DreamBlooms/WeMM-Embedding-2B-GGUF/resolve/main/WeMM-Embedding-2B-Q4_K_M.gguf?download=true) |
| WeMM mmproj | `mmproj-WeMM-Embedding-2B-BF16.gguf` | `models/WeMM/` | [Download](https://huggingface.co/DreamBlooms/WeMM-Embedding-2B-GGUF/resolve/main/mmproj-WeMM-Embedding-2B-BF16.gguf?download=true) |
| Qwen3 Embedding | `Qwen3-Embedding-4B-Q4_K_M.gguf` | `models/qwen3/` | [Download](https://huggingface.co/Qwen/Qwen3-Embedding-4B-GGUF/resolve/main/Qwen3-Embedding-4B-Q4_K_M.gguf?download=true) |
| Gemma Chat | `gemma-4-E2B-it-UD-Q4_K_XL.gguf` | `models/LLM/` | [Download](https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/gemma-4-E2B-it-UD-Q4_K_XL.gguf?download=true) and mmproj(https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF/resolve/main/mmproj-BF16.gguf?download=true) |

> **Note:** The `models/` directory is ignored by `.gitignore`. You only need to download the models you actually plan to use.
## Feature Overview

| Stage | Implementation |
| --- | --- |
| Embedding | `Qwen3-Embedding-4B-Q4_K_M.gguf`, 2560 dimensions, provided via `llama-server.exe --embedding` as an OpenAI-compatible `/v1/embeddings` |
| Fallback Embedding | `WeMM-Embedding-2B`, 2048 dimensions, can be used for multimodal-related experiments |
| Vector store | Qdrant local embedded mode, data directory `data/qdrant`; different embedding models use different collections, such as `rag_knowledge_qwen3`, `rag_knowledge_wemm` |
| Sparse retrieval | jieba tokenization + rank_bm25, index persisted to `data/index/bm25_<model>.pkl` |
| Fusion | RRF (Reciprocal Rank Fusion, k=60) |
| Reranking | bi-encoder cosine similarity reranking |
| Generation | Local llama.cpp + gguf instruct model, or any OpenAI-compatible endpoint |
| Web | FastAPI + native HTML/JS frontend, no npm build required |

Other capabilities:

- Generative Q&A: retrieval, context assembly, answers with citation numbers
- SSE streaming output: status, citations, thinking process, tokens returned chunk by chunk
- thinking model support: thinking process separated from main text
- Citation list: `[1] [2]` in answers correspond to specific files and sections
- Indexing concurrency protection: only one indexing task is allowed at a time
- Stale document cleanup: residual chunks from deleted or renamed documents are cleaned during indexing
- Multi-turn conversation: session persistence, history injection, follow-up rewriting
- Web search: web results can be appended after local results
- Cloud API: switch between local llama.cpp or OpenAI-compatible cloud endpoints
- Settings and usage: server-side persistent settings, cumulative token usage

---

## How to Run (embedded Python)

The project comes with embedded Python located at `runtime/python3.12`. The embedded distribution's `python312._pth` fixes `sys.path`, so the following methods do not work:

```bat
:: Does not work
runtime\python3.12\python.exe -m src.cli serve

:: Does not work, PYTHONPATH is ignored by ._pth
set PYTHONPATH=C:\Users\mfxq2\Desktop\RAG
runtime\python3.12\python.exe -m src.cli serve
```

The correct way is to run through `run.py` in the project root:

```bat
runtime\python3.12\python.exe run.py <subcommand>
```

`run.py` is located in the project root. When run as a script, it adds the project root to `sys.path` and switches standard output to UTF-8, avoiding garbled Chinese text in the Windows console.

---

## Quick Start

The following commands are all executed from the project root.

### 1. Environment self-check

```bat
cd C:\Users\mfxq2\Desktop\RAG
runtime\python3.12\python.exe run.py check
```

Check items include: Python runtime, `llama-server.exe`, embedding model files, number of Markdown documents, Qdrant collection, number of indexed chunks, BM25 index, and available generative LLM models.

### 2. Build index

```bat
runtime\python3.12\python.exe run.py index --rebuild
```

Indexing writes to Qdrant and generates the BM25 index file.

### 3. Ask

```bat
:: Pure retrieval, does not call the generation model
runtime\python3.12\python.exe run.py search "nmap -sS 是什么"

:: Retrieval + generative Q&A
runtime\python3.12\python.exe run.py ask "nmap -sS 是什么"
```

### 4. Web UI

```bat
runtime\python3.12\python.exe run.py serve
```

Open <http://127.0.0.1:8000/ui>.

---

## Command-Line Usage

The unified entry point is `run.py`.

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

### Subcommand Description

| Subcommand | Purpose | Common parameters |
| --- | --- | --- |
| `check` | Environment self-check | — |
| `config` | Print current effective configuration and validate | `--skip-validate` |
| `index` | Build / rebuild index | `--rebuild`, `--no-prune`, `--model`, `--pdf`, `--pdf-images`, `--images` |
| `stats` | Full-database chunk statistics | `--json` |
| `search` | Pure retrieval | `--top-k`, `--no-bm25`, `--no-rerank`, `--model`, `--context`, `--json`, `--web` |
| `ask` | Retrieval + generative Q&A | `--top-k`, `--model`, `--provider`, `--llm`, `--mode fast\|precise`, `--fast`, `--precise`, `--no-stream`, `--show-thinking`, `--json`, `--web` |
| `models` | Model list / details / switch | `--use`, `--clear`, `--detail`, `--all`, `--json` |
| `llm` | View generation model status or test-run prompt | `--provider`, `--prompt` |
| `serve` | Start FastAPI Web service | — |
| `chat` | Terminal interactive multi-turn chat | `--top-k`, `--llm`, `--provider`, `--mode`, `--show-thinking`, `--no-images`, `--web` |
| `cloud` | Configure / test / switch cloud LLM | `--base-url`, `--model`, `--api-key`, `--test`, `--use`, `--clear` |
| `test` | Run unit tests | `--pattern`, `-v` |

When the generation model is unavailable, `ask` prints `[error]` and exits with code `2`, while also suggesting that you can use `run.py search` instead.

---

## Q&A Modes: Fast / Precise

`ask`, `/api/ask`, `/api/ask/stream`, and the Web UI all support mode switching.

| Mode | Thinking process | `max_tokens` | `temperature` |
| --- | --- | --- | --- |
| `fast` | Off | 512 | 0.1 |
| `precise` | On | 1024 | 0.2 |

The default mode is determined by `RAG_LLM_MODE`, defaulting to `precise`.

Mode control is implemented through a request-level parameter:

```json
{"chat_template_kwargs": {"enable_thinking": false}}
```

`fast` disables the thinking process, `precise` enables it. `reasoning_budget` is not used to control the thinking process in the current implementation.

---

## Model Management

Put gguf files into `models/LLM/` and they will be automatically discovered. You can also specify other search directories via `RAG_LLM_MODEL_DIRS`.

Currently `models/LLM/` contains:

| File | Purpose |
| --- | --- |
| `gemma-4-E2B-it-UD-Q4_K_XL.gguf` | Chat model, can also read images with a vision projector |
| `mmproj-gemma-4-E2B-it-BF16.gguf` | Vision projector |

### Model Type Identification

`run.py models` reads GGUF header metadata and distinguishes:

| Type | Basis | Can do Q&A |
| --- | --- | --- |
| `chat` Chat | Main model with `tokenizer.chat_template` | Yes |
| `translation` Translation | `general.tags` contains `translation` | Yes, but not set as default |
| `embedding` Vector | Architecture belongs to bert/bge/gte, etc. | No |
| `vision` Projector | Filename `mmproj-`/`mtp-`, or architecture is `clip` | No |
| `base` Base | No chat template | No |

Multimodal chat models are still classified as `chat`; pure projectors are classified as `vision`.

### VRAM Estimation and Selection Order

```
Weight size + KV cache + reserve (default 3GB, for resident embedding model) ≤ VRAM budget
```

KV cache estimation:

```
2 × number of layers × KV heads × dimension per head × context length × 2 bytes
```

Selection order:

1. Project bundled directory first
2. Chat-capable
3. Fits in VRAM
4. Preferred keywords
5. Size

Models that do not fit are marked; they can still be selected manually, but will automatically fall back to CPU inference.

### Switching Models

```bat
runtime\python3.12\python.exe run.py models --use Qwen3.8-4B
```

You can also switch in the dropdown box in the top bar of the Web UI. When switching:

1. Stop the current llama-server and free VRAM
2. Write `data/llm_selection.json`
3. The new model is lazily loaded on the next question

Only one chat model is resident at a time.

### Excluding Models

Models matched by `RAG_LLM_EXCLUDE` will not appear in the list and cannot be selected by name, index, or interface.

### Model Search Directories

By default, only `models/LLM` is scanned. To temporarily include external models, explicitly override:

```bat
set RAG_LLM_MODEL_DIRS=models\LLM;D:\other\models
```

---

## Multimodal Retrieval (Images)

### Current Model Configuration

`models/LLM/` contains one chat model and one vision projector:

| File | Purpose |
| --- | --- |
| `gemma-4-E2B-it-UD-Q4_K_XL.gguf` | Chat + image reading |
| `mmproj-gemma-4-E2B-it-BF16.gguf` | Vision projector |

The chat service automatically attaches the paired mmproj. The same llama-server can both chat and read images; the visual captioner reuses that service when needed.

### Asking Directly About Images

Because the chat service has mmproj, you can ask about images directly:

```bat
runtime\python3.12\python.exe run.py chat
你> /image 7869275C8C80EC713F001C54309B788D.jpg
已附加图片：7869275C8C80EC713F001C54309B788D.jpg
你> 这张图里有什么？用一句话说明
```

The HTTP API also supports this: the `image` field of `POST /api/chat` can pass a path relative to `File/image` or a `data:` URL.

When an image is attached, a separate prompt is used and the pure RAG template is not reused.

### Image Vectorization Scheme

llama.cpp's `/v1/embeddings` does not support image input. Therefore the following scheme is used:

```
Image → Vision model generates text description
      → Text embedding
      → Write to the same vector store as text
```

Image captions are cached by "path + size + mtime" in `data/captions_cache.json`; repeated indexing will not recompute them.

### Usage

```bat
:: Indexing processes images under File/image by default
runtime\python3.12\python.exe run.py index --rebuild

:: Skip images
runtime\python3.12\python.exe run.py index --rebuild --no-images
```

`include_images` in retrieval / Q&A requests controls whether images are included in results.

### Switching to WeMM for Vectorization

```bat
set RAG_EMBEDDING_MODEL=wemm
runtime\python3.12\python.exe run.py index --rebuild
```

WeMM is 2048-dimensional, while Qwen3 is 2560-dimensional, so they are written to different collections.

---

## Two Usage Methods: Local Offline / Cloud API

Generative Q&A supports two methods, switchable in the CLI or Web UI.

### 1. Local Offline

llama.cpp runs gguf locally, fully offline.

### 2. Cloud API

Supports any OpenAI-compatible endpoint, such as OpenAI, DeepSeek, Moonshot, Tongyi Qianwen, Zhipu GLM, local Ollama / LM Studio / vLLM, etc.

```bat
:: Configure; leaving api_key empty means keep the existing Key unchanged
runtime\python3.12\python.exe run.py cloud ^
    --base-url https://api.deepseek.com/v1 ^
    --model deepseek-chat ^
    --api-key sk-xxxxxxxx

runtime\python3.12\python.exe run.py cloud --test
runtime\python3.12\python.exe run.py cloud --use openai
runtime\python3.12\python.exe run.py cloud --use llama_cpp
runtime\python3.12\python.exe run.py cloud --clear
```

Common endpoints:

| Service | Base URL |
| --- | --- |
| OpenAI | `https://api.openai.com/v1` |
| DeepSeek | `https://api.deepseek.com/v1` |
| Moonshot | `https://api.moonshot.cn/v1` |
| Tongyi Qianwen | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| Zhipu GLM | `https://open.bigmodel.cn/api/paas/v4` |
| Local Ollama | `http://127.0.0.1:11434/v1` |

### API Key Conventions

- The Key is stored in `data/llm_cloud.json`; `data/` is ignored by `.gitignore`
- External interfaces only return a masked value, not plaintext
- The Key is not printed in logs
- Switching to cloud is rejected when configuration is incomplete, returning 400

---

## Web Search

The local knowledge base only covers documents under `File/`. After enabling web search, search results are appended after local results and enter Context together. Citations with `url` and `source_type=web` are rendered as clickable external links in the frontend.

### Backend Selection

Bing is used by default.

| Backend | Requires key | Description |
| --- | --- | --- |
| `bing` | No | Default backend, key-free, stable structure |
| `baidu` | No | Key-free, returns redirect links |
| `duckduckgo` | No | May fail certificate validation in some proxy environments |
| `searxng` | No | Instance address must be filled in |
| `tavily` / `serper` / `brave` | Yes | API-based, requires Key |

### Usage

```bat
:: Command line
runtime\python3.12\python.exe run.py search "问题" --web
runtime\python3.12\python.exe run.py ask "问题" --web --web-limit 5
runtime\python3.12\python.exe run.py chat --web

:: Or use WebUI bottom-left "Settings" → "Web Search"
```

HTTP interfaces add `use_web` / `web_limit` / `web_fetch_pages` to the body of `/api/search`, `/api/ask`, and `/api/chat`.

### Fetching Body Text and Summaries

When `fetch_pages` is enabled, the main text of the first N web pages is fetched in parallel, default 3. A single page body is truncated to `max_page_chars`, default 3000.

### Implementation Notes

- Proxies must be passed explicitly, to avoid httpx failing to parse IPv6 bracket entries in `NO_PROXY` when reading environment variables.
- HTML body extraction does not depend on lxml / bs4; it uses standard-library-level regex processing, prioritizes extracting `<article>` / `<main>` / common body containers, and then removes the leading navigation menu.
- Before fetching, the target address is validated, rejecting non-http(s) and intranet addresses.

---

## Settings and Usage Statistics

### Settings Persistence

WebUI settings are stored server-side in `data/ui_settings.json`, not in localStorage. There are three groups of settings:

| Group | Contents |
| --- | --- |
| `general` | `language`(zh/en), `theme`(dark/light/system), `font_size` |
| `retrieval` | `top_k`, `use_bm25`, `use_reranker`, `include_images`, `min_relevance` |
| `chat` | `mode`(fast/precise), `condense`, `stream` |

Writes use deep merge + whitelist validation: submit only the fields to change, unknown groups / fields are ignored, enum values only accept fixed values, and numeric values are clamped to legal ranges.

### Token Usage Statistics

The `usage` of each call is accumulated over time and persisted to `data/usage_stats.json`, viewable by model, by purpose (`chat` / `ask` / `condense`), and by day.

Usage for streaming responses must be explicitly requested:

```json
{"stream": true, "stream_options": {"include_usage": true}}
```

The server appends a final chunk with empty `choices` and only `usage`.

---

## Multi-Turn Conversation

Single-turn Q&A forgets after each question. The conversation feature solves two things:

1. Remember context: history messages are passed to the generation model together
2. Make follow-ups retrievable: before each turn, use the LLM to rewrite the follow-up into an independent retrievable question

Vector retrieval and BM25 only look at the literal content of the query. Follow-ups like "What about the second point?", "Explain in more detail", or "What permissions does it need?" do not themselves contain retrievable semantics, and direct retrieval would recall irrelevant content. Therefore, before each turn, condense is performed first, and then the rewritten query is used for retrieval.

If rewriting fails, output is empty, output is too long, or output is the same as the original, it falls back to the original question without interrupting the conversation. Turning off `condense` can save this call.

### Usage

```bat
:: Terminal interactive chat
runtime\python3.12\python.exe run.py chat

:: In-session commands
/new         Start a new session
/history     View questions in this session
/citations   Show citations from the last answer
/mode fast   Switch mode
/quit        Exit
```

The Web UI has an independent "Chat" tab, supporting session list, switching, deletion, and streaming output.

Sessions are persisted in `data/conversations/<id>.json`, and can continue after restarting the service. Session IDs come from the URL and use strict whitelist validation.

---

## Relevance Threshold and Retrieval Strategy

The current strategy is: any input is always retrieved once, then filtered by relevance threshold after reranking.

```
Any input
   ↓
Always retrieve once
   ↓
Filter by relevance threshold 0.45 after reranking
   ├─ Has results → use RAG, annotate citations
   └─ No results → answer naturally as an ordinary question
```

The default relevance threshold is controlled by `RAG_MIN_RELEVANCE`, default `0.45`. Set to `0` to disable filtering.

The old "first decide whether to retrieve" router can be enabled via `RAG_ROUTER_ENABLED=1`; it is disabled by default.

---

## Retrieval and Generation Flow

```
User question
   │
   ├─► Dense retrieval   Qwen3-Embedding-4B (2560d) ──► Qdrant query_points
   │
   ├─► Sparse retrieval  jieba tokenization ──► rank_bm25 (data/index/bm25_<model>.pkl)
   │
   ├─► Fusion            RRF (k=60)
   │
   ├─► Reranking         EmbeddingReranker (bi-encoder cosine similarity)
   │
   ├─► Context assembly  context.py (with citation numbers)
   │
   └─► Generation        llama.cpp (gguf instruct model) / OpenAI-compatible endpoint
                         └─► Answer + citation list (thinking process returned separately)
```

---

## Web UI

```bat
runtime\python3.12\python.exe run.py serve
```

- Web UI: <http://127.0.0.1:8000/ui>
- API docs (Swagger): <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

The frontend is `web/index.html` + `web/index.css`, native HTML/JS, zero dependencies, no npm build required.

The left sidebar "Knowledge Base" displays by type groups: Markdown / PDF / Image / Text, and marks whether each has been indexed.

### Settings Panel

The "Settings" button in the bottom-left opens a modal:

| Category | Contents |
| --- | --- |
| General | Language, appearance, font size |
| Model | Current effective model and switching, cloud API configuration |
| Retrieval | TopK, BM25, Rerank, include images, relevance threshold |
| Chat | Default mode, follow-up rewriting, streaming output |
| Usage | Cumulative token statistics and reset |
| About | Version, number of indexed chunks, current model, project path |

Settings are stored server-side in `data/ui_settings.json`; changes take effect immediately and are persisted via `PATCH /api/settings`.

Themes support dark / light / follow system. Languages support Chinese-English switching, implemented with `data-i18n` attributes + dictionaries.

After backend code changes, the service must be restarted. Qdrant local mode locks `data/qdrant` with a file lock, so only one process can access it at a time. Do not run `run.py index` in another terminal while the service is running.

---

## HTTP API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Health check, includes `llm_available` / `indexed_chunks` / `indexing` |
| `GET` | `/api/config` | Current configuration |
| `GET` | `/api/documents` | Knowledge base list, grouped by type, with indexed status |
| `GET` | `/api/documents/{path}` | Single document information |
| `POST` | `/api/chunks/preview` | Chunk preview |
| `GET` | `/api/chunks/stats` | Full-database chunk statistics |
| `POST` | `/api/search` | Hybrid retrieval, `include_images` controls whether images are included |
| `GET` | `/api/images/{path}` | Knowledge base images, `?w=` scales proportionally as thumbnail |
| `POST` | `/api/ask` | Retrieval + generative Q&A, `mode` can be `fast` / `precise` |
| `POST` | `/api/ask/stream` | SSE streaming Q&A |
| `POST` | `/api/chat` | Multi-turn chat |
| `POST` | `/api/chat/stream` | Multi-turn chat SSE streaming |
| `GET` | `/api/conversations` | Session list |
| `POST` | `/api/conversations` | Create session |
| `GET` | `/api/conversations/{id}` | Session details |
| `DELETE` | `/api/conversations/{id}` | Delete session |
| `GET` | `/api/llm/status` | Generation model status |
| `GET` | `/api/llm/models` | Selectable local model list |
| `POST` | `/api/llm/select` | Switch local model |
| `GET` | `/api/llm/providers` | Local offline / cloud API status |
| `POST` | `/api/llm/provider` | Switch usage method |
| `GET` | `/api/llm/cloud` | Cloud configuration, only returns masked Key |
| `POST` | `/api/llm/cloud` | Save cloud configuration |
| `POST` | `/api/llm/cloud/test` | Test cloud endpoint connectivity |
| `POST` | `/api/llm/cloud/clear` | Delete cloud configuration and API Key |
| `GET` | `/api/settings` | WebUI settings |
| `PATCH` | `/api/settings` | Update settings |
| `POST` | `/api/settings/reset` | Restore default settings |
| `GET` | `/api/usage` | Cumulative token usage |
| `POST` | `/api/usage/reset` | Reset cumulative usage |
| `GET` | `/api/web/config` | Web search configuration |
| `PATCH` | `/api/web/config` | Update web configuration |
| `POST` | `/api/web/config/clear` | Clear web configuration |
| `POST` | `/api/web/test` | Web connectivity test |
| `POST` | `/api/web/search` | Web search only |
| `GET` | `/api/index/status` | Index status |
| `POST` | `/api/index` | Trigger indexing; returns 409 if a task is already running |
| `GET` | `/ui` | Web UI |

### SSE Event Types (`/api/ask/stream`)

| Event | Meaning |
| --- | --- |
| `status` | Stage hint |
| `citations` | List of matched reference materials |
| `reasoning` | Thinking process increment of thinking model |
| `token` | Answer body increment |
| `done` | End, includes elapsed time and model name |
| `error` | Error |

---

## Environment Variables

The following are the main environment variables, all with default values. See `src/config.py` for finer-grained configuration.

| Variable | Default | Description |
| --- | --- | --- |
| `RAG_EMBEDDING_MODEL` | `qwen3` | embedding model: `qwen3` \| `wemm` |
| `RAG_VISION_ENABLED` | `true` | Whether to enable vision model |
| `RAG_VISION_MODEL` / `RAG_VISION_MMPROJ` | Auto-paired | Explicitly specify vision main model and projector |
| `RAG_VISION_PORT` | `8083` | Vision model port |
| `RAG_VISION_PROMPT` | Built-in | Prompt used to generate image descriptions |
| `RAG_VISION_MAX_TOKENS` | `512` | Maximum length of a single image description |
| `RAG_VISION_BM25` | `true` | Whether image descriptions are included in BM25 |
| `RAG_LLM_LOAD_MMPROJ` | `true` | Whether chat service loads paired vision projector |
| `RAG_MIN_RELEVANCE` | `0.45` | Relevance threshold, 0 means disabled |
| `RAG_ROUTER_ENABLED` | `false` | Whether to enable old decide-then-retrieve router |
| `RAG_WEB_HOST` | `127.0.0.1` | Web service listen address |
| `RAG_WEB_PORT` | `8000` | Web service port |
| `RAG_LLM_ENABLED` | `true` | Whether to enable generative Q&A |
| `RAG_LLM_PROVIDER` | `llama_cpp` | `llama_cpp` \| `openai` |
| `RAG_LLM_MODEL` | empty | Explicitly specify gguf model path |
| `RAG_LLM_MODEL_DIRS` | `models\LLM` | Auto-discovery search directories, separated by `;` |
| `RAG_LLM_PREFERRED` | see `src/config.py` | Preferred keyword-matched model names, separated by `,` |
| `RAG_LLM_BASE_URL` | empty | OpenAI-compatible endpoint address |
| `RAG_LLM_API_KEY` | empty | Endpoint key |
| `RAG_LLM_NAME` | empty | Model name reported in requests |
| `RAG_LLM_PORT` | `8082` | llama-server port |
| `RAG_LLM_CTX` | `8192` | Context length |
| `RAG_LLM_GPU_LAYERS` | `-1` | Number of layers offloaded to GPU, `-1` means all |
| `RAG_LLM_THREADS` | CPU cores / 2 | Number of threads |
| `RAG_LLM_MAX_TOKENS` | `1024` | Maximum tokens per generation |
| `RAG_LLM_TEMPERATURE` | `0.2` | Sampling temperature |
| `RAG_LLM_REASONING` | `auto` | Server-level thinking: `on` \| `off` \| `auto` |
| `RAG_LLM_MODE` | `precise` | Default Q&A mode: `fast` \| `precise` |
| `RAG_LLM_EXCLUDE` | see `src/config.py` | Excluded models, comma-separated substrings |
| `RAG_LLM_VRAM_GB` | `8.0` | VRAM budget, used for model selection |
| `RAG_LLM_VRAM_RESERVE_GB` | `3.0` | VRAM reserved for embedding model |
| `RAG_LLM_TIMEOUT` | `300.0` | Request timeout, seconds |

The code also supports: `RAG_LLM_BATCH`, `RAG_LLM_TOP_P`, `RAG_LLM_REPEAT_PENALTY`, etc.

### Port Allocation

| Service | Port |
| --- | --- |
| Embedding (Qwen3) | `8080` |
| WeMM Embedding | `8081` |
| Generative LLM | `8082` |
| Web service | `8000` |

Ports are started and reclaimed by the `llama-server` subprocess management module, and are all shut down on normal exit.

---

## Directory Structure

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
│   ├── Markdown/            # 27 .md knowledge base documents
│   ├── image/               # Sample images
│   ├── PDF/                 # Currently empty
│   └── text/                # Currently empty
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

`data/`, `models/`, and `runtime/` are ignored in `.gitignore`. `File/Markdown/` is the knowledge base itself and should be included in version control.

---

## FAQ / Troubleshooting

### 1. `ModuleNotFoundError: No module named 'src'`

Cause: `-m` was used, or an attempt was made to solve it via `PYTHONPATH`. Under embedded Python, both methods are ineffective.

Solution: Use `run.py` instead, and make sure the current directory is the project root.

```bat
cd C:\Users\mfxq2\Desktop\RAG
runtime\python3.12\python.exe run.py serve
```

### 2. Model Not Found or Q&A Degrades to Pure Retrieval

Symptom: In `run.py check`, "Generative LLM model" is `FAIL`, or `ask` reports that generative Q&A is unavailable.

Solution: Explicitly specify the path with `RAG_LLM_MODEL`:

```bat
set RAG_LLM_MODEL=D:\GGUF_models\gemma-4-E4B-it-UD-Q4_K_XL.gguf
runtime\python3.12\python.exe run.py check
```

You can also put the gguf into `models\LLM\`, or add its directory to `RAG_LLM_MODEL_DIRS`.

### 3. Insufficient VRAM

Try:

- Do not keep multiple large models resident at the same time
- Reduce `RAG_LLM_GPU_LAYERS`, e.g. `set RAG_LLM_GPU_LAYERS=20`, or set `0` for pure CPU
- Lower `RAG_LLM_CTX`, e.g. `4096`
- Switch to a smaller model

When VRAM is insufficient, `LlamaCppChat` automatically falls back to CPU inference with `-ngl 0`, and `(CPU)` is appended to the model name.

### 4. llama-server Port Occupied

Default ports: embedding `8080`, WeMM `8081`, LLM `8082`.

```bat
netstat -ano | findstr :8082
taskkill /PID <PID> /F

:: Or change the port
set RAG_LLM_PORT=8092
runtime\python3.12\python.exe run.py serve
```

### 5. Qdrant Directory Occupied

Qdrant local embedded mode only allows one process to open it at a time. Close all processes using `data/qdrant`, confirm there are no residual `python.exe` / `llama-server.exe`, and if necessary delete the `.lock` file and rebuild the index.

Do not open multiple `run.py serve` at the same time, and do not run `run.py index` in another terminal while the service is running. The API layer `/api/index` already has concurrency protection; repeated triggers return 409.

### 6. Garbled Chinese in Console

`run.py` has switched standard streams to UTF-8, and `.bat` first executes `chcp 65001`. If there is still garbled text, confirm that you are running in `cmd.exe`.

### 7. Retrieval Returns No Results

First confirm the index exists: `run.py check` to see whether "Indexed chunks" is greater than 0. If it is 0, run:

```bat
runtime\python3.12\python.exe run.py index --rebuild
```

### 8. Old Documents Still in the Index

After a document is deleted or renamed, its chunks are cleaned by default on the next `index`. If `--no-prune` was used, run `index` again without that parameter.

---

## Development

### Dependencies

Runtime dependencies are in `requirements.txt`: fastapi, uvicorn, pydantic, httpx, qdrant-client, numpy, rank-bm25, jieba, PyMuPDF, Pillow.

Development dependencies are in `requirements-dev.txt`:

```bat
runtime\python3.12\python.exe -m pip install -r requirements-dev.txt
```

To run this project formally, only `requirements.txt` is needed.

### Code Conventions

- Source code remains compatible with the `run.py` entry point; do not guide users in documentation to use `python -m src.xxx`
- When adding a new embedding model, register it synchronously in `EMBEDDING_MODELS` in `src/config.py`, and ensure the collection name follows the `rag_knowledge_<model>` format
- The frontend is native HTML/JS/CSS; no build is needed after modification, but the service must be restarted after backend code changes