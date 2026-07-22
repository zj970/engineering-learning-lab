# RSS 信息源筛选原则

## 本质

个人学习型 RSS 系统的目标不是“覆盖所有技术新闻”，而是稳定获得少量能推动主线学习的高质量输入。对当前项目来说，RSS 源要服务 `Android Framework / AOSP / LineageOS / Linux 底层 / AI 工具链` 这些主线，而不是制造更多待清理的信息噪声。

## 原理

优质信息源一般按信号强度分层：

1. 官方源：项目、平台、框架团队直接发布，适合跟踪版本变化、API 变化、安全公告和路线调整。
2. 源码源：Git log、release note、changelog，适合训练源码阅读和变更分析能力。
3. 工程实践源：大型工程团队复盘性能、稳定性、基础设施、工具链问题，适合补工程判断。
4. 社区源：适合发现热点和真实问题，但噪声高，不能压过主线输入。
5. 泛科技媒体：适合了解趋势，不适合作为每日深读主来源。

## 流程

选择 RSS 源时按下面顺序判断：

1. 先问它是否服务当前学习任务，而不是只看热度。
2. 优先选择官方 feed、源码 feed、release note feed。
3. 对社区和媒体源限制分类位置，避免同一源重复出现在多个主题下。
4. 连续抓取失败、404、XML 不规范或长期超时的源，应标记为待替换。
5. 每天只选 1 条主线深读，RSS 系统负责筛选，不负责制造阅读压力。

## 当前建议

- `Android Developers Blog`、`AndroidX Release Notes`、`LineageOS Blog`、`Kotlin Blog` 适合 Android 主线。
- `LWN.net`、`Linux Kernel Mainline`、`Rust Blog`、`This Week in Rust` 适合 Linux / 系统编程主线。
- `OpenAI News`、`Hugging Face Blog`、`Google DeepMind Blog`、`Google Research Blog`、`Simon Willison` 适合 AI 工具链和工程化观察。
- `Martin Fowler`、`GitHub Engineering`、`Cloudflare Blog`、`JetBrains IDEA Blog` 适合工程实践。
- `LinuxDo`、`V2EX`、`阮一峰周刊` 适合中文侧向输入，但应放在社区或周刊分类中，不宜多分类重复。

## 问题

当前 `sources.json` 中存在几类典型问题：

- 部分源已经返回 404，例如 `source.android.com/docs/rss.xml`、`OpenAI Research RSS`、`Anthropic News RSS`、`郭霖 CSDN RSS`。
- 部分源不是标准 RSS，或 XML 不规范，例如部分中文媒体源和掘金 API。
- `少数派`、`阮一峰`、`LinuxDo` 等源跨分类重复，会增加日报条目数量。
- `AOSP Gitiles` 的 `format=JSON` 可用，但不是 RSS；如果要跟踪源码变更，应先扩展脚本解析 JSON。

## 个人理解

信息源不是越多越好。对学习系统来说，RSS 源应该像训练集：质量、标签和目标一致性比数量更重要。当前阶段最值得保留的是能直接帮助理解 Android Framework、AOSP 构建、Linux 内核机制和 AI 工具链工程化的来源。
