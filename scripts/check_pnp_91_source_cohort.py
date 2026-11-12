#!/usr/bin/env python3
"""Q091: read-only supplied-key cohort-maturity regression and source/sample conflict.

The actual archived PostgreSQL query is extracted at test time and translated
with narrowly asserted date/series substitutions for SQLite fixtures. These
checks are NOT native PostgreSQL, official grading or a learner completion.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
QUESTION = BASE / ("12. Dates and Time/"
                   "P091. Cumulative value per customer by cohort (LTV curve).md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
SOURCE_SHA = "cf11e56982938b3227f711e00534237f88d451aa"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"


def blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def pinned_original_sql() -> str:
    assert blob_sha(QUESTION) == SOURCE_SHA, "Q091 original question changed"
    assert blob_sha(KEY) == KEY_SHA, "Supplied PostgreSQL source key changed"
    q = QUESTION.read_text(encoding="utf-8-sig")
    assert "# PNP Q091." in q
    assert "NOT SOLVED YET" in q
    assert "## Official solution\n\nPending" in q
    assert "## My solution — SQLite\n\nPending" in q
    assert "## My solution — SQL Server\n\nPending" in q
    assert "2025-01-01" in q and "2026-01-01" in q
    src = KEY.read_text(encoding="utf-8-sig")
    match = re.search(r"^-- Q91\. [^\n]*\n(.*?)(?=^-- Q92\.|\Z)",
                      src, re.M | re.S)
    assert match, "Missing Q91 exact original source-key section"
    sql = match.group(1).strip()
    assert sql.startswith("WITH anchor AS") and sql.endswith(";")
    return sql


def replace_exact(sql: str, old: str, new: str, count: int = 1) -> str:
    assert sql.count(old) == count, "Unexpected supplied-key dialect drift: " + old
    return sql.replace(old, new)


def sqlite_date_translation(sql: str) -> str:
    """Preserve the supplied CTE/window/business logic; adapt only PG syntax."""
    sql = replace_exact(
        sql,
        "(DATE_TRUNC('month', MAX(o.OrderDate) + 1) - INTERVAL '1 month')::date",
        "(CASE WHEN MAX(o.OrderDate) = "
        "date(MAX(o.OrderDate), 'start of month', '+1 month', '-1 day') "
        "THEN date(MAX(o.OrderDate), 'start of month') "
        "ELSE date(MAX(o.OrderDate), 'start of month', '-1 month') END)")
    sql = replace_exact(sql, "DATE_TRUNC('month', MIN(o.OrderDate))::date",
                        "date(MIN(o.OrderDate), 'start of month')")
    sql = replace_exact(
        sql, "DATE_TRUNC('quarter', fo.first_month)::date",
        "date(fo.first_month, 'start of year', printf('+%d months', "
        "3 * CAST((CAST(strftime('%m', fo.first_month) AS INTEGER) - 1) / 3 "
        "AS INTEGER)))", count=2)
    sql = replace_exact(
        sql, "EXTRACT(YEAR  FROM o.OrderDate) - EXTRACT(YEAR  FROM fo.first_month)",
        "CAST(strftime('%Y', o.OrderDate) AS INTEGER) - "
        "CAST(strftime('%Y', fo.first_month) AS INTEGER)")
    sql = replace_exact(
        sql, "EXTRACT(MONTH FROM o.OrderDate) - EXTRACT(MONTH FROM fo.first_month)",
        "CAST(strftime('%m', o.OrderDate) AS INTEGER) - "
        "CAST(strftime('%m', fo.first_month) AS INTEGER)")
    sql = replace_exact(sql, "oo.month_offset::int", "oo.month_offset")
    series = "SELECT 0 AS month_offset" + "".join(
        f" UNION ALL SELECT {n}" for n in range(1, 13))
    sql = replace_exact(
        sql, "CROSS JOIN generate_series(0, 12) AS m(month_offset)",
        "CROSS JOIN (" + series + ") AS m")
    maturity = re.compile(
        r"\(s\.cohort_quarter \+ INTERVAL '2 months'\s*"
        r"\+ s\.month_offset \* INTERVAL '1 month'\)::date")
    sql, n = maturity.subn(
        "date(s.cohort_quarter, '+2 months', "
        "printf('+%d months', s.month_offset))", sql)
    assert n == 1, "Unexpected source-key maturity expression"
    for token in ("DATE_TRUNC", "EXTRACT(", "INTERVAL ", "::", "generate_series"):
        assert token not in sql, "Unadapted PG syntax: " + token
    assert "FROM curve AS cv" in sql
    assert "cv.is_complete" in sql
    return sql


def execute(sql: str, orders: list[tuple]) -> list[tuple]:
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE Orders (OrderID INTEGER, CustomerID INTEGER, "
                   "OrderDate TEXT, Total_Order_Amount REAL)")
        db.executemany("INSERT INTO Orders VALUES (?, ?, ?, ?)", orders)
        return db.execute(sql).fetchall()


def check() -> None:
    original = pinned_original_sql()
    print("PASS Q091 original question/source key Git blobs and Pending statuses")
    sql = sqlite_date_translation(original)
    original_sample = [
        (1, 10, "2025-01-05", 100),
        (2, 10, "2025-04-05", 50),
        (3, 10, "2026-01-31", 50),
        (4, 20, "2026-01-10", 80),
    ]
    sample_key_result = [
        ("2025-01-01", 1, 100, 150, 150, None),
        ("2026-01-01", 1, None, None, None, None),
    ]
    actual = execute(sql, original_sample)
    assert actual == sample_key_result, (actual, sample_key_result)
    # The original source illustration claims m12=200 and m0=80 instead.
    source_claim = [
        ("2025-01-01", 1, 100, 150, 150, 200),
        ("2026-01-01", 1, 80, None, None, None),
    ]
    assert actual != source_claim
    assert actual[0][:5] == source_claim[0][:5]
    assert actual[0][5] is None and source_claim[0][5] == 200
    assert actual[1][2] is None and source_claim[1][2] == 80
    print("PASS Q091 original illustration: exact key reproduces TWO "
          "documented source/output conflicts (not a task pass)")
    mature = original_sample + [(5, 30, "2027-01-31", 60)]
    expected_mature = [
        ("2025-01-01", 1, 100, 150, 150, 200),
        ("2026-01-01", 1, 80, 80, 80, None),
        ("2027-01-01", 1, None, None, None, None),
    ]
    result = execute(sql, mature)
    assert result == expected_mature, (result, expected_mature)
    print("PASS Q091 independent later-anchor fixture: mature/immature "
          "quarter thresholds")
    assert execute(sql, []) == []
    print("PASS Q091 empty Orders boundary (0 cohort rows)")
    print("Q091 remains NOT official-output verified or independently learner-solved; "
          "native PostgreSQL/PDF/full-dataset parity pending")


if __name__ == "__main__":
    check()
