#!/usr/bin/env python3
"""SHA-pinned bounded PNP Q009-Q016 audit; no learner credit for pending Q009-Q014."""
import hashlib,re,sqlite3
from pathlib import Path
B=Path(__file__).resolve().parents[1]/"99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
F={
9:("3. Sorting and Grouping/P009. Check how Active and Allowed are encoded.md","f05436e3324db07b77b278e3db0caeafe3d68dc8"),
10:("4. Aggregation/P010. Headline order KPIs.md","00d89791c3250cc2667bdda00964cfb6a674e9bc"),
11:("4. Aggregation/P011. How much of the catalogue has ever sold.md","f8d950741d1020668a7c421b6bdc869ffc4fdbb0"),
12:("4. Aggregation/P012. Price and discount statistics per category ID.md","603612b78b5012fab45736509e900be6b449b19c"),
13:("3. Sorting and Grouping/P013. States with at least five customers.md","bd16f49572bc74b52b88f914287d5b218786c08f"),
14:("3. Sorting and Grouping/P014. Orders per month in 2025.md","4f9f75bac8eed5f2b0cc6de6c625e5c0e3b25700"),
15:("2. Joins/P015. Product count for every category.md","1a7920340ec3b70b7c84d429c0c334d11c0e6e55"),
16:("2. Joins/P016. December 2025 orders with customer names.md","b7a9ad139303eb84aec0fef9772c34028de12f4c")}
K=B/"Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
def sha(p):
 b=p.read_bytes()
 return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
def keyq(k,n):
 m=re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)",k)
 assert m,f"Q{n} missing supplied key"
 return m.group(1).strip()
def fence(s,h,end=None):
 assert s.count(h)==1
 t=s.split(h,1)[1]
 if end:t=t.split(end,1)[0]
 tick=chr(96)*3
 return [q.strip() for q in re.findall(r"(?ms)^"+tick+r"sql\s*\n(.*?)\n"+tick,t)]
def db(*dd):
 c=sqlite3.connect(":memory:")
 for x in dd:c.execute(x)
 return c
def check(c,q,w,label):
 a=c.execute(q).fetchall()
 assert a==w,f"{label}: {a!r} != {w!r}"
