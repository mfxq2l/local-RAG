# Nmap 深度学习与实战手册（完善版）

## 📖 适用人群

- 网络安全学习者 / 渗透测试初学者
- 系统管理员 / 网络工程师
- CTF 玩家 / 安全爱好者
- 想深入理解 Nmap 工作原理的开发者

## ⚠️ 免责声明

**本手册仅供授权安全测试、学习研究使用。** 未经授权扫描他人系统属于违法行为，使用者需自行承担一切法律责任。

## 📑 目录

### 第一部分：基础与安装
- [第一章：Nmap 概述与安装](#第一章nmap-概述与安装)
- [第二章：Nmap 版本与新特性](#第二章nmap-版本与新特性)
- [第三章：Nmap 配置与运行环境](#第三章nmap-配置与运行环境)

### 第二部分：扫描技术全解
- [第四章：Nmap 工作原理](#第四章nmap-工作原理)
- [第五章：扫描生命周期](#第五章扫描生命周期)
- [第六章：主机发现完整对比](#第六章主机发现完整对比)
- [第七章：SCTP / FTP Bounce / IP 协议扫描](#第七章sctp--ftp-bounce--ip-协议扫描)
- [第八章：深入理解 -A 参数](#第八章深入理解--a-参数)

### 第三部分：指纹识别
- [第九章：服务版本检测原理](#第九章服务版本检测原理)
- [第十章：操作系统指纹原理](#第十章操作系统指纹原理)
- [第十一章：扫描结果深度分析](#第十一章扫描结果深度分析)

### 第四部分：NSE 引擎
- [第十二章：NSE 深入](#第十二章nse-深入)
- [第十三章：NSE 库详解与脚本调试](#第十三章nse-库详解与脚本调试)
- [第十四章：NSE 高级开发](#第十四章nse-高级开发)

### 第五部分：隐蔽与绕过
- [第十五章：IDS/IPS 绕过进阶](#第十五章idsips-绕过进阶)

### 第六部分：自动化与集成
- [第十六章：自动化扫描与开发](#第十六章自动化扫描与开发)
- [第十七章：输出解析与报告生成](#第十七章输出解析与报告生成)
- [第十八章：第三方工具集成](#第十八章第三方工具集成)

### 第七部分：实战与防御
- [第十九章：真实渗透流程](#第十九章真实渗透流程)
- [第二十章：云环境与合规](#第二十章云环境与合规)
- [第二十一章：防御视角](#第二十一章防御视角)
- [第二十二章：IPv6 专项](#第二十二章ipv6-专项)
- [第二十三章：性能调优](#第二十三章性能调优)
- [第二十四章：常见错误排查](#第二十四章常见错误排查)
- [第二十五章：学习路线](#第二十五章学习路线)

### 第八部分：命令速查
- [一、目标指定](#一目标指定)
- [二、主机发现](#二主机发现找谁在线)
- [三、端口扫描](#三端口扫描看开了哪些门)
- [四、扫描技术](#四扫描技术怎么扫)
- [五、服务与系统识别](#五服务与系统识别扒信息)
- [六、脚本扫描](#六脚本扫描nse-引擎核心功能)
- [七、速度与性能](#七速度与性能快慢自己调)
- [八、防火墙绕过](#八防火墙绕过隐身技巧)
- [九、输出格式](#九输出格式保存结果)
- [十、常用组合拳](#十常用组合拳实战套路)
- [十一、端口状态解读](#十一端口状态解读)
- [十二、扫描类型对比](#十二扫描类型对比快速参考)
- [十三、NSE 脚本类别大全](#十三nse-脚本类别大全)
- [十四、Zenmap](#十四zenmap图形界面)
- [十五、常用参数速记表](#十五常用参数速记表)
- [常见错误速查](#-常见错误速查)


# 第一部分：基础与安装

## 第一章：Nmap 概述与安装

### 1.1 Nmap 是什么

Nmap（Network Mapper）是最流行的开源网络发现和安全审计工具，由 Gordon Lyon（Fyodor）于 1997 年发布。其核心能力包括：主机发现、端口扫描、服务/版本检测、操作系统识别、NSE 脚本引擎。

Nmap 是有状态扫描器，它管理 TCP 连接的完整生命周期或跟踪探测-响应对的状态，以确保最大的准确性。与无状态扫描器（如 Masscan）不同，Nmap 为每个探测维护套接字状态，使其能够执行操作系统指纹识别、服务版本检测（-sV）以及通过 NSE 进行漏洞扫描等复杂任务。

### 1.2 Linux 安装

```bash
# Debian / Ubuntu / Kali
sudo apt update
sudo apt install nmap

# RHEL / CentOS / Fedora
sudo yum install nmap
# 或
sudo dnf install nmap

# Arch
sudo pacman -S nmap

# openSUSE
sudo zypper install nmap

# 验证
nmap --version
```

### 1.3 Windows 安装

方式一：官方安装程序

访问 `https://nmap.org/download#windows` 下载最新稳定版安装程序。运行安装程序时，会自动安装 Npcap（Windows 下的抓包驱动），务必勾选。

方式二：包管理器

```powershell
# winget
winget install Insecure.Nmap

# Chocolatey
choco install nmap
```

### 1.4 macOS 安装

```bash
# Homebrew（推荐）
brew install nmap

# MacPorts
sudo port install nmap
```

### 1.5 源码编译安装

```bash
# 下载源码
wget https://nmap.org/dist/nmap-7.96.tar.bz2
tar -xjf nmap-7.96.tar.bz2
cd nmap-7.96

# 配置编译
./configure --prefix=/usr/local
make -j$(nproc)
sudo make install

# 更新脚本数据库
sudo nmap --script-updatedb
```

### 1.6 Docker 中使用 Nmap

```bash
# 拉取镜像
docker pull securecodebox/nmap

# 运行（需要 NET_RAW 权限）
docker run --rm --cap-add=NET_RAW --cap-add=NET_ADMIN \
    securecodebox/nmap -sS 192.168.1.1
```

> ⚠️ 注意：容器默认缺少 `CAP_NET_RAW` 和 `CAP_NET_ADMIN`，无法进行 SYN 扫描和 OS 检测。

### 1.7 免 sudo 运行 SYN 扫描

```bash
# 方法一：设置 capability（推荐）
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap

# 验证
getcap /usr/bin/nmap

# 方法二：添加到 sudoers
sudo visudo
# 添加：username ALL=(root) NOPASSWD: /usr/bin/nmap
```

### 1.8 Nmap 配置文件位置

| 平台 | 配置目录 |
|------|---------|
| Linux | `/usr/share/nmap/` |
| macOS | `/usr/local/share/nmap/` |
| Windows | `C:\Program Files (x86)\Nmap\` |

关键数据文件：

- `nmap-service-probes` — 服务指纹库
- `nmap-os-db` — 操作系统指纹库
- `nmap-services` — 端口服务映射
- `nmap-payloads` — UDP 扫描载荷
- `nmap-rpc` — RPC 程序映射
- `nmap-mac-prefixes` — MAC 厂商前缀
- `nselib/` — NSE 库目录
- `scripts/` — NSE 脚本目录

### 1.9 更新脚本和数据库

```bash
sudo nmap --script-updatedb    # 更新 NSE 脚本数据库
sudo nmap --iflist             # 列出可用网络接口
nmap -e eth0 ...               # 指定网络接口
nmap --send-eth ...            # 使用以太网帧发送
nmap --send-ip ...             # 使用 IP 包发送
```


## 第二章：Nmap 版本与新特性

### 2.1 Nmap 7.x 主要版本演进

| 版本 | 发布日期 | 主要特性 |
|------|---------|----------|
| 7.00 | 2015-11 | NSE 大规模扩展、成熟 IPv6 支持、SSL/TLS 扫描、Ncat 增强 |
| 7.40 | 2016-12 | SCTP 扫描支持（-sY/-sZ）、默认主机发现优化 |
| 7.80 | 2019-08 | 新增大量 NSE 脚本、Zenmap 改进 |
| 7.91 | 2020-10 | 脚本库更新、性能优化 |
| 7.92 | 2021-08 | 兼容性修复、新增脚本 |
| 7.94 | 2022-11 | 服务指纹库更新 |
| 7.95 | 2024-09 | SNMP 指纹更精确、UDP 端口评估改进 |
| 7.96 | 2025-05 | 并行 DNS 解析（百万域名从 49 小时到 1 小时）、Zenmap 暗黑模式、 |
| 7.98 | 2025-08 | 修复 FTP Bounce 缓冲区溢出、DNS 递归处理崩溃、TCP Connect 扫描问题 |

### 2.2 Nmap 7.96 重点改进

- **并行 DNS 解析**：Nmap 现在并行执行正向 DNS 查询，100 万个域名的解析时间从约 49 小时降至约 1 小时
- **新增默认连接关闭模式**：更安全地处理连接关闭
- **新增 `-q` 选项**：延迟程序退出，给用户时间查看错误信息
- **Zenmap 暗黑模式**：图形界面新增主题选项
- **修复 TCP 端口扫描误报**：修正了将开放端口错误标记为 filtered 的问题

### 2.3 版本升级建议

```bash
# 检查当前版本
nmap --version

# 查看更新日志
# https://nmap.org/changelog.html

# 新版优势
# - 更快的扫描速度
# - 更新的 OS 和服务指纹库（提升识别准确率）
# - 修复已知 bug
# - 新增 NSE 脚本

# 升级后务必更新脚本数据库
sudo nmap --script-updatedb
```


## 第三章：Nmap 配置与运行环境

### 3.1 网络接口管理

```bash
# 查看所有可用接口
nmap --iflist

# 输出示例：
# DEV  (SHORT)  IP/MASK              TYPE     UP MTU   MAC
# eth0 (eth0)   192.168.1.100/24     ethernet up 1500  00:11:22:33:44:55
# lo   (lo)     127.0.0.1/8          loopback up 65536
# wlan0(wlan0)  10.0.0.50/24         ethernet up 1500  aa:bb:cc:dd:ee:ff

# 指定接口扫描
nmap -e eth0 192.168.1.1

# 指定发送方式
nmap --send-eth 192.168.1.1   # 使用以太网帧（默认局域网）
nmap --send-ip 192.168.1.1    # 使用 IP 包（默认远程）
```

### 3.2 DNS 配置

```bash
nmap -n 192.168.1.1            # 不解析 DNS（加速扫描）
nmap -R 192.168.1.1            # 强制反向解析所有 IP
nmap --system-dns 192.168.1.1  # 使用系统 DNS 解析器
nmap --dns-servers 8.8.8.8 192.168.1.1  # 指定 DNS 服务器
```

### 3.3 权限要求汇总

| 扫描类型 | 是否需要 root | 原因 |
|---------|-------------|------|
| `-sS` SYN 扫描 | ✅ 需要 | 原始套接字 |
| `-sT` 全连接扫描 | ❌ 不需要 | 使用系统 connect() |
| `-sU` UDP 扫描 | ✅ 需要 | 原始套接字 |
| `-O` OS 检测 | ✅ 需要 | 原始套接字 |
| `-sA/-sN/-sF/-sX` | ✅ 需要 | 原始套接字 |
| `-sV` 版本检测 | ❌ 不需要 | 使用普通连接 |
| `--script` NSE | 视脚本而定 | 部分需要原始套接字 |

### 3.4 环境变量

```bash
# 设置 Nmap 数据目录
export NMAPDIR=~/.nmap

# 设置脚本搜索路径
export NSE_Script_Path=/custom/scripts/
```


# 第二部分：扫描技术全解

## 第四章：Nmap 工作原理

### 4.1 TCP SYN 扫描原理（-sS）

这是 Nmap 默认且最常用的扫描方式。

```
客户端（你）                    目标服务器

   |--- SYN 包 ---------------->|
   |                             |
   |<--- SYN/ACK 包 ------------|   ← 端口开放
   |                             |
   |--- RST 包 ---------------->|   ← 立即关闭连接（不完成握手）
   |                             |
```

**为什么不完成三次握手？** 正常 TCP 连接：`SYN → SYN/ACK → ACK`；SYN 扫描：`SYN → SYN/ACK → RST`。好处是**不建立完整连接**，目标应用层不会记录日志，更隐蔽。

**结果判断：**

| 响应 | 端口状态 | 说明 |
|------|----------|------|
| SYN/ACK | `open` | 端口开放，有服务监听 |
| RST | `closed` | 端口关闭，无服务 |
| 无响应（超时） | `filtered` | 被防火墙/IDS 丢弃 |
| ICMP 不可达 | `filtered` | 被防火墙拒绝 |

### 4.2 TCP 全连接扫描原理（-sT）

```
SYN -------->
     <------ SYN/ACK
ACK -------->
     <------ 数据/关闭
```

完成完整的 TCP 三次握手。优点：不需要 root 权限。缺点：目标会记录完整连接日志，容易被发现。

### 4.3 UDP 扫描原理（-sU）

UDP 是无连接协议，扫描方式不同。发送 UDP 包到目标端口：**开放**收到 UDP 响应（如 DNS 返回数据）；**关闭**收到 ICMP 端口不可达（Type 3, Code 3）；**过滤**无响应或 ICMP 被拦截。UDP 扫描慢且不可靠，因为 UDP 可能丢包。

### 4.4 隐秘扫描系列（NULL / FIN / Xmas）

| 扫描类型 | 发送的包 | 开放端口响应 | 关闭端口响应 |
|----------|----------|--------------|--------------|
| `-sN` NULL | 不设置任何标志位 | 无响应 | RST |
| `-sF` FIN | 只设置 FIN 标志 | 无响应 | RST |
| `-sX` Xmas | FIN+PSH+URG 全亮 | 无响应 | RST |

> 💡 **原理**：RFC 规定，收到无效标志组合的包，如果端口关闭应回复 RST；如果端口开放则忽略（不回复）。所以**无响应 = open/filtered**，RST = closed。

### 4.5 TCP ACK 扫描原理（-sA）

发送 ACK 包（不是 SYN），不管端口开/关都会返回 RST。目的不是判断端口开放，而是**探测防火墙规则**。如果收到 RST → 端口未被过滤（`unfiltered`）；如果无响应 → 端口被过滤（`filtered`）。

### 4.6 TCP 窗口扫描（-sW）与 Maimon 扫描（-sM）

**窗口扫描（-sW）** ：利用 TCP 窗口字段的差异来判断端口状态。当收到 RST 时，某些系统会返回不同的窗口大小来指示端口是开放还是关闭。在大多数系统上不可靠。

**Maimon 扫描（-sM）** ：发送 FIN+ACK 包。根据 RFC 793，关闭端口应回复 RST，开放端口应忽略。但许多系统（尤其是 Windows）不遵循此规范，因此该扫描主要对某些 Unix 系统有效。

### 4.7 空闲扫描原理（-sI）

空闲扫描（Idle Scan）是最隐蔽的扫描方式，利用僵尸主机的 IP ID 递增特性：

```
步骤1：探测僵尸机的 IP ID 当前值（发送 SYN/ACK，读取响应中的 IP ID）
步骤2：伪造僵尸机的源 IP，向目标发送 SYN 包
步骤3：再次探测僵尸机的 IP ID，如果增加 ≥ 2，说明目标端口开放
```

**僵尸机条件**：空闲、IP ID 全局递增（非随机）。查找僵尸机：`nmap --script=ipidseq`。空闲扫描的好处是**完全隐藏真实源 IP**——目标只会看到僵尸机的 IP。

### 4.8 TCP 扫描技术对比

| 扫描类型 | 参数 | 标志位 | 需要 root | 适用场景 |
|----------|------|--------|----------|----------|
| SYN 扫描 | `-sS` | SYN | ✅ | 通用（默认） |
| 全连接 | `-sT` | SYN/ACK | ❌ | 无 root 时 |
| ACK 扫描 | `-sA` | ACK | ✅ | 探测防火墙 |
| 窗口扫描 | `-sW` | ACK | ✅ | 特定系统 |
| Maimon | `-sM` | FIN/ACK | ✅ | 特定 Unix |
| NULL | `-sN` | 无 | ✅ | 绕过无状态防火墙 |
| FIN | `-sF` | FIN | ✅ | 绕过无状态防火墙 |
| Xmas | `-sX` | FIN+PSH+URG | ✅ | 绕过无状态防火墙 |


## 第五章：扫描生命周期

实际渗透测试中，Nmap 扫描是按阶段推进的：

```
┌─────────────────────────────────────────────────────────┐
│                    1. 目标指定                          │
│         (单个IP / IP段 / 域名 / 文件导入)              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    2. 主机发现                         │
│    (判断哪些主机在线，避免扫离线设备浪费时间)           │
│    -sn / -PE / -PR (ARP) / -Pn (跳过)                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    3. 端口扫描                         │
│    (发现开放端口，找到攻击面)                          │
│    -sS / -sT / -sU / -p-                              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    4. 服务/版本识别                     │
│    (确认端口上跑的是什么软件、什么版本)                 │
│    -sV                                                │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    5. 操作系统识别                      │
│    (判断目标是什么系统，方便后续针对性攻击)             │
│    -O                                                 │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    6. NSE 脚本扫描                     │
│    (漏洞检测、信息枚举、暴力破解等)                     │
│    --script=vuln / --script=default                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    7. 结果输出与分析                    │
│    -oN / -oX / -oG / 人工分析 + 报告生成              │
└─────────────────────────────────────────────────────────┘
```


## 第六章：主机发现完整对比

### 6.1 主机发现技术对比表

| 技术 | 参数 | 发送的包 | 需要 root | 适用场景 |
|------|------|---------|----------|----------|
| ARP Ping | `-PR` | ARP 请求 | ❌ | **局域网最准** |
| ICMP Echo | `-PE` | ICMP Echo | ✅ | 跨网段 |
| ICMP Timestamp | `-PP` | ICMP 时间戳 | ✅ | ICMP 被过滤时 |
| ICMP Netmask | `-PM` | ICMP 地址掩码 | ✅ | 特定网络 |
| TCP SYN Ping | `-PS` | TCP SYN | ✅ | 绕过 ICMP 封锁 |
| TCP ACK Ping | `-PA` | TCP ACK | ✅ | 绕过无状态防火墙 |
| UDP Ping | `-PU` | UDP 包 | ✅ | UDP 服务探测 |
| SCTP INIT Ping | `-PY` | SCTP INIT | ✅ | SCTP 网络 |
| IP 协议 Ping | `-PO` | IP 包 | ✅ | 非 TCP/UDP 协议 |

### 6.2 Nmap 默认主机发现策略

Nmap 4.85BETA10 起，默认主机发现使用四探针组合 `-PE -PS443 -PA80 -PP`，比之前的 `-PE -PA80` 多发现 14% 的互联网主机。非 root 用户默认使用 `-PS80,443`。ARP Ping 在本地以太网仍是默认方式。

### 6.3 IPv6 主机发现

IPv6 环境下，`-PR` 使用 ICMPv6 Neighbor Discovery 代替 ARP。Nmap 通常对本地以太网连接的主机执行 ARP 或 IPv6 Neighbor Discovery 发现。IPv6 扫描始终使用系统解析器。

```bash
nmap -6 -sn 2001:db8::/64        # IPv6 主机发现
nmap -6 -PR 2001:db8::1          # ICMPv6 Neighbor Discovery
```


## 第七章：SCTP / FTP Bounce / IP 协议扫描

### 7.1 SCTP 扫描（-sY / -sZ）

SCTP（流控制传输协议）是用于电话相关应用的第四层协议。Nmap 7.40 起支持 SCTP 扫描。

```bash
# SCTP INIT 扫描（-sY）：相当于 TCP SYN 扫描
# 开放端口返回 INIT-ACK，关闭端口返回 ABORT
nmap -sY 192.168.1.1
nmap -sY -p 7,9,20,21,22,80,179,443,1021,2049,2225,2905,3097,3863,3864,3868,5090,5091,5215,6704,6705,6706,7626,8471,9082,9084,9900,9901,9902,10023,11161,11162,11163,11164,11165,11166,11167,11168,11169,11170,11171,11172,11173,11174,11175,11176,11177,11178,11179,11180,11181,11182,11183,11184,11185,11186,11187,11188,11189,11190,11191,11192,11193,11194,11195 192.168.1.1

# SCTP COOKIE-ECHO 扫描（-sZ）：开放端口静默，关闭端口返回 ABORT
nmap -sZ 192.168.1.1

# SCTP 主机发现
nmap -PY 192.168.1.1

# SCTP 专用 IP 协议扫描
nmap -sO -p sctp 192.168.1.1

# SCTP 路由追踪
nmap -sY --traceroute 192.168.1.1

# 使用 Adler32 算法（RFC 2960，已弃用但兼容旧设备）
nmap -sY --adler32 192.168.1.1

# 测试目标（官方 SCTP 测试服务器）
nmap -sY scanme.csnc.ch --reason
nmap -sZ scanme.csnc.ch --reason
```

> ⚠️ SCTP 不通过大多数 NAT 设备，扫描公网 SCTP 服务可能受限。

### 7.2 FTP Bounce 扫描（-b）

FTP Bounce 扫描利用 FTP 服务器的 PORT 命令，让 FTP 服务器代替攻击者扫描目标。这是一种非常隐蔽的扫描方式，因为流量来自 FTP 服务器而非攻击者。

```bash
# 基本用法：通过 FTP 服务器扫描目标
nmap -b ftp-server 目标IP
nmap -b anonymous@ftp.example.com 192.168.1.1

# 指定 FTP 端口
nmap -b ftp.example.com:2121 192.168.1.1

# 通过 FTP 服务器扫描多个端口
nmap -b ftp.example.com -p 21,22,80,443 192.168.1.1
```

**适用条件**：FTP 服务器允许匿名登录、允许 PORT 命令、允许连接到任意 IP/端口。现代 FTP 服务器大多已禁用此功能。

### 7.3 IP 协议扫描（-sO）

IP 协议扫描用于确定目标主机支持哪些 IP 协议（TCP、UDP、ICMP、IGMP、GRE、ESP、AH、SCTP 等）。

```bash
# 扫描所有 IP 协议
nmap -sO 192.168.1.1

# 扫描特定协议
nmap -sO -p 1,6,17,47,50,51,132 192.168.1.1

# 输出示例：
# PROTOCOL  STATE  SERVICE
# 1         open   icmp
# 6         open   tcp
# 17        open   udp
# 47        open   gre
# 50        open   esp
# 51        open   ah

# 结合 SCTP 协议扫描
nmap -sO -p sctp 192.168.1.1
```

**使用场景**：探测非常规协议（GRE、ESP、AH），发现 VPN 或隧道服务；判断防火墙对非 TCP/UDP 协议的处理策略。


## 第八章：深入理解 -A 参数

```bash
nmap -A 192.168.1.1
```

很多人管它叫“全家桶”，它到底包含什么？

| 组件 | 等效参数 | 说明 |
|------|----------|------|
| 服务版本检测 | `-sV` | 识别端口上的服务及版本 |
| 操作系统检测 | `-O` | 猜测目标操作系统 |
| 默认脚本 | `--script=default` | 运行 NSE 默认安全脚本 |
| 路由追踪 | `--traceroute` | 显示到达目标的网络路径 |

**什么时候用 `-A`？**

- ✅ 信息收集阶段，想快速获取目标全貌
- ✅ 目标少（1~3 个），不担心流量大
- ❌ 大批量扫描（整个网段）→ 太慢
- ❌ 需要隐蔽扫描 → 流量特征太明显


# 第三部分：指纹识别

## 第九章：服务版本检测原理

### 9.1 检测机制

服务版本检测使用 `nmap-service-probes` 数据库，该文件包含 Nmap 在端口探测期间用于确定端口上监听程序的探测包和匹配表达式。

工作流程：

1. Nmap 向开放端口发送一系列探测包（Probe）
2. 接收服务响应
3. 将响应与数据库中的匹配规则（match）进行比对
4. 识别服务名称、版本、额外信息

### 9.2 数据库文件结构

`nmap-service-probes` 文件的关键指令：

```
# Probe 指令：定义探测包
Probe UDP DNSStatusRequest q|\0\0\x10\0\0\0\0\0\0\0\0\0| ports 53,135

# match 指令：匹配响应
match domain m|^\0\0\x90\x04\0\0\0\0\0\0\0\0|

# 软匹配（softmatch）：仅用于识别服务类型
softmatch http m|^HTTP/1\.[01]|

# 端口注册
ports 80,443
```

`Probe` 指令告诉 Nmap 发送什么字符串来识别各种服务，`match` 指令用于解析响应。

### 9.3 版本强度

```bash
# 强度 0-9，默认 7
nmap -sV --version-intensity 0 192.168.1.1   # 最轻量（最快，可能不准）
nmap -sV --version-intensity 9 192.168.1.1   # 最重量（最准，最慢）

# 快捷方式
nmap -sV --version-light 192.168.1.1         # 等价于 intensity 2
nmap -sV --version-all 192.168.1.1           # 等价于 intensity 9

# 显示探测过程
nmap -sV --version-trace 192.168.1.1

# 扫描所有端口（不仅开放端口）
nmap -sV --allports 192.168.1.1

# 显示版本数据库统计
nmap --versiondb
```

### 9.4 服务指纹提交

当 Nmap 收到服务响应但无法匹配数据库时，会打印特殊指纹和提交 URL。如果你确认端口上运行的是什么服务，可以提交指纹帮助完善数据库。


## 第十章：操作系统指纹原理

### 10.1 TCP/IP 栈指纹技术

Nmap 最著名的功能之一是使用 TCP/IP 栈指纹进行远程 OS 检测。Nmap 向远程主机发送一系列 TCP 和 UDP 数据包，检查响应中的几乎每一位信息。执行数十项测试后，Nmap 将结果与其 `nmap-os-db` 数据库中超过 2600 个已知 OS 指纹进行比较，如果匹配则输出 OS 详情。

### 10.2 关键指纹特征

Nmap 检测的 TCP/IP 特征包括：

| 特征 | 说明 |
|------|------|
| TCP ISN 采样 | 初始序列号生成模式（递增/随机/时间相关） |
| TCP 选项支持 | 支持的 TCP 选项及顺序 |
| IP ID 采样 | IP 头中 ID 字段的生成模式 |
| 初始窗口大小 | TCP 窗口字段的初始值 |
| TTL 值 | IP 生存时间 |
| DF 位 | 不分片标志 |
| TCP 时间戳 | 时间戳选项的行为 |

### 10.3 OS 指纹数据库

每个指纹包含：操作系统的自由文本描述；提供厂商名称（如 Sun）、底层 OS（如 Solaris）、OS 代次（如 10）和设备类型（通用、路由器、交换机、游戏主机等）的分类；大多数指纹还有 Common Platform Enumeration（CPE）表示。

### 10.4 OS 匹配算法

Nmap 的匹配算法相对简单：将目标指纹与 `nmap-os-db` 中的每个参考指纹逐一测试，每个通过的测试获得一定分数。OS 匹配 90% 意味着获得了 90% 的分数。每个测试的分数定义在 `nmap-os-db` 的 MatchPoints 结构中。

### 10.5 附带信息

OS 检测还能启用一些额外测试：

- **TCP 序列可预测性分类**：衡量建立伪造 TCP 连接的难度，对于利用基于源 IP 的信任关系（rlogin、防火墙规则）有用。在 `-v` 模式下报告
- **IP ID 序列生成**：大多数机器属于“增量”类，容易受到高级信息收集和欺骗攻击。在 `-O -v` 模式下报告
- **目标运行时间推测**：使用 TCP 时间戳选项猜测机器上次重启时间，仅在 verbose 模式下打印

### 10.6 OS 检测控制参数

```bash
nmap -O 192.168.1.1                    # 基本 OS 检测
nmap -O --osscan-limit 192.168.1.1     # 仅对满足条件的主机扫描
nmap -O --osscan-guess 192.168.1.1     # 大胆猜测（同 --fuzzy）
nmap -O --max-os-tries 3 192.168.1.1   # 最大尝试次数
nmap -O -v 192.168.1.1                 # 显示额外信息
```


## 第十一章：扫描结果深度分析

### 11.1 真实案例分析

假设扫描输出：

```
PORT     STATE    SERVICE     VERSION
22/tcp   open     ssh         OpenSSH 7.4 (protocol 2.0)
80/tcp   open     http        nginx 1.14.0
443/tcp  filtered https       ?
3306/tcp closed   mysql       ?
```

**分析思路：**

| 端口 | 状态 | 分析 | 下一步动作 |
|------|------|------|------------|
| 22 | open | SSH 暴露在外，版本 OpenSSH 7.4 | 查 CVE，尝试弱密码爆破 |
| 80 | open | nginx 1.14.0 | Web 目录枚举，查看网页标题 |
| 443 | filtered | HTTPS 被防火墙过滤 | 可能只对内网开放 |
| 3306 | closed | MySQL 未监听 | 可能在内网其他机器上 |

### 11.2 端口状态解读

| 状态 | 含义 | 实际意义 |
|------|------|----------|
| `open` | 端口开放，有服务监听 | 可尝试连接、爆破、漏洞利用 |
| `closed` | 端口关闭，无服务 | 但主机在线，可尝试其他端口 |
| `filtered` | 被防火墙/IDS 过滤 | 尝试用 `-sS -f -D` 绕过 |
| `unfiltered` | 能到达但不确定开/关 | ACK 扫描特有，需进一步确认 |
| `open\|filtered` | 开放或被过滤 | UDP 扫描常见，需其他方式验证 |

### 11.3 使用 --reason 显示判断依据

```bash
nmap --reason 192.168.1.1
# 输出示例：
# PORT   STATE SERVICE REASON
# 22/tcp open  ssh     syn-ack
# 80/tcp open  http    syn-ack
# 443/tcp filtered https no-response
```


# 第四部分：NSE 引擎

## 第十二章：NSE 深入

### 12.1 NSE 工作流程

```
Nmap 扫描发现开放端口
        ↓
识别端口上的服务（-sV）
        ↓
根据服务匹配可用脚本
        ↓
按类别/名称执行选中的 Lua 脚本
        ↓
收集脚本返回的结果
        ↓
整合输出到扫描报告
```

### 12.2 NSE 脚本类别说明

| 类别 | 说明 | 使用场景 | 风险 |
|------|------|----------|------|
| `default` | 默认脚本，安全快速 | 通用扫描 | 低 |
| `safe` | 不会 crash 目标 | 生产环境 | 低 |
| `discovery` | 服务发现/信息枚举 | 信息收集 | 中 |
| `vuln` | 漏洞检测 | 安全评估 | 中 |
| `exploit` | 漏洞利用 | 渗透测试 | 高 |
| `brute` | 暴力破解 | 弱密码检测 | 高 |
| `dos` | DoS 攻击 | 仅授权测试 | 极高 |
| `intrusive` | 侵入式 | 可能影响目标 | 高 |
| `malware` | 检测恶意软件 | 安全分析 | 中 |
| `external` | 调用外部 API | 信息收集 | 中（可能泄露） |
| `fuzzer` | 模糊测试 | 漏洞发现 | 高 |
| `auth` | 认证相关 | 弱密码检测 | 中 |
| `broadcast` | 广播发现 | 局域网 | 低 |

### 12.3 脚本执行顺序

NSE 脚本的执行顺序由规则类型决定：

1. **prerule** — 在扫描之前执行（如广播发现）
2. **hostrule** — 针对每个主机执行
3. **portrule** — 针对每个开放端口执行
4. **postrule** — 在扫描完成后执行

### 12.4 脚本选择与通配符

```bash
# 精确脚本名
nmap --script=http-title 目标

# 通配符
nmap --script="smb-*" 目标          # 所有 smb- 开头脚本
nmap --script="http-*,smb-*" 目标   # 多个通配符

# 类别
nmap --script=discovery 目标
nmap --script="default or safe" 目标

# 排除类别
nmap --script="not intrusive" 目标

# 组合表达式
nmap --script="http-* and not http-brute" 目标
```


## 第十三章：NSE 库详解与脚本调试

### 13.1 核心 NSE 库

NSE 脚本可以调用丰富的库来简化开发。常用库包括：

| 库名 | 用途 | 关键函数 |
|------|------|----------|
| `nmap` | 基础功能 | `new_socket()`、`get_timeout()`、`set_timeout()` |
| `http` | HTTP 请求 | `http.get()`、`http.post()`、`http.pipeline()` |
| `smb` | SMB 协议 | `smb.start_session()`、`smb.list_shares()` |
| `ssh2` | SSH 协议 | `ssh2.connect()`、`ssh2.auth_password()` |
| `ssl` | SSL/TLS | `ssl.connect()`、`ssl.get_certificate()` |
| `dns` | DNS 查询 | `dns.query()`、`dns.reverse()` |
| `mysql` | MySQL | `mysql.connect()`、`mysql.query()` |
| `pgsql` | PostgreSQL | `pgsql.connect()` |
| `mongodb` | MongoDB | `mongodb.connect()` |
| `stdnse` | 标准工具 | `stdnse.format_output()`、`stdnse.get_script_args()` |
| `comm` | 通信 | `comm.exchange()`、`comm.tryssl()` |
| `bin` | 二进制处理 | `bin.pack()`、`bin.unpack()` |

### 13.2 脚本参数传递

```bash
# 基本用法
nmap --script=smb-enum-shares --script-args smbuser=admin,smbpass=secret 192.168.1.1

# 从文件读取参数
nmap --script=xxx --script-args-file=args.txt 目标

# 查看脚本帮助
nmap --script-help=http-title
nmap --script-help="smb-*"

# 脚本中使用参数
# 在 Lua 脚本中：
# local user = stdnse.get_script_args("smb-enum-shares.smbuser")
# 或
# local user = stdnse.get_script_args(SCRIPT_NAME .. ".smbuser")
```

### 13.3 NSE 脚本调试

有两种调试 NSE 脚本的方法：

```bash
# 方法一：--script-trace 显示脚本收发的通信
nmap --script-trace --script=http-title 192.168.1.1

# 方法二：-d[0-9] 增加调试信息级别
nmap -d --script=http-title 192.168.1.1    # 调试级别 1
nmap -d3 --script=http-title 192.168.1.1   # 调试级别 3
nmap -d9 --script=http-title 192.168.1.1   # 调试级别 9（最详细）
```

在脚本中使用调试输出：

```lua
-- 详细模式输出
stdnse.verbose(2, "当 verbosity 级别 > 1 时打印")
stdnse.verbose2("同上")

-- 调试输出
stdnse.debug(2, "当 debug 级别 > 1 时打印")
stdnse.debug2("同上")
```

### 13.4 NSE 数据文件

如果脚本需要从数据库文件读取信息，文件应放在 `nselib/data/` 目录中。可以用 `nmap.fetchfile(filename)` 验证文件在 Nmap 搜索路径中是否可读。

### 13.5 NSE 注册表

`nmap.registry` 是一个 Lua 表，用于在扫描期间在所有脚本之间共享变量：

```lua
-- 写入
nmap.registry.credentials.http = { username = "admin", password = "pass" }

-- 读取
local creds = nmap.registry.credentials.http
```


## 第十四章：NSE 高级开发

### 14.1 NSE 脚本完整结构

```lua
local nmap = require "nmap"
local stdnse = require "stdnse"
local http = require "http"
local shortport = require "shortport"

description = [[
检测目标 HTTP 服务并获取标题。
]]

author = "Your Name"
license = "Same as Nmap--See https://nmap.org/book/man-legal.html"
categories = {"discovery", "safe"}

-- 端口规则：只在 HTTP 端口执行
portrule = shortport.http

-- 主执行函数
action = function(host, port)
    local response = http.get(host, port, "/")
    if response and response.status then
        local title = response.body:match("<title>(.-)</title>")
        if title then
            return "页面标题: " .. title
        end
        return "HTTP 状态码: " .. response.status
    end
    return nil
end
```

### 14.2 异常处理

```lua
-- 使用 pcall 保护可能出错的调用
local status, result = pcall(function()
    return http.get(host, port, "/")
end)

if not status then
    stdnse.debug1("HTTP 请求失败: %s", result)
    return nil
end
```

### 14.3 返回结构化结果

```lua
action = function(host, port)
    local result = stdnse.output_table()
    result["服务"] = "HTTP"
    result["版本"] = "nginx/1.14.0"
    result["标题"] = "Welcome"
    return result
end
```

### 14.4 脚本发布

开发完成后，可以将脚本提交到 Nmap 官方仓库。需要遵循 Nmap 脚本开发规范，包括代码风格、文档注释、测试用例等。


# 第五部分：隐蔽与绕过

## 第十五章：IDS/IPS 绕过进阶

### 15.1 TTL 操纵

发送 TTL 恰好到达 IDS/IPS 但不足以到达最终系统的数据包，然后发送具有相同序列号的另一组数据包，让 IPS/IDS 认为它们是重复的而不检查，但实际上这些包携带恶意内容。Nmap 选项：`--ttl <value>`。

### 15.2 绕过签名检测

向数据包添加随机数据，使固定的 IPS/IDS 签名不太可能匹配。Nmap 选项：`--data-length 25`。

### 15.3 分片数据包

将数据包分片发送。如果 IDS/IPS 没有重组能力，分片将到达最终主机。如果 IDS/IPS 没有正确地重组所有分片并分析，包含恶意特征的完整字节流可能不会在单个数据包中出现，从而绕过基于签名的检测。Nmap 选项：`-f` 或 `--mtu 8`（必须是 8 的倍数）。

```bash
nmap -f 192.168.1.1                 # 分片
nmap -f --mtu 32 192.168.1.1        # 指定 MTU
```

### 15.4 无效校验和

某些防火墙和 IDS 可能不验证校验和。攻击者可以发送一个被传感器解释但被最终主机拒绝的数据包。例如：发送带 RST 标志和无效校验和的数据包，IPS/IDS 可能认为这会关闭连接，但最终主机会因校验和无效而丢弃。

```bash
nmap --badsum 192.168.1.1
```

### 15.5 不常见的 IP 和 TCP 选项

传感器可能忽略设置了某些标志和选项的 IP/TCP 头数据包，而目标主机会接受。Nmap 支持 `--data`、`--data-string`、`--data-length` 等选项来添加自定义数据。

### 15.6 诱饵与欺骗

```bash
# 诱饵扫描：RND:5 表示随机 5 个诱饵，ME 表示真实 IP 的位置
nmap -D RND:5,ME 192.168.1.1
nmap -D 192.168.1.2,192.168.1.3,ME 192.168.1.1

# MAC 地址欺骗
nmap --spoof-mac 0 192.168.1.1          # 随机 MAC
nmap --spoof-mac Apple 192.168.1.1      # Apple 设备 MAC

# 源端口欺骗（某些防火墙只允许特定源端口）
nmap -g 53 192.168.1.1                  # 用 DNS 源端口
nmap --source-port 80 192.168.1.1       # 用 HTTP 源端口

# 源 IP 欺骗
nmap -S 192.168.1.200 192.168.1.1
```

### 15.7 时序控制

```bash
# 降低扫描速率
nmap --scan-delay 1s 192.168.1.1
nmap --max-scan-delay 10s 192.168.1.1
nmap -T0 192.168.1.1                    # Paranoid 模式
nmap -T1 192.168.1.1                    # Sneaky 模式

# 限制速率
nmap --min-rate 10 192.168.1.1
nmap --max-rate 100 192.168.1.1
```

### 15.8 代理与跳板

```bash
# HTTP/SOCKS4 代理（不支持 SOCKS5）
nmap --proxies http://proxy:8080 目标
nmap --proxies socks4://proxy:1080 目标

# 配合 proxychains
proxychains nmap -sT -Pn 目标

# SSH 隧道
ssh -L 1080:localhost:1080 user@跳板
nmap --proxies socks4://127.0.0.1:1080 目标
```

### 15.9 绕过策略汇总表

| 技术 | Nmap 选项 | 适用场景 | 有效性 |
|------|----------|---------|--------|
| 分片 | `-f` / `--mtu` | 无状态防火墙 | 现代防火墙多能重组 |
| 诱饵 | `-D` | 隐藏源 IP | 中 |
| TTL 操纵 | `--ttl` | 绕过 IDS | 中 |
| 随机数据 | `--data-length` | 绕过签名 | 中 |
| 无效校验和 | `--badsum` | 检测防火墙 | 低 |
| 源端口 | `-g` | 特定防火墙规则 | 低-中 |
| 慢速扫描 | `-T0/-T1` | 绕过 IDS | 高（但慢） |
| 代理 | `--proxies` | 隐藏源 IP | 中 |
| MAC 欺骗 | `--spoof-mac` | 局域网 | 低 |


# 第六部分：自动化与集成

## 第十六章：自动化扫描与开发

### 16.1 Python 调用 Nmap

```python
import subprocess
import xml.etree.ElementTree as ET

def nmap_scan(target, ports="1-1000"):
    """执行 Nmap 扫描并返回 XML 结果"""
    cmd = [
        "nmap", "-sS", "-sV",
        "-p", ports,
        "-oX", "-",          # XML 输出到 stdout
        target
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def parse_nmap_xml(xml_output):
    """解析 Nmap XML 输出"""
    root = ET.fromstring(xml_output)
    for host in root.findall("host"):
        addr = host.find("address").get("addr")
        for port in host.findall("ports/port"):
            port_id = port.get("portid")
            state = port.find("state").get("state")
            service = port.find("service")
            service_name = service.get("name") if service is not None else "unknown"
            version = service.get("version", "") if service is not None else ""
            print(f"{addr}:{port_id}  {state}  {service_name} {version}")

if __name__ == "__main__":
    xml_data = nmap_scan("192.168.1.1", "22,80,443")
    parse_nmap_xml(xml_data)
```

### 16.2 使用 python-nmap 库

```python
# pip install python-nmap
import nmap

nm = nmap.PortScanner()
nm.scan('192.168.1.1', '22-443', arguments='-sV')

for host in nm.all_hosts():
    print(f"主机: {host} ({nm[host].hostname()})")
    print(f"状态: {nm[host].state()}")
    for proto in nm[host].all_protocols():
        ports = nm[host][proto].keys()
        for port in sorted(ports):
            state = nm[host][proto][port]['state']
            name = nm[host][proto][port]['name']
            version = nm[host][proto][port].get('version', '')
            print(f"  {port}/{proto}  {state}  {name} {version}")
```

### 16.3 使用 libnmap 解析 XML

```python
# pip install python-libnmap
from libnmap.parser import NmapParser

# 从文件解析
report = NmapParser.parse_fromfile("scan.xml")

# 从字符串解析
report = NmapParser.parse(xml_string)

for host in report.hosts:
    print(f"主机: {host.address} ({host.hostnames})")
    for service in host.services:
        print(f"  {service.port}/{service.protocol}  {service.state}  {service.service}")
        for script_out in service.scripts_results:
            print(f"    脚本 {script_out['id']}: {script_out['output']}")
```

### 16.4 自动化资产扫描脚本

```python
import subprocess
import ipaddress
import json

def auto_discover(network="192.168.1.0/24"):
    """自动发现内网资产"""
    # 第一步：主机发现
    ping_scan = subprocess.run(
        ["nmap", "-sn", network],
        capture_output=True, text=True
    )

    online_hosts = []
    for line in ping_scan.stdout.split("\n"):
        if "Nmap scan report for" in line:
            ip = line.split()[-1]
            online_hosts.append(ip)

    print(f"发现 {len(online_hosts)} 台在线主机")

    # 第二步：端口扫描
    results = {}
    for host in online_hosts:
        print(f"扫描 {host} ...")
        port_scan = subprocess.run(
            ["nmap", "-sS", "-sV", "-T4",
             "-p", "22,80,443,3306,8080", host],
            capture_output=True, text=True
        )
        results[host] = port_scan.stdout

    # 第三步：保存结果
    with open("assets.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results

if __name__ == "__main__":
    auto_discover("192.168.1.0/24")
```

### 16.5 扫描报告生成

```bash
# XML 转 HTML
nmap -A 192.168.1.1 -oX scan.xml
xsltproc scan.xml -o scan.html

# 使用 nmap-formatter 转 JSON
# pip install nmap-formatter 或使用 Docker
nmap-formatter json scan.xml > scan.json
nmap-formatter markdown scan.xml > scan.md

# 使用 nmap-helper 转换
# nmap-helper convert scan.xml
```


## 第十七章：输出解析与报告生成

### 17.1 输出格式对比

| 格式 | 选项 | 可读性 | 可解析性 | 适用场景 |
|------|------|--------|---------|----------|
| Normal | `-oN` | 高 | 低 | 人工查看 |
| XML | `-oX` | 低 | **极高** | 工具集成 |
| Grepable | `-oG` | 中 | 中 | grep 搜索 |
| JSON | 第三方转换 | 中 | 高 | 现代工具链 |
| 全部 | `-oA` | — | — | 保留所有格式 |

### 17.2 XML 结构详解

```xml
<?xml version="1.0"?>
<nmaprun scanner="nmap" args="nmap -sS -sV 192.168.1.1" start="1700000000">
  <host>
    <status state="up" reason="syn-ack"/>
    <address addr="192.168.1.1" addrtype="ipv4"/>
    <hostnames>
      <hostname name="server.local" type="PTR"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="22">
        <state state="open" reason="syn-ack"/>
        <service name="ssh" product="OpenSSH" version="7.4"/>
      </port>
      <port protocol="tcp" portid="80">
        <state state="open" reason="syn-ack"/>
        <service name="http" product="nginx" version="1.14.0"/>
        <script id="http-title" output="Welcome to nginx"/>
      </port>
    </ports>
    <os>
      <osmatch name="Linux 3.2 - 4.9" accuracy="95"/>
    </os>
  </host>
  <runstats>
    <finished time="1700000100" elapsed="100"/>
  </runstats>
</nmaprun>
```

### 17.3 Grepable 格式解析

```bash
# Grepable 格式每行以 Host: 开头
nmap -oG result.gnmap 192.168.1.1
cat result.gnmap | grep "Ports:" | head

# 输出示例：
# Host: 192.168.1.1 ()	Ports: 22/open/tcp//ssh///, 80/open/tcp//http///

# 提取开放端口
grep "Ports:" result.gnmap | awk '{print $2, $4}'
```

### 17.4 JSON 转换与解析

```bash
# 安装 nmap-formatter
# https://github.com/vdjagilev/nmap-formatter

# 转换为 JSON
nmap-formatter json scan.xml

# 使用 jq 处理
nmap-formatter json scan.xml | jq '.Host[] | {ip: .Address, ports: [.Ports[].Port]}'

# Python 中使用 xmltodict 转换
pip install xmltodict
python -c "
import xmltodict, json
with open('scan.xml') as f:
    data = xmltodict.parse(f.read())
print(json.dumps(data, indent=2))
"
```

### 17.5 报告生成工具

```bash
# xsltproc（XML → HTML）
xsltproc scan.xml -o scan.html

# nmap-formatter
nmap-formatter html scan.xml > scan.html
nmap-formatter markdown scan.xml > scan.md
nmap-formatter csv scan.xml > scan.csv

# 使用 Metasploit 导入
msfconsole
msf6> db_import scan.xml
msf6> hosts
msf6> services
```


## 第十八章：第三方工具集成

### 18.1 扫描器对比

| 特性 | Nmap (v7.96) | Masscan (v1.3.2) | RustScan (v2.1.1) | ZMap (v3.0.0) |
|------|-------------|-------------------|-------------------|----------------|
| 最大 PPS | ~1,000 (稳定) | 25,000,000 | ~100,000 (突发) | 1,440,000 |
| 扫描技术 | 有状态 | 无状态 | 自适应 | 无状态 |
| 服务检测 | ✅ (版本检测) | ❌ | ✅ (通过 Nmap) | ❌ |
| 脚本引擎 | ✅ (NSE) | ❌ | ❌ | ❌ |
| IPv6 支持 | ✅ | ✅ | ✅ | ✅ (v3.0+) |
| 主要场景 | 单机审计 | 全网扫描 | 快速内网侦察 | 全球研究 |

Nmap 是网络发现的金标准，具有无与伦比的精度。Masscan 通过自定义 TCP/IP 栈实现每秒 2500 万包的扫描速度。RustScan 提供比 Nmap 快 400 倍的端口发现，并能将结果传给 Nmap 做深度分析。ZMap 适用于学术性全网研究。

### 18.2 Masscan + Nmap 组合

```bash
# 第一步：Masscan 快速发现开放端口
masscan -p1-65535 --rate=10000 192.168.1.0/24 -oG masscan_out.txt

# 提取开放端口
grep "open" masscan_out.txt | awk '{print $4}' | cut -d'/' -f1 | sort -u > ports.txt

# 第二步：Nmap 详细扫描
nmap -sV -sC -p $(cat ports.txt | tr '\n' ',' | sed 's/,$//') 192.168.1.1
```

### 18.3 RustScan + Nmap 组合

```bash
# RustScan 快速发现 + Nmap 深度分析
rustscan -a 192.168.1.1 --range 1-65535 -- -sV -sC

# 批量扫描
rustscan -a 192.168.1.0/24 --ulimit 5000 -- -sV -oX results.xml
```

### 18.4 与 Metasploit 集成

```bash
# 在 Metasploit 中导入 Nmap 结果
msfconsole
msf6> db_import scan.xml
msf6> hosts
msf6> services
msf6> vulns

# 直接从 Metasploit 运行 Nmap
msf6> db_nmap -sV -O 192.168.1.1
```

### 18.5 与 Web 扫描工具集成

```bash
# httpx 存活探测
cat subdomains.txt | httpx -o alive.txt

# Nuclei 模板化扫描
nuclei -l alive.txt -t cves/ -o nuclei_results.txt

# Nmap → httpx 流程
nmap -p 80,443,8080 --open -oG - 192.168.1.0/24 | grep "Ports:" | awk '{print $2}' | httpx
```


# 第七部分：实战与防御

## 第十九章：真实渗透流程

### 19.1 标准渗透测试阶段

渗透测试遵循信息收集、漏洞评估和利用等标准阶段。

```
阶段1：信息收集 → 阶段2：扫描与枚举 → 阶段3：漏洞评估 → 阶段4：利用 → 阶段5：后渗透
```

### 19.2 Nmap 在渗透测试中的使用

**阶段1：信息收集**

```bash
# 域名解析
dig +short target.com
nslookup target.com

# 子域名枚举
nmap --script=dns-brute target.com

# 被动信息收集（不直接接触目标）
# 使用 Shodan、Censys、FOFA 等
```

**阶段2：扫描与枚举**

```bash
# 第一步：主机发现
nmap -sn 192.168.1.0/24 -oA discovery

# 第二步：快速端口扫描（常用端口）
nmap -sS -T4 --top-ports 1000 192.168.1.1 -oA quick_scan

# 第三步：全端口扫描
nmap -sS -p- --min-rate 1000 192.168.1.1 -oA full_scan

# 第四步：针对开放端口的详细扫描
nmap -sV -sC -O -p 22,80,443,3306 192.168.1.1 -oA detailed_scan

# 第五步：NSE 脚本扫描
nmap --script=vuln -p 80,443 192.168.1.1 -oA vuln_scan
```

**阶段3：漏洞评估**

```bash
# SMB 漏洞检测
nmap --script=smb-vuln-* -p 445 192.168.1.1

# Web 漏洞检测
nmap --script=http-vuln-* -p 80,443 192.168.1.1

# 使用 vulners 脚本
nmap --script=vulners -sV 192.168.1.1
```

### 19.3 HTB/CTF 中的 Nmap 套路

```bash
# HTB 标准开局
# 1. 全端口快速扫描
nmap -p- --min-rate 5000 -T4 -oN allports 10.10.10.x

# 2. 对开放端口做详细扫描
nmap -sV -sC -p 22,80,443 -oN detailed 10.10.10.x

# 3. 根据结果选择攻击路径
#    - 80/443 → Web 枚举（gobuster、ffuf）
#    - 22 → SSH 爆破或密钥利用
#    - 445 → SMB 枚举
#    - 3306 → 数据库访问
```

### 19.4 内网渗透中的 Nmap

```bash
# 内网存活发现
nmap -sn 10.0.0.0/24 -oG alive.txt

# 内网服务扫描
nmap -sS -sV -T4 --open -iL alive.txt -oA internal_scan

# 内网横向移动前扫描
nmap -sS -p 22,135,139,445,3389,5985,5986 10.0.0.0/24 -oA lateral_scan
```


## 第二十章：云环境与合规

### 20.1 云服务商扫描政策

**AWS**：扫描活动必须遵守 AWS 可接受使用政策和服务条款。只能扫描你组织拥有的资源或有明确许可扫描的资源。未经授权的端口扫描违反 AWS 可接受使用政策。AWS Trust & Safety 不认可未经授权的渗透测试，并保留限制或阻止不符合指南的流量的权利。

**其他云平台**：阿里云、腾讯云、Azure 等有类似政策。扫描前务必确认授权范围。

### 20.2 安全组对扫描的影响

AWS 安全组提供有状态过滤。如果安全组允许来自任何源（0.0.0.0/0）的流量到特定端口，该端口将暴露于端口扫描。高风险端口（20/21 FTP、22 SSH、3306 MySQL、1433 MSSQL）不应允许公开访问。

### 20.3 云环境扫描策略

```bash
# 从云内部扫描（绕过安全组外部限制）
# 在 EC2 实例上安装 Nmap
sudo yum install nmap

# 使用 VPC 流日志分析
# 云控制台 → VPC → 流日志 → 分析异常流量

# 扫描云环境的常见服务
nmap -sS -sV -p 22,80,443,3306,6379,27017,9200 -T4 10.0.0.0/24
```

### 20.4 合规要求

| 标准 | 对扫描的要求 |
|------|-------------|
| PCI DSS | 季度外部扫描、年度内部扫描，需授权 |
| 等保 2.0 | 定期漏洞扫描，需书面授权 |
| ISO 27001 | 风险评估包含扫描 |
| GDPR | 扫描不涉及个人数据时无特殊限制 |

### 20.5 扫描授权与法律风险

**务必获取书面授权**，明确：扫描范围（IP/域名）、扫描时间、扫描类型、紧急联系人、数据处理方式。


## 第二十一章：防御视角

### 21.1 扫描行为的网络特征

| 行为 | 特征 | 检测方法 |
|------|------|----------|
| SYN 扫描 | 大量 SYN 包，没有 ACK 后续 | 统计短时间内 SYN 包数量 |
| 全端口扫描 | 短时间内访问 65535 个端口 | 连接数异常激增 |
| 主机发现 | 大量 ICMP Echo 请求 | ICMP 流量监控 |
| 分片扫描 | IP 分片异常 | 检查分片重组 |
| NSE 扫描 | 大量特定服务的探测请求 | 应用层日志分析 |

### 21.2 防御措施

**防火墙规则：**

```bash
# iptables 限制 SYN 频率
iptables -A INPUT -p tcp --syn -m limit --limit 1/s -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# nftables
nft add rule inet filter input tcp flags syn limit rate 1/second accept
nft add rule inet filter input tcp flags syn drop
```

**IDS/IPS 规则（Snort）：**

```
alert tcp $EXTERNAL_NET any -> $HOME_NET any (
    msg:"NMAP SYN scan";
    flags:S,12;
    threshold: type both, track by_src, count 20, seconds 10;
    sid:1000001;
)
```

**其他防御措施：**

- 端口敲击（Port Knocking）隐藏服务端口
- 部署 Honeypot 诱捕扫描器
- 速率限制（`fail2ban`、`sshguard`）
- 减少攻击面（关闭不必要的端口）

### 21.3 红队 vs 蓝队视角对比

| 维度 | 红队（攻击者） | 蓝队（防御者） |
|------|---------------|---------------|
| 目标 | 发现漏洞，突破边界 | 发现并阻断攻击 |
| Nmap 用法 | `-sS -f -D -T0` 隐蔽扫描 | 用 Nmap 做资产盘点 |
| 关注点 | 开放端口、漏洞 | 异常扫描流量、告警 |
| 工具 | Nmap + 代理 + 跳板 | IDS + 防火墙日志 |


## 第二十二章：IPv6 专项

### 22.1 IPv6 扫描基础

Nmap 自 2002 年起支持 IPv6 的大部分流行功能。要使用 IPv6，源和目标都必须配置为使用 IPv6。IPv6 地址只能使用 IP 地址或完全限定域名指定。

```bash
nmap -6 2001:db8::1                # 扫描单个 IPv6
nmap -6 2001:db8::/64              # 扫描 IPv6 网段
nmap -6 -sn 2001:db8::/64          # IPv6 主机发现
nmap -6 -sV -A -p- 2001:db8::1     # IPv6 全端口详细扫描
```

### 22.2 IPv6 主机发现

IPv6 环境下，`-PR` 使用 ICMPv6 Neighbor Discovery 代替 ARP。Nmap 通常对本地以太网连接的主机执行 ARP 或 IPv6 Neighbor Discovery 发现。

```bash
nmap -6 -PR 2001:db8::1            # ICMPv6 Neighbor Discovery
nmap -6 -PE 2001:db8::1            # ICMPv6 Echo
```

### 22.3 IPv6 与 IPv4 的差异

| 特性 | IPv4 | IPv6 |
|------|------|------|
| 地址配置 | DHCP/静态 | SLAAC/DHCPv6/静态 |
| 主机发现 | ARP | NDP（Neighbor Discovery） |
| 广播 | 支持 | 不支持（用组播） |
| 地址空间 | 2^32 | 2^128 |
| 扫描难度 | 低 | 高（地址空间大） |
| NAT | 普遍 | 不常用 |


## 第二十三章：性能调优

### 23.1 大规模网段扫描策略

```bash
# 第一阶段：快速主机发现（使用 Masscan 或 Nmap -sn）
nmap -sn 10.0.0.0/16 -T4 --min-rate 10000 -oG alive.gnmap

# 第二阶段：从存活主机中扫描常用端口
nmap -sS -T4 --top-ports 100 -iL alive_hosts.txt -oA common_ports

# 第三阶段：对发现开放端口的主机进行详细扫描
nmap -sV -sC -O -iL hosts_with_ports.txt -oA detailed
```

### 23.2 时间模板与并行参数

```bash
# 时间模板
nmap -T4 192.168.1.1              # Aggressive（常用）
nmap -T5 192.168.1.1              # Insane（可能丢包）

# 并行控制
nmap --min-hostgroup 64 192.168.1.0/24   # 最小并行组
nmap --max-hostgroup 128 192.168.1.0/24  # 最大并行组
nmap --min-parallelism 10                # 最小并行探测
nmap --max-parallelism 100               # 最大并行探测

# RTT 控制
nmap --min-rtt-timeout 100ms 192.168.1.1
nmap --max-rtt-timeout 1000ms 192.168.1.1

# 重试控制
nmap --max-retries 3 192.168.1.1         # 默认 10

# 速率控制
nmap --min-rate 1000 192.168.1.1
nmap --max-rate 5000 192.168.1.1

# 超时控制
nmap --host-timeout 30m 192.168.1.1
nmap --script-timeout 10m 192.168.1.1
```

### 23.3 UDP 扫描调优

```bash
# UDP 扫描默认很慢，需要调优
nmap -sU -p 53,161,123,67,68 --max-retries 1 --host-timeout 5m 192.168.1.1

# 结合 TCP 扫描
nmap -sS -sU -p T:22,80,443,U:53,161 192.168.1.1
```

### 23.4 分布式扫描

```bash
# 多台机器同时扫描不同网段
# 机器1：nmap -sS -T4 10.0.0.0/24 -oA scan1
# 机器2：nmap -sS -T4 10.0.1.0/24 -oA scan2
# 机器3：nmap -sS -T4 10.0.2.0/24 -oA scan3

# 使用 --randomize-hosts 避免被检测
nmap --randomize-hosts 192.168.1.0/24
```


## 第二十四章：常见错误排查

### 24.1 权限问题

```
Failed to open device eth0
```

**原因**：SYN 扫描（`-sS`）需要原始套接字权限。

**解决**：

```bash
sudo nmap -sS target
# 或
sudo setcap cap_net_raw+ep /usr/bin/nmap
```

### 24.2 主机发现问题

```
Host seems down
```

**原因**：默认会先 Ping（ICMP），被防火墙拦截。

**解决**：

```bash
nmap -Pn target   # 跳过主机发现
```

### 24.3 端口扫描超时

```
scanning 65535 ports, 100% complete
但结果为空
```

**可能原因**：防火墙拦截了所有探测包；目标使用了 Port Knocking；网络质量差。

**解决**：

```bash
nmap -sS -f --mtu 32 --scan-delay 1s target
```

### 24.4 脚本执行失败

```
NSE: failed to initialize script
```

**原因**：脚本依赖的 Lua 库缺失。

**解决**：

```bash
sudo apt update && sudo apt install --reinstall nmap
sudo nmap --script-updatedb
```

### 24.5 AppArmor 限制

```bash
# 检查 nmap 的 AppArmor 状态
sudo aa-status | grep nmap

# 如果处于 enforce 模式，临时禁用
sudo aa-complain /usr/bin/nmap
```

### 24.6 常见错误速查表

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `Failed to open device eth0` | 没有 root 权限 | 用 `sudo` 执行 |
| `No targets were specified` | 没写目标 IP | 检查命令语法 |
| `Host seems down` | 防火墙拦截了 Ping | 加 `-Pn` 跳过主机发现 |
| `All 1000 scanned ports are filtered` | 被防火墙过滤 | 尝试 `-sS -f -D` 绕过 |
| `NSE: script timed out` | 脚本执行太慢 | 用 `--script-timeout` 调大 |
| `Couldn't open a raw socket` | 容器缺少 CAP_NET_RAW | 加 `--cap-add=NET_RAW` |
| `Permission denied` | 非 root 执行 SYN 扫描 | 用 `sudo` 或 setcap |
| `NSE: failed to initialize script` | Lua 库缺失 | 更新 Nmap 和脚本库 |


## 第二十五章：学习路线

```
┌──────────────────────────────────────────────┐
│  Level 1: 基础命令掌握                        │
│  - 目标指定、主机发现、端口扫描              │
│  - 能看懂扫描结果，区分 open/closed/filtered │
└──────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│  Level 2: TCP/IP 协议理解                    │
│  - 三次握手、四次挥手                        │
│  - SYN/ACK/RST/FIN 标志位含义               │
│  - 理解不同扫描方式的数据包差异              │
└──────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│  Level 3: Nmap 原理深入                      │
│  - 理解各扫描参数背后的数据包交互            │
│  - 知道什么时候用什么扫描方式                │
│  - 服务指纹和 OS 指纹原理                    │
└──────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│  Level 4: NSE 开发                          │
│  - 读懂 NSE 脚本代码                        │
│  - 能写简单的自定义脚本                     │
│  - 掌握 Lua 基本语法                        │
│  - 熟练使用 NSE 库                          │
└──────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│  Level 5: 安全自动化                        │
│  - Python + Nmap 自动化扫描                 │
│  - 结果解析、报告生成、AI 分析              │
│  - Masscan/RustScan 集成                    │
└──────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│  Level 6: 红队高级                          │
│  - IDS/IPS 绕过                             │
│  - 云环境渗透                                │
│  - 内网横向移动                              │
└──────────────────────────────────────────────┘
```


# 第八部分：命令速查

## 一、目标指定

```bash
nmap 192.168.1.1                  # 扫描单个 IP
nmap 192.168.1.1-100              # 扫描 IP 段
nmap 192.168.1.0/24               # 扫描整个子网
nmap 192.168.1.1,2,3              # 多个指定 IP
nmap -iL targets.txt              # 从文件读取
nmap --exclude 192.168.1.2        # 排除某个 IP
nmap --excludefile exclude.txt    # 从文件排除
nmap -6 2001:db8::1               # IPv6 地址
nmap -6 2001:db8::/64             # IPv6 网段
```

## 二、主机发现（找谁在线）

```bash
nmap -sn 192.168.1.0/24           # Ping 扫描（只找在线设备）
nmap -Pn 192.168.1.1              # 跳过 Ping
nmap -PS 192.168.1.1              # TCP SYN Ping
nmap -PS22,80,443 192.168.1.1     # 指定端口
nmap -PA 192.168.1.1              # TCP ACK Ping
nmap -PU 192.168.1.1              # UDP Ping
nmap -PE 192.168.1.1              # ICMP Echo Ping
nmap -PP 192.168.1.1              # ICMP Timestamp Ping
nmap -PM 192.168.1.1              # ICMP Netmask Ping
nmap -PR 192.168.1.1              # ARP Ping（局域网推荐）
nmap -PY 192.168.1.1              # SCTP INIT Ping
nmap -PO 192.168.1.1              # IP 协议 Ping
nmap --traceroute 192.168.1.1     # 路由追踪
```

## 三、端口扫描（看开了哪些门）

```bash
nmap -p 80 192.168.1.1            # 单个端口
nmap -p 80,443,22 192.168.1.1     # 多个端口
nmap -p 1-1000 192.168.1.1        # 端口范围
nmap -p- 192.168.1.1              # 所有端口
nmap -F 192.168.1.1               # 快速扫描（前 100 个）
nmap --top-ports 200 192.168.1.1  # 最常用 200 个
nmap -r 192.168.1.1               # 顺序扫描
nmap -p U:53,T:80 192.168.1.1     # 混合扫描
```

## 四、扫描技术（怎么扫）

```bash
nmap -sS 192.168.1.1              # TCP SYN 半开扫描
nmap -sT 192.168.1.1              # TCP 全连接扫描
nmap -sA 192.168.1.1              # TCP ACK 扫描
nmap -sW 192.168.1.1              # TCP 窗口扫描
nmap -sM 192.168.1.1              # TCP Maimon 扫描
nmap -sN 192.168.1.1              # TCP Null 扫描
nmap -sF 192.168.1.1              # TCP FIN 扫描
nmap -sX 192.168.1.1              # TCP Xmas 扫描
nmap -sU 192.168.1.1              # UDP 扫描
nmap -sU -sS 192.168.1.1          # UDP + TCP
nmap -sO 192.168.1.1              # IP 协议扫描
nmap -sY 192.168.1.1              # SCTP INIT 扫描
nmap -sZ 192.168.1.1              # SCTP COOKIE-ECHO 扫描
nmap -sI 僵尸机IP 目标IP          # 空闲扫描
nmap -b ftp-server 目标           # FTP Bounce 扫描
```

## 五、服务与系统识别（扒信息）

```bash
nmap -sV 192.168.1.1              # 服务版本检测
nmap -sV --version-light 192.168.1.1   # 轻量级
nmap -sV --version-all 192.168.1.1     # 重量级
nmap -sV --version-intensity 8 192.168.1.1  # 强度 0-9
nmap -O 192.168.1.1               # 操作系统检测
nmap -O --osscan-guess 192.168.1.1    # 大胆猜测
nmap -O --osscan-limit 192.168.1.1    # 限制扫描条件
nmap -A 192.168.1.1               # 综合扫描
```

## 六、脚本扫描（NSE 引擎，核心功能）

```bash
nmap --script=脚本名 192.168.1.1  # 指定脚本
nmap --script=default 192.168.1.1 # 默认脚本
nmap --script=all 192.168.1.1     # 所有脚本（慎用）
nmap --script=auth 192.168.1.1    # 认证相关
nmap --script=discovery 192.168.1.1   # 服务发现
nmap --script=vuln 192.168.1.1    # 漏洞扫描
nmap --script=exploit 192.168.1.1 # 漏洞利用
nmap --script=brute 192.168.1.1   # 暴力破解
nmap --script=dos 192.168.1.1     # DoS 攻击
nmap --script=safe 192.168.1.1    # 安全脚本
nmap --script=http-title 192.168.1.1
nmap --script=http-enum 192.168.1.1
nmap --script=http-headers 192.168.1.1
nmap --script=smb-enum-shares 192.168.1.1
nmap --script=smb-os-discovery 192.168.1.1
nmap --script=smb-vuln* 192.168.1.1
nmap --script=ssh-brute 192.168.1.1
nmap --script=mysql-empty-password 192.168.1.1
nmap --script=dns-brute 192.168.1.1
nmap --script=http-enum --script-args http-enum.fingerprintfile=./myfile.txt
nmap --script-help=http-title
```

## 七、速度与性能（快慢自己调）

```bash
nmap -T0 192.168.1.1                # 极慢（Paranoid）
nmap -T1 192.168.1.1                # 慢（Sneaky）
nmap -T2 192.168.1.1                # 较慢（Polite）
nmap -T3 192.168.1.1                # 正常（默认）
nmap -T4 192.168.1.1                # 快（Aggressive）
nmap -T5 192.168.1.1                # 极快（Insane）
nmap --min-hostgroup 64 192.168.1.0/24
nmap --max-hostgroup 64 192.168.1.0/24
nmap --min-parallelism 10
nmap --max-parallelism 100
nmap --min-rtt-timeout 100ms
nmap --max-rtt-timeout 1000ms
nmap --max-retries 3
nmap --scan-delay 1s
nmap --max-scan-delay 10s
nmap --host-timeout 30m
nmap --script-timeout 10m
nmap --min-rate 1000
nmap --max-rate 5000
```

## 八、防火墙绕过（隐身技巧）

```bash
nmap -f 192.168.1.1                 # 分片数据包
nmap -f --mtu 32 192.168.1.1        # 指定 MTU
nmap -D 192.168.1.2,ME 192.168.1.1  # 诱饵
nmap -D RND:5,ME 192.168.1.1        # 随机诱饵
nmap --spoof-mac 00:11:22:33:44:55 192.168.1.1  # 伪造 MAC
nmap --spoof-mac 0 192.168.1.1      # 随机 MAC
nmap --spoof-mac Apple 192.168.1.1  # Apple MAC
nmap -g 53 192.168.1.1              # 源端口欺骗
nmap --source-port 53 192.168.1.1   # 同上
nmap --data-length 25 192.168.1.1   # 附加随机数据
nmap --data 0xDEADBEEF 192.168.1.1  # 附加指定数据
nmap --badsum 192.168.1.1           # 错误校验和
nmap --ttl 128 192.168.1.1          # 设置 TTL
nmap --randomize-hosts 192.168.1.0/24   # 随机化主机顺序
nmap --proxies http://proxy:8080    # HTTP 代理
nmap --proxies socks4://proxy:1080  # SOCKS4 代理
```

## 九、输出格式（保存结果）

```bash
nmap -v 192.168.1.1                 # 详细输出
nmap -vv 192.168.1.1                # 非常详细
nmap -d 192.168.1.1                 # 调试模式
nmap -d3 192.168.1.1                # 调试级别 1-9
nmap -oN result.txt 192.168.1.1     # 普通文本
nmap -oX result.xml 192.168.1.1     # XML 格式
nmap -oG result.gnmap 192.168.1.1   # Grepable 格式
nmap -oA result 192.168.1.1         # 所有格式
nmap --append-output 192.168.1.1    # 追加
nmap --resume result.gnmap          # 恢复中断
nmap --reason 192.168.1.1           # 显示状态原因
nmap --open 192.168.1.1             # 只显示开放端口
nmap --packet-trace 192.168.1.1     # 显示收发的包
nmap --stats-every 5s 192.168.1.1   # 定期输出进度
```

## 十、常用组合拳（实战套路）

```bash
# 快速发现局域网设备
nmap -sn 192.168.1.0/24

# 快速扫描常用端口 + 版本 + 系统
nmap -sS -sV -O -T4 192.168.1.1

# 全端口快速扫描
nmap -p- --min-rate 1000 192.168.1.1

# 扫网页服务并获取标题
nmap -p 80,443,8080,8443 --script=http-title 192.168.1.1

# 扫永恒之蓝漏洞
nmap -p 445 --script=smb-vuln* 192.168.1.1

# 扫 UDP 常用端口
nmap -sU -p 53,161,123,67,68 192.168.1.1

# 绕过防火墙扫描
nmap -sS -f -D 192.168.1.2,ME -g 53 192.168.1.1

# 扫描并保存所有格式
nmap -A -T4 192.168.1.1 -oA scan_result

# 从文件批量扫描
nmap -iL targets.txt -sV -oN batch_scan.txt

# SCTP 扫描
nmap -sY -p 7,9,20,21,22,80,179,443 scanme.csnc.ch --reason

# 空闲扫描
nmap -sI 僵尸机IP 目标IP

# FTP Bounce 扫描
nmap -b ftp.example.com 192.168.1.1
```

## 十一、端口状态解读

| 状态 | 含义 |
|------|------|
| `open` | 端口开放，有服务在监听（可以连接） |
| `closed` | 端口关闭，没有服务（但主机在线） |
| `filtered` | 被防火墙过滤，不确定状态 |
| `unfiltered` | 能访问到，但不确定开放/关闭 |
| `open\|filtered` | 开放或被过滤，无法区分 |
| `closed\|filtered` | 关闭或被过滤，无法区分 |

## 十二、扫描类型对比（快速参考）

| 扫描类型 | 参数 | 优点 | 缺点 |
|----------|------|------|------|
| SYN 半开 | `-sS` | 快、隐蔽、默认 | 需要 root 权限 |
| TCP 全连接 | `-sT` | 无需 root | 有日志，慢 |
| UDP | `-sU` | 扫 UDP 服务 | 慢、不可靠 |
| ACK | `-sA` | 探测防火墙规则 | 不判断端口开放 |
| SCTP INIT | `-sY` | 扫 SCTP 服务 | 需要 root |
| SCTP COOKIE | `-sZ` | 扫 SCTP 服务 | 需要 root |
| 空闲扫描 | `-sI` | 完全隐藏 | 需要僵尸机 |
| FTP Bounce | `-b` | 隐藏源 IP | 需要 FTP 服务器 |
| 版本检测 | `-sV` | 识别服务版本 | 略慢 |
| 系统检测 | `-O` | 识别操作系统 | 需要开放端口 |
| 综合扫描 | `-A` | 信息最全 | 最慢、最明显 |

## 十三、NSE 脚本类别大全

| 类别 | 说明 |
|------|------|
| `auth` | 认证绕过、弱密码检测 |
| `broadcast` | 广播发现（局域网） |
| `brute` | 暴力破解 |
| `default` | 默认脚本（安全、快速） |
| `discovery` | 服务发现 |
| `dos` | DoS 攻击（高危） |
| `exploit` | 漏洞利用（高危） |
| `external` | 调用外部 API |
| `fuzzer` | 模糊测试 |
| `intrusive` | 侵入式 |
| `malware` | 检测恶意软件 |
| `safe` | 安全脚本 |
| `version` | 服务版本增强检测 |
| `vuln` | 漏洞检测 |

## 十四、Zenmap（图形界面）

```bash
sudo apt install zenmap
zenmap
```

功能：图形化扫描配置、结果可视化、拓扑图展示、保存/加载配置、对比扫描结果。

## 十五、常用参数速记表

| 分类 | 参数 | 说明 |
|------|------|------|
| **目标** | `-sn` | 发现主机 |
| | `-Pn` | 跳过主机发现 |
| | `-iL` | 从文件读取 |
| **端口** | `-p` | 指定端口 |
| | `-F` | 快速扫描 |
| | `-p-` | 全端口 |
| **扫描类型** | `-sS` | SYN 半开 |
| | `-sT` | TCP 全连接 |
| | `-sU` | UDP |
| | `-sV` | 服务版本 |
| | `-O` | 操作系统 |
| | `-A` | 综合扫描 |
| | `-sY` | SCTP INIT |
| | `-sZ` | SCTP COOKIE |
| | `-sI` | 空闲扫描 |
| **脚本** | `--script` | 运行脚本 |
| | `--script-args` | 脚本参数 |
| | `--script-trace` | 脚本调试 |
| **速度** | `-T0` ~ `-T5` | 时间模板 |
| **规避** | `-f` | 分片 |
| | `-D` | 诱饵 |
| | `-g` | 源端口欺骗 |
| | `--ttl` | TTL 操纵 |
| | `--data-length` | 随机数据 |
| **输出** | `-v` | 详细 |
| | `-oN`/`-oX`/`-oG` | 输出格式 |
| | `-oA` | 所有格式 |
| | `--reason` | 显示原因 |
| | `--open` | 只显示开放 |


## ⚠️ 常见错误速查

| 错误信息 | 原因 | 解决方法 |
|----------|------|----------|
| `Failed to open device eth0` | 没有 root 权限 | 用 `sudo` 执行 |
| `No targets were specified` | 没写目标 IP | 检查命令语法 |
| `Host seems down` | 防火墙拦截了 Ping | 加 `-Pn` 跳过主机发现 |
| `All 1000 scanned ports are filtered` | 被防火墙过滤 | 尝试 `-sS -f -D` 绕过 |
| `NSE: script timed out` | 脚本执行太慢 | 用 `--script-timeout` 调大 |
| `Couldn't open a raw socket` | 容器缺少 CAP_NET_RAW | 加 `--cap-add=NET_RAW` |
| `Permission denied` | 非 root 执行 SYN 扫描 | 用 `sudo` 或 setcap |
| `NSE: failed to initialize script` | Lua 库缺失 | 更新 Nmap 和脚本库 |


> **提示**：本手册按“安装配置 → 扫描技术 → 指纹识别 → NSE 引擎 → 隐蔽绕过 → 自动化集成 → 实战防御 → 命令速查”组织，适合网络安全学习者、渗透测试人员和系统管理员使用。重点掌握：**TCP/IP 协议原理、各扫描类型的数据包交互、服务与 OS 指纹识别、NSE 脚本开发、IDS/IPS 绕过技术、Python 自动化**。实践中建议结合 Wireshark 分析数据包，配合 Masscan/RustScan 提升效率，始终在授权范围内进行测试。