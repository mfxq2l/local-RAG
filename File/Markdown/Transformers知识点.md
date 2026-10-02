# Hugging Face Transformers 完整使用指南



## 1. 概述与安装

Hugging Face Transformers 是目前最流行的开源 NLP/多模态模型库，提供了数千个预训练模型，覆盖文本分类、生成、翻译、问答、图像识别、语音识别等任务。它的核心设计理念是让开发者通过统一 API 轻松加载、微调和部署各类 Transformer 模型。

### 1.1 核心依赖安装

```bash
pip install transformers datasets evaluate accelerate
```

根据使用的深度学习框架选择安装 PyTorch 或 TensorFlow：

```bash
# PyTorch（推荐）
pip install torch

# TensorFlow
pip install tensorflow
```

`datasets` 用于加载和预处理数据集，`evaluate` 用于加载评估指标，`accelerate` 用于多设备推理和训练加速。

### 1.2 可选依赖

```bash
# ONNX 导出
pip install transformers[onnx]

# 量化支持
pip install bitsandbytes

# 训练加速
pip install deepspeed

# PEFT 微调
pip install peft trl

# 注意力优化
pip install flash-attn

# TensorRT / OpenVINO 导出
pip install optimum[exporters]
```

### 1.3 2026 年推荐技术栈

当前开源微调的事实标准组合为：

```bash
pip install "transformers>=4.44" "peft>=0.12" "trl>=0.9" \
  "bitsandbytes>=0.43" "datasets" "accelerate" "flash-attn"
```

- **transformers** — 模型与分词器
- **peft** — LoRA/QLoRA 实现
- **trl** — SFTTrainer、DPOTrainer、GRPOTrainer
- **bitsandbytes** — 4-bit/8-bit 量化
- **accelerate** — 多 GPU/分布式启动
- **flash-attn** — 内存高效注意力

### 1.4 登录 Hugging Face Hub

```bash
huggingface-cli login
# 或使用环境变量
export HF_TOKEN="hf_..."
```

如需使用镜像加速：

```bash
export HF_ENDPOINT="https://hf-mirror.com"
```


## 2. Pipeline：快速上手推理

`pipeline()` 是 Transformers 中最简单、最快速的推理接口，只需一行代码即可完成从模型加载到推理的全过程。

### 2.1 基本用法

```python
from transformers import pipeline

# 文本分类
classifier = pipeline("text-classification")
result = classifier("I love this movie!")
print(result)

# 文本生成
generator = pipeline("text-generation", model="gpt2")
result = generator("The secret to baking a good cake is", max_length=50)
print(result)

# 情感分析（指定模型）
pipe = pipeline("text-classification", model="LiliLe/my_awesome_model")
result = pipe("This is great!")

# 对话式生成（使用 messages 格式）
messages = [{"role": "user", "content": "Explain quantum mechanics clearly."}]
pipe = pipeline("text-generation", model="openai/gpt-oss-120b",
                torch_dtype="auto", device_map="auto")
outputs = pipe(messages, max_new_tokens=256)
print(outputs[0]["generated_text"][-1])
```

### 2.2 支持的常见任务

| 任务 | Pipeline ID | 模态 |
|------|------------|------|
| 文本分类 | `pipeline("text-classification")` | NLP |
| 文本生成 | `pipeline("text-generation")` | NLP |
| 命名实体识别 | `pipeline("ner")` | NLP |
| 问答 | `pipeline("question-answering")` | NLP |
| 摘要 | `pipeline("summarization")` | NLP |
| 翻译 | `pipeline("translation")` | NLP |
| 填充掩码 | `pipeline("fill-mask")` | NLP |
| 零样本分类 | `pipeline("zero-shot-classification")` | NLP |
| 图像分类 | `pipeline("image-classification")` | CV |
| 目标检测 | `pipeline("object-detection")` | CV |
| 图像分割 | `pipeline("image-segmentation")` | CV |
| 语音识别 | `pipeline("automatic-speech-recognition")` | Audio |
| 音频分类 | `pipeline("audio-classification")` | Audio |
| 视觉问答 | `pipeline("vqa")` | 多模态 |
| 图像描述 | `pipeline("image-to-text")` | 多模态 |
| 文档问答 | `pipeline("document-question-answering")` | 多模态 |

### 2.3 Pipeline 的局限性

`pipeline()` 适合快速验证和简单推理。当需要精细控制生成参数、自定义预处理逻辑或做批量高效推理时，应直接使用 `AutoModel` 和 `AutoTokenizer`。


## 3. AutoClass：模型与分词器的加载

### 3.1 核心概念

Transformers 通过 **AutoClass** 机制自动识别并加载正确的模型架构和分词器，无需手动指定具体的模型类。

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("LiliLe/my_awesome_model")
model = AutoModelForSequenceClassification.from_pretrained(
    "LiliLe/my_awesome_model",
    device_map="auto"  # 自动分配设备
)
```

### 3.2 常用 AutoModel 类型

| AutoModel 类 | 适用任务 |
|-------------|---------|
| `AutoModel` | 通用基础模型（输出隐藏状态） |
| `AutoModelForSequenceClassification` | 序列分类 |
| `AutoModelForCausalLM` | 因果语言模型（自回归生成） |
| `AutoModelForSeq2SeqLM` | 序列到序列生成 |
| `AutoModelForQuestionAnswering` | 问答 |
| `AutoModelForTokenClassification` | 序列标注 |
| `AutoModelForMaskedLM` | 掩码语言模型 |
| `AutoModelForImageClassification` | 图像分类 |
| `AutoModelForObjectDetection` | 目标检测 |
| `AutoModelForSpeechSeq2Seq` | 语音序列到序列 |
| `AutoModelForMultimodalLM` | 多模态语言模型 |

### 3.3 Tokenizer 的使用

```python
text = "Hello, world!"
inputs = tokenizer(text, return_tensors="pt")
print(inputs)
# {'input_ids': tensor([[101, 7592, 1010, 2088, 999, 102]]),
#  'attention_mask': tensor([[1, 1, 1, 1, 1, 1]])}
```

**批量处理与填充：**

```python
texts = ["Hello", "How are you?", "This is a longer sentence"]
inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
```

**特殊 Token 管理：**

```python
# 查看特殊 token
print(tokenizer.bos_token)   # <s>
print(tokenizer.eos_token)   # </s>
print(tokenizer.pad_token)   # <pad>
print(tokenizer.unk_token)   # <unk>

