#!/usr/bin/env python3
"""Independent, read-only SQL-Joins foundation source/output audit.

Replays original archived teaching queries against their original sample setup.
Not a Bosscoder Academy graded exercise, SQL Server runtime, or learner solution.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
          "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/"
          "2. Joins/0. Foundation Notes.md")
SOURCE_BLOB = "b65b32c17a8c35a3130a3164799c307bc02dbf17"

# Reconstructed by the auditor from each immutable chapter's *displayed* Result
# table, in printed order. SQL NULL is represented by Python None.
# These are classroom teaching examples, not an authenticated answer key.
DISPLAYED = [
    [(1, "Ada"), (2, "Ben"), (3, "Cara"), (4, "Dev")],
    [(101, 1, 30, "paid", "2026-01-05"),
     (102, 1, 20, "pending", "2026-01-20"),
     (103, 2, 40, "paid", "2026-01-12"),
     (104, None, 10, "paid", "2026-02-01")],
    [("Ada", 101, 30), ("Ada", 102, 20), ("Ben", 103, 40)],
    [("Ada", 101, 30), ("Ada", 102, 20), ("Ben", 103, 40),
     ("Cara", None, None), ("Dev", None, None)],
    [("Ada", 2, 2), ("Ben", 1, 1), ("Cara", 1, 0), ("Dev", 1, 0)],
    [("Ada", 101), ("Ada", 102), ("Ben", 103), (None, 104)],
    [("Ada", 101), ("Ada", 102), ("Ben", 103),
     ("Cara", None), ("Dev", None), (None, 104)],
    [(1, "Ada", 101), (1, "Ada", 102), (2, "Ben", 103),
     (3, "Cara", None), (4, "Dev", None), (None, None, 104)],
    [("Ada", 101), ("Ben", 103), ("Cara", None), ("Dev", None)],
    [("Ada", 101), ("Ben", 103)],
    [(1, "Ada"), (2, "Ben")],
    [(3, "Cara"), (4, "Dev")],
    [(3, "Cara"), (4, "Dev")],
    [("Ada", "Online"), ("Ada", "Store"),
     ("Ben", "Online"), ("Ben", "Store")],
    [("Asha", None), ("Ben", "Asha"), ("Cara", "Asha"), ("Dara", "Ben")],
    [(101, 1, "Pen", "Gift"), (101, 2, "Mug", "Fragile"),
     (103, 1, "Book", "Express")],
    [(101, "2026-01-05", "Bronze"), (102, "2026-01-20", "Silver"),
     (103, "2026-01-12", "Gold"), (104, "2026-02-01", None)],
    [(1, 10, 1, 10), (1, 10, 2, 20),
     (2, 20, 1, 10), (2, 20, 2, 20)],
    [(101, 30, 30), (102, 0, 0), (103, 40, 40), (104, 0, 0)],
]

def verify_original():
    raw = SOURCE.read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert git_blob == SOURCE_BLOB, f"Archived Joins chapter unexpectedly changed: {git_blob}"
    fences = re.findall(r"(?m)^" + chr(96) * 3 +
                        r"sql[ \t]*\n(.*?)^" + chr(96) * 3 + r"[ \t]*$",
                        raw.decode("utf-8-sig"), re.DOTALL | re.MULTILINE)
    assert len(fences) == 20, f"Expected 19 displayed-query fences and 1 setup: {len(fences)}"
    assert len(DISPLAYED) == 19
    assert fences[0].strip().startswith("SELECT customer_id, customer_name")
    assert fences[5].strip().startswith("SELECT C.customer_name, O.order_id")
    assert "RIGHT JOIN" in fences[5] and "FULL OUTER JOIN" in fences[6]
    assert "UNION ALL" in fences[7]
    assert "NOT EXISTS" in fences[11]
    assert "WITH line_totals AS" in fences[18]
    assert fences[19].strip().startswith("CREATE TABLE Customers")

    # Do not count RIGHT/FULL as executed when the SQLite binary lacks them.
    assert sqlite3.sqlite_version_info >= (3, 39, 0), (
        "SQLite 3.39+ needed to replay original RIGHT and FULL JOIN fences"
    )
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(fences[19])  # Use untouched chapter DDL and literal inserts.
    for table, count in [("Customers", 4), ("Orders", 4),
                         ("Channels", 2), ("Employees", 4),
                         ("OrderLines", 3), ("LineNotes", 3),
                         ("CustomerTiers", 3), ("Payments", 3)]:
        got = db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert got == count, f"Original sample setup {table}: {got} != {count}"

    for idx, (query, printed) in enumerate(zip(fences[:19], DISPLAYED), 1):
        rows = db.execute(query.strip()).fetchall()
        assert rows == printed, f"Original Joins teaching fence {idx:02}: {rows!r} != {printed!r}"
    db.close()

def verify_synthetic():
    # Five auditor-authored counterexample groups, DISTINCT from the displayed
    # chapter rows; no source exercise or archived learner submission is changed.
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE P(pid INTEGER PRIMARY KEY);
        INSERT INTO P VALUES(1),(2),(3);
        CREATE TABLE C(cid INTEGER PRIMARY KEY,pid INTEGER,flag TEXT);
        INSERT INTO C VALUES(10,1,'paid'),(11,1,'pending'),(12,2,'pending'),(13,NULL,'paid');
        CREATE TABLE Lines(order_id INTEGER,line_no INTEGER,amount INTEGER);
        INSERT INTO Lines VALUES(1,1,10),(1,2,10);
        CREATE TABLE Notes(order_id INTEGER,line_no INTEGER,note TEXT);
        INSERT INTO Notes VALUES(1,1,'a'),(1,2,'b');
        CREATE TABLE Pay(order_id INTEGER,ref INTEGER,amount INTEGER);
        INSERT INTO Pay VALUES(1,1,10),(1,2,10);
        CREATE TABLE Events(pid INTEGER,event_date TEXT);
        INSERT INTO Events VALUES(1,'2026-01-20');
        CREATE TABLE Tiers(pid INTEGER,start_date TEXT,end_date TEXT,tier TEXT);
        INSERT INTO Tiers VALUES
        (1,'2026-01-01','2026-01-31','Bronze'),
        (1,'2026-01-15','2026-02-15','Silver');
    """)
    # S1. NULL inside the child subquery poisons NOT IN; correlated anti-join does not.
    assert db.execute("""
        SELECT pid FROM P WHERE pid NOT IN (SELECT pid FROM C)
    """).fetchall() == []
    assert db.execute("""
        SELECT pid FROM P WHERE NOT EXISTS (SELECT 1 FROM C WHERE C.pid=P.pid)
        ORDER BY pid
    """).fetchall() == [(3,)]

    # S2. The paid restriction's ON/WHERE location changes which parents survive.
    assert db.execute("""
        SELECT P.pid,C.cid FROM P LEFT JOIN C ON C.pid=P.pid AND C.flag='paid'
        ORDER BY P.pid,C.cid
    """).fetchall() == [(1,10),(2,None),(3,None)]
    assert db.execute("""
        SELECT P.pid,C.cid FROM P LEFT JOIN C ON C.pid=P.pid WHERE C.flag='paid'
        ORDER BY P.pid,C.cid
    """).fetchall() == [(1,10)]

    # S3. Composite join keys avoid a false two-by-two pairing.
    assert db.execute("""
        SELECT COUNT(*) FROM Lines L JOIN Notes N ON L.order_id=N.order_id
    """).fetchone() == (4,)
    assert db.execute("""
        SELECT COUNT(*) FROM Lines L JOIN Notes N
        ON L.order_id=N.order_id AND L.line_no=N.line_no
    """).fetchone() == (2,)

    # S4. Two overlapping tiers create two matches for one event (policy undefined).
    assert db.execute("""
        SELECT tier FROM Events E JOIN Tiers T
          ON E.pid=T.pid AND E.event_date>=T.start_date
         AND E.event_date<=T.end_date ORDER BY tier
    """).fetchall() == [("Bronze",),("Silver",)]

    # S5. Two child tables create 2x2 multiplication; DISTINCT loses valid repeats.
    assert db.execute("""
        SELECT COUNT(*),SUM(L.amount),SUM(DISTINCT L.amount)
        FROM Lines L JOIN Pay P ON L.order_id=P.order_id
    """).fetchone() == (4,40,10)
    assert db.execute("""
        SELECT SUM(amount) FROM Lines
    """).fetchone() == (20,)
    db.close()

def main():
    verify_original()
    verify_synthetic()
    print("PASS: original Bosscoder Joins foundation source blob unchanged; "
          "20 SQL fences inventoried, 19 unmodified sample queries replayed "
          "and matched against 19 individually transcribed displayed result "
          "tables with original scratch setup (including SQLite 3.39+ RIGHT/FULL); "
          "five separately synthetic boundary groups passed. "
          "NO official Academy grading, SQL Server runtime, original platform "
          "datasets, new learner submissions, or mastery.")

if __name__ == "__main__":
    main()
