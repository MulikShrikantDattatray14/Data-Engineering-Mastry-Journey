#!/usr/bin/env python3
"""Partial A021-A030 audit. Source-pinned; reviewer examples, NOT supplied answers.

All ten archived learner and provider answer slots are pending. This script
must not write any source, journal, completion or foundation file. SQL here is
auditor-authored to test bounded *principles*, never official-answer parity.
"""
import hashlib
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
PINS = {
    "A021": ("3. Sorting and Grouping/A021. Which weekday brings in the most orders.md", "ecbffb7cdd43adf69c8b08a861e0e00efe4c5964", 5),
    "A022": ("4. Aggregation/A022. Turn order status into columns one row per customer, counts per st.md", "0ea4e11d0f88dbc1f493c8bf988dc75b0018a91f", 6),
    "A023": ("4. Aggregation/A023. Revenue by category with 2025 and 2026 side by side.md", "80ff729583250f12a84a21948d7b579748c74385", 6),
    "A024": ("4. Aggregation/A024. Cancellation rate per customer as a percentage.md", "9ee7fe4ccc0fddad0445f3c826d2da066378f521", 6),
    "A025": ("3. Sorting and Grouping/A025. Customers who ordered in both 2025 and 2026.md", "6472992948dbc22431e0cfc060c8b76e70e9592a", 6),
    "A026": ("4. Aggregation/A026. Unpivot turn three metric columns of a summary table into labelval.md", "496bef1b16778344cc2db5f17e23c3a2e9934ebf", 6),
    "A027": ("4. Aggregation/A027. First order, last order and active lifespan per customer.md", "e04c9c77c24074b9ee487c44f3a3ec2bb8fa8c45", 6),
    "A028": ("6. SubQueries/A028. Employees paid above the average of their own department.md", "604c8cdbce16585ec2bac1aae993c5a665770d48", 7),
    "A029": ("6. SubQueries/A029. The most recent order for every customer, ties allowed.md", "0acf6cd02ea12eeb48afedc842b837f94cc03627", 7),
    "A030": ("6. SubQueries/A030. Products priced above their category average.md", "880601ae007f5e973173e60e78796ca0372af20d", 7),
}

def check_preserved_sources():
    for sid, (relative, pin, page) in PINS.items():
        data = (BASE / relative).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert actual == pin, (sid, "preserved original Git blob changed", actual)
        text = data.decode("utf-8")
        assert text.startswith(f"# Advanced Q{sid[1:]}. "), sid
        assert f"question {int(sid[1:])}, PDF p. {page}" in text, sid
        for section in ("## Question and image", "### Sample input and expected output",
                        "## Schema", "## My solution — SQLite",
                        "## My solution — SQL Server", "## Official solution"):
            assert section in text, (sid, section)
        assert "NOT SOLVED YET" in text, sid
        assert "## My solution — SQLite\n\nPending." in text, sid
        assert "## My solution — SQL Server\n\nPending." in text, sid
        assert "## Official solution\n\nPending until" in text, sid
        assert "seven-table" in text, sid
    print("PASS: A021-A030 10/10 immutable original source blobs, locally attributed PDF pages, original pending learner/answer state")

