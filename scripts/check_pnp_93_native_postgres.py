#!/usr/bin/env python3
"""Untranslated PostgreSQL 16 replay of immutable PNP Q093 supplied SQL.

Original illustration and bounded synthetic discrepancy cases only. This is
not official answer verification, a learner solution, or full dataset parity.
"""
from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCE = BASE / ("14. Data Quality and Deduplication/"
                 "P093. Possible duplicate order submissions.md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
SOURCE_BLOB = "2b53cdb94d64cb19581be48c9af6f0a8670b72c2"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"
REVIEW = "Review: send same-basket pairs to support"
CLEAR = "No duplicate submissions"

CREATE_ORDERS = """CREATE TEMP TABLE Orders (
 OrderID integer PRIMARY KEY, CustomerID integer, OrderDate date,
 Total_Order_Amount numeric, PaymentID integer, ShipperID integer
) ON COMMIT DROP"""
CREATE_DETAILS = """CREATE TEMP TABLE OrderDetails (
 OrderDetailID integer PRIMARY KEY, OrderID integer,
 ProductID integer, Quantity integer
) ON COMMIT DROP"""
INSERT_ORDERS = ("INSERT INTO Orders (OrderID,CustomerID,OrderDate,"
                 "Total_Order_Amount,PaymentID,ShipperID) VALUES (%s,%s,%s,%s,%s,%s)")
INSERT_DETAILS = ("INSERT INTO OrderDetails (OrderDetailID,OrderID,ProductID,Quantity)"
                  " VALUES (%s,%s,%s,%s)")


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def original_sql():
    assert git_blob(SOURCE) == SOURCE_BLOB, "original P093 task modified"
    assert git_blob(KEY) == KEY_BLOB, "original supplier key modified"
    task = SOURCE.read_text(encoding="utf-8-sig")
    for token in ("# PNP Q093.", "NOT SOLVED YET", "same_day_pairs",
                  "same_basket_pairs", "same_amount_pairs", "exact_copies",
                  "## My solution — SQLite\n\nPending",
                  "## Official solution\n\nPending"):
        assert token in task, ("original source/status drift", token)
    key = KEY.read_text(encoding="utf-8-sig")
    hit = re.search(r"(?ms)^-- Q93\. [^\n]*\n(.*?)(?=^-- Q94\.|\Z)", key)
    assert hit, "original supplied Q093 source not found"
    sql = hit.group(1).strip()
    assert sql.startswith("WITH product_lines AS (") and sql.endswith(";")
    for token in ("STRING_AGG(", "BOOL_AND(", "IS NOT DISTINCT FROM",
                  "JOIN signatures AS sg ON sg.OrderID = o.OrderID",
                  "WHERE sg.basket_known", "COUNT(*) FILTER (WHERE sp.same_amount)"):
        assert token in sql, ("original Q093 SQL changed", token)
    print(f"INSPECTED P093 source blob {SOURCE_BLOB}, supplied-key blob {KEY_BLOB},"
          " preserved learner/official Pending")
    return sql


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
        autocommit=True)


def execute(conn, sql, orders, details):
    # Every fixture uses fresh scratch tables automatically dropped at commit.
    with conn.transaction():
        conn.execute(CREATE_ORDERS)
        conn.execute(CREATE_DETAILS)
        with conn.cursor() as cur:
            if orders:
                cur.executemany(INSERT_ORDERS, orders)
            if details:
                cur.executemany(INSERT_DETAILS, details)
        got = conn.execute(sql).fetchall()
        assert len(got) == 1, got
        return got[0]


def fixture(conn, sql, label, orders, details, expected):
    got = execute(conn, sql, orders, details)
    assert got == expected, (label, got, expected)
    print(f"PASS P093 NATIVE_POSTGRES ORIGINAL_KEY {label}: {got!r}")


def main():
    sql = original_sql()
    with connect() as conn:
        version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        assert 160000 <= version < 170000, version
        print(f"NATIVE PostgreSQL server_version_num={version}; Q093 exact key, no adapters")
        fixture(conn, sql, "original_illustration",
                [(1, 10, "2026-01-01", 20, 5, 7),
                 (2, 10, "2026-01-01", 20, 5, 7)],
                [(1, 1, 101, 2), (2, 2, 101, 2)],
                (1, 1, 1, 1, REVIEW))
        fixture(conn, sql, "independent_three_pairs",
                [(1, 10, "2026-01-01", 20, 5, 7),
                 (2, 10, "2026-01-01", 25, 5, 7),
                 (3, 10, "2026-01-01", 20, 5, 7),
                 (4, 10, "2026-01-02", 20, 5, 7),
                 (5, 11, "2026-01-01", 20, 5, 7)],
                [(1, 1, 101, 2), (2, 2, 101, 2), (3, 3, 102, 1),
                 (4, 4, 101, 2), (5, 5, 101, 2)],
                (3, 1, 1, 0, REVIEW))
        fixture(conn, sql, "empty_orders", [], [],
                (0, 0, 0, 0, CLEAR))
        fixture(conn, sql, "KNOWN_GAP_missing_order_details_pair_dropped",
                [(1, 10, "2026-01-01", 20, 5, 7),
                 (2, 10, "2026-01-01", 20, 5, 7)],
                [(1, 1, 101, 2)], (0, 0, 0, 0, CLEAR))
        fixture(conn, sql, "KNOWN_GAP_null_quantity_pair_dropped",
                [(1, 10, "2026-01-01", 20, 5, 7),
                 (2, 10, "2026-01-01", 20, 5, 7)],
                [(1, 1, 101, None), (2, 2, 101, None)],
                (0, 0, 0, 0, CLEAR))
        fixture(conn, sql, "KNOWN_NULL_POLICY_same_basket_exact_but_amount_count_zero",
                [(1, 10, "2026-01-01", None, 5, 7),
                 (2, 10, "2026-01-01", None, 5, 7)],
                [(1, 1, 101, 2), (2, 2, 101, 2)],
                (1, 1, 0, 1, REVIEW))
    print("PARTIAL P093: 3 bounded fixture passes plus 3 documented source-key"
          " discrepancies. No original PDF/full data/provider official answer"
          " verification or independent learner completion.")


if __name__ == "__main__":
    main()
