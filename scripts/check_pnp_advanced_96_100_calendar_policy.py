#!/usr/bin/env python3
"""Reviewer-only source-pinned A096-A100 cross-policy tests; not provider or learner answers."""
import calendar
from collections import Counter, defaultdict
from datetime import date, timedelta
import hashlib
import sqlite3
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/2.PNP- foundations and practice/12. Dates and Time")
PINS = {
    "A096": "403c5e129970268f24a925e8527d55d833b7a3f6",
    "A097": "5fd46f87854e52c3ba4c22fd56e635774c04edd6",
    "A098": "89555669d558721ab2f949a612d377c0095680e0",
    "A099": "ac542b2b0366010d6888354e8a8b047475349bb5",
    "A100": "277fafe7f196cdcb7b2eaef65602ef39c2455dc5",
}

def source(sid):
    matches = list(BASE.glob(sid + ". *.md"))
    if len(matches) != 1:
        raise AssertionError((sid, matches))
    raw = matches[0].read_bytes()
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if digest != PINS[sid]:
        raise AssertionError((sid, "Git blob mismatch", digest))
    return raw.decode("utf-8")

def day(s):
    return date.fromisoformat(s[:10]) if s is not None else None

def db_for(ddl, inserts):
    db = sqlite3.connect(":memory:")
    db.executescript(ddl)
    for sql, rows in inserts:
        db.executemany(sql, rows)
    return db

