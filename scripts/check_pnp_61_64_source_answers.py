#!/usr/bin/env python3
"""Read-only source-fenced PNP Q061-Q064 supplied-key checks, SQLite scope.

Extracts original archived PostgreSQL answer-key queries, pins five original
Git blobs and executes four independently retyped illustrative contracts plus
five separate synthetic boundary groups. PostgreSQL-only constructs in Q061,
Q063, Q064 are replaced by asserted, narrowly scoped SQLite equivalents.
Neither native PostgreSQL parity, original full-data results, Academy grading,
nor new learner solves are asserted.
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
    61: ("12. Dates and Time/P061. Monthly cohort retention.md", "b6bf67ee468f10bcfab8dcfa0f81cd9ad7656e60"),
    62: ("15. Analytics and Performance/P062. Which products make up 80% of list-price value (Pareto).md", "564ea158c8601820176feb7d17632c8bf5fda6d0"),
    63: ("15. Analytics and Performance/P063. RFM segmentation.md", "37c05e67792bfbad5ffac4a83638511e0caaa2b0"),
    64: ("12. Dates and Time/P064. Three-month moving average of order value, with no missing months.md", "cebae7618f34327faeabd6790aeddbbd4a95e41d"),
}

def git_blob(path):
    contents = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(contents)).encode() + b"\0" + contents).hexdigest()

def original_sql(number, source):
    match = re.search(rf"(?ms)^-- Q{number}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", source)
    assert match, f"Q{number}: supplied-key SQL missing"
    query = match.group(1).strip()
    assert query.startswith("WITH "), number
    return query

def replace_exact(query, old, new, count=1):
    assert query.count(old) == count, f"SQL drift, expected {count} occurrence(s): {old}"
    return query.replace(old, new)

def executable(number, query):
    if number == 61:
        swaps = [
            ("DATE_TRUNC('month', o.OrderDate)::date", "date(o.OrderDate,'start of month')"),
            ("EXTRACT(YEAR  FROM cm.activity_month)", "CAST(strftime('%Y', cm.activity_month) AS INT)"),
            ("EXTRACT(YEAR  FROM co.cohort_month)", "CAST(strftime('%Y', co.cohort_month) AS INT)"),
            ("EXTRACT(MONTH FROM cm.activity_month)", "CAST(strftime('%m', cm.activity_month) AS INT)"),
            ("EXTRACT(MONTH FROM co.cohort_month)", "CAST(strftime('%m', co.cohort_month) AS INT)"),
            ("DATE_TRUNC('month', MAX(o.OrderDate)::date + 1)::date", "date(MAX(o.OrderDate), '+1 day', 'start of month')"),
            ("cc.cohort_month + INTERVAL '1 month'", "date(cc.cohort_month,'+1 month')"),
            ("cc.cohort_month + INTERVAL '2 months'", "date(cc.cohort_month,'+2 month')"),
            ("cc.cohort_month + INTERVAL '3 months'", "date(cc.cohort_month,'+3 month')"),
            ("cc.cohort_month + INTERVAL '6 months'", "date(cc.cohort_month,'+6 month')"),
        ]
        for before, after in swaps:
            query = replace_exact(query, before, after)
    elif number == 63:
        assert query.count("MAX(o.OrderDate)::date") == 2, "Q063 date-cast shape drift"
        query = replace_exact(
            query, "a.as_of_date - MAX(o.OrderDate)::date",
            "CAST(julianday(a.as_of_date) - julianday(date(MAX(o.OrderDate))) AS INT)"
        )
        query = replace_exact(query, "MAX(o.OrderDate)::date", "date(MAX(o.OrderDate))")
    elif number == 64:
        swaps = [
            ("DATE_TRUNC('month', MIN(o.OrderDate))::date", "date(MIN(o.OrderDate),'start of month')", 1),
            ("DATE_TRUNC('month', MAX(o.OrderDate))::date", "date(MAX(o.OrderDate),'start of month')", 1),
            ("DATE_TRUNC('month', o.OrderDate)::date", "date(o.OrderDate,'start of month')", 2),
            ("WITH bounds AS (", "WITH RECURSIVE bounds AS (", 1),
            (
                "    SELECT gs::date AS order_month\n    FROM bounds AS b\n    CROSS JOIN generate_series(b.first_month, b.last_month, INTERVAL '1 month') AS gs",
                "    SELECT b.first_month AS order_month FROM bounds AS b WHERE b.first_month IS NOT NULL\n"
                "    UNION ALL\n"
                "    SELECT date(ms.order_month,'+1 month') FROM month_spine AS ms "
                "CROSS JOIN bounds AS b WHERE ms.order_month < b.last_month", 1
            ),
        ]
        for before, after, count in swaps:
            query = replace_exact(query, before, after, count)
    for forbidden in ("::", "DATE_TRUNC(", "EXTRACT(", " INTERVAL ", "generate_series("):
        assert forbidden not in query, f"Q{number}: unhandled PostgreSQL syntax {forbidden}"
    return query

SCHEMAS = {
    61: ["Orders(OrderID INT,CustomerID INT,OrderDate TEXT)"],
    62: ["Products(ProductID INT,Product TEXT,Sale_Price REAL)",
         "OrderDetails(OrderDetailID INT,ProductID INT,Quantity INT)"],
    63: ["Customers(CustomerID INT)",
         "Orders(OrderID INT,CustomerID INT,OrderDate TEXT,Total_Order_Amount INT)"],
    64: ["Orders(OrderID INT,OrderDate TEXT,Total_Order_Amount INT)"],
}

# Data and expected outputs transcribed independently from the original Markdown
# illustrative tables; source PDF supplies only output field descriptions.
ILLUSTRATIONS = {
    61: (
        {"Orders": [(1,1,"2025-01-05"),(2,1,"2025-02-05"),(3,1,"2025-07-31"),
                    (4,2,"2025-01-10"),(5,2,"2025-03-10"),
                    (6,3,"2025-04-01"),(7,3,"2025-05-01")]},
        [("2025-01-01",2,50.0,50.0,0.0,50.0),
         ("2025-04-01",1,100.0,0.0,0.0,None)],
    ),
    62: (
        {"Products": [(1,"A",60),(2,"B",30),(3,"C",10)],
         "OrderDetails": [(11,1,1),(12,2,1),(13,3,1)]},
        [(1,"A",60.0,60.0,60.0,"Top 80%"),
         (2,"B",30.0,30.0,90.0,"Top 80%"),
         (3,"C",10.0,10.0,100.0,"Long tail")],
    ),
    63: (
        {"Customers": [(i,) for i in range(1,6)],
         "Orders": [(10+i,i,f"2025-01-0{i}",10*i) for i in range(1,6)]},
        [(5,0,1,50,5,1,5,"New or promising"),
         (4,1,1,40,4,1,4,"New or promising"),
         (3,2,1,30,3,1,3,"Needs attention"),
         (2,3,1,20,2,1,2,"Hibernating"),
         (1,4,1,10,1,1,1,"Hibernating")],
    ),
    64: (
        {"Orders": [(1,"2025-01-01",100),(2,"2025-03-01",300),(3,"2025-04-01",100)]},
        [("2025-01-01",100,None),("2025-02-01",0,None),
         ("2025-03-01",300,133.33),("2025-04-01",100,133.33)],
    ),
}

# Separate auditor-created fixtures. Not new source-provided samples.
SYNTHETIC = {
    61: [
        (
            {"Orders": [(1,1,"2024-12-15"),(2,1,"2025-01-01"),(3,1,"2025-01-31"),
                        (4,1,"2025-03-05"),(5,2,"2024-12-20"),(6,2,"2025-02-10"),
                        (7,3,"2025-02-01"),(8,3,"2025-03-01"),
                        (9,3,"2025-05-31"),(10,None,"2025-04-20")]},
            [("2024-12-01",2,50.0,50.0,50.0,None),
             ("2025-02-01",1,100.0,0.0,100.0,None)],
        ),
    ],
    62: [
        (
            {"Products": [(1,"A",60),(2,"B",30),(3,"C",10),
                          (4,"No sale",99),(5,"Zero",5),(6,"Negative",-5)],
             "OrderDetails": [(11,1,1),(12,2,1),(13,3,1),(14,3,2),
                              (15,5,0),(16,6,1),(17,999,200)]},
            [(1,"A",60.0,50.0,50.0,"Top 80%"),
             (2,"B",30.0,25.0,75.0,"Top 80%"),
             (3,"C",30.0,25.0,100.0,"Top 80%")],
        ),
        (
            {"Products": [(1,"A",80),(2,"B",20)],
             "OrderDetails": [(11,1,1),(12,2,1)]},
            [(1,"A",80.0,80.0,80.0,"Top 80%"),
             (2,"B",20.0,20.0,100.0,"Long tail")],
        ),
    ],
    63: [
        (
            {"Customers": [(i,) for i in range(1,8)],
             "Orders": [(11,1,"2025-01-01",10),(12,1,"2025-01-03",15),
                        (13,2,"2025-01-02",20),(14,3,"2025-01-03",30),
                        (15,4,"2025-01-04",40),(16,5,"2025-01-05",50),
                        (17,6,"2025-01-05",50),(18,999,"2025-01-06",5000),
                        (19,5,None,100)]},
            [(5,1,1,50,4,1,4,"New or promising"),
             (6,1,1,50,4,1,4,"New or promising"),
             (4,2,1,40,3,1,3,"Needs attention"),
             (1,3,2,25,1,5,1,"At risk"),
             (3,3,1,30,1,1,2,"Hibernating"),
             (2,4,1,20,1,1,1,"Hibernating")],
        ),
    ],
    64: [
        (
            {"Orders": [(1,"2024-12-01",90),(2,"2025-02-02",30),
                        (3,"2025-02-06",None),(4,"2025-03-01",30),
                        (5,"2025-04-01",0),(6,None,999)]},
            [("2024-12-01",90,None),("2025-01-01",0,None),
             ("2025-02-01",30,40.0),("2025-03-01",30,20.0),
             ("2025-04-01",0,20.0)],
        ),
    ],
}

def run_fixture(number, sql, values, wanted, name):
    db = sqlite3.connect(":memory:")
    try:
        for definition in SCHEMAS[number]:
            db.execute("CREATE TABLE " + definition)
        for table, rows in values.items():
            if rows:
                slots = ",".join("?" for _ in rows[0])
                db.executemany(f"INSERT INTO {table} VALUES({slots})", rows)
        observed = db.execute(sql).fetchall()
        assert observed == wanted, f"Q{number} {name}: {observed!r} != {wanted!r}"
    finally:
        db.close()

def main():
    assert sqlite3.sqlite_version_info >= (3,39,0), "Requires SQLite >=3.39 for window/FILTER support"
    assert git_blob(KEY) == KEY_SHA, "Archived supplied key changed"
    key_text = KEY.read_text(encoding="utf-8")
    for number, (relative, expected_sha) in SOURCES.items():
        original = BASE / relative
        assert git_blob(original) == expected_sha, f"Q{number}: original source drift"
        source = original.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{number:03d}.", "### Sample input and expected output",
                       "## Schema", "NOT SOLVED YET", "## Official solution", "Pending"):
            assert marker in source, f"Q{number}: absent source marker {marker}"
        sql = executable(number, original_sql(number, key_text))
        values, expected = ILLUSTRATIONS[number]
        run_fixture(number, sql, values, expected, "source illustration")
        for ix, (values, expected) in enumerate(SYNTHETIC[number], start=1):
            run_fixture(number, sql, values, expected, f"synthetic #{ix}")
    print("PASS: Q061-Q064 four source/key blob pins; 4 Markdown illustration contracts; "
          "5 independent synthetic groups (2 for Q062). PostgreSQL-only syntax narrowly "
          "transcribed to SQLite for Q061/Q063/Q064. No original dataset/native PG/official grade/learner solve.")

if __name__ == "__main__":
    main()
