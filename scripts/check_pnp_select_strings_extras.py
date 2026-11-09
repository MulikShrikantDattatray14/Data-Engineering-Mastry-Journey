"""Review original archived SELECT SQL with independent in-memory SQLite data.

All test data are auditor-authored, not the original PNP dataset. The saved
learner SQL is extracted unchanged from preserved question Markdown. Additional
reviewer queries are NEVER attributed to a learner or official answer key.
"""
from pathlib import Path
from urllib.parse import unquote
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "01. SQL Mastery" / "PNP-PROBLEM-INDEX.md"


def archived_sql(pid, heading="My solution — SQLite"):
    rows = [row for row in INDEX.read_text(encoding="utf-8").splitlines()
            if row.startswith("| " + pid + " |")]
    assert len(rows) == 1, pid
    link = re.search(r"\]\(<([^>]+)>\)", rows[0])
    assert link, pid
    file = (INDEX.parent / unquote(link.group(1))).resolve()
    assert file.is_relative_to(ROOT), (pid, "unsafe source path")
    body = file.read_text(encoding="utf-8")
    section = re.search(r"^## " + re.escape(heading) +
                        r"\s*\n([\s\S]*?)(?=^## |\Z)", body, re.M)
    assert section, (pid, heading)
    fence = re.escape(chr(96) * 3)
    code = re.search(fence + r"sql\s*\n(.*?)" + fence, section.group(1), re.S)
    assert code, (pid, "no saved SQL")
    return code.group(1).strip()


def rows(setup, query):
    with sqlite3.connect(":memory:") as db:
        db.executescript(setup)
        return db.execute(query).fetchall()


def check(pid, setup, expected):
    actual = rows(setup, archived_sql(pid))
    assert actual == expected, (pid, actual, expected)
    print("PASS", pid, "archived SQLite SQL vs independent synthetic rows")


