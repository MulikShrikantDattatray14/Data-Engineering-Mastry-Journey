#!/usr/bin/env python3
"""Read-only reviewer checks: W3Schools SQL RIGHT/FULL/SELF, CASE, NULL, AND/OR/NOT.

W3Schools pages were read manually on 2026-11-13. The SQL below is independently
authored SQLite fixture code. It does NOT execute W3Schools editor exercises,
authenticate an official key, or establish learner completion.
"""
from __future__ import annotations

import hashlib
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "99. Reference Materials/W3SCHOOLS-TOPICS.md": "c6328c2eb420f47e5585026a7bf3c0a4e41be720",
    "01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md": "d181dd73f96b1f2b7327600e290d52e9fd59a976",
    "01. SQL Mastery/02. Joins/0. Foundation Notes.md": "61d952c98f02a62c6591caaedf5c02cf0b43e3b1",
    "01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md": "af9cc8d5d47e0279fe0d8b0f9276b700ce496888",
    "01. SQL Mastery/PNP-ADVANCED-PENDING-A002-A003-A006-A007-A008-A009-NATIVE-POSTGRES-PARTIAL-AUDIT.md": "4871597413dc98e4c7300a7070c9b218a9b3aa19",
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/2. Joins/A006. MySQL has no FULL OUTER JOIN. Emulate one between customers and or.md": "20e4460e715ec53fd41f063e1368fa3753f2a0fd",
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/2. Joins/A011. List all pairs of colleagues in the same department, without mirro.md": "fb8226a93e2b3fa12e98b32bc29d13747157114c",
}

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

