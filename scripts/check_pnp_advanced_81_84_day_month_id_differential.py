#!/usr/bin/env python3
"""PARTIAL reviewer-only A081-A084 day/month/id gaps-and-islands oracles.

The imported A081-A090 checker contains auditor-authored SQLite SQL, not an
official MySQL answer or independent learner submission. All DBs are in memory.
"""
import hashlib
import itertools
import sqlite3
import unittest
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

import check_pnp_advanced_81_90_sources as previous

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/13. Gaps and Islands")
P065 = ("P065. Longest run of consecutive months with an order.md",
        "a7b40c93d66c2fa77e188081f41b91b91a581155")

def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def run(code, orders=(), ids=()):
    with closing(sqlite3.connect(":memory:")) as db:
        db.executescript(previous.SCHEMA)
        db.executemany("INSERT INTO orders(order_id,cust_id,order_date) VALUES (?,?,?)",
                       [(i,c,d) for i,(c,d) in enumerate(orders,1)])
        db.executemany("INSERT INTO seat_bookings(id) VALUES (?)", [(x,) for x in ids])
        return db.execute(previous.SQL[code]).fetchall()

def day_ranges(raw):
    days=sorted({date.fromisoformat(x[:10]) for x in raw if x is not None})
    if not days: return []
    out=[]; start=last=days[0]
    for x in days[1:]:
        if x!=last+timedelta(days=1):
            out.append((start.isoformat(),last.isoformat()))
            start=x
        last=x
    out.append((start.isoformat(),last.isoformat()))
    return out

def has_three_months(raw):
    months=sorted({date.fromisoformat(x[:10]).year*12+
                   date.fromisoformat(x[:10]).month for x in raw if x is not None})
    return any(months[i+1]==months[i]+1 and months[i+2]==months[i]+2
               for i in range(len(months)-2))

def int_ranges(values):
    ids=sorted({x for x in values if x is not None})
    if not ids: return []
    out=[]; start=last=ids[0]
    for x in ids[1:]:
        if x!=last+1:
            out.append((start,last))
            start=x
        last=x
    out.append((start,last))
    return out

