"""Auditor-only execution of original PNP Python mentorship companion code, PDF pp.21–24.

Read every lesson's original run/edit-linked Python snippet, run it unchanged in
isolated scratch directories (with explicitly linked setup blocks where needed),
and compare the archived output/data. This does not check every PDF image or
constitute any independent learner exercise, official graded pass, or mastery.
The 744-file archive and learner progress are never written.
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
MASTER = (ROOT / "99. Reference Materials" / "Original Mastery Snapshot"
          / "2. Python Mastry")
SOURCE = MASTER / "1. Python from Zero"
DATA = MASTER / "python_de_dataset"
LESSONS = {
    21: ("17. Reading errors.md", "9159ef47b425806d4622584284b1a145543f5222", 5),
    22: ("18. Files - read and write.md", "d47356de0ec044cc16cd61377535266af3a3c50f", 7),
    23: ("19. Mini project - monthly sales report.md", "30992048e800aa0aaf8e8940546993d5b48be366", 5),
    24: ("20. Practice set 0 - first steps.md", "5c5ee4773abcf2b797bd08d46a6a6421388b0962", 5),
}
DATA_SHAS = {
    "orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
    "customers.json": "d6125fce237e7f7e3193667946d1eb117cd19db0",
    "events.jsonl": None,  # existence/extension only; not read by the lesson
}
LINK = re.compile(
    r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/"
    r"\?lesson=(\d+)&snippet=(\d+)>\)"
)
FENCE = r"(?:~~~|" + re.escape(chr(96)*3) + r")"
PYTHON = re.compile(r"(?ms)^" + FENCE + r"python[ \t]*\n(.*?)^\s*" + FENCE + r"\s*$")
TEXT = re.compile(r"(?ms)^" + FENCE + r"text[ \t]*\n(.*?)^\s*" + FENCE + r"\s*$")
NO_DISPLAY = {(22, 1), (22, 6), (23, 1), (23, 2), (23, 3)}
EXPECTED_ERROR = {(21, 1): "ZeroDivisionError: division by zero"}
# These examples explicitly depend on earlier source snippets. Never rewrite
# source code to silently make an isolated example work.
CONTEXT = {
    (22, 2): [(22, 1)],
    (22, 4): [(22, 1)],
    (22, 6): [(22, 1)],
    (23, 4): [(23, 1), (23, 2), (23, 3)],
    (23, 5): [(23, 2)],
}
FILES_CREATED = {
    (22, 1): {"sample_orders.csv": (
        "order_id,customer_id,order_date,status,amount\n"
        "101,1,2025-01-10,delivered,1198.00\n"
        "102,2,2025-01-11,cancelled,1999.00\n"
        "103,1,2025-01-12,delivered,796.00\n"
    )},
    (22, 5): {"scratch_report.txt": (
        "date,revenue\n2025-04-20,2397\n2025-04-28,1598\n"
    )},
    (22, 6): {"reports/2025-04/summary.txt": "orders,15\n"},
}

def git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()


def get_snippets(page: int) -> dict[int, tuple[str, str | None]]:
    filename, expected_sha, count = LESSONS[page]
    source = SOURCE / filename
    raw = source.read_bytes()
    actual_sha = git_blob_sha(raw)
    if actual_sha != expected_sha:
        raise AssertionError(f"original source SHA changed for {filename}: {actual_sha}")
    body = raw.decode("utf-8-sig")
    links = list(LINK.finditer(body))
    found: dict[int, tuple[str, str | None]] = {}
    for i, match in enumerate(links):
        lesson, number = map(int, match.groups())
        if lesson != page - 4:
            raise AssertionError(f"{filename} snippet {number}: wrong source lesson {lesson}")
        span = body[match.end():links[i + 1].start() if i+1 < len(links) else len(body)]
        py = PYTHON.search(span)
        shown = TEXT.search(span)
        if number in found or not py:
            raise AssertionError(f"{filename} snippet {number}: duplicate/missing code")
        if (page, number) in NO_DISPLAY and shown is not None:
            raise AssertionError(f"{filename} snippet {number}: unexpected printed transcript")
        if (page, number) not in NO_DISPLAY and shown is None:
            raise AssertionError(f"{filename} snippet {number}: missing printed transcript")
        found[number] = (py.group(1).strip("\n"),
                         shown.group(1).strip("\n") if shown else None)
    if set(found) != set(range(1, count + 1)):
        raise AssertionError(f"{filename}: snippets {sorted(found)} != expected 1..{count}")
    return found


def compact(output: str) -> str:
    # Only remove display-only trailing whitespace and boundary newlines.
    return "\n".join(line.rstrip() for line in output.strip("\n").splitlines())


def execute_source(code: str) -> tuple[subprocess.CompletedProcess[str], dict[str, str]]:
    # Use original dataset bytes as read-only INPUTS copied to scratch. All
    # scratch report writes remain outside repository/source archive.
    with tempfile.TemporaryDirectory(prefix="mentorship-pages21to24-") as td:
        cwd = Path(td)
        dataset = cwd / "python_de_dataset"
        dataset.mkdir()
        for name, expected_sha in DATA_SHAS.items():
            path = DATA / name
            if not path.is_file():
                raise AssertionError(f"required original dataset missing: {path}")
            if expected_sha is not None and git_blob_sha(path.read_bytes()) != expected_sha:
                raise AssertionError(f"original dataset blob changed: {name}")
            shutil.copyfile(path, dataset / name)
        run = subprocess.run(
            [sys.executable, "-I", "-B", "-c", code],
            cwd=cwd, input="", capture_output=True, text=True, timeout=12,
            check=False, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        generated = {}
        for name in ("sample_orders.csv", "scratch_report.txt",
                     "reports/2025-04/summary.txt"):
            path = cwd / name
            if path.exists():
                generated[name] = path.read_text(encoding="utf-8")
        # Make sure the input orders and customers remained unmodified.
        for name, expected_sha in DATA_SHAS.items():
            if expected_sha is not None:
                assert git_blob_sha((dataset / name).read_bytes()) == expected_sha, name
        return run, generated


class MentorshipPages21To24(unittest.TestCase):
    def test_all_22_original_linked_snippets(self) -> None:
        by_page = {page: get_snippets(page) for page in LESSONS}
        checked = 0
        for page, snippets in by_page.items():
            for number, (code, shown) in snippets.items():
                key = page, number
                with self.subTest(pdf_page=page, source_snippet=number):
                    context = [by_page[p][n][0] for p, n in CONTEXT.get(key, [])]
                    run, generated = execute_source("\n\n".join(context + [code]))
                    if key in EXPECTED_ERROR:
                        self.assertNotEqual(run.returncode, 0)
                        self.assertIn(EXPECTED_ERROR[key], run.stderr)
                        self.assertEqual(compact(shown or ""), EXPECTED_ERROR[key])
                    else:
                        self.assertEqual(run.returncode, 0, f"{key}: {run.stderr}")
                        if key == (22, 6):
                            self.assertEqual(
                                compact(run.stdout),
                                "True False\n['customers.json', 'events.jsonl']"
                                "\n['reports/2025-04/summary.txt']"
                            )
                        elif shown is None:
                            self.assertEqual(run.stdout, "", f"{key}: undeclared output")
                        else:
                            self.assertEqual(compact(run.stdout), compact(shown))
                    if key in FILES_CREATED:
                        for path, expected in FILES_CREATED[key].items():
                            self.assertEqual(generated.get(path), expected, f"{key}: {path}")
                    checked += 1
        self.assertEqual(checked, 22)

    def test_source_and_fixture_inventory(self) -> None:
        self.assertEqual(sum(x[2] for x in LESSONS.values()), 22)
        self.assertEqual(set(CONTEXT), {(22, 2), (22, 4), (22, 6), (23, 4), (23, 5)})
        self.assertEqual(set(EXPECTED_ERROR), {(21, 1)})
        self.assertEqual(len(NO_DISPLAY), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
