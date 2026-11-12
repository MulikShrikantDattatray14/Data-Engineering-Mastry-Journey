#!/usr/bin/env python3
"""Partial, independent PNP Q095 original-query native PostgreSQL 16 audit.

Read original Git-blob-pinned source question and supplier SQL; execute BOTH
the archived intentionally faulty starting query and unmodified supplier key
in disposable transaction-scoped TEMP tables. No learner work/grade edits.
"""
import hashlib
import os
import re
from decimal import Decimal
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
QUESTION = BASE / ("14. Data Quality and Deduplication/"
                   "P095. Debug a revenue-by-category query that gives wrong numbers.md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
QUESTION_BLOB = "6556470a667af5ddb73e9adce81e65bb4331cb3b"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"
DDL = (
    "CREATE TEMP TABLE Category (CategoryID integer, CategoryName text) ON COMMIT DROP",
    "CREATE TEMP TABLE Products (ProductID integer, CategoryID integer, Sale_Price numeric) ON COMMIT DROP",
    "CREATE TEMP TABLE Orders (OrderID integer, OrderDate date, Total_Order_Amount numeric) ON COMMIT DROP",
    "CREATE TEMP TABLE OrderDetails (OrderDetailID integer, OrderID integer, ProductID integer, Quantity integer) ON COMMIT DROP",
)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def source_queries():
    assert git_blob(QUESTION) == QUESTION_BLOB, "archived Q095 question changed"
    assert git_blob(KEY) == KEY_BLOB, "archived supplier answer changed"
    question = QUESTION.read_text(encoding="utf-8")
    for marker in ("# PNP Q095.", "NOT SOLVED YET", "## Schema",
                   "### Sample input and expected output", "Home | 0 | 0",
                   "Unmapped | 1 | 5", "Audio | 1 | 20",
                   "## Official solution", "Pending"):
        assert marker in question, marker
    start = re.search(r"(?s)\*\*Starting query supplied for this debugging task:\*\*"
                      r"\s*\x60\x60\x60sql\n(.*?)\n\x60\x60\x60", question)
    assert start, "original intentionally incorrect Q095 starting SQL missing"
    original_bad = start.group(1).strip()
    assert "SUM(o.Total_Order_Amount)" in original_bad
    assert "WHERE o.OrderDate >=" in original_bad
    assert original_bad.endswith(";")
    source = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q95\.[^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", source)
    assert match, "original supplier Q095 corrected SQL missing"
    supplied = match.group(1).strip()
    for marker in ("FULL JOIN category_sales AS cs ON cs.CategoryID = cat.CategoryID",
                   "COUNT(DISTINCT yl.OrderID)", "SUM(yl.list_price_value)",
                   "DATE_TRUNC('year'", "ORDER BY list_price_value, CategoryName"):
        assert marker in supplied, marker
    assert supplied.startswith("WITH latest_year AS (") and supplied.endswith(";")
    print("INSPECTED native Q095: both exact original Git blobs; learner NOT SOLVED YET / Pending")
    return original_bad, supplied


def run(conn, query, categories=(), products=(), orders=(), lines=()):
    with conn.transaction():
        for ddl in DDL:
            conn.execute(ddl)
        with conn.cursor() as cur:
            data = (("Category", categories, 2), ("Products", products, 3),
                    ("Orders", orders, 3), ("OrderDetails", lines, 4))
            for table, records, width in data:
                if records:
                    cur.executemany(
                        f"INSERT INTO {table} VALUES (" + ",".join(["%s"] * width) + ")",
                        records)
        return conn.execute(query).fetchall()


def normalized(rows):
    return [(name, n, Decimal(value)) for name, n, value in rows]


def source_illustration(conn, start, corrected):
    categories = [(1, "Audio"), (2, "Home")]
    products = [(101, 1, 10), (102, 99, 5)]
    orders = [(1, "2026-01-01", 25)]
    lines = [(1, 1, 101, 2), (2, 1, 102, 1)]
    kw = dict(categories=categories, products=products, orders=orders, lines=lines)
    actual = run(conn, corrected, **kw)
    assert normalized(actual) == [
        ("Home", 0, Decimal(0)),
        ("Unmapped", 1, Decimal(5)),
        ("Audio", 1, Decimal(20))
    ], actual
    bad = run(conn, start, **kw)
    assert bad == [("Audio", 1, Decimal(25))], bad
    print("PASS Q095 native original example: corrected Home 0 / Unmapped 5 / Audio 20")
    print("REPRODUCED source intentionally-bad query: Audio 1 order / inflated header 25; Home and Unmapped missing")


def independent_boundaries(conn, corrected):
    got = run(conn, corrected,
        categories=[(1, "Audio"), (2, "Home"), (3, "Empty"), (4, "Audio")],
        products=[(101, 1, 10), (102, 99, 5), (103, 2, 7),
                  (104, 4, 4), (105, 1, None), (106, None, 9)],
        orders=[(1, "2026-01-01", 25), (2, "2026-12-31", 80),
                (3, "2025-12-31", 2000)],
        lines=[(1,1,101,2), (2,1,102,1), (3,2,101,3), (4,2,103,2),
               (5,3,104,500), (6,2,106,1), (7,2,105,1),
               (8,2,103,1), (9,2,999,1)])
    assert normalized(got) == [
        ("Audio", 0, Decimal(0)), ("Empty", 0, Decimal(0)),
        ("Unmapped", 2, Decimal(14)), ("Home", 1, Decimal(21)),
        ("Audio", 2, Decimal(50))
    ], got
    print("PASS Q095 native independent Jan/Dec/latest-year, 2025-exclusion, distinct orders, NULL price, missing catalog/product, same-name separate IDs")
    print("CONDITIONAL Q095: duplicate category names yield separate identically labelled rows; output has no CategoryID")


def empty_and_unmapped(conn, corrected):
    got = run(conn, corrected, categories=[(1, "Audio"), (2, "Home")])
    assert normalized(got) == [("Audio",0,Decimal(0)), ("Home",0,Decimal(0))], got
    got = run(conn, corrected, products=[(1,99,8)],
              orders=[(5,"2026-06-03",16)], lines=[(11,5,1,2)])
    assert normalized(got) == [("Unmapped",1,Decimal(16))], got
    got = run(conn, corrected, categories=[(1,"Audio")],
              products=[(1,1,None), (2,1,3)],
              orders=[(5,"2026-06-03",6)],
              lines=[(11,5,1,2), (12,5,2,2)])
    assert normalized(got) == [("Audio",1,Decimal(6))], got
    print("PASS Q095 native no-orders, missing Category table records and NULL-price line boundaries")


def source_faults_and_label_collision(conn, start, corrected):
    kw = dict(categories=[(1,"Audio")], products=[(101,1,10)],
              orders=[(1,"2026-01-01",100)],
              lines=[(1,1,101,2), (2,1,101,3)])
    wrong = run(conn, start, **kw)
    fixed = run(conn, corrected, **kw)
    assert wrong == [("Audio",2,Decimal(200))], wrong
    assert normalized(fixed) == [("Audio",1,Decimal(50))], fixed
    print("REPRODUCED original starter join-multiplication: 2 rows / 200 header vs 1 order / 50 list-price")

    got = run(conn, corrected,
        categories=[(1,"Unmapped"),(2,"Audio")],
        products=[(101,1,5),(102,99,7)],
        orders=[(1,"2026-05-01",12)],
        lines=[(1,1,101,1),(2,1,102,1)])
    assert normalized(got) == [
        ("Audio",0,Decimal(0)),
        ("Unmapped",1,Decimal(5)), ("Unmapped",1,Decimal(7))
    ], got
    print("CONDITIONAL Q095 native label collision: literal CategoryName Unmapped vs missing category each show Unmapped")
    print("SOURCE GAP: supplied corrected key lacks explicit starting-query fault-by-fault row-count/total explanation")


def main():
    start, corrected = source_queries()
    with psycopg.connect(
        host=os.environ.get("PGHOST","127.0.0.1"),
        port=os.environ.get("PGPORT","5432"),
        dbname=os.environ.get("PGDATABASE","audit"),
        user=os.environ.get("PGUSER","audit"),
        password=os.environ.get("PGPASSWORD","audit"),
        autocommit=True) as conn:
        ver = int(conn.execute("SHOW server_version_num").fetchone()[0])
        assert 160000 <= ver < 170000, ver
        print(f"PASS native PostgreSQL server_version_num={ver}; both source SQL queries run UNMODIFIED")
        source_illustration(conn, start, corrected)
        independent_boundaries(conn, corrected)
        empty_and_unmapped(conn, corrected)
        source_faults_and_label_collision(conn, start, corrected)
    print("PARTIAL Q095: 4 native fixture groups; native synthetic evidence != official provider grade, original dataset/PDF parity, or learner independent solve")


if __name__ == "__main__":
    main()