# 添加自定义特殊 token
tokenizer.add_special_tokens({"additional_special_tokens": ["<|custom|>"]})
model.resize_token_embeddings(len(tokenizer))
```

特殊 token 是模型理解序列结构的关键标记，包括句首（bos）、句尾（eos）、填充（pad）、未知（unk）等。

### 3.4 Fast vs Slow Tokenizer

Transformers 提供两种分词器实现：

| 特性 | Fast Tokenizer | Slow Tokenizer |
|------|---------------|---------------|
| 实现语言 | Rust（`tokenizers` 库） | Python |
| 速度 | 快（并行处理） | 慢 |
| 偏移映射 | 支持 `offset_mapping` | 不支持 |
| 训练新词表 | 支持 `train_new_from_iterator` | 不支持 |
| 默认选择 | `AutoTokenizer` 默认返回 Fast | 需显式指定 `use_fast=False` |

```python
# 强制使用 slow tokenizer
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased", use_fast=False)

# Fast tokenizer 的偏移映射（用于问答等任务）
inputs = tokenizer("Hello world", return_offsets_mapping=True)
print(inputs["offset_mapping"])  # [(0, 5), (6, 11)]
```

### 3.5 训练自定义分词器

`train_new_from_iterator` 仅支持 Fast Tokenizer，使用生成器可避免将整个数据集加载到内存：

```python
from transformers import AutoTokenizer

old_tokenizer = AutoTokenizer.from_pretrained("gpt2")

def get_training_corpus():
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="train")
    for i in range(0, len(dataset), 1000):
        yield dataset[i : i + 1000]["text"]

new_tokenizer = old_tokenizer.train_new_from_iterator(
    get_training_corpus(), vocab_size=32000
)
new_tokenizer.save_pretrained("./my_tokenizer")
```

### 3.6 Padding Side 与生成任务

因果语言模型（GPT、LLaMA 等）生成时需要 **left padding**，否则 padding token 会干扰生成位置：

```python
tokenizer.padding_side = "left"  # 生成任务必须设为 left
tokenizer.pad_token = tokenizer.eos_token
```

分类和序列标注任务通常使用 **right padding**（默认）。

### 3.7 对话模板

对于指令微调模型，使用 `apply_chat_template` 自动插入正确的特殊 token：

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain PPO in one sentence."},
]
prompt = tokenizer.apply_chat_template(messages, tokenize=False)
# 输出包含 <|begin_of_text|> 等特殊 token 的完整 prompt

# 直接返回 token IDs
input_ids = tokenizer.apply_chat_template(
    messages, tokenize=True, return_tensors="pt",
    add_generation_prompt=True
)
```


## 4. DataCollator：数据整理与动态填充

DataCollator 是连接 Dataset 与模型输入的桥梁，核心能力是**按批动态填充**：将批内样本填充到该批最长序列的长度，而非统一填充到数据集全局最大长度，避免大量无意义的填充计算。

### 4.1 DataCollatorWithPadding

最常用的数据整理器，适用于分类、NER、问答等任务：

```python
from transformers import DataCollatorWithPadding

data_collator = DataCollatorWithPadding(
    tokenizer=tokenizer,
    padding=True,        # 动态填充到批内最长
    return_tensors="pt",
    max_length=None      # 不限制最大长度
)

# 使用方式：直接传给 Trainer 的 data_collator 参数
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    data_collator=data_collator,
)
```

### 4.2 DataCollatorForLanguageModeling

用于因果语言模型（CLM）和掩码语言模型（MLM）训练：

```python
from transformers import DataCollatorForLanguageModeling

# 因果语言模型（GPT 风格）：mlm=False
tokenizer.pad_token = tokenizer.eos_token
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  # 自动右移一位作为标签
)

# 掩码语言模型（BERT 风格）：mlm=True
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=True,
    mlm_probability=0.15,  # 15% 的 token 被掩码
)
```

### 4.3 DataCollatorForSeq2Seq

用于 T5、BART 等序列到序列模型：

```python
from transformers import DataCollatorForSeq2Seq

data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    padding=True,
    label_pad_token_id=-100,  # 标签中的 padding 忽略
)
```

### 4.4 DataCollatorForTokenClassification

用于 NER、词性标注等序列标注任务：

```python
from transformers import DataCollatorForTokenClassification

data_collator = DataCollatorForTokenClassification(
    tokenizer=tokenizer,
    padding=True,
    label_pad_token_id=-100,
)
```

### 4.5 自定义 DataCollator

继承 `DataCollatorWithPadding` 并添加额外字段：

```python
from dataclasses import dataclass
from transformers import DataCollatorWithPadding
import torch

@dataclass
class CustomDataCollator(DataCollatorWithPadding):
    def __call__(self, features):
        batch = super().__call__(features)
        # 添加自定义字段
        batch["custom_field"] = torch.tensor(
            [f["custom_field"] for f in features]
        )
        return batch
```


## 5. 模型保存与加载

### 5.1 保存模型和分词器

```python
model.save_pretrained("./my_model")
tokenizer.save_pretrained("./my_model")
```

默认使用 `safetensors` 格式保存。如需保存为 PyTorch bin 格式：

```python
model.save_pretrained("./my_model", safe_serialization=False)
```

### 5.2 重新加载

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained("./my_model")
tokenizer = AutoTokenizer.from_pretrained("./my_model")
```

### 5.3 保存生成配置

```python
# 保存模型时同时保存生成配置
model.generation_config.save_pretrained("./my_model")

