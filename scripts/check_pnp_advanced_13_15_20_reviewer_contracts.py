#!/usr/bin/env python3
"""A013/A015-A020 source-pinned, read-only reviewer SQLite fixtures.

NO source/provider solution is used: all SQL here is auditor-authored.
NOT official MySQL 8 keys, original PDF/dataset parity, learner solutions,
student grades, or mastery. 21 fixture groups are synthetic or derived
from explicitly labelled local illustrations. Never write archive files.
"""
import hashlib
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCES = {
    "A013": ("2. Joins/A013. Customers who bought product 101 but never product 202.md",
             "fbe7edcdc1b633e1574ca54cf538653a757cc522"),
    "A015": ("9. Windowing Functions/A015. Show each employee next to their department average, without colla.md",
             "6140bffe76e4aaecec6fd28005aa0bc47ab842df"),
    "A016": ("3. Sorting and Grouping/A016. Departments where the average salary tops 50,000 and headcount is.md",
             "362737f84e5ee2b6fecb67ba74ec1e112a6010f3"),
    "A017": ("3. Sorting and Grouping/A017. Revenue by product category, highest first.md",
             "183466f25cf4a1d4d81674d70d06c9e0411ba09e"),
    "A018": ("3. Sorting and Grouping/A018. Monthly count of distinct buyers, cancelled orders excluded.md",
             "3d32fe4d91a33e305e91e486ebe8b1b9dd270a14"),
    "A019": ("4. Aggregation/A019. Category revenue with a grand-total row at the bottom.md",
             "82fccf042cbe4093ffc65c9af78ceb2ee07e6223"),
    "A020": ("4. Aggregation/A020. Average order value per customer, only for customers with 3+ order.md",
             "f3b7856077cf2ca55e7727e2bc51bd8450cc8cc8"),
}
# These are reviewer hypotheses, not transcriptions of provider/MySQL answers.
QUERIES = {
    "A013": """SELECT DISTINCT o.cust_id
      FROM orders AS o JOIN order_items AS i ON i.order_id=o.order_id
     WHERE o.cust_id IS NOT NULL AND i.product_id=101
       AND NOT EXISTS (
           SELECT 1 FROM orders AS banned
             JOIN order_items AS bad ON bad.order_id=banned.order_id
            WHERE banned.cust_id=o.cust_id AND bad.product_id=202)
     ORDER BY o.cust_id""",
    "A015": """SELECT emp_id,dept_id,salary,
                     AVG(salary) OVER (PARTITION BY dept_id)
                 FROM employees ORDER BY emp_id""",
    "A016": """SELECT dept_id, COUNT(*) AS headcount, AVG(salary) AS avg_salary
                 FROM employees GROUP BY dept_id
                HAVING COUNT(*)>=5 AND AVG(salary)>50000
                ORDER BY dept_id""",
    "A017": """SELECT p.category,SUM(i.qty*i.unit_price) AS revenue
                 FROM products AS p JOIN order_items AS i
                   ON i.product_id=p.product_id
                GROUP BY p.category
                ORDER BY revenue DESC,p.category""",
    "A018": """SELECT strftime('%Y-%m',order_date) AS month,
                       COUNT(DISTINCT cust_id)
                 FROM orders
                WHERE order_date IS NOT NULL AND cust_id IS NOT NULL
                  AND status <> 'cancelled'
                GROUP BY strftime('%Y-%m',order_date)
                ORDER BY month""",
    "A019": """WITH grouped AS (
                  SELECT p.category AS category,SUM(i.qty*i.unit_price) AS revenue
                    FROM products AS p JOIN order_items AS i
                      ON i.product_id=p.product_id
                   GROUP BY p.category)
                 SELECT category,revenue FROM (
                   SELECT category,revenue,0 AS is_grand_total FROM grouped
                   UNION ALL
                   SELECT 'Total',SUM(revenue),1 FROM grouped)
                 ORDER BY is_grand_total,category""",
    "A020": """SELECT cust_id,COUNT(*) AS orders_count,AVG(amount) AS avg_amount
                 FROM orders WHERE cust_id IS NOT NULL
                GROUP BY cust_id HAVING COUNT(*)>=3
                ORDER BY cust_id""",
}
DDL = (
    "CREATE TABLE employees(emp_id INTEGER, dept_id INTEGER, salary REAL);"
    "CREATE TABLE orders(order_id INTEGER, cust_id INTEGER, order_date TEXT,"
    "status TEXT, amount REAL);"
    "CREATE TABLE products(product_id INTEGER, category TEXT);"
    "CREATE TABLE order_items(item_id INTEGER, order_id INTEGER, product_id INTEGER,"
    "qty INTEGER, unit_price REAL);"
)
INSERTS = {
    "employees": "INSERT INTO employees VALUES (?,?,?)",
    "orders": "INSERT INTO orders VALUES (?,?,?,?,?)",
    "products": "INSERT INTO products VALUES (?,?)",
    "order_items": "INSERT INTO order_items VALUES (?,?,?,?,?)",
}
# Each entry: (source id, descriptive reviewer group, table rows, independently
# hand-computed expected tuples). Source's local sample is NOT an official PDF output.
CASES = [
 ("A013","local example",
  {"orders":[(10,1,None,None,None),(11,1,None,None,None),(12,2,None,None,None)],
   "order_items":[(1,10,101,1,1),(2,11,202,1,1),(3,12,101,1,1)]},[(2,)]),
 ("A013","duplicate 101 purchases and orphan item",
  {"orders":[(1,1,None,None,None),(2,1,None,None,None),(3,2,None,None,None),
             (4,3,None,None,None),(5,3,None,None,None)],
   "order_items":[(1,1,101,1,1),(2,1,101,1,1),(3,2,101,1,1),
                  (4,3,101,1,1),(5,4,101,1,1),(6,5,202,1,1),
                  (7,999,101,1,1)]},[(1,),(2,)]),
 ("A013","NULL customer, 202-only, and empty-match exclusions",
  {"orders":[(1,None,None,None,None),(2,8,None,None,None),(3,9,None,None,None)],
   "order_items":[(1,1,101,1,1),(2,2,202,1,1)]},[]),
 ("A015","local example",
  {"employees":[(1,10,40000),(2,10,60000),(3,20,90000)]},
  [(1,10,40000,50000.0),(2,10,60000,50000.0),(3,20,90000,90000.0)]),
 ("A015","NULL department and NULL salary denominator",
  {"employees":[(1,None,100),(2,None,300),(3,10,200),(4,10,None)]},
  [(1,None,100,200.0),(2,None,300,200.0),(3,10,200,200.0),(4,10,None,200.0)]),
 ("A015","singleton with missing salary and empty department",
  {"employees":[(1,10,None),(2,20,80)]},
  [(1,10,None,None),(2,20,80,80.0)]),
 ("A016","local >=5 and >50000 illustration",
  {"employees":[(1,10,60000),(2,10,60000),(3,10,60000),
                (4,10,60000),(5,10,60000),(6,20,100000)]},
  [(10,5,60000.0)]),
 ("A016","exact threshold and insufficient headcount",
  {"employees":[(1,1,50000),(2,1,50000),(3,1,50000),(4,1,50000),(5,1,50000),
                (6,2,90000),(7,2,90000),(8,2,90000),(9,2,90000)]},[]),
 ("A016","five rows, one NULL salary; COUNT star vs AVG denominator",
  {"employees":[(1,10,60000),(2,10,60000),(3,10,60000),
                (4,10,60000),(5,10,None)]},[(10,5,60000.0)]),
 ("A017","local line-price example",
  {"products":[(101,"Audio"),(102,"Home")],
   "order_items":[(1,1,101,2,10),(2,1,102,1,30)]},
  [("Home",30.0),("Audio",20.0)]),
 ("A017","same-category fan-out, unsold category, NULL line arithmetic",
  {"products":[(1,"A"),(2,"A"),(3,"B"),(4,"Unused")],
   "order_items":[(1,1,1,2,10),(2,1,2,1,5),(3,1,3,1,30),
                  (4,1,3,None,10)]},
  [("B",30.0),("A",25.0)]),
 ("A017","all categories unsold",{"products":[(1,"A"),(2,"B")]},[]),
 ("A018","local distinct-buyer illustration",
  {"orders":[(1,10,"2026-01-05","completed",None),
             (2,10,"2026-01-07","completed",None),
             (3,20,"2026-01-09","cancelled",None),
             (4,20,"2026-02-01","completed",None)]},
  [("2026-01",1),("2026-02",1)]),
 ("A018","multiple buyers, duplicate orders and cancelled-only month",
  {"orders":[(1,1,"2025-12-01","completed",None),
             (2,1,"2025-12-31","completed",None),
             (3,2,"2025-12-05","shipped",None),
             (4,3,"2026-01-02","cancelled",None)]},[("2025-12",2)]),
 ("A018","NULLs and mixed-case cancelled are undefined source policies",
  {"orders":[(1,1,"2026-03-05","Cancelled",None),
             (2,2,"2026-03-06","cancelled",None),
             (3,3,None,"completed",None),
             (4,4,"2026-03-07",None,None),
             (5,None,"2026-03-07","completed",None)]},[("2026-03",1)]),
 ("A019","local total-row example",
  {"products":[(101,"Audio"),(102,"Home")],
   "order_items":[(1,1,101,2,10),(2,1,102,1,30)]},
  [("Audio",20.0),("Home",30.0),("Total",50.0)]),
 ("A019","literal Total category collides with total label",
  {"products":[(1,"Audio"),(2,"Total")],
   "order_items":[(1,1,1,2,10),(2,1,2,1,30)]},
  [("Audio",20.0),("Total",30.0),("Total",50.0)]),
 ("A019","no order items produces NULL grand total",
  {"products":[(1,"Audio")]},[("Total",None)]),
 ("A020","local >=3 order sample",
  {"orders":[(1,10,None,None,10),(2,10,None,None,20),
             (3,10,None,None,30),(4,20,None,None,100),
             (5,20,None,None,100)]},[(10,3,20.0)]),
 ("A020","three orders, one NULL amount; count vs mean denominator",
  {"orders":[(1,1,None,None,10),(2,1,None,None,30),
             (3,1,None,None,None),(4,2,None,None,99),
             (5,2,None,None,99)]},[(1,3,20.0)]),
 ("A020","NULL customer excluded by reviewer assumption",
  {"orders":[(1,None,None,None,5),(2,None,None,None,5),
             (3,None,None,None,5),(4,1,None,None,2)]},[]),
]
def verify_originals():
    for sid,(relative,expected_sha) in SOURCES.items():
        raw=(BASE/relative).read_bytes()
        found=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        assert found == expected_sha, f"{sid} immutable Git-blob mismatch {found}"
        s=raw.decode("utf-8")
        assert s.startswith(f"# Advanced Q{sid[1:]}. "),sid
        assert "NOT SOLVED YET" in s and "## My solution — SQLite\n\nPending." in s,sid
        assert "## Official solution\n\nPending until" in s,sid
    print("PASS original-source guard: 7/7 immutable PNP source blobs and Pending histories")
def verify_cases():
    assert len(CASES)==21 and {x[0] for x in CASES}==set(SOURCES)
    counts={sid:0 for sid in SOURCES}
    for sid,label,tables,expected in CASES:
        with sqlite3.connect(":memory:") as db:
            db.executescript(DDL)
            for table,rows in tables.items():
                db.executemany(INSERTS[table],rows)
            found=db.execute(QUERIES[sid]).fetchall()
            assert found==expected,(
                f"{sid} {label}: expected={expected!r}, found={found!r}")
        counts[sid]+=1
        print(f"PASS {sid}: {label} (synthetic/local illustration)")
    assert list(counts.values())==[3]*7, counts
    print("PASS: 21/21 reviewer-only SQLite fixture groups; seven source IDs")
if __name__=="__main__":
    verify_originals()
    verify_cases()
    print("PARTIAL ONLY: 0 source MySQL keys executed, 0 authenticated official "
          "answers, 0 learner submissions/completions, 0 native MySQL parity; "
          "PDF render, source dataset, semantics and licensing unresolved.")
