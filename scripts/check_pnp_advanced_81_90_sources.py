#!/usr/bin/env python3
"""PARTIAL A081-A090 immutable-source assertions and reviewer-only SQLite cases.

No MySQL-provider solution, original PDF parity, saved learner solve, or grade is
claimed. All candidate SQL here is written by the auditor; writes affect only
fresh in-memory SQLite fixture tables, never repo archives or user databases.
"""
import hashlib
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ('99. Reference Materials/Original Mastery Snapshot/'
               '1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice')
PINS = {
    'A081': ('13. Gaps and Islands', 'e55eab41df5a04044c62b7294a1eb27c91a4eda2', 16),
    'A082': ('13. Gaps and Islands', 'e731eacbf70559c37d324b1cd84a1f859d694bdc', 16),
    'A083': ('13. Gaps and Islands', 'd4baa6518ee90522ac5a5a24368980015d965ecd', 16),
    'A084': ('13. Gaps and Islands', '33d010d698baa4b2f0b891d602aedc226c349017', 16),
    'A085': ('14. Data Quality and Deduplication', '3d7d0259231887892bd70f70cd017333ccda7001', 17),
    'A086': ('14. Data Quality and Deduplication', 'bb228c4f897bd6b93d25de198cd3f9bd3fc033eb', 17),
    'A087': ('14. Data Quality and Deduplication', 'd701707e2810e2d9065f2bb362e35f8310a5d8ba', 17),
    'A088': ('14. Data Quality and Deduplication', '4426613948ef36cf4d5d7bf67e5e4eca3cc0ea4e', 17),
    'A089': ('14. Data Quality and Deduplication', 'b93db48be869c37c1b28b47b70d755ca87bd4666', 17),
    'A090': ('14. Data Quality and Deduplication', 'c8f9f650232f532b202677d8cfd75f0eda4d041f', 17),
}
SCHEMA = '''
CREATE TABLE orders(order_id INTEGER,cust_id INTEGER,order_date TEXT,status TEXT,amount REAL);
CREATE TABLE payments(payment_id INTEGER,order_id INTEGER,paid_at TEXT,amount REAL,method TEXT);
CREATE TABLE seat_bookings(id INTEGER);
CREATE TABLE customer_snapshots(cust_id INTEGER,updated_at TEXT,version INTEGER,value TEXT);
'''
SQL = {
'A081': '''WITH days AS (SELECT DISTINCT cust_id,date(order_date) d FROM orders WHERE order_date IS NOT NULL),
numbered AS (SELECT cust_id,d,julianday(d)-ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY d) g FROM days)
SELECT cust_id,MIN(d),MAX(d) FROM numbered GROUP BY cust_id,g ORDER BY cust_id,MIN(d)''',
'A082': '''WITH days AS (SELECT DISTINCT cust_id,date(order_date) d FROM orders WHERE order_date IS NOT NULL),
numbered AS (SELECT cust_id,d,julianday(d)-ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY d) g FROM days),
streaks AS (SELECT cust_id,COUNT(*) n FROM numbered GROUP BY cust_id,g)
SELECT cust_id,MAX(n) FROM streaks GROUP BY cust_id ORDER BY cust_id''',
'A083': '''WITH months AS (SELECT DISTINCT cust_id,CAST(strftime('%Y',order_date) AS INTEGER)*12+
CAST(strftime('%m',order_date) AS INTEGER) m FROM orders WHERE order_date IS NOT NULL),
numbered AS (SELECT cust_id,m,m-ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY m) grp FROM months),
streaks AS (SELECT cust_id,COUNT(*) n FROM numbered GROUP BY cust_id,grp)
SELECT DISTINCT cust_id FROM streaks WHERE n>=3 ORDER BY cust_id''',
'A084': '''WITH ids AS (SELECT DISTINCT id FROM seat_bookings WHERE id IS NOT NULL),
numbered AS (SELECT id,id-ROW_NUMBER() OVER(ORDER BY id) grp FROM ids)
SELECT MIN(id),MAX(id) FROM numbered GROUP BY grp ORDER BY MIN(id)''',
'A085': '''SELECT order_id,paid_at,COUNT(*) row_count FROM payments GROUP BY order_id,paid_at
HAVING COUNT(*)>1 ORDER BY order_id,paid_at''',
'A086': '''WITH ranked AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY order_id ORDER BY paid_at ASC,payment_id ASC) rn FROM payments)
SELECT payment_id,order_id,paid_at,amount FROM ranked WHERE rn=1 ORDER BY order_id''',
'A087': '''DELETE FROM payments WHERE payment_id IN (
SELECT payment_id FROM (SELECT payment_id,ROW_NUMBER() OVER(PARTITION BY order_id,paid_at ORDER BY payment_id) rn FROM payments)
WHERE rn>1)''',
'A088': '''DELETE FROM payments WHERE payment_id IN (
SELECT payment_id FROM (SELECT payment_id,ROW_NUMBER() OVER(PARTITION BY order_id,paid_at ORDER BY payment_id) rn FROM payments)
WHERE rn>1)''',
'A089': '''WITH groups AS (SELECT COUNT(*) n FROM payments GROUP BY order_id,paid_at)
SELECT COALESCE(SUM(CASE WHEN n>1 THEN 1 ELSE 0 END),0),
COALESCE(SUM(CASE WHEN n>1 THEN n-1 ELSE 0 END),0) FROM groups''',
'A090': '''WITH ranked AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY cust_id ORDER BY updated_at DESC,version DESC) rn FROM customer_snapshots)
SELECT cust_id,updated_at,version,value FROM ranked WHERE rn=1 ORDER BY cust_id''',
}

