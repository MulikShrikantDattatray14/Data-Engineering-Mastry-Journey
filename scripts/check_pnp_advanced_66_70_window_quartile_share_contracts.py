#!/usr/bin/env python3
"""Reviewer-only source-pinned PNP A066-A070 SQLite contracts; not official keys or learner answers."""
from contextlib import closing
from itertools import product
from pathlib import Path
import hashlib
import sqlite3
import unittest

BASE=Path(__file__).resolve().parents[1]/("99. Reference Materials/Original Mastery Snapshot/"
"1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/9. Windowing Functions")
PINS={
"A066":("A066. Show the difference between ROWS and RANGE when values tie.md","67ae69cbbdaee250db53057171ab3482ccb108f9",13),
"A067":("A067. Running total that resets at the start of every month.md","d9ad182199cd687c0fdfaaf846575b1d6aaa3f90",13),
"A068":("A068. Each order against the biggest order seen so far for that customer.md","130c2d5e7f9efc5f7a0afd073618f4f04b98f3eb",13),
"A069":("A069. Split customers into four spend quartiles.md","518a30fa3c649e61d29ed1326741d2b24537c0ec",14),
"A070":("A070. Each category's share of total revenue, as a percentage.md","289da2f3137fe948b437a414a00754a5a7109cab",14)}
PEERS="""SELECT order_id,amount,
 SUM(amount) OVER (ORDER BY amount,order_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),
 SUM(amount) OVER (ORDER BY amount RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
 FROM orders ORDER BY amount,order_id"""
MONTH="""SELECT order_id,order_date,amount,
 SUM(amount) OVER (PARTITION BY substr(order_date,1,7) ORDER BY order_date,order_id
 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
 FROM orders WHERE order_date IS NOT NULL ORDER BY order_date,order_id"""
MAXSOFAR="""WITH r AS (SELECT order_id,cust_id,order_date,amount,
 MAX(amount) OVER (PARTITION BY cust_id ORDER BY order_date,order_id
 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS mx FROM orders)
 SELECT order_id,cust_id,amount,mx,amount-mx FROM r ORDER BY cust_id,order_date,order_id"""
TILES="""WITH spend AS (SELECT cust_id,SUM(amount) AS total FROM orders
 WHERE cust_id IS NOT NULL GROUP BY cust_id)
 SELECT cust_id,total,NTILE(4) OVER (ORDER BY total DESC,cust_id)
 FROM spend ORDER BY total DESC,cust_id"""
SHARES="""WITH revenue AS (SELECT p.category,SUM(i.qty*i.unit_price) AS total
 FROM order_items i JOIN products p ON p.product_id=i.product_id GROUP BY p.category)
 SELECT category,total,ROUND(100.0*total/NULLIF(SUM(total) OVER (),0),2)
 FROM revenue ORDER BY category"""

def orders(rows,sql):
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE orders (order_id INTEGER,cust_id INTEGER,order_date TEXT,amount INTEGER,status TEXT)")
        db.executemany("INSERT INTO orders VALUES(?,?,?,?,?)",
                       [(*r,"delivered") if len(r)==4 else r for r in rows])
        return db.execute(sql).fetchall()

def shares(products,items):
    with closing(sqlite3.connect(":memory:")) as db:
        db.execute("CREATE TABLE products (product_id INTEGER,category TEXT)")
        db.execute("CREATE TABLE order_items (item_id INTEGER,product_id INTEGER,qty INTEGER,unit_price INTEGER)")
        db.executemany("INSERT INTO products VALUES(?,?)",products)
        db.executemany("INSERT INTO order_items VALUES(?,?,?,?)",items)
        return db.execute(SHARES).fetchall()

