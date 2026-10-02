
---

# 网络安全/渗透测试/二进制逆向/Web安全/移动端调试/密码破解 超级速查手册

> **作者**：mfxq2l  
> **提示**：该合集整理资料如果合理使用是你的帮手，违规使用是你的狱友！  
> *“如果你看不懂这些文件，说明你是个好人；如果你看懂了，说明你是个……有技术的好人。”*

---

## 📖 项目简介

欢迎来到这份 **“网络安全/渗透测试/二进制逆向/Web安全/移动端调试/密码破解”** 超级速查手册。就是有点杂，嘻嘻嘻。

这是一份由 **22 个 Markdown/TXT 速查卡** 组成的知识库，涵盖了从 Web 渗透、二进制漏洞、网络嗅探、密码爆破、移动端调试，到 JavaScript 安全、Linux 运维、甚至大模型指令的全方位技术笔记。

**一句话概括**：这是你忘了某条命令时，不需要百度/Google/Bing/StackOverflow 的底气。

---

## 📂 文件目录与详细说明

### 1. Burp Suite sqlmap 速查卡.txt
**用途**：Web 安全测试 & SQL 注入自动化

- Burp Suite 抓包、改包、重放、爆破流程
- sqlmap 拖库、拿 Shell、Cookie 注入
- Burp + sqlmap 联合作战（从抓包到注入一条龙）

**适合人群**：想成为 Web 安全测试工程师，或者想给自家网站做“免费压力测试”的人。

> ⚠️ **温馨提示**：不要在未授权的网站上使用，否则你可能收获的不是漏洞报告，而是 《网络安全法》学习通知书。

---

### 2. C速查卡.md
**用途**：C 语言完整语法手册（从 Hello World 到指针到链表）

- 数据类型、运算符、控制流、数组、指针、结构体
- 动态内存管理、文件操作、预处理器、编译链接
- 位操作技巧、GDB 调试、Valgrind 内存检测
- C11/C17/C23 新特性

**适合人群**：学 C 学到怀疑人生的人，以及想理解“为什么 Python 那么慢”的人。

> 💡 **冷知识**：C 语言的指针，就像生活——你以为你掌控了它，其实它随时可能让你 Segfault。

---

### 3. exe包装.md
**用途**：C / Python 程序打包成 EXE 速查

- gcc 编译选项（-O2、-static、-mwindows）
- PyInstaller 打包参数（--onefile、--noconsole）
- UPX 压缩、资源文件嵌入、批量打包脚本

**适合人群**：写了个工具想发给 Windows 朋友，但不想让他们看到你的源代码（或者不想让他们看到你用了 50 个第三方库）。

> 🤡 **黑色幽默**：打包后的 exe 文件大小，往往和你的 Python 技术水平成反比。

---

### 4. HTML速查卡.md
**用途**：HTML 标签完全手册（含语义化布局 & 表单）

- 文档基础模板、文本标签、链接、列表、表格
- 图片/视频/音频、语义化布局标签
- 表单（所有 input 类型）、全局属性、HTML 实体

**适合人群**：前端初学者，或者想写个钓鱼页面但忘了 `<input>` 怎么写的“安全专家”。

> 🎣 **友情提醒**：HTML 本身是无辜的，用得好是网页，用不好是“社工”工具。

---

### 5. ip转发.txt
**用途**：ARP 欺骗与 IP 转发（内网中间人攻击）

- 开启 IP 转发
- arpspoof 双向欺骗（手机 ↔ 网关）
- 清除 ARP 缓存恢复网络

**适合人群**：想在内网做流量分析，或者想给室友演示“为什么我的网速突然变慢了”的人。

> ⚠️ **免责声明**：ARP 欺骗在大部分公司是 **开除套餐**，在大部分学校是 **处分套餐**。请在有线网络下使用，Wi-Fi 环境下效果更佳（也更危险）。

---

### 6. JavaScript 安全速成公式卡 .txt
**用途**：JavaScript 语法 + XSS 攻击全流程

- 变量、函数、事件、DOM 操作
- XSS 核心 payload：alert()、document.cookie
- 窃取 Cookie / localStorage、键盘记录、钓鱼弹窗
- 综合 XSS 工具箱（偷 Cookie、偷页面、偷表单、键盘记录）

