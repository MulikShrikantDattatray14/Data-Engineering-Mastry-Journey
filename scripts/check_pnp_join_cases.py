"""Auditor-only SQLite fixtures grounded in PNP join-question source texts.

These are illustrative edge-case regressions, not answers to the user's
unsolved questions or execution of the original PDF's official SQL.
"""
import sqlite3


def check(name, actual, expected):
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")
    print("PASS:", name)


def test_full_join_emulation():
    db = sqlite3.connect(":memory:")
    db.executescript("""CREATE TABLE customers(cust_id INTEGER PRIMARY KEY,cust_name TEXT);
    CREATE TABLE orders(order_id INTEGER PRIMARY KEY,cust_id INTEGER);
    INSERT INTO customers VALUES (1,'Asha'),(2,'Mira');
    INSERT INTO orders VALUES (10,1),(13,1),(11,3),(12,NULL);""")
    rows = db.execute("""WITH combined AS (
      SELECT c.cust_id,c.cust_name,o.order_id FROM customers c
      LEFT JOIN orders o ON c.cust_id=o.cust_id
      UNION ALL
      SELECT o.cust_id,c.cust_name,o.order_id FROM orders o
      LEFT JOIN customers c ON o.cust_id=c.cust_id
      WHERE c.cust_id IS NULL)
    SELECT cust_id,cust_name,order_id FROM combined
    ORDER BY COALESCE(order_id,0),COALESCE(cust_id,0)""").fetchall()
    check("A006 full-join unmatched customers, orphan/NULL orders and multiorder rows",
          rows, [(2,'Mira',None),(1,'Asha',10),(3,None,11),
                 (None,None,12),(1,'Asha',13)])


def test_shipper_grain():
    db = sqlite3.connect(":memory:")
    db.executescript("""CREATE TABLE shippers(shipper_id INTEGER PRIMARY KEY,name TEXT);
    CREATE TABLE orders(order_id INTEGER PRIMARY KEY,shipper_id INTEGER,amount INTEGER);
    CREATE TABLE lines(line_id INTEGER,order_id INTEGER,qty INTEGER);
    INSERT INTO shippers VALUES (1,'FastShip'),(2,'SlowShip');
    INSERT INTO orders VALUES (10,1,100),(11,1,200),(12,2,50),(13,99,40);
    INSERT INTO lines VALUES (1,10,2),(2,10,3),(3,11,4),(4,12,1);""")
    wrong = db.execute("""SELECT SUM(o.amount) FROM orders o
       LEFT JOIN lines l ON l.order_id=o.order_id
       WHERE o.shipper_id=1""").fetchone()[0]
    rows = db.execute("""WITH line_totals AS (
         SELECT order_id,SUM(qty) units FROM lines GROUP BY order_id)
      SELECT COALESCE(s.name,'Unknown shipper'),COUNT(o.order_id),
        SUM(o.amount),SUM(COALESCE(lt.units,0))
      FROM orders o LEFT JOIN shippers s ON s.shipper_id=o.shipper_id
      LEFT JOIN line_totals lt ON lt.order_id=o.order_id
      GROUP BY COALESCE(s.name,'Unknown shipper')
      ORDER BY SUM(o.amount) DESC""").fetchall()
    check("P029 naive line join inflates money", wrong, 400)
    check("P029 preaggregate lines at order grain; unknown shipper",
          rows, [('FastShip',2,300,9),('SlowShip',1,50,1),
                 ('Unknown shipper',1,40,0)])


def test_category_status():
    db = sqlite3.connect(":memory:")
    db.executescript("""CREATE TABLE category(id INTEGER,name TEXT);
    CREATE TABLE products(id INTEGER,category_id INTEGER);
    CREATE TABLE lines(product_id INTEGER,qty INTEGER);
    INSERT INTO category VALUES (1,'Empty'),(2,'Unsold'),(3,'Mixed'),(4,'All sold');
    INSERT INTO products VALUES (10,2),(20,3),(21,3),(30,4);
    INSERT INTO lines VALUES (20,2),(20,1),(30,3);""")
    rows = db.execute("""WITH item_totals AS (
        SELECT product_id,SUM(qty) units FROM lines GROUP BY product_id),
      by_cat AS (SELECT c.id,c.name,COUNT(p.id) product_count,
          SUM(CASE WHEN it.product_id IS NOT NULL THEN 1 ELSE 0 END) products_sold,
          COALESCE(SUM(it.units),0) units_sold
        FROM category c LEFT JOIN products p ON p.category_id=c.id
        LEFT JOIN item_totals it ON it.product_id=p.id
        GROUP BY c.id,c.name)
      SELECT id,product_count,products_sold,units_sold,
       CASE WHEN product_count=0 THEN 'No products'
            WHEN products_sold=0 THEN 'Products but no sales'
            WHEN products_sold<product_count THEN 'Some products unsold'
            ELSE 'All products sold' END status
       FROM by_cat ORDER BY id""").fetchall()
    check("P039 empty/unsold/partial/full, multiple line rows",
          rows, [(1,0,0,0,'No products'),(2,1,0,0,'Products but no sales'),
                 (3,2,1,3,'Some products unsold'),(4,1,1,3,'All products sold')])


def test_pair_counts():
    db = sqlite3.connect(":memory:")
    db.executescript("""CREATE TABLE products(id INTEGER,subcategory TEXT);
    CREATE TABLE lines(order_id INTEGER,product_id INTEGER);
    INSERT INTO products VALUES (1,'Tea'),(2,'Snacks'),(3,'Coffee'),(4,'Tea');
    INSERT INTO lines VALUES (10,1),(10,4),(10,2),(11,1),(11,3),
                            (12,1),(12,2),(12,2);""")
    rows = db.execute("""WITH distinct_aisles AS (
      SELECT DISTINCT l.order_id,p.subcategory
      FROM lines l JOIN products p ON p.id=l.product_id
      WHERE p.subcategory IS NOT NULL),
    co_occurrences AS (
      SELECT a.subcategory a,b.subcategory b,COUNT(*) orders_together
      FROM distinct_aisles a JOIN distinct_aisles b
      ON a.order_id=b.order_id AND a.subcategory<b.subcategory
      GROUP BY a.subcategory,b.subcategory)
    SELECT a,b,orders_together FROM co_occurrences
    ORDER BY orders_together DESC,a,b""").fetchall()
    check("P070 unique unordered pairs per order despite repeated lines",
          rows, [('Snacks','Tea',2),('Coffee','Tea',1)])


if __name__ == "__main__":
    test_full_join_emulation()
    test_shipper_grain()
    test_category_status()
    test_pair_counts()
    print("PASS: four source-aligned PNP join fixtures")
