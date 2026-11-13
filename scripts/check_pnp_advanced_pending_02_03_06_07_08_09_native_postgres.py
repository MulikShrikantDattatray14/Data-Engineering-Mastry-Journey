#!/usr/bin/env python3
"""A002/A003/A006/A007/A008/A009: source-pinned *reviewer-only* PostgreSQL 16 probes.

The preserved learner SQL and displayed official-answer sections for all six
questions say Pending. Every executable query below is authored by the auditor
as an explicit synthetic principle model, NOT a recovered MySQL solution,
officially authenticated answer, learner submission, or proof of mastery.
No original source/dataset/progress/canonical notes are modified.
"""
import hashlib
import os
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
PINS = {
    "A002": ("6. SubQueries/A002. Second highest salary, no LIMIT and no window function.md",
             "d797abb456ebf1a35ad4ade88c345170c997043c"),
    "A003": ("9. Windowing Functions/A003. Third highest distinct salary, ties collapsed.md",
             "3d93fdfbec83c68a495dee74e044b24fb0470004"),
    "A006": ("2. Joins/A006. MySQL has no FULL OUTER JOIN. Emulate one between customers and or.md",
             "20e4460e715ec53fd41f063e1368fa3753f2a0fd"),
    "A007": ("6. SubQueries/A007. Product IDs that exist in products but were never ordered — set-op.md",
             "92d491023d8184e85e1732f4122b967e31575d52"),
    "A008": ("2. Joins/A008. Build a complete date × category grid so empty combinations still.md",
             "668f755b58b74935d9be1b7f6e2f635b713b4ec8"),
    "A009": ("2. Joins/A009. Bucket every product into a price band using a non-equi join.md",
             "6bcfa001f4a28934d4e06d277463eb242822a4de"),
}
DDL = {
    "A002": ("CREATE TEMP TABLE employees(emp_id INTEGER PRIMARY KEY, salary NUMERIC)",),
    "A003": ("CREATE TEMP TABLE employees(emp_id INTEGER PRIMARY KEY, salary NUMERIC)",),
    "A006": ("CREATE TEMP TABLE customers(cust_id INTEGER PRIMARY KEY, cust_name TEXT)",
             "CREATE TEMP TABLE orders(order_id INTEGER PRIMARY KEY, cust_id INTEGER)"),
    "A007": ("CREATE TEMP TABLE products(product_id INTEGER PRIMARY KEY)",
             "CREATE TEMP TABLE order_items(item_id INTEGER PRIMARY KEY, product_id INTEGER)"),
    "A008": ("CREATE TEMP TABLE report_dates(report_date DATE PRIMARY KEY)",
             "CREATE TEMP TABLE categories(category TEXT PRIMARY KEY)"),
    "A009": ("CREATE TEMP TABLE products(product_id INTEGER PRIMARY KEY, price NUMERIC)",
             "CREATE TEMP TABLE price_bands(band TEXT PRIMARY KEY, min_price NUMERIC, max_price NUMERIC)"),
}
SQL = {
    "A002": ("""SELECT MAX(salary) FROM employees
                 WHERE salary < (SELECT MAX(salary) FROM employees)""",),
    "A003": ("""SELECT MAX(salary) FROM (
                    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS r
                    FROM employees WHERE salary IS NOT NULL
                 ) ranked WHERE r=3""",),
    "A006": ("""SELECT COALESCE(c.cust_id,o.cust_id) AS cust_id, c.cust_name, o.order_id
                 FROM customers c LEFT JOIN orders o ON c.cust_id=o.cust_id
                 UNION ALL
                 SELECT o.cust_id, c.cust_name, o.order_id
                 FROM orders o LEFT JOIN customers c ON c.cust_id=o.cust_id
                 WHERE c.cust_id IS NULL""",
             """SELECT COALESCE(c.cust_id,o.cust_id), c.cust_name, o.order_id
                FROM customers c FULL OUTER JOIN orders o ON c.cust_id=o.cust_id"""),
    "A007": ("""SELECT product_id FROM products
                  EXCEPT SELECT product_id FROM order_items""",
             """SELECT p.product_id FROM products p
                  WHERE NOT EXISTS (SELECT 1 FROM order_items i
                                    WHERE i.product_id=p.product_id)"""),
    "A008": ("""SELECT d.report_date::text, c.category FROM report_dates d
                  CROSS JOIN categories c""",),
    "A009": ("""SELECT p.product_id, b.band FROM products p
                  LEFT JOIN price_bands b
                    ON p.price >= b.min_price AND p.price < b.max_price""",
             """SELECT p.product_id, b.band FROM products p
                  JOIN price_bands b
                    ON p.price >= b.min_price AND p.price < b.max_price"""),
}
# Review fixtures: expected tuples are hand asserted, never derived from the SQL under test.
FIXTURES = [
 ("A002","local illustration",{"employees":("emp_id,salary",[(1,300),(2,200),(3,100)])},
  [[(200,)]]),
 ("A002","tied top and NULL",{"employees":("emp_id,salary",[(1,300),(2,300),(3,200),(4,100),(5,None)])},
  [[(200,)]]),
 ("A002","one distinct and empty",{"employees":("emp_id,salary",[(1,7),(2,7)])},
  [[(None,)]]),
 ("A002","empty table",{},[[(None,)]]),
 ("A003","local illustration",{"employees":("emp_id,salary",[(1,300),(2,200),(3,200),(4,100)])},
  [[(100,)]]),
 ("A003","top tie / NULL / fourth distinct",{"employees":("emp_id,salary",[(1,500),(2,500),(3,300),(4,200),(5,100),(6,None)])},
  [[(200,)]]),
 ("A003","only two distinct salary levels",{"employees":("emp_id,salary",[(1,200),(2,100),(3,100),(4,None)])},
  [[(None,)]]),
 ("A003","empty table",{},[[(None,)]]),
 ("A006","local orphan illustration",{
   "customers":("cust_id,cust_name",[(1,"Asha"),(2,"Mira")]),
   "orders":("order_id,cust_id",[(10,1),(11,3)])},
  [[(1,"Asha",10),(2,"Mira",None),(3,None,11)]]*2),
 ("A006","multiple matches / NULL key / orphan",{
   "customers":("cust_id,cust_name",[(1,"Asha"),(2,"Mira")]),
   "orders":("order_id,cust_id",[(10,1),(11,1),(12,None),(13,999)])},
  [[(1,"Asha",10),(1,"Asha",11),(2,"Mira",None),(None,None,12),(999,None,13)]]*2),
 ("A006","only orphan orders",{"orders":("order_id,cust_id",[(20,42),(21,None)])},
  [[(42,None,20),(None,None,21)]]*2),
 ("A006","both empty",{},[[]]*2),
 ("A007","local illustration",{
   "products":("product_id",[(101,),(102,)]),
   "order_items":("item_id,product_id",[(1,101)])}, [[(102,)]]*2),
 ("A007","duplicate uses / NULL / unknown product",{
   "products":("product_id",[(101,),(102,),(103,)]),
   "order_items":("item_id,product_id",[(1,101),(2,101),(3,None),(4,999),(5,103)])},
  [[(102,)]]*2),
 ("A007","all unbought",{"products":("product_id",[(101,),(102,)])},
  [[(101,),(102,)]]*2),
 ("A007","no products",{"order_items":("item_id,product_id",[(1,7)])},[[]]*2),
 ("A008","illustrated two-by-two",{
   "report_dates":("report_date",[("2026-01-01",),("2026-01-02",)]),
   "categories":("category",[("Audio",),("Home",)])},
  [[("2026-01-01","Audio"),("2026-01-01","Home"),("2026-01-02","Audio"),("2026-01-02","Home")]]),
 ("A008","one date one category",{
   "report_dates":("report_date",[("2026-02-01",)]),
   "categories":("category",[("Books",)])},[[("2026-02-01","Books")]]),
 ("A008","date dimension empty",{"categories":("category",[("Audio",)])},[[]]),
 ("A008","category dimension empty",{"report_dates":("report_date",[("2026-02-01",)])},[[]]),
 ("A009","local half-open bands",{
   "products":("product_id,price",[(101,20),(102,75)]),
   "price_bands":("band,min_price,max_price",[("Low",0,50),("Mid",50,100)])},
  [[(101,"Low"),(102,"Mid")],[(101,"Low"),(102,"Mid")]]),
 ("A009","boundaries / out of-range / NULL",{
   "products":("product_id,price",[(1,0),(2,50),(3,100),(4,-1),(5,None)]),
   "price_bands":("band,min_price,max_price",[("Low",0,50),("Mid",50,100)])},
  [[(1,"Low"),(2,"Mid"),(3,None),(4,None),(5,None)],
   [(1,"Low"),(2,"Mid")]]),
 ("A009","overlap shows duplicate product rows",{
   "products":("product_id,price",[(1,60),(2,125)]),
   "price_bands":("band,min_price,max_price",[("Mid",50,100),("Overlap",60,130)])},
  [[(1,"Mid"),(1,"Overlap"),(2,"Overlap")],
   [(1,"Mid"),(1,"Overlap"),(2,"Overlap")]]),
 ("A009","no bands means LEFT and INNER differ",{
   "products":("product_id,price",[(1,20)])},
  [[(1,None)],[]]),
]

