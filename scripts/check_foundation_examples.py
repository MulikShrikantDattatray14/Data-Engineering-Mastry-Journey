"""Run small original teaching examples used in the canonical SQL/Python foundations.

This is not a substitute for independent source-problem grading.
"""
import sqlite3
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


def sql_case(name, statements, expected):
    db = sqlite3.connect(":memory:")
    try:
        parts = [p.strip() for p in statements.split(";") if p.strip()]
        for statement in parts[:-1]:
            db.execute(statement)
        actual = db.execute(parts[-1]).fetchall()
        assert actual == expected, f"{name}: expected {expected}, got {actual}"
        print("PASS SQL", name)
    finally:
        db.close()


def run_examples():
    sql_case("Advanced SELECT", """
        CREATE TABLE Orders(order_id INT,customer_id INT,status TEXT,amount INT);
        INSERT INTO Orders VALUES
           (101,1,'paid',1200),(102,2,'pending',2000),
           (103,1,'paid',800),(104,3,'paid',1500);
        SELECT order_id,customer_id,amount FROM Orders
        WHERE status='paid' AND amount>1000
        ORDER BY amount DESC,order_id;
    """, [(104,3,1500),(101,1,1200)])

    sql_case("WHERE/GROUP BY/HAVING", """
        CREATE TABLE Orders(order_id INT,customer_id INT,amount INT,status TEXT);
        INSERT INTO Orders VALUES
            (1,10,100,'paid'),(2,20,50,'paid'),
            (3,10,300,'paid'),(4,20,200,'pending');
        SELECT customer_id,SUM(amount) AS paid_total FROM Orders
        WHERE status='paid' GROUP BY customer_id
        HAVING SUM(amount)>=100 ORDER BY paid_total DESC,customer_id ASC;
    """, [(10,400)])

    sql_case("Aggregate NULL handling", """
        CREATE TABLE Transactions(id INT,status TEXT,amount INT);
        INSERT INTO Transactions VALUES
            (1,'paid',100),(2,'paid',200),(3,'failed',50),(4,'paid',NULL);
        SELECT COUNT(*),COUNT(amount),SUM(amount),AVG(1.0*amount)
        FROM Transactions;
    """, [(4,3,350,350/3)])

    sql_case("CTE stages", """
        CREATE TABLE Orders(order_id INT,customer_id INT,status TEXT,amount INT);
        INSERT INTO Orders VALUES
            (1,10,'paid',100),(2,10,'paid',250),
            (3,20,'failed',500),(4,20,'paid',50);
        WITH paid_orders AS (
            SELECT customer_id,amount FROM Orders WHERE status='paid'
        ), customer_totals AS (
            SELECT customer_id,SUM(amount) total FROM paid_orders
            GROUP BY customer_id
        )
        SELECT customer_id,total FROM customer_totals
        WHERE total>=300 ORDER BY total DESC,customer_id;
    """, [(10,350)])

    sql_case("Correlated subquery", """
        CREATE TABLE Employees(employee_id INT,dept TEXT,salary INT);
        INSERT INTO Employees VALUES
            (1,'A',100),(2,'A',200),(3,'B',300),(4,'B',500);
        SELECT e.employee_id,e.dept,e.salary FROM Employees e
        WHERE e.salary > (
            SELECT AVG(1.0*x.salary) FROM Employees x WHERE x.dept=e.dept
        ) ORDER BY e.employee_id;
    """, [(2,'A',200),(4,'B',500)])

    sql_case("String normalization", """
        SELECT LOWER(TRIM('  MEERA@EXAMPLE.COM  '));
    """, [('meera@example.com',)])

    sql_case("Window cumulative sum", """
        CREATE TABLE Sales(id INT, customer TEXT, amount INT);
        INSERT INTO Sales VALUES
            (1,'A',100),(2,'B',200),(3,'A',300),(4,'A',500);
        SELECT id,customer,amount,
            SUM(amount) OVER (
                PARTITION BY customer ORDER BY id
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) FROM Sales ORDER BY id;
    """, [(1,'A',100,100),(2,'B',200,200),(3,'A',300,400),(4,'A',500,900)])

    sql_case("Recursive CTE termination", """
        WITH RECURSIVE numbers(n) AS (
            SELECT 1 UNION ALL
            SELECT n+1 FROM numbers WHERE n<5
        ) SELECT n FROM numbers ORDER BY n;
    """, [(1,),(2,),(3,),(4,),(5,)])

    ids = {10,20,30,20,10}
    ids.add(40)
    assert (len(ids),20 in ids,50 in ids) == (4, True, False)
    print("PASS Python sets source illustration")

    orders = [
        {"id":101, "status":"delivered", "amount":120},
        {"id":102, "status":"cancelled", "amount":900},
        {"id":103, "status":"delivered", "amount":80}
    ]
    assert [r["amount"] for r in orders if r["status"]=="delivered"] == [120,80]
    print("PASS Python comprehensions")

    def positive(values):
        for value in values:
            if value > 0:
                yield value
    gen = positive([100,-5,200])
    assert [next(gen),next(gen),list(gen)] == [100,200,[]]
    print("PASS Python generator one-pass behavior")

    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE orders(order_id INTEGER PRIMARY KEY,amount INTEGER)")
        def load(rows):
            with db:
                db.executemany(
                    "INSERT INTO orders(order_id,amount) VALUES (?,?) "
                    "ON CONFLICT(order_id) DO UPDATE SET amount=excluded.amount",
                    rows
                )
        load([(101,100),(102,200)])
        load([(101,100),(102,200)])
        assert db.execute("SELECT COUNT(*),SUM(amount) FROM orders").fetchone()==(2,300)
    print("PASS Python idempotent SQLite load")

    for asset in [
        "02. Python Mastery/03. Lists and Slicing/assets/sales-every-second.svg",
        "01. SQL Mastery/03. Sorting and Grouping/assets/where-group-having.svg",
        "01. SQL Mastery/09. Window Functions/assets/running-totals-by-partition.svg",
    ]:
        doc = ElementTree.parse(ROOT/asset)
        root=doc.getroot()
        assert root.tag.endswith("svg"), f"Invalid SVG root: {asset}"
        assert root.find("{http://www.w3.org/2000/svg}title") is not None, f"Missing title: {asset}"
        print("PASS SVG", asset)


if __name__ == "__main__":
    run_examples()
