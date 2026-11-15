"""Source-pinned read-only Python-from-Zero lessons 11-15 original output audit.

All original source, learner history and canonical notes stay unchanged.
Synthetic test results are not official answers, learner work or mastery.
"""
from __future__ import annotations
import ast
from collections import defaultdict
from decimal import Decimal
import hashlib
from itertools import product
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry" / "1. Python from Zero"
PIN = {
  11: ("11. Tuples and sets.md", "3a2788bfc668b3a1ebe5bfd6f58f8fc8c9bfcb2e", 15, 5, 5),
  12: ("12. Dictionaries - key and value.md", "3602334cd9cc779f89eface11b82f844954068a8", 16, 7, 7),
  13: ("13. Which data structure.md", "1142a434f0bda23d683eaf2de5176a4c13020438", 17, 3, 2),
  14: ("14. Functions - reusable steps.md", "cb497c2660c6e3ae34b330f372ef087fa3550d4b", 18, 6, 6),
  15: ("15. Functions part 2 - mini pipeline.md", "abf9377580230db87cc4632ae933478e89bc4df2", 19, 6, 4),
}
FENCE = re.compile(r"(?ms)^(" + re.escape(chr(96) * 3) + r"|~~~)(python|text)[ \t]*\n(.*?)^\1[ \t]*$")

def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def blocks(n, kind):
    name, sha, page, codes, outputs = PIN[n]
    raw = (BASE / name).read_bytes()
    assert blob(raw) == sha, "Original source SHA mismatch: " + name
    source = raw.decode("utf-8-sig")
    assert f"page {page} of 80" in source, "Missing source page attribution"
    fences = FENCE.findall(source)
    py = [body for _, label, body in fences if label == "python"]
    txt = [body for _, label, body in fences if label == "text"]
    assert (len(py), len(txt)) == (codes, outputs), f"Source fence count changed on {n}"
    return py if kind == "python" else txt

def run(n, indices, extra=""):
    code = "\n\n".join(blocks(n, "python")[i] for i in indices) + "\n" + extra
    with tempfile.TemporaryDirectory(prefix="python-source-11-15-") as tmp:
        return subprocess.run([sys.executable, "-c", code], cwd=tmp,
                              capture_output=True, text=True, timeout=20, check=False)

def exact(n, indices, text_id):
    proc = run(n, indices)
    assert proc.returncode == 0, proc.stderr
    assert proc.stderr == ""
    assert proc.stdout == blocks(n, "text")[text_id], (n, indices, repr(proc.stdout))