SCHEMAS = {
    "orders": "CREATE TABLE orders(order_id INTEGER, cust_id INTEGER, order_date TEXT, status TEXT)",
    "items": "CREATE TABLE order_items(item_id INTEGER, order_id INTEGER, product_id INTEGER, qty REAL, unit_price REAL)",
    "products": "CREATE TABLE products(product_id INTEGER, category TEXT, price REAL)",
    "employees": "CREATE TABLE employees(emp_id INTEGER, dept_id INTEGER, salary REAL)",
    "summary": "CREATE TABLE cust_summary(cust_id INTEGER, delivered INTEGER, cancelled INTEGER, placed INTEGER)",
}
INSERT = {
    "orders": "INSERT INTO orders VALUES (?,?,?,?)",
    "items": "INSERT INTO order_items VALUES (?,?,?,?,?)",
    "products": "INSERT INTO products VALUES (?,?,?)",
    "employees": "INSERT INTO employees VALUES (?,?,?)",
    "summary": "INSERT INTO cust_summary VALUES (?,?,?,?)",
}
SQL = {
    "A021": """WITH counts AS (
      SELECT CASE strftime('%w',order_date)
        WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday' WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday' WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday' WHEN '6' THEN 'Saturday' END weekday,
        COUNT(*) n
      FROM orders WHERE date(order_date) IS NOT NULL GROUP BY 1
    ), ranked AS (
      SELECT weekday,n,DENSE_RANK() OVER (ORDER BY n DESC) r FROM counts
    ) SELECT weekday,n FROM ranked WHERE r=1 ORDER BY weekday""",
    "A022": """SELECT cust_id,
      SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END),
      SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END)
      FROM orders GROUP BY cust_id ORDER BY cust_id""",
    "A023": """SELECT p.category,
      SUM(CASE WHEN strftime('%Y',o.order_date)='2025' THEN oi.qty*oi.unit_price ELSE 0 END),
      SUM(CASE WHEN strftime('%Y',o.order_date)='2026' THEN oi.qty*oi.unit_price ELSE 0 END)
      FROM order_items oi JOIN orders o ON oi.order_id=o.order_id
      JOIN products p ON p.product_id=oi.product_id
      GROUP BY p.category ORDER BY p.category""",
    "A024": """SELECT cust_id,
      ROUND(100.0*SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END)/COUNT(*),2)
      FROM orders GROUP BY cust_id ORDER BY cust_id""",
    "A025": """SELECT cust_id FROM orders WHERE cust_id IS NOT NULL
      GROUP BY cust_id HAVING
      SUM(CASE WHEN strftime('%Y',order_date)='2025' THEN 1 ELSE 0 END)>0
      AND SUM(CASE WHEN strftime('%Y',order_date)='2026' THEN 1 ELSE 0 END)>0
      ORDER BY cust_id""",
    "A026": """WITH expanded AS (
      SELECT cust_id,1 n,'delivered' metric,delivered val FROM cust_summary
      UNION ALL SELECT cust_id,2,'cancelled',cancelled FROM cust_summary
      UNION ALL SELECT cust_id,3,'placed',placed FROM cust_summary
    ) SELECT cust_id,metric,val FROM expanded ORDER BY cust_id,n""",
    "A027": """SELECT cust_id,MIN(order_date),MAX(order_date),
      CAST(julianday(MAX(order_date))-julianday(MIN(order_date)) AS INTEGER)
      FROM orders WHERE cust_id IS NOT NULL AND date(order_date) IS NOT NULL
      GROUP BY cust_id ORDER BY cust_id""",
    "A028": """SELECT e.emp_id,e.dept_id,e.salary FROM employees e
      WHERE e.salary > (SELECT AVG(d.salary) FROM employees d
                        WHERE d.dept_id=e.dept_id)
      ORDER BY e.emp_id""",
    "A029": """SELECT o.order_id,o.cust_id,o.order_date FROM orders o
      WHERE o.order_date=(SELECT MAX(x.order_date) FROM orders x
                          WHERE x.cust_id=o.cust_id)
      ORDER BY o.order_id""",
    "A030": """SELECT p.product_id,p.category,p.price FROM products p
      WHERE p.price>(SELECT AVG(x.price) FROM products x
                     WHERE x.category=p.category) ORDER BY p.product_id""",
}

def test(sid, label, data, expected):
    # Each call is a new isolated in-memory SQLite DB. No tests compare two
    # candidate queries to each other; each asserts independently expected rows.
    with sqlite3.connect(":memory:") as db:
        for table, rows in data.items():
            db.execute(SCHEMAS[table])
            if rows:
                db.executemany(INSERT[table], rows)
        actual = db.execute(SQL[sid]).fetchall()
    assert actual == expected, f"{sid} {label}: {actual!r} != {expected!r}"
    print(f"PASS {sid} {label} (auditor-authored SQL, not official key)")

