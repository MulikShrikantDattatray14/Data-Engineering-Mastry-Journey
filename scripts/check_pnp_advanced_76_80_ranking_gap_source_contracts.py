#!/usr/bin/env python3
"""PARTIAL immutable-source PNP Advanced A076-A080 reviewer.

Archived local illustrations and auditor-authored SQLite/Python differential fixtures
ONLY; not supplier MySQL 8, provider answers, PDF-render parity, original datasets,
learner work, grading, or mastery. Original archives and learner records stay read-only.
"""
import hashlib
import itertools
import sqlite3
import unittest
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/")
SOURCES = {
    "A076": ("9. Windowing Functions", "Top 2 customers by spend in each city.md",
             "6b87c321406a65cdcdc346a81fe554877da20752", 15),
    "A077": ("9. Windowing Functions", "Each customer's second most recent order.md",
             "3851825388394342b08a04c3b8c7ce11fdd80c91", 15),
    "A078": ("6. SubQueries", "Top 3 salaries per department without any window function.md",
             "77c072224bf2f069b2468f2f299e7ca75f86f0d8", 15),
    "A079": ("9. Windowing Functions", "Most recent order per customer, returning the whole row, no CTE.md",
             "390c1f009ed8cc0c101a047f32e74946bdf6c644", 15),
    "A080": ("13. Gaps and Islands", "Find the missing order_id ranges in the sequence.md",
             "b3741537d5ed13dd50ba5df11023ed7db542a60e", 16),
}
SCHEMA = """
CREATE TABLE customers(cust_id INTEGER,city TEXT);
CREATE TABLE orders(order_id INTEGER,cust_id INTEGER,order_date TEXT,status TEXT,amount REAL);
CREATE TABLE employees(emp_id INTEGER,dept_id INTEGER,salary REAL);
"""
# SQL below is auditor-authored reviewer logic. No supplied official answer is replayed.
QUERIES = {
    "A076": """
        SELECT city,cust_id,total_spend FROM (
          SELECT city,cust_id,total_spend,
            ROW_NUMBER() OVER (PARTITION BY city
                               ORDER BY total_spend DESC,cust_id) rn
          FROM (SELECT c.city,c.cust_id,SUM(o.amount) total_spend
                FROM customers c JOIN orders o ON o.cust_id=c.cust_id
                GROUP BY c.city,c.cust_id)
        ) WHERE rn<=2 ORDER BY city,cust_id
    """,
    "A077": """
        SELECT cust_id,order_id,order_date,amount FROM (
          SELECT cust_id,order_id,order_date,amount,
            ROW_NUMBER() OVER (PARTITION BY cust_id
                               ORDER BY order_date DESC,order_id DESC) rn
          FROM orders
        ) WHERE rn=2 ORDER BY cust_id
    """,
    "A078": """
        SELECT e.emp_id,e.dept_id,e.salary FROM employees e
        WHERE e.salary IS NOT NULL
          AND (SELECT COUNT(DISTINCT e2.salary) FROM employees e2
               WHERE (e2.dept_id=e.dept_id OR
                      (e2.dept_id IS NULL AND e.dept_id IS NULL))
                 AND e2.salary>e.salary)<3
        ORDER BY e.dept_id,e.salary DESC,e.emp_id
    """,
    "A079": """
        SELECT order_id,cust_id,order_date,status,amount FROM (
          SELECT order_id,cust_id,order_date,status,amount,
            ROW_NUMBER() OVER (PARTITION BY cust_id
                               ORDER BY order_date DESC,order_id DESC) rn
          FROM orders
        ) WHERE rn=1 ORDER BY cust_id
    """,
    "A080": """
        SELECT order_id+1 start_id,next_id-1 end_id FROM (
          SELECT order_id,LEAD(order_id) OVER (ORDER BY order_id) next_id
          FROM (SELECT DISTINCT order_id FROM orders WHERE order_id IS NOT NULL)
        ) WHERE next_id>order_id+1 ORDER BY start_id
    """,
}

def execute(which, records):
    with closing(sqlite3.connect(":memory:")) as conn:
        conn.executescript(SCHEMA)
        for table, rows in records.items():
            if rows:
                conn.executemany("INSERT INTO "+table+" VALUES ("+
                                 ",".join("?" * len(rows[0]))+")", rows)
        return conn.execute(QUERIES[which]).fetchall()

