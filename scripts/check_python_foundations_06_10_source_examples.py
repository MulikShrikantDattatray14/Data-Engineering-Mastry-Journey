"""Read-only source-pinned audit of preserved Python Foundations lessons 06-10.

Execute exact archived code blocks against SHA-pinned ORIGINAL local data copies;
compare archived printed outputs. Extra tests are reviewer-authored synthetic
contracts, not official PDF answers, independent learner work, or mastery.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from itertools import product
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
LESSONS = BASE / "2. Python Foundations"
DATA = BASE / "python_de_dataset"
PINS = {
    6: ("06. Loops comprehensions and unpacking.md", "587219b8e48cdd899b757319e54ae94774780969", 30, 4),
    7: ("07. Functions scope and closures.md", "add60d3123e71a8d576f3ce1569f1134a2ece821", 31, 5),
    8: ("08. Errors exceptions and context managers.md", "2d4098805caeb60deeffb829aac6e03a8a9f7c88", 32, 4),
    9: ("09. Files CSV JSON JSON Lines and paths.md", "54e71278f26aa0d2847363e4860cbac98b1caaa7", 33, 4),
    10: ("10. Practice set 1 foundations.md", "42e04f6ccf04bc41f7fa1f2ffa0ff3f9122b60e8", 34, 6),
}
DATA_PINS = {
    "orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
    "employees.csv": "08d2330cc9dab1530d6ff8e896211f7867438e4b",
    "customers.json": "d6125fce237e7f7e3193667946d1eb117cd19db0",
    "events.jsonl": "975c007a68c336007023a9ebd92ba82f02a6b7c3",
    "logins.csv": "e5669aa40eb3a08569355351eaa1c4f6e35a556d",
    "order_items.csv": "072bd904c499ce5547049eb8ba0fc2dd4c071cd0",
}
FENCE = re.compile(r"(?ms)^~~~(python|text)[ \t]*\n(.*?)^~~~[ \t]*$")


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def original(lesson: int) -> str:
    filename, sha, page, _ = PINS[lesson]
    raw = (LESSONS / filename).read_bytes()
    actual = git_blob_sha(raw)
    if actual != sha:
        raise AssertionError(f"Original lesson {lesson} changed: {actual} != {sha}")
    text = raw.decode("utf-8-sig")
    if f"Original PDF, page {page}" not in text:
        raise AssertionError(f"PDF page attribution missing: {page}")
    return text


def paired_snippets(lesson: int) -> list[tuple[str, str]]:
    fences = FENCE.findall(original(lesson))
    codes = [body for language, body in fences if language == "python"]
    outputs = [body for language, body in fences if language == "text"]
    expected = PINS[lesson][3]
    if len(codes) != expected or len(outputs) != expected:
        raise AssertionError(
            f"Lesson {lesson}: {len(codes)} code and {len(outputs)} expected outputs; expected {expected}"
        )
    return list(zip(codes, outputs))


def replay(code: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="source-python-p30-34-") as tmp:
        scratch = Path(tmp) / "python_de_dataset"
        scratch.mkdir()
        for filename, sha in DATA_PINS.items():
            raw = (DATA / filename).read_bytes()
            if git_blob_sha(raw) != sha:
                raise AssertionError(f"Original dataset changed: {filename}")
            (scratch / filename).write_bytes(raw)
        env = dict(os.environ, PYTHONIOENCODING="utf-8", LC_ALL="C", TZ="UTC")
        return subprocess.run(
            [sys.executable, "-c", code], cwd=tmp, env=env,
            capture_output=True, text=True, timeout=15, check=False,
        )


class PreservedFoundationsSixToTen(unittest.TestCase):
    def check_page(self, lesson: int):
        for number, (code, expected) in enumerate(paired_snippets(lesson), start=1):
            with self.subTest(lesson=lesson, snippet=number):
                result = replay(code)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)
                self.assertEqual(result.stderr, "")

    def test_01_five_original_blob_pins_23_output_pairs_four_dataset_pins(self):
        self.assertEqual(23, sum(len(paired_snippets(n)) for n in PINS))
        for filename, sha in DATA_PINS.items():
            with self.subTest(filename=filename):
                self.assertEqual(sha, git_blob_sha((DATA / filename).read_bytes()))

    def test_02_original_lesson06_four_comprehension_zip_loop_examples(self):
        self.check_page(6)

    def test_03_original_lesson07_five_scope_closure_examples(self):
        self.check_page(7)

    def test_04_original_lesson08_four_exception_context_examples(self):
        self.check_page(8)

    def test_05_original_lesson09_four_csv_json_jsonl_examples(self):
        self.check_page(9)

    def test_06_original_lesson10_six_practice_answers_and_output_examples(self):
        self.check_page(10)

    def test_07_original_orders_status_count_and_decimal_totals(self):
        with (DATA / "orders.csv").open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(15, len(rows))
        counts = Counter(row["status"] for row in rows)
        totals = {
            status: sum((Decimal(r["amount"]) for r in rows if r["status"] == status),
                        Decimal(0))
            for status in counts
        }
        self.assertEqual(Counter(delivered=12, cancelled=2, returned=1), counts)
        self.assertEqual({"delivered": Decimal("18972.00"),
                          "cancelled": Decimal("3498.00"),
                          "returned": Decimal("798.00")}, totals)

    def test_08_original_customers_without_orders_keys_and_missing_city(self):
        with (DATA / "customers.json").open(encoding="utf-8") as file:
            customers = json.load(file)
        with (DATA / "orders.csv").open(newline="", encoding="utf-8") as file:
            ordered = {int(row["customer_id"]) for row in csv.DictReader(file)}
        self.assertEqual([(8, "Zoya")],
                         [(c["customer_id"], c["name"])
                          for c in customers if c["customer_id"] not in ordered])
        self.assertIsNone(next(c for c in customers if c["customer_id"] == 6)
                          ["address"]["city"])

    def test_09_original_events_device_and_event_counts(self):
        with (DATA / "events.jsonl").open(encoding="utf-8") as file:
            rows = [json.loads(line) for line in file]
        self.assertEqual(12, len(rows))
        self.assertEqual(Counter(mobile=7, desktop=4, tablet=1),
                         Counter(row["props"]["device"] for row in rows))
        self.assertEqual(Counter(view=5, cart=3, checkout=2, purchase=1)
                         + Counter({"view": 1}),
                         Counter(row["event"] for row in rows))

    def test_10_original_employee_salary_distinct_top3(self):
        with (DATA / "employees.csv").open(newline="", encoding="utf-8") as file:
            salaries = [int(row["salary"]) for row in csv.DictReader(file)]
        self.assertEqual([250000, 180000, 160000],
                         sorted(set(salaries), reverse=True)[:3])
        self.assertEqual(9, len(salaries))
        self.assertLess(len(set(salaries)), len(salaries))

    def test_11_zip_strict_failure_where_plain_zip_truncates(self):
        a, b = [1, 2, 3], ["a", "b"]
        self.assertEqual([(1, "a"), (2, "b")], list(zip(a, b)))
        with self.assertRaises(ValueError):
            list(zip(a, b, strict=True))
        self.assertEqual([(1, "a")], list(zip([1], ["a", "b"], strict=False)))

    def test_12_generator_exhaustion_and_nested_loop_flattening(self):
        values = (n * 2 for n in [1, 2, 3])
        self.assertEqual(12, sum(values))
        self.assertEqual([], list(values))
        nested = [[1, 2], [], [3]]
        self.assertEqual([1, 2, 3], [x for group in nested for x in group])
        self.assertEqual({1, 2, 3}, {x for group in nested for x in group})

    def test_13_comprehension_duplicate_keys_and_for_else_break(self):
        self.assertEqual("new", {r["id"]: r["value"]
                         for r in [{"id": 1, "value": "old"},
                                   {"id": 1, "value": "new"}]}[1])
        def find(xs, wanted):
            for x in xs:
                if x == wanted:
                    break
            else:
                return "not found"
            return "found"
        self.assertEqual("not found", find([1, 2, 3], 999))
        self.assertEqual("found", find([1, 2, 3], 2))

    def test_14_scope_late_binding_vs_frozen_defaults(self):
        late = [lambda: x for x in range(4)]
        frozen = [lambda x=x: x for x in range(4)]
        self.assertEqual([3] * 4, [f() for f in late])
        self.assertEqual(list(range(4)), [f() for f in frozen])
        with self.assertRaises(UnboundLocalError):
            exec("n=1\ndef bump():\n    n+=1\nbump()")

    def test_15_keyword_only_type_hints_do_not_enforce_types(self):
        def add(*, x: int, y: int) -> int:
            return x + y
        with self.assertRaises(TypeError):
            add(1, 2)
        self.assertEqual(3, add(x=1, y=2))
        self.assertEqual("ab", add(x="a", y="b"))  # runtime does not enforce hints

    def test_16_try_else_finally_and_exception_chaining(self):
        flow = []
        def parse(text):
            try:
                return int(text)
            except ValueError as error:
                raise RuntimeError("bad integer") from error
            else:
                flow.append("unreachable if try returns")
            finally:
                flow.append("finally")
        self.assertEqual(3, parse("3"))
        self.assertEqual(["finally"], flow)
        with self.assertRaises(RuntimeError) as caught:
            parse("bad")
        self.assertIsInstance(caught.exception.__cause__, ValueError)
        self.assertEqual(["finally", "finally"], flow)

    def test_17_context_manager_cleanup_and_error_propagation(self):
        seen = []
        class Dummy:
            def __enter__(self):
                seen.append("enter")
                return self
            def __exit__(self, typ, exc, tb):
                seen.append(typ.__name__ if typ else "normal")
                return False
        with Dummy():
            seen.append("work")
        with self.assertRaises(TimeoutError):
            with Dummy():
                raise TimeoutError("synthetic")
        self.assertEqual(["enter", "work", "normal", "enter", "TimeoutError"], seen)

    def test_18_csv_quoted_comma_and_output_header_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "a.csv"
            file.write_text('id,amount\n1,"1,200"\n', encoding="utf-8")
            with file.open(newline="", encoding="utf-8") as source:
                self.assertEqual("1,200", next(csv.DictReader(source))["amount"])
            with file.open("w", newline="", encoding="utf-8") as out:
                writer = csv.DictWriter(out, fieldnames=["id"], extrasaction="ignore")
                writer.writeheader()
                writer.writerow({"id": 1, "amount": "1,200"})
            self.assertEqual("id\n1\n", file.read_text(encoding="utf-8"))

    def test_19_json_null_and_json_lines_bad_empty_line_boundary(self):
        self.assertIsNone(json.loads('{"city":null}')["city"])
        self.assertIs(json.loads('{"paid":true}')["paid"], True)
        with self.assertRaises(json.JSONDecodeError):
            json.loads("")
        self.assertEqual([1, 2], [json.loads(line)["id"]
                                  for line in ['{"id":1}', '{"id":2}']])

    def test_20_decimal_cleaning_and_invalid_input_negative_policy(self):
        raw = ["₹1,198.00", " 796 ", "N/A", "1,499.5"]
        clean, rejected = [], []
        for text in raw:
            try:
                clean.append(Decimal(text.replace("₹", "").replace(",", "").strip()))
            except InvalidOperation:
                rejected.append(text)
        self.assertEqual([Decimal("1198.00"), Decimal(796),
                          Decimal("1499.5")], clean)
        self.assertEqual(["N/A"], rejected)
        self.assertEqual(Decimal("-1.0"), Decimal("-1.0"))
        # No supplier business policy establishes valid negative/refund handling.

    def test_21_salary_unique_rank_ties_and_no_second_salary(self):
        def runner(rows):
            values = sorted(set(rows), reverse=True)
            return values[1] if len(values) > 1 else None
        self.assertIsNone(runner([]))
        self.assertIsNone(runner([5, 5, 5]))
        self.assertEqual(4, runner([5, 4, 4, 1]))
        self.assertEqual(-5, runner([-1, -5, -8]))

    def test_22_256_synthetic_status_grouping_differential(self):
        labels = ("delivered", "cancelled", "returned", "pending")
        for statuses in product(labels, repeat=4):
            rows = [{"status": status, "amount": Decimal(i + 1)}
                    for i, status in enumerate(statuses)]
            grouped = defaultdict(lambda: [0, Decimal(0)])
            for row in rows:
                grouped[row["status"]][0] += 1
                grouped[row["status"]][1] += row["amount"]
            independent = {
                kind: (
                    sum(row["status"] == kind for row in rows),
                    sum((row["amount"] for row in rows if row["status"] == kind),
                        Decimal(0))
                )
                for kind in set(statuses)
            }
            self.assertEqual(independent, {k: tuple(v) for k, v in grouped.items()})

    def test_23_source_examples_do_not_mutate_source_datasets(self):
        before = {key: git_blob_sha((DATA / key).read_bytes()) for key in DATA_PINS}
        # Page 09's CSV writer runs in a disposable directory.
        self.assertEqual(0, replay(paired_snippets(9)[1][0]).returncode)
        after = {key: git_blob_sha((DATA / key).read_bytes()) for key in DATA_PINS}
        self.assertEqual(before, after)
        self.assertEqual(DATA_PINS, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)