**适合人群**：想在 DVWA 上体验“黑客”快感，或者写前端时想知道“哪些写法会被 XSS 利用”的人。

> 🔥 **名句**：`<img src=x onerror="alert('XSS')">` 是 Web 安全界的 “Hello World”，只不过它打招呼的方式是弹窗。

---

### 7. java速查卡.md
**用途**：Java 完整语法手册（从入门到 JVM）

- 基础语法、面向对象、集合框架、泛型、异常
- 多线程、JVM 内存结构、类加载机制、反射
- Lambda、Stream API、Optional、NIO
- 常见框架（Spring/MyBatis）速览、性能优化、面试陷阱

**适合人群**：准备 Java 面试的人，或者写 Spring Boot 写到忘了 HashMap 原理的人。

> 💼 **面试铁律**：问 HashMap 原理的，不一定真想考你；但答不上来的，一定过不了。

---

### 8. John Hydra 速查卡 用途 密码破解与爆破.txt
**用途**：John the Ripper（哈希破解）+ Hydra（在线爆破）

- John 破解 MD5/SHA1/NTLM/Linux Shadow
- Hydra 爆破 SSH / FTP / Web 表单 / HTTP Basic
- 字典路径（rockyou.txt）与联合作战

**适合人群**：想测试密码强度的人，或者觉得“123456”是世界上最安全的密码的人。

> 🔐 **破防时刻**：RockYou.txt 里最大的秘密不是密码，而是 **人类对简单密码的执念**。

---

### 9. linux操作.md
**用途**：Linux 命令完整手册（超详细版，含 SSH/Cron/Systemd/firewall）

- 文件操作、权限管理、重定向/管道、搜索
- 进程管理、磁盘/内存、网络命令、文本处理
- Vim、环境变量、压缩解压、软件包管理
- SSH 免密登录 & 端口转发、Cron 定时任务、Systemd 服务管理
- iptables/ufw 防火墙、tmux 终端复用、rsync 备份、tcpdump 抓包

**适合人群**：所有用 Linux 的人——包括那些只在 WSL 里 `ls` 的人。

> 🐧 **Linux 哲学**：当你觉得某个操作很麻烦时，说明你还没找到那个能“一行命令搞定”的工具。通常它已经在 /usr/bin/ 里等你很久了。

---

### 10. Metasploit 速查公式卡 使用方法.txt
**用途**：Metasploit 框架完整使用流程

- 启动、搜索、选择模块、设置参数、攻击
- 永恒之蓝（MS17-010）、Struts2、vsftpd 后门
- Meterpreter 内网渗透（提权、hashdump、键盘记录、截屏）
- 路由添加、横向移动、持久化后门

**适合人群**：想玩 Kali 但被 msfconsole 的 ASCII 艺术吓到的人。

> 🚀 **MSF 三字经**：Search（找武器）、Use（上膛）、Set（瞄准）、Exploit（开火）——比打游戏简单，比打游戏危险。

---

### 11. nmap知识点.md
**用途**：Nmap 完整命令手册（最全版）

- 目标指定、主机发现、端口扫描技术（SYN/ACK/UDP/Null/Xmas）
- 服务版本识别、OS 指纹识别、NSE 脚本引擎
- 防火墙绕过（分片、诱饵、源端口欺骗）
- 速度控制、输出格式、Zenmap 图形界面

**适合人群**：想知道“目标开了哪些端口”的人，以及想搞清楚 `-sS` 和 `-sT` 区别的人。

> 🔎 **Nmap 名言**：不是所有端口都值得扫，但所有端口都应该被扫一遍——至少在你无聊的时候。

---

### 12. ollama指令.txt
**用途**：Ollama 大模型本地部署命令速查

- 拉取模型、运行模型、查看/停止/删除模型
- 自定义模型创建（Modelfile）、API 服务启动
- CUDA 状态查看（nvidia-smi）

**适合人群**：想在本地跑 LLaMA 2 / Mistral / Qwen，但又不想看官方文档的人。

> 🤖 **AI 界的玩笑**：Ollama 让你在本地跑大模型，而跑起来的那个模型，可能还没你聪明——但功耗比你高。

---

### 13. python库.md
**用途**：Python 常用库速查（含安装 & 场景选择）

