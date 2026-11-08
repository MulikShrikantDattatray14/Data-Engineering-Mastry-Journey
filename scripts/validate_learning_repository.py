"""Offline checks for canonical learning notes, source integrity and progress."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def check(ok: bool, message: str) -> None:
    if not ok:
        errors.append(message)


def git_blob_sha(path: Path) -> str:
    content = path.read_bytes()
    header = f"blob {len(content)}\\0".encode()
    return hashlib.sha1(header + content).hexdigest()


def check_sources() -> None:
    manifest = json.loads((ROOT / "99. Reference Materials/SOURCE-INVENTORY.json").read_text(encoding="utf-8"))
    entries = manifest["entries"]
    check(len(entries) == 744, f"Expected 744 inventory entries, found {len(entries)}")

    journey = [e for e in entries if e["source"] == "data-engineering-journey/main"]
    mastery = [e for e in entries if e["source"] == "Data-Engineering-Mastry/main"]
    check(len(journey) == 192, f"Expected 192 Journey entries, found {len(journey)}")
    check(len(mastery) == 552, f"Expected 552 pinned Mastery entries, found {len(mastery)}")

    old_prefix = "UNIFIED-REPOSITORY/99. Reference Materials/Legacy Journey Snapshot/"
    for e in journey:
        relative = e["preserved_path"]
        if relative.startswith(old_prefix):
            relative = "99. Reference Materials/Legacy Journey Snapshot/" + relative[len(old_prefix):]
        f = ROOT / relative
        check(f.is_file(), f"Missing historic Journey source: {relative}")
        if f.is_file():
            check(git_blob_sha(f) == e["git_blob_sha"], f"Changed historic Journey blob: {relative}")

    submodule_path = "99. Reference Materials/Original Mastery Repository"
    stage = subprocess.run(["git", "ls-files", "--stage", "--", submodule_path],
                           cwd=ROOT, check=True, capture_output=True, text=True).stdout
    check("160000 bef07ec3e20825eb8e29bd9afc9f6d7ad8c77e3a" in stage,
          "Mastery submodule pin has changed; reverify original 552 source entries")


def check_indexes() -> None:
    index = json.loads((ROOT / "99. Reference Materials/TOPIC-AND-PROBLEM-INDEX.json").read_text(encoding="utf-8"))
    pages = [x["pdf_page"] for x in index["python"]["indexed_lesson_pages"]]
    check(sorted(pages) == list(range(5, 81)), "Python PDF lessons do not cover every page from 5 through 80 exactly once")
    ids = [x["id"] for x in index["sql"]["pnpmastery_questions"]]
    check(len(ids) == 205 and len(set(ids)) == 205, "PNP SQL problem IDs must be 205 distinct source IDs")

    active = ROOT / "10. Learning Progress/daily-progress.json"
    plan = json.loads(active.read_text(encoding="utf-8"))
    check(isinstance(plan.get("daily"), list), "Canonical progress file lacks daily array")
    for date in ("2026-11-07", "2026-11-08"):
        days = [d for d in plan["daily"] if d.get("date") == date]
        check(len(days) == 1, f"Missing unique holiday entry {date}")
        if days:
            check(days[0].get("study_status") == "holiday_no_study", f"Holiday incorrectly credited as studied: {date}")


def check_local_markdown_links() -> None:
    # Original references may retain their own older relative links. Audit canonical pages here.
    files = (ROOT / "01. SQL Mastery", ROOT / "02. Python Mastery",
             ROOT / "03. Database Design and Modeling", ROOT / "04. Data Pipelines and ETL",
             ROOT / "05. Apache Spark", ROOT / "06. Cloud and Orchestration",
             ROOT / "07. Data System Design", ROOT / "08. Projects",
             ROOT / "09. Interview Preparation", ROOT / "10. Learning Progress",
             ROOT / "99. Reference Materials", ROOT / "docs")
    rx = re.compile(r"\\]\\((?:<([^>]+)>|([^)]*))\\)")
    for folder in files:
        for md in folder.rglob("*.md"):
            if "Legacy Journey Snapshot" in md.parts:
                continue
            content = md.read_text(encoding="utf-8")
            for match in rx.finditer(content):
                href = (match.group(1) or match.group(2)).strip()
                if not href or href.startswith(("#", "mailto:")) or re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I):
                    continue
                relative = unquote(href.split("#", 1)[0])
                path = (md.parent / relative).resolve()
                check(path.is_relative_to(ROOT), f"Relative link escapes repository: {md.relative_to(ROOT)} -> {href}")
                if path.is_relative_to(ROOT):
                    check(path.exists(), f"Broken internal link: {md.relative_to(ROOT)} -> {href}")


def main() -> int:
    check_sources()
    check_indexes()
    check_local_markdown_links()
    if errors:
        for error in errors:
            print("FAIL:", error)
        print(f"Total failures: {len(errors)}")
        return 1
    print("PASS: 192 Journey files SHA-verified, Mastery source submodule pinned,")
    print("      76 Python PDF pages and 205 PNP SQL IDs indexed,")
    print("      canonical progress and local Markdown links validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
