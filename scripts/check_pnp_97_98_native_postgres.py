#!/usr/bin/env python3
"""PNP Q097/Q098: original-key native PostgreSQL 16 source audit (PARTIAL).

Read-only, SHA-guarded, transaction-scoped synthetic verification. All candidate
SQL is the UNMODIFIED bundled source key. Counterexamples document contract
ambiguities; they are not successful official-answer grades or learner solves.
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
QUESTIONS = {
    97: ("9. Windowing Functions/P097. What do customers buy on their second order.md",
         "9bf349ac0fe866697d481d3206ecd4598ec3c76e"),
    98: ("15. Analytics and Performance/P098. Category association rules support, confidence, lift.md",
         "526ba18093580b581cb8ef5442a2ce31b222f3fd"),
}
DDL = (
    "CREATE TEMP TABLE Category (CategoryID integer, CategoryName text) ON COMMIT DROP",
    "CREATE TEMP TABLE Products (ProductID integer, CategoryID integer, Sale_Price numeric) ON COMMIT DROP",
    "CREATE TEMP TABLE Orders (OrderID integer, CustomerID integer, OrderDate date) ON COMMIT DROP",
    "CREATE TEMP TABLE OrderDetails (OrderDetailID integer, OrderID integer, ProductID integer, Quantity integer) ON COMMIT DROP",
)
D = Decimal


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def read_source():
    assert git_blob(KEY) == KEY_SHA, "original supplier key changed"
    key_text = KEY.read_text(encoding="utf-8")
    queries = {}
    for num, (rel, sha) in QUESTIONS.items():
        question = BASE / rel
        assert git_blob(question) == sha, f"original Q{num} question changed"
        md = question.read_text(encoding="utf-8")
        for part in (f"# PNP Q{num:03d}.", "NOT SOLVED YET",
                     "### Sample input and expected output", "## Schema",
                     "## My solution", "## Official solution",
                     "Pending until you have completely solved"):
            assert part in md, f"Q{num} missing immutable historical marker: {part}"
        matched = re.search(
            rf"(?ms)^-- Q{num}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key_text)
        assert matched, f"Q{num} supplied key not found"
        sql = matched.group(1).strip()
        assert sql.startswith("WITH ") and sql.endswith(";")
        assert "OrderDetails" in sql and "Category" in sql
        queries[num] = sql
        print(f"INSPECTED Q{num} immutable original question/key; historical learner NOT SOLVED YET, source official-display Pending")
    assert "ROW_NUMBER()" in queries[97] and "'No second order'" in queries[97]
    assert "COUNT(DISTINCT b.OrderID)" in queries[98] and "2.0 AS min_support_pct" in queries[98]
    return queries


def fixture(conn, number, query, label, tables, expected):
    with conn.transaction():
        for ddl in DDL:
            conn.execute(ddl)
        for name, rows in tables.items():
            if rows:
                args = ",".join(["%s"] * len(rows[0]))
                with conn.cursor() as cur:
                    cur.executemany(f"INSERT INTO {name} VALUES ({args})", rows)
        actual = conn.execute(query).fetchall()
        assert actual == expected, (
            f"Q{number} {label}: actual {actual!r}, independent expected {expected!r}")
        print(f"PASS Q{number} native {label}: rows={len(actual)}")
        return actual


def q97(conn, sql):
    cats = [(1, "Audio"), (2, "Home")]
    prods = [(101, 1, 5), (102, 2, 10)]
    fixture(conn, 97, sql, "original 3-order illustration",
            {"Category": cats, "Products": prods,
             "Orders": [(1,10,"2026-01-01"), (2,10,"2026-01-10"),
                        (3,20,"2026-01-02")],
             "OrderDetails": [(1,1,101,2), (2,2,102,1), (3,3,101,1)]},
            [("Audio","Home",1,D("50.00")),
             ("Audio","No second order",1,D("50.00"))])

    fixture(conn, 97, sql, "independent tie, missing lines, unmapped and second-order boundaries",
            {"Category": [(1,"Audio"), (2,"Home"), (3,"Other")],
             "Products": [(101,1,10), (102,2,10), (103,3,6)],
             "Orders": [(1,10,"2026-01-01"), (2,10,"2026-01-02"),
                        (3,20,"2026-01-01"), (4,20,"2026-01-02"),
                        (5,30,"2026-01-01"), (6,40,"2026-01-01"),
                        (7,40,"2026-01-02")],
             "OrderDetails": [(1,1,101,1), (2,2,102,1),
                              (3,3,101,1), (4,3,102,1),
                              (5,5,999,1)]},
            [("Audio","Home",1,D("50.00")),
             ("Audio","No line items",1,D("50.00")),
             ("No line items","No line items",1,D("100.00")),
             ("Unmapped","No second order",1,D("100.00"))])

    fixture(conn, 97, sql, "CONTRACT GAP real category named No second order merges with absent second order",
            {"Category": [(1,"Audio"), (2,"No second order")],
             "Products": [(101,1,5), (102,2,10)],
             "Orders": [(1,10,"2026-01-01"), (2,20,"2026-01-01"),
                        (3,20,"2026-01-02")],
             "OrderDetails": [(1,1,101,1), (2,2,101,1), (3,3,102,1)]},
            [("Audio","No second order",2,D("100.00"))])

    fixture(conn, 97, sql, "CONTRACT POLICY NULL date drops earlier otherwise counted customer order",
            {"Category": cats, "Products": prods,
             "Orders": [(1,10,None), (2,10,"2026-01-02")],
             "OrderDetails": [(1,1,101,1), (2,2,102,1)]},
            [("Home","No second order",1,D("100.00"))])
    fixture(conn, 97, sql, "empty Orders and lines",
            {"Category": cats, "Products": prods}, [])


def q98(conn, sql):
    cats = [(1, "Audio"), (2, "Home")]
    prods = [(101, 1, 5), (102, 2, 10)]
    fixture(conn, 98, sql, "original four-basket directed-rule illustration",
            {"Category": cats, "Products": prods,
             "OrderDetails": [(1,1,101,1), (2,1,102,1),
                              (3,2,101,1), (4,2,102,1),
                              (5,3,101,1), (6,4,102,1)]},
            [("Audio","Home",2,D("50.00"),D("66.67"),D("0.889")),
             ("Home","Audio",2,D("50.00"),D("66.67"),D("0.889"))])

    fixture(conn, 98, sql, "independent deduped order/category and directed-rule ranking",
            {"Category": cats,
             "Products": [(101,1,5), (102,2,10),
                          (103,2,12), (104,99,4)],
             "OrderDetails": [(1,1,101,1), (2,1,101,1),
                              (3,1,102,1), (4,1,103,1),
                              (5,2,101,1), (6,2,102,1),
                              (7,3,101,1), (8,4,102,1),
                              (9,5,101,1), (10,5,104,1)]},
            [("Unmapped","Audio",1,D("20.00"),D("100.00"),D("1.250")),
             ("Audio","Unmapped",1,D("20.00"),D("25.00"),D("1.250")),
             ("Home","Audio",2,D("40.00"),D("66.67"),D("0.833")),
             ("Audio","Home",2,D("40.00"),D("50.00"),D("0.833"))])

    fixture(conn, 98, sql, "CONTRACT POLICY orphan-product-only order omitted from basket denominator",
            {"Category": cats, "Products": prods,
             "OrderDetails": [(1,1,101,1), (2,1,999,1),
                              (3,2,101,1), (4,2,102,1),
                              (5,3,102,1), (6,4,999,1)]},
            [("Audio","Home",1,D("33.33"),D("50.00"),D("0.750")),
             ("Home","Audio",1,D("33.33"),D("50.00"),D("0.750"))])

    def many(n):
        return [(1,1,101,1), (2,1,102,1)] + [
            (order_id + 1, order_id, 101, 1) for order_id in range(2,n+1)]

    fixture(conn, 98, sql, "50-basket exactly 2-percent support inclusive",
            {"Category": cats, "Products": prods, "OrderDetails": many(50)},
            [("Home","Audio",1,D("2.00"),D("100.00"),D("1.000")),
             ("Audio","Home",1,D("2.00"),D("2.00"),D("1.000"))])

    fixture(conn, 98, sql, "51-basket sub-2-percent support excluded",
            {"Category": cats, "Products": prods, "OrderDetails": many(51)}, [])

    fixture(conn, 98, sql, "empty eligible basket denominator",
            {"Category": cats, "Products": prods}, [])


def main():
    queries = read_source()
    with psycopg.connect(host=os.getenv("PGHOST", "127.0.0.1"),
                         port=os.getenv("PGPORT", "5432"),
                         dbname=os.getenv("PGDATABASE", "audit"),
                         user=os.getenv("PGUSER", "audit"),
                         password=os.getenv("PGPASSWORD", "audit"),
                         autocommit=True) as conn:
        version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        assert 160000 <= version < 170000, version
        print(f"PASS native PostgreSQL server_version_num={version}, unmodified Q097 Q098 supplier key")
        q97(conn, queries[97])
        q98(conn, queries[98])
    print("PARTIAL: 11 native fixture groups, including 2 source examples; "
          "counterexamples document open semantics, not official grades. "
          "NO full Commerce v2/PDF parity or learner independent solves.")


if __name__ == "__main__":
    main()
