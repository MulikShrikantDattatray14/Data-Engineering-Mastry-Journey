#!/usr/bin/env python3
"""PARTIAL independent reviewer for preserved PNP Advanced A071-A075.

Only immutable archived Markdown illustrations and auditor-authored SQLite fixtures
are exercised. NOT native source MySQL8, authenticated official solutions, original
PDF page-render parity, supplied production data, learner submissions, or mastery.
"""
import hashlib
import itertools
import sqlite3
from contextlib import closing
import statistics
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/"
               "9. Windowing Functions")
SOURCES = {
    "A071": ("Every employee's salary as a share of their department's payroll.md",
             "7b0a26b7a6a6343fd45bac299c1094f377642c90", 14),
    "A072": ("Median salary — MySQL has no MEDIAN function.md",
             "8c4a92cfaba2acb7e7235ba03c2fafdeb110c3bb", 14),
    "A073": ("The top 20% of customers by spend.md",
             "f54d3676e0a921fa7a9caaf71bbd3fce461f7c62", 14),
    "A074": ("Top 3 products by revenue inside each category.md",
             "100e4cfc4e2a90e3911f17ad25dede61ff30d1b4", 15),
    "A075": ("The latest payment row for every order.md",
             "df907567f01bead61ff67afa5845aa5a7bf32dd5", 15),
}
SCHEMA = """
CREATE TABLE employees(emp_id INTEGER,dept_id INTEGER,salary REAL);
CREATE TABLE orders(order_id INTEGER,cust_id INTEGER,status TEXT,amount REAL);
CREATE TABLE products(product_id INTEGER,category TEXT);
CREATE TABLE order_items(item_id INTEGER,product_id INTEGER,qty REAL,unit_price REAL);
CREATE TABLE payments(payment_id INTEGER,order_id INTEGER,paid_at TEXT,amount REAL);
"""
QUERIES = {
 "A071": """
 WITH e AS (
 SELECT emp_id,dept_id,salary,
 SUM(salary) OVER(PARTITION BY dept_id) payroll FROM employees)
 SELECT emp_id,dept_id,salary,payroll,
 ROUND(100.0*salary/NULLIF(payroll,0),2) AS pct
 FROM e ORDER BY emp_id
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
 SELECT cust_id,SUM(amount) total FROM orders GROUP BY cust_id),
 ranked AS (
 SELECT cust_id,total,ROW_NUMBER() OVER(ORDER BY total DESC,cust_id) rn,
 COUNT(*) OVER() n FROM spend)
 SELECT cust_id,total FROM ranked
 WHERE rn<=CAST((n+4)/5 AS INTEGER) ORDER BY total DESC,cust_id
 """,
 "A074": """
 WITH rev AS (
 SELECT p.category,p.product_id,SUM(i.qty*i.unit_price) revenue
 FROM order_items i JOIN products p ON p.product_id=i.product_id
 GROUP BY p.category,p.product_id),
 ranked AS (
 SELECT category,product_id,revenue,
 ROW_NUMBER() OVER(PARTITION BY category ORDER BY revenue DESC,product_id) rn
 FROM rev)
 SELECT category,product_id,revenue FROM ranked WHERE rn<=3
 ORDER BY revenue DESC,category,product_id
 """,
 "A075": """
 WITH ranked AS (
 SELECT payment_id,order_id,paid_at,amount,
 ROW_NUMBER() OVER(PARTITION BY order_id
 ORDER BY paid_at DESC,payment_id DESC) rn FROM payments)
 SELECT payment_id,order_id,paid_at,amount FROM ranked
 WHERE rn=1 ORDER BY order_id
 """
}
def run(which, records):
    with closing(sqlite3.connect(":memory:")) as c:
        c.executescript(SCHEMA)
        for table, vals in records.items():
            if not vals:
                continue
            n = len(vals[0])
            c.executemany("INSERT INTO "+table+" VALUES ("+",".join("?"*n)+")", vals)
        return c.execute(QUERIES[which]).fetchall()

