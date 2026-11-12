#!/usr/bin/env python3
"""PARTIAL A061-A070 audit: pinned original prompts and reviewer-only SQLite examples.

No source archive is changed. SQL below is auditor-authored, not an official
MySQL answer, an authenticated PDF excerpt, a learner attempt, or a grade.
"""
import hashlib
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/"
    "9. Windowing Functions"
)
PINS = {
    "A061": ("Customers whose most recent order was smaller than the one before.md", "6f3f440cd2152e07b509fbf1492921d375829acc", 12),
    "A062": ("Compare every month against the same month last year.md", "c74e070703fb111ec138c4b89426ed9a0c43f45e", 12),
    "A063": ("Running total of revenue by date.md", "f1b80eb27b6079414263f1497d9041a340ee6bd7", 13),
    "A064": ("Running total of spend per customer, oldest order first.md", "18cb163bef2ba0e0ebc699aeeb3d54cfbe68a0d1", 13),
    "A065": ("Seven-day moving average of daily revenue, calendar-correct.md", "3ed636792e25455903a75daf3fa31e4d58a16fb9", 13),
    "A066": ("Show the difference between ROWS and RANGE when values tie.md", "67ae69cbbdaee250db53057171ab3482ccb108f9", 13),
    "A067": ("Running total that resets at the start of every month.md", "d9ad182199cd687c0fdfaaf846575b1d6aaa3f90", 13),
    "A068": ("Each order against the biggest order seen so far for that customer.md", "130c2d5e7f9efc5f7a0afd073618f4f04b98f3eb", 13),
    "A069": ("Split customers into four spend quartiles.md", "518a30fa3c649e61d29ed1326741d2b24537c0ec", 14),
    "A070": ("Each category's share of total revenue, as a percentage.md", "289da2f3137fe948b437a414a00754a5a7109cab", 14),
}
SCHEMA = """
CREATE TABLE orders(order_id INTEGER, cust_id INTEGER, order_date TEXT, amount REAL);
CREATE TABLE products(product_id INTEGER, category TEXT);
CREATE TABLE order_items(item_id INTEGER, product_id INTEGER, qty INTEGER, unit_price REAL);
"""
SQL = {
"A061": """
WITH seen AS (
 SELECT cust_id,order_id,amount,
   LAG(amount) OVER(PARTITION BY cust_id ORDER BY order_date,order_id) previous_amount,
   ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY order_date DESC,order_id DESC) latest_rank
 FROM orders)
SELECT cust_id,order_id,amount,previous_amount FROM seen
WHERE latest_rank=1 AND amount<previous_amount ORDER BY cust_id
""",
"A062": """
WITH monthly AS (
 SELECT substr(order_date,1,7) month,SUM(amount) revenue
 FROM orders WHERE order_date IS NOT NULL GROUP BY substr(order_date,1,7))
SELECT cur.month,cur.revenue,prev.revenue,cur.revenue-prev.revenue
FROM monthly cur LEFT JOIN monthly prev
 ON prev.month=printf('%04d-%s',CAST(substr(cur.month,1,4) AS INTEGER)-1,substr(cur.month,6,2))
ORDER BY cur.month
""",
"A063": """
WITH daily AS (
 SELECT order_date,SUM(amount) daily_revenue FROM orders
 WHERE order_date IS NOT NULL GROUP BY order_date)
SELECT order_date,daily_revenue,
 SUM(daily_revenue) OVER(ORDER BY order_date ROWS UNBOUNDED PRECEDING)
FROM daily ORDER BY order_date
""",
"A064": """
SELECT cust_id,order_id,amount,
 SUM(amount) OVER(PARTITION BY cust_id ORDER BY order_date,order_id ROWS UNBOUNDED PRECEDING)
FROM orders ORDER BY cust_id,order_date,order_id
""",
"A065": """
WITH RECURSIVE bounds(first,last) AS (
 SELECT MIN(order_date),MAX(order_date) FROM orders WHERE order_date IS NOT NULL),
calendar(day) AS (
 SELECT first FROM bounds WHERE first IS NOT NULL
 UNION ALL SELECT date(day,'+1 day') FROM calendar,bounds WHERE day<last),
daily AS (
 SELECT order_date,SUM(amount) revenue FROM orders
 WHERE order_date IS NOT NULL GROUP BY order_date),
filled AS (
 SELECT calendar.day,COALESCE(daily.revenue,0) revenue
 FROM calendar LEFT JOIN daily ON daily.order_date=calendar.day),
rolling AS (
 SELECT day,ROW_NUMBER() OVER(ORDER BY day) seq,
 SUM(revenue) OVER(ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) seven_total
 FROM filled)
SELECT day,seven_total,ROUND(seven_total/7.0,2)
FROM rolling WHERE seq>=7 ORDER BY day
""",
"A066": """
SELECT order_id,amount,
 SUM(amount) OVER(ORDER BY amount,order_id ROWS UNBOUNDED PRECEDING) rows_total,
 SUM(amount) OVER(ORDER BY amount RANGE UNBOUNDED PRECEDING) range_total
FROM orders ORDER BY amount,order_id
""",
"A067": """
SELECT order_date,amount,
 SUM(amount) OVER(PARTITION BY substr(order_date,1,7)
 ORDER BY order_date,order_id ROWS UNBOUNDED PRECEDING)
FROM orders ORDER BY order_date,order_id
""",
"A068": """
WITH levels AS (
 SELECT order_id,cust_id,order_date,amount,
 MAX(amount) OVER(PARTITION BY cust_id ORDER BY order_date,order_id
 ROWS UNBOUNDED PRECEDING) max_so_far
 FROM orders)
SELECT order_id,amount,max_so_far,amount-max_so_far
FROM levels ORDER BY cust_id,order_date,order_id
""",
"A069": """
WITH spend AS (
 SELECT cust_id,SUM(amount) total_spend FROM orders
 GROUP BY cust_id)
SELECT cust_id,total_spend,
 NTILE(4) OVER(ORDER BY total_spend DESC,cust_id) quartile
FROM spend ORDER BY total_spend DESC,cust_id
""",
"A070": """
WITH category_revenue AS (
 SELECT p.category,SUM(i.qty*i.unit_price) revenue
 FROM order_items i JOIN products p ON p.product_id=i.product_id
 GROUP BY p.category)
SELECT category,revenue,
 ROUND(100.0*revenue/NULLIF(SUM(revenue) OVER(),0),2)
FROM category_revenue ORDER BY revenue DESC,category
""",
}

