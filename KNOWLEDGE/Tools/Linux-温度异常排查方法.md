# Linux 温度异常排查方法

## 本质

CPU / GPU 温度异常不是单一温度数值问题，而是“负载、功耗、电源策略、显示链路、驱动状态、散热策略”共同作用的结果。

排查时不能直接问“哪个温度高”，而要问：

- 谁在消耗功耗
- 哪个设备没有进入省电状态
- 温度上升时是否有真实负载
- 是否是显示刷新率、电源管理或内核参数导致空闲功耗偏高

---

## 原理

### CPU 侧

需要同时看：

- `sensors` 中的 `Tctl` / CCD 温度
- `ps` / `top` 中的进程 CPU 占用
- `cpufreq` governor
- `amd_pstate` 或 Intel pstate 状态
- C-state / boost / 内核启动参数

### GPU 侧

对混合显卡笔记本，要分清：

- 独显是否 active / suspended
- 核显是否承担显示输出
- `gpu_busy_percent` 是否有真实 3D 负载
- 显示刷新率是否过高
- NVIDIA / AMD runtime power management 是否正常

### 开机日志侧

需要分层看：

- failed units：直接故障
- slow units：拖慢开机
- repeated warning：噪声或配置问题
- thermal / throttling / power 相关日志：温度和功耗直接证据

---

## 流程

1. 记录硬件和内核：

```bash
uname -a
lscpu
lspci -k | grep -A4 -i 'vga\|3d\|display'
```

2. 看开机耗时：

```bash
systemd-analyze
systemd-analyze blame
systemd-analyze critical-chain
systemctl --failed
```

3. 看错误日志：

```bash
journalctl -b -p warning..alert --no-pager
journalctl -b --no-pager | grep -Ei 'thermal|thrott|nvidia|amdgpu|power'
```

4. 采温度和功耗：

```bash
sensors
nvidia-smi
cat /sys/class/drm/card*/device/gpu_busy_percent
```

5. 同时看进程负载：

```bash
ps -eo pid,comm,%cpu,%mem,args --sort=-%cpu | head
```

6. 做对比实验：

- 240Hz 与 60Hz 对比
- 插电与电池对比
- dGPU active 与 suspended 对比
- 修改内核电源参数前后对比

---

## 问题

常见误判：

- 看到 GPU 温度就以为是独显在跑，其实可能是核显显示链路。
- 看到 CPU 温度高就以为有进程占用，其实可能是电源策略让空闲功耗高。
- 只看 `top`，不看 `sensors` / `PPT` / runtime power state。
- 把 KDE / portal warning 当作温度根因，忽略真正的功耗证据。

---

## 个人理解

温度排查要像性能分析一样做“证据闭环”：温度只是结果，功耗是直接原因，负载和电源策略是上游原因。没有对比实验前，不应该直接下结论或修改大量配置。