- 基础库（os/sys/json/re/time/datetime/hashlib）
- 数据科学三件套（numpy/pandas/matplotlib）
- 网络请求（requests/aiohttp）、Web 框架（Flask/FastAPI）
- 数据库（sqlite3/pymongo/redis）、ML/DL（sklearn/torch/transformers）
- 图像（PIL/opencv）、音频（librosa）、中文分词（jieba）

**适合人群**：用 Python 写脚本的人，以及“明明可以用 Shell 却偏要用 Python”的人。

> 🐍 **Python 定律**：你可以用它写 AI、写 Web、写爬虫、写游戏……但最终你 90% 的时间都在 `pip install` 和解决依赖冲突。

---

### 14. python知识点.md
**用途**：Python 完整语法手册（基础 + 进阶）

- 变量/数据类型/运算符/字符串/列表/元组/集合/字典
- 控制流/函数/装饰器/生成器/异常/文件操作
- 类与对象/模块/包/多线程/多进程/asyncio
- 正则/枚举/dataclass/类型注解/pip/虚拟环境
- 性能优化技巧、常见陷阱、项目模板

**适合人群**：想从“会写 Python”变成“真会写 Python”的人。

> 📚 **Python 真谛**：你不需要背下所有语法，你只需要记得“出问题的时候去查速查卡”。

---

### 15. scrcpy 命令大全 + 无线调试大全.txt
**用途**：Android 投屏与无线调试完全指南

- scrcpy 投屏参数（分辨率/码率/帧率/录制）
- 无线调试三种方法（自动/手动/Android 11+配对码）
- ADB 无线连接、快捷键大全（MOD+f 全屏、MOD+w 去黑边）
- 常用 ADB 命令（截屏/录屏/输入/按键模拟）

**适合人群**：想用电脑控制手机的人，以及想“无线调试”但总连不上的人。

> 📱 **无线调试的真相**：当你终于连上手机的那一刻，你发现手机已经没电了。

---

### 16. scrcpy的知识点.txt
**用途**：scrcpy 补充命令（仅 2 条，但超实用）

- `adb shell input text 123456` —— 自动输入密码
- `adb shell input keyevent 26` —— 唤醒屏幕

**适合人群**：懒得在手机上打字的人，或者想写个“自动解锁手机”脚本的人。

> 🔑 **极简主义**：这两条命令，值回整个 README 的阅读时间。

---

### 17. Web 安全三件套 完整公式 靶场 .txt
**用途**：Web 渗透完整攻击链（信息收集 → SQL 注入 → Burp 拦截）

- dirb / gobuster 目录扫描
- sqlmap 自动注入 → `--dbs` → `--tables` → `--dump`
- Burp 抓包改包全流程
- 实战靶场：http://testphp.vulnweb.com

**适合人群**：想体验“一条龙渗透”但不想看 100 页教程的人。

> 🎯 **靶场法则**：在 testphp.vulnweb.com 上你无所不能，在生产环境上你寸步难行——这就是现实。

---

### 18. XSS 完整公式卡 .md
**用途**：XSS 攻击完整手册（初级 → 高级 → 蠕虫）

- 反射型/存储型/DOM 型 XSS 区别
- 初级 Payload（`<script>alert(1)</script>`）
- 中级绕过（大小写/双写/编码/换行/注释）
- 高级绕过（with/eval/setTimeout/模板字符串）
- 窃取 Cookie / localStorage / 键盘记录 / 钓鱼 / 蠕虫
- BeEF 框架使用、CSP 绕过、防御速查

**适合人群**：想在 DVWA 上“弹窗自由”的人，以及想搞懂“为什么输入框不能随便填”的人。

> 💀 **XSS 界的名言**：你永远不知道一个输入框能造成多大的伤害——直到你看到 `document.cookie` 出现在你的服务器日志里。

---

### 19. 歌词获取.txt
**用途**：lrcup 歌词自动下载 & 嵌入音频文件

- `lrcup autosearch --embed --download .` 一键获取歌词
- 批量嵌入歌词到 .flac / .mp3 / .wav 文件
- 带成功/失败提示的批处理脚本

**适合人群**：听歌但不想手动搜歌词的人，或者想把 .lrc 文件塞进音频文件里的“强迫症”用户。

> 🎵 **程序员听歌哲学**：我可以忍受音质差，但绝对不能忍受歌词不同步。

