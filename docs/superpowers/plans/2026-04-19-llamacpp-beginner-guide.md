# llama.cpp Beginner Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a beginner-oriented `llama.cpp` guide for readers with Linux basics and update project structure docs to include the new `Tools` knowledge category.

**Architecture:** Create one focused knowledge document under `KNOWLEDGE/Tools/` that explains `llama.cpp` by layers:定位、组件、模型类型、量化与显存、最小示例、GUI/服务化、常见误区和推荐组合。 Update `README.md` only to reflect the new knowledge category and keep the repository tree accurate.

**Tech Stack:** Markdown, existing repository structure

---

### Task 1: Create The Knowledge Guide

**Files:**
- Create: `/home/zj970/ai-study/KNOWLEDGE/Tools/llama.cpp-入门指南.md`
- Test: manual markdown and content review

- [ ] **Step 1: Write the guide sections**

```markdown
# llama.cpp 入门指南

## 本质
## 原理
## 流程
## 问题
## 个人理解
```

- [ ] **Step 2: Verify section coverage**

Run: `sed -n '1,260p' /home/zj970/ai-study/KNOWLEDGE/Tools/llama.cpp-入门指南.md`
Expected: the guide covers 定位、组件、模型类型、量化、示例、GUI、误区和推荐组合.

### Task 2: Update Repository Structure Docs

**Files:**
- Modify: `/home/zj970/ai-study/README.md`

- [ ] **Step 1: Add Tools to the README tree**

```markdown
├── KNOWLEDGE/
│   ├── Android/
│   ├── DataStructure/
│   ├── DesignPattern/
│   ├── Framework/
│   ├── Misc/
│   └── Tools/
```

- [ ] **Step 2: Verify the README tree**

Run: `sed -n '1,260p' /home/zj970/ai-study/README.md`
Expected: `KNOWLEDGE/Tools/` appears in the tree and no unrelated structure changes are introduced.

### Task 3: Record The Session

**Files:**
- Create: `/home/zj970/ai-study/SESSIONS/2026-04-19-26.md`

- [ ] **Step 1: Write the session summary**

```markdown
# 会话记录
...
```

- [ ] **Step 2: Verify the session file**

Run: `sed -n '1,220p' /home/zj970/ai-study/SESSIONS/2026-04-19-26.md`
Expected: the file records the document design approval and implementation outcome.
