# Android 17 WMS 调试与实验手册

## 基线

- `android17-release`
- `frameworks/base@94b4c163b7df`

本文目标不是罗列所有命令，而是建立“问题 -> 最小状态 -> 调用链 -> trace/test”的调试顺序。

---

## 调试原则

遇到窗口问题时，先写出四个判断，再运行命令：

1. 问题属于窗口注册、布局、输入、Surface、Transition 还是 Configuration？
2. 预期状态归哪个对象：DisplayContent、Task、ActivityRecord、WindowToken 还是 WindowState？
3. 状态应该在哪个线程、哪次 Binder 或 transaction 后生效？
4. 最小可复现实验是什么？

推荐证据层级：

```text
dumpsys 静态快照
 -> 精准 ProtoLog/logcat
 -> Perfetto/Winscope 时序
 -> 相关 WmTests
 -> 最小源码修改验证假设
```

---

## 一、dumpsys window

先查看当前版本支持的分类：

```bash
adb shell dumpsys window -h
```

### 高频命令

```bash
# 运行时容器树和窗口遍历
adb shell dumpsys window containers

# 单个 Display 的窗口、配置与布局状态
adb shell dumpsys window displays

# WindowToken 列表
adb shell dumpsys window tokens

# WindowState 列表
adb shell dumpsys window windows

# 当前可见窗口，减少输出噪声
adb shell dumpsys window visible
adb shell dumpsys window visible-apps

# Session、策略、动画和最后一次 ANR
adb shell dumpsys window sessions
adb shell dumpsys window policy
adb shell dumpsys window animator
adb shell dumpsys window lastanr

# Proto 输出，便于脚本或 Winscope 相关工具处理
adb shell dumpsys window --proto > window.pb
```

`dumpsys window` 还支持窗口名子串或对象十六进制标识作为过滤条件：

```bash
adb shell dumpsys window com.example.demo
```

### 阅读顺序

1. `containers`：先确认父子层级。
2. `displays`：确认 Display、Configuration、layout needed、焦点。
3. `windows/visible`：确认目标 WindowState 的 attrs、frame、visibility、surface。
4. `tokens`：确认窗口 token 类型与归属。
5. `policy/animator/lastanr`：按问题类型补充。

---

## 二、输入和 Surface 状态

```bash
# InputDispatcher、InputReader、focused window/application、channel
adb shell dumpsys input

# SurfaceFlinger 全局状态
adb shell dumpsys SurfaceFlinger

# 只列 Surface layer 名称，快速找目标窗口
adb shell dumpsys SurfaceFlinger --list
```

对输入问题至少对齐三项：

- WMS 的 `mCurrentFocus` 和目标 `WindowState`。
- InputDispatcher 的 focused window/application。
- 触摸坐标对应的 InputWindowHandle 区域和 Z-order。

对黑屏/闪烁问题至少对齐：

- WindowState 是否 requested visible / visible / drawn。
- SurfaceControl 是否存在、父节点是否正确。
- 客户端是否提交 buffer。
- transaction 是否包含 show/hide/crop/alpha 异常。

---

## 三、cmd window 与 wm

`frameworks/base/cmds/wm/wm.sh` 最终进入 `cmd window`，两种写法使用同一个 `WindowManagerShellCommand`。

```bash
adb shell wm size
adb shell wm density

adb shell cmd window size
adb shell cmd window density
```

### 可控实验

```bash
adb shell wm size 1080x1920
adb shell wm density 420

# 实验结束必须恢复
adb shell wm size reset
adb shell wm density reset
```

修改显示参数可能触发 Configuration 更新、Activity relaunch、Shell display-change transition 和布局重算。不要在未记录原始值时直接修改真实设备。

当前版本还支持旋转、orientation request、letterbox、多窗口配置和 display windowing mode。执行前先查看帮助，避免使用旧版本参数：

```bash
adb shell cmd window help
```

---

## 四、ProtoLog、Perfetto 与 Winscope

### ProtoLog

WMS ProtoLog 入口：

```bash
adb shell cmd window logging
```

当前帮助提供 `start/stop/enable/disable/enable-text/disable-text`。具体 group 参数应以设备命令帮助为准。

注意：system_server WMS 与 SystemUI 的 WMShell 是不同进程。`WindowManagerShellCommand` 的提示明确要求 WMShell 日志通过 `SystemUIService WMShell` 管理，不要把两套日志开关混在一起。

