#!/usr/bin/env python3
"""PARTIAL A071-A080 source-pinned audit, reviewer-authored SQLite fixtures.

These are NOT provider-authenticated MySQL answers, official grades, archived
learner submissions, a native MySQL comparison, or evidence of learner mastery.
Original source archives are read only; all SQL below is explicitly auditor SQL.
"""
import hashlib
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/")
PINS = {
    "A071": ("9. Windowing Functions", "Every employee's salary as a share of their department's payroll.md", "7b0a26b7a6a6343fd45bac299c1094f377642c90", 14),
    "A072": ("9. Windowing Functions", "Median salary — MySQL has no MEDIAN function.md", "8c4a92cfaba2acb7e7235ba03c2fafdeb110c3bb", 14),
    "A073": ("9. Windowing Functions", "The top 20% of customers by spend.md", "f54d3676e0a921fa7a9caaf71bbd3fce461f7c62", 14),
    "A074": ("9. Windowing Functions", "Top 3 products by revenue inside each category.md", "100e4cfc4e2a90e3911f17ad25dede61ff30d1b4", 15),
    "A075": ("9. Windowing Functions", "The latest payment row for every order.md", "df907567f01bead61ff67afa5845aa5a7bf32dd5", 15),
    "A076": ("9. Windowing Functions", "Top 2 customers by spend in each city.md", "6b87c321406a65cdcdc346a81fe554877da20752", 15),
    "A077": ("9. Windowing Functions", "Each customer's second most recent order.md", "3851825388394342b08a04c3b8c7ce11fdd80c91", 15),
    "A078": ("6. SubQueries", "Top 3 salaries per department without any window function.md", "77c072224bf2f069b2468f2f299e7ca75f86f0d8", 15),
    "A079": ("9. Windowing Functions", "Most recent order per customer, returning the whole row, no CTE.md", "390c1f009ed8cc0c101a047f32e74946bdf6c644", 15),
    "A080": ("13. Gaps and Islands", "Find the missing order_id ranges in the sequence.md", "b3741537d5ed13dd50ba5df11023ed7db542a60e", 16),
}
SCHEMA = """
CREATE TABLE employees(emp_id INTEGER, dept_id INTEGER, salary REAL);
CREATE TABLE customers(cust_id INTEGER, city TEXT);
CREATE TABLE orders(order_id INTEGER, cust_id INTEGER, order_date TEXT, status TEXT, amount REAL);
CREATE TABLE products(product_id INTEGER, category TEXT);
CREATE TABLE order_items(item_id INTEGER, product_id INTEGER, qty REAL, unit_price REAL);
CREATE TABLE payments(payment_id INTEGER, order_id INTEGER, paid_at TEXT, amount REAL);
"""
SQL = {
"A071": """
WITH payroll AS (
 SELECT emp_id,dept_id,salary,
 SUM(salary) OVER (PARTITION BY dept_id) dept_payroll FROM employees)
SELECT emp_id,dept_id,salary,dept_payroll,
 ROUND(100.0*salary/NULLIF(dept_payroll,0),2)
FROM payroll ORDER BY emp_id
""",
"A072": """
WITH ranked AS (
 SELECT salary, ROW_NUMBER() OVER(ORDER BY salary) rn,
 COUNT(*) OVER() n FROM employees WHERE salary IS NOT NULL)
SELECT AVG(salary) FROM ranked
WHERE rn IN (CAST((n+1)/2 AS INTEGER),CAST((n+2)/2 AS INTEGER))
""",
"A073": """
WITH spend AS (
 SELECT cust_id,SUM(amount) total_spend FROM orders GROUP BY cust_id),
 ranked AS (
 SELECT cust_id,total_spend,
 ROW_NUMBER() OVER(ORDER BY total_spend DESC,cust_id) rn,
 COUNT(*) OVER() n FROM spend)
SELECT cust_id,total_spend FROM ranked
WHERE rn<=CAST((n+4)/5 AS INTEGER) ORDER BY total_spend DESC,cust_id
""",
"A074": """
WITH revenue AS (
 SELECT p.category,p.product_id,SUM(i.qty*i.unit_price) revenue
 FROM order_items i JOIN products p ON p.product_id=i.product_id
 GROUP BY p.category,p.product_id),
 ranked AS (
 SELECT category,product_id,revenue,
 ROW_NUMBER() OVER(PARTITION BY category ORDER BY revenue DESC,product_id) rn
 FROM revenue)
SELECT category,product_id,revenue FROM ranked
WHERE rn<=3 ORDER BY revenue DESC,category,product_id
""",
"A075": """
WITH ranked AS (
 SELECT payment_id,order_id,paid_at,amount,
 ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY paid_at DESC,payment_id DESC) rn
 FROM payments)
SELECT payment_id,order_id,paid_at,amount FROM ranked
WHERE rn=1 ORDER BY order_id
""",
"A076": """
WITH spend AS (
 SELECT c.city,c.cust_id,COALESCE(SUM(o.amount),0) total_spend
 FROM customers c LEFT JOIN orders o ON o.cust_id=c.cust_id
 GROUP BY c.city,c.cust_id),
 ranked AS (
 SELECT city,cust_id,total_spend,
 ROW_NUMBER() OVER(PARTITION BY city ORDER BY total_spend DESC,cust_id) rn
 FROM spend)
SELECT city,cust_id,total_spend FROM ranked
WHERE rn<=2 ORDER BY city,rn
""",
"A077": """
WITH ranked AS (
 SELECT order_id,cust_id,order_date,amount,
 ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY order_date DESC,order_id DESC) rn
 FROM orders)
SELECT cust_id,order_id,order_date,amount FROM ranked
WHERE rn=2 ORDER BY cust_id
""",
"A078": """
SELECT e.emp_id,e.dept_id,e.salary FROM employees e
WHERE e.salary IS NOT NULL AND (
 SELECT COUNT(DISTINCT h.salary) FROM employees h
 WHERE h.dept_id=e.dept_id AND h.salary>e.salary
)<3 ORDER BY e.dept_id,e.salary DESC,e.emp_id
""",
"A079": """
SELECT order_id,cust_id,order_date,status,amount FROM (
 SELECT o.*,ROW_NUMBER() OVER(
 PARTITION BY cust_id ORDER BY order_date DESC,order_id DESC) rn
 FROM orders o)
WHERE rn=1 ORDER BY cust_id
""",
"A080": """
WITH distinct_ids AS (
 SELECT DISTINCT order_id FROM orders WHERE order_id IS NOT NULL),
 with_prev AS (
 SELECT order_id,LAG(order_id) OVER(ORDER BY order_id) previous_id
 FROM distinct_ids)
SELECT previous_id+1 start_id,order_id-1 end_id FROM with_prev
WHERE order_id-previous_id>1 ORDER BY start_id
"""
}