def main():
    check_preserved_sources()
    o = lambda id,cust,date,status=None: (id,cust,date,status)
    test("A021","archived local illustration",{"orders":[o(1,1,"2026-01-05"),o(2,2,"2026-01-05"),o(3,3,"2026-01-06")]},[("Monday",2)])
    test("A021","tie/NULL diagnostic; all tied days retained only by reviewer policy",{"orders":[o(1,1,"2026-01-05"),o(2,2,"2026-01-06"),o(3,3,None)]},[("Monday",1),("Tuesday",1)])
    test("A022","archived local illustration",{"orders":[o(1,10,None,"completed"),o(2,10,None,"cancelled"),o(3,20,None,"completed")]},[(10,1,1),(20,1,0)])
    test("A022","unlisted status/NULL remains outside displayed status columns",{"orders":[o(1,10,None,"placed"),o(2,10,None,None),o(3,20,None,"cancelled")]},[(10,0,0),(20,0,1)])
    test("A023","archived local illustration",{"products":[(101,"Audio",None),(102,"Home",None)],
         "orders":[o(1,1,"2025-06-01"),o(2,1,"2026-06-01"),o(3,1,"2025-07-01")],
         "items":[(1,1,101,1,10),(2,2,101,1,15),(3,3,102,1,5)]},[("Audio",10,15),("Home",5,0)])
    test("A023","date/year edge, repeated items, orphan product and out-of-period lines",{
         "products":[(101,"Audio",None),(103,"Home",None)],
         "orders":[o(1,1,"2025-12-31"),o(2,2,"2026-01-01"),o(3,3,"2024-01-01")],
         "items":[(1,1,101,2,4),(2,1,101,3,1),(3,2,101,1,5),(4,3,103,100,8),(5,2,999,1,7)]},[("Audio",11,5),("Home",0,0)])
    test("A024","archived local illustration",{"orders":[o(1,10,None,"cancelled"),o(2,10,None,"completed"),o(3,20,None,"completed")]},[(10,50),(20,0)])
    test("A024","fractional denominator/NULL-status inclusion",{"orders":[o(1,10,None,"cancelled"),o(2,10,None,"cancelled"),o(3,10,None,"placed"),o(4,20,None,None)]},[(10,66.67),(20,0)])
    test("A025","archived local illustration",{"orders":[o(1,10,"2025-03-01"),o(2,10,"2026-02-01"),o(3,20,"2026-04-01")]},[(10,)])
    test("A025","duplicate orders, NULL customer, unrelated years",{"orders":[o(1,1,"2025-01-01"),o(2,1,"2026-12-31"),o(3,1,"2026-12-31"),o(4,2,"2024-01-01"),o(5,None,"2025-01-01"),o(6,None,"2026-01-01")]},[(1,)])
    test("A026","archived local illustration",{"summary":[(1,2,1,3)]},[(1,"delivered",2),(1,"cancelled",1),(1,"placed",3)])
    test("A026","multiple customers, NULL metrics not silently discarded",{"summary":[(1,None,0,2),(2,0,1,None)]},[(1,"delivered",None),(1,"cancelled",0),(1,"placed",2),(2,"delivered",0),(2,"cancelled",1),(2,"placed",None)])
    test("A027","archived local illustration",{"orders":[o(1,10,"2026-01-01"),o(2,10,"2026-01-11"),o(3,20,"2026-02-01")]},[(10,"2026-01-01","2026-01-11",10),(20,"2026-02-01","2026-02-01",0)])
    test("A027","year crossing, NULL dates and zero lifespan",{"orders":[o(1,1,"2025-12-31"),o(2,1,"2026-01-02"),o(3,1,None),o(4,2,"2026-02-01")]},[(1,"2025-12-31","2026-01-02",2),(2,"2026-02-01","2026-02-01",0)])
    test("A028","archived local illustration",{"employees":[(1,10,40000),(2,10,60000),(3,20,90000)]},[(2,10,60000)])
    test("A028","ties, NULL salary, NULL department and isolated department",{"employees":[(1,10,100),(2,10,100),(3,10,300),(4,10,None),(5,20,5),(6,None,999)]},[(3,10,300)])
    test("A029","archived local illustration; keep same-date ties",{"orders":[o(1,10,"2026-01-01"),o(2,10,"2026-01-05"),o(3,10,"2026-01-05"),o(4,20,"2026-01-02")]},[(2,10,"2026-01-05"),(3,10,"2026-01-05"),(4,20,"2026-01-02")])
    test("A029","multiple customers, null dates, all-null-only customer",{"orders":[o(1,10,"2025-01-01"),o(2,10,"2026-01-01"),o(3,10,"2026-01-01"),o(4,20,None),o(5,30,"2026-06-01")]},[(2,10,"2026-01-01"),(3,10,"2026-01-01"),(5,30,"2026-06-01")])
    test("A030","archived local illustration",{"products":[(101,"Audio",100),(102,"Audio",300),(103,"Home",50)]},[(102,"Audio",300)])
    test("A030","ties, NULL price, NULL category excluded under reviewer policy",{"products":[(1,"Audio",10),(2,"Audio",30),(3,"Audio",None),(4,"Home",40),(5,"Home",40),(6,None,100)]},[(2,"Audio",30)])
    print("PARTIAL: 10 source statements independently inspected + 20 SQLite groups using reviewer-authored principle queries. NO official SQL replay, PDF/native MySQL parity, new learner completion or mastery. All ten answers still pending.")

if __name__ == "__main__":
    main()
