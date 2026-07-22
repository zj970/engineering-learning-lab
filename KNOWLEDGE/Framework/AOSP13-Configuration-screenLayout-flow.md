# AOSP 13 Configuration screenLayout 流转

## 本质

`Configuration` 不是一个只在 AMS 或 ATMS 中保存的全局变量，而是 Android Framework 根据全局配置、Display 配置、Task 配置、Activity override 配置逐层合成后分发给应用进程的运行时资源配置。

因此，修改 `Configuration#screenLayout` 时，如果只在下游消费点 hook，可能短暂生效，但后续重新计算配置时又被源头的旧值覆盖。

## 原理

关键链路可以拆成三类：

1. 全局配置：通常由 ATMS 维护并分发，影响系统范围资源配置。
2. 进程启动配置：应用 attach 时 AMS/ATMS 给进程一个配置快照。
3. Activity 配置：`ActivityRecord` 根据父级 WindowContainer 和自身 override 配置计算最终配置。

Launcher3 首次烧录或开机时，容易经历多次配置变化：进程 attach、Activity launch、Display/WindowContainer 配置更新、Launcher 资源和 DeviceProfile 初始化。只要其中某次分发仍携带旧 `screenLayout`，Launcher 就会表现为先加载 hook 后的值，再加载 hook 前的值。

## 流程

典型观察路径：

1. `ATMS#updateConfigurationLocked` 更新全局配置。
2. `AMS#attachApplicationLocked` 给新进程下发初始配置。
3. `ActivityRecord#resolveOverrideConfiguration` 计算 Activity 级 override。
4. `ActivityThread` 接收配置变化，触发资源更新、Activity configChanged 或 relaunch。
5. Launcher3 根据当前资源配置重算布局和 DeviceProfile。

## 常见问题

- hook 点太靠后：只改了某次分发结果，没有改配置源头。
- 配置副本未统一：`new Configuration()`、`setTo()`、`updateFrom()` 后又出现旧值。
- bit mask 修改错误：`screenLayout` 中多个字段共存，整体赋值可能覆盖 layout direction 或 long 等位。
- Launcher3 缓存重算：首次启动时先用一个配置初始化，随后收到新配置又重新加载。

## 个人理解

这类问题应按“配置源头一致性”处理，而不是按“看到哪里旧就在哪里 hook”处理。正确排查方式是给每一次配置创建、复制、更新、分发加日志，找出旧值重新出现的第一现场。只有找到源头后，再决定是否在 Display/WindowContainer 级别统一修改，还是在应用兼容策略层做定向调整。

## App 定向修改 long 位

如果目标只是让部分 App 命中 `-long` 资源，不应该整体覆盖 `screenLayout`，也不应该修改全局配置。应只修改目标配置副本中的 long 位：

```java
config.screenLayout = (config.screenLayout & ~Configuration.SCREENLAYOUT_LONG_MASK)
        | Configuration.SCREENLAYOUT_LONG_YES;
```

多 App 场景应使用白名单策略，并尽量在 server 侧 Activity 配置分发路径统一处理。`AMS#attachApplicationLocked` 只能影响进程启动初始配置，后续 Activity 配置变化仍可能覆盖；`ATMS#updateConfigurationLocked` 容易影响全局；`ActivityRecord` 或 ClientTransaction 下发前的配置副本更适合做按包名定向修正。

即使在 `AMS#attachApplicationLocked` 中通过 `new Configuration` 创建副本后再修改，也只能说明没有污染全局对象，不能说明运行期配置稳定。因为 Activity launch、relaunch、`onConfigurationChanged` 等路径仍可能下发由 `ActivityRecord`/`WindowContainer` 重新合成的配置，覆盖 attach 阶段下发给进程的初始配置。

如果 AMS 和 ActivityRecord 两侧都已经 hook，但问题只在 Launcher3 首次烧录或恢复出厂后概率出现，应把排查重点转向 Launcher3 首次初始化链路。Launcher3 会初始化 DeviceProfile、InvariantDeviceProfile、workspace 数据库、默认布局和资源缓存，且可能使用 WindowMetrics、DisplayController、Application context 或历史缓存，而不完全依赖当前 Activity 的 `Configuration.screenLayout`。此时要先证明旧值是否仍由 system_server 下发；如果不是，则应排查 Launcher3 内部 profile/cache 的首次写入时序。
