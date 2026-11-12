#!/usr/bin/env python3
"""Partial A091-A100 source-pinned SQLite fixture audit; NO official/learner verification."""
import hashlib
import sqlite3
from pathlib import Path
BASE = Path(__file__).resolve().parents[1] / ('99. Reference Materials/Original Mastery Snapshot/'
    '1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice')
PINS = {
'A091':('11. NULL Logic','8b8d8dd763bfe3455a96b2b030874813baa640e7',18),
'A092':('11. NULL Logic','01e258132caf62d9de02ea1a8abf364ab99e21a0',18),
'A093':('11. NULL Logic','70d5ceadc9fa1c6e105a80624f40656e52cf2bc3',18),
'A094':('11. NULL Logic','c3c7571909e4be539c95f83e6e0be50d6c85e8a6',18),
'A095':('11. NULL Logic','dc3eb037dbae6341c974185fd9c5baf6df794698',18),
'A096':('12. Dates and Time','403c5e129970268f24a925e8527d55d833b7a3f6',19),
'A097':('12. Dates and Time','5fd46f87854e52c3ba4c22fd56e635774c04edd6',19),
'A098':('12. Dates and Time','89555669d558721ab2f949a612d377c0095680e0',19),
'A099':('12. Dates and Time','ac542b2b0366010d6888354e8a8b047475349bb5',19),
'A100':('12. Dates and Time','277fafe7f196cdcb7b2eaef65602ef39c2455dc5',19)}
SCHEMA = '''
CREATE TABLE employees(emp_id INTEGER,manager_id INTEGER,salary REAL);
CREATE TABLE customer_contacts(cust_id INTEGER,work_phone TEXT,mobile TEXT,email TEXT);
CREATE TABLE stage(id INTEGER,batch_code TEXT);
CREATE TABLE target(id INTEGER,batch_code TEXT);
CREATE TABLE order_items(item_id INTEGER,discount REAL);
CREATE TABLE orders(order_id INTEGER,cust_id INTEGER,order_date TEXT);
CREATE INDEX idx_order_date ON orders(order_date);
CREATE TABLE customers(cust_id INTEGER,signup_date TEXT);
'''
# Candidate SQL is authored only by the auditor, not supplied by a course/provider.
SQL = {
'A091': 'SELECT COUNT(*),COUNT(manager_id),COUNT(DISTINCT manager_id) FROM employees',
'A092': 'SELECT emp_id,salary FROM employees ORDER BY salary IS NULL,salary DESC,emp_id',
'A093': "SELECT cust_id,COALESCE(work_phone,mobile,email,'no contact') FROM customer_contacts ORDER BY cust_id",
'A094': '''SELECT s.id,t.id FROM stage s JOIN target t
 ON s.batch_code=t.batch_code OR (s.batch_code IS NULL AND t.batch_code IS NULL)
 ORDER BY s.id,t.id''',
'A095': '''SELECT AVG(discount),CAST(SUM(discount) AS REAL)/NULLIF(COUNT(*),0),
 CAST(SUM(discount) AS REAL)/NULLIF(COUNT(discount),0) FROM order_items''',
# Archived DATEDIFF(CURDATE(),order_date)<=30 includes future dates: source-equivalent lower-only.
'A096': "SELECT order_id FROM orders WHERE order_date >= date('2026-02-01','-30 days') ORDER BY order_id",
'A097': '''SELECT order_id,date(order_date,'start of month'),
date(order_date,'start of month','+1 month','-1 day') FROM orders ORDER BY order_id''',
'A098': '''SELECT date(order_date,'-' || ((CAST(strftime('%w',order_date) AS INTEGER)+6)%7) || ' days'),
COUNT(*) FROM orders WHERE order_date IS NOT NULL GROUP BY 1 ORDER BY 1''',
'A099': '''WITH firsts AS (SELECT cust_id,MIN(order_date) first_order_date FROM orders
WHERE order_date IS NOT NULL GROUP BY cust_id)
SELECT c.cust_id,f.first_order_date FROM customers c JOIN firsts f USING(cust_id)
WHERE julianday(f.first_order_date)-julianday(c.signup_date) BETWEEN 0 AND 7 ORDER BY c.cust_id''',
'A100': '''WITH firsts AS (SELECT cust_id,MIN(order_date) first_date FROM orders
WHERE order_date IS NOT NULL GROUP BY cust_id)
SELECT strftime('%Y%m',f.first_date),COUNT(DISTINCT f.cust_id)
FROM firsts f WHERE EXISTS (SELECT 1 FROM orders o WHERE o.cust_id=f.cust_id
AND o.order_date>=date(f.first_date,'start of month','+1 month')
AND o.order_date<date(f.first_date,'start of month','+2 months'))
GROUP BY 1 ORDER BY 1'''}
def inspect():
    assert len(PINS)==len(SQL)==10
    for sid,(folder,expected,page) in PINS.items():
        matches=list((BASE/folder).glob(sid+'. *.md'))
        assert len(matches)==1,(sid,matches)
        raw=matches[0].read_bytes()
        sha=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert sha==expected,(sid,'Git blob mismatch',sha,expected)
        s=raw.decode('utf-8')
        for marker in ('# Advanced Q'+sid[1:]+'.',
                       'question '+str(int(sid[1:]))+', PDF p. '+str(page),
                       '### Sample input and expected output (illustrative)',
                       'NOT SOLVED YET',
                       '## My solution — SQLite\n\nPending.',
                       '## My solution — SQL Server\n\nPending.',
                       '## Official solution\n\nPending until'):
            assert marker in s,(sid,'missing original record',marker)
        if sid=='A096': assert 'DATEDIFF(CURDATE(), order_date) <= 30' in s
        print('PASS',sid,'pinned original statement, illustrative example, Pending learner and official fields')
