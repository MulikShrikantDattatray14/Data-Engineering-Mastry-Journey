"""Reviewer-authored SQLite edge-case fixtures for the 16 archived PNP Date/Time prompts.

A passed fixture tests one specified semantic property on synthetic data. It is NOT an
original MySQL/SQL Server key, original full-dataset output, or a learner submission.
"""
import sqlite3
import unittest
from pathlib import Path

SOURCE_DIR = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/"
    "2.PNP- foundations and practice/12. Dates and Time"
)
IDS = ("A096", "A097", "A098", "A099", "A100", "P020", "P040", "P061",
       "P064", "P066", "P069", "P075", "P076", "P081", "P085", "P091")


def db(schema, insert, values):
    conn = sqlite3.connect(":memory:")
    conn.executescript(schema)
    conn.executemany(insert, values)
    return conn


class DatesAndTimeSourceChecks(unittest.TestCase):
    def test_source_integrity_16_prompts(self):
        self.assertTrue(SOURCE_DIR.is_dir(), "Original date/time source archive not found")
        for ident in IDS:
            matches = list(SOURCE_DIR.glob(ident + ".*.md"))
            self.assertEqual(len(matches), 1, f"Missing/duplicate source: {ident}")
            content = matches[0].read_text(encoding="utf-8")
            self.assertIn("## Question and image", content)
            self.assertIn("## Official solution", content)

    def test_a096_index_predicate_and_future_date_ambiguity(self):
        con = db("CREATE TABLE orders (id INT,order_date TEXT); CREATE INDEX ix_dates ON orders(order_date);",
                 "INSERT INTO orders VALUES (?,?)",
                 [(1,"2026-01-01"),(2,"2026-01-02"),(3,"2026-02-01"),(4,"2026-02-02")])
        sql = "SELECT id FROM orders WHERE order_date >= date('2026-02-01','-30 days') ORDER BY id"
        self.assertEqual(con.execute(sql).fetchall(), [(2,),(3,),(4,)])
        plan = con.execute("EXPLAIN QUERY PLAN SELECT id FROM orders WHERE order_date >= date('2026-02-01','-30 days')").fetchall()
        self.assertTrue(any("USING" in row[-1] and "ix_dates" in row[-1] for row in plan), plan)
        # The source's DATEDIFF(today,order_date)<=30 has NO future-date upper bound.
        # A new <=today predicate would change results; do not call it equivalent.

    def test_a098_monday_weeks_cross_year(self):
        con = db("CREATE TABLE orders (id INT,order_date TEXT)", "INSERT INTO orders VALUES (?,?)",
                 [(1,"2026-01-04"),(2,"2026-01-05"),(3,"2026-01-07"),(4,"2026-01-11"),(5,"2026-01-12")])
        rows = con.execute("""
            SELECT date(order_date, '-' || ((CAST(strftime('%w',order_date) AS INT)+6)%7) || ' days') AS mon,
                   COUNT(*) FROM orders GROUP BY mon ORDER BY mon
        """).fetchall()
        self.assertEqual(rows, [("2025-12-29",1),("2026-01-05",3),("2026-01-12",1)])

    def test_a099_first_order_seven_day_boundary(self):
        con = db("CREATE TABLE customers (cust_id INT,signup_date TEXT);"
                 "CREATE TABLE orders (id INT,cust_id INT,order_date TEXT);",
                 "INSERT INTO customers VALUES (?,?)",
                 [(1,"2026-01-01"),(2,"2026-01-01"),(3,"2026-01-01"),(4,"2026-01-01")])
        con.executemany("INSERT INTO orders VALUES (?,?,?)",
                        [(11,1,"2026-01-08"),(12,2,"2026-01-09"),
                         (13,4,"2025-12-31"),(14,4,"2026-01-02")])
        rows = con.execute("""
            WITH f AS (SELECT cust_id,MIN(order_date) AS first_d FROM orders GROUP BY cust_id)
            SELECT c.cust_id FROM customers c JOIN f USING(cust_id)
            WHERE f.first_d >= c.signup_date AND f.first_d <= date(c.signup_date,'+7 days')
            ORDER BY c.cust_id
        """).fetchall()
        self.assertEqual(rows, [(1,)])
        # Policy for pre-signup first orders is not specified by the advanced source.

    def test_a100_first_month_next_calendar_month_distinct_customers(self):
        con = db("CREATE TABLE orders (id INT,cust_id INT,order_date TEXT)", "INSERT INTO orders VALUES (?,?,?)",
                 [(1,10,"2026-01-10"),(2,10,"2026-02-05"),(3,20,"2026-01-20"),
                  (4,20,"2026-03-01"),(5,30,"2026-02-01"),(6,30,"2026-03-10"),
                  (7,10,"2026-02-06")])
        rows = con.execute("""
            WITH firsts AS (SELECT cust_id,date(MIN(order_date),'start of month') AS cohort
                            FROM orders GROUP BY cust_id),
                 retained AS (SELECT DISTINCT f.cust_id,f.cohort FROM firsts f
                              JOIN orders o ON o.cust_id=f.cust_id
                                  AND date(o.order_date,'start of month')=date(f.cohort,'+1 month'))
            SELECT strftime('%Y%m',cohort),COUNT(*) FROM retained GROUP BY cohort ORDER BY cohort
        """).fetchall()
        self.assertEqual(rows, [("202601",1),("202602",1)])

    def test_p020_november_boundary_and_null_delivery(self):
        con = db("CREATE TABLE Orders (OrderID INT,OrderDate TEXT,ShipDate TEXT,DeliveryDate TEXT)",
                 "INSERT INTO Orders VALUES (?,?,?,?)",
                 [(1,"2025-11-01","2025-11-03","2025-11-06"),(2,"2025-11-02",None,None),
                  (3,"2025-10-31","2025-11-01","2025-11-04"),(4,"2025-12-01",None,None)])
        rows = con.execute("""
            SELECT OrderID,
            CAST(julianday(ShipDate)-julianday(OrderDate) AS INT),
            CAST(julianday(DeliveryDate)-julianday(OrderDate) AS INT)
            FROM Orders WHERE OrderDate >= '2025-11-01' AND OrderDate < '2025-12-01'
            ORDER BY OrderDate,OrderID
        """).fetchall()
        self.assertEqual(rows, [(1,2,5),(2,None,None)])

    def test_p040_negative_signup_gap_flag_is_retained(self):
        con = db("CREATE TABLE Customers (CustomerID INT,DateEntered TEXT);"
                 "CREATE TABLE Orders (OrderID INT,CustomerID INT,OrderDate TEXT);",
                 "INSERT INTO Customers VALUES (?,?)",
                 [(1,"2025-01-03"),(2,"2025-01-05"),(3,"2025-01-01")])
        con.executemany("INSERT INTO Orders VALUES (?,?,?)",
                        [(10,1,"2025-01-01"),(11,1,"2025-01-10"),(12,2,"2025-01-07")])
        rows = con.execute("""
            WITH firsts AS (SELECT CustomerID,MIN(OrderDate) AS first_date FROM Orders GROUP BY CustomerID)
            SELECT c.CustomerID,CAST(julianday(f.first_date)-julianday(c.DateEntered) AS INT),
                   CASE WHEN f.first_date<c.DateEntered THEN 'Order before sign-up' END
            FROM Customers c JOIN firsts f USING(CustomerID) ORDER BY c.CustomerID
        """).fetchall()
        self.assertEqual(rows, [(1,-2,"Order before sign-up"),(2,2,None)])

    def test_p064_missing_months_filled_before_window(self):
        con = db("CREATE TABLE Orders (OrderID INT,OrderDate TEXT,Total_Order_Amount REAL)",
                 "INSERT INTO Orders VALUES (?,?,?)",
                 [(1,"2025-01-01",100),(2,"2025-03-01",300),(3,"2025-04-01",100)])
        rows = con.execute("""
            WITH RECURSIVE bounds AS (
              SELECT date(MIN(OrderDate),'start of month') AS first_m,
                     date(MAX(OrderDate),'start of month') AS last_m FROM Orders),
            months(month) AS (
              SELECT first_m FROM bounds UNION ALL
              SELECT date(month,'+1 month') FROM months,bounds WHERE month<last_m),
            sums AS (SELECT date(OrderDate,'start of month') AS month,
                            SUM(Total_Order_Amount) AS value FROM Orders GROUP BY 1),
            series AS (SELECT m.month,COALESCE(s.value,0) AS value
                       FROM months m LEFT JOIN sums s USING(month)),
            moving AS (SELECT month,value,
              ROUND(AVG(value) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),2) AS avg3,
              ROW_NUMBER() OVER(ORDER BY month) AS rn FROM series)
            SELECT month,value,CASE WHEN rn>=3 THEN avg3 END FROM moving ORDER BY month
        """).fetchall()
        self.assertEqual(rows, [("2025-01-01",100,None),("2025-02-01",0,None),
                                ("2025-03-01",300,133.33),("2025-04-01",100,133.33)])

    def test_p075_seven_and_twenty_eight_day_windows_distinct(self):
        con = db("CREATE TABLE Orders (OrderID INT,CustomerID INT,OrderDate TEXT)",
                 "INSERT INTO Orders VALUES (?,?,?)",
                 [(1,10,"2026-03-02"),(2,20,"2026-03-29"),(3,20,"2026-03-29")])
        rows = con.execute("""
            WITH RECURSIVE bounds AS (SELECT MIN(OrderDate) AS first_d,
                MAX(OrderDate) AS last_d FROM Orders),
            weeks(n,week_end) AS (SELECT 0,last_d FROM bounds UNION ALL
                SELECT n+1,date(week_end,'-7 days') FROM weeks WHERE n<11)
            SELECT w.week_end,
              (SELECT COUNT(DISTINCT CustomerID) FROM Orders
               WHERE OrderDate BETWEEN date(w.week_end,'-6 days') AND w.week_end),
              (SELECT COUNT(DISTINCT CustomerID) FROM Orders
               WHERE OrderDate BETWEEN date(w.week_end,'-27 days') AND w.week_end)
            FROM weeks w CROSS JOIN bounds b
            WHERE date(w.week_end,'-27 days')>=b.first_d ORDER BY w.week_end
        """).fetchall()
        self.assertEqual(rows, [("2026-03-29",1,2)])

    def test_p081_feb29_prior_year_is_feb28(self):
        con = db("CREATE TABLE Orders (OrderID INT,OrderDate TEXT,Total_Order_Amount REAL)",
                 "INSERT INTO Orders VALUES (?,?,?)",
                 [(1,"2023-01-10",100),(2,"2023-03-01",200),(3,"2024-01-10",150),(4,"2024-02-29",150)])
        rows = con.execute("""
            WITH mx AS (SELECT MAX(OrderDate) AS last_d FROM Orders),
            bounds AS (SELECT date(last_d,'start of year') AS ystart,last_d AS yend,
              date(last_d,'start of year','-1 year') AS pstart,
              CASE WHEN strftime('%m-%d',last_d)='02-29'
                THEN printf('%04d-02-28',CAST(strftime('%Y',last_d) AS INT)-1)
                ELSE printf('%04d-%s',CAST(strftime('%Y',last_d) AS INT)-1,
                            strftime('%m-%d',last_d)) END AS pend FROM mx)
            SELECT ystart,yend,pstart,pend,
              (SELECT COUNT(*) FROM Orders WHERE OrderDate BETWEEN ystart AND yend),
              (SELECT SUM(Total_Order_Amount) FROM Orders WHERE OrderDate BETWEEN ystart AND yend),
              (SELECT COUNT(*) FROM Orders WHERE OrderDate BETWEEN pstart AND pend),
              (SELECT SUM(Total_Order_Amount) FROM Orders WHERE OrderDate BETWEEN pstart AND pend)
            FROM bounds
        """).fetchall()
        self.assertEqual(rows, [("2024-01-01","2024-02-29","2023-01-01","2023-02-28",
                                 2,300,1,100)])

    def test_p085_180_day_threshold_and_lag_before_time_filter(self):
        con = db("CREATE TABLE Orders (OrderID INT,CustomerID INT,OrderDate TEXT,Total_Order_Amount REAL)",
                 "INSERT INTO Orders VALUES (?,?,?,?)",
                 [(1,10,"2025-01-01",100),(2,10,"2025-07-01",80),
                  (3,20,"2025-06-01",50),(4,20,"2025-07-01",60),
                  (5,30,"2025-01-02",40),(6,30,"2025-07-01",70)])
        rows = con.execute("""
            WITH anchor AS (SELECT MAX(OrderDate) AS max_d FROM Orders),
            ordered AS (SELECT OrderID,CustomerID,OrderDate,Total_Order_Amount,
              LAG(OrderDate) OVER (PARTITION BY CustomerID ORDER BY OrderDate,OrderID) AS previous_d
              FROM Orders)
            SELECT CustomerID,previous_d,OrderDate,
              CAST(julianday(OrderDate)-julianday(previous_d) AS INT)
            FROM ordered CROSS JOIN anchor
            WHERE OrderDate BETWEEN date(max_d,'-12 months') AND max_d
              AND julianday(OrderDate)-julianday(previous_d)>=180 ORDER BY CustomerID
        """).fetchall()
        self.assertEqual(rows, [(10,"2025-01-01","2025-07-01",181),
                                (30,"2025-01-02","2025-07-01",180)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
