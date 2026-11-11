#!/usr/bin/env python3
"""Pinned read-only audit of PNP Q077-Q080 supplied key on bounded SQLite fixtures.

Runs queries extracted from the archived PostgreSQL supplied answer key, with
explicitly asserted compatibility transformations. NOT provider grading, full
data parity, native PostgreSQL, or learner achievement. Q080 NULL-subcategory
counterexample is asserted as a known key/contract ambiguity, not marked correct.
"""
import hashlib
import re
import sqlite3
import statistics
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    '99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/'
    '1. SQL Mastry/2.PNP- foundations and practice'
)
KEY = BASE / 'Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql'
KEY_SHA = '7912c8e676621c513e0b635a40c6ee299404676e'
PINS = {
  77: ('2. Joins/P077. Single-source products and the value at risk.md', '22d728c1686886684dcea80381b71303aed52056'),
  78: ('9. Windowing Functions/P078. Expensive within their sub-category but selling below its median.md', 'c8baea659a6c96edd55d0eed03b805907d05a681'),
  79: ('9. Windowing Functions/P079. At which order does a customer cross 10,000 in spend.md', '8446d5ea1b09182909e452ce05b4c62141f6bdb4'),
  80: ('6. SubQueries/P080. Sub-category repurchase rate within 90 days.md', '49c42503bdf27ed5369854f47011360329e6ab45'),
}
SCHEMA = {
  77: ['Products(ProductID INT, Product TEXT, Sale_Price REAL)',
       'Suppliers(SupplierID INT, CompanyName TEXT, Country TEXT)',
       'OrderDetails(OrderDetailID INT, ProductID INT, Quantity INT, SupplierID INT)'],
  78: ['Products(ProductID INT, Product TEXT, Sub_Category TEXT, Sale_Price REAL)',
       'OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT, Quantity INT, SupplierID INT)'],
  79: ['Orders(OrderID INT, CustomerID INT, OrderDate TEXT, Total_Order_Amount REAL)'],
  80: ['Products(ProductID INT, Sub_Category TEXT)',
       'Orders(OrderID INT, CustomerID INT, OrderDate TEXT)',
       'OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT)'],
}
def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def replace_exact_once(sql, old, new):
    assert sql.count(old) == 1, f'unexpected source excerpt count: {old[:55]}'
    return sql.replace(old, new)

def extract(key, n):
    m = re.search(rf'(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)', key)
    assert m, f'missing archived Q{n} key'
    sql = m.group(1).strip()
    assert sql.startswith('WITH ') and sql.endswith(';'), n
    return sql

def sqlite_equivalent(n, sql):
    # No substitutions for Q077: SQLite executes its supplied SQL unchanged.
    if n == 78:
        sql = replace_exact_once(
            sql, 'PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY s.units_sold)',
            'median_exact(s.units_sold)')
        sql = replace_exact_once(sql, 's.price_pct_rank::numeric', 's.price_pct_rank')
    elif n == 79:
        # PostgreSQL DISTINCT ON is emulated with a ROW_NUMBER over the already
        # filtered crossing rows, ordered by original computed order_number.
        pattern = (r'first_crossing AS \(\s*SELECT DISTINCT ON \(r.CustomerID\)'
                   r'.*?\n\)\nSELECT fc.CustomerID,')
        match = re.search(pattern, sql, flags=re.S)
        assert match and len(re.findall(pattern, sql, flags=re.S)) == 1
        substitute = '''first_crossing AS (
    SELECT ranked.CustomerID, ranked.order_number,
           ranked.OrderDate, ranked.first_order_date, ranked.running_spend
    FROM (
        SELECT r.*,
               ROW_NUMBER() OVER (PARTITION BY r.CustomerID ORDER BY r.order_number) AS crossing_rank
        FROM running AS r
        WHERE r.running_spend >= 10000
    ) AS ranked
    WHERE ranked.crossing_rank = 1
)
SELECT fc.CustomerID,'''
        sql = sql[:match.start()] + substitute + sql[match.end():]
        sql = replace_exact_once(
            sql, 'fc.OrderDate - fc.first_order_date',
            'CAST(julianday(fc.OrderDate) - julianday(fc.first_order_date) AS INTEGER)')
    elif n == 80:
        sql = replace_exact_once(sql, 'a.last_day - 90',
                                 "DATE(a.last_day, '-90 days')")
        sql = replace_exact_once(sql, 'e.first_purchase_date + 90',
                                 "DATE(e.first_purchase_date, '+90 days')")
    assert not any(x in sql for x in ('::numeric', 'DISTINCT ON (', 'PERCENTILE_CONT(',
                                      'WITHIN GROUP (', 'a.last_day - 90',
                                      'e.first_purchase_date + 90'))
    return sql

