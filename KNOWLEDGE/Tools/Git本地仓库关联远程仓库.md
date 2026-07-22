# Git 本地仓库关联远程仓库

## 本质

“初始化 Git 仓库”和“关联远程仓库”是两件事：

- 本地存在 `.git/`，说明已经执行过 `git init` 或克隆过仓库。
- `git remote -v` 没有输出，只说明尚未配置远程地址。
- 本地和远程都有独立提交时，需要先判断历史关系，不能直接强推覆盖。

---

## 原理

Git 的本地分支和远程跟踪分支是不同引用：

```text
main              本地分支
origin/main       最近一次 fetch 得到的远程分支状态
origin            远程仓库地址的别名
```

`git fetch` 只更新远程跟踪引用，不会自动修改当前工作区。`git push -u origin main` 则把本地 `main` 推送到远程，并建立 upstream 关系。

---

## 安全流程

### 1. 核对本地状态

```bash
git rev-parse --is-inside-work-tree
git branch --show-current
git status --short --branch
git remote -v
```

### 2. 配置并获取远程

```bash
git remote add origin <remote-url>
git fetch origin main
```

### 3. 比较历史

```bash
git log --oneline --decorate --graph --all
git merge-base main origin/main
```

若 `merge-base` 失败，说明两边没有共同祖先。常见原因是本地先提交过文件，而 GitHub 创建仓库时又初始化了 README 或 LICENSE。

### 4. 提交前保护隐私

先创建 `.gitignore`，再验证：

```bash
git check-ignore -v <private-file>
git status --short
git diff --cached --stat
```

不要在创建忽略规则前直接执行 `git add .`。如果敏感文件已经进入历史，仅补 `.gitignore` 不会删除历史内容。

### 5. 合并独立历史

确认两边内容都要保留后：

```bash
git merge origin/main --allow-unrelated-histories
```

`--allow-unrelated-histories` 只应该在已经确认两条独立历史来源时使用。远程只有 LICENSE、README 等初始化文件时，通常可以显式合并并保留双方提交。

### 6. 推送并建立 upstream

```bash
git push -u origin main
git status --short --branch
```

---

## 常见问题

### 1. 为什么不能直接 `git push --force`？

强推会重写远程分支，可能删除远程已有提交。除非明确知道远程内容应被覆盖，否则优先 fetch、检查和 merge。

### 2. 为什么 `.gitignore` 没有忽略文件？

可能原因：

- 规则路径与实际文件类型不匹配。
- 文件已经被 Git 跟踪。
- 更靠后的否定规则重新包含了该文件。

使用下面的命令查看命中的具体规则：

```bash
git check-ignore -v <path>
```

### 3. 为什么本地是 master，远程是 main？

这是默认分支命名差异。确认团队约定后可在本地改名：

```bash
git branch -m main
```

---

## 个人理解

远程关联的关键不是把 URL 写进 `.git/config`，而是先保护隐私、确认历史关系，再建立可追踪的 upstream。可靠顺序是：

```text
检查 -> 忽略 -> 扫描 -> 提交 -> 合并 -> 推送 -> 验证
```
