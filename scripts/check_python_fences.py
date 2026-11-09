"""Check syntactic validity of all fenced Python snippets in canonical notes.

This is intentionally *syntax only*. It does not pretend that snippets with
external files, network services, or interactive input are executable in CI.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "02. Python Mastery"
FENCE = re.compile(r"(?ms)^([ 	]*)(```|~~~)(python|py)\s*\n(.*?)^\1\2\s*$")


def main() -> int:
    files = sorted(CANONICAL.glob("*/0. Foundation Notes.md"))
    if not files:
        print("FAIL: no canonical Python foundation notes found")
        return 1

    failed = []
    checked = 0
    for path in files:
        body = path.read_text(encoding="utf-8-sig")
        for index, match in enumerate(FENCE.finditer(body), 1):
            checked += 1
            code = match.group(4)
            try:
                ast.parse(code, filename=f"{path.name}:block-{index}")
            except SyntaxError as error:
                failed.append(f"{path.relative_to(ROOT)} block {index}: "
                              f"{error.msg} at snippet line {error.lineno}")

    for failure in failed:
        print("FAIL:", failure)
    print(f"Python syntax audit: {checked} fenced blocks in {len(files)} canonical chapters; "
          f"{len(failed)} errors")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
