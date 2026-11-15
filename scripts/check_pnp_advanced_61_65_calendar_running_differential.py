#!/usr/bin/env python3
"""Immutable-source-pinned, reviewer-authored A061-A065 SQLite contracts.

Original archived sample outputs are replayed; all other queries and test
fixtures here are independent synthetic reviewer work, not official MySQL
answers, original provider grading, or historical learner submissions.
"""
from contextlib import closing
from datetime import date, timedelta
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
    "A061": ("A061. Customers whose most recent order was smaller than the one before.md",
             "6f3f440cd2152e07b509fbf1492921d375829acc", 12),
    "A062": ("A062. Compare every month against the same month last year.md",
             "c74e070703fb111ec138c4b89426ed9a0c43f45e", 12),
    "A063": ("A063. Running total of revenue by date.md",
             "f1b80eb27b6079414263f1497d9041a340ee6bd7", 13),
    "A064": ("A064. Running total of spend per customer, oldest order first.md",
             "18cb163bef2ba0e0ebc699aeeb3d54cfbe68a0d1", 13),
    "A065": ("A065. Seven-day moving average of daily revenue, calendar-correct.md",
             "3ed636792e25455903a75daf3fa31e4d58a16fb9", 13),
}
LATEST = """WITH r AS (
 SELECT cust_id,order_id,order_date,amount,
        LAG(amount) OVER (PARTITION BY cust_id
                           ORDER BY order_date,order_id) AS prior,
        ROW_NUMBER() OVER (PARTITION BY cust_id
                           ORDER BY order_date DESC,order_id DESC) AS recency
 FROM orders)
SELECT cust_id,order_id,amount,prior FROM r
WHERE recency=1 AND amount<prior ORDER BY cust_id"""
YOY = """WITH monthly AS (
 SELECT substr(order_date,1,7) AS month,SUM(amount) AS revenue
 FROM orders WHERE order_date IS NOT NULL GROUP BY substr(order_date,1,7))
SELECT m.month,m.revenue,y.revenue,m.revenue-y.revenue
FROM monthly m LEFT JOIN monthly y
 ON y.month=printf('%04d-%02d',CAST(substr(m.month,1,4) AS INTEGER)-1,
                   CAST(substr(m.month,6,2) AS INTEGER))
ORDER BY m.month"""
DAY = """WITH daily AS (
 SELECT order_date,SUM(amount) AS revenue
 FROM orders WHERE order_date IS NOT NULL GROUP BY order_date)
SELECT order_date,revenue,
 SUM(revenue) OVER (ORDER BY order_date
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
FROM daily ORDER BY order_date"""
CUSTOMER = """SELECT cust_id,order_id,amount,
 SUM(amount) OVER (PARTITION BY cust_id ORDER BY order_date,order_id
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
FROM orders ORDER BY cust_id,order_date,order_id"""
MOVING = """WITH RECURSIVE calendar(day) AS (
 SELECT MIN(order_date) FROM orders WHERE order_date IS NOT NULL
 UNION ALL SELECT date(day,'+1 day') FROM calendar
 WHERE day<(SELECT MAX(order_date) FROM orders WHERE order_date IS NOT NULL)),
daily AS (SELECT order_date,SUM(amount) AS revenue
          FROM orders WHERE order_date IS NOT NULL GROUP BY order_date),
filled AS (SELECT c.day,COALESCE(d.revenue,0) AS revenue
           FROM calendar c LEFT JOIN daily d ON d.order_date=c.day),
rolled AS (
 SELECT day, SUM(revenue) OVER (
   ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS total,
 COUNT(*) OVER (
   ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS days
 FROM filled)
SELECT day,total,total/7.0 FROM rolled WHERE days=7 ORDER BY day"""

def run(rows, query):
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("""CREATE TABLE orders
            (order_id INTEGER,cust_id INTEGER,order_date TEXT,amount INTEGER,status TEXT)""")
        db.executemany("INSERT INTO orders VALUES(?,?,?,?,?)",
                       [(*r,"delivered") if len(r)==4 else r for r in rows])
        return db.execute(query).fetchall()

