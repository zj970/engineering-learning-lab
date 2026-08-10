# Sunshine 与 Moonlight 清晰度调优

## 本质

串流画面清晰度由一条完整链路共同决定：

```text
主机桌面分辨率/比例
  -> Sunshine 捕获
  -> H.264 / HEVC / AV1 编码
  -> Wi-Fi / 有线网络传输
  -> Pad 硬件解码
  -> 缩放到 Pad 屏幕
```

调高码率只能减少压缩损失，无法补回源分辨率缺失的像素。如果主机只捕获 1920x1080，2.5K 或 2.8K Pad 最终仍要放大 1080p，文字和细线会发虚。

---

## 原理

### 1. 先匹配分辨率和宽高比

优先让主机实际输出、Moonlight 请求视口和 Pad 屏幕比例一致。三者不一致会产生缩放、黑边或裁切。

- 16:9 Pad：可先测试 2560x1440@60。
- 16:10 Pad：优先使用 2560x1600@60 等同宽高比模式。
- 3:2 Pad：优先建立接近原生比例的主机显示模式或虚拟显示器。

Moonlight 选择更高分辨率不代表主机桌面会自动变成该分辨率。必须从 Sunshine 日志同时确认客户端视口与 `Desktop resolution`。

### 2. 再确认实际编码格式

在相同主观质量下，HEVC 通常比 H.264 更节省码率；AV1 还要求 Pad 提供稳定的硬件解码。不能只看 RTX 显卡支持什么，必须看客户端在 RTSP 协商中声明什么，以及 Sunshine 最终创建了哪个编码器。

```text
clientSupportHevc:0 + h264_nvenc -> 当前实际是 H.264
clientSupportHevc:1 + hevc_nvenc -> HEVC 已真正生效
```

如果 Pad 不支持对应格式的硬件解码，强制使用它可能增加延迟、耗电或直接回退。

### 3. 码率必须服从网络稳定性

清晰度和稳定性存在约束关系：码率超过链路持续承载能力后，丢包、重传恢复和网络抖动会使体验更差。

可用于 60 FPS 局域网基线测试的起点：

| 分辨率 | HEVC 起点 | H.264 起点 |
|--------|-----------|------------|
| 1920x1080 | 25-40 Mbps | 40-60 Mbps |
| 2560x1440 / 2560x1600 | 50-60 Mbps | 60-80 Mbps |
| 2.8K 附近 | 60-80 Mbps | 80-100 Mbps |

这些值不是固定答案。每次增加 10 Mbps 后观察 Moonlight 性能统计；`Frames dropped by network connection` 应长期接近 0%。

### 4. 编码参数用于提高码率利用效率

对 NVENC，Sunshine 官方文档给出两项明确建议：

- `nvenc_twopass = quarter_res`：官方默认值。两遍编码改善运动矢量检测和帧内码率分配，并减少码率尖峰。
- `nvenc_h264_cavlc = disabled`：使用默认 CABAC。CAVLC 已过时，同画质约多需要 10% 码率，只适合很老的解码设备。

更高的 `nvenc_preset` 能改善固定码率下的压缩质量，但会增加编码延迟。应从 P1/P2 向 P4 小步测试，并持续观察服务端帧处理耗时，不要一开始就使用 P7。

---

## 排查流程

1. 在 Moonlight 打开性能统计，记录网络丢帧、网络抖动丢帧、解码延迟和渲染延迟。
2. 从 Sunshine 会话初始化日志确认客户端视口、FPS、请求码率和编码格式。
3. 确认 Sunshine 捕获的 `Desktop resolution` 与客户端请求一致。
4. 先用 60 FPS 建立稳定基线，再改变分辨率或码率；每轮只改一个变量。
5. 网络丢帧接近 0% 后再提高码率；若已经清晰但延迟升高，回退上一档。

网络侧基线是主机有线连接路由器、Pad 使用 5 GHz 或 6 GHz Wi-Fi，并避免 VPN/代理改变局域网 UDP 路由。Android 客户端帧节奏先使用 Moonlight 官方推荐的 `Balanced`。

---

## 常见问题

### FEC 显示 40% 就代表丢包 40% 吗？

不一定。Sunshine 可能为满足最少 parity shard 数量，在很小的 FEC block 上自动抬高百分比。真正的网络判断要看 Moonlight 的网络丢帧/抖动统计，以及 Sunshine 是否出现 `sendmsg`、`sendmmsg` 错误。

### Moonlight 设置 100 Mbps，为什么 Sunshine 只有 60 Mbps？

Sunshine 的 `max_bitrate` 会截断客户端请求。某些 nightly 构建还可能出现 Web UI 单位文案与运行语义不一致。可将主机上限设为 0，让 Moonlight 单点控制码率，并以运行日志中的 `Streaming bitrate` 复核。

### 服务端编码只有 2 ms，为什么仍然模糊？

编码快只说明 GPU 能按时产出帧，不说明源分辨率足够、编码格式高效或码率足够。清晰度问题要先看源分辨率和客户端缩放。

### 为什么详细日志不应长期打开？

Verbose/debug 会持续产生大量逐帧日志。官方文档提示这可能影响串流性能；完成诊断后应恢复 Info 级别。

---

## 个人理解

清晰度调优的正确顺序是：

```text
分辨率与比例 > 实际编码格式 > 编码效率参数 > 码率 > 网络微调
```

先提高码率很容易掩盖源分辨率错误，并把问题转化成 Wi-Fi 丢包。每次都从运行时协商验证设置是否真正生效，比只查看界面选项可靠。

---

## 参考资料

- [Sunshine 配置文档](https://docs.lizardbyte.dev/projects/sunshine/latest/md_docs_2configuration.html)
- [Sunshine 当前版本配置源码](https://github.com/LizardByte/Sunshine/blob/14ffa6fdaa53f7b51512be2b3d24f3939695403c/docs/configuration.md)
- [Moonlight 常见问题](https://github.com/moonlight-stream/moonlight-docs/wiki/Frequently-Asked-Questions)
- [Moonlight Android](https://github.com/moonlight-stream/moonlight-android)
