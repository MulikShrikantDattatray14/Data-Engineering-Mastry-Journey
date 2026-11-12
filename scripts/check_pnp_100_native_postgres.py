#!/usr/bin/env python3
"""Forensic PNP P100 original-key replay on disposable native PostgreSQL 16.

Execute the SHA-pinned, unmodified PostgreSQL key: no SQLite rewriting, no
provider-certified answer, no original dataset parity and no learner completion.
Assertions of *reproduced defects* must never be counted as clean key passes.
"""
import hashlib
import re
from decimal import Decimal
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
QUESTION = BASE / ("15. Analytics and Performance/"
                   "P100. Monthly KPI scorecard with month-over-month change.md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
QUESTION_BLOB = "1c6b25889256fa585ef272b581a676a98759e555"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"

CREATE_ORDERS = """CREATE TEMP TABLE Orders (
    OrderID integer, CustomerID integer, OrderDate date,
    Total_Order_Amount numeric, DeliveryDate date
) ON COMMIT DROP"""
CREATE_DETAILS = """CREATE TEMP TABLE OrderDetails (
    OrderDetailID integer, OrderID integer, Quantity numeric
) ON COMMIT DROP"""
LABELS = (
    "Orders", "Order value", "Average order value", "Active customers",
    "New customers", "Repeat-customer order share",
    "On-time delivery (<= 7 days)", "Units",
)


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()


def extract_key():
    assert git_blob(QUESTION) == QUESTION_BLOB, "Original P100 statement changed"
    assert git_blob(KEY) == KEY_BLOB, "Original P100 supplied answer changed"
    statement = QUESTION.read_text(encoding="utf-8")
    for marker in ("PNP Q100", "2026-12-28", "On-time delivery",
                   "NOT SOLVED YET", "## Official solution", "Pending"):
        assert marker in statement, marker
    assert "| On-time delivery | % |" in statement
    source = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q100\\.[^\\n]*\\n(.*?)(?=^-- Q\\d+\\.|\\Z)", source)
    assert match is not None, "Original Q100 answer block missing"
    sql = match.group(1).strip()
    assert sql.startswith("WITH anchor AS (") and sql.endswith(";")
    assert "JOIN period_units AS pu ON pu.period = po.period" in sql
    assert "JOIN kpis AS l ON p.period = 'prior' AND l.period = 'latest'" in sql
    assert "CROSS JOIN LATERAL" in sql
    assert "'On-time delivery (<= 7 days)'" in sql
    print("PASS original P100 statement and supplied-key Git blob SHA guards")
    return sql


def execute(conn, sql, orders, details):
    """Each case has freshly scoped tables, dropped automatically at commit."""
    with conn.transaction():
        conn.execute(CREATE_ORDERS)
        conn.execute(CREATE_DETAILS)
        with conn.cursor() as cur:
            if orders:
                cur.executemany("INSERT INTO Orders VALUES (%s,%s,%s,%s,%s)", orders)
            if details:
                cur.executemany("INSERT INTO OrderDetails VALUES (%s,%s,%s)", details)
        return conn.execute(sql).fetchall()


def num(value):
    return None if value is None else Decimal(str(value)).quantize(Decimal("0.01"))


def assert_scorecard(rows):
    assert len(rows) == 8, (len(rows), rows)
    assert tuple(r[0] for r in rows) == LABELS, rows
    assert tuple(r[1] for r in rows) == (
        "count", "money", "money", "count", "count", "%", "%", "count"
    ), rows


def original_sample(conn, sql):
    orders = [
        (1, 10, "2026-11-05", 100, "2026-11-10"),
        (2, 20, "2026-11-10", 100, "2026-11-20"),
        (3, 10, "2026-12-05", 200, "2026-12-10"),
        (4, 30, "2026-12-15", 100, None),
        (5, 10, "2026-12-28", 100, "2026-12-28"),
    ]
    details = [(i, i, q) for i, q in enumerate((2, 1, 3, 2, 1), 1)]
    rows = execute(conn, sql, orders, details)
    assert_scorecard(rows)
    expected = [
        (2, 3, 1, 50), (200, 400, 200, 100),
        (100, 133.33, 33.33, 33.33), (2, 2, 0, 0),
        (2, 1, -1, -50), (0, 66.67, 66.67, None),
        (50, 100, 50, None), (3, 6, 3, 100),
    ]
    for row, values in zip(rows, expected):
        assert tuple(num(v) for v in row[2:6]) == tuple(num(v) for v in values), (row, values)
        assert row[6:] == (
            "2026-11-01 to 2026-11-28",
            "2026-12-01 to 2026-12-28",
        ), row
    assert rows[6][0] != "On-time delivery", "Source output label unexpectedly matches"
    print("PASS native original five-order numerical illustration + 8 KPI windows")
    print("REPRODUCED original displayed 'On-time delivery' vs source SQL '(<= 7 days)' label")


def missing_lines(conn, sql):
    orders = [(1, 10, "2026-11-05", 100, "2026-11-06"),
              (2, 10, "2026-12-15", 200, "2026-12-16")]
    assert execute(conn, sql, orders, [(1, 2, 3)]) == []
    assert execute(conn, sql, orders, [(1, 1, 2)]) == []
    print("REPRODUCED native source INNER JOIN zero KPI rows on either missing-line period")


def prior_absent(conn, sql):
    orders = [(1, 30, "2026-12-28", 100, "2026-12-28")]
    assert execute(conn, sql, orders, [(1, 1, 1)]) == []
    assert execute(conn, sql, [], []) == []
    print("REPRODUCED native latest-only/prior-empty zero scorecard rows; empty Orders also zero")


def shorter_month_and_invalid_delivery(conn, sql):
    orders = [(1, 20, "2026-02-28", 120, "2026-02-27"),
              (2, 30, "2026-03-31", 240, "2026-04-10")]
    rows = execute(conn, sql, orders, [(1, 1, 2), (2, 2, 3)])
    assert_scorecard(rows)
    assert all(r[6:] == (
        "2026-02-01 to 2026-02-28", "2026-03-01 to 2026-03-31"
    ) for r in rows), rows
    assert tuple(num(x) for x in rows[0][2:6]) == (
        num(1), num(1), num(0), num(0)
    ), rows[0]
    assert rows[6][2] is None and num(rows[6][3]) == num(0), rows[6]
    print("PASS native Feb-28 / Mar-31 period cap and pre-order delivery exclusion")


def null_quantity(conn, sql):
    orders = [(1, 10, "2026-11-05", 100, "2026-11-06"),
              (2, 10, "2026-12-15", 200, "2026-12-16")]
    rows = execute(conn, sql, orders, [(1, 1, None), (2, 2, None)])
    assert_scorecard(rows)
    assert rows[7][2] is None and rows[7][3] is None, rows[7]
    assert tuple(num(v) for v in rows[0][2:4]) == (num(1), num(1))
    print("PASS native matching NULL-quantity detail rows retain 8 KPIs, Units NULL")


def main():
    sql = extract_key()
    with psycopg.connect(autocommit=True) as conn:
        version = conn.execute("SHOW server_version_num").fetchone()[0]
        assert 160000 <= int(version) < 170000, version
        print(f"PASS native PostgreSQL server_version_num={version}; original SQL unmodified")
        original_sample(conn, sql)
        missing_lines(conn, sql)
        prior_absent(conn, sql)
        shorter_month_and_invalid_delivery(conn, sql)
        null_quantity(conn, sql)
    print("PARTIAL P100: five disposable native Postgres groups; discrepancy fixtures are NOT clean answer passes, provider grades or learner solves")


if __name__ == "__main__":
    main()
