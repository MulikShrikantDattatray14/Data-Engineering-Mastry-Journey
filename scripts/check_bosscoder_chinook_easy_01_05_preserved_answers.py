#!/usr/bin/env python3
"""Read-only replay of archived Chinook easy Q1-Q5; synthetic SQLite, not provider grading."""
import hashlib
import re
import sqlite3
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / ("99. Reference Materials/Original Mastery Snapshot/"
 "1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/A. PNP easy")
PINS = {
 1: ("1.Countries with at least ten invoices.md","7fc848a7bab1d47a84a867dfe9f8917cfcc6aa07"),
 2: ("2.Top five genres by revenue.md","1133845497f01802872fa7a7ff7797d158072080"),
 3: ("3.Track count per media type.md","d5cc9796cb5992812620af9ac7c9c7acf04c7949"),
 4: ("4.Premium-priced tracks.md","3fb69c2e889e17cdee9bfb021074c212b31108b3"),
 5: ("5.Distinct billing countries.md","a7d795aba6c97b8395ee6b70733d0dddabcd570e"),
}

def source(n):
    filename, want = PINS[n]
    raw = (BASE / filename).read_bytes()
    got = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    assert got == want, (filename, got)
    return raw.decode("utf-8")

def saved(n, kind):
    doc = source(n)
    block = re.search(r"^## "+re.escape(kind)+r"\s*\n(.*?)(?=^## |\Z)", doc, re.M|re.S)
    assert block, (n,kind,"missing section")
    match = re.search(r"\x60{3}sql\s*\n(.*?)\n\x60{3}",block.group(1),re.S)
    assert match, (n,kind,"missing SQL")
    return match.group(1).strip()

def replay(n, setup, rows):
    db = sqlite3.connect(":memory:")
    try:
        db.executescript(setup)
        for statement,data in rows:
            db.executemany(statement,data)
        mine = db.execute(saved(n,"My solution — SQLite")).fetchall()
        key = db.execute(saved(n,"Official solution")).fetchall()
        return mine,key
    finally:
        db.close()

