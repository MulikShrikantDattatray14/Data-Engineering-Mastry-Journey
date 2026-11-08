#!/usr/bin/env python3
"""Validate internal GitHub and relative study links before publishing.

Usage: python scripts/check_study_links.py
Only repository-owned paths are checked; outside websites are not probed.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OWNER = "MulikShrikantDattatray14"
REPO = "data-engineering-journey"
GITHUB_BASE = f"/{OWNER}/{REPO}"
MARKDOWN_LINK = re.compile(r"!?(?:\\?\[[^\]]*\])\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_LINK = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']")
FENCE = re.compile(r"(?ms)^\s*```.*?^\s*```\s*$")
issues = []
checked = 0


def validate(source: str, link: str) -> None:
    """Check an internal link against the actual default-branch file tree."""
    global checked
    link = link.strip().strip("<>")
    if not link or link.startswith("#") or "${" in link:
        return
    u = urlsplit(link)
    if u.scheme in ("mailto", "data", "javascript"):
        return
    if u.scheme in ("http", "https"):
        if u.netloc.lower() != "github.com" or not u.path.startswith(GITHUB_BASE + "/"):
            return
        suffix = u.path[len(GITHUB_BASE):].split("/")
        if len(suffix) < 4 or suffix[1] not in ("blob", "tree"):
            return  # Repo homepage, settings, commits, issues, etc.
        if suffix[2] != "main":
            issues.append(f"{source}: malformed GitHub link (expected /blob/main or /tree/main): {link}")
            return
        candidate = ROOT.joinpath(*map(unquote, suffix[3:])).resolve()
    else:
        if link.startswith("/") or u.scheme:
            return
        candidate = (ROOT / source).parent.joinpath(unquote(u.path)).resolve()

    checked += 1
    if not candidate.is_relative_to(ROOT):
        issues.append(f"{source}: link leaves repository root: {link}")
    elif not candidate.exists():
        issues.append(f"{source}: missing target: {link}")


for md in sorted(ROOT.rglob("*.md")):
    # Exclude generated/cache directories and fenced code examples.
    if ".git" in md.parts or "node_modules" in md.parts:
        continue
    name = md.relative_to(ROOT).as_posix()
    text = FENCE.sub("", md.read_text(encoding="utf-8"))
    for pattern in (MARKDOWN_LINK, HTML_LINK):
        for match in pattern.finditer(text):
            validate(name, match.group(1))

# Static HTML links only. Dynamic JS-template strings are excluded by validate().
for html in sorted((ROOT / "dashboard").glob("*.html")):
    name = html.relative_to(ROOT).as_posix()
    for match in HTML_LINK.finditer(html.read_text(encoding="utf-8")):
        validate(name, match.group(1))

progress_path = ROOT / "progress/daily-progress.json"
if progress_path.exists():
    tracker = json.loads(progress_path.read_text(encoding="utf-8"))
    for day in tracker.get("daily", []):
        prefix = f"progress/daily-progress.json:{day.get('date', 'unknown')}"
        for link in day.get("evidence_links", []):
            validate(prefix, link)
        practice = day.get("practice", {})
        validate(prefix, practice.get("index_url", ""))
        for record in practice.get("questions", []) + practice.get("concepts", []):
            validate(prefix, record.get("url", ""))
        execution = day.get("execution", {})
        for record in execution.get("slots", []) + execution.get("tasks", []):
            validate(prefix, record.get("href", ""))

if issues:
    print(f"FAIL: {len(issues)} broken internal references; {checked} links checked.")
    for issue in issues:
        print(" - " + issue)
    sys.exit(1)
print(f"PASS: {checked} internal GitHub/relative links resolve to existing repository targets.")
