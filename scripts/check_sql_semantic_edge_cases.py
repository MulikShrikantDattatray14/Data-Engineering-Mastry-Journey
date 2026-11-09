"""Source-aligned SQL semantic regression fixtures, not learner solutions.

Small SQLite fixtures cover representative traps found while reviewing PNP
problem descriptions. The tests verify behaviors, not full 205 source answers.
"""
import sqlite3


def check(label, actual, expected):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")
    print("PASS:", label)


def test_anti_join_null():
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER);
        INSERT INTO customers VALUES (1,'Asha'),(2,'Mira'),(3,'Zoya');
        INSERT INTO orders VALUES (10,1),(11,NULL);
    """)
    bad = db.execute(
        "SELECT id FROM customers WHERE id NOT IN "
        "(SELECT customer_id FROM orders) ORDER BY id"
    ).fetchall()
    good = db.execute(
        "SELECT id FROM customers WHERE NOT EXISTS "
        "(SELECT 1 FROM orders WHERE orders.customer_id=customers.id) "
        "ORDER BY id"
    ).fetchall()
    check("NOT IN nullable subquery is unsafe", bad, [])
    check("NOT EXISTS preserves unmatched keys", good, [(2,), (3,)])


def test_latest_order_ties():
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE orders(order_id INTEGER, customer_id INTEGER, day TEXT);
        INSERT INTO orders VALUES
        (1,10,'2025-01-01'),(2,10,'2025-01-02'),
        (3,10,'2025-01-02'),(4,20,'2025-01-01');
    """)
    rows = db.execute("""
        WITH ranked AS (
            SELECT order_id, customer_id,
                   ROW_NUMBER() OVER (
                       PARTITION BY customer_id
                       ORDER BY day DESC, order_id DESC
                   ) AS rn
            FROM orders
        )
        SELECT customer_id,order_id FROM ranked
        WHERE rn=1 ORDER BY customer_id
    """).fetchall()
    check("latest row same-day deterministic tie-break", rows, [(10,3),(20,4)])


def test_daily_preaggregation():
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE orders(day TEXT, amount INTEGER);
        INSERT INTO orders VALUES
        ('2025-01-01',100),('2025-01-02',50),
        ('2025-02-01',200),('2025-03-01',10),('2025-03-01',20);
    """)
    rows = db.execute("""
        WITH daily AS (
            SELECT day,SUM(amount) AS day_sum
            FROM orders GROUP BY day
        )
        SELECT day,day_sum,
            SUM(day_sum) OVER (
                PARTITION BY substr(day,1,7)
                ORDER BY day
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS month_to_date
        FROM daily ORDER BY day
    """).fetchall()
    check("duplicate same-day orders aggregate before MTD", rows,
          [('2025-01-01',100,100),('2025-01-02',50,150),
           ('2025-02-01',200,200),('2025-03-01',30,30)])


def test_active_quarter_growth():
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE quarters(customer_id INTEGER, quarter INTEGER, spend INTEGER);
        INSERT INTO quarters VALUES (10,1,10),(10,2,20),(10,4,30),
                                    (20,1,10),(20,2,5),(20,3,20);
    """)
    rows = db.execute("""
        WITH evaluated AS (
            SELECT customer_id,quarter,spend,
                   LAG(spend) OVER (PARTITION BY customer_id ORDER BY quarter)
                       AS previous
            FROM quarters
        ),
        eligibility AS (
            SELECT customer_id, COUNT(*) AS active_quarters,
                   SUM(CASE WHEN previous IS NOT NULL AND spend <= previous
                            THEN 1 ELSE 0 END) AS declines
            FROM evaluated GROUP BY customer_id
        )
        SELECT customer_id FROM eligibility
        WHERE active_quarters>=3 AND declines=0 ORDER BY customer_id
    """).fetchall()
    check("active quarters can skip an inactive quarter", rows, [(10,)])


if __name__ == "__main__":
    test_anti_join_null()
    test_latest_order_ties()
    test_daily_preaggregation()
    test_active_quarter_growth()
    print("PASS: four focused SQL semantics checks")