# 加载时自动读取
model = AutoModelForCausalLM.from_pretrained("./my_model")
# model.generation_config 已包含自定义解码参数
```

### 5.4 指定版本和修订

```python
# 加载特定版本
model = AutoModel.from_pretrained(
    "bert-base-uncased",
    revision="refs/pr/1",       # 分支或 PR
    cache_dir="./cache",        # 自定义缓存目录
    force_download=False,       # 是否强制重新下载
)

# 离线模式
model = AutoModel.from_pretrained("./my_model", local_files_only=True)
```

`save_pretrained()` 和 `from_pretrained()` 是 Transformers 中模型持久化的标准方式，支持本地路径和 Hugging Face Hub 上的模型 ID。


## 6. 文本生成与推理

### 6.1 基本生成

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

inputs = tokenizer("The future of AI is", return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

### 6.2 GenerationConfig：生成配置

`GenerationConfig` 控制模型的解码策略，定义在 `src/transformers/generation/configuration_utils.py` 中。模型的解码策略定义在生成配置中，即使用户没有为模型保存自定义配置，默认配置也会生效。

```python
from transformers import GenerationConfig

# 查看当前生成配置
print(model.generation_config)
# GenerationConfig {
#   "bos_token_id": 50256,
#   "eos_token_id": 50256,
# }
# 只显示与默认值不同的字段

# 创建自定义生成配置
gen_config = GenerationConfig(
    max_new_tokens=200,
    do_sample=True,
    temperature=0.7,
    top_p=0.95,
    top_k=40,
    repetition_penalty=1.1,
    no_repeat_ngram_size=3,
    eos_token_id=model.config.eos_token_id,
)

# 方式一：传入 generate()
outputs = model.generate(**inputs, generation_config=gen_config)

# 方式二：设为模型默认配置
model.generation_config = gen_config
outputs = model.generate(**inputs)

# 保存生成配置
gen_config.save_pretrained("./my_model")
```

### 6.3 解码策略详解

| 策略 | 关键参数 | 特点 | 适用场景 |
|------|---------|------|---------|
| 贪心搜索 | 默认 | 每步选概率最高的 token | 确定性任务 |
| 束搜索 | `num_beams>1` | 保留多条候选路径 | 翻译、摘要 |
| 多项式采样 | `do_sample=True` | 按概率随机采样 | 创意写作 |
| Top-K 采样 | `top_k=K` | 仅从概率最高的 K 个中采样 | 平衡质量与多样性 |
| 核采样 | `top_p=P` | 从累积概率达 P 的最小集合中采样 | 通用生成 |
| 对比搜索 | `penalty_alpha>0` | 惩罚重复，保持连贯 | 长文本生成 |
| 辅助解码 | `assistant_model` | 小模型草稿+大模型验证 | 加速推理 |

### 6.4 LogitsProcessor：约束解码

通过 LogitsProcessor 在生成过程中动态修改 logits，实现约束解码：

```python
from transformers import LogitsProcessor, LogitsProcessorList
import torch

class ForbiddenTokensProcessor(LogitsProcessor):
    """禁止特定 token 被生成"""
    def __init__(self, forbidden_token_ids):
        self.forbidden_token_ids = forbidden_token_ids

    def __call__(self, input_ids, scores):
        for token_id in self.forbidden_token_ids:
            scores[:, token_id] = -float("inf")
        return scores

# 使用
processor = ForbiddenTokensProcessor([tokenizer.encode("bad")[0]])
outputs = model.generate(
    **inputs,
    logits_processor=LogitsProcessorList([processor]),
    max_new_tokens=50,
)
```

### 6.5 流式输出

**方式一：TextStreamer（终端流式打印）**

```python
from transformers import TextStreamer

streamer = TextStreamer(
    tokenizer,
    skip_prompt=True,            # 不打印输入 prompt
    skip_special_tokens=True     # 过滤特殊 token
)

model.generate(**inputs, streamer=streamer, max_new_tokens=100)
```

**方式二：TextIteratorStreamer（可编程迭代器）**

适合 Web 应用、FastAPI 接口等需要自定义处理逻辑的场景：

```python
from threading import Thread
from transformers import TextIteratorStreamer

streamer = TextIteratorStreamer(
    tokenizer, skip_prompt=True, skip_special_tokens=True
)

generate_kwargs = dict(
    **inputs, streamer=streamer, max_new_tokens=200,
    do_sample=True, temperature=0.7, top_p=0.95
)

thread = Thread(target=model.generate, kwargs=generate_kwargs)
thread.start()

for text_chunk in streamer:
    print(text_chunk, end="", flush=True)  # 每个 chunk 可立即转发给前端

thread.join()
```

### 6.6 只获取新生成的 Token

`generate()` 默认返回 `prompt + 新生成` 的完整序列。只取新生成部分：

```python
outputs = model.generate(**inputs, max_new_tokens=50)
new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
print(tokenizer.decode(new_tokens, skip_special_tokens=True))
```

### 6.7 KV Cache

KV Cache 缓存已计算的 Key/Value 状态，避免重复计算，显著加速自回归生成：

```python
# 默认启用（use_cache=True）
outputs = model.generate(**inputs, max_new_tokens=100, use_cache=True)

# 禁用（调试用，显存换速度）
outputs = model.generate(**inputs, max_new_tokens=100, use_cache=False)
```

### 6.8 投机解码（Speculative Decoding）

使用小型辅助模型快速生成草稿 token，再由大模型批量验证，加速推理：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

assistant_model = AutoModelForCausalLM.from_pretrained("gpt2")
main_model = AutoModelForCausalLM.from_pretrained("gpt2-large")

outputs = main_model.generate(
    **inputs,
    assistant_model=assistant_model,
    max_new_tokens=200,
    do_sample=True,
)
```


## 7. Trainer：模型微调

`Trainer` 是 Transformers 提供的高级训练 API，封装了训练循环、日志记录、检查点保存、评估、混合精度等功能，无需手写训练代码。

### 7.1 基本微调流程

