#!/usr/bin/env python3
"""Bounded PNP Q017-Q024 source/key audit. No learner credit or provider grading."""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
)
FILES = {
    17: ("2. Joins/P017. Orders with payment type and shipper.md", "ef18f202ba1b0f9c5a67eeadffb2e1edbbd92855"),
    18: ("2. Joins/P018. Customers with no order in the last 90 days.md", "99aa9cae179fa3fd8f37db42ca89599438207c0d"),
    19: ("2. Joins/P019. Units sold per product.md", "6522a8f6311829759852236f2252b454aefb34df"),
    20: ("12. Dates and Time/P020. Days to ship and days to deliver.md", "4c67d821f100d9fb8a340fbe4a2fb9f0f2b5706c"),
    21: ("3. Sorting and Grouping/P021. Top five customers by number of orders.md", "3c16327cc3d4ab6b5c16d6b5a8bd29b1a5fff499"),
    22: ("3. Sorting and Grouping/P022. Orders with more than eight line items.md", "df7e47951ecb9df9ac44cc904eb503270c95bf6d"),
    23: ("8. Advance string functions, regex and clause/P023. Chocolate or cookie products under 250, excluding sugar-free.md", "720b0e8e7124c63e45d7af5c325b6b29a31a90a8"),
    24: ("11. NULL Logic/P024. Suppliers outside India or with no email.md", "8ba26281be0328894890d8a7015f19a3f617c952"),
}
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_HASH = "7912c8e676621c513e0b635a40c6ee299404676e"

def blobsha(p):
    b = p.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def key_sql(text, n):
    m = re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", text)
    assert m, f"Missing Q{n} supplied key"
    return m.group(1).strip()

def sql_tokens(sql):
    """Compare immutable SQL tokens while ignoring only layout whitespace.

    A SQL string literal (including ' ' inside CONCAT_WS) stays exact.
    """
    return re.findall(r"'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|[A-Za-z_]\\w*|\\d+(?:\\.\\d+)?|::|>=|<=|<>|!=|[^\\s]", sql)

def learner_sql(text):
    s = text.split("## My solution — SQLite", 1)[1].split("### Step-by-step", 1)[0]
    m = re.search(r"(?ms)^" + "\x60"*3 + r"sql\s*\n(.*?)\n" + "\x60"*3, s)
    assert m, "Missing historical SQLite query"
    return m.group(1).strip()

def connection(*ddls):
    c = sqlite3.connect(":memory:")
    c.create_function("CONCAT_WS", -1, lambda sep, *items:
                      None if sep is None else str(sep).join(str(v) for v in items if v is not None))
    for ddl in ddls:
        c.execute(ddl)
    return c

def expect(c, sql, rows, label):
    actual = c.execute(sql).fetchall()
    assert actual == rows, f"{label}: got {actual!r}, expected {rows!r}"

def adapt_pg(n, sql):
    """Explicit SQLite diagnostics only; never claim native PostgreSQL verification."""
    if n == 17:
        old = "(SELECT MAX(latest.OrderDate)::date - 6 FROM Orders AS latest)"
        new = "(SELECT date(MAX(latest.OrderDate), '-6 days') FROM Orders AS latest)"
        assert old in sql
        return sql.replace(old, new)
    if n == 18:
        old = "(SELECT MAX(OrderDate) FROM Orders) - 89"
        new = "date((SELECT MAX(OrderDate) FROM Orders), '-89 days')"
        assert old in sql
        return sql.replace(old, new)
    if n == 20:
        sql, ns = re.subn(r"o\.ShipDate::date\s*-\s*o\.OrderDate::date",
            "CAST(julianday(date(o.ShipDate)) - julianday(date(o.OrderDate)) AS INTEGER)", sql)
        sql, nd = re.subn(r"o\.DeliveryDate::date\s*-\s*o\.OrderDate::date",
            "CAST(julianday(date(o.DeliveryDate)) - julianday(date(o.OrderDate)) AS INTEGER)", sql)
        sql, dates = re.subn(r"\bDATE '([^']+)'", r"'\1'", sql)
        assert (ns, nd, dates) == (1, 1, 2)
        return sql
    if n == 23:
        sql, cnt = re.subn(r"p\.Sub_Category ILIKE", "LOWER(p.Sub_Category) LIKE", sql)
        sql, cnt2 = re.subn(r"p\.Product NOT ILIKE", "LOWER(p.Product) NOT LIKE", sql)
        assert (cnt, cnt2) == (2, 1)
        return sql
    assert n in (19, 22, 24), f"Q{n} needs independent runtime/dialect validation"
    return sql