### Perfetto/Winscope

当前 Android 17 使用 Perfetto 数据源：

- WMS：`android.windowmanager`
- Shell Transition：`com.android.wm.shell.transition`

建议一次窗口/转场实验同时采集：

- WindowManager
- SurfaceFlinger layers
- SurfaceFlinger transactions
- Input events（输入问题）
- Shell transitions（任务/Activity 转场问题）

当前 `WindowTracingPerfetto` 对旧式 `wm tracing start/stop` 命令明确不再执行原来的文件 trace 逻辑，因此不要依赖旧教程中的 `/data/misc/wmtrace/wm_trace.winscope` 流程。

### Trace 阅读顺序

1. 在 WM hierarchy 找 ActivityRecord、WindowState、DisplayArea 层级。
2. 在 SF layers 找对应 SurfaceControl 与 leash。
3. 对齐 relayout、finishDrawing、show/hide transaction。
4. 转场问题再查看 collect、onTransactionReady、Shell handler、finish。
5. 输入问题再对齐 focused token、InputWindowHandle 和 event target。

---

## 五、WmTests

### 环境前提

从 AOSP 根目录执行：

```bash
cd /home/zj970/android/aosp-last
source build/envsetup.sh
lunch <你的目标>
```

主设备端测试模块为 `WmTests`，源码位于：

```text
frameworks/base/services/tests/wmtests/src/com/android/server/wm
```

### 建议从单类目标开始

```bash
atest WmTests-wm-WindowContainerTests
atest WmTests-wm-RootWindowContainerTests
atest WmTests-wm-DisplayContentTests
atest WmTests-wm-WindowManagerServiceTests
atest WmTests-wm-WindowStateTests
atest WmTests-wm-TransitionControllerTest
```

后续专题：

```bash
atest WmTests-wm-DisplayPolicyTests
atest WmTests-wm-SurfaceAnimatorTest
atest WmTests-wm-SurfaceAnimationRunnerTest
atest WmTests-wm-TransitionTests
atest WmTests-wm-TaskSnapshotControllerTest
```

目标名来自本地 `services/tests/wmtests/Android.bp` 和 `TEST_MAPPING`。源码更新后应重新搜索，不能长期假设目标名不变。

输入目标没有独立 `InputMonitorTest`；相关断言主要分布在 `WindowStateTests` 和 `WindowManagerServiceTests`。

---

## 六、八个最小实验

### 实验 1：运行时容器树映射

**目标**：把 UML 映射到真实设备。

步骤：

1. 启动一个测试 Activity。
2. 执行 `dumpsys window containers`。
3. 找出 DisplayContent、TaskDisplayArea、Task、ActivityRecord、WindowState。
4. 标注每个节点的父节点与 Z-order。

完成标准：能解释应用窗口和 system window 为什么位于不同 DisplayArea 分支。

### 实验 2：addWindow 线程与 Binder 边界

**目标**：验证注册窗口不是首帧显示。

建议日志点：

- `WindowManagerGlobal.addView()`
- `ViewRootImpl.setView()`
- `Session.addToDisplayAsUser()`
- `WindowManagerService.addWindow()`
- `WindowToken.addWindow()`

每条日志包含时间、线程名、pid/tid、窗口 token。完成标准：能指出 UI 线程与 system_server Binder 线程的切换位置。

### 实验 3：首次 relayout 和 draw

**目标**：对齐 frame、Surface 和 buffer。

步骤：

1. 记录 `ViewRootImpl.performTraversals/relayoutWindow/performDraw`。
2. 记录 WMS `relayoutWindow/finishDrawingWindow`。
3. 同时录制 WM/SF trace。
4. 标出 client-surface 或 server-surface 分支。

完成标准：能解释 relayout 返回时为什么仍不一定可见。

### 实验 4：焦点与输入目标

**目标**：区分窗口焦点、输入焦点和触摸目标。

步骤：

1. 准备两个 Activity 和一个可触摸 Overlay。
2. 依次点击、切前后台、显示 IME。
3. 保存 `dumpsys window windows`、`dumpsys input`。
4. 对比 InputWindowHandle 区域和 Z-order。

完成标准：解释至少一个“mCurrentFocus 正确但触摸落到其他窗口”的场景。