def source_check():
    for sid,(path,pinned) in PINS.items():
        data=(BASE/path).read_bytes()
        got=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        assert got==pinned, f"{sid}: source archive changed {got}"
        s=data.decode("utf-8")
        assert s.startswith(f"# Advanced Q{sid[1:]}. ")
        assert "NOT SOLVED YET" in s
        assert "## My solution — SQLite\n\nPending." in s
        assert "## My solution — SQL Server\n\nPending." in s
        assert "## Official solution\n\nPending until" in s
        assert "Illustrative example" in s
        print(f"PIN {sid} {got}; indexed + statement inspected; all source answers pending")

def sorted_rows(rows):
    return sorted(rows,key=repr)

def main():
    source_check()
    with psycopg.connect(host=os.getenv("PGHOST","127.0.0.1"),
                         port=os.getenv("PGPORT","5432"),
                         user=os.getenv("PGUSER","audit"),
                         password=os.getenv("PGPASSWORD","audit"),
                         dbname=os.getenv("PGDATABASE","audit")) as conn:
        with conn.cursor() as cur:
            cur.execute("SHOW server_version_num")
            version=int(cur.fetchone()[0])
            assert version//10000==16, version
            print(f"Native PostgreSQL server_version_num={version}")
    for sid,label,records,expected_queries in FIXTURES:
        assert len(expected_queries)==len(SQL[sid])
        with psycopg.connect(host=os.getenv("PGHOST","127.0.0.1"),
                             port=os.getenv("PGPORT","5432"),
                             user=os.getenv("PGUSER","audit"),
                             password=os.getenv("PGPASSWORD","audit"),
                             dbname=os.getenv("PGDATABASE","audit")) as conn:
            with conn.cursor() as cur:
                for ddl in DDL[sid]:
                    cur.execute(ddl)
                for table,(col_csv,rows) in records.items():
                    cols=col_csv.split(",")
                    if rows:
                        placeholders=",".join(["%s"]*len(cols))
                        cur.executemany(f"INSERT INTO {table}({col_csv}) VALUES ({placeholders})",rows)
                for idx,statement in enumerate(SQL[sid]):
                    cur.execute(statement)
                    actual=cur.fetchall()
                    expected=expected_queries[idx]
                    assert sorted_rows(actual)==sorted_rows(expected),(
                        sid,label,idx,actual,expected)
            conn.rollback()
        print(f"PASS {sid} {label}: {len(expected_queries)} auditor-authored "
              f"query variant(s), independently expected rows")
    print(f"PARTIAL ONLY: {len(FIXTURES)} independent native PostgreSQL 16 "
          "synthetic fixture groups across 6 already-inspected source IDs. "
          "No source official/learner answer exists in these Markdown records. "
          "PDF/MySQL/dataset parity, live grading, independent learner solve "
          "and comprehensive audit signoff NOT established.")

if __name__=="__main__":
    main()
