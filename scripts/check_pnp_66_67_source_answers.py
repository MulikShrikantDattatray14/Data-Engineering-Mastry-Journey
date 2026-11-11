#!/usr/bin/env python3
"""Read-only, source-pinned Q066/Q067 supplied-key audit.

The actual archived PostgreSQL SQL is extracted and given narrowly asserted
SQLite adaptations for date subtraction and ordered-set percentiles. Checks
two original Markdown illustrations and four independently authored synthetic
boundary groups. This is NOT native PostgreSQL, complete source-dataset
execution, provider grading, or a learner-completed solution.
"""
import hashlib
import math
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
SOURCES = {
    66: ("12. Dates and Time/P066. How fast do customers come back for a second order.md",
         "6f9872c8f72dd666be3e356318aec2175156e6ce"),
    67: ("15. Analytics and Performance/P067. Median vs mean order value by payment type.md",
         "590aa7f85667f81d124c0f9248b1c8721f009868"),
}
SCHEMAS = {
    66: ("Orders(OrderID INT, CustomerID INT, OrderDate TEXT)",),
    67: ("Payments(PaymentID INT, PaymentType TEXT)",
         "Orders(OrderID INT, PaymentID INT, Total_Order_Amount REAL)"),
}
ILLUSTRATIVE = {
    66: (
        {"Orders": [(1,1,"2025-01-01"),(2,1,"2025-01-01"),(3,1,"2025-01-04"),
                    (4,2,"2025-01-02"),(5,3,"2024-02-01"),(6,3,"2024-02-05")]},
        [(2024,1,1,100.0,4.0,4.0),(2025,2,1,50.0,3.0,3.0)]
    ),
    67: (
        {"Payments": [(1,"UPI"),(2,"Card")],
         "Orders": [(1,1,10),(2,1,20),(3,1,30),
                    (4,2,10),(5,2,10),(6,2,100)]},
        [("Card",3,40.0,10.0,4.0),("UPI",3,20.0,20.0,1.0)]
    ),
}
SYNTHETIC = {
    66: [
        (
            {"Orders": [
                (1,10,"2024-12-31"),(2,10,"2024-12-31"),(3,10,"2025-01-01"),
                (4,11,"2024-02-29"),(5,11,"2024-03-01"),
                (6,12,"2024-03-10"),
                (7,17,"2024-05-01"),(8,17,"2024-05-10"),(9,17,"2024-05-12"),
                (10,13,"2025-01-01"),(11,13,"2025-01-05"),
                (12,14,"2025-02-01"),(13,14,"2025-02-03"),
                (14,15,"2025-02-02"),(15,18,"2026-01-01"),
                (16,None,"2026-01-01"),(17,99,None)
            ]},
            [(2024,4,3,75.0,1.0,5.0),(2025,3,2,66.67,3.0,3.5),
             (2026,1,0,0.0,None,None)]
        ),
        (
            {"Orders": [
                (1,100,"2023-01-01"),(2,100,"2023-01-02"),
                (3,101,"2023-01-01"),(4,101,"2023-01-03"),
                (5,102,"2023-01-01"),(6,102,"2023-01-10"),
                (7,103,"2023-01-01"),(8,103,"2023-01-11"),
                (9,104,"2023-01-01"),
                (10,100,"2023-01-02")
            ]},
            [(2023,5,4,80.0,5.5,9.3)]
        )
    ],
    67: [
        (
            {"Payments": [(1,"Card"),(2,"UPI"),(3,"Wire")],
             "Orders": [
                (1,1,10),(2,1,20),(3,1,30),
                (4,2,0),(5,2,0),(6,2,10),
                (7,999,10),(8,None,30),(9,999,20),(10,999,None),
                (11,3,5),(12,3,15),(13,3,35),(14,3,45)
             ]},
            [("Card",3,20.0,20.0,1.0),("Unknown",3,20.0,20.0,1.0),
             ("Wire",4,25.0,25.0,1.0),("UPI",3,3.33,0.0,None)]
        ),
        (
            {"Payments": [(1,"Card"),(2,"Card"),(3,"Cash"),(4,"Bank")],
             "Orders": [(1,1,10),(2,2,20),
                        (3,3,None),(4,3,0),(5,3,0),(6,3,0),
                        (7,999,-10),(8,999,10),(9,999,None),(10,4,None)]},
            [("Card",2,15.0,15.0,1.0),("Cash",3,0.0,0.0,None),
             ("Unknown",2,0.0,0.0,None)]
        )
    ]
}

