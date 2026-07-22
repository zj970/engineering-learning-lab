# RSS 阅读器选型：Inoreader / RSS Guard / Newsboat / FreshRSS

## 本质

RSS 阅读器不是单一类别软件。选型时要先区分四个角色：在线服务、本地 GUI 客户端、终端客户端、自托管聚合服务。

## 原理

- Inoreader 是托管型 RSS 服务，重点是跨设备同步、规则过滤、搜索、Newsletter、社交源和自动化。
- RSS Guard 是桌面 GUI 客户端，重点是本地阅读体验，同时可通过插件同步 Feedly、Inoreader、FreshRSS、Miniflux 等服务。
- Newsboat 是终端 RSS/Atom 阅读器，重点是键盘流、速度、脚本化和配置文件，不负责浏览器级 HTML/CSS 渲染。
- FreshRSS 是自托管 RSS 聚合器和 Web 阅读器，重点是数据自控、Web 访问、多用户和 Google Reader 兼容 API。

## 流程

选择时按下面顺序判断：

1. 是否需要多设备同步：需要则优先 Inoreader 或 FreshRSS。
2. 是否接受自托管维护：接受则 FreshRSS；不接受则 Inoreader。
3. 是否主要在 Linux 桌面阅读：是则 RSS Guard 适合作为客户端。
4. 是否偏好终端和键盘操作：是则 Newsboat。
5. 是否重视网页排版、图片和 CSS：终端 Newsboat 不适合，应选 GUI/Web 阅读器。

## 对比

| 工具 | 类型 | 数据位置 | 主要优势 | 主要代价 |
|---|---|---|---|---|
| Inoreader | 在线 RSS 服务 | 服务商云端 | 同步、搜索、规则、过滤、Newsletter、移动端成熟 | 高级功能付费，数据依赖服务商 |
| RSS Guard | 本地 GUI 客户端 | 本地或同步到远端服务 | Arch/Linux 桌面体验好，支持多种 Feed 格式和在线服务同步 | 跨设备能力依赖外部服务 |
| Newsboat | 终端客户端 | 本地配置和缓存 | 轻量、快速、键盘流、适合脚本化 | 不支持浏览器级 HTML/CSS/JS 渲染 |
| FreshRSS | 自托管 Web 服务 | 自己的服务器 | 数据可控、免费开源、多用户、移动端可通过 API 接入 | 需要部署、备份、更新和维护 |

## 常见组合

- 普通跨设备阅读：Inoreader。
- Arch 桌面阅读：RSS Guard。
- 终端学习和高效扫读：Newsboat。
- 数据自控和长期知识库：FreshRSS + RSS Guard 或 FreshRSS + 手机客户端。
- 实用组合：Inoreader 或 FreshRSS 负责同步，RSS Guard 负责桌面阅读，Newsboat 负责终端快速处理。

## 问题

- 不要把 RSS Guard 和 FreshRSS 当成同类：RSS Guard 是客户端，FreshRSS 是服务端。
- 不要期待 Newsboat 像浏览器一样显示网页：它主要把 HTML 转成终端文本。
- 不要只看“免费”：Inoreader 省维护，FreshRSS 省订阅费但增加运维成本。
- 不要把订阅源管理和阅读界面混在一起：服务端负责聚合与同步，客户端负责阅读体验。

## 个人理解

当前阶段如果目标是学习 Linux、Android、AOSP 和 AI 工具链，最实际的方案是先用 RSS Guard 建立阅读习惯；如果后续需要手机和多设备同步，再接入 Inoreader 或自托管 FreshRSS。Newsboat 适合作为进阶工具，用来训练终端配置、文本处理和信息流自动化。

## 参考

- Inoreader 官方功能页：https://www.inoreader.com/features/
- Inoreader 官方价格页：https://www.inoreader.com/pricing
- RSS Guard 官方文档：https://rssguard.readthedocs.io/en/stable/supported-readers.html
- Newsboat 官方主页：https://newsboat.org/
- FreshRSS 官方文档：https://freshrss.github.io/FreshRSS/en/