def main():
    p001 = """
    CREATE TABLE Products(ProductID INTEGER,Brand TEXT);
    INSERT INTO Products VALUES
      (1,'Nike'),(2,' Nike '),(3,NULL),(4,''),(5,'  '),
      (6,'Adidas'),(7,'Adidas');
    """
    check("P001",p001,[('Adidas',),('Nike',)])
    official_excerpt = rows(p001, archived_sql("P001","Official solution"))
    assert official_excerpt == [(' Nike ',),('Adidas',),('Nike',)], official_excerpt
    print("PASS P001 archived official-excerpt / learner SELECT-DISTINCT mismatch reproduced")

    check("P002", """
    CREATE TABLE Products(ProductID INTEGER,Product TEXT,Brand TEXT,Sale_Price REAL);
    INSERT INTO Products VALUES
      (2,'Two','B',100),(1,'One','B',100),(3,'Three','B',0),
      (50,'Missing','B',NULL),
      (11,'A','X',1000),(12,'B','X',900),(13,'C','X',800),
      (14,'D','X',700),(15,'E','X',600),(16,'F','X',500),
      (17,'G','X',400),(18,'H','X',300),(19,'I','X',200);
    """, [(i,chr(54+i),'X',float(1200-100*(i-9))) for i in range(11,20)] +
         [(1,'One','B',100.0)])

    check("P003", """
    CREATE TABLE Customers(CustomerID INTEGER,FirstName TEXT,LastName TEXT,
                           City TEXT,State TEXT);
    INSERT INTO Customers VALUES
      (1,'A','One',' mUmBaI ','MH'),(2,'B','Two','Pune','MH'),
      (3,'C','Three','Bangalore','KA'),(4,'D','Four','Bengaluru','KA'),
      (5,'E','Five',' Bombay ','MH'),(6,'F','Six','New Delhi','DL');
    """, [(3,'C','Three','Bangalore','KA'),(4,'D','Four','Bengaluru','KA'),
          (5,'E','Five','Bombay','MH'),(1,'A','One','mUmBaI','MH'),
          (6,'F','Six','New Delhi','DL')])

    check("P005", """
    CREATE TABLE Orders(OrderID INTEGER,CustomerID INTEGER,OrderDate TEXT,
                        Total_Order_Amount REAL);
    INSERT INTO Orders VALUES
      (5,1,'2025-04-01',50),(1,1,'2024-12-31 23:59:59',10),
      (4,2,'2025-03-31 23:59:59',40),
      (3,2,'2025-01-01 09:00:00',30),
      (2,1,'2025-01-01 09:00:00',20);
    """, [(2,1,'2025-01-01 09:00:00',20.0),
          (3,2,'2025-01-01 09:00:00',30.0),
          (4,2,'2025-03-31 23:59:59',40.0)])

    # P007's actual archived query has no ProductID tie-breaker. Compare equal
    # percentages unordered; this fixture cannot certify deterministic ties.
    actual = rows("""
    CREATE TABLE Products(ProductID INTEGER,Product TEXT,
                          Market_Price REAL,Sale_Price REAL);
    INSERT INTO Products VALUES (1,'A',100,80),(2,'B',0,0),
      (3,'C',200,150),(4,'D',NULL,80),(5,'E',50,40);
    """, archived_sql("P007"))
    assert actual[0] == (3,'C',200.0,150.0,50.0,25.0),actual
    assert set(actual[1:3]) == {(1,'A',100.0,80.0,20.0,20.0),
                                 (5,'E',50.0,40.0,10.0,20.0)},actual
    assert set(actual[3:]) == {(2,'B',0.0,0.0,None,None),
                                (4,'D',None,80.0,None,None)},actual
    print("PASS P007 saved query arithmetic and NULL; nondeterministic ties flagged")

    check("P008", """
    CREATE TABLE Products(ProductID INTEGER,Product TEXT,Sale_Price REAL);
    INSERT INTO Products VALUES
      (1,'Budget',199.99),(2,'MidMin',200),(3,'MidMax',699.5),
      (4,'Premium',700),(5,'Missing',NULL);
    """, [(1,'Budget',199.99,'Budget'),(2,'MidMin',200.0,'Mid'),
          (3,'MidMax',699.5,'Mid'),(4,'Premium',700.0,'Premium'),
          (5,'Missing',None,'Unknown')])

    # The next four queries are auditor-authored. P023 and X002/X004/X005
    # have NO submitted learner answers; extras have NO supplied answer key.
    sweets = rows("""
    CREATE TABLE Products(ProductID INTEGER,Product TEXT,Sub_Category TEXT,Sale_Price REAL);
    INSERT INTO Products VALUES
      (1,'Cocoa Cookie','Cookies',200),(2,'Sugar-free Choc','Chocolate',150),
      (3,'Tea Biscuit','Biscuits',100),(4,'Dark Bar','CHOCOLATE',249),
      (5,'sugar free snack','cookies',100),(6,'Expensive','Chocolate',250),
      (7,NULL,'Cookie',50);
    """, """
    SELECT ProductID FROM Products
    WHERE (LOWER(COALESCE(Sub_Category,'')) LIKE '%chocolate%'
        OR LOWER(COALESCE(Sub_Category,'')) LIKE '%cookie%')
      AND Sale_Price < 250 AND Product IS NOT NULL
      AND LOWER(Product) NOT LIKE '%sugar-free%'
      AND LOWER(Product) NOT LIKE '%sugar free%'
    ORDER BY Sale_Price,ProductID;
    """)
    assert sweets == [(1,),(4,)],sweets
    print("PASS P023 reviewer-only filter; sugar-free spelling policy unresolved")

    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE Products(ProductID INTEGER,Brand TEXT,Rating REAL)")
        db.executemany("INSERT INTO Products VALUES(?,?,?)",
                       [(i,'Alpha',4.0) for i in range(1,21)] +
                       [(21,'Alpha',None),(22,'Beta',5.0)])
        rated = db.execute("""
          SELECT Brand,COUNT(Rating),ROUND(AVG(Rating),2)
          FROM Products GROUP BY Brand
          HAVING COUNT(Rating)>=20 ORDER BY Brand;
        """).fetchall()
    assert rated == [('Alpha',20,4.0)],rated
    print("PASS X002 reviewer-only rated COUNT denominator; no official key")

    bands = rows("""
    CREATE TABLE Products(ProductID INTEGER,Rating REAL);
    CREATE TABLE OrderDetails(OrderDetailID INTEGER,ProductID INTEGER,Quantity INTEGER);
    INSERT INTO Products VALUES (1,2.5),(2,3.5),(3,4.0),(4,NULL),(5,4.5);
    INSERT INTO OrderDetails VALUES (11,1,2),(12,2,4),(13,3,3),(14,3,3),(15,5,2);
    """, """
    WITH per_product AS (
      SELECT p.ProductID,p.Rating,COALESCE(SUM(d.Quantity),0) units
      FROM Products p LEFT JOIN OrderDetails d ON p.ProductID=d.ProductID
      GROUP BY p.ProductID,p.Rating
    ), labeled AS (
      SELECT CASE WHEN Rating IS NULL THEN 'unrated'
                  WHEN Rating<3 THEN 'below 3'
                  WHEN Rating<4 THEN '3 to below 4'
                  ELSE '4 and above' END band,units FROM per_product
    )
    SELECT band,COUNT(*),ROUND(AVG(units),2)
    FROM labeled GROUP BY band ORDER BY band;
    """)
    assert bands == [('3 to below 4',1,4.0),('4 and above',2,4.0),
                     ('below 3',1,2.0),('unrated',1,0.0)],bands
    print("PASS X004 reviewer-only per-product average; no official key")

    unused = rows("""
    CREATE TABLE Products(ProductID INTEGER,Product TEXT,Rating REAL);
    CREATE TABLE OrderDetails(OrderDetailID INTEGER,ProductID INTEGER);
    INSERT INTO Products VALUES (1,'A',4.0),(2,'B',5.0),(3,'C',NULL);
    INSERT INTO OrderDetails VALUES (11,2),(12,999);
    """, """
    SELECT p.ProductID,p.Product,p.Rating FROM Products p
    WHERE p.Rating IS NOT NULL AND NOT EXISTS (
      SELECT 1 FROM OrderDetails d WHERE d.ProductID=p.ProductID
    ) ORDER BY p.ProductID;
    """)
    assert unused == [(1,'A',4.0)],unused
    print("PASS X005 reviewer-only rated-not-ordered; no official key")
    print("10 fixture groups passed: six archived learner SQL, four reviewer queries.")
    print("One extra P001 excerpt mismatch reproduced. No official-dataset signoff.")


if __name__ == "__main__":
    main()
