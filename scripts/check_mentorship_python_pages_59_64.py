"""Independent, read-only Python mentorship companion checks, PDF pages 59-64.

10 verbatim fenced stdout transcripts, 3 explicitly prose-described output contracts,
and 6 separate auditor-synthetic boundary groups. Source-printed answers != learner work.
PDF visual fidelity and the official assessment platform are NOT verified here.
"""
from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
PATTERNS = MASTER / "5. Coding Round Patterns"
DATA = MASTER / "python_de_dataset"

# Page: (original file, original Git blob hash, linked example count, lesson ID)
LESSONS = {
    59: ("02. Frequency count and top K.md", "350a7dfeb5dce40d04d96d96257e8585e960f10d", 2, 2),
    60: ("03. Grouping and latest-record deduplication.md", "8d47fce0c80d73b56ad31a6a651e63d0f00bec6c", 2, 3),
    61: ("04. Windows and sorted streams.md", "cc8c1f039305179c4b42188309107b1fd902e41b", 2, 4),
    62: ("05. Flatten nested JSON.md", "424cb41f568a9833a17173e42bd3957a0689033c", 3, 5),
    63: ("06. Sessions and streaks.md", "2594187cfb8cf0290dff99345cfe842618a09f59", 2, 6),
    64: ("07. Parse logs.md", "a766d7427e0cafee1ea227ace0418ec692a25fa4", 2, 7),
}
DATA_SHA = {
    "orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
    "order_items.csv": "072bd904c499ce5547049eb8ba0fc2dd4c071cd0",
    "events.jsonl": "975c007a68c336007023a9ebd92ba82f02a6b7c3",
    "customers.json": "d6125fce237e7f7e3193667946d1eb117cd19db0",
    "logins.csv": "e5669aa40eb3a08569355351eaa1c4f6e35a556d",
    "app.log": "d75778a27a947725c57b84134ec32297f45bb9df",
}
# These three have prose-only "Expected" descriptions, not exact transcript fences.
PROSE_ONLY = {(62, 1), (62, 3), (64, 1)}
LINK = re.compile(
    r"\[▶ Run and edit this example\]\(<http://127\.0\.0\.1:8765/"
    r"\?part=(\d+)&lesson=(\d+)&snippet=(\d+)>\)"
)
FENCE = re.compile(r"(?ms)^(\x60{3}|\~{3})(python|text)[ \t]*\n(.*?)^\1[ \t]*$")


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def preserved_datasets() -> None:
    for name, expected in DATA_SHA.items():
        actual = blob_sha((DATA / name).read_bytes())
        assert actual == expected, f"Archived dataset changed: {name}: {actual}"


def source_examples(page: int) -> dict[int, tuple[str, str | None]]:
    name, original_sha, count, lesson = LESSONS[page]
    raw = (PATTERNS / name).read_bytes()
    assert blob_sha(raw) == original_sha, f"Archived source p.{page} changed"
    body = raw.decode("utf-8-sig")
    links = list(LINK.finditer(body))
    assert len(links) == count, f"p.{page} link count changed"
    examples = {}
    for i, link in enumerate(links):
        part, lesson_id, snippet = map(int, link.groups())
        assert (part, lesson_id, snippet) == (5, lesson, i + 1), (
            f"Wrong original source link p.{page} #{i+1}: {link.groups()}"
        )
        end = links[i + 1].start() if i + 1 < len(links) else len(body)
        region = body[link.end():end]
        fences = [(m.group(2), m.group(3).strip("\n")) for m in FENCE.finditer(region)]
        assert fences and fences[0][0] == "python", f"No original source code p.{page} #{snippet}"
        stdout = None
        if (page, snippet) not in PROSE_ONLY:
            assert len(fences) >= 2 and fences[1][0] == "text", (
                f"No original printed stdout contract p.{page} #{snippet}"
            )
            stdout = fences[1][1]
        else:
            assert not any(kind == "text" for kind, _ in fences[1:]), (
                f"Prose-only contract unexpectedly changed p.{page} #{snippet}"
            )
        examples[snippet] = (fences[0][1], stdout)
    assert list(examples) == list(range(1, count + 1))
    return examples


def prepare_scratch(path: Path, override: dict[str, bytes] | None = None) -> None:
    target = path / "python_de_dataset"
    target.mkdir()
    for name in DATA_SHA:
        shutil.copyfile(DATA / name, target / name)
    for name, value in (override or {}).items():
        assert name in DATA_SHA, "Synthetic override must target known scratch-only dataset"
        (target / name).write_bytes(value)


