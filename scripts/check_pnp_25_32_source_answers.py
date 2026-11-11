#!/usr/bin/env python3
"""Bounded read-only audit of PNP Q025-Q032 preserved statements and supplied key.

Evidence tiers: statement/hash inspected, key provenance, exact historical Q026
learner replay, translated PostgreSQL-to-SQLite illustrative checks, independent
synthetic boundaries. No provider grades, original dataset, or learner credit.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    '99. Reference Materials/Original Mastery Snapshot/'
    '1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice'
)
FILES = {
    25: ('3. Sorting and Grouping/P025. Customer sign-ups by year and quarter.md', '83aa4cc8662789b80f95fc9b64531d226a95ec80'),
    26: ('2. Joins/P026. List-price value by category.md', '52e88f44276743481672cb887dae0c37b1403f2a'),
    27: ('2. Joins/P027. Average order value by customer state.md', '2b9a2a20334e9d24401c8720dc1b0ecbe723e985'),
    28: ('6. SubQueries/P028. Payment mix share of orders and value.md', 'cfd74c395f45c091f355c76b8f6f6d34b202d737'),
    29: ('2. Joins/P029. Order value and units by shipper without double counting.md', '1de7e98ef33506a617e4f7483e1c70acbd1b6f67'),
    30: ('5. CTEs/P030. Repeat versus one-time customers.md', '7a978d67c2b3fe71ec7b5645c7465f34034806a5'),
    31: ('6. SubQueries/P031. Customers who spend more than the average customer.md', '304fea2577f697fbc7409ed229c8547a16e8cc9c'),
    32: ('6. SubQueries/P032. Products priced above their category average.md', '170580e306f77c61cc209dec055388a53684016c'),
}
KEY = BASE / 'Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql'
KEY_BLOB = '7912c8e676621c513e0b635a40c6ee299404676e'

def blobsha(path):
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def key_sql(text, n):
    match = re.search(rf'(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)', text)
    assert match, f'Q{n} missing from supplied key'
    return match.group(1).strip()

def learner_sql(text):
    section = text.split('## My solution — SQLite', 1)[1].split('### Step-by-step', 1)[0]
    match = re.search(r'(?ms)^' + '\x60'*3 + r'sql\s*\n(.*?)\n' + '\x60'*3, section)
    assert match, 'Historically recorded Q026 SQLite solution absent'
    return match.group(1).strip()

def provenance():
    assert blobsha(KEY) == KEY_BLOB, 'Supplied answer-key archive was modified'
    key_text = KEY.read_text(encoding='utf8')
    records, queries = {}, {}
    for n, (relative, source_hash) in FILES.items():
        path = BASE / relative
        assert blobsha(path) == source_hash, f'Q{n:03d} archive SHA changed'
        source = path.read_text(encoding='utf8')
        assert source.startswith(f'# PNP Q{n:03d}.')
        assert '### Sample input and expected output' in source and '## Schema' in source
        assert '## Official solution' in source and '## My solution — SQLite' in source
        if n == 26:
            assert 'Solved (recorded)' in source
            found = re.search(r'(?ms)^## Official solution.*?^' + '\x60'*3 + r'sql\s*\n(.*?)\n' + '\x60'*3, source)
            assert found and ' '.join(found.group(1).split()) == ' '.join(key_sql(key_text, n).split()), 'Q026 archived official excerpt differs from supplied key'
            assert 'FULL OUTER JOIN Category' in learner_sql(source)
        else:
            assert 'NOT SOLVED YET' in source
            assert '## My solution — SQLite\n\nPending.' in source
            assert '## Official solution\n\nPending' in source
        records[n] = source
        queries[n] = key_sql(key_text, n)
        assert queries[n].upper().startswith(('SELECT ', 'WITH ')), n
    return records, queries

def to_sqlite(n, sql):
    """Narrow, asserted PostgreSQL syntax adaptations, never native PG proof."""
    if n == 25:
        year = "CAST(strftime('%Y', c.DateEntered) AS INTEGER)"
        quarter = "CAST(((CAST(strftime('%m', c.DateEntered) AS INTEGER)-1)/3+1) AS INTEGER)"
        sql, a = re.subn(r'EXTRACT\(YEAR FROM c\.DateEntered\)::int', lambda _:year, sql)
        sql, b = re.subn(r'EXTRACT\(QUARTER FROM c\.DateEntered\)::int', lambda _:quarter, sql)
        assert (a, b) == (2, 2), 'Q025 key changed: revisit date translation'
    return sql

def connect(*ddl):
    c = sqlite3.connect(':memory:')
    # Q031 PostgreSQL CONCAT_WS: NULL items omitted; no claim of Unicode parity.
    c.create_function('CONCAT_WS', -1, lambda sep, *items: None if sep is None else str(sep).join(str(v) for v in items if v is not None))
    for q in ddl:
        c.execute(q)
    return c

def expect(c, sql, rows, description):
    actual = c.execute(sql).fetchall()
    assert actual == rows, f'{description}: got {actual!r}, expected {rows!r}'

def test_samples_and_boundaries(records, queries):
    # P025: two sign-ups in Q1, one Q2, one NULL; extra December and leap day.
    c=connect('CREATE TABLE Customers(CustomerID INT,DateEntered TEXT)')
    c.executemany('INSERT INTO Customers VALUES(?,?)',[(1,'2025-01-15'),(2,'2025-03-01'),(3,'2025-04-01'),(4,None)])
    q=to_sqlite(25,queries[25])
    expect(c,q,[(2025,1,2),(2025,2,1),(None,None,1)],'P025 illustrative grouping')
    c.executemany('INSERT INTO Customers VALUES(?,?)',[(5,'2024-02-29'),(6,'2025-12-31'),(7,None)])
    expect(c,q,[(2024,1,1),(2025,1,2),(2025,2,1),(2025,4,1),(None,None,2)],'P025 leap/day/NULL quarter boundary')
    c.close()

    # P026: exact historical learner SQLite FULL JOIN includes unsold Category;
    # unchanged supplied key omits the unsold category, even though task says 'every'.
    c=connect('CREATE TABLE Category(CategoryID INT,CategoryName TEXT)',
              'CREATE TABLE Products(ProductID INT,CategoryID INT,Sale_Price REAL)',
              'CREATE TABLE OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT,Quantity INT)')
    c.executemany('INSERT INTO Category VALUES(?,?)',[(1,'Drinks'),(2,'Snacks'),(3,'Stationery')])
    c.executemany('INSERT INTO Products VALUES(?,?,?)',[(10,1,10),(11,1,8),(20,2,5),(30,99,7)])
    c.executemany('INSERT INTO OrderDetails VALUES(?,?,?,?)',[(1,100,10,2),(2,100,11,1),(3,100,20,1),(4,101,30,3),(5,102,999,4)])
    learner=learner_sql(records[26]); key=queries[26]
    expect(c,learner,[('Drinks',1,3,28.0),('Unmapped',1,3,21.0),('Snacks',1,1,5.0),('Stationery',0,0,0),('Unknown product',1,4,None)],'P026 historical learner exact illustrative output')
    expect(c,key,[('Drinks',1,3,28.0),('Unmapped',1,3,21.0),('Snacks',1,1,5.0),('Unknown product',1,4,None)],'P026 key excludes unsold Category')
    c.execute("INSERT INTO Category VALUES(4,'Empty Category')")
    rows=c.execute(learner).fetchall()
    assert ('Empty Category',0,0,0) in rows and ('Empty Category',0,0,0) not in c.execute(key).fetchall(),'P026 distinct real unsold category'
    c.close()

    # P027: threshold 10, COUNT(DISTINCT CustomerID), NULL amount excluded from AVG.
    c=connect('CREATE TABLE Customers(CustomerID INT, State TEXT)',
              'CREATE TABLE Orders(OrderID INT,CustomerID INT,Total_Order_Amount REAL)')
    c.executemany('INSERT INTO Customers VALUES(?,?)',[(1,'Karnataka'),(2,'Karnataka'),(3,'   ')])
    c.executemany('INSERT INTO Orders VALUES(?,?,?)',[(i,1 if i<=5 else 2,100) for i in range(1,11)])
    expect(c,queries[27],[('Karnataka',2,10,1000.0,100.0)],'P027 illustrative 10-order threshold')
    c.executemany('INSERT INTO Orders VALUES(?,?,?)',[(i,3 if i<=15 else 999,(100 if i<20 else None)) for i in range(11,21)])
    expect(c,queries[27],[('Karnataka',2,10,1000.0,100.0),('Unknown',2,10,900.0,100.0)],'P027 unknown/NULL and 10-order synthetic')
    c.close()

    # P028: source sample order and value shares; separate Unknown/empty denominator.
    c=connect('CREATE TABLE Payments(PaymentID INT,PaymentType TEXT)',
              'CREATE TABLE Orders(OrderID INT,PaymentID INT,Total_Order_Amount REAL)')
    c.executemany('INSERT INTO Payments VALUES(?,?)',[(1,'UPI'),(2,'Card')])
    c.executemany('INSERT INTO Orders VALUES(?,?,?)',[(10,1,100),(11,1,200),(12,2,300)])
    expect(c,queries[28],[('UPI',2,66.67,300.0,50.0),('Card',1,33.33,300.0,50.0)],'P028 illustrative percentages')
    c.executemany('INSERT INTO Orders VALUES(?,?,?)',[(13,None,0),(14,999,0)])
    expect(c,queries[28],[('UPI',2,40.0,300.0,50.0),('Unknown',2,40.0,0.0,0.0),('Card',1,20.0,300.0,50.0)],'P028 unknown ids / denomination')
    c.execute('DELETE FROM Orders')
    expect(c,queries[28],[],'P028 empty order universe')
    c.close()

    # P029: preaggregate line-level units BEFORE header-level value to avoid fanout.
    c=connect('CREATE TABLE Shippers(ShipperID INT,CompanyName TEXT)',
              'CREATE TABLE Orders(OrderID INT,ShipperID INT,Total_Order_Amount REAL)',
              'CREATE TABLE OrderDetails(OrderDetailID INT,OrderID INT,Quantity INT)')
    c.executemany('INSERT INTO Shippers VALUES(?,?)',[(1,'FastShip'),(2,'SlowShip')])
    c.executemany('INSERT INTO Orders VALUES(?,?,?)',[(10,1,100),(11,1,200),(12,2,50)])
    c.executemany('INSERT INTO OrderDetails VALUES(?,?,?)',[(1,10,2),(2,10,3),(3,11,4),(4,12,1)])
    expect(c,queries[29],[('FastShip',2,300.0,9),('SlowShip',1,50.0,1)],'P029 illustrative fanout-safe value')
    c.execute('INSERT INTO Orders VALUES(13,999,15)')
    c.execute('INSERT INTO Orders VALUES(14,NULL,25)')
    expect(c,queries[29],[('FastShip',2,300.0,9),('SlowShip',1,50.0,1),('Unknown shipper',2,40.0,0)],'P029 orphan/no-line/NULL shipper')
    c.close()

    # P030: ordering customers only; NULL CustomerID dropped explicitly by key.
    c=connect('CREATE TABLE Orders(OrderID INT,CustomerID INT)')
    c.executemany('INSERT INTO Orders VALUES(?,?)',[(1,10),(2,20),(3,20),(4,30)])
    expect(c,queries[30],[('One-time',2,66.67),('Repeat',1,33.33)],'P030 illustrative distribution')
    c.executemany('INSERT INTO Orders VALUES(?,?)',[(5,None),(6,None),(7,30),(8,40)])
    expect(c,queries[30],[('One-time',2,50.0),('Repeat',2,50.0)],'P030 NULL ID exclusions and repeat transition')
    c.close()

    # P031: true customer-grain AVG, not order-grain; orphan id included.
    c=connect('CREATE TABLE Customers(CustomerID INT,FirstName TEXT,LastName TEXT)',
              'CREATE TABLE Orders(OrderID INT,CustomerID INT,Total_Order_Amount REAL)')
    c.executemany('INSERT INTO Customers VALUES(?,?,?)',[(1,'Asha','Rao'),(2,'Ben','Das'),(3,'Cia','Sen')])
    c.executemany('INSERT INTO Orders VALUES(?,?,?)',[(10,1,300),(11,2,100),(12,3,200)])
    expect(c,queries[31],[(1,'Asha Rao',300.0,200.0,50.0)],'P031 illustrative per-customer benchmark')
    c.execute('INSERT INTO Orders VALUES(13,999,700)')
    expect(c,queries[31],[(999,'Unknown customer',700.0,325.0,115.38)],'P031 orphan/benchmark recalc')
    c.close()

    # P032: correlated AVG within Category 5009 only, strict comparison.
    c=connect('CREATE TABLE Products(ProductID INT,Product TEXT,CategoryID INT,Sale_Price REAL)')
    c.executemany('INSERT INTO Products VALUES(?,?,?,?)',[(1,'Tea',5009,100),(2,'Coffee',5009,200),(3,'Juice',5009,300),(4,'Bread',5010,500)])
    expect(c,queries[32],[(3,'Juice',5009,300.0,200.0)],'P032 illustrative correlation')
    c.executemany('INSERT INTO Products VALUES(?,?,?,?)',[(5,'Water',5009,None),(6,'Luxury',5010,10000)])
    expect(c,queries[32],[(3,'Juice',5009,300.0,200.0)],'P032 NULL price, strict >, other category')
    c.close()
    print('PASS: 8 immutable source records and supplied key; Q026 exact historical learner SQL; 8 illustrative and 8 synthetic bounded groups. No provider grades or new learner solves.')

def main():
    records,queries=provenance()
    test_samples_and_boundaries(records,queries)

if __name__ == '__main__':
    main()
