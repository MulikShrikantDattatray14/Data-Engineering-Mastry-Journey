#!/usr/bin/env python3
"""Read-only Q083/Q084 source-key audit, bounded SQLite compatibility replay.

Q083 extracts the immutable PostgreSQL supplied key and adapts its date,
numeric and ordered-set-percentile operators. Q084 extracts the immutable
delivered-order predicate and reconstructs PostgreSQL ROLLUP grouping sets
explicitly for SQLite: this is NOT native PostgreSQL parity. The regression
asserts observed source-key/spec conflicts; passing it does not award a
provider grade or declare either task fully correct or learner-completed.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
SOURCES = {
    83: ("15. Analytics and Performance/P083. Underperforming sub-categories in the last six months.md",
         "b1339a417e6f47b85792b43d45f32edf32f281ad"),
    84: ("4. Aggregation/P084. Delivery time by state and shipper with subtotals.md",
         "e019aa308f9726e1328a44e24e89c7c4db677701"),
}
DDL = {
    83: ["Category(CategoryID INT, CategoryName TEXT, Active TEXT)",
         "Products(ProductID INT, CategoryID INT, Sub_Category TEXT)",
         "Orders(OrderID INT, OrderDate TEXT)",
         "OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT, Quantity INT)"],
    84: ["Customers(CustomerID INT, State TEXT)",
         "Shippers(ShipperID INT, CompanyName TEXT)",
         "Orders(OrderID INT, CustomerID INT, ShipperID INT, OrderDate TEXT, ShipDate TEXT, DeliveryDate TEXT)"],
}


def git_blob(path):
    value = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(value)).encode() + b"\0" + value).hexdigest()


def replace_once(sql, original, replacement):
    count = sql.count(original)
    assert count == 1, f"supplier SQL drift for {original!r}: {count} matches"
    return sql.replace(original, replacement)


def extract(key, n):
    match = re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key)
    assert match, f"Q{n} missing supplied key section"
    sql = match.group(1).strip()
    assert sql.startswith("WITH ") and sql.endswith(";"), n
    return sql


class Percentile25:
    def __init__(self):
        self.values = []

    def step(self, x):
        if x is not None:
            self.values.append(float(x))

    def finalize(self):
        if not self.values:
            return None
        v = sorted(self.values)
        at = (len(v) - 1) * .25
        i = int(at)
        return v[i] + (v[min(i + 1, len(v) - 1)] - v[i]) * (at - i)


def sqlite_q83(key_sql):
    """Only explicit dialect substitutions; all relational key logic retained."""
    sql = replace_once(key_sql,
                       "(MAX(o.OrderDate) - INTERVAL '6 months')::date",
                       "DATE(MAX(o.OrderDate), '-6 months')")
    sql = replace_once(sql,
                       "COALESCE(SUM(ru.units), 0)::numeric / COUNT(*)",
                       "1.0 * COALESCE(SUM(ru.units), 0) / COUNT(*)")
    sql = replace_once(sql,
                       "PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY s.units_per_product)",
                       "PERCENTILE_25(s.units_per_product)")
    sql = replace_once(sql, "t.category_p25::numeric", "t.category_p25")
    assert "GROUP BY cat.CategoryName, p.Sub_Category" in sql
    assert "GROUP BY s.CategoryName" in sql
    for pg_only in ("::", "INTERVAL ", "PERCENTILE_CONT", "WITHIN GROUP"):
        assert pg_only not in sql
    return sql


def sqlite_q84(key_sql):
    """Extract exact delivered-order CTE; emulate three key ROLLUP grouping sets.

    The original GROUPING()/ROLLUP/window ORDER BY cannot execute in SQLite;
    do not present this independently constructed grouping-set reconstruction
    as execution of the original PostgreSQL aggregation syntax.
    """
    assert "GROUP BY ROLLUP (d.state, d.shipper_name)" in key_sql
    assert "GROUPING(d.state, d.shipper_name)" in key_sql
    assert "MAX(COUNT(*)) OVER (PARTITION BY d.state)" in key_sql
    delimiter = "\nSELECT CASE WHEN GROUPING(d.state)"
    assert key_sql.count(delimiter) == 1
    prefix = key_sql.split(delimiter, 1)[0]
    assert prefix.startswith("WITH delivered AS (") and prefix.rstrip().endswith(")")
    prefix = replace_once(prefix, "o.DeliveryDate::date - o.OrderDate::date",
                          "CAST(julianday(o.DeliveryDate) - julianday(o.OrderDate) AS INTEGER)")
    assert "o.ShipDate IS NULL" in prefix
    assert "o.DeliveryDate >= o.OrderDate" in prefix
    assert "o.DeliveryDate >= o.ShipDate" in prefix
    columns = ("COUNT(*) AS delivered_orders, "
               "CASE WHEN COUNT(*) >= 5 THEN ROUND(AVG(d.delivery_days), 2) END AS avg_delivery_days")
    return (prefix + ",\nrollup_rows AS (\n"
            " SELECT d.state AS state, d.shipper_name AS shipper_name,"
            " 'State x shipper' AS row_level, " + columns +
            " FROM delivered AS d GROUP BY d.state, d.shipper_name\n"
            " UNION ALL\n SELECT d.state, 'All shippers', 'State subtotal', " + columns +
            " FROM delivered AS d GROUP BY d.state\n"
            " UNION ALL\n SELECT 'All states', 'All shippers', 'Grand total', " + columns +
            " FROM delivered AS d\n)\n"
            "SELECT state, shipper_name, row_level, delivered_orders, avg_delivery_days"
            " FROM rollup_rows;")


def execute(n, sql, rows):
    db = sqlite3.connect(":memory:")
    try:
        if n == 83:
            db.create_aggregate("PERCENTILE_25", 1, Percentile25)
        for d in DDL[n]:
            db.execute("CREATE TABLE " + d)
        for table, values in rows.items():
            if values:
                db.executemany("INSERT INTO " + table + " VALUES (" +
                               ",".join("?" for _ in values[0]) + ")", values)
        return db.execute(sql).fetchall()
    finally:
        db.close()


def check(n, sql, rows, expected, label):
    got = execute(n, sql, rows)
    # Q084's source illustration places Swift before Slow, whereas supplied
    # ORDER BY sorts shipper names; output contract itself does not require
    # that illustration order. Compare row values without claiming order parity.
    if n == 84:
        assert sorted(map(repr, got)) == sorted(map(repr, expected)), (
            f"Q{n} {label}: {got!r} != {expected!r}")
    else:
        assert got == expected, f"Q{n} {label}: {got!r} != {expected!r}"
    print(f"PASS Q{n} {label} ({len(got)} rows)")


def q83_tests(sql):
    sample = {
        "Category": [(1, "Care", "Y")],
        "Products": [(101,1,"A"),(102,1,"B"),(103,1,"C"),(104,1,"D")],
        "Orders": [(1,"2026-06-30"),(2,"2026-06-30"),(3,"2026-06-30")],
        "OrderDetails": [(1,1,102,10),(2,2,103,20),(3,3,104,30)],
    }
    check(83, sql, sample, [("Care","A",1,0,0.0,7.5)],
          "original four-subcategory P25 illustration")
    boundary = {
        "Category": [(1,"Care","Y"),(2,"Dormant","N")],
        "Products": [(101,1,"A"),(105,1,"A"),(102,1,"B"),(103,1,"C"),
                     (104,1,"D"),(999,2,"Z")],
        "Orders": [(1,"2026-06-30"),(2,"2025-12-30"),(3,"2026-05-01")],
        "OrderDetails": [(1,1,102,10),(2,1,103,20),(3,1,104,30),
                         (4,2,101,999),(5,3,999,900)],
    }
    check(83, sql, boundary, [("Care","A",2,0,0.0,7.5)],
          "independent six-month exclusive boundary, denominator and inactive category")
    # Two distinct IDs both named Care. Supplier groups by NAME rather than ID;
    # its group for subcategory A merges 0 and 100 units, losing the real loser.
    collision = {
        "Category": [(1,"Care","Y"),(2,"Care","Y")],
        "Products": [(101,1,"A"),(102,1,"B"),(103,1,"C"),(104,1,"D"),
                     (201,2,"A")],
        "Orders": [(1,"2026-06-30")],
        "OrderDetails": [(1,1,102,10),(2,1,103,20),(3,1,104,30),
                         (4,1,201,100)],
    }
    observed = execute(83, sql, collision)
    assert observed == [("Care","B",1,10,10.0,17.5)], observed
    expected_by_category_id = [("Care","A",1,0,0.0,7.5)]
    assert observed != expected_by_category_id
    print("KNOWN Q083 CONDITIONAL CONTRACT FAILURE: duplicate CategoryName across "
          "different CategoryIDs merges subcategory A; key returns B, whereas "
          "per-category-ID semantics require A. Provider grading not known.")


def q84_tests(sql):
    sample = {
        "Customers": [(10,"CA")], "Shippers": [(1,"Swift"),(2,"Slow")],
        "Orders": [(i,10,1,"2026-01-01","2026-01-02","2026-01-03")
                   for i in range(1,6)] +
                  [(6,10,2,"2026-01-01","2026-01-02","2026-01-05")],
    }
    check(84, sql, sample,
          [("CA","Swift","State x shipper",5,2.0),
           ("CA","Slow","State x shipper",1,None),
           ("CA","All shippers","State subtotal",6,2.33),
           ("All states","All shippers","Grand total",6,2.33)],
          "original six-order ROLLUP row-value illustration")
    boundary = {
        "Customers": [(10,"  "),(11,"NY")], "Shippers": [(1,"Courier")],
        "Orders": ([(i,10,None,"2026-02-01","2026-02-01","2026-02-02")
                    for i in range(1,6)] +
                   [(6,11,1,"2026-02-01","2026-02-02","2026-02-03"),
                    (7,11,1,"2026-02-01","2026-01-31","2026-02-03"),
                    (8,11,1,"2026-02-01","2026-02-05","2026-02-03"),
                    (9,11,1,"2026-02-03","2026-02-03","2026-02-01")]),
    }
    check(84, sql, boundary,
          [("Unknown","Unknown shipper","State x shipper",5,1.0),
           ("NY","Courier","State x shipper",1,None),
           ("Unknown","All shippers","State subtotal",5,1.0),
           ("NY","All shippers","State subtotal",1,None),
           ("All states","All shippers","Grand total",6,1.17)],
          "independent missing-state/shipper, invalid sequence and five-count suppression")
    no_ship = {
        "Customers": [(10,"CA")], "Shippers": [(1,"Swift"),(2,"Slow")],
        "Orders": [(1,10,1,"2026-01-01","2026-01-02","2026-01-03"),
                   (2,10,2,"2026-01-01",None,"2026-01-05")],
    }
    got = execute(84, sql, no_ship)
    assert ("CA","Slow","State x shipper",1,None) in got, got
    assert ("All states","All shippers","Grand total",2,None) in got, got
    print("KNOWN Q084 CONDITIONAL DATE-VALIDITY CONTRACT CONFLICT: supplied key "
          "includes delivered order with missing ShipDate, contrary to strict "
          "order->ship->delivery requirement and Q088's validation rule.")


def main():
    assert git_blob(KEY) == KEY_SHA, "supplier key hash changed"
    key = KEY.read_text(encoding="utf-8")
    for n,(rel,pin) in SOURCES.items():
        path = BASE / rel
        assert git_blob(path) == pin, f"original Q{n} hash changed"
        source = path.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{n:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output", "## Schema",
                       "## Official solution", "Pending"):
            assert marker in source, (n, marker)
        print(f"INSPECTED Q{n}: intact statement, original sample, schema, pending learner")
    q83_tests(sqlite_q83(extract(key,83)))
    q84_tests(sqlite_q84(extract(key,84)))
    print("PARTIAL: 2 source illustrations and 2 synthetic groups pass bounded "
          "SQLite equivalence; 2 conditional discrepancy fixtures reproduced. "
          "Q084 ROLLUP is reconstructed, not executed natively. Neither task "
          "receives provider grade or independent learner completion.")


if __name__ == "__main__":
    main()
