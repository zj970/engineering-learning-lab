# Linux 网络接口识别与使用状态判断

## 本质

`ifconfig` 展示的是网络接口，不等于物理网卡列表。一条网络连接可能同时经过多个接口：

```text
应用 -> TUN 代理接口 -> 路由/NAT -> 物理网卡 -> 局域网或互联网
容器 -> veth -> Docker bridge -> NAT -> 物理网卡
```

因此，“接口存在”“接口启用”“链路可用”“被路由选中”“当前有流量”必须分开判断。

---

## 原理

常见接口名称及作用：

| 接口 | 典型作用 |
|---|---|
| `lo` | 本机回环，承载 `127.0.0.1` 和 `::1` 通信 |
| `enp*` / `eth*` | 有线物理网卡 |
| `wlp*` / `wlan*` | 无线物理网卡 |
| `tun*` / `tap*` / 代理名称 | VPN 或透明代理创建的隧道接口 |
| `docker0` | Docker 默认 bridge |
| `br-<ID>` | Docker Compose 等创建的用户自定义 bridge |
| `veth*` | 容器网络命名空间与宿主机 bridge 之间的虚拟网线 |

接口标志的含义：

- `UP`：管理员已启用接口。
- `RUNNING`：内核认为链路或虚拟端点可工作。
- `LOOPBACK`：本机回环接口。
- `POINTOPOINT`、`NOARP`：常见于 TUN/VPN，不使用普通以太网 ARP。
- RX/TX packets：累计计数，不是当前速率。

`UP` 和 `RUNNING` 都不能单独证明接口正在传输业务数据。配置了 IP 也只说明接口具备通信条件。

---

## 判断流程

先查看简洁状态：

```bash
ip -br link
ip -br addr
```

再判断指定目标实际走哪个接口：

```bash
ip route get 1.1.1.1
ip route get 192.168.51.11
```

输出中的 `dev` 是路由选中的接口，`src` 是使用的源地址。存在 VPN 或透明代理时，还应检查策略路由：

```bash
ip rule
ip route show table all
```

连续观察计数器，判断接口此刻是否有流量：

```bash
watch -d -n 1 'ip -s link show enp4s0; ip -s link show FlClash'
```

数字持续增加才表示采样期间有流量。要查看所有接口的实时速率，可使用 `bmon`、`nload` 或 `sar -n DEV 1`。

---

## Docker 网络映射

列出 Docker 网络及其完整 ID：

```bash
docker network ls --no-trunc
```

`br-2368c857ae9c` 通常对应 network ID 以 `2368c857ae9c` 开头的 bridge 网络。查看每个网络连接的容器：

```bash
docker network inspect $(docker network ls -q) \
  --format '{{.Name}} -> {{range .Containers}}{{.Name}} {{else}}(无运行容器){{end}}'
```

查看某个 bridge 下挂的宿主机接口：

```bash
ip link show master br-2368c857ae9c
```

bridge 只有 `UP`、没有 `RUNNING`，而且 RX/TX 长期不增长时，通常表示 Docker 网络定义仍然存在，但当前没有活动容器端点。

这类 bridge 只是清理候选，不能只凭 `DOWN` 判断可以删除。先查看网络所属的 Compose 项目和容器引用：

```bash
docker network inspect <network-ID> \
  --format 'name={{.Name}} project={{index .Labels "com.docker.compose.project"}} containers={{len .Containers}}'
```

确认不再需要后，应让 Docker 删除网络对象：

```bash
docker network rm <网络名称或ID>
```

不要直接执行 `ip link delete br-...`，否则只删除内核接口，没有同步 Docker 保存的网络状态。

---

## 常见问题

### 为什么代理接口和物理网卡都有大量流量？

同一批数据可能先经过 TUN 接口，再由代理程序通过物理网卡发送。两边计数都增长是正常现象，不能相加后当作真实业务流量。

### `dropped` 不为 0 就一定是网络丢包吗？

不一定。它可能来自内核队列、驱动、虚拟 bridge 广播或接口没有接收端。先观察计数是否持续增长，再结合网卡详细统计：

```bash
ip -s link show enp4s0
ethtool -S enp4s0
```

### `inet6 fe80::` 表示能访问 IPv6 互联网吗？

不表示。`fe80::/10` 是链路本地地址，只能用于当前二层链路；是否具备 IPv6 外网能力还要看全局 IPv6 地址和 IPv6 路由。

---

## 个人理解

判断接口是否“在用”必须先明确问题：是问物理出口、指定目标的路由、容器连接，还是当前实时流量。接口名称负责说明身份，路由负责说明去向，计数器变化负责说明此刻是否传输；三者结合才有可靠结论。
