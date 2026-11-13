#!/usr/bin/env python3
"""Auditor-only A015/A021/A024/A027/A028 source-policy tests; never learner/official SQL."""
import hashlib
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ('99. Reference Materials/Original Mastery Snapshot/'
                 '1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice')
PINS = {
 'A015': ('9. Windowing Functions/A015. Show each employee next to their department average, without colla.md','6140bffe76e4aaecec6fd28005aa0bc47ab842df'),
 'A021': ('3. Sorting and Grouping/A021. Which weekday brings in the most orders.md','ecbffb7cdd43adf69c8b08a861e0e00efe4c5964'),
 'A024': ('4. Aggregation/A024. Cancellation rate per customer as a percentage.md','9ee7fe4ccc0fddad0445f3c826d2da066378f521'),
 'A027': ('4. Aggregation/A027. First order, last order and active lifespan per customer.md','e04c9c77c24074b9ee487c44f3a3ec2bb8fa8c45'),
 'A028': ('6. SubQueries/A028. Employees paid above the average of their own department.md','604c8cdbce16585ec2bac1aae993c5a665770d48'),
}
def db_for(table,rows):
    d=sqlite3.connect(':memory:')
    ddl={'employees':'CREATE TABLE employees(emp_id INTEGER,dept_id INTEGER,salary REAL)',
         'orders':'CREATE TABLE orders(order_id INTEGER,cust_id INTEGER,order_date TEXT,status TEXT)'}
    n=3 if table=='employees' else 4
    d.execute(ddl[table])
    d.executemany('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in range(n))+')',rows)
    return d

WINDOW='SELECT emp_id,dept_id,salary,AVG(salary) OVER(PARTITION BY dept_id) FROM employees ORDER BY emp_id'
CORR="""SELECT e.emp_id,e.dept_id,e.salary,
 (SELECT AVG(d.salary) FROM employees d WHERE d.dept_id=e.dept_id)
 FROM employees e ORDER BY e.emp_id"""
NULLSAFE=CORR.replace('d.dept_id=e.dept_id','d.dept_id IS e.dept_id')
ABOVE="""SELECT e.emp_id FROM employees e WHERE e.salary >
 (SELECT AVG(d.salary) FROM employees d WHERE d.dept_id=e.dept_id)
 ORDER BY e.emp_id"""
ABOVE_NULLSAFE=ABOVE.replace('d.dept_id=e.dept_id','d.dept_id IS e.dept_id')
ABOVE_WINDOW="""SELECT emp_id FROM
 (SELECT emp_id,salary,AVG(salary) OVER(PARTITION BY dept_id) avg_pay FROM employees)
 WHERE salary>avg_pay ORDER BY emp_id"""
WEEKDAY="""WITH c AS (
 SELECT strftime('%w',order_date) w,COUNT(*) n
 FROM orders WHERE strftime('%w',order_date) IS NOT NULL
 GROUP BY strftime('%w',order_date))
 SELECT w,n FROM c WHERE n=(SELECT MAX(n) FROM c) ORDER BY w"""
RATE="""SELECT cust_id,ROUND(100.0*SUM(CASE WHEN status='cancelled' THEN 1 ELSE 0 END)/COUNT(*),2)
 FROM orders GROUP BY cust_id ORDER BY cust_id"""
RATE_NORMAL=RATE.replace("status='cancelled'","lower(trim(status))='cancelled'")
LIFESPAN="""SELECT cust_id,MIN(order_date),MAX(order_date),
 CAST(julianday(MAX(order_date))-julianday(MIN(order_date)) AS INT)
 FROM orders WHERE cust_id IS NOT NULL AND order_date IS NOT NULL
 GROUP BY cust_id ORDER BY cust_id"""

