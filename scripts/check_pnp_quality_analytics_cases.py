"""Auditor-authored synthetic SQLite regression checks, never official SQL or learner solutions.
These checks deliberately leave MySQL-only behavior, full original datasets and official PDFs unverified.
"""
from pathlib import Path
import math
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
IDS={
"14. Data Quality and Deduplication":("A085","A086","A087","A088","A089","A090","P037","P071","P072","P086","P087","P088","P089","P090","P092","P093","P095"),
"15. Analytics and Performance":("P062","P063","P067","P073","P083","P094","P096","P098","P099","P100"),
}

def db(script):
    con=sqlite3.connect(":memory:")
    con.executescript(script)
    return con

class QualityAnalyticsAudit(unittest.TestCase):
    def test_all_27_archived_question_sections_present(self):
        self.assertEqual(sum(len(v) for v in IDS.values()),27)
        for folder,ids in IDS.items():
            for ident in ids:
                paths=list((BASE/folder).glob(ident+".*.md"))
                self.assertEqual(len(paths),1,(folder,ident))
                txt=paths[0].read_text(encoding="utf-8")
                for heading in ("## Question and image","## Schema","## My solution — SQLite",
                                "## My solution — SQL Server","## Official solution"):
                    self.assertIn(heading,txt,(ident,heading))

    def test_a085_null_duplicate_group(self):
        c=db("""CREATE TABLE payments(id INT,order_id INT,paid_at TEXT,amount INT);
        INSERT INTO payments VALUES (1,10,'2026-01-01',10),(2,10,'2026-01-01',20),
        (3,20,NULL,30),(4,20,NULL,40),(5,30,'2026-01-01',50);""")
        got=c.execute("""SELECT order_id,paid_at,COUNT(*) n FROM payments
                          GROUP BY order_id,paid_at HAVING COUNT(*)>1 ORDER BY order_id""").fetchall()
        self.assertEqual(got,[(10,"2026-01-01",2),(20,None,2)])
        c.close()

    def test_a086_earliest_payment_tie_break(self):
        c=db("""CREATE TABLE payments(id INT,order_id INT,paid_at TEXT);
        INSERT INTO payments VALUES (1,10,'2026-01-03'),(2,10,'2026-01-01'),
        (3,10,'2026-01-01'),(4,20,'2026-02-01');""")
        got=c.execute("""WITH ranked AS (SELECT *,ROW_NUMBER() OVER
                        (PARTITION BY order_id ORDER BY paid_at,id) rn FROM payments)
                        SELECT id,order_id FROM ranked WHERE rn=1 ORDER BY order_id""").fetchall()
        self.assertEqual(got,[(2,10),(4,20)])
        c.close()

    def test_a087_physical_delete_keeps_lowest_key(self):
        c=db("""CREATE TABLE payments(id INT PRIMARY KEY,order_id INT,paid_at TEXT);
        INSERT INTO payments VALUES (1,10,'2026-01-01'),(2,10,'2026-01-01'),
        (3,10,'2026-01-02'),(4,20,NULL),(5,20,NULL);""")
        c.execute("""DELETE FROM payments WHERE id IN (
            SELECT id FROM (SELECT id,ROW_NUMBER() OVER
              (PARTITION BY order_id,paid_at ORDER BY id) rn FROM payments) WHERE rn>1)""")
        self.assertEqual(c.execute("SELECT id FROM payments ORDER BY id").fetchall(),
                         [(1,),(3,),(4,)])
        c.close()

    def test_a089_duplicate_groups_vs_excess_rows(self):
        c=db("""CREATE TABLE payments(id INT,order_id INT,paid_at TEXT);
        INSERT INTO payments VALUES (1,10,'a'),(2,10,'a'),(3,10,'a'),(4,20,'b'),(5,20,'b'),(6,30,'c');""")
        got=c.execute("""WITH g AS (SELECT COUNT(*) n FROM payments GROUP BY order_id,paid_at)
           SELECT SUM(CASE WHEN n>1 THEN 1 ELSE 0 END),
                  SUM(CASE WHEN n>1 THEN n-1 ELSE 0 END) FROM g""").fetchone()
        self.assertEqual(got,(2,3))
        c.close()

    def test_p071_normalized_email_and_signup_ties(self):
        c=db("""CREATE TABLE customers(id INT,email TEXT,entered TEXT);
        INSERT INTO customers VALUES (1,' ASHA@example.com ','2026-01-01'),
         (2,'asha@example.com','2026-01-05'),(3,'ASHA@EXAMPLE.COM','2026-01-01'),
         (4,NULL,'2026-01-01'),(5,'  ','2026-01-02'),(6,'','2026-01-03');""")
        got=c.execute("""WITH x AS (
           SELECT *,LOWER(TRIM(email)) email_key FROM customers
           WHERE NULLIF(TRIM(email),'') IS NOT NULL),
           r AS (SELECT *,FIRST_VALUE(id) OVER
              (PARTITION BY email_key ORDER BY entered,id) survivor,
            ROW_NUMBER() OVER (PARTITION BY email_key ORDER BY entered,id) rn FROM x)
           SELECT id,survivor FROM r WHERE rn>1 ORDER BY id""").fetchall()
        self.assertEqual(got,[(2,1),(3,1)])
        c.close()

    def test_p072_same_supplier_vs_split(self):
        c=db("""CREATE TABLE lines(id INT,oid INT,pid INT,qty INT,supplier INT);
        INSERT INTO lines VALUES (1,10,101,2,7),(2,10,101,3,7),
          (3,20,102,1,7),(4,20,102,4,8),(5,30,103,1,9);""")
        got=c.execute("""SELECT oid,pid,COUNT(*) lines,SUM(qty) units,
          CASE WHEN COUNT(DISTINCT supplier)>1 THEN 'split' ELSE 'consolidate' END action
          FROM lines GROUP BY oid,pid HAVING COUNT(*)>1 ORDER BY oid""").fetchall()
        self.assertEqual(got,[(10,101,2,5,"consolidate"),(20,102,2,5,"split")])
        c.close()

    def test_p089_null_safe_update_and_retry(self):
        c=db("""CREATE TABLE source(id INT PRIMARY KEY,d TEXT,amount INT);
        CREATE TABLE target(id INT PRIMARY KEY,d TEXT,amount INT,etl_updated_at TEXT);
        INSERT INTO source VALUES (1,'2026-01-10',100),(2,'2026-01-11',200),(3,NULL,50),
            (4,'2025-12-01',30);
        INSERT INTO target VALUES (1,'2026-01-10',100,'old'),
            (2,'2026-01-11',150,'old'),(4,'2025-12-01',30,'old');""")
        def run():
            batch=c.execute("""SELECT s.id,s.d,s.amount,t.id,t.d,t.amount FROM source s
                  LEFT JOIN target t ON t.id=s.id
                  WHERE s.d >= date((SELECT MAX(d) FROM target),'-21 days') OR s.d IS NULL
                  ORDER BY s.id""").fetchall()
            counts={"inserted":0,"updated":0,"unchanged":0}
            for id_,d,amount,old_id,old_d,old_amount in batch:
                if old_id is None: action="inserted"
                elif old_d != d or old_amount != amount: action="updated"
                else: action="unchanged"
                counts[action]+=1
                c.execute("""INSERT INTO target VALUES (?,?,?,'new')
                      ON CONFLICT(id) DO UPDATE SET d=excluded.d, amount=excluded.amount,
                       etl_updated_at='new'
                      WHERE target.d IS NOT excluded.d OR target.amount IS NOT excluded.amount""",
                       (id_,d,amount))
            return counts
        self.assertEqual(run(),{"inserted":1,"updated":1,"unchanged":1})
        self.assertEqual(run(),{"inserted":0,"updated":0,"unchanged":3})
        self.assertEqual(c.execute("SELECT amount,etl_updated_at FROM target WHERE id=1").fetchone(),(100,"old"))
        self.assertEqual(c.execute("SELECT amount,etl_updated_at FROM target WHERE id=2").fetchone(),(200,"new"))
        self.assertEqual(c.execute("SELECT amount FROM target WHERE id=4").fetchone(),(30,))
        c.close()

    def test_p092_merge_preserves_total_orders(self):
        c=db("""CREATE TABLE customers(id INT,email TEXT);
        CREATE TABLE orders(id INT,cid INT);
        INSERT INTO customers VALUES (10,' ASHA@example.com '),(20,'asha@example.com'),
          (30,'bela@example.com');
        INSERT INTO orders VALUES (1,10),(2,20),(3,30);""")
        raw=c.execute("""WITH c AS (SELECT cid,COUNT(*) n FROM orders GROUP BY cid)
           SELECT COUNT(*),SUM(n>=2),SUM(n) FROM c""").fetchone()
        merged=c.execute("""WITH c AS (
            SELECT LOWER(TRIM(customers.email)) key,COUNT(*) n
            FROM orders JOIN customers ON customers.id=orders.cid GROUP BY key)
            SELECT COUNT(*),SUM(n>=2),SUM(n) FROM c""").fetchone()
        self.assertEqual((raw,merged),((3,0,3),(2,1,3)))
        c.close()

    def test_p095_zero_sale_category_and_unmapped_lines(self):
        c=db("""CREATE TABLE category(id INT,name TEXT);
        CREATE TABLE products(id INT,catid INT,price INT);
        CREATE TABLE orders(id INT,d TEXT);
        CREATE TABLE detail(oid INT,pid INT,qty INT);
        INSERT INTO category VALUES (1,'Audio'),(2,'Home');
        INSERT INTO products VALUES (101,1,10),(102,99,5);
        INSERT INTO orders VALUES (1,'2026-01-01');
        INSERT INTO detail VALUES (1,101,2),(1,102,1);""")
        q="""WITH sold AS (SELECT COALESCE(c.name,'Unmapped') label,o.id oid,d.qty*p.price v
          FROM detail d JOIN orders o ON o.id=d.oid JOIN products p ON p.id=d.pid
          LEFT JOIN category c ON c.id=p.catid WHERE o.d>='2026-01-01' AND o.d<'2027-01-01'),
         labels AS (SELECT name label FROM category UNION SELECT label FROM sold)
         SELECT l.label,COUNT(DISTINCT s.oid),COALESCE(SUM(s.v),0) val
         FROM labels l LEFT JOIN sold s ON s.label=l.label
         GROUP BY l.label ORDER BY val,l.label"""
        self.assertEqual(c.execute(q).fetchall(),
            [("Home",0,0),("Unmapped",1,5),("Audio",1,20)])
        c.close()

    def test_p062_pareto_includes_crossing_product(self):
        c=db("""CREATE TABLE v(pid INT,value INT);
        INSERT INTO v VALUES (1,60),(2,30),(3,10);""")
        got=c.execute("""WITH x AS (
          SELECT pid,value,SUM(value) OVER () total,
             SUM(value) OVER (ORDER BY value DESC,pid ROWS UNBOUNDED PRECEDING) running
          FROM v)
          SELECT pid,ROUND(100.0*running/total,2),
           CASE WHEN running-value<0.8*total THEN 'Top 80%' ELSE 'Long tail' END
          FROM x ORDER BY value DESC,pid""").fetchall()
        self.assertEqual(got,[(1,60.0,"Top 80%"),(2,90.0,"Top 80%"),(3,100.0,"Long tail")])
        c.close()

    def test_p094_supplier_hhi(self):
        c=db("""CREATE TABLE line(supplier INT,qty INT,price INT);
        INSERT INTO line VALUES (7,3,25),(8,1,25);""")
        got=c.execute("""WITH s AS (SELECT supplier,SUM(qty*price) value FROM line GROUP BY supplier),
          total AS (SELECT SUM(value) grand FROM s)
          SELECT ROUND(SUM((100.0*s.value/total.grand)*(100.0*s.value/total.grand)),0)
          FROM s CROSS JOIN total""").fetchone()[0]
        self.assertEqual(got,6250.0)
        c.close()

    def test_p098_distinct_category_baskets_and_directed_lift(self):
        c=db("""CREATE TABLE basket(oid INT,category TEXT);
         INSERT INTO basket VALUES (1,'Audio'),(1,'Audio'),(1,'Home'),
            (2,'Audio'),(2,'Home'),(3,'Audio'),(4,'Home');""")
        got=c.execute("""WITH distinct_b AS (SELECT DISTINCT oid,category FROM basket),
          all_b AS (SELECT COUNT(DISTINCT oid) n FROM distinct_b),
          singles AS (SELECT category,COUNT(*) n FROM distinct_b GROUP BY category),
          pairs AS (SELECT a.category a,b.category b,COUNT(*) both
           FROM distinct_b a JOIN distinct_b b ON a.oid=b.oid AND a.category<>b.category
           GROUP BY a.category,b.category)
          SELECT p.a,p.b,p.both,ROUND(100.0*p.both/ab.n,2),
            ROUND(100.0*p.both/sa.n,2),ROUND(1.0*p.both*ab.n/sa.n/sb.n,3)
          FROM pairs p JOIN singles sa ON sa.category=p.a
           JOIN singles sb ON sb.category=p.b CROSS JOIN all_b ab
          ORDER BY p.a,p.b""").fetchall()
        self.assertEqual(got,[("Audio","Home",2,50.0,66.67,0.889),
                              ("Home","Audio",2,50.0,66.67,0.889)])
        c.close()

    def test_p099_prior_eight_sample_sd_excludes_current(self):
        c=db("""CREATE TABLE weeks(week TEXT,orders INT);
         INSERT INTO weeks VALUES ('2026-01-05',10),('2026-01-12',10),
          ('2026-01-19',10),('2026-01-26',10),('2026-02-02',10),
          ('2026-02-09',10),('2026-02-16',10),('2026-02-23',11),('2026-03-02',20);""")
        prior=c.execute("""WITH s AS (
           SELECT week,orders,COUNT(orders) OVER
             (ORDER BY week ROWS BETWEEN 8 PRECEDING AND 1 PRECEDING) n,
             AVG(orders) OVER
             (ORDER BY week ROWS BETWEEN 8 PRECEDING AND 1 PRECEDING) mean
           FROM weeks)
           SELECT n,mean FROM s WHERE week='2026-03-02'""").fetchone()
        self.assertEqual(prior,(8,10.125))
        amounts=[x[0] for x in c.execute(
            "SELECT orders FROM weeks WHERE week<'2026-03-02' ORDER BY week DESC LIMIT 8").fetchall()]
        sample_sd=math.sqrt(sum((x-prior[1])**2 for x in amounts)/(len(amounts)-1))
        self.assertAlmostEqual(sample_sd,0.3535533905932738,9)
        self.assertAlmostEqual((20-prior[1])/sample_sd,27.930717856,5)
        c.close()

if __name__=="__main__":
    unittest.main()