def order_row(order_id, cust_id, date, amount=0, status="ok"):
    return (order_id,cust_id,date,status,amount)

class SourcePinnedA076A080Reviewer(unittest.TestCase):
    def test_01_original_git_blobs_and_pending_state(self):
        self.assertEqual(len(SOURCES),5)
        for code,(folder,name,blob,page) in SOURCES.items():
            source=(BASE/folder/(code+". "+name)).read_bytes()
            actual=hashlib.sha1(b"blob "+str(len(source)).encode()+b"\0"+source).hexdigest()
            self.assertEqual(actual,blob,code)
            text=source.decode("utf-8")
            for marker in ("# Advanced Q"+code[1:]+".",
                           "question "+str(int(code[1:]))+", PDF p. "+str(page),
                           "### Sample input and expected output (illustrative)",
                           "The PDF does not provide separate sample input",
                           "NOT SOLVED YET",
                           "## My solution — SQLite\n\nPending.",
                           "## My solution — SQL Server\n\nPending.",
                           "## Official solution\n\nPending until"):
                self.assertIn(marker,text,(code,marker))

    # These 5 are archived Markdown-authored local illustrations, not PDF examples.
    def test_02_a076_archived_local_illustration(self):
        c=[(1,"Pune"),(2,"Pune"),(3,"Pune"),(4,"Delhi")]
        o=[order_row(i+10,i,"2026-01-01",v)
           for i,v in enumerate((100,80,60,40),1)]
        self.assertEqual(execute("A076",{"customers":c,"orders":o}),
                         [("Delhi",4,40),("Pune",1,100),("Pune",2,80)])

    def test_03_a077_archived_local_illustration(self):
        o=[order_row(1,10,"2026-01-01",10),
           order_row(2,10,"2026-01-05",20),
           order_row(3,10,"2026-01-09",30),
           order_row(4,20,"2026-02-01",40)]
        self.assertEqual(execute("A077",{"orders":o}),
                         [(10,2,"2026-01-05",20)])

    def test_04_a078_archived_local_illustration(self):
        e=[(1,10,100),(2,10,90),(3,10,80),(4,10,70),(5,20,60)]
        self.assertEqual(execute("A078",{"employees":e}),
                         [(1,10,100),(2,10,90),(3,10,80),(5,20,60)])
        self.assertNotIn("OVER (",QUERIES["A078"].upper())

    def test_05_a079_archived_local_illustration(self):
        o=[order_row(1,10,"2026-01-01",10,"delivered"),
           order_row(2,10,"2026-01-03",20,"delivered"),
           order_row(3,20,"2026-02-01",30,"pending")]
        self.assertEqual(execute("A079",{"orders":o}),[o[1],o[2]])
        self.assertNotIn("WITH ",QUERIES["A079"].upper())

    def test_06_a080_archived_local_illustration(self):
        o=[order_row(i,10,None) for i in (1,2,5,8)]
        self.assertEqual(execute("A080",{"orders":o}),[(3,4),(6,7)])

    # Reviewer-defined policies and counterexamples, not provider requirements.
    def test_07_a076_customer_grain_and_no_order_policy(self):
        c=[(1,"A"),(2,"A"),(3,"A"),(4,"A"),(5,None)]
        o=[order_row(1,1,"2026-01-01",5),
           order_row(2,1,"2026-01-02",10),
           order_row(3,2,"2026-01-02",9),
           order_row(4,3,"2026-01-02",8),
           order_row(5,5,"2026-01-02",1)]
        self.assertEqual(execute("A076",{"customers":c,"orders":o}),
                         [(None,5,1),("A",1,15),("A",2,9)])

    def test_08_a077_tied_and_null_dates_single_order(self):
        o=[order_row(1,1,None),order_row(2,1,"2026-01-01"),
           order_row(3,1,"2026-01-01"),order_row(4,2,None)]
        self.assertEqual(execute("A077",{"orders":o}),
                         [(1,2,"2026-01-01",0)])

    def test_09_a078_three_distinct_salary_levels_not_three_people(self):
        e=[(1,1,100),(2,1,100),(3,1,90),(4,1,80),(5,1,70),
           (6,None,30),(7,None,20),(8,None,None)]
        self.assertEqual(execute("A078",{"employees":e}),
                         [(6,None,30),(7,None,20),(1,1,100),(2,1,100),
                          (3,1,90),(4,1,80)])

    def test_10_a079_tied_date_stable_id_and_null_date(self):
        o=[order_row(1,1,None),order_row(2,1,"2026-01-02"),
           order_row(3,1,"2026-01-02"),order_row(4,2,None)]
        self.assertEqual(execute("A079",{"orders":o}),[o[2],o[3]])

    def test_11_a080_duplicates_negative_and_null_ids(self):
        o=[order_row(i,1,None) for i in (-3,-3,-1,0,3,None)]
        self.assertEqual(execute("A080",{"orders":o}),[(-2,-2),(1,2)])

    def test_12_a076_81_independent_city_spend_oracles(self):
        c=[(1,"A"),(2,"A"),(3,"A"),(4,"B")]
        for amounts in itertools.product((-5,0,10),repeat=4):
            o=[order_row(i,i,"2026-01-01",v)
               for i,v in enumerate(amounts,1)]
            expected=[]
            for city in ("A","B"):
                ranked=sorted([(i,amounts[i-1]) for i,loc in c if loc==city],
                              key=lambda pair:(-pair[1],pair[0]))[:2]
                expected.extend(sorted((city,i,float(v)) for i,v in ranked))
            self.assertEqual(execute("A076",{"customers":c,"orders":o}),
                             expected,amounts)

    def test_13_a077_256_independent_second_order_oracles(self):
        dates=(None,"2026-01-01","2026-01-02","2026-01-03")
        for ds in itertools.product(dates,repeat=4):
            o=[order_row(i,1 if i<=2 else 2,ds[i-1],i)
               for i in range(1,5)]
            expected=[]
            for cust in (1,2):
                ranked=sorted((r for r in o if r[1]==cust),
                              key=lambda r:(r[2] is not None,r[2] or "",r[0]),
                              reverse=True)
                expected.append((cust,ranked[1][0],ranked[1][2],ranked[1][4]))
            self.assertEqual(execute("A077",{"orders":o}),expected,ds)

    def test_14_a078_256_independent_distinct_salary_level_oracles(self):
        for salaries in itertools.product((-1,0,10,20),repeat=4):
            e=[(i,1,v) for i,v in enumerate(salaries,1)]
            top=set(sorted(set(salaries),reverse=True)[:3])
            expected=sorted((r for r in e if r[2] in top),
                            key=lambda r:(-r[2],r[0]))
            self.assertEqual(execute("A078",{"employees":e}),expected,salaries)

    def test_15_a079_256_independent_whole_latest_row_oracles(self):
        dates=(None,"2026-01-01","2026-01-02","2026-01-03")
        for ds in itertools.product(dates,repeat=4):
            o=[order_row(i,1 if i<=2 else 2,ds[i-1],i,"s"+str(i))
               for i in range(1,5)]
            expected=[max((r for r in o if r[1]==cust),
                          key=lambda r:(r[2] is not None,r[2] or "",r[0]))
                      for cust in (1,2)]
            self.assertEqual(execute("A079",{"orders":o}),expected,ds)

    def test_16_a080_256_independent_set_gap_oracles(self):
        for flags in itertools.product((False,True),repeat=8):
            values=[i+1 for i,flag in enumerate(flags) if flag]
            expected=[]
            for left,right in zip(values,values[1:]):
                if right-left>1:
                    expected.append((left+1,right-1))
            self.assertEqual(execute("A080",{"orders":[order_row(i,1,None)
                                                      for i in values]}),
                             expected,flags)

    def test_17_a078_ties_in_three_salaries_are_not_three_rows(self):
        e=[(1,1,100),(2,1,90),(3,1,80),(4,1,80),(5,1,70)]
        self.assertEqual(len(execute("A078",{"employees":e})),4)
        # ROW_NUMBER LIMIT 3 would produce only 3: vendor tie policy unknown.

    def test_18_a080_min_max_bound_and_no_id_sequence(self):
        self.assertEqual(execute("A080",{}),[])
        self.assertEqual(execute("A080",{"orders":[order_row(20,1,None)]}),[])
        self.assertEqual(execute("A080",{"orders":[order_row(10,1,None),
                                                   order_row(13,1,None)]}),
                         [(11,12)])
        # No claim for missing IDs before 10 or after 13.

if __name__=="__main__":
    unittest.main(verbosity=2)