def inspect():
    assert len(PINS)==len(SQL)==10
    for sid,(directory,filename,expected_sha,page) in PINS.items():
        path=BASE/directory/(sid+". "+filename)
        raw=path.read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        assert blob==expected_sha,(sid,"preserved blob changed",blob,expected_sha)
        text=raw.decode("utf-8")
        for marker in ("# Advanced Q"+sid[1:]+".",
                       "question "+str(int(sid[1:]))+", PDF p. "+str(page),
                       "seven-table example schema",
                       "### Sample input and expected output (illustrative)",
                       "The PDF does not provide separate sample input",
                       "NOT SOLVED YET",
                       "## My solution — SQLite\n\nPending.",
                       "## My solution — SQL Server\n\nPending.",
                       "## Official solution\n\nPending until"):
            assert marker in text,(sid,"missing source marker",marker)
        print("PASS",sid,"original Git blob, local illustration, unaltered Pending fields")

def check(sid,name,records,expected):
    with sqlite3.connect(":memory:") as db:
        db.executescript(SCHEMA)
        for table,values in records.items():
            if values:
                n=len(values[0])
                assert all(len(row)==n for row in values),(sid,table)
                db.executemany("INSERT INTO "+table+" VALUES ("+",".join("?"*n)+")",values)
        actual=db.execute(SQL[sid]).fetchall()
        assert actual==expected,(sid,name,actual,expected)
    print("PASS",sid,name,"(reviewer-only SQLite fixture; not official or learner SQL)")

def orders(rows):
    return {"orders":rows}

