#!/usr/bin/env python3
"""Read-only Q097/Q098 supplied PostgreSQL-key replay with immutable source pins.

Both extracted SQL statements run unchanged on SQLite. Original supplied examples
and independent edge fixtures are asserted; no native PostgreSQL, complete
commerce dataset, provider-graded answer, or learner mastery is claimed.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
SOURCE = {
    97: ("9. Windowing Functions/P097. What do customers buy on their second order.md",
         "9bf349ac0fe866697d481d3206ecd4598ec3c76e"),
    98: ("15. Analytics and Performance/"
         "P098. Category association rules support, confidence, lift.md",
         "526ba18093580b581cb8ef5442a2ce31b222f3fd"),
}
DDL = {
    97: ("Category(CategoryID INT, CategoryName TEXT)",
         "Products(ProductID INT, CategoryID INT, Sale_Price REAL)",
         "Orders(OrderID INT, CustomerID INT, OrderDate TEXT)",
         "OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT, Quantity INT)"),
    98: ("Category(CategoryID INT, CategoryName TEXT)",
         "Products(ProductID INT, CategoryID INT, Sale_Price REAL)",
         "OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT, Quantity INT)"),
}


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def supplied_sql(key, n):
    match = re.search(rf"^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)",
                      key, re.M | re.S)
    assert match, f"Missing original supplied Q{n} answer"
    sql = match.group(1).strip()
    assert sql.startswith("WITH ") and sql.endswith(";"), n
    assert "::" not in sql and "INTERVAL " not in sql, "Unexpected dialect drift"
    return sql


def execute(n, sql, records):
    with sqlite3.connect(":memory:") as db:
        for ddl in DDL[n]:
            db.execute("CREATE TABLE " + ddl)
        for table, rows in records.items():
            if rows:
                db.executemany("INSERT INTO " + table + " VALUES (" +
                               ",".join("?" for _ in rows[0]) + ")", rows)
        return db.execute(sql).fetchall()


def check(n, sql, records, expected, label):
    actual = execute(n, sql, records)
    assert actual == expected, (
        f"Q{n} {label}: got {actual!r}, expected {expected!r}")
    print(f"PASS Q{n} {label}: {len(actual)} rows")


def test_97(sql):
    check(97, sql, {
        "Category": [(1, "Audio"), (2, "Home")],
        "Products": [(101, 1, 5), (102, 2, 10)],
        "Orders": [(1, 10, "2026-01-01"), (2, 10, "2026-01-10"),
                   (3, 20, "2026-01-02")],
        "OrderDetails": [(1, 1, 101, 2), (2, 2, 102, 1), (3, 3, 101, 1)],
    }, [("Audio", "Home", 1, 50.0),
        ("Audio", "No second order", 1, 50.0)],
        "original 3-order first/second-category illustration")

    check(97, sql, {
        "Category": [(1, "Audio"), (2, "Home"), (3, "Other")],
        "Products": [(101, 1, 10), (102, 2, 10), (103, 3, 6)],
        "Orders": [(1, 10, "2026-01-01"), (2, 10, "2026-01-02"),
                   (3, 20, "2026-01-01"), (4, 20, "2026-01-02"),
                   (5, 30, "2026-01-01"), (6, 40, "2026-01-01"),
                   (7, 40, "2026-01-02")],
        "OrderDetails": [(1, 1, 101, 1), (2, 2, 102, 1),
                         (3, 3, 101, 1), (4, 3, 102, 1),
                         (5, 5, 999, 1)],
    }, [("Audio", "Home", 1, 50.0),
        ("Audio", "No line items", 1, 50.0),
        ("No line items", "No line items", 1, 100.0),
        ("Unmapped", "No second order", 1, 100.0)],
        "independent category-tie/no-lines/unmapped/second-order cases")
    check(97, sql, {"Category": [(1, "Audio")], "Orders": [],
                    "Products": [], "OrderDetails": []},
          [], "empty-customer-order boundary")


def test_98(sql):
    check(98, sql, {
        "Category": [(1, "Audio"), (2, "Home")],
        "Products": [(101, 1, 5), (102, 2, 10)],
        "OrderDetails": [(1, 1, 101, 1), (2, 1, 102, 1),
                         (3, 2, 101, 1), (4, 2, 102, 1),
                         (5, 3, 101, 1), (6, 4, 102, 1)],
    }, [("Audio", "Home", 2, 50.0, 66.67, 0.889),
        ("Home", "Audio", 2, 50.0, 66.67, 0.889)],
        "original 4-basket bidirectional association illustration")

    check(98, sql, {
        "Category": [(1, "Audio"), (2, "Home")],
        "Products": [(101, 1, 5), (102, 2, 10),
                     (103, 2, 12), (104, 99, 4)],
        "OrderDetails": [(1, 1, 101, 1), (2, 1, 101, 1),
                         (3, 1, 102, 1), (4, 1, 103, 1),
                         (5, 2, 101, 1), (6, 2, 102, 1),
                         (7, 3, 101, 1), (8, 4, 102, 1),
                         (9, 5, 101, 1), (10, 5, 104, 1)],
    }, [("Unmapped", "Audio", 1, 20.0, 100.0, 1.25),
        ("Audio", "Unmapped", 1, 20.0, 25.0, 1.25),
        ("Home", "Audio", 2, 40.0, 66.67, 0.833),
        ("Audio", "Home", 2, 40.0, 50.0, 0.833)],
        "independent deduped lines, unmapped category, directed rule ranking")
    check(98, sql, {"Category": [(1, "Audio")],
                    "Products": [(101, 1, 5)],
                    "OrderDetails": []},
          [], "empty-basket denominator boundary")


def main():
    assert git_blob(KEY) == KEY_SHA, "Archived PostgreSQL supplied key changed"
    key = KEY.read_text(encoding="utf-8")
    for n, (path, sha) in SOURCE.items():
        original = BASE / path
        assert git_blob(original) == sha, f"Q{n} archived Markdown changed"
        md = original.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{n:03d}.", "NOT SOLVED YET", "## Schema",
                       "### Sample input and expected output",
                       "## Official solution", "Pending"):
            assert marker in md, f"Missing Q{n} original marker: {marker}"
        sql = supplied_sql(key, n)
        {97: test_97, 98: test_98}[n](sql)
        print(f"INSPECTED Q{n}: archived statement/key unchanged; learner pending")
    print("PARTIAL ONLY: 2 original illustrations + 2 synthetic groups "
          "+ 2 empty-data boundaries. No provider grade, full-data/native "
          "PostgreSQL parity or independent learner mastery.")


if __name__ == "__main__":
    main()
