#!/usr/bin/env python3
"""Read-only, SHA-pinned audit of original Bosscoder SQL Sorting/Grouping teaching fences.

Replays literal archived SQLite examples on their printed sample setup and
checks separately authored SQLite boundaries. This is not Academy grading,
a SQL Server run, or an independently solved learner assignment.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
          "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/"
          "3. Sorting and Grouping/0. Foundation Notes.md")
SOURCE_BLOB = "11deb453f5249389014ac450fa1e3d6089b118dc"

# Original displayed result tables, manually and independently transcribed.
# The 13 entries match the 13 SELECT/CTE SQLite fences in their original order.
# SQL NULL is Python None; tuples preserve printed final ORDER BY where supplied.
DISPLAYED = [
    [(1, 1, 100), (4, 2, 100), (6, 3, 100), (7, 3, 100),
     (2, 1, 50), (3, 1, 20)],
    [(1, 100), (4, 100)],
    [(3, 20), (2, 50), (1, 100), (4, 100), (6, 100),
     (7, 100), (5, None), (8, None)],
    [(5, "pending"), (8, "pending"), (1, "paid"), (2, "paid"),
     (4, "paid"), (6, "paid"), (7, "paid"), (3, "returned")],
    [(1, 3, 170, 56.67), (2, 2, 100, 100),
     (3, 2, 200, 100), (4, 1, None, None)],
    [(1, 10, 2), (1, 20, 1), (2, 10, 2), (3, 10, 1),
     (3, 20, 1), (4, 20, 1)],
    [(1, 3, 3, 2), (2, 2, 2, 1), (3, 2, 2, 2), (4, 1, 1, 1)],
    [(6,)],
    [(1, 150), (3, 200)],
    [(1, "Ana", 150), (2, "Ben", 100), (3, "Ana", 200)],
    [(10, 1, "2020-06-01", 100), (10, 4, "2020-06-01", 100),
     (20, 6, "2020-06-03", 100)],
    [(1,), (3,)],
    [(3,)],
]


def archived_queries() -> list[str]:
    raw = SOURCE.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert blob == SOURCE_BLOB, f"Source chapter altered: {blob}"
    md = raw.decode("utf-8-sig")
    # Preserve original code verbatim; inventories distinguish source language.
    matches = re.findall(r"(?m)^"+chr(96)*3+r"(sql|sqlserver)[ \t]*\n(.*?)^"
                         +chr(96)*3+r"[ \t]*$", md, re.MULTILINE | re.DOTALL)
    assert len(matches) == 15, f"Expected 13 SQLite queries, one SQL Server TOP, one setup: {len(matches)}"
    assert [lang for lang, _ in matches].count("sqlserver") == 1
    assert [lang for lang, _ in matches].count("sql") == 14
    assert matches[2][0] == "sqlserver" and "SELECT TOP (2)" in matches[2][1]
    sqlite_fences = [code for lang, code in matches if lang == "sql"]
    assert len(sqlite_fences) == 14
    assert sqlite_fences[-1].lstrip().startswith("CREATE TABLE Customers")
    assert sqlite_fences[0].lstrip().startswith("SELECT order_id, customer_id, amount")
    assert "COUNT(DISTINCT product_id)" in sqlite_fences[6]
    assert "SELECT COUNT(*) AS unique_pairs" in sqlite_fences[7]
    assert "WITH first_dates AS" in sqlite_fences[10]
    assert "HAVING COUNT(DISTINCT P.product_id)" in sqlite_fences[11]
    return sqlite_fences


def verify_printed(fences: list[str]) -> None:
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(fences[13])  # Exact archived scratch CREATE and INSERT fence.
    for table, count in [("Customers", 4), ("Product", 2), ("Orders", 8)]:
        assert db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == count
    assert len(DISPLAYED) == 13
    for idx, (original, printed) in enumerate(zip(fences[:13], DISPLAYED), 1):
        actual = db.execute(original).fetchall()
        assert actual == printed, f"Original displayed-output contract {idx:02}: {actual!r} != {printed!r}"
    db.close()


def synthetic_database() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE Customers(customer_id INT PRIMARY KEY, name TEXT, region TEXT);
        INSERT INTO Customers VALUES (1,'Same','A'),(2,'Same','B'),
                                      (3,'Solo','C'),(4,'Solo','D');
        CREATE TABLE Product(product_id INT PRIMARY KEY);
        INSERT INTO Product VALUES (10),(20);
        CREATE TABLE Orders(order_id INT PRIMARY KEY, customer_id INT,
                            product_id INT, order_date TEXT, status TEXT, amount INT);
        INSERT INTO Orders VALUES
          (1,1,10,'2021-01-01','paid',10),
          (2,1,20,'2021-01-03','paid',10),
          (3,1,10,'2021-02-01','returned',NULL),
          (4,2,10,'2021-01-02','paid',10),
          (5,2,20,'2021-01-04','paid',10),
          (6,3,10,'2021-01-05','pending',NULL),
          (7,4,20,'2021-01-06','returned',100);
    """)
    return db