def main():
    inspect()
    check("A071","local salary-payroll illustration",{"employees":[(1,10,40),(2,10,60),(3,20,80)]},
          [(1,10,40,100,40.0),(2,10,60,100,60.0),(3,20,80,80,100.0)])
    check("A071","zero and NULL denominator policies",{"employees":[(1,10,0),(2,10,0),(3,20,None),(4,20,20)]},
          [(1,10,0,0,None),(2,10,0,0,None),(3,20,None,20,None),(4,20,20,20,100.0)])
    check("A072","local even-count median",{"employees":[(1,10,40),(2,10,60),(3,10,80),(4,10,100)]},[(70.0,)])
    check("A072","odd-count median ignoring NULL",{"employees":[(1,10,10),(2,10,None),(3,10,30),(4,10,50)]},[(30.0,)])
    check("A073","local top one of five",orders([(1,10,"",None,100),(2,20,"",None,80),(3,30,"",None,60),(4,40,"",None,40),(5,50,"",None,20)]),
          [(10,100)])
    check("A073","six customers ceil-to-two and tie breaker",orders([(1,1,"",None,100),(2,2,"",None,90),(3,3,"",None,90),(4,4,"",None,30),(5,5,"",None,20),(6,6,"",None,10)]),
          [(1,100),(2,90)])
    check("A074","local category top-three illustration",{
          "products":[(1,"Books"),(2,"Books"),(3,"Books"),(4,"Books"),(5,"Audio")],
          "order_items":[(11,1,1,40),(12,2,1,30),(13,3,1,20),(14,4,1,10),(15,5,1,5)]},
          [("Books",1,40),("Books",2,30),("Books",3,20),("Audio",5,5)])
    check("A074","revenue ties and unsold products excluded",{
          "products":[(1,"Books"),(2,"Books"),(3,"Books"),(4,"Books"),(5,"Audio"),(6,"Audio")],
          "order_items":[(1,1,1,10),(2,2,1,10),(3,3,1,5),(4,4,1,3),(5,5,1,7)]},
          [("Books",1,10),("Books",2,10),("Audio",5,7),("Books",3,5)])
    check("A075","local latest-payment illustration",{
          "payments":[(1,10,"2026-01-01 09:00",50),(2,10,"2026-01-02 09:00",50),(3,20,"2026-01-03 09:00",20)]},
          [(2,10,"2026-01-02 09:00",50),(3,20,"2026-01-03 09:00",20)])
    check("A075","timestamp tie resolved by ID and NULL earlier",{
          "payments":[(1,10,"2026-01-01",50),(2,10,"2026-01-01",60),(3,20,None,30),(4,20,"2026-01-01",40)]},
          [(2,10,"2026-01-01",60),(4,20,"2026-01-01",40)])
    check("A076","local top-two per city",{
          "customers":[(1,"Pune"),(2,"Pune"),(3,"Pune"),(4,"Delhi")],
          "orders":[(11,1,"",None,100),(12,2,"",None,80),(13,3,"",None,60),(14,4,"",None,40)]},
          [("Delhi",4,40),("Pune",1,100),("Pune",2,80)])
    check("A076","equal spend and customer with zero orders",{
          "customers":[(1,"Pune"),(2,"Pune"),(3,"Pune"),(4,"Mumbai")],
          "orders":[(11,1,"",None,100),(12,2,"",None,100),(13,3,"",None,40)]},
          [("Mumbai",4,0),("Pune",1,100),("Pune",2,100)])
    check("A077","local second-most-recent example",orders([
          (1,10,"2026-01-01",None,10),(2,10,"2026-01-05",None,20),
          (3,10,"2026-01-09",None,30),(4,20,"2026-02-01",None,40)]),
          [(10,2,"2026-01-05",20)])
    check("A077","same-day tie by ID and single-order exclusion",orders([
          (1,10,"2026-01-01",None,10),(2,10,"2026-01-01",None,20),
          (3,10,"2026-01-01",None,30),(4,20,"2026-02-01",None,40),
          (5,30,"2026-03-01",None,50),(6,30,"2026-03-02",None,60)]),
          [(10,2,"2026-01-01",20),(30,5,"2026-03-01",50)])
    check("A078","local top-three distinct salaries",{"employees":[
          (1,10,100),(2,10,90),(3,10,80),(4,10,70),(5,20,60)]},
          [(1,10,100),(2,10,90),(3,10,80),(5,20,60)])
    check("A078","three salary bands includes tied employees",{"employees":[
          (1,10,100),(2,10,100),(3,10,90),(4,10,80),(5,10,70),(6,20,50)]},
          [(1,10,100),(2,10,100),(3,10,90),(4,10,80),(6,20,50)])
    check("A079","local whole-row latest order without CTE",orders([
          (1,10,"2026-01-01","delivered",10),(2,10,"2026-01-03","delivered",20),
          (3,20,"2026-02-01","pending",30)]),
          [(2,10,"2026-01-03","delivered",20),(3,20,"2026-02-01","pending",30)])
    check("A079","timestamp tie by order ID and NULL sorting",orders([
          (1,10,"2026-01-03","delivered",10),(2,10,"2026-01-03","pending",20),
          (3,20,None,"pending",30),(4,20,"2026-01-01","refunded",40)]),
          [(2,10,"2026-01-03","pending",20),(4,20,"2026-01-01","refunded",40)])
    check("A080","local gaps between min and max only",orders([
          (1,1,None,None,None),(2,1,None,None,None),
          (5,1,None,None,None),(8,1,None,None,None)]),
          [(3,4),(6,7)])
    check("A080","duplicates do not create fake gaps; multiple intervals",orders([
          (1,1,None,None,None),(1,1,None,None,None),(4,1,None,None,None),
          (5,1,None,None,None),(9,1,None,None,None),(11,1,None,None,None)]),
          [(2,3),(6,8),(10,10)])
    print("PARTIAL: ten original statements SHA-pinned, twenty bounded reviewer-only fixture groups; "
          "native MySQL/PDF answers, learner solutions and full original datasets not verified.")

if __name__=="__main__":
    main()
