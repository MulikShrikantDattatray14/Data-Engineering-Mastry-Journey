"""Execute actual saved SQLite JOIN answers on independent, disposable fixtures.

Reviewer tests, not user submissions or official answer verification. The source
Markdown is immutable. Never count these tests as newly solved exercises.
"""
from pathlib import Path
from urllib.parse import unquote
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "01. SQL Mastery" / "PNP-PROBLEM-INDEX.md"


def saved_answer(pid):
    lines = INDEX.read_text(encoding="utf-8").splitlines()
    matching = [row for row in lines if row.startswith("| " + pid + " |")]
    assert len(matching) == 1, f"{pid}: expected one indexed file"
    link = re.search(r"\]\(<([^>]+)>\)", matching[0])
    assert link, f"{pid}: missing source link"
    path = (INDEX.parent / unquote(link.group(1))).resolve()
    assert path.is_relative_to(ROOT), f"{pid}: unsafe path"
    source = path.read_text(encoding="utf-8")
    fence = chr(96) * 3
    match = re.search(r"## My solution — SQLite[\s\S]*?" +
                      re.escape(fence) + r"sql\s*\n(.*?)" + re.escape(fence),
                      source, flags=re.S)
    assert match, f"{pid}: saved answer missing (do not synthesize)"
    return match.group(1).strip()


def verify(pid, setup, expected, ordered=True):
    db = sqlite3.connect(":memory:")
    db.executescript(setup)
    actual = db.execute(saved_answer(pid)).fetchall()
    lhs = actual if ordered else sorted(actual, key=repr)
    rhs = expected if ordered else sorted(expected, key=repr)
    assert lhs == rhs, f"{pid}: {actual!r} != {expected!r}"
    print("PASS", pid, "archived answer vs independent fixture")


