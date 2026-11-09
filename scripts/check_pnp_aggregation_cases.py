"""Reviewer-created SQLite aggregation edge cases linked to archived PNP questions.
These do not run official PDF SQL or award learner progress.
"""
import sqlite3


def check(label, schema, query, expected):
    db = sqlite3.connect(':memory:')
    db.executescript(schema)
    actual = db.execute(query).fetchall()
    assert actual == expected, f'{label}: {actual!r} != {expected!r}'
    print('PASS:', label)


def catalogue():
    check('P011 left-join row count vs sale-line count', '''
CREATE TABLE Products(ProductID INT);
CREATE TABLE OrderDetails(OrderDetailID INT,ProductID INT);
INSERT INTO Products VALUES (1),(2),(3);
INSERT INTO OrderDetails VALUES (10,1),(11,1),(12,2),(13,99);
''', '''SELECT COUNT(*) rows_after_join,COUNT(d.OrderDetailID) sale_lines,
 COUNT(DISTINCT p.ProductID) listed_products,
 COUNT(DISTINCT CASE WHEN d.OrderDetailID IS NOT NULL THEN p.ProductID END) sold,
 ROUND(100.0*COUNT(DISTINCT CASE WHEN d.OrderDetailID IS NOT NULL
 THEN p.ProductID END)/NULLIF(COUNT(DISTINCT p.ProductID),0),2) pct
 FROM Products p LEFT JOIN OrderDetails d ON p.ProductID=d.ProductID''',
          [(4,3,3,2,66.67)])


def brands():
    check('P047 product threshold not inflated by sales lines', '''
CREATE TABLE Products(ProductID INT,Brand TEXT,Sale_Price INT);
CREATE TABLE OrderDetails(ProductID INT,Quantity INT);
INSERT INTO Products VALUES (1,'Nova',10),(2,'Nova',20),(3,'Nova',30),
 (4,'Solo',5),(5,NULL,7),(6,NULL,8),(7,NULL,9);
INSERT INTO OrderDetails VALUES (1,2),(1,3),(2,1),(5,4);
''', '''WITH sold AS (
 SELECT ProductID,SUM(Quantity) units FROM OrderDetails GROUP BY ProductID)
 SELECT COALESCE(p.Brand,'Unbranded') brand,COUNT(p.ProductID) products_listed,
 COUNT(CASE WHEN s.ProductID IS NOT NULL THEN 1 END) products_sold,
 COALESCE(SUM(s.units),0) units_sold,
 COALESCE(SUM(s.units*p.Sale_Price),0) list_price_value
 FROM Products p LEFT JOIN sold s ON p.ProductID=s.ProductID
 GROUP BY COALESCE(p.Brand,'Unbranded') HAVING COUNT(p.ProductID)>=3
 ORDER BY list_price_value DESC,brand''',
          [('Nova',3,2,6,70),('Unbranded',3,1,4,28)])


def suppliers():
    check('P051 distinct suppliers, null-only order in denominator', '''
CREATE TABLE OrderDetails(OrderID INT,SupplierID INT);
INSERT INTO OrderDetails VALUES (10,NULL),(10,NULL),(20,1),(20,NULL),
 (30,1),(30,2),(40,1),(40,2),(40,3);
''', '''WITH per_order AS (
 SELECT OrderID,COUNT(DISTINCT SupplierID) suppliers
 FROM OrderDetails GROUP BY OrderID),
 bucketed AS (SELECT CASE WHEN suppliers=0 THEN 'No supplier recorded'
 WHEN suppliers=1 THEN 'Single supplier' WHEN suppliers=2 THEN '2 suppliers'
 ELSE '3+ suppliers' END label FROM per_order)
 SELECT label,COUNT(*),ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM per_order),2)
 FROM bucketed GROUP BY label
 ORDER BY CASE label WHEN 'No supplier recorded' THEN 0
 WHEN 'Single supplier' THEN 1 WHEN '2 suppliers' THEN 2 ELSE 3 END''',
          [('No supplier recorded',1,25.0),('Single supplier',1,25.0),
           ('2 suppliers',1,25.0),('3+ suppliers',1,25.0)])


