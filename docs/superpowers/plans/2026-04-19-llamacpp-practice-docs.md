# llama.cpp 实操补充文档 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增两篇独立的 `llama.cpp` 实操知识文档，分别覆盖常用命令速查和本地知识库最小链路，并保持现有入门指南不变。

**Architecture:** 采用“主指南不动、补充文档独立新增”的方式，把概念认知、命令操作和知识库链路拆成三层文档。实施时先写命令速查，再写最小链路，最后统一校验结构、边界和文件落盘情况。

**Tech Stack:** Markdown、现有知识库目录结构、终端只读验证命令

---

### Task 1: 编写 `llama.cpp` 常用命令速查

**Files:**
- Create: `/home/zj970/ai-study/KNOWLEDGE/Tools/llama.cpp-常用命令速查.md`
- Reference: `/home/zj970/ai-study/KNOWLEDGE/Tools/llama.cpp-入门指南.md`
- Reference: `/home/zj970/ai-study/docs/superpowers/specs/2026-04-19-llamacpp-practice-docs-design.md`

- [ ] **Step 1: 按固定结构列出文档骨架**

文档必须包含以下章节：

```md
# llama.cpp 常用命令速查

## 本质
## 原理
## 流程
## 示例
## 扩展建议
```

其中：
- `本质` 说明该文档是“命令入口手册”，不是安装教程
- `原理` 只解释命令分类和关键参数思路
- `流程` 说明使用前提与阅读顺序
- `示例` 放入高频命令
- `扩展建议` 提示下一步如何延伸

- [ ] **Step 2: 写入高频命令内容**

示例内容至少覆盖：

```bash
llama-cli --list-devices

llama-cli \
  -m ~/models/chat/qwen2.5-7b-instruct-q4_k_m.gguf \
  -ngl 20 \
  -p "请用三句话解释什么是操作系统" \
  -n 256

llama-cli \
  -m ~/models/coder/qwen2.5-coder-7b-instruct-q4_k_m.gguf \
  -ngl 20 \
  -p "请写一个 Java 函数判断字符串是否为回文，并解释时间复杂度" \
  -n 256

llama-embedding \
  -m ~/models/embed/Qwen3-Embedding-4B-Q4_K_M.gguf \
  -ngl 10 \
  -p "什么是操作系统"

llama-server \
  -m ~/models/chat/qwen2.5-7b-instruct-q4_k_m.gguf \
  -ngl 20 \
  --port 8080
```

每条命令都要补充：
- 这条命令用来干什么
- 为什么需要这些关键参数
- 新手最容易误解的点是什么

- [ ] **Step 3: 补充参数速查和误区**

至少解释以下参数或概念：

```text
-m
-ngl
-n
--port
PATH
LD_LIBRARY_PATH
```

并明确指出：
- `-n` 不是上下文窗口
- `PATH` 和 `LD_LIBRARY_PATH` 不是一回事
- embedding 的输出不是自然语言

- [ ] **Step 4: 自查内容边界**

检查并修正文档，确保：

```text
1. 没有写成安装教程
2. 没有长篇重复入门指南中的概念解释
3. 命令示例都与当前已验证过的模型类型一致
4. 所有命令都可被初学者直接看懂用途
```

- [ ] **Step 5: 验证文件落盘**

Run:

```bash
sed -n '1,260p' /home/zj970/ai-study/KNOWLEDGE/Tools/llama.cpp-常用命令速查.md
```

Expected:

```text
文档包含完整标题与五个结构段落，命令示例和误区章节可见。
```

### Task 2: 编写“本地知识库最小链路”文档

**Files:**
- Create: `/home/zj970/ai-study/KNOWLEDGE/Tools/本地知识库最小链路-embedding-检索-回答.md`
- Reference: `/home/zj970/ai-study/KNOWLEDGE/Tools/llama.cpp-入门指南.md`
- Reference: `/home/zj970/ai-study/docs/superpowers/specs/2026-04-19-llamacpp-practice-docs-design.md`

- [ ] **Step 1: 按固定结构列出文档骨架**

文档必须包含以下章节：

```md
# 本地知识库最小链路：embedding + 检索 + 回答

## 本质
## 原理
## 流程
## 示例
## 扩展建议
```

其中：
- `本质` 解释该文档要回答“最小链路怎么串起来”
- `原理` 解释 embedding、检索、回答三段分工
- `流程` 说明数据如何流动
- `示例` 用伪流程或最小命令说明闭环
- `扩展建议` 说明如何演进到真正 RAG

- [ ] **Step 2: 写清最小链路的数据流**

文档必须明确四步：

```text
1. 文档切分
2. 文档向量化
3. 用户问题向量化并做相似度检索
4. 将召回片段拼进提示词，再交给 chat 模型回答
```

要求写清：
- embedding 模型负责“转向量”
- 检索逻辑负责“找相关内容”
- chat 模型负责“组织最终自然语言回答”

- [ ] **Step 3: 给出最小可理解示例**

示例必须至少包含以下形式之一，并配文字解释：

```text
文档A/文档B -> embedding -> 向量
用户问题 -> embedding -> 问题向量
问题向量 vs 文档向量 -> 相似度排序
Top-K 文本片段 + 用户问题 -> chat 模型 -> 最终回答
```

要求：
- 不引入数据库
- 不引入第三方框架
- 不写成完整 Python 工程实现

- [ ] **Step 4: 写出边界和下一步演进**

必须明确当前方案不覆盖：

```text
向量数据库
reranker
多路召回
知识库更新策略
服务化 API
```

并补充下一步可以如何升级到更完整的本地 RAG。

- [ ] **Step 5: 验证文件落盘**

Run:

```bash
sed -n '1,260p' /home/zj970/ai-study/KNOWLEDGE/Tools/本地知识库最小链路-embedding-检索-回答.md
```

Expected:

```text
文档包含完整标题与五个结构段落，并清晰区分 embedding、检索、回答三段职责。
```

### Task 3: 统一校验与会话沉淀

**Files:**
- Create: `/home/zj970/ai-study/SESSIONS/2026-04-19-27.md`
- Verify: `/home/zj970/ai-study/KNOWLEDGE/Tools/llama.cpp-常用命令速查.md`
- Verify: `/home/zj970/ai-study/KNOWLEDGE/Tools/本地知识库最小链路-embedding-检索-回答.md`

- [ ] **Step 1: 检查两篇新文档与入门指南分工是否清晰**

检查标准：

```text
1. 入门指南负责概念认知
2. 命令速查负责高频命令
3. 最小链路负责知识库闭环
4. 三篇文档没有大段重复
```

- [ ] **Step 2: 写会话记录**

会话记录必须包含：

```md
## 问题
## 分析
## 关键知识点
## 我的薄弱点
## 收获
## 后续任务
```

并明确：
- `我的薄弱点` 用用户视角描述
- `收获` 写用户本轮得到的东西

- [ ] **Step 3: 最终验证文件存在**

Run:

```bash
ls -l \
  /home/zj970/ai-study/KNOWLEDGE/Tools/llama.cpp-常用命令速查.md \
  /home/zj970/ai-study/KNOWLEDGE/Tools/本地知识库最小链路-embedding-检索-回答.md \
  /home/zj970/ai-study/SESSIONS/2026-04-19-27.md
```

Expected:

```text
三个文件都存在，时间戳为当前执行阶段生成。
```
