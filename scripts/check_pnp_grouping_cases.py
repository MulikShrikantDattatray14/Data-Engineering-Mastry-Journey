"""Independent grouping edge-case fixtures aligned to 13 PNP source question texts.
Only synthetic reviewer data; no learner answers or official PDFs executed.
"""
import sqlite3

def check(name, schema, sql, expected):
    db=sqlite3.connect(':memory:')
    db.executescript(schema)
    actual=db.execute(sql).fetchall()
    assert actual==expected,(name,actual,expected)
    print('PASS:',name)

def test_flags():
    check('P009 raw NULL flag groups', """
CREATE TABLE Category(Active INTEGER);
CREATE TABLE Payments(Allowed TEXT);
INSERT INTO Category VALUES (1),(1),(0),(NULL);
INSERT INTO Payments VALUES ('Y'),('N'),('N'),(NULL);
""","""SELECT source,raw,cnt FROM (
 SELECT 'Category' source,CAST(Active AS TEXT) raw,COUNT(*) cnt FROM Category GROUP BY Active
 UNION ALL
 SELECT 'Payments',CAST(Allowed AS TEXT),COUNT(*) FROM Payments GROUP BY Allowed)
 ORDER BY source,raw IS NOT NULL,raw""",
 [('Category',None,1),('Category','0',1),('Category','1',2),
  ('Payments',None,1),('Payments','N',2),('Payments','Y',1)])

def test_buyers():
    check('A018 distinct buyers after excluding canceled',"""
CREATE TABLE orders(order_date TEXT,cust_id INTEGER,status TEXT);
INSERT INTO orders VALUES ('2026-01-03',10,'completed'),('2026-01-04',10,'completed'),
 ('2026-01-05',20,'cancelled'),('2026-01-06',NULL,'completed'),
 ('2026-02-01',20,'completed');""","""
SELECT substr(order_date,1,7),COUNT(DISTINCT cust_id) FROM orders
WHERE lower(status)<>'cancelled' GROUP BY substr(order_date,1,7) ORDER BY 1""",
 [('2026-01',1),('2026-02',1)])

def test_distinct_product_buyers():
    db=sqlite3.connect(':memory:')
    db.executescript('CREATE TABLE orders(order_id INTEGER,cust_id INTEGER);'
                     'CREATE TABLE order_items(order_id INTEGER,product_id INTEGER);')
    db.executemany('INSERT INTO orders VALUES (?,?)',[(i,i) for i in range(1,12)]+[(12,1),(13,1)])
    db.executemany('INSERT INTO order_items VALUES (?,?)',
                   [(i,101) for i in range(1,14)]+[(i,202) for i in range(1,11)]+[(12,202)])
    actual=db.execute("""SELECT i.product_id,COUNT(DISTINCT o.cust_id)
       FROM order_items i JOIN orders o ON i.order_id=o.order_id
       GROUP BY i.product_id HAVING COUNT(DISTINCT o.cust_id)>10
       ORDER BY i.product_id""").fetchall()
    assert actual==[(101,11)],actual
    print('PASS: A039 repeated orders do not inflate unique people')

def test_months():
    check('P014 observed 2025 months and timestamp boundaries',"""
CREATE TABLE Orders(OrderDate TEXT,Total_Order_Amount INTEGER);
INSERT INTO Orders VALUES ('2024-12-31 23:59',900),('2025-01-01',100),
 ('2025-01-31 23:59',50),('2025-03-01',200),('2026-01-01',300);""","""
SELECT substr(OrderDate,1,7)||'-01',COUNT(*),SUM(Total_Order_Amount)
FROM Orders WHERE OrderDate>='2025-01-01' AND OrderDate<'2026-01-01'
GROUP BY substr(OrderDate,1,7) ORDER BY 1""",
 [('2025-01-01',2,150),('2025-03-01',1,200)])

