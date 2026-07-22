#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any
import re
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
SOURCES_FILE = ROOT / "tools" / "daily_info" / "sources.json"
TEMPLATE_FILE = ROOT / "TEMPLATES" / "daily_info" / "daily-info.md"
OUTPUT_DIR = ROOT / "data" / "daily_info"
USER_AGENT = "Mozilla/5.0 (daily-info-bot)"
MAX_ITEMS_PER_SOURCE = 5

PRIORITY_RULES = {
    "高优先级": ["official", "官方", "aosp", "kernel", "framework", "release", "research", "security"],
    "中优先级": ["tool", "效率", "ai", "linux", "android", "工程"],
}
ERROR_PREFIX = "抓取失败："
TRANSLATION_PLACEHOLDER = "中文翻译待补充"
TRANSLATABLE_CHARS_RE = re.compile(r"[A-Za-z]")
LOCAL_ITEM_RE = re.compile(r"^- \[(?P<title>.+?)\]\((?P<link>[^)]+)\)", re.MULTILINE)


def load_sources() -> dict[str, Any]:
    return json.loads(SOURCES_FILE.read_text(encoding="utf-8"))


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")


def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_bilingual_summary(summary: str, is_error: bool = False) -> dict[str, str]:
    english = summary.strip() if summary else "No summary available."
    if is_error:
        return {
            "summary_en": english,
            "summary_zh": "当前抓取失败，暂无中文翻译。",
        }
    if not TRANSLATABLE_CHARS_RE.search(english):
        return {
            "summary_en": english,
            "summary_zh": "原文非英文或信息不足，建议人工补充中文说明。",
        }
    return {
        "summary_en": english,
        "summary_zh": TRANSLATION_PLACEHOLDER,
    }


