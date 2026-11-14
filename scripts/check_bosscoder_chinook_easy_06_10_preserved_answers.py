#!/usr/bin/env python3
"""Source-pinned Chinook easy Q6-Q10 answer-pair checks; only synthetic SQLite."""
import hashlib
import re
import sqlite3
import unittest
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/"
    "1.Bosscoder Academy - foundational notes and Assignments/A. PNP easy"
)
PINS = {
    6: ("6.Customers based in Brazil.md", "16b7268f92facff08a1f7d705f49b15bc211b99e"),
    7: ("7.Five longest tracks.md", "21e281a09d308a7de43afe8c1d601bd090420b7c"),
    8: ("8.Employees hired after 2003.md", "8c92f0421a4bac472754c85f52181a358f3c9a92"),
    9: ("9.Rock or Jazz genres.md", "e7b3d7c33fe11fadf6b966aa1106d1480c2a7796"),
    10: ("10.List tracks with their genre name.md", "e616954b430fb1988bbe52ca62781b3a6832edcb"),
}

def original(n):
    filename, pin = PINS[n]
    raw = (BASE / filename).read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert sha == pin, (filename, sha)
    doc = raw.decode("utf-8")
    assert "Solved (recorded): 2026-10-13" in doc, filename
    return doc

def archived_sql(n, section):
    doc = original(n)
    match = re.search(r"^## " + re.escape(section) + r"\s*\n(.*?)(?=^## |\Z)", doc, re.M | re.S)
    assert match, (n, section, "missing heading")
    fence = re.search(r"\x60{3}sql\s*\n(.*?)\n\x60{3}", match.group(1), re.S)
    assert fence, (n, section, "missing SQL fence")
    return fence.group(1).strip()

def replay(n, setup, inserts):
    db = sqlite3.connect(":memory:")
    try:
        db.executescript(setup)
        for sql, rows in inserts:
            db.executemany(sql, rows)
        mine = db.execute(archived_sql(n, "My solution — SQLite")).fetchall()
        key = db.execute(archived_sql(n, "Official solution")).fetchall()
        return mine, key
    finally:
        db.close()

