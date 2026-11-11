#!/usr/bin/env python3
"""Read-only, source-pinned Q049–Q056 supplied-key/illustration checks.

SQLite tests use exactly extracted archived key SQL, except explicitly asserted
narrow dialect adaptations. Not original full-data, native PG, provider grading,
or new learner submissions. Original archives are never rewritten.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/'99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice'
SOURCES={
49:('9. Windowing Functions/P049. Top three products by units in each category.md','1abe60e63a3619063fc89b3c68d471d1e206da74'),
50:('3. Sorting and Grouping/P050. Customers who buy across at least ten categories.md','cdbac6cd158e97b6dea4097096f10a7fb1474577'),
51:('4. Aggregation/P051. Orders fulfilled by one supplier vs several.md','3f1379343f171b902f5d0192cd6dd871615da4e0'),
52:('4. Aggregation/P052. Where shipping time goes dispatch vs transit by shipper.md','aef86827cfe0cc05c73a38b9220b7643fcb00932'),
53:('2. Joins/P053. Thirty-day sign-up to purchase conversion by country.md','033d6e23cd28980d5a2be18cd0d5c608688e0c53'),
54:('4. Aggregation/P054. Weighted vs simple average discount by sub-category.md','5daffd10cf5c996f282b57c9949101d4badfc320'),
55:('4. Aggregation/P055. Category list-price value latest year vs previous year.md','2415c76713a73b642a0e67f2635adfa23dceffb6'),
56:('6. SubQueries/P056. Customers who ordered last year but not this year.md','d3f9054810b8c0337089b088a873d89444f1fa9b'),
}
KEY=BASE/'Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql'
KEY_SHA='7912c8e676621c513e0b635a40c6ee299404676e'

def blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def supplied_sql(n,text):
    m=re.search(rf'(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)',text)
    assert m, f'Missing supplied-key Q{n}'
    return m.group(1).strip()

def source_queries():
    assert blob(KEY)==KEY_SHA,'original PostgreSQL key drift'
    text=KEY.read_text(encoding='utf-8')
    queries={}
    for n,(rel,sha) in SOURCES.items():
        f=BASE/rel
        assert blob(f)==sha,f'P{n:03d} original file drift'
        source=f.read_text(encoding='utf-8')
        assert source.startswith(f'# PNP Q{n:03d}.')
        for marker in ('### Sample input and expected output','## Schema',
                       'NOT SOLVED YET','## My solution — SQLite\n\nPending.',
                       '## Official solution\n\nPending'):
            assert marker in source,(n,marker)
        queries[n]=supplied_sql(n,text)
        assert queries[n].startswith(('SELECT ','WITH ')),n
    return queries

def swap(q,old,new,count=1):
    assert q.count(old)==count,(old,q.count(old))
    return q.replace(old,new)

def adapt(n,q):
    if n==50:
        # Source's PG array-aggregation is emulated via a DISTINCT numeric
        # ordered rowset. This is not a claim of PG16 runtime equivalence.
        q=swap(q,"ARRAY_TO_STRING(ARRAY_AGG(DISTINCT p.CategoryID ORDER BY p.CategoryID), ', ')",
          """(SELECT GROUP_CONCAT(ordered_cat.CategoryID, ', ')
               FROM (SELECT DISTINCT p2.CategoryID AS CategoryID, o2.CustomerID AS CustomerID
                     FROM Orders o2 JOIN OrderDetails od2 ON od2.OrderID=o2.OrderID
                     JOIN Products p2 ON p2.ProductID=od2.ProductID
                     WHERE p2.CategoryID IS NOT NULL ORDER BY p2.CategoryID) AS ordered_cat
               WHERE ordered_cat.CustomerID=o.CustomerID)""")
    if n==52:
        for old,new in (
          ('o.ShipDate::date     - o.OrderDate::date','(julianday(date(o.ShipDate)) - julianday(date(o.OrderDate)))'),
          ('o.DeliveryDate::date - o.ShipDate::date','(julianday(date(o.DeliveryDate)) - julianday(date(o.ShipDate)))'),
          ('o.DeliveryDate::date - o.OrderDate::date','(julianday(date(o.DeliveryDate)) - julianday(date(o.OrderDate)))')):
            q=swap(q,old,new)
    if n==53:
        q=swap(q,'fo.first_order_date::date - c.DateEntered::date',
               '(julianday(date(fo.first_order_date)) - julianday(date(c.DateEntered)))',2)
    if n in (55,56):
        q=swap(q,"DATE_TRUNC('year', MAX(o.OrderDate))::date","date(MAX(o.OrderDate), 'start of year')")
        q=q.replace("a.latest_year_start - INTERVAL '1 year'","date(a.latest_year_start, '-1 year')")
        q=q.replace("a.latest_year_start + INTERVAL '1 year'","date(a.latest_year_start, '+1 year')")
    assert '::' not in q and 'DATE_TRUNC(' not in q and "INTERVAL '" not in q,n
    return q

# Sample inputs/expected values below were independently transcribed from
# the immutable question Markdown. Additive fixtures are auditor-synthetic.
CASES={
49:(
 ['Category(CategoryID INT,CategoryName TEXT)','Products(ProductID INT,Product TEXT,CategoryID INT)','OrderDetails(OrderDetailID INT,ProductID INT,Quantity INT)'],
 {'Category':[(1,'Drinks'),(2,'Snacks')],'Products':[(1,'Tea',1),(2,'Coffee',1),(3,'Juice',1),(4,'Water',1),(5,'Cookie',2)],'OrderDetails':[(11,1,10),(12,2,8),(13,3,8),(14,4,1),(15,5,2)]},
 [('Drinks',1,1,'Tea',10),('Drinks',2,2,'Coffee',8),('Drinks',2,3,'Juice',8),('Drinks',3,4,'Water',1),('Snacks',1,5,'Cookie',2)],
 {'Products':[(6,'Orphan',99),(7,'Green tea',1),(8,'Unsold',2),(9,'NullCat',None)],'OrderDetails':[(16,6,7),(17,7,8),(18,9,1),(19,1,1)]},
 [('Drinks',1,1,'Tea',11),('Drinks',2,2,'Coffee',8),('Drinks',2,3,'Juice',8),('Drinks',2,7,'Green tea',8),('Drinks',3,4,'Water',1),('Snacks',1,5,'Cookie',2),('Unmapped',1,6,'Orphan',7),('Unmapped',1,9,'NullCat',1)]
),
50:(
 ['Products(ProductID INT,CategoryID INT)','Orders(OrderID INT,CustomerID INT)','OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT)'],
 {'Products':[(i,i) for i in range(1,11)],'Orders':[(100,1)],'OrderDetails':[(i,100,i) for i in range(1,11)]},
 [(1,10,'1, 2, 3, 4, 5, 6, 7, 8, 9, 10',1)],
 {'Products':[(11,11),(12,None),(13,2)],'Orders':[(101,1),(102,2)],'OrderDetails':[(11,101,11),(12,101,12),(13,101,13),(14,102,1),(15,102,2),(16,102,11),(17,101,1)]},
 [(1,11,'1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11',2)]
),
51:(
 ['OrderDetails(OrderDetailID INT,OrderID INT,SupplierID INT)'],
 {'OrderDetails':[(1,10,None),(2,20,1),(3,30,1),(4,30,2),(5,40,1),(6,40,2),(7,40,3)]},
 [('No supplier recorded',1,25),('Single supplier',1,25),('2 suppliers',1,25),('3+ suppliers',1,25)],
 {'OrderDetails':[(8,50,None),(9,50,5),(10,60,2),(11,60,2),(12,70,1),(13,70,2),(14,70,3),(15,70,4)]},
 [('No supplier recorded',1,round(100/7,2)),('Single supplier',3,round(300/7,2)),('2 suppliers',1,round(100/7,2)),('3+ suppliers',2,round(200/7,2))]
),
52:(
 ['Shippers(ShipperID INT,CompanyName TEXT)','Orders(OrderID INT,ShipperID INT,OrderDate TEXT,ShipDate TEXT,DeliveryDate TEXT)'],
 {'Shippers':[(1,'FastShip'),(2,'QuickShip')],'Orders':[(1,1,'2025-01-01','2025-01-03','2025-01-05'),(2,1,'2025-01-02',None,None),(3,2,'2025-01-01','2025-01-02','2025-01-03')]},
 [('FastShip',1,2,2,4,1),('QuickShip',1,1,1,2,0)],
 {'Orders':[(4,1,'2025-01-01','2025-01-01','2025-01-01'),(5,2,'2025-02-04','2025-02-03','2025-02-05'),(6,None,'2025-03-01','2025-03-02','2025-03-07'),(7,99,'2025-01-01','2025-01-02',None)]},
 [('Unknown shipper',1,1,5,6,1),('FastShip',2,1,1,2,1),('QuickShip',1,1,1,2,1)]
),
53:(
 ['Customers(CustomerID INT,Country TEXT,DateEntered TEXT)','Orders(OrderID INT,CustomerID INT,OrderDate TEXT)'],
 {'Customers':[(1,'India','2025-01-01'),(2,'India','2025-01-01'),(3,'USA','2025-01-01')],'Orders':[(10,1,'2025-01-10'),(11,3,'2025-02-05')]},
 [('USA',1,0,0),('India',2,1,50)],
 {'Customers':[(4,'India','2025-01-01'),(5,' usa ','2025-01-01'),(6,None,'2025-01-01'),(7,'India','2025-01-01')],'Orders':[(12,4,'2025-01-31'),(13,4,'2025-02-05'),(14,5,'2025-01-31'),(15,6,'2024-12-31'),(16,7,'2025-01-01')]},
 [('USA',1,0,0),('Unknown',1,0,0),('India',4,3,75),('usa',1,1,100)]
),
54:(
 ['Products(ProductID INT,Sub_Category TEXT,Market_Price REAL,Sale_Price REAL)','OrderDetails(OrderDetailID INT,ProductID INT,Quantity INT)'],
 {'Products':[(1,'Tea',100,90),(2,'Tea',100,50)],'OrderDetails':[(11,1,1),(12,2,3)]},
 [('Tea',2,30,4,40)],
 {'Products':[(3,'Tea',100,200),(4,'Coffee',200,100),(5,'Coffee',50,50),(6,None,100,75),(7,'Tea',0,0),(8,'Tea',100,80)],'OrderDetails':[(13,4,0),(14,6,2),(15,8,0)]},
 [('Tea',3,round(80/3,2),4,40),('Unknown',1,25,2,25),('Coffee',2,25,0,None)]
),
55:(
 ['Category(CategoryID INT,CategoryName TEXT)','Products(ProductID INT,CategoryID INT,Sale_Price REAL)','Orders(OrderID INT,OrderDate TEXT)','OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT,Quantity INT)'],
 {'Category':[(1,'Drinks'),(2,'Snacks')],'Products':[(10,1,10),(20,2,5)],'Orders':[(100,'2024-01-01'),(101,'2025-01-01')],'OrderDetails':[(1,100,10,2),(2,101,10,3),(3,101,20,2)]},
 [('Drinks',20,30,50),('Snacks',0,10,None)],
 {'Products':[(30,99,3)],'Orders':[(102,'2026-02-01'),(103,'2026-03-01')],'OrderDetails':[(4,102,10,4),(5,103,30,2)]},
 [('Drinks',30,40,round(100/3,2)),('Snacks',10,0,-100),('Unmapped',0,6,None)]
),
56:(
 ['Customers(CustomerID INT,FirstName TEXT,LastName TEXT)','Orders(OrderID INT,CustomerID INT,OrderDate TEXT)'],
 {'Customers':[(1,'Asha','Rao'),(2,'Ben','Das')],'Orders':[(10,1,'2024-03-01'),(11,1,'2024-12-01'),(12,2,'2024-05-01'),(13,2,'2025-01-01')]},
 [(1,'Asha Rao','2024-12-01',2)],
 {'Orders':[(14,3,'2025-06-01'),(15,4,'2026-01-01'),(16,2,'2024-06-01'),(17,5,None)]},
 [(3,'Unknown customer','2025-06-01',1),(2,'Ben Das','2025-01-01',1)]
)
}

def insert(db,name,rows):
    if rows: db.executemany('INSERT INTO '+name+' VALUES('+','.join('?' for _ in rows[0])+')',rows)

def exercise(n,query):
    ddl,source,expected,edge,edge_expected=CASES[n]
    db=sqlite3.connect(':memory:')
    db.create_function('CONCAT_WS',-1,lambda separator,*parts: separator.join(str(p) for p in parts if p is not None))
    try:
        for d in ddl: db.execute('CREATE TABLE '+d)
        for name,rows in source.items(): insert(db,name,rows)
        observed=db.execute(query).fetchall()
        assert observed==expected,f'P{n:03d} original illustrative contract: {observed!r} vs {expected!r}'
        for name,rows in edge.items(): insert(db,name,rows)
        observed=db.execute(query).fetchall()
        assert observed==edge_expected,f'P{n:03d} independent boundary contract: {observed!r} vs {edge_expected!r}'
    finally: db.close()

def conditional_divergences(executable):
    # A source-label/coverage difference is a documented divergence, NOT a PASS.
    db=sqlite3.connect(':memory:')
    for definition in ('Category(CategoryID INT,CategoryName TEXT)',
                       'Products(ProductID INT,CategoryID INT,Sale_Price REAL)',
                       'Orders(OrderID INT,OrderDate TEXT)',
                       'OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT,Quantity INT)'):
        db.execute('CREATE TABLE '+definition)
    db.execute("INSERT INTO Category VALUES(7,'Empty category')")
    db.execute("INSERT INTO Orders VALUES(101,'2025-01-01')")
    assert db.execute(executable[55]).fetchall()==[], 'Q055 empty category diagnostic drift'
    db.close()

    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE Shippers(ShipperID INT, CompanyName TEXT)')
    db.execute('CREATE TABLE Orders(OrderID INT,ShipperID INT,OrderDate TEXT,ShipDate TEXT,DeliveryDate TEXT)')
    db.executemany('INSERT INTO Shippers VALUES(?,?)',[(1,'Same'),(2,'Same')])
    db.executemany('INSERT INTO Orders VALUES(?,?,?,?,?)',[
        (1,1,'2025-01-01','2025-01-02','2025-01-03'),
        (2,2,'2025-01-01','2025-01-02','2025-01-03')])
    assert db.execute(executable[52]).fetchall()==[('Same',2,1,1,2,0)],'Q052 duplicate-name diagnostic drift'
    db.close()

def main():
    originals=source_queries()
    executable={n:adapt(n,q) for n,q in originals.items()}
    for n,q in executable.items(): exercise(n,q)
    conditional_divergences(executable)
    print('PASS: 8 source pins, key blob, 8 illustrative SQL samples and 8 synthetic boundaries; Q052/Q055 known conditional divergences reproduced; no official grade or learner solve.')

if __name__=='__main__': main()
