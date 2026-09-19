# Deepin Wine TrayManager 非 Deepin 桌面依赖

## 本质

一些 Deepin Wine 封装应用会在启动流程里调用 `com.deepin.dde.TrayManager`，用来获取托盘窗口或判断已有实例。  
这个 DBus 服务是 Deepin 桌面环境相关组件，在 KDE/Plasma、i3、Hyprland 等非 Deepin 桌面里通常不存在。

---

## 原理

封装脚本会把 tray 窗口、已有 bottle、启动 block 等逻辑绑在一起：

```text
get_tray_window
-> 访问 com.deepin.dde.TrayManager
-> 读取 TrayIcons
-> 判断是否已有活动窗口
-> 决定是否 kill block app
```

如果 `TrayManager` 不存在，Python 端会抛出：

```text
org.freedesktop.DBus.Error.NameHasNoOwner
org.freedesktop.DBus.Error.ServiceUnknown
```

这通常说明：

- Deepin 桌面服务缺失；
- 托盘检测失效；
- 封装脚本可能误判当前窗口状态。

---

## 流程

先区分两种情况：

1. 只是 tray 检测失败，但主程序仍在运行。  
   这种情况常见表现是程序已启动但没有托盘图标，或窗口被最小化到看不见。

2. 主程序确实退出。  
   这时要继续查 wine 日志、进程列表和封装脚本是否把应用杀掉。

检查命令：

```bash
pgrep -af 'WXWork|wine|wineserver'
journalctl --user -b | rg -i 'TrayManager|WXWork|wine|DBus|seh|loaddll'
```

---

## 问题

常见误判：

- 把 `TrayManager` 缺失当作 Wine 本体崩溃；
- 看到 DBus 异常就直接重建 prefix；
- 没区分“托盘检测失败”和“主进程退出”。

---

## 个人理解

这类封装应用对桌面环境的假设很强。  
在非 Deepin 桌面上，`TrayManager` 缺失不是边角噪音，而是启动链路中的真实兼容性变量。  
排障时必须先判断主程序是否还活着，再判断 tray 失败是否只是表象。