def blob_sha(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def extract(number, archive):
    match = re.search(rf"(?ms)^-- Q{number}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", archive)
    assert match, f"missing Q{number} in supplied SQL archive"
    sql = match.group(1).strip()
    assert sql.startswith("WITH ") and sql.endswith(";"), f"Q{number} SQL structure changed"
    return sql

def substitute(sql, old, new, count=1):
    assert sql.count(old) == count, f"source expression occurrence mismatch ({old!r})"
    return sql.replace(old, new)

class ContinuousPercentile:
    def __init__(self, probability):
        self.probability = probability
        self.values = []
    def step(self, value):
        if value is not None:
            self.values.append(float(value))
    def finalize(self):
        if not self.values:
            return None
        ordered = sorted(self.values)
        position = (len(ordered) - 1) * self.probability
        low = int(math.floor(position))
        high = int(math.ceil(position))
        return ordered[low] + (ordered[high] - ordered[low]) * (position - low)

def adapt(number, sql):
    if number == 66:
        sql = substitute(sql, "o.OrderDate::date AS order_date",
                         "DATE(o.OrderDate) AS order_date")
        sql = substitute(sql, "s.next_order_date - s.order_date",
                         "(julianday(s.next_order_date) - julianday(s.order_date))")
        sql = substitute(sql, "EXTRACT(YEAR FROM fo.first_order_date)::int",
                         "CAST(strftime('%Y', fo.first_order_date) AS INTEGER)")
        sql = substitute(sql, "GROUP BY EXTRACT(YEAR FROM fo.first_order_date)",
                         "GROUP BY CAST(strftime('%Y', fo.first_order_date) AS INTEGER)")
        sql = substitute(sql,
            "(PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY fo.days_to_second))::numeric",
            "PERCENTILE_CONT_50(fo.days_to_second)")
        sql = substitute(sql,
            "(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY fo.days_to_second))::numeric",
            "PERCENTILE_CONT_75(fo.days_to_second)")
    elif number == 67:
        sql = substitute(sql,
            "(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY o.Total_Order_Amount))::numeric",
            "PERCENTILE_CONT_50(o.Total_Order_Amount)")
    else:
        raise AssertionError("unexpected question")
    assert not any(token in sql for token in ("::", "PERCENTILE_CONT(", "WITHIN GROUP", "EXTRACT("))
    return sql

def run_fixture(number, sql, dataset, expected, label):
    db = sqlite3.connect(":memory:")
    try:
        db.create_aggregate("PERCENTILE_CONT_50", 1, lambda: ContinuousPercentile(0.5))
        db.create_aggregate("PERCENTILE_CONT_75", 1, lambda: ContinuousPercentile(0.75))
        for schema in SCHEMAS[number]:
            db.execute("CREATE TABLE " + schema)
        for table, rows in dataset.items():
            if rows:
                db.executemany("INSERT INTO " + table + " VALUES (" +
                               ",".join("?" for _ in rows[0]) + ")", rows)
        actual = db.execute(sql).fetchall()
        assert actual == expected, f"Q{number} {label}: got {actual!r}; expected {expected!r}"
    finally:
        db.close()

def main():
    assert sqlite3.sqlite_version_info >= (3, 39, 0)
    assert blob_sha(KEY) == KEY_SHA, "supplied key archive changed"
    archive = KEY.read_text(encoding="utf-8")
    for number, (relative, pinned_sha) in SOURCES.items():
        original = BASE / relative
        assert blob_sha(original) == pinned_sha, f"Q{number} source changed"
        content = original.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{number:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output", "## Schema",
                       "## Official solution", "Pending"):
            assert marker in content, f"Q{number} missing source marker: {marker}"
        sql = adapt(number, extract(number, archive))
        run_fixture(number, sql, *ILLUSTRATIVE[number], "archived Markdown illustration")
        for index, (data, expected) in enumerate(SYNTHETIC[number], start=1):
            run_fixture(number, sql, data, expected, f"synthetic boundary group #{index}")
    print("PASS: source-pinned Q066/Q067; 2 illustrated output contracts + "
          "4 independent synthetic groups via explicit SQLite percentiles/date emulation. "
          "NOT native PostgreSQL, full source data, official grading, or learner mastery.")

if __name__ == "__main__":
    main()
