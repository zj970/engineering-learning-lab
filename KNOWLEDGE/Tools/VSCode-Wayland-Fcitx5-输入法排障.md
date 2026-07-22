# VS Code Wayland Fcitx5 输入法排障

## 本质

VS Code 在 Linux 桌面下是 Electron 应用。KDE Wayland 场景中，中文输入和剪贴板不是单一链路，而是多个层次协作：

```text
KDE / KWin Wayland 会话
-> Fcitx5 DBus 服务和 Wayland 输入法前端
-> Rime 插件与输入方案配置
-> Electron / Chromium Ozone 平台
-> VS Code 编辑器窗口
```

如果终端输入正常、VS Code 异常，不要直接删除 Rime 配置。应先确认 VS Code 到底走 Wayland 原生还是 XWayland，以及 Fcitx5 是否只有一个有效实例。

---

## 原理

Arch 的 `/usr/bin/code` 启动脚本通常会读取：

```text
~/.config/code-flags.conf
```

并把其中的参数追加给 VS Code 主程序。桌面文件 `/usr/share/applications/code.desktop` 一般只写：

```text
Exec=code %F
```

因此，若只在终端临时执行：

```bash
code --ozone-platform=wayland --enable-wayland-ime
```

只能影响这一次启动。通过桌面图标、URL handler 或已有窗口复用时，可能又回到不同参数组合。

`Warning: 'enable-wayland-ime' is not in the list of known options, but still passed to Electron/Chromium.` 的含义是：VS Code CLI 自己不认识该参数，但仍把参数传给 Electron/Chromium；它不是“参数完全没传”的证据。

---

## 流程

1. 确认 VS Code 命令入口：

```bash
which code
sed -n '1,120p' /usr/bin/code
code --version
```

2. 查长期启动参数：

```bash
sed -n '1,120p' ~/.config/code-flags.conf
sed -n '1,160p' ~/.vscode/argv.json
sed -n '1,120p' /usr/share/applications/code.desktop
```

3. 查当前真实进程参数：

```bash
ps -eo pid,ppid,stat,lstart,cmd | rg -i '[c]ode|[f]citx5|[r]ime|[x]wayland'
```

重点看 VS Code 主进程是否包含：

```text
--ozone-platform=wayland
--enable-wayland-ime
```

4. 查桌面输入法环境：

```bash
env | rg '^(XDG_CURRENT_DESKTOP|XDG_SESSION_TYPE|GTK_IM_MODULE|QT_IM_MODULE|XMODIFIERS|WAYLAND_DISPLAY|DISPLAY)='
```

5. 查 Fcitx5 是否重复启动：

```bash
journalctl --user -b 0 --no-pager | rg -i 'fcitx|rime|dbus|already running|failed'
```

若看到：

```text
Unable to request dbus name. Is there another fcitx already running?
```

说明至少有一个 Fcitx5 实例因 DBus 名称被占用而退出。输入法可能仍可用，但候选框样式、前端连接和状态同步容易出现不稳定。

6. 查剪贴板桥接问题：

```bash
journalctl --user -b 0 --no-pager | rg -i 'selection|clipboard|xwayland|wayland|klipper'
```

若看到：

```text
Incoming X selection conversion failed
```

通常说明 Wayland 与 XWayland 之间 selection/clipboard 转换失败。表现可能是从浏览器复制后无法粘贴到另一个应用。

7. 查候选框配色是否来自不同 UI 前端：

```bash
rg -n 'UseAccentColor|Theme|DisabledAddons' ~/.config/fcitx5/config ~/.config/fcitx5/conf/classicui.conf
journalctl --user -b 0 --no-pager | rg -i 'fcitx|kimpanel|classicui|Loaded addon'
```

如果浏览器候选框是灰色，而 VS Code/IDEA 是蓝色，优先怀疑部分应用走了 KDE Input Method Panel，即 `kimpanel`。这时只改：

```text
UseAccentColor=False
```

可能无效，因为该选项只影响 Classic UI。可以用下面配置强制禁用 `kimpanel`：

```text
~/.config/fcitx5/config
DisabledAddons=kimpanel
```

然后重启 Fcitx5：

```bash
fcitx5-remote -e
fcitx5 --disable kimpanel -d
```

启动日志中应看到：

```text
Override Disabled Addons: {kimpanel}
Loaded addon classicui
```

---

## 问题

常见误判：

- 看到 `--enable-wayland-ime` 的 warning 就认为参数无效；实际它可能已经传给 Electron。
- 只检查 `~/.vscode/argv.json`，忽略 Arch 下更直接的 `~/.config/code-flags.conf`。
- 在沙箱或容器里运行 `fcitx5-diagnose`，误以为宿主 Fcitx5 没运行。
- 只看 VS Code 日志，忽略 KWin 的剪贴板/selection 错误。
- 看到终端输入正常，就排除 Fcitx5 重复启动或 Electron Wayland 输入链路问题。
- 看到候选框蓝色就只改 Classic UI 主题，但实际绘制者可能是 KDE Input Method Panel。
- 以为 `fcitx5-remote -r` 能应用 addon 启停变化；禁用 `kimpanel` 后通常需要重启 Fcitx5。

---

## 个人理解

VS Code 输入法问题要按层次排查：

```text
启动参数层：code 是否稳定带上 Wayland/IME flags
桌面会话层：KDE 是否是 Wayland，会话变量是否正确
输入法服务层：Fcitx5 是否只有一个有效实例并持有 DBus 名称
候选面板层：Classic UI 还是 KDE Input Method Panel 在绘制候选框
Rime 配置层：schema、词库、部署过程是否报错
剪贴板层：Wayland 和 XWayland selection 是否转换失败
```

只有把这些层次拆开，才能解释“终端正常但 VS Code 不正常”这类看似矛盾的现象。
