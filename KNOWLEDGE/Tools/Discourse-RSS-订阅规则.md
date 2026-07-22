# Discourse RSS 订阅规则

## 本质

RSS 是站点把内容更新暴露给订阅器的一种机器可读格式。Discourse 默认支持多类 RSS 入口，常见做法是在特定页面路径后追加 `.rss`。

## 原理

Discourse 的 RSS 链接通常映射到列表页、分类页、标签页、主题页或用户活动页。分类和主题链接里常见的数字 ID 是稳定定位关键，slug 更多用于可读性。

## 常见格式

- 最新话题：`https://example.com/latest.rss`
- 热门话题：`https://example.com/top.rss`
- 指定时间范围热门：`https://example.com/top.rss?period=weekly`
- 分类：`https://example.com/c/<category_slug>/<category_id>.rss`
- 标签：`https://example.com/tag/<tag_name>.rss`
- 单个主题：`https://example.com/t/<topic_slug>/<topic_id>.rss`
- 用户活动：`https://example.com/u/<username>/activity.rss`

## 验证流程

1. 先打开目标页面，确认 URL 结构。
2. 在 URL 末尾追加 `.rss`，或按官方格式拼接。
3. 用浏览器或 `curl -i -L` 请求。
4. 判断 HTTP 状态码是否为 200。
5. 判断 `Content-Type` 是否为 `application/rss+xml`。

## 常见问题

- 不是所有页面都有 RSS，例如部分 Discourse 实例中 `/new.rss` 可能返回 404。
- 分类 feed 不能只写 slug，通常需要包含分类 ID。
- 站点登录限制、Cloudflare、插件或站点配置可能影响 RSS 可访问性。

## 个人理解

Discourse RSS 的关键不是“记住所有链接”，而是理解 URL 到内容列表的映射：列表页、分类页、主题页都有机会导出 feed；遇到不确定入口时，用状态码和内容类型验证，比靠猜测更可靠。