def run_original(code: str, override: dict[str, bytes] | None = None) -> subprocess.CompletedProcess[str]:
    preserved_datasets()
    with tempfile.TemporaryDirectory(prefix="mentor-59-64-") as folder:
        work = Path(folder)
        prepare_scratch(work, override)
        (work / "source.py").write_text(code + "\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(work / "source.py")],
            cwd=work, input="", capture_output=True, text=True,
            timeout=25, check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        for name, sha in DATA_SHA.items():
            path = work / "python_de_dataset" / name
            if override and name in override:
                assert path.read_bytes() == override[name], f"Scratch override modified: {name}"
            else:
                assert blob_sha(path.read_bytes()) == sha, f"Scratch input modified: {name}"
    preserved_datasets()
    return result


def normalize(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.strip("\n").splitlines())


def source_scope(page: int, snippet: int) -> dict:
    """Execute original example definitions unchanged against copies, then inspect globals."""
    code, _ = source_examples(page)[snippet]
    preserved_datasets()
    with tempfile.TemporaryDirectory(prefix="mentor-59-64-synthetic-") as folder:
        work = Path(folder)
        prepare_scratch(work)
        module_name = f"auditor_source_page_{page}_example_{snippet}"
        module = types.ModuleType(module_name)
        sys.modules[module_name] = module
        before = Path.cwd()
        try:
            os.chdir(work)
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(code, f"archived-page-{page}-snippet-{snippet}", "exec"), module.__dict__)
        finally:
            os.chdir(before)
    preserved_datasets()
    return module.__dict__


