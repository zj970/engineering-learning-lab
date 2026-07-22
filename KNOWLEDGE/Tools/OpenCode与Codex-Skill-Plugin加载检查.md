# OpenCode 与 Codex Skill / Plugin 加载检查

## 本质

检查 AI 编码代理的 skill 和 plugin 时，不能只扫描目录。至少要区分四种状态：

1. **已下载**：文件或 marketplace 快照存在于磁盘。
2. **已配置**：配置文件声明了路径或插件。
3. **已发现**：CLI 的诊断命令能列出该项。
4. **已加载**：当前模型提示或插件运行时实际包含该项。

只有目录存在，最多能证明“已下载”。例如 Codex 的 `~/.codex/.tmp/plugins` 是 marketplace 快照，不代表其中的插件已经安装或加载。

---

## 原理

### OpenCode

OpenCode 的 skill 可以来自：

- 内置 skill
- 项目 `.opencode/skill/` 或 `.opencode/skills/`
- 全局 `~/.config/opencode/skill/` 或 `skills/`
- 兼容目录 `~/.claude/skills/`、`~/.agents/skills/`
- `opencode.json` 的 `skills.paths` 或 `skills.urls`

外部 plugin 可以来自：

- `opencode.json` 的 `plugin` 数组
- 项目或全局 `.opencode/plugin(s)/` 下自动发现的 `.js`、`.ts` 文件

`~/.codex/skills` 不是 OpenCode 的默认 skill 来源，所以 Codex 中可用的 skill 不会自动出现在 OpenCode 中。

### Codex

Codex 的 skill 主要来自 `$CODEX_HOME/skills`，系统 skill 位于其中的 `.system/`。CLI 当前没有独立的 `codex skill list`，因此要把目录清单与模型可见提示交叉验证。

Codex plugin 则有明确的管理命令。`codex plugin list --json` 的 `installed` 才是已安装插件；marketplace 只提供候选项。

---

## 检查流程

### 1. 确认版本和配置入口

```bash
opencode --version
opencode debug paths

codex --version
codex doctor --json
```

先确认实际执行的是哪一个版本，避免检查了错误的全局安装或配置目录。

### 2. 检查 OpenCode skill

```bash
opencode debug skill
```

这是 OpenCode 运行时可发现 skill 的主要依据。重点看：

- `name`
- `location`
- 是否出现预期的自定义 skill

### 3. 检查 OpenCode 外部 plugin

```bash
opencode debug config | jq '.plugin // []'

find .opencode/plugin .opencode/plugins \
  ~/.config/opencode/plugin ~/.config/opencode/plugins \
  -maxdepth 2 -type f \( -name '*.js' -o -name '*.ts' \) -print 2>/dev/null
```

第一条检查配置声明，第二条检查自动发现目录。若二者都为空，可以判断没有外部 plugin。

`opencode debug v2` 在 OpenCode `1.18.4` 中没有枚举内置插件名称，不能把它输出的 provider catalog 当作 plugin 清单。

### 4. 检查 Codex skill

```bash
find ~/.codex/skills -name SKILL.md -printf '%h\n' | sort
```

若需要确认“当前模型实际看见什么”，可以使用：

```bash
codex debug prompt-input
```

该命令会输出完整的模型输入，只应在本机检查，不要直接公开原始输出。搜索其中的 `### Available skills` 段落，并与目录清单对照。

### 5. 检查 Codex plugin

```bash
codex plugin list --json
codex plugin marketplace list --json
```

判断规则：

- `installed` 非空：存在已安装插件。
- `marketplaces` 非空：只说明配置了插件来源。
- marketplace 根目录存在大量 manifest：仍不能证明插件已经安装。

---

## 常见问题

### 1. 为什么目录里有 skill，CLI 却看不到？

常见原因包括：

- 目录不在该工具的默认扫描范围
- `SKILL.md` 路径层级或文件名不符合约定
- frontmatter 缺少有效的 `name` 或 `description`
- 工具在启动时加载配置，修改后尚未重启

### 2. 为什么诊断命令在沙箱中失败？

某些“只读诊断”仍会初始化日志或状态文件。例如 OpenCode 会写 `~/.local/share/opencode/log/`，Codex 也可能写 `~/.codex/`。在只允许写工作区的沙箱中，这类命令可能报只读文件系统错误。

这时应先确认错误路径，再仅对原诊断命令申请必要权限，不要直接扩大整个会话的文件系统权限。

### 3. marketplace 中的插件算已加载吗？

不算。marketplace 相当于软件源，插件 manifest 相当于候选包信息；只有安装状态和运行时状态才能证明插件已加载。

---

## 个人理解

可靠的配置排查不是“找到文件就结束”，而是建立证据链：

```text
磁盘文件 -> 配置声明 -> CLI 发现 -> 当前运行时可见
```

越靠右，证据越接近用户实际体验。目录扫描适合定位来源，CLI 解析结果适合确认配置，模型输入或插件安装清单才适合回答“当前加载了什么”。
