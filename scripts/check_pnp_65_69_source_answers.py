#!/usr/bin/env python3
"""Read-only Q065/Q068/Q069 source-key audit: exact archived key SQL plus
minimal ASSERTED PostgreSQL-to-SQLite date/boolean adaptations.

Three original Markdown illustrative fixtures and four separately designed
synthetic groups; not native PG16, full source dataset, provider grading,
official authenticated answers, or independent learner completion.
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
    68: ("9. Windowing Functions/P068. Second-highest spender in each state, counting delivered orders on.md", "a80b0bf2147dc7d8e92612541b34a80b9017b154"),
    69: ("12. Dates and Time/P069. Customers whose spend grew every active quarter of the latest year.md", "e9cacb210d57d3218b6ad98ca8f2a5b9343e4f8a"),
}
SCHEMAS = {
    65: ("Orders(OrderID INT, CustomerID INT, OrderDate TEXT)",),
    68: ("Customers(CustomerID INT, FirstName TEXT, LastName TEXT, State TEXT)",
         "Orders(OrderID INT, CustomerID INT, OrderDate TEXT, DeliveryDate TEXT, Total_Order_Amount REAL)"),
    69: ("Orders(OrderID INT, CustomerID INT, OrderDate TEXT, Total_Order_Amount REAL)",),
}

# Rows/output individually transcribed from untouched PNP Markdown, not from
# the SQL answer key. These illustrations were authored in the archive and
# do not constitute original official-PDF dataset output evidence.
ILLUSTRATIVE = {
    65: (
        {"Orders": [(1,10,"2025-01-01"),(2,10,"2025-02-01"),(3,10,"2025-04-01"),
                    (4,10,"2025-05-01"),(5,20,"2025-01-01"),(6,20,"2025-02-01"),(7,20,"2025-03-01")]},
        [(20,"2025-01-01","2025-03-01",3),(10,"2025-04-01","2025-05-01",2)]
    ),
    68: (
        {"Customers": [(1,"Asha","Rao","Karnataka"),(2,"Ben","Das","Karnataka"),(3,"Cia","Sen","Karnataka")],
         "Orders": [(10,1,"2025-01-01","2025-01-02",100),(11,2,"2025-01-01","2025-01-02",80),
                    (12,3,"2025-01-01","2025-01-02",80)]},
        [("Karnataka",2,"Ben Das",80,2),("Karnataka",3,"Cia Sen",80,2)]
    ),
    69: (
        {"Orders": [(1,10,"2025-01-01",10),(2,10,"2025-04-01",20),(3,10,"2025-10-01",30),
                    (4,20,"2025-01-01",10),(5,20,"2025-04-01",5),(6,20,"2025-07-01",20)]},
        [(10,3,10,30)]
    )
}

# Explicitly different fixtures / independent boundary expectations.
SYNTHETIC = {
    65: [
        (
            {"Orders": [(1,1,"2024-12-05"),(2,1,"2025-01-25"),(3,1,"2025-02-01"),
                        (4,1,"2025-02-26"),(5,2,"2025-01-01"),(6,2,"2025-02-01"),
                        (7,2,"2025-05-01"),(8,2,"2025-06-01"),(9,3,"2025-04-01"),
                        (10,3,"2025-05-01"),(11,3,"2025-06-01"),(12,4,"2025-02-05"),
                        (13,4,None)]},
            [(3,"2025-04-01","2025-06-01",3),(1,"2024-12-01","2025-02-01",3),
             (2,"2025-05-01","2025-06-01",2),(4,"2025-02-01","2025-02-01",1)]
        ),
        (
            {"Orders": [(1,200,"2025-01-01"),(2,200,"2025-02-01")] +
                       [(i+3,100+i,"2025-03-01") for i in range(12)]},
            [(200,"2025-01-01","2025-02-01",2)] +
            [(100+i,"2025-03-01","2025-03-01",1) for i in range(12)]
        ),
    ],
    68: [
        (
            {"Customers": [(1,"A","One"," "),(2,"B","Two",None),(3,"C","Three",""),
                           (4,"D","Four","NY"),(5,"E","Five","NY")],
             "Orders": [(1,1,"2025-01-01","2025-01-02",100),
                        (2,2,"2025-01-01","2025-01-02",80),
                        (3,3,"2025-01-01","2025-01-02",80),
                        (4,4,"2025-01-01","2025-01-02",10),
                        (5,5,"2025-01-01","2025-01-02",0),
                        (6,999,"2025-01-01","2025-01-02",70),
                        (7,888,"2025-01-01","2025-01-02",30),
                        (8,2,"2025-01-02","2025-01-01",900)]},
            [("Unknown",2,"B Two",80,2),("Unknown",3,"C Three",80,2),
             ("Unmapped customer",888,"Unknown customer",30,2)]
        )
    ],
    69: [
        (
            {"Orders": [(1,100,"2024-12-31",9999),
                        (2,1,"2025-01-01",10),(3,1,"2025-07-01",20),(4,1,"2025-10-01",30),
                        (5,2,"2025-01-01",10),(6,2,"2025-04-01",20),(7,2,"2025-07-01",20),
                        (8,3,"2025-01-01",1),(9,3,"2025-04-01",2),
                        (10,4,"2025-01-01",1),(11,4,"2025-01-07",1),
                        (12,4,"2025-04-01",4),(13,4,"2025-10-01",6),
                        (14,5,"2025-01-01",-10),(15,5,"2025-04-01",0),(16,5,"2025-10-01",10),
                        (17,6,"2025-01-01",10),(18,6,"2025-04-01",None),(19,6,"2025-07-01",30),
                        (20,7,None,1000)]},
            [(1,3,10,30),(5,3,-10,10),(4,3,2,6)]
        )
    ],
}

def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def extract_sql(number, archive):
    match = re.search(rf"(?ms)^-- Q{number}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", archive)
    assert match, f"Q{number}: supplied query not present"
    sql = match.group(1).strip()
    assert sql.startswith("WITH ") and sql.endswith(";"), f"Q{number}: key structure changed"
    return sql

def replace_exact(sql, source, replacement, count=1):
    actual = sql.count(source)
    assert actual == count, f"expected {count} exact PG expression(s), found {actual}: {source}"
    return sql.replace(source, replacement)

def adapt_sql(number, sql):
    # These are explicit transformations solely to execute the untouched
    # supplied PostgreSQL key's logic on SQLite, NOT a native PG16 run.
    if number == 65:
        sql = replace_exact(sql, "DATE_TRUNC('month', o.OrderDate)::date",
                            "DATE(o.OrderDate, 'start of month')")
        sql = replace_exact(
            sql,
            "(EXTRACT(YEAR FROM cm.order_month) * 12 + EXTRACT(MONTH FROM cm.order_month))::int",
            "(CAST(strftime('%Y', cm.order_month) AS INTEGER) * 12 + "
            "CAST(strftime('%m', cm.order_month) AS INTEGER))")
    elif number == 68:
        sql = replace_exact(sql, "o.DeliveryDate::date", "DATE(o.DeliveryDate)")
        sql = replace_exact(sql, "o.OrderDate::date", "DATE(o.OrderDate)")
    elif number == 69:
        sql = replace_exact(sql, "DATE_TRUNC('year', MAX(o.OrderDate))::date",
                            "DATE(MAX(o.OrderDate), 'start of year')")
        sql = replace_exact(
            sql, "DATE_TRUNC('quarter', o.OrderDate)::date",
            "DATE(o.OrderDate, 'start of year', '+' || "
            "(CAST((CAST(strftime('%m', o.OrderDate) AS INTEGER) - 1) / 3 AS INTEGER) * 3) || ' months')",
            count=2)
        sql = replace_exact(sql, "a.year_start + INTERVAL '1 year'",
                            "DATE(a.year_start, '+1 year')")
        sql = replace_exact(
            sql,
            "BOOL_AND(COALESCE(c.quarter_spend > c.prev_spend, FALSE)) FILTER (WHERE c.quarter_seq > 1)",
            "MIN(COALESCE(c.quarter_spend > c.prev_spend, 0)) FILTER (WHERE c.quarter_seq > 1) = 1")
    else:
        raise AssertionError(f"unreviewed query {number}")
    assert not any(token in sql for token in ("::date", "DATE_TRUNC", "EXTRACT(", "BOOL_AND(", "INTERVAL '"))
    return sql

def check_fixture(number, sql, dataset, expected, label):
    db = sqlite3.connect(":memory:")
    try:
        # SQLite versions on CI can predate CONCAT_WS; this shim exactly
        # mimics PostgreSQL's non-NULL concatenation for non-NULL separators.
        db.create_function("CONCAT_WS", -1, lambda separator, *parts:
                           None if separator is None else separator.join(str(x) for x in parts if x is not None))
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
    assert sqlite3.sqlite_version_info >= (3, 39, 0), "SQLite FILTER/window runtime is required"
    assert git_blob(KEY) == KEY_SHA, "preserved supplied-key blob changed"
    archive = KEY.read_text(encoding="utf-8")
    for number, (relative, sha) in SOURCES.items():
        original = BASE / relative
        assert git_blob(original) == sha, f"Q{number}: original source changed"
        content = original.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{number:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output", "## Schema",
                       "## Official solution", "Pending"):
            assert marker in content, f"Q{number}: source marker missing: {marker}"
        sql = adapt_sql(number, extract_sql(number, archive))
        check_fixture(number, sql, *ILLUSTRATIVE[number], "archived Markdown illustration")
        for ix, (dataset, expected) in enumerate(SYNTHETIC[number], 1):
            check_fixture(number, sql, dataset, expected, f"independent synthetic #{ix}")
    print("PASS: Q065/Q068/Q069 pinned archived SQL; 3 source illustrations + "
          "4 synthetic SQLite boundary groups. Explicit PG-to-SQLite adaptations; "
          "no native PostgreSQL, full data, provider grade, or learner solve.")

if __name__ == "__main__":
    main()
