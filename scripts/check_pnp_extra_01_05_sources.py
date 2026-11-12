#!/usr/bin/env python3
"""Extra X001-X005: original README/prompt identity + auditor-only SQLite fixtures."""
import hashlib, sqlite3
from pathlib import Path
BASE = Path(__file__).resolve().parents[1] / ('99. Reference Materials/Original Mastery Snapshot/'
    '1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice')
PINS = {'X001':'64263c8b18c5d86ad29761ade25b1e5089231ede',
        'X002':'119cf5e1e585f5e489feae778cbb709f3852c8a6',
        'X003':'5c2077f3c3867f2eb9d07739f447a2129b60dc62',
        'X004':'d47730dee16635b10f650412cc81cc06f02fa6d7',
        'X005':'3ff60456a287f52c1fa9512b4a3951d1c653be62'}
README = 'eb75fac446057899effefcb10029ff2048674ea2'
SCHEMA = '''
CREATE TABLE Products(ProductID INTEGER,Product TEXT,CategoryID INTEGER,Sub_Category TEXT,Brand TEXT,Rating REAL);
CREATE TABLE Category(CategoryID INTEGER,CategoryName TEXT);
CREATE TABLE OrderDetails(OrderDetailID INTEGER,ProductID INTEGER,Quantity INTEGER);
'''
# Synthetic candidate SQL is auditor-written. README explicitly provides NO answer key.
SQL = {
'X001': '''SELECT p.CategoryID,c.CategoryName,COUNT(*) product_count,
 COUNT(p.Rating) rated_count,ROUND(100.0*COUNT(p.Rating)/COUNT(*),2) rated_share_pct
 FROM Products p LEFT JOIN Category c ON p.CategoryID=c.CategoryID
 GROUP BY p.CategoryID,c.CategoryName ORDER BY p.CategoryID''',
'X002': '''SELECT Brand,COUNT(*) rated_product_count,ROUND(AVG(Rating),2) average_rating
 FROM Products WHERE Rating IS NOT NULL GROUP BY Brand
 HAVING COUNT(*)>=20 ORDER BY Brand''',
'X003': '''WITH units AS (SELECT p.ProductID,p.Product,p.Sub_Category,p.Rating,
 COALESCE(SUM(od.Quantity),0) units FROM Products p
 LEFT JOIN OrderDetails od ON od.ProductID=p.ProductID GROUP BY p.ProductID),
 ranked AS (SELECT *,ROW_NUMBER() OVER(PARTITION BY Sub_Category ORDER BY units,ProductID) rn,
 COUNT(*) OVER(PARTITION BY Sub_Category) n,
 AVG(Rating) OVER(PARTITION BY Sub_Category) avg_rating FROM units),
 medians AS (SELECT Sub_Category,
 AVG(CASE WHEN rn=(n+1)/2 OR rn=(n+2)/2 THEN units END) median_units
 FROM ranked GROUP BY Sub_Category)
 SELECT r.ProductID,r.Product,r.Rating,r.units FROM ranked r
 JOIN medians m ON r.Sub_Category IS m.Sub_Category
 WHERE r.Rating>r.avg_rating AND r.units<m.median_units ORDER BY r.ProductID''',
'X004': '''WITH units AS (SELECT p.ProductID,p.Rating,COALESCE(SUM(od.Quantity),0) units
 FROM Products p LEFT JOIN OrderDetails od ON od.ProductID=p.ProductID
 GROUP BY p.ProductID),
 bands AS (SELECT CASE WHEN Rating IS NULL THEN 'unrated'
 WHEN Rating<3 THEN 'below 3' WHEN Rating<4 THEN '3 to below 4'
 ELSE '4 and above' END band,units FROM units)
 SELECT band,COUNT(*),ROUND(AVG(units),2) FROM bands GROUP BY band
 ORDER BY CASE band WHEN 'below 3' THEN 1 WHEN '3 to below 4' THEN 2
 WHEN '4 and above' THEN 3 ELSE 4 END''',
'X005': '''SELECT p.ProductID,p.Product,p.Rating FROM Products p
 WHERE p.Rating IS NOT NULL AND NOT EXISTS
 (SELECT 1 FROM OrderDetails od WHERE od.ProductID=p.ProductID)
 ORDER BY p.ProductID'''
}
def pin(path,expected):
    b=path.read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    assert actual==expected,(str(path),actual,expected)
    return b.decode('utf-8')