def main():
    verify("A001", """
      CREATE TABLE departments(dept_id INTEGER PRIMARY KEY,dept_name TEXT);
      CREATE TABLE employees(emp_id INTEGER PRIMARY KEY,dept_id INTEGER);
      INSERT INTO departments VALUES(1,'Sales'),(2,'Support'),(3,'Legal');
      INSERT INTO employees VALUES(10,1),(11,1),(12,99);
    """, [(1,"Sales",2),(2,"Support",0),(3,"Legal",0)], False)

    verify("A010", """
      CREATE TABLE employees(emp_id INTEGER PRIMARY KEY,emp_name TEXT,manager_id INTEGER,salary INTEGER);
      INSERT INTO employees VALUES(1,'Asha',NULL,100),(2,'Bela',1,120),
       (3,'Chitra',1,100),(4,'Dev',99,500),(5,'Esha',2,130),(6,'Farah',2,NULL);
    """, [(2,"Bela"),(5,"Esha")], False)

    verify("A012", """
      CREATE TABLE employees(emp_id INTEGER PRIMARY KEY,emp_name TEXT,manager_id INTEGER);
      INSERT INTO employees VALUES(1,'Asha',NULL),(2,'Ben',1),(3,'Cia',1),
       (4,'Dev',1),(5,'Eva',2),(6,'Finn',2),(7,'Gia',NULL),(8,'Hal',7),
       (9,'Ira',7),(10,'Jan',7),(11,'Kai',99),(12,'Lee',99),(13,'Moe',99);
    """, [(1,3),(7,3)], False)

    verify("A014", """
      CREATE TABLE employees(emp_id INTEGER PRIMARY KEY,emp_name TEXT,manager_id INTEGER);
      INSERT INTO employees VALUES(1,'Asha',NULL),(2,'Ben',1),(3,'Cia',1),
       (4,'Dev',2),(5,'Eva',NULL),(6,'Finn',99);
    """, [(3,"Cia"),(4,"Dev"),(5,"Eva"),(6,"Finn")], False)

    verify("P015", """
      CREATE TABLE Category(CategoryID INTEGER PRIMARY KEY,CategoryName TEXT);
      CREATE TABLE Products(ProductID INTEGER PRIMARY KEY,CategoryID INTEGER);
      INSERT INTO Category VALUES(1,'Empty'),(2,'Two'),(3,'One');
      INSERT INTO Products VALUES(10,2),(11,2),(20,3),(30,999);
    """, [(1,"Empty",0),(3,"One",1),(2,"Two",2)])

    verify("P016", """
      CREATE TABLE Customers(CustomerID INTEGER PRIMARY KEY,FirstName TEXT,LastName TEXT,City TEXT);
      CREATE TABLE Orders(OrderID INTEGER PRIMARY KEY,OrderDate TEXT,CustomerID INTEGER,Total_Order_Amount REAL);
      INSERT INTO Customers VALUES(1,'Ada','Lovelace',' Pune '),(2,'Ben',NULL,' Mumbai ');
      INSERT INTO Orders VALUES(10,'2025-12-01',1,100),(11,'2025-12-31 23:45:00',2,200),
       (12,'2026-01-01',1,300),(13,'2025-11-30',1,400),(14,'2025-12-20',999,500);
    """, [(10,"2025-12-01","Ada Lovelace","Pune",100.0),
          (11,"2025-12-31 23:45:00","Ben","Mumbai",200.0)])

    verify("P017", """
      CREATE TABLE Orders(OrderID INTEGER PRIMARY KEY,OrderDate TEXT,PaymentID INTEGER,ShipperID INTEGER);
      CREATE TABLE Payments(PaymentID INTEGER PRIMARY KEY,PaymentType TEXT);
      CREATE TABLE Shippers(ShipperID INTEGER PRIMARY KEY,CompanyName TEXT);
      INSERT INTO Payments VALUES(1,'Card'); INSERT INTO Shippers VALUES(1,'FastShip');
      INSERT INTO Orders VALUES(1,'2026-04-10 09:00:00',1,1),(2,'2026-04-04',NULL,NULL),
       (3,'2026-04-03',1,1),(4,'2026-04-10 09:00:00',999,999);
    """, [(4,"2026-04-10 09:00:00","Unknown","Unknown"),
          (1,"2026-04-10 09:00:00","Card","FastShip"),
          (2,"2026-04-04","Unknown","Unknown")])

    verify("P018", """
      CREATE TABLE Customers(CustomerID INTEGER PRIMARY KEY,FirstName TEXT,LastName TEXT,Email TEXT,DateEntered TEXT);
      CREATE TABLE Orders(OrderID INTEGER PRIMARY KEY,CustomerID INTEGER,OrderDate TEXT);
      INSERT INTO Customers VALUES(1,'Ada','A','ada@x','2024-01-01'),
       (2,'Ben','B','ben@x','2024-01-02'),(3,'Cia','C','cia@x','2024-01-03'),
       (4,'Dev','D','dev@x','2024-01-04');
      INSERT INTO Orders VALUES(10,1,'2025-04-02'),(11,2,'2025-04-01'),
       (12,4,'2025-06-30');
    """, [(2,"Ben B","ben@x","2024-01-02"),
          (3,"Cia C","cia@x","2024-01-03")])

    verify("P019", """
      CREATE TABLE Products(ProductID INTEGER PRIMARY KEY,Product TEXT);
      CREATE TABLE OrderDetails(OrderDetailID INTEGER PRIMARY KEY,OrderID INTEGER,ProductID INTEGER,Quantity INTEGER);
      INSERT INTO Products VALUES(1,'Pen'),(2,'Bag');
      INSERT INTO OrderDetails VALUES(1,10,1,2),(2,10,1,3),
       (3,11,2,1),(4,12,999,4);
    """, [(1,"Pen",5,2,1),(999,None,4,1,1),(2,"Bag",1,1,1)])

    assert sqlite3.sqlite_version_info >= (3,39,0), "P026 requires FULL OUTER JOIN SQLite 3.39+"
    verify("P026", """
      CREATE TABLE Category(CategoryID INTEGER PRIMARY KEY,CategoryName TEXT);
      CREATE TABLE Products(ProductID INTEGER PRIMARY KEY,CategoryID INTEGER,Sale_Price REAL);
      CREATE TABLE OrderDetails(OrderDetailID INTEGER PRIMARY KEY,OrderID INTEGER,ProductID INTEGER,Quantity INTEGER);
      INSERT INTO Category VALUES(1,'Drinks'),(2,'Snacks'),(3,'Stationery');
      INSERT INTO Products VALUES(10,1,10),(11,1,8),(20,2,5),(30,99,7);
      INSERT INTO OrderDetails VALUES(1,100,10,2),(2,100,11,1),
       (3,100,20,1),(4,101,30,3),(5,102,999,4);
    """, [("Drinks",1,3,28.0),("Unmapped",1,3,21.0),
          ("Snacks",1,1,5.0),("Stationery",0,0,0),
          ("Unknown product",1,4,None)])
    print("PASS: ten archived JOIN answer cases; no new learner mastery awarded")


if __name__ == "__main__":
    main()