def check(sid,name,rows,expected):
    with sqlite3.connect(':memory:') as db:
        db.executescript(SCHEMA)
        for table,items in rows.items():
            if not items: continue
            n=len(items[0])
            assert all(len(item)==n for item in items)
            db.executemany('INSERT INTO '+table+' VALUES ('+','.join('?'*n)+')',items)
        actual=db.execute(SQL[sid]).fetchall()
        assert actual==expected,(sid,name,actual,expected)
        if sid=='A096':
            plan=db.execute("EXPLAIN QUERY PLAN SELECT order_id FROM orders WHERE order_date >= date('2026-02-01','-30 days')").fetchall()
            assert any('SEARCH' in str(p[-1]) and 'idx_order_date' in str(p[-1]) for p in plan),(sid,plan)
    print('PASS',sid,name,'(bounded auditor SQLite, NOT official/learner verification)')
def e(r): return {'employees':r}
def o(r): return {'orders':r}
def main():
    inspect()
    check('A091','local three counts',e([(1,None,0),(2,1,0),(3,1,0),(4,2,0)]),[(4,3,2)])
    check('A091','all NULL managers',e([(1,None,0),(2,None,0)]),[(2,0,0)])
    check('A092','local NULL last',e([(1,None,None),(2,None,100),(3,None,50)]),[(2,100.0),(3,50.0),(1,None)])
    check('A092','ties/negative/zero/two NULL',e([(1,None,None),(2,None,-1),(3,None,0),(4,None,0),(5,None,None)]),[(3,0.0),(4,0.0),(2,-1.0),(1,None),(5,None)])
    check('A093','local contact fallback',{'customer_contacts':[(1,'555-0101','555-0201','ana@example.com'),(2,None,'555-0202','ben@example.com'),(3,None,None,'cy@example.com'),(4,None,None,None)]},[(1,'555-0101'),(2,'555-0202'),(3,'cy@example.com'),(4,'no contact')])
    check('A093','empty strings are non-NULL',{'customer_contacts':[(1,'','111','a@b'),(2,None,'','a@b'),(3,None,None,None)]},[(1,''),(2,''),(3,'no contact')])
    check('A094','local NULL-safe join',{'stage':[(1,None),(2,'A')],'target':[(10,None),(20,'A')]},[(1,10),(2,20)])
    check('A094','NULL many-to-many join',{'stage':[(1,None),(2,None),(3,'B')],'target':[(10,None),(11,None),(12,'A')]},[(1,10),(1,11),(2,10),(2,11)])
    check('A095','local NULL denominator example',{'order_items':[(1,10),(2,None),(3,20)]},[(15.0,10.0,15.0)])
    check('A095','all-NULL discount',{'order_items':[(1,None),(2,None)]},[(None,None,None)])
    check('A096','local 30-day threshold and index-plan',o([(1,1,'2026-01-01'),(2,1,'2026-01-02'),(3,1,'2026-01-31'),(4,1,'2026-02-01')]),[(2,),(3,),(4,)])
    check('A096','original DATEDIFF condition includes FUTURE date',o([(1,1,'2026-01-02'),(2,1,'2026-02-02'),(3,1,None),(4,1,'2025-12-01')]),[(1,),(2,)])
    check('A097','local first-last month',o([(1,1,'2026-01-15'),(2,1,'2026-02-10')]),[(1,'2026-01-01','2026-01-31'),(2,'2026-02-01','2026-02-28')])
    check('A097','leap February, December, NULL',o([(1,1,'2024-02-29'),(2,1,'2026-12-31'),(3,1,None)]),[(1,'2024-02-01','2024-02-29'),(2,'2026-12-01','2026-12-31'),(3,None,None)])
    check('A098','local week starts Monday',o([(1,1,'2026-01-04'),(2,1,'2026-01-05'),(3,1,'2026-01-07'),(4,1,'2026-01-11'),(5,1,'2026-01-12')]),[('2025-12-29',1),('2026-01-05',3),('2026-01-12',1)])
    check('A098','cross-year and same-day counts',o([(1,1,'2025-12-29'),(2,1,'2026-01-04'),(3,1,'2026-01-05'),(4,1,'2026-01-05'),(5,1,None)]),[('2025-12-29',2),('2026-01-05',2)])
    check('A099','local signup plus exactly seven days',{'customers':[(1,'2026-01-01'),(2,'2026-01-01'),(3,'2026-01-01')],'orders':[(11,1,'2026-01-08'),(12,2,'2026-01-09')]},[(1,'2026-01-08')])
    check('A099','earlier pre-signup first order excludes',{'customers':[(1,'2026-01-10'),(2,'2026-01-10'),(3,None)],'orders':[(1,1,'2026-01-09'),(2,1,'2026-01-12'),(3,2,'2026-01-10'),(4,3,'2026-01-11')]},[(2,'2026-01-10')])
    check('A100','local following-calendar-month cohort',o([(1,10,'2026-01-10'),(2,10,'2026-02-05'),(3,20,'2026-01-20'),(4,20,'2026-03-01'),(5,30,'2026-02-01'),(6,30,'2026-03-10')]),[('202601',1),('202602',1)])
    check('A100','Dec to Jan and repeated return dedup',o([(1,1,'2025-12-30'),(2,1,'2026-01-01'),(3,1,'2026-01-22'),(4,2,'2025-12-01'),(5,2,'2025-12-28'),(6,3,'2026-01-01'),(7,3,'2026-02-01')]),[('202512',1),('202601',1)])
    print('PARTIAL A091-A100: 10 pinned original source statements, 20 reviewer-only fixtures. Source PDF, native MySQL and learner work not verified.')
if __name__=='__main__': main()
