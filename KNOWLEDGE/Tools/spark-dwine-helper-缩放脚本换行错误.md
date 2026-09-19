# spark-dwine-helper 缩放脚本换行错误

## 本质

`spark-dwine-helper` 的 `scale-set-helper/get-scale.sh` 在缩放选项列表里有一处错误的行续接：

```bash
3.5  \   
4.0`
```

反斜杠后面带空格，shell 不会把下一行正确合并，结果 `4.0` 会被当成命令执行，出现：

```text
4.0: 未找到命令
```

---

## 原理

shell 中的反斜杠只有在行尾且后面没有其他字符时，才表示续行。  
如果 `\` 后面还有空格，续行关系就会失效，脚本会被拆成两段错误命令。

这类错误常见表现是：

- 某个看起来像参数的数字被当成命令；
- 报错位置指向看似无害的列表末尾；
- 交互式选择器在最后一个选项附近失败。

---

## 流程

排查时先看原脚本：

```bash
nl -ba /opt/spark-dwine-helper/spark-dwine-helper/scale-set-helper/get-scale.sh | sed -n '60,80p'
sed -n '67,76p' /opt/spark-dwine-helper/spark-dwine-helper/scale-set-helper/get-scale.sh | sed -n 'l'
```

如果要临时绕过：

```bash
mkdir -p ~/.config/spark-wine
printf '1.0\n' > ~/.config/spark-wine/scale.txt
```

或者先设置：

```bash
export DEEPIN_WINE_SCALE=1.0
```

如果要永久修复，删除 `\` 后面的空格，并确保行尾续接符紧贴换行。

---

## 问题

常见误判：

- 以为是 Wine 主程序出错；
- 以为是 D-Bus 故障导致整个应用无法启动；
- 直接重建 prefix，但根因其实是初始化脚本。

---

## 个人理解

这种问题属于“封装层脚本缺陷”，不是应用层业务错误。  
先修脚本输入，再看 `TrayManager` 这类桌面依赖是否真的影响启动。
