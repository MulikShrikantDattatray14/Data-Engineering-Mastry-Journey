#!/usr/bin/env python3
"""Partial A051-A060 source inspection and bounded reviewer SQLite window tests.

Do not treat reviewer's SQL as provider answers, grading, learner attempts or mastery.
The original source archive is NEVER modified by this read-only checker.
"""
import hashlib
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/"
    "9. Windowing Functions")
PINS = {
    "A051": ("A051. Show ROW_NUMBER, RANK and DENSE_RANK together and explain the diff.md", "2593dee4fa58352b31442c2a49bdcb149fd30010", 11),
    "A052": ("A052. Rank employees by salary inside each department.md", "1580cbe5bd7a7de498021483be39e67e49c5da72", 11),
    "A053": ("A053. The highest-paid employee per department, ties broken by earliest.md", "2415e2fb39c673626f3fc803d37d6964703ca6ac", 11),
    "A054": ("A054. Percentile position of each salary within the company.md", "aee8087b885167e552415ab48df1c9aaa9e1d84c", 11),
    "A055": ("A055. Share of employees earning at or below each salary.md", "8c8c4d7ead577f786ab77919f6c04bc0798a7344", 11),
    "A056": ("A056. Rank categories by revenue — a window on top of an aggregate.md", "fb9e57e02cd038ed2cd312ed64c2769f7e38fb3d", 11),
    "A057": ("A057. Month-over-month revenue change in absolute terms.md", "69fa22926de433ee2b8190d2e5d64bf8b10bde1c", 12),
    "A058": ("A058. Same thing as a growth percentage, safe against a zero denominator.md", "5a1aecd38b429843c4bad310e1c25e2809ac5e4d", 12),
    "A059": ("A059. Days between each customer's consecutive orders.md", "82bfe53ac71b6023478235d16b297e5d95d8f14c", 12),
    "A060": ("A060. Next order date per customer, with a placeholder when there isn't.md", "6237a4bfa32b819c41c85a6e07b5a7a302489ab4", 12),
}
EMP = """CREATE TABLE employees(
    emp_id INTEGER, dept_id INTEGER, salary REAL, hire_date TEXT);"""
ORDERS = """CREATE TABLE orders(
    order_id INTEGER, cust_id INTEGER, order_date TEXT, amount REAL);"""
ITEMS = """CREATE TABLE products(product_id INTEGER, category TEXT);
CREATE TABLE order_items(item_id INTEGER, product_id INTEGER, qty INTEGER, unit_price REAL);"""
REVIEWER_SQL = {
 "A051": """SELECT emp_id,salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC,emp_id) row_number,
    RANK() OVER (ORDER BY salary DESC) salary_rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) dense_rank
    FROM employees ORDER BY salary DESC,emp_id""",
 "A052": """SELECT emp_id,dept_id,salary,
    RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) salary_rank
    FROM employees ORDER BY dept_id,salary DESC,emp_id""",
 "A053": """WITH chosen AS (
    SELECT dept_id,emp_id,salary,
    ROW_NUMBER() OVER (PARTITION BY dept_id
       ORDER BY salary DESC,hire_date ASC,emp_id ASC) rn
    FROM employees)
    SELECT dept_id,emp_id,salary FROM chosen WHERE rn=1 ORDER BY dept_id""",
 "A054": """SELECT emp_id,salary,
    PERCENT_RANK() OVER (ORDER BY salary ASC) percentile_rank
    FROM employees ORDER BY salary,emp_id""",
 "A055": """SELECT emp_id,salary,
    CUME_DIST() OVER (ORDER BY salary ASC) share_at_or_below
    FROM employees ORDER BY salary,emp_id""",
 "A056": """WITH category_revenue AS (
    SELECT p.category,SUM(oi.qty*oi.unit_price) revenue
    FROM order_items oi JOIN products p ON p.product_id=oi.product_id
    GROUP BY p.category)
    SELECT category,revenue,RANK() OVER (ORDER BY revenue DESC) revenue_rank
    FROM category_revenue ORDER BY revenue DESC,category""",
 "A057": """WITH monthly AS (
    SELECT substr(order_date,1,7) month,SUM(amount) revenue
    FROM orders WHERE order_date IS NOT NULL GROUP BY substr(order_date,1,7)),
    lagged AS (SELECT month,revenue,LAG(revenue) OVER (ORDER BY month) prior
    FROM monthly)
    SELECT month,revenue,prior,revenue-prior FROM lagged ORDER BY month""",
 "A058": """WITH monthly AS (
    SELECT substr(order_date,1,7) month,SUM(amount) revenue
    FROM orders WHERE order_date IS NOT NULL GROUP BY substr(order_date,1,7)),
    lagged AS (SELECT month,revenue,LAG(revenue) OVER (ORDER BY month) prior
    FROM monthly)
    SELECT month,revenue,prior,
    (revenue-prior)*100.0/NULLIF(prior,0)
    FROM lagged ORDER BY month""",
 "A059": """WITH timed AS (
    SELECT cust_id,order_id,order_date,
    LAG(order_date) OVER (PARTITION BY cust_id
       ORDER BY order_date,order_id) prior FROM orders)
    SELECT cust_id,order_id,
    CASE WHEN prior IS NULL THEN NULL
         ELSE CAST(julianday(order_date)-julianday(prior) AS INTEGER) END
    FROM timed ORDER BY cust_id,order_date,order_id""",
 "A060": """WITH timed AS (
    SELECT cust_id,order_id,order_date,
    LEAD(order_date) OVER (PARTITION BY cust_id
       ORDER BY order_date,order_id) next_date FROM orders)
    SELECT cust_id,order_id,COALESCE(next_date,'No later order')
    FROM timed ORDER BY cust_id,order_date,order_id""",
}

