#!/usr/bin/env python3
"""Read-only PNP Advanced A096–A100 dates audit against disposable native MySQL 8.

ALL inputs below are auditor-created, not source datasets, provider answer keys,
learner submissions or coursework mastery. Only ephemeral audit tables are touched.
"""
import datetime as dt
import hashlib
import itertools
import os
import re
import unittest
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
               "1. SQL Mastry/2.PNP- foundations and practice/12. Dates and Time")
PINS = {
    "A096": "403c5e129970268f24a925e8527d55d833b7a3f6",
    "A097": "5fd46f87854e52c3ba4c22fd56e635774c04edd6",
    "A098": "89555669d558721ab2f949a612d377c0095680e0",
    "A099": "ac542b2b0366010d6888354e8a8b047475349bb5",
    "A100": "277fafe7f196cdcb7b2eaef65602ef39c2455dc5",
}


def source(sid):
    paths = list(BASE.glob(sid + ". *.md"))
    if len(paths) != 1:
        raise AssertionError((sid, "missing or duplicated source", paths))
    raw = paths[0].read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if blob != PINS[sid]:
        raise AssertionError((sid, "original Git blob has changed", blob))
    return raw.decode("utf-8")


class NativeDatesAndRetention(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.getenv("MYSQL_DATABASE") != "audit" or os.getenv("MYSQL_USER") != "audit":
            raise RuntimeError("Only disposable audit schema/user are permitted")
        cls.db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            database="audit", user="audit", password=os.environ["MYSQL_PASSWORD"],
            charset="utf8mb4", autocommit=True)
        with cls.db.cursor() as c:
            c.execute("SELECT VERSION()")
            ver = c.fetchone()[0]
        if not ver.startswith("8.0."):
            raise RuntimeError("Requires real native MySQL 8.0; got " + ver)
        print("A096-A100 native MySQL version " + ver, flush=True)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def run_sql(self, sql, params=None):
        with self.db.cursor() as c:
            c.execute(sql, params)
            return c.fetchall() if c.description else c.rowcount

    def put(self, table, rows):
        if rows:
            with self.db.cursor() as c:
                p = ",".join(["%s"] * len(rows[0]))
                c.executemany("INSERT INTO " + table + " VALUES (" + p + ")", rows)

    def setUp(self):
        for table in ("orders", "customers"):
            self.run_sql("DROP TABLE IF EXISTS " + table)
        self.run_sql("""CREATE TABLE orders(
          order_id INT PRIMARY KEY, cust_id INT NULL, order_date DATETIME NULL,
          INDEX idx_order_date(order_date)) ENGINE=InnoDB""")
        self.run_sql("""CREATE TABLE customers(
          cust_id INT PRIMARY KEY, signup_date DATE NULL) ENGINE=InnoDB""")

    def tearDown(self):
        for table in ("orders", "customers"):
            self.run_sql("DROP TABLE IF EXISTS " + table)

    def orders(self, rows):
        self.put("orders", rows)

    def a096(self, anchor="2026-02-01"):
        return self.run_sql("""SELECT order_id FROM orders
          WHERE order_date >= DATE_SUB(%s, INTERVAL 30 DAY)
          ORDER BY order_id""", (anchor,))

    def a097(self):
        return self.run_sql("""SELECT order_id,
          DATE_FORMAT(order_date,'%Y-%m-01') AS month_start,
          LAST_DAY(order_date) AS month_end
          FROM orders ORDER BY order_id""")

    def a098(self):
        return self.run_sql("""SELECT DATE_SUB(DATE(order_date),
          INTERVAL WEEKDAY(order_date) DAY) AS monday,
          COUNT(*) AS n FROM orders
          WHERE order_date IS NOT NULL GROUP BY monday ORDER BY monday""")

    def a099(self):
        return self.run_sql("""SELECT c.cust_id,DATE(firsts.first_order) AS first_order
          FROM customers c JOIN
           (SELECT cust_id,MIN(order_date) AS first_order
            FROM orders GROUP BY cust_id) firsts ON firsts.cust_id=c.cust_id
          WHERE firsts.first_order >= c.signup_date
            AND firsts.first_order < DATE_ADD(c.signup_date,INTERVAL 8 DAY)
          ORDER BY c.cust_id""")

    def a100(self):
        return self.run_sql("""WITH firsts AS
          (SELECT cust_id,DATE_FORMAT(MIN(order_date),'%Y-%m-01') AS first_month
           FROM orders WHERE cust_id IS NOT NULL AND order_date IS NOT NULL
           GROUP BY cust_id)
          SELECT DATE_FORMAT(f.first_month,'%Y%m') AS cohort,
            COUNT(DISTINCT o.cust_id) AS retained_m1
          FROM firsts f JOIN orders o ON o.cust_id=f.cust_id
            AND o.order_date >= DATE_ADD(f.first_month,INTERVAL 1 MONTH)
            AND o.order_date < DATE_ADD(f.first_month,INTERVAL 2 MONTH)
          GROUP BY cohort ORDER BY cohort""")

    def test_01_pin_five_sources_and_unsolved_learner_status(self):
        for sid in PINS:
            with self.subTest(sid=sid):
                s = source(sid)
                self.assertIn("NOT SOLVED YET", s)
                self.assertIn("PDF p. 19", s)
                self.assertIn("Sample input and expected output (illustrative)", s)
                self.assertIn("## My solution — SQLite\n\nPending.", s)
                self.assertIn("## My solution — SQL Server\n\nPending.", s)
                self.assertIn("## Official solution\n\nPending", s)

    def test_02_a096_literal_original_query_replayed_live(self):
        s = source("A096")
        found = re.search(r"```sql\n(.*?)\n```", s, re.S)
        self.assertIsNotNone(found)
        literal = found.group(1)
        self.assertIn("DATEDIFF(CURDATE(), order_date) <= 30", literal)
        today = self.run_sql("SELECT CURDATE()")[0][0]
        self.orders([(1,None,today-dt.timedelta(days=31)),
                     (2,None,today-dt.timedelta(days=30)),
                     (3,None,today),(4,None,today+dt.timedelta(days=1)),
                     (5,None,None)])
        ids = sorted(x[0] for x in self.run_sql(literal))
        fast = [x[0] for x in self.a096(today.isoformat())]
        self.assertEqual(ids, [2,3,4])
        self.assertEqual(ids, fast)
        # Source's <= 30 predicate also includes future-dated rows.

    def test_03_a096_source_illustration_replayed(self):
        self.orders([(1,None,"2026-01-01"),(2,None,"2026-01-02"),
                     (3,None,"2026-01-31"),(4,None,"2026-02-01")])
        self.assertEqual([x[0] for x in self.a096()], [2,3,4])

    def test_04_a096_timestamp_inclusive_midnight_and_future(self):
        self.orders([(1,None,"2026-01-01 23:59:59"),
                     (2,None,"2026-01-02 00:00:00"),
                     (3,None,"2026-02-01 23:59:59"),
                     (4,None,"2026-05-01 00:00:00"),
                     (5,None,None)])
        self.assertEqual([x[0] for x in self.a096()], [2,3,4])

    def test_05_a096_index_range_eligibility_not_performance_claim(self):
        self.orders([(i,None, dt.date(2026,1,1) + dt.timedelta(days=i))
                     for i in range(1,101)])
        plan = self.run_sql("""EXPLAIN SELECT order_id FROM orders
           FORCE INDEX(idx_order_date)
           WHERE order_date >= DATE_SUB('2026-02-01',INTERVAL 30 DAY)""")[0]
        # MySQL EXPLAIN: id/select_type/table/partitions/type/possible_keys/key...
        self.assertEqual(plan[6], "idx_order_date")
        self.assertEqual(plan[4], "range")
        # Hinted synthetic plan shows eligible range access, not production speed.

    def test_06_a097_source_first_and_last_of_month(self):
        self.orders([(1,None,"2026-01-15"),(2,None,"2026-02-10")])
        got = [(i,a,str(b)) for i,a,b in self.a097()]
        self.assertEqual(got, [(1,"2026-01-01","2026-01-31"),
                               (2,"2026-02-01","2026-02-28")])

    def test_07_a097_leap_february_year_end_and_null(self):
        self.orders([(1,None,"2024-02-29 23:59:59"),
                     (2,None,"2025-12-31"),(3,None,None)])
        got = [(i,a,str(b) if b is not None else None)
               for i,a,b in self.a097()]
        self.assertEqual(got,[(1,"2024-02-01","2024-02-29"),
                              (2,"2025-12-01","2025-12-31"),(3,None,None)])

    def test_08_a098_source_monday_week_example(self):
        self.orders([(i,None,day) for i,day in enumerate(
            ["2026-01-04","2026-01-05","2026-01-07",
             "2026-01-11","2026-01-12"],1)])
        self.assertEqual([(str(d),n) for d,n in self.a098()],
                         [("2025-12-29",1),("2026-01-05",3),
                          ("2026-01-12",1)])

    def test_09_a098_week_rollovers_leap_and_null(self):
        self.orders([(1,None,"2024-02-29"),(2,None,"2024-03-03"),
                     (3,None,"2024-03-04"),(4,None,None),
                     (5,None,"2026-01-01")])
        self.assertEqual([(str(d),n) for d,n in self.a098()],
                         [("2024-02-26",2),("2024-03-04",1),
                          ("2025-12-29",1)])

    def test_10_a098_every_weekday_python_date_oracle(self):
        anchor = dt.date(2026,1,5)  # Monday
        self.orders([(i,None,anchor+dt.timedelta(days=i-1))
                     for i in range(1,15)])
        self.assertEqual([(str(d),n) for d,n in self.a098()],
                         [("2026-01-05",7),("2026-01-12",7)])

    def test_11_a099_source_first_order_7day_boundary(self):
        self.put("customers",[(1,"2026-01-01"),(2,"2026-01-01"),
                              (3,"2026-01-01")])
        self.orders([(11,1,"2026-01-08"),(12,2,"2026-01-09")])
        self.assertEqual([(i,str(d)) for i,d in self.a099()],
                         [(1,"2026-01-08")])

    def test_12_a099_earlier_order_invalidates_later_eligible(self):
        self.put("customers",[(1,"2026-01-05"),(2,"2026-01-05"),
                              (3,"2026-01-05"),(4,None)])
        self.orders([(1,1,"2026-01-04"),(2,1,"2026-01-08"),
                     (3,2,"2026-01-12 23:59:59"),
                     (4,3,"2026-01-13 00:00:00"),
                     (5,4,"2026-01-06")])
        self.assertEqual([(i,str(d)) for i,d in self.a099()],
                         [(2,"2026-01-12")])

    def test_13_a099_independent_first_order_date_oracle(self):
        signup = dt.date(2026,1,10)
        self.put("customers",[(1,signup)])
        choices = (None,-1,0,7,8)
        for pair in itertools.product(choices, repeat=2):
            self.run_sql("DELETE FROM orders")
            values = [signup+dt.timedelta(days=d) for d in pair if d is not None]
            self.orders([(j+1,1,v) for j,v in enumerate(values)])
            expected = [(1,str(min(values)))] if values and 0 <= (min(values)-signup).days <= 7 else []
            actual = [(i,str(d)) for i,d in self.a099()]
            self.assertEqual(actual, expected, pair)

    def test_14_a100_source_month_one_retention(self):
        self.orders([(1,10,"2026-01-10"),(2,10,"2026-02-05"),
                     (3,20,"2026-01-20"),(4,20,"2026-03-01"),
                     (5,30,"2026-02-01"),(6,30,"2026-03-10")])
        self.assertEqual(self.a100(), (("202601",1),("202602",1)))

    def test_15_a100_december_to_january_and_multiple_returns(self):
        self.orders([(1,10,"2025-12-31"),(2,10,"2026-01-01"),
                     (3,10,"2026-01-31"),(4,20,"2026-01-31"),
                     (5,20,"2026-02-01"),(6,20,"2026-02-28"),
                     (7,30,"2026-01-01"),(8,30,"2026-03-01"),
                     (9,None,"2026-02-02")])
        self.assertEqual(self.a100(), (("202512",1),("202601",1)))

    def test_16_a100_no_return_month_omitted_policy_unverified(self):
        self.orders([(1,1,"2026-01-31"),(2,1,"2026-01-31"),
                     (3,2,"2026-02-10"),(4,2,"2026-04-01")])
        self.assertEqual(self.a100(), ())
        # The archived illustration shows only nonzero cohorts; whether
        # a zero-retained cohort should be displayed remains undetermined.

    def test_17_a100_python_oracle_125_three_order_combinations(self):
        dates = (None,"2025-12-31","2026-01-15",
                 "2026-02-01","2026-03-01")
        for three in itertools.product(dates,repeat=3):
            self.run_sql("DELETE FROM orders")
            real = [dt.date.fromisoformat(d) for d in three if d]
            self.orders([(i+1,1,d) for i,d in enumerate(real)])
            if not real:
                expected = ()
            else:
                first = min(real)
                ym = lambda d: d.year*12+d.month
                returned = any(ym(d)==ym(first)+1 for d in real)
                expected = ((first.strftime("%Y%m"),1),) if returned else ()
            self.assertEqual(self.a100(), expected, three)

    def test_18_a098_a099_a100_null_date_source_gap(self):
        self.orders([(1,None,None),(2,1,None)])
        self.put("customers",[(1,"2026-01-01")])
        self.assertEqual(self.a098(), ())
        self.assertEqual(self.a099(), ())
        self.assertEqual(self.a100(), ())


if __name__ == "__main__":
    unittest.main(verbosity=2)
