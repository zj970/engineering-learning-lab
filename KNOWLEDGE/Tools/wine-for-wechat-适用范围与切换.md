# wine-for-wechat 适用范围与切换

## 本质

`wine-for-wechat` 是 Arch Linux 上面向普通微信 `WeChat` 的 Wine 补丁版方案，常和 `wine-wechat-setup` 一起使用。  
它不是企业微信 `WeCom` 的通用替代品。

---

## 原理

ArchWiki 和 Arch Linux 中文论坛给出的推荐链路是：

```text
wine-for-wechat
-> 提供面向微信的补丁版 Wine
-> wine-wechat-setup 负责安装、启动和配置
```

这个方案的目标是普通微信客户端。  
企业微信 `com.qq.weixin.work.deepin` 是另一条基于 Deepin Wine 的封装链路，启动脚本、依赖、D-Bus 假设都不同。

---

## 流程

如果目标是普通微信：

```bash
sudo pacman -Rns com.qq.weixin.work.deepin deepin-wine10-stable spark-dwine-helper
yay -S wine-for-wechat wine-wechat-setup
```

然后按 `wine-wechat-setup` 的提示下载微信安装包并完成配置。

如果目标仍然是企业微信：

- 不要直接切到 `wine-for-wechat`；
- 应该继续修复 Deepin Wine 封装链路或换专门的企业微信方案。

---

## 问题

常见误判：

- 把微信和企业微信当成同一个兼容层问题；
- 看到论坛里说 `wine-for-wechat` 就默认可以替代企业微信；
- 没先确认当前目标应用到底是哪一个。

---

## 个人理解

兼容层方案不是只看“能不能跑 Wine”，还要看它服务的具体应用和封装脚本。  
微信和企业微信表面相近，实际是两条不同的安装和启动路径。
