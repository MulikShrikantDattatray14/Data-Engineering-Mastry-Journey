"""Read-only source-linked audit: mentorship PDF companion pages 31–34.

Runs all 19 original linked Python code blocks verbatim against their published
stdout in isolated temporary workspaces. Verifies archived Git blob hashes.
This is NOT PDF-image review, independently solved exercises, or platform grading.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
SOURCE = MASTER / "2. Python Foundations"
DATASET = MASTER / "python_de_dataset"

# PDF page: (original archived source name, Git blob SHA, expected snippet count)
LESSONS = {
    31: ("07. Functions scope and closures.md",
         "add60d3123e71a8d576f3ce1569f1134a2ece821", 5),
    32: ("08. Errors exceptions and context managers.md",
         "2d4098805caeb60deeffb829aac6e03a8a9f7c88", 4),
    33: ("09. Files CSV JSON JSON Lines and paths.md",
         "54e71278f26aa0d2847363e4860cbac98b1caaa7", 4),
    34: ("10. Practice set 1 foundations.md",
         "42e04f6ccf04bc41f7fa1f2ffa0ff3f9122b60e8", 6),
}
# Snapshot dataset, NOT fabricated fixture data.
DATA_SHAS = {
    "orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
    "customers.json": "d6125fce237e7f7e3193667946d1eb117cd19db0",
    "events.jsonl": "975c007a68c336007023a9ebd92ba82f02a6b7c3",
    "employees.csv": "08d2330cc9dab1530d6ff8e896211f7867438e4b",
    "logins.csv": "e5669aa40eb3a08569355351eaa1c4f6e35a556d",
    "order_items.csv": "072bd904c499ce5547049eb8ba0fc2dd4c071cd0",
}
LINK = re.compile(
    r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/"
    r"\?part=2&lesson=(\d+)&snippet=(\d+)>\)"
)
PYTHON = re.compile(r"(?ms)^~~~python[ \t]*\n(.*?)^~~~[ \t]*$")
TEXT = re.compile(r"(?ms)^~~~text[ \t]*\n(.*?)^~~~[ \t]*$")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    ).hexdigest()


def assert_dataset_preserved() -> None:
    for file, sha in DATA_SHAS.items():
        actual = git_blob_sha((DATASET / file).read_bytes())
        assert actual == sha, f"Archived dataset mismatch: {file}: {actual}"


def source_snippets(page: int) -> dict[int, tuple[str, str]]:
    filename, sha, count = LESSONS[page]
    original = (SOURCE / filename).read_bytes()
    assert git_blob_sha(original) == sha, f"Archived lesson changed: {filename}"
    body = original.decode("utf-8-sig")
    links = list(LINK.finditer(body))
    snippets = {}
    for i, link in enumerate(links):
        lesson, number = map(int, link.groups())
        assert lesson == page - 24, f"Unexpected lesson number p.{page} #{number}"
        end = links[i + 1].start() if i + 1 < len(links) else len(body)
        segment = body[link.end():end]
        source = PYTHON.search(segment)
        expected = TEXT.search(segment)
        assert source and expected, f"Missing source or expected transcript p.{page} #{number}"
        assert number not in snippets, f"Duplicated source link p.{page} #{number}"
        snippets[number] = (source.group(1).strip("\n"), expected.group(1).strip("\n"))
    assert sorted(snippets) == list(range(1, count + 1)), (
        f"Broken source-linked inventory on p.{page}: {sorted(snippets)}"
    )
    return snippets


def normalize_display(text: str) -> str:
    """Ignore display-only outer blank lines and line-end space, not content."""
    return "\n".join(line.rstrip() for line in text.strip("\n").splitlines())


def run_archived_code(code: str) -> subprocess.CompletedProcess[str]:
    assert_dataset_preserved()
    with tempfile.TemporaryDirectory(prefix="mentor-pages31-34-") as tmp:
        workspace = Path(tmp)
        shutil.copytree(DATASET, workspace / "python_de_dataset")
        run = subprocess.run(
            [sys.executable, "-I", "-B", "-c", code],
            cwd=workspace,
            input="",
            capture_output=True,
            encoding="utf-8",
            text=True,
            timeout=12,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        )
        for name, sha in DATA_SHAS.items():
            assert git_blob_sha((workspace / "python_de_dataset" / name).read_bytes()) == sha, (
                f"Example modified scratch input copy: {name}"
            )
    assert_dataset_preserved()
    return run


class MentorshipArchivedPages31To34(unittest.TestCase):
    def test_every_archived_source_example_vs_published_transcript(self) -> None:
        checked = 0
        for page in LESSONS:
            for number, (code, expected) in source_snippets(page).items():
                with self.subTest(page=page, original_snippet=number):
                    proc = run_archived_code(code)
                    self.assertEqual(proc.returncode, 0, proc.stderr)
                    self.assertEqual(
                        normalize_display(proc.stdout),
                        normalize_display(expected),
                        f"Published stdout differs at p.{page}, example {number}",
                    )
                    checked += 1
        self.assertEqual(checked, 19)

    def test_archived_4_source_and_6_dataset_hashes(self) -> None:
        self.assertEqual([x[2] for x in LESSONS.values()], [5, 4, 4, 6])
        for page in LESSONS:
            self.assertEqual(len(source_snippets(page)), LESSONS[page][2])
        assert_dataset_preserved()


if __name__ == "__main__":
    unittest.main(verbosity=2)
