#!/usr/bin/env python3
"""Read-only, pinned-source PNP Q073-Q076 bounded SQL replay.

Runs actual archived PostgreSQL key queries with narrowly asserted SQLite date
rewrites, not handwritten replacement answers. Q076 is deliberately flagged:
the archived key omits 10 zero-order months expected by its source illustration.
Neither native PostgreSQL, full-dataset parity, official grading nor learner work.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / '99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice'
KEY = BASE / 'Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql'
PINS = {
  73: ('15. Analytics and Performance/P073. Category share of list-price value latest vs previous year.md', '715dc885bfbba0fbee422535c95b1f35310367ef'),
  74: ('9. Windowing Functions/P074. Customers whose latest order is below their own average.md', '62b0653774a78898ce98c0ca257ed872dd6ff5a2'),
  75: ('12. Dates and Time/P075. Rolling 28-day active customers, week by week.md', 'f04c07cb922afc3648e3f799c3d327d0ceff3381'),
  76: ('12. Dates and Time/P076. Order value from new vs returning customers by month.md', '5c991b66eb5a87e858a021b0c94f0e93c173f190'),
}
SCHEMA = {
  73: ['Category(CategoryID INT, CategoryName TEXT)', 'Products(ProductID INT, CategoryID INT, Sale_Price REAL)', 'Orders(OrderID INT, OrderDate TEXT)', 'OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT, Quantity INT)'],
  74: ['Orders(OrderID INT, CustomerID INT, OrderDate TEXT, Total_Order_Amount REAL)'],
  75: ['Orders(OrderID INT, CustomerID INT, OrderDate TEXT)'],
  76: ['Orders(OrderID INT, CustomerID INT, OrderDate TEXT, Total_Order_Amount REAL)'],
}
# Independently retyped source Markdown illustrations, not official grading data.
EXAMPLES = {
  73: ({'Category': [(1,'Audio'),(2,'Home')], 'Products':[(101,1,10),(102,2,5),(103,99,5)],
        'Orders':[(1,'2025-06-01'),(2,'2026-06-01')],
        'OrderDetails':[(1,1,101,8),(2,1,102,4),(3,2,101,6),(4,2,102,5),(5,2,103,3)]},
       [('Unmapped',0,15,15),('Home',20,25,5),('Audio',80,60,-20)]),
  74: ({'Orders':[(1,10,'2026-01-01',100),(2,10,'2026-01-02',100),
                  (3,10,'2026-01-03',100),(4,10,'2026-04-01',60),
                  (5,20,'2026-03-20',50)]},
       [(10,'2026-04-01',60,3,100,40)]),
  75: ({'Orders':[(1,10,'2026-03-02'),(2,20,'2026-03-29')]},
       [('2026-03-29',1,2)]),
  76: ({'Orders':[(1,10,'2025-01-01',100),(2,10,'2025-12-01',50),
                  (3,20,'2025-12-05',100),(4,10,'2026-01-05',75),
                  (5,20,'2026-01-07',25),(6,30,'2026-01-10',50)]},
       [('2025-12-01',1,1,100,50,33.33),('2026-01-01',1,2,50,100,66.67)]),
}
# Independent boundary groups (one per question); explicit expected results.
BOUNDARIES = {
  73: ({'Category': [(1,'Audio'),(2,'Home')], 'Products':[(101,1,10),(102,2,10)],
        'Orders':[(1,'2025-02-01'),(2,'2026-03-01')],
        'OrderDetails':[(1,1,101,5),(2,2,102,3),(3,2,101,1)]},
       [('Home',0,75,75),('Audio',100,25,-75)]),
  74: ({'Orders':[(1,10,'2026-01-01',100),(2,10,'2026-01-02',100),
                  (3,10,'2026-01-03',100),(4,10,'2026-04-01',60),
                  (5,40,'2026-03-31',100),(6,40,'2026-03-31',100),
                  (7,40,'2026-04-01',100),(8,40,'2026-04-01',50),
                  (9,30,'2025-12-01',100),(10,30,'2025-12-02',100),
                  (11,30,'2025-12-03',100),(12,30,'2026-01-01',10),
                  (13,50,'2026-04-01',10)]},
       [(40,'2026-04-01',50,3,100,50),(10,'2026-04-01',60,3,100,40)]),
  75: ({'Orders':[(1,1,'2026-01-01'),(2,1,'2026-01-20'),
                  (3,2,'2026-01-30'),(4,1,'2026-02-05'),
                  (5,3,'2026-02-15'),(6,2,'2026-02-26'),
                  (7,4,'2026-03-01')]},
       [('2026-02-01',1,2),('2026-02-08',1,2),('2026-02-15',1,3),
        ('2026-02-22',0,3),('2026-03-01',2,4)]),
  76: ({'Orders':[(1,10,'2024-01-01',5),(2,10,'2026-02-01',50),
                  (3,20,'2026-02-02',30),(4,20,'2026-02-07',20),
                  (5,10,'2026-03-01',25),(6,30,'2026-03-02',10)]},
       [('2026-02-01',2,1,50,50,50),('2026-03-01',1,1,10,25,71.43)]),
}
def git_blob_sha(path):
    raw=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def replace_once(sql, src, dst):
    assert sql.count(src)==1, f'source expression no longer unique: {src}'
    return sql.replace(src,dst)
def key_sql(number, key):
    match=re.search(rf'(?ms)^-- Q{number}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)',key)
    assert match,f'Q{number} missing key'
    sql=match.group(1).strip()
    assert sql.startswith('WITH ') and sql.endswith(';')
    return sql
def adapt(number,sql):
    if number==73:
        changes=[('EXTRACT(YEAR FROM MAX(o.OrderDate))::int',"CAST(strftime('%Y', MAX(o.OrderDate)) AS INTEGER)"),
                 ('EXTRACT(YEAR FROM o.OrderDate)',"CAST(strftime('%Y', o.OrderDate) AS INTEGER)"),
                 ('MAKE_DATE(a.latest_year - 1, 1, 1)',"printf('%04d-01-01', a.latest_year - 1)"),
                 ('MAKE_DATE(a.latest_year + 1, 1, 1)',"printf('%04d-01-01', a.latest_year + 1)")]
    elif number==74:
        changes=[('MAX(o.OrderDate)::date','DATE(MAX(o.OrderDate))'),
                 ('a.last_day - 89',"DATE(a.last_day, '-89 days')")]
    elif number==75:
        changes=[('MIN(o.OrderDate)::date','DATE(MIN(o.OrderDate))'),
                 ('MAX(o.OrderDate)::date','DATE(MAX(o.OrderDate))'),
                 ('b.last_day - 7 * g.n - 27',"DATE(b.last_day, printf('-%d days', 7 * g.n + 27))"),
                 ('b.last_day - 7 * g.n',"DATE(b.last_day, printf('-%d days', 7 * g.n))"),
                 ('generate_series(0, 11) AS g(n)','seq AS g'),
                 ('WITH bounds AS (','WITH RECURSIVE seq(n) AS (VALUES(0) UNION ALL SELECT n+1 FROM seq WHERE n < 11), bounds AS ('),
                 ('we.week_end - 6',"DATE(we.week_end, '-6 days')"),
                 ('we.week_end - 27',"DATE(we.week_end, '-27 days')"),
                 ('we.week_end + 1',"DATE(we.week_end, '+1 day')")]
    elif number==76:
        changes=[("DATE_TRUNC('month', MAX(o.OrderDate))::date","DATE(MAX(o.OrderDate), 'start of month')"),
                 ("DATE_TRUNC('month', o.OrderDate)::date","DATE(o.OrderDate, 'start of month')"),
                 ("DATE_TRUNC('month', MIN(o.OrderDate) OVER (PARTITION BY o.CustomerID))::date",
                  "DATE(MIN(o.OrderDate) OVER (PARTITION BY o.CustomerID), 'start of month')"),
                 ("(a.last_month - INTERVAL '11 months')::date","DATE(a.last_month, '-11 months')")]
    else: raise AssertionError(number)
    for old,new in changes: sql=replace_once(sql,old,new)
    assert not any(word in sql for word in ('::','MAKE_DATE','generate_series','DATE_TRUNC','EXTRACT(', "INTERVAL '"))
    return sql
def replay(number,sql,dataset,expected,label):
    db=sqlite3.connect(':memory:')
    try:
        for schema in SCHEMA[number]: db.execute('CREATE TABLE '+schema)
        for table,rows in dataset.items():
            if rows: db.executemany('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in rows[0])+')',rows)
        actual=db.execute(sql).fetchall()
        assert actual==expected,f'Q{number} {label} got {actual!r}; expected {expected!r}'
        return actual
    finally: db.close()
def main():
    assert sqlite3.sqlite_version_info >= (3,39,0)
    assert git_blob_sha(KEY)=='7912c8e676621c513e0b635a40c6ee299404676e','archived key changed'
    archive=KEY.read_text(encoding='utf-8')
    for number,(rel,sha) in PINS.items():
        file=BASE/rel
        assert git_blob_sha(file)==sha,f'Q{number} archived source changed'
        source=file.read_text(encoding='utf-8')
        for marker in (f'# PNP Q{number:03d}.','NOT SOLVED YET',
                       '### Sample input and expected output','## Schema',
                       '## Official solution','Pending'):
            assert marker in source,f'Q{number} missing preserved evidence marker'
        sql=adapt(number,key_sql(number,archive))
        returned=replay(number,sql,*EXAMPLES[number],'archived illustration returned rows')
        replay(number,sql,*BOUNDARIES[number],'independent synthetic boundary')
        if number==76:
            assert len(returned)==2 and '2025-02-01' not in {row[0] for row in returned}
            print('Q076 source-contract FAILURE reproduced: key emits only 2 populated months, missing 10 of the 12 calendar months required by the question/illustration')
    print('PASS: pinned Q073-Q076 provenance, 4 bounded returned-row illustrations and 4 synthetic fixtures. Q076 full illustrated 12-month contract FAILS; not native PostgreSQL, provider grading or learner mastery.')
if __name__=='__main__': main()