class IndependentOriginalElevenToFifteen(unittest.TestCase):
    def test_01_original_blob_pins_pages_and_fence_census(self):
        self.assertEqual(27, sum(len(blocks(n, "python")) for n in PIN))
        self.assertEqual(24, sum(len(blocks(n, "text")) for n in PIN))

    def test_02_lesson11_all_five_original_exact_printouts(self):
        for i in range(5):
            with self.subTest(source=i): exact(11, [i], i)

    def test_03_lesson12_six_original_exact_printouts(self):
        for i in (0, 2, 3, 4, 5, 6):
            with self.subTest(source=i): exact(12, [i], i)

    def test_03b_source12_original_trailing_space_output_discrepancy(self):
        # Source intentionally PRESERVED, not silently normalized or rewritten.
        # Original code's print(product, end=" ") emits a trailing space.
        observed = run(12, [1])
        self.assertEqual(0, observed.returncode, observed.stderr)
        expected_display = blocks(12, "text")[1]
        self.assertIn("Mouse Hub Pens\n", expected_display)
        self.assertEqual(
            expected_display.replace("Mouse Hub Pens\n", "Mouse Hub Pens \n", 1),
            observed.stdout,
        )
        self.assertNotEqual(expected_display, observed.stdout)

    def test_04_lesson13_one_exact_ordered_original_printout(self):
        exact(13, [1], 0)

    def test_05_lesson13_original_timer_is_unstable_not_a_fixed_output(self):
        proc = run(13, [0])
        self.assertEqual(0, proc.returncode, proc.stderr)
        lines = proc.stdout.splitlines()
        self.assertEqual(["True", "True"], lines[:2])
        self.assertEqual(3, len(lines))
        self.assertRegex(lines[2], r"^list [0-9]+\.[0-9]{2} ms vs set [0-9]+\.[0-9]{4} ms$")

    def test_06_lesson13_set_order_is_unstable_verify_values_only(self):
        proc = run(13, [2])
        self.assertEqual(0, proc.returncode, proc.stderr)
        a, b = proc.stdout.strip().splitlines()
        values = ast.literal_eval(a)
        self.assertEqual(3, len(values))
        self.assertEqual({"Aarav", "Diya", "Kabir"}, set(values))
        self.assertEqual({"b", "a", "n"}, ast.literal_eval(b))

    def test_07_lesson14_five_original_success_outputs(self):
        for code_id in (0, 1, 2, 4, 5):
            with self.subTest(source=code_id): exact(14, [code_id], code_id)

    def test_08_lesson14_original_expected_nameerror(self):
        proc = run(14, [3])
        self.assertNotEqual(0, proc.returncode)
        self.assertEqual("", proc.stdout)
        self.assertIn(blocks(14, "text")[3].strip(), proc.stderr)

    def test_09_lesson15_four_original_outputs_including_composed_pipeline(self):
        for codes, out in [([0], 0), ([1], 1), ([2, 3, 4], 2), ([5], 3)]:
            with self.subTest(codes=codes): exact(15, codes, out)

    def test_10_tuple_is_fixed_but_member_list_can_change(self):
        value = ([101], "Pune")
        value[0].append(102)
        self.assertEqual(([101, 102], "Pune"), value)
        with self.assertRaises(TypeError): value[0] = []  # type: ignore[index]

    def test_11_set_boolean_duplicate_and_nonhashable_member(self):
        self.assertEqual({True}, {True, 1, 1.0})
        with self.assertRaises(TypeError): {["not hashable"]}  # type: ignore[list-item]
        self.assertIsInstance({}, dict)
        self.assertIsInstance(set(), set)

    def test_12_dictionary_missing_vs_explicit_none_and_overwrites(self):
        value = {"a": None, "b": 0}
        self.assertIsNone(value.get("a", "fallback"))
        self.assertEqual("fallback", value.get("c", "fallback"))
        with self.assertRaises(KeyError): _ = value["c"]
        value["a"] = 10
        self.assertEqual(["a", "b"], list(value))
        self.assertEqual(2, {"a": 1, "a": 2}["a"])

    def test_13_zip_truncation_distinct_key_and_exact_money(self):
        self.assertEqual({1: 20}, dict(zip([1, 1, 2], [10, 20])))
        with self.assertRaises(ValueError): list(zip([1, 2], [10], strict=True))
        grouped = defaultdict(Decimal)
        for city, amount in [("Pune", "1.10"), ("Delhi", "2"), ("Pune", "0.20")]:
            grouped[city] += Decimal(amount)
        self.assertEqual({"Pune": Decimal("1.30"), "Delhi": Decimal("2")}, dict(grouped))

    def test_14_original_pipeline_rejects_bad_float_but_admits_nan(self):
        suffix = ("\ntry:\n    parse('106,delivered,not-a-number')\n"
                  "except ValueError:\n    print('ValueError')\n"
                  "import math\nprint(math.isnan(parse('107,delivered,NaN')['amount']))\n"
                  "print(parse('bad row') is None)\n")
        proc = run(15, [2, 3], suffix)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertEqual("ValueError\nTrue\nTrue\n", proc.stdout)

    def test_15_original_pipeline_duplicates_id_and_float_cents(self):
        suffix = ("\nrows = [parse('101,delivered,0.1'), parse('101,delivered,0.2')]\n"
                  "print(summarise(keep_delivered(rows)))\n")
        proc = run(15, [2, 3, 4], suffix)
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertIn("{'orders': 2, 'revenue': 0.30000000000000004}\n", proc.stdout)
        self.assertEqual(Decimal("0.3"), Decimal("0.1") + Decimal("0.2"))

    def test_16_243_synthetic_status_combinations_against_independent_oracle(self):
        for statuses in product(("delivered", "cancelled", "returned"), repeat=5):
            transformed = [(f" {s.upper()} ", i + 1) for i, s in enumerate(statuses)]
            actual = sum(v for s, v in transformed if s.strip().lower() == "delivered")
            expected = sum(i + 1 for i, s in enumerate(statuses) if s == "delivered")
            self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main(verbosity=2)
