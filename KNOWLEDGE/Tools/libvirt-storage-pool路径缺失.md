# libvirt storage pool 路径缺失

## 本质

`libvirtd` 报某个目录不存在，通常是 storage pool 指向的本地目录被删除、移动或未创建，但该 pool 仍配置为自动启动。

典型日志：

```text
cannot open directory '/path/to/pool': No such file or directory
Failed to autostart storage pool 'xxx'
```

---

## 原理

libvirt storage pool 是虚拟化资源池，用来管理：

- ISO 文件目录
- 虚拟磁盘目录
- LVM / ZFS / 网络存储等后端

如果 pool 设置了 autostart，`libvirtd` 启动时会自动激活它。目录型 pool 的目标路径不存在时，激活失败，但通常不会阻止系统启动。

---

## 流程

查看 pool：

```bash
virsh pool-list --all
virsh pool-info iso-pool
virsh pool-dumpxml iso-pool
```

保留并修复：

```bash
mkdir -p /home/zj970/work/ISO
virsh pool-start iso-pool
```

不再使用则禁用自动启动：

```bash
virsh pool-autostart iso-pool --disable
```

确认不用后删除定义：

```bash
virsh pool-undefine iso-pool
```

---

## 个人理解

这类问题更像“环境卫生”问题，不是性能根因。它值得清理，因为它会污染开机日志、降低排障效率，但不应和 CPU/GPU 温度异常直接画等号。
