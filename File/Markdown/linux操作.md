# Linux 命令速查卡（小白超详细完整版·完善版）


## 目录

**第一部分：基础操作**
- [一、文件与目录操作](#一文件与目录操作最基础)
- [二、查看文件内容](#二查看文件内容)
- [三、文件权限管理](#三文件权限管理)
- [四、重定向与管道](#四重定向与管道)
- [五、搜索与查找](#五搜索与查找)
- [六、压缩与解压](#六压缩与解压)
- [七、用户与权限管理](#七用户与权限管理)
- [八、进程管理](#八进程管理)
- [九、磁盘与内存管理](#九磁盘与内存管理)
- [十、网络命令](#十网络命令)

**第二部分：文本处理**
- [十一、文本处理命令](#十一文本处理命令)
- [十二、sed/awk 进阶](#十二sedawk-进阶)
- [十三、正则表达式速查](#十三正则表达式速查grepsedawk-通用)
- [十四、文本处理工具链补全](#十四文本处理工具链补全)
- [十五、xargs 并行处理](#十五xargs-并行处理)

**第三部分：编辑器与终端**
- [十六、Vim 编辑器速查](#十六vim-编辑器速查)
- [十七、nano / emacs 速查](#十七nano--emacs-速查)
- [十八、终端与 Shell 环境](#十八终端与-shell-环境)
- [十九、常用快捷键](#十九常用快捷键)
- [二十、tmux / screen 终端复用器](#二十tmux--screen-终端复用器)

**第四部分：Shell 脚本编程**
- [二十一、Shell 脚本基础](#二十一shell-脚本基础)
- [二十二、Shell 变量与参数](#二十二shell-变量与参数)
- [二十三、Shell 条件与循环](#二十三shell-条件与循环)
- [二十四、Shell 函数与数组](#二十四shell-函数与数组)
- [二十五、Shell 字符串操作](#二十五shell-字符串操作)
- [二十六、Shell 错误处理与调试](#二十六shell-错误处理与调试)
- [二十七、Shell 脚本实战](#二十七shell-脚本实战)

**第五部分：系统管理**
- [二十八、环境变量与别名](#二十八环境变量与别名)
- [二十九、系统信息](#二十九系统信息)
- [三十、硬件信息与内核模块](#三十硬件信息与内核模块)
- [三十一、软件包管理](#三十一软件包管理)
- [三十二、日志与系统启动](#三十二日志与系统启动)
- [三十三、systemd 服务管理](#三十三systemd-服务管理)
- [三十四、systemd timers](#三十四systemd-timers)
- [三十五、定时任务 cron / at](#三十五定时任务-cron--at)

**第六部分：权限与安全**
- [三十六、权限与安全进阶](#三十六权限与安全进阶)
- [三十七、防火墙](#三十七防火墙ufwiptablesnftables)
- [三十八、SELinux / AppArmor](#三十八selinux--apparmor)
- [三十九、SSH 远程管理](#三十九ssh-远程管理)
- [四十、加密与哈希](#四十加密与哈希)

**第七部分：磁盘与文件系统**
- [四十一、文件系统与磁盘管理](#四十一文件系统与磁盘管理)
- [四十二、LVM 逻辑卷管理](#四十二lvm-逻辑卷管理)
- [四十三、RAID 与 Swap](#四十三raid-与-swap)
- [四十四、软链接与硬链接](#四十四软链接与硬链接-ln)

**第八部分：性能与监控**
- [四十五、系统监控](#四十五系统监控)
- [四十六、性能分析工具](#四十六性能分析工具)
- [四十七、系统调优](#四十七系统调优)

**第九部分：网络进阶**
- [四十八、网络进阶与诊断](#四十八网络进阶与诊断)
- [四十九、curl 进阶](#四十九curl-进阶api-调试神器)
- [五十、tcpdump 抓包分析](#五十tcpdump-抓包分析)
- [五十一、lsof 详细用法](#五十一lsof-详细用法)

**第十部分：传输与备份**
- [五十二、rsync 同步备份](#五十二rsync-同步备份)
- [五十三、scp / sftp / sshfs](#五十三scp--sftp--sshfs)
- [五十四、备份工具](#五十四备份工具)

**第十一部分：容器与虚拟化**
- [五十五、容器与虚拟化](#五十五容器与虚拟化)

**第十二部分：实战与速查**
- [五十六、综合组合拳](#五十六综合组合拳常用实战)
- [五十七、速查小抄](#五十七速查小抄)

---

# 第一部分：基础操作

## 一、文件与目录操作（最基础）

```bash
ls                      # 列出当前目录内容
ls -l                   # 详细列表格式（权限、大小、时间）
ls -a                   # 显示所有文件（包括 . 开头的隐藏文件）
ls -la                  # 组合：详细 + 隐藏
ls -lh                  # 人类可读的大小（K、M、G）
ls -lt                  # 按修改时间排序（最新的在最前）
ls -ltr                 # 按修改时间反向排序（最旧在最前）
ls -lS                  # 按文件大小排序（大在前）
ls -R                   # 递归列出子目录
ls -d */                # 只列出目录

cd 目录名               # 进入目录
cd ..                   # 返回上一级目录
cd ~                    # 回到用户主目录
cd /                    # 回到根目录
cd -                    # 回到上一次所在的目录

pwd                     # 显示当前所在路径

mkdir 文件夹名          # 创建文件夹
mkdir -p a/b/c          # 递归创建多层目录
mkdir -m 755 dir        # 创建时指定权限

rmdir 文件夹名          # 删除空文件夹
rm 文件名               # 删除文件
rm -r 文件夹名          # 递归删除文件夹
rm -rf 文件夹名         # 强制删除（危险！）
rm -i 文件名            # 删除前询问
rm -v 文件名            # 显示删除过程
rm -rf /                # ⚠️ 千万别运行！！！会删光整个系统

cp 源文件 目标文件      # 复制文件
cp -r 源文件夹 目标文件夹 # 递归复制文件夹
cp -i 源文件 目标文件   # 覆盖前询问
cp -v 源文件 目标文件   # 显示复制过程
cp -p 源文件 目标文件   # 保留权限/时间戳
cp -a 源 目标           # 归档模式（等价于 -dpR）
cp -u 源 目标           # 仅当源更新时才复制

mv 源文件 目标文件      # 移动文件（也可用于重命名）
mv old.txt new.txt      # 重命名
mv file.txt /tmp/       # 移动到 /tmp 目录
mv -i 源 目标           # 覆盖前询问
mv -n 源 目标           # 不覆盖已存在文件

touch 文件名            # 创建空文件，或更新文件时间戳
touch -t 202401011200 file  # 指定时间戳

file 文件名             # 查看文件类型
stat 文件名             # 查看文件详细状态（inode、权限、时间）
tree 目录名             # 树形显示目录结构（需安装）
basename /path/to/file  # 提取文件名
dirname /path/to/file   # 提取目录名
realpath 文件           # 显示绝对路径
```

## 二、查看文件内容

```bash
cat 文件名              # 输出整个文件内容
cat file1.txt file2.txt # 合并多个文件
cat -n 文件名           # 显示行号
cat -A 文件名           # 显示不可见字符

less 文件名             # 分页查看（大文件用）
# less 中快捷键：
# 空格/PgDn 下一页  b/PgUp 上一页  g 首行  G 尾行
# /关键词 向下搜索  ?关键词 向上搜索  n/N 下一个/上一个
# q 退出  F 实时跟踪（类似 tail -f）  Ctrl+C 退出跟踪

more 文件名             # 分页查看（不如 less）
head -n 10 文件名       # 前 10 行
head -c 100 文件名      # 前 100 字节
tail -n 10 文件名       # 后 10 行
tail -f 文件名          # 实时追踪（看日志）
tail -F 文件名          # 文件被轮转后继续跟踪
tail -n +5 文件名       # 从第 5 行开始输出

tac 文件名              # 反向输出
nl 文件名               # 带行号输出
wc -l 文件名            # 统计行数
```

## 三、文件权限管理

```bash
# 权限格式：-rwxr-xr-x
# 第1位：- 文件 / d 目录 / l 链接 / c 字符设备 / b 块设备
# 第2-4位：所有者权限（u）
# 第5-7位：组权限（g）
# 第8-10位：其他人权限（o）

# 数字表示法：r=4, w=2, x=1
# 7 = rwx  6 = rw-  5 = r-x  4 = r--  0 = ---

chmod 755 文件名        # 所有者 rwx，组 r-x，其他 r-x
chmod 644 文件名        # 所有者 rw-，组 r--，其他 r--
chmod 600 文件名        # 只有所有者可读写（如 SSH 私钥）
chmod 777 文件名        # 所有人全部权限（⚠️ 危险）
chmod +x 文件名         # 所有人添加执行权限
chmod u+x 文件名        # 只给所有者添加执行
chmod go-w 文件名       # 去掉组和其他人的写入
chmod -R 755 目录       # 递归修改

chown 用户:组 文件名    # 修改所有者和组
chown 用户名 文件名     # 只修改所有者
chown :组名 文件名      # 只修改组
chown -R 用户:组 文件夹 # 递归修改

chgrp 组名 文件名       # 只改所属组

# 特殊权限（详见“权限与安全进阶”）
chmod u+s 文件          # SUID（执行时以文件所有者身份运行）
chmod g+s 目录          # SGID（新文件继承目录的组）
chmod +t 目录           # Sticky Bit（只有文件所有者可删除）

# 默认权限掩码（详见“权限与安全进阶”）
umask                   # 查看当前掩码
umask 022               # 设置掩码
```

## 四、重定向与管道

```bash
# 重定向
command > file.txt      # 标准输出重定向（覆盖）
command >> file.txt     # 标准输出重定向（追加）
command 2> error.txt    # 标准错误重定向
command &> output.txt   # 标准输出和错误都重定向
command &>> output.txt  # 同上，追加
command 2>&1            # 将标准错误合并到标准输出
command > out.txt 2>&1  # 同 &>
command 1>out.txt 2>err.txt  # 分别重定向

# 输入重定向
sort < file.txt         # 从文件读取输入
command <<< "字符串"    # Here String

# Here Document（多行输入）
cat << EOF
第一行
第二行
EOF

# 使用变量（不加引号会展开）
cat << EOF
当前用户：$USER
EOF

# 禁用变量展开
cat << 'EOF'
$USER 不会被展开
EOF

# 常用特殊设备文件
command > /dev/null     # 丢弃输出
command 2> /dev/null    # 丢弃错误
command &> /dev/null    # 丢弃所有

# 管道
ls -la | grep ".txt"    # 过滤 .txt
ps aux | grep python    # 查 python 进程
cat file.txt | wc -l    # 统计行数
history | grep ssh      # 搜历史
dmesg | less            # 分页看内核日志
ls -la | sort -k5 -nr   # 按第5列（大小）降序

# tee：同时输出到屏幕和文件
command | tee file.txt          # 输出并写入（覆盖）
command | tee -a file.txt       # 输出并追加
command | tee file1 file2       # 输出到多个文件

# 进程替换
diff <(ls dir1) <(ls dir2)      # 比较两个命令输出
```

## 五、搜索与查找

```bash
# grep 基础
grep "关键词" 文件名              # 搜索
grep -r "关键词" 目录             # 递归搜索
grep -i "关键词" 文件名           # 忽略大小写
grep -n "关键词" 文件名           # 显示行号
grep -v "关键词" 文件名           # 反向匹配
grep -l "关键词" *.txt           # 只显示文件名
grep -c "关键词" 文件名           # 统计匹配行数
grep -E "正则" 文件名             # 扩展正则（同 egrep）
grep -F "字符串" 文件名           # 固定字符串（不做正则）
grep -w "word" 文件名             # 全词匹配
grep -o "关键词" 文件名           # 只输出匹配部分
grep -A 3 "关键词" 文件           # 显示匹配后3行
grep -B 3 "关键词" 文件           # 显示匹配前3行
grep -C 3 "关键词" 文件           # 前后各3行
grep --include="*.py" -r "import" .  # 只搜 .py
grep --exclude="*.log" -r "error" .  # 排除 .log
grep -P "\d+" file                # Perl 兼容正则

# 排除自身
ps aux | grep -v grep | grep nginx

# find
find / -name "文件名"             # 从根目录查找
find /home -name "*.txt"         # 查找 .txt
find . -iname "*.TXT"            # 忽略大小写
find . -type d                   # 只找目录
find . -type f                   # 只找文件
find . -type l                   # 只找链接
find . -size +100M               # 大于 100M
find . -size -1k                 # 小于 1k
find . -mtime -7                 # 7 天内修改
find . -mtime +30                # 30 天前修改
find . -mmin -60                 # 60 分钟内修改
find . -user 用户名              # 属于某用户
find . -perm 644                 # 权限为 644
find . -empty                    # 空文件/目录
find . -maxdepth 2 -name "*.py"  # 限制深度
find . -name "*.tmp" -delete     # 找到后删除
find . -name "*.log" -exec rm {} \;  # 找到后执行
find . -name "*.txt" -exec cp {} /tmp/ \;
find . -type f -print0 | xargs -0 rm  # 处理空格文件名

# which / whereis / type
which python                     # 命令的完整路径
whereis python                   # 命令 + man 手册位置
type ls                          # 判断是内置/别名/文件

# locate（基于数据库，快速）
sudo updatedb                    # 更新数据库
locate 文件名                    # 快速查找
```

## 六、压缩与解压

```bash
# tar（打包）
tar -cvf archive.tar 文件夹/      # 打包
tar -xvf archive.tar              # 解包
tar -tvf archive.tar              # 查看内容
tar -xvf archive.tar -C /目标目录 # 解压到指定目录

# tar.gz
tar -czvf archive.tar.gz 文件夹/  # 打包 + gzip
tar -xzvf archive.tar.gz          # 解压
tar -tzvf archive.tar.gz          # 查看

# tar.bz2
tar -cjvf archive.tar.bz2 文件夹/
tar -xjvf archive.tar.bz2

# tar.xz
tar -cJvf archive.tar.xz 文件夹/
tar -xJvf archive.tar.xz

# tar.zst（zstd，现代，快）
tar --zstd -cvf archive.tar.zst 文件夹/
tar --zstd -xvf archive.tar.zst

# tar 高级
tar -czvf a.tar.gz --exclude="*.log" --exclude="cache" dir/
tar -czvf a.tar.gz --exclude-from=exclude.txt dir/
tar -xzvf a.tar.gz --strip-components=1  # 去掉一级目录
tar -rvf a.tar newfile            # 追加到已有 tar

# zip（Windows 兼容）
zip -r archive.zip 文件夹/        # 压缩
zip -e archive.zip 文件           # 加密压缩
unzip archive.zip                 # 解压
unzip archive.zip -d 目标目录     # 解压到指定目录
unzip -l archive.zip              # 列出内容

# gzip / bzip2 / xz / zstd（单文件）
gzip file.txt                     # 压缩为 file.txt.gz
gunzip file.txt.gz                # 解压
gzip -k file.txt                  # 保留原文件
gzip -9 file.txt                  # 最大压缩

bzip2 file.txt                    # 压缩为 file.txt.bz2
bunzip2 file.txt.bz2

xz file.txt                       # 压缩为 file.txt.xz
unxz file.txt.xz
xz -9 -T0 file                    # 多线程最大压缩

zstd file.txt                     # 压缩
zstd -d file.txt.zst              # 解压
zstd -19 -T0 file                 # 最大压缩

# 7z / rar
7z a archive.7z 文件夹/           # 压缩（需 p7zip）
7z x archive.7z                   # 解压
rar a archive.rar 文件夹/         # 需 rar
unrar x archive.rar

# 并行压缩
pigz file                         # 并行 gzip
pbzip2 file                       # 并行 bzip2
```

## 七、用户与权限管理

```bash
whoami                  # 当前用户名
id                      # UID、GID、所属组
id 用户名               # 查看指定用户
who                     # 当前登录用户
w                       # 更详细的登录信息
last                    # 最近登录记录
lastlog                 # 所有用户最后登录时间

sudo 命令               # 以 root 权限执行
sudo -i                 # 切换到 root 交互式 shell
sudo -u 用户 命令       # 以指定用户执行
su - 用户名             # 切换用户
sudo su -               # 切到 root

useradd 用户名          # 创建用户
useradd -m 用户名       # 创建用户并建家目录
useradd -m -s /bin/bash 用户名  # 指定 shell
useradd -G 组1,组2 用户名  # 加入附加组
passwd 用户名           # 设置/修改密码
userdel 用户名          # 删除用户
userdel -r 用户名       # 删除用户和家目录
usermod -aG 组名 用户名 # 添加到组
usermod -s /bin/zsh 用户名  # 修改 shell
usermod -L 用户名       # 锁定用户
usermod -U 用户名       # 解锁用户

groupadd 组名           # 创建组
groupdel 组名           # 删除组
gpasswd -a 用户 组      # 添加用户到组
gpasswd -d 用户 组      # 从组移除用户
groups 用户名           # 查看用户所属组

chage -l 用户名         # 查看密码过期信息
chage -M 90 用户名      # 90 天强制改密码
```

## 八、进程管理

```bash
ps                      # 当前终端进程
ps aux                  # 所有进程（详细）
ps -ef                  # 另一种格式
ps aux | grep python
ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head  # 按内存排序

pstree                  # 树形显示
pstree -p               # 显示 PID

top                     # 实时任务管理器
# top 中快捷键：
# q 退出  k 杀进程  M 按内存排序  P 按CPU排序  1 显示所有CPU

htop                    # 更美观（需安装）

kill 进程ID             # 发 SIGTERM
kill -9 进程ID          # 强制杀（SIGKILL）
kill -15 进程ID         # SIGTERM（默认）
killall 进程名          # 按名字结束
pkill -f "关键词"       # 按命令行匹配
pgrep -f "关键词"       # 查找 PID

jobs                    # 后台任务
bg %1                   # 挂起任务放后台
fg %1                   # 后台任务调前台
Ctrl + Z                # 挂起当前前台任务
command &               # 后台运行

nohup command &         # 后台运行，退出终端不停止
nohup command > out.log 2>&1 &   # 常用组合
disown                  # 脱离终端

# 优先级
nice -n 10 命令         # 以指定 nice 值启动（-20 最高，19 最低）
renice -n 5 -p PID      # 修改进程 nice
ionice -c 2 -n 7 -p PID # 修改 IO 优先级

# /proc 文件系统
ls /proc/PID/           # 进程信息目录
cat /proc/PID/cmdline   # 命令行
cat /proc/PID/environ   # 环境变量
cat /proc/PID/status    # 状态
ls -l /proc/PID/fd/     # 打开的文件描述符
cat /proc/PID/limits    # 资源限制

# 后台任务管理
screen / tmux           # 见“终端复用器”章节
```

## 九、磁盘与内存管理

```bash
df -h                   # 磁盘分区使用情况
df -i                   # inode 使用情况
df -T                   # 显示文件系统类型

du -sh 目录名           # 目录总大小
du -sh *                # 当前目录下每个文件/文件夹
du -h --max-depth=1     # 一级目录大小
du -ah | sort -h        # 按大小排序
du -sh --exclude="*.log" 目录  # 排除

free -h                 # 内存使用
free -m                 # MB
free -g                 # GB
cat /proc/meminfo       # 详细内存信息

lsblk                   # 磁盘分区结构
lsblk -f                # 显示文件系统
fdisk -l                # 查看所有磁盘分区（需 root）
parted -l               # 查看分区

mount                   # 查看已挂载
mount /dev/sdb1 /mnt    # 挂载
umount /mnt             # 卸载
umount -l /mnt          # 懒卸载（等待使用结束）
findmnt                 # 查看挂载树

sync                    # 缓存写入磁盘
echo 3 > /proc/sys/vm/drop_caches  # 清空缓存（慎用）

# 磁盘使用分析
ncdu /home              # 交互式（需安装）
duf                     # 更好的 df（需安装）
```

## 十、网络命令

```bash
# 网卡信息
ifconfig                # 旧版（需 net-tools）
ip addr                 # 新版推荐
ip a                    # 简写
ip link                 # 链路层
ip -s link              # 显示统计

# 连通性
ping 域名/IP            # 测试连通
ping -c 4 8.8.8.8       # ping 4 次
ping -i 0.5 目标        # 间隔 0.5s
ping6 目标              # IPv6

# HTTP 请求
curl http://example.com
curl -I http://...      # 只看响应头
curl -O 下载链接        # 下载
wget 下载链接           # 下载（支持断点续传）
wget -c 下载链接        # 断点续传
wget -r -p -k http://example.com  # 镜像整站

# 端口与连接
netstat -tulnp          # 监听端口（旧）
ss -tulnp               # 新版（更快）
ss -tanp                # 所有 TCP
ss -s                   # 统计
lsof -i :80             # 查看占用 80 端口
fuser -n tcp 80         # 另一种查看

# 端口测试
telnet 主机 端口        # 测试端口
nc -zv 主机 端口        # netcat
nc -zv 主机 80-90       # 端口范围
nmap 目标IP             # 端口扫描
nmap -p 1-1000 目标     # 指定范围

# DNS
host 域名               # 查 IP
nslookup 域名           # DNS 查询
dig 域名                # 详细 DNS
dig +short 域名         # 简洁
dig @8.8.8.8 域名       # 指定 DNS
dig -x IP               # 反向查询

# 路由
route -n                # 路由表（旧）
ip route                # 路由表（新）
traceroute 目标         # 路由追踪
mtr 目标                # 更好（结合 ping + traceroute）
tracepath 目标          # 不需要 root

# ARP
arp -a                  # ARP 缓存（旧）
ip neigh                # ARP 缓存（新）

# 网络管理
nmcli device status     # NetworkManager
nmcli con show          # 连接
nmtui                   # 文本界面
```

---

# 第二部分：文本处理

## 十一、文本处理命令

```bash
sort 文件名             # 排序
sort -r 文件名          # 降序
sort -n 文件名          # 按数字
sort -h 文件名          # 人类可读数字
sort -k2 文件名         # 按第2列
sort -t',' -k2 文件名   # 逗号分隔，第2列
sort -u 文件名          # 去重排序
sort -f 文件名          # 忽略大小写

uniq                    # 去重（需先排序）
sort file.txt | uniq
sort file.txt | uniq -c # 统计次数
sort file.txt | uniq -d # 只显示重复行
sort file.txt | uniq -u # 只显示不重复行

wc 文件名               # 行数、单词数、字节数
wc -l 文件名            # 行数
wc -w 文件名            # 单词数
wc -c 文件名            # 字节数
wc -m 文件名            # 字符数

cut -d',' -f1 file.csv  # 逗号分隔，第1列
cut -d',' -f1,3 file    # 第1、3列
cut -d',' -f1-3 file    # 第1到3列
cut -c1-10 file.txt     # 前10字符
cut -c1,5,10 file.txt   # 指定字符位置

paste file1 file2       # 按行合并（默认 TAB）
paste -d',' f1 f2       # 指定分隔符
paste -s file           # 所有行合并成一行

join file1 file2        # 按共同字段合并
join -t',' -1 1 -2 2 f1 f2  # 指定分隔符和字段

tr 'a-z' 'A-Z' < file   # 小写转大写
tr -d '\n' < file       # 删除换行
tr -s ' ' < file        # 压缩连续空格
tr -c 'a-zA-Z' '\n' < file  # 非字母替换为换行
```

## 十二、sed/awk 进阶

### sed 进阶

```bash
# 基础
sed 's/old/new/' file           # 替换每行第一个
sed 's/old/new/g' file          # 替换全部
sed 's/old/new/2' file          # 替换每行第2个
sed -i 's/old/new/g' file       # 原地修改
sed -i.bak 's/old/new/g' file   # 备份后修改

# 行范围
sed '2,5d' file                 # 删除 2-5 行
sed '2,5p' file                 # 打印 2-5 行
sed -n '2,5p' file              # 只打印 2-5 行
sed '5,$d' file                 # 删除第5行到最后
sed '1!d' file                  # 只保留第1行
sed '$d' file                   # 删除最后一行

# 模式匹配
sed '/pattern/d' file           # 删除包含 pattern 的行
sed -n '/start/,/end/p' file    # 打印 start 到 end 之间
sed '/start/,/end/d' file       # 删除
sed '/pattern/!d' file          # 只保留匹配行

# 多行处理
sed 'N; s/\n/ /' file           # 合并两行为一行
sed 'N; s/\n//' file            # 删除换行
sed ':a; N; $!ba; s/\n/,/g' file  # 所有行合并为一行

# 使用变量（双引号才能展开）
name="小明"
sed "s/NAME/${name}/g" file

# 多个表达式
sed -e 's/old1/new1/g' -e 's/old2/new2/g' file
sed 's/old1/new1/g; s/old2/new2/g' file

# 正则分组引用
echo "2024-01-15" | sed 's/\(....\)-\(..\)-\(..\)/\3\/\2\/\1/'
# 15/01/2024

# 扩展正则
sed -E 's/(a|b)+/X/g' file

# 只输出匹配部分
echo "abc123def" | sed 's/[^0-9]//g'   # 123

# 在匹配行后追加
sed '/pattern/a\新增的行' file
# 在匹配行前插入
sed '/pattern/i\插入的行' file
# 替换匹配行
sed '/pattern/c\替换后的行' file
```

### awk 进阶

```bash
# 基础
awk '{print $1}' file           # 第1列
awk '{print $1, $3}' file       # 第1、3列
awk '{print $NF}' file          # 最后一列
awk '{print $(NF-1)}' file      # 倒数第2列

# 分隔符
awk -F: '{print $1}' /etc/passwd
awk -F'[,;]' '{print $1}' file  # 多分隔符
awk 'BEGIN{FS=","; OFS="-"}{print $1,$2}' file

# 变量
awk -v name="小明" '{print name, $0}' file

# BEGIN/END
awk 'BEGIN{print "开始"} {print $1} END{print "结束"}' file

# 条件
awk '$3 > 100 {print $1, $3}' file
awk '$2 ~ /error/ {print $0}' file    # 匹配
awk '$2 !~ /error/ {print $0}' file   # 不匹配
awk 'NR > 1' file                      # 跳过第1行
awk 'NR % 2 == 0' file                 # 偶数行

# 数组（去重、统计）
awk '{count[$1]++} END{for(k in count) print k, count[k]}' file

# 求和 / 平均
awk '{sum+=$1} END{print sum}' file
awk '{sum+=$1} END{print sum/NR}' file

# 格式化输出
awk '{printf "%-10s %5d\n", $1, $2}' file

# 内置变量
NR      # 当前行号
NF      # 当前行字段数
FNR     # 当前文件的行号
FILENAME # 文件名
FS      # 字段分隔符
OFS     # 输出分隔符
RS      # 记录分隔符
ORS     # 输出记录分隔符

# 流程控制
awk '{if ($1 > 100) print "大"; else print "小"}' file

# 实战：Nginx 日志分析
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -10   # 访问最多 IP
awk '{print $7}' access.log | sort | uniq -c | sort -nr | head -10   # 访问最多 URL
awk '{sum+=$10} END{print sum/1024/1024 " MB"}' access.log           # 总流量
awk '$9 == 404 {print $7}' access.log | sort | uniq -c | sort -nr    # 404 URL
```

## 十三、正则表达式速查（grep/sed/awk 通用）

```
.       匹配任意单个字符（除换行）
^       行首
$       行尾
*       前一个字符 0 次或多次
+       前一个字符 1 次或多次（-E）
?       前一个字符 0 次或 1 次（-E）
[]      字符集合
[^]     排除字符集
|       或（-E）
()      分组（-E）
{n}     恰好 n 次（-E）
{n,}    至少 n 次
{n,m}   n 到 m 次
\b      单词边界
\B      非单词边界
\s      空白
\S      非空白
\d      数字（-P）
\w      单词字符（-P）
```

常用示例：

```bash
grep -E '^#' config.txt                    # 以 # 开头
grep -E 'error|fail' log.txt               # error 或 fail
grep -E '^[0-9]{11}$' file                 # 11位数字
grep -E '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'  # 邮箱
grep -E '^([0-9]{1,3}\.){3}[0-9]{1,3}$' file  # IP
grep -P '\d{4}-\d{2}-\d{2}' file           # 日期
grep -E '[[:space:]]+$' file               # 行尾空格
grep -E '^\s*$' file                       # 空行
```

## 十四、文本处理工具链补全

```bash
# diff / patch
diff file1 file2                # 比较
diff -u file1 file2             # 统一格式
diff -r dir1 dir2               # 递归比较
diff -y file1 file2             # 并排比较
vimdiff file1 file2             # 图形化比较
diff -u old new > patch.diff
patch < patch.diff              # 应用补丁
patch -R < patch.diff           # 撤销

# comm（比较已排序文件）
comm file1 file2                # 三列：仅1、仅2、共同
comm -12 file1 file2            # 只显示共同行

# split / csplit
split -l 1000 big.txt part_     # 每1000行拆一个
split -b 10M big.bin part_      # 每10M拆一个
csplit file '/pattern/' '{*}'   # 按模式拆分

# column / fmt / fold
column -t file                  # 对齐列
column -t -s',' file.csv        # 逗号分隔对齐
fmt -w 80 file                  # 每行80字符
fold -w 80 file                 # 强制折行

# expand / unexpand
expand file                     # Tab 转空格
unexpand file                   # 空格转 Tab

# rev / shuf
rev file                        # 反转每行
shuf file                       # 随机打乱行
shuf -n 5 file                  # 随机取5行

# dos2unix / unix2dos
dos2unix file                   # CRLF → LF
unix2dos file                   # LF → CRLF
file file.txt                   # 查看类型（含换行符）

# iconv（编码转换）
iconv -f GBK -t UTF-8 file > out
iconv -l                        # 列出所有编码

# tee
command | tee file              # 屏幕 + 文件
command | tee -a file           # 追加

# script（记录终端会话）
script session.log              # 开始录制
exit                            # 停止

# jq（JSON）
curl -s api.com | jq .
curl -s api.com | jq '.data[0].name'
echo '{"a":1}' | jq '.a'
jq '.[] | {name: .name}' file.json
jq -r '.name' file.json         # 原始输出（无引号）

# yq（YAML，需安装）
yq '.key' file.yaml
yq -i '.key = "value"' file.yaml

# xmlstarlet
xmlstarlet sel -t -v "//name" file.xml
```

## 十五、xargs 并行处理

```bash
# 基础
ls *.txt | xargs rm
cat files.txt | xargs -n 1 grep "hello"

# 处理带空格文件名
find . -name "*.txt" -print0 | xargs -0 rm

# 并行执行
echo {1..10} | xargs -n 1 -P 4 sleep
find . -name "*.jpg" | xargs -P 4 -I {} convert {} {}.png

# 替换字符串
find . -name "*.txt" | xargs -I {} cp {} /backup/{}

# 分批
ls | xargs -n 50 rm

# 与 find -exec 对比
find . -name "*.txt" -exec rm {} \;       # 每个文件一次 rm
find . -name "*.txt" -exec rm {} +        # 批量传参（类似 xargs）
find . -name "*.txt" -print0 | xargs -0 rm
```

---

# 第三部分：编辑器与终端

## 十六、Vim 编辑器速查

```bash
vim 文件名              # 打开
vim +10 文件名          # 打开并跳到第10行
vim +/pattern 文件名    # 打开并搜索

# 三种模式：普通、插入、命令

# 退出
:q                      # 退出
:q!                     # 强制退出
:w                      # 保存
:wq / ZZ / :x           # 保存退出
:w 新文件名             # 另存为

# 普通模式移动
h/j/k/l                 # 左下上右
w / b                   # 下/上一个单词
0 / ^ / $               # 行首/首个非空/行尾
gg / G                  # 文件首/尾
:n                      # 跳到第 n 行
Ctrl+f / Ctrl+b         # 下一页/上一页
%                       # 匹配括号
{ / }                   # 段落跳转

# 编辑
dd                      # 删除当前行
ndd                     # 删除 n 行
yy                      # 复制当前行
nyy                     # 复制 n 行
p / P                   # 粘贴到下方/上方
x / X                   # 删除光标字符/前一个
r                       # 替换单个字符
cw                      # 替换单词
u                       # 撤销
Ctrl+r                  # 重做
.                       # 重复上次操作

# 进入插入模式
i / I                   # 前/行首插入
a / A                   # 后/行尾插入
o / O                   # 下一行/上一行插入
s / S                   # 删除字符/整行后插入

# 可视模式
v                       # 字符可视
V                       # 行可视
Ctrl+v                  # 块可视
y / d / c               # 复制/删除/修改
> / <                   # 缩进/反缩进

# 搜索替换
/pattern                # 向下搜索
?pattern                # 向上搜索
n / N                   # 下一个/上一个
*                       # 搜索光标下单词
:%s/old/new/g           # 全局替换
:%s/old/new/gc          # 替换前确认
:5,10s/old/new/g        # 5-10 行替换

# 分屏
:sp 文件                # 水平分屏
:vsp 文件               # 垂直分屏
Ctrl+w h/j/k/l          # 切换窗口
Ctrl+w q                # 关闭当前窗口

# 标签页
:tabnew 文件
:tabn / :tabp           # 下/上一个标签
:tabc                   # 关闭当前标签

# 宏
qa                      # 开始录制到寄存器 a
q                       # 停止录制
@a                      # 执行宏 a
10@a                    # 执行 10 次

# 寄存器
"ayy                    # 复制到寄存器 a
"ap                     # 从寄存器 a 粘贴
:reg                    # 查看所有寄存器

# 配置文件 ~/.vimrc
set number              # 显示行号
set relativenumber      # 相对行号
set tabstop=4           # Tab 宽度
set shiftwidth=4        # 缩进宽度
set expandtab           # Tab 转空格
set autoindent          # 自动缩进
set hlsearch            # 高亮搜索
set ignorecase          # 忽略大小写
set smartcase           # 智能大小写
syntax on               # 语法高亮
```

## 十七、nano / emacs 速查

```bash
# nano（简单易用）
nano 文件
# Ctrl+O 保存  Ctrl+X 退出  Ctrl+W 搜索  Ctrl+K 剪切行
# Ctrl+U 粘贴  Ctrl+G 帮助  Ctrl+\ 替换
# Alt+U 撤销  Alt+E 重做

# emacs（强大）
emacs 文件
# Ctrl+X Ctrl+S 保存  Ctrl+X Ctrl+C 退出
# Ctrl+S 搜索  Ctrl+X Ctrl+F 打开文件
# Ctrl+X 2 水平分屏  Ctrl+X 3 垂直分屏
# Ctrl+G 取消当前命令
```

## 十八、终端与 Shell 环境

```bash
# Shell 类型
echo $SHELL             # 当前 shell
cat /etc/shells         # 所有可用 shell
chsh -s /bin/zsh        # 修改默认 shell

# Bash 启动文件加载顺序
# 登录 shell：/etc/profile → ~/.bash_profile → ~/.bashrc → /etc/bash.bashrc
# 非登录 shell：~/.bashrc

# 常用文件
~/.bashrc               # 交互式非登录 shell
~/.bash_profile         # 登录 shell
~/.profile              # 通用（非 bash 专用）
~/.bash_logout          # 退出时
/etc/profile            # 全局登录
/etc/bash.bashrc        # 全局交互
/etc/profile.d/*.sh     # 额外全局脚本

# 重新加载
source ~/.bashrc
. ~/.bashrc

# 提示符 PS1
echo $PS1
export PS1='\u@\h:\w\$ '   # 用户@主机:路径$
# \u 用户  \h 主机  \w 完整路径  \W 目录名  \d 日期  \t 时间
# \n 换行  \$ #或$  \! 历史编号

# 历史
history                 # 历史命令
history 10              # 最近10条
history -c              # 清空当前会话历史
history -w              # 写入 ~/.bash_history
history -d 100          # 删除第100条
HISTSIZE=10000          # 内存中历史数
HISTFILESIZE=20000      # 文件历史数
HISTCONTROL=ignoredups:erasedups  # 忽略重复

# 命令历史搜索
Ctrl+R                  # 反向搜索
!100                    # 执行第100条
!!                      # 上一条
!ssh                    # 最近以 ssh 开头的
!$                      # 上一条命令的最后一个参数
!*                      # 上一条命令的所有参数
!^                      # 上一条命令的第一个参数
Alt+.                   # 循环上一条命令参数

# 通配符
*       任意多个字符
?       任意一个字符
[abc]   a/b/c 中任一个
[a-z]   a-z 中任一个
{1,2}   1 或 2
{a..z}  a-z 所有
~       家目录
~user   指定用户家目录

# Brace Expansion
echo {1..10}            # 1 2 ... 10
echo {a..e}             # a b c d e
echo file{1,2,3}.txt    # file1.txt file2.txt file3.txt
mkdir -p project/{src,test,docs}
touch file{1..5}.log

# 环境变量
env                     # 所有变量
export VAR=value        # 导出变量
unset VAR               # 删除
printenv PATH           # 查看
echo $PATH              # 使用
export PATH=$PATH:/new/path  # 追加

# 重要环境变量
PATH        命令搜索路径
HOME        家目录
USER        当前用户
SHELL       当前 shell
PWD         当前目录
OLDPWD      上一个目录
LANG        语言
LC_ALL      本地化
EDITOR      默认编辑器
PS1         提示符
TERM        终端类型
```

## 十九、常用快捷键

```bash
# 终端控制
Ctrl + C        # 终止当前命令
Ctrl + Z        # 挂起当前命令
Ctrl + D        # 退出终端（同 exit）
Ctrl + L        # 清屏
Ctrl + S        # 暂停输出（恢复用 Ctrl+Q）
Ctrl + Q        # 恢复输出

# 行编辑
Ctrl + A        # 行首
Ctrl + E        # 行尾
Ctrl + U        # 删除光标前所有
Ctrl + K        # 删除光标后所有
Ctrl + W        # 删除光标前一个单词
Ctrl + Y        # 粘贴上一步删除的内容
Alt + D         # 删除光标后一个单词
Alt + B / F     # 光标按单词前后
Alt + T         # 交换前两个单词

# 历史
Ctrl + P / ↑    # 上一条
Ctrl + N / ↓    # 下一条
Ctrl + R        # 搜索历史
Ctrl + G        # 退出搜索

# 补全
Tab             # 自动补全
Tab Tab         # 列出所有候选
Alt + ?         # 列出候选

# 复制粘贴（终端里）
Ctrl + Shift + C   # 复制
Ctrl + Shift + V   # 粘贴

# 其他
Ctrl + X Ctrl + E   # 用编辑器编辑当前命令
!!                  # 重复上一条
!关键词             # 执行最近以关键词开头的
```

## 二十、tmux / screen 终端复用器

```bash
# tmux
apt install tmux

# 会话
tmux                            # 启动
tmux new -s 会话名              # 命名会话
tmux ls                         # 列出会话
tmux attach -t 会话名           # 连接
tmux a                          # 连接最近会话
tmux kill-session -t 会话名     # 杀死
tmux kill-server                # 杀死所有

# 快捷键（先按 Ctrl+B）
?       # 帮助
d       # detach（脱离）
c       # 新窗口
,       # 重命名窗口
&       # 关闭窗口
n / p   # 下/上一个窗口
0-9     # 切换窗口
w       # 窗口列表
%       # 垂直分屏
"       # 水平分屏
方向键  # 切换分屏
x       # 关闭分屏
z       # 最大化/还原
{ / }   # 交换分屏
[       # 复制模式（q 退出）
]       # 粘贴
t       # 显示时钟
:       # 命令模式
[       # 滚动模式，方向键或 PgUp/PgDn

# 配置文件 ~/.tmux.conf
set -g mouse on                 # 鼠标支持
set -g base-index 1             # 窗口从 1 开始
setw -g pane-base-index 1       # 分屏从 1 开始
set -g history-limit 10000      # 历史行数

# screen（旧版替代）
screen                          # 启动
screen -S 名字                  # 命名
screen -ls                      # 列出
screen -r 名字                  # 恢复
screen -d -r 名字               # 强制恢复
Ctrl+A d                        # detach
Ctrl+A c                        # 新窗口
Ctrl+A n/p                      # 切窗口
Ctrl+A "                        # 窗口列表
Ctrl+A S                        # 水平分屏
Ctrl+A |                        # 垂直分屏
Ctrl+A Tab                      # 切换分屏
Ctrl+A X                        # 关闭分屏
```

---

# 第四部分：Shell 脚本编程

## 二十一、Shell 脚本基础

```bash
#!/usr/bin/env bash
# Shebang：指定解释器
# 用 env 方式更可移植（自动找 PATH 中的 bash）

# 执行方式
chmod +x script.sh && ./script.sh    # 加执行权限后运行
bash script.sh                       # 用 bash 运行
source script.sh                     # 在当前 shell 中运行（能修改环境）

# 注释
# 单行注释
: '
多行注释（用 : 和单引号）
第二行
'

# 基本结构
#!/usr/bin/env bash
set -euo pipefail    # 严格模式：错误退出、未定义变量报错、管道错误传播

main() {
    echo "Hello, World!"
}

main "$@"
```

## 二十二、Shell 变量与参数

```bash
# 变量定义（等号两边不能有空格）
name="小明"
age=18
readonly PI=3.14        # 只读
unset name              # 删除

# 引用
echo "$name"            # 双引号：展开变量
echo '$name'            # 单引号：不展开
echo "${name}你好"      # 推荐用 {}

# 默认值
${var:-default}         # var 未设置或为空 → default（不修改 var）
${var:=default}         # 未设置或为空 → 赋值 default 并返回
${var:+other}           # var 已设置 → other
${var:?error}           # 未设置 → 报错退出

# 长度/截取
${#var}                 # 长度
${var:2}                # 从索引 2 到结尾
${var:2:3}              # 从索引 2 取 3 个字符

# 特殊变量
$0                      # 脚本名
$1 $2 ...               # 位置参数
${10}                   # 第 10 个参数（必须用 {}）
$#                      # 参数个数
$@                      # 所有参数（每个独立）
$*                      # 所有参数（合并成一个）
$?                      # 上一条命令退出码
$$                      # 当前 PID
$!                      # 最后一个后台进程 PID
$_                      # 上一条命令的最后一个参数

# 遍历参数
for arg in "$@"; do
    echo "$arg"
done

# 数组
arr=("a" "b" "c")
echo "${arr[0]}"        # 第一个
echo "${arr[@]}"        # 所有元素
echo "${#arr[@]}"       # 元素个数
arr+=("d")              # 追加
unset arr[1]            # 删除

# 关联数组（Bash 4+）
declare -A map
map[name]="小明"
map[age]=18
echo "${map[name]}"
for key in "${!map[@]}"; do
    echo "$key = ${map[$key]}"
done

# 命令替换
now=$(date +%Y-%m-%d)
now=`date +%Y-%m-%d`    # 旧写法

# 算术
$(( 1 + 2 ))
$(( 10 / 3 ))           # 3
$(( 10 % 3 ))           # 1
a=5; ((a++)); echo $a   # 6
let "a = a + 1"

# 环境变量 vs 本地变量
export VAR=value        # 子进程可见
VAR=value               # 仅当前 shell
```

## 二十三、Shell 条件与循环

```bash
# if
if [ "$a" -gt 10 ]; then
    echo "大于10"
elif [ "$a" -eq 10 ]; then
    echo "等于10"
else
    echo "小于10"
fi

# [[ ]] 更强大（Bash 特有）
if [[ "$name" == "小明" ]]; then
    echo "匹配"
fi

# 数值比较
[ $a -eq $b ]    # 等于
[ $a -ne $b ]    # 不等
[ $a -gt $b ]    # 大于
[ $a -ge $b ]    # 大于等于
[ $a -lt $b ]    # 小于
[ $a -le $b ]    # 小于等于

# 字符串比较
[ "$a" = "$b" ]      # 相等
[ "$a" != "$b" ]     # 不等
[ -z "$a" ]          # 空
[ -n "$a" ]          # 非空
[[ "$a" < "$b" ]]    # 字典序比较

# 文件测试
[ -e file ]      # 存在
[ -f file ]      # 是普通文件
[ -d dir ]       # 是目录
[ -l file ]      # 是链接
[ -r file ]      # 可读
[ -w file ]      # 可写
[ -x file ]      # 可执行
[ -s file ]      # 非空
[ f1 -nt f2 ]    # f1 比 f2 新
[ f1 -ot f2 ]    # f1 比 f2 旧

# 逻辑
[ cond1 ] && [ cond2 ]    # 与
[ cond1 ] || [ cond2 ]    # 或
[ ! cond ]                # 非
[[ cond1 && cond2 ]]      # 更简洁

# case
case "$1" in
    start)
        echo "启动"
        ;;
    stop)
        echo "停止"
        ;;
    restart|reload)
        echo "重启"
        ;;
    *)
        echo "未知命令"
        exit 1
        ;;
esac

# for
for i in 1 2 3 4 5; do
    echo "$i"
done

for i in {1..10}; do
    echo "$i"
done

for i in $(seq 1 10); do
    echo "$i"
done

for i in {1..10..2}; do    # 步长 2
    echo "$i"
done

for ((i=0; i<10; i++)); do
    echo "$i"
done

for f in *.txt; do
    [ -e "$f" ] || continue    # 没有匹配时跳过
    echo "$f"
done

# while
count=0
while [ $count -lt 5 ]; do
    echo $count
    ((count++))
done

# 逐行读文件
while IFS= read -r line; do
    echo "$line"
done < file.txt

# 无限循环
while true; do
    ...
done

# until
until [ $count -ge 5 ]; do
    ((count++))
done

# break / continue
for i in {1..10}; do
    [ $i -eq 3 ] && continue
    [ $i -eq 7 ] && break
    echo $i
done

# select（菜单）
select opt in "选项1" "选项2" "退出"; do
    case $opt in
        "退出") break ;;
        *) echo "选择了 $opt" ;;
    esac
done
```

## 二十四、Shell 函数与数组

```bash
# 函数定义
greet() {
    echo "Hello, $1"
}

function greet2 {
    echo "Hello, $1"
}

# 调用
greet "小明"

# 参数
# 函数内 $1 $2 $@ $# 与脚本参数独立
func() {
    echo "参数个数：$#"
    echo "所有参数：$@"
}

# 返回值（只能是 0-255 的退出码）
check() {
    if [ -f "$1" ]; then
        return 0
    else
        return 1
    fi
}

if check /etc/passwd; then
    echo "存在"
fi

# 返回字符串（用 echo + 命令替换）
get_name() {
    echo "小明"
}
name=$(get_name)

# 局部变量
func() {
    local x=10       # 只在函数内有效
    echo $x
}

# 递归
factorial() {
    if [ $1 -le 1 ]; then
        echo 1
    else
        echo $(( $1 * $(factorial $(( $1 - 1 ))) ))
    fi
}
echo $(factorial 5)   # 120

# 数组
arr=("a" "b" "c")
arr[10]="k"           # 稀疏数组
echo "${arr[@]}"
echo "${!arr[@]}"     # 所有索引

# 遍历数组
for item in "${arr[@]}"; do
    echo "$item"
done
```

## 二十五、Shell 字符串操作

```bash
str="Hello World"

# 长度
${#str}                 # 11

# 截取
${str:0:5}              # Hello
${str:6}                # World
${str: -5}              # World（负号前有空格）

# 替换
${str/World/Python}     # Hello Python（替换第一个）
${str//l/L}             # HeLLo WorLd（替换所有）
${str/#Hello/Hi}        # 开头替换
${str/%World/Earth}     # 结尾替换

# 删除
${str#Hello }           # 从开头删除最短匹配
${str##*o}              # 从开头删除最长匹配
${str% *}               # 从末尾删除最短匹配
${str%% *}              # 从末尾删除最长匹配

# 大小写（Bash 4+）
${str,,}                # 全小写
${str^^}                # 全大写

# 文件名处理
path="/home/user/file.txt"
${path##*/}             # file.txt（basename）
${path%/*}              # /home/user（dirname）
${path%.*}              # /home/user/file（去扩展名）
${path##*.}             # txt（扩展名）

# 变量间接引用
name="USER"
echo ${!name}           # 等价于 $USER

# 默认值
${var:-default}
${var:=default}
${var:+value}
```

## 二十六、Shell 错误处理与调试

```bash
# 严格模式
set -e          # 命令失败立即退出
set -u          # 未定义变量报错
set -o pipefail # 管道中任一命令失败则失败
set -x          # 打印执行的每条命令（调试）
set +x          # 关闭

# 组合
set -euo pipefail

# trap（信号处理）
trap 'echo "清理..."; rm -f /tmp/tmpfile' EXIT
trap 'echo "收到 SIGINT"; exit 1' INT
trap 'echo "收到 SIGTERM"' TERM

# 常用信号
# EXIT  脚本退出时
# INT   Ctrl+C
# TERM  kill 默认信号
# ERR   命令失败（配合 set -e）

# 错误处理函数
error_exit() {
    echo "错误：$1" >&2
    exit 1
}

[ -f "$file" ] || error_exit "文件不存在"

# 捕获错误行号
trap 'echo "错误在第 $LINENO 行"' ERR

# 调试
bash -x script.sh        # 打印每条命令
bash -n script.sh        # 语法检查（不执行）
shellcheck script.sh     # 静态检查（推荐）

# shellcheck 常见问题
# SC2086：变量未加引号
# SC2046：命令替换未加引号
# SC2181：直接检查 $? 应改成 if 语句
```

## 二十七、Shell 脚本实战

### 备份脚本

```bash
#!/usr/bin/env bash
set -euo pipefail

SRC="/var/www"
DST="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=7

mkdir -p "$DST"
tar -czf "$DST/www_${DATE}.tar.gz" -C "$SRC" .

# 清理旧备份
find "$DST" -name "www_*.tar.gz" -mtime +$KEEP_DAYS -delete

echo "备份完成：$DST/www_${DATE}.tar.gz"
```

### 服务监控

```bash
#!/usr/bin/env bash
set -euo pipefail

SERVICE="nginx"
EMAIL="admin@example.com"

if ! systemctl is-active --quiet "$SERVICE"; then
    echo "$SERVICE 未运行，尝试重启..."
    systemctl restart "$SERVICE"
    sleep 3
    if ! systemctl is-active --quiet "$SERVICE"; then
        echo "$SERVICE 重启失败" | mail -s "服务告警" "$EMAIL"
        exit 1
    fi
fi
```

### 参数解析

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat << EOF
用法：$0 [-v] [-o 输出] 输入文件
    -v          详细模式
    -o 文件     指定输出文件
    -h          显示帮助
EOF
    exit 0
}

VERBOSE=false
OUTPUT=""

while getopts "vo:h" opt; do
    case $opt in
        v) VERBOSE=true ;;
        o) OUTPUT="$OPTARG" ;;
        h) usage ;;
        \?) usage ;;
    esac
done
shift $((OPTIND - 1))

INPUT="${1:-}"
[ -z "$INPUT" ] && { echo "缺少输入文件"; usage; }
[ ! -f "$INPUT" ] && { echo "文件不存在：$INPUT"; exit 1; }

$VERBOSE && echo "处理 $INPUT"
```

### 日志清理

```bash
#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/var/log/myapp"
DAYS=30

find "$LOG_DIR" -name "*.log" -mtime +$DAYS -exec gzip {} \;
find "$LOG_DIR" -name "*.log.gz" -mtime +90 -delete

echo "清理完成"
```

---

# 第五部分：系统管理

## 二十八、环境变量与别名

```bash
echo $PATH              # 查看 PATH
echo $HOME
env                     # 所有环境变量
export VAR=value        # 设置（临时）
export PATH=$PATH:/new  # 追加路径
unset VAR               # 删除

alias ll='ls -la'       # 设置别名
alias gs='git status'
alias ..='cd ..'
alias ...='cd ../..'
unalias ll              # 删除

# 永久生效
~/.bashrc               # 当前用户
~/.bash_profile         # 登录时
/etc/profile            # 全局
/etc/profile.d/*.sh     # 全局额外脚本

source ~/.bashrc        # 重新加载
```

## 二十九、系统信息

```bash
uname -a                # 内核和系统信息
uname -r                # 内核版本
uname -m                # 架构（x86_64/aarch64）
cat /etc/os-release     # 发行版信息
lsb_release -a          # 发行版（需 lsb-release）
cat /etc/issue          # 登录前信息

cat /proc/cpuinfo       # CPU 信息
lscpu                   # 友好的 CPU 信息
nproc                   # CPU 核心数
cat /proc/meminfo       # 内存
lsmem                   # 内存布局

hostname                # 主机名
hostnamectl             # 详细主机信息
hostnamectl set-hostname 新名  # 修改主机名

uptime                  # 运行时间和负载
# 输出：当前时间 运行时间 用户数 1/5/15分钟负载
date                    # 当前时间
cal                     # 日历
timedatectl             # 时间/时区信息
timedatectl set-timezone Asia/Shanghai  # 设置时区

whoami / id             # 用户信息
who / w / last          # 登录信息

# 系统启动
systemctl reboot        # 重启
systemctl poweroff      # 关机
shutdown -h now         # 立即关机
shutdown -h +10         # 10 分钟后关机
shutdown -r now         # 立即重启
shutdown -c             # 取消
```

## 三十、硬件信息与内核模块

```bash
# 硬件信息
lscpu                   # CPU
lsmem                   # 内存
lspci                   # PCI 设备（显卡、网卡等）
lsusb                   # USB 设备
lshw                    # 硬件总览（需 root）
lshw -short             # 简洁
dmidecode               # 主板/BIOS 信息（需 root）
dmidecode -t memory     # 内存详情
hwinfo                  # 详细硬件信息（需安装）

# 磁盘健康
smartctl -a /dev/sda    # SMART 信息（需 smartmontools）
smartctl -H /dev/sda    # 健康状态

# 温度/风扇
sensors                 # 温度传感器（需 lm-sensors）
sensors-detect          # 探测传感器

# 内核模块
lsmod                   # 已加载模块
modinfo 模块名          # 模块信息
modprobe 模块名         # 加载模块
modprobe -r 模块名      # 卸载模块
insmod /path/mod.ko     # 直接加载
rmmod 模块名            # 卸载
depmod -a               # 更新依赖

# 持久化模块
# /etc/modules-load.d/xxx.conf
# 写入模块名

# 内核参数
sysctl -a               # 所有参数
sysctl net.ipv4.ip_forward  # 查看
sysctl -w net.ipv4.ip_forward=1  # 临时修改
# 持久化：/etc/sysctl.d/99-custom.conf
```

## 三十一、软件包管理

```bash
# Debian / Ubuntu（apt）
apt update                      # 更新源
apt upgrade                     # 升级所有
apt full-upgrade                # 升级（可卸载依赖）
apt install 软件名
apt install -y 软件名           # 自动确认
apt install ./file.deb          # 安装本地 deb
apt remove 软件名               # 卸载（保留配置）
apt purge 软件名                # 彻底卸载
apt autoremove                  # 清理无用依赖
apt autoclean                   # 清理旧缓存
apt search 关键词
apt show 软件名
apt list --installed
apt list --upgradable
dpkg -l                         # 列出已安装
dpkg -L 软件名                  # 列出文件
dpkg -i file.deb                # 安装本地
dpkg -r 软件名                  # 卸载

# Red Hat / CentOS / Fedora（yum / dnf）
yum install 软件名
dnf install 软件名
dnf update
dnf remove 软件名
dnf search 关键词
dnf list installed
rpm -ivh file.rpm               # 安装
rpm -qa                         # 列出已安装
rpm -qf /path/to/file           # 文件属于哪个包
rpm -ql 软件名                  # 包的文件

# Arch（pacman）
pacman -S 软件名                # 安装
pacman -Syu                     # 升级系统
pacman -R 软件名                # 卸载
pacman -Rns 软件名              # 卸载+依赖+配置
pacman -Ss 关键词               # 搜索
pacman -Qs 关键词               # 搜索已安装
pacman -Ql 软件名               # 列出文件

# openSUSE（zypper）
zypper install 软件名
zypper update
zypper remove 软件名
zypper search 关键词

# 通用
snap install 软件名             # Snap
snap list
snap remove 软件名

flatpak install flathub 应用ID  # Flatpak
flatpak list
flatpak uninstall 应用ID

# 源码编译
./configure --prefix=/usr/local
make -j$(nproc)
sudo make install
sudo make uninstall             # 如果有

# 语言包管理
pip install 包                  # Python
npm install 包                  # Node.js
cargo install 包                # Rust
go install 包                   # Go
```

## 三十二、日志与系统启动

```bash
# 日志目录
/var/log/syslog         # Debian/Ubuntu 系统日志
/var/log/messages       # RHEL/CentOS 系统日志
/var/log/auth.log       # 认证日志（Ubuntu）
/var/log/secure         # 认证日志（RHEL）
/var/log/kern.log       # 内核日志
/var/log/dpkg.log       # 包管理日志
/var/log/apt/           # apt 日志
/var/log/nginx/         # Nginx 日志
/var/log/mysql/         # MySQL 日志

# 查看日志
tail -f /var/log/syslog
less /var/log/syslog
grep "error" /var/log/syslog
journalctl              # systemd 日志（推荐）

# journalctl
journalctl                      # 所有日志
journalctl -u 服务名            # 指定服务
journalctl -u nginx -f          # 实时跟踪
journalctl -n 100               # 最近 100 行
journalctl --since "1 hour ago"
journalctl --since today
journalctl --since "2024-01-01" --until "2024-01-02"
journalctl -p err               # 只看错误
journalctl -b                   # 本次启动
journalctl -b -1                # 上次启动
journalctl -k                   # 内核日志
journalctl -o json              # JSON 格式
journalctl --disk-usage         # 占用空间
journalctl --vacuum-size=500M   # 限制大小
journalctl --vacuum-time=7d     # 保留时间

# dmesg（内核环形缓冲）
dmesg                           # 内核日志
dmesg -T                        # 人类可读时间
dmesg -w                        # 实时跟踪
dmesg | tail
dmesg | grep -i error

# logrotate（日志轮转）
# /etc/logrotate.conf 主配置
# /etc/logrotate.d/ 子配置

# 示例配置
# /var/log/myapp/*.log {
#     daily
#     rotate 7
#     compress
#     delaycompress
#     missingok
#     notifempty
#     create 0644 www-data www-data
#     postrotate
#         systemctl reload myapp
#     endscript
# }

logrotate -d /etc/logrotate.conf   # 调试
logrotate -f /etc/logrotate.conf   # 强制运行

# 启动流程
# BIOS/UEFI → MBR/GPT → GRUB → 内核 → initramfs → systemd → targets

# systemd targets
systemctl get-default               # 当前默认 target
systemctl set-default multi-user.target  # 设置默认
systemctl isolate graphical.target  # 切换
systemctl list-units --type=target

# 常用 target
# poweroff.target     关机
# rescue.target       单用户
# multi-user.target   多用户命令行
# graphical.target   图形界面
# reboot.target       重启

# GRUB
update-grub                     # 更新 GRUB（Debian/Ubuntu）
grub-mkconfig -o /boot/grub/grub.cfg
# 编辑 /etc/default/grub 后执行 update-grub

# 单用户模式
# 启动时按 e 编辑内核行，末尾加 single 或 init=/bin/bash
# 或 systemctl rescue

# chroot
mount /dev/sda1 /mnt
mount --bind /dev /mnt/dev
mount --bind /proc /mnt/proc
mount --bind /sys /mnt/sys
chroot /mnt
```

## 三十三、systemd 服务管理

```bash
# 服务管理
systemctl start 服务名
systemctl stop 服务名
systemctl restart 服务名
systemctl reload 服务名         # 重载配置（不中断）
systemctl status 服务名
systemctl enable 服务名         # 开机自启
systemctl disable 服务名
systemctl is-enabled 服务名
systemctl is-active 服务名
systemctl mask 服务名           # 禁用（比 disable 更强）
systemctl unmask 服务名

# 列出
systemctl list-units --type=service
systemctl list-unit-files --type=service
systemctl list-dependencies 服务名

# 创建自定义服务
# /etc/systemd/system/myapp.service
```

```ini
[Unit]
Description=我的应用
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/myapp
Environment="NODE_ENV=production"
EnvironmentFile=/etc/myapp/env
ExecStart=/opt/myapp/start.sh
ExecStop=/opt/myapp/stop.sh
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal
# 资源限制
LimitNOFILE=65536
# 安全加固
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload         # 修改后重新加载
systemctl enable myapp
systemctl start myapp
```

```bash
# 日志
journalctl -u myapp -f
journalctl -u myapp --since today

# 其他
systemctl reboot
systemctl poweroff
systemctl suspend
systemctl hibernate
systemctl rescue
systemctl emergency
```

## 三十四、systemd timers

systemd timers 是 cron 的现代替代，集成日志、依赖管理、精准调度。

```bash
# 查看现有 timer
systemctl list-timers
systemctl list-timers --all
systemctl status 名字.timer

# 启用/禁用
systemctl enable --now 名字.timer
systemctl disable --now 名字.timer
```

创建自定义 timer：

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=每日备份

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh
```

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=每日凌晨 2 点运行备份

[Timer]
OnCalendar=daily
# 或 OnCalendar=*-*-* 02:00:00
# 或 OnCalendar=Mon..Fri 09:00
# 或 OnCalendar=*:0/15  （每15分钟）
Persistent=true
# Persistent：错过的时间若系统关机，开机后补运行
RandomizedDelaySec=300
# 随机延迟（避免同一时刻大量任务）

[Install]
WantedBy=timers.target
```

```bash
systemctl daemon-reload
systemctl enable --now backup.timer
systemctl list-timers

# OnCalendar 常用
# minutely / hourly / daily / weekly / monthly / yearly
# *-*-* *:*:00            每分钟
# *-*-* *:0/5:00          每5分钟
# *-*-* 02:00:00          每天 2 点
# Mon *-*-* 09:00:00      每周一 9 点
# *-*-01 00:00:00         每月1号
# 2024-01-01 00:00:00     指定时间
```

## 三十五、定时任务 cron / at

```bash
# cron
crontab -e                     # 编辑当前用户
crontab -l                     # 列出
crontab -r                     # 删除所有
crontab -u 用户名 -e           # 编辑指定用户（需 root）

# 格式
# ┌──────── 分钟 (0-59)
# │ ┌────── 小时 (0-23)
# │ │ ┌──── 日 (1-31)
# │ │ │ ┌── 月 (1-12)
# │ │ │ │ ┌ 周 (0-7，0/7 都是周日)
# * * * * * 命令
```

```bash
* * * * * cmd                   # 每分钟
*/5 * * * * cmd                 # 每5分钟
0 * * * * cmd                   # 每小时
0 2 * * * cmd                   # 每天 2 点
0 2 * * 1 cmd                   # 每周一 2 点
0 2 1 * * cmd                   # 每月1号
0 2 1 1 * cmd                   # 每年 1 月 1 日
*/15 9-17 * * 1-5 cmd           # 工作日 9-17 每15分钟
30 8 * * 2,4,6 cmd              # 周二、四、六 8:30
0 0 1,15 * * cmd                # 每月1、15号
@reboot cmd                     # 开机运行
@daily cmd                      # 同 0 0 * * *
@weekly cmd
@monthly cmd
@yearly cmd
```

```bash
# 重要：cron 中 % 需转义
0 2 * * * date >> /tmp/date_$(date +\%Y\%m\%d).log

# 系统级目录
/etc/crontab                    # 系统主配置（多一列用户）
/etc/cron.d/                    # 额外配置
/etc/cron.hourly/               # 每小时
/etc/cron.daily/                # 每天
/etc/cron.weekly/               # 每周
/etc/cron.monthly/              # 每月

# 权限控制
/etc/cron.allow                 # 白名单
/etc/cron.deny                  # 黑名单

# 日志
grep CRON /var/log/syslog
journalctl -u cron

# at（一次性任务）
at 10:00                         # 10:00 执行
at now + 1 hour
at midnight
at -l                           # 列出
at -r 任务号                    # 删除
at -c 任务号                    # 查看内容
# 输入命令后 Ctrl+D 结束

# batch（系统负载低时执行）
batch
# 输入命令后 Ctrl+D

# anacron（关机错过的任务开机后补运行）
# /etc/anacrontab
```

---

# 第六部分：权限与安全

## 三十六、权限与安全进阶

```bash
# umask（默认权限掩码）
umask                   # 查看（如 0022）
umask -S                # 符号形式
umask 027               # 设置
# 文件默认 666 - umask，目录默认 777 - umask

# SUID / SGID / Sticky Bit
chmod u+s 文件          # SUID：执行时以文件所有者身份
chmod g+s 目录          # SGID：新文件继承目录的组
chmod +t 目录           # Sticky：只有所有者可删除
chmod 4755 文件         # SUID + 755
chmod 2755 目录         # SGID + 755
chmod 1777 目录         # Sticky + 777（如 /tmp）

# 查找特殊权限文件
find / -perm -4000 -type f 2>/dev/null   # SUID 文件
find / -perm -2000 -type f 2>/dev/null   # SGID 文件

# ACL（访问控制列表）
getfacl 文件            # 查看 ACL
setfacl -m u:用户名:rw 文件   # 给用户授权
setfacl -m g:组名:rx 文件     # 给组授权
setfacl -x u:用户名 文件      # 删除
setfacl -b 文件               # 删除所有 ACL
setfacl -R -m u:用户名:rw 目录 # 递归

# sudoers
visudo                          # 安全编辑（推荐）
# 格式：用户 主机=(运行身份) 命令
# 例如：
# user1 ALL=(ALL:ALL) ALL
# %admin ALL=(ALL) NOPASSWD: ALL

# 系统用户文件
cat /etc/passwd
# 用户名:x:UID:GID:注释:家目录:shell
cat /etc/shadow                 # 密码哈希（需 root）
cat /etc/group
# 组名:x:GID:成员列表

# 校验
pwck                            # 检查 /etc/passwd
grpck                           # 检查 /etc/group

# 文件属性（chattr）
chattr +i 文件                  # 不可修改（连 root 也不行）
chattr +a 文件                  # 只能追加
chattr -i 文件                  # 取消
lsattr 文件                     # 查看属性
```

## 三十七、防火墙（ufw/iptables/nftables）

### ufw（Ubuntu 默认）

```bash
ufw status
ufw status verbose
ufw enable
ufw disable
ufw default deny incoming
ufw default allow outgoing

ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3000:3010/tcp
ufw allow from 192.168.1.0/24
ufw allow from 192.168.1.100 to any port 22
ufw deny 23/tcp
ufw delete allow 80/tcp
ufw reset
ufw --dry-run enable

ufw app list                     # 应用配置
ufw allow 'Nginx Full'
```

### iptables

```bash
# 查看
iptables -L
iptables -L -v -n
iptables -t nat -L

# 基本规则
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -j DROP

# 拒绝 IP
iptables -A INPUT -s 192.168.1.100 -j DROP

# 限制 SSH 暴力破解
iptables -A INPUT -p tcp --dport 22 -m limit --limit 3/minute --limit-burst 5 -j ACCEPT

# 端口转发
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

# 保存/恢复
iptables-save > rules.v4
iptables-restore < rules.v4

# 持久化（Debian/Ubuntu）
apt install iptables-persistent
netfilter-persistent save
netfilter-persistent reload

# 清空
iptables -F
iptables -t nat -F
iptables -X
```

### nftables（现代替代）

```bash
nft list ruleset                 # 查看
nft add table inet filter
nft add chain inet filter input '{ type filter hook input priority 0 ; }'
nft add rule inet filter input tcp dport 22 accept
nft add rule inet filter input tcp dport { 80, 443 } accept
nft add rule inet filter input drop
nft delete rule inet filter input handle N
nft flush ruleset

# 持久化：/etc/nftables.conf
systemctl enable nftables
systemctl reload nftables
```

### firewalld（RHEL/CentOS）

```bash
firewall-cmd --state
firewall-cmd --list-all
firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --zone=public --remove-port=80/tcp --permanent
firewall-cmd --reload
firewall-cmd --add-service=http --permanent
firewall-cmd --add-rich-rule='rule family="ipv4" source address="192.168.1.0/24" accept' --permanent
```

## 三十八、SELinux / AppArmor

```bash
# SELinux
getenforce                      # Enforcing / Permissive / Disabled
setenforce 0                    # 临时切换为 Permissive
setenforce 1                    # Enforcing

sestatus                        # 详细状态
ls -Z 文件                      # 查看 SELinux 上下文
ps -eZ                          # 进程上下文

# 修改上下文
chcon -t httpd_sys_content_t /var/www/html/file
restorecon -Rv /var/www/html    # 恢复默认

# 布尔值
getsebool -a
getsebool httpd_can_network_connect
setsebool -P httpd_can_network_connect on

# 策略管理
semanage fcontext -a -t httpd_sys_content_t "/myapp(/.*)?"
restorecon -Rv /myapp

# 配置 /etc/selinux/config
# SELINUX=enforcing / permissive / disabled

# 日志
ausearch -m avc -ts recent
sealert -a /var/log/audit/audit.log

# AppArmor
aa-status
aa-enforce /etc/apparmor.d/usr.sbin.nginx
aa-complain /etc/apparmor.d/usr.sbin.nginx
aa-disable /etc/apparmor.d/usr.sbin.nginx
apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx
```

## 三十九、SSH 远程管理

```bash
# 基础连接
ssh 用户名@主机IP
ssh -p 2222 用户名@主机IP
ssh 用户名@主机IP "命令"
ssh -i ~/.ssh/key 用户名@主机IP

# 免密登录
ssh-keygen -t ed25519 -C "comment"      # 推荐 ed25519
ssh-keygen -t rsa -b 4096               # RSA 4096
ssh-copy-id 用户名@主机IP
# 或手动
cat ~/.ssh/id_ed25519.pub | ssh 用户名@主机IP "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# SSH 配置文件 ~/.ssh/config
```

```
Host myserver
    HostName 192.168.1.100
    Port 2222
    User root
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host jumpserver
    HostName jump.example.com
    User jumpsuer

Host internalserver
    HostName 10.0.0.100
    User root
    ProxyJump jumpserver
```

```bash
# 端口转发
ssh -L 8080:localhost:80 用户名@远程主机       # 本地转发
ssh -R 9090:localhost:22 用户名@远程主机       # 远程转发
ssh -D 1080 用户名@远程主机                    # SOCKS5 代理
ssh -L 3306:db.internal:3306 用户名@跳板机     # 通过跳板访问内网 DB
ssh -J 跳板 目标                               # ProxyJump 简写

# 保持连接
ssh -o ServerAliveInterval=60 用户名@主机
# 或在 config 中设置

# 传输文件
scp file.txt 用户名@主机:/path/
scp 用户名@主机:/path/file.txt ./
scp -r 文件夹/ 用户名@主机:/path/
scp -P 2222 file.txt 用户名@主机:/path/    # 注意 -P 大写
scp -i key file.txt 用户名@主机:/path/

# sftp
sftp 用户名@主机
# 交互：ls cd put get mkdir rm lcd lpwd lls
sftp> put local.txt /remote/
sftp> get /remote/file.txt ./

# sshfs（挂载远程目录）
sshfs 用户名@主机:/远程路径 /本地挂载点
fusermount -u /本地挂载点                       # 卸载

# 服务端配置 /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 22222
AllowUsers user1 user2
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 3
```

```bash
systemctl restart sshd
```

## 四十、加密与哈希

```bash
# 哈希
md5sum 文件                     # MD5（不安全，只校验完整性）
sha1sum 文件                    # SHA1（不安全）
sha256sum 文件                  # SHA256（推荐）
sha512sum 文件
sha256sum -c checksums.txt      # 校验
# checksums.txt 格式：<哈希>  <文件名>

# 生成哈希文件
sha256sum file1 file2 > checksums.txt

# openssl
openssl dgst -sha256 文件
openssl rand -base64 32         # 生成随机 base64
openssl rand -hex 32            # 生成随机 hex

# 对称加密（aes-256-cbc）
openssl enc -aes-256-cbc -salt -in file.txt -out file.enc
openssl enc -d -aes-256-cbc -in file.enc -out file.txt

# 生成密钥对
openssl genrsa -out private.key 4096
openssl rsa -in private.key -pubout -out public.key

# 自签名证书
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# gpg
gpg --gen-key                   # 生成密钥
gpg --list-keys
gpg --export -a "user" > public.key
gpg --import public.key
gpg -e -r "user" file           # 加密
gpg -d file.gpg                 # 解密
gpg -s file                     # 签名
gpg --verify file.sig file      # 验证

# 密码哈希（用于用户）
openssl passwd -6               # SHA-512 crypt
mkpasswd -m sha-512             # 需 whois 包

# fail2ban（防暴力破解）
apt install fail2ban
# /etc/fail2ban/jail.local
# [sshd]
# enabled = true
# maxretry = 3
# bantime = 1h
systemctl enable fail2ban
systemctl restart fail2ban
fail2ban-client status
fail2ban-client status sshd
fail2ban-client set sshd unbanip 1.2.3.4
```

---

# 第七部分：磁盘与文件系统

## 四十一、文件系统与磁盘管理

```bash
# 查看磁盘
lsblk                           # 块设备
lsblk -f                        # 含文件系统
blkid                           # 设备 UUID
fdisk -l                        # 分区表（需 root）
parted -l
df -hT                          # 挂载点与类型

# 分区（MBR：fdisk，GPT：gdisk 或 parted）
fdisk /dev/sdb
# 命令：n 新建  d 删除  p 打印  w 保存  q 退出
parted /dev/sdb
# (parted) mklabel gpt
# (parted) mkpart primary ext4 0% 100%
# (parted) print

# 格式化
mkfs.ext4 /dev/sdb1             # ext4
mkfs.xfs /dev/sdb1              # xfs
mkfs.btrfs /dev/sdb1            # btrfs
mkfs.vfat /dev/sdb1             # FAT32
mkfs.ntfs /dev/sdb1             # NTFS
mkswap /dev/sdb1                # Swap

# 检查修复
fsck /dev/sdb1                  # 需卸载
fsck -y /dev/sdb1               # 自动修复
e2fsck -f /dev/sdb1             # ext2/3/4 强制检查
tune2fs -l /dev/sdb1            # 查看 ext 文件系统信息
tune2fs -c 30 /dev/sdb1         # 每30次挂载检查
xfs_repair /dev/sdb1            # XFS 修复
xfs_info /dev/sdb1

# 挂载
mount /dev/sdb1 /mnt
mount -t ext4 /dev/sdb1 /mnt    # 指定类型
mount -o ro /dev/sdb1 /mnt      # 只读
mount -o remount,rw /mnt        # 重挂为读写
mount --bind /src /dst          # 绑定挂载
umount /mnt
umount -l /mnt                  # 懒卸载
fuser -m /mnt                   # 查看谁在用
lsof +D /mnt                    # 谁打开了文件

# /etc/fstab（开机自动挂载）
# <设备>          <挂载点>  <类型>  <选项>           <dump> <pass>
# UUID=xxx        /         ext4    defaults         0      1
# /dev/sdb1       /data     xfs     defaults,noatime 0      2
# tmpfs           /tmp      tmpfs   defaults,size=2G  0      0

mount -a                        # 测试 fstab
systemctl daemon-reload         # fstab 修改后

# 挂载选项
# defaults     rw,suid,dev,exec,auto,nouser,async
# noatime      不更新访问时间（性能）
# ro           只读
# rw           读写
# noexec       禁止执行
# nosuid       忽略 SUID
# nodev        忽略设备文件
# user         普通用户可挂载

# 磁盘信息
smartctl -a /dev/sda            # SMART
badblocks -sv /dev/sdb          # 坏道检测
hdparm -tT /dev/sda             # 速度测试

# 磁盘配额
quotacheck -cug /home
quotaon /home
edquota -u 用户名
repquota /home
```

## 四十二、LVM 逻辑卷管理

```bash
# 物理卷（PV）
pvcreate /dev/sdb /dev/sdc
pvs                             # 列出
pvdisplay
pvremove /dev/sdb

# 卷组（VG）
vgcreate myvg /dev/sdb /dev/sdc
vgs
vgdisplay
vgextend myvg /dev/sdd          # 扩容 VG
vgreduce myvg /dev/sdd          # 缩容 VG
vgremove myvg

# 逻辑卷（LV）
lvcreate -L 10G -n mylv myvg    # 创建 10G
lvcreate -l 100%FREE -n mylv myvg  # 用全部剩余
lvs
lvdisplay
lvremove /dev/myvg/mylv

# 扩容（在线）
lvextend -L +5G /dev/myvg/mylv
lvextend -l +100%FREE /dev/myvg/mylv
resize2fs /dev/myvg/mylv            # ext4
xfs_growfs /mnt                     # xfs

# 缩容（ext4 需先卸载）
umount /mnt
e2fsck -f /dev/myvg/mylv
resize2fs /dev/myvg/mylv 8G
lvreduce -L 8G /dev/myvg/mylv
mount /mnt
# XFS 不支持缩容！

# 快照
lvcreate -L 1G -s -n snap /dev/myvg/mylv
mount /dev/myvg/snap /mnt/snap
```

## 四十三、RAID 与 Swap

```bash
# RAID（mdadm）
apt install mdadm

# 创建 RAID 1
mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb1 /dev/sdc1

# 创建 RAID 5
mdadm --create /dev/md0 --level=5 --raid-devices=3 /dev/sdb1 /dev/sdc1 /dev/sdd1

# 查看
cat /proc/mdstat
mdadm --detail /dev/md0

# 添加/移除
mdadm --add /dev/md0 /dev/sde1
mdadm --fail /dev/md0 /dev/sdb1
mdadm --remove /dev/md0 /dev/sdb1

# 保存配置
mdadm --detail --scan >> /etc/mdadm/mdadm.conf
update-initramfs -u

# 停止
mdadm --stop /dev/md0

# Swap
mkswap /dev/sdb1
swapon /dev/sdb1
swapoff /dev/sdb1
swapon --show
free -h

# /etc/fstab
# /dev/sdb1  none  swap  sw  0  0

# Swap 文件
dd if=/dev/zero of=/swapfile bs=1M count=4096
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
# /etc/fstab
# /swapfile  none  swap  sw  0  0

# swappiness（使用 swap 倾向，0-100）
sysctl vm.swappiness
sysctl -w vm.swappiness=10
```

## 四十四、软链接与硬链接 ln

```bash
# 软链接
ln -s /实际路径/文件 链接名
ln -s /usr/bin/python3 /usr/local/bin/python
ln -sf 新目标 链接名            # 强制覆盖

# 硬链接
ln 源文件 硬链接名              # 只能文件，同文件系统

# 区别
# 软链接：跨文件系统、可指向目录、删除原文件链接失效、inode 不同
# 硬链接：同文件系统、不能指向目录、删除原文件不影响、inode 相同

# 查看
ls -li                          # inode 号
readlink 软链接名
readlink -f 软链接名            # 完整解析
stat 文件
find . -type l                  # 查找所有软链接
find . -xtype l                 # 查找失效软链接

# 删除软链接
rm 链接名                       # 不删原文件
rm -rf 链接名/                  # ⚠️ 危险！会删原目录内容

# 修复失效软链接
find . -xtype l -delete
```

---

# 第八部分：性能与监控

## 四十五、系统监控

```bash
# 整体
top                             # 实时
htop                            # 更美观
btop                            # 更现代（需安装）
glances                         # 全面
atop                            # 历史记录
nmon                            # 综合

# CPU
mpstat 1                        # 每个 CPU 核心
mpstat -P ALL 1
sar -u 1 5                      # 历史（需 sysstat）
pidstat -u 1                    # 进程级
vmstat 1                        # 虚拟内存+CPU+IO
vmstat 1 5                      # 每秒 1 次，共 5 次

# 内存
free -h
vmstat -s
cat /proc/meminfo
pmap PID                        # 进程内存映射
smem -tk                        # 按进程内存

# 磁盘 IO
iostat -x 1                     # 扩展统计
iotop                           # 进程级（需 root）
ioping .                        # IO 延迟
fio                             # 压力测试

# 网络
iftop                           # 实时流量
nethogs                         # 按进程
nload
bmon
bandwhich                       # 现代
ss -s
sar -n DEV 1                    # 网络统计

# 进程
ps aux --sort=-%mem | head
ps aux --sort=-%cpu | head
pgrep -f 关键词
pidstat 1
strace -p PID                   # 系统调用追踪
ltrace -p PID                   # 库调用
perf top                        # 性能分析

# 文件与用户
lsof                            # 打开的文件
fuser 文件                      # 谁在用
w                               # 登录用户
last / lastlog
```

## 四十六、性能分析工具

```bash
# perf（Linux 自带）
perf top
perf stat 命令
perf record -g 命令
perf report
perf trace 命令

# strace / ltrace
strace 命令                     # 跟踪系统调用
strace -p PID
strace -e trace=open,read 命令  # 只跟踪特定调用
strace -c 命令                  # 统计
ltrace 命令                     # 库调用

# gdb
gdb 程序
# 命令：run / break / next / step / print / bt / quit

# valgrind（内存调试）
valgrind --leak-check=full 程序
valgrind --tool=callgrind 程序  # 性能分析

# bpftrace / eBPF
bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s\n", comm); }'
# bcc 工具：execsnoop、opensnoop、biolatency 等

# 火焰图
# perf record -F 99 -g -p PID -- sleep 30
# perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg

# 内存分析
valgrind --tool=massif 程序
heaptrack 程序
```

## 四十七、系统调优

```bash
# 内核参数（sysctl）
sysctl -a
sysctl net.ipv4.ip_forward
sysctl -w net.ipv4.ip_forward=1
# 持久化：/etc/sysctl.d/99-custom.conf

# 常用调优
# 网络
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_fin_timeout = 15
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

# 文件描述符
fs.file-max = 2097152
# 用户级：/etc/security/limits.conf
# * soft nofile 65535
# * hard nofile 65535

# 虚拟内存
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# 资源限制（ulimit）
ulimit -a                       # 查看
ulimit -n 65535                 # 临时修改
# 持久化：/etc/security/limits.conf

# cgroups（资源控制）
systemd-cgtop
systemctl set-property 服务名 CPUQuota=50%
systemctl set-property 服务名 MemoryMax=1G

# CPU 频率
cpupower frequency-info
cpupower frequency-set -g performance

# 进程优先级
nice -n -10 命令
renice -n -5 -p PID
ionice -c 1 -n 0 -p PID
```

---

# 第九部分：网络进阶

## 四十八、网络进阶与诊断

```bash
# ip 子命令
ip addr show
ip addr add 192.168.1.100/24 dev eth0
ip addr del 192.168.1.100/24 dev eth0
ip link set eth0 up
ip link set eth0 down
ip link set eth0 mtu 1500
ip route show
ip route add 10.0.0.0/8 via 192.168.1.1
ip route del 10.0.0.0/8
ip neigh show                   # ARP
ip -s link                      # 统计

# DNS
cat /etc/resolv.conf
cat /etc/hosts
cat /etc/nsswitch.conf
systemd-resolve --status        # systemd-resolved
resolvectl status

# DNS 查询
dig 域名
dig +short 域名
dig @8.8.8.8 域名
dig -x IP
dig +trace 域名                 # 追踪 DNS 解析
host 域名
nslookup 域名
drill 域名

# 网络诊断
mtr 目标                        # 连续 traceroute
mtr --report 目标
tracepath 目标
traceroute -T 目标              # TCP
traceroute -I 目标              # ICMP

# 流量监控
iftop -i eth0
nethogs eth0
bmon
nload
bandwhich
iptraf-ng

# 带宽测试
speedtest-cli
iperf3 -s                       # 服务端
iperf3 -c 服务器                # 客户端

# 网络管理器
nmcli device status
nmcli con show
nmcli con up eth0
nmcli con add type ethernet ifname eth0 con-name myeth
nmtui                           # 文本界面

# netplan（Ubuntu 18+）
# /etc/netplan/*.yaml
# network:
#   version: 2
#   ethernets:
#     eth0:
#       dhcp4: true
netplan apply

# 网络命名空间
ip netns add ns1
ip netns list
ip netns exec ns1 bash
ip netns delete ns1

# 端口转发（socat）
socat TCP-LISTEN:8080,fork TCP:localhost:80

# nc（netcat）
nc -l 1234                      # 监听
nc 主机 1234                    # 连接
nc -zv 主机 80                  # 测试端口
nc -zv 主机 80-90
nc -u 主机 端口                 # UDP
# 文件传输
# 接收端：nc -l 1234 > file
# 发送端：nc 主机 1234 < file
```

## 四十九、curl 进阶（API 调试神器）

```bash
# 基础
curl http://example.com
curl -X POST http://example.com/api
curl -X PUT
curl -X DELETE
curl -X PATCH

# Header
curl -H "Content-Type: application/json" url
curl -H "Authorization: Bearer token"
curl -A "Mozilla/5.0" url       # User-Agent
curl -e "http://referer" url    # Referer

# 数据
curl -d "name=小明&age=18" -X POST url
curl -d '{"name":"小明"}' -H "Content-Type: application/json" url
curl --data-binary @file.json -H "Content-Type: application/json" url
curl -F "file=@/path/file.txt" url      # 文件上传
curl -F "name=小明" -F "file=@a.txt" url

# Cookie
curl -b "session=abc" url
curl -c cookies.txt url                 # 保存
curl -b cookies.txt url                 # 使用

# 重定向
curl -L url
curl -L --max-redirs 5 url

# 超时
curl --connect-timeout 5 --max-time 30 url

# 详细信息
curl -v url
curl -I url                     # 只看响应头
curl -i url                     # 头 + 体
curl -s url                     # 静默
curl -o /dev/null -s -w "%{http_code}\n" url  # 只看状态码

# 下载
curl -O url                     # 原文件名
curl -o myfile.zip url
curl -C - -O url                # 断点续传
curl --limit-rate 1M -O url     # 限速

# 代理
curl -x http://proxy:8080 url
curl --socks5 127.0.0.1:1080 url

# 证书
curl -k url                     # 忽略证书验证
curl --cacert ca.pem url
curl --cert client.pem --key key.pem url

# 组合示例
curl -s -X POST https://api.example.com/v1/users \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"name":"小明","age":18}' | jq .

# 常见替代
# httpie:  http POST api.com name=小明 age:=18
# xh:      xh POST api.com name=小明 age:=18
```

## 五十、tcpdump 抓包分析

```bash
# 基础
tcpdump -i eth0
tcpdump -i any
tcpdump -i eth0 -nn            # 不解析域名和端口名

# 过滤
tcpdump host 192.168.1.100
tcpdump src 192.168.1.100
tcpdump dst 192.168.1.100
tcpdump port 80
tcpdump port 80 or port 443
tcpdump portrange 1-1024
tcpdump tcp
tcpdump udp
tcpdump icmp

# 组合
tcpdump -i eth0 'tcp port 80 and host 192.168.1.100'
tcpdump -i eth0 'not port 22'
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'   # SYN 包
tcpdump -i eth0 'host 192.168.1.100 and (port 80 or port 443)'

# 保存/读取
tcpdump -w capture.pcap
tcpdump -r capture.pcap
tcpdump -C 100 -W 10 -G 3600 -w capture_%Y%m%d_%H%M%S.pcap

# 常用参数
-n              # 不解析域名
-nn             # 不解析域名和端口
-v / -vv / -vvv # 详细
-s 0            # 抓完整包
-c 100          # 抓 100 个停止
-A              # ASCII 输出
-X              # hex + ASCII
-e              # 显示链路层头
-w file         # 保存
-r file         # 读取
-i any          # 所有接口
-Q in / out / inout  # 方向

# 实战
# 抓 HTTP 请求头
tcpdump -i eth0 -A 'tcp port 80 and (tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420)'
# 抓 HTTP 响应头
tcpdump -i eth0 -A 'tcp port 80 and (tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x48545450)'
# 抓 DNS
tcpdump -i eth0 -nn port 53
# 抓 SSH
tcpdump -i eth0 -nn port 22

# 配合 Wireshark
# 用 tcpdump 保存，再用 Wireshark 打开分析
```

## 五十一、lsof 详细用法

```bash
# 端口占用
lsof -i :80
lsof -i :1-1024
lsof -i tcp
lsof -i udp
lsof -i @192.168.1.1
lsof -i tcp:80

# 进程
lsof -p PID
lsof -c nginx
lsof -u 用户名
lsof -u ^root                   # 排除 root

# 文件/目录
lsof /var/log/syslog
lsof +D /var/log/
lsof +d /var/log/               # 不递归

# 组合
lsof -i -a -p PID               # 进程 + 网络
lsof -i -a -u 用户名

# 恢复删除的文件
lsof | grep deleted
# 得到 PID 和 FD
cp /proc/PID/fd/FD /recover/path

# 常用
lsof -t -i:8080                 # 只输出 PID
kill -9 $(lsof -t -i:8080)
```

---

# 第十部分：传输与备份

## 五十二、rsync 同步备份

```bash
# 基础
rsync -av /源目录/ /目标目录/           # 注意结尾 /
rsync -av /源目录 /目标目录/            # 复制目录本身
rsync -avz /源/ user@host:/目标/        # 远程 + 压缩
rsync -avz user@host:/源/ /目标/
rsync -avz -e "ssh -p 2222" /源/ user@host:/目标/

# 常用参数
-a              # 归档（-rlptgoD）
-v              # 详细
-z              # 压缩
-P              # --partial --progress
--delete        # 目标中删除源没有的（同步）
--exclude="*.log"
--exclude-from=exclude.txt
--include="*.txt"
--dry-run       # 试运行
--bwlimit=1m    # 限速
--partial       # 支持断点
--progress      # 显示进度
--numeric-ids   # 不映射用户/组
--chown=user:group
--chmod=D755,F644

# 实战
rsync -avzP --delete /home/user/ /backup/user_$(date +%Y%m%d)/
rsync -avzP -e ssh --exclude="cache" /var/www/ root@backup:/backup/www/
rsync -avzP --exclude=".git" --exclude="node_modules" ./ user@host:/app/

# 同步删除（危险，先 --dry-run）
rsync -av --delete --dry-run /src/ /dst/
rsync -av --delete /src/ /dst/

# 镜像（-a 保持属性）
rsync -aHAX --delete /src/ /dst/
# -H 硬链接  -A ACL  -X xattr
```

## 五十三、scp / sftp / sshfs

```bash
# scp
scp file.txt user@host:/path/
scp user@host:/path/file.txt ./
scp -r dir/ user@host:/path/
scp -P 2222 file.txt user@host:/path/
scp -i key.pem file.txt user@host:/path/
scp -C file.txt user@host:/path/    # 压缩

# sftp
sftp user@host
sftp -P 2222 user@host
# 命令：
# ls, cd, pwd, mkdir, rm, rmdir
# lls, lcd, lpwd（本地）
# put 本地文件 [远程路径]
# get 远程文件 [本地路径]
# mput / mget（批量）
# bye / exit

# sshfs（挂载远程目录）
sshfs user@host:/remote /mnt/local
sshfs -p 2222 user@host:/remote /mnt/local
sshfs -o allow_other user@host:/remote /mnt/local
fusermount -u /mnt/local

# 自动挂载（/etc/fstab）
# user@host:/remote /mnt/local fuse.sshfs _netdev,allow_other 0 0

# 其他
lftp                            # 强大的 FTP/SFTP 客户端
ftp                             # 传统 FTP
```

## 五十四、备份工具

```bash
# dd（块级复制）
dd if=/dev/sda of=/dev/sdb bs=4M
dd if=/dev/sda of=disk.img bs=4M
dd if=disk.img of=/dev/sda bs=4M
dd if=/dev/zero of=file bs=1M count=1000    # 生成 1G 文件
dd if=/dev/urandom of=file bs=1M count=10   # 随机内容
dd if=/dev/cdrom of=cd.iso
# 显示进度（需 pv）
dd if=/dev/sda | pv | dd of=/dev/sdb bs=4M

# tar 备份
tar -czvf backup.tar.gz /重要目录/
tar -xzvf backup.tar.gz -C /恢复路径/

# rsync（推荐，见上文）
rsync -avzP --delete /src/ /backup/

# 增量备份工具
# rsnapshot（基于 rsync）
apt install rsnapshot
# /etc/rsnapshot.conf
rsnapshot daily
rsnapshot weekly
rsnapshot monthly

# borg（去重、加密）
apt install borgbackup
borg init --encryption=repokey /backup/repo
borg create /backup/repo::archive_$(date +%Y%m%d) /home
borg list /backup/repo
borg extract /backup/repo::archive_20240101
borg prune --keep-daily=7 --keep-weekly=4 /backup/repo

# restic（现代、快）
apt install restic
restic init --repo /backup/restic
restic -r /backup/restic backup /home
restic -r /backup/restic snapshots
restic -r /backup/restic restore latest --target /restore

# duplicity（加密、增量）
duplicity /home file:///backup/
duplicity restore file:///backup/ /restore/

# timeshift（系统快照）
timeshift --create
timeshift --list
timeshift --restore

# dump / restore（传统）
dump -0uaf backup.dump /
restore -rf backup.dump

# 云备份
rclone config
rclone sync /local remote:bucket/path
rclone copy /local remote:bucket/path
rclone ls remote:bucket

# 数据库备份
mysqldump -u root -p db > db.sql
mysqldump -u root -p --all-databases > all.sql
mysql -u root -p db < db.sql
pg_dump db > db.sql
psql db < db.sql
```

---

# 第十一部分：容器与虚拟化

## 五十五、容器与虚拟化

### Docker

```bash
# 安装
apt install docker.io
# 或官方脚本
curl -fsSL https://get.docker.com | sh

# 服务
systemctl start docker
systemctl enable docker
systemctl status docker

# 镜像
docker images
docker pull nginx
docker pull nginx:1.25
docker rmi nginx
docker rmi -f nginx             # 强制
docker image prune              # 清理未使用
docker image prune -a           # 清理所有未使用
docker history nginx

# 容器
docker run nginx
docker run -d --name web -p 8080:80 nginx
docker run -it ubuntu bash
docker run --rm ubuntu echo hi  # 运行后自动删除
docker run -v /host:/container nginx
docker run -e VAR=value nginx
docker run --network host nginx
docker run --restart=always nginx

# 查看
docker ps                       # 运行中
docker ps -a                    # 所有
docker ps -q                    # 只 ID
docker logs 容器
docker logs -f 容器
docker logs --tail 100 容器

# 管理
docker start 容器
docker stop 容器
docker restart 容器
docker rm 容器
docker rm -f 容器
docker exec -it 容器 bash
docker cp 文件 容器:/path/
docker cp 容器:/path/ 文件
docker inspect 容器
docker stats                    # 实时资源
docker top 容器

# 网络
docker network ls
docker network create mynet
docker network inspect mynet
docker network connect mynet 容器

# 卷
docker volume ls
docker volume create myvol
docker volume inspect myvol
docker volume rm myvol
docker volume prune

# 构建
docker build -t myimage .
docker build -t myimage:v1 -f Dockerfile.prod .
docker tag myimage user/myimage:v1
docker push user/myimage:v1

# Dockerfile 示例
# FROM python:3.11-slim
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY . .
# EXPOSE 8000
# CMD ["python", "main.py"]

# compose
docker compose up -d
docker compose down
docker compose ps
docker compose logs -f
docker compose build
docker compose pull

# docker-compose.yml
# services:
#   web:
#     image: nginx
#     ports:
#       - "8080:80"
#     volumes:
#       - ./html:/usr/share/nginx/html
#     depends_on:
#       - db
#   db:
#     image: postgres
#     environment:
#       POSTGRES_PASSWORD: secret
#     volumes:
#       - pgdata:/var/lib/postgresql/data
# volumes:
#   pgdata:

# 清理
docker system prune             # 清理未使用
docker system prune -a --volumes # 彻底清理
docker system df                # 磁盘占用
```

### Podman（无守护进程）

```bash
podman run -d --name web -p 8080:80 nginx
podman ps -a
podman exec -it web bash
podman build -t myimage .
podman generate systemd --new --name web > ~/.config/systemd/user/web.service
```

### LXC / LXD

```bash
# LXD
snap install lxd
lxd init
lxc launch ubuntu:22.04 mycontainer
lxc list
lxc exec mycontainer bash
lxc stop mycontainer
lxc delete mycontainer
lxc snapshot mycontainer snap1
lxc restore mycontainer snap1
```

### KVM / QEMU

```bash
# 检查支持
egrep -c '(vmx|svm)' /proc/cpuinfo

# 安装
apt install qemu-kvm libvirt-daemon-system virtinst bridge-utils

# 管理
virsh list --all
virsh start vm
virsh shutdown vm
virsh destroy vm                # 强制关闭
virsh undefine vm
virsh console vm

# 创建
virt-install --name vm1 --ram 2048 --vcpus 2 \
    --disk path=/var/lib/libvirt/images/vm1.qcow2,size=20 \
    --cdrom /path/to/iso \
    --network bridge=virbr0 \
    --graphics vnc

virt-manager                    # 图形界面
```

### Kubernetes 基础

```bash
# kubectl
kubectl get pods
kubectl get nodes
kubectl get svc
kubectl get all
kubectl describe pod 名字
kubectl logs pod 名字
kubectl exec -it pod 名字 -- bash
kubectl apply -f deploy.yaml
kubectl delete -f deploy.yaml
kubectl scale deployment/myapp --replicas=3
kubectl rollout status deployment/myapp
kubectl rollout undo deployment/myapp
kubectl port-forward pod/名字 8080:80
```

---

# 第十二部分：实战与速查

## 五十六、综合组合拳（常用实战）

```bash
# 查看日志最新100行并实时跟踪
tail -n 100 -f /var/log/syslog

# 查找大文件
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null

# 统计 IP 访问次数
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -20

# 批量重命名
for f in *.txt; do mv "$f" "${f%.txt}.md"; done

# 备份目录（带时间戳）
tar -czvf backup_$(date +%Y%m%d).tar.gz /重要目录/

# 查看端口占用并杀死
lsof -i :8080
kill -9 $(lsof -t -i:8080)

# 持续监控
watch -n 2 'ls -la | wc -l'

# 下载整站
wget -r -p -k http://example.com

# 快速 HTTP 服务
python3 -m http.server 8000

# 找最大10个文件
du -ah . | sort -rh | head -10

# 删除30天前日志
find /var/log -name "*.log" -mtime +30 -delete

# 计算目录大小排序
du -sh */ | sort -h

# 查看某个命令的所有路径
which -a python

# 批量替换（所有 .txt）
sed -i 's/old/new/g' *.txt

# 查找包含特定内容的文件
grep -rl "关键词" .

# 安全拷贝（只拷贝新文件）
rsync -av --ignore-existing /src/ /dst/

# 分析 Nginx 日志
# 访问最多 IP
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head
# 访问最多 URL
awk '{print $7}' access.log | sort | uniq -c | sort -nr | head
# 404 URL
awk '$9 == 404 {print $7}' access.log | sort | uniq -c | sort -nr | head
# 总流量
awk '{sum+=$10} END{print sum/1024/1024 " MB"}' access.log

# 实时监控网络连接数
watch -n 1 'ss -tan | awk "NR>1 {print \$1}" | sort | uniq -c'

# 找出占用 CPU 最高的进程
ps aux --sort=-%cpu | head -5

# 找出占用内存最高的进程
ps aux --sort=-%mem | head -5

# 批量杀进程
pkill -f "python.*script.py"

# 检查磁盘满
df -h | awk 'NR>1 && int($5) > 80 {print}'

# 查找重复文件（基于 MD5）
find . -type f -exec md5sum {} + | sort | uniq -w32 -dD

# 压缩并分卷
tar -czvf - /dir | split -b 100M - backup.tar.gz.part_

# 合并分卷
cat backup.tar.gz.part_* | tar -xzvf -

# 生成随机密码
openssl rand -base64 16
# 或
tr -dc 'A-Za-z0-9!@#$%' < /dev/urandom | head -c 20
```

## 五十七、速查小抄

### 文件操作

```bash
ls -la       # 看所有文件
cd ..        # 返回上级
rm -rf       # 删除（危险！）
cp -r        # 复制文件夹
mv           # 移动/重命名
```

### 查看内容

```bash
cat          # 整个文件
less         # 分页
tail -f      # 实时日志
head -n      # 前 N 行
grep         # 搜索
```

### 权限

```bash
chmod 755    # 文件权限
chown        # 改所有者
chgrp        # 改组
umask        # 默认掩码
sudo         # 提权
```

### 进程

```bash
ps aux | grep   # 找进程
kill -9         # 杀进程
top / htop      # 任务管理器
pkill -f        # 按名杀
pgrep -f        # 查 PID
```

### 网络

```bash
ping            # 测连通
ss -tulnp       # 看端口
curl / wget     # 下载
lsof -i :80     # 占用 80
ip a            # 网卡
mtr 目标        # 路由追踪
```

### 压缩

```bash
tar -czvf    # 压缩 .tar.gz
tar -xzvf    # 解压
tar -tzvf    # 查看
zip / unzip  # zip
xz / zstd    # 现代压缩
```

### 系统

```bash
df -h        # 磁盘
free -h      # 内存
uname -a     # 内核
uptime       # 运行时间
lscpu        # CPU
lsblk        # 磁盘
```

### SSH

```bash
ssh user@host              # 连接
ssh-keygen                 # 生成密钥
ssh-copy-id user@host      # 复制公钥
scp file user@host:/path   # 上传
-L / -R / -D               # 端口转发
```

### cron / systemd

```bash
crontab -e                 # 编辑定时任务
crontab -l                 # 查看
* * * * * command          # 分 时 日 月 周
systemctl start/stop/restart/status/enable/disable
journalctl -u 服务名 -f
systemctl list-timers
```

### 防火墙

```bash
ufw allow 22/tcp
ufw enable
ufw status

iptables -L -v -n
firewall-cmd --list-all
```

### tmux

```bash
tmux new -s name
tmux ls
tmux attach -t name
Ctrl+B d    # 脱离
Ctrl+B %    # 垂直分屏
Ctrl+B "    # 水平分屏
Ctrl+B c    # 新窗口
```

### rsync

```bash
rsync -avzP --delete 源/ 目标/
rsync -avzP -e ssh 源/ user@host:/目标/
```

### tcpdump

```bash
tcpdump -i eth0 -nn port 80 -w capture.pcap
tcpdump -r capture.pcap
```

### curl

```bash
curl -I url                      # 只看响应头
curl -X POST -d "data" url       # POST
curl -H "Auth: token" url        # 带 Header
curl -s url | jq .               # JSON 格式化
```

### 磁盘 / LVM

```bash
lsblk / df -h / du -sh
pvcreate / vgcreate / lvcreate
lvextend -l +100%FREE /dev/vg/lv
resize2fs /dev/vg/lv
```

### 日志

```bash
journalctl -u 服务名 -f
journalctl --since "1 hour ago"
tail -f /var/log/syslog
dmesg -T
```

### 安全

```bash
getenforce / setenforce
aa-status
fail2ban-client status
sha256sum 文件
gpg -e -r user file
```

---