class PNPAdvancedA081A084IndependentReviewer(unittest.TestCase):
    def test_01_original_git_blobs_and_pending_state(self):
        for sid in ("A081","A082","A083","A084"):
            folder,sha,page=previous.PINS[sid]
            files=list((previous.BASE/folder).glob(sid+". *.md"))
            self.assertEqual(len(files),1,sid)
            raw=files[0].read_bytes()
            self.assertEqual(blob(raw),sha,sid)
            text=raw.decode("utf-8")
            for marker in ("# Advanced Q"+sid[1:]+".",
                           "question "+str(int(sid[1:]))+", PDF p. 16",
                           "### Sample input and expected output (illustrative)",
                           "NOT SOLVED YET",
                           "## My solution — SQLite\n\nPending.",
                           "## My solution — SQL Server\n\nPending.",
                           "## Official solution\n\nPending until"):
                self.assertIn(marker,text,(sid,marker))
        raw=(BASE/P065[0]).read_bytes()
        self.assertEqual(blob(raw),P065[1])

    def test_02_a081_archived_local_illustration(self):
        rows=[(10,"2026-01-01"),(10,"2026-01-02"),(10,"2026-01-04"),(20,"2026-02-01")]
        self.assertEqual(run("A081",rows),[(10,"2026-01-01","2026-01-02"),
            (10,"2026-01-04","2026-01-04"),(20,"2026-02-01","2026-02-01")])

    def test_03_a082_archived_local_illustration(self):
        rows=[(10,x) for x in ("2026-01-01","2026-01-02","2026-01-03","2026-01-05")]
        rows += [(20,x) for x in ("2026-02-10","2026-02-11")]
        self.assertEqual(run("A082",rows),[(10,3),(20,2)])

    def test_04_a083_archived_local_illustration(self):
        rows=[(10,x) for x in ("2026-01-10","2026-02-10","2026-03-10")]
        rows += [(20,x) for x in ("2026-01-10","2026-03-10","2026-04-10")]
        self.assertEqual(run("A083",rows),[(10,)])

    def test_05_a084_archived_local_illustration(self):
        self.assertEqual(run("A084",ids=(1,2,3,7,8,10)),[(1,3),(7,8),(10,10)])

    def test_06_a081_243_independent_python_oracles(self):
        days=("2025-12-30","2025-12-31","2026-01-01","2026-01-03","2026-01-04")
        for counts in itertools.product(range(3),repeat=5):
            rows=[(1,x) for x,n in zip(days,counts) for _ in range(n)]
            rows += [(2,"2026-02-28"),(2,"2026-03-01")]
            expected=[(1,a,b) for a,b in day_ranges([x for c,x in rows if c==1])]
            expected += [(2,"2026-02-28","2026-03-01")]
            self.assertEqual(run("A081",rows),expected,counts)

    def test_07_a082_243_independent_python_oracles(self):
        days=("2025-12-30","2025-12-31","2026-01-01","2026-01-03","2026-01-04")
        for counts in itertools.product(range(3),repeat=5):
            rows=[(1,x) for x,n in zip(days,counts) for _ in range(n)]
            rows += [(2,"2026-02-01")]
            spans=day_ranges([x for c,x in rows if c==1])
            expected=[(1,max((date.fromisoformat(b)-date.fromisoformat(a)).days+1
                             for a,b in spans))] if spans else []
            expected += [(2,1)]
            self.assertEqual(run("A082",rows),expected,counts)

    def test_08_a083_729_independent_python_oracles(self):
        months=("2025-10-10","2025-11-10","2025-12-10","2026-01-10",
                "2026-03-10","2026-04-10")
        for counts in itertools.product(range(3),repeat=6):
            rows=[(1,x) for x,n in zip(months,counts) for _ in range(n)]
            rows += [(2,"2026-01-01"),(2,"2026-03-01")]
            expected=[(1,)] if has_three_months([x for c,x in rows if c==1]) else []
            self.assertEqual(run("A083",rows),expected,counts)

    def test_09_a084_729_independent_python_oracles(self):
        values=(-3,-2,0,1,4,5)
        for counts in itertools.product(range(3),repeat=6):
            ids=[v for v,n in zip(values,counts) for _ in range(n)]
            self.assertEqual(run("A084",ids=ids),int_ranges(ids),counts)

    def test_10_a081_a082_64_cross_question_length_invariants(self):
        days=("2026-01-01","2026-01-02","2026-01-03",
              "2026-01-05","2026-01-06","2026-01-08")
        for bits in itertools.product((0,1),repeat=6):
            rows=[(1,x) for x,flag in zip(days,bits) if flag]
            intervals=run("A081",rows)
            longest=max(((date.fromisoformat(b)-date.fromisoformat(a)).days+1
                         for _,a,b in intervals),default=None)
            self.assertEqual(run("A082",rows),[(1,longest)] if longest else [],bits)

    def test_11_leap_day_three_day_interval(self):
        rows=[(1,x) for x in ("2024-02-28","2024-02-29","2024-03-01")]
        self.assertEqual(run("A081",rows),[(1,"2024-02-28","2024-03-01")])
        self.assertEqual(run("A082",rows),[(1,3)])

    def test_12_duplicate_days_and_null_order_dates(self):
        rows=[(1,"2025-12-31"),(1,"2026-01-01"),(1,"2026-01-01"),
              (1,"2026-01-03"),(2,None)]
        self.assertEqual(run("A081",rows),[(1,"2025-12-31","2026-01-01"),
            (1,"2026-01-03","2026-01-03")])
        self.assertEqual(run("A082",rows),[(1,2)])

    def test_13_months_deduplicate_across_december_january(self):
        rows=[(1,x) for x in ("2025-12-01","2026-01-11","2026-01-20","2026-02-01")]
        rows += [(2,x) for x in ("2026-01-01","2026-03-01")]
        self.assertEqual(run("A083",rows),[(1,)])

    def test_14_id_null_duplicate_negative_boundaries(self):
        self.assertEqual(run("A084",ids=(-2,-1,-1,1,2,4,None)),[(-2,-1),(1,2),(4,4)])
        self.assertEqual(run("A084",ids=(None,None)),[])

    def test_15_invalid_nonnull_date_creates_phantom_streak(self):
        # Synthetic counterexample of auditor query; source may require valid dates.
        self.assertEqual(run("A081",[(1,"not-a-date")]),[(1,None,None)])
        self.assertEqual(run("A082",[(1,"not-a-date")]),[(1,1)])

    def test_16_timezone_policy_is_not_mysql_native_parity(self):
        rows=[(1,"2026-01-01T23:30:00-02:00"),
              (1,"2026-01-03T00:01:00+02:00")]
        self.assertEqual(run("A081",rows),[(1,"2026-01-02","2026-01-02")])
        self.assertEqual(run("A082",rows),[(1,1)])

    def test_17_p065_and_a083_different_output_contracts(self):
        p065=(BASE/P065[0]).read_text(encoding="utf-8")
        a083=list(BASE.glob("A083. *.md"))
        self.assertIn("Return the ten customers with the longest streaks",p065)
        self.assertIn("keeping everyone tied with tenth place",p065)
        self.assertEqual(len(a083),1)
        self.assertIn("Customers with three or more consecutive months",
                      a083[0].read_text(encoding="utf-8"))

if __name__=="__main__":
    unittest.main(verbosity=2)