class SourcePinnedPolicyChecks(unittest.TestCase):
    def test_01_all_original_sha_and_pending_fields(self):
        self.assertEqual(len(SOURCES),5)
        for k,(name,expected,page) in SOURCES.items():
            data=(BASE/(k+". "+name)).read_bytes()
            real=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            self.assertEqual(real,expected,k)
            body=data.decode("utf-8")
            for marker in ("# Advanced Q"+k[1:]+".",
                           "question "+str(int(k[1:]))+", PDF p. "+str(page),
                           "seven-table example schema",
                           "### Sample input and expected output (illustrative)",
                           "The PDF does not provide separate sample input",
                           "NOT SOLVED YET",
                           "## My solution — SQLite\n\nPending.",
                           "## My solution — SQL Server\n\nPending.",
                           "## Official solution\n\nPending until"):
                self.assertIn(marker,body,(k,marker))

    # Five LOCAL archive-authored illustrations, not supplier-certified output.
    def test_02_a071_local_illustration(self):
        self.assertEqual(run("A071",{"employees":[(1,10,40),(2,10,60),(3,20,80)]}),
                         [(1,10,40,100,40),(2,10,60,100,60),(3,20,80,80,100)])
    def test_03_a072_local_illustration(self):
        self.assertEqual(run("A072",{"employees":[(1,1,40),(2,1,60),(3,1,80),(4,1,100)]}),
                         [(70.0,)])
    def test_04_a073_local_illustration(self):
        self.assertEqual(run("A073",{"orders":[(i,i*10,"ok",v) for i,v in
                           enumerate((100,80,60,40,20),1)]}),[(10,100)])
    def test_05_a074_local_illustration(self):
        products=[(1,"Books"),(2,"Books"),(3,"Books"),(4,"Books"),(5,"Audio")]
        lines=[(i+10,i,1,5 if i==5 else 50-10*i) for i in range(1,6)]
        self.assertEqual(run("A074",{"products":products,"order_items":lines}),
                         [("Books",1,40),("Books",2,30),
                          ("Books",3,20),("Audio",5,5)])
    def test_06_a075_local_illustration(self):
        rows=[(1,10,"2026-01-01 09:00",50),
              (2,10,"2026-01-02 09:00",50),
              (3,20,"2026-01-03 09:00",20)]
        self.assertEqual(run("A075",{"payments":rows}),[rows[1],rows[2]])

    # Explicitly model reviewer policy; vendor rules remain unauthenticated.
    def test_07_a071_zero_payroll_and_null_salary(self):
        r=run("A071",{"employees":[(1,1,0),(2,1,0),(3,2,None),(4,2,20)]})
        self.assertEqual([x[-1] for x in r],[None,None,None,100])
    def test_08_a072_odd_empty_and_null(self):
        self.assertEqual(run("A072",{"employees":[(1,1,None),(2,1,-5),(3,1,7),(4,1,9)]}),[(7.0,)])
        self.assertEqual(run("A072",{}),[(None,)])
    def test_09_a073_ceil_and_tie_policy(self):
        rs=[(i,i,"complete",100 if i<=3 else 0) for i in range(1,7)]
        self.assertEqual(run("A073",{"orders":rs}),[(1,100),(2,100)])
        self.assertEqual(run("A073",{}),[])
    def test_10_a074_tied_category_and_refund_policy(self):
        p=[(1,"B"),(2,"B"),(3,"B"),(4,"B")]
        rows=[(i,i,1,10) for i in range(1,5)]
        self.assertEqual([r[1] for r in run("A074",{"products":p,"order_items":rows})],[1,2,3])
        rows.append((5,4,-2,10))
        self.assertEqual([r[1] for r in run("A074",{"products":p,"order_items":rows})],[1,2,3])
    def test_11_a075_timestamp_ties_and_null(self):
        rs=[(1,5,None,0),(2,5,"2026-01-01",1),(3,5,"2026-01-01",2),
            (4,6,None,4),(5,6,None,5)]
        self.assertEqual(run("A075",{"payments":rs}),[rs[2],rs[4]])

    # Deterministic Python reference contracts: no official-key claim.
    def test_12_a071_64_independent_salary_combinations(self):
        for values in itertools.product((None,-5,0,10),repeat=3):
            rs=[(1,10,values[0]),(2,10,values[1]),(3,20,values[2])]
            actual=run("A071",{"employees":rs})
            for emp,dept,salary,payroll,pct in actual:
                total=sum(v for _,d,v in rs if d==dept and v is not None)
                expected=None if salary is None or total==0 else round(100*salary/total,2)
                self.assertEqual(pct,expected,(values,emp))
    def test_13_a072_341_independent_median_combinations(self):
        options=(-3,0,4,None)
        for n in range(5):
            for vals in itertools.product(options,repeat=n):
                rs=[(i,1,v) for i,v in enumerate(vals)]
                eligible=[v for v in vals if v is not None]
                expected=float(statistics.median(eligible)) if eligible else None
                self.assertEqual(run("A072",{"employees":rs})[0][0],expected,vals)
    def test_14_a073_81_independent_customer_spend_combinations(self):
        for vals in itertools.product((-3,0,3),repeat=4):
            rs=[(i,i,"complete",v) for i,v in enumerate(vals,1)]
            expected=sorted([(i,float(v)) for i,v in enumerate(vals,1)],
                            key=lambda p:(-p[1],p[0]))[:1]
            self.assertEqual(run("A073",{"orders":rs}),expected,vals)
    def test_15_a074_81_independent_category_rank_combinations(self):
        p=[(1,"B"),(2,"B"),(3,"B"),(4,"B"),(5,"A")]
        for vals in itertools.product((-1,0,2),repeat=4):
            lines=[(i,i,1,v) for i,v in enumerate(vals,1)]
            lines.append((5,5,1,3))
            actual=run("A074",{"products":p,"order_items":lines})
            best=sorted([(v,i) for i,v in enumerate(vals,1)],key=lambda x:(-x[0],x[1]))[:3]
            expected=sorted([("B",i,float(v)) for v,i in best]+[("A",5,3.0)],
                            key=lambda x:(-x[2],x[0],x[1]))
            self.assertEqual(actual,expected,vals)
    def test_16_a075_256_independent_latest_payment_combinations(self):
        for states in itertools.product((None,"2026-01-01","2026-01-02","2026-01-03"),repeat=4):
            rs=[(1,10,states[0],1),(2,10,states[1],2),
                (3,20,states[2],3),(4,20,states[3],4)]
            expected=[]
            for order in (10,20):
                group=[r for r in rs if r[1]==order]
                expected.append(max(group,key=lambda r:(r[2] is not None,r[2] or "",r[0])))
            self.assertEqual(run("A075",{"payments":rs}),expected,states)

    # Concrete reviewer counterexamples, not inferred supplier defects.
    def test_17_a074_duplicate_product_id_fanout(self):
        rec={"products":[(1,"B"),(1,"B")],"order_items":[(1,1,1,10)]}
        self.assertEqual(run("A074",rec),[("B",1,20.0)])
        self.assertNotEqual(run("A074",rec)[0][-1],10.0)
    def test_18_a075_iso_offset_text_order_is_not_instant_order(self):
        from datetime import datetime
        rs=[(1,10,"2026-01-01T02:00:00+02:00",1),
            (2,10,"2026-01-01T01:30:00+00:00",2)]
        self.assertEqual(run("A075",{"payments":rs})[0][0],1)
        self.assertGreater(datetime.fromisoformat(rs[1][2]),
                           datetime.fromisoformat(rs[0][2]))

if __name__=="__main__":
    unittest.main(verbosity=2)
