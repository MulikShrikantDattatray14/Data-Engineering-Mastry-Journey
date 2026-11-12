#!/usr/bin/env python3
"""Read-only partial audit for Advanced SQL A031-A040.

Source-pinned local examples and independently designed edge fixtures.
All candidate SQL except A035's deliberately broken archived query is
AUDITOR-AUTHORED. This script proves neither official solutions nor mastery.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
PINS = {
 "A031": ("6. SubQueries/A031. Customers whose lifetime spend beats the average lifetime spend.md", "c6cff00bb74113b9ec4a43a59542f6474abf2f40", 7),
 "A032": ("6. SubQueries/A032. Each category and its single best-selling product name.md", "664e76fc3d426cf1ea9ad04840862847d31eeeaf", 7),
 "A033": ("6. SubQueries/A033. Orders larger than that customer's own average order.md", "bf1949125ec92270f1a1ed0bb74f3fe0c6a224bd", 7),
 "A034": ("6. SubQueries/A034. Customers who placed at least one order — write it three ways.md", "b188907b69acead999e19e2256ad5fb812d2305d", 8),
 "A035": ("6. SubQueries/A035. Why does this return zero rows, and how do you fix it.md", "249ae7c5f629a258505e46b3f9a44fa2749aa3d6", 8),
 "A036": ("6. SubQueries/A036. Departments with at least one employee earning above 100,000.md", "f92cbe24f967ded03eb01e5eda093a94bfba6468", 8),
 "A037": ("6. SubQueries/A037. Orders that contain any Electronics product.md", "da7c4fe83f06a585c1b7e0142ac3039e68109961", 8),
 "A038": ("6. SubQueries/A038. Customers who have bought every product in the Audio category (rel.md", "bce5e8d3a156c85b8f0bb29540e437e83ccab5be", 8),
 "A039": ("3. Sorting and Grouping/A039. Products bought by more than 10 distinct customers.md", "1f798377ac12922c1f937e29011fc10e5fb3ca1a", 8),
 "A040": ("5. CTEs/A040. Rewrite the spend above average spend query with a CTE defined onc.md", "f3d3e722370834a65b532edd0ecfa36f0227d5f4", 9),
}
SCHEMA = {
 "orders": "CREATE TABLE orders(order_id INTEGER,cust_id INTEGER,amount REAL,status TEXT)",
 "products": "CREATE TABLE products(product_id INTEGER,product_name TEXT,category TEXT)",
 "items": "CREATE TABLE order_items(item_id INTEGER,order_id INTEGER,product_id INTEGER,qty REAL)",
 "customers": "CREATE TABLE customers(cust_id INTEGER,cust_name TEXT)",
 "employees": "CREATE TABLE employees(emp_id INTEGER,emp_name TEXT,manager_id INTEGER,dept_id INTEGER,salary REAL)",
 "departments": "CREATE TABLE departments(dept_id INTEGER,dept_name TEXT)",
}
TARGET = {"items": "order_items"}
SQL = {
 "A031": """WITH spend AS (SELECT cust_id,SUM(amount) total FROM orders
             WHERE cust_id IS NOT NULL GROUP BY cust_id)
             SELECT cust_id,total FROM spend
             WHERE total>(SELECT AVG(total) FROM spend) ORDER BY cust_id""",
 "A032": """WITH units AS (
             SELECT p.product_id,p.product_name,p.category,COALESCE(SUM(i.qty),0) units
             FROM products p LEFT JOIN order_items i ON i.product_id=p.product_id
             GROUP BY p.product_id,p.product_name,p.category),
             ranking AS (SELECT *,ROW_NUMBER() OVER (
               PARTITION BY category ORDER BY units DESC,product_id ASC) rn FROM units)
             SELECT category,product_name FROM ranking WHERE rn=1 ORDER BY category""",
 "A033": """SELECT o.order_id,o.cust_id,o.amount FROM orders o WHERE
             o.amount > (SELECT AVG(x.amount) FROM orders x WHERE x.cust_id=o.cust_id)
             ORDER BY o.order_id""",
 "A034_EXISTS": """SELECT c.cust_id,c.cust_name FROM customers c WHERE EXISTS
             (SELECT 1 FROM orders o WHERE o.cust_id=c.cust_id) ORDER BY c.cust_id""",
 "A034_IN": """SELECT c.cust_id,c.cust_name FROM customers c WHERE c.cust_id
             IN (SELECT o.cust_id FROM orders o) ORDER BY c.cust_id""",
 "A034_JOIN": """SELECT DISTINCT c.cust_id,c.cust_name FROM customers c JOIN orders o
             ON c.cust_id=o.cust_id ORDER BY c.cust_id""",
 "A035_FIX": """SELECT e.emp_id,e.emp_name FROM employees e WHERE NOT EXISTS
             (SELECT 1 FROM employees m WHERE m.manager_id=e.emp_id)
             ORDER BY e.emp_id""",
 "A036": """SELECT d.dept_id,d.dept_name FROM departments d WHERE EXISTS
             (SELECT 1 FROM employees e WHERE e.dept_id=d.dept_id AND e.salary>100000)
             ORDER BY d.dept_id""",
 "A037": """SELECT DISTINCT oi.order_id FROM order_items oi JOIN products p
             ON p.product_id=oi.product_id WHERE p.category='Electronics'
             AND oi.order_id IS NOT NULL ORDER BY oi.order_id""",
 "A038": """SELECT c.cust_id FROM customers c WHERE NOT EXISTS
             (SELECT 1 FROM products p WHERE p.category='Audio' AND NOT EXISTS
                (SELECT 1 FROM orders o JOIN order_items oi ON oi.order_id=o.order_id
                 WHERE o.cust_id=c.cust_id AND oi.product_id=p.product_id))
             ORDER BY c.cust_id""",
 "A039": """SELECT i.product_id,COUNT(DISTINCT o.cust_id) distinct_buyers
             FROM order_items i JOIN orders o ON o.order_id=i.order_id
             WHERE i.product_id IS NOT NULL GROUP BY i.product_id
             HAVING COUNT(DISTINCT o.cust_id)>10 ORDER BY i.product_id""",
 "A040": """WITH spend AS (SELECT cust_id,SUM(amount) lifetime_spend FROM orders
             WHERE cust_id IS NOT NULL GROUP BY cust_id)
             SELECT cust_id,lifetime_spend FROM spend
             WHERE lifetime_spend>(SELECT AVG(lifetime_spend) FROM spend)
             ORDER BY cust_id""",
}

def preserved():
    texts = {}
    for sid,(rel,sha,page) in PINS.items():
        data=(BASE/rel).read_bytes()
        got=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        assert got==sha,(sid,"source blob changed",got)
        t=data.decode("utf-8")
        assert t.startswith("# Advanced Q"+sid[1:]+"."),sid
        assert "question "+str(int(sid[1:]))+", PDF p. "+str(page) in t,sid
        for segment in ("## Question and image","### Sample input and expected output",
                        "## Schema","seven-table","NOT SOLVED YET",
                        "## My solution — SQLite\n\nPending.",
                        "## My solution — SQL Server\n\nPending.",
                        "## Official solution\n\nPending until"):
            assert segment in t,(sid,segment)
        texts[sid]=t
    broken=re.search(r"(?s)\x60\x60\x60sql\s*(SELECT \*.*?;)\s*\x60\x60\x60",texts["A035"])
    assert broken,"A035 original broken SQL code block missing"
    assert "NOT IN (SELECT manager_id FROM employees)" in broken.group(1)
    assert "source does not include the earlier query to rewrite" in texts["A040"]
    print("PASS source identity/pending-state: 10/10 original Git blobs, A035 actual broken SQL, A040 missing predecessor")
    return broken.group(1)

def run(db,sql):
    return db.execute(sql).fetchall()

def fixture(sid,label,rows,expected,broken=None):
    with sqlite3.connect(":memory:") as db:
        for key in rows:
            db.execute(SCHEMA[key])
            vals=rows[key]
            if vals:
                db.executemany("INSERT INTO "+TARGET.get(key,key)+" VALUES ("+
                               ",".join("?" for _ in vals[0])+")",vals)
        if sid=="A034":
            results=[run(db,SQL["A034_"+m]) for m in ("EXISTS","IN","JOIN")]
            assert all(x==expected for x in results),(sid,label,results,expected)
        elif sid=="A035":
            assert broken is not None
            before=run(db,broken)
            assert before==expected[0],(sid,label,"original NULL-sensitive query",before,expected[0])
            after=run(db,SQL["A035_FIX"])
            assert after==expected[1],(sid,label,"reviewer NOT EXISTS",after,expected[1])
        else:
            actual=run(db,SQL[sid])
            assert actual==expected,(sid,label,actual,expected)
    print("PASS",sid,label,"(reviewer SQL only, except A035 observed broken source)")

def main():
    broken=preserved()
    O=lambda oid,cid,amount=0,status=None:(oid,cid,amount,status)
    I=lambda iid,oid,pid,qty=1:(iid,oid,pid,qty)
    fixture("A031","archived local illustration",{"orders":[O(1,10,100),O(2,20,100),O(3,20,200)]},[(20,300)])
    fixture("A031","NULL totals, tied averages and orphan/NULL customer",{"orders":[O(1,1,50),O(2,2,50),O(3,3,200),O(4,4,None),O(5,None,999)]},[(3,200)])
    fixture("A032","archived local units illustration",{"products":[(101,"Speaker","Audio"),(102,"Headphones","Audio"),(103,"Kettle","Home")],
         "items":[I(1,1,101,2),I(2,1,102,3),I(3,1,103,1)]},[("Audio","Headphones"),("Home","Kettle")])
    fixture("A032","ties and unsold products: reviewer lowest-ID policy",{"products":[(1,"First","Audio"),(2,"Second","Audio"),(3,"Lamp","Home"),(4,"Other","Home")],
         "items":[I(1,1,1,2),I(2,1,2,2)]},[("Audio","First"),("Home","Lamp")])
    fixture("A033","archived local illustration",{"orders":[O(1,10,100),O(2,10,200),O(3,20,50)]},[(2,10,200)])
    fixture("A033","same-customer ties, NULL and one-order customer",{"orders":[O(1,10,100),O(2,10,100),O(3,10,400),O(4,20,None),O(5,30,50),O(6,None,999)]},[(3,10,400)])
    fixture("A034","archived local illustration, all three approaches",{"customers":[(10,"Asha"),(20,"Bela")],"orders":[O(1,10),O(2,10)]},[(10,"Asha")])
    fixture("A034","duplicate orders, unlinked customers and NULL foreign keys",{"customers":[(10,"Asha"),(20,"Bela"),(30,"Cara")],
         "orders":[O(1,10),O(2,10),O(3,999),O(4,None),O(5,30)]},[(10,"Asha"),(30,"Cara")])
    fixture("A035","archived source NULL poison demonstration",{"employees":[(1,"Boss",None,1,0),(2,"Ada",1,1,0),(3,"Ben",1,1,0)]},([],[(2,"Ada"),(3,"Ben")]),broken)
    fixture("A035","no NULL managers: original coincidentally works",{"employees":[(1,"A",2,1,0),(2,"B",1,1,0),(3,"C",1,1,0)]},([(3,"C",1,1,0)],[(3,"C")]),broken)
    fixture("A036","archived local illustration",{"departments":[(10,"Sales"),(20,"Support")],
         "employees":[(1,"A",None,10,120000),(2,"B",None,10,80000),(3,"C",None,20,90000)]},[(10,"Sales")])
    fixture("A036","strict salary bound, NULL salary and orphan department",{"departments":[(10,"Sales"),(20,"Support"),(30,"Design")],
         "employees":[(1,"A",None,10,100000),(2,"B",None,10,None),(3,"C",None,20,100001),(4,"D",None,999,200000)]},[(20,"Support")])
    fixture("A037","archived local illustration",{"products":[(101,"Phone","Electronics"),(102,"Pan","Home")],
         "items":[I(1,10,101),I(2,10,102),I(3,20,102)]},[(10,)])
    fixture("A037","duplicate electronics and orphan category/NULL order",{"products":[(101,"Phone","Electronics"),(102,"TV","Electronics"),(103,"Cup","Home")],
         "items":[I(1,10,101),I(2,10,102),I(3,11,999),I(4,12,103),I(5,None,101)]},[(10,)])
    fixture("A038","archived local illustration (customer fixture inferred from IDs)",{"customers":[(10,"A"),(20,"B")],
         "products":[(101,"Earbud","Audio"),(102,"Speaker","Audio"),(103,"Kettle","Home")],
         "orders":[O(1,10),O(2,20)],"items":[I(1,1,101),I(2,1,102),I(3,2,101)]},[(10,)])
    fixture("A038","duplicate purchases and no Audio: vacuous truth reviewer policy",{"customers":[(10,"A"),(20,"B")],
         "products":[(103,"Kettle","Home")],"orders":[O(1,10),O(2,20)],
         "items":[I(1,1,103),I(2,1,103)]},[(10,),(20,)])
    eleven=[O(i,i) for i in range(1,12)]
    fixture("A039","archived 11-distinct-customer illustration",{"orders":eleven,
         "items":[I(i,i,101) for i in range(1,12)]},[(101,11)])
    fixture("A039","10 versus 11 buyers; repeat orders/NULL buyer do not inflate",{"orders":[O(i,i) for i in range(1,12)]+[O(12,1),O(13,None)],
         "items":[I(i,i,101) for i in range(1,14)]+[I(i+20,i,102) for i in range(1,11)]},[(101,11)])
    fixture("A040","archived local CTE illustration (same output as A031)",{"orders":[O(1,10,100),O(2,20,100),O(3,20,200)]},[(20,300)])
    fixture("A040","empty Orders: no ordering-customer average",{"orders":[]},[])
    print("PARTIAL PASS: 10 statement inspections + 20 bounded SQLite groups; A035 original broken query reproduced. NO provider PDF answer verified, native MySQL, original datasets, independent learner solves or mastery.")

if __name__=="__main__":
    main()
