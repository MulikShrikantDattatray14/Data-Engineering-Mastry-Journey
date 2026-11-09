"""Source-linked runtime audit, archived Python mentorship companion, PDF pp.25-30.

Inspects every Run/edit Python snippet in the six archived Part-2 lessons,
checks published stdout from unchanged source code and preserves source blobs.
This is auditor source-example verification only, NOT original PDF imagery
verification, official grading, or independent learner coursework.
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
DATA = MASTER / "python_de_dataset" / "orders.csv"
DATA_SHA = "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2"

# PDF page -> (immutable companion source filename, source Git blob SHA, links).
LESSONS = {
    25: ("01. The 6-step approach to any coding question.md",
         "2a176fd611ed9ec50dc8873927b56c349be0651a", 3),
    26: ("02. Names objects and mutability.md",
         "0e8557654df4677b9bd58c05921b7338cd336203", 4),
    27: ("03. Numbers strings and dates.md",
         "91de7da6ba563322381b46dce78a2ebcb2ce7e61", 4),
    28: ("04. Lists tuples sets and Big-O.md",
         "15e912de271e31108a3fabf7e0abab63ff522f3d", 3),
    29: ("05. Dicts defaultdict and Counter.md",
         "7d372ee509f2e539c8cfa0c8bdcc87a50909edce", 5),
    30: ("06. Loops comprehensions and unpacking.md",
         "587219b8e48cdd899b757319e54ae94774780969", 4),
}
LINK = re.compile(
    r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/"
    r"\?part=2&lesson=(\d+)&snippet=(\d+)>\)"
)
PYTHON = re.compile(r"(?ms)^~~~python[ \t]*\n(.*?)^~~~[ \t]*$")
TEXT = re.compile(r"(?ms)^~~~text[ \t]*\n(.*?)^~~~[ \t]*$")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def snippets_for_page(page: int) -> dict[int, tuple[str, str]]:
    filename, sha, count = LESSONS[page]
    raw = (SOURCE / filename).read_bytes()
    assert git_blob_sha(raw) == sha, f"Archived source changed: {filename}"
    body = raw.decode("utf-8-sig")
    matches = list(LINK.finditer(body))
    found = {}
    for i, match in enumerate(matches):
        lesson, number = map(int, match.groups())
        assert lesson == page - 24, f"Unexpected lesson ID in {filename}: {lesson}"
        segment = body[match.end():matches[i + 1].start() if i + 1 < len(matches) else len(body)]
        code = PYTHON.search(segment)
        output = TEXT.search(segment)
        assert code is not None and output is not None, (
            f"Missing archived source or output for PDF p.{page} example {number}"
        )
        assert number not in found, f"Duplicate snippet p.{page} #{number}"
        found[number] = (code.group(1).strip("\n"), output.group(1).strip("\n"))
    assert sorted(found) == list(range(1, count + 1)), (
        f"Wrong numbered inventory for p.{page}: {sorted(found)}"
    )
    return found


def normalize(text: str) -> str:
    # Discard display-only outer blank lines and trailing whitespace, but
    # preserve all interior lines, values and ordering.
    return "\n".join(line.rstrip() for line in text.strip("\n").splitlines())


def run_exact_source(code: str) -> subprocess.CompletedProcess[str]:
    assert git_blob_sha(DATA.read_bytes()) == DATA_SHA, "Archived orders.csv changed"
    with tempfile.TemporaryDirectory(prefix="audit-mentor-pages25to30-") as scratch:
        work = Path(scratch)
        (work / "python_de_dataset").mkdir()
        shutil.copyfile(DATA, work / "python_de_dataset" / "orders.csv")
        process = subprocess.run(
            [sys.executable, "-I", "-B", "-c", code],
            cwd=work,
            input="",
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=12,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        assert git_blob_sha((work / "python_de_dataset" / "orders.csv").read_bytes()) == DATA_SHA
    assert git_blob_sha(DATA.read_bytes()) == DATA_SHA
    return process


class AuditMentorshipPages25To30(unittest.TestCase):
    def test_all_23_original_source_links_and_published_outputs(self) -> None:
        verified = 0
        for page in LESSONS:
            snippets = snippets_for_page(page)
            for number, (code, shown) in snippets.items():
                with self.subTest(pdf_page=page, snippet=number):
                    process = run_exact_source(code)
                    self.assertEqual(process.returncode, 0,
                                     f"p.{page} #{number}: {process.stderr}")
                    self.assertEqual(normalize(process.stdout), normalize(shown),
                                     f"Source output mismatch p.{page} #{number}")
                    verified += 1
        self.assertEqual(verified, 23)

    def test_source_inventory_and_data_blob(self) -> None:
        self.assertEqual(list(LESSONS), [25, 26, 27, 28, 29, 30])
        self.assertEqual(sum(row[2] for row in LESSONS.values()), 23)
        self.assertEqual(git_blob_sha(DATA.read_bytes()), DATA_SHA)


if __name__ == "__main__":
    unittest.main(verbosity=2)
