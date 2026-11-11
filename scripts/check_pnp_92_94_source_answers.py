#!/usr/bin/env python3
"""Bounded read-only original-key replay for PNP Q092 and Q094 (SQLite).

Source SHA pins protect the archived questions and supplied PostgreSQL key.
SQLite compatibility: Q092's one ::text cast becomes CAST(... AS TEXT);
Q094's CONCAT() is supplied as a 2-argument UDF (the key uses non-NULL ID).
All other relational SQL is extracted and executed unchanged. No provider grade,
native PostgreSQL/full-dataset parity or independent learner solve is claimed.
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
SOURCES = {
    92: ("14. Data Quality and Deduplication/"
         "P092. How duplicate accounts distort the repeat-customer rate.md",
         "314f8e6cf95d3a70b21e841f799942bbc27fe587"),
    94: ("15. Analytics and Performance/"
         "P094. Supplier concentration per category (HHI).md",
         "8e62e472a3e5307405d9c3491a15ed5b630e780e"),
}
DDL = {
    92: ("Customers(CustomerID INT, Email TEXT)", "Orders(OrderID INT, CustomerID INT)"),
    94: ("Category(CategoryID INT, CategoryName TEXT)",
         "Products(ProductID INT, CategoryID INT, Sale_Price REAL)",
         "Suppliers(SupplierID INT, CompanyName TEXT)",
         "OrderDetails(OrderDetailID INT, ProductID INT, Quantity INT, SupplierID INT)"),
}

def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def extract(key, n):
    found = re.search(rf"^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)",
                      key, re.M | re.S)
    assert found, f"Q{n} missing supplied SQL"
    result = found.group(1).strip()
    assert result.startswith("WITH ") and result.endswith(";"), n
    return result

def adapt(n, sql):
    if n == 92:
        old = "c.CustomerID::text"
        assert sql.count(old) == 1, "Q092 cast drift"
        sql = sql.replace(old, "CAST(c.CustomerID AS TEXT)")
    if n == 94:
        assert sql.count("CONCAT('Unknown supplier ', cs.SupplierID)") == 1
    assert "::" not in sql, "PostgreSQL cast drift"
    return sql

def run(n, sql, records):
    db = sqlite3.connect(":memory:")
    db.create_function("CONCAT", 2, lambda a, b: str(a) + str(b))
    try:
        for ddl in DDL[n]:
            db.execute("CREATE TABLE " + ddl)
        for table, rows in records.items():
            if rows:
                db.executemany("INSERT INTO " + table + " VALUES (" +
                               ",".join("?" for _ in rows[0]) + ")", rows)
        return db.execute(sql).fetchall()
    finally:
        db.close()

def check(n, sql, rows, expected, label):
    actual = run(n, sql, rows)
    assert actual == expected, f"Q{n} {label}: got {actual!r}; expected {expected!r}"
    print(f"PASS Q{n} {label}: {len(actual)} rows")

def verify_92(sql):
    check(92, sql, {
        "Customers": [(10, " ASHA@example.com "), (20, "asha@example.com"),
                      (30, "bela@example.com")],
        "Orders": [(1, 10), (2, 20), (3, 30)],
    }, [("Raw CustomerID", 3, 0, 0., 3),
        ("Merged by email", 2, 1, 50., 3)],
        "original case-and-trim 3-order illustration")
    check(92, sql, {
        "Customers": [(10, " x@EXAMPLE.COM "), (20, "X@example.com"),
                      (30, "   "), (40, None), (50, "unused@abc.com")],
        "Orders": [(1, 10), (2, 10), (3, 20), (4, 30), (5, 40)],
    }, [("Raw CustomerID", 4, 1, 25., 5),
        ("Merged by email", 3, 1, 33.33, 5)],
        "independent blank/NULL/unordered accounts and no-orders customer")
    # The full source says one row PER method; the supplied query emits neither
    # method for zero orders. This check records the counterexample, not a pass.
    empty = run(92, sql, {"Customers": [(10, "x@y.com")], "Orders": []})
    assert empty == [], f"Q092 empty-orders regression changed: {empty!r}"
    print("KNOWN Q092 conditional completeness failure: no Orders -> 0 method rows, "
          "where source requests both methods; NULL rates require policy.")

def verify_94(sql):
    check(94, sql, {
        "Category": [(1, "Audio")],
        "Products": [(101, 1, 25)],
        "Suppliers": [(7, "Alpha"), (8, "Beta")],
        "OrderDetails": [(1, 101, 3, 7), (2, 101, 1, 8)],
    }, [("Audio", 2, "Alpha", 75., 6250., "Highly concentrated")],
        "original 75/25 HHI illustration")
    check(94, sql, {
        "Category": [(1, "Audio"), (2, "Home")],
        "Products": [(101, 1, 10), (102, 2, 15), (103, 99, 5)],
        "Suppliers": [(5, "Listed")],
        "OrderDetails": [(1, 101, 1, 9), (2, 101, 1, 5),
                         (3, 102, 2, 7), (4, 103, 4, 11)],
    }, [("Home", 1, "Unknown supplier 7", 100., 10000., "Single source"),
        ("Unmapped", 1, "Unknown supplier 11", 100., 10000., "Single source"),
        ("Audio", 2, "Listed", 50., 5000., "Highly concentrated")],
        "independent unmapped category, missing supplier and equal-value tie")
    zero = run(94, sql, {
        "Category": [(1, "Audio")], "Products": [(101, 1, 0)],
        "Suppliers": [(5, "Listed")],
        "OrderDetails": [(1, 101, 1, 5), (2, 101, 1, 9)],
    })
    assert zero == [("Audio", 2, "Listed", None, None, "Unconcentrated")], zero
    print("KNOWN Q094 undefined zero-denominator semantics: two suppliers "
          "with zero total value yield NULL share/HHI and 'Unconcentrated'; "
          "business definition requires clarification, not an official failure.")

def main():
    assert git_blob(KEY) == KEY_SHA, "Supplied PostgreSQL source-key blob drift"
    key = KEY.read_text(encoding="utf-8")
    for n, (path, sha) in SOURCES.items():
        original = BASE / path
        assert git_blob(original) == sha, f"Original PNP Q{n} blob drift"
        content = original.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{n:03d}.", "NOT SOLVED YET", "## Schema",
                       "### Sample input and expected output",
                       "## Official solution", "Pending"):
            assert marker in content, f"Q{n}: source marker {marker!r} absent"
        print(f"INSPECTED Q{n}: unchanged archived source and pending learner")
        sql = adapt(n, extract(key, n))
        {92: verify_92, 94: verify_94}[n](sql)
    print("PARTIAL ONLY: 2 original illustrative outputs + 2 synthetic "
          "fixture groups passed; 2 conditional diagnostics recorded. "
          "No provider answer verification, native PG parity or learner mastery.")

if __name__ == "__main__":
    main()