```python
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)
from datasets import load_dataset
import numpy as np
import evaluate

# 1. 加载模型和分词器
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# 2. 加载和预处理数据集
dataset = load_dataset("imdb")

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True)

tokenized_datasets = dataset.map(tokenize_function, batched=True)

# 3. 加载评估指标
metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# 4. 配置训练参数
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",            # 注意：4.41+ 使用 eval_strategy
    save_strategy="epoch",
    logging_steps=100,
    load_best_model_at_end=True,
    fp16=True,
    report_to="tensorboard",
    gradient_accumulation_steps=2,    # 梯度累积
    max_grad_norm=1.0,                # 梯度裁剪
    warmup_ratio=0.1,                 # 预热比例
    lr_scheduler_type="cosine",       # 学习率调度
)

# 5. 创建 Trainer（使用 DataCollatorWithPadding 动态填充）
from transformers import DataCollatorWithPadding
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    compute_metrics=compute_metrics,
    data_collator=data_collator,
)

# 6. 开始训练
trainer.train()

# 7. 保存模型
trainer.save_model("./fine_tuned_model")
tokenizer.save_pretrained("./fine_tuned_model")
```

### 7.2 版本兼容性说明

`evaluation_strategy` 在 Transformers 4.41+ 中已被重命名为 `eval_strategy`。旧参数仍然可用但会触发弃用警告，并计划在 4.46 版本中移除。

```python
# 旧版（< 4.41）
training_args = TrainingArguments(evaluation_strategy="epoch")

# 新版（>= 4.41）
training_args = TrainingArguments(eval_strategy="epoch")
```

从 4.36.0 起，如果未指定 `eval_strategy`，默认值为 `"no"`，即不会自动运行评估。需要显式设置：

```python
training_args = TrainingArguments(
    eval_strategy="steps",       # 或 "epoch"
    eval_steps=100,              # eval_strategy="steps" 时生效
    load_best_model_at_end=True,
)
```

### 7.3 自定义 Trainer

当需要修改训练逻辑时，可以子类化 `Trainer` 并覆盖特定方法：

```python
import torch
from transformers import Trainer

class CustomTrainer(Trainer):
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        # 自定义损失计算，例如加入类别权重
        weight = self.class_weights.to(logits.device) if self.class_weights is not None else None
        loss_fct = torch.nn.CrossEntropyLoss(weight=weight)
        loss = loss_fct(
            logits.view(-1, self.model.config.num_labels),
            labels.view(-1),
        )
        return (loss, outputs) if return_outputs else loss
```

可覆盖的方法包括 `get_train_dataloader`、`get_eval_dataloader`、`create_optimizer_and_scheduler`、`training_step` 等。

### 7.4 自定义数据集

除 `datasets` 库外，也可以使用 PyTorch 的 `Dataset`：

```python
from torch.utils.data import Dataset

class MyDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.encodings = tokenizer(
            texts, truncation=True, padding=True, max_length=max_length
        )
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)
```

### 7.5 评估指标

使用 `evaluate` 库加载标准指标：

```python
import evaluate

# 分类任务
accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")

# 生成任务
rouge = evaluate.load("rouge")
bleu = evaluate.load("sacrebleu")  # 推荐 sacrebleu
meteor = evaluate.load("meteor")

# 序列标注
seqeval = evaluate.load("seqeval")
```

`evaluate` 库支持加载数十种标准评估指标，返回统一的 `compute()` 接口。

### 7.6 生成任务的 compute_metrics

生成任务需要设置 `predict_with_generate=True`，并解码预测结果后再计算指标：

```python
def compute_metrics(eval_pred, tokenizer):
    predictions, labels = eval_pred
    # 确保 predictions 在 vocab_size 范围内
    vocab_size = tokenizer.vocab_size
    pad_id = tokenizer.pad_token_id or 0
    predictions = np.where(predictions >= vocab_size, pad_id, predictions)

    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    # 将标签中的 -100 替换为 pad_token_id
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    # 计算 BLEU 和 ROUGE
    bleu_result = bleu.compute(predictions=decoded_preds, references=decoded_labels)
    rouge_result = rouge.compute(predictions=decoded_preds, references=decoded_labels)
    return {
        "bleu": bleu_result["score"],
        "rougeL": rouge_result["rougeL"],
    }

training_args = TrainingArguments(
    predict_with_generate=True,
    generation_max_length=128,
    eval_strategy="epoch",
)
```

### 7.7 Trainer 回调（Callback）

`TrainerCallback` 允许在训练过程中插入自定义逻辑：

```python
from transformers import TrainerCallback, TrainerControl, TrainerState
from transformers import TrainingArguments

class EarlyStoppingCallback(TrainerCallback):
    def __init__(self, patience=3):
        self.patience = patience
        self.best_metric = None
        self.counter = 0

    def on_evaluate(self, args, state, control, metrics=None, **kwargs):
        current = metrics.get("eval_loss", float("inf"))
        if self.best_metric is None or current < self.best_metric:
            self.best_metric = current
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                control.should_training_stop = True
        return control

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    callbacks=[EarlyStoppingCallback(patience=3)],
)
```

### 7.8 超参数搜索

`Trainer` 支持四种超参数搜索后端：optuna、sigopt、raytune 和 wandb：

```python
def model_init():
    return AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=2
    )

trainer = Trainer(
    model_init=model_init,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics,
)

best_run = trainer.hyperparameter_search(
    direction="maximize",
    backend="optuna",
    n_trials=20,
    hp_space=lambda _: {
        "learning_rate": trial.suggest_float("learning_rate", 1e-5, 5e-5, log=True),
        "per_device_train_batch_size": trial.suggest_categorical(
            "per_device_train_batch_size", [8, 16, 32]
        ),
        "num_train_epochs": trial.suggest_int("num_train_epochs", 2, 5),
    },
)
print(best_run.hyperparameters)
```


## 8. 自定义训练循环（原生 PyTorch）

当 `Trainer` 的封装无法满足需求时，需要手写训练循环。常见场景包括：多任务联合训练、复杂损失结构、动态调整训练策略等。

### 8.1 使用 Accelerate 简化分布式训练

