# 学习任务

## 基本信息

- 时间：2026-04-24
- 主题：建立每日信息采集与沉淀工作流
- 当前阶段：L2 向 L3 过渡

---

## 目标

- 总目标：建立一个每天可执行的本地信息采集闭环，围绕 Android Framework、AI、Linux 内核、工程效率工具、科技前沿，自动生成可复盘的 Markdown 日报。
- 阶段目标：在 1 周内跑通“配置来源 -> 本地抓取 -> 初步分类 -> 输出 Markdown -> 人工深读”最小链路，并开始按输出质量迭代来源配置。

---

## 背景判断

- 当前能力：已经能明确学习主题，但缺少稳定的信息获取与沉淀系统。
- 主要薄弱点：信息输入分散，来源质量不稳定，容易看得多但沉淀少。
- 约束条件：需要低阻力、可本地保存、可长期扩展的方案，避免依赖复杂平台。

---

## 任务拆解

### 任务 1

- 任务目标：确认默认信息源是否适合当前关注主题。
- 执行步骤：连续 3 天运行 `python3 tools/daily_info/generate_daily_info.py`，每天检查 5 个主题下的输出条目是否相关；记录无效源、低质量源和缺失主题。
- 验证方式：每天至少标记 3 条“高价值”与 3 条“应淘汰”条目。
- 完成标准：形成 1 份需要保留 / 替换 / 新增的信息源调整清单。

### 任务 2

- 任务目标：建立人工深读与知识沉淀习惯。
- 执行步骤：每天从生成的日报中选 1 条高优先级信息做深读；把结论写入当天 Markdown 或对应知识文档。
- 验证方式：连续 5 天，每天至少补充 1 条“原理 / 判断 / 下一步动作”。
- 完成标准：能够回顾 5 天记录并说清楚哪些主题最有价值。

### 任务 3

- 任务目标：迭代优先级分类规则。
- 执行步骤：观察生成结果中的“高 / 中 / 低优先级”是否符合实际；根据误判情况调整 `PRIORITY_RULES` 或来源标签。
- 验证方式：修改后重新生成一天日报，对比分类变化是否更接近你的判断。
- 完成标准：误判明显减少，高优先级列表能直接支持当天深读选择。

---

## 节奏安排

- 每周投入：20~30 分钟 / 天。
- 建议节奏：早上生成日报并快扫，晚上选 1 条深读并补充沉淀；周末统一调整信息源与分类规则。

---

## 复盘要求

- 本周收获：哪些来源最稳定、哪些主题最值得长期跟踪。
- 暴露问题：抓取失败、摘要不准、分类误判、信息冗余。
- 下周调整：删除噪音源、增加高质量官方源、优化规则或模板。

---

## Android 9 Launcher3 源码学习

### 基本信息

- 时间：2026-07-20
- 主题：建立 Android 9 Launcher3 系统开发能力
- 当前阶段：L2 向 L3 过渡

### 目标

- 总目标：能够基于 `/home/zj970/android/aosp-last/packages/apps/Launcher3` 独立定位、修改和验证 Launcher3 的核心功能。
- 阶段目标：掌握启动、模型加载、UI 层级、状态机、拖拽和数据库六条主链，并完成至少一个真实定制需求。

### 背景判断

- 当前能力：已经具备 Android Framework 源码调用链追踪能力，能够阅读 Activity、WMS、AMS 和 Configuration 相关代码。
- 主要薄弱点：对大型系统应用的构建变体、模型与 UI 分层、异步加载和持久化一致性还缺少完整实践。
- 约束条件：必须以当前 Android 9 源码为准，区分普通 Launcher 与 Quickstep，不能直接套用新版 Launcher3 资料。

### 任务拆解

#### 任务 1：验证启动与加载链路

- 任务目标：能解释 Launcher 冷启动到首屏图标显示的完整过程。
- 执行步骤：在 `LauncherProvider.onCreate()`、`Launcher.onCreate()`、`LauncherModel.startLoader()`、`LoaderTask.run()` 和 `LoaderResults.bindWorkspace()` 增加临时日志。
- 验证方式：通过线程名和时间戳确认 Provider、主线程、launcher-loader 和首屏绑定顺序。
- 完成标准：能够不看文档画出冷启动时序图并说明同步重绑分支。

