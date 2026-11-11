#!/usr/bin/env python3
"""Scoped, read-only source audit of PNP Q065-Q072.

Pins all eight immutable question records and the supplied PostgreSQL answer
archive. Executes exact supplied-key SQL for Q070-Q072 on six separately
asserted SQLite fixtures (three archived illustrative and three independent
synthetic groups). Q065-Q069 are STATEMENT INSPECTED ONLY in this script.
SQLite outputs are neither native PostgreSQL parity nor provider grading,
original full-data results, or evidence of learner-independent completion.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
SOURCES = {
    65: ("13. Gaps and Islands/P065. Longest run of consecutive months with an order.md", "a7b40c93d66c2fa77e188081f41b91b91a581155"),
    66: ("12. Dates and Time/P066. How fast do customers come back for a second order.md", "6f9872c8f72dd666be3e356318aec2175156e6ce"),
    67: ("15. Analytics and Performance/P067. Median vs mean order value by payment type.md", "590aa7f85667f81d124c0f9248b1c8721f009868"),
    68: ("9. Windowing Functions/P068. Second-highest spender in each state, counting delivered orders on.md", "a80b0bf2147dc7d8e92612541b34a80b9017b154"),
    69: ("12. Dates and Time/P069. Customers whose spend grew every active quarter of the latest year.md", "e9cacb210d57d3218b6ad98ca8f2a5b9343e4f8a"),
    70: ("2. Joins/P070. Sub-categories most often bought together.md", "17ae031a4000d0974a5c1043c684732cc8ae136a"),
    71: ("14. Data Quality and Deduplication/P071. Deduplicate customer accounts by email.md", "d2cae3c82004124d3fe445ea5b65eb664b0ff952"),
    72: ("14. Data Quality and Deduplication/P072. Same product on several lines of one order split or duplicate.md", "62250373aafa5402aa879a731f4fafe40165a7f4"),
}

SCHEMAS = {
    70: ("Products(ProductID INT,Sub_Category TEXT)", "OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT)"),
    71: ("Customers(CustomerID INT,Email TEXT,DateEntered TEXT)",),
    72: ("OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT,Quantity INT,SupplierID INT)",),
}
# Rows independently transcribed from the preserved Markdown, not copied
# from the PostgreSQL supplied key. Each has an additional synthetic fixture.
ILLUSTRATIVE = {
    70: (
        {"Products": [(1,"Tea"),(2,"Snacks"),(3,"Coffee")],
         "OrderDetails": [(1,10,1),(2,10,2),(3,11,1),(4,11,3),(5,12,1),(6,12,2)]},
        [("Snacks","Tea",2),("Coffee","Tea",1)],
    ),
    71: (
        {"Customers": [(1," ASHA@example.com ","2026-01-01"),(2,"asha@example.com","2026-01-05"),
                       (3,"ASHA@EXAMPLE.COM","2026-01-01"),(4,None,"2026-01-02")]},
        [("asha@example.com",1,2,"2026-01-01","2026-01-05"),
         ("asha@example.com",1,3,"2026-01-01","2026-01-01")],
    ),
    72: (
        {"OrderDetails": [(1,10,101,2,7),(2,10,101,3,7),(3,20,102,1,7),(4,20,102,4,8)]},
        [(1,10,101,2,7,1,2,5,"Same supplier: consolidate","keep, set quantity to total"),
         (2,10,101,3,7,2,2,5,"Same supplier: consolidate","remove"),
         (3,20,102,1,7,1,2,5,"Split across suppliers","keep"),
         (4,20,102,4,8,2,2,5,"Split across suppliers","keep")],
    ),
}
SYNTHETIC = {
    70: (
        {"Products": [(1,"A"),(2,"B"),(3,"C"),(4,""),(5,None)],
         "OrderDetails": [(1,1,1),(2,1,1),(3,1,2),(4,2,1),(5,2,3),
                          (6,3,4),(7,3,2),(8,4,5),(9,4,1)]},
        [("","B",1),("A","B",1),("A","C",1)],
    ),
    71: (
        {"Customers": [(9,"X@X.COM",None),(7,"x@x.com","2020-05-01"),
                       (8," x@x.com ",None),(10,"   ","2020-01-01"),(11,None,"2020-01-01")]},
        [("x@x.com",7,8,"2020-05-01",None),("x@x.com",7,9,"2020-05-01",None)],
    ),
    72: (
        {"OrderDetails": [(1,1,10,3,None),(2,1,10,4,7),
                          (3,2,20,5,None),(4,2,20,6,None),(5,3,30,9,7)]},
        [(1,1,10,3,None,1,2,7,"Same supplier: consolidate","keep, set quantity to total"),
         (2,1,10,4,7,2,2,7,"Same supplier: consolidate","remove"),
         (3,2,20,5,None,1,2,11,"Same supplier: consolidate","keep, set quantity to total"),
         (4,2,20,6,None,2,2,11,"Same supplier: consolidate","remove")],
    ),
}

def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def extract_sql(num, key):
    match = re.search(rf"(?ms)^-- Q{num}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key)
    assert match, f"Q{num}: missing supplied-key excerpt"
    query = match.group(1).strip()
    assert query.startswith("WITH "), f"Q{num}: unexpected supplied-key structure"
    return query

def run_fixture(num, sql, data, expected, label):
    db = sqlite3.connect(":memory:")
    try:
        for schema in SCHEMAS[num]:
            db.execute("CREATE TABLE " + schema)
        for table, rows in data.items():
            if rows:
                slots = ",".join("?" for _ in rows[0])
                db.executemany(f"INSERT INTO {table} VALUES ({slots})", rows)
        actual = db.execute(sql).fetchall()
        assert actual == expected, f"Q{num} {label}: {actual!r} != {expected!r}"
    finally:
        db.close()

def main():
    assert sqlite3.sqlite_version_info >= (3, 39, 0), "SQLite window support required"
    assert git_blob(KEY) == KEY_SHA, "supplied PostgreSQL key drift"
    key = KEY.read_text(encoding="utf-8")
    for num, (relative, sha) in SOURCES.items():
        src = BASE / relative
        assert git_blob(src) == sha, f"Q{num}: immutable original Markdown drift"
        txt = src.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{num:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output", "## Schema",
                       "## Official solution", "Pending"):
            assert marker in txt, f"Q{num}: missing source marker {marker}"
        sql = extract_sql(num, key)
        if num in SCHEMAS:
            for label, fixtures in (("archived illustration", ILLUSTRATIVE),
                                    ("independent synthetic", SYNTHETIC)):
                run_fixture(num, sql, *fixtures[num], label)
    print("PASS: all 8 archived Q065-Q072 question/key blob pins; Q070-Q072 exact "
          "supplied-key SQL: 3 illustrative + 3 independent synthetic SQLite fixtures. "
          "Q065-Q069 statement inspection only; no native PG/full data/provider grade/learner solves.")

if __name__ == "__main__":
    main()
