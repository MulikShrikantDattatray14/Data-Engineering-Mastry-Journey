#!/usr/bin/env python3
"""Read-only, original Git-blob-pinned historical Q21-Q25 Chinook SQL replay.

These source statements are distinct from the PNP P/A/X 205-question series.
Tests use disposable reviewer SQLite fixtures, NOT original Chinook database grading.
"""
import hashlib
import re
import sqlite3
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/"
    "1.Bosscoder Academy - foundational notes and Assignments/A. PNP easy"
)
PINS = {
    21: ("21.Playlists that are still empty.md", "350e4dde865f63a3cefd25c4ca03f81d43c501cc"),
    22: ("22.Composer coverage by genre.md", "bef0cc433a50d324c069ec0b7d678da3c0fb99c9"),
    23: ("23.Individuals vs business customers.md", "56b0073a7aeb4a327aaadcb41136941be599a698"),
    24: ("24.Track counts for every playlist — empty ones included.md", "0f9779fb11c8e673dfae9f1911f6b4b7da119cd3"),
    25: ("25.Monthly revenue across the full history.md", "f7f63f95b9d7ee390061f6d19477ee5e63b57e65"),
}

def original(n):
    name, pin = PINS[n]
    raw = (BASE / name).read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert sha == pin, (name, sha, pin)
    doc = raw.decode("utf-8")
    date = "2026-10-13" if n == 21 else "2026-10-15"
    assert "Solved (recorded): " + date in doc, name
    return doc

def sql(n, heading):
    document = original(n)
    section = re.search(r"^## " + re.escape(heading) + r"\s*\n(.*?)(?=^## |\Z)",
                        document, re.M | re.S)
    assert section, (n, heading, "missing heading")
    fenced = re.search(r"`{3}sql\s*\n(.*?)\n`{3}", section.group(1), re.S)
    assert fenced, (n, heading, "missing SQL block")
    return fenced.group(1).strip()

def replay(n, schema, inserts):
    con = sqlite3.connect(":memory:")
    try:
        con.executescript(schema)
        for command, rows in inserts:
            con.executemany(command, rows)
        learner = con.execute(sql(n, "My solution — SQLite")).fetchall()
        attributed = con.execute(sql(n, "Official solution")).fetchall()
        return learner, attributed
    finally:
        con.close()

PLAYLIST_SCHEMA = (
    "CREATE TABLE Playlist(PlaylistId INT,Name TEXT);"
    "CREATE TABLE PlaylistTrack(PlaylistId INT,TrackId INT);"
)
GENRE_SCHEMA = (
    "CREATE TABLE Genre(GenreId INT,Name TEXT);"
    "CREATE TABLE Track(TrackId INT,GenreId INT,Composer TEXT);"
)