class ExactMedian:
    def __init__(self):
        self.values = []
    def step(self, number):
        if number is not None:
            self.values.append(number)
    def finalize(self):
        return statistics.median(self.values) if self.values else None

def replay(n, sql, data, expected, label):
    db = sqlite3.connect(':memory:')
    db.create_aggregate('median_exact', 1, ExactMedian)
    try:
        for table in SCHEMA[n]:
            db.execute('CREATE TABLE ' + table)
        for table, rows in data.items():
            if rows:
                db.executemany(
                    'INSERT INTO ' + table + ' VALUES (' +
                    ','.join('?' for _ in rows[0]) + ')', rows)
        actual = db.execute(sql).fetchall()
        assert actual == expected, (
            f'Q{n} {label}: actual={actual!r}, expected={expected!r}')
        print(f'PASS Q{n} {label}: {len(actual)} output rows')
    finally:
        db.close()

def sample_77():
    return (
      {'Products':[(101,'Keyboard',10),(102,'Mouse',10),(103,'Cable',10)],
       'Suppliers':[(7,'Alpha','India'),(8,'Beta','India'),(9,'Gamma','Nepal')],
       'OrderDetails':[(1,101,2,7),(2,102,3,8),(3,102,1,9),(4,103,1,None)]},
      [(101,'Keyboard','Alpha','India',20,28.57)]
    )
def boundaries_77():
    return (
      {'Products':[(1,'A',5),(2,'B',10),(3,'C',20),(4,'D',0)],
       'Suppliers':[(7,'Alpha','India'),(8,'Beta','Nepal')],
       'OrderDetails':[(1,1,4,7),(2,1,2,7),(3,2,1,7),
                       (4,2,1,8),(5,3,1,999),(6,4,1,7)]},
      [(1,'A','Alpha','India',30,42.86),
       (3,'C','Unknown supplier','Unknown',20,28.57),
       (4,'D','Alpha','India',0,0)]
    )

def priced_products(tied=False, missing_price=False):
    rows = [(i, 'Other' if i != 20 else 'Premium shampoo', 'Hair care',
             None if missing_price and i == 20 else
             (20 if tied and i == 19 else i)) for i in range(1,21)]
    details = [(i,1,i,10,7) for i in range(1,19 if tied else 20)]
    return {'Products':rows, 'OrderDetails':details}
def sample_78():
    return priced_products(), [('Hair care',20,'Premium shampoo',20,1.0,0,10)]
def boundaries_78():
    return priced_products(tied=True), [
      ('Hair care',19,'Other',20,0.95,0,10),
      ('Hair care',20,'Premium shampoo',20,0.95,0,10)]
def null_price_counterexample_78():
    return priced_products(missing_price=True), []

def sample_79():
    return (
      {'Orders':[(1,10,'2026-01-01',4000),(2,10,'2026-01-05',3000),
                 (3,10,'2026-01-10',3000),(4,20,'2026-01-10',2000)]},
      [(10,3,'2026-01-10',9,10000)]
    )
