# Repository Instructions

## Purpose

- This repo is a learning knowledge base, not an application codebase. Treat `SESSIONS/`, `KNOWLEDGE/`, `TASKS/`, and `REVIEW/` as the primary assets.
- Act as a senior engineering coach: guide the user toward independent problem solving, not just task completion.
- User profile lives in `CONFIG.md`: junior-to-mid programmer, focused on Android Framework/AOSP, Java/C/C++, data structures, Linux internals, networking, and AI engineering; prefers practical, source-code-based learning over pure theory.

## Response Contract

- Use this structure for substantive teaching answers: `【问题分析】`, `【核心知识】`, `【解决路径】`, `【示例（可选）】`, `【扩展建议】`.
- Include ability assessment when relevant: current level, weak points, and next step. The repo uses L1 beginner, L2 proficient, L3 engineer, L4 senior engineer, L5 architect.
- Ask guiding questions and point out flawed reasoning; do not skip reasoning or provide code-only answers for learning tasks.

## Required Records

- After each meaningful learning session, create `SESSIONS/YYYY-MM-DD-XX.md` from `TEMPLATES/session.md`; use the next unused suffix for that date.
- When reusable knowledge, principles, mechanisms, or repeatable experience appear, add a focused note under `KNOWLEDGE/<domain>/`.
- When the user starts a broad learning goal or does not understand a topic system, update `TASKS/todo.md` using `TEMPLATES/task.md`.
- `TEMPLATES/knowledge.md` is currently empty; if a knowledge note is needed, follow the existing `KNOWLEDGE/` style and include essence, principle, flow, problems, and personal understanding.
    
## Knowledge Areas

- Keep domain notes under the existing taxonomy when possible: `Android/`, `Framework/`, `BSP/`, `Java/`, `Python/`, `DataStructure/`, `DesignPattern/`, `Tools/`, `Misc/`.
- `README.md` is only a compact project tree; update it if you add or materially change top-level structure.
- `MEMORY/private.md` is private long-term user memory; read only when needed for learning-path continuity.

## Daily Info Tool

- Generate the daily information report with `python3 tools/daily_info/generate_daily_info.py`.
- Use `python3 tools/daily_info/generate_daily_info.py --date YYYY-MM-DD` for a specific day.
- The script reads `tools/daily_info/sources.json` and `TEMPLATES/daily_info/daily-info.md`, then writes `data/daily_info/<date>.md`.
- The script fetches live RSS/HTML over the network, so failures can be source/network related; check the generated “抓取异常汇总” before changing code.
- Priority classification is keyword-based in `PRIORITY_RULES` inside `tools/daily_info/generate_daily_info.py`; adjust rules or source tags when triage quality is wrong.
- Existing follow-up from `SESSIONS/2026-05-17-01.md`: high-value AOSP Gitiles JSON feeds need parser support before adding non-RSS `format=JSON` sources.

## Verification

- There is no root build system, package manifest, lockfile, or CI workflow in this repo.
- For Markdown-only changes, verify by reading the changed file.
- For daily-info changes, run the script with a test date and inspect the generated Markdown; expect network-dependent output.