def main():
 assert sha(K)=="7912c8e676621c513e0b635a40c6ee299404676e"
 k=K.read_text(encoding="utf8")
 docs={}
 for n,(p,h) in F.items():
  path=B/p
  assert sha(path)==h,f"Q{n} source changed"
  t=path.read_text(encoding="utf8")
  assert t.startswith(f"# PNP Q{n:03d}.") and "Illustrative example" in t
  if n<=14:
   assert "NOT SOLVED YET" in t and "## My solution — SQLite\n\nPending." in t
   assert "## Official solution\n\nPending" in t
  else:
   assert "Solved (recorded)" in t
   assert " ".join(fence(t,"## Official solution")[0].split())==" ".join(keyq(k,n).split())
  docs[n]=t
 c=db("CREATE TABLE Category(CategoryID INT,Active TEXT)","CREATE TABLE Payments(PaymentID INT,Allowed TEXT)")
 c.executemany("INSERT INTO Category VALUES(?,?)",[(1,"1"),(2,"1"),(3,"0"),(4,None)])
 c.executemany("INSERT INTO Payments VALUES(?,?)",[(1,"Y"),(2,"N"),(3,"N")])
 assert set(c.execute(keyq(k,9)))=={("Category","Active","1",2),("Category","Active","0",1),("Category","Active",None,1),("Payments","Allowed","Y",1),("Payments","Allowed","N",2)}
 c.close()
 c=db("CREATE TABLE Orders(OrderID INT,CustomerID INT,OrderDate TEXT,Total_Order_Amount REAL)")
 c.executemany("INSERT INTO Orders VALUES(?,?,?,?)",[(1,10,"2025-01-01",100),(2,10,"2025-01-02",200),(3,20,"2025-01-03",300)])
 check(c,keyq(k,10),[(3,2,600.0,200.0,"2025-01-01","2025-01-03")],"Q010 source sample")
 c.close()
 c=db("CREATE TABLE Products(ProductID INT)","CREATE TABLE OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT)")
 c.executemany("INSERT INTO Products VALUES(?)",[(1,),(2,),(3,)])
 c.executemany("INSERT INTO OrderDetails VALUES(?,?,?)",[(1,10,1),(2,11,1),(3,11,2)])
 check(c,keyq(k,11),[(4,3,3,2,66.67)],"Q011 source sample")
 c.close()
 c=db("CREATE TABLE Products(ProductID INT,CategoryID INT,Sale_Price REAL,Market_Price REAL)")
 c.executemany("INSERT INTO Products VALUES(?,?,?,?)",[(1,10,80,100),(2,10,100,100)])
 check(c,keyq(k,12),[(10,2,80.0,100.0,90.0,1,10.0)],"Q012 source sample")
 c.close()
 c=db("CREATE TABLE Customers(CustomerID INT,State TEXT)")
 c.executemany("INSERT INTO Customers VALUES(?,?)",[(i,"Karnataka") for i in range(1,6)]+[(6,"Maharashtra")])
 check(c,keyq(k,13),[("Karnataka",5)],"Q013 source sample")
 c.close()
 q14=keyq(k,14)
 t14=q14.replace("DATE_TRUNC('month', o.OrderDate)::date","date(substr(o.OrderDate,1,7) || '-01')")
 t14=re.sub(r"\bDATE '([^']+)'",r"'\1'",t14)
 assert t14!=q14,"Q014 PG translation missing"
 c=db("CREATE TABLE Orders(OrderID INT,OrderDate TEXT,Total_Order_Amount REAL)")
 c.executemany("INSERT INTO Orders VALUES(?,?,?)",[(1,"2025-01-01",100),(2,"2025-01-31",50),(3,"2025-03-01",200),(4,"2024-12-01",300)])
 check(c,t14,[("2025-01-01",2,150.0),("2025-03-01",1,200.0)],"Q014 SQLite translated sample")
 c.close()
 q15=fence(docs[15],"## My solution — SQLite","## My solution — SQL Server")[0]
 c=db("CREATE TABLE Category(CategoryID INT,CategoryName TEXT)","CREATE TABLE Products(ProductID INT,CategoryID INT)")
 c.executemany("INSERT INTO Category VALUES(?,?)",[(1,"Snacks"),(2,"Toys")])
 c.executemany("INSERT INTO Products VALUES(?,?)",[(10,1),(11,1)])
 for q in (q15,keyq(k,15)):
  check(c,q,[(2,"Toys",0),(1,"Snacks",2)],"Q015 saved/key source sample")
 c.close()
 q16=fence(docs[16],"## My solution — SQLite","## My solution — SQL Server")
 assert len(q16)==2
 c=db("CREATE TABLE Customers(CustomerID INT,FirstName TEXT,LastName TEXT,City TEXT)","CREATE TABLE Orders(OrderID INT,CustomerID INT,OrderDate TEXT,Total_Order_Amount REAL)")
 c.execute("INSERT INTO Customers VALUES(1,'Anu','Sen',' Delhi ')")
 c.executemany("INSERT INTO Orders VALUES(?,?,?,?)",[(10,1,"2025-12-01",100),(11,1,"2026-01-01",150)])
 for q in q16:
  check(c,q,[(10,"2025-12-01","Anu Sen","Delhi",100.0)],"Q016 saved learner source sample")
 c.close()
 # Independent synthetic counterexamples, not provider sample rows.
 c=db("CREATE TABLE Customers(CustomerID INT,State TEXT)")
 c.executemany("INSERT INTO Customers VALUES(?,?)",[(i,None) for i in range(1,6)]+[(i," ") for i in range(6,11)])
 check(c,keyq(k,13),[("",5),("Unknown",5)],"Q013 blank-vs-NULL ambiguity")
 c.close()
 c=db("CREATE TABLE Products(ProductID INT)","CREATE TABLE OrderDetails(OrderDetailID INT,OrderID INT,ProductID INT)")
 check(c,keyq(k,11),[(0,0,0,0,None)],"Q011 zero-denominator boundary")
 c.close()
 c=db("CREATE TABLE Category(CategoryID INT,CategoryName TEXT)","CREATE TABLE Products(ProductID INT,CategoryID INT)")
 c.executemany("INSERT INTO Category VALUES(?,?)",[(1,"A"),(2,"B"),(3,"C")])
 c.executemany("INSERT INTO Products VALUES(?,?)",[(1,1),(2,2),(3,999)])
 check(c,q15,[(3,"C",0),(1,"A",1),(2,"B",1)],"Q015 tie, zero, orphan")
 c.close()
 c=db("CREATE TABLE Customers(CustomerID INT,FirstName TEXT,LastName TEXT,City TEXT)","CREATE TABLE Orders(OrderID INT,CustomerID INT,OrderDate TEXT,Total_Order_Amount REAL)")
 c.executemany("INSERT INTO Customers VALUES(?,?,?,?)",[(1,"A",None," Pune "),(2,None,"K","Mumbai")])
 c.executemany("INSERT INTO Orders VALUES(?,?,?,?)",[(1,1,"2025-11-30 23:59:59",1),(2,1,"2025-12-01 00:00:00",2),(3,2,"2025-12-31 23:59:59",3),(4,2,"2026-01-01 00:00:00",4),(5,999,"2025-12-30",5)])
 for q in q16:
  check(c,q,[(2,"2025-12-01 00:00:00","A","Pune",2.0),(3,"2025-12-31 23:59:59","K","Mumbai",3.0)],"Q016 timestamp/nullable-name/orphan")
 c.close()
 print("PASS: eight unchanged sources and statuses, eight illustrative contracts, four synthetic boundary groups.")
 print("Q009-014: pending/ungraded. Q014 PostgreSQL syntax translated for SQLite. No full dataset or provider grade.")
if __name__=="__main__":main()