def weighted_discounts():
    check('P054 product-average vs unit-weighted average', '''
CREATE TABLE Products(ProductID INT,Sub_Category TEXT,Market_Price INT,Sale_Price INT);
CREATE TABLE OrderDetails(ProductID INT,Quantity INT);
INSERT INTO Products VALUES (1,'Tea',100,90),(2,'Tea',100,50),
 (3,'Tea',100,80),(4,'Tea',0,0),(5,'Empty',100,90);
INSERT INTO OrderDetails VALUES (1,1),(2,2),(2,1),(4,100);
''', '''WITH units AS (SELECT ProductID,SUM(Quantity) units
 FROM OrderDetails GROUP BY ProductID),
 eligible AS (SELECT p.Sub_Category,p.ProductID,
 100.0*(p.Market_Price-p.Sale_Price)/p.Market_Price discount_pct,
 COALESCE(u.units,0) units FROM Products p
 LEFT JOIN units u ON p.ProductID=u.ProductID
 WHERE p.Market_Price>0 AND p.Sale_Price<=p.Market_Price)
 SELECT Sub_Category,COUNT(*),ROUND(AVG(discount_pct),2),SUM(units),
 ROUND(SUM(discount_pct*units)/NULLIF(SUM(units),0),2)
 FROM eligible GROUP BY Sub_Category ORDER BY Sub_Category''',
          [('Empty',1,10.0,0,None),('Tea',3,26.67,4,40.0)])


def baskets():
    check('P059 average order baskets with empty orders excluded', '''
CREATE TABLE Orders(OrderID INT,OrderDate TEXT);
CREATE TABLE OrderDetails(OrderID INT,ProductID INT,Quantity INT);
INSERT INTO Orders VALUES (1,'2025-01-01'),(2,'2025-01-02'),
 (3,'2025-02-01'),(4,'2025-02-02');
INSERT INTO OrderDetails VALUES (1,1,2),(1,2,3),(2,1,1),
 (4,3,2),(4,3,1);
''', '''WITH order_basket AS (
 SELECT o.OrderID,substr(o.OrderDate,1,7)||'-01' month,
 SUM(d.Quantity) units,COUNT(DISTINCT d.ProductID) product_count
 FROM Orders o JOIN OrderDetails d ON d.OrderID=o.OrderID
 GROUP BY o.OrderID,substr(o.OrderDate,1,7))
 SELECT month,COUNT(*),ROUND(AVG(units*1.0),2),
 ROUND(AVG(product_count*1.0),2)
 FROM order_basket GROUP BY month ORDER BY month''',
          [('2025-01-01',2,3.0,1.5),('2025-02-01',1,3.0,1.0)])


def subtotals():
    check('P084 count-threshold and weighted state/grand totals', '''
CREATE TABLE Orders(OrderID INT,State TEXT,Shipper TEXT,days INT);
INSERT INTO Orders VALUES (1,'CA','Swift',2),(2,'CA','Swift',2),
 (3,'CA','Swift',2),(4,'CA','Swift',2),(5,'CA','Swift',2),
 (6,'CA','Slow',4),(7,'NY','Swift',8);
''', '''WITH grouped AS (
 SELECT State state,Shipper shipper,'State x shipper' row_level,
 COUNT(*) n,ROUND(AVG(days*1.0),2) mean,0 sortkey FROM Orders
 GROUP BY State,Shipper
 UNION ALL
 SELECT State,'All shippers','State subtotal',COUNT(*),
 ROUND(AVG(days*1.0),2),1 FROM Orders GROUP BY State
 UNION ALL
 SELECT 'All states','All shippers','Grand total',COUNT(*),
 ROUND(AVG(days*1.0),2),2 FROM Orders)
 SELECT state,shipper,row_level,n,CASE WHEN n>=5 THEN mean END
 FROM grouped ORDER BY sortkey,state,shipper''',
          [('CA','Slow','State x shipper',1,None),
           ('CA','Swift','State x shipper',5,2.0),
           ('NY','Swift','State x shipper',1,None),
           ('CA','All shippers','State subtotal',6,2.33),
           ('NY','All shippers','State subtotal',1,None),
           ('All states','All shippers','Grand total',7,3.14)])


if __name__ == '__main__':
    catalogue()
    brands()
    suppliers()
    weighted_discounts()
    baskets()
    subtotals()
    print('PASS: six reviewer-authored aggregation regressions; no source solutions certified')