class ReviewerTests(unittest.TestCase):
 def test_original_five_git_blobs_preserved_pending(self):
    for sid,(relative,pin) in PINS.items():
        data=(SOURCE/relative).read_bytes()
        sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        with self.subTest(source=sid):
            self.assertEqual(sha,pin)
            body=data.decode('utf-8')
            self.assertTrue(body.startswith('# Advanced Q'+sid[1:]+'. '))
            self.assertIn('NOT SOLVED YET',body)
            self.assertIn('## My solution — SQLite\n\nPending.',body)
            self.assertIn('## My solution — SQL Server\n\nPending.',body)
            self.assertIn('## Official solution\n\nPending until',body)
    self.assertIn('Write both a correlated-subquery version and a window-function version',
                  (SOURCE/PINS['A015'][0]).read_text())

 def test_a015_local_illustration_both_strategies(self):
    with db_for('employees',[(1,10,40000),(2,10,60000),(3,20,90000)]) as db:
        expected=[(1,10,40000,50000),(2,10,60000,50000),(3,20,90000,90000)]
        self.assertEqual(db.execute(WINDOW).fetchall(),expected)
        self.assertEqual(db.execute(CORR).fetchall(),expected)

 def test_a015_plain_equality_null_department_discrepancy(self):
    with db_for('employees',[(1,None,100),(2,None,300),(3,10,200),(4,10,None)]) as db:
        self.assertEqual(db.execute(WINDOW).fetchall(),
            [(1,None,100,200),(2,None,300,200),(3,10,200,200),(4,10,None,200)])
        self.assertEqual(db.execute(CORR).fetchall(),
            [(1,None,100,None),(2,None,300,None),(3,10,200,200),(4,10,None,200)])

 def test_a015_null_safe_correlation_matches_window_four_datasets(self):
    for rows in [[],[(1,None,None)],[(1,None,100),(2,None,300),(3,1,None)],
                 [(1,1,10),(2,1,None),(3,1,30),(4,2,12),(5,2,12)]]:
        with self.subTest(rows=rows),db_for('employees',rows) as db:
            self.assertEqual(db.execute(NULLSAFE).fetchall(),db.execute(WINDOW).fetchall())

 def test_a015_sqlite_plan_shapes_no_speed_inference(self):
    with db_for('employees',[(i,i%4,i*100) for i in range(1,41)]) as db:
        db.execute('CREATE INDEX ix_dept ON employees(dept_id)')
        p=' '.join(r[3] for r in db.execute('EXPLAIN QUERY PLAN '+CORR))
        q=' '.join(r[3] for r in db.execute('EXPLAIN QUERY PLAN '+WINDOW))
        self.assertIn('CORRELATED SCALAR SUBQUERY',p)
        self.assertIn('CO-ROUTINE',q)

 def test_a028_null_department_changes_above_average_results(self):
    rows=[(1,None,100),(2,None,300),(3,10,100),(4,10,300),(5,20,None)]
    with db_for('employees',rows) as db:
        self.assertEqual(db.execute(ABOVE).fetchall(),[(4,)])
        self.assertEqual(db.execute(ABOVE_NULLSAFE).fetchall(),[(2,),(4,)])
        self.assertEqual(db.execute(ABOVE_WINDOW).fetchall(),[(2,),(4,)])

 def test_a021_ties_and_all_null(self):
    with db_for('orders',[(1,1,'2026-01-05',None),(2,2,'2026-01-06',None),(3,3,None,None)]) as db:
        self.assertEqual(db.execute(WEEKDAY).fetchall(),[('1',1),('2',1)])
    with db_for('orders',[(1,1,None,None)]) as db:
        self.assertEqual(db.execute(WEEKDAY).fetchall(),[])

 def test_a021_timezone_changes_weekday_under_utc_policy(self):
    rows=[(1,1,'2026-01-04T23:30:00-02:00',None),(2,2,'2026-01-04',None)]
    with db_for('orders',rows) as db:
        self.assertEqual(db.execute("SELECT order_id,strftime('%w',order_date) FROM orders ORDER BY order_id").fetchall(),[(1,'1'),(2,'0')])
        self.assertEqual(db.execute(WEEKDAY).fetchall(),[('0',1),('1',1)])

 def test_a024_cancellation_case_normalization_and_null_denominator(self):
    rows=[(1,10,None,'cancelled'),(2,10,None,'Cancelled'),
          (3,10,None,'placed'),(4,10,None,None),(5,20,None,' completed ')]
    with db_for('orders',rows) as db:
        self.assertEqual(db.execute(RATE).fetchall(),[(10,25),(20,0)])
        self.assertEqual(db.execute(RATE_NORMAL).fetchall(),[(10,50),(20,0)])

 def test_a024_order_driven_query_omits_zero_order_customer(self):
    with db_for('orders',[(1,10,None,'cancelled')]) as db:
        db.execute('CREATE TABLE customers(cust_id INTEGER)')
        db.executemany('INSERT INTO customers VALUES (?)',[(10,),(20,)])
        self.assertEqual(db.execute(RATE).fetchall(),[(10,100)])
        self.assertEqual(db.execute("""SELECT c.cust_id,COUNT(o.order_id)
          FROM customers c LEFT JOIN orders o ON o.cust_id=c.cust_id
          GROUP BY c.cust_id ORDER BY c.cust_id""").fetchall(),[(10,1),(20,0)])

 def test_a027_date_only_and_leap_day(self):
    rows=[(1,10,'2026-01-01',None),(2,10,'2026-01-11',None),
          (3,20,'2024-02-28',None),(4,20,'2024-03-01',None)]
    with db_for('orders',rows) as db:
        self.assertEqual(db.execute(LIFESPAN).fetchall(),
                         [(10,'2026-01-01','2026-01-11',10),(20,'2024-02-28','2024-03-01',2)])

 def test_a027_timezone_offsets_invert_lexical_first_last(self):
    rows=[(1,1,'2026-01-03T00:30:00+14:00',None),
          (2,1,'2026-01-02T23:30:00-12:00',None)]
    with db_for('orders',rows) as db:
        result=db.execute("""SELECT MIN(order_date),MAX(order_date),
           julianday(MIN(order_date)),julianday(MAX(order_date)) FROM orders""").fetchone()
        self.assertGreater(result[2],result[3])
        self.assertLess(db.execute(LIFESPAN).fetchone()[3],0)
        self.assertGreater(db.execute("""SELECT MAX(julianday(order_date))-MIN(julianday(order_date))
            FROM orders""").fetchone()[0],0)

if __name__=='__main__':
 unittest.main(verbosity=2)
