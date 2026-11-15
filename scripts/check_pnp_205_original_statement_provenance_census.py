#!/usr/bin/env python3
"""Read-only, *structural* census of 205 archived PNP SQL question statements.

Source presence, provenance, original statement wording, explanatory examples,
publisher solutions and learner coursework are different evidence classes.
This deliberately DOES NOT run or assert 205 official SQL answers, verify
PDF page images, interpret semantics, or award learner credit.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path
import re
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "01. SQL Mastery/PNP-PROBLEM-INDEX.md"
ARCHIVE = ROOT / "99. Reference Materials/Original Mastery Snapshot"
BASE = ARCHIVE / "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
P_PDF = BASE / "Source Materials/Updated_100_SQL_Interview_Questions.pdf"
A_PDF = BASE / "Source Materials/Advanced_SQL_100_Query_Questions_Vol1 (2).pdf"
X_README = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/README.md"
PINNED = {
    INDEX: "e407ada692fe6291d5f60692088d99afffbff128",
    P_PDF: "65b9eab3cf82e363f072dd317a7c963f03503b95",
    A_PDF: "d9788de757020c4290a5e4f3ada778252f74e889",
}
ROWS = re.compile(
    r"^\|\s*([PAX]\d{3})\s*\|\s*\[[^\]]+\]\(<([^>]+)>\)\s*\|\s*([^|]+)\|",
    re.M,
)
HEADING = {
    "P": re.compile(r"^# PNP Q(\d{3})\.", re.M),
    "A": re.compile(r"^# Advanced Q(\d{3})\.", re.M),
    "X": re.compile(r"^# Extra Q(\d{3})\.", re.M),
}
EXPECTED = {f"P{i:03d}" for i in range(1, 101)} | {
    f"A{i:03d}" for i in range(1, 101)} | {
    f"X{i:03d}" for i in range(1, 6)
}


def sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def census() -> dict[str, dict[str, object]]:
    assert sha(INDEX) == PINNED[INDEX], "Original 205-question index changed"
    found: dict[str, dict[str, object]] = {}
    for ident, url, status in ROWS.findall(INDEX.read_text(encoding="utf-8")):
        assert ident not in found, f"Duplicate index record: {ident}"
        resolved = (INDEX.parent / unquote(url)).resolve()
        assert resolved.is_relative_to(ARCHIVE.resolve()), (ident, "escaped archive", resolved)
        assert resolved.is_file(), (ident, "missing source", resolved)
        assert resolved.name.startswith(ident + "."), (ident, "wrong source ID", resolved)
        raw = resolved.read_bytes()
        data = raw.decode("utf-8-sig")
        found[ident] = {
            "path": resolved,
            "text": data,
            "blob": hashlib.sha1(
                b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
            ).hexdigest(),
            "status": status.strip(),
        }
    assert set(found) == EXPECTED, (
        "Not exactly 100 P + 100 A + 5 X records",
        sorted(EXPECTED ^ set(found)),
    )
    return found


class StructuralOriginalStatementCensus(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entries = census()

    def test_01_all_205_source_files_have_unique_archived_path_and_git_blob(self):
        self.assertEqual(205, len(self.entries))
        self.assertEqual(205, len({str(e["path"]) for e in self.entries.values()}))
        self.assertEqual(205, len({e["blob"] for e in self.entries.values()}))
        self.assertEqual(Counter({"P": 100, "A": 100, "X": 5}),
                         Counter(k[0] for k in self.entries))

    def test_02_all_original_headings_match_source_family_and_numeric_id(self):
        for ident, entry in self.entries.items():
            with self.subTest(source=ident):
                match = HEADING[ident[0]].search(str(entry["text"]))
                self.assertIsNotNone(match, (ident, "missing original heading"))
                self.assertEqual(int(ident[1:]), int(match.group(1)))

    def test_03_each_archived_question_contains_an_explicit_nonempty_task(self):
        for ident, entry in self.entries.items():
            with self.subTest(source=ident):
                text = str(entry["text"])
                m = re.search(r"^\*\*Task\.\*\*\s*(.+)$", text, re.M)
                self.assertIsNotNone(m, (ident, "missing Task paragraph"))
                self.assertGreater(len(m.group(1).strip()), 8, ident)
                self.assertIn("## Question and image", text, ident)

    def test_04_family_source_attribution_and_live_source_binary_identity(self):
        for path, pin in PINNED.items():
            with self.subTest(path=path.name):
                self.assertEqual(pin, sha(path), "Original/index changed")
        self.assertTrue(X_README.is_file())
        for ident, entry in self.entries.items():
            with self.subTest(source=ident):
                text = str(entry["text"])
                self.assertIn("**Source:**", text)
                if ident[0] == "P":
                    self.assertIn("100 SQL Interview Questions", text)
                elif ident[0] == "A":
                    self.assertIn("Advanced SQL 100 Query Questions", text)
                    self.assertIn("The source solutions use MySQL 8", text)
                else:
                    self.assertIn("PrepNPlaced bundle README", text)
                    self.assertIn("no answer key is supplied", text.lower())

    def test_05_source_output_and_illustration_described_not_authenticated(self):
        for ident, entry in self.entries.items():
            with self.subTest(source=ident):
                body = str(entry["text"])
                self.assertIn("### Sample input and expected output", body)
                if ident[0] == "A":
                    self.assertIn("illustrative", body.lower(), ident)
                if ident[0] == "X":
                    self.assertIn("no sample rows or expected-output table", body.lower())

    def test_06_source_schema_section_present_not_provider_dataset_parity(self):
        for ident, entry in self.entries.items():
            with self.subTest(source=ident):
                self.assertIn("## Schema", str(entry["text"]), ident)

    def test_07_archived_learner_and_official_sections_present_not_solved(self):
        for ident, entry in self.entries.items():
            with self.subTest(source=ident):
                body = str(entry["text"])
                self.assertIn("## My solution", body, ident)
                self.assertIn("## Official solution", body, ident)
                if ident[0] == "X":
                    self.assertIn(
                        "No official solution is provided in the source bundle", body, ident
                    )

    def test_08_advanced_and_extra_original_source_difficulty_is_estimated(self):
        for ident, entry in self.entries.items():
            with self.subTest(source=ident):
                if ident[0] in ("A", "X"):
                    self.assertIn("Practice difficulty (estimated)", str(entry["text"]))

    def test_09_index_learning_status_is_preserved_not_inferred_from_tests(self):
        statuses = Counter(str(e["status"]) for e in self.entries.values())
        self.assertEqual(205, sum(statuses.values()))
        self.assertFalse(any(not status for status in statuses))
        print("CENSUS index-status labels (historical, NOT new credit):",
              dict(sorted(statuses.items())))

    def test_10_distinguish_source_archive_from_provider_answer_and_grading(self):
        a = [self.entries[f"A{i:03d}"] for i in range(1, 101)]
        x = [self.entries[f"X{i:03d}"] for i in range(1, 6)]
        self.assertEqual(100, len(a))
        self.assertEqual(5, len(x))
        self.assertTrue(all("The source solutions use MySQL 8" in str(e["text"])
                            for e in a))
        self.assertTrue(all("no answer key is supplied" in str(e["text"]).lower()
                            for e in x))
        print("PARTIAL: 205 distinct original Markdown statements structurally checked.")
        print("NOT CHECKED: 205 original rendered PDF/README question semantic parity;"
              " 205 official SQL outputs; original provider grading; learner mastery.")
        print("NOTE: A-PDF MySQL answer text is not authenticated by archive metadata."
              " X README expressly has no supplied answer key.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
