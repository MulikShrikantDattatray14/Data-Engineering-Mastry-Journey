#!/usr/bin/env python3
"""Partial, read-only PNP Q087/Q088 source-key replay.

Q087 uses a declared PostgreSQL ARRAY_AGG slice -> SQLite ordered-list emulation.
Q088 uses a declared correlated LATERAL VALUES -> SQLite json_each translation.
These tests are bounded illustrations and synthetic boundaries only, not native
PostgreSQL or full commerce data, provider grades, or independent learner work.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/2.PNP- foundations and practice"
)
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
SOURCES = {
    87: ("14. Data Quality and Deduplication/P087. Referential integrity audit across all seven relationships.md",
         "28bed1fe1c7d2e6c4c92e68f6a619a6fb2780e02"),
    88: ("14. Data Quality and Deduplication/P088. Date validity audit.md",
         "52c73f3594668d77afbe679b25a84997fb3ced59"),
}
RELATIONS = [
    "Products.CategoryID -> Category", "Orders.CustomerID -> Customers",
    "Orders.PaymentID -> Payments", "Orders.ShipperID -> Shippers",
    "OrderDetails.OrderID -> Orders", "OrderDetails.ProductID -> Products",
    "OrderDetails.SupplierID -> Suppliers",
]
DDL87 = [
    "Category(CategoryID INT)", "Products(ProductID INT, CategoryID INT)",
    "Customers(CustomerID INT)", "Payments(PaymentID INT)",
    "Shippers(ShipperID INT)", "Orders(OrderID INT, CustomerID INT, PaymentID INT, ShipperID INT)",
    "OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT, SupplierID INT)",
    "Suppliers(SupplierID INT)",
]
DDL88 = [
    "Customers(CustomerID INT, DateEntered TEXT)",
    "Orders(OrderID INT, CustomerID INT, OrderDate TEXT, ShipDate TEXT, DeliveryDate TEXT)",
]

def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def extract(key, n):
    match = re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key)
    assert match, f"missing Q{n} key"
    sql = match.group(1).strip()
    assert sql.startswith("WITH ") and sql.endswith(";"), n
    return sql

def adapt87(sql):
    pg_array = (r"ARRAY_TO_STRING\(\s*\(ARRAY_AGG\(DISTINCT ck\.fk_value ORDER BY ck\.fk_value\)"
                r"\s*FILTER \(WHERE ck\.fk_value IS NOT NULL AND ck\.no_parent\)\)\[1:5\],\s*', '\)")
    sqlite_array = """(SELECT GROUP_CONCAT(t.fk_value, ', ')
       FROM (SELECT DISTINCT k.fk_value FROM child_keys AS k
             WHERE k.rel_id = r.rel_id AND k.fk_value IS NOT NULL AND k.no_parent
             ORDER BY k.fk_value LIMIT 5) AS t)"""
    output, count = re.subn(pg_array, sqlite_array, sql)
    assert count == 1, "Q087 source ARRAY_AGG clause drift"
    assert "ARRAY_AGG" not in output and "ARRAY_TO_STRING" not in output
    return output

# Exact Q088 source rules, equivalently projected with json_each instead of PG LATERAL VALUES.
# Replaced segment is hash-pinned and each source rule is asserted before translation.
ORDER88 = """order_checks AS (
    SELECT CAST(json_extract(j.value, '$[0]') AS INTEGER) AS rule_id,
           json_extract(j.value, '$[1]') AS rule,
           json_extract(j.value, '$[2]') AS severity,
           o.OrderID AS record_id,
           CAST(json_extract(j.value, '$[3]') AS INTEGER) AS violated
    FROM Orders AS o
    LEFT JOIN Customers AS c ON c.CustomerID = o.CustomerID
    CROSS JOIN anchor AS a
    CROSS JOIN json_each(json_array(
        json_array(1, 'Order date missing', 'error', o.OrderDate IS NULL),
        json_array(2, 'Shipped before ordered', 'error', o.ShipDate < o.OrderDate),
        json_array(3, 'Delivered before shipped', 'error', o.DeliveryDate < o.ShipDate),
        json_array(4, 'Delivered before ordered', 'error', o.DeliveryDate < o.OrderDate),
        json_array(5, 'Delivered with no ship date', 'error', o.DeliveryDate IS NOT NULL AND o.ShipDate IS NULL),
        json_array(6, 'Ordered before customer sign-up', 'warning', o.OrderDate < c.DateEntered),
        json_array(7, 'Delivered after 7-day promise', 'warning',
                   CAST(julianday(o.DeliveryDate) - julianday(o.OrderDate) AS INTEGER) > 7),
        json_array(8, 'Not shipped 14+ days after order', 'warning',
                   o.ShipDate IS NULL AND o.DeliveryDate IS NULL
                   AND CAST(julianday(a.max_order_date) - julianday(o.OrderDate) AS INTEGER) >= 14)
    )) AS j
),
"""
RULE88 = [
    "Order date missing", "Shipped before ordered", "Delivered before shipped",
    "Delivered before ordered", "Delivered with no ship date",
    "Ordered before customer sign-up", "Delivered after 7-day promise",
    "Not shipped 14+ days after order",
]
def adapt88(sql):
    start = sql.index("order_checks AS (")
    end = sql.index("customer_checks AS (")
    old = sql[start:end]
    assert old.count("CROSS JOIN LATERAL") == 1 and old.count("VALUES") == 1
    assert old.count("AS r(rule_id, rule, severity, violated)") == 1
    for name in RULE88:
        assert old.count("'" + name + "'") == 1, name
    assert old.count("o.DeliveryDate::date - o.OrderDate::date > 7") == 1
    assert old.count("a.max_order_date::date - o.OrderDate::date >= 14") == 1
    sql = sql[:start] + ORDER88 + sql[end:]
    original = "(ARRAY_AGG(ac.record_id ORDER BY ac.record_id) FILTER (WHERE ac.violated))[1:5]"
    assert sql.count(original) == 1, "Q088 source array slice drift"
    replacement = """(SELECT GROUP_CONCAT(t.record_id, ', ') FROM
           (SELECT s.record_id FROM all_checks AS s
            WHERE s.rule_id = ac.rule_id AND s.violated
            ORDER BY s.record_id LIMIT 5) AS t)"""
    sql = sql.replace(original, replacement)
    assert "LATERAL" not in sql and "ARRAY_AGG" not in sql and "::date" not in sql
    return sql

def run(n, sql, fixture, expected, label):
    db = sqlite3.connect(":memory:")
    try:
        for table in DDL87 if n == 87 else DDL88:
            db.execute("CREATE TABLE " + table)
        for table, values in fixture.items():
            if values:
                db.executemany("INSERT INTO " + table + " VALUES (" +
                               ",".join("?" for _ in values[0]) + ")", values)
        result = db.execute(sql).fetchall()
        assert result == expected, f"Q{n} {label} actual={result!r} expected={expected!r}"
        print(f"PASS Q{n} {label}: {len(result)} rows")
    finally:
        db.close()

def q87():
    sample = {
        "Category": [(1,)], "Products": [(101,1)], "Customers": [(10,)],
        "Payments": [(20,)], "Shippers": [(30,)],
        "Orders": [(100,10,20,30)], "OrderDetails": [(1,100,101,999)],
        "Suppliers": [(7,)],
    }
    expect_sample = [(name,1,0,int(i==6),"999" if i==6 else None)
                     for i,name in enumerate(RELATIONS)]
    varied = {
        "Category":[(1,)], "Products":[(101,1),(102,None),(103,99)],
        "Customers":[(10,)], "Payments":[(20,)], "Shippers":[(30,)],
        "Orders":[(100,10,20,30),(101,None,99,None),(102,88,None,30)],
        "OrderDetails":[(1,100,101,7),(2,777,999,900),(3,777,999,900),
                        (4,None,102,None),(5,777,103,901),
                        (6,778,None,902),(7,779,999,903),(8,780,999,904),
                        (9,781,999,905),(10,782,999,906)],
        "Suppliers":[(7,)],
    }
    expect_varied = list(zip(RELATIONS,
        [3,3,3,3,10,10,10],
        [1,1,1,1,1,1,1],
        [1,1,1,0,8,6,8],
        ["99","88","99",None,"777, 778, 779, 780, 781","999","900, 901, 902, 903, 904"]))
    empty = [(name,0,0,0,None) for name in RELATIONS]
    return [(sample,expect_sample,"original seven-relationship illustration"),
            (varied,expect_varied,"independent orphan/null/duplicate/five-key cap"),
            ({},empty,"independent all-empty table seven-row invariant")]

RULES88 = [
    ("Order date missing","error"),("Shipped before ordered","error"),
    ("Delivered before shipped","error"),("Delivered before ordered","error"),
    ("Delivered with no ship date","error"),
    ("Ordered before customer sign-up","warning"),
    ("Delivered after 7-day promise","warning"),
    ("Not shipped 14+ days after order","warning"),
    ("Customer sign-up date missing","warning"),
]
def q88():
    sample = {"Customers":[(10,"2026-01-01")],
              "Orders":[(1,10,"2026-01-02","2026-01-01","2026-01-05"),
                        (2,10,"2026-01-20",None,None)]}
    sample_expected = [(i,n,s,2 if i<9 else 1,int(i==2),
                        50.0 if i==2 else 0.0,"1" if i==2 else None)
                       for i,(n,s) in enumerate(RULES88,1)]
    varied = {"Customers":[(10,"2026-01-10"),(11,None)],
              "Orders":[(1,10,None,None,None),
                        (2,10,"2026-01-01","2025-12-31","2026-01-20"),
                        (3,11,"2026-01-20",None,"2026-01-21"),
                        (4,10,"2026-02-20",None,None),
                        (5,10,"2026-02-01",None,None),
                        (6,10,"2026-01-19","2026-01-22","2026-01-18")]}
    violation_ids = ["1","2","6","6","3","2","2","5","11"]
    varied_expected = [(i,n,s,6 if i<9 else 2,1,16.67 if i<9 else 50.0,violation_ids[i-1])
                       for i,(n,s) in enumerate(RULES88,1)]
    return [(sample,sample_expected,"original all-nine-rule illustration"),
            (varied,varied_expected,"independent nine distinct violation types")]

def main():
    assert sqlite3.sqlite_version_info >= (3,39,0), sqlite3.sqlite_version
    assert blob(KEY) == KEY_SHA, "archived supplied answer blob drift"
    key = KEY.read_text(encoding="utf8")
    sql = {}
    for n,(path,pin) in SOURCES.items():
        source = BASE / path
        assert blob(source) == pin, f"Q{n} source blob drift"
        s = source.read_text(encoding="utf8")
        for marker in (f"# PNP Q{n:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output", "## Schema",
                       "## Official solution", "Pending"):
            assert marker in s, f"Q{n} original marker missing: {marker}"
        sql[n] = extract(key,n)
        print(f"INSPECTED Q{n}: source + supplied key hash pinned; learner NOT SOLVED YET")
    for rows,expected,label in q87():
        run(87,adapt87(sql[87]),rows,expected,label)
    for rows,expected,label in q88():
        run(88,adapt88(sql[88]),rows,expected,label)
    # Explicit unresolved source contract: nine-rule scorecard even if sources empty.
    run(88,adapt88(sql[88]),{},[],"diagnostic actual empty-source returns zero rules")
    print("KNOWN Q088 CONTRACT FAILURE: empty Orders/Customers return 0 rule rows, "
          "but the source requests fixed nine rules including zeros.")
    print("PARTIAL: Q087 & Q088 key-derived SQLite fixtures passed; "
          "native PG, complete data and provider grading NOT verified. "
          "Q083/Q084 remain source/key inspected only; no learner completion.")

if __name__ == "__main__":
    main()
