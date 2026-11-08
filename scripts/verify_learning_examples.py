"""Regression checks for representative original teaching examples (not learner mastery)."""
import sqlite3

def run_sql_examples():
    db = sqlite3.connect(":memory:")
    db.executescript("""
    CREATE TABLE Customers(CustomerID INTEGER PRIMARY KEY, Name TEXT);
    CREATE TABLE Orders(OrderID INTEGER PRIMARY KEY, CustomerID INTEGER, Amount INTEGER);
    INSERT INTO Customers VALUES(1,'Asha'),(2,'Ravi');
    INSERT INTO Orders VALUES(101,1,300),(102,1,700),(103,2,450);
    """)
    got=db.execute("""
      SELECT OrderID,Amount FROM Orders WHERE Amount>=400
      ORDER BY Amount DESC,OrderID
    """).fetchall()
    assert got==[(102,700),(103,450)], got

    db.executescript("""
    CREATE TABLE Logins(user_id INT,login_date TEXT);
    INSERT INTO Logins VALUES
    (1,'2025-01-01'),(1,'2025-01-02'),(1,'2025-01-03'),
    (1,'2025-01-05'),(1,'2025-01-06'),(2,'2025-01-01'),(2,'2025-01-03');
    """)
    got=db.execute("""
    WITH unique_days AS (
      SELECT DISTINCT user_id,login_date FROM Logins
    ), numbered AS (
      SELECT user_id,login_date,
      ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) rn
      FROM unique_days
    ), islands AS (
      SELECT user_id,login_date,
      date(login_date,'-'||rn||' day') island_key
      FROM numbered
    )
    SELECT user_id,MIN(login_date),MAX(login_date),COUNT(*)
    FROM islands GROUP BY user_id,island_key ORDER BY user_id,MIN(login_date)
    """).fetchall()
    expected=[(1,'2025-01-01','2025-01-03',3),(1,'2025-01-05','2025-01-06',2),
              (2,'2025-01-01','2025-01-01',1),(2,'2025-01-03','2025-01-03',1)]
    assert got==expected,got

    db.executescript("""
    CREATE TABLE Sales(sale_id INTEGER,category TEXT,amount INTEGER);
    INSERT INTO Sales VALUES(1,'Home',200),(2,'Home',100),(3,'Books',100);
    """)
    got=db.execute("""
    WITH category_revenue AS (
      SELECT category,SUM(amount) revenue FROM Sales GROUP BY category
    )
    SELECT category,revenue,
           ROUND(100.0*revenue/SUM(revenue) OVER (),1)
    FROM category_revenue ORDER BY revenue DESC,category
    """).fetchall()
    assert got==[('Home',300,75.0),('Books',100,25.0)],got

    db.executescript("""
    CREATE TABLE RawOrders(ingestion_id INT,order_id INT,updated_at TEXT,status TEXT,amount INT);
    INSERT INTO RawOrders VALUES
      (1,101,'2025-03-01 10:00','PAID',100),
      (2,101,'2025-03-01 11:00','paid',120),
      (3,102,'2025-03-02 09:00','failed',-5),
      (4,103,'2025-03-02 10:00',' paid ',200);
    """)
    got=db.execute("""
    WITH ranked AS (
      SELECT *,ROW_NUMBER() OVER (
        PARTITION BY order_id ORDER BY updated_at DESC,ingestion_id DESC
      ) rn FROM RawOrders
    ), latest AS (
      SELECT order_id,lower(trim(status)) clean_status,amount
      FROM ranked WHERE rn=1
    )
    SELECT order_id,clean_status,amount FROM latest
    WHERE clean_status='paid' AND amount>=0 ORDER BY order_id
    """).fetchall()
    assert got==[(101,'paid',120),(103,'paid',200)],got

    db.executescript("""
    CREATE TABLE Products(ProductID INT,Product TEXT,Brand TEXT,Sale_Price INT,Market_Price INT);
    INSERT INTO Products VALUES
      (1,'Mug','Home',100,100),(2,'Lamp','Home',150,150),
      (3,'Mystery','Home',NULL,100),(4,'Bottle','Home',90,100);
    """)
    got=db.execute("""
    SELECT ProductID,Product,Brand,Sale_Price,Market_Price,
      CASE WHEN Market_Price=Sale_Price THEN 'Full price' END discount_display
    FROM Products WHERE Market_Price IS NOT NULL
      AND Sale_Price IS NOT NULL AND Market_Price-Sale_Price==0
    ORDER BY Sale_Price DESC,ProductID ASC LIMIT 10
    """).fetchall()
    assert got==[(2,'Lamp','Home',150,150,'Full price'),
                 (1,'Mug','Home',100,100,'Full price')],got

def run_python_examples():
    sales=[100,200,300,400,500,600,700]
    assert sales[::2]==[100,300,500,700]
    assert sales[::-1]==[700,600,500,400,300,200,100]
    assert "  PAID ".strip().lower()=="paid"
    assert "101,Pune,2500".split(",")==["101","Pune","2500"]
    assert -13//4==-4 and -13%4==3
    ids={10,20,30,20,10}
    ids.add(40)
    assert len(ids)==4 and (20 in ids) and (50 not in ids)
    transaction=(101,"SUCCESS",2500,"INR")
    assert transaction[:2]+(3000,)+transaction[3:]==(101,"SUCCESS",3000,"INR")
    raw=[1200,1500,-300,1800,0,2200]
    assert [x for x in raw if x>0]==[1200,1500,1800,2200]

if __name__=="__main__":
    run_sql_examples()
    run_python_examples()
    print("PASS: 5 SQL worked results and Python fundamentals verified; no mastery credit awarded.")
