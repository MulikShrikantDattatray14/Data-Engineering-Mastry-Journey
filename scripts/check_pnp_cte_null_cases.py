"""Independent SQLite fixtures for archived PNP CTE/NULL source requirements.

These are auditor-made edge-case probes, NOT official datasets, official
solutions, or evidence that the learner independently solved the questions.
"""
import sqlite3


def check(label, schema, query, expected):
    with sqlite3.connect(":memory:") as db:
        db.executescript(schema)
        actual = db.execute(query).fetchall()
    assert actual == expected, f"{label}: actual={actual!r}, expected={expected!r}"
    print("PASS:", label)


def department_vs_company():
    check("A042 employee-weighted company average", """
        CREATE TABLE employees(emp_id INT, dept_id INT, salary REAL);
        INSERT INTO employees VALUES (1,10,50),(2,10,70),(3,20,120);
    """, """
        WITH dept AS (
            SELECT dept_id, AVG(salary) dept_mean
            FROM employees GROUP BY dept_id
        ), company AS (SELECT AVG(salary) company_mean FROM employees)
        SELECT dept_id, ROUND(dept_mean,2), ROUND(company_mean,2)
        FROM dept CROSS JOIN company ORDER BY dept_id
    """, [(10,60.0,80.0),(20,120.0,80.0)])


def rank_outside_window():
    check("A043 RANK ties filter in outer SELECT", """
        CREATE TABLE employees(emp_id INT, emp_name TEXT, salary INT);
        INSERT INTO employees VALUES (1,'Ada',90),(2,'Ben',90),
                                     (3,'Cora',80),(4,'Dee',70);
    """, """
        WITH ranked AS (
            SELECT emp_id, emp_name, RANK() OVER (ORDER BY salary DESC) r
            FROM employees
        )
        SELECT emp_name,r FROM ranked WHERE r<=2 ORDER BY r,emp_id
    """, [('Ada',1),('Ben',1)])


def order_spine():
    check("A044 zero-item orders stay in spine", """
        CREATE TABLE orders(order_id INT,cust_id INT);
        CREATE TABLE order_items(item_id INT,order_id INT,qty INT);
        INSERT INTO orders VALUES (10,1),(11,2),(12,3);
        INSERT INTO order_items VALUES (1,10,2),(2,10,1),(3,99,4);
    """, """
        WITH spine AS (SELECT order_id,cust_id FROM orders),
        item_counts AS (SELECT order_id,COUNT(item_id) n
                        FROM order_items GROUP BY order_id)
        SELECT s.order_id,s.cust_id,COALESCE(i.n,0)
        FROM spine s LEFT JOIN item_counts i ON s.order_id=i.order_id
        ORDER BY s.order_id
    """, [(10,1,2),(11,2,0),(12,3,0)])


def payment_events():
    check("A045 duplicate event rows before aggregation", """
        CREATE TABLE payments(payment_id INT,order_id INT,paid_at TEXT,amount INT);
        INSERT INTO payments VALUES (1,10,'2026-01-03',50),
          (2,10,'2026-01-03',50),(3,10,'2026-01-04',20),
          (4,11,'2026-01-05',40);
    """, """
        WITH numbered AS (
            SELECT *, ROW_NUMBER() OVER (
                PARTITION BY order_id,paid_at ORDER BY payment_id) rn
            FROM payments
        ), unique_events AS (SELECT order_id,amount FROM numbered WHERE rn=1)
        SELECT order_id,SUM(amount) FROM unique_events
        GROUP BY order_id ORDER BY order_id
    """, [(10,70),(11,40)])


def repeat_buyer_share():
    check("P030 NULL buyer excluded from ordering-buyer denominator", """
        CREATE TABLE Orders(OrderID INT,CustomerID INT);
        INSERT INTO Orders VALUES (1,10),(2,20),(3,20),(4,30),(5,NULL);
    """, """
        WITH counts AS (
            SELECT CustomerID,COUNT(*) n FROM Orders
            WHERE CustomerID IS NOT NULL GROUP BY CustomerID
        ), buckets AS (
            SELECT CASE WHEN n>=2 THEN 'Repeat' ELSE 'One-time' END label
            FROM counts
        )
        SELECT label,COUNT(*),ROUND(100.0*COUNT(*)/
          NULLIF((SELECT COUNT(*) FROM counts),0),2)
        FROM buckets GROUP BY label ORDER BY label
    """, [('One-time',2,66.67),('Repeat',1,33.33)])


def three_counts():
    check("A091 COUNT vs COUNT(column) vs COUNT DISTINCT", """
        CREATE TABLE employees(emp_id INT,manager_id INT);
        INSERT INTO employees VALUES (1,NULL),(2,1),(3,1),(4,2);
    """, """
        SELECT COUNT(*),COUNT(manager_id),COUNT(DISTINCT manager_id)
        FROM employees
    """, [(4,3,2)])


def null_safe_join():
    check("A094 two NULL keys on each side create four matches", """
        CREATE TABLE stage(id INT,batch_code TEXT);
        CREATE TABLE target(id INT,batch_code TEXT);
        INSERT INTO stage VALUES (1,NULL),(2,NULL),(3,'A');
        INSERT INTO target VALUES (10,NULL),(11,NULL),(20,'A');
    """, """
        SELECT s.id,t.id FROM stage s JOIN target t
        ON (s.batch_code=t.batch_code OR
            (s.batch_code IS NULL AND t.batch_code IS NULL))
        ORDER BY s.id,t.id
    """, [(1,10),(1,11),(2,10),(2,11),(3,20)])


def average_vs_counts():
    check("A095 AVG excludes NULL, denominator counts differ", """
        CREATE TABLE order_items(item_id INT,discount INT);
        INSERT INTO order_items VALUES (1,10),(2,NULL),(3,20);
    """, """
        SELECT AVG(discount),SUM(discount)*1.0/COUNT(*),
               SUM(discount)*1.0/NULLIF(COUNT(discount),0)
        FROM order_items
    """, [(15.0,10.0,15.0)])


def supplier_issue_labels():
    check("P024 multiple issue flags vs blanks/unknowns", """
        CREATE TABLE Suppliers(SupplierID INT,Country TEXT,Email TEXT);
        INSERT INTO Suppliers VALUES (1,'India','a@example.com'),
          (2,'USA',NULL),(3,NULL,'b@example.com'),
          (4,'India','  '),(5,NULL,NULL);
    """, """
        WITH flags AS (
          SELECT SupplierID,
            CASE WHEN Country IS NULL OR TRIM(Country)='' THEN 'Country missing'
                 WHEN Country<>'India' THEN 'Outside India' ELSE NULL END country_issue,
            CASE WHEN Email IS NULL OR TRIM(Email)='' THEN 'No email' ELSE NULL END email_issue
          FROM Suppliers
        )
        SELECT SupplierID,COALESCE(country_issue,'') ||
            CASE WHEN country_issue IS NOT NULL AND email_issue IS NOT NULL
                 THEN '; ' ELSE '' END || COALESCE(email_issue,'') AS issue
        FROM flags WHERE country_issue IS NOT NULL OR email_issue IS NOT NULL
        ORDER BY SupplierID
    """, [(2,'Outside India; No email'),(3,'Country missing'),
          (4,'No email'),(5,'Country missing; No email')])


if __name__ == '__main__':
    for task in (department_vs_company, rank_outside_window, order_spine,
                 payment_events, repeat_buyer_share, three_counts,
                 null_safe_join, average_vs_counts, supplier_issue_labels):
        task()
    print('9 independent reviewer-made SQLite fixtures passed (no official answers certified).')