---

### 20. 网络追踪与信息收集速查卡.md
**用途**：网络追踪与信息收集完整手册（含溯源反制）

- 路由追踪（tracert / traceroute / mtr）
- IP 归属查询（whois / ipinfo / ip-api / AbuseIPDB）
- DNS 深度挖掘（dig / nslookup / DNS 历史 / 公共 DNS）
- Whois 反查、端口扫描（nmap / masscan / rustscan）
- 子域名收集（amass / subfinder / crt.sh）
- CDN 绕过、SSL 证书分析、ASN/BGP 查询、威胁情报
- 隐匿与反溯源（代理 / Tor / VPN）

**适合人群**：想搞清楚“流量从哪来、到哪去、中间经过了谁”的人，或者想当“网络侦探”的人。

> 🕵️ **信息收集的本质**：你不是在扫描，你是在画地图。地图画得越细，你想去的地方就越容易到达——无论你想去的是“漏洞”还是“监狱”。

---

### 21. 无线调试控制.txt
**用途**：ADB 手机调试完全命令手册

- 基础连接（USB / 无线 / tcpip）
- 查看设备信息（型号 / 分辨率 / 电池 / CPU）
- 文件传输（push / pull）、应用管理（install / uninstall）
- 模拟操作（点击 / 滑动 / 输入文字 / 按键事件）
- 截图 / 录屏 / 打开 & 强制停止 APP

**适合人群**：想用电脑控制手机的人，或者想写“自动化手机脚本”但不想装任何第三方工具的人。

> 📲 **ADB 的浪漫**：当你用 `adb shell input tap` 点开某个 APP 时，你感受到的不是技术，而是“懒到极致后的创造力”。

---

### 22. 密码字典路径参考（分散在各文件中）

本仓库中虽然没有独立的“字典文件”，但多个速查卡反复提到以下路径：

```bash
/usr/share/wordlists/rockyou.txt.gz      # 经典密码字典（需解压）
/usr/share/wordlists/dirb/common.txt     # Web 目录扫描字典
/usr/share/wordlists/fasttrack.txt       # 常用弱密码
/usr/share/wordlists/metasploit/         # MSF 专用字典
/usr/share/wordlists/dirb/big.txt        # 更大的目录字典
```

解压 rockyou：

```bash
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
```

> 🔓 **一句话点评**：世界上 90% 的密码破解成功，靠的不是算力，而是 **人类对“123456”和“password”的深沉热爱**。

---

## 🧠 使用建议

### 如果你是初学者
- 先从 `linux操作.md` 和 `python知识点.md` 开始
- 再学 `HTML速查卡.md` 和 `JavaScript 安全速成公式卡 .txt`
- 最后挑战 `nmap知识点.md` 和 `Burp Suite sqlmap 速查卡.txt`
- **别急着用 `Metasploit 速查公式卡` 去扫你室友的电脑**——除非你提前写好了解释信。

### 如果你已有基础
- 直接 `Ctrl+F` 搜你忘记的命令
- 把常用命令做成 alias 或脚本
- 记得给自己配置一个 VPN / Tor 环境（保护自己，也保护他人）

### 如果你想进阶
- 结合多个文件打组合拳（如 `nmap` 扫端口 → `sqlmap` 注数据 → `John` 破哈希 → `Hydra` 爆破 SSH）
- 用 `网络追踪与信息收集速查卡.md` 做完整的信息收集链路
- 把 `XSS 完整公式卡` 的 payload 都跑一遍 DVWA

---

## ⚠️ 法律责任声明

**本文档中的所有内容仅供学习和授权安全测试使用。**

未经授权对任何系统进行渗透测试、密码破解、端口扫描、ARP 欺骗、SQL 注入、XSS 攻击等行为，均涉嫌违反 **《中华人民共和国网络安全法》** 及相关法律法规。

**作者不承担任何因使用本文档内容而导致的法律责任。**

> 记住：你的技术应该用来保护系统，而不是破坏它们。

---

## 🙏 致谢

- 所有开源工具的作者（nmap、sqlmap、Burp Suite、Metasploit、John、Hydra、scrcpy、Ollama 等）
- 安全社区的无私分享者
- 所有把密码设成 `123456` 的人（让破解工具显得很厉害）

---