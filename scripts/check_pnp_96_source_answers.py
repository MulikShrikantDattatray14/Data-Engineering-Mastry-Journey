#!/usr/bin/env python3
"""Q096 immutable-source/supplier-key row-equivalence audit; SQLite only."""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCE = BASE / ("15. Analytics and Performance/"
                 "P096. Make a slow order report sargable and index it.md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
PINS = {SOURCE: "bcee556369e0af953521ec9ec1b8be96d71986e2",
        KEY: "7912c8e676621c513e0b635a40c6ee299404676e"}

def queries():
    for path, expected in PINS.items():
        data = path.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert blob == expected, f"Original archived file drifted: {path}"
    md = SOURCE.read_text(encoding="utf-8")
    for token in ("# PNP Q096.", "NOT SOLVED YET", "## Schema",
                  "### Sample input and expected output", "## Official solution", "Pending"):
        assert token in md, token
    match = re.search(r"\x60{3}sql\s*\n(.*?)\x60{3}", md, re.S)
    assert match, "Missing original non-sargable SQL"
    slow = match.group(1).strip()
    for pg, lite in (
        ("TO_CHAR(o.OrderDate, 'YYYY-MM')", "STRFTIME('%Y-%m', o.OrderDate)"),
        ("TO_CHAR(MAX(OrderDate), 'YYYY-MM')", "STRFTIME('%Y-%m', MAX(OrderDate))")
    ):
        assert slow.count(pg) == 1, pg
        slow = slow.replace(pg, lite)
    key = KEY.read_text(encoding="utf-8")
    match = re.search(r"^-- Q96\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key, re.M | re.S)
    assert match, "Missing original Q096 answer"
    supplied = match.group(1).strip()
    assert supplied.startswith("WITH month_bounds AS") and supplied.endswith(";")
    for pg, lite in (
        ("DATE_TRUNC('month', MAX(o.OrderDate))::date",
         "DATE(MAX(o.OrderDate), 'start of month')"),
        ("(DATE_TRUNC('month', MAX(o.OrderDate)) + INTERVAL '1 month')::date",
         "DATE(MAX(o.OrderDate), 'start of month', '+1 month')")
    ):
        assert supplied.count(pg) == 1, pg
        supplied = supplied.replace(pg, lite)
    assert not any(s in supplied for s in ("DATE_TRUNC", "::", "INTERVAL "))
    return slow, supplied

def check(slow, supplied, orders, details, expected, name):
    with sqlite3.connect(":memory:") as db:
        db.executescript("""
          CREATE TABLE Orders (OrderID INT PRIMARY KEY, CustomerID INT,
                               OrderDate TEXT, Total_Order_Amount REAL);
          CREATE TABLE OrderDetails (OrderDetailID INT PRIMARY KEY,
                                     OrderID INT, Quantity INT);
          CREATE INDEX idx_q096_orders_date ON Orders(OrderDate,Total_Order_Amount,OrderID);
          CREATE INDEX idx_q096_lines_order ON OrderDetails(OrderID);
        """)
        db.executemany("INSERT INTO Orders VALUES (?,?,?,?)", orders)
        db.executemany("INSERT INTO OrderDetails VALUES (?,?,?)", details)
        actual = db.execute(supplied).fetchall()
        baseline = db.execute(slow).fetchall()
        assert actual == baseline, f"{name}: source-query mismatch: {actual!r} vs {baseline!r}"
        assert actual == expected, f"{name}: unexpected output: {actual!r}"
        plan = [r[3] for r in db.execute("EXPLAIN QUERY PLAN " + supplied)]
        assert any("idx_q096_lines_order" in item for item in plan)
        date_seek = any("SEARCH o USING INDEX idx_q096_orders_date" in item for item in plan)
        print(f"PASS Q096 {name}: {len(actual)} rows; source-key equality; "
              f"SQLite detail index observed, date-range seek observed={date_seek}")

def main():
    slow, supplied = queries()
    check(slow, supplied, [
        (1,10,"2026-12-01",2000),(2,20,"2026-12-05",2500),
        (3,30,"2026-12-06",1500)],
        [(1,1,1),(2,1,2)],
        [(2,"2026-12-05",20,2500,0,0),
         (1,"2026-12-01",10,2000,2,3)],
        "original December illustration")
    check(slow, supplied, [
        (1,10,"2026-01-01",2000),(2,20,"2025-12-31",2500),
        (3,30,"2026-01-31",5000),(4,40,"2026-02-01",10000),
        (5,50,"2026-02-28",1999),(6,60,None,25000),
        (7,70,"2026-02-14",None),(8,80,"2026-02-27",2000)],
        [(1,4,10),(2,4,None),(3,4,-4),(4,2,8),(5,8,2),(6,8,3)],
        [(4,"2026-02-01",40,10000,3,6),
         (8,"2026-02-27",80,2000,2,5)],
        "independent month-change/threshold/NULL/multiline boundaries")
    check(slow, supplied, [
        (9,90,"2026-03-30",2100),(10,91,"2026-03-31",2000),
        (11,92,"2026-04-01",100),(12,93,"2026-04-02",None)],
        [(1,9,7)], [], "latest month has no qualifying orders")
    check(slow, supplied, [], [], [], "all empty")
    print("PARTIAL ONLY: one original illustration, three boundary groups; "
          "original-source slow-query equality, two asserted PG date adaptations. "
          "SQLite EXPLAIN is not native PostgreSQL EXPLAIN; source key does not "
          "include requested CREATE INDEX/EXPLAIN evidence; no provider grade, "
          "full-data parity, or independently solved learner coursework.")

if __name__ == "__main__":
    main()
