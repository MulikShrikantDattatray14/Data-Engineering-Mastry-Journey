#!/usr/bin/env python3
"""Read-only, source-hash-pinned PNP Q033-Q040 supplied-key illustration audit.

All SQL is extracted from the preserved PostgreSQL answer-key archive. Narrow
dialect adaptations are explicitly checked below. This is NOT native PostgreSQL,
Commerce v2 original-data parity, grading, or independent learner coursework.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
)
SOURCES = {
    33: ("6. SubQueries/P033. Products that have never been ordered.md", "5bc9bbd856f54271fc629d76a6bb0bc99e9290d5"),
    34: ("9. Windowing Functions/P034. Each supplier's share of units supplied.md", "fde47d98e49a8f6cc94745b05ff3bf65f02f4eae"),
    35: ("4. Aggregation/P035. Late-delivery rate by shipper.md", "8464f2c30c50459a7c9a991ea9f741ccdfee814d"),
    36: ("4. Aggregation/P036. Payment method mix by month as columns.md", "6d271928f88ba21507a4a4e7238bbea750a69437"),
    37: ("14. Data Quality and Deduplication/P037. Prove no order was paid with a method that is not allowed.md", "13de904886a87807a7c8ea3dc6efe0a6b538c670"),
    38: ("2. Joins/P038. Products from inactive categories that still sold in the latest ye.md", "50e5ec07b777015e77f0df613c58ed89cb642a81"),
    39: ("2. Joins/P039. Categories with no products, and categories with products but no s.md", "ab83ec76cdc388b209732cff739c62e6b6da3421"),
    40: ("12. Dates and Time/P040. Days from sign-up to first order.md", "4ce15aa0ccceccb219027b787309af57a1416c34"),
}
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"

def blobsha(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def source_key(n, key_text):
    m = re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key_text)
    assert m, f"Missing archived Q{n} SQL"
    return m.group(1).strip()

def provenance():
    assert blobsha(KEY) == KEY_SHA, "Original supplied-key archive drift"
    key_text = KEY.read_text(encoding="utf-8")
    queries = {}
    for n, (relative, expected_sha) in SOURCES.items():
        path = BASE / relative
        assert blobsha(path) == expected_sha, f"P{n:03d} archived source drift"
        src = path.read_text(encoding="utf-8")
        assert src.startswith(f"# PNP Q{n:03d}.")
        assert "### Sample input and expected output" in src and "## Schema" in src
        assert "NOT SOLVED YET" in src and "## My solution — SQLite\n\nPending." in src
        assert "## Official solution\n\nPending" in src
        queries[n] = source_key(n, key_text)
        assert queries[n].startswith(("SELECT ", "WITH ")), n
    return queries

def replace_once(sql, old, new, count=1):
    assert sql.count(old) == count, f"Original source dialect unexpectedly changed: {old}"
    return sql.replace(old, new)

def sqlite_sql(n, sql):
    """Exact key except the following restricted PostgreSQL -> SQLite translations."""
    if n == 35:
        sql = replace_once(sql, "o.DeliveryDate::date - o.OrderDate::date",
                           "CAST(julianday(date(o.DeliveryDate)) - julianday(date(o.OrderDate)) AS INTEGER)")
    if n == 36:
        sql = replace_once(sql, "DATE_TRUNC('month', o.OrderDate)::date",
                           "date(o.OrderDate, 'start of month')")
        sql = replace_once(sql, "DATE_TRUNC('month', o.OrderDate)",
                           "date(o.OrderDate, 'start of month')")
    if n == 38:
        sql = replace_once(sql, "DATE_TRUNC('year', MAX(o.OrderDate))::date",
                           "date(MAX(o.OrderDate), 'start of year')")
        sql = replace_once(sql, "ly.year_start + INTERVAL '1 year'",
                           "date(ly.year_start, '+1 year')")
    if n == 39:
        sql = replace_once(sql, "COUNT(DISTINCT od.ProductID)::numeric",
                           "CAST(COUNT(DISTINCT od.ProductID) AS REAL)")
    if n == 40:
        sql = replace_once(sql, "fo.first_order_date::date - c.DateEntered::date",
                           "CAST(julianday(date(fo.first_order_date)) - julianday(date(c.DateEntered)) AS INTEGER)")
        sql = replace_once(sql, "fo.first_order_date::date < c.DateEntered::date",
                           "date(fo.first_order_date) < date(c.DateEntered)")
    assert "::" not in sql and "DATE_TRUNC(" not in sql and "INTERVAL '" not in sql, n
    return sql

def fixture(*ddl):
    db = sqlite3.connect(":memory:")
    for definition in ddl:
        db.execute(definition)
    return db

def check(db, sql, expected, context):
    got = db.execute(sql).fetchall()
    assert got == expected, f"{context}: actual={got!r}, expected={expected!r}"

def inspect_outputs(q):
    # P033: source illustrative output; NULL foreign keys do not poison NOT EXISTS.
    db=fixture("CREATE TABLE Products(ProductID INT, Product TEXT, Brand TEXT, CategoryID INT, Sale_Price REAL)",
               "CREATE TABLE OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT)")
    db.executemany("INSERT INTO Products VALUES(?,?,?,?,?)",[(1,"Pen","Nova",10,5),(2,"Cup","Home",20,10)])
    db.execute("INSERT INTO OrderDetails VALUES(10,100,1)")
    check(db,q[33],[(2,"Cup","Home",20,10.0)],"P033 illustrative")
    db.executemany("INSERT INTO Products VALUES(?,?,?,?,?)",[(3,"Book","Paper",10,8),(4,"Desk","Office",None,30)])
    db.execute("INSERT INTO OrderDetails VALUES(11,101,NULL)")
    check(db,q[33],[(4,"Desk","Office",None,30.0),(3,"Book","Paper",10,8.0),(2,"Cup","Home",20,10.0)],"P033 nullable line, stable category ordering")
    db.close()

    # P034: unstocked supplier still shown; missing/unknown SupplierID counts in denominator.
    db=fixture("CREATE TABLE Suppliers(SupplierID INT,CompanyName TEXT)",
               "CREATE TABLE OrderDetails(OrderDetailID INT,SupplierID INT,Quantity INT)")
    db.executemany("INSERT INTO Suppliers VALUES(?,?)",[(1,"Alpha"),(2,"Beta"),(3,"Gamma")])
    db.executemany("INSERT INTO OrderDetails VALUES(?,?,?)",[(1,1,2),(2,1,3),(3,2,5)])
    check(db,q[34],[(1,"Alpha",5,50.0),(2,"Beta",5,50.0),(3,"Gamma",0,0.0)],"P034 illustrative")
    db.executemany("INSERT INTO OrderDetails VALUES(?,?,?)",[(4,999,4),(5,None,1)])
    check(db,q[34],[(1,"Alpha",5,33.33),(2,"Beta",5,33.33),(999,"Unknown supplier",4,26.67),
                    (None,"Unknown supplier",1,6.67),(3,"Gamma",0,0.0)],"P034 orphan and NULL supplier, whole-denominator")
    db.close()

    # P035: 7 days is on time; ship-before-order has its own invalid bucket.
    db=fixture("CREATE TABLE Shippers(ShipperID INT,CompanyName TEXT)",
               "CREATE TABLE Orders(OrderID INT,ShipperID INT,OrderDate TEXT,ShipDate TEXT,DeliveryDate TEXT)")
    db.executemany("INSERT INTO Shippers VALUES(?,?)",[(1,"FastShip"),(2,"QuickShip")])
    db.executemany("INSERT INTO Orders VALUES(?,?,?,?,?)",[(1,1,"2025-01-01","2025-01-02","2025-01-10"),
        (2,1,"2025-01-01","2025-01-02","2025-01-05"),(3,1,"2025-01-01",None,None),
        (4,1,"2025-01-05","2025-01-04","2025-01-06"),
        (5,2,"2025-01-01","2025-01-02","2025-01-03")])
    check(db,q[35],[("FastShip",2,1,50.0,1,1),("QuickShip",1,0,0.0,0,0)],"P035 illustrative")
    db.executemany("INSERT INTO Orders VALUES(?,?,?,?,?)",[(6,2,"2025-01-01","2025-01-02","2025-01-08"),
        (7,None,"2025-01-01","2025-01-02","2025-01-10"),
        (8,999,"2025-01-01","2024-12-31",None)])
    check(db,q[35],[("Unknown shipper",1,1,100.0,1,0),("FastShip",2,1,50.0,1,1),
                    ("QuickShip",2,0,0.0,0,0)],"P035 7-day boundary, missing shipper and NULL-delivery classification")
    db.close()

    # P036: distinct month buckets, EMI and unmatched IDs in other_or_unknown.
    db=fixture("CREATE TABLE Payments(PaymentID INT, PaymentType TEXT)",
               "CREATE TABLE Orders(OrderID INT,OrderDate TEXT,PaymentID INT)")
    db.executemany("INSERT INTO Payments VALUES(?,?)",[(1,"UPI"),(2,"Credit Card"),(3,"EMI")])
    db.executemany("INSERT INTO Orders VALUES(?,?,?)",[(1,"2025-01-01",1),(2,"2025-01-02",2),
        (3,"2025-01-03",3),(4,"2025-02-01",1),(5,"2025-02-02",None)])
    check(db,q[36],[("2025-02-01",1,0,0,0,0,0,1,2),("2025-01-01",1,1,0,0,0,0,1,3)],"P036 illustrative")
    db.executemany("INSERT INTO Payments VALUES(?,?)",[(4,"Wallet"),(5,"Debit Card")])
    db.executemany("INSERT INTO Orders VALUES(?,?,?)",[(6,"2025-02-28",4),(7,"2025-02-28",999),
        (8,None,5),(9,"2025-03-01",5)])
    check(db,q[36],[("2025-03-01",0,0,1,0,0,0,0,1),
        ("2025-02-01",1,0,0,0,0,1,2,4),("2025-01-01",1,1,0,0,0,0,1,3)],"P036 six-column pivot, NULL date excluded")
    db.close()

    # P037: status/violations, false for blank/NULL flags and orders at header grain.
    db=fixture("CREATE TABLE Payments(PaymentID INT,PaymentType TEXT,Allowed TEXT)",
               "CREATE TABLE Orders(OrderID INT,PaymentID INT,Total_Order_Amount REAL)")
    db.executemany("INSERT INTO Payments VALUES(?,?,?)",[(1,"UPI","Y"),(2,"Card","N"),(3,"Cash",None)])
    db.executemany("INSERT INTO Orders VALUES(?,?,?)",[(10,1,100),(11,2,50)])
    check(db,q[37],[(2,"Card","N",0,1,50.0,"VIOLATION: not allowed but used"),
        (1,"UPI","Y",1,1,100.0,"OK"),(3,"Cash",None,0,0,0,"Not allowed, unused")],"P037 illustrative")
    db.executemany("INSERT INTO Payments VALUES(?,?,?)",[(4,"Wallet"," yes "),(5,"Pay Later","  ")])
    db.executemany("INSERT INTO Orders VALUES(?,?,?)",[(12,5,None),(13,999,99)])
    check(db,q[37],[(2,"Card","N",0,1,50.0,"VIOLATION: not allowed but used"),
        (5,"Pay Later","  ",0,1,0,"VIOLATION: not allowed but used"),
        (1,"UPI","Y",1,1,100.0,"OK"),(3,"Cash",None,0,0,0,"Not allowed, unused"),
        (4,"Wallet"," yes ",1,0,0,"Allowed, unused")],"P037 blank flag, NULL amount and unknown payment ID")
    db.close()

    # P038: latest year comes from Orders, not maximum sold line; inactive status.
    db=fixture("CREATE TABLE Category(CategoryID INT,CategoryName TEXT,Active TEXT)",
               "CREATE TABLE Products(ProductID INT,Product TEXT,CategoryID INT)",
               "CREATE TABLE Orders(OrderID INT,OrderDate TEXT)",
               "CREATE TABLE OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT,Quantity INT)")
    db.executemany("INSERT INTO Category VALUES(?,?,?)",[(1,"Old stock","0"),(2,"Current stock","1")])
    db.executemany("INSERT INTO Products VALUES(?,?,?)",[(10,"Old mug",1),(20,"New mug",2)])
    db.executemany("INSERT INTO Orders VALUES(?,?)",[(100,"2025-01-01"),(101,"2024-01-01")])
    db.executemany("INSERT INTO OrderDetails VALUES(?,?,?,?)",[(1,100,10,2),(2,101,10,3),(3,100,20,5)])
    check(db,q[38],[(10,"Old mug","Old stock",2,"2025-01-01")],"P038 illustrative latest year")
    db.executemany("INSERT INTO Products VALUES(?,?,?)",[(30,"New old stock",1)])
    db.executemany("INSERT INTO OrderDetails VALUES(?,?,?,?)",[(4,100,30,5),(5,100,10,1)])
    check(db,q[38],[(30,"New old stock","Old stock",5,"2025-01-01"),
                    (10,"Old mug","Old stock",3,"2025-01-01")],"P038 repeated lines and order quantity")
    db.execute("INSERT INTO Orders VALUES(102,'2026-01-01')")
    check(db,q[38],[],"P038 newer calendar year with zero lines")
    db.close()

    # P039: COUNT DISTINCT products must resist duplicate sales lines.
    db=fixture("CREATE TABLE Category(CategoryID INT,CategoryName TEXT)",
               "CREATE TABLE Products(ProductID INT,CategoryID INT)",
               "CREATE TABLE OrderDetails(OrderDetailID INT,ProductID INT,Quantity INT)")
    db.executemany("INSERT INTO Category VALUES(?,?)",[(1,"Empty"),(2,"Unsold"),(3,"Mixed"),(4,"All sold")])
    db.executemany("INSERT INTO Products VALUES(?,?)",[(10,2),(20,3),(21,3),(30,4)])
    db.executemany("INSERT INTO OrderDetails VALUES(?,?,?)",[(1,20,2),(2,30,3)])
    check(db,q[39],[(1,"Empty",0,0,0,"No products"),(2,"Unsold",1,0,0,"Products but no sales"),
                    (3,"Mixed",2,1,2,"Some products unsold"),(4,"All sold",1,1,3,"All products sold")],"P039 illustrative")
    db.executemany("INSERT INTO OrderDetails VALUES(?,?,?)",[(3,20,4),(4,999,7)])
    check(db,q[39],[(1,"Empty",0,0,0,"No products"),(2,"Unsold",1,0,0,"Products but no sales"),
                    (3,"Mixed",2,1,6,"Some products unsold"),(4,"All sold",1,1,3,"All products sold")],"P039 duplicate lines and orphan ignored")
    db.close()

    # P040: earliest date and negative flag remain visible.
    db=fixture("CREATE TABLE Customers(CustomerID INT, DateEntered TEXT)",
               "CREATE TABLE Orders(OrderID INT,CustomerID INT,OrderDate TEXT)")
    db.executemany("INSERT INTO Customers VALUES(?,?)",[(1,"2025-01-03"),(2,"2025-01-05")])
    db.executemany("INSERT INTO Orders VALUES(?,?,?)",[(10,1,"2025-01-01"),(11,1,"2025-01-10"),(12,2,"2025-01-07")])
    check(db,q[40],[(1,"2025-01-03","2025-01-01",-2,"Order before sign-up"),
                    (2,"2025-01-05","2025-01-07",2,None)],"P040 illustrative")
    db.execute("INSERT INTO Customers VALUES(3,NULL)")
    db.execute("INSERT INTO Orders VALUES(13,3,'2025-01-03')")
    check(db,q[40],[(1,"2025-01-03","2025-01-01",-2,"Order before sign-up"),
                    (2,"2025-01-05","2025-01-07",2,None),
                    (3,None,"2025-01-03",None,None)],"P040 nullable signup and NULLS LAST")
    db.close()

def main():
    sources = provenance()
    queries = {n: sqlite_sql(n, statement) for n, statement in sources.items()}
    inspect_outputs(queries)
    print("PASS: eight immutable archived PNP Q033-Q040 records, key SHA, eight illustrative SQL outputs and eight synthetic boundaries. No provider grades, native PG result certification or new learner mastery.")

if __name__ == "__main__":
    main()