def boundaries_79():
    return (
      {'Orders':[(1,11,'2026-01-01',6000),(2,11,'2026-01-01',5000),
                 (3,11,'2026-01-02',-5000),(4,11,'2026-01-03',5000),
                 (5,22,'2026-01-01',None),(6,22,'2026-01-11',10000),
                 (7,33,'2026-01-01',9999),(8,None,'2026-01-01',15000),
                 (9,44,None,15000)]},
      [(11,2,'2026-01-01',0,11000),
       (22,2,'2026-01-11',10,10000)]
    )

def sample_80():
    orders = [(i,i,'2026-01-01') for i in range(1,31)]
    orders += [(30+i,i,'2026-01-20') for i in range(1,7)]
    orders += [(37,99,'2026-04-15')]
    details = [(oid,oid,101 if oid < 37 else 102) for oid,_,_ in orders]
    return (
      {'Products':[(101,'Tea'),(102,'Other')], 'Orders':orders,
       'OrderDetails':details},
      [('Tea',30,6,20.0)]
    )
def boundaries_80():
    orders=[(i,i,'2026-01-01') for i in range(1,31)]
    orders += [(30+i,i,'2026-02-01') for i in range(1,8)]
    orders += [(38,1,'2026-01-01'), (39,1,'2026-04-10'),
               (40,31,'2026-05-01'), (41,99,'2026-05-15')]
    details=[(oid,oid,101 if oid != 41 else 102) for oid,_,_ in orders]
    return (
      {'Products':[(101,'Tea'),(102,'Other')], 'Orders':orders,
       'OrderDetails':details},
      [('Tea',30,7,23.33)]
    )
def null_subcategory_counterexample_80():
    orders=[(i,i,'2026-01-01') for i in range(1,31)]
    orders += [(30+i,i,'2026-01-20') for i in range(1,31)]
    orders += [(61,99,'2026-05-15')]
    details=[(oid,oid,101 if oid<=60 else 102) for oid,_,_ in orders]
    return (
      {'Products':[(101,None),(102,'Other')], 'Orders':orders,
       'OrderDetails':details},
      [(None,30,0,0.0)]  # Known NULL join mismatch: 30 real repeaters omitted.
    )

SAMPLES={77:sample_77, 78:sample_78, 79:sample_79, 80:sample_80}
BOUNDARIES={77:boundaries_77, 78:boundaries_78,
            79:boundaries_79, 80:boundaries_80}
def main():
    assert sqlite3.sqlite_version_info >= (3,39,0)
    assert blob(KEY) == KEY_SHA, 'supplied answer key source changed'
    key = KEY.read_text(encoding='utf-8')
    for number,(rel,pin) in PINS.items():
        source_file = BASE/rel
        assert blob(source_file) == pin, f'Q{number} original source changed'
        source = source_file.read_text(encoding='utf-8')
        for marker in (f'# PNP Q{number:03d}.', 'NOT SOLVED YET',
                       '### Sample input and expected output',
                       '## Schema', '## Official solution', 'Pending'):
            assert marker in source, f'Q{number} missing {marker}'
        sql = sqlite_equivalent(number,extract(key,number))
        replay(number,sql,*SAMPLES[number](),'archived illustration')
        replay(number,sql,*BOUNDARIES[number](),'independent boundary')
        if number==78:
            replay(number,sql,*null_price_counterexample_78(),
                   'NULL-priced twentieth product exclusion (conditional)')
        if number==80:
            replay(number,sql,*null_subcategory_counterexample_80(),
                   'NULL-subcategory join failure (known discrepancy)')
    print('PASS: 4 SHA-pinned question sources + supplier key, 4 illustration contracts, '
          '4 independent boundary groups, and 2 conditional counterexamples. '
          'Q080 NULL subcategory repeaters FAIL task intuition; '
          'no provider grading/native PostgreSQL/full-dataset/learner completion.')
if __name__ == '__main__':
    main()
