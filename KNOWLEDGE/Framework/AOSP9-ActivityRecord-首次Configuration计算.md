# AOSP 9 ActivityRecord 首次 Configuration 计算

## 本质

Android 9 中 Activity 首次启动时，发给客户端的配置不是只由 `ActivityRecord` 单独计算出来的，而是由 `ConfigurationContainer` 层级先维护“全量配置”和“合并 override 配置”，再在 `ActivityStackSupervisor#realStartActivityLocked()` 中组合成 `MergedConfiguration` 下发。

## 原理

关键对象有两类配置：

- `getConfiguration()`：当前容器的完整配置，等于父级完整配置加本级 override。
- `getMergedOverrideConfiguration()`：从根到当前容器的 override 累积结果，用于发给客户端作为 Activity override config。

`ConfigurationContainer#onConfigurationChanged()` 会执行：

```java
mFullConfiguration.setTo(newParentConfig);
mFullConfiguration.updateFrom(mOverrideConfiguration);
```

`ConfigurationContainer#onMergedOverrideConfigurationChanged()` 会执行：

```java
mMergedOverrideConfiguration.setTo(parent.getMergedOverrideConfiguration());
mMergedOverrideConfiguration.updateFrom(mOverrideConfiguration);
```

因此，Activity 的最终可见配置来自层级合成，而不是某个单一字段。

## 流程

首次启动核心链路：

1. `ActivityRecord` 构造时用 `service.getConfiguration()` 初始化 `mLastReportedConfiguration`，这是初始记录基线。
2. `realStartActivityLocked()` 启动前如 `checkConfig=true`，先调用 `ensureVisibilityAndConfig()`，通过 WM 更新 display override configuration。
3. `realStartActivityLocked()` 创建：

```java
new MergedConfiguration(
        mService.getGlobalConfiguration(),
        r.getMergedOverrideConfiguration())
```

4. `LaunchActivityItem.obtain()` 把 `globalConfiguration` 和 `overrideConfiguration` 分别传到客户端。
5. `LaunchActivityItem.preExecute()` 用 global config 更新进程 pending config。
6. `ActivityClientRecord` 保存 override config。
7. `ActivityThread#performLaunchActivity()` 用 `mCompatConfiguration` 加 `r.overrideConfig` 合成传给 `Activity.attach()` 的配置。
8. `ContextImpl.createActivityContext()` 用同一个 override config 创建 Activity Resources。

## 常见问题

- 把 `ActivityRecord` 构造函数中的 `_configuration` 当作最终首次配置。它只是 `mLastReportedConfiguration` 的初始化基线。
- 只看 `getConfiguration()`，忽略 `getMergedOverrideConfiguration()`。前者是 server 内部完整配置，后者才是 launch transaction 下发的 Activity override。
- 忽略 `checkConfig=true` 的启动前更新。进程 attach 后首次拉起 Activity 时，`realStartActivityLocked()` 可能先让 WM 重新计算 display override。
- 只改全局配置，后续 Task/Activity override 仍可能覆盖尺寸、方向、`screenLayout` 等字段。

## 个人理解

排查 Android 9 Activity 首次配置，要按“全局配置 + 层级 override + 客户端合成”三段看。服务端下发的是 `MergedConfiguration(global, mergedOverride)`，客户端真正用于 Activity 的是 `mCompatConfiguration.updateFrom(overrideConfig)` 后的结果。