def check_sources():
    assert len(PINS)==10
    for sid,(filename,sha,page) in PINS.items():
        data=(BASE/filename).read_bytes()
        got=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        assert got==sha,(sid,"original archive differs",got,sha)
        t=data.decode("utf-8")
        number=int(sid[1:])
        markers=(
            "# Advanced Q"+sid[1:]+".",
            "question "+str(number)+", PDF p. "+str(page),
            "### Sample input and expected output (illustrative)",
            "The PDF does not provide separate sample input",
            "## Schema", "seven-table example schema",
            "NOT SOLVED YET",
            "## My solution — SQLite\n\nPending.",
            "## My solution — SQL Server\n\nPending.",
            "## Official solution\n\nPending until",
        )
        for marker in markers:
            assert marker in t,(sid,"missing archived text",marker)
        print("PASS",sid,"original blob and statement/illustration/pending fields inspected")

def check_case(sid,name,schema,rows,expected):
    with sqlite3.connect(":memory:") as db:
        db.executescript(schema)
        for table,values in rows.items():
            if values:
                db.executemany("INSERT INTO "+table+" VALUES ("+
                    ",".join("?" for _ in values[0])+")",values)
        observed=db.execute(REVIEWER_SQL[sid]).fetchall()
        assert observed==expected,(sid,name,observed,expected)
    print("PASS",sid,name,"(synthetic SQLite reviewer SQL, NOT original supplier key)")

