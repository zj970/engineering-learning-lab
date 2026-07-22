# Soong 预编译库 undefined module 排查

## 本质

`Soong` 报：

```text
"A" depends on undefined module "B"
```

本质是 `Android.bp` 中某个模块的 `shared_libs`、`static_libs` 或其他依赖列表引用了模块 `B`，但当前源码树没有任何可见 `Android.bp` / `Android.mk` 定义这个模块。

在设备适配场景中，常见原因是私有 blob 提取不完整：某个预编译 `.so` 已存在，但它依赖的另一个私有 `.so` 没有被提取，也没有被生成对应 `cc_prebuilt_library_shared` 模块。

---

## 原理

对于预编译共享库，Soong 会读取 `Android.bp`：

```bp
cc_prebuilt_library_shared {
    name: "libA",
    shared_libs: ["libB"],
}
```

如果 `libB` 没有模块定义，即使运行期设备上可能存在同名库，编译期也会失败。

判断 `libB` 是否真实依赖，不能只看 `Android.bp`，还要看 ELF 动态依赖：

```bash
readelf -d path/to/libA.so | grep NEEDED
```

如果 `NEEDED` 中确实存在 `libB.so`，说明它不是脚本随便生成的假依赖，而是这个 blob 的真实动态链接依赖。

---

## 流程

1. 定位报错模块和缺失模块。
2. 搜索源码树中是否已有缺失模块定义：

```bash
rg -n "name: \"libB\"|libB" .
```

3. 检查缺失 `.so` 是否已经存在：

```bash
find . -name 'libB.so'
```

4. 检查依赖方 ELF：

```bash
readelf -d libA.so | grep NEEDED
```

5. 如果 `.so` 不存在，优先从同机型官方 vendor / super / payload 中重新提取。
6. 如果 `.so` 存在但没有模块定义，应补充 `proprietary-files.txt` 并重新运行 `setup-makefiles.sh` 生成 vendor makefile / Android.bp。
7. 不建议直接删除 `shared_libs` 依赖，因为这只是在绕过编译期检查，运行期仍可能因为动态库缺失崩溃。

---

## 问题

当前 `cas` 案例中：

```text
vendor/xiaomi/cas/Android.bp:2000:1: "libI420colorconvert" depends on undefined module "libmm-color-convertor".
```

已确认：

- `libI420colorconvert.so` 存在于 `vendor/xiaomi/cas/proprietary/vendor/lib64/`
- `libmm-color-convertor.so` 当前源码树不存在
- `readelf -d libI420colorconvert.so` 显示真实依赖 `libmm-color-convertor.so`
- `device/xiaomi/cas/proprietary-files.txt` 当前只列了 `libI420colorconvert.so`，没有列 `libmm-color-convertor.so`

因此根因更像是 `cas` 私有 blob 提取不完整，而不是 Soong 本身问题。

---

## 个人理解

`undefined module` 不是简单的“少一行 Android.bp”。在 vendor blob 场景里，它通常意味着“依赖闭包不完整”。正确修复路径是补齐真实 blob 和模块定义，而不是删依赖、改名或随便找同名库替代。