def inspect():
    assert len(PINS)==len(SQL)==10
    for sid,(folder,expected_sha,page) in PINS.items():
        matches=list((BASE/folder).glob(sid+'. *.md'))
        assert len(matches)==1,(sid,'source file count',matches)
        path=matches[0]
        raw=path.read_bytes()
        sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert sha==expected_sha,(sid,'immutable source differs',sha,expected_sha)
        content=raw.decode('utf8')
        required=['# Advanced Q'+sid[1:]+'.',
                  'question '+str(int(sid[1:]))+', PDF p. '+str(page),
                  'seven-table example schema',
                  'NOT SOLVED YET',
                  '## My solution — SQLite\n\nPending.',
                  '## My solution — SQL Server\n\nPending.',
                  '## Official solution\n\nPending until']
        for marker in required:
            assert marker in content,(sid,'missing source section',marker)
        if sid=='A088':
            assert 'DELETE FROM payments' in content and 'SELECT MIN(payment_id)' in content
        print('PASS',sid,'immutable Git blob; statement/schema/sample and untouched Pending fields')

def check(sid,name,tables,expected,mutates=False):
    with sqlite3.connect(':memory:') as db:
        db.executescript(SCHEMA)
        for table,rows in tables.items():
            if rows:
                count=len(rows[0])
                assert all(len(r)==count for r in rows),(sid,table)
                db.executemany('INSERT INTO '+table+' VALUES ('+','.join('?'*count)+')',rows)
        if mutates:
            db.execute(SQL[sid]);actual=db.execute('SELECT payment_id,order_id,paid_at,amount FROM payments ORDER BY payment_id').fetchall()
        else:
            actual=db.execute(SQL[sid]).fetchall()
        assert actual==expected,(sid,name,actual,expected)
    print('PASS',sid,name,'(auditor-only bounded SQLite, NOT official/learner SQL)')

def o(rows): return {'orders':[(id,c,d,None,None) for id,c,d in rows]}
def p(rows): return {'payments':[(id,order,dt,amount,None) for id,order,dt,amount in rows]}

