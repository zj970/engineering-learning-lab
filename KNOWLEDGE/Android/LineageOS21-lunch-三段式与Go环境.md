# LineageOS 21 lunch 三段式与 Go 环境影响

## 本质

在当前 `LineageOS 21 / Android 14` 源码树中，`lunch` 目标不再按传统两段式：

```bash
<product>-<variant>
```

而是要求三段式：

```bash
<product>-<release>-<variant>
```

对 `cas` 当前源码树来说，正确目标是：

```bash
lineage_cas-ap2a-userdebug
```

其中：

- `lineage_cas` 是产品名
- `ap2a` 是当前 LineageOS release 配置名
- `userdebug` 是构建变体

---

## 原理

当前 `build/envsetup.sh` 中的 `lunch` 明确要求：

```text
Valid combos must be of the form <product>-<release>-<variant>
```

`release` 值来自 LineageOS 的 release 配置。当前源码树中：

```bash
vendor/lineage/vars/aosp_target_release
```

记录：

```text
aosp_target_release=ap2a
```

同时：

```bash
vendor/lineage/release/release_config_map.mk
```

声明了：

```make
$(call declare-release-config, ap2a, ...)
```

因此 `lineage_cas-userdebug` 会因为缺少 `release` 段而直接被判定为非法格式。

---

## 流程

当 `lunch lineage_cas-userdebug` 报错时，应按下面顺序排查：

1. 先看报错是否是格式问题。
2. 如果提示必须是 `<product>-<release>-<variant>`，就补上 release 段。
3. 查当前 release：

```bash
cat vendor/lineage/vars/aosp_target_release
```

4. 对 `cas` 使用：

```bash
lunch lineage_cas-ap2a-userdebug
```

5. 如果出现 Go 标准库相关错误，再检查用户级 Go 配置。

---

## 问题

本次环境中还出现了第二个问题：用户级 Go 配置固定了：

```bash
GO111MODULE=on
```

位置：

```bash
/home/zj970/.config/go/env
```

这会干扰 Android 源码树中的预编译 Go 工具，导致类似错误：

```text
package unsafe is not in std
package internal/goversion is not in std
```

验证发现，临时关闭 module 模式后，Go 标准库解析恢复正常：

```bash
GO111MODULE=off prebuilts/go/linux-x86/bin/go list unsafe internal/goversion encoding
```

---

## 个人理解

这类问题容易被误判为“源码不是 Android 14”或“设备树没有同步完整”。实际上它包含两层：

- 第一层是 `lunch` 规则变化：目标格式从两段变成三段。
- 第二层是宿主机用户环境污染：`GO111MODULE=on` 影响 Android 内置 Go 工具。

排查时要先读错误格式，再看 release 配置，最后检查宿主机环境变量。不要一看到 `Device cas not found` 就立刻判断设备树缺失。
