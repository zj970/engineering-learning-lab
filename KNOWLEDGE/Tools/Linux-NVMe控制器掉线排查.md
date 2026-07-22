# Linux NVMe 控制器掉线排查

## 本质

NVMe 相关的文件系统错误不一定是文件系统本身导致的。很多场景中，真正的根因在更底层：NVMe 控制器掉线、PCIe 链路恢复失败、电源管理兼容性、SSD 固件缺陷或主板 BIOS 问题。

典型链路：

```text
NVMe 控制器掉线
-> 内核 reset 控制器
-> reset 失败或命令被 abort
-> 块设备返回 I/O error
-> ext4/btrfs 出现读写错误
-> 文件系统 journal abort 或 remount read-only
```

排查时不要只盯着 `EXT4-fs error`，要继续向上游追到 `nvme`、`pcie`、`aer`、`reset`、`timeout` 等内核日志。

---

## 原理

### NVMe SMART 字段

常用字段：

```text
critical_warning
temperature
available_spare
percentage_used
media_errors
num_err_log_entries
unsafe_shutdowns
```

关键区别：

- `media_errors`：介质或数据完整性错误。该字段增长时，硬件风险明显升高。
- `num_err_log_entries`：NVMe Error Information Log 的累计条目数，不是坏块数量。
- `critical_warning`：控制器给出的严重健康告警，非 0 时应优先备份和换盘评估。
- `percentage_used`：寿命消耗估计值，不是精确寿命倒计时。

如果出现：

```text
media_errors = 0
num_err_log_entries > 0
```

不能直接判定 SSD 有坏块。需要结合错误日志类型判断。例如 `Invalid Field in Command` 更像命令、驱动、固件或兼容性问题。

### 电源管理参数

`nvme_core.default_ps_max_latency_us=0`：

- 作用层级：NVMe 设备内部电源状态。
- 主要影响：禁用或限制 APST 深度省电。
- 排查价值：绕过部分 SSD 从低功耗状态唤醒失败导致的 `controller is down`。

`pcie_aspm=off`：

- 作用层级：PCIe 链路级电源管理。
- 主要影响：关闭 L0s/L1/L1.1/L1.2 等 ASPM 状态。
- 排查价值：绕过链路省电/恢复过程中的兼容性问题。

`pcie_port_pm=off`：

- 作用层级：PCIe Root Port/端口级电源管理。
- 主要影响：关闭端口电源管理。
- 排查价值：绕过端口层电源管理导致的设备掉线。

三者分别覆盖：

```text
NVMe 控制器内部省电
PCIe 链路省电
PCIe 端口省电
```

---

## 流程

1. 查看最近 boot：

```bash
journalctl --list-boots
```

2. 提取错误日志：

```bash
journalctl -b -2 -p err..alert --no-pager
journalctl -b -1 -p err..alert --no-pager
journalctl -b 0 -p err..alert --no-pager
```

3. 过滤存储相关内核日志：

```bash
journalctl -k -b 0 --no-pager | rg -i 'nvme|pcie|aer|reset|timeout|abort|I/O error|ext4|btrfs'
```

重点看：

```text
controller is down
will reset
reset failure
Host Aborted Command
I/O error
EXT4-fs error
Remounting filesystem read-only
```

4. 确认设备和挂载关系：

```bash
lsblk -o NAME,MODEL,SERIAL,SIZE,FSTYPE,MOUNTPOINTS,UUID
findmnt -no SOURCE,FSTYPE,OPTIONS /
findmnt -no SOURCE,FSTYPE,OPTIONS /home
```

5. 查看 SMART：

```bash
sudo smartctl -a /dev/nvme0n1
sudo smartctl -a /dev/nvme1n1
```

或安装 `nvme-cli` 后：

```bash
sudo nvme smart-log /dev/nvme0
sudo nvme smart-log /dev/nvme1
sudo nvme error-log /dev/nvme0
sudo nvme error-log /dev/nvme1
```

6. 如果内核日志提示电源管理问题，测试启动参数：

```text
nvme_core.default_ps_max_latency_us=0 pcie_aspm=off pcie_port_pm=off
```

重启后验证：

```bash
cat /proc/cmdline
cat /sys/module/nvme_core/parameters/default_ps_max_latency_us
```

7. 控制器稳定后，再离线检查文件系统：

```bash
sudo e2fsck -n /dev/nvme1n1p1
sudo e2fsck -f /dev/nvme1n1p1
```

对根分区或 `/home`，优先使用 Live USB 或救援环境，确保目标分区未挂载。

---

## 问题

常见误判：

- 看到 `EXT4-fs error` 就直接认为 ext4 是根因。
- 看到 `num_err_log_entries` 很大就认为 SSD 有大量坏块。
- 没有先备份就执行 `fsck -y`。
- 控制器还在掉线时反复修文件系统，导致问题扩大。
- 只看 SMART，不看 `journalctl -k` 中的 `controller is down` 和 reset 过程。
- 只加一个 `pcie_aspm=off`，但忽略内核明确提示的 `nvme_core.default_ps_max_latency_us=0` 和 `pcie_port_pm=off`。

---

## 个人理解

NVMe 掉盘排查要分层：文件系统是症状层，块设备是故障表现层，NVMe 控制器和 PCIe 电源管理才可能是根因层。

处理顺序应该是：

```text
备份数据
-> 读取日志证据
-> 判断是介质错误还是控制器/链路错误
-> 临时禁用高风险省电路径验证假设
-> 控制器稳定后再修文件系统
-> 最后再考虑固件、BIOS、插槽、内核版本或换盘
```

不要把 `fsck` 当作第一步。`fsck` 只能修复文件系统结构，不能修复 NVMe 控制器掉线。