```python
from accelerate import Accelerator
import torch
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_scheduler
from datasets import load_dataset

accelerator = Accelerator()

model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

dataset = load_dataset("imdb", split="train[:5000]")

def tokenize(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=256)

dataset = dataset.map(tokenize, batched=True)
dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)
lr_scheduler = get_scheduler(
    "cosine", optimizer=optimizer,
    num_warmup_steps=100, num_training_steps=1000,
)

model, optimizer, dataloader, lr_scheduler = accelerator.prepare(
    model, optimizer, dataloader, lr_scheduler
)

model.train()
for epoch in range(3):
    for step, batch in enumerate(dataloader):
        outputs = model(**batch)
        loss = outputs.loss
        accelerator.backward(loss)

        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()

        if step % 100 == 0:
            accelerator.print(f"Epoch {epoch}, Step {step}, Loss: {loss.item():.4f}")
```

### 8.2 手动混合精度与梯度累积

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()
accumulation_steps = 4

model.train()
for step, batch in enumerate(dataloader):
    with autocast(dtype=torch.bfloat16):
        outputs = model(**batch)
        loss = outputs.loss / accumulation_steps

    scaler.scale(loss).backward()

    if (step + 1) % accumulation_steps == 0:
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()
        lr_scheduler.step()
```


## 9. PEFT：参数高效微调

参数高效微调在保持基座模型权重冻结的前提下，仅训练少量适配器参数，大幅降低显存需求，使得在消费级 GPU 上微调大模型成为可能。

### 9.1 LoRA 微调

LoRA 通过训练低秩矩阵来适配模型，核心参数包括秩 `r`、缩放 `lora_alpha`、丢弃率 `lora_dropout` 和目标模块 `target_modules`：

```python
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig
from trl import SFTTrainer, SFTConfig

model_id = "meta-llama/Llama-3.1-8B"
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype="bfloat16",
    attn_implementation="flash_attention_2",
)

dataset = load_dataset("json", data_files="train.jsonl", split="train")

peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
)

sft_config = SFTConfig(
    output_dir="./llama3-sft",
    num_train_epochs=2,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
    max_seq_length=4096,
    packing=True,                # 拼接短序列提高吞吐
    assistant_only_loss=True,    # 仅对 assistant 回复计算损失
)

trainer = SFTTrainer(
    model=model,
    args=sft_config,
    train_dataset=dataset,
    peft_config=peft_config,
    processing_class=tokenizer,
)
trainer.train()
trainer.save_model("./llama3-sft/final")
```

### 9.2 QLoRA：4-bit 量化 + LoRA

QLoRA 将基座模型以 4-bit 量化加载，进一步降低显存需求，使得 7B 模型可在单张 16GB GPU 上训练：

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,   # 双重量化
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B",
    quantization_config=bnb_config,
    device_map="auto",
)

# 为 4-bit 模型准备训练
from peft import prepare_model_for_kbit_training
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# trainable params: 4,194,304 || all params: 8,034,242,560 || trainable%: 0.05
```

### 9.3 适配器保存、加载与合并

```python
# 保存适配器（仅保存 LoRA 权重，体积极小）
model.save_pretrained("./lora_adapter")

# 加载适配器
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B")
model = PeftModel.from_pretrained(base_model, "./lora_adapter")

# 合并适配器到基座模型（推理时使用，消除推理开销）
merged_model = model.merge_and_unload()
merged_model.save_pretrained("./merged_model")
```

### 9.4 PEFT 方法对比

| 方法 | 原理 | 参数量 | 显存节省 | 适用场景 |
|------|------|--------|---------|---------|
| LoRA | 低秩矩阵分解 | 0.01%-1% | ~60% | 通用微调 |
| QLoRA | LoRA + 4-bit 量化 | 0.01%-1% | ~75% | 单卡微调大模型 |
| P-Tuning | 可训练 prompt 前缀 | <0.1% | ~80% | 少样本场景 |
| Prefix Tuning | 每层添加前缀向量 | 0.1%-1% | ~70% | 生成任务 |
| IA3 | 缩放激活值 | <0.01% | ~85% | 极致参数效率 |


## 10. 量化：降低显存占用

量化通过将权重和激活值表示为更低精度的数据类型来减少内存和计算成本，使得在消费级硬件上运行大模型成为可能。

### 10.1 bitsandbytes 动态量化

最简便的量化方式，无需预量化检查点：

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# 4-bit NF4 量化
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config,
    device_map="auto",
)

# 8-bit 量化
bnb_config_8bit = BitsAndBytesConfig(load_in_8bit=True)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=bnb_config_8bit,
    device_map="auto",
)
```

### 10.2 GPTQ / AWQ 预量化模型加载

GPTQ 和 AWQ 是两种主流的离线量化方法，需要预量化检查点，加载时自动解析量化参数：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# 加载 GPTQ 量化模型
model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/Llama-2-7B-GPTQ",
    device_map="auto",
)

# 加载 AWQ 量化模型
model = AutoModelForCausalLM.from_pretrained(
    "TheBloke/una-cybertron-7B-v2-AWQ",
    low_cpu_mem_usage=True,
    device_map="cuda:0",
)
```

Transformers 通过 `HfQuantizer` 类支持量化技术的扩展。

### 10.3 量化方案对比

| 方法 | 精度 | 显存节省 | 是否需要校准 | 适用场景 |
|------|------|---------|------------|---------|
| bitsandbytes 8-bit | int8 | ~50% | 否 | 快速部署 |
| bitsandbytes 4-bit | NF4/FP4 | ~75% | 否 | 消费级 GPU |
| GPTQ | int4 | ~75% | 是（离线） | 生产推理 |
| AWQ | int4 | ~75% | 是（离线） | 生产推理 |


## 11. 性能优化

### 11.1 设备分配

```python
# 自动分配到可用设备（需要 accelerate）
model = AutoModelForCausalLM.from_pretrained(
    model_name, device_map="auto"
)

# 手动指定设备
model = AutoModelForCausalLM.from_pretrained(
    model_name, device_map={"": "cuda:0"}  # 全部放 GPU 0
)

# 控制显存使用
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    max_memory={0: "10GiB", 1: "10GiB", "cpu": "30GiB"},
)
```

