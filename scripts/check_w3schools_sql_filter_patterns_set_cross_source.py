#!/usr/bin/env python3
"""Read-only, source-pinned cross-source checks for eight W3Schools SQL lessons.

Official lesson bodies were manually inspected 2026-11-13; this executable is
reviewer-authored SQLite fixtures, NOT a W3Schools editor replay, official key,
user submission, or proof of mastery. No source files are written.
"""
import hashlib
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "99. Reference Materials/W3SCHOOLS-TOPICS.md": "c6328c2eb420f47e5585026a7bf3c0a4e41be720",
    "01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md": "d181dd73f96b1f2b7327600e290d52e9fd59a976",
    "01. SQL Mastery/01. Advanced SELECT/0. Foundation Notes.md": "1ed1077d492a3bd9db25018650b5c1f3cae1371f",
    "01. SQL Mastery/03. Sorting and Grouping/0. Foundation Notes.md": "5cf690cb6ca5942795fe332aa447bbf77e14232e",
    "01. SQL Mastery/06. Subqueries/0. Foundation Notes.md": "0414dd556eb4e327d45971763eb91e3730a6ce09",
    "01. SQL Mastery/08. SQL Strings and Patterns/0. Foundation Notes.md": "63649bd6ad3a44449873136d90d3bbb2c724dbab",
    "01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md": "af9cc8d5d47e0279fe0d8b0f9276b700ce496888",
    "01. SQL Mastery/BOSSCODER-SELECT-FOUNDATION-INDEPENDENT-AUDIT.md": "787d8e1a6fb0dc23f530902f359853fd262c9a23",
    "01. SQL Mastery/BOSSCODER-SUBQUERIES-INDEPENDENT-AUDIT.md": "4a3bc13d132d1cd246c5d1c3e7255871f124087d",
}
OFFICIAL_PAGES = ("sql_distinct.asp", "sql_where.asp", "sql_orderby.asp",
                  "sql_like.asp", "sql_in.asp", "sql_between.asp",
                  "sql_exists.asp", "sql_union.asp")