#### 任务 2：完成 Workspace 数据实践

- 任务目标：掌握 View、ItemInfo、BgDataModel 和 launcher.db 的一致性。
- 执行步骤：移动一个图标、创建一个文件夹、添加一个 Widget，分别跟踪 `Workspace`、`ModelWriter` 和 `LauncherProvider`。
- 验证方式：重启 Launcher 后布局保持一致，并核对 Favorites 表对应字段。
- 完成标准：能够独立定位“界面已变化但重启恢复”类问题。

#### 任务 3：完成一个真实定制需求

- 任务目标：从需求分析、源码定位、修改、构建到回归测试完成一次闭环。
- 执行步骤：优先选择默认布局、网格尺寸、图标样式、All Apps 或状态动画中的一个需求。
- 验证方式：按照技术文档的最小验证矩阵检查冷启动、配置变化、拖拽持久化及应用安装卸载。
- 完成标准：形成对应知识文档和会话记录，并能说明修改影响的模块边界。

### 节奏安排

- 每周投入：3 次，每次 45~60 分钟。
- 建议节奏：一次阅读主链、一次加日志验证、一次完成小修改和复盘。

### 复盘要求

- 本周收获：能否脱离全文索引定位启动、模型、UI、状态、拖拽和数据库问题。
- 暴露问题：是否混淆普通 Launcher 与 Quickstep，是否遗漏线程和持久化边界。
- 下周调整：根据真实定制需求补充更聚焦的 Launcher3 专题文档。

---

## Android 17 WMS 系统学习

### 基本信息

- 时间：2026-07-22
- 主题：基于本地 Android 17 源码建立 WindowManagerService 系统开发能力
- 当前阶段：L2 向 L3 过渡

### 目标

- 总目标：能够基于 `/home/zj970/android/aosp-last/frameworks/base` 独立解释、定位、调试和修改 WMS 的核心流程。
- 阶段目标：用 8 周完成启动与对象树、窗口添加、relayout/绘制、Surface 遍历、输入/焦点、Insets/策略、Transitions、多显示和调试实践，并完成一个可验证的小型定制或故障分析。

### 背景判断

- 当前能力：已经能跟踪 `wm size -> Configuration -> Activity` 专题链路，也具备阅读 Framework Java 源码和 Binder 调用的基础。
- 主要薄弱点：缺少现代 WMS/ATMS 共用容器树的整体模型，容易把旧 Android 9 的 `AppWindowToken/TaskStack/AppTransition` 资料套到 Android 17。
- 约束条件：源码基线固定为 `android17-release`、`frameworks/base@94b4c163b7df`；每个阶段必须同时包含源码证据、运行时观察和自己的图，不能只阅读文档。

### 任务拆解

#### 任务 1：建立版本意识和 WMS 全景地图

- 任务目标：能解释 WMS、ATMS、IMS、WindowManagerPolicy、WM Shell 和 SurfaceFlinger 的边界。
- 执行步骤：阅读 `SystemServer`、`WindowManagerService.main()`、`ActivityTaskManagerService.setWindowManager()`；运行 `dumpsys window containers/displays`；手工复画总体框架图。
- 验证方式：随机指出一个类时，能说明它运行在哪个进程/线程、归哪个子系统、主要持有什么状态。
- 完成标准：不看文档画出启动关系和进程边界，正确说明 WMS/ATMS 共用全局锁与 Root 容器树。

#### 任务 2：掌握 WindowContainer 对象树

- 任务目标：理解 Z-order、Configuration、Surface 和 Activity 生命周期如何映射到同一棵树。
- 执行步骤：阅读 `WindowContainer`、`RootWindowContainer`、`DisplayContent`、`DisplayArea`、`TaskDisplayArea`、`TaskFragment`、`Task`、`ActivityRecord`、`WindowToken`、`WindowState`。
- 验证方式：把 `dumpsys window containers` 的真实节点映射到 UML 类和父子关系。
- 完成标准：能分别画出应用窗口与系统窗口两条容器分支，并解释 `ActivityRecord` 为什么是 Activity 与窗口树的连接点。

