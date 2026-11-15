#!/usr/bin/env python3
"""Read-only source-pinned PNP A056-A060 reviewer cross-contract tests.

Every executable query and fixture here is auditor-authored SQLite, never
the source provider's MySQL 8 answer, historical learner work or grading.
"""
from contextlib import closing
from datetime import date
from itertools import product
from pathlib import Path
import hashlib
import sqlite3
import unittest

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/"
    "9. Windowing Functions"
)
PINS = {
    "A056": ("A056. Rank categories by revenue — a window on top of an aggregate.md",
             "fb9e57e02cd038ed2cd312ed64c2769f7e38fb3d", 11),
    "A057": ("A057. Month-over-month revenue change in absolute terms.md",
             "69fa22926de433ee2b8190d2e5d64bf8b10bde1c", 12),
    "A058": ("A058. Same thing as a growth percentage, safe against a zero denominator.md",
             "5a1aecd38b429843c4bad310e1c25e2809ac5e4d", 12),
    "A059": ("A059. Days between each customer's consecutive orders.md",
             "82bfe53ac71b6023478235d16b297e5d95d8f14c", 12),
    "A060": ("A060. Next order date per customer, with a placeholder when there isn't.md",
             "6237a4bfa32b819c41c85a6e07b5a7a302489ab4", 12),
}
CAT_SQL = """WITH category_revenue AS (
 SELECT p.category,SUM(oi.qty*oi.unit_price) AS revenue
 FROM order_items oi JOIN products p ON p.product_id=oi.product_id
 GROUP BY p.category)
SELECT category,revenue,RANK() OVER (ORDER BY revenue DESC) AS rev_rank
FROM category_revenue ORDER BY revenue DESC,category"""
MONTH_SQL = """WITH monthly AS (
 SELECT substr(order_date,1,7) AS month,SUM(amount) AS revenue
 FROM orders WHERE order_date IS NOT NULL GROUP BY substr(order_date,1,7)),
 lagged AS (
 SELECT month,revenue,LAG(revenue) OVER (ORDER BY month) AS prev
 FROM monthly)
SELECT month,revenue,prev,revenue-prev AS absolute_change,
 (revenue-prev)*100.0/NULLIF(prev,0) AS growth_pct
FROM lagged ORDER BY month"""
SEQUENCE_SQL = """WITH sequenced AS (
 SELECT cust_id,order_id,order_date,
  LAG(order_date) OVER (PARTITION BY cust_id ORDER BY order_date,order_id) AS prev_date,
  LEAD(order_date) OVER (PARTITION BY cust_id ORDER BY order_date,order_id) AS next_date,
  LEAD(order_id) OVER (PARTITION BY cust_id ORDER BY order_date,order_id) AS next_id
 FROM orders)
SELECT cust_id,order_id,order_date,prev_date,next_date,next_id,
 CASE WHEN prev_date IS NULL THEN NULL
      ELSE CAST(julianday(order_date)-julianday(prev_date) AS INTEGER) END AS days_since,
 COALESCE(next_date,'No later order') AS displayed_next_date
FROM sequenced ORDER BY cust_id,order_date,order_id"""

def categories(products, items):
    with closing(sqlite3.connect(":memory:")) as db:
        db.executescript("""CREATE TABLE products(product_id INTEGER,category TEXT);
        CREATE TABLE order_items(item_id INTEGER,product_id INTEGER,qty INTEGER,unit_price INTEGER);""")
        db.executemany("INSERT INTO products VALUES (?,?)",products)
        db.executemany("INSERT INTO order_items VALUES (?,?,?,?)",items)
        return db.execute(CAT_SQL).fetchall()

def monthly(orders):
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE orders(order_id INTEGER,cust_id INTEGER,order_date TEXT,amount INTEGER)")
        db.executemany("INSERT INTO orders VALUES (?,?,?,?)",orders)
        return db.execute(MONTH_SQL).fetchall()

def sequenced(orders):
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE orders(order_id INTEGER,cust_id INTEGER,order_date TEXT,amount INTEGER)")
        db.executemany("INSERT INTO orders VALUES (?,?,?,?)",orders)
        return db.execute(SEQUENCE_SQL).fetchall()

