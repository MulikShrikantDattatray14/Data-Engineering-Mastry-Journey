"""Auditor-authored SQLite window semantics fixtures: synthetic, never official SQL or learner answers.
Source archives and learner/progress files are never edited by this runner.
"""
from pathlib import Path
import sqlite3
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/9. Windowing Functions"
IDS=("A003","A015",*[f"A{i:03}" for i in range(51,78)],"A079",
     "P034","P041","P042","P043","P044","P045","P049","P058",
     "P060","P068","P074","P078","P079","P082","P097")

def rows(schema, entries, query):
    db=sqlite3.connect(":memory:")
    try:
        db.executescript(schema)
        for name, values in entries.items():
            db.executemany(f"INSERT INTO {name} VALUES ({','.join('?' for _ in values[0])})",values)
        return db.execute(query).fetchall()
    finally:
        db.close()

class WindowAudit(unittest.TestCase):
    def test_archived_source_45_present(self):
        self.assertEqual(len(IDS),45)
        for ident in IDS:
            found=list(SOURCE.glob(ident+".*.md"))
            self.assertEqual(len(found),1,ident)
            original=found[0].read_text(encoding="utf-8")
            self.assertIn("## Question and image",original,ident)
            self.assertIn("## Official solution",original,ident)

    def test_a003_distinct_third_salary(self):
        q="""WITH x AS (SELECT DISTINCT salary FROM e WHERE salary IS NOT NULL),
        r AS (SELECT salary,DENSE_RANK() OVER (ORDER BY salary DESC) rn FROM x)
        SELECT MAX(CASE WHEN rn=3 THEN salary END) FROM r"""
        self.assertEqual(rows("CREATE TABLE e(salary INT)",{"e":[(300,),(200,),(200,),(100,),(None,)]},q),[(100,)])
        self.assertEqual(rows("CREATE TABLE e(salary INT)",{"e":[(300,),(200,)]},q),[(None,)])

    def test_a051_a052_p042_rank_ties(self):
        r=rows("CREATE TABLE e(id INT,dept INT,salary INT)",{"e":[(1,10,100),(2,10,90),(3,10,90),(4,10,80),(5,20,80)]},
        """SELECT id,ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC,id),
        RANK() OVER (PARTITION BY dept ORDER BY salary DESC),
        DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) FROM e ORDER BY id""")
        self.assertEqual(r,[(1,1,1,1),(2,2,2,2),(3,3,2,2),(4,4,4,3),(5,1,1,1)])

    def test_a054_a055_percentile_and_cumulative_distribution(self):
        r=rows("CREATE TABLE e(id INT,salary INT)",{"e":[(1,40),(2,60),(3,60),(4,80)]},
        "SELECT id,ROUND(PERCENT_RANK() OVER(ORDER BY salary),6),ROUND(CUME_DIST() OVER(ORDER BY salary),6) FROM e ORDER BY id")
        self.assertEqual(r,[(1,0.,0.25),(2,0.333333,0.75),(3,0.333333,0.75),(4,1.,1.)])

    def test_a057_a058_p044_calendar_month_and_zero_denominator(self):
        r=rows("CREATE TABLE o(id INT,d TEXT,amount INT)",{"o":[(1,"2026-01-01",100),(2,"2026-03-01",0),(3,"2026-04-01",30)]},
        """WITH m AS (SELECT substr(d,1,7)||'-01' mo,SUM(amount) v FROM o GROUP BY mo)
        SELECT m.mo,m.v,p.v,CASE WHEN p.v IS NOT NULL THEN m.v-p.v END,
        CASE WHEN p.v<>0 THEN ROUND(100.0*(m.v-p.v)/p.v,2) END
        FROM m LEFT JOIN m p ON p.mo=date(m.mo,'-1 month') ORDER BY m.mo""")
        self.assertEqual(r,[("2026-01-01",100,None,None,None),("2026-03-01",0,None,None,None),("2026-04-01",30,0,30,None)])

    def test_a062_calendar_yoy_sparse_months(self):
        r=rows("CREATE TABLE o(d TEXT,amount INT)",{"o":[("2025-01-01",100),("2026-01-01",150),("2026-02-01",20)]},
        """WITH m AS (SELECT substr(d,1,7)||'-01' mo,SUM(amount) v FROM o GROUP BY mo)
        SELECT m.mo,m.v,p.v FROM m LEFT JOIN m p ON p.mo=date(m.mo,'-1 year') ORDER BY m.mo""")
        self.assertEqual(r,[("2025-01-01",100,None),("2026-01-01",150,100),("2026-02-01",20,None)])

    def test_a063_a066_rows_vs_range_peers(self):
        r=rows("CREATE TABLE o(id INT,amount INT)",{"o":[(1,10),(2,10),(3,20)]},
        """SELECT id,SUM(amount) OVER(ORDER BY amount,id ROWS UNBOUNDED PRECEDING),
        SUM(amount) OVER(ORDER BY amount RANGE UNBOUNDED PRECEDING) FROM o ORDER BY id""")
        self.assertEqual(r,[(1,10,20),(2,20,20),(3,40,40)])

    def test_a065_calendar_correct_7_day_average(self):
        r=rows("CREATE TABLE o(d TEXT,amount INT)",{"o":[("2026-01-01",10),("2026-01-03",20),("2026-01-07",40)]},
        """WITH RECURSIVE days(d) AS (SELECT MIN(d) FROM o UNION ALL SELECT date(d,'+1 day') FROM days WHERE d<(SELECT MAX(d) FROM o)),
        daily AS (SELECT d,SUM(amount) v FROM o GROUP BY d),
        filled AS (SELECT days.d,COALESCE(daily.v,0) v FROM days LEFT JOIN daily USING(d)),
        w AS (SELECT d,SUM(v) OVER(ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) total,
        COUNT(*) OVER(ORDER BY d ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) cnt FROM filled)
        SELECT d,total,total*1.0/cnt FROM w WHERE cnt=7""")
        self.assertEqual(r,[("2026-01-07",70,10.)])

    def test_a072_median_odd_even_excluding_null(self):
        q="""WITH r AS (SELECT salary,ROW_NUMBER() OVER(ORDER BY salary) rn,COUNT(*) OVER() n FROM e WHERE salary IS NOT NULL)
        SELECT AVG(salary) FROM r WHERE rn IN ((n+1)/2,(n+2)/2)"""
        self.assertEqual(rows("CREATE TABLE e(salary REAL)",{"e":[(40.,),(60.,),(80.,),(100.,),(None,)]},q),[(70.,)])
        self.assertEqual(rows("CREATE TABLE e(salary REAL)",{"e":[(40.,),(60.,),(80.,)]},q),[(60.,)])

    def test_a074_p049_tied_third_distinct_units(self):
        r=rows("CREATE TABLE x(id INT,units INT)",{"x":[(1,10),(2,8),(3,8),(4,1),(5,0)]},
        """WITH r AS (SELECT id,DENSE_RANK() OVER(ORDER BY units DESC) dr,RANK() OVER(ORDER BY units DESC) rr FROM x)
        SELECT id,dr,rr FROM r WHERE dr<=3 ORDER BY id""")
        self.assertEqual(r,[(1,1,1),(2,2,2),(3,2,2),(4,3,4)])

    def test_a075_a077_p058_deterministic_latest_and_second(self):
        r=rows("CREATE TABLE o(id INT,cust INT,d TEXT)",{"o":[(1,10,"2026-01-01"),(2,10,"2026-01-05"),(3,10,"2026-01-05"),(4,20,"2026-02-01")]},
        """WITH r AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY cust ORDER BY d DESC,id DESC) rn FROM o)
        SELECT cust,id,rn FROM r WHERE rn<=2 ORDER BY cust,rn""")
        self.assertEqual(r,[(10,3,1),(10,2,2),(20,4,1)])

    def test_p034_supplier_orphans_and_zero_supply(self):
        r=rows("CREATE TABLE s(id INT);CREATE TABLE l(id INT,supplier INT,qty INT)",
        {"s":[(1,),(2,)],"l":[(1,1,3),(2,99,2)]},
        """WITH keys AS (SELECT id supplier FROM s UNION SELECT supplier FROM l), total AS (SELECT SUM(qty) v FROM l)
        SELECT k.supplier,COALESCE(SUM(l.qty),0),ROUND(100.0*COALESCE(SUM(l.qty),0)/NULLIF(total.v,0),2)
        FROM keys k LEFT JOIN l ON k.supplier=l.supplier CROSS JOIN total GROUP BY k.supplier,total.v ORDER BY k.supplier""")
        self.assertEqual(r,[(1,3,60.),(2,0,0.),(99,2,40.)])

    def test_p068_delivered_second_rank_ties(self):
        r=rows("CREATE TABLE o(id INT,cust INT,d TEXT,delivery TEXT,amount INT)",
        {"o":[(1,1,"2026-01-01","2026-01-02",100),(2,2,"2026-01-01","2026-01-02",80),
              (3,3,"2026-01-01","2026-01-02",80),(4,4,"2026-01-01",None,1000)]},
        """WITH s AS (SELECT cust,SUM(amount) v FROM o WHERE delivery IS NOT NULL AND delivery>=d GROUP BY cust),
        r AS (SELECT *,DENSE_RANK() OVER(ORDER BY v DESC) rn FROM s)
        SELECT cust,v FROM r WHERE rn=2 ORDER BY cust""")
        self.assertEqual(r,[(2,80),(3,80)])

    def test_p078_twenty_product_median_and_percentile(self):
        r=rows("CREATE TABLE p(id INT,price INT,units INT)",{"p":[(i,i,10 if i<20 else 0) for i in range(1,21)]},
        """WITH d AS (SELECT *,PERCENT_RANK() OVER(ORDER BY price) pct,
        ROW_NUMBER() OVER(ORDER BY units,id) rn,COUNT(*) OVER() ct FROM p),
        med AS (SELECT AVG(units) m FROM d WHERE rn IN ((ct+1)/2,(ct+2)/2))
        SELECT d.id,ROUND(d.pct,2),med.m FROM d CROSS JOIN med
        WHERE d.ct>=20 AND d.pct>=0.75 AND d.units<med.m""")
        self.assertEqual(r,[(20,1.,10.)])

    def test_p079_first_lifetime_threshold(self):
        r=rows("CREATE TABLE o(id INT,cust INT,d TEXT,amount INT)",
        {"o":[(1,10,"2026-01-01",4000),(2,10,"2026-01-05",3000),(3,10,"2026-01-10",3000),
              (4,10,"2026-01-11",5000),(5,20,"2026-01-01",9999)]},
        """WITH r AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY cust ORDER BY d,id) rn,
        SUM(amount) OVER(PARTITION BY cust ORDER BY d,id ROWS UNBOUNDED PRECEDING) running,
        MIN(d) OVER(PARTITION BY cust) first_d FROM o),
        x AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY cust ORDER BY rn) cn FROM r WHERE running>=10000)
        SELECT cust,rn,d,CAST(julianday(d)-julianday(first_d) AS INT),running FROM x WHERE cn=1""")
        self.assertEqual(r,[(10,3,"2026-01-10",9,10000)])

    def test_p097_no_second_order_retained_in_denominator(self):
        r=rows("CREATE TABLE path(cust INT,first_cat TEXT,second_cat TEXT)",
        {"path":[(10,"Audio","Home"),(20,"Audio",None),(30,"Food","Food")]},
        """WITH p AS (SELECT first_cat,COALESCE(second_cat,'No second order') sc,
        COUNT(*) n FROM path GROUP BY first_cat,sc)
        SELECT first_cat,sc,n,ROUND(100.0*n/SUM(n) OVER(PARTITION BY first_cat),2) FROM p ORDER BY first_cat,sc""")
        self.assertEqual(r,[("Audio","Home",1,50.),("Audio","No second order",1,50.),("Food","Food",1,100.)])
        # Input paths already have dominant order categories; not a full P097 solution.

if __name__=="__main__":
    unittest.main(verbosity=2)
