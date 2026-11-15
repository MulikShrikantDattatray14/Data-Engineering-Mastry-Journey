#!/usr/bin/env python3
"""Source-pinned native PostgreSQL 16 replay: PNP Q081/Q082, reviewer-only fixtures.

Executes the preserved supplier-attributed queries unchanged against transaction-local
test tables. Does not establish original-CSV output, graded official correctness,
PDF image parity, historical student solution or independent mastery.
"""
import hashlib
import os
import re
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCES = {
    81: ("12. Dates and Time/P081. Year-to-date vs same period last year.md",
         "054faf9e755d6f7212a7c8906be5165aa922abf8"),
    82: ("9. Windowing Functions/P082. Each customer's favourite category.md",
         "b12c819076c2418c805dd88a020278c3007a85e0"),
}
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def source_key():
    assert git_blob(KEY) == KEY_SHA, "supplied answer archive changed"
    entire = KEY.read_text(encoding="utf-8")
    queries = {}
    for n, (rel, pin) in SOURCES.items():
        path = BASE / rel
        assert git_blob(path) == pin, f"Q{n} original question changed"
        statement = path.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{n:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output",
                       "## My solution — SQLite\n\nPending.",
                       "## My solution — SQL Server\n\nPending.",
                       "## Official solution\n\nPending"):
            assert marker in statement, (n, marker)
        match = re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)",
                          entire)
        assert match, f"no source key Q{n}"
        queries[n] = match.group(1).strip()
        assert queries[n].startswith("WITH ") and queries[n].endswith(";")
    assert "a.ytd_end - INTERVAL '1 year'" in queries[81]
    assert "NULLIF(t.prior_ytd_value, 0)" in queries[81]
    assert "COUNT(DISTINCT o.OrderID)" in queries[82]
    assert "cc.last_bought DESC," in queries[82]  # no NULLS LAST
    assert "COALESCE(cat.CategoryName, 'Unmapped')" in queries[82]
    return queries


SQL = source_key()


def connect():
    return psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
        autocommit=True)


def replay(n, orders=(), details=(), products=(), categories=()):
    """Test-only schema mirrors relevant original column names and types."""
    with connect() as conn:
        with conn.transaction():
            if n == 81:
                conn.execute("CREATE TEMP TABLE Orders("
                             "OrderID INT PRIMARY KEY, OrderDate DATE,"
                             " Total_Order_Amount NUMERIC(12,2)) ON COMMIT DROP")
            else:
                conn.execute("CREATE TEMP TABLE Orders("
                             "OrderID INT PRIMARY KEY, CustomerID INT, OrderDate DATE)"
                             " ON COMMIT DROP")
                conn.execute("CREATE TEMP TABLE OrderDetails("
                             "OrderDetailID INT PRIMARY KEY, OrderID INT,"
                             " ProductID INT, Quantity INT) ON COMMIT DROP")
                conn.execute("CREATE TEMP TABLE Products("
                             "ProductID INT PRIMARY KEY, CategoryID INT) ON COMMIT DROP")
                conn.execute("CREATE TEMP TABLE Category("
                             "CategoryID INT PRIMARY KEY, CategoryName VARCHAR(50))"
                             " ON COMMIT DROP")
            with conn.cursor() as cur:
                if orders:
                    cur.executemany(
                        "INSERT INTO Orders VALUES (" +
                        ",".join(["%s"] * len(orders[0])) + ")", orders)
                if n == 82:
                    for table, rows in (
                        ("OrderDetails", details),
                        ("Products", products),
                        ("Category", categories),
                    ):
                        if rows:
                            cur.executemany(
                                "INSERT INTO " + table + " VALUES (" +
                                ",".join(["%s"] * len(rows[0])) + ")", rows)
            return conn.execute(SQL[n]).fetchall()


D = Decimal