class AdvancedCalendarPolicyReviewer(unittest.TestCase):
    def test_01_original_archive_sources_and_pending_fields(self):
        for sid in PINS:
            with self.subTest(sid=sid):
                body = source(sid)
                self.assertIn("NOT SOLVED YET", body)
                self.assertIn("PDF p. 19", body)
                self.assertIn("illustrative", body)
                self.assertIn("## My solution — SQLite\n\nPending.", body)
                self.assertIn("## My solution — SQL Server\n\nPending.", body)
                self.assertIn("## Official solution\n\nPending", body)
        self.assertIn("DATEDIFF(CURDATE(), order_date) <= 30", source("A096"))

    def test_02_a096_lower_bound_future_rows_and_index_probe(self):
        today = date(2026, 2, 1)
        rows = [(1,"2026-01-01"),(2,"2026-01-02"),(3,"2026-02-01 23:59:00"),
                (4,"2026-02-02"),(5,"2027-02-01"),(6,None),
                (7,"2026-01-02 00:00:00")]
        db = db_for("CREATE TABLE orders(id INT,order_date TEXT);"
                    "CREATE INDEX ix_a096 ON orders(order_date);",
                    [("INSERT INTO orders VALUES (?,?)",rows)])
        try:
            start = (today - timedelta(days=30)).isoformat()
            got = [r[0] for r in db.execute(
                "SELECT id FROM orders WHERE order_date >= ? ORDER BY id",(start,))]
            python_oracle = [i for i, d in rows if day(d) is not None
                             and (today-day(d)).days <= 30]
            self.assertEqual(got, python_oracle)
            self.assertEqual(got, [2,3,4,5,7])
            plan = db.execute(
                "EXPLAIN QUERY PLAN SELECT id FROM orders WHERE order_date >= ?",
                (start,)).fetchall()
            self.assertTrue(any("SEARCH" in r[-1] and "ix_a096" in r[-1]
                                for r in plan),plan)
            true_past_only = [i for i,d in rows if day(d) is not None
                              and 0 <= (today-day(d)).days <= 30]
            self.assertEqual(true_past_only,[2,3,7])
        finally:
            db.close()

    def test_03_a097_month_end_leap_year_timestamp_and_null(self):
        rows = [(1,"2024-02-29"),(2,"2025-02-17 11:00:00"),
                (3,"2026-12-31"),(4,"2027-01-01"),(5,None)]
        db = db_for("CREATE TABLE orders(id INT,order_date TEXT);",
                    [("INSERT INTO orders VALUES (?,?)",rows)])
        try:
            got = db.execute(
                "SELECT id,date(order_date,'start of month'),"
                "date(order_date,'start of month','+1 month','-1 day') "
                "FROM orders ORDER BY id").fetchall()
            oracle = [(i, date(d.year,d.month,1).isoformat(),
                       date(d.year,d.month,calendar.monthrange(d.year,d.month)[1]).isoformat())
                      if (d:=day(s)) is not None else (i,None,None)
                      for i,s in rows]
            self.assertEqual(got,oracle)
            self.assertEqual((got[0][2],got[1][2]),("2024-02-29","2025-02-28"))
        finally:
            db.close()

    def test_04_a098_monday_week_cross_year_and_duplicate_rows(self):
        rows = [(1,"2025-12-28"),(2,"2025-12-29"),(3,"2026-01-04"),
                (4,"2026-01-05"),(5,"2026-01-05 17:00:00"),(6,None),
                (7,"2027-01-03"),(8,"2027-01-04")]
        db = db_for("CREATE TABLE orders(id INT,order_date TEXT);",
                    [("INSERT INTO orders VALUES (?,?)",rows)])
        try:
            got = db.execute(
                "SELECT date(order_date,'-'||"
                "((CAST(strftime('%w',order_date) AS INTEGER)+6)%7)||' days') AS monday,"
                "COUNT(*) FROM orders WHERE order_date IS NOT NULL "
                "GROUP BY monday ORDER BY monday").fetchall()
            oracle = Counter((day(d)-timedelta(days=day(d).weekday())).isoformat()
                             for _,d in rows if d is not None)
            self.assertEqual(got,sorted(oracle.items()))
            self.assertEqual(oracle["2025-12-29"],2)
            self.assertEqual(oracle["2026-01-05"],2)
        finally:
            db.close()

    def test_05_a099_first_order_not_later_eligible_order(self):
        customers = [(1,"2026-01-01"),(2,"2026-01-01"),(3,"2026-01-01"),
                     (4,"2026-01-01"),(5,"2026-01-01"),(6,None)]
        orders = [(11,1,"2026-01-08"),(12,2,"2026-01-09"),
                  (13,3,"2025-12-31"),(14,3,"2026-01-02"),
                  (15,4,"2026-01-01"),(16,4,"2026-01-03"),
                  (17,5,None),(18,6,"2026-01-02")]
        db = db_for("CREATE TABLE customers(cust_id INT,signup_date TEXT);"
                    "CREATE TABLE orders(id INT,cust_id INT,order_date TEXT);",
                    [("INSERT INTO customers VALUES (?,?)",customers),
                     ("INSERT INTO orders VALUES (?,?,?)",orders)])
        try:
            got = db.execute(
                "WITH firsts AS (SELECT cust_id,MIN(date(order_date)) AS first_d "
                "FROM orders GROUP BY cust_id) "
                "SELECT c.cust_id,f.first_d FROM customers c JOIN firsts f USING(cust_id)"
                " WHERE f.first_d >= c.signup_date "
                "AND f.first_d <= date(c.signup_date,'+7 days') "
                "ORDER BY c.cust_id").fetchall()
            first = {}
            for _,cid,stamp in orders:
                d = day(stamp)
                if d is not None:
                    first[cid] = min(first.get(cid,d),d)
            oracle = [(cid,first[cid].isoformat()) for cid,signup in customers
                      if signup is not None and cid in first and
                      0 <= (first[cid]-day(signup)).days <= 7]
            self.assertEqual(got,oracle)
            self.assertEqual(got,[(1,"2026-01-08"),(4,"2026-01-01")])
            self.assertEqual(first[3],date(2025,12,31))
        finally:
            db.close()

    def test_06_a100_zero_cohorts_year_rollover_and_duplicate_orders(self):
        rows = [(1,10,"2026-01-10"),(2,10,"2026-02-05"),(3,10,"2026-02-06"),
                (4,20,"2026-01-20"),(5,20,"2026-03-01"),
                (6,30,"2026-02-01"),(7,30,"2026-03-10"),
                (8,40,"2025-12-31"),(9,40,"2026-01-31"),
                (10,50,"2026-03-01"),(11,60,None)]
        db = db_for("CREATE TABLE orders(id INT,cust_id INT,order_date TEXT);",
                    [("INSERT INTO orders VALUES (?,?,?)",rows)])
        try:
            got = db.execute(
                "WITH firsts AS (SELECT cust_id,date(MIN(order_date),'start of month') AS cohort "
                "FROM orders GROUP BY cust_id), eligible AS ("
                "SELECT cust_id,cohort FROM firsts WHERE cohort IS NOT NULL)"
                "SELECT strftime('%Y%m',f.cohort),COUNT(*),"
                "SUM(CASE WHEN EXISTS (SELECT 1 FROM orders o WHERE o.cust_id=f.cust_id "
                "AND date(o.order_date,'start of month')=date(f.cohort,'+1 month')) "
                "THEN 1 ELSE 0 END) FROM eligible f "
                "GROUP BY f.cohort ORDER BY f.cohort").fetchall()
            groups = defaultdict(list)
            for _,cid,stamp in rows:
                if stamp is not None:
                    groups[cid].append(day(stamp))
            oracle = defaultdict(lambda: [0,0])
            for dates in groups.values():
                first = min(dates)
                key = f"{first.year:04d}{first.month:02d}"
                next_year = first.year+int(first.month == 12)
                next_month = 1 if first.month == 12 else first.month+1
                oracle[key][0] += 1
                oracle[key][1] += int(any(d.year == next_year and d.month == next_month
                                          for d in dates))
            self.assertEqual(got,[(key,*counts) for key,counts in sorted(oracle.items())])
            self.assertEqual(got,[("202512",1,1),("202601",2,1),
                                  ("202602",1,1),("202603",1,0)])
        finally:
            db.close()

    def test_07_a100_next_calendar_month_is_not_fixed_30_day_gap(self):
        rows = [(1,1,"2025-12-01"),(2,1,"2026-01-31"),
                (3,2,"2026-01-31"),(4,2,"2026-02-01"),
                (5,3,"2026-01-01"),(6,3,"2026-01-31")]
        db = db_for("CREATE TABLE orders(id INT,cust_id INT,order_date TEXT);",
                    [("INSERT INTO orders VALUES (?,?,?)",rows)])
        try:
            got = db.execute(
                "WITH f AS (SELECT cust_id,MIN(order_date) AS first_order "
                "FROM orders GROUP BY cust_id)"
                "SELECT f.cust_id FROM f JOIN orders o ON o.cust_id=f.cust_id "
                "WHERE date(o.order_date,'start of month')="
                "date(f.first_order,'start of month','+1 month') "
                "GROUP BY f.cust_id ORDER BY f.cust_id").fetchall()
            self.assertEqual(got,[(1,),(2,)])
            self.assertGreater((date(2026,1,31)-date(2025,12,1)).days,30)
            self.assertLess((date(2026,2,1)-date(2026,1,31)).days,30)
            self.assertEqual((date(2026,1,31)-date(2026,1,1)).days,30)
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)
