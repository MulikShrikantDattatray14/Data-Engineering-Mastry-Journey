#!/usr/bin/env python3
"""Bounded PUBLIC source exposure / provenance / credential-marker audit.

Read-only; does NOT assert third-party licenses, permissions, PII clearance,
binary/PDF safety, external vendor grading, or learner mastery.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "99. Reference Materials"
ARCHIVE_A = "99. Reference Materials/Original Mastery Snapshot/"
ARCHIVE_B = "99. Reference Materials/Legacy Journey Snapshot/"
INVENTORY = "99. Reference Materials/SOURCE-INVENTORY.json"
LEGACY_LICENSE = "99. Reference Materials/Legacy Journey Snapshot/LICENSE"
EXPECTED_LEGACY_LICENSE_SHA = "d0d01053e2ae3d7e9879d8d3a2a81e36482cb9aa"
EXPECTED_PDFS = {
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/Source Materials/Advanced_SQL_100_Query_Questions_Vol1 (2).pdf": ("d9788de757020c4290a5e4f3ada778252f74e889", 1654592),
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/Source Materials/PrepNPlaced_SQL_100_v2/100_SQL_Interview_Questions.pdf": ("65b9eab3cf82e363f072dd317a7c963f03503b95", 3185404),
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/Source Materials/Updated_100_SQL_Interview_Questions.pdf": ("65b9eab3cf82e363f072dd317a7c963f03503b95", 3185404),
    "99. Reference Materials/Original Mastery Snapshot/2. Python Mastry/Source/1793477658005.pdf": ("90f8abc8a0bf4c865a6b545938a2b285204a008e", 488120),
}
EXPECTED_BINARY_EXTENSIONS = {
    ".pdf": 4, ".zip": 2, ".xlsx": 1, ".png": 15, ".jpg": 15
}
# Deliberately high-confidence signatures only. This does NOT detect all
# credentials, email addresses, identity data, or embedded PDF/image content.
CREDENTIAL_SIGNATURES = {
    "private_key_block": re.compile(rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"),
    "github_classic_pat": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "github_fine_grained_pat": re.compile(rb"\bgithub_pat_[A-Za-z0-9_]{50,}\b"),
    "aws_access_key_id": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
}
TEXT_SUFFIXES = {".md", ".txt", ".py", ".json", ".csv", ".sql", ".yml", ".yaml", ".ini", ".sh"}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def tracked() -> list[str]:
    result = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [p for p in result.decode("utf-8").split("\0") if p]


class PublicArchiveBoundaryAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = tracked()
        cls.original = sorted(p for p in cls.paths if p.startswith((ARCHIVE_A, ARCHIVE_B)))

    def test_01_two_original_archives_are_physically_tracked_at_552_and_192(self):
        self.assertEqual(sum(p.startswith(ARCHIVE_A) for p in self.original), 552)
        self.assertEqual(sum(p.startswith(ARCHIVE_B) for p in self.original), 192)
        self.assertEqual(len(self.original), 744)
        self.assertFalse((ROOT / ".gitmodules").exists())

    def test_02_all_744_inventory_entries_match_actual_archived_bytes(self):
        info = json.loads((ROOT / INVENTORY).read_text(encoding="utf-8"))
        self.assertEqual(info["summary"]["original_mastry_files"], 552)
        self.assertEqual(info["summary"]["original_journey_files"], 192)
        entries = info["entries"]
        self.assertEqual(len(entries), 744)
        paths = [entry["preserved_path"] for entry in entries]
        self.assertEqual(len(paths), len(set(paths)), "duplicate manifest path")
        self.assertEqual(set(paths), set(self.original), "manifest / physical archive path drift")
        for entry in entries:
            path = entry["preserved_path"]
            with self.subTest(source=path):
                data = (ROOT / path).read_bytes()
                self.assertEqual(len(data), entry["bytes"])
                self.assertEqual(git_blob_sha(data), entry["git_blob_sha"])

    def test_03_four_original_pdf_blob_hashes_and_duplicate_identity(self):
        pdfs = sorted(p for p in self.original if p.lower().endswith(".pdf"))
        self.assertEqual(pdfs, sorted(EXPECTED_PDFS))
        for path, (sha, size) in EXPECTED_PDFS.items():
            with self.subTest(source=path):
                content = (ROOT / path).read_bytes()
                self.assertEqual(len(content), size)
                self.assertTrue(content.startswith(b"%PDF-"))
                self.assertEqual(git_blob_sha(content), sha)
        sql_100 = [p for p in pdfs if p.endswith("100_SQL_Interview_Questions.pdf")]
        self.assertEqual(len(sql_100), 2)
        self.assertEqual((ROOT / sql_100[0]).read_bytes(), (ROOT / sql_100[1]).read_bytes())

    def test_04_original_binary_formats_require_separate_content_review(self):
        extensions = Counter(Path(p).suffix.lower() for p in self.original)
        for suffix, count in EXPECTED_BINARY_EXTENSIONS.items():
            with self.subTest(extension=suffix):
                self.assertEqual(extensions[suffix], count)
        self.assertEqual(extensions[".csv"], 16)
        for path in self.original:
            suffix = Path(path).suffix.lower()
            if suffix in (".zip", ".xlsx"):
                with self.subTest(archive_file=path):
                    self.assertTrue((ROOT / path).read_bytes().startswith(b"PK"))
        # Do not call this visual/PDF/ZIP, PII or third-party-license clearance.

    def test_05_historical_mit_notice_is_not_a_root_or_provider_license(self):
        license_paths = [p for p in self.paths if Path(p).name.upper() in
                         {"LICENSE", "LICENSE.MD", "LICENSE.TXT", "COPYING", "NOTICE"}]
        self.assertEqual(license_paths, [LEGACY_LICENSE])
        license_bytes = (ROOT / LEGACY_LICENSE).read_bytes()
        self.assertEqual(git_blob_sha(license_bytes), EXPECTED_LEGACY_LICENSE_SHA)
        self.assertIn(b"MIT License", license_bytes)
        self.assertFalse((ROOT / "LICENSE").exists())
        # Presence of historical own MIT text is NOT third-party reuse permission.

    def test_06_no_high_confidence_secret_markers_in_original_text_files(self):
        suspicious = []
        scanned = 0
        for path in self.original:
            if Path(path).suffix.lower() not in TEXT_SUFFIXES:
                continue
            content = (ROOT / path).read_bytes()
            scanned += 1
            for category, pattern in CREDENTIAL_SIGNATURES.items():
                if pattern.search(content):
                    # Report only category/count; NEVER print any credentials.
                    suspicious.append(category)
        self.assertGreater(scanned, 600)
        self.assertFalse(suspicious,
                         "High-confidence credential signature categories: "
                         + ", ".join(sorted(set(suspicious))))

    def test_07_explicit_four_source_attribution_is_not_rights_signoff(self):
        ref = (REFERENCE / "SOURCE-COVERAGE-MATRIX.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for source in ("Bosscoder", "PNP", "W3Schools", "ChatGPT"):
            with self.subTest(source=source):
                self.assertIn(source, ref)
                self.assertIn(source, readme)
        self.assertIn("four-source", ref.lower().replace("four-source", "four-source"))
        self.assertIn("audit", readme.lower())
        # This checks attribution text exists; does not establish copyright grants.


if __name__ == "__main__":
    unittest.main(verbosity=2)
