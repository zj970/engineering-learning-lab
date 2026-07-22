# cas 设备依赖树梳理

## 本质

所谓“设备依赖树”，本质上不是刷机教程，也不是单纯的仓库列表。  
它回答的是下面这几个问题：

- 当前产品入口从哪个 `mk` 文件开始
- 设备树继承了哪些 `common` 配置
- 编译这个设备时，还需要哪些 `device / vendor / kernel / hardware` 仓库
- 哪些依赖是源码级依赖，哪些依赖是 blob / vendor 级依赖

如果这层关系没有理清，后面做 `repo sync`、`lunch`、编译、刷机时就很容易陷入“缺一个仓就补一个仓”的被动状态。

对 `Xiaomi Mi 10 Ultra / cas` 来说，当前最重要的不是立刻全量同步源码，而是先把依赖树骨架读出来，确认：

- 产品入口
- 设备继承链
- 额外依赖仓
- 当前阻塞点

---

## 原理

对于基于 LineageOS 的设备树，查找依赖树通常按固定顺序进行。  
这套顺序不仅适用于 `cas`，后面换别的设备也一样可以复用。

### 1. 从 `AndroidProducts.mk` 找产品入口

这是最上层入口。  
它通常会告诉你当前设备真正的产品定义文件是谁。

在 `cas` 中，对应文件是：

- `device/xiaomi/cas/AndroidProducts.mk`

当前结论：

```make
PRODUCT_MAKEFILES := \
    $(LOCAL_DIR)/lineage_cas.mk
```

也就是说，`lineage_cas.mk` 是 `cas` 的产品主入口。

### 2. 从 `lineage_*.mk` 找产品继承链

第二步看产品定义文件本身继承了什么。

在 `cas` 中，对应文件是：

- `device/xiaomi/cas/lineage_cas.mk`

当前结论：

```make
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)
$(call inherit-product, device/xiaomi/cas/device.mk)
```

这说明：

- `cas` 是 64 位手机产品
- 带 telephony 基础能力
- 继承了 LineageOS 的手机通用配置
- 真正的设备级依赖入口转到 `device/xiaomi/cas/device.mk`

### 3. 从 `device.mk` 找设备级依赖

`device.mk` 是最关键的设备级汇总文件。  
它通常会暴露：

- 继承哪个 `common` 设备树
- 是否显式继承 vendor makefile
- 设备专属 overlay / copy file / package

在 `cas` 中，对应文件是：

- `device/xiaomi/cas/device.mk`

当前已经确认的关键继承关系：

```make
$(call inherit-product, device/xiaomi/sm8250-common/kona.mk)
$(call inherit-product, vendor/xiaomi/cas/cas-vendor.mk)
```

这说明：

- `cas` 不是完全独立设备树，而是建立在 `sm8250-common` 上
- `vendor/xiaomi/cas` 是编译链里的硬依赖

### 4. 从 `lineage.dependencies` 找额外仓库

这是最直接的“依赖声明文件”。  
很多设备树不会在文档里写清楚缺哪些仓，但会在这里告诉你。

在 `cas` 中：

- `device/xiaomi/cas/lineage.dependencies`

内容是：

```json
[
  {
    "repository": "android_device_xiaomi_sm8250-common",
    "target_path": "device/xiaomi/sm8250-common"
  }
]
```

说明 `cas` 专属设备树明确依赖：

- `device/xiaomi/sm8250-common`

在 `sm8250-common` 中：

- `device/xiaomi/sm8250-common/lineage.dependencies`

内容是：

```json
[
  {
    "repository": "android_hardware_xiaomi",
    "target_path": "hardware/xiaomi"
  },
  {
    "repository": "android_kernel_xiaomi_sm8250",
    "target_path": "kernel/xiaomi/sm8250"
  }
]
```

说明 `sm8250-common` 还额外依赖：

- `hardware/xiaomi`
- `kernel/xiaomi/sm8250`

### 5. 从 `BoardConfig*.mk` 找硬件层依赖

如果 `lineage.dependencies` 告诉你“缺哪个仓”，那么 `BoardConfig*.mk` 会告诉你“为什么缺它”。

在 `cas` 当前这条链里，最重要的是：

- `device/xiaomi/sm8250-common/BoardConfigCommon.mk`

已经确认的关键项：

```make
TARGET_KERNEL_SOURCE := kernel/xiaomi/sm8250
TARGET_SURFACEFLINGER_UDFPS_LIB := //hardware/xiaomi:libudfps_extension.xiaomi
```

这两条分别说明：

- 内核源码来自 `kernel/xiaomi/sm8250`
- UDFPS 相关实现来自 `hardware/xiaomi`

也就是说，`hardware/xiaomi` 不是“可能需要”，而是当前配置里已经有明确引用。

### 6. 从 `proprietary-files.txt / extract-files.sh / setup-makefiles.sh` 找 blob 依赖

这类文件解决的是 vendor / blob 层问题。

在 `cas` 中，关键文件有：

- `device/xiaomi/cas/proprietary-files.txt`
- `device/xiaomi/cas/extract-files.sh`
- `device/xiaomi/cas/setup-makefiles.sh`

在 `sm8250-common` 中，关键文件有：

- `device/xiaomi/sm8250-common/proprietary-files.txt`
- `device/xiaomi/sm8250-common/proprietary-files-phone.txt`
- `device/xiaomi/sm8250-common/extract-files.sh`
- `device/xiaomi/sm8250-common/setup-makefiles.sh`

这些文件用来回答：

- 设备需要哪些专有 blob
- 这些 blob 是设备专属还是 common 共享
- 生成 `*-vendor.mk` 的脚本链路是什么