class SourceQ081Q082NativePostgres(unittest.TestCase):
    def test_01_immutable_source_blobs_and_pending_historical_state(self):
        self.assertEqual(git_blob(KEY), KEY_SHA)
        for path, sha in SOURCES.values():
            self.assertEqual(git_blob(BASE / path), sha)

    def test_02_native_postgresql_16_not_sqlite_translation(self):
        with connect() as conn:
            version = int(conn.execute("SHOW server_version_num").fetchone()[0])
        self.assertTrue(160000 <= version < 170000, version)

    def test_03_q081_original_leap_day_illustration_and_prior_march_exclusion(self):
        got = replay(81, orders=[
            (1, "2023-01-10", 100), (2, "2023-03-01", 200),
            (3, "2024-01-10", 150), (4, "2024-02-29", 150)])
        self.assertEqual(got, [(
            date(2024, 1, 1), date(2024, 2, 29),
            date(2023, 1, 1), date(2023, 2, 28),
            2, D("300"), 1, D("100"), D("200.00"))])

    def test_04_q081_nonleap_inclusive_latest_and_prior_boundary(self):
        got = replay(81, orders=[
            (1, "2025-01-01", 100), (2, "2025-07-10", 150),
            (3, "2025-07-11", 1000), (4, "2026-01-01", 200),
            (5, "2026-07-10", 300)])
        self.assertEqual(got, [(
            date(2026, 1, 1), date(2026, 7, 10),
            date(2025, 1, 1), date(2025, 7, 10),
            2, D("500"), 2, D("250"), D("100.00"))])

    def test_05_q081_no_prior_orders_returns_null_growth_not_infinity(self):
        got = replay(81, orders=[(1, "2026-08-01", 250)])
        self.assertEqual(got[0][4:], (1, D("250"), 0, D("0"), None))

    def test_06_q081_zero_valued_prior_has_undefined_growth(self):
        got = replay(81, orders=[
            (1, "2025-02-01", 0), (2, "2026-02-01", 50)])
        self.assertEqual(got[0][4:], (1, D("50"), 1, D("0"), None))

    def test_07_q081_null_amount_counts_order_but_not_value(self):
        got = replay(81, orders=[
            (1, "2025-01-10", 100), (2, "2026-01-10", None),
            (3, "2026-01-10", 50)])
        self.assertEqual(got[0][4:], (2, D("50"), 1, D("100"), D("-50.00")))

    def test_08_q081_all_null_order_dates_yield_null_period_row(self):
        got = replay(81, orders=[(1, None, 100)])
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0], (None, None, None, None, 0, D("0"), 0, D("0"), None))
        # This is a missing-anchor policy gap, not evidence of bad source CSV data.

    def test_09_q081_empty_orders_yield_null_period_row(self):
        self.assertEqual(replay(81), [
            (None, None, None, None, 0, D("0"), 0, D("0"), None)])

    def test_10_q082_original_audio_two_of_three_illustration(self):
        got = replay(82,
            categories=[(1, "Audio"), (2, "Home")],
            products=[(101, 1), (102, 2)],
            orders=[(1, 10, "2026-01-01")],
            details=[(1, 1, 101, 2), (2, 1, 102, 1)])
        self.assertEqual(got, [(10, "Audio", 2, D("66.67"))])

    def test_11_q082_more_distinct_orders_breaks_equal_units_tie(self):
        got = replay(82,
            categories=[(1, "Alpha"), (2, "Beta")],
            products=[(101, 1), (102, 2)],
            orders=[(1, 10, "2026-01-03"), (2, 10, "2026-01-01"),
                    (3, 10, "2026-01-02")],
            details=[(1, 1, 101, 2), (2, 2, 102, 1), (3, 3, 102, 1)])
        self.assertEqual(got, [(10, "Beta", 2, D("50.00"))])

    def test_12_q082_latest_valid_date_breaks_units_and_order_tie(self):
        got = replay(82,
            categories=[(1, "Alpha"), (2, "Beta")],
            products=[(101, 1), (102, 2)],
            orders=[(1, 10, "2026-01-01"), (2, 10, "2026-01-05")],
            details=[(1, 1, 101, 2), (2, 2, 102, 2)])
        self.assertEqual(got, [(10, "Beta", 2, D("50.00"))])

    def test_13_q082_alphabetical_final_tie_break(self):
        got = replay(82,
            categories=[(1, "Beta"), (2, "Alpha")],
            products=[(101, 1), (102, 2)],
            orders=[(1, 10, "2026-01-01")],
            details=[(1, 1, 101, 1), (2, 1, 102, 1)])
        self.assertEqual(got, [(10, "Alpha", 1, D("50.00"))])

    def test_14_q082_missing_product_bucket_is_unmapped(self):
        got = replay(82,
            categories=[(1, "Audio")],
            products=[(101, 1)],
            orders=[(1, 10, "2026-01-01")],
            details=[(1, 1, 101, 1), (2, 1, 999, 3)])
        self.assertEqual(got, [(10, "Unmapped", 3, D("75.00"))])

    def test_15_q082_null_latest_order_date_sorts_before_real_date(self):
        got = replay(82,
            categories=[(1, "Alpha"), (2, "Beta")],
            products=[(101, 1), (102, 2)],
            orders=[(1, 10, None), (2, 10, "2026-01-02")],
            details=[(1, 1, 101, 2), (2, 2, 102, 2)])
        self.assertEqual(got, [(10, "Alpha", 2, D("50.00"))])
        # PostgreSQL ORDER BY last_bought DESC defaults NULLS FIRST.
        # If most-recent means valid dated purchase, Beta should win instead.
        # Original loader allows nullable OrderDate; real CSV population unverified.

    def test_16_q082_zero_quantity_yields_undefined_percentage(self):
        got = replay(82,
            categories=[(1, "Audio")], products=[(101, 1)],
            orders=[(1, 10, "2026-01-01")],
            details=[(1, 1, 101, 0)])
        self.assertEqual(got, [(10, "Audio", 0, None)])

    def test_17_q082_unmapped_label_collision_combines_name_and_unknown(self):
        got = replay(82,
            categories=[(1, "Unmapped"), (2, "Audio")],
            products=[(101, 1), (102, 2)],
            orders=[(1, 10, "2026-01-01")],
            details=[(1, 1, 101, 2), (2, 1, 999, 3), (3, 1, 102, 4)])
        self.assertEqual(got, [(10, "Unmapped", 5, D("55.56"))])
        # Same display name merges actual category with missing-product bucket.

    def test_18_q082_null_customer_excluded_as_no_known_banner_identity(self):
        got = replay(82,
            categories=[(1, "Audio")], products=[(101, 1)],
            orders=[(1, None, "2026-01-01"), (2, 10, "2026-01-01")],
            details=[(1, 1, 101, 7), (2, 2, 101, 2)])
        self.assertEqual(got, [(10, "Audio", 2, D("100.00"))])

    def test_19_q082_no_details_returns_no_favourite(self):
        self.assertEqual(replay(82,
            categories=[(1, "Audio")], products=[(101, 1)],
            orders=[(1, 10, "2026-01-01")]), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