class ReviewerOnlySqlCases(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
    def tearDown(self):
        self.db.close()
    def rows(self, sql):
        return self.db.execute(sql).fetchall()

    def test_00_source_archive_is_immutable(self):
        for name, sha in PINS.items():
            with self.subTest(source=name):
                self.assertEqual(git_blob_sha((ROOT / name).read_bytes()), sha)

    def test_01_right_join_equivalent_keeps_unmatched_right_rows(self):
        self.db.executescript("""
          CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT);
          CREATE TABLE orders(id INTEGER PRIMARY KEY, cust_id INTEGER);
          INSERT INTO customers VALUES (1,'A'),(2,'B');
          INSERT INTO orders VALUES (10,1),(11,3),(12,NULL);
        """)
        self.assertEqual(self.rows("""
          SELECT o.id,c.id FROM orders AS o
          LEFT JOIN customers AS c ON c.id=o.cust_id ORDER BY o.id
        """), [(10,1),(11,None),(12,None)])
        # A right-preserving join is not equivalent to a customer-preserving left join.
        self.assertEqual(self.rows("""
          SELECT c.id,o.id FROM customers c
          LEFT JOIN orders o ON c.id=o.cust_id ORDER BY c.id
        """), [(1,10),(2,None)])

    def test_02_full_outer_emulation_preserves_both_sides_and_bag_duplicates(self):
        self.db.executescript("""
          CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT);
          CREATE TABLE orders(id INTEGER PRIMARY KEY, cust_id INTEGER);
          INSERT INTO customers VALUES (1,'A'),(2,'B');
          INSERT INTO orders VALUES (10,1),(11,3),(12,NULL),(13,1);
        """)
        sql = """
          SELECT c.id,c.name,o.id,o.cust_id FROM customers c
          LEFT JOIN orders o ON c.id=o.cust_id
          UNION ALL
          SELECT c.id,c.name,o.id,o.cust_id FROM orders o
          LEFT JOIN customers c ON c.id=o.cust_id
          WHERE c.id IS NULL
        """
        self.assertEqual(sorted(self.rows(sql), key=lambda x: x[2] if x[2] is not None else -1),
                         [(2,'B',None,None),(1,'A',10,1),(None,None,11,3),
                          (None,None,12,None),(1,'A',13,1)])
        self.assertEqual(len(self.rows(sql)),5)

    def test_03_full_outer_empty_side_and_all_unmatched(self):
        self.db.executescript("""
          CREATE TABLE l(id INTEGER PRIMARY KEY);
          CREATE TABLE r(id INTEGER PRIMARY KEY, left_id INTEGER);
          INSERT INTO r VALUES (1,9),(2,NULL);
        """)
        self.assertEqual(self.rows("""
          SELECT l.id,r.id FROM l LEFT JOIN r ON l.id=r.left_id
          UNION ALL
          SELECT l.id,r.id FROM r LEFT JOIN l ON l.id=r.left_id WHERE l.id IS NULL
          ORDER BY 2
        """), [(None,1),(None,2)])

    def test_04_self_join_source_style_mirrors_pairs_and_ordered_pair_removes_them(self):
        self.db.executescript("""
          CREATE TABLE e(id INT, dept INT);
          INSERT INTO e VALUES (1,10),(2,10),(3,10),(4,20),(5,NULL);
        """)
        self.assertEqual(len(self.rows("""
          SELECT a.id,b.id FROM e a JOIN e b
          ON a.dept=b.dept AND a.id<>b.id
        """)),6)
        self.assertEqual(self.rows("""
          SELECT a.id,b.id FROM e a JOIN e b
          ON a.dept=b.dept AND a.id<b.id ORDER BY a.id,b.id
        """),[(1,2),(1,3),(2,3)])

    def test_05_case_first_true_wins_and_missing_else_is_null(self):
        self.db.executescript("""
          CREATE TABLE p(price INTEGER);
          INSERT INTO p VALUES (10),(20),(50),(51),(NULL);
        """)
        self.assertEqual(self.rows("""
          SELECT price, CASE
            WHEN price <= 20 THEN 'low'
            WHEN price <= 50 THEN 'middle'
            ELSE 'other' END
          FROM p ORDER BY rowid
        """),[(10,'low'),(20,'low'),(50,'middle'),(51,'other'),(None,'other')])
        self.assertEqual(self.rows("""
          SELECT CASE WHEN price > 100 THEN 'high' END FROM p
        """),[(None,)]*5)

    def test_06_coalesce_is_first_nonnull_not_first_nonblank(self):
        self.db.executescript("""
          CREATE TABLE contacts(a TEXT,b TEXT,c TEXT);
          INSERT INTO contacts VALUES ('  ',NULL,'x@example.test'),
                                     (NULL,'555',NULL),
                                     (NULL,NULL,NULL);
        """)
        self.assertEqual(self.rows("""
          SELECT COALESCE(a,b,c,'none') FROM contacts
        """),[('  ',),('555',),('none',)])
        self.assertEqual(self.rows("""
          SELECT COALESCE(NULLIF(TRIM(a),''),NULLIF(TRIM(b),''),
                          NULLIF(TRIM(c),''),'none') FROM contacts
        """),[('x@example.test',),('555',),('none',)])

    def test_07_null_arithmetic_vs_explicit_zero_substitution(self):
        self.db.executescript("""
          CREATE TABLE stock(price REAL, on_hand INT, inbound INT);
          INSERT INTO stock VALUES (10,2,NULL),(10,2,3);
        """)
        self.assertEqual(self.rows("""
          SELECT price*(on_hand+inbound),price*(on_hand+COALESCE(inbound,0))
          FROM stock
        """),[(None,20.0),(50.0,50.0)])

    def test_08_and_or_operator_precedence_and_parentheses(self):
        self.db.executescript("""
          CREATE TABLE t(id INT, country TEXT, score INT);
          INSERT INTO t VALUES (1,'Spain',90),(2,'Spain',30),
                               (3,'Brazil',90),(4,'France',90),(5,NULL,90);
        """)
        self.assertEqual(self.rows("""
          SELECT id FROM t WHERE country='Spain' OR country='Brazil' AND score>50
          ORDER BY id
        """),[(1,),(2,),(3,)])
        self.assertEqual(self.rows("""
          SELECT id FROM t WHERE (country='Spain' OR country='Brazil') AND score>50
          ORDER BY id
        """),[(1,),(3,)])

    def test_09_not_preserves_sql_unknown(self):
        self.db.executescript("""
          CREATE TABLE t(id INT, country TEXT);
          INSERT INTO t VALUES (1,'Spain'),(2,'Brazil'),(3,NULL);
        """)
        self.assertEqual(self.rows("""
          SELECT id FROM t WHERE NOT country='Spain' ORDER BY id
        """),[(2,)])
        self.assertEqual(self.rows("""
          SELECT id FROM t WHERE country<>'Spain' OR country IS NULL ORDER BY id
        """),[(2,),(3,)])

    def test_10_left_join_on_filter_vs_where_filter(self):
        self.db.executescript("""
          CREATE TABLE c(id INT);
          CREATE TABLE o(id INT,cid INT,status TEXT);
          INSERT INTO c VALUES (1),(2);
          INSERT INTO o VALUES (10,1,'pending');
        """)
        self.assertEqual(self.rows("""
          SELECT c.id,o.id FROM c LEFT JOIN o
          ON c.id=o.cid AND o.status='paid' ORDER BY c.id
        """),[(1,None),(2,None)])
        self.assertEqual(self.rows("""
          SELECT c.id,o.id FROM c LEFT JOIN o ON c.id=o.cid
          WHERE o.status='paid' ORDER BY c.id
        """),[])

    def test_11_right_only_filter_must_use_nonnullable_left_match_key(self):
        self.db.executescript("""
          CREATE TABLE c(id INT PRIMARY KEY, note TEXT);
          CREATE TABLE o(id INT, cid INT);
          INSERT INTO c VALUES (1,NULL),(2,'ok');
          INSERT INTO o VALUES (10,1),(11,9);
        """)
        # Nullable note would misclassify matched customer 1 as right-only.
        self.assertEqual(self.rows("""
          SELECT o.id FROM o LEFT JOIN c ON o.cid=c.id
          WHERE c.id IS NULL ORDER BY o.id
        """),[(11,)])
        self.assertEqual(self.rows("""
          SELECT o.id FROM o LEFT JOIN c ON o.cid=c.id
          WHERE c.note IS NULL ORDER BY o.id
        """),[(10,),(11,)])

if __name__ == "__main__":
    unittest.main(verbosity=2)