class HistoricalChinookTwentyOneThroughTwentyFive(unittest.TestCase):
    def test_01_all_five_original_blobs_and_saved_sql_sections(self):
        for n in PINS:
            with self.subTest(question=n):
                document = original(n)
                self.assertIn("## Question and image", document)
                for section in ("My solution — SQLite", "My solution — SQL Server", "Official solution"):
                    self.assertTrue(sql(n, section))

    def test_02_q21_original_four_playlist_illustration(self):
        a, b = replay(21, PLAYLIST_SCHEMA, [
            ("INSERT INTO Playlist VALUES (?,?)", [(1,"Morning"),(2,"Quiet"),(3,"Evening"),(4,"Later")]),
            ("INSERT INTO PlaylistTrack VALUES (?,?)", [(1,101),(1,102),(3,103)]),
        ])
        self.assertEqual(a, [(2,"Quiet"),(4,"Later")])
        self.assertEqual(b, a)

    def test_03_q21_nullable_matched_trackid_is_a_false_empty_for_learner(self):
        a, b = replay(21, PLAYLIST_SCHEMA, [
            ("INSERT INTO Playlist VALUES (?,?)", [(1,"Has null association"),(2,"Actually empty"),(3,"Has track")]),
            ("INSERT INTO PlaylistTrack VALUES (?,?)", [(1,None),(3,42)]),
        ])
        self.assertEqual(a, [(1,"Has null association"),(2,"Actually empty")])
        self.assertEqual(b, [(2,"Actually empty")])

    def test_04_q22_original_composer_illustration(self):
        a, b = replay(22, GENRE_SCHEMA, [
            ("INSERT INTO Genre VALUES (?,?)", [(1,"Rock"),(2,"Jazz"),(3,"Pop"),(4,"Classical")]),
            ("INSERT INTO Track VALUES (?,?,?)", [(1,1,"A. Reed"),(2,1,None),(3,1,"B. Stone"),
                                                   (4,2,"C. Blue"),(5,2,"D. Brass"),(6,3,None)]),
        ])
        expected = [("Jazz",2,2,100.0),("Rock",3,2,66.7),("Pop",1,0,0.0)]
        self.assertEqual((a,b), (expected,expected))

    def test_05_q22_duplicate_genre_names_merge_in_attributed_answer(self):
        a, b = replay(22, GENRE_SCHEMA, [
            ("INSERT INTO Genre VALUES (?,?)", [(1,"Rock"),(2,"Rock")]),
            ("INSERT INTO Track VALUES (?,?,?)", [(10,1,"C"),(20,2,None)]),
        ])
        self.assertEqual(a, [("Rock",1,1,100.0),("Rock",1,0,0.0)])
        self.assertEqual(b, [("Rock",2,1,50.0)])

    def test_06_q22_empty_string_is_nonnull_composer(self):
        a, b = replay(22, GENRE_SCHEMA, [
            ("INSERT INTO Genre VALUES (?,?)", [(1,"Rock")]),
            ("INSERT INTO Track VALUES (?,?,?)", [(10,1,"")]),
        ])
        self.assertEqual((a,b), ([("Rock",1,1,100.0)], [("Rock",1,1,100.0)]))

    def test_07_q23_original_customer_type_illustration(self):
        a, b = replay(23, "CREATE TABLE Customer(CustomerId INT,Company TEXT);", [
            ("INSERT INTO Customer VALUES (?,?)", [(1,None),(2,"Acme"),(3,None),
                                                     (4,"Blue Ltd"),(5,"Cedar Inc")]),
        ])
        expected = [("Business",3),("Individual",2)]
        self.assertEqual((a,b),(expected,expected))

    def test_08_q23_blank_company_is_classed_as_business_not_missing(self):
        a, b = replay(23, "CREATE TABLE Customer(CustomerId INT,Company TEXT);", [
            ("INSERT INTO Customer VALUES (?,?)", [(1,None),(2,""),(3,"  "),(4,"Acme")]),
        ])
        self.assertEqual((a,b),([("Business",3),("Individual",1)],
                                [("Business",3),("Individual",1)]))

    def test_09_q24_original_duplicate_name_and_zero_count_illustration(self):
        a, b = replay(24, PLAYLIST_SCHEMA, [
            ("INSERT INTO Playlist VALUES (?,?)", [(1,"Focus"),(2,"Empty"),(3,"Focus"),(4,"More")]),
            ("INSERT INTO PlaylistTrack VALUES (?,?)", [(1,101),(1,102),(3,103),(4,104),(4,105)]),
        ])
        expected = [(1,"Focus",2),(4,"More",2),(3,"Focus",1),(2,"Empty",0)]
        self.assertEqual((a,b),(expected,expected))

    def test_10_q24_nullable_trackid_not_counted_even_with_membership(self):
        a, b = replay(24, PLAYLIST_SCHEMA, [
            ("INSERT INTO Playlist VALUES (?,?)", [(1,"Linked null"),(2,"Empty"),(3,"Repeated")]),
            ("INSERT INTO PlaylistTrack VALUES (?,?)", [(1,None),(3,8),(3,8)]),
        ])
        expected = [(3,"Repeated",2),(1,"Linked null",0),(2,"Empty",0)]
        self.assertEqual((a,b),(expected,expected))

    def test_11_q21_q24_consistent_empty_playlist_ids_on_valid_links(self):
        inserts = [
            ("INSERT INTO Playlist VALUES (?,?)", [(1,"One"),(2,"Empty"),(3,"Three"),(4,"Empty again")]),
            ("INSERT INTO PlaylistTrack VALUES (?,?)", [(1,7),(3,8),(3,9)]),
        ]
        a21, k21 = replay(21, PLAYLIST_SCHEMA, inserts)
        a24, k24 = replay(24, PLAYLIST_SCHEMA, inserts)
        self.assertEqual(a21,k21)
        self.assertEqual(a24,k24)
        self.assertEqual({id for id,name in a21}, {id for id,name,n in a24 if n == 0})

    def test_12_q25_original_multi_year_month_illustration(self):
        a, b = replay(25, "CREATE TABLE Invoice(InvoiceId INT, InvoiceDate TEXT, Total REAL);", [
            ("INSERT INTO Invoice VALUES (?,?,?)", [
                (1,"2023-01-10 10:00:00",10.25),(2,"2023-01-28 12:00:00",20.1),
                (3,"2023-02-05 09:00:00",5.0),(4,"2024-01-01 08:00:00",7.5),
                (5,"2024-01-20 14:00:00",2.5),(6,"2024-02-08 17:00:00",8.25),
            ]),
        ])
        expected = [("2023-01",30.35),("2023-02",5.0),("2024-01",10.0),("2024-02",8.25)]
        self.assertEqual((a,b),(expected,expected))

    def test_13_q25_missing_calendar_month_is_not_generated(self):
        a, b = replay(25, "CREATE TABLE Invoice(InvoiceId INT, InvoiceDate TEXT, Total REAL);", [
            ("INSERT INTO Invoice VALUES (?,?,?)", [(1,"2024-01-10",10.0),(2,"2024-03-02",5.0)]),
        ])
        self.assertEqual((a,b),([("2024-01",10.0),("2024-03",5.0)],
                                [("2024-01",10.0),("2024-03",5.0)]))

    def test_14_q25_invalid_or_missing_timestamp_groups_under_null_month(self):
        a, b = replay(25, "CREATE TABLE Invoice(InvoiceId INT, InvoiceDate TEXT, Total REAL);", [
            ("INSERT INTO Invoice VALUES (?,?,?)", [(1,"not-a-date",3.5),(2,None,1.5),
                                                     (3,"2024-04-05",None),(4,"2024-04-10",2.0)]),
        ])
        expected = [(None,5.0),("2024-04",2.0)]
        self.assertEqual((a,b),(expected,expected))

if __name__ == "__main__":
    unittest.main(verbosity=2)
