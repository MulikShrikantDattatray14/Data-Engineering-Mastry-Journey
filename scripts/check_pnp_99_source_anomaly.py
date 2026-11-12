#!/usr/bin/env python3
"""Read-only, SHA-pinned partial audit of archived PNP Q099 PostgreSQL key.

Replay the original key under narrowly asserted SQLite compatibility adaptations:
ISO Monday dates, date arithmetic, a weekly generate_series recursive spine,
and sample standard deviation as a SQLite window function. This verifies bounded
local fixtures, NOT native PostgreSQL/PDF/provider output or learner mastery.
"""
import hashlib
import re
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCE = BASE / "15. Analytics and Performance/P099. Flag unusual weeks in order volume.md"
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
SOURCE_SHA = "69f4a36c43f3df6da10fd0b35a3eab302fb946d1"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def replace_n(sql, old, new, n=1):
    count = sql.count(old)
    assert count == n, ("unexpected original SQL shape", old, count, n)
    return sql.replace(old, new)


def source_sql():
    assert git_blob(SOURCE) == SOURCE_SHA, "archived original Q099 changed"
    assert git_blob(KEY) == KEY_SHA, "archived supplied PostgreSQL key changed"
    question = SOURCE.read_text(encoding="utf-8")
    for marker in ("# PNP Q099.", "previous eight weeks", "sample standard deviation",
                   "2026-03-02", "27.93", "## Schema", "NOT SOLVED YET",
                   "## Official solution", "Pending"):
        assert marker in question, ("missing immutable question marker", marker)
    saved_key = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q99\.[^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", saved_key)
    assert match, "original Q99 key section absent"
    sql = match.group(1).strip()
    assert sql.startswith("WITH bounds AS (") and sql.endswith(";")
    assert "ROWS BETWEEN 8 PRECEDING AND 1 PRECEDING" in sql
    assert "STDDEV_SAMP(w.orders) OVER prior_8w" in sql
    sql = replace_n(sql, "WITH bounds AS (", "WITH RECURSIVE bounds AS (")
    sql = replace_n(
        sql,
        "DATE_TRUNC('week', MIN(o.OrderDate) + 6)::date",
        "WEEK_START(DATE(MIN(o.OrderDate), '+6 days'))")
    sql = replace_n(
        sql,
        "DATE_TRUNC('week', MAX(o.OrderDate) - 6)::date",
        "WEEK_START(DATE(MAX(o.OrderDate), '-6 days'))")
    sql = replace_n(
        sql,
        "week_spine AS (\n"
        "    SELECT gs::date AS week_start\n"
        "    FROM bounds AS b\n"
        "    CROSS JOIN generate_series(b.first_full_week, b.last_full_week, INTERVAL '7 days') AS gs\n"
        "),",
        "week_spine(week_start) AS (\n"
        "    SELECT first_full_week FROM bounds WHERE first_full_week <= last_full_week\n"
        "    UNION ALL\n"
        "    SELECT DATE(week_start, '+7 days') FROM week_spine, bounds\n"
        "    WHERE week_start < bounds.last_full_week\n"
        "),")
    sql = replace_n(
        sql, "DATE_TRUNC('week', o.OrderDate)::date",
        "WEEK_START(o.OrderDate)", n=2)
    # Avoid SQLite/Python empty-frame window-UDF crashes: implement the
    # sample stddev identity from built-in SUM and COUNT window functions.
    # This is a scoped dialect adaptation, not a replacement source answer.
    sql = replace_n(
        sql, "STDDEV_SAMP(w.orders) OVER prior_8w",
        "CASE WHEN COUNT(*) OVER prior_8w >= 2 THEN "
        "SQRT((SUM(1.0*w.orders*w.orders) OVER prior_8w "
        "- (SUM(1.0*w.orders) OVER prior_8w * SUM(1.0*w.orders) OVER prior_8w) "
        "/ (COUNT(*) OVER prior_8w)) / ((COUNT(*) OVER prior_8w) - 1)) END")
    for unsupported in ("DATE_TRUNC(", "generate_series(", "::date", "INTERVAL '7 days'", "STDDEV_SAMP("):
        assert unsupported not in sql, unsupported
    print("PASS Q099 source and supplied-key Git blob identity; original historical Pending preserved")
    print("SCOPE Q099: asserted PG-to-SQLite week/date/spine/stddev adaptations; original remaining SQL preserved")
    return sql


def iso_week_start(raw):
    if raw is None:
        return None
    day = date.fromisoformat(str(raw)[:10])
    return (day - timedelta(days=day.weekday())).isoformat()



def execute(sql, orders):
    connection = sqlite3.connect(":memory:")
    try:
        connection.create_function("WEEK_START", 1, iso_week_start)
        connection.execute("CREATE TABLE Orders(OrderID INTEGER, OrderDate TEXT)")
        if orders:
            connection.executemany("INSERT INTO Orders VALUES (?,?)", orders)
        return connection.execute(sql).fetchall()
    finally:
        connection.close()


def weekly_orders(counts, first_monday="2026-01-05"):
    start = date.fromisoformat(first_monday)
    records = []
    for index, count in enumerate(counts):
        monday = start + timedelta(days=7 * index)
        for j in range(count):
            # Last order on Sunday proves the last data week is complete.
            day = monday + timedelta(days=6 if j == count - 1 else 0)
            records.append((len(records) + 1, day.isoformat()))
    return records


def main():
    sql = source_sql()

    # The source compact table gives weekly counts, not individual date rows.
    # Place the last order each week on Sunday so the last observed week is
    # indeed complete through 2026-03-08, as explicitly stated in the source.
    sample = execute(sql, weekly_orders([10, 10, 10, 10, 10, 10, 10, 11, 20]))
    assert len(sample) == 9, sample
    assert sample[0] == ("2026-03-02", 20, 10.13, 0.35, 27.93, 1), sample[0]
    assert all(row[-1] is None for row in sample[1:]), sample
    print("PASS Q099 source illustrated last-week result (plus 8 earlier weeks required by return-all task)")

    missing_week = execute(sql, weekly_orders([8, 8, 8, 8, 0, 8, 8, 8, 8, 8, 100]))
    assert len(missing_week) == 11, missing_week
    feb2 = next(row for row in missing_week if row[0] == "2026-02-02")
    assert feb2[1] == 0 and feb2[-1] is None, feb2
    assert missing_week[0][0] == "2026-03-16" and missing_week[0][1] == 100
    assert missing_week[0][-1] == 1 and missing_week[0][4] is not None, missing_week[0]
    print("PASS Q099 independent zero-order missing-week calendar spine and extreme spike")

    flat = execute(sql, weekly_orders([10] * 9))
    assert len(flat) == 9 and flat[0] == ("2026-03-02", 10, 10.0, 0.0, None, None), flat
    print("PASS Q099 constant prior-eight baseline: zero spread yields NULL score and flag")

    # Both Jan 5 and Mar 2 boundary weeks are incomplete on these data.
    partial = execute(sql, [(1, "2026-01-06"), (2, "2026-01-12"),
                            (3, "2026-02-02"), (4, "2026-03-04")])
    assert len(partial) == 7, partial
    assert partial[0][0] == "2026-02-23" and partial[-1][0] == "2026-01-12"
    assert next(r for r in partial if r[0] == "2026-02-02")[1] == 1
    assert sum(r[1] for r in partial) == 2, partial
    print("PASS Q099 independent incomplete beginning/end weeks excluded, intermediate zero weeks retained")

    assert execute(sql, []) == []
    assert execute(sql, [(1, None), (2, None)]) == []
    assert execute(sql, [(1, "2026-01-06")]) == []
    print("PASS Q099 empty, all-NULL date and single-incomplete-week boundaries")
    print("PARTIAL Q099: five bounded groups; original SQL adapted for SQLite, not native PG/PDF, no learner solve.")


if __name__ == "__main__":
    main()
