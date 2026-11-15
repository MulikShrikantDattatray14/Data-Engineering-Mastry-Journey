#!/usr/bin/env python3
"""Independent source-pinned, native PostgreSQL 16 contract probes: PNP Q037/071/072.

Runs the UNMODIFIED bundled supplier-key SQL against tiny, explicit, auditor-created
fixtures in temporary transaction-scoped tables. Source illustrations are replayed,
then data-quality counterexamples are independently checked. This is not a full
Commerce v2 / rendered PDF parity check, authenticated provider grading, a
learner submission, or mastery. Original archives and learner state are read-only.
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
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
SOURCE_PINS = {
    37: ("14. Data Quality and Deduplication/"
         "P037. Prove no order was paid with a method that is not allowed.md",
         "13de904886a87807a7c8ea3dc6efe0a6b538c670"),
    71: ("14. Data Quality and Deduplication/"
         "P071. Deduplicate customer accounts by email.md",
         "d2cae3c82004124d3fe445ea5b65eb664b0ff952"),
    72: ("14. Data Quality and Deduplication/"
         "P072. Same product on several lines of one order split or duplicate.md",
         "62250373aafa5402aa879a731f4fafe40165a7f4"),
}
DDL = {
    37: (
        "CREATE TEMP TABLE Payments(PaymentID INTEGER,PaymentType TEXT,Allowed TEXT) ON COMMIT DROP",
        "CREATE TEMP TABLE Orders(OrderID INTEGER,PaymentID INTEGER,Total_Order_Amount NUMERIC) ON COMMIT DROP",
    ),
    71: (
        "CREATE TEMP TABLE Customers(CustomerID INTEGER,Email TEXT,DateEntered DATE) ON COMMIT DROP",
    ),
    72: (
        "CREATE TEMP TABLE OrderDetails(OrderDetailID INTEGER,OrderID INTEGER,ProductID INTEGER,"
        "Quantity INTEGER,SupplierID INTEGER) ON COMMIT DROP",
    ),
}


def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def load_source_sql():
    assert git_blob(KEY) == KEY_SHA, "original supplier-key archive drift"
    key = KEY.read_text(encoding="utf-8")
    out = {}
    for n, (relative, pin) in SOURCE_PINS.items():
        path = BASE / relative
        assert git_blob(path) == pin, f"Q{n}: original statement drift"
        text = path.read_text(encoding="utf-8")
        for marker in (
            f"# PNP Q{n:03d}.", "NOT SOLVED YET",
            "### Sample input and expected output", "## Schema",
            "## My solution — SQLite\n\nPending.",
            "## My solution — SQL Server\n\nPending.",
            "## Official solution\n\nPending",
        ):
            assert marker in text, f"Q{n}: missing historical/source marker {marker!r}"
        m = re.search(
            rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key
        )
        assert m, f"Q{n}: supplier-key excerpt absent"
        sql = m.group(1).strip()
        assert sql.startswith("WITH ") and sql.endswith(";"), n
        out[n] = sql
    assert "COALESCE(UPPER(TRIM(CAST(pay.Allowed AS VARCHAR)))" in out[37]
    assert "NULLS LAST" in out[71]
    assert "COUNT(DISTINCT od.SupplierID)" in out[72]
    return out


SQL = load_source_sql()


def native(n, tables, diagnostics=()):
    """Run exact source SQL in a disposable transaction; no persistent DB writes."""
    with psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
        autocommit=True,
    ) as conn:
        with conn.transaction():
            for ddl in DDL[n]:
                conn.execute(ddl)
            for table, rows in tables.items():
                if not rows:
                    continue
                bind = ",".join(["%s"] * len(rows[0]))
                with conn.cursor() as cur:
                    cur.executemany(f"INSERT INTO {table} VALUES ({bind})", rows)
            actual = conn.execute(SQL[n]).fetchall()
            extra = [conn.execute(statement).fetchall() for statement in diagnostics]
    return actual, extra


class NativeQualityKeyForensics(unittest.TestCase):
    def test_01_source_blob_pins_and_pending_learner_status(self):
        self.assertEqual(set(SQL), {37, 71, 72})
        self.assertEqual(git_blob(KEY), KEY_SHA)
        for n, (relative, expected) in SOURCE_PINS.items():
            self.assertEqual(git_blob(BASE / relative), expected, n)

    def test_02_native_postgres_version_16(self):
        with psycopg.connect(
            host=os.getenv("PGHOST", "127.0.0.1"),
            port=os.getenv("PGPORT", "5432"),
            dbname=os.getenv("PGDATABASE", "audit"),
            user=os.getenv("PGUSER", "audit"),
            password=os.getenv("PGPASSWORD", "audit"),
        ) as conn:
            version = int(conn.execute("SHOW server_version_num").fetchone()[0])
            self.assertTrue(160000 <= version < 170000, version)

    def test_03_q037_original_three_payment_illustration(self):
        rows, _ = native(37, {
            "Payments": [(1, "UPI", "Y"), (2, "Card", "N"), (3, "Cash", None)],
            "Orders": [(10, 1, 100), (11, 2, 50)],
        })
        self.assertEqual(rows, [
            (2, "Card", "N", False, 1, Decimal("50"), "VIOLATION: not allowed but used"),
            (1, "UPI", "Y", True, 1, Decimal("100"), "OK"),
            (3, "Cash", None, False, 0, Decimal("0"), "Not allowed, unused"),
        ])

    def test_04_q037_no_yes_true_one_blank_null_flag_normalization(self):
        rows, _ = native(37, {
            "Payments": [
                (1, "No", "No"), (2, "Yes", " yes "), (3, "True", "TRUE"),
                (4, "One", "1"), (5, "Blank", "  "), (6, "Missing", None)
            ],
            "Orders": [(10, 1, 10), (11, 5, 20), (12, 2, 30)],
        })
        self.assertEqual([(r[0], r[3], r[6]) for r in rows], [
            (1, False, "VIOLATION: not allowed but used"),
            (5, False, "VIOLATION: not allowed but used"),
            (2, True, "OK"),
            (3, True, "Allowed, unused"),
            (4, True, "Allowed, unused"),
            (6, False, "Not allowed, unused"),
        ])

    def test_05_q037_orphan_payment_id_not_reported_by_payment_dimension(self):
        rows, diagnostic = native(37, {
            "Payments": [(1, "UPI", "Y"), (2, "Card", "N")],
            "Orders": [(10, 999, 80)],
        }, diagnostics=[(
            "SELECT o.OrderID FROM Orders o "
            "LEFT JOIN Payments p ON p.PaymentID=o.PaymentID "
            "WHERE p.PaymentID IS NULL ORDER BY o.OrderID"
        )])
        # Exact source output contains no violation, despite an orphan payment reference.
        self.assertEqual([(r[0], r[6]) for r in rows],
                         [(1, "Allowed, unused"), (2, "Not allowed, unused")])
        self.assertEqual(diagnostic[0], [(10,)])

    def test_06_q037_null_amount_and_duplicate_orders_at_header_grain(self):
        rows, _ = native(37, {
            "Payments": [(1, "Card", "N")],
            "Orders": [(11, 1, None), (12, 1, 20), (13, 1, 30)],
        })
        self.assertEqual(rows, [
            (1, "Card", "N", False, 3, Decimal("50"), "VIOLATION: not allowed but used")
        ])

    def test_07_q071_original_email_group_illustration(self):
        rows, _ = native(71, {"Customers": [
            (1, " ASHA@example.com ", "2026-01-01"),
            (2, "asha@example.com", "2026-01-05"),
            (3, "ASHA@EXAMPLE.COM", "2026-01-01"),
            (4, None, "2026-01-02"),
        ]})
        self.assertEqual(rows, [
            ("asha@example.com", 1, 2, date(2026, 1, 1), date(2026, 1, 5)),
            ("asha@example.com", 1, 3, date(2026, 1, 1), date(2026, 1, 1)),
        ])

    def test_08_q071_blank_missing_email_excluded_and_id_tiebreaker(self):
        rows, _ = native(71, {"Customers": [
            (10, " x@y.co ", "2026-01-01"),
            (4, "X@Y.CO", "2026-01-01"),
            (5, "x@y.co", "2026-02-01"),
            (6, " ", "2025-01-01"),
            (7, None, "2025-01-01"),
            (8, "different@y.co", "2025-01-01"),
        ]})
        self.assertEqual(rows, [
            ("x@y.co", 4, 5, date(2026, 1, 1), date(2026, 2, 1)),
            ("x@y.co", 4, 10, date(2026, 1, 1), date(2026, 1, 1)),
        ])

    def test_09_q071_missing_registration_date_uses_explicit_nulls_last_policy(self):
        rows, _ = native(71, {"Customers": [
            (1, "x@example.com", None),
            (2, "X@EXAMPLE.COM", "2026-01-01"),
            (3, " x@example.com ", None),
        ]})
        self.assertEqual(rows, [
            ("x@example.com", 2, 1, date(2026, 1, 1), None),
            ("x@example.com", 2, 3, date(2026, 1, 1), None),
        ])
        # This is a defensible supplier-key policy; the question does not
        # independently define how a NULL registration date proves "earliest".

    def test_10_q072_original_split_vs_same_supplier_illustration(self):
        rows, _ = native(72, {"OrderDetails": [
            (1, 10, 101, 2, 7), (2, 10, 101, 3, 7),
            (3, 20, 102, 1, 7), (4, 20, 102, 4, 8),
        ]})
        self.assertEqual(rows, [
            (1, 10, 101, 2, 7, 1, 2, 5, "Same supplier: consolidate", "keep, set quantity to total"),
            (2, 10, 101, 3, 7, 2, 2, 5, "Same supplier: consolidate", "remove"),
            (3, 20, 102, 1, 7, 1, 2, 5, "Split across suppliers", "keep"),
            (4, 20, 102, 4, 8, 2, 2, 5, "Split across suppliers", "keep"),
        ])

    def test_11_q072_mixed_known_and_null_supplier_is_not_proof_of_same_source(self):
        rows, diag = native(72, {"OrderDetails": [
            (1, 10, 101, 2, None), (2, 10, 101, 3, 7),
        ]}, diagnostics=[(
            "SELECT COUNT(DISTINCT SupplierID),"
            "COUNT(*) FILTER (WHERE SupplierID IS NULL) FROM OrderDetails"
        )])
        self.assertEqual([(r[0], r[8], r[9]) for r in rows], [
            (1, "Same supplier: consolidate", "keep, set quantity to total"),
            (2, "Same supplier: consolidate", "remove"),
        ])
        self.assertEqual(diag[0], [(1, 1)])  # NULL excluded by DISTINCT, unknown supplier remains.

    def test_12_q072_all_unknown_supplier_ids_also_consolidate(self):
        rows, diag = native(72, {"OrderDetails": [
            (1, 10, 101, 2, None), (2, 10, 101, 3, None),
        ]}, diagnostics=["SELECT COUNT(DISTINCT SupplierID) FROM OrderDetails"])
        self.assertEqual(diag[0], [(0,)])
        self.assertEqual([r[8] for r in rows], ["Same supplier: consolidate"] * 2)

    def test_13_q072_null_group_keys_are_grouped_but_lost_on_equality_rejoin(self):
        rows, diag = native(72, {"OrderDetails": [
            (1, None, 101, 2, 7), (2, None, 101, 3, 8),
            (3, 20, None, 4, 7), (4, 20, None, 5, 8),
        ]}, diagnostics=[(
            "SELECT OrderID,ProductID,COUNT(*) FROM OrderDetails "
            "GROUP BY OrderID,ProductID HAVING COUNT(*)>1 "
            "ORDER BY OrderID NULLS LAST,ProductID NULLS LAST"
        )])
        self.assertEqual(len(diag[0]), 2)
        self.assertEqual(rows, [])

    def test_14_q072_null_quantities_make_sum_partial_not_safe_cleanup_instruction(self):
        rows, diag = native(72, {"OrderDetails": [
            (1, 10, 101, None, 7), (2, 10, 101, 5, 7),
        ]}, diagnostics=["SELECT COUNT(*) FILTER (WHERE Quantity IS NULL) FROM OrderDetails"])
        self.assertEqual(diag[0], [(1,)])
        self.assertEqual([(r[0], r[7], r[9]) for r in rows], [
            (1, 5, "keep, set quantity to total"), (2, 5, "remove")
        ])

    def test_15_q072_three_lines_deterministic_position_and_total(self):
        rows, _ = native(72, {"OrderDetails": [
            (9, 10, 101, 10, 7), (2, 10, 101, 20, 7), (5, 10, 101, 30, 7),
        ]})
        self.assertEqual([(r[0], r[5], r[6], r[7], r[9]) for r in rows], [
            (2, 1, 3, 60, "keep, set quantity to total"),
            (5, 2, 3, 60, "remove"),
            (9, 3, 3, 60, "remove"),
        ])


if __name__ == "__main__":
    unittest.main(verbosity=2)