`device_map="auto"` 需要安装 `accelerate` 库，否则会静默回退到 CPU。

### 11.2 混合精度

```python
# 推理时使用半精度
model = AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype=torch.float16, device_map="auto"
)

# 使用 bfloat16（A100+ 推荐）
model = AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype=torch.bfloat16, device_map="auto"
)
```

### 11.3 注意力实现优化

```python
# FlashAttention 2（需要 flash-attn 库，Ampere+ GPU）
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    attn_implementation="flash_attention_2",
    torch_dtype=torch.bfloat16,
)

# SDPA（PyTorch 2.0+ 内置，通用性最好）
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    attn_implementation="sdpa",
    torch_dtype=torch.bfloat16,
)

# 查看当前注意力实现
print(model.config._attn_implementation)
```

### 11.4 梯度检查点

以时间换空间，用重计算减少激活值内存：

```python
# 方式一：TrainingArguments
training_args = TrainingArguments(
    gradient_checkpointing=True,
    gradient_checkpointing_kwargs={"use_reentrant": False},
)

# 方式二：模型手动启用
model.gradient_checkpointing_enable()
```

### 11.5 批量推理

```python
from transformers import pipeline

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0,
    batch_size=8,
)

results = pipe(["prompt1", "prompt2", "prompt3"], max_new_tokens=50)
```

### 11.6 推理加速工具

**vLLM**：高吞吐量推理引擎，支持 PagedAttention 和连续批处理，提供 OpenAI 兼容 API：

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-hf \
    --port 8000