def inspect():
    source=pin(BASE/'Source Materials/PrepNPlaced_SQL_100_v2/README.md',README)
    assert 'Extra practice: product ratings' in source and 'there is no answer key' in source
    assert len(PINS)==len(SQL)==5
    for sid,sha in PINS.items():
        m=list((BASE/'7. Extra Problems').glob(sid+'. *.md'))
        assert len(m)==1,(sid,m)
        s=pin(m[0],sha)
        for text in ('# Extra Q'+sid[1:]+'. Product ratings','NOT SOLVED YET',
            '### Sample input and expected output (illustrative)',
            '## My solution — SQLite\n\nPending.',
            '## My solution — SQL Server\n\nPending.',
            '## Official solution\n\nNo official solution is provided'):
            assert text in s,(sid,text)
        assert 'item '+str(int(sid[1:])) in s
        print('PASS',sid,'original archived prompt blob, README item and unsolved status')
    print('PASS README original pinned: all five independent prompts explicitly lack official answers')
def check(sid,name,tables,expected):
    with sqlite3.connect(':memory:') as db:
        db.executescript(SCHEMA)
        for table,rows in tables.items():
            if not rows: continue
            n=len(rows[0])
            assert all(len(r)==n for r in rows)
            db.executemany('INSERT INTO '+table+' VALUES ('+','.join('?'*n)+')',rows)
        actual=db.execute(SQL[sid]).fetchall()
        assert actual==expected,(sid,name,actual,expected)
    print('PASS',sid,name,'(reviewer SQLite; no official key or learner completion)')
def p(rows):return {'Products':rows}
def main():
    inspect()
    check('X001','local missing-category retains group',{'Category':[(1,'Electronics')],
       'Products':[(1,'A',1,'X','B',4),(2,'B',1,'X','B',None),(3,'C',99,'Y','B',3),(4,'D',99,'Y','B',None)]},
       [(1,'Electronics',2,1,50.0),(99,None,2,1,50.0)])
    check('X001','all-NULL ratings and NULL category',p([(1,'A',None,'X','B',None),(2,'B',None,'X','B',None),(3,'C',5,'Y','B',4)]),
       [(None,None,2,0,0.0),(5,None,1,1,100.0)])
    check('X002','20 rated Alpha and one highly rated Beta',p(
       [(i,'P',1,'X','Alpha',4) for i in range(1,21)]+[(21,'P',1,'X','Beta',5)]),[('Alpha',20,4.0)])
    check('X002','19 rated rejected; exact 20 excluding NULL',p(
       [(i,'P',1,'X','Small',5) for i in range(1,20)]+
       [(i,'P',1,'X','Big',3.5) for i in range(20,40)]+[(40,'P',1,'X','Big',None)]),
       [('Big',20,3.5)])
    check('X003','local above average below median',{'Products':[(1,'Item A',1,'Headphones','B',5),(2,'Item B',1,'Headphones','B',3),(3,'Item C',1,'Headphones','B',4)],
       'OrderDetails':[(11,1,1),(12,2,5),(13,3,3)]},[(1,'Item A',5.0,1)])
    check('X003','even median and unrated unsold product',{'Products':[(1,'A',1,'S','B',5),(2,'B',1,'S','B',3),(3,'C',1,'S','B',4),(4,'D',1,'S','B',None)],
       'OrderDetails':[(1,2,2),(2,3,4),(3,4,6)]},[(1,'A',5.0,0)])
    check('X004','local rating bands and unsold zero',{'Products':[(1,'A',1,'S','B',2.5),(2,'B',1,'S','B',3.5),(3,'C',1,'S','B',4.0),(4,'D',1,'S','B',None),(5,'E',1,'S','B',4.5)],
       'OrderDetails':[(11,1,2),(12,2,4),(13,3,6),(14,5,2)]},
       [('below 3',1,2.0),('3 to below 4',1,4.0),('4 and above',2,4.0),('unrated',1,0.0)])
    check('X004','boundary exactly 3/4, repeated lines and unrated',{'Products':[(1,'A',1,'S','B',3),(2,'B',1,'S','B',4),(3,'C',1,'S','B',None)],
       'OrderDetails':[(1,1,2),(2,1,4),(3,2,0)]},
       [('3 to below 4',1,6.0),('4 and above',1,0.0),('unrated',1,0.0)])
    check('X005','local rated-but-never-ordered',{'Products':[(1,'Item A',1,'S','B',4),(2,'Item B',1,'S','B',5),(3,'Item C',1,'S','B',None)],
       'OrderDetails':[(11,2,1)]},[(1,'Item A',4.0)])
    check('X005','orphan order detail and zero quantity still counts',{'Products':[(1,'A',1,'S','B',4),(2,'B',1,'S','B',5),(3,'C',1,'S','B',None)],
       'OrderDetails':[(1,2,0),(2,99,10)]},[(1,'A',4.0)])
    print('PARTIAL X001-X005: five original source checks, README explicitly no key, ten reviewer fixtures.')
if __name__=='__main__':main()