#### 任务 3：跟通窗口添加和移除

- 任务目标：理解 View 加入 WindowManager 后，WMS 如何校验 token、创建 WindowState、建立 InputChannel 并挂入容器树。
- 执行步骤：跟踪 `WindowManagerGlobal.addView -> ViewRootImpl.setView -> Session.addToDisplayAsUser -> WMS.addWindow -> WindowToken.addWindow`，再反向跟踪 remove 流程。
- 验证方式：在关键点添加临时日志或断点，对齐应用 UI 线程与 system_server Binder 线程的时序。
- 完成标准：能说明 addWindow 完成了什么、没有完成什么，以及为什么还需要首次 relayout/draw。

#### 任务 4：掌握 relayout、首帧和 Surface placement

- 任务目标：区分 frame 计算、Surface 创建、客户端绘制、finishDrawing 和 Transaction 提交。
- 执行步骤：跟踪 `performTraversals -> relayoutWindow -> WMS.relayoutWindow`、client/server 两条 Surface 路径、`finishDrawing` 以及 `WindowSurfacePlacer.performSurfacePlacement`。
- 验证方式：用 Perfetto/Winscope 或 trace/log 对齐 relayout、draw、finishDrawing、show 和 SurfaceFlinger 提交时间。
- 完成标准：能独立画出首次显示时序图，并正确区分 `performLayout`、`assignWindowLayers`、`prepareSurfaces`。

#### 任务 5：掌握焦点、输入、Insets 和策略

- 任务目标：理解窗口几何、焦点和输入目标如何同步到 InputDispatcher，以及 `PhoneWindowManager` 与 `DisplayPolicy` 的职责差异。
- 执行步骤：跟踪 `openInputChannel`、`InputMonitor`、focused token、`DisplayPolicy.layoutWindowLw()`、`WindowLayout.computeFrames()` 和 Insets 状态。
- 验证方式：使用两个 Activity、IME 和 Overlay 做焦点/触摸实验，对比 `dumpsys window windows` 与 `dumpsys input`。
- 完成标准：能解释当前焦点窗口、输入焦点和触摸命中目标为什么可能不同。

#### 任务 6：掌握动画与 Shell Transitions

- 任务目标：理解局部 Surface 动画和跨任务 Shell Transition 的两套机制。
- 执行步骤：先读 `SurfaceAnimator/SurfaceAnimationRunner`，再读 `TransitionController/Transition` 和 WM Shell `Transitions/TransitionHandler`。
- 验证方式：录制一次 Activity 启动与返回的 Perfetto/Winscope trace，标出 collect、transaction ready、Shell start、finish 四个阶段。
- 完成标准：能说明 Android 17 为何不能再用旧 `AppTransition` 作为主控制器，并解释 `WindowAnimator` 仍承担的职责。

#### 任务 7：掌握 Configuration、旋转与多显示

- 任务目标：理解每个 Display 的 `DisplayContent/DisplayPolicy/InputMonitor/DisplayArea` 以及默认屏与副屏配置分支。
- 执行步骤：跟踪 Android 17 的 `wm size`、`setForcedSize`、`reconfigureDisplayLocked`、`computeScreenConfiguration`，再创建 VirtualDisplay 或模拟副屏。
- 验证方式：对比修改前后的 `dumpsys window displays`、Activity 重建/回调和 Shell display-change transition；实验结束执行 reset。
- 完成标准：画出默认屏 global Configuration 与副屏 override Configuration 分支图。

#### 任务 8：完成一个 WMS 实战闭环

- 任务目标：从问题定义、源码定位、修改、构建、运行到回归形成 L3 级闭环。
- 执行步骤：从窗口策略、调试增强、多显示行为、转场、Insets 或 WindowState 状态问题中选择一个小需求；先写假设和影响面，再修改。
- 验证方式：执行相关 `WmTests-wm-*` 测试，配合 dumpsys/trace 验证，并覆盖启动、旋转、前后台、IME 和异常恢复场景。
- 完成标准：提交一份包含根因、调用链、改动点、测试矩阵和回归风险的专题文档。

### 节奏安排

