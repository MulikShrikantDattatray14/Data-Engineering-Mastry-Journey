#!/usr/bin/env python3
"""PNP Q096: source-pinned, read-only native PostgreSQL 16 partial independent audit.

Replays both complete archived SQL statements UNMODIFIED on transaction-scoped
synthetic fixtures. The indexes and EXPLAIN probes here are auditor-only:
the supplied Q096 key itself contains neither index DDL nor plans.
"""
import hashlib
import os
import re
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
QUESTION = BASE / ("15. Analytics and Performance/"
                   "P096. Make a slow order report sargable and index it.md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
QUESTION_BLOB = "bcee556369e0af953521ec9ec1b8be96d71986e2"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"
DDL = (
    "CREATE TEMP TABLE Orders (OrderID integer PRIMARY KEY, CustomerID integer, "
    "OrderDate date, Total_Order_Amount numeric) ON COMMIT DROP",
    "CREATE TEMP TABLE OrderDetails (OrderDetailID integer PRIMARY KEY, "
    "OrderID integer, Quantity integer) ON COMMIT DROP",
)


def git_blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def original_queries():
    assert git_blob(QUESTION) == QUESTION_BLOB, "original Q096 source changed"
    assert git_blob(KEY) == KEY_BLOB, "bundled Q096 answer changed"
    md = QUESTION.read_text(encoding="utf-8")
    for marker in ("# PNP Q096.", "NOT SOLVED YET", "## Schema",
                   "### Sample input and expected output", "OrderID", "line_items",
                   "## Official solution", "Pending", "EXPLAIN"):
        assert marker in md, marker
    starter = re.search(
        r"(?s)\*\*Starting query supplied for this debugging task:\*\*\s*"
        r"\x60\x60\x60sql\s*\n(.*?)\n\x60\x60\x60", md)
    assert starter, "Q096 original slow SQL missing"
    slow = starter.group(1).strip()
    assert slow.startswith("SELECT o.OrderID,") and slow.endswith(";")
    assert "TO_CHAR(o.OrderDate, 'YYYY-MM')" in slow
    assert "SELECT COUNT(*) FROM OrderDetails" in slow
    supplied = KEY.read_text(encoding="utf-8")
    found = re.search(r"(?ms)^-- Q96\.[^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", supplied)
    assert found, "Q096 archived supplier SQL missing"
    key = found.group(1).strip()
    assert key.startswith("WITH month_bounds AS (") and key.endswith(";")
    for term in ("DATE_TRUNC('month'", "LEFT JOIN OrderDetails",
                 "o.OrderDate <  mb.next_month_start",
                 "COUNT(od.OrderID)", "GROUP BY o.OrderID"):
        assert term in key, term
    assert "CREATE INDEX" not in key.upper() and "EXPLAIN" not in key.upper()
    print("INSPECTED exact archived Q096 source/key Git blobs; original learner NOT SOLVED YET and official display Pending")
    return slow, key


def setup(conn):
    for sql in DDL:
        conn.execute(sql)


def test_case(conn, slow, key, name, orders, details, expected):
    with conn.transaction():
        setup(conn)
        with conn.cursor() as cur:
            if orders:
                cur.executemany("INSERT INTO Orders VALUES (%s,%s,%s,%s)", orders)
            if details:
                cur.executemany("INSERT INTO OrderDetails VALUES (%s,%s,%s)", details)
        actual = conn.execute(key).fetchall()
        original = conn.execute(slow).fetchall()
        assert actual == original, f"{name}: source original/key differ: {original!r} vs {actual!r}"
        assert actual == expected, f"{name}: incorrect output: {actual!r}"
        print(f"PASS Q096 native {name}: rows={len(actual)}; exact slow SQL == exact supplied SQL; independent expected rows")


def small_cases(conn, slow, key):
    test_case(conn, slow, key, "original December source sample",
        [(1,10,"2026-12-01",2000),(2,20,"2026-12-05",2500),
         (3,30,"2026-12-06",1500)],
        [(1,1,1),(2,1,2)],
        [(2,date(2026,12,5),20,Decimal(2500),0,0),
         (1,date(2026,12,1),10,Decimal(2000),2,3)])
    test_case(conn, slow, key, "independent Feb-boundary and NULL/multiple-line cases",
        [(1,10,"2026-01-01",2000),(2,20,"2025-12-31",2500),
         (3,30,"2026-01-31",5000),(4,40,"2026-02-01",10000),
         (5,50,"2026-02-28",1999),(6,60,None,25000),
         (7,70,"2026-02-14",None),(8,80,"2026-02-27",2000)],
        [(1,4,10),(2,4,None),(3,4,-4),(4,2,8),(5,8,2),(6,8,3)],
        [(4,date(2026,2,1),40,Decimal(10000),3,6),
         (8,date(2026,2,27),80,Decimal(2000),2,5)])
    test_case(conn, slow, key, "latest data month has zero qualifying orders",
        [(9,90,"2026-03-30",2100),(10,91,"2026-03-31",2000),
         (11,92,"2026-04-01",100),(12,93,"2026-04-02",None)],
        [(1,9,7)], [])
    test_case(conn, slow, key, "empty source Orders/OrderDetails", [], [], [])
    print("CONTRACT ambiguity: 'current month' in prose vs MAX(OrderDate) month in both actual source SQL queries")


def plan_nodes(plan):
    yield plan
    for node in plan.get("Plans", ()):
        yield from plan_nodes(node)


def plan_index_names(plan):
    return sorted({n["Index Name"] for n in plan_nodes(plan) if "Index Name" in n})


def explain(conn, query):
    payload = conn.execute("EXPLAIN (FORMAT JSON, COSTS TRUE) " + query).fetchone()[0]
    return payload[0]["Plan"]


def synthetic_index_proof(conn, slow, key):
    with conn.transaction():
        setup(conn)
        # Auditor-only synthetic 18,000-row date distribution, not real dataset.
        conn.execute("""
            INSERT INTO Orders (OrderID,CustomerID,OrderDate,Total_Order_Amount)
            SELECT g, g % 987, DATE '2020-01-01' + (g % 2190),
                   CASE WHEN g % 7 = 0 THEN 3000 ELSE 1000 END
            FROM generate_series(1,18000) AS g
        """)
        conn.execute("""
            INSERT INTO OrderDetails (OrderDetailID,OrderID,Quantity)
            SELECT g, ((g * 37) % 18000) + 1, (g % 5) + 1
            FROM generate_series(1,9000) AS g
        """)
        conn.execute("ANALYZE Orders")
        conn.execute("ANALYZE OrderDetails")
        without_index = explain(conn, key)
        conn.execute("CREATE INDEX idx_q096_orderdate ON Orders(OrderDate, OrderID)")
        conn.execute("CREATE INDEX idx_q096_detail_order ON OrderDetails(OrderID)")
        conn.execute("ANALYZE Orders")
        conn.execute("ANALYZE OrderDetails")
        actual = conn.execute(key).fetchall()
        original = conn.execute(slow).fetchall()
        assert actual == original and len(actual) > 0, "index fixture source row-equivalence failed"
        with_index = explain(conn, key)
        probe = explain(conn, """
            SELECT OrderID FROM Orders
            WHERE OrderDate >= DATE '2025-12-01'
              AND OrderDate < DATE '2026-01-01'
        """)
        probe_indexes = plan_index_names(probe)
        assert "idx_q096_orderdate" in probe_indexes, (
            "synthetic isolated indexed half-open-date-range EXPLAIN did not observe source's proposed date index",
            probe_indexes)
        print(f"PASS Q096 native 18,000 synthetic orders/9,000 lines: exact original/key row equality ({len(actual)} result rows)")
        print(f"EXPLAIN native DEFAULT unindexed supplied query index names: {plan_index_names(without_index)}")
        print(f"EXPLAIN native DEFAULT indexed supplied query index names: {plan_index_names(with_index)}")
        print(f"PASS native independent half-open date-range EXPLAIN: {probe_indexes}")
        print("CAUTION: index DDL and probes are reviewer-only; planner choices and latency are workload-dependent; no source-key index proposal/EXPLAIN or real-data benchmark")


def main():
    slow, key = original_queries()
    with psycopg.connect(
        host=os.getenv("PGHOST","127.0.0.1"),
        port=os.getenv("PGPORT","5432"),
        dbname=os.getenv("PGDATABASE","audit"),
        user=os.getenv("PGUSER","audit"),
        password=os.getenv("PGPASSWORD","audit"),
        autocommit=True) as conn:
        version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        assert 160000 <= version < 170000, version
        print(f"PASS native PostgreSQL server_version_num={version}; original slow and supplier key SQL UNMODIFIED")
        small_cases(conn, slow, key)
        synthetic_index_proof(conn, slow, key)
    print("PARTIAL Q096: four bounded examples + one synthetic EXPLAIN/index demonstration; official provider grade, source PDF/full data parity, comprehensive performance proof and learner independent solve NOT verified")


if __name__ == "__main__":
    main()
