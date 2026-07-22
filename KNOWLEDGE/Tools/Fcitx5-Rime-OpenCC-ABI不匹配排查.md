# Fcitx5 Rime OpenCC ABI 不匹配排查

## 本质

Rime 在 Fcitx5 中通常以插件形式加载。若日志中出现 `Failed to load library for addon rime` 和 `undefined symbol`，问题往往不在输入方案配置，而在动态库 ABI/符号匹配。

典型链路：

```text
opencc 或 librime 升级
-> 运行时动态库版本与编译期预期不一致
-> fcitx5-rime 加载 /usr/lib/fcitx5/librime.so
-> 动态链接器解析 librime 依赖符号
-> opencc 符号缺失或 ABI 不匹配
-> Rime 插件加载失败
```

---

## 原理

`fcitx5-rime` 依赖 `librime`，`librime` 又依赖 `opencc`。如果 `opencc` 先升级，而 `librime` 还没有升级到匹配版本，就可能出现：

```text
Error: /usr/lib/librime.so.1: undefined symbol: opencc::Converter::Convert(...)
```

这类错误发生在动态链接阶段，含义是：

- 程序或插件已经找到 `.so` 文件；
- 但加载 `.so` 时发现某个符号无法解析；
- 插件不会进入正常初始化流程；
- 用户感知为输入法不可用或 Rime 消失。

它不同于 Rime 配置错误。配置错误通常会出现在 Rime 部署、词库、schema、用户目录等日志中，而不是动态链接器的 `undefined symbol`。

---

## 流程

1. 确认启动边界：

```bash
journalctl --list-boots
```

2. 查上次启动的输入法日志：

```bash
journalctl --user -b -1 --no-pager | rg -i 'rime|fcitx|undefined|symbol|coredump'
journalctl -b -1 --no-pager | rg -i 'rime|fcitx|undefined|symbol|coredump'
```

重点看：

```text
Failed to load library for addon rime
Could not load addon rime
undefined symbol
```

3. 查本次启动是否已恢复：

```bash
journalctl --user -b 0 --no-pager | rg -i 'rime|fcitx|undefined|symbol'
```

如果看到：

```text
Loaded addon rime
```

说明 Rime 插件已经正常加载。

4. 查包版本和包归属：

```bash
pacman -Q fcitx5 fcitx5-rime librime opencc
pacman -Qo /usr/lib/fcitx5/librime.so /usr/lib/librime.so.1 /usr/lib/libopencc.so.1.3
```

5. 查升级时间线：

```bash
rg 'librime|opencc|fcitx5-rime|fcitx5 ' /var/log/pacman.log
```

重点确认是否存在：

```text
opencc 先升级
librime 后升级
fcitx5-rime 未同步升级或无需升级
```

6. 验证当前动态链接状态：

```bash
ldd -r /usr/lib/fcitx5/librime.so
ldd -r /usr/lib/librime.so.1
```

如果没有 `undefined symbol` 或 `not found`，说明当前动态库依赖已经可解析。

7. 区分关机信号与崩溃：

```text
Fcitx 5.x -- Get Signal No.: 15
```

通常表示关机、重启或用户会话退出时收到 SIGTERM，不等价于崩溃。是否真的崩溃应看 `coredumpctl`：

```bash
coredumpctl list -b -1 --no-pager | rg -i 'rime|fcitx'
```

---

## 问题

常见误判：

- 看到 Rime 不可用就先删配置目录，忽略了动态库错误。
- 把关机时的 `Signal No.: 15` 当作崩溃根因。
- 只看当前启动正常，不回看上次启动的失败日志和包升级时间线。
- 只升级 `fcitx5-rime`，但实际需要匹配的是 `librime` 与 `opencc`。

---

## 个人理解

输入法问题要分层：

```text
桌面会话层：KWin/Plasma/SDDM 是否正常
输入法框架层：Fcitx5 是否启动、DBus 名称是否正常
插件层：fcitx5-rime 是否加载
动态库层：librime/opencc 符号是否匹配
配置层：schema、词库、用户配置是否正确
```

`undefined symbol` 属于动态库层问题，应该先查包版本、升级日志和 `ldd -r`。只有动态库加载成功后，再去排查 Rime 配置层问题。