def inspect():
    assert len(PINS)==len(SQL)==10
    for sid,(suffix,expected_sha,page) in PINS.items():
        path=BASE/(sid+". "+suffix)
        raw=path.read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        assert blob==expected_sha,(sid,"archive Git blob changed",blob,expected_sha)
        t=raw.decode("utf-8")
        required=[
          "# Advanced Q"+sid[1:]+".", "question "+str(int(sid[1:]))+", PDF p. "+str(page),
          "## Schema", "seven-table example schema",
          "### Sample input and expected output (illustrative)",
          "The PDF does not provide separate sample input",
          "NOT SOLVED YET", "## My solution — SQLite\n\nPending.",
          "## My solution — SQL Server\n\nPending.",
          "## Official solution\n\nPending until"
        ]
        for marker in required:
            assert marker in t,(sid,"required original source marker absent",marker)
        print("PASS",sid,"original Git blob, source statement, local sample and Pending learner/official fields")

def check(sid,label,rows,expected):
    with sqlite3.connect(":memory:") as db:
        db.executescript(SCHEMA)
        for table, values in rows.items():
            if values:
                width=len(values[0])
                assert all(len(v)==width for v in values)
                db.executemany("INSERT INTO "+table+" VALUES ("+",".join("?" for _ in range(width))+")", values)
        observed=db.execute(SQL[sid]).fetchall()
        assert observed==expected,(sid,label,observed,expected)
    print("PASS",sid,label,"(auditor-only SQLite; NOT an official or learner solution)")

def order_rows(rows):
    """Map (order_id,cust_id,date,amount) tuples to the local test schema."""
    return {"orders":rows}

