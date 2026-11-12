#!/usr/bin/env python3
"""Native PostgreSQL 16 regression of the ORIGINAL PNP Q091 supplier key.

Bounded disposable scratch-table observations, not official answer grading,
full provider PDF/data parity, learner independent completion, or full signoff.
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
QUESTION = BASE / ("12. Dates and Time/"
                   "P091. Cumulative value per customer by cohort (LTV curve).md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
SOURCE_BLOB = "cf11e56982938b3227f711e00534237f88d451aa"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"

CREATE = """CREATE TEMP TABLE Orders (
    OrderID integer PRIMARY KEY, CustomerID integer,
    OrderDate date, Total_Order_Amount numeric
) ON COMMIT DROP"""
INSERT = ("INSERT INTO Orders (OrderID, CustomerID, OrderDate, Total_Order_Amount) "
          "VALUES (%s, %s, %s, %s)")


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def original_sql() -> str:
    assert git_blob(QUESTION) == SOURCE_BLOB, "original Q091 question changed"
    assert git_blob(KEY) == KEY_BLOB, "original supplier Q91 answer key changed"
    task = QUESTION.read_text(encoding="utf-8-sig")
    for token in ("# PNP Q091.", "NOT SOLVED YET",
                  "## My solution — SQLite\n\nPending",
                  "## Official solution\n\nPending",
                  "2025-01-01", "2026-01-01"):
        assert token.replace("\n", "\n") in task, ("archived task/status drift", token)
    key_text = KEY.read_text(encoding="utf-8-sig")
    match = re.search(r"(?ms)^-- Q91\. [^\n]*\n(.*?)(?=^-- Q92\.|\Z)",
                      key_text)
    assert match, "cannot find original Q91 key"
    sql = match.group(1).strip()
    assert sql.startswith("WITH anchor AS") and sql.endswith(";")
    for token in ("DATE_TRUNC('month', MAX(o.OrderDate) + 1)",
                  "DATE_TRUNC('quarter', fo.first_month)",
                  "generate_series(0, 12)",
                  "s.cohort_quarter + INTERVAL '2 months'",
                  "cv.is_complete", "FILTER (WHERE cv.month_offset = 12"):
        assert token in sql, ("supplier logic drift", token)
    print(f"INSPECTED Q091 original source Git blob {SOURCE_BLOB}; "
          f"supplier SQL key {KEY_BLOB}; learner and official Pending")
    return sql


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
        autocommit=True)


def execute(sql: str, rows: list[tuple]) -> list[tuple]:
    with connect() as conn:
        with conn.transaction():
            conn.execute(CREATE)
            if rows:
                with conn.cursor() as cur:
                    cur.executemany(INSERT, rows)
            raw = conn.execute(sql).fetchall()
            return [
                (r[0].isoformat(), int(r[1]), *(
                    None if value is None else float(value) for value in r[2:]))
                for r in raw
            ]


def check():
    sql = original_sql()
    with connect() as conn:
        version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        assert 160000 <= version < 170000, version
    print(f"NATIVE PostgreSQL server_version_num={version}; "
          "ORIGINAL_KEY unmodified, no SQLite adapters")

    sample = [
        (1, 10, "2025-01-05", 100),
        (2, 10, "2025-04-05", 50),
        (3, 10, "2026-01-31", 50),
        (4, 20, "2026-01-10", 80),
    ]
    got = execute(sql, sample)
    key_expected = [
        ("2025-01-01", 1, 100.0, 150.0, 150.0, None),
        ("2026-01-01", 1, None, None, None, None),
    ]
    assert got == key_expected, ("original four-order native output", got)
    supplied_illustration = [
        ("2025-01-01", 1, 100.0, 150.0, 150.0, 200.0),
        ("2026-01-01", 1, 80.0, None, None, None),
    ]
    assert got != supplied_illustration
    assert got[0][:5] == supplied_illustration[0][:5]
    assert got[0][5] is None and supplied_illustration[0][5] == 200
    assert got[1][2] is None and supplied_illustration[1][2] == 80
    print("PASS Q091 ORIGINAL_KEY four-order source: two original sample/key "
          "cell discrepancies REPRODUCED (not contract pass)")

    later = execute(sql, sample + [(5, 30, "2027-01-31", 60)])
    assert later == [
        ("2025-01-01", 1, 100.0, 150.0, 150.0, 200.0),
        ("2026-01-01", 1, 80.0, 80.0, 80.0, None),
        ("2027-01-01", 1, None, None, None, None),
    ], later
    print("PASS Q091 ORIGINAL_KEY independently extended January-2027 anchor")

    # A non-end-of-month maximum date is not counted as a completed month.
    partial = [(1, 10, "2025-01-05", 100),
               (2, 20, "2026-03-15", 20)]
    complete = [(1, 10, "2025-01-05", 100),
                (2, 20, "2026-03-31", 20)]
    early, finished = execute(sql, partial), execute(sql, complete)
    assert early[0] == ("2025-01-01", 1, 100.0, 100.0, 100.0, None), early
    assert finished[0] == ("2025-01-01", 1, 100.0, 100.0, 100.0, 100.0), finished
    assert early[1] == ("2026-01-01", 1, None, None, None, None), early
    assert finished[1] == ("2026-01-01", 1, 20.0, None, None, None), finished
    print("PASS Q091 ORIGINAL_KEY midmonth vs last-day cutoff; Q1-2026 m0 "
          "becomes mature only at March month-end")

    assert execute(sql, []) == [], "empty Orders must have no cohorts"
    print("PASS Q091 ORIGINAL_KEY empty Orders boundary")
    print("PARTIAL Q091: native source-output conflict remains; no provider-grade "
          "official solution verification, complete PDF/data parity or learner solve")


if __name__ == "__main__":
    check()
