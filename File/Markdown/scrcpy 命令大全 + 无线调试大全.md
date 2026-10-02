
---

# scrcpy 命令大全 + 无线调试完整手册

> **scrcpy**（Screen Copy）是一款开源的 Android 设备投屏与控制工具，支持 USB 和无线连接，延迟低、功能强大。

---

## 目录

- [一、scrcpy 基础命令](#一scrcpy-基础命令)
- [二、显示与画质控制](#二显示与画质控制)
- [三、屏幕录制](#三屏幕录制)
- [四、控制选项](#四控制选项)
- [五、无线调试完整流程](#五无线调试完整流程)
- [六、ADB 无线管理命令](#六adb-无线管理命令)
- [七、快捷键大全](#七快捷键大全)
- [八、常见问题解决](#八常见问题解决)
- [九、组合拳实战](#九组合拳实战)
- [十、输入与文本操作](#十输入与文本操作)
- [十一、多设备管理](#十一多设备管理)
- [十二、高级功能](#十二高级功能)
- [十三、附录：速查卡片](#十三附录速查卡片)

---

## 一、scrcpy 基础命令

| 命令 | 说明 |
|------|------|
| `scrcpy` | 启动投屏（默认 USB 连接） |
| `scrcpy -s 设备序列号` | 指定设备投屏（多设备时使用） |
| `scrcpy -d` | 选择通过 USB 连接的唯一设备 |
| `scrcpy -e` | 选择通过 TCP/IP 连接的唯一设备 |
| `scrcpy --version` | 查看 scrcpy 版本 |
| `scrcpy --help` | 查看所有帮助信息 |

```bash
# 使用示例
scrcpy -s 192.168.1.100:5555    # 指定无线设备
scrcpy -d                        # 自动选择 USB 设备
```

---

## 二、显示与画质控制

| 命令 | 说明 |
|------|------|
| `scrcpy --max-size 1024` | 限制分辨率（短边为 1024 像素） |
| `scrcpy -m 800` | 同上，简写形式 |
| `scrcpy --max-fps 30` | 限制帧率为 30fps |
| `scrcpy --bit-rate 2M` | 设置视频码率为 2Mbps |
| `scrcpy -b 8M` | 设置码率（默认 8Mbps） |
| `scrcpy --crop 1440:3216:0:0` | 裁剪画面（宽:高:x:y） |
| `scrcpy --rotation 90` | 旋转屏幕（0/90/180/270） |
| `scrcpy --lock-video-orientation 0` | 锁定方向（0=横屏，1=竖屏） |
| `scrcpy --display-id 0` | 指定显示设备 ID（多屏手机） |

```bash
# 使用示例：低画质省带宽
scrcpy -m 720 -b 2M --max-fps 15

# 使用示例：高清投屏
scrcpy -m 1920 -b 16M --max-fps 60
```

---

## 三、屏幕录制

| 命令 | 说明 |
|------|------|
| `scrcpy --record file.mp4` | 投屏同时录制视频 |
| `scrcpy -r file.mp4` | 同上，简写形式 |
| `scrcpy -r file.mkv` | 录制为 MKV 格式 |
| `scrcpy --no-display --record file.mp4` | 只录屏不显示（后台录制） |
| `scrcpy -Nr file.mp4` | 同上，简写形式 |
| `scrcpy -r file.mp4 --no-audio` | 不录制音频 |

```bash
# 使用示例：后台录制（不显示窗口）
scrcpy --no-display --record /path/to/recording.mp4

# 使用示例：高清录制
scrcpy -r demo.mp4 -m 1920 -b 16M
```

---

## 四、控制选项

| 命令 | 说明 |
|------|------|
| `scrcpy --no-control` | 只投屏，不控制设备（仅查看） |
| `scrcpy -n` | 同上，简写形式 |
| `scrcpy --turn-screen-off` | 投屏时关闭手机屏幕（省电） |
| `scrcpy -S` | 同上，简写形式 |
| `scrcpy --stay-awake` | 防止设备休眠 |
| `scrcpy -w` | 同上，简写形式 |
| `scrcpy -Sw` | 关屏 + 保持唤醒（组合） |
| `scrcpy --show-touches` | 显示触摸点（演示用） |
| `scrcpy -t` | 同上，简写形式 |
| `scrcpy --always-on-top` | 窗口始终置顶 |
| `scrcpy --window-title "我的手机"` | 自定义窗口标题 |
| `scrcpy --push-target=/sdcard/Download` | 拖放文件的目标目录 |
| `scrcpy --hid-keyboard` | HID 键盘模式（模拟物理键盘） |
| `scrcpy -K` | 同上，简写形式 |
| `scrcpy --hid-mouse` | HID 鼠标模式 |
| `scrcpy -M` | 同上，简写形式 |
| `scrcpy --prefer-text` | 优先使用文本输入（非 HID） |

```bash
# 使用示例：演示模式（显示触摸 + 置顶）
scrcpy -t --always-on-top

# 使用示例：省电关屏
scrcpy -Sw
```

---

## 五、无线调试完整流程

### 方法 A：一键自动模式（推荐）

```bash
# USB 连接手机后直接运行
scrcpy --tcpip
# 自动完成：获取 IP → 启用 TCP 模式 → 连接 → 启动投屏
```

### 方法 B：手动模式（最稳）

#### 1. USB 连接手机
```bash
adb usb
adb devices              # 确认设备已连接
```

#### 2. 切换到无线模式
```bash
adb tcpip 5555
# 显示：restarting in TCP mode port: 5555
```

#### 3. 拔掉 USB 线

#### 4. 获取手机 IP（三种方式）
```bash
# 方式1：手机上查看
# 设置 → 关于手机 → 状态信息 → IP 地址

# 方式2：通过 ADB 命令（未断开 USB 时）
adb shell ip route | awk '{print $9}'

# 方式3：使用 nmap 扫描局域网
nmap -sP 192.168.10.0/24   # 替换为你的网段
```

#### 5. ADB 无线连接
```bash
adb connect 192.168.10.12:5555
# 成功显示：connected to 192.168.10.12:5555
```

#### 6. 启动 scrcpy
```bash
scrcpy
```

### 方法 C：Android 11+ 配对码模式（无需 USB）

#### 1. 手机上操作
```
设置 → 开发者选项 → 无线调试 → 开启
点击 "使用配对码配对设备" → 记录 IP、端口和配对码
```

#### 2. Kali 里配对
```bash
adb pair 192.168.10.12:配对端口
# 输入手机上显示的 6 位配对码
```

#### 3. 连接并投屏
```bash
adb connect 192.168.10.12:连接端口
scrcpy
```

---

## 六、ADB 无线管理命令

| 命令 | 说明 |
|------|------|
| `adb tcpip 5555` | 开启 TCP 模式（端口 5555） |
| `adb connect 192.168.10.12:5555` | 无线连接手机 |
| `adb disconnect` | 断开所有无线连接 |
| `adb disconnect 192.168.10.12:5555` | 断开指定设备 |
| `adb usb` | 切回 USB 模式 |
| `adb devices` | 查看已连接设备列表 |
| `adb kill-server` | 停止 ADB 服务 |
| `adb start-server` | 启动 ADB 服务 |

---

## 七、快捷键大全

> **MOD 默认 = Alt 键**（可修改为其他键）

### 7.1 窗口与显示控制

| 快捷键 | 作用 |
|------|------|
| `MOD + f` | 切换全屏模式 |
| `MOD + ←/→` | 向左/右旋转显示 |
| `MOD + g` | 窗口调整为 1:1（完美像素） |
| `MOD + w` / 双击左键 | 调整窗口去黑边 |
| `MOD + h` / 中键 | 点击 HOME 键 |
| `MOD + b` / 右键² | 点击返回键 |
| `MOD + s` | 点击多任务键（概览） |
| `MOD + m` | 点击菜单键 |

### 7.2 电源与屏幕控制

| 快捷键 | 作用 |
|------|------|
| `MOD + p` | 点击电源键 |
| 右键（屏幕熄灭时） | 点亮屏幕 |
| `MOD + o` | 关闭手机屏幕（保持投屏） |
| `MOD + Shift + o` | 打开手机屏幕 |
| `MOD + r` | 旋转手机屏幕 |

### 7.3 系统与通知

| 快捷键 | 作用 |
|------|------|
| `MOD + n` | 展开通知栏 |
| `MOD + n + n` | 展开快捷设置面板 |
| `MOD + Shift + n` | 折叠通知栏 |
| `MOD + ↑` | 音量 + |
| `MOD + ↓` | 音量 - |

### 7.4 剪贴板操作

| 快捷键 | 作用 |
|------|------|
| `MOD + c` | 复制手机内容到电脑剪贴板 |
| `MOD + v` | 粘贴电脑剪贴板内容到手机 |
| `MOD + Shift + v` | 注入电脑剪贴板文本（模拟输入） |

### 7.5 其他功能

| 快捷键 | 作用 |
|------|------|
| `MOD + i` | 显示 FPS 计数器 |
| `MOD + d` | 在手机上启动/关闭调试模式 |

> **说明**：右键单击² 在屏幕关闭时是点亮屏幕，开启时是返回键。

---

## 八、常见问题解决

### 8.1 连接失败
```bash
# 重启 ADB 服务
adb kill-server
adb start-server
adb connect 192.168.10.12:5555

# 检查防火墙（Windows）
# 允许端口 5555 通过防火墙

# 检查手机是否在同一局域网
ping 192.168.10.12
```

### 8.2 多个设备冲突
```bash
# 查看所有设备
adb devices

# 指定设备启动
scrcpy -s 192.168.10.12:5555
scrcpy -s 设备序列号
```

### 8.3 画面卡顿
```bash
# 降低画质和码率
scrcpy -b 2M --max-size 800 --max-fps 15

# 使用有线连接（更稳定）
scrcpy
```

### 8.4 输入法不能用
```bash
# 启用 HID 键盘模式（需要 Android 11+）
scrcpy --hid-keyboard

# 或在手机上切换输入法为 "物理键盘"
```

### 8.5 无法拖拽安装 APK
```bash
# 直接将 APK 文件拖拽到 scrcpy 窗口即可安装
# 或使用命令行
adb install app.apk
```

### 8.6 音频无法传输（Android 10+）
```bash
# scrcpy 本身不支持音频传输
# 使用 sndcpy 配合
https://github.com/rom1v/sndcpy

# 或使用 Android 11 的内置音频转发
```

---

## 九、组合拳实战

### 9.1 后台录制手机屏幕
```bash
scrcpy --no-display --record 录制视频.mp4 --max-size 720
```

### 9.2 低延迟投屏（游戏/演示）
```bash
scrcpy --bit-rate 10M --max-fps 60 --max-size 1080
```

### 9.3 省电模式（关手机屏幕）
```bash
scrcpy -Sw --max-fps 30
```

### 9.4 一键无线连接 + 启动
```bash
adb tcpip 5555 && adb connect 192.168.10.12:5555 && scrcpy
```

### 9.5 多窗口投屏（多台设备）
```bash
# 终端1
scrcpy -s 192.168.1.101:5555 --window-title "手机A"

# 终端2
scrcpy -s 192.168.1.102:5555 --window-title "手机B"
```

### 9.6 演示模式（高清 + 触摸显示 + 置顶）
```bash
scrcpy -t --always-on-top -m 1920 -b 16M
```

### 9.7 投屏并录制 + 关屏
```bash
scrcpy -S -r demo_$(date +%Y%m%d).mp4
```

---

## 十、输入与文本操作

### 10.1 通过 ADB 输入文本
```bash
# 输入指定文本
adb shell input text "Hello World"

# 输入密码（注意特殊字符需转义）
adb shell input text "123456"

# 模拟按键
adb shell input keyevent 26    # 电源键（唤醒/锁屏）
adb shell input keyevent 3     # Home 键
adb shell input keyevent 4     # 返回键
adb shell input keyevent 24    # 音量+
adb shell input keyevent 25    # 音量-
adb shell input keyevent 224   # 点亮屏幕
```

### 10.2 常用 Keyevent 对照表

| 按键 | 键码 |
|------|------|
| Home | `3` |
| 返回 | `4` |
| 电源 | `26` |
| 音量+ | `24` |
| 音量- | `25` |
| 拍照 | `27` |
| 点亮屏幕 | `224` |
| 多任务 | `187` |
| 菜单 | `82` |
| 搜索 | `84` |

---

## 十一、多设备管理

```bash
# 查看所有已连接设备
adb devices
# 输出示例：
# 192.168.1.100:5555    device
# 192.168.1.101:5555    device
# emulator-5554         device

# 指定设备投屏
scrcpy -s 192.168.1.100:5555

# 同时连接多个设备（多个终端）
# 终端1
scrcpy -s 192.168.1.100:5555 --window-title "Pixel 6"

# 终端2
scrcpy -s 192.168.1.101:5555 --window-title "Galaxy S23"
```

---

## 十二、高级功能

### 12.1 自定义窗口位置（X11/Wayland）
```bash
# Linux 下设置窗口位置（需配合 wmctrl）
scrcpy && wmctrl -r "我的手机" -e 0,100,100,800,600
```

### 12.2 视频流输出到文件
```bash
# 输出原始视频流到文件
scrcpy --no-audio --record=video.h264

# 使用 FFmpeg 处理
scrcpy --no-display --record - | ffmpeg -i - -c:v copy output.mp4
```

### 12.3 自定义 MOD 键
```bash
# 将 MOD 键改为左 Ctrl
scrcpy --shortcut-mod=lctrl

# 可用值：lctrl, rctrl, lalt, ralt, lsuper, rsuper
```

### 12.4 多显示器支持（Android 10+）
```bash
# 列出所有显示器
adb shell dumpsys display

# 投屏到指定显示器
scrcpy --display-id 1
```

### 12.5 摄像头镜像（Android 12+）
```bash
# 将手机摄像头作为虚拟摄像头
scrcpy --camera-id=0 --video-codec=h264
```

---

## 十三、附录：速查卡片

### 快速启动
```bash
scrcpy                    # USB 投屏
scrcpy --tcpip            # 一键无线投屏
scrcpy -Sw                # 关屏投屏（省电）
scrcpy --no-display -r demo.mp4  # 后台录屏
```

### 画质优化
```bash
# 高清流畅
scrcpy -m 1920 -b 16M --max-fps 60

# 低带宽
scrcpy -m 720 -b 2M --max-fps 15

# 完美像素（1:1）
scrcpy -m 1080 --no-resize
```

### 无线连接流程
```bash
# 步骤1（USB连接时）
adb tcpip 5555

# 步骤2（拔掉USB后）
adb connect 手机IP:5555

# 步骤3
scrcpy
```

### 快捷键速记
| 快捷键 | 功能 |
|------|------|
| `Alt + f` | 全屏 |
| `Alt + h` | Home |
| `Alt + b` | 返回 |
| `Alt + o` | 关屏 |
| `Alt + p` | 电源 |
| `Alt + c/v` | 剪贴板 |
| `右键` | 返回/亮屏 |

---

> **提示**：scrcpy 默认 MOD 键是 `Alt`，可以在启动时通过 `--shortcut-mod` 参数修改。最新版 scrcpy 支持音频传输（Android 11+）和虚拟摄像头功能。