def main():
    inspect()
    check("A061","archived most-recent-smaller illustration",order_rows([
      (1,10,"2026-01-01",100),(2,10,"2026-01-03",80),
      (3,20,"2026-01-01",50),(4,20,"2026-01-03",70)]),
      [(10,2,80,100)])
    check("A061","same-date ties, single-order and non-decreasing latest",order_rows([
      (1,10,"2026-01-01",100),(2,10,"2026-01-02",80),(3,10,"2026-01-03",90),
      (4,20,"2026-01-01",40),(5,20,"2026-01-03",30),
      (6,30,"2026-01-02",10),(7,40,"2026-01-01",60),(8,40,"2026-01-01",10)]),
      [(20,5,30,40),(40,8,10,60)])

    check("A062","archived year-over-year January comparison",order_rows([
      (1,1,"2025-01-10",100),(2,1,"2026-01-10",150)]),
      [("2025-01",100,None,None),("2026-01",150,100,50)])
    check("A062","missing prior-year months are not LAG(12) or prior observed",order_rows([
      (1,1,"2025-01-10",50),(2,1,"2025-02-10",30),
      (3,1,"2026-01-10",60),(4,1,"2026-03-10",80)]),
      [("2025-01",50,None,None),("2025-02",30,None,None),
       ("2026-01",60,50,10),("2026-03",80,None,None)])

    check("A063","archived multi-order daily grouping",order_rows([
      (1,1,"2026-01-01",10),(2,1,"2026-01-01",20),
      (3,1,"2026-01-02",5)]),
      [("2026-01-01",30,30),("2026-01-02",5,35)])
    check("A063","missing day, negative correction and NULL date ignored",order_rows([
      (1,1,"2026-01-01",10),(2,2,"2026-01-03",-4),
      (3,1,"2026-01-03",5),(4,1,None,99)]),
      [("2026-01-01",10,10),("2026-01-03",1,11)])

    check("A064","archived customer-specific running spend",order_rows([
      (1,10,"2026-01-01",10),(2,10,"2026-01-03",20),
      (3,20,"2026-01-02",5)]),
      [(10,1,10,10),(10,2,20,30),(20,3,5,5)])
    check("A064","same-date order-ID tie and independent customer partition",order_rows([
      (2,10,"2026-01-01",7),(1,10,"2026-01-01",3),
      (3,20,"2026-01-01",9),(4,10,"2026-01-03",0)]),
      [(10,1,3,3),(10,2,7,10),(10,4,0,10),(20,3,9,9)])

    check("A065","archived complete seven calendar-day window with zero days",order_rows([
      (1,1,"2026-01-01",10),(2,1,"2026-01-03",20),
      (3,1,"2026-01-07",40)]),
      [("2026-01-07",70,10.0)])
    check("A065","February-to-March calendar boundary and rolling eighth day",order_rows([
      (1,1,"2026-02-27",7),(2,1,"2026-03-01",21),
      (3,1,"2026-03-06",14)]),
      [("2026-03-05",28,4.0),("2026-03-06",35,5.0)])

    check("A066","archived ROWS versus RANGE peer-group sums",order_rows([
      (1,1,"2026-01-01",10),(2,1,"2026-01-02",10),(3,1,"2026-01-03",20)]),
      [(1,10,10,20),(2,10,20,20),(3,20,40,40)])
    check("A066","three peer values show RANGE includes full peer group",order_rows([
      (3,1,"2026-01-01",5),(1,1,"2026-01-01",5),
      (2,1,"2026-01-01",5),(4,1,"2026-01-01",10)]),
      [(1,5,5,15),(2,5,10,15),(3,5,15,15),(4,10,25,25)])

    check("A067","archived monthly reset across January and February",order_rows([
      (1,1,"2026-01-30",10),(2,1,"2026-01-31",20),
      (3,1,"2026-02-01",5)]),
      [("2026-01-30",10,10),("2026-01-31",20,30),
       ("2026-02-01",5,5)])
    check("A067","year and same-day ties explicitly ordered by ID",order_rows([
      (2,1,"2025-12-31",5),(1,1,"2025-12-31",10),
      (3,1,"2026-01-01",7),(4,1,"2026-01-02",8)]),
      [("2025-12-31",10,10),("2025-12-31",5,15),
       ("2026-01-01",7,7),("2026-01-02",8,15)])

    check("A068","archived max-so-far and current-peak difference",order_rows([
      (1,10,"2026-01-01",40),(2,10,"2026-01-03",25),
      (3,10,"2026-01-04",60)]),
      [(1,40,40,0),(2,25,40,-15),(3,60,60,0)])
    check("A068","customer partition and same-day ID tie",order_rows([
      (2,10,"2026-01-01",10),(1,10,"2026-01-01",20),
      (3,20,"2026-01-01",3),(4,20,"2026-01-02",1)]),
      [(1,20,20,0),(2,10,20,-10),(3,3,3,0),(4,1,3,-2)])

    check("A069","archived four-customer quartiles",order_rows([
      (1,10,"2026-01-01",80),(2,20,"2026-01-01",60),
      (3,30,"2026-01-01",40),(4,40,"2026-01-01",20)]),
      [(10,80,1),(20,60,2),(30,40,3),(40,20,4)])
    check("A069","six customers, aggregation before NTILE and uneven buckets",order_rows([
      (1,10,"2026-01-01",40),(2,10,"2026-01-02",60),
      (3,20,"2026-01-01",50),(4,30,"2026-01-01",30),
      (5,40,"2026-01-01",20),(6,50,"2026-01-01",10),
      (7,60,"2026-01-01",0)]),
      [(10,100,1),(20,50,1),(30,30,2),(40,20,2),(50,10,3),(60,0,4)])

    check("A070","archived two-category revenue percentages",{
      "products":[(1,"Electronics"),(2,"Books")],
      "order_items":[(11,1,7,10),(12,2,3,10)]},
      [("Electronics",70,70.0),("Books",30,30.0)])
    check("A070","zero denominator returns NULL; orphan product excluded",{
      "products":[(1,"A"),(2,"B")],
      "order_items":[(11,1,0,10),(12,2,0,10),(13,99,1,100)]},
      [("A",0,None),("B",0,None)])
    print("PARTIAL: 10 source statements blob-pinned; 20 reviewer-only SQLite fixture groups. "
          "No original MySQL key/PDF, native MySQL, independent learner answer or mastery.")

if __name__=="__main__":
    main()
