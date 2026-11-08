#!/usr/bin/env python3
"""Repoint canonical Markdown source links from old repo URLs to local archived files.

Only changes authored learning/navigation Markdown; never edits archived original files.
Idempotent, checks target existence, and reports any source links not remapped.
"""
from __future__ import annotations
import pathlib
import re
import sys
from urllib.parse import unquote, quote, urlsplit
ROOT = pathlib.Path(__file__).resolve().parents[1]
OLD = re.compile(r'https://github[.]com/MulikShrikantDattatray14/Data-Engineering-Mastry/(?:blob|tree)/(?:main|bef07ec3e20825eb8e29bd9afc9f6d7ad8c77e3a)/[^\s)>]+')
ARCHIVE = ROOT / "99. Reference Materials/Original Mastery Snapshot"
SKIP = ("99. Reference Materials/Legacy Journey Snapshot", "99. Reference Materials/Original Mastery Snapshot")
def run():
    edits, substitutions, unresolved = [], 0, []
    for p in ROOT.rglob("*.md"):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(SKIP) or ".git" in p.parts:
            continue
        old_text = p.read_text(encoding="utf-8")
        def replace(match):
            nonlocal substitutions
            original = match.group(0)
            url = urlsplit(original)
            m = re.match(r"/MulikShrikantDattatray14/Data-Engineering-Mastry/(?:blob|tree)/(?:main|bef07ec3e20825eb8e29bd9afc9f6d7ad8c77e3a)/(.*)",url.path)
            if not m:
                return original
            source_name = unquote(m.group(1))
            target = ARCHIVE / source_name
            if not target.exists():
                unresolved.append((rel,original))
                return original
            link = pathlib.Path(__import__("os").path.relpath(target,p.parent)).as_posix()
            link = "/".join(quote(piece, safe="-_.") for piece in link.split("/"))
            if url.fragment:
                link += "#" + url.fragment
            if url.query:
                link += "?" + url.query
            substitutions += 1
            return link
        new_text = OLD.sub(replace,old_text)
        if new_text != old_text:
            p.write_text(new_text,encoding="utf-8")
            edits.append(rel)
    print(f"Repointed {substitutions} original source links across {len(edits)} canonical documents.")
    for x in unresolved[:30]:
        print("UNRESOLVED",*x,file=sys.stderr)
    if unresolved:
        print(f"Unresolved: {len(unresolved)}",file=sys.stderr)
        return 1
    return 0
if __name__ == "__main__":
    raise SystemExit(run())