def verify_synthetic(fences: list[str]) -> None:
    db = synthetic_database()
    # S1. Same customer name must not merge identities; NULL-only aggregates
    # stay unknown, while COUNT(*) still counts the order row.
    assert db.execute(fences[4]).fetchall() == [
        (1,3,20,10), (2,2,20,10), (3,1,None,None), (4,1,100,100)]
    assert db.execute(fences[9]).fetchall() == [
        (1,"Same",20), (2,"Same",20)]

    # S2. Distinct customer/product pairs count 6 despite duplicate order
    # events. COUNT(*) and COUNT(DISTINCT product_id) measure different grains.
    assert db.execute(fences[7]).fetchall() == [(6,)]
    assert db.execute(fences[6]).fetchall() == [
        (1,3,3,2),(2,2,2,2),(3,1,1,1),(4,1,1,1)]
    # Separate classic text-concatenation collision: (1,23) vs (12,3).
    db.execute("DELETE FROM Orders")
    db.executemany("INSERT INTO Orders VALUES (?,?,?,?,?,?)", [
        (21,1,23,'2021-01-01','paid',1),
        (22,12,3,'2021-01-01','paid',1)])
    assert db.execute(fences[7]).fetchall() == [(2,)]
    db.close()

    db = synthetic_database()
    # S3. Full catalog coverage is 2 paid products, not two purchases.
    assert db.execute(fences[11]).fetchall() == [(1,), (2,)]
    # Customer 1 meets catalog coverage but has a returned event; only 2
    # satisfies the *separate* A-and-B-but-no-returns source contract.
    assert db.execute(fences[12]).fetchall() == [(2,)]
    # The optional empty-catalog caveat is NOT handled by this query:
    # it sees only paid-order groups; do not call this an all-customers proof.
    db.execute("DELETE FROM Product")
    assert db.execute(fences[11]).fetchall() == []
    assert db.execute("SELECT customer_id FROM Customers ORDER BY customer_id").fetchall() == [
        (1,), (2,), (3,), (4,)]
    db.close()

    # S4. A newly returned event MUST remain visible to HAVING even if its
    # amount is NULL; both otherwise qualifying customers now have returns.
    db = synthetic_database()
    db.execute("INSERT INTO Orders VALUES(8,2,10,'2021-03-01','returned',NULL)")
    assert db.execute(fences[12]).fetchall() == []
    db.close()

    # S5. First-date ties and identical calendar dates across products must
    # preserve every earliest row but never cross-join other product IDs.
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE Orders(order_id INT, customer_id INT, product_id INT,
                            order_date TEXT, status TEXT, amount INT);
        INSERT INTO Orders VALUES
         (11,1,10,'2026-01-01','paid',5),
         (12,2,10,'2026-01-01','paid',6),
         (13,3,10,'2026-01-02','paid',7),
         (14,4,20,'2026-01-01','paid',8),
         (15,5,20,'2026-02-02','paid',9);
    """)
    assert db.execute(fences[10]).fetchall() == [
        (10,11,'2026-01-01',5), (10,12,'2026-01-01',6),
        (20,14,'2026-01-01',8)]
    db.close()

    # S6. ORDER BY NULL-last flag and deterministic ties are tested with
    # the original SELECT, on a separately authored fixture.
    db = synthetic_database()
    assert db.execute(fences[2]).fetchall() == [
        (1,10),(2,10),(4,10),(5,10),(7,100),(3,None),(6,None)]
    assert db.execute(fences[1]).fetchall() == [(7,100),(1,10)]
    db.close()


def main() -> None:
    original = archived_queries()
    verify_printed(original)
    verify_synthetic(original)
    print("PASS: immutable original Bosscoder Sorting/Grouping foundation: "
          "15 language-tagged SQL fences inventoried (13 SQLite SELECT/CTE "
          "and one original scratch setup replayed, SQL Server TOP inventoried "
          "but NOT run); all 13 source-printed output contracts and six auditor-"
          "synthetic boundary groups passed under SQLite. No Academy official "
          "grading, platform datasets, SQL Server execution, new learner solutions "
          "or mastery.")


if __name__ == "__main__":
    main()
