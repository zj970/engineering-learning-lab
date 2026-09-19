# Arch makepkg debug 包自动生成机制

## 本质

Arch 的 `makepkg` 可以根据 `/etc/makepkg.conf` 的 `OPTIONS` 自动生成 `*-debug` 包。即使 `PKGBUILD` 没有显式声明 debug 子包，只要全局启用了 `debug`，构建结果也可能包含额外的 debug 包。

典型配置：

```bash
OPTIONS=(strip docs !libtool !staticlibs emptydirs zipman purge debug lto)
```

这里的关键组合是：

```text
strip + debug
```

`strip` 负责从二进制文件中剥离符号，`debug` 负责把调试符号放到独立的 debug 包中。

---

## 原理

`makepkg.conf` 中的 `debug` 选项含义不是“打印调试日志”，而是“为包生成调试信息”。当它和 `strip` 同时启用时，`makepkg` 会：

1. 扫描包内 ELF 二进制或动态库；
2. 提取调试符号；
3. 在 `/usr/lib/debug/.build-id/` 下生成 build-id 对应的调试文件；
4. 额外产出一个 `包名-debug` 软件包。

因此，安装日志中可能出现：

```text
Packages (2) xxx  xxx-debug
```

哪怕 `PKGBUILD` 只有一个普通的 `package()` 函数。

---

## 流程

判断 debug 包来源：

```bash
rg -n "pkgname|package_.*debug|options|debug" PKGBUILD
rg -n "^OPTIONS=|debug|strip" /etc/makepkg.conf /etc/makepkg.conf.d
```

如果 `PKGBUILD` 没有显式 debug 子包，而 `/etc/makepkg.conf` 有 `debug`：

```bash
cp /etc/makepkg.conf ./makepkg-no-debug.conf
```

把：

```bash
OPTIONS=(strip docs !libtool !staticlibs emptydirs zipman purge debug lto)
```

改为：

```bash
OPTIONS=(strip docs !libtool !staticlibs emptydirs zipman purge !debug lto)
```

然后对单个包使用临时配置构建：

```bash
yay -S <aur-package> --cleanbuild --makepkgconf "$PWD/makepkg-no-debug.conf"
```

或在 AUR 目录中直接：

```bash
makepkg --config "$PWD/makepkg-no-debug.conf" -si
```

---

## 问题

常见误判：

- 看到 `xxx-debug` 就认为 `PKGBUILD` 一定显式写了 split package。
- 用 `pacman --overwrite /usr/lib/debug/...` 强行覆盖已有文件。
- 修改全局 `/etc/makepkg.conf` 后忘记恢复，影响所有后续 AUR 构建。

更干净的处理方式是：只为当前问题包使用临时 `makepkg.conf` 禁用 `debug`。

---

## 个人理解

`makepkg` 的 debug 包机制属于“构建策略”，不是“安装策略”。所以问题出在安装阶段，但根因往往要回到构建阶段查：

```text
PKGBUILD 是否显式声明 debug 子包
-> 没有
-> makepkg.conf 是否启用 debug
-> 启用
-> 自动产出 xxx-debug
-> pacman 安装时发现 /usr/lib/debug/.build-id 文件归属冲突
```

遇到这类问题，应该先关掉本次构建的 debug 产物，而不是覆盖已有文件。