def parse_rss(content: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    root = ET.fromstring(content)
    for item in root.findall(".//item")[:MAX_ITEMS_PER_SOURCE]:
        title = clean_text(item.findtext("title", default="无标题"))
        link = clean_text(item.findtext("link", default=""))
        summary = clean_text(item.findtext("description", default=""))[:160]
        items.append({"title": title, "link": link, "summary": summary})
    if items:
        return items
    ns_entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")[:MAX_ITEMS_PER_SOURCE]
    for entry in ns_entries:
        title = clean_text(entry.findtext("{http://www.w3.org/2005/Atom}title", default="无标题"))
        link = ""
        for link_node in entry.findall("{http://www.w3.org/2005/Atom}link"):
            href = link_node.attrib.get("href", "")
            rel = link_node.attrib.get("rel", "alternate")
            if href and rel == "alternate":
                link = href
                break
            if href and not link:
                link = href
        summary = clean_text(entry.findtext("{http://www.w3.org/2005/Atom}summary", default=""))[:160]
        if not summary:
            summary = clean_text(entry.findtext("{http://www.w3.org/2005/Atom}content", default=""))[:160]
        items.append({"title": title, "link": link, "summary": summary})
    return items


def parse_html(content: str) -> list[dict[str, str]]:
    titles = re.findall(r"<a[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", content, flags=re.I | re.S)
    items: list[dict[str, str]] = []
    for link, raw_title in titles:
        title = clean_text(raw_title)
        if len(title) < 12:
            continue
        if title.lower() in {"sign in", "read more", "home"}:
            continue
        items.append({"title": title[:120], "link": link, "summary": "HTML title capture only. Manual review recommended."})
        if len(items) >= MAX_ITEMS_PER_SOURCE:
            break
    return items


def normalize_title(title: str) -> str:
    title = clean_text(title).lower()
    title = re.sub(r"[^\w\u4e00-\u9fff]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def normalize_link(link: str) -> str:
    if not link:
        return ""
    parts = urlsplit(link.strip())
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/")
    return urlunsplit((scheme, netloc, path, "", ""))


def dedupe_items(items: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    deduped: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    removed = 0

    for item in items:
        if item["title"].startswith(ERROR_PREFIX):
            deduped.append(item)
            continue
        key = (normalize_title(item.get("title", "")), normalize_link(item.get("link", "")))
        if key in seen_keys:
            removed += 1
            continue
        seen_keys.add(key)
        deduped.append(item)
    return deduped, removed


def load_local_history_keys(output_date: str) -> set[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    current_filename = f"{output_date}.md"

    if not OUTPUT_DIR.exists():
        return keys

    for path in sorted(OUTPUT_DIR.glob("*.md")):
        if path.name == current_filename:
            continue
        content = path.read_text(encoding="utf-8")
        for match in LOCAL_ITEM_RE.finditer(content):
            key = (normalize_title(match.group("title")), normalize_link(match.group("link")))
            if key[0] or key[1]:
                keys.add(key)
    return keys


def dedupe_against_local_history(
    items: list[dict[str, Any]],
    local_history_keys: set[tuple[str, str]],
) -> tuple[list[dict[str, Any]], int]:
    if not local_history_keys:
        return items, 0

    deduped: list[dict[str, Any]] = []
    removed = 0

    for item in items:
        key = (normalize_title(item.get("title", "")), normalize_link(item.get("link", "")))
        if key in local_history_keys:
            removed += 1
            continue
        deduped.append(item)
    return deduped, removed


def classify_priority(item: dict[str, Any]) -> str:
    if item.get("title", "").startswith(ERROR_PREFIX):
        return "抓取异常"
    haystack = " ".join([
        item.get("title", ""),
        item.get("summary_en", item.get("summary", "")),
        " ".join(item.get("tags", [])),
    ]).lower()
    for label, keywords in PRIORITY_RULES.items():
        if any(keyword in haystack for keyword in keywords):
            return label
    return "低优先级"


def build_category_section(category_name: str, items: list[dict[str, Any]]) -> str:
    lines = [f"### {category_name}", ""]
    if not items:
        lines.append("- 暂无可用条目")
        return "\n".join(lines)
    for item in items:
        lines.append(
            f"- [{item['title']}]({item['link']})"
            f"\n  - 来源：{item['source_name']}"
            f"\n  - 标签：{', '.join(item['tags'])}"
            f"\n  - 简介（EN）：{item['summary_en'] or 'No summary available.'}"
            f"\n  - 简介（ZH）：{item['summary_zh'] or '中文翻译待补充'}"
            f"\n  - 初步分类：{item['priority']}"
        )
    return "\n".join(lines)


def build_issue_section(issues_by_category: dict[str, list[dict[str, Any]]]) -> str:
    if not issues_by_category:
        return "- 今日无抓取异常"
    sections: list[str] = []
    for category_name, issues in issues_by_category.items():
        sections.append(f"### {category_name}")
        sections.append("")
        for item in issues:
            sections.append(
                f"- {item['source_name']}"
                f"\n  - 地址：{item['link']}"
                f"\n  - 错误：{item['summary_en']}"
            )
        sections.append("")
    return "\n".join(sections).strip()


def render_priority_section(items: list[dict[str, Any]]) -> str:
    if not items:
        return "- 暂无"
    return "\n".join([f"- {item['title']}（{item['source_name']}）" for item in items[:8]])


def generate(output_date: str) -> Path:
    source_data = load_sources()
    category_sections: list[str] = []
    collected: list[dict[str, Any]] = []
    issues_by_category: dict[str, list[dict[str, Any]]] = {}
    dedup_removed_total = 0
    local_dedup_removed_total = 0
    local_history_keys = load_local_history_keys(output_date)

    for category in source_data["categories"]:
        category_items: list[dict[str, Any]] = []
        category_issues: list[dict[str, Any]] = []
        for source in category["sources"]:
            try:
                content = fetch_text(source["url"])
                raw_items = parse_rss(content) if source["type"] == "rss" else parse_html(content)
            except Exception as error:
                raw_items = [{
                    "title": f"抓取失败：{source['name']}",
                    "link": source["url"],
                    "summary": f"Fetch error: {error}",
                }]
            for raw_item in raw_items:
                bilingual_summary = build_bilingual_summary(
                    raw_item.get("summary", ""),
                    is_error=raw_item.get("title", "").startswith(ERROR_PREFIX),
                )
                item = {
                    **raw_item,
                    **bilingual_summary,
                    "source_name": source["name"],
                    "tags": source.get("tags", []),
                }
                item["priority"] = classify_priority(item)
                if item["priority"] == "抓取异常":
                    category_issues.append(item)
                    continue
                category_items.append(item)

        category_items, removed_count = dedupe_items(category_items)
        dedup_removed_total += removed_count
        category_items, local_removed_count = dedupe_against_local_history(category_items, local_history_keys)
        local_dedup_removed_total += local_removed_count
        category_sections.append(build_category_section(category["name"], category_items))
        collected.extend(category_items)
        if category_issues:
            issues_by_category[category["name"]] = category_issues

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    high = [item for item in collected if item["priority"] == "高优先级"]
    medium = [item for item in collected if item["priority"] == "中优先级"]
    low = [item for item in collected if item["priority"] == "低优先级"]
    issue_count = sum(len(items) for items in issues_by_category.values())
    top_focus = high[0]["title"] if high else (medium[0]["title"] if medium else "暂无，建议人工选择 1 条深读")

    content = template
    content = content.replace("{{date}}", output_date)
    content = content.replace("{{generated_at}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    content = content.replace("{{total_items}}", str(len(collected)))
    content = content.replace("{{dedup_removed}}", str(dedup_removed_total))
    content = content.replace("{{local_dedup_removed}}", str(local_dedup_removed_total))
    content = content.replace("{{issue_count}}", str(issue_count))
    content = content.replace("{{top_focus}}", top_focus)
    content = content.replace("{{needs_review}}", str(len(medium) + len(low)))
    content = content.replace("{{category_sections}}", "\n\n".join(category_sections))
    content = content.replace("{{high_priority}}", render_priority_section(high))
    content = content.replace("{{medium_priority}}", render_priority_section(medium))
    content = content.replace("{{low_priority}}", render_priority_section(low))
    content = content.replace("{{issue_sections}}", build_issue_section(issues_by_category))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{output_date}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成每日信息 Markdown")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    args = parser.parse_args()
    path = generate(args.date)
    print(path)
