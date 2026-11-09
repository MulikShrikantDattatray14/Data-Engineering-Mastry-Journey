"""Reviewer-authored SQLite fixtures for PNP SubQueries source statements.

Synthetic examples only: NOT official SQL answers, full source data, or learner solves.
Source-by-source caveats: 01. SQL Mastery/PNP-SEMANTIC-AUDIT.md.
"""
import sqlite3
import unittest


def fixture(schema, data):
    con = sqlite3.connect(":memory:")
    con.executescript(schema)
    for table, rows in data.items():
        for row in rows:
            con.execute("INSERT INTO " + table + " VALUES (" + ",".join("?" for _ in row) + ")", row)
    return con


class SubquerySourceFixtures(unittest.TestCase):
    def test_A002_second_distinct_salary(self):
        con = fixture("CREATE TABLE employees(id INT, salary INT);",
                      {"employees": [(1,300),(2,300),(3,200),(4,100),(5,None)]})
        q = "SELECT MAX(salary) FROM employees WHERE salary<(SELECT MAX(salary) FROM employees)"
        self.assertEqual(con.execute(q).fetchone()[0], 200)
        con.execute("DELETE FROM employees WHERE salary < 300")
        self.assertIsNone(con.execute(q).fetchone()[0])
        con.close()

    def test_A007_excepts_and_null_safe_anti_join(self):
        con = fixture("CREATE TABLE products(id INT); CREATE TABLE items(id INT);",
                      {"products": [(1,),(2,),(3,),(4,)], "items": [(1,),(1,),(3,),(None,)]})
        q1 = "SELECT id FROM products EXCEPT SELECT id FROM items"
        q2 = "SELECT p.id FROM products p WHERE NOT EXISTS(SELECT 1 FROM items i WHERE i.id=p.id) ORDER BY p.id"
        self.assertEqual(con.execute(q1).fetchall(), [(2,),(4,)])
        self.assertEqual(con.execute(q2).fetchall(), [(2,),(4,)])
        con.close()

    def test_A029_latest_order_ties_remain(self):
        con = fixture("CREATE TABLE orders(id INT,cust INT,day TEXT);",
                      {"orders": [(1,10,"2026-01-01"),(2,10,"2026-01-05"),
                                  (3,10,"2026-01-05"),(4,20,"2026-01-02")]})
        q = "SELECT o.id FROM orders o WHERE o.day=(SELECT MAX(x.day) FROM orders x WHERE x.cust=o.cust) ORDER BY o.id"
        self.assertEqual(con.execute(q).fetchall(), [(2,),(3,),(4,)])
        con.close()

    def test_A034_exists_in_join_distinct_three_equivalent_semijoins(self):
        con = fixture("CREATE TABLE customers(id INT);CREATE TABLE orders(id INT,cust INT);",
                      {"customers":[(10,),(20,),(30,)],"orders":[(1,10),(2,10),(3,None),(4,99)]})
        queries = ["SELECT id FROM customers WHERE id IN (SELECT cust FROM orders)",
                   "SELECT c.id FROM customers c WHERE EXISTS(SELECT 1 FROM orders o WHERE o.cust=c.id)",
                   "SELECT DISTINCT c.id FROM customers c JOIN orders o ON o.cust=c.id"]
        for q in queries:
            self.assertEqual(con.execute(q).fetchall(), [(10,)])
        con.close()

    def test_A035_not_in_null_poisoning(self):
        con = fixture("CREATE TABLE employees(id INT, manager INT);",
                      {"employees":[(1,None),(2,1),(3,1)]})
        broken = "SELECT id FROM employees WHERE id NOT IN (SELECT manager FROM employees)"
        safe = """SELECT e.id FROM employees e WHERE NOT EXISTS (
                  SELECT 1 FROM employees m WHERE m.manager=e.id) ORDER BY e.id"""
        self.assertEqual(con.execute(broken).fetchall(), [])
        self.assertEqual(con.execute(safe).fetchall(), [(2,),(3,)])
        con.close()

    def test_A038_relational_division_and_empty_target(self):
        con = fixture("""CREATE TABLE customers(id INT);
                         CREATE TABLE products(id INT,category TEXT);
                         CREATE TABLE orders(id INT,cust INT);
                         CREATE TABLE items(ord INT,product INT);""",
                      {"customers":[(10,),(20,),(30,)],
                       "products":[(101,"Audio"),(102,"Audio"),(103,"Home")],
                       "orders":[(1,10),(2,20),(3,10)],
                       "items":[(1,101),(1,102),(2,101),(3,101)]})
        q = """SELECT c.id FROM customers c WHERE NOT EXISTS(
                 SELECT 1 FROM products p WHERE p.category='Audio' AND NOT EXISTS(
                   SELECT 1 FROM orders o JOIN items i ON i.ord=o.id
                   WHERE o.cust=c.id AND i.product=p.id)) ORDER BY c.id"""
        self.assertEqual(con.execute(q).fetchall(), [(10,)])
        con.execute("DELETE FROM products WHERE category='Audio'")
        self.assertEqual(con.execute(q).fetchall(), [(10,),(20,),(30,)])
        con.close()

    def test_A078_top_three_distinct_salary_tiers_includes_ties(self):
        con = fixture("CREATE TABLE employees(id INT,dept INT,salary INT);",
                      {"employees":[(1,10,100),(2,10,90),(3,10,90),(4,10,80),
                                    (5,10,70),(6,20,60),(7,20,None)]})
        q = """SELECT e.id FROM employees e WHERE e.salary IS NOT NULL AND
               (SELECT COUNT(DISTINCT x.salary) FROM employees x
                WHERE x.dept=e.dept AND x.salary>e.salary)<3 ORDER BY e.id"""
        self.assertEqual(con.execute(q).fetchall(), [(1,),(2,),(3,),(4,),(6,)])
        con.close()

    def test_P028_unknown_payment_and_global_count_value_share(self):
        con = fixture("""CREATE TABLE Payments(id INT,method TEXT);
                         CREATE TABLE Orders(id INT,payment INT,amount REAL);""",
                      {"Payments":[(1,"UPI")],
                       "Orders":[(1,1,100),(2,1,100),(3,999,300),(4,None,500)]})
        q = """SELECT COALESCE(p.method,'Unknown'),COUNT(*),
                    ROUND(100.0*COUNT(*)/(SELECT COUNT(*) FROM Orders),2),
                    SUM(o.amount),ROUND(100.0*SUM(o.amount)/(SELECT SUM(amount) FROM Orders),2)
               FROM Orders o LEFT JOIN Payments p ON p.id=o.payment
               GROUP BY COALESCE(p.method,'Unknown') ORDER BY 1"""
        self.assertEqual(con.execute(q).fetchall(),
                         [("UPI",2,50.0,200.0,20.0),("Unknown",2,50.0,800.0,80.0)])
        con.close()

    def test_P057_union_all_keeps_both_partner_roles(self):
        con = fixture("""CREATE TABLE Suppliers(id INT,company TEXT,phone TEXT,email TEXT,country TEXT);
                         CREATE TABLE Shippers(id INT,company TEXT,phone TEXT);""",
                      {"Suppliers":[(1,"Alpha","111","a@x.com","India")],
                       "Shippers":[(2,"Alpha","222")]})
        q = """SELECT 'Supplier' role,id,company,phone,email,country FROM Suppliers
               UNION ALL SELECT 'Shipper',id,company,phone,NULL,NULL FROM Shippers
               ORDER BY company,role,id"""
        self.assertEqual(con.execute(q).fetchall(),
                         [("Shipper",2,"Alpha","222",None,None),
                          ("Supplier",1,"Alpha","111","a@x.com","India")])
        con.close()

    def test_P080_later_day_90_day_window_and_30_eligible_buyers(self):
        con = sqlite3.connect(":memory:")
        con.execute("CREATE TABLE purchases(customer INT,category TEXT,day TEXT)")
        rows = [(i,"Tea","2026-01-01") for i in range(1,31)]
        rows += [(i,"Tea","2026-01-20") for i in range(1,7)]
        rows += [(7,"Tea","2026-01-01"),(7,"Tea","2026-04-02"),
                 (31,"Tea","2026-04-14"),(99,"Other","2026-04-15")]
        con.executemany("INSERT INTO purchases VALUES (?,?,?)",rows)
        q = """WITH firsts AS (
                 SELECT customer,category,MIN(date(day)) first_day FROM purchases
                 GROUP BY customer,category
               ), eligible AS (
                 SELECT f.* FROM firsts f
                 WHERE julianday((SELECT MAX(date(day)) FROM purchases))-julianday(f.first_day)>=90
               ), flags AS (
                 SELECT e.category,e.customer,
                   EXISTS(SELECT 1 FROM purchases p WHERE p.category=e.category
                          AND p.customer=e.customer AND date(p.day)>e.first_day
                          AND julianday(date(p.day))-julianday(e.first_day)<=90) repeated
                 FROM eligible e
               )
               SELECT category,COUNT(*),SUM(repeated),ROUND(100.0*SUM(repeated)/COUNT(*),2)
               FROM flags GROUP BY category HAVING COUNT(*)>=30"""
        self.assertEqual(con.execute(q).fetchall(), [("Tea",30,6,20.0)])
        con.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