class CrossSourceFilteringAndSet(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript("""
            CREATE TABLE Customers(id INTEGER PRIMARY KEY, city TEXT,
                                   name TEXT, score INTEGER);
            INSERT INTO Customers VALUES
              (1,'Berlin','Alice',10),(2,'Berlin','alex',20),
              (3,'London','Bob',20),(4,NULL,'Zed',NULL),
              (5,'Paris','Anne',30),(6,'London','Lulu',NULL);
            CREATE TABLE Orders(id INTEGER PRIMARY KEY, cust_id INTEGER,
                                created_at TEXT, price INTEGER);
            INSERT INTO Orders VALUES
              (11,1,'2026-07-01 00:00:00',40),
              (12,1,'2026-07-31 23:59:59',150),
              (13,3,'2026-08-01 00:00:00',200),
              (14,NULL,'2026-07-15 12:00:00',50);
            CREATE TABLE RegionA(value TEXT);
            INSERT INTO RegionA VALUES ('DE'),('UK'),('DE'),(NULL);
            CREATE TABLE RegionB(value TEXT);
            INSERT INTO RegionB VALUES ('UK'),('FR'),(NULL);
        """)

    def tearDown(self):
        self.db.close()

    def q(self, sql):
        return self.db.execute(sql).fetchall()

    def test_00_exact_git_blob_guards_and_scope(self):
        self.assertEqual(len(OFFICIAL_PAGES), 8)
        for path, expected in PINS.items():
            with self.subTest(path=path):
                b = (ROOT / path).read_bytes()
                got = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
                self.assertEqual(got, expected)
        index = (ROOT / "99. Reference Materials/W3SCHOOLS-TOPICS.md").read_text()
        for page in ("sql_like.asp", "sql_in.asp", "sql_exists.asp"):
            self.assertIn(page, index)

    def test_01_distinct_null_and_count_distinct_differ(self):
        self.assertEqual(self.q("SELECT DISTINCT city FROM Customers ORDER BY city"),
                         [(None,),('Berlin',),('London',),('Paris',)])
        self.assertEqual(self.q("SELECT COUNT(DISTINCT city) FROM Customers"), [(3,)])
        self.assertEqual(self.q("SELECT COUNT(*) FROM (SELECT DISTINCT city,name FROM Customers)"), [(6,)])

    def test_02_where_three_valued_filtering(self):
        self.assertEqual(self.q("SELECT id FROM Customers WHERE score>=20 ORDER BY id"),
                         [(2,),(3,),(5,)])
        self.assertEqual(self.q("SELECT id FROM Customers WHERE NOT(score>=20) ORDER BY id"),
                         [(1,)])
        self.assertEqual(self.q("SELECT id FROM Customers WHERE score>=20 OR score IS NULL ORDER BY id"),
                         [(2,),(3,),(4,),(5,),(6,)])

    def test_03_order_by_tie_and_explicit_null_last(self):
        self.assertEqual(self.q("SELECT id FROM Customers ORDER BY score DESC,id ASC"),
                         [(5,),(2,),(3,),(1,),(4,),(6,)])
        self.assertEqual(self.q("""
          SELECT id FROM Customers
          ORDER BY CASE WHEN score IS NULL THEN 1 ELSE 0 END,score ASC,id ASC
        """), [(1,),(2,),(3,),(5,),(4,),(6,)])
        self.assertEqual(self.q("SELECT id FROM Customers ORDER BY score DESC,id LIMIT 2"),
                         [(5,),(2,)])

    def test_04_like_percent_underscore_and_null(self):
        self.assertEqual(self.q("SELECT id FROM Customers WHERE name LIKE 'A%' ORDER BY id"),
                         [(1,),(2,),(5,)])
        self.assertEqual(self.q("SELECT id FROM Customers WHERE city LIKE 'L_nd_n' ORDER BY id"),
                         [(3,),(6,)])
        self.assertEqual(self.q("SELECT 'A_B' LIKE 'A!_B' ESCAPE '!'"), [(1,)])

    def test_05_in_and_not_in_null_poisoning(self):
        self.assertEqual(self.q("SELECT id FROM Customers WHERE city IN ('Berlin','London') ORDER BY id"),
                         [(1,),(2,),(3,),(6,)])
        self.assertEqual(self.q("SELECT 'Tokyo' NOT IN (SELECT city FROM Customers)"), [(None,)])
        self.assertEqual(self.q("""
            SELECT NOT EXISTS(SELECT 1 FROM Customers WHERE city='Tokyo')
        """), [(1,)])

    def test_06_between_inclusive_with_null(self):
        self.assertEqual(self.q("SELECT id FROM Customers WHERE score BETWEEN 10 AND 20 ORDER BY id"),
                         [(1,),(2,),(3,)])
        self.assertEqual(self.q("SELECT id FROM Customers WHERE score NOT BETWEEN 10 AND 20 ORDER BY id"),
                         [(5,)])

    def test_07_date_between_date_only_excludes_last_day_timestamp(self):
        self.assertEqual(self.q("""
          SELECT id FROM Orders WHERE created_at BETWEEN '2026-07-01' AND '2026-07-31'
          ORDER BY id
        """), [(11,)])
        self.assertEqual(self.q("""
          SELECT id FROM Orders WHERE created_at>='2026-07-01'
            AND created_at<'2026-08-01' ORDER BY id
        """), [(11,),(12,),(14,)])

    def test_08_correlated_exists_is_semijoin_not_fanout(self):
        self.assertEqual(self.q("""
          SELECT id FROM Customers c WHERE EXISTS
          (SELECT 1 FROM Orders o WHERE o.cust_id=c.id) ORDER BY id
        """), [(1,),(3,)])
        self.assertEqual(self.q("""
          SELECT COUNT(*) FROM Customers c WHERE EXISTS
          (SELECT 1 FROM Orders o WHERE o.price>100)
        """), [(6,)])

    def test_09_union_distinct_versus_union_all(self):
        self.assertEqual(self.q("""
          SELECT value FROM RegionA UNION SELECT value FROM RegionB
          ORDER BY value
        """), [(None,),('DE',),('FR',),('UK',)])
        self.assertEqual(self.q("""
          SELECT COUNT(*) FROM (SELECT value FROM RegionA
          UNION ALL SELECT value FROM RegionB)
        """), [(7,)])
        with self.assertRaises(sqlite3.OperationalError):
            self.q("SELECT value FROM RegionA UNION SELECT value,1 FROM RegionB")

    def test_10_precedence_and_parentheses_not_interchangeable(self):
        self.assertEqual(self.q("""
          SELECT id FROM Customers WHERE city='Berlin' OR city='Paris' AND score>20
          ORDER BY id
        """), [(1,),(2,),(5,)])
        self.assertEqual(self.q("""
          SELECT id FROM Customers WHERE (city='Berlin' OR city='Paris') AND score>20
          ORDER BY id
        """), [(5,)])

    def test_11_empty_input_set_and_exists(self):
        self.db.execute("DELETE FROM RegionB")
        self.assertEqual(self.q("SELECT EXISTS (SELECT 1 FROM RegionB)"), [(0,)])
        self.assertEqual(self.q("SELECT NOT EXISTS (SELECT 1 FROM RegionB)"), [(1,)])
        self.assertEqual(self.q("SELECT COUNT(*) FROM (SELECT value FROM RegionA UNION SELECT value FROM RegionB)"),
                         [(3,)])


if __name__ == "__main__":
    print("AUDITOR-ONLY SQLite:", sqlite3.sqlite_version)
    unittest.main(verbosity=2)
