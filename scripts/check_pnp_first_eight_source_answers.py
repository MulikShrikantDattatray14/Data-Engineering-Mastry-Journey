#!/usr/bin/env python3
"""Source-pinned PNP Q001-Q008 supplied-key and saved-answer checks.

Expected source-sample rows come from archived ILLUSTRATIVE Markdown examples,
not the original PostgreSQL provider dataset. All tests are read-only.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
FILES = {
  1: ("0. SQL basics/P001. Brand directory.md","6daaa2d1453dbaaf28ff43278d45ea0a339b3601"),
  2: ("1. Intro to SQL and Advanced Select/P002. Ten highest-priced products.md","2c33c20b483675b6b73cec8da609b89e391af09d"),
  3: ("1. Intro to SQL and Advanced Select/P003. Customers in metro cities.md","2260186b5eb5dba4b6eeb9d9bbe6cf4c4a3ffa76"),
  4: ("8. Advance string functions, regex and clause/P004. Customer emails that cannot be delivered.md","a79ad97c4bc4417a3c24ae094bf37218a7570cb3"),
  5: ("1. Intro to SQL and Advanced Select/P005. Orders placed in Q1 2025.md","ebebd5c3755712ab9ff69676269eb69be574578f"),
  6: ("11. NULL Logic/P006. Most expensive products that are never discounted.md","777dcceccf731128d314c4dbdb7905c0369c8d6c"),
  7: ("1. Intro to SQL and Advanced Select/P007. Discount amount and percentage per product.md","da19af9f18ffb044c2ef52e7329dceff740e0e81"),
  8: ("1. Intro to SQL and Advanced Select/P008. Price band labels.md","a7821e2ffaa2dca14311e87f2faa042350ad3705"),
}
KEY_PATH = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_HASH = "7912c8e676621c513e0b635a40c6ee299404676e"
SCHEMA = {
 "Products": "CREATE TABLE Products(ProductID INTEGER,Product TEXT,Brand TEXT,Sale_Price REAL,Market_Price REAL)",
 "Customers": "CREATE TABLE Customers(CustomerID INTEGER,FirstName TEXT,LastName TEXT,City TEXT,State TEXT,Email TEXT)",
 "Orders": "CREATE TABLE Orders(OrderID INTEGER,CustomerID INTEGER,OrderDate TEXT,Total_Order_Amount REAL)",
}
# Fixture tuples are manually transcribed from the preserved illustrative rows.
SAMPLES = {
1: ("Products","ProductID Brand",[(1,"Nike"),(2," Nike "),(3,None),(4,""),(5,"   "),(6,"Adidas"),(7,"Puma"),(8,"Adidas")]),
2: ("Products","ProductID Product Brand Sale_Price",[(4,"Mug","Home",100),(20,"Bottle","Home",100),(30,"Sticker","Home",0),(31,"Mystery item","Home",None),(101,"Headphones","Nova",900),(102,"Tablet","Nova",800),(103,"Monitor","Pixel",700),(104,"Keyboard","Typeco",600),(105,"Speaker","Nova",500),(106,"Router","Netco",400),(107,"Camera","Pixel",300),(108,"Mouse","Typeco",200),(109,"Lamp","Home",150)]),
3: ("Customers","CustomerID FirstName LastName City State",[(12,"Asha","Rao"," Bengaluru ","Karnataka"),(5,"Nisha","Shah","MUMBAI","Maharashtra"),(21,"Riya","Patil","Pune","Maharashtra"),(3,"Dev","Kumar","Delhi","Delhi"),(7,"Mira","Das","Bengaluru","Karnataka"),(9,"Farah","Ali"," Chennai ","Tamil Nadu"),(14,"Isha","Kumar","Bangalore","Karnataka"),(6,"Omar","Khan"," Bombay ","Maharashtra"),(8,"Lea","Singh","New Delhi","Delhi")]),
4: ("Customers","CustomerID FirstName LastName Email",[(1,"Asha","Rao",None),(2,"Ben","Das","ben das@example.com"),(3,"Cia","Sen","cia.example.com"),(4,"Dev","Roy","dev@example.com")]),
5: ("Orders","OrderID CustomerID OrderDate Total_Order_Amount",[(1,10,"2024-12-31",50),(2,11,"2025-01-01",100),(3,12,"2025-03-31",200),(4,13,"2025-04-01",300)]),
6: ("Products","ProductID Product Brand Sale_Price Market_Price",[(1,"Mug","Home",100,100),(2,"Lamp","Home",150,150),(3,"Mystery","Home",None,100),(4,"Bottle","Home",90,100)]),
7: ("Products","ProductID Product Market_Price Sale_Price",[(1,"Mug",100,80),(2,"Sticker",0,0),(3,"Lamp",200,150)]),
8: ("Products","ProductID Product Sale_Price",[(1,"Pen",199),(2,"Book",200),(3,"Bag",699.50),(4,"Watch",700),(5,"Mystery",None)]),
}
# Expected result tuples independently typed from each Markdown source sample.
EXPECTED = {
1:[("Adidas",),("Nike",),("Puma",)],
2:[(101,"Headphones","Nova",900),(102,"Tablet","Nova",800),(103,"Monitor","Pixel",700),(104,"Keyboard","Typeco",600),(105,"Speaker","Nova",500),(106,"Router","Netco",400),(107,"Camera","Pixel",300),(108,"Mouse","Typeco",200),(109,"Lamp","Home",150),(4,"Mug","Home",100)],
3:[(14,"Isha","Kumar","Bangalore","Karnataka"),(7,"Mira","Das","Bengaluru","Karnataka"),(12,"Asha","Rao","Bengaluru","Karnataka"),(6,"Omar","Khan","Bombay","Maharashtra"),(9,"Farah","Ali","Chennai","Tamil Nadu"),(3,"Dev","Kumar","Delhi","Delhi"),(5,"Nisha","Shah","MUMBAI","Maharashtra"),(8,"Lea","Singh","New Delhi","Delhi")],
4:[(1,"Asha","Rao",None,"Missing"),(2,"Ben","Das","ben das@example.com","Contains a space"),(3,"Cia","Sen","cia.example.com","Not in name@domain.tld form")],
5:[(2,11,"2025-01-01",100),(3,12,"2025-03-31",200)],
6:[(2,"Lamp","Home",150,150,"Full price"),(1,"Mug","Home",100,100,"Full price")],
7:[(3,"Lamp",200,150,50,25.0),(1,"Mug",100,80,20,20.0),(2,"Sticker",0,0,None,None)],
8:[(1,"Pen",199,"Budget"),(2,"Book",200,"Mid"),(3,"Bag",699.50,"Mid"),(4,"Watch",700,"Premium"),(5,"Mystery",None,"Unknown")],
}
def git_hash(path):
    b = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
def sql_after(text, heading):
    assert text.count(heading) == 1, heading
    ticks = chr(96)*3
    m = re.search(r"(?s)"+ticks+r"sql\s*\n(.*?)\n"+ticks, text.split(heading,1)[1])
    assert m is not None, heading
    return m.group(1).strip()
def equivalent_sql(a,b):
    return " ".join(a.split()) == " ".join(b.split())
def key_query(key,n):
    m = re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)",key)
    assert m, n
    return m.group(1).strip()
def translated(n,sql):
    # 5/6 are PostgreSQL-only syntax, so a translated SQLite diagnostic
    # must NOT be recorded as original PostgreSQL runtime verification.
    if n == 5:
        return re.sub(r"\bDATE\s+'([^']+)'",r"'\1'",sql)
    if n == 6:
        return sql.replace("::text","")
    return sql
def check(got,want,label):
    assert got == want, f"{label}: got {got!r}, expected {want!r}"
def fixture(n):
    table,fields,rows=SAMPLES[n]
    con=sqlite3.connect(":memory:")
    con.execute(SCHEMA[table])
    cols=fields.split()
    con.executemany("INSERT INTO "+table+"("+",".join(cols)+") VALUES("+",".join("?" for _ in cols)+")",rows)
    return con
def run(con,sql):
    return con.execute(sql).fetchall()
def edges(q,off):
    # Eight independent, author-made counterexample groups, not source rows.
    c=sqlite3.connect(":memory:"); c.execute(SCHEMA["Products"])
    c.executemany("INSERT INTO Products(ProductID,Brand) VALUES(?,?)",[(3," Alpha "),(2,"Alpha"),(1,""),(4,None),(5,"Beta")])
    check(run(c,q[1]),[("Alpha",),("Beta",)],"Q1 trim boundary")
    raw=run(c,off[1]); assert len(raw)==3 and (" Alpha ",) in raw and ("Alpha",) in raw,raw
    c.close()
    c=sqlite3.connect(":memory:"); c.execute(SCHEMA["Products"])
    c.executemany("INSERT INTO Products(ProductID,Product,Brand,Sale_Price) VALUES(?,?,?,?)",[(i,f"p{i}","X",100) for i in range(12,0,-1)]+[(99,"missing","X",None)])
    check([r[0] for r in run(c,q[2])],list(range(1,11)),"Q2 top-N ties")
    check(run(c,q[2]),run(c,off[2]),"Q2 key comparison")
    c.close()
    c=sqlite3.connect(":memory:"); c.execute(SCHEMA["Customers"])
    c.executemany("INSERT INTO Customers(CustomerID,FirstName,LastName,City,State) VALUES(?,?,?,?,?)",[(4,"D","R","mumbai","S"),(3,"C","R","BENGALURU","S"),(2,"B","R","Bangalore","S"),(1,"A","R",None,"S"),(5,"E","R"," Pune ","S")])
    check([r[0] for r in run(c,q[3])],[2,3,4],"Q3 cleaned-case sort")
    check([r[0] for r in run(c,off[3])],[3,2,4],"Q3 preserved-key raw-case sort divergence")
    c.close()
    c=sqlite3.connect(":memory:"); c.execute(SCHEMA["Customers"])
    c.executemany("INSERT INTO Customers(CustomerID,FirstName,LastName,Email) VALUES(?,?,?,?)",[(1,"A","Z","  "),(2,"B","Z","x@y.z"),(3,"C","Z","x @y.z"),(4,"D","Z","x@y"),(5,"E","Z",None)])
    check([(r[0],r[-1]) for r in run(c,q[4])],[(1,"Missing"),(3,"Contains a space"),(4,"Not in name@domain.tld form"),(5,"Missing")],"Q4 precedence")
    check(run(c,q[4]),run(c,off[4]),"Q4 key comparison")
    c.close()
    c=sqlite3.connect(":memory:"); c.execute(SCHEMA["Orders"])
    c.executemany("INSERT INTO Orders VALUES(?,?,?,?)",[(1,10,"2024-12-31 23:59:59",1),(2,10,"2025-01-01 00:00:00",2),(3,10,"2025-03-31 23:59:59",3),(4,10,"2025-04-01 00:00:00",4),(5,10,None,5)])
    check([r[0] for r in run(c,q[5])],[2,3],"Q5 timestamps")
    check(run(c,q[5]),run(c,translated(5,off[5])),"Q5 SQLite-translated key diagnostic")
    c.close()
    c=sqlite3.connect(":memory:"); c.execute(SCHEMA["Products"])
    c.executemany("INSERT INTO Products(ProductID,Product,Brand,Sale_Price,Market_Price) VALUES(?,?,?,?,?)",[(1,"missing1","X",None,90),(2,"missing2","X",90,None),(3,"fullzero","X",0,0),(4,"discount","X",90,100),(5,"full","X",120,120)])
    check([r[0] for r in run(c,q[6])],[5,3],"Q6 missing and full-price")
    check(run(c,q[6]),run(c,translated(6,off[6])),"Q6 SQLite-translated key diagnostic")
    c.close()
    c=sqlite3.connect(":memory:"); c.execute(SCHEMA["Products"])
    c.executemany("INSERT INTO Products(ProductID,Product,Market_Price,Sale_Price) VALUES(?,?,?,?)",[(1,"missing",None,5),(2,"zero",0,0),(3,"negative",50,60),(4,"positive",100,50)])
    check([(r[0],r[-2],r[-1]) for r in run(c,q[7])],[(4,50,50.0),(3,-10,-20.0),(1,None,None),(2,None,None)],"Q7 negative/missing/zero")
    check(run(c,q[7]),run(c,off[7]),"Q7 key comparison")
    c.close()
    c=sqlite3.connect(":memory:"); c.execute(SCHEMA["Products"])
    c.executemany("INSERT INTO Products(ProductID,Product,Sale_Price) VALUES(?,?,?)",[(1,"a",199.99),(2,"b",200),(3,"c",699.5),(4,"d",700),(5,"e",None),(6,"f",-1)])
    check([r[-1] for r in run(c,q[8])],["Budget","Mid","Mid","Premium","Unknown","Budget"],"Q8 boundary values")
    check(run(c,q[8]),run(c,off[8]),"Q8 key comparison")
    c.close()
def main():
    assert git_hash(KEY_PATH) == KEY_HASH, "Preserved source key changed"
    key=KEY_PATH.read_text(encoding="utf-8")
    assert key.startswith("-- 100 SQL interview questions: final solutions")
    q,off={},{}
    for n,(path,sha) in FILES.items():
        source=BASE/path
        assert git_hash(source)==sha,f"Q{n} immutable source changed"
        content=source.read_text(encoding="utf-8")
        assert f"# PNP Q{n:03d}." in content
        assert "Illustrative example" in content
        assert "Solved (recorded)" in content
        q[n]=sql_after(content,"## My solution — SQLite")
        off[n]=sql_after(content,"## Official solution")
        assert equivalent_sql(off[n],key_query(key,n)),f"Q{n} copied key does not match source archive"
        c=fixture(n)
        try:
            check(run(c,q[n]),EXPECTED[n],f"Q{n} saved SQL and illustrative sample")
            if n==1:
                # Known failure in archived official key on its OWN illustrative
                # source input. Preserve it as a reproduced discrepancy.
                rows=run(c,off[n])
                assert len(rows)==4 and (" Nike ",) in rows and ("Nike",) in rows,rows
            else:
                check(run(c,translated(n,off[n])),EXPECTED[n],
                      f"Q{n} key sample (translated for PG-only Q5/6)")
        finally:
            c.close()
        print(f"Q{n:03d}: hash, supplied-key excerpt, saved-SQL illustrative replay checked")
    edges(q,off)
    print("PASS: 8 historical-SQL illustrative outputs, 8 independent synthetic groups,")
    print("8 source-key provenance excerpts; 7 key-derived illustrative outputs")
    print("(Q5/Q6 SQLite translations, not native PostgreSQL);")
    print("Q1 official-key raw/trim divergence reproduced, NOT a passing contract.")
if __name__=="__main__":
    main()
