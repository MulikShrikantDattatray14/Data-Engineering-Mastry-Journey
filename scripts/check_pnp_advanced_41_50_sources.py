#!/usr/bin/env python3
"""Partial independent A041–A050 audit. Source-pinned; read-only.

All successful candidate SQL is AUDITOR-AUTHORED SQLite, not provider MySQL or
learner work. A043 also executes its literal archived *broken* query.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/(
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
PINS={
 "A041":("5. CTEs/A041. Chain two CTEs monthly revenue, then only the months above the yea.md","cf1871f0ab44e36aeca7c5194e4612273020f298",9),
 "A042":("5. CTEs/A042. Compare every department average against the company average in on.md","2b7bbd8e917f2c75f91410868eedc4dde818f78f",9),
 "A043":("5. CTEs/A043. Filter on a window function result — why WHERE fails and what to d.md","b4830fd8ce95dac743c9f668cc360d8821a04f91",9),
 "A044":("5. CTEs/A044. Build a clean order spine, then attach item counts to it.md","e6d31713cd9ae72ad5dc0fbe6685b79e586860b3",9),
 "A045":("5. CTEs/A045. Deduplicate first, aggregate second — in one readable statement.md","d5b4c69444f8f32e67cd433e6b63239856bc5511",9),
 "A046":("10. Recursive CTE/A046. Generate every date in January 2026, with no calendar table.md","257e50b61a42df3981b449efe21301ba5958e4ef",10),
 "A047":("10. Recursive CTE/A047. Every employee under manager 5, at any depth, with their level.md","c7fbaf8e8160a0c469541a23c6cfa11b7b1facc7",10),
 "A048":("10. Recursive CTE/A048. Print the full reporting path of every employee up to the top.md","ad946a1b825a46f064f0d6304b68b116bf0c887c",10),
 "A049":("10. Recursive CTE/A049. How deep does the org chart go.md","761046ba33b6c5c3b1b3e1e93e12cb58c37d7998",10),
 "A050":("10. Recursive CTE/A050. Split 'a,b,c' into one row per value.md","b0cb6b6e51c73a157b0ffdc6367ee8594c07d925",10),
}
REVIEWER={
 "A041":"""WITH monthly AS (
    SELECT CAST(strftime('%Y',order_date) AS INTEGER) year,
           CAST(strftime('%m',order_date) AS INTEGER) month,
           SUM(amount) monthly_revenue FROM orders
    WHERE status='delivered' AND amount IS NOT NULL AND order_date IS NOT NULL
    GROUP BY 1,2),
    compared AS (SELECT year,month,monthly_revenue,
    AVG(monthly_revenue) OVER (PARTITION BY year) observed_month_avg FROM monthly)
    SELECT year,month,monthly_revenue FROM compared
    WHERE monthly_revenue>observed_month_avg ORDER BY year,month""",
 "A043":"""WITH ranked AS (SELECT emp_name,RANK() OVER (ORDER BY salary DESC) r
    FROM employees) SELECT emp_name,r FROM ranked WHERE r<=5 ORDER BY r,emp_name""",
 "A044":"""WITH spine AS (SELECT order_id,cust_id FROM orders),
    item_counts AS (SELECT order_id,COUNT(*) item_count FROM order_items GROUP BY order_id)
    SELECT s.order_id,s.cust_id,COALESCE(i.item_count,0) FROM spine s
    LEFT JOIN item_counts i ON i.order_id=s.order_id ORDER BY s.order_id""",
 "A045":"""WITH dedup AS (SELECT order_id,paid_at,amount,
    ROW_NUMBER() OVER (PARTITION BY order_id,paid_at ORDER BY payment_id) rn FROM payments)
    SELECT order_id,SUM(amount) total_paid FROM dedup WHERE rn=1
    GROUP BY order_id ORDER BY order_id""",
 "A046":"""WITH RECURSIVE calendar(d) AS (
    SELECT date('2026-01-01') UNION ALL SELECT date(d,'+1 day')
    FROM calendar WHERE d<'2026-01-31') SELECT d FROM calendar ORDER BY d""",
 "A047":"""WITH RECURSIVE reports(emp_id,emp_name,level,visited) AS (
    SELECT emp_id,emp_name,1,printf(',%d,',emp_id)
    FROM employees WHERE manager_id=5 AND emp_id<>5
    UNION ALL
    SELECT e.emp_id,e.emp_name,r.level+1,r.visited||e.emp_id||','
    FROM employees e JOIN reports r ON e.manager_id=r.emp_id
    WHERE e.emp_id<>5 AND instr(r.visited,printf(',%d,',e.emp_id))=0 AND r.level<100)
    SELECT emp_id,emp_name,level FROM reports ORDER BY level,emp_id""",
 "A050":"""WITH RECURSIVE parts(value,rest,ordinal) AS (
    SELECT substr(src,1,instr(src||',',',')-1),
           substr(src||',',instr(src||',',',')+1),1 FROM (SELECT ? AS src)
    UNION ALL
    SELECT substr(rest,1,instr(rest,',')-1),substr(rest,instr(rest,',')+1),ordinal+1
    FROM parts WHERE rest<>'')
    SELECT value FROM parts WHERE value<>'' ORDER BY ordinal""",
}
def check_sources():
    assert len(PINS)==10
    sources={}
    for sid,(rel,sha,page) in PINS.items():
        data=(BASE/rel).read_bytes()
        actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        assert actual==sha,(sid,"original source changed",actual)
        t=data.decode("utf-8")
        assert t.startswith("# Advanced Q"+sid[1:]+".")
        for marker in (
            "question "+str(int(sid[1:]))+", PDF p. "+str(page),
            "### Sample input and expected output (illustrative)",
            "## Schema","seven-table example schema","NOT SOLVED YET",
            "## My solution — SQLite\n\nPending.",
            "## My solution — SQL Server\n\nPending.",
            "## Official solution\n\nPending until"):
            assert marker in t,(sid,marker)
        sources[sid]=t
        print("PASS",sid,"source identity/statement/pending-state inspected")
    sqlblock=chr(96)*3+"sql"
    m=re.search(re.escape(sqlblock)+r"\s*(SELECT emp_name, RANK\(\).*?;)\s*"+
                re.escape(chr(96)*3),sources["A043"],re.S)
    assert m and "WHERE r <= 5" in m.group(1),"missing original broken A043 query"
    assert "same "+chr(96)+"(order_id, paid_at)"+chr(96) in sources["A045"]
    assert "31 date rows in total" in sources["A046"]
    return m.group(1)

def case(sid,label,schema,rows,expected,broken=None,input_value=None):
    with sqlite3.connect(":memory:") as db:
        db.executescript(schema)
        for table,values in rows.items():
            if values:
                db.executemany("INSERT INTO "+table+" VALUES ("+
                               ",".join("?" for _ in values[0])+")",values)
        if sid=="A043":
            assert broken
            try:
                db.execute(broken).fetchall()
            except sqlite3.OperationalError as error:
                assert "window function" in str(error),str(error)
            else:
                raise AssertionError("A043 archived invalid SQL unexpectedly succeeded")
        got=db.execute(REVIEWER[sid],(input_value,) if sid=="A050" else ()).fetchall()
        assert got==expected,(sid,label,got,expected)
    print("PASS",sid,label,"(reviewer SQLite; A043 additionally source broken SQL)")

def main():
    broken=check_sources()
    revenue="CREATE TABLE orders(order_id INTEGER,order_date TEXT,status TEXT,amount REAL);"
    case("A041","archived three-month illustration",revenue,
         {"orders":[(1,"2026-01-10","delivered",100),(2,"2026-02-10","delivered",300),
                    (3,"2026-03-10","delivered",200)]},[(2026,2,300)])
    case("A041","two-year partition, exclude cancelled, ties",revenue,
         {"orders":[(1,"2025-01-10","delivered",100),(2,"2025-02-10","delivered",900),
                    (3,"2026-01-10","delivered",200),(4,"2026-02-10","delivered",200),
                    (5,"2026-03-10","cancelled",900)]},[(2025,2,900)])
    employees="CREATE TABLE employees(emp_id INTEGER,emp_name TEXT,manager_id INTEGER,salary REAL);"
    source_names=[("Ada",90000),("Ben",80000),("Cora",70000),("Dan",60000),("Eva",50000),("Finn",40000)]
    case("A043","archived rank illustration",employees,
         {"employees":[(i,name,None,salary) for i,(name,salary) in enumerate(source_names,1)]},
         [("Ada",1),("Ben",2),("Cora",3),("Dan",4),("Eva",5)],broken)
    case("A043","salary tie at fifth rank includes both peers",employees,
         {"employees":[(1,"A",None,90000),(2,"B",None,80000),(3,"C",None,70000),
                       (4,"D",None,60000),(5,"E",None,50000),(6,"F",None,50000),
                       (7,"G",None,40000)]},
         [("A",1),("B",2),("C",3),("D",4),("E",5),("F",5)],broken)
    orders="CREATE TABLE orders(order_id INTEGER,cust_id INTEGER);CREATE TABLE order_items(item_id INTEGER,order_id INTEGER,qty INTEGER);"
    case("A044","archived order-spine illustration",orders,
         {"orders":[(10,1),(11,2)],"order_items":[(1,10,2),(2,10,1)]},
         [(10,1,2),(11,2,0)])
    case("A044","duplicate item rows, orphan and no-item order",orders,
         {"orders":[(10,1),(11,2)],"order_items":[(1,10,2),(1,10,2),(99,42,1)]},
         [(10,1,2),(11,2,0)])
    payments="CREATE TABLE payments(payment_id INTEGER,order_id INTEGER,paid_at TEXT,amount REAL);"
    case("A045","archived duplicate-payment illustration",payments,
         {"payments":[(1,10,"2026-01-03 10:00",50),
                      (2,10,"2026-01-03 10:00",50),
                      (3,10,"2026-01-04 09:00",20)]},[(10,70)])
    case("A045","conflicting amounts/NULL timestamp, FIRST-ID assumption",payments,
         {"payments":[(1,10,"2026-01-03",50),(2,10,"2026-01-03",60),
                      (3,20,None,30),(4,20,None,40)]},[(10,50),(20,30)])
    case("A046","full inclusive January 2026 (31 dates, no February)","",{},
         [(f"2026-01-{day:02d}",) for day in range(1,32)])
    case("A047","archived manager 5 and grandchildren",employees,
         {"employees":[(1,"CEO",None,None),(5,"Mira",1,None),(6,"Ana",5,None),
                       (7,"Ben",6,None),(8,"Cy",5,None),(9,"Dev",1,None)]},
         [(6,"Ana",1),(8,"Cy",1),(7,"Ben",2)])
    case("A047","cycle excludes manager 5, unrelated subtree",employees,
         {"employees":[(5,"Mira",7,None),(6,"Ana",5,None),(7,"Ben",6,None),
                       (8,"Cy",5,None),(9,"Other",None,None)]},
         [(6,"Ana",1),(8,"Cy",1),(7,"Ben",2)])
    case("A050","archived literal a,b,c","",{},[("a",),("b",),("c",)],input_value="a,b,c")
    case("A050","empty-token policy is reviewer-only","",{},[("a",),("b",)],input_value="a,,b,")
    print("PARTIAL: 10 original SHA-pinned records; 13 SQLite fixture groups for 7 IDs, one literal broken-query reproduction. No PDF or provider answer authenticated, native MySQL, learner completions or mastery.")
if __name__=="__main__":
    main()