def main():
    check_sources()
    e=lambda rows:[tuple(list(r)+[None]) if len(r)==3 else r for r in rows]
    check_case("A051","archived ROW_NUMBER/RANK/DENSE_RANK tie illustration",EMP,
        {"employees":e([(1,1,100),(2,1,90),(3,1,90),(4,1,80)])},
        [(1,100,1,1,1),(2,90,2,2,2),(3,90,3,2,2),(4,80,4,4,3)])
    check_case("A051","all salary peers keep deterministic row numbers",EMP,
        {"employees":e([(3,1,50),(1,1,50),(2,1,50)])},
        [(1,50,1,1,1),(2,50,2,1,1),(3,50,3,1,1)])
    check_case("A052","archived separate department ranking",EMP,
        {"employees":e([(1,10,100),(2,10,90),(3,10,90),(4,20,80)])},
        [(1,10,100,1),(2,10,90,2),(3,10,90,2),(4,20,80,1)])
    check_case("A052","two independent departments and rank gap",EMP,
        {"employees":e([(1,10,20),(2,10,20),(3,10,10),(4,20,1)])},
        [(1,10,20,1),(2,10,20,1),(3,10,10,3),(4,20,1,1)])
    check_case("A053","archived earliest-hire salary tie",EMP,
        {"employees":[(1,10,100,"2020-01-01"),(2,10,100,"2019-01-01"),
                      (3,20,80,"2021-01-01")]},
        [(10,2,100),(20,3,80)])
    check_case("A053","double tie resolved by employee ID; salary before hire date",EMP,
        {"employees":[(9,10,100,"2010-01-01"),(5,10,200,"2020-01-01"),
                      (2,10,200,"2020-01-01"),(4,20,40,"2022-01-01")]},
        [(10,2,200),(20,4,40)])
    check_case("A054","archived percentile rank",EMP,
        {"employees":e([(1,10,40000),(2,10,60000),(3,10,80000)])},
        [(1,40000,0.0),(2,60000,0.5),(3,80000,1.0)])
    check_case("A054","two low-salary peers share percentile and max is one",EMP,
        {"employees":e([(2,10,100),(1,10,100),(3,10,300)])},
        [(1,100,0.0),(2,100,0.0),(3,300,1.0)])
    check_case("A055","archived cumulative fraction includes salary peers",EMP,
        {"employees":e([(1,10,40000),(2,10,60000),(3,10,60000),(4,10,80000)])},
        [(1,40000,0.25),(2,60000,0.75),(3,60000,0.75),(4,80000,1.0)])
    check_case("A055","all tied salaries yield cumulative fraction one",EMP,
        {"employees":e([(2,10,80),(1,10,80),(3,10,80)])},
        [(1,80,1.0),(2,80,1.0),(3,80,1.0)])
    check_case("A056","archived category revenue illustration",ITEMS,
        {"products":[(1,"Electronics"),(2,"Books")],
         "order_items":[(11,1,2,10),(12,2,1,15)]},
        [("Electronics",20,1),("Books",15,2)])
    check_case("A056","multi-product category, revenue peers, orphan item excluded",ITEMS,
        {"products":[(1,"A"),(2,"A"),(3,"B"),(4,"C")],
         "order_items":[(11,1,1,5),(12,2,1,5),(13,3,1,10),(14,99,1,500),
                        (15,4,1,2)]},
        [("A",10,1),("B",10,1),("C",2,3)])
    check_case("A057","archived three-month absolute changes",ORDERS,
        {"orders":[(1,1,"2026-01-10",100),(2,1,"2026-02-10",130),
                   (3,1,"2026-03-10",90)]},
        [("2026-01",100,None,None),("2026-02",130,100,30),
         ("2026-03",90,130,-40)])
    check_case("A057","missing February: lag is previous observed month, NOT calendar month",ORDERS,
        {"orders":[(1,1,"2026-01-10",100),(2,1,"2026-03-10",120)]},
        [("2026-01",100,None,None),("2026-03",120,100,20)])
    check_case("A058","archived zero denominator and growth percent",ORDERS,
        {"orders":[(1,1,"2026-01-10",0),(2,1,"2026-02-10",100),
                   (3,1,"2026-03-10",150)]},
        [("2026-01",0,None,None),("2026-02",100,0,None),
         ("2026-03",150,100,50.0)])
    check_case("A058","decline into zero, following zero previous and missing month",ORDERS,
        {"orders":[(1,1,"2025-12-10",100),(2,1,"2026-01-10",0),
                   (3,1,"2026-03-10",50)]},
        [("2025-12",100,None,None),("2026-01",0,100,-100.0),
         ("2026-03",50,0,None)])
    check_case("A059","archived per-customer consecutive days",ORDERS,
        {"orders":[(1,10,"2026-01-01",0),(2,10,"2026-01-04",0),
                   (3,10,"2026-01-10",0),(4,20,"2026-02-01",0)]},
        [(10,1,None),(10,2,3),(10,3,6),(20,4,None)])
    check_case("A059","same-date orders, deterministic order_id tie and partition",ORDERS,
        {"orders":[(2,10,"2026-01-03",0),(1,10,"2026-01-03",0),
                   (3,10,"2026-01-06",0),(4,20,"2026-01-04",0)]},
        [(10,1,None),(10,2,0),(10,3,3),(20,4,None)])
    check_case("A060","archived LEAD and placeholder illustration",ORDERS,
        {"orders":[(1,10,"2026-01-01",0),(2,10,"2026-01-04",0),
                   (3,20,"2026-02-01",0)]},
        [(10,1,"2026-01-04"),(10,2,"No later order"),
         (20,3,"No later order")])
    check_case("A060","same-day tie, partition; placeholder only at end",ORDERS,
        {"orders":[(2,10,"2026-01-01",0),(1,10,"2026-01-01",0),
                   (3,10,"2026-01-02",0),(4,20,"2026-01-01",0)]},
        [(10,1,"2026-01-01"),(10,2,"2026-01-02"),
         (10,3,"No later order"),(20,4,"No later order")])
    print("PARTIAL: 10 inspected, original Git blob SHA pinned; 20 bounded reviewer SQLite fixtures. No original MySQL key, PDF parity, independent learner answer or mastery verified.")

if __name__=="__main__":
    main()