```

```python
# 客户端调用（OpenAI 兼容）
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
response = client.chat.completions.create(
    model="meta-llama/Llama-2-7b-hf",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

**Transformers Serve**：Transformers 内置的 OpenAI 兼容服务：

```bash
transformers serve
transformers chat localhost:8000 --model-name-or-path openai/gpt-oss-120b
```


## 12. 分布式训练

### 12.1 数据并行（DDP）

通过 `accelerate` 配置多 GPU 数据并行：

```bash
accelerate config  # 交互式配置
accelerate launch train.py  # 启动训练
```

`Trainer` 与 `accelerate` 无缝集成，自动处理数据并行、梯度同步和设备管理。

### 12.2 FSDP（完全分片数据并行）

FSDP 将参数、梯度和优化器状态切片到多张 GPU 上，每次计算前通过 all-gather 聚合完整参数，计算后释放。以更多通信为代价，换取“训练比单卡显存更大的模型”的能力。

**前置要求：** PyTorch >= 2.1.0，已安装 `accelerate`。

**配置方式一：accelerate config**

```bash
accelerate config
# 交互式选择 FSDP 相关选项
```

**配置方式二：JSON 配置文件**

创建 `fsdp_config.json`：

```json
{
    "fsdp_transformer_layer_cls_to_wrap": ["LlamaDecoderLayer"],
    "fsdp_auto_wrap_policy": "TRANSFORMER_BASED_WRAP",
    "fsdp_backward_prefetch": "backward_pre",
    "fsdp_sharding_strategy": "FULL_SHARD",
    "fsdp_state_dict_type": "SHARDED_STATE_DICT",
    "fsdp_cpu_ram_efficient_loading": true,
    "fsdp_offload_params": false
}
```

```python
training_args = TrainingArguments(
    output_dir="./results",
    fsdp="full_shard auto_wrap",
    fsdp_config="fsdp_config.json",
    per_device_train_batch_size=4,
    bf16=True,
)

trainer = Trainer(model=model, args=training_args, train_dataset=dataset)
trainer.train()
```

**FSDP vs DDP vs DeepSpeed 对比：**

| 策略 | 通信量 | 显存效率 | 适用场景 |
|------|--------|---------|---------|
| DDP | 低 | 每卡完整模型 | 模型可放入单卡 |
| FSDP | 高 | 参数/梯度/优化器分片 | 显存受限，单卡放不下 |
| ZeRO-2 | 中 | 优化器状态分片 | 显存受限，单卡放不下优化器状态 |
| ZeRO-3 | 高 | 参数+梯度+优化器分片 | 超大模型，单卡放不下参数 |

### 12.3 DeepSpeed 集成

DeepSpeed 通过 ZeRO 优化器实现显存高效的大规模训练：

```python
training_args = TrainingArguments(
    output_dir="./results",
    deepspeed="ds_config.json",
    per_device_train_batch_size=8,
    num_train_epochs=3,
)
```

`ds_config.json` 示例（ZeRO Stage 2）：

```json
{
    "zero_optimization": {
        "stage": 2,
        "offload_optimizer": {"device": "cpu"},
        "allgather_partitions": true,
        "overlap_comm": true
    },
    "bf16": {"enabled": true},
    "train_batch_size": 64,
    "gradient_accumulation_steps": 4
}
```

### 12.4 多节点训练

当单台机器 GPU 不足时，使用 Accelerate 配置多节点训练：

```yaml
# multi_node.yaml
compute_environment: LOCAL_MACHINE
distributed_type: FSDP
num_machines: 2
machine_rank: 0  # 0 为主节点，1 为第二节点
main_process_ip: 192.168.1.100
main_process_port: 29500
num_processes: 16
```

```bash
# 主节点
accelerate launch --config_file multi_node.yaml --machine_rank 0 train.py

# 第二节点
accelerate launch --config_file multi_node.yaml --machine_rank 1 train.py
```

### 12.5 并行策略选择

| 策略 | 通信量 | 适用场景 |
|------|--------|---------|
| DDP | 低 | 模型可放入单卡 |
| FSDP | 中高 | 显存受限，单卡放不下 |
| ZeRO-2 | 中 | 显存受限，单卡放不下优化器状态 |
| ZeRO-3 | 高 | 超大模型，单卡放不下参数 |
| 流水线并行 | 中 | 超深模型 |
| 张量并行 | 高 | 超宽模型 |


## 13. 多模态：AutoProcessor 与视觉-语言模型

### 13.1 AutoProcessor

`AutoProcessor` 是处理多模态输入的统一接口，封装了文本分词器和图像/音频特征提取器：

```python
from transformers import AutoProcessor, AutoModelForMultimodalLM

model_id = "Qwen/Qwen3-VL-2B-Instruct"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForMultimodalLM.from_pretrained(
    model_id, dtype="auto", device_map="auto"
)

# 处理图文输入
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "url": "https://example.com/image.jpg"},
            {"type": "text", "text": "Describe this image."},
        ],
    }
]

inputs = processor.apply_chat_template(
    messages, tokenize=True, return_tensors="pt",
    add_generation_prompt=True
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=256)
print(processor.decode(outputs[0], skip_special_tokens=True))
```

### 13.2 图像分类微调（ViT）

```python
from transformers import AutoModelForImageClassification, AutoImageProcessor
from torchvision.transforms import Compose, Resize, ToTensor, Normalize

model_id = "google/vit-base-patch16-224-in21k"
image_processor = AutoImageProcessor.from_pretrained(model_id)

# 准备标签映射
labels = dataset["train"].features["label"].names
id2label = {i: label for i, label in enumerate(labels)}
label2id = {label: i for i, label in enumerate(labels)}

model = AutoModelForImageClassification.from_pretrained(
    model_id,
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True,
)

def transform(example_batch):
    inputs = image_processor(
        [x.convert("RGB") for x in example_batch["image"]],
        return_tensors="pt",
    )
    inputs["labels"] = [label2id[l] for l in example_batch["label"]]
    return inputs

# 使用 Trainer 微调（与 NLP 流程一致）
```

### 13.3 语音识别微调（Whisper）

```python
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import torchaudio

processor = WhisperProcessor.from_pretrained("openai/whisper-small")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

# 加载音频（Whisper 要求 16kHz 采样率）
waveform, sample_rate = torchaudio.load("audio.wav")
if sample_rate != 16000:
    resampler = torchaudio.transforms.Resample(sample_rate, 16000)
    waveform = resampler(waveform)

# 处理
inputs = processor(
    waveform.squeeze().numpy(),
    sampling_rate=16000,
    return_tensors="pt",
)

# 推理
generated_ids = model.generate(inputs.input_features)
transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(transcription)
```


## 14. 模型导出与部署

### 14.1 导出为 ONNX

ONNX 是跨框架的模型交换格式，可在多种运行时中高效执行：

```bash
pip install optimum[exporters]

# 使用 optimum-cli 导出
optimum-cli export onnx --model ./my_model ./onnx_output/
```

```python
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

model = ORTModelForSequenceClassification.from_pretrained("./onnx_output")
tokenizer = AutoTokenizer.from_pretrained("./my_model")

inputs = tokenizer("Hello world", return_tensors="pt")
outputs = model(**inputs)
```

### 14.2 导出为 TensorRT

TensorRT 是 NVIDIA 的高性能推理优化器，适用于 GPU 部署：

```bash
# 通过 Optimum 导出并优化
optimum-cli export onnx --model ./my_model ./onnx_output/
trtexec --onnx=./onnx_output/model.onnx --saveEngine=model.engine --fp16
```

### 14.3 导出为 OpenVINO

适用于 Intel CPU/GPU/NPU 的推理优化：

```bash
optimum-cli export openvino --model ./my_model ./openvino_output/
```

```python
from optimum.intel import OVModelForSequenceClassification
model = OVModelForSequenceClassification.from_pretrained("./openvino_output")
```

### 14.4 导出为 TorchScript

```python
from transformers import AutoModel
import torch

model = AutoModel.from_pretrained("bert-base-uncased")
model.eval()

# 追踪（同时传入 attention_mask）
dummy_input_ids = torch.randint(0, 1000, (1, 128))
dummy_attention_mask = torch.ones(1, 128, dtype=torch.long)
traced_model = torch.jit.trace(model, (dummy_input_ids, dummy_attention_mask))
torch.jit.save(traced_model, "traced_model.pt")
```

### 14.5 使用 TGI 部署服务

Text Generation Inference (TGI) 是 Hugging Face 官方的生产级推理服务框架：

```bash
docker run --gpus all --shm-size 1g -p 8080:80 \
    -v $PWD/data:/data \
    ghcr.io/huggingface/text-generation-inference:latest \
    --model-id meta-llama/Llama-2-7b-hf
```

TGI 提供 OpenAI 兼容的 API，支持连续批处理、张量并行等生产级特性。TGI 原生支持 safetensors 格式。

### 14.6 使用 vLLM 部署服务

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-hf \
    --tensor-parallel-size 2 \
    --port 8000
```

### 14.7 部署方案选择

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 生产级 GPU 服务 | TGI / vLLM | 高吞吐、连续批处理 |
| 边缘设备 | ONNX + ONNX Runtime | 跨平台、轻量 |
| Intel CPU/GPU | OpenVINO | Intel 硬件优化 |
| NVIDIA GPU 极致性能 | TensorRT | 最低延迟 |
| 本地消费级硬件 | GGUF + llama.cpp | 低资源消耗 |


## 15. Hugging Face Hub 工程化

### 15.1 推送模型到 Hub

```python
# 方式一：模型对象
model.push_to_hub(
    repo_id="your-org/my-model",
    commit_message="Initial model and card",
    tags=["text-classification", "bert"],
)
tokenizer.push_to_hub("your-org/my-model")

# 方式二：Trainer 推送（自动包含训练指标）
trainer.push_to_hub(
    tags="translation",
    commit_message="Training complete",
)
```

### 15.2 模型卡（Model Card）

模型卡是 Hub 上的 `README.md`，包含元数据和用途说明：

```markdown
---
language: en
license: apache-2.0
tags:
  - text-classification
  - sentiment-analysis
datasets:
  - imdb
metrics:
  - accuracy
base_model: distilbert-base-uncased
---

# My Sentiment Model

## 用途
用于 IMDb 影评情感二分类。

## 训练数据
IMDb 数据集，25,000 条训练样本。

## 评估结果
- Accuracy: 0.92
- F1: 0.91

## 限制
仅适用于英文影评，不适用于其他领域。
```

### 15.3 私有模型与访问控制

```python
# 推送私有模型
model.push_to_hub("your-org/private-model", private=True)

# 加载私有模型（需已登录）
model = AutoModel.from_pretrained("your-org/private-model", token=True)
```

### 15.4 使用 trust_remote_code

某些模型需要自定义代码才能加载：

```python
model = AutoModel.from_pretrained(
    "some-org/custom-model",
    trust_remote_code=True,  # 允许执行 Hub 上的自定义代码
)
```

**安全警告**：`trust_remote_code=True` 会执行 Hub 上的任意 Python 代码，仅应在信任的仓库上使用。


## 16. 常见问题与最佳实践

### 16.1 常见问题

**问题：显存不足（OOM）**

- 启用量化（bitsandbytes 4-bit/8-bit）
- 使用 `device_map="auto"` 自动分配
- 减小 `per_device_train_batch_size`，配合梯度累积
- 使用 `gradient_checkpointing=True` 以时间换空间
- 使用 QLoRA 微调替代全量微调

**问题：`device_map="auto"` 不生效**

确保已安装 `accelerate`：`pip install accelerate`。未安装时会静默回退到 CPU。

**问题：GPT-2 没有 pad token**

```python
tokenizer.pad_token = tokenizer.eos_token
```

**问题：训练时 loss 为 NaN**

- 降低学习率
- 启用梯度裁剪（`max_grad_norm=1.0`）
- 检查数据中是否有异常值
- 使用混合精度时尝试 FP32 验证

**问题：`eval_strategy` 报错**

Transformers 4.41+ 中 `evaluation_strategy` 已重命名为 `eval_strategy`。如果使用旧版本，请降级 `transformers<4.41`。

**问题：生成结果包含 prompt**

```python
# 只取新生成的 token
new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
print(tokenizer.decode(new_tokens, skip_special_tokens=True))
```

**问题：`train_new_from_iterator` 报 AttributeError**

该方法仅适用于 Fast Tokenizer。确保使用 `AutoTokenizer.from_pretrained(..., use_fast=True)`。

**问题：生成任务填充方向错误**

因果语言模型生成需要 left padding：

```python
tokenizer.padding_side = "left"
tokenizer.pad_token = tokenizer.eos_token
```

### 16.2 最佳实践

**推理场景：**

- 优先使用 `AutoModel` + `AutoTokenizer` 而非 `pipeline`，以便精细控制生成参数
- 大模型务必启用量化（bitsandbytes 4-bit 性价比最高）
- 使用 `torch_dtype=torch.bfloat16` 减少显存占用
- 流式输出优先选择 `TextIteratorStreamer`（可编程）而非 `TextStreamer`（仅终端）
- 因果模型生成时设置 `padding_side="left"`
- 使用 `model.generation_config` 统一管理生成参数

**微调场景：**

- 优先使用 LoRA/QLoRA 而非全量微调，显存需求降低 60%-75%
- 小模型先用 `Trainer` 快速验证流程，再根据需求自定义
- 使用 `SFTConfig(assistant_only_loss=True)` 仅对 assistant 回复计算损失
- 使用 `packing=True` 拼接短序列提高吞吐
- 多卡训练优先用 `accelerate launch`，配合 FSDP 或 DeepSpeed ZeRO 优化
- 始终设置 `load_best_model_at_end=True` 和 `save_strategy="epoch"`
- 使用 `fp16` 或 `bf16` 混合精度加速训练
- 使用 `DataCollatorWithPadding` 实现动态填充，避免全局最大长度填充

**部署场景：**

- 生产级服务推荐 TGI 或 vLLM
- 边缘设备推荐导出 ONNX + ONNX Runtime
- Intel 硬件推荐 OpenVINO
- 本地消费级硬件推荐 GGUF 格式 + llama.cpp

**模型保存与共享：**

- 默认使用 `safetensors` 格式（更安全、加载更快）
- 保存时同时保存 tokenizer 和 generation_config
- 上传到 Hugging Face Hub 时添加模型卡说明用途和限制
- 使用 `push_to_hub` 时附带 tags 和 metrics 便于检索

### 16.3 学习路径建议

| 阶段 | 内容 | 前置知识 |
|------|------|---------|
| 入门 | Pipeline + AutoClass + 推理 | Python, PyTorch 基础 |
| 基础 | Trainer 微调 + 数据预处理 | 入门阶段 |
| 进阶 | PEFT/LoRA/QLoRA + 量化 + 流式输出 | 基础阶段 |
| 高级 | 自定义训练循环 + FSDP/DeepSpeed | 进阶阶段 |
| 专家 | 多模态 + 模型导出 + 生产部署 | 高级阶段 |


## 17. 参考资料

- **官方文档**: https://huggingface.co/docs/transformers
- **快速入门**: https://huggingface.co/docs/transformers/quicktour
- **Trainer 文档**: https://huggingface.co/docs/transformers/main_classes/trainer
- **量化指南**: https://huggingface.co/docs/transformers/main_classes/quantization
- **序列化导出**: https://huggingface.co/docs/transformers/serialization
- **模型 Hub**: https://huggingface.co/models
- **Optimum 库**: https://huggingface.co/docs/optimum
- **Accelerate 库**: https://huggingface.co/docs/accelerate
- **PEFT 库**: https://huggingface.co/docs/peft
- **TRL 库**: https://huggingface.co/docs/trl
- **Datasets 库**: https://huggingface.co/docs/datasets
- **Evaluate 库**: https://huggingface.co/docs/evaluate
- **vLLM 文档**: https://docs.vllm.ai
- **TGI 文档**: https://huggingface.co/docs/text-generation-inference
- **FSDP 指南**: https://huggingface.co/docs/transformers/fsdp
- **Generation Strategies**: https://huggingface.co/docs/transformers/generation_strategies