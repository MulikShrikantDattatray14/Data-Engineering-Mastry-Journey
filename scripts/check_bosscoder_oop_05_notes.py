#!/usr/bin/env python3
"""Audit original preserved Journey-derived Bosscoder OOP Lecture 05 notes.
The 20-page private Academy PDF, original graded MCQ answers, and learner records
are NOT public CI inputs. Do not count these checks as Academy grades/mastery.
"""
from __future__ import annotations

import ast
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ARCHIVE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-05"
)
NOTE_SHA = {
    "01-classes-objects-methods.md": "d4edea0c25bb4e3ba9f993c7be510783d53ba3cb",
    "02-inheritance-and-mro.md": "37fcd48c2ae27037ac7240d08ccd1a33be73c611",
    "03-encapsulation-polymorphism-abstraction.md": "e8fd269bfdaab9f667746e1ebdf371a0ecf7de21",
}
MCQ_SHA = {
    "q01-class-instance-attributes.md": "5af9009d9f01b17366c641efcd54f0b16910c969",
    "q02-private-name-hasattr.md": "f34d83fabdef488eb501ec8dda7eef60d436cd52",
    "q03-method-shadowing.md": "9ba45edd4052c7e436ca54ef12ff8845946a0d4a",
    "q04-staticmethod-class-call.md": "4189716be2e86ec62cb2598fb7648031751b7d5b",
    "q05-method-shadowing-variant.md": "fe2b5837a64ba60d1f2ea696b5a29c62632241a2",
    "q06-abstract-class.md": "74ae715d294ac099291724c7434c9102af0ede68",
    "q07-polymorphic-override.md": "5a18928eb83ee05720444bb77d3645634a968b5d",
    "q08-diamond-method-resolution.md": "d2fc2d897589947e1fb6f4aafecf9101bbb55357",
    "q09-mro-tuple.md": "46d2054921d7a907be8640afb16922db0c18f5de",
    "q10-subclass-constructor.md": "9593fa307e7a692c97672252c4da5cdae70d5926",
    "q11-shared-class-list.md": "ad68c62247b10da80e11d7680ec74867e27b832b",
    "q12-explicit-super.md": "4ef15709785cf6f7a34759682631aaef17ab21a9",
}


def pinned_text(path: Path, expected: str) -> str:
    raw = path.read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()
    assert sha == expected, (path, sha, expected)
    return raw.decode("utf-8")


def python_fences(markdown: str) -> list[str]:
    marker = chr(96) * 3
    return re.findall(
        r"^" + re.escape(marker + "python") + r"\\s*\\n(.*?)^" + re.escape(marker) + r"\\s*$",
        markdown, flags=re.M | re.S,
    )


def execute(code: str, expected: str, directory: Path, label: str) -> None:
    ast.parse(code)
    (directory / "lesson.py").write_text(code, encoding="utf-8")
    p = subprocess.run(
        [sys.executable, "lesson.py"], cwd=directory, capture_output=True, text=True, timeout=10,
    )
    assert p.returncode == 0 and p.stderr == "", (label, p.returncode, p.stderr)
    assert p.stdout == expected, (label, repr(p.stdout), repr(expected))


def archived_source_contracts() -> None:
    all_notes = [python_fences(pinned_text(ARCHIVE / name, sha)) for name, sha in NOTE_SHA.items()]
    assert [len(x) for x in all_notes] == [4, 3, 4], [len(x) for x in all_notes]
    outputs = [
        ["orders.csv: 250 rows\\n", "daily-load test\\n", "1\\nsales\\n", "True\\n"],
        ["", "", "['Combined', 'FromApi', 'FromFile', 'Origin', 'object']\\n"],
        ["", "1 1\\n", "10 records\\n", "[{'id': 1}]\\n"],
    ]
    with tempfile.TemporaryDirectory(prefix="bc05-archived-") as tmp:
        directory = Path(tmp)
        for chapter, (fences, expected_list) in enumerate(zip(all_notes, outputs, strict=True), 1):
            for i, (code, expected) in enumerate(zip(fences, expected_list, strict=True), 1):
                execute(code, expected, directory, f"archived chapter {chapter} fence {i}")
    print("PASS: 11/11 exact archived Journey-derived OOP Python fence stdout checks")

    for name, sha in MCQ_SHA.items():
        t = pinned_text(ARCHIVE / "assignments" / name, sha)
        assert "**Chosen option:** Pending" in t and "**Review:** Pending" in t, name
        assert "**Platform completion:** Not verified" in t, name
        assert "## Problem to reason about" in t and "## Four choices" in t, name
        last_choices = t.split("## Four choices")[-1].split("## Your independent attempt")[0]
        opts = re.findall(r"^([1-4])\\. ", last_choices, flags=re.M)
        assert opts == ["1", "2", "3", "4"], (name, opts)
    print("PASS: 12/12 distinct original archived MCQ statement/options/status SHA pins, all pending")
    # Historical records Q01-Q08 duplicate their choice headings; Q06 option wording differs.
    # Pin and report without rewriting original archives or pretending there is an official key.


def synthetic_boundaries() -> None:
    class Job:
        mode = "default"
        def __init__(self):
            self.mode = "instance"
    x = Job()
    assert (x.mode, Job.mode) == ("instance", "default")
    print("PASS synthetic 1: class versus instance shadowing")

    class Hidden:
        def __init__(self):
            self.__secret = 7
            self._internal = 3
    obj = Hidden()
    assert not hasattr(obj, "__secret") and hasattr(obj, "_Hidden__secret")
    assert getattr(obj, "_Hidden__secret") == 7 and hasattr(obj, "_internal")
    print("PASS synthetic 2: name mangling is not access security")

    class Shadow:
        def run(self):
            return "method"
    s = Shadow()
    s.run = "attribute"
    assert s.run == "attribute" and Shadow.run(Shadow()) == "method"
    print("PASS synthetic 3: instance property shadows non-data descriptor")

    from abc import ABC, abstractmethod
    class AbstractReader(ABC):
        @abstractmethod
        def read(self):
            pass
    class Unimplemented(AbstractReader):
        pass
    try:
        Unimplemented()
    except TypeError:
        pass
    else:
        raise AssertionError("Unimplemented abstract class should not instantiate")
    print("PASS synthetic 4: ABC implementation obligation")

    log = []
    class Root:
        def go(self):
            log.append("Root")
    class Left(Root):
        def go(self):
            log.append("Left"); super().go()
    class Right(Root):
        def go(self):
            log.append("Right"); super().go()
    class Diamond(Left, Right):
        pass
    Diamond().go()
    assert log == ["Left", "Right", "Root"]
    assert Diamond.__mro__ == (Diamond, Left, Right, Root, object)
    print("PASS synthetic 5: cooperative C3 diamond MRO")

    class Shared:
        ids = []
        def __init__(self, value):
            self.ids.append(value)
    first, second = Shared(1), Shared(2)
    assert first.ids is second.ids is Shared.ids
    assert first.ids == [1, 2]
    print("PASS synthetic 6: shared class mutable state")

    class Base:
        def speak(self):
            return "base"
    class Child(Base):
        def speak(self):
            return "child"
    y = Child()
    assert (y.speak(), super(Child, y).speak()) == ("child", "base")
    print("PASS synthetic 7: explicit super follows post-Child MRO")


if __name__ == "__main__":
    archived_source_contracts()
    synthetic_boundaries()
    print("PASS: OOP Lecture 05 archived-public-notes checks, not private PDF cell parity or Academy grading")
