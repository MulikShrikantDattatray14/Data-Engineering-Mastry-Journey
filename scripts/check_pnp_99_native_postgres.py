#!/usr/bin/env python3
"""P099 independent original-key native PostgreSQL 16 replay (partial).

Execute the immutable supplier SQL exactly as archived, with disposable TEMP
Orders; no dialect changes, learner progress edits or provider grade claims.
Negative counterexamples document source contract limitations, not clean passes.
"""
import hashlib
import re
from datetime import date, timedelta
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
QUESTION = BASE / "15. Analytics and Performance/P099. Flag unusual weeks in order volume.md"
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
QUESTION_BLOB = "69f4a36c43f3df6da10fd0b35a3eab302fb946d1"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"
CREATE_ORDERS = """CREATE TEMP TABLE Orders (
    OrderID integer, OrderDate date
) ON COMMIT DROP"""


def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def original_sql():
    assert blob(QUESTION) == QUESTION_BLOB, "original P099 question changed"
    assert blob(KEY) == KEY_BLOB, "original supplied PostgreSQL key changed"
    question = QUESTION.read_text(encoding="utf-8")
    for marker in ("# PNP Q099.", "previous eight weeks",
                   "sample standard deviation", "2026-03-02", "27.93",
                   "NOT SOLVED YET", "## Official solution", "Pending"):
        assert marker in question, marker
    source = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q99\.[^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", source)
    assert match, "archived supplier Q099 answer block missing"
    sql = match.group(1).strip()
    assert sql.startswith("WITH bounds AS (") and sql.endswith(";")
    for marker in ("generate_series(", "STDDEV_SAMP(w.orders) OVER prior_8w",
                   "ROWS BETWEEN 8 PRECEDING AND 1 PRECEDING",
                   "ROUND(s.z_score, 2)", "ORDER BY is_anomaly DESC NULLS LAST"):
        assert marker in sql, marker
    print("PASS P099 original question and supplier-key Git blob SHA guards")
    return sql


def weekly_orders(counts, first_monday="2026-01-05"):
    start = date.fromisoformat(first_monday)
    rows = []
    for index, count in enumerate(counts):
        monday = start + timedelta(weeks=index)
        for j in range(count):
            # Sunday for the last event makes each occupied week observed through Sunday.
            day = monday + timedelta(days=6 if j == count - 1 else 0)
            rows.append((len(rows) + 1, day))
    return rows


def run(conn, sql, orders):
    with conn.transaction():
        conn.execute(CREATE_ORDERS)
        with conn.cursor() as cur:
            if orders:
                cur.executemany("INSERT INTO Orders VALUES (%s,%s)", orders)
        return conn.execute(sql).fetchall()


def as_tuple(row):
    """Normalize the PG date/NUMERIC/boolean result for exact displayed checks."""
    return (row[0].isoformat(), row[1],
            None if row[2] is None else format(row[2], ".2f"),
            None if row[3] is None else format(row[3], ".2f"),
            None if row[4] is None else format(row[4], ".2f"), row[5])


def source_sample(conn, sql):
    rows = run(conn, sql, weekly_orders([10, 10, 10, 10, 10, 10, 10, 11, 20]))
    assert len(rows) == 9, rows
    assert as_tuple(rows[0]) == ("2026-03-02", 20, "10.13", "0.35", "27.93", True), rows[0]
    assert all(r[5] is None for r in rows[1:]), rows
    print("PASS native P099 original nine-week sample: last week 20/10.13/0.35/27.93/TRUE")


def missing_interior(conn, sql):
    rows = run(conn, sql, weekly_orders([8, 8, 8, 8, 0, 8, 8, 8, 8, 8, 100]))
    assert len(rows) == 11, rows
    zero = next(r for r in rows if r[0] == date(2026, 2, 2))
    assert zero[1] == 0 and zero[5] is None, zero
    assert rows[0][0] == date(2026, 3, 16) and rows[0][1] == 100
    assert rows[0][5] is True, rows[0]
    print("PASS native P099 zero-count interior week and flagged independent spike")


def constant_history(conn, sql):
    rows = run(conn, sql, weekly_orders([10] * 9))
    assert len(rows) == 9, rows
    assert as_tuple(rows[0]) == ("2026-03-02", 10, "10.00", "0.00", None, None), rows[0]
    print("PASS native P099 identical preceding eight: STDDEV_SAMP=0; z-score and flag NULL")


def partial_boundaries(conn, sql):
    orders = [(1, date(2026, 1, 6)), (2, date(2026, 1, 12)),
              (3, date(2026, 2, 2)), (4, date(2026, 3, 4))]
    rows = run(conn, sql, orders)
    assert len(rows) == 7, rows
    assert rows[0][0] == date(2026, 2, 23) and rows[-1][0] == date(2026, 1, 12), rows
    assert next(r for r in rows if r[0] == date(2026, 2, 2))[1] == 1
    assert sum(r[1] for r in rows) == 2, rows
    print("PASS native P099 partial first/last event weeks excluded; empty middle weeks retained")


def absent_dates(conn, sql):
    assert run(conn, sql, []) == []
    assert run(conn, sql, [(1, None), (2, None)]) == []
    assert run(conn, sql, [(1, date(2026, 1, 6))]) == []
    print("PASS native P099 empty Orders, all-NULL dates, lone incomplete week")


def silent_trailing_week(conn, sql):
    # On Monday Mar 16, the calendar week Mar 9-15 is complete. With no
    # orders after Mar 8, the source SQL derives the cutoff from MAX(OrderDate)
    # and cannot produce a Mar 9 zero-count week (the potential broken feed).
    rows = run(conn, sql, weekly_orders([10] * 8 + [20]))
    assert rows and rows[0][0] == date(2026, 3, 2), rows
    assert date(2026, 3, 9) not in {r[0] for r in rows}
    print("REPRODUCED native P099: as-of 2026-03-16 trailing complete silent week 2026-03-09 omitted")
    print("CONTRACT GAP: no as-of date/watermark provided; observation does NOT prove provider-graded failure")


def main():
    sql = original_sql()
    with psycopg.connect(autocommit=True) as conn:
        version = conn.execute("SHOW server_version_num").fetchone()[0]
        assert 160000 <= int(version) < 170000, version
        print(f"PASS native PostgreSQL server_version_num={version}; original SQL executed UNMODIFIED")
        source_sample(conn, sql)
        missing_interior(conn, sql)
        constant_history(conn, sql)
        partial_boundaries(conn, sql)
        absent_dates(conn, sql)
        silent_trailing_week(conn, sql)
    print("PARTIAL P099: six native fixture groups; negative repro is NOT clean key verification")
    print("NO provider-authenticated official answer / original PDF parity / independent learner solve")


if __name__ == "__main__":
    main()