### 7. `README.md` 只能当设备简介，不能当依赖树文档

当前 `device/xiaomi/cas/README.md` 和 `device/xiaomi/sm8250-common/README.md` 主要提供：

- 设备规格
- 芯片平台
- 简单说明

它们可以帮助快速建立设备认知，但不能代替依赖树梳理。

---

## 流程

如果以后要快速判断一个新设备的依赖树，建议固定按下面顺序走：

### 第一步：找产品入口

看：

- `AndroidProducts.mk`

目的：

- 找出当前产品真正入口文件

在 `cas` 中，结论是：

- 入口是 `lineage_cas.mk`

### 第二步：找产品继承链

看：

- `lineage_cas.mk`

目的：

- 确认产品级继承了哪些基础 product 与设备树入口

在 `cas` 中，结论是：

- 产品最终转入 `device/xiaomi/cas/device.mk`

### 第三步：找设备级继承关系

看：

- `device.mk`

目的：

- 找 `common` 设备树
- 找 vendor makefile

在 `cas` 中，结论是：

- 继承 `device/xiaomi/sm8250-common/kona.mk`
- 继承 `vendor/xiaomi/cas/cas-vendor.mk`

### 第四步：找显式依赖仓

看：

- `lineage.dependencies`

目的：

- 找还没同步但构建会需要的仓库

在 `cas` 中，目前结论是：

- `cas -> sm8250-common`
- `sm8250-common -> hardware/xiaomi + kernel/xiaomi/sm8250`

### 第五步：找硬件层硬依赖

看：

- `BoardConfig.mk`
- `BoardConfigCommon.mk`

目的：

- 确认内核、硬件库、分区、平台、屏幕、指纹等关键硬件配置从哪里来

### 第六步：找 blob 与 vendor 生成链

看：

- `proprietary-files*.txt`
- `extract-files.sh`
- `setup-makefiles.sh`

目的：

- 判断 vendor 仓、blob 列表和生成逻辑是否完整

---

## 问题

### 1. `cas` 当前已确认的依赖树骨架

当前已经确认的主链如下：

```text
AndroidProducts.mk
  -> lineage_cas.mk
      -> device/xiaomi/cas/device.mk
          -> device/xiaomi/sm8250-common/kona.mk
          -> vendor/xiaomi/cas/cas-vendor.mk
```

以及显式依赖链：

```text
device/xiaomi/cas/lineage.dependencies
  -> device/xiaomi/sm8250-common

device/xiaomi/sm8250-common/lineage.dependencies
  -> hardware/xiaomi
  -> kernel/xiaomi/sm8250
```

结合当前已经确认存在的仓库，第一版依赖树至少包括：

- `device/xiaomi/cas`
- `device/xiaomi/sm8250-common`
- `vendor/xiaomi/cas`
- `vendor/xiaomi/sm8250-common`
- `kernel/xiaomi/sm8250`
- `hardware/xiaomi`

### 2. 当前已确认的阻塞点

当前最明确的阻塞点不是 `device` 树，也不是 `kernel`，而是：

- `vendor/xiaomi/cas`

具体问题：

- `proprietary_vendor_xiaomi_cas` 仓库本体可访问
- 仓库里当前只有 1 个 `git-lfs` 文件
- 该文件对应对象在远端返回 `404`

缺失文件为：

```text
proprietary/vendor/lib64/camera/com.qti.tuned.cas_semco_ov48c_wide.bin
```

这意味着当前问题不是“整套 vendor 仓不可用”，而是“vendor/cas 存在单点 blob 缺失”。

### 3. 当前待确认项

虽然依赖树骨架已经比较清楚，但还没有完全闭环，当前待确认项包括：

- `hardware/xiaomi` 的具体分支与同步结果
- 去掉 `vendor/xiaomi/cas` 后，其它健康仓是否可以全部同步通过
- `cas-vendor.mk` 是否对缺失的 camera tuning blob 有硬依赖
- 是否存在更完整的 `vendor/xiaomi/cas` 来源

---

## 个人理解

这次以 `cas` 为例，最大的收获不是“找到了几个仓库名”，而是建立了一套更稳定的阅读顺序：

1. 先找产品入口
2. 再找产品继承链
3. 再找设备级继承
4. 再找 `lineage.dependencies`
5. 再看 `BoardConfig*.mk`
6. 最后才去碰 blob 与 vendor 问题

这样做的好处是：

- 不会一开始就被 `vendor` 问题带偏
- 能先确认设备树骨架是不是成立
- 能把“缺仓”和“缺 blob”区分开

对 `cas` 当前这条线来说，已经可以得出一个比较明确的判断：

- 设备树主干是成立的
- `sm8250-common` 继承关系是清晰的
- 当前最主要的问题集中在 `vendor/xiaomi/cas` 的单点 blob 缺失，而不是整套依赖树都不对

后面继续推进时，优先级应该是：

1. 补齐 `hardware/xiaomi`
2. 确认健康仓全部同步通过
3. 再单独处理 `vendor/xiaomi/cas` 的 blob 问题

---

## 参考入口

- `device/xiaomi/cas/AndroidProducts.mk`
- `device/xiaomi/cas/lineage_cas.mk`
- `device/xiaomi/cas/device.mk`
- `device/xiaomi/cas/lineage.dependencies`
- `device/xiaomi/cas/proprietary-files.txt`
- `device/xiaomi/sm8250-common/lineage.dependencies`
- `device/xiaomi/sm8250-common/BoardConfigCommon.mk`
- `device/xiaomi/sm8250-common/proprietary-files.txt`
- LineageOS Wiki: Working with proprietary blobs
- LineageOS Wiki: Extracting blobs from zips
