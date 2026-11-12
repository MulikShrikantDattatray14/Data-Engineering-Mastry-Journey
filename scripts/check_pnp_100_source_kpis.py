#!/usr/bin/env python3
"""Read-only PNP P100 source-key replay; pin originals and disclose mismatch cases.

The immutable PostgreSQL SQL is extracted at runtime, then explicitly adapted
for SQLite's date functions, numeric casts and correlated LATERAL VALUES syntax.
This is *not* provider-certified or native PostgreSQL answer verification.
No historical learner attempts, archived sources or foundation notes are written.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
QUESTION = BASE / ("15. Analytics and Performance/"
                   "P100. Monthly KPI scorecard with month-over-month change.md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
QUESTION_SHA = "1c6b25889256fa585ef272b581a676a98759e555"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"


def git_blob(path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def replace_n(sql, old, new, n=1):
    assert sql.count(old) == n, (old, sql.count(old), n)
    return sql.replace(old, new)


def extract_and_adapt():
    assert git_blob(QUESTION) == QUESTION_SHA, "Archived P100 question was modified"
    assert git_blob(KEY) == KEY_SHA, "Archived supplied P100 key was modified"
    question = QUESTION.read_text(encoding="utf-8")
    for marker in ("# PNP Q100.", "2026-12-28",
                   "On-time delivery", "OrderDetails",
                   "NOT SOLVED YET", "## Official solution", "Pending"):
        assert marker in question, ("Original P100 source marker missing", marker)
    key = KEY.read_text(encoding="utf-8")
    m = re.search(r"(?ms)^-- Q100\.[^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key)
    assert m, "Original P100 PostgreSQL section absent"
    sql = m.group(1).strip()
    assert sql.startswith("WITH anchor AS (") and sql.endswith(";")
    assert "JOIN period_units AS pu ON pu.period = po.period" in sql
    assert "JOIN kpis AS l ON p.period = 'prior' AND l.period = 'latest'" in sql
    # Only asserted PostgreSQL -> SQLite date/cast/operator substitutions.
    sql = replace_n(sql, "DATE_TRUNC('month', a.last_day)::date",
                    "DATE(a.last_day, 'start of month')")
    sql = replace_n(sql,
                    "(DATE_TRUNC('month', a.last_day) - INTERVAL '1 month')::date",
                    "DATE(a.last_day, 'start of month', '-1 month')", 2)
    old = ("DATE(a.last_day, 'start of month', '-1 month')"
           "\n                     + (EXTRACT(DAY FROM a.last_day)::int - 1)")
    new = ("DATE(a.last_day, 'start of month', '-1 month',"
           "\n                     printf('+%d days', CAST(strftime('%d', a.last_day) AS INT) - 1))")
    sql = replace_n(sql, old, new)
    sql = replace_n(sql,
                    "(DATE_TRUNC('month', a.last_day) - INTERVAL '1 day')::date",
                    "DATE(a.last_day, 'start of month', '-1 day')")
    sql = replace_n(sql, "LEAST(", "MIN(")
    sql = replace_n(sql, "::numeric", "", 4)
    sql = replace_n(sql,
                    "po.DeliveryDate - po.OrderDate <= 7",
                    "julianday(po.DeliveryDate) - julianday(po.OrderDate) <= 7")
    # SQLite has no LATERAL VALUES: derive the eight displayed rows verbatim
    # from the source key, and use its JSON table-valued function instead.
    lateral = re.search(
        r"CROSS JOIN LATERAL \(\s*VALUES (.*?)\) AS v"
        r"\(sort_order, kpi, unit, prior_value, latest_value\)",
        sql, re.S)
    assert lateral, "Original P100 lateral rows have changed"
    rows = re.findall(
        r"\(\s*(\d+),\s*'([^']+)',\s*'([^']+)',"
        r"\s*(p\.\w+),\s*(l\.\w+)\s*\)", lateral.group(1))
    assert len(rows) == 8 and [int(r[0]) for r in rows] == list(range(1, 9)), rows
    assert [r[1] for r in rows] == [
        "Orders", "Order value", "Average order value", "Active customers",
        "New customers", "Repeat-customer order share",
        "On-time delivery (<= 7 days)", "Units"], rows
    objects = []
    for sort_order, label, unit, prior, latest in rows:
        objects.append(
            "json_object('sort_order'," + sort_order +
            ",'kpi','" + label + "','unit','" + unit +
            "','prior_value'," + prior + ",'latest_value'," + latest + ")")
    sql = sql[:lateral.start()] + (
        "CROSS JOIN json_each(json_array(\n    " +
        ",\n    ".join(objects) +
        "\n)) AS v") + sql[lateral.end():]
    for col in ("kpi", "unit", "prior_value", "latest_value", "sort_order"):
        sql = sql.replace("v." + col, "json_extract(v.value, '$." + col + "')")
    for unsupported in ("DATE_TRUNC(", "::", "INTERVAL ", "LATERAL",
                        "EXTRACT(DAY", "LEAST("):
        assert unsupported not in sql, ("Unexpected dialect in P100", unsupported)
    print("PASS P100 immutable original question and supplied-key Git blob identities")
    print("SCOPE: PG dates/casts/LATERAL display adapter; original window/KPI joins/aggregates retained")
    return sql


def execute(sql, orders, lines):
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE TABLE Orders("
                   "OrderID INT, CustomerID INT, OrderDate TEXT,"
                   "Total_Order_Amount REAL, DeliveryDate TEXT)")
        db.execute("CREATE TABLE OrderDetails(OrderDetailID INT, OrderID INT, Quantity INT)")
        db.executemany("INSERT INTO Orders VALUES (?,?,?,?,?)", orders)
        db.executemany("INSERT INTO OrderDetails VALUES (?,?,?)", lines)
        return db.execute(sql).fetchall()
    finally:
        db.close()


def check_sample(sql):
    orders = [(1, 10, "2026-11-05", 100, "2026-11-10"),
              (2, 20, "2026-11-10", 100, "2026-11-20"),
              (3, 10, "2026-12-05", 200, "2026-12-10"),
              (4, 30, "2026-12-15", 100, None),
              (5, 10, "2026-12-28", 100, "2026-12-28")]
    rows = execute(sql, orders, [(1, 1, 2), (2, 2, 1), (3, 3, 3),
                                 (4, 4, 2), (5, 5, 1)])
    expected = [
        ("Orders", "count", 2, 3, 1, 50.0),
        ("Order value", "money", 200, 400, 200, 100.0),
        ("Average order value", "money", 100, 133.33, 33.33, 33.33),
        ("Active customers", "count", 2, 2, 0, 0.0),
        ("New customers", "count", 2, 1, -1, -50.0),
        ("Repeat-customer order share", "%", 0, 66.67, 66.67, None),
        ("On-time delivery (<= 7 days)", "%", 50, 100, 50, None),
        ("Units", "count", 3, 6, 3, 100.0),
    ]
    assert len(rows) == 8, rows
    for actual, expected_row in zip(rows, expected):
        assert actual[:6] == expected_row, (actual, expected_row)
        assert actual[6:] == ("2026-11-01 to 2026-11-28",
                              "2026-12-01 to 2026-12-28"), actual
    # Source's own expected-output label is "On-time delivery"; key adds
    # "(<= 7 days)". Arithmetic passes but exact source-label contract fails.
    assert "| On-time delivery | % |" in QUESTION.read_text(encoding="utf-8")
    assert rows[6][0] != "On-time delivery"
    print("PASS P100 original five-order illustration numerical KPI and windows; "
          "REPRODUCED exact output-label mismatch on on-time delivery")


def check_missing_units(sql):
    orders = [(1, 10, "2026-11-05", 100, "2026-11-06"),
              (2, 10, "2026-12-15", 200, "2026-12-16")]
    # The KPI task counts every valid Orders header. A period can have zero
    # OrderDetails; the supplied INNER JOIN to period_units instead deletes
    # that whole period and thus all eight report rows.
    assert execute(sql, orders, [(1, 2, 3)]) == []
    assert execute(sql, orders, [(1, 1, 2)]) == []
    print("REPRODUCED P100 key's INNER JOIN period_units defect: missing line "
          "items in either month suppress all eight KPIs despite valid orders")


def check_shorter_month_and_dates(sql):
    orders = [(1, 20, "2026-02-28", 120, "2026-02-27"),
              (2, 30, "2026-03-31", 240, "2026-04-10")]
    rows = execute(sql, orders, [(1, 1, 2), (2, 2, 3)])
    assert len(rows) == 8, rows
    assert all(r[6:] == ("2026-02-01 to 2026-02-28",
                         "2026-03-01 to 2026-03-31") for r in rows), rows
    assert rows[0][:6] == ("Orders", "count", 1, 1, 0, 0), rows[0]
    # Invalid pre-order delivery ignored in denominator; latest late delivery.
    assert rows[6][2] is None and rows[6][3] == 0, rows[6]
    print("PASS P100 shorter-month end cap and pre-order delivery excluded")


def check_missing_prior_and_empty(sql):
    latest_only = [(1, 30, "2026-12-28", 100, "2026-12-28")]
    assert execute(sql, latest_only, [(1, 1, 1)]) == []
    assert execute(sql, [], []) == []
    print("REPRODUCED P100 no-prior-month returns no report; "
          "PASS empty-Orders boundary (report has zero rows)")


def check_null_units(sql):
    orders = [(1, 10, "2026-11-05", 100, "2026-11-06"),
              (2, 10, "2026-12-15", 200, "2026-12-16")]
    rows = execute(sql, orders, [(1, 1, None), (2, 2, None)])
    assert len(rows) == 8 and rows[7][2] is None and rows[7][3] is None, rows
    assert rows[0][2:4] == (1, 1), rows
    print("PASS P100 NULL-Quantity line rows retain KPI output with NULL units; "
          "distinct from zero OrderDetails suppression")


def main():
    sql = extract_and_adapt()
    check_sample(sql)
    check_missing_units(sql)
    check_shorter_month_and_dates(sql)
    check_missing_prior_and_empty(sql)
    check_null_units(sql)
    print("PARTIAL P100 only: 5 bounded fixture groups. "
          "No native PostgreSQL/provider PDF/full dataset/learner grade.")


if __name__ == "__main__":
    main()