class MentorshipPages59To64(unittest.TestCase):
    def test_source_hash_link_inventory_and_data_preservation(self):
        self.assertEqual(list(LESSONS), list(range(59, 65)))
        self.assertEqual([v[2] for v in LESSONS.values()], [2, 2, 2, 3, 2, 2])
        self.assertEqual(sum(v[2] for v in LESSONS.values()), 13)
        preserved_datasets()
        for page in LESSONS:
            with self.subTest(page=page):
                self.assertEqual(len(source_examples(page)), LESSONS[page][2])

    def test_all_10_exact_source_published_transcripts(self):
        count = 0
        for page in LESSONS:
            for number, (code, expected) in source_examples(page).items():
                if expected is None:
                    continue
                with self.subTest(page=page, source_snippet=number):
                    completed = run_original(code)
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    self.assertEqual(completed.stderr, "")
                    self.assertEqual(normalize(completed.stdout), normalize(expected))
                    count += 1
        self.assertEqual(count, 10)

    def test_all_3_prose_described_source_outputs(self):
        self.assertEqual({(p, n) for p in LESSONS for n, (_, text) in source_examples(p).items()
                          if text is None}, PROSE_ONLY)
        for page, number in sorted(PROSE_ONLY):
            with self.subTest(page=page, source_snippet=number):
                code, _ = source_examples(page)[number]
                completed = run_original(code)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stderr, "")
                lines = completed.stdout.strip().splitlines()
                if (page, number) == (62, 1):
                    self.assertEqual(len(lines), 2)
                    diya, sana = map(ast.literal_eval, lines)
                    self.assertEqual(diya["address.city"], "Mumbai")
                    self.assertEqual(diya["tags.0"], "referral")
                    self.assertIsNone(sana["address.city"])
                    self.assertEqual(sana["tags"], [])
                elif (page, number) == (62, 3):
                    self.assertEqual(ast.literal_eval(lines[0]),
                                     ["user_id", "ts", "event", "props.page", "props.device"])
                    self.assertEqual(len(lines), 5)
                    self.assertEqual([row.split()[2] for row in lines[2:]], ["view", "cart", "checkout"])
                    self.assertEqual([row.split()[3] for row in lines[2:]],
                                     ["/p/4", "/cart", "/checkout"])
                elif (page, number) == (64, 1):
                    self.assertEqual(lines[0],
                                     "13 parsed; skipped: [(7, '--- scheduler restarted ---')]")
                    row = ast.literal_eval(lines[1])
                    self.assertEqual((row["job"], row["level"], row["step"], row["rows"], row["ms"]),
                                     ("customers_dim", "ERROR", "load", None, "5003"))

    # Synthetic tests below deliberately use NON-original, auditor-created inputs.
    def test_synthetic_p59_frequency_and_heap_tie_break(self):
        source1, _ = source_examples(59)[1]
        orders = (b"order_id,customer_id,order_date,status,amount\n"
                  b"1,1,2025-01-01,delivered,10\n"
                  b"2,1,2025-01-02,delivered,10\n"
                  b"3,2,2025-01-03,returned,2\n")
        events = (b'{"props":{"page":"/a"}}\n{"props":{"page":"/a"}}\n'
                  b'{"props":{"page":"/b"}}\n')
        result = run_original(source1, {"orders.csv": orders, "events.jsonl": events})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[('delivered', 2)] 2", result.stdout)
        self.assertIn("[('/a', 2), ('/b', 1)]", result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith("True"))
        source2, _ = source_examples(59)[2]
        tied = (b"order_id,customer_id,order_date,status,amount\n"
                b"1,3,2025-01-01,delivered,10\n"
                b"2,1,2025-01-01,delivered,10\n"
                b"3,2,2025-01-01,delivered,10\n"
                b"4,4,2025-01-01,delivered,5\n")
        result = run_original(source2, {"orders.csv": tied})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([ast.literal_eval(s) for s in result.stdout.splitlines()],
                         [[("1", 10.0), ("2", 10.0), ("3", 10.0)]] * 2)

    def test_synthetic_p60_missing_basket_and_equal_timestamp(self):
        source, _ = source_examples(60)[1]
        headers = (b"order_id,customer_id,order_date,status,amount\n"
                   b"101,1,2025-01-01,delivered,10\n"
                   b"102,1,2025-01-01,delivered,15\n")
        items = (b"order_id,product_id,qty,unit_price\n101,1,1,9\n999,2,1,6\n")
        result = run_original(source, {"orders.csv": headers, "order_items.csv": items})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 orders checked, mismatches: ['101', '102']", result.stdout)
        # The source excludes orphan 999 from the mismatch list: a documented gap.
        scope = source_scope(60, 2)
        self.assertEqual(scope["latest"][103]["status"], "delivered")
        code, _ = source_examples(60)[2]
        loop = code[code.index("latest = {}"):]
        scope = {"feed": [
            {"order_id": 4, "status": "first", "ts": "2025-01-01 00:00"},
            {"order_id": 4, "status": "second", "ts": "2025-01-01 00:00"},
            {"order_id": 4, "status": "older", "ts": "2024-12-31 23:59"},
        ]}
        with contextlib.redirect_stdout(io.StringIO()):
            exec(loop, scope)
        self.assertEqual(scope["latest"][4]["status"], "first")

    def test_synthetic_p61_sparse_days_and_sorted_merge(self):
        source, _ = source_examples(61)[1]
        # Preserved source's rolling logic, with synthetic missing calendar days.
        rolling = source[source.index("window = deque()"):]
        scope = {"deque": __import__("collections").deque,
                 "daily": [("04-01", 1), ("04-20", 2), ("04-21", 3), ("04-22", 4)]}
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(rolling, scope)
        self.assertIn("04-21 3-day: 6", buf.getvalue())  # Three ROWS, not three DAYS.
        self.assertIn("04-22 3-day: 9", buf.getvalue())
        merge = source_scope(61, 2)["merge_two"]
        self.assertEqual(merge([1, 1], [1, 2]), [1, 1, 1, 2])
        self.assertEqual(merge([], [1, 2]), [1, 2])

    def test_synthetic_p62_flatten_empty_dict_collision_and_explode(self):
        flatten = source_scope(62, 1)["flatten"]
        self.assertEqual(flatten({"address": {}}), {"address": {}})
        self.assertEqual(flatten({"a": {"b": 1}, "a.b": 2})["a.b"], 2)
        explode = source_scope(62, 2)["explode"]
        rows = list(explode({"order_id": 1, "customer": {"id": 7}, "items": []}, "items"))
        self.assertEqual(rows, [{"order_id": 1, "customer.id": 7}])

    def test_synthetic_p63_exact_idle_boundary_and_earlier_tie(self):
        source, _ = source_examples(63)[1]
        events = (b'{"user_id":9,"ts":"2025-04-01T10:31:00","event":"later"}\n'
                  b'{"user_id":9,"ts":"2025-04-01T10:00:00","event":"first"}\n'
                  b'{"user_id":9,"ts":"2025-04-01T10:30:00","event":"boundary"}\n'
                  b'{"user_id":9,"ts":"2025-04-01T11:02:00","event":"new"}\n')
        result = run_original(source, {"events.jsonl": events})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(),
                         "9 [['first', 'boundary', 'later'], ['new']]")
        source, _ = source_examples(63)[2]
        logins = (b"user_id,login_date\n9,2025-04-01\n9,2025-04-02\n"
                  b"9,2025-04-05\n9,2025-04-06\n9,2025-04-06\n")
        result = run_original(source, {"logins.csv": logins})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "9 longest: 2 days from 2025-04-01")

    def test_synthetic_p64_reject_trailing_garbage_and_report_errors(self):
        namespace = source_scope(64, 1)
        regex = namespace["line_pattern"]
        valid = ("2025-04-01 02:05:02 ERROR job=customers_dim "
                 "step=load duration_ms=5003")
        self.assertIsNotNone(regex.fullmatch(valid))
        self.assertIsNone(regex.fullmatch(valid + " garbage"))
        self.assertIsNotNone(regex.match(valid + " garbage"))
        self.assertIsNotNone(regex.fullmatch(valid.replace("04-01", "99-99")))
        code, _ = source_examples(64)[2]
        synthetic = (valid + '\n' + valid.replace("5003", "6000")
                     + '\n--- junk ---\n').encode()
        result = run_original(code, {"app.log": synthetic})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("customers_dim 2 2 ('load', 6000)", result.stdout)
        self.assertIn("[(None, 2)]", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
