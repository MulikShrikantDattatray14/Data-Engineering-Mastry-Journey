#!/usr/bin/env python3
"""Audit the actual 205 PNP source IDs and links, not a fictional Q101-Q205.

This checks inventory existence and key coverage only: never solution correctness,
provider grading, learner independence, or all source-specific exercises.
"""
import hashlib
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "01. SQL Mastery/PNP-PROBLEM-INDEX.md"
KEY = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
              "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/"
              "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql")
INDEX_SHA = "e407ada692fe6291d5f60692088d99afffbff128"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"

def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def main():
    assert git_blob(INDEX) == INDEX_SHA, "Canonical PNP inventory changed"
    assert git_blob(KEY) == KEY_SHA, "Original 100-query supplied key changed"
    rows = re.findall(r"^\|\s*([PAX]\d{3})\s*\|\s*\[[^\]]+\]\(<([^>]+)>\)",
                      INDEX.read_text(encoding="utf-8"), re.M)
    expected = ({f"P{i:03d}" for i in range(1, 101)}
                | {f"A{i:03d}" for i in range(1, 101)}
                | {f"X{i:03d}" for i in range(1, 6)})
    actual = [question_id for question_id, _ in rows]
    assert len(rows) == len(expected) == 205
    assert len(set(actual)) == len(actual), "Duplicated PNP source ID"
    assert set(actual) == expected, f"Missing/extra original IDs: {set(actual)^expected}"
    for question_id, link in rows:
        path = (INDEX.parent / unquote(link)).resolve()
        assert path.is_relative_to(ROOT), f"Unsafe archive link: {question_id}"
        assert "Original Mastery Snapshot" in path.parts
        assert path.is_file(), f"Broken archived source link: {question_id} {path}"
        assert path.name.startswith(question_id + "."), f"Linked wrong ID: {question_id}"
        assert path.stat().st_size > 100, f"Suspiciously empty source: {question_id}"
    keys = [int(i) for i in re.findall(
        r"^-- Q(\d+)\.\s+", KEY.read_text(encoding="utf-8"), re.M)]
    assert len(keys) == len(set(keys)) == 100
    assert set(keys) == set(range(1, 101))
    print("PASS: 205 distinct source links resolve inside archived originals:"
          " P001-P100=100, A001-A100=100, X001-X005=5.")
    print("PASS: the pinned 100-query supplied PostgreSQL key holds precisely"
          " Q1-Q100; its Q identifiers map to the P-series, not nonexistent"
          " P101-P205 archive names.")
    print("OPEN: A and X task-specific output/official-key/learner checks remain"
          " separate. Indexed/source-exists is NOT statement-inspected,"
          " synthetic-tested, official-answer-verified or independently solved.")

if __name__ == "__main__":
    main()