class ChinookEasySixThroughTen(unittest.TestCase):
    def test_01_exact_source_pins_and_recorded_solution_sections(self):
        for n in PINS:
            with self.subTest(question=n):
                self.assertIn("## Question and image", original(n))
                self.assertTrue(archived_sql(n, "My solution — SQLite"))
                self.assertTrue(archived_sql(n, "My solution — SQL Server"))
                self.assertTrue(archived_sql(n, "Official solution"))

    def test_02_q6_brazil_exact_country_filter_and_name_order(self):
        rows = [
            (1, "Bruno", "Silva", "Brazil", "b@example.org"),
            (2, "Ana", "Silva", "Brazil", "a@example.org"),
            (3, "Joao", "Almeida", "Brazil", "j@example.org"),
            (4, "Luis", "Almeida", "Brazil", "l@example.org"),
            (5, "Mia", "Jones", "brazil", "m@example.org"),
            (6, "Paul", "Jones", None, "p@example.org"),
        ]
        mine, key = replay(6, "CREATE TABLE Customer(CustomerId INT, FirstName TEXT, LastName TEXT, Country TEXT, Email TEXT);", [
            ("INSERT INTO Customer VALUES (?,?,?,?,?)", rows)])
        expected = [("Joao", "Almeida", "j@example.org"), ("Luis", "Almeida", "l@example.org"),
                    ("Ana", "Silva", "a@example.org"), ("Bruno", "Silva", "b@example.org")]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)

    def test_03_q6_equal_first_last_names_have_no_email_tiebreak(self):
        rows = [(1, "Ana", "Silva", "Brazil", "z@x"),
                (2, "Ana", "Silva", "Brazil", "a@x"),
                (3, "Bruno", "Silva", "Brazil", "b@x")]
        mine, key = replay(6, "CREATE TABLE Customer(CustomerId INT, FirstName TEXT, LastName TEXT, Country TEXT, Email TEXT);", [
            ("INSERT INTO Customer VALUES (?,?,?,?,?)", rows)])
        self.assertEqual(mine, key)
        self.assertEqual(Counter(mine), Counter([("Ana", "Silva", "z@x"), ("Ana", "Silva", "a@x"), ("Bruno", "Silva", "b@x")]))
        # Exact order of identical name keys is not guaranteed by the archived queries.

    def test_04_q7_five_longest_and_fractional_seconds(self):
        rows = [(1, "Alpha", 150000), (2, "Echo", 500500), (3, "Beta", 120000),
                (4, "Gamma", 400000), (5, "Delta", 600125), (6, "Foxtrot", 300000),
                (7, "Grove", 200000)]
        mine, key = replay(7, "CREATE TABLE Track(TrackId INT, Name TEXT, Milliseconds INT);", [
            ("INSERT INTO Track VALUES (?,?,?)", rows)])
        expected = [("Delta", 600125, 600.125), ("Echo", 500500, 500.5),
                    ("Gamma", 400000, 400.0), ("Foxtrot", 300000, 300.0), ("Grove", 200000, 200.0)]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)

    def test_05_q7_fifth_place_tie_has_no_secondary_sort(self):
        rows = [(1, "A", 9000), (2, "B", 8000), (3, "C", 7000), (4, "D", 6000),
                (5, "E", 5000), (6, "F", 5000), (7, "Missing", None)]
        mine, key = replay(7, "CREATE TABLE Track(TrackId INT, Name TEXT, Milliseconds INT);", [
            ("INSERT INTO Track VALUES (?,?,?)", rows)])
        self.assertEqual(mine, key)
        self.assertEqual(len(mine), 5)
        self.assertEqual([x[0] for x in mine[:4]], ["A", "B", "C", "D"])
        self.assertIn(mine[4], [("E", 5000, 5.0), ("F", 5000, 5.0)])
        # The source has no secondary key to select one of tied fifth-place tracks.

    def test_06_q8_inclusive_text_datetime_threshold_and_null(self):
        rows = [(1, "Eva", "Chen", "2005-06-15 09:00:00"),
                (2, "Omar", "Lee", "2003-12-31 23:59:59"),
                (3, "Jane", "Adams", "2004-01-01 00:00:00"),
                (4, "Lina", "Young", "2004-01-01 00:00:01"),
                (5, "No", "Date", None)]
        mine, key = replay(8, "CREATE TABLE Employee(EmployeeId INT, FirstName TEXT, LastName TEXT, HireDate TEXT);", [
            ("INSERT INTO Employee VALUES (?,?,?,?)", rows)])
        expected = [("Jane", "Adams", "2004-01-01 00:00:00"),
                    ("Lina", "Young", "2004-01-01 00:00:01"),
                    ("Eva", "Chen", "2005-06-15 09:00:00")]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)

    def test_07_q9_in_values_case_and_null_behavior(self):
        rows = [(1, "Rock"), (2, "Jazz"), (3, "Pop"), (4, "ROCK"), (5, None), (6, "Jazz")]
        mine, key = replay(9, "CREATE TABLE Genre(GenreId INT, Name TEXT);", [
            ("INSERT INTO Genre VALUES (?,?)", rows)])
        expected = [(2, "Jazz"), (6, "Jazz"), (1, "Rock")]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)

    def test_08_q10_source_example_join_count_and_zero_genre(self):
        mine, key = replay(10, "CREATE TABLE Genre(GenreId INT, Name TEXT);"
                           "CREATE TABLE Track(TrackId INT, Name TEXT, GenreId INT);", [
            ("INSERT INTO Genre VALUES (?,?)", [(1, "Rock"), (2, "Jazz"), (3, "Classical"), (4, "Pop")]),
            ("INSERT INTO Track VALUES (?,?,?)", [(1, "Stone", 1), (2, "Cliff", 1),
             (3, "Blue", 2), (4, "Swing", 2), (5, "Sonata", 3), (6, "Orphan", 999), (7, "No Genre", None)])])
        expected = [("Jazz", 2), ("Rock", 2), ("Classical", 1)]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)

    def test_09_q10_distinct_ids_with_same_display_name_remain_separate(self):
        mine, key = replay(10, "CREATE TABLE Genre(GenreId INT, Name TEXT);"
                           "CREATE TABLE Track(TrackId INT, Name TEXT, GenreId INT);", [
            ("INSERT INTO Genre VALUES (?,?)", [(1, "Shared"), (2, "Shared"), (3, "Solo"), (4, "Empty")]),
            ("INSERT INTO Track VALUES (?,?,?)", [(1, "a", 1), (2, "b", 1), (3, "c", 2), (4, "d", 3),
             (5, "e", 3), (6, "f", 3)])])
        expected = [("Solo", 3), ("Shared", 2), ("Shared", 1)]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)
        # Key-granular groups can share a displayed label; unlike Q2 this pair agrees.

if __name__ == "__main__":
    unittest.main(verbosity=2)
