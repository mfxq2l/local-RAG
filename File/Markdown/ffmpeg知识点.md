# FFmpeg 完整知识点速查卡（基础 + 进阶 + 实战）

## 目录

- **第一部分：基础概念与安装**
  - [一、FFmpeg 是什么](#一ffmpeg-是什么)
  - [二、安装与验证](#二安装与验证)
  - [三、命令行整体格式](#三命令行整体格式)
  - [四、常用信息查询命令](#四常用信息查询命令)
- **第二部分：核心参数详解**
  - [五、全局参数](#五全局参数)
  - [六、输入参数](#六输入参数)
  - [七、输出参数](#七输出参数)
  - [八、流选择与映射](#八流选择与映射)
  - [九、视频参数](#九视频参数)
  - [十、音频参数](#十音频参数)
  - [十一、字幕参数](#十一字幕参数)
- **第三部分：编解码器**
  - [十二、视频编码器对比](#十二视频编码器对比)
  - [十三、H.264 编码参数（libx264）](#十三h264-编码参数libx264)
  - [十四、H.265 编码参数（libx265）](#十四h265-编码参数libx265)
  - [十五、音频编码器与参数](#十五音频编码器与参数)
- **第四部分：滤镜系统**
  - [十六、滤镜基础语法](#十六滤镜基础语法)
  - [十七、常用视频滤镜](#十七常用视频滤镜)
  - [十八、常用音频滤镜](#十八常用音频滤镜)
  - [十九、复杂滤镜图（filter_complex）](#十九复杂滤镜图filter_complex)
  - [二十、文字与水印叠加](#二十文字与水印叠加)
- **第五部分：硬件加速**
  - [二十一、硬件加速概览](#二十一硬件加速概览)
  - [二十二、NVIDIA NVENC](#二十二nvidia-nvenc)
  - [二十三、Intel QSV](#二十三intel-qsv)
  - [二十四、Linux VAAPI](#二十四linux-vaapi)
  - [二十五、Apple VideoToolbox](#二十五apple-videotoolbox)
- **第六部分：实战场景**
  - [二十六、格式转换](#二十六格式转换)
  - [二十七、视频压缩与码率控制](#二十七视频压缩与码率控制)
  - [二十八、视频裁剪与拼接](#二十八视频裁剪与拼接)
  - [二十九、音频处理](#二十九音频处理)
  - [三十、字幕处理](#三十字幕处理)
  - [三十一、图片与视频互转](#三十一图片与视频互转)
  - [三十二、流媒体推流](#三十二流媒体推流)
- **第七部分：高级技巧**
  - [三十三、两遍编码](#三十三两遍编码)
  - [三十四、多线程与性能优化](#三十四多线程与性能优化)
  - [三十五、常见错误与解决办法](#三十五常见错误与解决办法)
  - [三十六、速查小抄](#三十六速查小抄)


# 第一部分：基础概念与安装

## 一、FFmpeg 是什么

FFmpeg 是一套完整的、跨平台的音视频处理工具集，包含：

| 工具 | 用途 |
|------|------|
| `ffmpeg` | 音视频转码、处理、推流 |
| `ffprobe` | 查看音视频文件信息 |
| `ffplay` | 简易播放器 |

核心库：

- `libavcodec` — 编解码库
- `libavformat` — 封装/解封装库
- `libavfilter` — 滤镜处理库
- `libswscale` — 视频缩放/像素格式转换
- `libswresample` — 音频重采样

## 二、安装与验证

```bash
# Windows（推荐 gyan.dev 或 BtbN 构建）
# 下载后解压，将 bin 目录加入 PATH

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# 验证安装
ffmpeg -version
ffmpeg -hwaccels        # 查看可用硬件加速方式
ffmpeg -encoders        # 查看可用编码器
ffmpeg -decoders        # 查看可用解码器
ffmpeg -filters         # 查看可用滤镜
ffmpeg -formats         # 查看支持的封装格式
ffmpeg -protocols       # 查看支持的协议
```

## 三、命令行整体格式

```bash
ffmpeg [全局参数] {[输入文件参数] -i 输入文件} ... {[输出文件参数] 输出文件}...
```

- 参数以 `-` 开头，后跟值
- 输入文件前用 `-i` 指定
- 输出文件放在最后
- 参数位置很重要：`-ss` 放在 `-i` 前（快速定位）和放在 `-i` 后（精确裁剪）效果不同

## 四、常用信息查询命令

```bash
# 查看文件信息
ffprobe -v error -show_format -show_streams input.mp4
ffprobe -v quiet -print_format json -show_streams input.mp4

# 查看帮助
ffmpeg -h                    # 基础帮助
ffmpeg -h long               # 更多选项
ffmpeg -h full               # 全部选项（非常长）
ffmpeg -h encoder=libx264    # 查看特定编码器参数
ffmpeg -h filter=scale       # 查看特定滤镜参数
ffmpeg -h muxer=mp4          # 查看特定封装器参数

# 查看版本与构建信息
ffmpeg -version
```


# 第二部分：核心参数详解

## 五、全局参数

```bash
-v <loglevel>       # 日志级别：quiet, panic, fatal, error, warning, info, verbose, debug, trace
-hide_banner        # 隐藏版权信息
-y                  # 覆盖输出文件（不询问）
-n                  # 不覆盖输出文件（已存在则退出）
-stats              # 显示编码进度（默认开启）
-nostats            # 关闭进度显示
-report             # 生成报告文件（调试用）
-benchmark          # 编码结束后显示耗时统计
-cpuflags <flags>   # 强制启用/禁用特定 CPU 指令集
```

## 六、输入参数

```bash
-i <input>          # 指定输入文件
-ss <time>          # 定位到指定时间（放在 -i 前：快速定位，关键帧精度；放在 -i 后：精确到帧，较慢）
-t <duration>       # 限制输入持续时间（放在 -i 前）
-to <time>          # 指定结束时间
-itsoffset <time>   # 输入时间偏移
-stream_loop <n>    # 循环输入次数（-1 表示无限循环）
-re                 # 按原始帧率读取（用于推流）
-readrate <rate>    # 限制读取速率
-f <fmt>            # 强制输入格式
-r <rate>           # 强制输入帧率
-ar <rate>          # 强制输入采样率
-ac <channels>      # 强制输入声道数
```

## 七、输出参数

```bash
-f <fmt>            # 强制输出格式
-t <duration>       # 输出持续时间
-to <time>          # 输出结束时间
-ss <time>          # 输出起始时间
-fs <size>          # 限制输出文件大小
-timestamp <time>   # 设置输出时间戳
-metadata key=value # 添加元数据
-shortest           # 以最短流结束输出
-movflags +faststart  # MP4 将 moov atom 移到文件头（适合网络播放）
-movflags +frag_keyframe+empty_moov  # 分片 MP4（适合流媒体）
```

## 八、流选择与映射

```bash
-map 0              # 选择所有流
-map 0:v            # 选择第一个输入的所有视频流
-map 0:a            # 选择第一个输入的所有音频流
-map 0:s            # 选择第一个输入的所有字幕流
-map 0:v:0          # 选择第一个输入的第 0 个视频流
-map 0:a:1          # 选择第一个输入的第 1 个音频流
-map 1:a            # 选择第二个输入的所有音频流
-map 0 -map -0:a    # 选择所有流但排除音频
-vn                 # 禁用视频输出
-an                 # 禁用音频输出
-sn                 # 禁用字幕输出
-dn                 # 禁用数据流输出
```

## 九、视频参数

```bash
-c:v <codec>        # 视频编码器（copy 表示不重新编码）
-vcodec <codec>     # 同上，别名
-b:v <bitrate>      # 视频码率（如 2M、1500k）
-vb <bitrate>       # 同上，别名
-r <rate>           # 输出帧率
-s <WxH>            # 输出分辨率（如 1280x720）
-aspect <ratio>     # 宽高比（如 16:9）
-pix_fmt <fmt>      # 像素格式（如 yuv420p、yuv444p、rgb24）
-vf <filter>        # 视频滤镜
-vframes <n>        # 输出帧数限制
-pass <n>           # 两遍编码的遍数
-crf <n>            # 恒定质量因子（libx264/libx265 专用）
-preset <name>      # 编码预设（速度/质量权衡）
-tune <name>        # 编码调优（如 film、animation、zerolatency）
-profile:v <name>   # 编码档次（如 baseline、main、high）
-level <n>          # 编码级别
-g <n>              # GOP 大小（关键帧间隔）
-bf <n>             # B 帧数量
-refs <n>           # 参考帧数量
```

## 十、音频参数

```bash
-c:a <codec>        # 音频编码器（copy 表示不重新编码）
-acodec <codec>     # 同上，别名
-b:a <bitrate>      # 音频码率（如 192k）
-ab <bitrate>       # 同上，别名
-ar <rate>          # 采样率（如 44100、48000）
-ac <channels>      # 声道数（1 单声道，2 立体声）
-aq <quality>       # 音频质量（编码器相关）
-af <filter>        # 音频滤镜
-aframes <n>        # 输出音频帧数限制
-vol <n>            # 音量（256 为原音量）
-sample_fmt <fmt>   # 采样格式（如 s16、fltp）
-channel_layout    # 声道布局（如 stereo、5.1）
```

## 十一、字幕参数

```bash
-c:s <codec>        # 字幕编码器（copy 表示复制）
-scodec <codec>     # 同上，别名
-sn                 # 禁用字幕
-fix_sub_duration   # 修复字幕持续时间
```

### 字幕格式支持

| 格式 | 类型 | 说明 |
|------|------|------|
| SRT | 文本 | 最常见，简单字幕 |
| ASS/SSA | 文本 | 支持样式、特效 |
| VTT | 文本 | Web 字幕 |
| PGS | 图形 | Blu-ray 字幕 |
| DVD Sub | 图形 | DVD 字幕 |
| MOV_TEXT | 文本 | MP4 内嵌字幕 |


# 第三部分：编解码器

## 十二、视频编码器对比

| 编码器 | FFmpeg 名称 | 压缩率 | 编码速度 | 兼容性 | 适用场景 |
|--------|------------|--------|----------|--------|----------|
| H.264 | `libx264` | 基准 | 快 | 最好 | 通用、Web、移动端 |
| H.265/HEVC | `libx265` | 比 H.264 好 25-50% | 慢 3-5 倍 | 较好 | 4K、存储 |
| VP9 | `libvpx-vp9` | 好 | 慢 | Web（Chrome/YouTube） | WebM |
| AV1 | `libsvtav1` / `libaom-av1` / `librav1e` | 最好（比 HEVC 好 30%） | 很慢 | 逐渐普及 | 流媒体、4K/8K |
| MPEG-4 | `mpeg4` | 一般 | 快 | 老设备 | 兼容旧设备 |

## 十三、H.264 编码参数（libx264）

```bash
# 基本用法
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium output.mp4

# CRF 值范围：0（无损）～ 51（最差），默认 23
# 推荐：18-28（18 接近无损，28 文件很小）

# 编码预设（从快到慢）：
# ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
# 默认 medium，速度与质量平衡

# 调优模式
# -tune film        电影内容
# -tune animation   动画
# -tune grain       保留颗粒感
# -tune stillimage  静态图像
# -tune fastdecode  快速解码
# -tune zerolatency 零延迟（直播用）

# 完整示例
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -crf 23 \
  -preset medium \
  -profile:v high \
  -level 4.1 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -c:a aac -b:a 128k \
  output.mp4
```

## 十四、H.265 编码参数（libx265）

```bash
# 基本用法
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -preset medium output.mp4

# 注意：libx265 的 CRF 默认值为 28（比 libx264 的 23 高）
# 同 preset 下 libx265 大约比 libx264 慢 3-5 倍，文件小 30-40%

# 10-bit 编码（减少色带）
ffmpeg -i input.mp4 -c:v libx265 -crf 26 -pix_fmt yuv420p10le output.mp4

# 完整示例
ffmpeg -i input.mp4 \
  -c:v libx265 \
  -crf 28 \
  -preset medium \
  -tag:v hvc1 \
  -pix_fmt yuv420p \
  -c:a aac -b:a 128k \
  output.mp4
```

## 十五、音频编码器与参数

```bash
# AAC（最常用，MP4/MKV 推荐）
ffmpeg -i input.mp4 -c:a aac -b:a 192k output.mp4

# MP3
ffmpeg -i input.wav -c:a libmp3lame -b:a 192k output.mp3

# Opus（同码率音质最好，适合 WebM/OGG）
ffmpeg -i input.wav -c:a libopus -b:a 128k output.opus

# FLAC（无损）
ffmpeg -i input.wav -c:a flac output.flac

# Vorbis（OGG 容器）
ffmpeg -i input.wav -c:a libvorbis -q:a 5 output.ogg

# 音频码率推荐
# AAC：96-128k（语音），192-256k（音乐）
# Opus：48-64k（语音），96-128k（音乐）
# MP3：128-192k（音乐）
```

### 音频采样率与声道

```bash
-ar 44100           # 44.1kHz（CD 标准）
-ar 48000           # 48kHz（视频标准）
-ar 22050           # 22.05kHz（低质量）
-ac 1               # 单声道
-ac 2               # 立体声
-ac 6               # 5.1 环绕声
-channel_layout 5.1 # 5.1 声道布局
```


# 第四部分：滤镜系统

## 十六、滤镜基础语法

```bash
# 简单滤镜（单输入单输出）
-vf "scale=1280:720"              # 视频滤镜
-af "volume=1.5"                  # 音频滤镜

# 滤镜链（用逗号分隔，按顺序执行）
-vf "scale=1280:720,eq=brightness=0.1"

# 复杂滤镜（多输入多输出）
-filter_complex "[0:v]scale=640:360[a];[1:v]scale=640:360[b];[a][b]hstack"

# 滤镜参数用冒号分隔
-vf "scale=1280:720:flags=lanczos"

# 查看滤镜参数
ffmpeg -h filter=scale
ffmpeg -h filter=crop
```

## 十七、常用视频滤镜

```bash
# scale — 缩放
-vf "scale=1280:720"                   # 指定宽高
-vf "scale=1280:-1"                    # 宽度 1280，高度自动
-vf "scale=-1:720"                     # 高度 720，宽度自动
-vf "scale=1280:720:flags=lanczos"     # 高质量缩放算法

# crop — 裁剪
-vf "crop=640:480:100:50"              # 宽:高:x偏移:y偏移
-vf "crop=iw/2:ih/2"                   # 中间一半

# pad — 填充
-vf "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black"  # 居中填充黑边

# transpose — 旋转
-vf "transpose=1"                      # 顺时针 90°
-vf "transpose=2"                      # 逆时针 90°
-vf "hflip"                            # 水平翻转
-vf "vflip"                            # 垂直翻转

# eq — 色彩调整
-vf "eq=brightness=0.1:contrast=1.2:saturation=1.5"
# brightness: -1.0 ～ 1.0
# contrast:   0.0 ～ 2.0（默认 1.0）
# saturation: 0.0 ～ 3.0（默认 1.0）
# gamma:      0.1 ～ 10.0（默认 1.0）

# hue — 色相调整
-vf "hue=h=90:s=1.2"                   # 色相旋转 90°

# fps — 帧率调整
-vf "fps=30"                           # 强制 30fps
-vf "fps=10"                           # 10fps（制作 GIF）

# setpts — 时间戳调整（变速）
-vf "setpts=0.5*PTS"                   # 2 倍速播放
-vf "setpts=2.0*PTS"                   # 0.5 倍速播放

# blur / boxblur — 模糊
-vf "boxblur=10:1"                     # 模糊半径 10
-vf "gblur=sigma=5"                    # 高斯模糊

# unsharp — 锐化
-vf "unsharp=5:5:1.5"

# denoise — 降噪
-vf "hqdn3d=4:3:6:4.5"                 # 高质量降噪
-vf "nlmeans=10:7:15"                  # 非局部均值降噪

# deinterlace — 去隔行
-vf "yadif=0:0:0"                      # 自动去隔行
-vf "bwdif"                            # 更好但更慢

# drawtext — 文字叠加（详见二十节）

# 组合示例
-vf "scale=1280:720,eq=contrast=1.1:saturation=1.2,unsharp=5:5:0.8"
```

## 十八、常用音频滤镜

```bash
# volume — 音量
-af "volume=1.5"                       # 放大 1.5 倍
-af "volume=0.5"                       # 缩小到 50%
-af "volume=6dB"                       # 增加 6dB
-af "volume=-3dB"                      # 减少 3dB
-af "volume=enable='between(t,10,20)':volume=0"  # 10-20 秒静音

# atempo — 变速（保持音调）
-af "atempo=2.0"                       # 2 倍速
-af "atempo=0.5"                       # 0.5 倍速
# 范围：0.5 ～ 100.0，超出需串联

# aresample — 重采样
-af "aresample=48000"                  # 重采样到 48kHz

# highpass / lowpass — 高通/低通滤波
-af "highpass=f=200"                   # 高通 200Hz（去除低频噪音）
-af "lowpass=f=3000"                   # 低通 3kHz

# equalizer — 均衡器
-af "equalizer=f=1000:t=q:w=1:g=5"     # 1kHz 增益 5dB

# dynaudnorm — 动态音频标准化
-af "dynaudnorm"                       # 标准化音量

# loudnorm — 响度标准化（EBU R128）
-af "loudnorm=I=-16:LRA=11:TP=-1.5"    # 适合播客

# silenceremove — 去除静音
-af "silenceremove=start_periods=1:start_threshold=-50dB"

# afade — 淡入淡出
-af "afade=t=in:st=0:d=3"              # 3 秒淡入
-af "afade=t=out:st=30:d=3"            # 3 秒淡出

# 多滤镜组合
-af "highpass=f=100,lowpass=f=8000,volume=1.2"
```

## 十九、复杂滤镜图（filter_complex）

```bash
# 基本语法
-filter_complex "[输入流标签]滤镜链[输出标签]; [标签]滤镜[标签]"

# 画中画（PiP）
ffmpeg -i main.mp4 -i pip.mp4 \
  -filter_complex "[0:v]scale=1920:1080[bg];[1:v]scale=480:270[pip];[bg][pip]overlay=W-w-10:H-h-10" \
  output.mp4

# 视频拼接（水平）
ffmpeg -i a.mp4 -i b.mp4 \
  -filter_complex "[0:v]scale=640:360[a];[1:v]scale=640:360[b];[a][b]hstack" \
  output.mp4

# 视频拼接（垂直）
ffmpeg -i a.mp4 -i b.mp4 \
  -filter_complex "[0:v]scale=640:360[a];[1:v]scale=640:360[b];[a][b]vstack" \
  output.mp4

# 网格布局（2x2）
ffmpeg -i a.mp4 -i b.mp4 -i c.mp4 -i d.mp4 \
  -filter_complex "[0:v]scale=640:360[a];[1:v]scale=640:360[b];[2:v]scale=640:360[c];[3:v]scale=640:360[d];[a][b]hstack[top];[c][d]hstack[bottom];[top][bottom]vstack" \
  output.mp4

# 音频混合
ffmpeg -i a.mp3 -i b.mp3 \
  -filter_complex "amix=inputs=2:duration=longest:dropout_transition=2" \
  output.mp3

# 视频+音频分别处理
ffmpeg -i input.mp4 \
  -filter_complex "[0:v]scale=1280:720[v];[0:a]volume=1.5[a]" \
  -map "[v]" -map "[a]" output.mp4

# 添加水印
ffmpeg -i input.mp4 -i logo.png \
  -filter_complex "[0:v][1:v]overlay=10:10" \
  output.mp4

# 水印带透明度和位置
ffmpeg -i input.mp4 -i logo.png \
  -filter_complex "[1:v]format=rgba,colorchannelmixer=aa=0.5[logo];[0:v][logo]overlay=W-w-20:20" \
  output.mp4
```

## 二十、文字与水印叠加

```bash
# drawtext — 文字叠加
ffmpeg -i input.mp4 \
  -vf "drawtext=text='Hello World':x=50:y=100:fontsize=48:fontcolor=white:fontfile=arial.ttf" \
  output.mp4

# 文字居中
-vf "drawtext=text='居中文字':x=(w-text_w)/2:y=(h-text_h)/2:fontsize=60:fontcolor=white"

# 文字带背景框
-vf "drawtext=text='标题':x=10:y=10:fontsize=40:fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=10"

# 文字带透明度
-vf "drawtext=text='水印':x=W-tw-10:y=10:fontsize=24:fontcolor=white@0.6"

# 定时显示文字
-vf "drawtext=text='广告':x=10:y=10:fontsize=30:enable='between(t,5,10)'"

# 从文件读取文字
-vf "drawtext=textfile=words.txt:fontfile=arial.ttf:x=10:y=10:fontsize=36"

# 淡入淡出文字
-vf "drawtext=text='Fade In':x=(w-text_w)/2:y=50:fontsize=48:fontcolor=white:alpha='if(lt(t,2),t/2,1)'"

# 水印叠加（overlay 滤镜）
ffmpeg -i input.mp4 -i logo.png \
  -filter_complex "[0:v][1:v]overlay=10:10" output.mp4

# 水印居中
-filter_complex "[0:v][1:v]overlay=(W-w)/2:(H-h)/2"

# 水印右下角
-filter_complex "[0:v][1:v]overlay=W-w-10:H-h-10"

# 动态水印位置（每秒移动）
-filter_complex "[0:v][1:v]overlay=x='if(gte(t,0),mod(t*100,W),0)':y=10"
```


# 第五部分：硬件加速

## 二十一、硬件加速概览

| 技术 | 厂商 | 平台 | 编码器名称 | 解码器名称 |
|------|------|------|-----------|-----------|
| NVENC/NVDEC | NVIDIA | Win/Linux | `h264_nvenc`, `hevc_nvenc` | `h264_cuvid` 等 |
| QSV | Intel | Win/Linux | `h264_qsv`, `hevc_qsv` | `h264_qsv` 等 |
| VAAPI | Intel/AMD | Linux | `h264_vaapi`, `hevc_vaapi` | `h264_vaapi` 等 |
| VideoToolbox | Apple | macOS/iOS | `h264_videotoolbox` | `h264_videotoolbox` |
| AMF | AMD | Windows | `h264_amf`, `hevc_amf` | — |
| MediaCodec | Android | Android | `h264_mediacodec` | — |

```bash
# 查看当前 FFmpeg 支持的硬件加速
ffmpeg -hwaccels

# 查看特定硬件编码器
ffmpeg -encoders | grep nvenc
ffmpeg -encoders | grep qsv
ffmpeg -encoders | grep vaapi
ffmpeg -encoders | grep videotoolbox
```

## 二十二、NVIDIA NVENC

```bash
# 查看 NVENC 是否可用
ffmpeg -encoders | grep nvenc

# H.264 NVENC 编码
ffmpeg -i input.mp4 -c:v h264_nvenc -preset p4 -b:v 5M output.mp4

# H.265 NVENC 编码
ffmpeg -i input.mp4 -c:v hevc_nvenc -preset p7 -cq 26 output.mp4

# 10-bit HEVC
ffmpeg -i input.mp4 -c:v hevc_nvenc -preset p7 \
  -profile:v main10 -pix_fmt p010le -cq 24 output.mp4

# NVENC 预设（p1 最快 ～ p7 最高质量）
# 旧版预设：fast, medium, slow, hq, bd, ll, llhq, lossless

# 码率控制模式
# -rc:v constqp    恒定 QP（最高质量）
# -rc:v vbr        可变码率（平衡）
# -rc:v cbr        恒定码率（直播）
# -rc:v vbr_hq     高质量 VBR

# 高级选项
ffmpeg -i input.mp4 \
  -c:v h264_nvenc \
  -preset p7 \
  -multipass fullres \
  -rc:v vbr_hq \
  -b:v 5M -maxrate 7M -bufsize 10M \
  -spatial-aq 1 \
  -temporal-aq 1 \
  -rc-lookahead 32 \
  -g 250 -bf 3 \
  output.mp4

# 硬件解码 + 硬件编码（全 GPU 管线）
ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i input.mp4 \
  -c:v h264_nvenc -preset p4 output.mp4

# 硬件解码 + 滤镜 + 硬件编码
ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i input.mp4 \
  -vf "scale_cuda=1280:720" \
  -c:v h264_nvenc -preset p4 output.mp4
```

## 二十三、Intel QSV

```bash
# H.264 QSV 编码
ffmpeg -i input.mp4 -c:v h264_qsv -preset medium -b:v 5M output.mp4

# H.265 QSV 编码
ffmpeg -i input.mp4 -c:v hevc_qsv -preset medium -global_quality 26 output.mp4

# 硬件解码 + 硬件编码
ffmpeg -hwaccel qsv -c:v h264_qsv -i input.mp4 \
  -c:v h264_qsv -preset medium output.mp4

# 完整示例
ffmpeg -hwaccel qsv -i input.mp4 \
  -c:v h264_qsv \
  -preset medium \
  -global_quality 25 \
  -look_ahead 1 \
  -c:a aac -b:a 128k \
  output.mp4
```

## 二十四、Linux VAAPI

```bash
# 查看 VAAPI 设备
ls /dev/dri/renderD*

# H.264 VAAPI 编码
ffmpeg -vaapi_device /dev/dri/renderD128 \
  -i input.mp4 \
  -vf "format=nv12,hwupload" \
  -c:v h264_vaapi -b:v 5M output.mp4

# H.265 VAAPI 编码
ffmpeg -vaapi_device /dev/dri/renderD128 \
  -i input.mp4 \
  -vf "format=nv12,hwupload" \
  -c:v hevc_vaapi -b:v 5M output.mp4

# 硬件解码 + 硬件编码
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 \
  -hwaccel_output_format vaapi -i input.mp4 \
  -c:v h264_vaapi output.mp4

# 硬件解码 + 滤镜 + 硬件编码
ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 \
  -hwaccel_output_format vaapi -i input.mp4 \
  -vf "scale_vaapi=1280:720" \
  -c:v h264_vaapi output.mp4
```

## 二十五、Apple VideoToolbox

```bash
# H.264 VideoToolbox 编码
ffmpeg -i input.mp4 -c:v h264_videotoolbox -b:v 5M output.mp4

# H.265 VideoToolbox 编码
ffmpeg -i input.mp4 -c:v hevc_videotoolbox -b:v 5M output.mp4

# 硬件解码
ffmpeg -hwaccel videotoolbox -i input.mp4 -c:v h264_videotoolbox output.mp4
```


# 第六部分：实战场景

## 二十六、格式转换

```bash
# 基本格式转换
ffmpeg -i input.mov output.mp4
ffmpeg -i input.avi output.mkv

# 无损转换（不重新编码，最快）
ffmpeg -i input.mp4 -c copy output.mkv

# 指定编码器转换
ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4

# 转换并压缩
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4

# 提取视频流（不含音频）
ffmpeg -i input.mp4 -an -c:v copy output.mp4

# 提取音频流
ffmpeg -i input.mp4 -vn -c:a copy output.aac
ffmpeg -i input.mp4 -vn -c:a libmp3lame -b:a 192k output.mp3
```

## 二十七、视频压缩与码率控制

```bash
# CRF 模式（恒定质量，推荐）
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4

# 目标码率模式
ffmpeg -i input.mp4 -b:v 1500k -b:a 192k output.mp4

# 两遍编码（更精确的码率控制）
# 第一遍
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -an -f null NUL
# 第二遍
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 -c:a aac -b:a 128k output.mp4

# 限制最大码率（适合流媒体）
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -maxrate 3M -bufsize 6M output.mp4

# 压缩到指定大小（粗略估算）
# 例如压缩到 10MB，视频时长 60 秒
# 总码率 = 10MB * 8 / 60 ≈ 1333kbps
ffmpeg -i input.mp4 -b:v 1200k -b:a 128k output.mp4
```

## 二十八、视频裁剪与拼接

```bash
# 裁剪（快速，关键帧精度，放在 -i 前）
ffmpeg -ss 00:01:00 -to 00:02:30 -i input.mp4 -c copy output.mp4

# 裁剪（精确，放在 -i 后）
ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:30 -c copy output.mp4

# 裁剪（指定时长）
ffmpeg -ss 00:01:00 -t 90 -i input.mp4 -c copy output.mp4

# 拼接（相同编码，用 concat 协议）
# 创建列表文件 list.txt：
# file 'part1.mp4'
# file 'part2.mp4'
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# 拼接（不同编码，用 concat 滤镜）
ffmpeg -i part1.mp4 -i part2.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]" \
  -map "[outv]" -map "[outa]" output.mp4
```

## 二十九、音频处理

```bash
# 提取音频
ffmpeg -i input.mp4 -vn -c:a copy output.aac

# 音频转码
ffmpeg -i input.wav -c:a libmp3lame -b:a 192k output.mp3

# 音频裁剪
ffmpeg -ss 00:00:30 -t 60 -i input.mp3 -c copy output.mp3

# 调整音量
ffmpeg -i input.mp3 -af "volume=1.5" output.mp3

# 音频拼接
ffmpeg -i a.mp3 -i b.mp3 -filter_complex "concat=n=2:v=0:a=1" output.mp3

# 音频混合
ffmpeg -i a.mp3 -i b.mp3 -filter_complex "amix=inputs=2:duration=longest" output.mp3

# 音频淡入淡出
ffmpeg -i input.mp3 -af "afade=t=in:st=0:d=3,afade=t=out:st=27:d=3" output.mp3

# 音频响度标准化
ffmpeg -i input.mp3 -af "loudnorm=I=-16:LRA=11:TP=-1.5" output.mp3

# 变速不变调
ffmpeg -i input.mp3 -af "atempo=1.5" output.mp3
```

## 三十、字幕处理

```bash
# 提取字幕
ffmpeg -i input.mkv -map 0:s:0 output.srt

# 嵌入字幕（软字幕，不重新编码）
ffmpeg -i input.mp4 -i subtitle.srt -c copy -c:s mov_text output.mp4

# 烧录字幕（硬字幕，重新编码视频）
ffmpeg -i input.mp4 -vf "subtitles=subtitle.srt" -c:a copy output.mp4

# 烧录 ASS 字幕并指定样式
ffmpeg -i input.mp4 -vf "ass=subtitle.ass" -c:a copy output.mp4

# 字幕同步偏移
ffmpeg -itsoffset 2 -i subtitle.srt -i input.mp4 -c copy output.mp4

# 字幕格式转换
ffmpeg -i input.srt output.ass
ffmpeg -i input.ass output.srt

# 多语言字幕轨道
ffmpeg -i input.mp4 -i chinese.srt -i english.srt \
  -map 0 -map 1 -map 2 \
  -c copy -c:s mov_text \
  -metadata:s:s:0 language=chi \
  -metadata:s:s:1 language=eng \
  output.mp4
```

## 三十一、图片与视频互转

```bash
# 视频 → 图片序列
ffmpeg -i input.mp4 -r 1 output_%03d.jpg          # 每秒 1 帧
ffmpeg -i input.mp4 -vf "fps=1" output_%04d.png   # 每秒 1 帧

# 提取单帧（指定时间）
ffmpeg -ss 00:01:30 -i input.mp4 -vframes 1 output.jpg

# 图片序列 → 视频
ffmpeg -framerate 30 -i frame_%03d.png -c:v libx264 -pix_fmt yuv420p output.mp4

# 图片 + 音频 → 视频
ffmpeg -loop 1 -i cover.jpg -i audio.mp3 \
  -c:v libx264 -tune stillimage -c:a aac -b:a 192k \
  -pix_fmt yuv420p -shortest output.mp4

# 视频 → GIF
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif

# 简单 GIF（质量较差）
ffmpeg -i input.mp4 -ss 00:00:05 -t 3 -vf "fps=10,scale=320:-1" output.gif

# GIF → 视频
ffmpeg -i input.gif -movflags faststart -pix_fmt yuv420p \
  -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" output.mp4

# 截图（每 10 秒一张）
ffmpeg -i input.mp4 -vf "fps=1/10" output_%03d.jpg

# 生成缩略图拼贴
ffmpeg -i input.mp4 -vf "fps=1/60,scale=320:-1,tile=4x4" output.jpg
```

## 三十二、流媒体推流

```bash
# RTMP 推流
ffmpeg -re -i input.mp4 \
  -c:v libx264 -preset veryfast -b:v 2M -maxrate 2M -bufsize 4M \
  -c:a aac -b:a 128k -ar 44100 \
  -f flv rtmp://live.example.com/app/streamkey

# 推流（复制流，不重新编码）
ffmpeg -re -i input.mp4 -c copy -f flv rtmp://live.example.com/app/streamkey

# HLS 输出
ffmpeg -i input.mp4 \
  -c:v libx264 -preset veryfast -b:v 2M \
  -c:a aac -b:a 128k \
  -f hls \
  -hls_time 10 \
  -hls_list_size 0 \
  -hls_segment_filename "segment_%03d.ts" \
  output.m3u8

# RTMP → HLS 转换
ffmpeg -i rtmp://input/stream -c copy -f flv http://output/stream.flv

# UDP 推流
ffmpeg -re -i input.mp4 -c copy -f mpegts udp://239.0.0.1:1234

# SRT 推流
ffmpeg -re -i input.mp4 -c copy -f mpegts "srt://host:port?mode=caller"

# 屏幕录制（Windows）
ffmpeg -f gdigrab -framerate 30 -i desktop -c:v libx264 -preset ultrafast output.mp4

# 屏幕录制（Linux）
ffmpeg -f x11grab -framerate 30 -i :0.0 -c:v libx264 -preset ultrafast output.mp4

# 摄像头录制（Windows）
ffmpeg -f dshow -i video="摄像头名称" -c:v libx264 output.mp4
```


# 第七部分：高级技巧

## 三十三、两遍编码

```bash
# 两遍编码用于精确控制输出文件大小

# 第一遍（分析）
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 1 -an -f null NUL
# Linux/macOS 用 /dev/null 代替 NUL

# 第二遍（编码）
ffmpeg -i input.mp4 -c:v libx264 -b:v 2M -pass 2 -c:a aac -b:a 128k output.mp4

# 清理 pass 日志
rm ffmpeg2pass-0.log
```

## 三十四、多线程与性能优化

```bash
# 设置线程数
-threads 4                    # 使用 4 个线程
-threads 0                    # 自动检测（默认）

# 编码速度优化
# 1. 使用更快的 preset
-preset ultrafast             # 最快

# 2. 使用硬件加速（详见第五部分）
-c:v h264_nvenc -preset p1

# 3. 使用 -c copy 避免重新编码
-c copy

# 4. 使用 -ss 放在 -i 前快速定位
ffmpeg -ss 00:01:00 -i input.mp4 -c copy output.mp4

# 5. 限制解码线程
-threads 2

# 6. 使用 -threads 控制编码线程
ffmpeg -i input.mp4 -c:v libx264 -threads 8 output.mp4

# 7. 视频滤镜多线程
-filter_threads 4

# 8. 使用 -benchmark 查看耗时
ffmpeg -i input.mp4 -c:v libx264 -benchmark output.mp4
```

## 三十五、常见错误与解决办法

| 错误 | 原因 | 解决办法 |
|------|------|----------|
| `No such file or directory` | 文件路径错误 | 检查路径，路径含空格时加引号 |
| `Invalid argument` | 参数错误 | 检查参数值范围 |
| `Codec not found` | 编码器不可用 | `ffmpeg -encoders` 查看可用编码器 |
| `Unknown encoder 'xxx'` | 编码器未编译进 FFmpeg | 换用其他编码器或重装完整版 |
| `moov atom not found` | MP4 文件不完整 | 使用 `-movflags +faststart` 重新封装 |
| `Conversion failed` | 编码失败 | 查看详细日志，检查输入文件 |
| `Protocol not found` | 协议不支持 | 检查 FFmpeg 编译选项 |
| `Permission denied` | 文件权限不足 | 检查文件权限 |
| `Output file #0 does not contain any stream` | 没有输出流 | 检查 `-map` 和流选择参数 |
| `Avi header missing` | AVI 文件损坏 | 尝试修复或换用其他工具 |
| `Invalid data found` | 输入数据损坏 | 检查输入文件完整性 |
| `height not divisible by 2` | 分辨率不是偶数 | 用 `scale=trunc(iw/2)*2:trunc(ih/2)*2` |
| `width not divisible by 2` | 同 | 用 `scale` 调整到偶数 |
| `Too many packets buffered` | 缓冲区溢出 | 加 `-max_muxing_queue_size 1024` |
| `discarding sub frame` | 时间戳问题 | 加 `-vsync 0` 或 `-fps_mode passthrough` |

### 常用调试方法

```bash
# 提高日志级别
ffmpeg -v debug -i input.mp4 output.mp4

# 只看错误
ffmpeg -v error -i input.mp4 output.mp4

# 静默模式
ffmpeg -v quiet -i input.mp4 output.mp4

# 生成报告文件
ffmpeg -report -i input.mp4 output.mp4
# 生成 ffmpeg-*.log 文件
```

## 三十六、速查小抄

### 最常用命令

```bash
ffmpeg -i input.mp4 output.avi           # 格式转换
ffmpeg -i input.mp4 -c copy output.mkv   # 无损转换
ffmpeg -i input.mp4 -vf scale=1280:-1 output.mp4  # 缩放
ffmpeg -i input.mp4 -ss 00:01:00 -t 30 -c copy output.mp4  # 裁剪
ffmpeg -i input.mp4 -vn -c:a copy output.aac  # 提取音频
ffmpeg -i input.mp4 -an -c:v copy output.mp4  # 提取视频
```

### 参数位置速记

| 参数 | `-i` 之前 | `-i` 之后 |
|------|----------|----------|
| `-ss` | 快速定位（关键帧精度） | 精确裁剪（帧精度） |
| `-t` | 限制输入时长 | 限制输出时长 |
| `-f` | 指定输入格式 | 指定输出格式 |

### 编码器速查

```bash
-c:v libx264          # H.264 软件编码（通用）
-c:v libx265          # H.265 软件编码（压缩率好）
-c:v h264_nvenc       # H.264 NVIDIA 硬件编码
-c:v hevc_nvenc       # H.265 NVIDIA 硬件编码
-c:v h264_qsv         # H.264 Intel 硬件编码
-c:v h264_vaapi       # H.264 Linux VAAPI
-c:a aac              # AAC 音频
-c:a libmp3lame       # MP3 音频
-c:a libopus          # Opus 音频
-c copy               # 不重新编码
```

### CRF 推荐值

| 编码器 | 范围 | 推荐值 | 说明 |
|--------|------|--------|------|
| libx264 | 0-51 | 23 | 18 接近无损，28 文件小 |
| libx265 | 0-51 | 28 | 比 x264 的 23 大约高 5 |
| libvpx-vp9 | 0-63 | 31 | 越低质量越好 |
| libsvtav1 | 0-63 | 35 | 越低质量越好 |

### Preset 速度对比

| Preset | libx264 | libx265 |
|--------|---------|----------|
| ultrafast | 最快 | — |
| superfast | 很快 | — |
| veryfast | 快 | — |
| faster | 较快 | — |
| fast | 中等 | — |
| medium | 平衡（默认） | 平衡（默认） |
| slow | 慢 | 慢 |
| slower | 很慢 | 很慢 |
| veryslow | 极慢 | 极慢 |
| placebo | 最慢 | 最慢 |

### 像素格式

| 格式 | 说明 |
|------|------|
| `yuv420p` | 最常用，兼容性最好 |
| `yuv422p` | 专业视频 |
| `yuv444p` | 无损色彩 |
| `yuv420p10le` | 10-bit，减少色带 |
| `rgb24` | RGB 格式 |
| `nv12` | 硬件加速常用 |

### 常用滤镜速查

| 滤镜 | 功能 | 示例 |
|------|------|------|
| `scale` | 缩放 | `scale=1280:720` |
| `crop` | 裁剪 | `crop=640:480:100:50` |
| `pad` | 填充 | `pad=1920:1080:0:0:black` |
| `overlay` | 叠加 | `overlay=10:10` |
| `drawtext` | 文字 | `drawtext=text='Hi'` |
| `fps` | 帧率 | `fps=30` |
| `setpts` | 变速 | `setpts=0.5*PTS` |
| `volume` | 音量 | `volume=1.5` |
| `atempo` | 音频变速 | `atempo=1.5` |
| `afade` | 淡入淡出 | `afade=t=in:d=3` |
| `subtitles` | 字幕 | `subtitles=sub.srt` |
| `eq` | 色彩 | `eq=contrast=1.2` |
| `transpose` | 旋转 | `transpose=1` |
| `hflip` / `vflip` | 翻转 | `hflip` |
| `boxblur` | 模糊 | `boxblur=10:1` |
| `unsharp` | 锐化 | `unsharp=5:5:1.5` |

### 硬件加速速查

```bash
# NVIDIA
-hwaccel cuda -hwaccel_output_format cuda -c:v h264_nvenc

# Intel QSV
-hwaccel qsv -c:v h264_qsv

# VAAPI（Linux）
-vaapi_device /dev/dri/renderD128 -vf "format=nv12,hwupload" -c:v h264_vaapi

# VideoToolbox（macOS）
-hwaccel videotoolbox -c:v h264_videotoolbox

# 查看可用硬件加速
ffmpeg -hwaccels
ffmpeg -encoders | grep nvenc
```

### 流媒体速查

```bash
# RTMP 推流
ffmpeg -re -i input.mp4 -c:v libx264 -preset veryfast -b:v 2M -c:a aac -b:a 128k -f flv rtmp://server/app/key

# HLS 输出
ffmpeg -i input.mp4 -c:v libx264 -f hls -hls_time 10 output.m3u8

# 屏幕录制（Windows）
ffmpeg -f gdigrab -framerate 30 -i desktop output.mp4

# 摄像头录制
ffmpeg -f dshow -i video="摄像头名称" output.mp4
```

### 常用封装格式

| 格式 | 扩展名 | 特点 |
|------|--------|------|
| MP4 | `.mp4` | 通用，网络播放首选 |
| MKV | `.mkv` | 容器灵活，支持多轨道 |
| WebM | `.webm` | Web 优化，VP8/VP9/AV1 |
| MOV | `.mov` | Apple 格式 |
| AVI | `.avi` | 老旧，兼容性差 |
| FLV | `.flv` | 直播推流常用 |
| TS | `.ts` | 流媒体，HLS 分片 |
| GIF | `.gif` | 动图，256 色限制 |

### 视频编码标准对比

| 标准 | 压缩率 | 编码速度 | 硬件支持 | 适用场景 |
|------|--------|----------|----------|----------|
| H.264 | 1x | 快 | 广泛 | 通用、Web、移动 |
| H.265 | 1.25-1.5x | 慢 3-5 倍 | 较好 | 4K、HDR、存储 |
| VP9 | 1.3x | 慢 | Chrome/YouTube | WebM、YouTube |
| AV1 | 1.5-1.6x | 很慢 | 逐渐普及 | 流媒体、8K |
| VVC | 1.8x | 极慢 | 很少 | 未来标准 |

### 常用元数据操作

```bash
# 设置标题
ffmpeg -i input.mp4 -metadata title="我的视频" output.mp4

# 设置语言
ffmpeg -i input.mp4 -metadata:s:a:0 language=chi output.mp4

# 查看元数据
ffprobe -show_format input.mp4
ffprobe -show_streams input.mp4
```