class Advanced66To70ReadOnlyContracts(unittest.TestCase):
    def test_01_original_blobs_and_preserved_pending_answers(self):
        for qid,(name,sha,page) in PINS.items():
            data=(BASE/name).read_bytes()
            blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            self.assertEqual(blob,sha,qid)
            txt=data.decode("utf-8")
            for marker in ("# Advanced Q"+qid[1:]+".",
                           "question "+str(int(qid[1:]))+", PDF p. "+str(page),
                           "### Sample input and expected output (illustrative)",
                           "The PDF does not provide separate sample input",
                           "NOT SOLVED YET",
                           "## My solution — SQLite\n\nPending.",
                           "## My solution — SQL Server\n\nPending.",
                           "## Official solution\n\nPending until"):
                self.assertIn(marker,txt,qid)

    def test_02_A066_archived_illustration(self):
        self.assertEqual(orders([(1,1,"2026-01-01",10),(2,1,"2026-01-01",10),
                                 (3,1,"2026-01-01",20)],PEERS),
                         [(1,10,10,20),(2,10,20,20),(3,20,40,40)])

    def test_03_A066_negative_peers(self):
        rows=[(3,1,"2026-01-01",0),(1,1,"2026-01-01",-5),
              (4,1,"2026-01-01",7),(2,1,"2026-01-01",-5)]
        self.assertEqual(orders(rows,PEERS),[(1,-5,-5,-10),(2,-5,-10,-10),
                                           (3,0,-10,-10),(4,7,-3,-3)])

    def test_04_A066_null_peers_and_ordered_ties(self):
        rows=[(2,1,"2026-01-01",None),(1,1,"2026-01-01",None),
              (4,1,"2026-01-01",2),(3,1,"2026-01-01",2)]
        self.assertEqual(orders(rows,PEERS),[(1,None,None,None),(2,None,None,None),
                                           (3,2,2,4),(4,2,4,4)])

    def test_05_A067_archived_month_reset(self):
        rows=[(1,1,"2026-01-30",10),(2,1,"2026-01-31",20),
              (3,1,"2026-02-01",5)]
        self.assertEqual(orders(rows,MONTH),[(1,"2026-01-30",10,10),
                                             (2,"2026-01-31",20,30),
                                             (3,"2026-02-01",5,5)])

    def test_06_A067_year_month_and_same_day_tie(self):
        rows=[(4,1,"2027-01-01",3),(3,1,"2026-02-01",2),
              (2,1,"2026-01-31",7),(1,1,"2026-01-31",5)]
        self.assertEqual(orders(rows,MONTH),[(1,"2026-01-31",5,5),
                                            (2,"2026-01-31",7,12),
                                            (3,"2026-02-01",2,2),
                                            (4,"2027-01-01",3,3)])
        self.assertEqual(orders([(1,1,None,300)],MONTH),[])

    def test_07_A067_81_monthly_python_oracle_combinations(self):
        dates=["2026-01-30","2026-01-31","2026-02-01","2026-02-01"]
        count=0
        for amounts in product((-2,0,3),repeat=4):
            rows=[(i+1,1,dates[i],amounts[i]) for i in range(4)]
            sums={}
            want=[]
            for i,(day,v) in enumerate(zip(dates,amounts)):
                m=day[:7]
                sums[m]=sums.get(m,0)+v
                want.append((i+1,day,v,sums[m]))
            self.assertEqual(orders(rows,MONTH),want)
            count+=1
        self.assertEqual(count,81)

    def test_08_A068_archived_running_max(self):
        rows=[(1,10,"2026-01-01",40),(2,10,"2026-01-03",25),
              (3,10,"2026-01-04",60)]
        self.assertEqual(orders(rows,MAXSOFAR),[(1,10,40,40,0),
                                                (2,10,25,40,-15),
                                                (3,10,60,60,0)])

    def test_09_A068_partition_negative_values(self):
        rows=[(2,10,"2026-01-02",-5),(1,10,"2026-01-01",-10),
              (4,20,"2026-01-02",2),(3,20,"2026-01-01",3)]
        self.assertEqual(orders(rows,MAXSOFAR),[(1,10,-10,-10,0),
                                                (2,10,-5,-5,0),
                                                (3,20,3,3,0),
                                                (4,20,2,3,-1)])

    def test_10_A068_null_and_same_day_tie(self):
        rows=[(1,10,"2026-01-01",None),(2,10,"2026-01-01",8),
              (3,10,"2026-01-01",None),(4,10,"2026-01-02",2)]
        self.assertEqual(orders(rows,MAXSOFAR),[(1,10,None,None,None),
                                                (2,10,8,8,0),
                                                (3,10,None,8,None),
                                                (4,10,2,8,-6)])

    def test_11_A068_81_running_max_python_oracle_combinations(self):
        count=0
        for vals in product((-5,0,4),repeat=4):
            rows=[(i+1,10,f"2026-01-0{i+1}",v) for i,v in enumerate(vals)]
            biggest=None
            want=[]
            for i,v in enumerate(vals):
                biggest=v if biggest is None else max(biggest,v)
                want.append((i+1,10,v,biggest,v-biggest))
            self.assertEqual(orders(rows,MAXSOFAR),want)
            count+=1
        self.assertEqual(count,81)

    def test_12_A069_archived_four_spend_quartiles(self):
        rows=[(1,10,"2026-01-01",80),(2,20,"2026-01-01",60),
              (3,30,"2026-01-01",40),(4,40,"2026-01-01",20)]
        self.assertEqual(orders(rows,TILES),[(10,80,1),(20,60,2),
                                             (30,40,3),(40,20,4)])

    def test_13_A069_equal_spend_and_six_bucket_sizes(self):
        rows=[(i,i*10,"2026-01-01",5) for i in range(1,7)]
        self.assertEqual(orders(rows,TILES),[(10,5,1),(20,5,1),
                                             (30,5,2),(40,5,2),
                                             (50,5,3),(60,5,4)])

    def test_14_A069_small_count_empty_and_null_customer(self):
        self.assertEqual(orders([],TILES),[])
        self.assertEqual(orders([(1,10,"2026-01-01",4)],TILES),
                         [(10,4,1)])
        rows=[(1,10,"2026-01-01",10),(2,20,"2026-01-01",20),
              (3,30,"2026-01-01",30),(4,None,"2026-01-01",900)]
        self.assertEqual(orders(rows,TILES),[(30,30,1),(20,20,2),(10,10,3)])

    def test_15_A069_256_spend_rank_python_oracle_combinations(self):
        count=0
        for amounts in product((0,2,4,6),repeat=4):
            rows=[(i+1,(i+1)*10,"2026-01-01",amounts[i]) for i in range(4)]
            ranked=sorted(((i+1)*10,v) for i,v in enumerate(amounts))
            ranked.sort(key=lambda x:(-x[1],x[0]))
            want=[(cust,v,n+1) for n,(cust,v) in enumerate(ranked)]
            self.assertEqual(orders(rows,TILES),want)
            count+=1
        self.assertEqual(count,256)

    def test_16_A070_archived_category_share_illustration(self):
        self.assertEqual(shares([(1,"Electronics"),(2,"Books")],
                                [(11,1,7,10),(12,2,3,10)]),
                         [("Books",30,30.0),("Electronics",70,70.0)])

    def test_17_A070_zero_denominator_refund_and_empty(self):
        self.assertEqual(shares([(1,"A"),(2,"B")],
                                [(1,1,1,10),(2,2,-1,10)]),
                         [("A",10,None),("B",-10,None)])
        self.assertEqual(shares([(1,"A")],[]),[])

    def test_18_A070_27_revenue_share_python_oracle_combinations(self):
        products=[(1,"A"),(2,"B"),(3,"C")]
        count=0
        for qs in product((0,1,3),repeat=3):
            den=10*sum(qs)
            want=[(ch,10*q,round(100*10*q/den,2) if den else None)
                  for ch,q in zip(("A","B","C"),qs)]
            self.assertEqual(shares(products,[(i,i,q,10) for i,q in enumerate(qs,1)]),
                             want)
            count+=1
        self.assertEqual(count,27)

    def test_19_A070_duplicate_product_key_and_orphan_join(self):
        products=[(1,"A"),(1,"A"),(2,"Unbought")]
        items=[(10,1,2,5),(11,99,100,100)]
        self.assertEqual(shares(products,items),[("A",20,100.0)])

    def test_20_A069_status_policy_is_not_an_official_solution(self):
        rows=[(1,10,"2026-01-01",100,"cancelled"),
              (2,10,"2026-01-02",20,"delivered"),
              (3,20,"2026-01-01",10,"delivered"),
              (4,None,"2026-01-03",500,"delivered")]
        self.assertEqual(orders(rows,TILES),[(10,120,1),(20,10,2)])
        self.assertEqual(orders(rows,
            "SELECT COUNT(*) FROM orders WHERE status='cancelled'"),[(1,)])
        self.assertEqual(shares([(1,"Unbought")],[]),[])

if __name__=="__main__":
    unittest.main(verbosity=2)
