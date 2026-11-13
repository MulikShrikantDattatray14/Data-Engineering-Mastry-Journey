#!/usr/bin/env python3
"""Independent PARTIAL PNP Q092/Q094 native PostgreSQL 16 supplier-key audit.

Only archive-hash-guarded, unmodified bundled PostgreSQL SQL is executed.
Disposable TEMP tables and exact asserted fixtures; negative tests deliberately
reproduce open source-contract gaps, not provider grades or learner completion.
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
    92: (
        "CREATE TEMP TABLE Customers (CustomerID integer, Email text) ON COMMIT DROP",
        "CREATE TEMP TABLE Orders (OrderID integer, CustomerID integer) ON COMMIT DROP",
    ),
    94: (
        "CREATE TEMP TABLE Category (CategoryID integer, CategoryName text) ON COMMIT DROP",
        "CREATE TEMP TABLE Products (ProductID integer, CategoryID integer, Sale_Price numeric) ON COMMIT DROP",
        "CREATE TEMP TABLE Suppliers (SupplierID integer, CompanyName text) ON COMMIT DROP",
        "CREATE TEMP TABLE OrderDetails (OrderDetailID integer, ProductID integer, Quantity integer, SupplierID integer) ON COMMIT DROP",
    ),
}
D = Decimal


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def read_originals():
    assert git_blob(KEY) == KEY_SHA, "original supplier SQL blob drift"
    source = KEY.read_text(encoding="utf-8")
    queries = {}
    for number, (name, sha) in SOURCES.items():
        original = BASE / name
        assert git_blob(original) == sha, f"Q{number} original question blob drift"
        md = original.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{number:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output", "## Schema",
                       "## My solution", "## Official solution",
                       "Pending until you have completely solved"):
            assert marker in md, f"Q{number} source marker missing: {marker}"
        match = re.search(
            rf"(?ms)^-- Q{number}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", source)
        assert match, f"Q{number} supplier SQL missing"
        sql = match.group(1).strip()
        assert sql.startswith("WITH ") and sql.endswith(";"), number
        queries[number] = sql
        print(f"INSPECTED Q{number}: immutable source and key, original learner NOT SOLVED YET / official display Pending")
    assert "c.CustomerID::text" in queries[92]
    assert "NULLIF(LOWER(TRIM(c.Email)), '')" in queries[92]
    assert "ROUND(cs.hhi, 0)" in queries[94]
    assert "CONCAT('Unknown supplier ', cs.SupplierID)" in queries[94]
    return queries


def run(conn, number, sql, tables):
    with conn.transaction():
        for ddl in DDL[number]:
            conn.execute(ddl)
        with conn.cursor() as cur:
            for table, rows in tables.items():
                if rows:
                    placeholders = ",".join(["%s"] * len(rows[0]))
                    cur.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
        return conn.execute(sql).fetchall()


def check(conn, number, sql, label, tables, expected):
    actual = run(conn, number, sql, tables)
    assert actual == expected, (
        f"Q{number} {label}: actual {actual!r} != expected {expected!r}")
    print(f"PASS Q{number} native {label}: {len(actual)} returned rows")


def verify_92(conn, sql):
    check(conn, 92, sql, "original case+trim illustration",
          {"Customers": [(10, " ASHA@example.com "), (20, "asha@example.com"),
                         (30, "bela@example.com")],
           "Orders": [(1,10),(2,20),(3,30)]},
          [("Raw CustomerID",3,0,D("0.00"),3),
           ("Merged by email",2,1,D("50.00"),3)])

    check(conn, 92, sql, "independent blank+NULL email and no-order customer",
          {"Customers": [(10, " x@EXAMPLE.COM "), (20, "X@example.com"),
                         (30, "   "), (40, None), (50, "unused@abc.com")],
           "Orders": [(1,10),(2,10),(3,20),(4,30),(5,40)]},
          [("Raw CustomerID",4,1,D("25.00"),5),
           ("Merged by email",3,1,D("33.33"),5)])

    check(conn, 92, sql, "orphan account IDs remain individually attributed",
          {"Customers": [(10, "A@x.com"), (20, "a@X.COM")],
           "Orders": [(1,10),(2,20),(3,999),(4,999)]},
          [("Raw CustomerID",3,1,D("33.33"),4),
           ("Merged by email",2,2,D("100.00"),4)])

    # With zero orders, the business description requests a row per method;
    # original key returns neither. Reproduce but DO NOT count as a clean pass.
    missing = run(conn, 92, sql,
                  {"Customers": [(10, "a@b.com")], "Orders": []})
    assert missing == [], f"Q092 empty-method regression changed: {missing!r}"
    print("REPRODUCED Q092 gap: zero orders yields ZERO method rows rather than two; undefined rates need source policy")

    # An Order without a CustomerID is dropped from both control totals.
    orphan = run(conn, 92, sql,
                 {"Customers": [(10, "a@b.com")],
                  "Orders": [(1,10),(2,None)]})
    assert orphan == [
        ("Raw CustomerID",1,0,D("0.00"),1),
        ("Merged by email",1,0,D("0.00"),1)
    ], orphan
    print("REPRODUCED Q092 conditional attribution: NULL CustomerID order excluded; totals match each other, not raw Orders count")


def verify_94(conn, sql):
    check(conn, 94, sql, "original 75/25 and HHI 6250 illustration",
          {"Category": [(1,"Audio")],
           "Products": [(101,1,25)],
           "Suppliers": [(7,"Alpha"),(8,"Beta")],
           "OrderDetails": [(1,101,3,7),(2,101,1,8)]},
          [("Audio",2,"Alpha",D("75.00"),D("6250"),"Highly concentrated")])

    check(conn, 94, sql, "independent absent supplier, unmapped category, 50/50 tie",
          {"Category": [(1,"Audio"),(2,"Home")],
           "Products": [(101,1,10),(102,2,15),(103,99,5)],
           "Suppliers": [(5,"Listed")],
           "OrderDetails": [(1,101,1,9),(2,101,1,5),
                            (3,102,2,7),(4,103,4,11)]},
          [("Home",1,"Unknown supplier 7",D("100.00"),D("10000"),"Single source"),
           ("Unmapped",1,"Unknown supplier 11",D("100.00"),D("10000"),"Single source"),
           ("Audio",2,"Listed",D("50.00"),D("5000"),"Highly concentrated")])

    check(conn, 94, sql, "2 equal suppliers zero denominator is undefined not unconcentrated",
          {"Category": [(1,"Audio")],
           "Products": [(101,1,0)],
           "Suppliers": [(5,"Listed")],
           "OrderDetails": [(1,101,1,5),(2,101,1,9)]},
          [("Audio",2,"Listed",None,None,"Unconcentrated")])
    print("REPRODUCED Q094 gap: zero category value -> NULL share and HHI, yet Unconcentrated band")

    check(conn, 94, sql, "NULL supplier and missing product excluded from supplier population",
          {"Category": [(1,"Audio")],
           "Products": [(101,1,10)],
           "Suppliers": [(5,"Listed")],
           "OrderDetails": [(1,101,2,5),(2,101,50,None),(3,999,8,9)]},
          [("Audio",1,"Listed",D("100.00"),D("10000"),"Single source")])
    print("REPRODUCED Q094 conditional coverage: unknown ProductID and NULL SupplierID lines ignored; source policy pending")

    check(conn, 94, sql, "no order lines yields no sales category",
          {"Category": [(1,"Audio")],
           "Products": [(101,1,10)], "Suppliers": [(5,"Listed")],
           "OrderDetails": []},
          [])


def main():
    sql = read_originals()
    with psycopg.connect(
        host=os.environ.get("PGHOST","127.0.0.1"),
        port=os.environ.get("PGPORT","5432"),
        dbname=os.environ.get("PGDATABASE","audit"),
        user=os.environ.get("PGUSER","audit"),
        password=os.environ.get("PGPASSWORD","audit"),
        autocommit=True) as conn:
        version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        assert 160000 <= version < 170000, version
        print(f"PASS native PostgreSQL server_version_num={version}; source SQL unchanged")
        verify_92(conn, sql[92])
        verify_94(conn, sql[94])
    print("PARTIAL ONLY: 10 bounded native fixture groups, including documented counterexamples; no original PDF/full-dataset parity, provider-authenticated answer, learner independent solve, or mastery")


if __name__ == "__main__":
    main()
