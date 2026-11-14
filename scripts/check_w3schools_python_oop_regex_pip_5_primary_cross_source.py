#!/usr/bin/env python3
"""Bounded source-pinned review of 5 hosted W3 Python pages vs preserved mentor/Bosscoder originals.

Only the two explicitly marked original mentor snippets are replayed verbatim.
Other tests are independently authored Python semantics, NOT W3 editor
acceptance, official Bosscoder answers, or learner submissions.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import FrozenInstanceError, dataclass
from decimal import Decimal
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / "99. Reference Materials" / "Original Mastery Snapshot" / "2. Python Mastry"
J = ROOT / "99. Reference Materials" / "Legacy Journey Snapshot" / "02-python" / "bosscoder" / "lecture-05"
CLASS_LESSON = M / "3. Advanced Python" / "03. Classes and dataclasses.md"
MODULE_LESSON = M / "1. Python from Zero" / "16. Modules packages and pip.md"
LOG_LESSON = M / "5. Coding Round Patterns" / "07. Parse logs.md"
LOG = M / "python_de_dataset" / "app.log"
ORIGINALS = (
    (CLASS_LESSON, "0a8c6988b3f29fa4256bfdcdcf54bb8219fbce98"),
    (MODULE_LESSON, "2002d657a4bb52dcd1e369a9083dfd1d7b5c37eb"),
    (LOG_LESSON, "a766d7427e0cafee1ea227ace0418ec692a25fa4"),
    (J / "01-classes-objects-methods.md", "d4edea0c25bb4e3ba9f993c7be510783d53ba3cb"),
    (J / "02-inheritance-and-mro.md", "37fcd48c2ae27037ac7240d08ccd1a33be73c611"),
    (J / "03-encapsulation-polymorphism-abstraction.md", "e8fd269bfdaab9f667746e1ebdf371a0ecf7de21"),
    (LOG, "d75778a27a947725c57b84134ec32297f45bb9df"),
)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def original_class_snippets() -> list[str]:
    text = CLASS_LESSON.read_text(encoding="utf-8")
    return re.findall(r"~~~python\n(.*?)\n~~~", text, flags=re.DOTALL)


def run_isolated(code: str) -> str:
    result = subprocess.run([sys.executable, "-c", code], text=True,
                            capture_output=True, timeout=15, check=False)
    if result.returncode != 0:
        raise AssertionError("isolated original source raised: " + result.stderr)
    return result.stdout.strip()


class W3PythonOopRegexPipFiveCrossSource(unittest.TestCase):
    def test_01_seven_preserved_original_blob_identities_and_primary_links(self):
        for path, expected in ORIGINALS:
            with self.subTest(path=path.name):
                self.assertEqual(expected, git_blob_sha(path.read_bytes()))
        self.assertIn("PDF page 37 of 80", CLASS_LESSON.read_text(encoding="utf-8"))
        self.assertIn("https://www.w3schools.com/python/python_classes.asp",
                      CLASS_LESSON.read_text(encoding="utf-8"))
        self.assertIn("https://www.w3schools.com/python/python_pip.asp",
                      MODULE_LESSON.read_text(encoding="utf-8"))
        self.assertIn("https://www.w3schools.com/python/python_regex.asp",
                      LOG_LESSON.read_text(encoding="utf-8"))
        self.assertIn("assignments unsolved", (J / "02-inheritance-and-mro.md").read_text(encoding="utf-8"))
        self.assertIn("no assignment completed", (J / "03-encapsulation-polymorphism-abstraction.md").read_text(encoding="utf-8"))

    def test_02_original_mentor_page37_frozen_order_example_stdout(self):
        examples = original_class_snippets()
        self.assertGreaterEqual(len(examples), 3)
        self.assertEqual("101 delivered 1198.00\nTrue\nrejected: amount must be positive",
                         run_isolated(examples[0]))

    def test_03_original_mentor_page37_alternate_constructor_stdout(self):
        examples = original_class_snippets()
        self.assertGreaterEqual(len(examples), 3)
        self.assertEqual("101", run_isolated(examples[2]))

    def test_04_class_attribute_not_copied_per_instance(self):
        class Batch:
            file_type = "csv"
        a, b = Batch(), Batch()
        Batch.file_type = "jsonl"
        self.assertEqual(("jsonl", "jsonl"), (a.file_type, b.file_type))
        self.assertNotIn("file_type", a.__dict__)

    def test_05_instance_shadowing_and_class_fallback(self):
        class Job:
            mode = "dev"
        first, second = Job(), Job()
        first.mode = "prod"
        self.assertEqual(("prod", "dev", "dev"), (first.mode, second.mode, Job.mode))
        del first.mode
        self.assertEqual("dev", first.mode)

    def test_06_mutable_class_level_list_sharing(self):
        class Batch:
            processed = []
        first, second = Batch(), Batch()
        first.processed.append("file-a")
        self.assertEqual(["file-a"], second.processed)
        first.processed = []
        self.assertEqual([], first.processed)
        self.assertEqual(["file-a"], second.processed)

    def test_07_method_shadowing_is_per_instance(self):
        class Processor:
            def run(self):
                return "original"
        a, b = Processor(), Processor()
        a.run = lambda: "shadow"
        self.assertEqual(("shadow", "original", "original"),
                         (a.run(), b.run(), Processor.run(a)))

    def test_08_classmethod_and_staticmethod_and_subclass_cls(self):
        class Order:
            def __init__(self, number):
                self.number = number

            @classmethod
            def parse(cls, text):
                return cls(int(text))

            @staticmethod
            def clean(text):
                return text.strip().lower()

        class SpecialOrder(Order):
            pass

        obj = SpecialOrder.parse("12")
        self.assertIsInstance(obj, SpecialOrder)
        self.assertEqual(12, obj.number)
        self.assertEqual("paid", Order.clean(" PAID "))

    def test_09_child_initializer_is_not_implicit_parent_call(self):
        class Parent:
            def __init__(self):
                self.ready = True

        class BrokenChild(Parent):
            def __init__(self):
                self.name = "bad"

        class GoodChild(Parent):
            def __init__(self):
                super().__init__()
                self.name = "ok"

        self.assertFalse(hasattr(BrokenChild(), "ready"))
        self.assertTrue(GoodChild().ready)

    def test_10_c3_diamond_cooperative_super_visits_each_base_once(self):
        seen = []

        class Root:
            def run(self):
                seen.append("root")

        class Left(Root):
            def run(self):
                seen.append("left")
                super().run()

        class Right(Root):
            def run(self):
                seen.append("right")
                super().run()

        class Both(Left, Right):
            pass

        Both().run()
        self.assertEqual(["left", "right", "root"], seen)
        self.assertEqual(("Both", "Left", "Right", "Root", "object"),
                         tuple(c.__name__ for c in Both.__mro__))

    def test_11_inconsistent_multiple_inheritance_order_rejected(self):
        class A: pass
        class B: pass
        class AB(A, B): pass
        class BA(B, A): pass

        with self.assertRaises(TypeError):
            type("Impossible", (AB, BA), {})

    def test_12_duck_typing_and_abstract_contract_distinguished(self):
        class Input(ABC):
            @abstractmethod
            def read(self):
                pass

        class FileInput(Input):
            def read(self):
                return ["a"]

        class ApiInput:
            def read(self):
                return ["b", "c"]

        with self.assertRaises(TypeError):
            Input()
        self.assertEqual([1, 2], [len(item.read()) for item in (FileInput(), ApiInput())])

    def test_13_frozen_dataclass_outer_attributes_not_deep_frozen(self):
        @dataclass(frozen=True, slots=True)
        class Record:
            order_id: int
            labels: list[str]

        row = Record(1, ["new"])
        with self.assertRaises(FrozenInstanceError):
            row.order_id = 2
        row.labels.append("paid")
        self.assertEqual(["new", "paid"], row.labels)
        self.assertFalse(hasattr(row, "__dict__"))

    def test_14_regex_search_match_fullmatch_are_distinct(self):
        p = re.compile(r"job=(?P<job>\w+)")
        sample = "INFO job=orders_daily trailing"
        self.assertEqual("orders_daily", p.search(sample).group("job"))
        self.assertIsNone(p.match(sample))
        self.assertIsNone(p.fullmatch(sample))
        self.assertIsNotNone(re.fullmatch(r"job=\w+", "job=orders_daily"))

    def test_15_regex_unicode_flags_and_named_optional_groups(self):
        self.assertTrue(bool(re.fullmatch(r"\d+", "१२३")))
        self.assertIsNone(re.fullmatch(r"\d+", "१२३", flags=re.ASCII))
        self.assertIsNone(re.search(r"^ERROR", "INFO\nERROR"))
        self.assertIsNotNone(re.search(r"^ERROR", "INFO\nERROR", flags=re.MULTILINE))
        expression = re.compile(r"job=(?P<job>\w+)(?: rows=(?P<rows>\d+))?")
        result = expression.fullmatch("job=orders_daily")
        self.assertEqual({"job": "orders_daily", "rows": None}, result.groupdict())

    def test_16_source_log_14_rows_13_parsed_one_quarantined(self):
        raw = LOG.read_text(encoding="utf-8").splitlines()
        self.assertEqual(14, len(raw))
        pattern = re.compile(
            r'(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+'
            r'(?P<level>INFO|WARN|ERROR)\s+'
            r'job=(?P<job>\w+)\s+step=(?P<step>\w+)'
            r'(?:\s+rows=(?P<rows>\d+))?\s+duration_ms=(?P<ms>\d+)'
            r'(?:\s+msg="(?P<msg>[^"]*)")?'
        )
        records, quarantined = [], []
        for number, line in enumerate(raw, start=1):
            found = pattern.fullmatch(line.strip())
            if found:
                records.append(found.groupdict())
            else:
                quarantined.append((number, line))
        self.assertEqual(13, len(records))
        self.assertEqual([(7, "--- scheduler restarted ---")], quarantined)
        self.assertEqual(Counter({"customers_dim": 7, "orders_daily": 6}),
                         Counter(row["job"] for row in records))
        self.assertEqual(3, sum(row["level"] == "ERROR" for row in records))
        self.assertEqual(1, sum(row["level"] == "WARN" for row in records))
        self.assertEqual(5003, max(int(row["ms"]) for row in records
                                   if row["job"] == "customers_dim"))
        self.assertIsNone(pattern.fullmatch(raw[0] + " unexpected_trailer"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
