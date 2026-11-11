#!/usr/bin/env python3
"""Audit guard for the seven legacy Data Engineering subject *roadmap stubs*.

This asserts immutable archive provenance and the source/teaching boundary.
It does NOT execute Spark/cloud jobs, verify source lessons, or credit learner work.
"""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "99. Reference Materials" / "Legacy Journey Snapshot"

# Git blob IDs obtained by independently inspecting the original preserved files.
# Each legacy subject directory contained exactly one README at audit time.
SOURCES = (
    ("03-databases-and-modeling", "03. Database Design and Modeling",
     "4db710f5f27e287371cc7b4c0305b6ff911e36de", "OLTP vs OLAP"),
    ("04-data-pipelines", "04. Data Pipelines and ETL",
     "218394bcb218acbcc4bb7689077e73b5f8e8c270", "idempotency"),
    ("05-apache-spark", "05. Apache Spark",
     "5a26de48654861b7d4c9fef15e622a6e18bde59f", "shuffles"),
    ("06-cloud-and-orchestration", "06. Cloud and Orchestration",
     "5a0fa8f0f4932f40d2f465c13403969068568479", "IAM"),
    ("07-system-design", "07. Data System Design",
     "b448fe0bfcd999d407c9d883629f86395030d2d0", "deduplication"),
    ("08-projects", "08. Projects",
     "decd51027e1e60142ff661eca76868aaf8315aef", "not yet built"),
    ("09-interview-preparation", "09. Interview Preparation",
     "fa722660dea3999723d34df9e54d56781e97d812", "mock interview"),
)


def git_blob_sha(path: Path) -> str:
    relative = path.relative_to(ROOT)
    return subprocess.check_output(
        ["git", "hash-object", "--", str(relative)],
        cwd=ROOT, text=True,
    ).strip()


class SubjectBoundaryAudit(unittest.TestCase):
    def test_each_of_seven_archived_readmes_is_exactly_preserved(self) -> None:
        for archived, _, sha, phrase in SOURCES:
            with self.subTest(source=archived):
                path = LEGACY / archived / "README.md"
                self.assertTrue(path.is_file(), str(path))
                self.assertEqual(git_blob_sha(path), sha)
                self.assertIn(phrase.lower(), path.read_text(encoding="utf-8").lower())

    def test_each_archived_subject_has_only_the_original_readme(self) -> None:
        # This checks the historical source inventory, NOT future canonical subjects.
        # A roadmap mention is not a runnable lesson or project.
        for archived, _, _, _ in SOURCES:
            with self.subTest(source=archived):
                actual = sorted(str(p.relative_to(LEGACY / archived))
                                for p in (LEGACY / archived).rglob("*") if p.is_file())
                self.assertEqual(actual, ["README.md"])

    def test_all_seven_canonical_subjects_are_explicitly_unfinished(self) -> None:
        for _, canonical, _, _ in SOURCES:
            with self.subTest(subject=canonical):
                path = ROOT / canonical / "README.md"
                self.assertTrue(path.is_file(), str(path))
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("not a claim that the curriculum has been completed", text)
                self.assertIn("original", text)

    def test_no_unsupported_mastery_credit_in_source_matrix(self) -> None:
        matrix = (ROOT / "99. Reference Materials" /
                  "SOURCE-COVERAGE-MATRIX.md").read_text(encoding="utf-8")
        self.assertIn("Deep-source integration waits for supplied material", matrix)
        self.assertIn("Concept-by-concept consolidation", matrix)


if __name__ == "__main__":
    unittest.main(verbosity=2)
