# `cas` 衍生 AOSP 实机开发主线 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `Arch Linux` 上为 `Xiaomi Mi 10 Ultra / cas` 建立一套可刷入、可回滚、可 `adb root`、可长期做 Framework 调试的 `LineageOS 21 / Android 14 userdebug + GApps` 开发基线。

**Architecture:** 采用“恢复安全网 -> 源码环境 -> recovery 刷机闭环 -> 稳定开发机 -> Framework 最小调试闭环”的顺序推进。第一阶段只追求稳定开发机，不把日用功能、纯 AOSP 裸适配或自编 recovery 混入主线。

**Tech Stack:** Arch Linux、repo、AOSP/LineageOS 源码、`cas` 设备树、recovery、adb、fastboot、ccache

---

### Task 1: 建立恢复安全网

**Files:**
- Reference: 官方 `cas` fastboot 固件清单
- Reference: 社区 recovery 镜像与校验信息
- Output: 本地恢复资产记录

- [ ] **Step 1: 固化当前设备信息**

记录并保存：

```text
当前系统版本
bootloader 解锁状态
slot 信息
fastboot getvar all 中的关键字段
```

- [ ] **Step 2: 准备官方回滚资产**

确保已拿到并校验：

```text
cas 官方 fastboot 固件包
解压后的刷机脚本或镜像文件
Linux 下可用的 adb / fastboot
```

- [ ] **Step 3: 准备第一阶段 recovery**

确认社区现成 recovery 可用，并保留：

```text
下载链接
文件名
校验值
适用机型 cas
```

- [ ] **Step 4: 写恢复前检查表**

检查表至少包含：

```text
电量
数据线
USB 识别
官方固件在手
recovery 在手
fastboot 工具可执行
允许清数据
```

### Task 2: 建立 Arch Linux 源码环境

**Files:**
- Output: 本地源码目录规划
- Output: 环境依赖清单

- [ ] **Step 1: 规划目录**

固定：

```text
源码目录
ccache 目录
out 目录
下载缓存目录
```

优先放在 `/home` 大空间分区。

- [ ] **Step 2: 安装并验证基础依赖**

至少验证：

```text
repo
git
jdk
adb
fastboot
python
ccache
压缩与解包工具
```

- [ ] **Step 3: 同步基线源码**

锁定：

```text
LineageOS 21 / Android 14
cas 设备树
sm8250-common
对应 kernel
对应 vendor
```

- [ ] **Step 4: 固定构建目标**

第一阶段只维护：

```text
cas userdebug
```

不要同时扩展到 `user`、其它 ROM 或更高 Android 版本。

### Task 3: 建立 recovery 刷机闭环

**Files:**
- Output: Linux 下 recovery 刷机流程记录

- [ ] **Step 1: 验证 recovery 入口**

确认以下至少一项可稳定完成：

```text
进入 recovery
adb sideload
分区挂载或刷包入口
```

- [ ] **Step 2: 固定首次刷机顺序**

顺序固定为：

```text
进入 recovery
必要清理
刷 ROM
刷 GApps
首次启动
失败则回 recovery 或 fastboot 回滚
```

- [ ] **Step 3: 首次刷入基线系统**

目标是：

```text
LineageOS 21 / Android 14
cas
userdebug
GApps
```

- [ ] **Step 4: 记录失败分流**

至少区分：

```text
无法刷入
卡开机
系统起来但 adb 不通
系统起来但 GApps 异常
```

### Task 4: 达成稳定开发机

**Files:**
- Output: 开发必需功能检查表

- [ ] **Step 1: 验证开发调试链路**

至少确认：

```text
adb devices
adb root
logcat
USB 连接稳定
```

- [ ] **Step 2: 验证开发必需功能**

手工检查：

```text
开机
显示
触控
充电
数据分区
Wi-Fi
蓝牙
音频
```

- [ ] **Step 3: 保留稳定基线**

记录：

```text
源码 revision
构建时间
刷入包名
GApps 包名
首刷结果
已知问题
```

### Task 5: 跑通 Framework 最小闭环

**Files:**
- Output: 1 条 Framework 改动验证记录

- [ ] **Step 1: 选择低风险改动点**

优先选：

```text
简单文案
系统属性读取
可见性强的默认行为
调试日志
```

- [ ] **Step 2: 完成一次真机验证**

固定闭环：

```text
改源码
重新编译
刷机
开机
观察变化
记录结果
```

- [ ] **Step 3: 不扩展到复杂定制**

在最小闭环没稳定前，不进入：

```text
大范围 Framework 重构
Native/BSP 混合排障
相机/基带完善
更高版本迁移
```

### Task 6: 纳入学习系统

**Files:**
- Modify: `TASKS/todo.md`
- Create: `SESSIONS/对应日期.md`

- [ ] **Step 1: 将该主线写入任务系统**

至少包含：

```text
总目标
第一里程碑
阶段拆解
验证方式
完成标准
```

- [ ] **Step 2: 固定节奏**

按每周 `10h` 设计：

```text
工作日晚间：轻任务
周末：重任务
```

- [ ] **Step 3: 每阶段结束后沉淀**

至少记录：

```text
本阶段收获
暴露问题
下一步调整
```
