"""Read-only archived mentorship companion audit, PDF-linked pp.75–80.

Runs source-published code directly from the immutable Markdown companion
against scratch copies of source data. Synthetic defects are distinct from
source-printed output contracts. Does not audit original PDF image/text parity,
official answers, Bosscoder grading or independent learner attempts.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
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
LESSON_DIR = MASTER / "7. Practice Prep Flow and Revision"
DATA_DIR = MASTER / "python_de_dataset"
LESSONS = {
    75: ("01. Interview set - Python coding.md", "0fe6a53bdcc34d3e7a8d082759bf67319858a85e", 4, 4, 1),
    76: ("02. Interview set - pandas.md", "4f874710d8e30834aa1d8f78fd4016018c7613b8", 5, 5, 2),
    77: ("03. Concept questions.md", "51a81d3ee396a05c426dd2f8c8e2f65ef9a1ae6f", 1, 3, 3),
    78: ("04. Complexity cheat sheet.md", "d9b4c7c13d4f4b816abeb2579415795d650ea7be", 2, 3, 4),
    79: ("05. Ten-week preparation flow.md", "cc6862cb0cd01e76ad8fee96fdf52793e3b13a9d", 0, 4, 5),
    80: ("06. Final revision sheet.md", "4d6089583b78516ac36d1ec8d8f1667b35f82cee", 3, 3, 6),
}
DATA = {
    "orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
    "events.jsonl": "975c007a68c336007023a9ebd92ba82f02a6b7c3",
}
FENCE = chr(96) * 3
PYTHON_FENCE = re.compile(r"(?ms)^" + FENCE + r"python[ \t]*\n(.*?)^" + FENCE + r"[ \t]*$")
TEXT_FENCE = re.compile(r"(?ms)^" + FENCE + r"text[ \t]*\n(.*?)^" + FENCE + r"[ \t]*$")
LINK = re.compile(r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/\?part=(\d+)&lesson=(\d+)&snippet=(\d+)>\)")


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def verify_originals() -> None:
    for name, sha, _, _, _ in LESSONS.values():
        file = LESSON_DIR / name
        assert git_blob_sha(file.read_bytes()) == sha, f"Original source changed: {file}"
    for name, sha in DATA.items():
        file = DATA_DIR / name
        assert git_blob_sha(file.read_bytes()) == sha, f"Original input changed: {file}"


def source_snippets(page: int) -> dict[int, tuple[str, str]]:
    name, _, count, prompt_count, lesson_id = LESSONS[page]
    raw = (LESSON_DIR / name).read_text(encoding="utf-8-sig")
    sections = raw.split("## Your turn", 1)
    assert len(sections) == 2, f"p.{page} missing practice section"
    practice = sections[1].split("## Continue", 1)[0]
    if page == 76:
        practice = practice.split("## More from", 1)[0]
    prompts = re.findall(r"(?m)^(\d+)\. ", practice)
    assert prompts == [str(i) for i in range(1, prompt_count + 1)], (page, prompts)
    links = list(LINK.finditer(raw))
    assert len(links) == count, f"p.{page}: source linked example count differs"
    examples: dict[int, tuple[str, str]] = {}
    for i, link in enumerate(links, 1):
        assert tuple(map(int, link.groups())) == (7, lesson_id, i), (page, i, link.groups())
        end = links[i].start() if i < len(links) else len(raw)
        region = raw[link.end():end]
        code_matches = list(PYTHON_FENCE.finditer(region))
        text_matches = list(TEXT_FENCE.finditer(region))
        assert len(code_matches) == 1 and len(text_matches) == 1, (page, i)
        code = code_matches[0].group(1).strip("\n")
        expected = text_matches[0].group(1).strip("\n")
        compile(code, f"original-page-{page}-example-{i}", "exec")
        examples[i] = (code, expected)
    return examples


def execute_original(page: int, number: int, replacements: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    verify_originals()
    with tempfile.TemporaryDirectory(prefix="original-p75-80-") as dirname:
        tmp = Path(dirname)
        working_data = tmp / "python_de_dataset"
        working_data.mkdir()
        for name in DATA:
            shutil.copyfile(DATA_DIR / name, working_data / name)
        if replacements:
            for name, body in replacements.items():
                assert name in DATA
                (working_data / name).write_text(body, encoding="utf-8")
        script = tmp / "source_example.py"
        script.write_text(source_snippets(page)[number][0] + "\n", encoding="utf-8")
        result = subprocess.run([sys.executable, "-B", str(script)], cwd=tmp,
                                capture_output=True, text=True, timeout=90, check=False,
                                env={**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONDONTWRITEBYTECODE": "1"})
        for name in DATA:
            if not replacements or name not in replacements:
                assert git_blob_sha((working_data / name).read_bytes()) == DATA[name], name
    verify_originals()
    return result


class SourceInventory(unittest.TestCase):
    def test_all_six_sources_practice_prompts_and_code_blocks(self):
        verify_originals()
        self.assertEqual({page: len(source_snippets(page)) for page in LESSONS},
                         {75: 4, 76: 5, 77: 1, 78: 2, 79: 0, 80: 3})
        self.assertEqual(sum(row[2] for row in LESSONS.values()), 15)
        self.assertEqual(sum(row[3] for row in LESSONS.values()), 22)

    def test_source_p77_34_oral_concept_questions(self):
        raw = (LESSON_DIR / LESSONS[77][0]).read_text(encoding="utf-8-sig")
        # 17 value/function, 13 data/pipeline, 4 complexity rows.
        blocks = [raw.split("## Python values and functions", 1)[1].split("## Files, data", 1)[0],
                  raw.split("## Files, data, databases, and pipelines", 1)[1].split("## Algorithms", 1)[0],
                  raw.split("## Algorithms and complexity", 1)[1].split("## Your turn", 1)[0]]
        counts = [len(re.findall(r"(?m)^\| [^|]+\? \|", block)) for block in blocks]
        self.assertEqual(counts, [17, 13, 4])

    def test_synthetic_p75_equal_timestamp_keeps_first_input_event(self):
        events = "\n".join([
            json.dumps({"user_id": 99, "ts": "2025-04-01T10:00:00", "event": "view", "props": {"device": "desktop"}}),
            json.dumps({"user_id": 99, "ts": "2025-04-01T10:00:00", "event": "cart", "props": {"device": "mobile"}}),
        ]) + "\n"
        result = execute_original(75, 1, {"events.jsonl": events})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "99 view desktop 10:00")
        # Original Q39 'Your turn' explicitly requests a lexicographic tie rule;
        # the published worked example does NOT implement it.

    def test_synthetic_p75_two_sum_duplicates_and_no_self_pair(self):
        csv_body = "order_id,customer_id,order_date,status,amount\n"
        csv_body += "1,1,2025-04-01,delivered,1000.00\n"
        csv_body += "2,2,2025-04-02,delivered,1847.00\n"
        csv_body += "3,2,2025-04-03,delivered,1847.00\n"
        result = execute_original(75, 3, {"orders.csv": csv_body})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "[('1', '2'), ('1', '3')]")

    def test_synthetic_p75_nested_key_collision(self):
        code = source_snippets(75)[4][0]
        local = {"__name__": "auditor"}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(code, "preserved-source-p75-q42", "exec"), local)
        with self.assertRaises(AttributeError):
            local["unflatten"]({"address": "Pune", "address.city": "Mumbai"})
        # Reversing the order silently loses the previous nested dictionary.
        self.assertEqual(local["unflatten"]({"address.city": "Mumbai", "address": "Pune"}),
                         {"address": "Pune"})

    def test_synthetic_p76_zero_prior_month_growth(self):
        csv_body = "order_id,customer_id,order_date,status,amount\n"
        csv_body += "1,1,2025-01-05,delivered,0.00\n"
        csv_body += "2,1,2025-02-05,delivered,50.00\n"
        result = execute_original(76, 2, {"orders.csv": csv_body})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2025-01 0.00 N/A", result.stdout)
        self.assertIn("2025-02 50.00 inf%", result.stdout)
        # Source explicitly says a business rule is needed for a zero denominator.


def create_stdout_case(page: int, number: int):
    def case(self):
        code, expected = source_snippets(page)[number]
        self.assertTrue(code and expected)
        result = execute_original(page, number)
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertFalse(result.stderr, result.stderr)
        self.assertEqual(result.stdout.strip(), expected)
    return case


for _page, (_, _, _count, _, _) in LESSONS.items():
    for _number in range(1, _count + 1):
        setattr(SourceInventory, f"test_original_p{_page}_snippet_{_number:02d}_exact_stdout",
                create_stdout_case(_page, _number))


if __name__ == "__main__":
    unittest.main(verbosity=2)
