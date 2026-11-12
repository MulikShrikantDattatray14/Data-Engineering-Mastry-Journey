#!/usr/bin/env python3
"""PARTIAL PNP Q089 audit: immutable-key batch/seed replays plus isolated UPSERT model.

The original PostgreSQL key is extracted and SHA-verified. Its original seed
SELECT and batch/watermark CTE are executed with *only asserted date syntax
substitutions* in SQLite. The data-modifying CTE/ON CONFLICT/RETURNING portion
cannot be executed inside SQLite; mutation and action classification below are
a transparent independent Python model, NOT native PostgreSQL validation.
Synthetic fixture success is not an official answer or learner completion.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCE = BASE / ("14. Data Quality and Deduplication/"
                 "P089. Incremental load with a watermark and lookback.md")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
SOURCE_SHA = "dc820d26afb08381d923f2cd215a0d64297a8d91"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
COLUMNS = ("OrderID", "CustomerID", "PaymentID", "OrderDate", "ShipperID",
           "Total_Order_Amount", "ShipDate", "DeliveryDate")


def blob_sha(path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()


def replace_once(sql, old, new):
    assert sql.count(old) == 1, ("original key shape drifted", old, sql.count(old))
    return sql.replace(old, new)


def extract_source_sql():
    assert blob_sha(SOURCE) == SOURCE_SHA, "Q089 original question blob changed"
    assert blob_sha(KEY) == KEY_SHA, "Q089 archived supplied key blob changed"
    src = SOURCE.read_text(encoding="utf-8")
    for marker in ("# PNP Q089.", "21-day lookback", "NULL OrderDate",
                   "inserted", "updated", "unchanged", "NOT SOLVED YET",
                   "## Official solution", "Pending"):
        assert marker in src, ("original question marker absent", marker)
    saved = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q89\.[^\n]*\n(.*?)(?=^-- Q90\.)", saved)
    assert match, "Q89 answer-key section missing"
    sql = match.group(1)
    for token in ("CREATE TEMP TABLE orders_target", "LIKE Orders INCLUDING ALL",
                  "MAX(src.OrderDate) - 14 AS run_date",
                  "MAX(t.OrderDate)", "SELECT 21 AS lookback_days",
                  "OR o.OrderDate IS NULL", "ON CONFLICT (OrderID) DO UPDATE",
                  "IS DISTINCT FROM", "RETURNING t.OrderID",
                  "WHEN u.OrderID IS NULL THEN 'unchanged'",
                  "WHEN b.already_loaded  THEN 'updated'",
                  "ELSE 'inserted'", "VALUES (1, 'inserted'), (2, 'updated'), (3, 'unchanged')"):
        assert token in sql, ("archived SQL expected token absent", token)
    seed = re.search(r"(?s)(INSERT INTO orders_target\s*\n"
                     r"\s*\(OrderID, CustomerID, PaymentID, OrderDate, ShipperID,"
                     r".*?WHERE o.OrderDate <= prev.run_date;)", sql)
    assert seed, "original prior-run INSERT...SELECT absent"
    seed_sql = replace_once(seed.group(1), "MAX(src.OrderDate) - 14",
                            "DATE(MAX(src.OrderDate), '-14 days')")
    batch = re.search(r"(?s)(WITH params AS \(.*?\n\)),\s*upserted AS \(", sql)
    assert batch, "original read-only watermark/batch CTE absent"
    batch_sql = batch.group(1)
    batch_sql = replace_once(batch_sql, "DATE '1900-01-01'", "'1900-01-01'")
    batch_sql = replace_once(batch_sql, "w.high_water_date - p.lookback_days",
                             "DATE(w.high_water_date, '-' || p.lookback_days || ' days')")
    projection = ", ".join("b." + c for c in COLUMNS)
    batch_sql += ("\nSELECT " + projection + ", b.already_loaded"
                  "\nFROM batch AS b ORDER BY b.OrderID;")
    return seed_sql, batch_sql


def database(rows, target=()):
    c = sqlite3.connect(":memory:")
    c.execute("""CREATE TABLE Orders (
       OrderID INTEGER PRIMARY KEY, CustomerID INTEGER, PaymentID INTEGER,
       OrderDate TEXT, ShipperID INTEGER, Total_Order_Amount REAL,
       ShipDate TEXT, DeliveryDate TEXT)""")
    c.execute("""CREATE TABLE orders_target (
       OrderID INTEGER PRIMARY KEY, CustomerID INTEGER, PaymentID INTEGER,
       OrderDate TEXT, ShipperID INTEGER, Total_Order_Amount REAL,
       ShipDate TEXT, DeliveryDate TEXT, etl_updated_at INTEGER NOT NULL DEFAULT 1)""")
    c.executemany("INSERT INTO Orders VALUES (?,?,?,?,?,?,?,?)", rows)
    c.executemany("INSERT INTO orders_target VALUES (?,?,?,?,?,?,?,?,?)", target)
    return c


def snapshot(c):
    return {r[0]: r[1:] for r in c.execute(
        "SELECT OrderID, CustomerID, PaymentID, OrderDate, ShipperID, "
        "Total_Order_Amount, ShipDate, DeliveryDate, etl_updated_at "
        "FROM orders_target ORDER BY OrderID")}


def replay_modeled_upsert(c, batch_sql):
    # SQLite cannot embed a write statement as a CTE. Execute the source's
    # original batch CTE and model its null-safe row-comparison/action branch.
    counts = {"inserted": 0, "updated": 0, "unchanged": 0}
    rows = c.execute(batch_sql).fetchall()
    set_clause = ", ".join(name + "=?" for name in COLUMNS[1:])
    for row in rows:
        values, was_loaded = tuple(row[:8]), bool(row[8])
        prior = c.execute("SELECT " + ", ".join(COLUMNS[1:]) +
                          " FROM orders_target WHERE OrderID=?", (row[0],)).fetchone()
        assert was_loaded == (prior is not None), "original EXISTS predicate drift"
        if prior is None:
            action = "inserted"
            c.execute("INSERT INTO orders_target VALUES (?,?,?,?,?,?,?,?,?)",
                      (*values, 2))
        elif prior != values[1:]:
            action = "updated"
            c.execute("UPDATE orders_target SET " + set_clause +
                      ", etl_updated_at=? WHERE OrderID=?",
                      (*values[1:], 2, row[0]))
        else:
            action = "unchanged"
        counts[action] += 1
    return tuple(counts[a] for a in ("inserted", "updated", "unchanged"))


def order(id_, date, amount, customer=10):
    return (id_, customer, None, date, None, amount, None, None)


def test_illustration(batch):
    # Faithfully use the target *supplied in the question*, not the key's
    # separate automatic 14-day-old target construction.
    orders = [order(1, "2026-01-10", 100), order(2, "2026-01-11", 200),
              order(3, None, 50), order(4, "2025-12-01", 30)]
    explicit = [(*order(1, "2026-01-10", 100), 7),
                (*order(2, "2026-01-11", 150), 7),
                (*order(4, "2025-12-01", 30), 7)]
    c = database(orders, explicit)
    assert replay_modeled_upsert(c, batch) == (1, 1, 1)
    rows = snapshot(c)
    assert rows[1][-1] == 7 and rows[2][-1] == 2 and rows[3][-1] == 2
    assert rows[4][-1] == 7 and rows[2][4] == 200
    assert replay_modeled_upsert(c, batch) == (0, 0, 3)
    assert snapshot(c) == rows, "rerun modified already-synced source"
    c.close()
    print("PASS Q089 explicit source-illustration target: 1/1/1 then idempotent 0/0/3")


def test_archived_key_seed(seed, batch):
    orders = [order(1, "2026-01-10", 100), order(2, "2026-01-11", 200),
              order(3, None, 50), order(4, "2025-12-01", 30)]
    c = database(orders)
    c.execute(seed)
    assert set(snapshot(c)) == {4}, "source 14-day seed did not select only Dec-1 row"
    observed = replay_modeled_upsert(c, batch)
    assert observed == (3, 0, 1), ("unexpected original seed/batch outcome", observed)
    assert observed != (1, 1, 1), "illustration/key seed discrepancy unexpectedly vanished"
    assert replay_modeled_upsert(c, batch) == (0, 0, 3)
    c.close()
    print("REPRODUCED Q089 source-key demo seed mismatch: 3/0/1 versus pictured 1/1/1")


def test_inclusive_watermark_and_nulls(batch):
    src = [order(10, "2026-01-22", 22),
           order(11, "2026-01-01", 101),
           order(12, "2026-01-01", 12),
           order(13, "2025-12-31", 13),
           order(14, None, 14),
           order(15, None, 15)]
    tgt = [(*order(10, "2026-01-22", 22), 7),
           (*order(11, "2026-01-01", 100), 7),
           (*order(15, None, 15), 7)]
    c = database(src, tgt)
    assert replay_modeled_upsert(c, batch) == (2, 1, 2)
    rows = snapshot(c)
    assert 13 not in rows and rows[10][-1] == 7 and rows[15][-1] == 7
    assert rows[11][-1] == 2 and rows[12][-1] == 2 and rows[14][-1] == 2
    assert replay_modeled_upsert(c, batch) == (0, 0, 5)
    assert snapshot(c) == rows
    c.close()
    print("PASS Q089 >=21-day inclusive cutoff, earlier excluded, NULL dates, unchanged timestamp, rerun")


def test_empty(batch, seed):
    c = database([])
    c.execute(seed)
    assert replay_modeled_upsert(c, batch) == (0, 0, 0)
    assert snapshot(c) == {}
    c.close()
    print("PASS Q089 empty Orders: zero for all three action categories (modeled)")


def main():
    seed, batch = extract_source_sql()
    test_illustration(batch)
    test_archived_key_seed(seed, batch)
    test_inclusive_watermark_and_nulls(batch)
    test_empty(batch, seed)
    print("PARTIAL Q089: source seed and batch SQL (date-adapted) executed in "
          "SQLite; upsert modeled in Python, NOT PostgreSQL original "
          "mutation/RETURNING; original PDF/full dataset/provider parity "
          "and learner completion remain unverified.")


if __name__ == "__main__":
    main()
