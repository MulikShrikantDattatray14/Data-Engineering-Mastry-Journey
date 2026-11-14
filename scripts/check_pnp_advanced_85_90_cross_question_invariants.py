#!/usr/bin/env python3
"""PARTIAL reviewer-only PNP Advanced A085-A090 cross-question audit.
Source-blob pinned; all writes in in-memory SQLite. No official MySQL or learner answer.
"""
import collections
import hashlib
import re
import sqlite3
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT / ("99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
             "1. SQL Mastry/2.PNP- foundations and practice/14. Data Quality and Deduplication")
PINS={
 "A085":"3d7d0259231887892bd70f70cd017333ccda7001",
 "A086":"bb228c4f897bd6b93d25de198cd3f9bd3fc033eb",
 "A087":"d701707e2810e2d9065f2bb362e35f8310a5d8ba",
 "A088":"4426613948ef36cf4d5d7bf67e5e4eca3cc0ea4e",
 "A089":"b93db48be869c37c1b28b47b70d755ca87bd4666",
 "A090":"c8f9f650232f532b202677d8cfd75f0eda4d041f",
}
DUPS="""SELECT order_id,paid_at,COUNT(*) FROM payments
        GROUP BY order_id,paid_at HAVING COUNT(*)>1"""
COUNTS="""SELECT COALESCE(SUM(n>1),0),COALESCE(SUM(CASE WHEN n>1 THEN n-1 ELSE 0 END),0)
          FROM (SELECT COUNT(*) n FROM payments GROUP BY order_id,paid_at)"""
DELETE="""DELETE FROM payments WHERE payment_id IN (
         SELECT payment_id FROM (SELECT payment_id,ROW_NUMBER() OVER
         (PARTITION BY order_id,paid_at ORDER BY payment_id) rn FROM payments)
         WHERE rn>1)"""
EARLIEST="""SELECT payment_id,order_id,paid_at FROM (
           SELECT payment_id,order_id,paid_at,ROW_NUMBER() OVER
           (PARTITION BY order_id ORDER BY paid_at,payment_id) rn FROM payments)
           WHERE rn=1"""
LATEST="""SELECT value FROM (SELECT value,ROW_NUMBER() OVER (
         PARTITION BY cust_id ORDER BY updated_at DESC,version DESC) rn
         FROM customer_snapshots) WHERE rn=1"""

def source(sid):
    paths=list(BASE.glob(sid+". *.md"))
    assert len(paths)==1,(sid,paths)
    raw=paths[0].read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    assert sha==PINS[sid],(sid,sha)
    return raw.decode("utf-8")

def database(rows=()):
    db=sqlite3.connect(":memory:")
    db.execute("CREATE TABLE payments(payment_id INTEGER PRIMARY KEY,order_id INTEGER,paid_at TEXT)")
    db.executemany("INSERT INTO payments VALUES(?,?,?)",rows)
    return db

class PaymentInvariants(unittest.TestCase):
    def test_six_sources_sha_pending_and_statement(self):
        for sid in PINS:
            with self.subTest(sid=sid):
                raw=source(sid)
                self.assertIn("# Advanced Q"+sid[1:]+".",raw)
                self.assertIn("PDF p. 17",raw)
                self.assertIn("NOT SOLVED YET",raw)
                self.assertIn("## My solution — SQLite\n\nPending.",raw)
                self.assertIn("## Official solution\n\nPending",raw)

    def test_a085_a089_a087_counts_survivors_and_rerun(self):
        cases=[
          [(1,10,"2026-01-01"),(2,10,"2026-01-01"),(3,10,"2026-02-01"),
           (4,20,"2026-03-01"),(5,20,"2026-03-01"),(6,20,"2026-03-01")],
          [(1,None,None),(2,None,None),(3,10,None),(4,10,None),
           (5,10,"2026-01-01"),(6,10,"2026-01-01"),(7,10,"2026-01-02")],
          [(1,10,"2026-01-01"),(2,10,"2026-01-02"),(3,20,None)],
          []
        ]
        for rows in cases:
            with self.subTest(rows=rows),database(rows) as db:
                counts=collections.Counter((o,t) for _,o,t in rows)
                want=sorted((str(o),str(t),n) for (o,t),n in counts.items() if n>1)
                got=sorted((str(o),str(t),n) for o,t,n in db.execute(DUPS))
                self.assertEqual(got,want)
                groups=sum(n>1 for n in counts.values())
                extra=sum(n-1 for n in counts.values() if n>1)
                self.assertEqual(db.execute(COUNTS).fetchone(),(groups,extra))
                db.execute(DELETE)
                actual=[v[0] for v in db.execute("SELECT payment_id FROM payments ORDER BY payment_id")]
                expected=sorted(min(pid for pid,o,t in rows if (o,t)==key) for key in counts)
                self.assertEqual(actual,expected)
                self.assertEqual(len(rows)-len(actual),extra)
                db.execute(DELETE)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM payments").fetchone(),(len(counts),))

    def test_a086_vs_a087_natural_key_changes_survivors(self):
        rows=[(1,10,"2026-01-01"),(2,10,"2026-02-01"),
              (3,10,"2026-02-01"),(4,20,"2026-03-01")]
        with database(rows) as db:
            self.assertEqual(db.execute(EARLIEST).fetchall(),
                             [(1,10,"2026-01-01"),(4,20,"2026-03-01")])
            db.execute(DELETE)
            self.assertEqual(db.execute("SELECT payment_id FROM payments ORDER BY payment_id").fetchall(),
                             [(1,),(2,),(4,)])
            self.assertEqual(db.execute(COUNTS).fetchone(),(0,0))

    def test_a088_original_delete_sql_runs_on_sqlite_not_mysql_evidence(self):
        m=re.search(r"(?s)\x60{3}sql\s*(.*?)\x60{3}",source("A088"))
        self.assertIsNotNone(m)
        sql=m.group(1).strip()
        self.assertIn("SELECT MIN(payment_id)",sql)
        with database([(1,10,"2026-01-01"),(2,10,"2026-01-01"),
                       (3,20,"2026-02-01")]) as db:
            db.execute(sql)
            self.assertEqual(db.execute("SELECT payment_id FROM payments ORDER BY payment_id").fetchall(),
                             [(1,),(3,)])

    def test_a086_null_timestamp_first_in_sqlite(self):
        with database([(1,10,None),(2,10,"2026-01-01")]) as db:
            self.assertEqual(db.execute(EARLIEST).fetchone(),(1,10,None))

    def test_a090_identical_tie_policy_changes_with_insertion_order(self):
        winners=[]
        for pair in [("first","second"),("second","first")]:
            with sqlite3.connect(":memory:") as db:
                db.execute("CREATE TABLE customer_snapshots(cust_id INTEGER,updated_at TEXT,version INTEGER,value TEXT)")
                db.executemany("INSERT INTO customer_snapshots VALUES(1,'2026-02-01',2,?)",
                               [(v,) for v in pair])
                winners.append(db.execute(LATEST).fetchone()[0])
        self.assertEqual(winners,["first","second"])

    def test_a087_rollback_in_temporary_database(self):
        with database([(1,10,"t"),(2,10,"t"),(3,20,"t")]) as db:
            db.execute("SAVEPOINT audit")
            db.execute(DELETE)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM payments").fetchone(),(2,))
            db.execute("ROLLBACK TO audit")
            db.execute("RELEASE audit")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM payments").fetchone(),(3,))

if __name__=="__main__":
    unittest.main(verbosity=2)
