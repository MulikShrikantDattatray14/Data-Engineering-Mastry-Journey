#!/usr/bin/env python3
"""Hash-pinned archived Journey-note checks for Bosscoder Python Lecture-04.
Private Academy PDF bytes, platform grades, learner attempts are never published/modified.
"""
from __future__ import annotations
import ast, hashlib, re, subprocess, sys, tempfile
from contextlib import ExitStack
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parents[1] / "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-04"
NOTE_SHA = {
    "01-modules-and-packages.md": "f901a1501a1d652353e918eb8209426549ee18c4",
    "02-namespaces-and-scope.md": "671e4edb860174b0d79f72fb71aefaab800f0b88",
    "03-errors-and-exceptions.md": "23cdfb1223176832609b8ea1404708b2ee707f89",
}
MCQ_SHA = {
    "q01.md": "2da86260dc526bc5207de315bebd8d20aad9fe89",
    "q02.md": "5ef441ab29e04249bdb347a6c0317bb2879d26a0",
    "q03.md": "e846847aea325e52df9988c286601e06f27d0501",
    "q04.md": "2dde93666919e6b35338397f8e292ba5d2df610f",
    "q05.md": "667e329c8db55534e69115940e3a75c0b9e02aa1",
    "q06.md": "5dfe9de35078ee849a7818c88175118d4cb88307",
    "q07.md": "7b3e407edf04b37e1b929195139567dba09f677b",
    "q08.md": "abc35b782290ba0de7d0cb00dc51a02851d1e7d0",
    "q09.md": "8866d908c51ec752cdffe6c1dd4132571dab4364",
    "q10.md": "2c53992126b23446d531b0e520484448efb10fa2",
    "q11.md": "a8ab3c28d5e8ede1cc4118c8c714d2ecb4fccbbc",
}
def pinned_text(path: Path, expected: str) -> str:
    raw = path.read_bytes()
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert digest == expected, f"Archived source mismatch: {path}: {digest} != {expected}"
    return raw.decode("utf-8")
def fences(content: str) -> list[str]:
    mark = chr(96) * 3
    return re.findall(r"^" + re.escape(mark + "python") + r"\s*\n(.*?)^" + re.escape(mark) + r"\s*$",
                      content, flags=re.M | re.S)
def run(source: str, expected: str, path: Path, name="snippet.py") -> None:
    ast.parse(source)
    (path / name).write_text(source, encoding="utf-8")
    p = subprocess.run([sys.executable, name], cwd=path, text=True, capture_output=True, timeout=10)
    assert p.returncode == 0, (name, p.returncode, p.stderr)
    assert p.stdout == expected, (name, repr(p.stdout), repr(expected))
    assert p.stderr == "", (name, p.stderr)
def source_note_checks() -> None:
    m, s, e = [fences(pinned_text(ARCHIVE / name, sha)) for name, sha in NOTE_SHA.items()]
    assert [len(m), len(s), len(e)] == [4, 3, 5], [len(m), len(s), len(e)]
    with tempfile.TemporaryDirectory(prefix="bc04-notes-") as tmp:
        d = Path(tmp)
        ast.parse(m[0])
        (d / "metrics.py").write_text(m[0], encoding="utf-8")
        run(m[1], "236.0\n0.18\n", d, "main.py")
        run(m[2], "Report generated\n", d, "main_guard.py")
        run(m[3], "Counter({'paid': 2, 'pending': 1})\n{\"rows\": 3}\n", d)
        for code, out in zip(s, ["('local', 'enclosing') global\n", "1 2\n", "2\n"], strict=True):
            run(code, out, d)
        for code, out in zip(e, ["Invalid position\n",
            "Could not parse count: invalid literal for int() with base 10: 'unavailable'\n",
            "", "", "Successfully parsed 12\nValidation attempt finished\n"], strict=True):
            run(code, out, d)
    print("PASS: 12/12 public archived Python note fences (including 2-file module example)")
    for name, sha in MCQ_SHA.items():
        t = pinned_text(ARCHIVE / "assignments" / name, sha)
        assert "**Status:** Pending student selection" in t, name
        assert "**Selection:** Pending" in t and "**Reviewed:** Pending" in t, name
        assert "## Question" in t and "## Four choices" in t, name
    print("PASS: 11/11 individual MCQ source-paraphrase hashes/statuses (ungraded)")
def synthetics() -> None:
    with tempfile.TemporaryDirectory(prefix="bc04-boundary-") as tmp:
        d = Path(tmp)
        code = "def f(): return 7\nif __name__ == '__main__':\n print('DIRECT')\n"
        (d / "demo.py").write_text(code, encoding="utf-8")
        run("import demo\nprint(demo.f())\n", "7\n", d, "importer.py")
        run(code, "DIRECT\n", d, "demo.py")
    print("PASS synthetic 1: main guard / import")
    try:
        exec(compile("x=7\ndef f():\n print(x)\n x=8\nf()\n", "<synthetic>", "exec"), {})
    except UnboundLocalError: pass
    else: raise AssertionError("UnboundLocalError expected")
    print("PASS synthetic 2: local variable binding")
    events = []
    try:
        try:
            events.append("try"); raise ValueError("bad")
        finally: events.append("inner-finally")
    except ValueError: events.append("outer-except")
    finally: events.append("outer-finally")
    assert events == ["try", "inner-finally", "outer-except", "outer-finally"]
    print("PASS synthetic 3: nested finally order")
    assert issubclass(ValueError, Exception) and not issubclass(KeyboardInterrupt, Exception)
    assert issubclass(KeyboardInterrupt, BaseException)
    print("PASS synthetic 4: exception hierarchy")
    events = []
    with ExitStack() as stack:
        stack.callback(events.append, "first"); stack.callback(events.append, "second")
    assert events == ["second", "first"]
    print("PASS synthetic 5: ExitStack callback order")
    original = ValueError("bad")
    try:
        try: raise original
        except ValueError as exc: raise RuntimeError("wrapped") from exc
    except RuntimeError as exc: assert exc.__cause__ is original
    else: raise AssertionError("Chained RuntimeError expected")
    print("PASS synthetic 6: chained cause")
if __name__ == "__main__":
    source_note_checks()
    synthetics()
    print("PASS: Lecture 04 public notes (not original Academy PDF execution/grading or learner mastery)")
