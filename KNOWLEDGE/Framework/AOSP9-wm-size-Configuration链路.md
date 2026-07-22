# AOSP 9 wm size 到 Configuration 分发链路

## 本质

Android 9 中执行 `adb shell wm size WxH` 后，系统不是直接通知某个 Activity 尺寸变化，而是先修改默认屏的 base display metrics，再由 WMS 重新计算屏幕级 `Configuration`，最后通过 AMS 更新全局配置并决定 Activity 是 relaunch 还是接收 `onConfigurationChanged()`。

关键点：Android 9 的 `wm size` 固定作用于 `Display.DEFAULT_DISPLAY`，默认屏的 display override configuration 会复制到 global configuration，所以这条链路最终走的是 AMS 全局配置更新。

## 原理

`wm size` 改的是 `DisplayContent.mBaseDisplayWidth / mBaseDisplayHeight`，不是 `mInitialDisplayWidth / mInitialDisplayHeight`。

- `mInitialDisplayWidth / Height`：物理初始屏幕尺寸。
- `mBaseDisplayWidth / Height / Density`：系统当前用于布局和配置计算的 base metrics，可被 `wm size`、`wm density` 覆盖。
- `DisplayContent#computeScreenConfiguration()`：根据 base metrics、rotation、policy decor 区域、density 等，计算 `orientation`、`screenWidthDp`、`screenHeightDp`、`smallestScreenWidthDp`、`screenLayout`、`appBounds`、`densityDpi` 等字段。

## 流程

以 `adb shell wm size 1080x1920` 为例：

1. `WindowManagerShellCommand#onCommand()` 识别 `size`，进入 `runDisplaySize()`。
2. `runDisplaySize()` 解析宽高后调用 `IWindowManager#setForcedDisplaySize(Display.DEFAULT_DISPLAY, w, h)`。
3. `WindowManagerService#setForcedDisplaySize()` 校验 `WRITE_SECURE_SETTINGS`，并限制只能修改默认屏。
4. `WindowManagerService#setForcedDisplaySizeLocked()` 调用 `DisplayContent#updateBaseDisplayMetrics()`，更新 `mBaseDisplayWidth / Height / Density`。
5. WMS 调用 `reconfigureDisplayLocked()`：
   - 配置 DisplayPolicy；
   - 标记 layout needed；
   - 调 `DisplayContent#computeScreenConfiguration()` 计算新的屏幕配置；
   - 如果和当前 display config 有 diff，就设置 `mWaitingForConfig=true`、冻结屏幕，并发送 `H.SEND_NEW_CONFIGURATION`。
6. `WindowManagerService#sendNewConfiguration()` 调用 `ActivityManagerService#updateDisplayOverrideConfiguration(null, displayId)`。
7. AMS 收到 `values=null` 后，回调 WMS `computeNewConfiguration(displayId)`，再次用 `DisplayContent#computeScreenConfiguration()` 得到正式配置。
8. 因为 displayId 是 `DEFAULT_DISPLAY`，AMS 进入 `updateGlobalConfigurationLocked()`：
   - 更新全局 configuration；
   - 调 `ActivityStackSupervisor#onConfigurationChanged()` 向 Activity/Task/Stack 配置树传播；
   - 给所有进程发送 `ConfigurationChangeItem`；
   - 发送 `ACTION_CONFIGURATION_CHANGED`；
   - 再调用 `performDisplayOverrideConfigUpdate()` 同步默认屏 override config。
9. AMS 调 `ensureConfigAndVisibilityAfterUpdate()`，让焦点栈顶部 Activity 执行 `ActivityRecord#ensureActivityConfiguration()`。
10. `ActivityRecord#ensureActivityConfiguration()` 比较上次上报配置和当前 `getConfiguration()`：
    - 若 Activity 没处理相关 `configChanges`，走 `relaunchActivityLocked()`；
    - 若 Activity 能处理变化，走 `scheduleConfigurationChanged(newMergedOverrideConfig)`，客户端收到 `ActivityConfigurationChangeItem`。

## 关键源码位置

- `WindowManagerShellCommand.java:60`、`:90`、`:125`：`wm size` 命令入口和默认屏调用。
- `WindowManagerService.java:5160`、`:5270`：设置 forced display size 并更新 base metrics。
- `WindowManagerService.java:5419`：重新计算 display configuration、冻结屏幕并发送新配置消息。
- `WindowManagerService.java:4392`、`:4417`：通知 AMS，并提供 `computeNewConfiguration()`。
- `DisplayContent.java:1268`、`:1421`、`:1805`：计算屏幕 configuration 与更新 base metrics。
- `ActivityManagerService.java:22724`、`:22772`、`:22580`、`:22843`：接收 WMS 通知、默认屏转全局配置、再检查 Activity。
- `ActivityRecord.java:2497`、`:2560`、`:2607`、`:2655`：Activity 配置检查、relaunch 或下发 override config。

## 常见问题

- 误以为 `wm size` 改的是物理屏幕尺寸。实际改的是 base metrics，物理初始值仍保留。
- 误以为 WMS 算完就直接发给 Activity。实际 WMS 先判断变化，再通知 AMS，由 AMS 统一更新全局配置和 Activity 生命周期。
- 忽略默认屏特殊分支。Android 9 中默认屏 override config 会复制到 global config，所以 `wm size` 常表现为全局配置变化。
- 只看全局 `ConfigurationChangeItem`。Activity 是否重启，还要看 `ActivityRecord#ensureActivityConfiguration()` 对当前 Activity 的完整配置 diff 和 manifest `configChanges` 判断。

## 个人理解

这条链路可以按“改 metrics -> 算 display config -> 更新 global config -> 配置树传播 -> Activity 生命周期决策”来记。`mMergedOverrideConfiguration` 在最后仍然重要：当 Activity 不需要 relaunch 时，服务端不会把完整全局配置再发一遍给 Activity，而是通过 Activity 级 transaction 发送 merged override config，让客户端和已收到的全局配置合成最终 Activity 配置。