- 每周投入：3 次，每次 60~90 分钟，共 8 周。
- 建议节奏：第一次读主链并写问题，第二次运行实验并收集证据，第三次复画图、做小测和补文档。
- 进入下一阶段前：必须能脱离文档画出当前主链，并回答阶段末的验收问题。

### 复盘要求

- 本周收获：新增了哪一个可复用对象模型或调用链？
- 暴露问题：是版本混淆、线程/锁遗漏、对象关系错误，还是只有静态阅读没有运行证据？
- 下周调整：缩小到一条主链补实验，不用增加无关类的阅读量。

---

## MVC、MVP、MVVM 与 MCP 架构实践

### 基本信息

- 时间：2026-07-22
- 主题：从会背架构定义过渡到能按依赖方向和场景选型
- 当前阶段：L2 向 L3 过渡

### 目标

- 总目标：能够判断现有 Android 代码实际采用的职责结构，独立选择 MVC/MVP/MVVM，并正确使用 MCP 连接 AI 外部能力。
- 阶段目标：两周内完成同一登录功能的 MVP/MVVM 对照实现、一次 Activity 职责审查和一次最小 MCP 会话分析。

### 背景判断

- 当前能力：已经接触 Android Framework、ViewModel 和 AI 编码工具，具备阅读调用链和接口的基础。
- 主要薄弱点：容易根据 Activity/ViewModel 等类名判断架构，尚未固定使用依赖方向、状态归属和测试方式进行判断；MCP 与 UI 架构的抽象层容易混淆。
- 约束条件：练习必须使用同一业务需求横向比较；MCP 实验只连接可信 Server，并明确权限、上下文和凭证边界。

### 任务拆解

#### 任务 1：实现 MVP 登录页

- 任务目标：理解 Presenter 持有 View 接口和命令式更新的收益与成本。
- 执行步骤：定义 `LoginView`、`LoginPresenter`、`LoginUseCase`；实现 Loading/Success/Error；在销毁时 detach。
- 验证方式：使用 mock View 验证输入校验、Loading 和成功/失败方法调用。
- 完成标准：能列出 View 接口膨胀、调用顺序和生命周期泄漏三个风险。

#### 任务 2：将同一登录页改为 MVVM

- 任务目标：理解 Action -> ViewModel -> UiState -> render 的状态驱动流程。
- 执行步骤：定义不可变 `LoginUiState`，用 StateFlow 暴露状态，将业务规则留在 `LoginUseCase`。
- 验证方式：断言 Idle -> Loading -> Success/Error 状态序列，并测试进程恢复所需的状态来源。
- 完成标准：能解释状态测试为何比验证多个 View 方法更稳定，以及什么不应放入 ViewModel。

#### 任务 3：审查一个现有 Activity/Fragment

- 任务目标：用职责和依赖方向判断实际架构，而不是按文件名贴标签。
- 执行步骤：分别标记 UI 渲染、事件协调、业务规则、数据访问；画出真实依赖图。
- 验证方式：指出至少一个混合职责，并提出最小重构顺序。
- 完成标准：能说明选择保留 MVC、迁移 MVP 或采用 MVVM 的具体理由。

#### 任务 4：观察最小 MCP 会话

- 任务目标：理解 MCP Host/Client/Server、能力协商和工具权限。
- 执行步骤：连接可信的只读 MCP Server，记录 `initialize`、`notifications/initialized`、`tools/list`、`tools/call` 和结果。
- 验证方式：写出 Client:Server 1:1 关系、协商能力、Server 可见上下文、用户确认和凭证位置。
- 完成标准：能解释 MCP 为什么不替代 MVVM，并给出一次敏感 Tool 调用的安全检查表。

### 节奏安排

- 每周投入：3 次，每次 45~60 分钟，共 2 周。
- 建议节奏：第一周完成 MVP/MVVM 对照；第二周完成 Activity 审查和只读 MCP 实验。

### 复盘要求

- 本周收获：哪个依赖方向或状态边界真正降低了测试和修改成本？
- 暴露问题：是否出现 God Presenter/God ViewModel，是否把 MCP 结果直接当可信输入？
- 下周调整：保留有效边界，删除只增加样板代码但没有隔离变化的抽象。