class Advanced61To65CalendarCrossContracts(unittest.TestCase):
    def test_01_five_immutable_originals_and_pending_state(self):
        self.assertEqual(len(PINS),5)
        for qid,(name,sha,page) in PINS.items():
            data=(BASE/name).read_bytes()
            blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            self.assertEqual(blob,sha,qid)
            text=data.decode("utf-8")
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
                self.assertIn(marker,text,qid)

    def test_02_A061_original_illustrative_latest_decrease(self):
        rows=[(1,10,"2026-01-01",100),(2,10,"2026-01-03",80),
              (3,20,"2026-01-01",50),(4,20,"2026-01-03",70)]
        self.assertEqual(run(rows,LATEST),[(10,2,80,100)])

    def test_03_A061_singletons_latest_ties_and_no_decrease(self):
        rows=[(1,10,"2026-01-01",10),(2,10,"2026-01-02",20),
              (3,10,"2026-01-02",19),(4,20,"2026-01-01",7),
              (5,30,"2026-01-01",11),(6,30,"2026-01-02",11)]
        self.assertEqual(run(rows,LATEST),[(10,3,19,20)])

    def test_04_A061_null_amount_and_cancelled_policy_is_not_supplier_answer(self):
        rows=[(1,10,"2026-01-01",100,"delivered"),
              (2,10,"2026-01-02",20,"cancelled"),
              (3,20,"2026-01-01",40,"delivered"),
              (4,20,"2026-01-02",None,"delivered")]
        self.assertEqual(run(rows,LATEST),[(10,2,20,100)])
        self.assertEqual(run(rows,"SELECT COUNT(*) FROM orders WHERE status='delivered'"),[(3,)])

    def test_05_A061_independent_python_latest_oracle_125_fixtures(self):
        count=0
        for amounts in product((0,1,2,3,4),repeat=3):
            rows=[(i+1,10,f"2026-01-0{i+1}",amounts[i]) for i in range(3)]
            expected=[(10,3,amounts[2],amounts[1])] if amounts[2]<amounts[1] else []
            self.assertEqual(run(rows,LATEST),expected)
            count+=1
        self.assertEqual(count,125)

    def test_06_A062_original_illustrative_same_month_last_year(self):
        rows=[(1,10,"2025-01-10",100),(2,10,"2026-01-10",150)]
        self.assertEqual(run(rows,YOY),
                         [("2025-01",100,None,None),("2026-01",150,100,50)])

    def test_07_A062_missing_previous_year_vs_previous_observation(self):
        rows=[(1,1,"2024-01-01",3),(2,1,"2025-02-01",10),
              (3,1,"2026-01-01",30)]
        self.assertEqual(run(rows,YOY),
                         [("2024-01",3,None,None),
                          ("2025-02",10,None,None),
                          ("2026-01",30,None,None)])

    def test_08_A062_multiyear_same_month_not_12_sparse_rows(self):
        rows=[(1,1,"2024-01-15",4),(2,1,"2025-01-15",5),
              (3,1,"2025-12-15",8),(4,1,"2026-01-15",6)]
        self.assertEqual(run(rows,YOY),
                         [("2024-01",4,None,None),
                          ("2025-01",5,4,1),
                          ("2025-12",8,None,None),
                          ("2026-01",6,5,1)])
        self.assertEqual(run([],YOY),[])

    def test_09_A062_independent_python_yearly_oracle_81_fixtures(self):
        months=("2025-01","2025-02","2026-01","2026-02")
        for amounts in product((-1,0,2),repeat=4):
            rows=[(i+1,1,m+"-15",amounts[i]) for i,m in enumerate(months)]
            actual=run(rows,YOY)
            mapping=dict(zip(months,amounts))
            want=[(m,v,mapping.get(f"{int(m[:4])-1:04d}-{m[5:]}"),
                   v-mapping[f"{int(m[:4])-1:04d}-{m[5:]}"]
                   if f"{int(m[:4])-1:04d}-{m[5:]}" in mapping else None)
                  for m,v in zip(months,amounts)]
            self.assertEqual(actual,want)

    def test_10_A063_original_illustrative_daily_running_total(self):
        rows=[(1,1,"2026-01-01",10),(2,1,"2026-01-01",20),
              (3,1,"2026-01-02",5)]
        self.assertEqual(run(rows,DAY),
                         [("2026-01-01",30,30),("2026-01-02",5,35)])

    def test_11_A063_negative_null_and_sparse_daily_aggregation(self):
        rows=[(1,1,"2026-01-01",50),(2,1,"2026-01-01",None),
              (3,1,"2026-01-04",-10),(4,1,None,999),
              (5,1,"2026-01-05",0)]
        self.assertEqual(run(rows,DAY),
                         [("2026-01-01",50,50),
                          ("2026-01-04",-10,40),
                          ("2026-01-05",0,40)])

    def test_12_A064_original_illustrative_customer_running_total(self):
        rows=[(1,10,"2026-01-01",10),(2,10,"2026-01-03",20),
              (3,20,"2026-01-02",5)]
        self.assertEqual(run(rows,CUSTOMER),
                         [(10,1,10,10),(10,2,20,30),(20,3,5,5)])

    def test_13_A064_duplicate_day_tiebreaker_and_independent_partitions(self):
        rows=[(3,10,"2026-01-03",4),(2,10,"2026-01-01",20),
              (1,10,"2026-01-01",5),(4,20,"2026-01-01",9)]
        self.assertEqual(run(rows,CUSTOMER),
                         [(10,1,5,5),(10,2,20,25),(10,3,4,29),(20,4,9,9)])

    def test_14_A064_sql_null_running_sum_and_order_status_policy(self):
        rows=[(1,10,"2026-01-01",None),(2,10,"2026-01-02",6),
              (3,10,"2026-01-03",-2)]
        self.assertEqual(run(rows,CUSTOMER),
                         [(10,1,None,None),(10,2,6,6),(10,3,-2,4)])

    def test_15_A065_original_seven_calendar_days_not_three_order_days(self):
        rows=[(1,1,"2026-01-01",10),(2,1,"2026-01-03",20),
              (3,1,"2026-01-07",40)]
        self.assertEqual(run(rows,MOVING),[("2026-01-07",70,10.0)])

    def test_16_A065_six_day_partial_excluded_then_rolls_and_leap_year(self):
        rows=[(1,1,"2024-02-26",14),(2,1,"2024-02-29",21),
              (3,1,"2024-03-03",7),(4,1,"2024-03-04",8)]
        self.assertEqual(run(rows,MOVING),
                         [("2024-03-03",42,6.0),("2024-03-04",36,36/7.0)])
        self.assertEqual(run([(1,1,"2026-01-01",1),
                              (2,1,"2026-01-06",2)],MOVING),[])
        self.assertEqual(run([],MOVING),[])

    def test_17_A065_independent_python_calendar_oracle_81_fixtures(self):
        start=date(2026,1,1)
        order_days=(0,2,6,7)
        for amounts in product((-1,0,3),repeat=4):
            rows=[(i+1,1,(start+timedelta(days=d)).isoformat(),v)
                  for i,(d,v) in enumerate(zip(order_days,amounts))]
            got=run(rows,MOVING)
            daily=dict(zip(order_days,amounts))
            expected=[]
            for end in (6,7):
                total=sum(daily.get(d,0) for d in range(end-6,end+1))
                expected.append(((start+timedelta(days=end)).isoformat(),
                                 total,total/7.0))
            self.assertEqual(got,expected)

    def test_18_A065_missing_days_change_denominator_and_report_horizon(self):
        rows=[(1,1,"2026-01-01",7),(2,1,"2026-01-03",14),
              (3,1,"2026-01-07",28)]
        self.assertEqual(run(rows,MOVING),[("2026-01-07",49,7.0)])
        self.assertNotEqual(49/3,49/7)
        # Reviewer horizon stops at latest observed date; original prompt has no
        # authoritative reporting end beyond its sample's January 7 boundary.

if __name__=="__main__":
    unittest.main(verbosity=2)
