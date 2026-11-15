#!/usr/bin/env python3
"""Cross-index source navigation review. Not PDF, semantic, official-answer or learner signoff."""
from __future__ import annotations
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "99. Reference Materials" / "Original Mastery Snapshot"
FILES = {
 "python_pdf": ("02. Python Mastery/PDF-COVERAGE-INDEX.md", "b1fe67b410e4dcd46402a55fa03d00cd12a3c2ab"),
 "python_gap": ("02. Python Mastery/SOURCE-GAP-REGISTER.md", "86f7d411c864714379e622c48d203f2d9ae658fb"),
 "sql_index": ("01. SQL Mastery/PNP-PROBLEM-INDEX.md", "e407ada692fe6291d5f60692088d99afffbff128"),
 "sql_gap": ("01. SQL Mastery/SOURCE-GAP-REGISTER.md", "6c66133aa8d9eb471b867d261913cf895e9248c3"),
 "structured": ("99. Reference Materials/TOPIC-AND-PROBLEM-INDEX.json", "1461741b28cc909f42d96eadbd24bc2247f8304b"),
}
PDF_ROW = re.compile(r"^\|\s*(\d{1,2})\s*\|[^|\n]*\|\s*\[Open original note\]\(([^)\n]+)\)\s*\|", re.M)
GAP_ROW = re.compile(r"^\|\s*(\d{1,2})\s*\|[^|\n]*\|\s*\[Preserved source\]\(<([^>]+)>\)\s*\|\s*([^|\n]+)\|", re.M)
SQL_GAP = re.compile(r"^\|\s*(\d+\.\s*[^|\n]+?)\s*\|\s*(\d+)\s*\|\s*\[[^\]]+\]\((?:<([^>]+)>|([^)]+))\)", re.M)
SQL_ROW = re.compile(r"^\|\s*([PAX]\d{3})\s*\|\s*\[[^\]]+\]\(<([^>]+)>\)\s*\|\s*([^|\n]+)\|", re.M)
IDS = ({f"P{i:03d}" for i in range(1, 101)} | {f"A{i:03d}" for i in range(1, 101)}
       | {f"X{i:03d}" for i in range(1, 6)})

def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def contents(key):
    return (ROOT / FILES[key][0]).read_text(encoding="utf-8-sig")

def resolve(origin, link):
    path = (origin.parent / unquote(link.split("#", 1)[0])).resolve()
    assert path.is_relative_to(ROOT), (origin, link, "outside repo")
    return path

def index_sql():
    result = defaultdict(dict)
    group = None
    for line in contents("sql_index").splitlines():
        if line.startswith("## "):
            group = line[3:].strip()
        m = SQL_ROW.match(line)
        if m:
            assert group and re.match(r"^\d+\.", group), line
            assert m[1] not in result[group], (group, m[1])
            result[group][m[1]] = (m[2], m[3].strip())
    return result

class SourceToConceptIndexAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(contents("structured"))
        cls.prows = list(PDF_ROW.finditer(contents("python_pdf")))
        cls.grows = list(GAP_ROW.finditer(contents("python_gap")))
        cls.python_pdf = {int(m[1]): m[2] for m in cls.prows}
        cls.python_gap = {int(m[1]): (m[2], m[3].strip()) for m in cls.grows}
        cls.sql = index_sql()
        cls.sgap = {}
        for m in SQL_GAP.finditer(contents("sql_gap")):
            name = m[1].strip()
            assert name not in cls.sgap, name
            cls.sgap[name] = (int(m[2]), m[3] or m[4])

    def test_01_five_original_index_git_blobs_match_independent_fetch(self):
        for path, sha in FILES.values():
            with self.subTest(path=path):
                self.assertEqual(sha, blob(ROOT / path))

    def test_02_python_three_indexes_have_exactly_pages_5_to_80(self):
        reference = set(range(5, 81))
        pages = [e["pdf_page"] for e in self.data["python"]["indexed_lesson_pages"]]
        for rowlist in ([int(m[1]) for m in self.prows],
                        [int(m[1]) for m in self.grows], pages):
            self.assertEqual(76, len(rowlist))
            self.assertEqual(reference, set(rowlist))

    def test_03_python_crosswalk_76_original_paths_identical_and_present(self):
        records = {e["pdf_page"]: e for e in self.data["python"]["indexed_lesson_pages"]}
        found = set()
        for page in range(5, 81):
            with self.subTest(page=page):
                path = (ARCHIVE / records[page]["source_path"]).resolve()
                self.assertEqual(path, resolve(ROOT / FILES["python_pdf"][0], self.python_pdf[page]))
                self.assertEqual(path, resolve(ROOT / FILES["python_gap"][0], self.python_gap[page][0]))
                self.assertTrue(path.is_file())
                found.add(path)
        self.assertEqual(76, len(found))

    def test_04_python_explicit_direct_foundation_links_25_and_no_link_51(self):
        yes, no = [], []
        for page in range(5, 81):
            note = self.python_gap[page][1]
            if note == "—":
                no.append(page)
                continue
            m = re.fullmatch(r"\[Open quick note\]\(<([^>]+)>\)", note)
            self.assertIsNotNone(m, (page, note))
            dest = resolve(ROOT / FILES["python_gap"][0], m[1])
            self.assertTrue(dest.is_file(), (page, dest))
            self.assertTrue(dest.is_relative_to(ROOT / "02. Python Mastery"))
            self.assertEqual("0. Foundation Notes.md", dest.name)
            yes.append(page)
        self.assertEqual((25, 51), (len(yes), len(no)))

    def test_05_python_index_is_not_graded_learner_progress(self):
        self.assertTrue(all(e["status"] == "source_preserved; independent study not implied"
                            for e in self.data["python"]["indexed_lesson_pages"]))
        self.assertEqual(76, contents("python_pdf").count("Source indexed; no automatic completion credit"))

    def test_06_sql_sixteen_group_totals_reconcile_exactly_205(self):
        self.assertEqual(16, len(self.sgap))
        self.assertEqual(set(self.sgap), set(self.sql))
        self.assertEqual(205, sum(len(v) for v in self.sql.values()))
        for chapter, (count, _) in self.sgap.items():
            with self.subTest(chapter=chapter):
                self.assertEqual(count, len(self.sql[chapter]))

    def test_07_sql_all_205_source_links_ids_folders_and_git_blobs_match_json(self):
        entries = {e["id"]: e for e in self.data["sql"]["pnpmastery_questions"]}
        self.assertEqual(205, len(entries))
        found = set()
        for chapter, rows in self.sql.items():
            for ident, (link, _state) in rows.items():
                with self.subTest(ident=ident):
                    actual = resolve(ROOT / FILES["sql_index"][0], link)
                    source = (ARCHIVE / entries[ident]["source_path"]).resolve()
                    self.assertEqual(actual, source)
                    self.assertTrue(actual.is_file())
                    self.assertEqual(chapter, actual.parent.name)
                    self.assertEqual(entries[ident]["source_blob_sha"], blob(actual))
                    found.add(ident)
        self.assertEqual(IDS, found)

    def test_08_sql_sixteen_canonical_topic_links_exist_and_are_distinct(self):
        target_paths = set()
        for chapter, (_, href) in self.sgap.items():
            with self.subTest(chapter=chapter):
                dest = resolve(ROOT / FILES["sql_gap"][0], href)
                self.assertTrue(dest.is_file())
                self.assertTrue(dest.is_relative_to(ROOT / "01. SQL Mastery"))
                if chapter != "7. Extra Problems":
                    self.assertEqual("0. Foundation Notes.md", dest.name)
                target_paths.add(dest)
        self.assertEqual(16, len(target_paths))

    def test_09_bosscoder_seven_lecture_links_point_to_archived_notes(self):
        path = ROOT / "02. Python Mastery/BOSSCODER-COVERAGE-INDEX.md"
        original = path.read_text(encoding="utf-8")
        matches = re.findall(r"^\|\s*([1-7])\s*\|[^|\n]*\|\s*\[Notes\]\(([^)]+)\)"
                             r"\s*\|\s*\[Page-by-page audit\]\(([^)]+)\)", original, re.M)
        self.assertEqual(7, len(matches))
        self.assertEqual({str(i) for i in range(1, 8)}, {m[0] for m in matches})
        for _, notes, audit in matches:
            for link in (notes, audit):
                target = resolve(path, link)
                self.assertTrue(target.is_file())
                self.assertTrue(target.is_relative_to(
                    ROOT / "99. Reference Materials/Legacy Journey Snapshot"))

    def test_10_historical_source_matrix_does_not_claim_semantic_signoff(self):
        matrix = (ROOT / "99. Reference Materials/SOURCE-COVERAGE-MATRIX.md").read_text(encoding="utf-8")
        self.assertIn("51 still need detailed topic auditing", matrix)
        self.assertIn("A mapped primer isn't guaranteed", matrix)
        self.assertIn("Deep-source integration waits for supplied material", matrix)
        self.assertIn("not yet complete", matrix)
        print("PARTIAL: 76 Python page links, 25 direct primers, 51 without direct primer link.")
        print("PARTIAL: 205 SQL source IDs in 16 chapters, seven Bosscoder Python lecture links.")
        print("NO PDF/official-answer/independent-learner/mastery signoff.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
