#!/usr/bin/env python3
"""Read-only upstream Git tree and source-inventory provenance regression tests.

This is structural exact-Git-tree equivalence, NOT PDF rendering, official answer
authentication, student completion, public redistribution authorization or PII signoff.
The source-commit/tree pair was independently retrieved from both original GitHub
repositories during the 2026-11-14 audit; CI checks preserved local Git objects.
"""
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "99. Reference Materials/SOURCE-INVENTORY.json"
MASTER = "99. Reference Materials/Original Mastery Snapshot"
JOURNEY = "99. Reference Materials/Legacy Journey Snapshot"
EXPECTED_SOURCE = {
    MASTER: {
        "source": "Data-Engineering-Mastry/main",
        "commit": "bef07ec3e20825eb8e29bd9afc9f6d7ad8c77e3a",
        "tree": "8a3c3bfb7b26588fceb13bf04b9af2fdee7df46e",
        "count": 552,
    },
    JOURNEY: {
        "source": "data-engineering-journey/main",
        "commit": "92666943f5d6a223db496d4fbdc7017f195d682d",
        "tree": "63b9330dcc63b6f8bfbd9ddad7a5be0bb845439e",
        "count": 192,
    },
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


class UpstreamArchiveTreeProvenance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
        cls.entries = cls.inventory["entries"]

    def test_01_entire_native_copy_subtrees_equal_directly_checked_upstream_trees(self):
        # A Git tree's SHA commits to all filenames, modes and child blob contents,
        # not just the separately generated 744-line source manifest.
        for folder, record in EXPECTED_SOURCE.items():
            with self.subTest(source=record["source"]):
                self.assertEqual(git("rev-parse", "HEAD:" + folder), record["tree"])

    def test_02_exactly_744_native_unchanged_original_paths_remain_git_tracked(self):
        # Decode NUL filenames explicitly; do not let git's quotePath alter names.
        raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        tracked = set(filter(None, raw.decode("utf-8").split("\0")))
        actual = {p for p in tracked if p.startswith(MASTER + "/") or p.startswith(JOURNEY + "/")}
        manifest_paths = [entry["preserved_path"] for entry in self.entries]
        self.assertEqual(len(manifest_paths), 744)
        self.assertEqual(len(set(manifest_paths)), 744)
        self.assertEqual(set(manifest_paths), actual)
        self.assertFalse((ROOT / ".gitmodules").exists())
        for folder, record in EXPECTED_SOURCE.items():
            with self.subTest(source=folder):
                self.assertEqual(sum(p.startswith(folder + "/") for p in actual), record["count"])

    def test_03_manifest_provenance_summary_reflects_physical_copy_not_submodule(self):
        s = self.inventory["summary"]
        self.assertEqual(s["original_mastry_files"], 552)
        self.assertEqual(s["original_journey_files"], 192)
        self.assertEqual(s["mastery_sha_verified"], 552)
        self.assertEqual(s["journey_sha_verified"], 192)
        self.assertNotIn("mastery_submodule_files", s)
        desc = self.inventory["verification"].lower()
        self.assertIn("physically copied", desc)
        self.assertNotIn("pinned submodule", desc)
        self.assertNotIn("not duplicated", desc)
        for record in EXPECTED_SOURCE.values():
            self.assertIn(record["commit"], self.inventory["verification"])

    def test_04_every_original_path_and_preservation_method_are_source_scoped(self):
        original_pairs = set()
        for entry in self.entries:
            with self.subTest(path=entry["preserved_path"]):
                self.assertEqual(entry["preservation_method"], "native_copy_sha_verified")
                relative = entry["original_path"]
                origin = entry["source"]
                parent = next((folder for folder, record in EXPECTED_SOURCE.items()
                               if record["source"] == origin), None)
                self.assertIsNotNone(parent)
                self.assertEqual(entry["preserved_path"], parent + "/" + relative)
                original_pairs.add((origin, relative))
                if parent == MASTER:
                    self.assertEqual(entry["source_commit"], EXPECTED_SOURCE[MASTER]["commit"])
        self.assertEqual(len(original_pairs), 744)
        # The original manifest has no per-entry Journey source_commit.
        # The independently checked Journey commit is pinned in the ledger/summary;
        # don't retroactively claim it was part of the original source manifest.


if __name__ == "__main__":
    unittest.main(verbosity=2)