def rank_equivalent_q21():
    # Auditor-authored SQLite transformation of WITH TIES, NOT the PostgreSQL key.
    return """
    WITH grouped AS (
      SELECT o.CustomerID,
             CASE WHEN c.CustomerID IS NULL THEN 'Unknown customer'
                  ELSE CONCAT_WS(' ', c.FirstName, c.LastName) END AS customer_name,
             COUNT(*) AS orders_placed
      FROM Orders o LEFT JOIN Customers c ON c.CustomerID=o.CustomerID
      GROUP BY o.CustomerID, c.CustomerID, c.FirstName, c.LastName
    ), ranked AS (
      SELECT *, RANK() OVER (ORDER BY orders_placed DESC) AS position
      FROM grouped
    )
    SELECT CustomerID, customer_name, orders_placed
    FROM ranked WHERE position <= 5
    ORDER BY orders_placed DESC, CustomerID
    """

def main():
    assert blobsha(KEY) == KEY_HASH, "Supplied key archive changed"
    keys = KEY.read_text(encoding="utf8")
    records = {}
    for n, (path, pinned) in FILES.items():
        original = BASE / path
        assert blobsha(original) == pinned, f"Q{n}: source changed"
        text = original.read_text(encoding="utf8")
        assert text.startswith(f"# PNP Q{n:03d}.") and "### Sample input and expected output" in text
        assert key_sql(keys, n).upper().startswith("SELECT "), f"Q{n} key missing SELECT"
        if n in (17, 18, 19):
            assert "Solved (recorded)" in text
            assert "## My solution — SQLite" in text
            assert sql_tokens(key_sql(keys, n)) == sql_tokens(
                re.search(r"(?ms)^## Official solution.*?^" + "\x60"*3 + r"sql\s*\n(.*?)\n" + "\x60"*3, text).group(1)
            ), f"Q{n}: public supplied key excerpt differs (non-layout token change)"
        else:
            assert "NOT SOLVED YET" in text
            assert "## My solution — SQLite\n\nPending." in text
            assert "## Official solution\n\nPending" in text
        records[n] = text

    # Q017: exact historical learner query + explicitly adapted supplied-key query.
    c = connection("CREATE TABLE Payments(PaymentID INT, PaymentType TEXT)",
                   "CREATE TABLE Shippers(ShipperID INT, CompanyName TEXT)",
                   "CREATE TABLE Orders(OrderID INT, OrderDate TEXT, PaymentID INT, ShipperID INT)")
    c.execute("INSERT INTO Payments VALUES(1,'UPI')")
    c.execute("INSERT INTO Shippers VALUES(1,'FastShip')")
    c.executemany("INSERT INTO Orders VALUES(?,?,?,?)",
                  [(1,'2025-12-24',1,1),(2,'2025-12-25',1,1),(3,'2025-12-31',None,None)])
    rows = [(3,'2025-12-31','Unknown','Unknown'),(2,'2025-12-25','UPI','FastShip')]
    for q in (learner_sql(records[17]), adapt_pg(17, key_sql(keys, 17))):
        expect(c, q, rows, "Q017 illustrative rows")
    c.execute("INSERT INTO Orders VALUES(4,'2025-12-25',99,99)")
    edge = [(3,'2025-12-31','Unknown','Unknown'),(4,'2025-12-25','Unknown','Unknown'),(2,'2025-12-25','UPI','FastShip')]
    for q in (learner_sql(records[17]), adapt_pg(17, key_sql(keys, 17))):
        expect(c, q, edge, "Q017 unrecognized-code and 7-day boundary")
    c.close()

    # Q018: known inactive customer, never-ordered customer, inclusive 90th day.
    c = connection("CREATE TABLE Customers(CustomerID INT,FirstName TEXT,LastName TEXT,Email TEXT,DateEntered TEXT)",
                   "CREATE TABLE Orders(OrderID INT,CustomerID INT,OrderDate TEXT)")
    c.executemany("INSERT INTO Customers VALUES(?,?,?,?,?)", [
       (1,'Asha','Rao','asha@example.com','2023-01-01'),
       (2,'Ben','Das','ben@example.com','2023-02-01'),
       (3,'Cia','Sen','cia@example.com','2024-01-01')])
    c.executemany("INSERT INTO Orders VALUES(?,?,?)",[(10,1,'2025-03-31'),(11,2,'2024-12-01')])
    rows=[(2,'Ben Das','ben@example.com','2023-02-01'),(3,'Cia Sen','cia@example.com','2024-01-01')]
    for q in (learner_sql(records[18]), adapt_pg(18, key_sql(keys,18))):
        expect(c,q,rows,"Q018 illustrative rows")
    c.executemany("INSERT INTO Customers VALUES(?,?,?,?,?)", [
       (4,'Dee','Ray','dee@example.com','2023-02-15'),
       (5,'Eva','Roy','eva@example.com','2023-03-01')])
    c.executemany("INSERT INTO Orders VALUES(?,?,?)",[(12,4,'2025-01-01'),(13,5,'2024-12-31')])
    edge=[rows[0],(5,'Eva Roy','eva@example.com','2023-03-01'),rows[1]]
    for q in (learner_sql(records[18]), adapt_pg(18, key_sql(keys,18))):
        expect(c,q,edge,"Q018 90th-day inclusion and earlier order")
    c.close()

    # Q019: SQL-key inner join and historical LEFT JOIN agree on referential sample;
    # known original dataset has orphan ProductIDs, so on synthetic orphan they diverge.
    c=connection("CREATE TABLE Products(ProductID INT,Product TEXT)",
                 "CREATE TABLE OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT,Quantity INT)")
    c.executemany("INSERT INTO Products VALUES(?,?)",[(1,'Pen'),(2,'Bag'),(3,'Cup')])
    c.executemany("INSERT INTO OrderDetails VALUES(?,?,?,?)",[(1,10,1,2),(2,11,1,3),(3,11,2,1)])
    rows=[(1,'Pen',5,2,2),(2,'Bag',1,1,1)]
    for q in (learner_sql(records[19]),adapt_pg(19,key_sql(keys,19))):
        expect(c,q,rows,"Q019 illustrative matched product")
    c.execute("INSERT INTO OrderDetails VALUES(4,12,999,4)")
    expect(c,learner_sql(records[19]),[(1,'Pen',5,2,2),(999,None,4,1,1),(2,'Bag',1,1,1)],"Q019 orphan kept by historical learner")
    expect(c,adapt_pg(19,key_sql(keys,19)),rows,"Q019 orphan dropped by supplied key")
    c.close()

    # Q020: supplied-key PostgreSQL date arithmetic explicitly translated to SQLite.
    c=connection("CREATE TABLE Orders(OrderID INT, OrderDate TEXT, ShipDate TEXT, DeliveryDate TEXT)")
    c.executemany("INSERT INTO Orders VALUES(?,?,?,?)",[(1,'2025-11-01','2025-11-03','2025-11-06'),
      (2,'2025-11-02',None,None),(3,'2025-10-31','2025-11-01','2025-11-04')])
    expect(c,adapt_pg(20,key_sql(keys,20)),[(1,'2025-11-01','2025-11-03','2025-11-06',2,5),
       (2,'2025-11-02',None,None,None,None)],"Q020 November illustrative and NULL")
    c.close()

    # Q021 original key FETCH FIRST ... WITH TIES is PostgreSQL-only in this CI.
    assert "FETCH FIRST 5 ROWS WITH TIES" in key_sql(keys,21)
    c=connection("CREATE TABLE Customers(CustomerID INT,FirstName TEXT,LastName TEXT)",
                 "CREATE TABLE Orders(OrderID INT,CustomerID INT)")
    names=[('Asha','Rao'),('Ben','Das'),('Cia','Sen'),('Dev','Roy'),('Ena','Jain'),('Farah','Ali')]
    c.executemany("INSERT INTO Customers VALUES(?,?,?)",[(i,*name) for i,name in enumerate(names,1)])
    c.executemany("INSERT INTO Orders VALUES(?,?)",[(i+10,i) for i in range(1,7)])
    expected=[(i,' '.join(name),1) for i,name in enumerate(names,1)]
    expect(c,rank_equivalent_q21(),expected,"Q021 auditor-translated six-way fifth-place tie")
    c.close()

    # Q022 original key executes unchanged in SQLite.
    c=connection("CREATE TABLE OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT,Quantity INT)")
    c.executemany("INSERT INTO OrderDetails VALUES(?,?,?,?)",
                  [(i,10,i if i<9 else 1,1) for i in range(1,10)]+[(10,11,2,1)])
    expect(c,key_sql(keys,22),[(10,9,8,9)],"Q022 exact source nine-row sample")
    c.close()

    # Q023: PostgreSQL ILIKE explicitly converted to ASCII-case-insensitive SQLite LIKE.
    c=connection("CREATE TABLE Products(ProductID INT,Product TEXT,Sub_Category TEXT,Sale_Price REAL)")
    c.executemany("INSERT INTO Products VALUES(?,?,?,?)",
      [(1,'Cocoa Cookie','Cookies',200),(2,'Sugar-free Choc','Chocolate',150),
       (3,'Tea Biscuit','Biscuits',100),(4,'Dark Bar','CHOCOLATE',249)])
    query=adapt_pg(23,key_sql(keys,23))
    expect(c,query,[(1,'Cocoa Cookie','Cookies',200.0),(4,'Dark Bar','CHOCOLATE',249.0)],"Q023 illustrative")
    c.executemany("INSERT INTO Products VALUES(?,?,?,?)",
      [(5,'cookie jumbo','COOKIE',250),(6,'sugar free cookie','Cookie',199),
       (7,'cookie mint','Cookies',0)])
    expect(c,query,[(7,'cookie mint','Cookies',0.0),(1,'Cocoa Cookie','Cookies',200.0),
                   (4,'Dark Bar','CHOCOLATE',249.0)],"Q023 price/sugar-free boundaries")
    c.close()

    # Q024 exact key SQL with explicit CONCAT_WS compatibility shim, not native PostgreSQL.
    c=connection("CREATE TABLE Suppliers(SupplierID INT,CompanyName TEXT,Country TEXT,Email TEXT)")
    c.executemany("INSERT INTO Suppliers VALUES(?,?,?,?)",
       [(1,'Local Foods','India','local@example.com'),(2,'Global Goods','USA',None),
        (3,'Mystery Supply',None,'mystery@example.com')])
    expect(c,key_sql(keys,24),[(2,'Global Goods','USA',None,'Outside India; No email'),
       (3,'Mystery Supply',None,'mystery@example.com','Country missing')],"Q024 illustrative")
    c.executemany("INSERT INTO Suppliers VALUES(?,?,?,?)",
       [(4,'Blank Country','   ','ok@example.com'),(5,'Blank Email',' INDIA ','  '),
        (6,'Both Missing',None,None)])
    expect(c,key_sql(keys,24),[(2,'Global Goods','USA',None,'Outside India; No email'),
       (3,'Mystery Supply',None,'mystery@example.com','Country missing'),
       (4,'Blank Country','   ','ok@example.com','Outside India'),
       (5,'Blank Email',' INDIA ','  ','No email'),
       (6,'Both Missing',None,None,'Country missing; No email')],"Q024 blank-country semantic mismatch")
    c.close()

    print("PASS: 8 immutable source records/statuses and supplied PostgreSQL key pinned.")
    print("PASS: Q017-020,Q022-024 illustrative contract checks; Q021 auditor-translated tie semantics only.")
    print("PASS: bounded synthetic boundaries; Q019 orphan join and Q024 blank-country differences CONFIRMED.")
    print("NOT VERIFIED: native PostgreSQL, full original dataset/PDF parity, Academy grades or new learner mastery.")

if __name__=="__main__":
    main()