def test_fifth_ties():
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE Orders(CustomerID INTEGER)')
    db.executemany('INSERT INTO Orders VALUES (?)',[(cid,) for cid,cnt
         in enumerate([8,7,7,6,5,5,4],start=1) for _ in range(cnt)])
    q="""WITH counted AS (SELECT CustomerID,COUNT(*) n FROM Orders GROUP BY CustomerID),
 ranked AS (SELECT CustomerID,n,RANK() OVER(ORDER BY n DESC) place FROM counted)
 SELECT CustomerID,n FROM ranked WHERE place<=5 ORDER BY n DESC,CustomerID"""
    actual=db.execute(q).fetchall()
    assert actual==[(1,8),(2,7),(3,7),(4,6),(5,5),(6,5)],actual
    dense=db.execute(q.replace('RANK() OVER','DENSE_RANK() OVER')).fetchall()
    assert dense!=actual and (7,4) in dense,dense
    print('PASS: P021 fifth position ties differ from DENSE_RANK')

def test_line_counts():
    check('P022 lines differ from distinct products and quantities',"""
CREATE TABLE OrderDetails(OrderID INTEGER,ProductID INTEGER,Quantity INTEGER);
INSERT INTO OrderDetails VALUES (10,1,2),(10,2,1),(10,3,1),(10,4,1),
 (10,5,1),(10,6,1),(10,7,1),(10,8,1),(10,1,2),
 (11,1,1),(11,2,1),(11,3,1),(11,4,1),(11,5,1),(11,6,1),(11,7,1),(11,8,1);
""","""SELECT OrderID,COUNT(*) lines,COUNT(DISTINCT ProductID),SUM(Quantity)
FROM OrderDetails GROUP BY OrderID HAVING COUNT(*)>8 ORDER BY lines DESC,OrderID""",
 [(10,9,8,11)])

def test_quarters():
    check('P025 Q2 on April 1 and NULL group last',"""
CREATE TABLE Customers(DateEntered TEXT);
INSERT INTO Customers VALUES ('2025-01-01'),('2025-03-31'),('2025-04-01'),
 ('2025-12-31'),('2026-01-01'),(NULL),(NULL);""","""
WITH signed AS (SELECT CAST(strftime('%Y',DateEntered) AS INTEGER) yr,
 (CAST(strftime('%m',DateEntered) AS INTEGER)-1)/3+1 q FROM Customers)
SELECT yr,q,COUNT(*) FROM signed GROUP BY yr,q ORDER BY yr IS NULL,yr,q""",
 [(2025,1,2),(2025,2,1),(2025,4,1),(2026,1,1),(None,None,2)])

def test_category_list():
    check('P050 numeric category list, repeated line and distinct orders',"""
CREATE TABLE Products(ProductID INTEGER,CategoryID INTEGER);
CREATE TABLE Orders(OrderID INTEGER,CustomerID INTEGER);
CREATE TABLE OrderDetails(OrderID INTEGER,ProductID INTEGER);
INSERT INTO Products VALUES (1,1),(2,2),(3,3),(4,4),(5,5),
 (6,6),(7,7),(8,8),(9,9),(10,10);
INSERT INTO Orders VALUES (100,1),(101,1),(102,2);
INSERT INTO OrderDetails VALUES (100,10),(100,9),(100,8),(100,7),
 (100,6),(100,5),(100,4),(100,3),(100,2),(100,1),(100,1),
 (101,10),(102,1);""","""
WITH owned AS (SELECT DISTINCT o.CustomerID,p.CategoryID FROM Orders o
 JOIN OrderDetails d ON d.OrderID=o.OrderID JOIN Products p ON p.ProductID=d.ProductID
 WHERE p.CategoryID IS NOT NULL),
 summary AS (SELECT CustomerID,COUNT(*) n FROM owned GROUP BY CustomerID)
SELECT s.CustomerID,s.n,
 (SELECT group_concat(CAST(CategoryID AS TEXT),', ') FROM
    (SELECT CategoryID FROM owned x WHERE x.CustomerID=s.CustomerID ORDER BY CategoryID)),
 (SELECT COUNT(DISTINCT o.OrderID) FROM Orders o JOIN OrderDetails d
   ON d.OrderID=o.OrderID WHERE o.CustomerID=s.CustomerID)
FROM summary s WHERE s.n>=10 ORDER BY s.CustomerID""",
 [(1,10,'1, 2, 3, 4, 5, 6, 7, 8, 9, 10',2)])

if __name__=='__main__':
    test_flags()
    test_buyers()
    test_distinct_product_buyers()
    test_months()
    test_fifth_ties()
    test_line_counts()
    test_quarters()
    test_category_list()
    print('PASS: eight source-aligned independent grouping regressions')