class ChinookPreservedAnswers(unittest.TestCase):
    def test_01_source_integrity_and_recorded_status(self):
        for n in PINS:
            with self.subTest(n=n):
                self.assertIn("Solved (recorded): 2026-10-13",source(n))
                self.assertTrue(saved(n,"My solution — SQLite"))
                self.assertTrue(saved(n,"Official solution"))

    def test_02_q1_inclusive_threshold_and_null_country(self):
        rows = [(i,"USA") for i in range(1,12)] + [(i,"Brazil") for i in range(12,22)]
        rows += [(i,"Canada") for i in range(22,32)] + [(i,None) for i in range(32,42)]
        rows += [(42,"France"),(43,"France")]
        mine,key = replay(1,"CREATE TABLE Invoice(InvoiceId INT,BillingCountry TEXT);",
                          [("INSERT INTO Invoice VALUES (?,?)",rows)])
        self.assertEqual(mine,key)
        self.assertEqual(mine,[("USA",11),(None,10),("Brazil",10),("Canada",10)])

    def test_03_q2_illustrative_top_five_and_tie(self):
        mine,key = replay(2,"CREATE TABLE Genre(GenreId INT,Name TEXT);"
                          "CREATE TABLE Track(TrackId INT,GenreId INT);"
                          "CREATE TABLE InvoiceLine(InvoiceLineId INT,TrackId INT,UnitPrice REAL,Quantity INT);",[
                          ("INSERT INTO Genre VALUES (?,?)",[(1,"Rock"),(2,"Jazz"),(3,"Classical"),(4,"Pop"),(5,"Blues"),(6,"Metal")]),
                          ("INSERT INTO Track VALUES (?,?)",[(101,1),(102,1),(201,2),(301,3),(401,4),(501,5),(601,6)]),
                          ("INSERT INTO InvoiceLine VALUES (?,?,?,?)",[(1,101,1,2),(2,102,1,3),(3,201,2,2),(4,301,1.5,2),(5,401,1,3),(6,501,2,1),(7,601,1,1),(8,101,1,1)])])
        self.assertEqual(mine,key)
        self.assertEqual(mine,[("Rock",6.0),("Jazz",4.0),("Classical",3.0),("Pop",3.0),("Blues",2.0)])

    def test_04_q2_duplicate_genre_names_disagree_with_key(self):
        mine,key = replay(2,"CREATE TABLE Genre(GenreId INT,Name TEXT);"
                          "CREATE TABLE Track(TrackId INT,GenreId INT);"
                          "CREATE TABLE InvoiceLine(InvoiceLineId INT,TrackId INT,UnitPrice REAL,Quantity INT);",[
                          ("INSERT INTO Genre VALUES (?,?)",[(1,"Shared"),(2,"Shared"),(3,"Solo")]),
                          ("INSERT INTO Track VALUES (?,?)",[(1,1),(2,2),(3,3)]),
                          ("INSERT INTO InvoiceLine VALUES (?,?,?,?)",[(1,1,2,1),(2,2,3,1),(3,3,4,1)])])
        self.assertEqual(mine,[("Solo",4.0),("Shared",3.0),("Shared",2.0)])
        self.assertEqual(key,[("Shared",5.0),("Solo",4.0)])

    def test_05_q3_illustrative_media_type_counts(self):
        mine,key = replay(3,"CREATE TABLE MediaType(MediaTypeId INT,Name TEXT);"
                          "CREATE TABLE Track(TrackId INT,MediaTypeId INT);",[
                          ("INSERT INTO MediaType VALUES (?,?)",[(1,"MPEG audio"),(2,"AAC audio"),(3,"WAV audio"),(4,"MPEG video"),(5,"AIFF audio")]),
                          ("INSERT INTO Track VALUES (?,?)",[(1,1),(2,1),(3,1),(4,2),(5,2),(6,3),(7,4),(8,5)])])
        self.assertEqual(mine,key)
        self.assertEqual(mine,[("MPEG audio",3),("AAC audio",2),("AIFF audio",1),("MPEG video",1),("WAV audio",1)])

    def test_06_q3_duplicate_media_names_disagree_with_key(self):
        mine,key = replay(3,"CREATE TABLE MediaType(MediaTypeId INT,Name TEXT);"
                          "CREATE TABLE Track(TrackId INT,MediaTypeId INT);",[
                          ("INSERT INTO MediaType VALUES (?,?)",[(1,"Same"),(2,"Same"),(3,"Other"),(4,"Empty")]),
                          ("INSERT INTO Track VALUES (?,?)",[(1,1),(2,1),(3,2),(4,3)])])
        self.assertEqual(mine,[("Same",2),("Other",1),("Same",1)])
        self.assertEqual(key,[("Same",3),("Other",1)])

    def test_07_q4_strict_price_null_and_alphabetical_tie(self):
        mine,key = replay(4,"CREATE TABLE Track(TrackId INT,Name TEXT,UnitPrice REAL);",[
                          ("INSERT INTO Track VALUES (?,?,?)",[(1,"Standard",0.99),(2,"Zebra",1.99),
                          (3,"Alpha",1.99),(4,"Cinema",2.99),(5,"Budget",0.49),(6,"Unknown",None)])])
        self.assertEqual(mine,key)
        self.assertEqual(mine,[("Cinema",2.99),("Alpha",1.99),("Zebra",1.99)])

    def test_08_q5_distinct_countries_and_single_null_group(self):
        mine,key = replay(5,"CREATE TABLE Invoice(InvoiceId INT,BillingCountry TEXT);",[
                          ("INSERT INTO Invoice VALUES (?,?)",[(1,"USA"),(2,"Brazil"),(3,"USA"),
                          (4,"Canada"),(5,"Brazil"),(6,None),(7,None)])])
        self.assertEqual(mine,key)
        self.assertEqual(mine,[(None,),("Brazil",),("Canada",),("USA",)])

if __name__ == "__main__":
    unittest.main(verbosity=2)
