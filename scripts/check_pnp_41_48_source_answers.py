#!/usr/bin/env python3
"""Read-only PNP Q041–Q048 source/key/illustration audit, not provider grading.

Queries are extracted from immutable original PostgreSQL supplied-key SQL.
SQLite execution uses only explicitly asserted dialect translations Q043–Q045.
Original full Commerce dataset and native PG results remain unverified.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/'99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice'
SOURCES={
41:('9. Windowing Functions/P041. Most expensive product in each category.md','30af7f9fe147026c0eecce83e4c8c693336fad37'),
42:('9. Windowing Functions/P042. RANK vs DENSE_RANK vs ROW_NUMBER on order counts.md','0c8d08af7bcbf884b1562c1f43927d5ec6175613'),
43:('9. Windowing Functions/P043. Month-to-date order value for the latest three months.md','a3ab0413e1dd409e49fa919bdd230448b4071aa4'),
44:('9. Windowing Functions/P044. Month-over-month growth in order value.md','09f943d73117f2581dfab16d877a26639f894178'),
45:("9. Windowing Functions/P045. Typical gap between a customer's orders.md",'76ce0abbf4c1f479cc684f4de2e03f2ac15b6ad1'),
46:('2. Joins/P046. Same-brand products where one costs at least twice the other.md','9477f89d7839be54cd8c90a38574ffd4fc954680'),
47:('4. Aggregation/P047. Brands with at least three products, and how much they sold.md','3994875bf71d07b93cedc9960a6fe3bc8de32c1d'),
48:('4. Aggregation/P048. Do discounted products sell more.md','055530607f0ae4ba79cd9ceaa4e04e5853f06e24'),
}
KEY=BASE/'Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql'
KEY_SHA='7912c8e676621c513e0b635a40c6ee299404676e'

def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def original_sql(n,text):
    m=re.search(rf'(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)',text)
    assert m, f'Q{n} supplied key not found'
    return m.group(1).strip()

def verify_sources():
    assert blob(KEY)==KEY_SHA, 'Original supplied-key drift'
    key=KEY.read_text(encoding='utf8')
    q={}
    for n,(relative,sha) in SOURCES.items():
        path=BASE/relative
        assert blob(path)==sha, f'P{n:03d} original source drift'
        source=path.read_text(encoding='utf8')
        assert source.startswith(f'# PNP Q{n:03d}.'),n
        for required in ('### Sample input and expected output','## Schema','NOT SOLVED YET',
                         '## My solution — SQLite\n\nPending.','## Official solution\n\nPending'):
            assert required in source,(n,required)
        q[n]=original_sql(n,key)
        assert q[n].startswith(('WITH ','SELECT ')),n
    return q

def replace(q,old,new,expected=1):
    assert q.count(old)==expected,(old,q.count(old))
    return q.replace(old,new)

def adapt(n,q):
    if n==43:
        q=replace(q,"(DATE_TRUNC('month', MAX(o.OrderDate)) - INTERVAL '2 months')::date",
                  "date(MAX(o.OrderDate), 'start of month', '-2 months')")
        q=replace(q,"(DATE_TRUNC('month', MAX(o.OrderDate)) + INTERVAL '1 month')::date",
                  "date(MAX(o.OrderDate), 'start of month', '+1 month')")
        q=replace(q,'o.OrderDate::date','date(o.OrderDate)',2)
        q=replace(q,"DATE_TRUNC('month', d.order_date)","date(d.order_date, 'start of month')")
    if n==44:
        q=replace(q,"DATE_TRUNC('month', o.OrderDate)::date","date(o.OrderDate, 'start of month')",2)
        q=replace(q,"m.order_month - INTERVAL '1 month'","date(m.order_month, '-1 month')")
    if n==45:
        q=replace(q,'o.OrderDate::date','julianday(date(o.OrderDate))',2)
    assert '::' not in q and 'DATE_TRUNC(' not in q and "INTERVAL '" not in q,n
    return q

# Each source illustration and a separate auditor-created edge case. This is NOT
# the original full source CSV/Postgres database and never a learner submission.
CASES={
41:(
  ['Category(CategoryID INT,CategoryName TEXT)','Products(ProductID INT,Product TEXT,CategoryID INT,Sale_Price REAL)'],
  {'Category':[(1,'Drinks'),(2,'Snacks')],
   'Products':[(1,'Tea',1,10),(2,'Coffee',1,10),(3,'Unknown drink',1,None),(4,'Cookie',2,5)]},
  [('Drinks',1,'Tea',10),('Drinks',2,'Coffee',10),('Snacks',4,'Cookie',5)],
  {'Products':[(5,'Unmapped ID',99,3),(6,'Unmapped NULL',None,7),(7,'Premium tea',1,12),(8,'No price',2,None)]},
  [('Drinks',7,'Premium tea',12),('Snacks',4,'Cookie',5),('Unmapped',5,'Unmapped ID',3),('Unmapped',6,'Unmapped NULL',7)]
),
42:(
  ['Orders(OrderID INT,CustomerID INT)'],
  {'Orders':[(1,10),(2,10),(3,20),(4,20),(5,30)]},
  [(10,2,1,1,1),(20,2,2,1,1),(30,1,3,3,2)],
  {'Orders':[(6,10),(7,40),(8,40),(9,30),(10,None)]},
  [(10,3,1,1,1),(20,2,2,2,2),(30,2,3,2,2),(40,2,4,2,2)]
),
43:(
  ['Orders(OrderID INT,OrderDate TEXT,Total_Order_Amount REAL)'],
  {'Orders':[(1,'2025-01-01',100),(2,'2025-01-02',50),(3,'2025-02-01',200),(4,'2025-03-01',10),(5,'2025-03-01',20)]},
  [('2025-01-01',100,100),('2025-01-02',50,150),('2025-02-01',200,200),('2025-03-01',30,30)],
  {'Orders':[(6,'2024-12-31',900),(7,'2025-03-31',7),(8,'2025-04-01',99),(9,'2025-04-01',1),(10,None,300)]},
  [('2025-02-01',200,200),('2025-03-01',30,30),('2025-03-31',7,37),('2025-04-01',100,100)]
),
44:(
  ['Orders(OrderID INT,OrderDate TEXT,Total_Order_Amount REAL)'],
  {'Orders':[(1,'2025-01-01',100),(2,'2025-03-01',150),(3,'2025-04-01',200)]},
  [('2025-01-01',100,None,None,None),('2025-03-01',150,None,None,None),('2025-04-01',200,150,50,33.33)],
  {'Orders':[(4,'2025-04-15',-50),(5,'2025-06-02',40),(6,'2025-07-01',0),(7,'2025-08-01',8),(8,None,200)]},
  [('2025-01-01',100,None,None,None),('2025-03-01',150,None,None,None),('2025-04-01',150,150,0,0),
   ('2025-06-01',40,None,None,None),('2025-07-01',0,40,-40,-100),('2025-08-01',8,0,8,None)]
),
45:(
  ['Orders(OrderID INT,CustomerID INT,OrderDate TEXT)'],
  {'Orders':[(1,10,'2025-01-01'),(2,10,'2025-01-04'),(3,10,'2025-01-10'),(4,20,'2025-01-02'),(5,20,'2025-01-08')]},
  [(10,3,4.5,6)],
  {'Orders':[(6,20,'2025-01-08'),(7,30,'2025-01-01'),(8,30,'2025-01-01'),(9,30,'2025-01-01'),(10,40,None),(11,40,'2025-01-02')]},
  [(30,3,0,0),(20,3,3,6),(10,3,4.5,6)]
),
46:(
  ['Products(ProductID INT,Product TEXT,Brand TEXT,Sub_Category TEXT,Sale_Price REAL)'],
  {'Products':[(1,'Small','Nova','Tea',50),(2,'Medium','Nova','Tea',120),(3,'Large','Nova','Tea',300)]},
  [('Nova','Tea','Small',50,'Large',300,6),('Nova','Tea','Medium',120,'Large',300,2.5),('Nova','Tea','Small',50,'Medium',120,2.4)],
  {'Products':[(4,'Tiny','Nova','Tea',0),(5,'Coffee','Nova','Coffee',999),(6,'NullBrand',None,'Tea',10),(7,'Twice','Nova','Tea',100)]},
  [('Nova','Tea','Small',50,'Large',300,6),('Nova','Tea','Twice',100,'Large',300,3),
   ('Nova','Tea','Medium',120,'Large',300,2.5),('Nova','Tea','Small',50,'Medium',120,2.4),('Nova','Tea','Small',50,'Twice',100,2)]
),
47:(
  ['Products(ProductID INT,Brand TEXT,Sale_Price REAL)','OrderDetails(OrderDetailID INT,ProductID INT,Quantity INT)'],
  {'Products':[(1,'Nova',10),(2,'Nova',20),(3,'Nova',30),(4,'Solo',5)],
   'OrderDetails':[(10,1,2),(11,2,1)]},
  [('Nova',3,2,3,40)],
  {'Products':[(5,'Nova',40),(6,None,5),(7,'',7),(8,'  ',11)],
   'OrderDetails':[(12,1,3),(13,6,2),(14,999,20),(15,8,0)]},
  [('Nova',4,2,6,70),('Unbranded',3,2,2,10)]
),
48:(
  ['Products(ProductID INT,Market_Price REAL,Sale_Price REAL)','OrderDetails(OrderDetailID INT,ProductID INT,Quantity INT)'],
  {'Products':[(1,100,100),(2,100,95),(3,100,80),(4,100,50),(5,0,0)],
   'OrderDetails':[(11,1,2),(12,2,1),(13,3,3),(14,5,4)]},
  [('Full price',1,1,2,2),('Up to 10%',1,1,1,1),('10% to 25%',1,1,3,3),
   ('Over 25%',1,0,0,0),('Unknown',1,1,4,4)],
  {'Products':[(6,100,90),(7,100,75),(8,100,105),(9,None,4),(10,100,None)],
   'OrderDetails':[(15,6,0),(16,7,2),(17,8,3)]},
  [('Full price',2,2,2.5,5),('Up to 10%',2,2,0.5,1),('10% to 25%',2,2,2.5,5),
   ('Over 25%',1,0,0,0),('Unknown',3,1,1.33,4)]
)}

def insert(db,table,tuples):
    if tuples:
        db.executemany(f'INSERT INTO {table} VALUES('+','.join('?' for _ in tuples[0])+')',tuples)

def check(n,sql):
    ddls,sample,expected,edge,expected_edge=CASES[n]
    db=sqlite3.connect(':memory:')
    try:
        for ddl in ddls: db.execute('CREATE TABLE '+ddl)
        for table,values in sample.items(): insert(db,table,values)
        got=db.execute(sql).fetchall()
        assert got==expected,f'P{n:03d} illustration: {got!r} != {expected!r}'
        for table,values in edge.items(): insert(db,table,values)
        got=db.execute(sql).fetchall()
        assert got==expected_edge,f'P{n:03d} synthetic: {got!r} != {expected_edge!r}'
    finally: db.close()

def main():
    queries=verify_sources()
    for n,original in queries.items(): check(n,adapt(n,original))
    print('PASS: 8 source hashes, preserved PostgreSQL key, 8 illustrated output replays and 8 synthetic groups; no native PG, provider grade or learner mastery.')

if __name__=='__main__': main()