### 实验 5：Insets 和 Frame

**目标**：理解 `DisplayPolicy` 和 `WindowLayout.computeFrames()`。

步骤：

1. 同一 Activity 切换 edge-to-edge。
2. 显示/隐藏 IME。
3. 旋转屏幕。
4. 对比 Window frame、app bounds、InsetsState。

完成标准：画出一次 frame 变化由哪些 Insets source 驱动。

### 实验 6：Shell Transition

**目标**：理解 collect 到 finish。

步骤：

1. 录制 Activity 启动、返回和任务切换。
2. 在 trace 中找 `TransitionController/Transition`。
3. 找 Shell `TransitionHandler`。
4. 对齐 start transaction、finish transaction 和动画 leash。

完成标准：标出 collect、onTransactionReady、startAnimation、finish 四个阶段。

### 实验 7：Configuration 与多显示

**目标**：比较默认屏 global config 与副屏 override config。

步骤：

1. 记录原始 `wm size/density`。
2. 修改默认屏 size 或 density，观察 Activity 重建/回调。
3. 创建 VirtualDisplay 或使用模拟副屏。
4. 把 Activity 启动到指定 Display 并比较配置。
5. 恢复所有 override。

完成标准：画出两条配置传播分支并说明 Shell display-change transition。

### 实验 8：真实故障闭环

选择黑屏、窗口层级错误、输入失焦、旋转重建异常或转场卡住中的一个问题。

报告模板：

```text
现象
最小复现
初始假设
dumpsys 证据
trace 证据
源码调用链
根因
修改
测试矩阵
残余风险
```

完成标准：不是“改完现象消失”，而是证据能解释修改前后的状态变化。

---

## 七、问题到工具的映射

| 现象 | 第一观察面 | 第二观察面 | 重点源码 |
|------|------------|------------|----------|
| 窗口未出现 | `dumpsys window visible/windows` | WM/SF trace | addWindow、relayout、finishDrawing |
| 黑屏/闪烁 | SF layers/transactions | WM hierarchy | WindowStateAnimator、prepareSurfaces |
| 窗口位置错误 | `dumpsys window displays` | Insets/WM trace | DisplayPolicy、WindowLayout |
| 点击错窗口 | `dumpsys input` + windows | input trace | InputMonitor、InputWindowHandle |
| 焦点异常 | windows/displays | ProtoLog focus group | updateFocusedWindowLocked |
| Activity 转场卡住 | Shell transition trace | WM/SF transactions | TransitionController、Transition |
| 旋转/尺寸异常 | displays + Activity 生命周期 | display-change trace | DisplayContent、Configuration |
| ANR | `dumpsys window lastanr` + input | system trace | InputManagerCallback、ANR controller |

---

## 八、实验纪律

- 修改 `wm size/density` 前记录原值，结束后 reset。
- 日志点必须带线程和对象标识，避免只打印“进入方法”。
- 一次实验只验证一个假设。
- trace 前先写预期节点，否则容易在时间线中无目标浏览。
- 不在核心持锁路径加入耗时日志或 I/O。
- 修改源码后至少运行一个最相关的 `WmTests-wm-*` 目标。
- 所有结论注明本地 commit，避免下次更新源码后继续使用失效行号。

---

## 关键源码入口

- `services/core/java/com/android/server/wm/WindowManagerService.java:7560`
- `services/core/java/com/android/server/wm/WindowManagerShellCommand.java:94`
- `services/core/java/com/android/server/wm/WindowTracingPerfetto.java:40`
- `services/core/java/com/android/server/wm/PerfettoTransitionTracer.java:39`
- `services/core/java/com/android/server/wm/InputMonitor.java:344`
- `services/core/java/com/android/server/wm/InputManagerCallback.java:47`
- `services/tests/wmtests/Android.bp:85`
- `services/tests/wmtests/TEST_MAPPING`

---

## 自测问题

1. 静态 dumpsys 与 Perfetto trace 分别适合回答什么问题？
2. 为什么当前版本不应继续依赖旧 `wm tracing start/stop` 教程？
3. 输入失焦时，为什么必须同时看 WMS 与 InputDispatcher？
4. 修改 WindowContainer 后应优先运行哪个测试？
5. 一个合格的 WMS 故障结论至少需要哪三类证据？