def main():
    inspect()
    check('A081','local consecutive days',o([(1,10,'2026-01-01'),(2,10,'2026-01-02'),(3,10,'2026-01-04'),(4,20,'2026-02-01')]),[(10,'2026-01-01','2026-01-02'),(10,'2026-01-04','2026-01-04'),(20,'2026-02-01','2026-02-01')])
    check('A081','duplicate dates and cross-year continuity',o([(1,1,'2025-12-31'),(2,1,'2026-01-01'),(3,1,'2026-01-01'),(4,1,'2026-01-03'),(5,2,None)]),[(1,'2025-12-31','2026-01-01'),(1,'2026-01-03','2026-01-03')])
    check('A082','local longest ordering streak',o([(1,10,'2026-01-01'),(2,10,'2026-01-02'),(3,10,'2026-01-03'),(4,10,'2026-01-05'),(5,20,'2026-02-10'),(6,20,'2026-02-11')]),[(10,3),(20,2)])
    check('A082','duplicate same-day rows not extra days and year crossing',o([(1,1,'2025-12-31'),(2,1,'2026-01-01'),(3,1,'2026-01-01'),(4,1,'2026-01-02'),(5,2,'2026-02-01')]),[(1,3),(2,1)])
    check('A083','local three-month example',o([(1,10,'2026-01-10'),(2,10,'2026-02-10'),(3,10,'2026-03-10'),(4,20,'2026-01-10'),(5,20,'2026-03-10'),(6,20,'2026-04-10')]),[(10,)])
    check('A083','December-January crossing, duplicate month, exact threshold',o([(1,1,'2025-12-01'),(2,1,'2026-01-11'),(3,1,'2026-01-20'),(4,1,'2026-02-01'),(5,2,'2026-01-01'),(6,2,'2026-03-01')]),[(1,)])
    check('A084','local seat range example',{'seat_bookings':[(1,),(2,),(3,),(7,),(8,),(10,)]},[(1,3),(7,8),(10,10)])
    check('A084','duplicate IDs, negative IDs and NULL',{'seat_bookings':[(-2,),(-1,),(-1,),(1,),(2,),(4,),(None,)]},[(-2,-1),(1,2),(4,4)])
    check('A085','local duplicate order/time',p([(1,10,'2026-01-01 09:00',50),(2,10,'2026-01-01 09:00',50),(3,10,'2026-01-02 09:00',20)]),[(10,'2026-01-01 09:00',2)])
    check('A085','NULL key and triple group',p([(1,10,None,20),(2,10,None,30),(3,20,'2026-01-01',10),(4,20,'2026-01-01',11),(5,20,'2026-01-01',12)]),[(10,None,2),(20,'2026-01-01',3)])
    check('A086','local earliest payment per order',p([(1,10,'2026-01-02 09:00',50),(2,10,'2026-01-01 09:00',20),(3,20,'2026-01-03 09:00',30)]),[(2,10,'2026-01-01 09:00',20),(3,20,'2026-01-03 09:00',30)])
    check('A086','earliest tie by payment ID and NULL timestamp sorts first',p([(1,10,'2026-01-01',10),(2,10,'2026-01-01',20),(3,20,'2026-01-01',30),(4,20,None,40)]),[(1,10,'2026-01-01',10),(4,20,None,40)])
    check('A087','local delete keeps lowest ID per key',p([(1,10,'2026-01-01 09:00',50),(2,10,'2026-01-01 09:00',50),(3,10,'2026-01-02 09:00',20)]),[(1,10,'2026-01-01 09:00',50),(3,10,'2026-01-02 09:00',20)],True)
    check('A087','triple and NULL-key groups; in-memory transaction only',p([(9,10,None,9),(3,10,None,3),(5,20,'2026-01-01',5),(2,20,'2026-01-01',2),(7,30,'2026-03-01',7)]),[(2,20,'2026-01-01',2),(3,10,None,3),(7,30,'2026-03-01',7)],True)
    check('A088','reviewer SQLite-safe deletion sample',p([(1,10,'2026-01-01 09:00',50),(2,10,'2026-01-01 09:00',50),(3,20,'2026-01-02 09:00',20)]),[(1,10,'2026-01-01 09:00',50),(3,20,'2026-01-02 09:00',20)],True)
    check('A088','reviewer corrected query keeps per-group minimum',p([(3,1,'2026-01-01',30),(1,1,'2026-01-01',10),(5,1,None,50),(4,1,None,40)]),[(1,1,'2026-01-01',10),(4,1,None,40)],True)
    check('A089','local two groups and three extras',p([(1,10,'2026-01-01',5),(2,10,'2026-01-01',5),(3,10,'2026-01-01',5),(4,20,'2026-01-02',5),(5,20,'2026-01-02',5)]),[(2,3)])
    check('A089','empty table zero metrics',{},[(0,0)])
    check('A090','local newest date then highest version',{'customer_snapshots':[(1,'2026-01-01',1,'old A'),(1,'2026-02-01',1,'newer A'),(1,'2026-02-01',2,'newest A'),(2,'2026-01-15',4,'old B'),(2,'2026-03-01',1,'new B')]},[(1,'2026-02-01',2,'newest A'),(2,'2026-03-01',1,'new B')])
    check('A090','version chosen on timestamp tie; later timestamp outranks larger version',{'customer_snapshots':[(1,'2026-01-01',99,'old'),(1,'2026-03-01',1,'new'),(2,'2026-02-01',1,'v1'),(2,'2026-02-01',2,'v2')]},[(1,'2026-03-01',1,'new'),(2,'2026-02-01',2,'v2')])
    print('PARTIAL A081-A090: ten SHA-pinned statements and twenty reviewer-only SQLite fixtures; original MySQL 8/PDF source and learner work unverified.')

if __name__=='__main__': main()
