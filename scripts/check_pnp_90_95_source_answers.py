#!/usr/bin/env python3
"""Bounded, read-only source-key assessment: PNP Q090 / Q095.

Q090 uses an audited, column-for-column UNION ALL emulation of PostgreSQL
CROSS JOIN LATERAL (VALUES...), NOT the native PostgreSQL operator. Q095
uses source SQL with only two asserted DATE_TRUNC/date-cast conversions.
Original source illustrations, synthetic boundary fixtures and contract
counterexamples are distinguished from official verification or mastery.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
SHA = {
    "key": "7912c8e676621c513e0b635a40c6ee299404676e",
    90: ("14. Data Quality and Deduplication/"
         "P090. Column-by-column completeness profile of Orders.md",
         "1fa536155bfc0115c796ae7c740d0b23dff851f7"),
    95: ("14. Data Quality and Deduplication/"
         "P095. Debug a revenue-by-category query that gives wrong numbers.md",
         "6556470a667af5ddb73e9adce81e65bb4331cb3b"),
}
ORDERS_COLUMNS = ("OrderID", "CustomerID", "PaymentID", "OrderDate",
                  "ShipperID", "Total_Order_Amount", "ShipDate", "DeliveryDate")
DDL = {
    90: ("Orders(OrderID INT, CustomerID INT, PaymentID INT, OrderDate TEXT, "
         "ShipperID INT, Total_Order_Amount REAL, ShipDate TEXT, DeliveryDate TEXT)",),
    95: ("Category(CategoryID INT, CategoryName TEXT)",
         "Products(ProductID INT, CategoryID INT, Sale_Price REAL)",
         "Orders(OrderID INT, OrderDate TEXT)",
         "OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT, Quantity INT)"),
}


def blob_sha(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def supplied_sql(key, question):
    match = re.search(rf"^-- Q{question}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)",
                      key, re.M | re.S)
    assert match, f"Missing original Q{question} supplied key"
    statement = match.group(1).strip()
    assert statement.startswith("WITH ") and statement.endswith(";")
    return statement


def adapt_90(sql):
    """Assert all original fields/order; replace only unsupported PG LATERAL."""
    assert "CROSS JOIN LATERAL (" in sql and "o.OrderDate > a.max_order_date - 30" in sql
    for index, name in enumerate(ORDERS_COLUMNS, 1):
        assert re.search(rf"\({index}, '{name}',\s+o\.{name}::text\)", sql), name
    assert "COUNT(*) FILTER (WHERE u.column_value IS NULL AND u.is_recent)" in sql
    selects = [
        f"SELECT {index} AS column_position, '{name}' AS column_name, "
        f"CAST(o.{name} AS TEXT) AS column_value, "
        "(o.OrderDate > DATE(a.max_order_date, '-30 days')) AS is_recent "
        "FROM Orders AS o CROSS JOIN anchor AS a"
        for index, name in enumerate(ORDERS_COLUMNS, 1)
    ]
    replacement = "unpivoted AS (\n" + "\nUNION ALL\n".join(selects) + (
        "\n)\nSELECT u.column_name,")
    adapted, changed = re.subn(
        r"unpivoted AS \(.*?\n\)\nSELECT u\.column_name,",
        lambda _m: replacement, sql, flags=re.S)
    assert changed == 1, "Original Q090 source shape has drifted"
    assert adapted.count("UNION ALL") == 7
    return adapted


def adapt_95(sql):
    assert "FULL JOIN category_sales AS cs ON cs.CategoryID = cat.CategoryID" in sql
    replacements = (
        ("DATE_TRUNC('year', MAX(o.OrderDate))::date",
         "DATE(MAX(o.OrderDate), 'start of year')"),
        ("(DATE_TRUNC('year', MAX(o.OrderDate)) + INTERVAL '1 year')::date",
         "DATE(MAX(o.OrderDate), 'start of year', '+1 year')"),
    )
    for original, converted in replacements:
        assert sql.count(original) == 1, f"Unexpected date expression: {original}"
        sql = sql.replace(original, converted)
    assert "DATE_TRUNC" not in sql and "::date" not in sql
    return sql


def replay(n, sql, rows):
    with sqlite3.connect(":memory:") as db:
        for table in DDL[n]:
            db.execute("CREATE TABLE " + table)
        for table, records in rows.items():
            if records:
                db.executemany("INSERT INTO " + table + " VALUES (" +
                               ",".join("?" for _ in records[0]) + ")", records)
        return db.execute(sql).fetchall()


def expect(n, sql, rows, wanted, label):
    actual = replay(n, sql, rows)
    assert actual == wanted, (
        f"Q{n} {label}\nexpected {wanted!r}\nactual   {actual!r}")
    print(f"PASS Q{n}: {label} ({len(actual)} result rows)")


def profile(total, nulls, recent_null_pct, distinct):
    return (total, nulls, round(100.0 * nulls / total, 2)
            if total else None, recent_null_pct, distinct)


def q90(sql):
    source = [
        (1, 10, None, "2026-01-01", 30, 100, "2026-01-02", "2026-01-04"),
        (2, 10, 20, "2026-01-31", None, 200, None, None)]
    want = [
        ("OrderID", *profile(2, 0, 0, 2)),
        ("CustomerID", *profile(2, 0, 0, 1)),
        ("PaymentID", *profile(2, 1, 0, 1)),
        ("OrderDate", *profile(2, 0, 0, 2)),
        ("ShipperID", *profile(2, 1, 100, 1)),
        ("Total_Order_Amount", *profile(2, 0, 0, 2)),
        ("ShipDate", *profile(2, 1, 100, 1)),
        ("DeliveryDate", *profile(2, 1, 100, 1))]
    expect(90, sql, {"Orders": source}, want,
           "original Jan-1/Jan-31 eight-column illustration")

    boundary = [
        (1, 10, None, "2026-01-01", 30, 100, "2026-01-02", "2026-01-04"),
        (2, 10, 20, "2026-01-02", None, 200, None, None),
        (3, 11, 20, "2026-01-31", 30, 200, "2026-01-31", None)]
    want = [
        ("OrderID", *profile(3, 0, 0, 3)),
        ("CustomerID", *profile(3, 0, 0, 2)),
        ("PaymentID", *profile(3, 1, 0, 1)),
        ("OrderDate", *profile(3, 0, 0, 3)),
        ("ShipperID", *profile(3, 1, 50, 1)),
        ("Total_Order_Amount", *profile(3, 0, 0, 2)),
        ("ShipDate", *profile(3, 1, 50, 2)),
        ("DeliveryDate", *profile(3, 2, 100, 1))]
    expect(90, sql, {"Orders": boundary}, want,
           "independent inclusive Jan-2/exclusive Jan-1 30-day boundary")
    expect(90, sql, {"Orders": [
        (4, 10, None, None, None, None, None, None)]},
        [("OrderID", 1, 0, 0.0, None, 1),
         ("CustomerID", 1, 0, 0.0, None, 1),
         ("PaymentID", 1, 1, 100.0, None, 0),
         ("OrderDate", 1, 1, 100.0, None, 0),
         ("ShipperID", 1, 1, 100.0, None, 0),
         ("Total_Order_Amount", 1, 1, 100.0, None, 0),
         ("ShipDate", 1, 1, 100.0, None, 0),
         ("DeliveryDate", 1, 1, 100.0, None, 0)],
        "missing anchor-date nullable denominator")
    expect(90, sql, {"Orders": []}, [],
           "KNOWN CONTRACT GAP: empty Orders returns zero columns, not eight")


def q95(sql):
    expect(95, sql, {
        "Category": [(1, "Audio"), (2, "Home")],
        "Products": [(101, 1, 10), (102, 99, 5)],
        "Orders": [(1, "2026-01-01")],
        "OrderDetails": [(1, 1, 101, 2), (2, 1, 102, 1)]
    }, [("Home", 0, 0), ("Unmapped", 1, 5.0), ("Audio", 1, 20.0)],
        "original no-sales category / unmapped product illustration")
    expect(95, sql, {
        "Category": [(1, "Audio"), (2, "Home"), (3, "Empty"), (4, "Audio")],
        "Products": [(101, 1, 10), (102, 99, 5), (103, 2, 7),
                     (104, 4, 4), (105, 1, None), (106, None, 9)],
        "Orders": [(1, "2026-01-01"), (2, "2026-12-31"), (3, "2025-12-31")],
        "OrderDetails": [(1, 1, 101, 2), (2, 1, 102, 1),
                         (3, 2, 101, 3), (4, 2, 103, 2),
                         (5, 3, 104, 500), (6, 2, 106, 1),
                         (7, 2, 105, 1), (8, 2, 103, 1),
                         (9, 2, 999, 1)]
    }, [("Audio", 0, 0), ("Empty", 0, 0), ("Unmapped", 2, 14.0),
        ("Home", 1, 21.0), ("Audio", 2, 50.0)],
        "independent 2025-excluded / 2026-boundary / distinct-order "
        "dedup / missing products / NULL price / same-name-ID categories")
    expect(95, sql, {"Category": [(1, "Audio"), (2, "Home")]},
           [("Audio", 0, 0), ("Home", 0, 0)],
           "empty-order boundary keeps original catalog categories")
    expect(95, sql, {
        "Products": [(1, 99, 8)],
        "Orders": [(5, "2026-06-03")],
        "OrderDetails": [(11, 5, 1, 2)]
    }, [("Unmapped", 1, 16.0)],
        "no Category rows but unmapped product is still counted")


def main():
    assert sqlite3.sqlite_version_info >= (3, 39), (
        "SQLite FULL JOIN support required by original Q095 key")
    assert blob_sha(KEY) == SHA["key"], "Original supplied PostgreSQL key drifted"
    key = KEY.read_text(encoding="utf-8")
    for n in (90, 95):
        path, sha = SHA[n]
        archived = BASE / path
        assert blob_sha(archived) == sha, f"Original Q{n} task source drifted"
        source = archived.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{n:03d}.", "NOT SOLVED YET", "## Schema",
                       "### Sample input and expected output", "Official solution",
                       "Pending"):
            assert marker in source, f"Q{n} missing archive marker {marker}"
        supplied = supplied_sql(key, n)
        if n == 90:
            q90(adapt_90(supplied))
        else:
            q95(adapt_95(supplied))
        print(f"INSPECTED Q{n}: source SHA, PostgreSQL key SHA and unsolved learner state")
    print("PARTIAL: Q090 LATERAL unpivot reconstructed; Q095 only date-cast "
          "adapted. Synthetic pass != native PostgreSQL verification, "
          "complete source-data parity, provider grading, or learner mastery.")


if __name__ == "__main__":
    main()
