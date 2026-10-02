# llama.cpp 操作手册速查卡（完整版）

## 目录
- [一、安装与基础命令](#一安装与基础命令)
- [二、模型管理](#二模型管理)
- [三、命令行对话 (CLI)](#三命令行对话-cli)
- [四、HTTP API 服务器 (Serve)](#四http-api-服务器-serve)
- [五、性能优化参数](#五性能优化参数)
- [六、常用模型推荐](#六常用模型推荐)
- [七、实用组合拳](#七实用组合拳)
- [八、速查小抄](#八速查小抄)

---

## 一、安装与基础命令

### 1. Windows 安装（WinGet）
```powershell
# 安装 Vulkan 版本（兼容所有显卡）
winget install llama.cpp

# 安装 CUDA 版本（NVIDIA 显卡专用，性能更好）
winget install --id ggml.llamacpp --exact

# 卸载
winget uninstall llama.cpp
```

### 2. 基础命令
```bash
llama version                      # 查看版本
llama help                         # 查看所有命令
llama help all                     # 查看所有命令（包括隐藏的）
llama <command> --help             # 查看具体命令的帮助
```

### 3. 可用命令列表
```bash
serve            # HTTP API 服务器
cli              # 命令行交互/单次推理
download         # 从 Hugging Face 下载模型
version          # 显示版本
licenses         # 显示第三方许可证
help             # 显示帮助
```

---

## 二、模型管理

### 1. 下载模型
```bash
# 从 Hugging Face 下载
llama download <模型ID> --include "量化版本" --dir ./models

# 示例：下载 Qwen3.5-9B Q4_K_M
llama download microsoft/Phi-3.5-mini-instruct-gguf --include "Q4_K_M" --dir ./models

# 只下载配置文件（不下载模型权重）
llama download <模型ID> --config-only

# 使用 Hugging Face Token（下载私有模型）
llama download <模型ID> --token hf_xxxxxx
```

### 2. 常用量化版本说明
| 量化版本 | 说明 | 文件大小 |
|---------|------|---------|
| `Q4_K_M` | **推荐**，质量和体积均衡 | 约4-5GB (9B模型) |
| `Q5_K_M` | 质量更高，体积稍大 | 约5-6GB (9B模型) |
| `Q3_K_M` | 体积更小，质量下降 | 约3-4GB (9B模型) |
| `Q8_0` | 高质量，体积大 | 约8-9GB (9B模型) |
| `F16` | 全精度，体积最大 | 约16-18GB (9B模型) |

### 3. GGUF 模型文件格式
```bash
# GGUF 是 llama.cpp 专用的量化模型格式
# 文件命名规则：模型名-量化版本.gguf
# 示例：Qwen3.5-9B-Q4_K_M.gguf
```

---

## 三、命令行对话 (CLI)

### 1. 基础对话
```bash
# 单次推理（问一个问题就退出）
llama cli -m <模型路径> -p "你的问题"

# 交互式对话（连续对话）
llama cli -m <模型路径>

# 交互式对话 + 系统提示词
llama cli -m <模型路径> --system-prompt "你是一个有帮助的助手"

# 从文件读取提示词
llama cli -m <模型路径> -f prompt.txt
```

### 2. 交互模式快捷键
| 快捷键 | 功能 |
|--------|------|
| `/exit` | 退出对话 |
| `/clear` | 清空对话历史 |
| `/save` | 保存当前会话 |
| `/load` | 加载保存的会话 |
| `Ctrl+C` | 强制退出 |

### 3. 参数详解
```bash
llama cli -m <模型路径> \
    -p "你好" \                    # 提示词
    -n 256 \                       # 生成最大 token 数
    -t 8 \                         # CPU 线程数
    -ngl 999 \                     # GPU 层数（999=全部）
    -c 4096 \                      # 上下文长度
    --temp 0.7 \                   # 温度（0-2，越高越随机）
    --top-k 40 \                   # Top-K 采样
    --top-p 0.9 \                  # Top-P 采样（核采样）
    --repeat-penalty 1.1 \         # 重复惩罚
    --seed 42 \                    # 随机种子（固定可复现）
    -b 512 \                       # 批处理大小
    --color \                      # 彩色输出
    --interactive \                # 交互模式
    --system-prompt "..." \        # 系统提示词
    -f prompt.txt \                # 从文件读取提示词
    --log-disable                  # 禁用日志
```

### 4. 温度参数速查
| 温度值 | 效果 |
|--------|------|
| `0.0` | 确定性输出（每次都一样） |
| `0.1-0.3` | 非常保守，适合代码生成 |
| `0.5-0.7` | **推荐**，平衡创造力和准确性 |
| `0.8-1.0` | 更有创造性 |
| `1.2+` | 非常随机，可能跑题 |

---

## 四、HTTP API 服务器 (Serve)

### 1. 基础启动
```bash
# 最基本启动
llama serve -m <模型路径>

# 启用 GPU 加速（全部层加载到显存）
llama serve -m <模型路径> -ngl 999

# 指定端口
llama serve -m <模型路径> --port 8080

# 绑定到所有网络接口（允许外部访问）
llama serve -m <模型路径> --host 0.0.0.0 --port 8080
```

### 2. 常用参数
```bash
llama serve -m <模型路径> \
    -ngl 999 \                    # GPU 层数
    -c 4096 \                     # 上下文长度
    --port 8080 \                 # 监听端口
    --host 127.0.0.1 \            # 监听地址
    --threads 8 \                 # CPU 线程数
    --threads-batch 4 \           # 批处理线程数
    --mlock \                     # 锁定内存（防止交换）
    --no-mmap \                   # 禁用内存映射
    --log-format json \           # JSON 格式日志
    --verbose \                   # 详细日志
    --api-key your-key-here       # 设置 API 密钥
```

### 3. API 端点
```bash
# 服务启动后，这些端点可用：

# 健康检查
GET  http://127.0.0.1:8080/health

# 模型信息
GET  http://127.0.0.1:8080/models

# 聊天补全（OpenAI 兼容）
POST http://127.0.0.1:8080/v1/chat/completions
POST http://127.0.0.1:8080/completion

# 嵌入
POST http://127.0.0.1:8080/v1/embeddings

# Token 计数
POST http://127.0.0.1:8080/tokenize
```

### 4. API 调用示例
```bash
# 使用 curl 调用
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen",
    "messages": [
      {"role": "system", "content": "你是一个有帮助的助手"},
      {"role": "user", "content": "你好，介绍一下你自己"}
    ],
    "temperature": 0.7,
    "max_tokens": 256
  }'

# 流式输出
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen",
    "messages": [{"role": "user", "content": "讲个笑话"}],
    "stream": true
  }'
```

### 5. 与第三方工具集成
```bash
# Chatbox（桌面端）
# 设置 API 地址：http://127.0.0.1:8080
# 选择 OpenAI API 兼容模式

# NextChat（Web 端）
# 设置接口地址：http://127.0.0.1:8080

# 任何支持 OpenAI API 的工具都可以连接
```

### 6. 后台运行（Windows）
```powershell
# 方法1：使用 Start-Process
Start-Process -WindowStyle Hidden llama serve -m "模型路径" -ngl 999

# 方法2：使用任务计划程序
# 创建启动时自动运行的任务

# 方法3：使用 PM2（需安装 Node.js）
pm2 start llama -- serve -m "模型路径" -ngl 999
pm2 save
pm2 startup
```

---

## 五、性能优化参数

### 1. GPU 加速参数
```bash
# NVIDIA GPU（CUDA 版本）
-ngl 999              # 全部层加载到 GPU
-ngl 20               # 只加载 20 层到 GPU

# AMD/Intel GPU（Vulkan 版本）
-ngl 999              # 同样使用 -ngl 参数

# 查看 GPU 使用情况
nvidia-smi            # NVIDIA
vulkaninfo            # Vulkan
```

### 2. CPU 优化参数
```bash
-t 8                  # 使用 8 个 CPU 线程
-tb 4                 # 批处理线程数
--mlock               # 锁定内存（防止交换）
--no-mmap             # 禁用内存映射（提高某些系统的稳定性）
```

### 3. 内存优化参数
```bash
-c 4096               # 上下文大小（越大越消耗内存）
--memory-f32          # 使用 float32（更精确但更慢）
--memory-f16          # 使用 float16（更快但稍差）
--rope-scaling <type> # RoPE 缩放（扩展上下文）
```

### 4. 参数推荐配置

| 硬件配置 | 推荐参数 |
|---------|---------|
| **RTX 3070 (8GB)** | `-ngl 999 -c 4096 -t 4` |
| **RTX 4090 (24GB)** | `-ngl 999 -c 8192 -t 8` |
| **无独显 (CPU only)** | `-t 8 -c 2048`（不加 -ngl） |
| **显存不足 4GB** | `-ngl 10 -c 2048` |

---

## 六、常用模型推荐

### 1. 中文模型
| 模型 | 参数 | 量化 | 大小 | 特点 |
|------|------|------|------|------|
| **Qwen3.5-9B** | 9B | Q4_K_M | 5.6GB | 阿里通义，中文能力最强 |
| **DeepSeek-R1** | 8B | Q4_K_M | 5.0GB | 推理能力强，逻辑严谨 |
| **GLM-4-9B** | 9B | Q4_K_M | 5.4GB | 智谱 AI，1M 超长上下文 |
| **Qwopus-9B-Coder** | 9B | Q4_K_M | 5.6GB | 代码生成专用 |

### 2. 英文/多语言模型
| 模型 | 参数 | 量化 | 大小 | 特点 |
|------|------|------|------|------|
| **Llama 3.1-8B** | 8B | Q4_K_M | 4.7GB | Meta，综合能力强 |
| **Mistral-7B** | 7B | Q4_K_M | 4.1GB | 高效，速度快 |
| **Phi-3.5-mini** | 3.8B | Q4_K_M | 2.3GB | 轻量，适合低配置 |
| **Granite-3.1-8B** | 8B | Q4_K_M | 4.4GB | IBM，企业级 |

### 3. 代码模型
| 模型 | 参数 | 量化 | 大小 | 特点 |
|------|------|------|------|------|
| **DeepSeek-Coder** | 6.7B | Q4_K_M | 3.9GB | 代码能力强 |
| **Qwen-Coder-9B** | 9B | Q4_K_M | 5.6GB | 通义代码版 |
| **CodeGeeX4-9B** | 9B | Q4_K_M | 5.5GB | 代码生成专用 |

### 4. 模型下载命令
```bash
# Qwen3.5-9B（推荐）
llama download lmstudio-community/Qwen3.5-9B-GGUF --include "Q4_K_M"

# DeepSeek-R1
llama download lmstudio-community/DeepSeek-R1-0528-Qwen3-8B-GGUF --include "Q4_K_M"

# Phi-3.5-mini（轻量级）
llama download microsoft/Phi-3.5-mini-instruct-gguf --include "Q4_K_M"

# GLM-4-9B（超长上下文）
llama download legraphista/glm-4-9b-chat-1m-GGUF --include "Q4_K"
```

---

## 七、实用组合拳

### 1. 启动 API 服务（后台运行）
```powershell
# Windows
Start-Process -WindowStyle Hidden llama serve -m "D:\model\Qwen3.5-9B-Q4_K_M.gguf" -ngl 999

# Linux (tmux)
tmux new -s llama
llama serve -m /path/to/model.gguf -ngl 999
# Ctrl+B d 脱离会话

# Linux (nohup)
nohup llama serve -m /path/to/model.gguf -ngl 999 > server.log 2>&1 &
```

### 2. 测试模型速度
```bash
# 测试纯 GPU 速度
llama cli -m <模型路径> -ngl 999 -p "写一篇关于AI的短文" -n 100

# 测试纯 CPU 速度
llama cli -m <模型路径> -p "写一篇关于AI的短文" -n 100 -t 8

# 查看详细性能统计（添加 -v 参数）
llama cli -m <模型路径> -ngl 999 -p "你好" -n 50 -v
```

### 3. 批量推理（处理多个问题）
```bash
# 使用命令行循环（Windows PowerShell）
$questions = @("问题1", "问题2", "问题3")
foreach ($q in $questions) {
    llama cli -m <模型路径> -p $q -n 100
}

# Linux bash
for q in "问题1" "问题2" "问题3"; do
    llama cli -m <模型路径> -p "$q" -n 100
done
```

### 4. 模型对比测试
```bash
# 测试多个模型对同一问题的回答
$models = @("model1.gguf", "model2.gguf", "model3.gguf")
foreach ($m in $models) {
    echo "=== 测试 $m ==="
    llama cli -m $m -p "你的测试问题" -n 100
}
```

### 5. 监控 API 服务
```bash
# 查看服务是否运行
curl http://127.0.0.1:8080/health

# 查看模型信息
curl http://127.0.0.1:8080/models

# 压力测试（使用 ab 工具）
ab -n 100 -c 10 -p post.json -T application/json http://127.0.0.1:8080/v1/chat/completions
```

### 6. 日志分析
```bash
# 查看服务器日志
tail -f server.log

# 统计请求数
grep "POST /v1/chat/completions" server.log | wc -l

# 查看平均响应时间
grep "time=" server.log | awk '{print $NF}' | awk -F= '{sum+=$2; count++} END {print sum/count "ms"}'
```

---

## 八、速查小抄

### 最常用命令
```bash
# 交互式对话
llama cli -m <模型> -ngl 999

# 启动 API 服务
llama serve -m <模型> -ngl 999 --port 8080

# 单次推理
llama cli -m <模型> -p "问题" -n 256
```

### 参数速查
```bash
-m <path>        # 模型路径（必填）
-ngl <num>       # GPU 层数（999=全部）
-p <prompt>      # 提示词
-n <num>         # 生成 token 数
-c <num>         # 上下文长度（默认 2048/4096）
-t <num>         # CPU 线程数
--temp <num>     # 温度（0-2）
--top-k <num>    # Top-K
--top-p <num>    # Top-P
--port <num>     # 服务器端口（默认 8080）
--host <ip>      # 服务器地址（默认 127.0.0.1）
```

### 常见问题排查
```bash
# 问题：CUDA 无法使用
# 检查 NVIDIA 驱动
nvidia-smi

# 检查 CUDA 版本
nvcc --version

# 问题：显存不足
# 减少 GPU 层数
-ngl 10

# 或减小上下文
-c 2048

# 问题：模型加载慢
# 使用内存映射（默认启用）
# 或增加 CPU 线程
-t 8

# 问题：生成质量差
# 调整温度
--temp 0.5

# 增加重复惩罚
--repeat-penalty 1.2
```

### 模型路径速写（Windows）
```powershell
# 你的模型都在 D:\model 下
$models = @{
    "qwen" = "D:\model\lmstudio-community\Qwen3.5-9B-GGUF\Qwen3.5-9B-Q4_K_M.gguf"
    "deepseek" = "D:\model\lmstudio-community\DeepSeek-R1-0528-Qwen3-8B-GGUF\DeepSeek-R1-0528-Qwen3-8B-Q4_K_M.gguf"
    "coder" = "D:\model\Jackrong\Qwopus3.5-9B-Coder-GGUF\Qwopus3.5-9B-coder-Exp-Q4_K_M.gguf"
}

# 快速使用（PowerShell 函数）
function qwen { llama cli -m $models['qwen'] -ngl 999 $args }
function ds { llama cli -m $models['deepseek'] -ngl 999 $args }
```

---

## 九、性能基准参考

### RTX 3070 (8GB) 实测速度
| 模型 | 量化 | 速度 (tokens/秒) | 显存占用 |
|------|------|-----------------|---------|
| Qwen3.5-9B | Q4_K_M | 25-30 | ~5GB |
| DeepSeek-R1-8B | Q4_K_M | 27-32 | ~4.5GB |
| Phi-3.5-mini | Q4_K_M | 45-50 | ~2.5GB |
| GLM-4-9B | Q4_K_M | 22-27 | ~5GB |