class PNPAdvancedRevenueLagLeadCrossContracts(unittest.TestCase):
    def test_01_immutable_five_original_blobs_and_pending_states(self):
        self.assertEqual(len(PINS),5)
        for qid,(filename,sha,page) in PINS.items():
            data=(BASE/filename).read_bytes()
            actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            self.assertEqual(actual,sha,qid)
            body=data.decode("utf-8")
            for marker in (
                "# Advanced Q"+qid[1:]+".",
                "question "+str(int(qid[1:]))+", PDF p. "+str(page),
                "### Sample input and expected output (illustrative)",
                "The PDF does not provide separate sample input",
                "NOT SOLVED YET",
                "## My solution — SQLite\n\nPending.",
                "## My solution — SQL Server\n\nPending.",
                "## Official solution\n\nPending until",
            ):
                self.assertIn(marker,body,qid)

    def test_02_A056_archived_illustrative_category_ranking(self):
        self.assertEqual(categories([(1,"Electronics"),(2,"Books")],
                                    [(11,1,2,10),(12,2,1,15)]),
                         [("Electronics",20,1),("Books",15,2)])

    def test_03_A056_orphan_no_sales_and_revenue_tie_policies(self):
        got=categories([(1,"A"),(2,"A"),(3,"B"),(4,"C"),(5,"Unused")],
                       [(11,1,1,5),(12,2,1,5),(13,3,1,10),
                        (14,4,1,2),(15,99,1,100000)])
        self.assertEqual(got,[("A",10,1),("B",10,1),("C",2,3)])
        self.assertNotIn("Unused",[r[0] for r in got])

    def test_04_A056_duplicate_product_key_can_inflate_joined_revenue(self):
        ordinary=categories([(1,"A")],[(1,1,1,9)])
        duplicated=categories([(1,"A"),(1,"A")],[(1,1,1,9)])
        self.assertEqual(ordinary,[("A",9,1)])
        self.assertEqual(duplicated,[("A",18,1)])

    def test_05_A056_independent_arithmetic_oracle_216_fixtures(self):
        count=0
        for quantities in product((-1,0,2),repeat=3):
            for prices in product((1,3),repeat=3):
                products=[(1,"A"),(2,"B"),(3,"C")]
                items=[(i+1,i+1,quantities[i],prices[i]) for i in range(3)]
                actual=categories(products,items)
                revenues={label: quantities[i]*prices[i]
                          for i,label in enumerate(("A","B","C"))}
                expected=sorted(
                    [(name,revenue,1+sum(other>revenue
                         for other in revenues.values()))
                     for name,revenue in revenues.items()],
                    key=lambda r:(-r[1],r[0]))
                self.assertEqual(actual,expected)
                count+=1
        self.assertEqual(count,216)

    def test_06_A056_money_decimal_and_refund_policy_not_authenticated(self):
        with closing(sqlite3.connect(":memory:")) as db:
            value=db.execute("SELECT 0.1 * 3").fetchone()[0]
        self.assertNotEqual(value,0.3)  # SQLite floating point; financial DECIMAL policy unspecified
        self.assertEqual(categories([(1,"Returns")],[(1,1,-1,10)]),
                         [("Returns",-10,1)])

    def test_07_A057_original_illustrative_month_absolute_change(self):
        rows=[(1,10,"2026-01-10",100),(2,10,"2026-02-10",130),
              (3,10,"2026-03-10",90)]
        self.assertEqual([r[:4] for r in monthly(rows)],
                         [("2026-01",100,None,None),("2026-02",130,100,30),
                          ("2026-03",90,130,-40)])

    def test_08_A058_original_illustrative_growth_zero_denominator(self):
        rows=[(1,10,"2026-01-10",0),(2,10,"2026-02-10",100),
              (3,10,"2026-03-10",150)]
        self.assertEqual(monthly(rows),
                         [("2026-01",0,None,None,None),
                          ("2026-02",100,0,100,None),
                          ("2026-03",150,100,50,50.0)])

    def test_09_A057_A058_gap_prev_observed_not_prior_calendar(self):
        rows=[(1,10,"2026-01-15",100),(2,10,"2026-03-15",120)]
        self.assertEqual(monthly(rows),
                         [("2026-01",100,None,None,None),
                          ("2026-03",120,100,20,20.0)])
        self.assertEqual(monthly([]),[])

    def test_10_A058_negative_or_zero_prior_and_null_month_inputs(self):
        rows=[(1,1,"2025-12-31",-100),(2,1,"2026-01-01",0),
              (3,1,"2026-02-01",50),(4,1,None,900)]
        self.assertEqual(monthly(rows),
                         [("2025-12",-100,None,None,None),
                          ("2026-01",0,-100,100,-100.0),
                          ("2026-02",50,0,50,None)])
        self.assertEqual(monthly([(1,1,"2026-02-01",None)]),
                         [("2026-02",None,None,None,None)])

    def test_11_A057_A058_independent_python_month_oracle_162_fixtures(self):
        cases=0
        for amounts in product((-100,0,100),repeat=4):
            for months in (("01","02","03","04"),("01","03","04","06")):
                rows=[(i+1,1,f"2026-{m}-15",amounts[i])
                      for i,m in enumerate(months)]
                actual=monthly(rows)
                for i,(month,revenue,prev,diff,pct) in enumerate(actual):
                    self.assertEqual((month,revenue),
                                     (f"2026-{months[i]}",amounts[i]))
                    previous=amounts[i-1] if i else None
                    self.assertEqual(prev,previous)
                    self.assertEqual(diff,amounts[i]-previous if i else None)
                    target=(amounts[i]-previous)*100/previous if i and previous else None
                    if target is None:
                        self.assertIsNone(pct)
                    else:
                        self.assertAlmostEqual(pct,target)
                cases+=1
        self.assertEqual(cases,162)

    def test_12_A057_status_policy_changes_monthly_revenue(self):
        with closing(sqlite3.connect(":memory:")) as db:
            db.execute("CREATE TABLE orders(order_date TEXT,amount INTEGER,status TEXT)")
            db.executemany("INSERT INTO orders VALUES (?,?,?)",
                           [("2026-01-01",100,"delivered"),
                            ("2026-01-02",999,"cancelled")])
            all_revenue=db.execute("SELECT SUM(amount) FROM orders").fetchone()[0]
            delivered=db.execute(
                "SELECT SUM(amount) FROM orders WHERE status='delivered'"
            ).fetchone()[0]
        self.assertEqual((all_revenue,delivered),(1099,100))

    def test_13_A059_archived_days_and_customer_partition(self):
        rows=[(1,10,"2026-01-01",0),(2,10,"2026-01-04",0),
              (3,10,"2026-01-10",0),(4,20,"2026-02-01",0)]
        self.assertEqual([(r[0],r[1],r[6]) for r in sequenced(rows)],
                         [(10,1,None),(10,2,3),(10,3,6),(20,4,None)])

    def test_14_A060_archived_next_order_date_and_placeholder(self):
        rows=[(1,10,"2026-01-01",0),(2,10,"2026-01-04",0),
              (3,20,"2026-02-01",0)]
        self.assertEqual([(r[0],r[1],r[7]) for r in sequenced(rows)],
                         [(10,1,"2026-01-04"),(10,2,"No later order"),
                          (20,3,"No later order")])

    def test_15_A059_leap_day_and_same_day_tie(self):
        rows=[(3,10,"2024-03-01",0),(2,10,"2024-02-28",0),
              (1,10,"2024-02-28",0)]
        self.assertEqual([(r[1],r[6]) for r in sequenced(rows)],
                         [(1,None),(2,0),(3,2)])

    def test_16_A059_null_date_predecessor_is_not_no_prior_row(self):
        rows=[(1,10,None,0),(2,10,"2026-01-01",0),
              (3,10,"2026-01-02",0)]
        self.assertEqual([(r[1],r[3],r[6]) for r in sequenced(rows)],
                         [(1,None,None),(2,None,None),(3,"2026-01-01",1)])

    def test_17_A060_null_next_date_collides_with_absent_next_row(self):
        rows=[(1,10,None,0),(2,10,None,0)]
        got=sequenced(rows)
        self.assertEqual([(r[1],r[5],r[7]) for r in got],
                         [(1,2,"No later order"),(2,None,"No later order")])
        # LEAD(order_id) distinguishes row presence; provider placeholder policy unknown.

    def test_18_A059_A060_independent_temporal_python_oracle_216_fixtures(self):
        dates=("2026-01-01","2026-01-03","2026-01-06")
        count=0
        for choices in product(tuple(product((10,20),dates)),repeat=3):
            rows=[(i+1,choices[i][0],choices[i][1],0) for i in range(3)]
            actual=sequenced(rows)
            expected=[]
            for customer in (10,20):
                selected=sorted([r for r in rows if r[1]==customer],
                                key=lambda r:(r[2],r[0]))
                for i,row in enumerate(selected):
                    prev=selected[i-1][2] if i else None
                    nxt=selected[i+1][2] if i+1<len(selected) else None
                    next_id=selected[i+1][0] if i+1<len(selected) else None
                    days=(date.fromisoformat(row[2])-date.fromisoformat(prev)).days if prev else None
                    expected.append((customer,row[0],row[2],prev,nxt,next_id,
                                     days,nxt if nxt else "No later order"))
            self.assertEqual(actual,expected)
            count+=1
        self.assertEqual(count,216)

if __name__=="__main__":
    unittest.main(verbosity=2)
