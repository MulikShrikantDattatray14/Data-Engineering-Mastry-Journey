#!/usr/bin/env python3
"""Read-only native PostgreSQL 16 replay of immutable PNP Q084 and Q090 keys.

The extracted, SHA-pinned original supplier SQL runs WITHOUT dialect translation
on disposable transaction-scoped PostgreSQL TEMP tables. Tests describe bounded
example / reviewer fixtures and known contract discrepancies, not a provider
grade, a complete original-dataset evaluation, or an independent learner solve.
"""
import hashlib
import os
import re
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_BLOB = "7912c8e676621c513e0b635a40c6ee299404676e"
SOURCES = {
    84: ("4. Aggregation/P084. Delivery time by state and shipper with subtotals.md",
         "e019aa308f9726e1328a44e24e89c7c4db677701"),
    90: ("14. Data Quality and Deduplication/P090. Column-by-column completeness profile of Orders.md",
         "1fa536155bfc0115c796ae7c740d0b23dff851f7"),
}
CREATE_ORDERS = """CREATE TEMP TABLE Orders (
 OrderID integer, CustomerID integer, PaymentID integer, OrderDate date,
 ShipperID integer, Total_Order_Amount numeric, ShipDate date, DeliveryDate date
) ON COMMIT DROP"""
CREATE_CUSTOMERS = "CREATE TEMP TABLE Customers (CustomerID integer, State text) ON COMMIT DROP"
CREATE_SHIPPERS = "CREATE TEMP TABLE Shippers (ShipperID integer, CompanyName text) ON COMMIT DROP"
COLUMNS = ("OrderID", "CustomerID", "PaymentID", "OrderDate",
           "ShipperID", "Total_Order_Amount", "ShipDate", "DeliveryDate")


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def extracted_key(key_text, number):
    match = re.search(rf"(?ms)^-- Q{number}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key_text)
    assert match, f"Original Q{number} key not found"
    sql = match.group(1).strip()
    assert sql.startswith("WITH ") and sql.endswith(";"), number
    if number == 84:
        assert "GROUP BY ROLLUP (d.state, d.shipper_name)" in sql
        assert "GROUPING(d.state, d.shipper_name)" in sql
        assert "MAX(COUNT(*)) OVER (PARTITION BY d.state)" in sql
        assert "o.ShipDate IS NULL" in sql
    else:
        assert "CROSS JOIN LATERAL" in sql and "COUNT(DISTINCT u.column_value)" in sql
        assert "o.OrderDate > a.max_order_date - 30" in sql
        for index, name in enumerate(COLUMNS, 1):
            assert f"({index}, '{name}'" in sql, name
    return sql


def run(conn, sql, orders, customers=(), shippers=()):
    """A read-only source query over a fresh, auto-dropped scratch schema."""
    with conn.transaction():
        conn.execute(CREATE_ORDERS)
        conn.execute(CREATE_CUSTOMERS)
        conn.execute(CREATE_SHIPPERS)
        if orders:
            conn.executemany(
                "INSERT INTO Orders VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", orders)
        if customers:
            conn.executemany("INSERT INTO Customers VALUES (%s,%s)", customers)
        if shippers:
            conn.executemany("INSERT INTO Shippers VALUES (%s,%s)", shippers)
        # Immutable original PostgreSQL key, without any SQL rewrites:
        return conn.execute(sql).fetchall()


def order(number, customer=10, shipper=1, order_date="2026-01-01",
          ship_date="2026-01-02", delivery="2026-01-03", payment=20, amount=100):
    return (number, customer, payment, order_date, shipper, amount, ship_date, delivery)


def q84(conn, sql):
    original = [order(i) for i in range(1, 6)] + [
        order(6, shipper=2, delivery="2026-01-05")]
    got = run(conn, sql, original, [(10, "CA")], [(1, "Swift"), (2, "Slow")])
    expected = [
        ("CA", "Swift", "State x shipper", 5, 2.0),
        ("CA", "Slow", "State x shipper", 1, None),
        ("CA", "All shippers", "State subtotal", 6, 2.33),
        ("All states", "All shippers", "Grand total", 6, 2.33)]
    norm = lambda rows: sorted((a,b,c,d,None if v is None else float(v)) for a,b,c,d,v in rows)
    assert norm(got) == norm(expected), (got, expected)
    print("PASS Q084 NATIVE_PG original six-order ROLLUP illustration (4 rows)")

    invalid = [order(1, shipper=1), order(2, shipper=2,
               ship_date=None, delivery="2026-01-05")]
    got = run(conn, sql, invalid, [(10,"CA")], [(1,"Swift"),(2,"Slow")])
    assert ("CA","Slow","State x shipper",1,None) in got, got
    assert ("All states","All shippers","Grand total",2,None) in got, got
    print("KNOWN Q084 NATIVE_PG CONTRACT GAP: NULL ShipDate counted as delivered (2 total)")

    # Coalescing data label before grouping merges a literal Unknown with missing State.
    collision = [order(1,customer=10), order(2,customer=11)]
    got = run(conn, sql, collision, [(10,None),(11,"Unknown")], [(1,"Swift")])
    assert ("Unknown","Swift","State x shipper",2,None) in got, got
    assert sum(x[2] == "State x shipper" for x in got) == 1, got
    print("KNOWN Q084 NATIVE_PG CONDITIONAL GAP: missing State merges literal 'Unknown'")

    got = run(conn, sql, [])
    assert got == [("All states","All shippers","Grand total",0,None)], got
    print("PASS Q084 NATIVE_PG empty delivered Orders gives grand-total zero row")


def q90(conn, sql):
    original = [
        order(1, payment=None, shipper=30, amount=100,
              ship_date="2026-01-02", delivery="2026-01-04"),
        order(2, payment=20, shipper=None, amount=200,
              order_date="2026-01-31", ship_date=None, delivery=None),
    ]
    got = run(conn, sql, original)
    expected = [
        ("OrderID",2,0,0.0,0.0,2), ("CustomerID",2,0,0.0,0.0,1),
        ("PaymentID",2,1,50.0,0.0,1), ("OrderDate",2,0,0.0,0.0,2),
        ("ShipperID",2,1,50.0,100.0,1),
        ("Total_Order_Amount",2,0,0.0,0.0,2),
        ("ShipDate",2,1,50.0,100.0,1),
        ("DeliveryDate",2,1,50.0,100.0,1)]
    assert got == [tuple(x if i not in (3,4) or x is None else round(float(x),2)
                         for i,x in enumerate(row)) for row in expected] or normalize90(got) == normalize90(expected), got
    print("PASS Q090 NATIVE_PG original eight-column, two-order illustration")

    boundary = [
        order(1,payment=None,shipper=30,order_date="2026-01-01"),
        order(2,payment=20,shipper=None,order_date="2026-01-02",
              ship_date=None,delivery=None),
        order(3,customer=11,payment=None,shipper=30,order_date="2026-01-31",
              ship_date=None,delivery=None),
    ]
    got = run(conn, sql, boundary)
    rows = {r[0]:r for r in got}
    assert len(got)==8 and [r[0] for r in got]==list(COLUMNS), got
    assert normalize90([rows["PaymentID"]]) == normalize90([("PaymentID",3,2,66.67,50.0,1)]), rows
    assert normalize90([rows["ShipDate"]]) == normalize90([("ShipDate",3,2,66.67,100.0,1)]), rows
    print("PASS Q090 NATIVE_PG Jan-01 excluded / Jan-02 included at Jan-31 anchor")

    got = run(conn, sql, [order(1, order_date=None, payment=None,
                         shipper=None, amount=None, ship_date=None, delivery=None)])
    assert len(got)==8 and all(x[4] is None for x in got), got
    assert next(r for r in got if r[0]=="OrderDate")[3]==100, got
    print("PASS Q090 NATIVE_PG NULL-only date anchor: eight rows with undefined recent ratio")

    got = run(conn, sql, [])
    assert got == [], got
    print("KNOWN Q090 NATIVE_PG CONTRACT GAP: empty Orders returns ZERO rows, not eight column profiles")


def normalize90(rows):
    return [(name,n,missing,None if allpct is None else round(float(allpct),2),
             None if recent is None else round(float(recent),2),distinct)
            for name,n,missing,allpct,recent,distinct in rows]


def main():
    assert git_blob(KEY)==KEY_BLOB, "archived supplied SQL changed"
    source_key = KEY.read_text(encoding="utf-8")
    for n,(rel,sha) in SOURCES.items():
        source = BASE/rel
        assert git_blob(source)==sha, f"Q{n} original source changed"
        txt=source.read_text(encoding="utf-8")
        for token in (f"# PNP Q{n:03d}.","NOT SOLVED YET","## Schema",
                      "## Official solution","Pending","### Sample input and expected output"):
            assert token in txt, (n,token)
        print(f"INSPECTED Q{n}: source blob {sha} + original learner Pending")
    with psycopg.connect(
        host=os.environ.get("PGHOST","127.0.0.1"),
        port=os.environ.get("PGPORT","5432"),
        user=os.environ.get("PGUSER","audit"),
        dbname=os.environ.get("PGDATABASE","audit"),
        password=os.environ.get("PGPASSWORD","audit"),
        autocommit=True) as conn:
        version=int(conn.execute("SHOW server_version_num").fetchone()[0])
        assert 160000 <= version < 170000, f"PostgreSQL 16 expected, got {version}"
        print(f"NATIVE PostgreSQL server_version_num={version}; original SQL unmodified")
        q84(conn, extracted_key(source_key,84))
        q90(conn, extracted_key(source_key,90))
    print("PARTIAL AUDIT: original native PostgreSQL executed on disposable fixtures; "
          "known semantic gaps persist, no provider grade, learner solve or full signoff.")


if __name__=="__main__":
    main()
