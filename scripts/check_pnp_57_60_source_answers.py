#!/usr/bin/env python3
"""Independent, read-only PNP Q057-Q060 supplied-key checks.

This verifies Git blob pins and replays the archived key on four retyped
illustrative examples plus separate auditor-created boundary fixtures in SQLite.
Q059 uses an asserted PostgreSQL DATE_TRUNC -> SQLite month conversion.
No claims about source PDF render, original full dataset, native PostgreSQL,
official grading, or independent learner completions.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
SOURCES = {
    57: ("6. SubQueries/P057. One contact directory for suppliers and shippers.md", "5c4f5002ed74fad21fcb425898954bc1cc8f81c1"),
    58: ("9. Windowing Functions/P058. Each customer's latest order.md", "3b2ae93ca8b2a77b14ea182490b4b629da88da2c"),
    59: ("4. Aggregation/P059. Basket size by month.md", "3faf0f41fdf123b3330dcda784ad27551104241d"),
    60: ("9. Windowing Functions/P060. Sub-category share of its category.md", "b40a23ff03ebbf20b578318dc6d8de78d62db15c"),
}
CASES = {
    57: (
        ["Suppliers(SupplierID INT,CompanyName TEXT,Phone TEXT,Email TEXT,Country TEXT)",
         "Shippers(ShipperID INT,CompanyName TEXT,Phone TEXT)"],
        {"Suppliers": [(1,"Alpha","111","alpha@example.com","India")],
         "Shippers": [(2,"Alpha","222")]},
        [("Shipper",2,"Alpha","222",None,None),("Supplier",1,"Alpha","111","alpha@example.com","India")],
        {"Suppliers": [(3,"Beta","333",None,None),(4,"Alpha","444","a2@example.com","USA")],
         "Shippers": [(5,"Alpha","555"),(6,"Beta","666")]},
        [("Shipper",2,"Alpha","222",None,None),("Shipper",5,"Alpha","555",None,None),
         ("Supplier",1,"Alpha","111","alpha@example.com","India"),
         ("Supplier",4,"Alpha","444","a2@example.com","USA"),
         ("Shipper",6,"Beta","666",None,None),("Supplier",3,"Beta","333",None,None)]
    ),
    58: (
        ["Customers(CustomerID INT,FirstName TEXT,LastName TEXT)",
         "Orders(OrderID INT,CustomerID INT,OrderDate TEXT,Total_Order_Amount INT)"],
        {"Customers": [(1,"Asha","Rao"),(2,"Ben","Das")],
         "Orders": [(1,1,"2025-01-01",100),(2,1,"2025-01-02",200),
                    (3,1,"2025-01-02",300),(4,2,"2025-01-01",50)]},
        [(1,"Asha Rao",3,"2025-01-02",300),(2,"Ben Das",4,"2025-01-01",50)],
        {"Orders": [(5,3,"2025-01-03",70),(6,2,"2025-01-04",None),
                    (7,1,None,500)]},
        [(2,"Ben Das",6,"2025-01-04",None),(3,"Unknown customer",5,"2025-01-03",70),
         (1,"Asha Rao",3,"2025-01-02",300)]
    ),
    59: (
        ["Orders(OrderID INT,OrderDate TEXT)",
         "OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT,Quantity INT)"],
        {"Orders": [(1,"2025-01-01"),(2,"2025-01-02"),(3,"2025-02-01"),(4,"2025-02-02")],
         "OrderDetails": [(11,1,1,2),(12,1,2,3),(13,2,1,1),(14,4,3,2)]},
        [("2025-01-01",2,3.0,1.5),("2025-02-01",1,2.0,1.0)],
        {"Orders": [(5,"2025-02-05"),(6,"2025-03-01")],
         "OrderDetails": [(15,5,3,2),(16,5,3,3),(17,1,1,1)]},
        [("2025-01-01",2,3.5,1.5),("2025-02-01",2,3.5,1.0)]
    ),
    60: (
        ["Category(CategoryID INT,CategoryName TEXT)",
         "Products(ProductID INT,CategoryID INT,Sub_Category TEXT,Sale_Price REAL)",
         "OrderDetails(OrderDetailID INT,ProductID INT,Quantity INT)"],
        {"Category": [(1,"Drinks")],
         "Products": [(1,1,"Hot",10),(2,1,"Hot",20),(3,1,"Cold",5)],
         "OrderDetails": [(11,1,2),(12,2,1),(13,3,2)]},
        [("Drinks","Hot",40.0,80.0),("Drinks","Cold",10.0,20.0)],
        {"Products": [(4,None,None,5),(5,1,"Cold",10)],
         "OrderDetails": [(14,4,2),(15,5,1)]},
        [("Drinks","Hot",40.0,round(200/3,2)),("Drinks","Cold",20.0,round(100/3,2)),
         ("Unmapped","Unknown",10.0,100.0)]
    ),
}

def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def original_sql(n, text):
    m=re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)",text)
    assert m, f"Q{n}: supplied-key SQL not found"
    query=m.group(1).strip()
    assert query.startswith(("SELECT ","WITH ")),n
    return query

def executable(n, query):
    if n == 59:
        token="DATE_TRUNC('month', o.OrderDate)::date"
        assert query.count(token)==2, "Q059 syntax changed; manual review needed"
        query=query.replace(token,"date(o.OrderDate,'start of month')")
    assert "::" not in query and "DATE_TRUNC(" not in query, n
    return query

def run_case(n, query):
    ddl, sample, expected, synthetic, expected_edge = CASES[n]
    db=sqlite3.connect(":memory:")
    db.create_function("CONCAT_WS",-1,
        lambda separator,*args: separator.join(str(a) for a in args if a is not None))
    try:
        for definition in ddl:
            db.execute("CREATE TABLE " + definition)
        for rows_by_table, label, wanted in [
            (sample,"illustrative",expected),
            (synthetic,"synthetic-additive",expected_edge)
        ]:
            for name, rows in rows_by_table.items():
                if rows:
                    db.executemany("INSERT INTO "+name+" VALUES(" + ",".join("?" for _ in rows[0]) + ")", rows)
            observed=db.execute(query).fetchall()
            assert observed == wanted, f"Q{n} {label}: {observed!r} != {wanted!r}"
    finally:
        db.close()

def known_conditional_divergence(q60):
    # Different IDs with equal display name are logically separate categories,
    # but supplied SQL partitions the percentage by category NAME.
    db=sqlite3.connect(":memory:")
    for definition in CASES[60][0]:
        db.execute("CREATE TABLE " + definition)
    db.executemany("INSERT INTO Category VALUES(?,?)",[(1,"Same"),(2,"Same")])
    db.executemany("INSERT INTO Products VALUES(?,?,?,?)",
                   [(11,1,"Hot",10),(12,2,"Cold",10)])
    db.executemany("INSERT INTO OrderDetails VALUES(?,?,?)",[(1,11,1),(2,12,1)])
    observed=db.execute(q60).fetchall()
    assert observed == [("Same","Cold",10.0,50.0),("Same","Hot",10.0,50.0)],observed
    db.close()

def main():
    assert blob(KEY)==KEY_SHA,"archived key drift"
    text=KEY.read_text(encoding="utf-8")
    qs={}
    for n,(relative,sha) in SOURCES.items():
        original=BASE/relative
        assert blob(original)==sha,f"Q{n}: original question drift"
        source=original.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{n:03d}.","### Sample input and expected output",
                       "## Schema","NOT SOLVED YET","## Official solution","Pending"):
            assert marker in source,(n,marker)
        qs[n]=executable(n,original_sql(n,text))
        run_case(n,qs[n])
    known_conditional_divergence(qs[60])
    print("PASS: Q057-Q060 four pinned sources + key, four illustrative SQL contracts, four synthetic SQL groups; Q060 duplicate-name conditional divergence reproduced. No official grade or learner solve.")

if __name__=="__main__":
    main()
