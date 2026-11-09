"""Read-only executable audit of mentorship archived companions for PDF pp.35-40.

Run all original source-linked Python code blocks verbatim against the corresponding
archived displayed stdout, not retyped examples. Input data and lesson Git blob
hashes are pinned, and all execution takes place in disposable workspaces.
This never certifies independent learner solutions, W3Schools, or original PDF fidelity.
Requires Python >=3.12 (original p.36 demonstrates itertools.batched).
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
SOURCE = MASTER / "3. Advanced Python"
DATASET = MASTER / "python_de_dataset"

# PDF page: (unaltered source Markdown name, Git blob SHA, exact linked code count).
LESSONS = {
    35: ("01. Iterators and generators.md", "3c0917fe25c30c03357d1c6dd54c9f015c376379", 5),
    36: ("02. itertools functools and sorting.md", "902860f8f6782dbba278dc14555c6b2ff55b1d2f", 5),
    37: ("03. Classes and dataclasses.md", "0a8c6988b3f29fa4256bfdcdcf54bb8219fbce98", 3),
    38: ("04. Decorators and context managers.md", "8d79172d50770f0ff3967cb21bc0d92a1aebca74", 4),
    39: ("05. Concurrency threads processes and asyncio.md", "8551301df777eb2770b1b1dc1d968dcadbeb54af", 4),
    40: ("06. Practice set 2 advanced.md", "af41c12d9e67d2d567cb54c07065b6a182d527e5", 5),
}
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
    r"\?part=3&lesson=(\d+)&snippet=(\d+)>\)"
)
PYTHON = re.compile(r"(?ms)^~~~python[ \t]*\n(.*?)^~~~[ \t]*$")
TEXT = re.compile(r"(?ms)^~~~text[ \t]*\n(.*?)^~~~[ \t]*$")


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def check_datasets() -> None:
    for name, expected in DATA_SHAS.items():
        actual = blob_sha((DATASET / name).read_bytes())
        assert actual == expected, f"Changed original source dataset: {name}: {actual}"


def source_snippets(page: int) -> dict[int, tuple[str, str]]:
    filename, expected_sha, expected_count = LESSONS[page]
    data = (SOURCE / filename).read_bytes()
    assert blob_sha(data) == expected_sha, f"Changed preserved lesson p.{page}: {filename}"
    content = data.decode("utf-8-sig")
    links = list(LINK.finditer(content))
    found: dict[int, tuple[str, str]] = {}
    for i, link in enumerate(links):
        lesson, snippet_id = map(int, link.groups())
        assert lesson == page - 34, f"Wrong source link p.{page} #{snippet_id}"
        end = links[i + 1].start() if i + 1 < len(links) else len(content)
        section = content[link.end():end]
        source = PYTHON.search(section)
        expected = TEXT.search(section)
        assert source and expected, f"Missing code/output pair p.{page} #{snippet_id}"
        assert snippet_id not in found, f"Repeated example p.{page} #{snippet_id}"
        found[snippet_id] = (source.group(1).strip("\n"), expected.group(1).strip("\n"))
    assert sorted(found) == list(range(1, expected_count + 1)), (
        f"Source-linked example inventory incomplete p.{page}: {sorted(found)}"
    )
    return found


def normalized(text: str) -> str:
    """Ignore display-only surrounding blanks and line-end spaces, not inner rows."""
    return "\n".join(line.rstrip() for line in text.strip("\n").splitlines())


def run_original(code: str) -> subprocess.CompletedProcess[str]:
    # A real script file (not -c) is essential for spawn-based process workers.
    # All source code is otherwise unmodified and each block runs in isolation.
    check_datasets()
    with tempfile.TemporaryDirectory(prefix="mentor-pages35-40-") as tmp:
        work = Path(tmp)
        shutil.copytree(DATASET, work / "python_de_dataset")
        script = work / "archived_example.py"
        script.write_text(code + "\n", encoding="utf-8")
        process = subprocess.run(
            [sys.executable, "-I", "-B", str(script)],
            cwd=work,
            input="",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=25,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            check=False,
        )
        for name, sha in DATA_SHAS.items():
            assert blob_sha((work / "python_de_dataset" / name).read_bytes()) == sha, (
                f"Example modified a scratch COPY of the source data: {name}"
            )
    check_datasets()
    return process


class MentorshipPages35To40(unittest.TestCase):
    def test_archived_lesson_hashes_and_complete_link_inventory(self) -> None:
        self.assertEqual(list(LESSONS), [35, 36, 37, 38, 39, 40])
        self.assertEqual([v[2] for v in LESSONS.values()], [5, 5, 3, 4, 4, 5])
        self.assertEqual(sum(v[2] for v in LESSONS.values()), 26)
        for page, (_, _, count) in LESSONS.items():
            self.assertEqual(len(source_snippets(page)), count)
        check_datasets()

    def test_all_26_source_examples_against_original_transcripts(self) -> None:
        self.assertGreaterEqual(sys.version_info, (3, 12),
                                "Archived page 36 uses itertools.batched, introduced in Python 3.12")
        checked = 0
        for page in LESSONS:
            for number, (code, expected) in source_snippets(page).items():
                with self.subTest(pdf_page=page, original_source_example=number):
                    result = run_original(code)
                    self.assertEqual(result.returncode, 0, f"p.{page} #{number}: {result.stderr}")
                    self.assertEqual(normalized(result.stdout), normalized(expected),
                                     f"Published stdout mismatch p.{page} example {number}")
                    self.assertEqual(result.stderr, "", f"Unexpected stderr p.{page} #{number}")
                    checked += 1
        self.assertEqual(checked, 26)


if __name__ == "__main__":
    unittest.main(verbosity=2)
