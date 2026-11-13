#!/usr/bin/env python3
"""Eight live W3Schools SQL pages: source-pinned, reviewer-only SQLite comparison.

No hosted W3 editor/datasets, native MySQL/SQL Server/Access grading, official
answers, historical learner attempts, or mastery are checked or credited.
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
    "01. SQL Mastery/01. Advanced SELECT/0. Foundation Notes.md": "1ed1077d492a3bd9db25018650b5c1f3cae1371f",
    "01. SQL Mastery/04. Aggregation/0. Foundation Notes.md": "7dcd722be94284602dd17e316dca9ce096954c33",
    "01. SQL Mastery/05. CTEs/0. Foundation Notes.md": "2716dfc5913b21468e1ffe19d05fc4876cc99d0d",
    "01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md": "af9cc8d5d47e0279fe0d8b0f9276b700ce496888",
    "01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md": "d2743783106fe64ca087b39216184a87e97d1a8c",
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/0. SQL basics/0. Foundation Notes.md": "073c87bebb2d7c72cca97e970a06de965a87abe5",
}
OFFICIAL_PAGES = (
    "sql_intro.asp", "sql_syntax.asp", "sql_max.asp", "sql_union_all.asp",
    "sql_any_all.asp", "sql_all.asp", "sql_drop_db.asp", "sql_datatypes.asp",
)

def blob_sha(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()

class ReviewerSqlBoundaries(unittest.TestCase):
    def test_01_source_preservation_and_selected_topic_links(self):
        for path, sha in PINS.items():
            with self.subTest(source=path):
                data = (ROOT / path).read_bytes()
                self.assertEqual(blob_sha(data), sha, "source content changed")
        selected = (ROOT / "99. Reference Materials/W3SCHOOLS-TOPICS.md").read_text()
        for slug in OFFICIAL_PAGES:
            with self.subTest(selected_link=slug):
                self.assertNotIn("https://www.w3schools.com/sql/" + slug, selected)

    def test_02_intro_read_only_select(self):
        with sqlite3.connect(":memory:") as db:
            db.executescript("CREATE TABLE customers(id INTEGER, city TEXT); INSERT INTO customers VALUES(1,'Pune'),(2,'Mumbai');")
            self.assertEqual(db.execute("SELECT id FROM customers WHERE city='Pune'").fetchall(), [(1,)])
            self.assertEqual(db.execute("SELECT COUNT(*) FROM customers").fetchone()[0], 2)

    def test_03_syntax_multi_statement_semicolons(self):
        with sqlite3.connect(":memory:") as db:
            db.executescript("CREATE TABLE t(id INTEGER); INSERT INTO t VALUES(2); INSERT INTO t VALUES(1);")
            self.assertEqual(db.execute("SELECT id FROM t ORDER BY id;").fetchall(), [(1,), (2,)])

    def test_04_max_ignores_null_and_numeric(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE t(v INTEGER)")
            db.executemany("INSERT INTO t VALUES(?)", [(5,), (None,), (9,), (-1,)])
            self.assertEqual(db.execute("SELECT MAX(v) FROM t").fetchone(), (9,))

    def test_05_max_empty_and_string_collation(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE t(v TEXT)")
            self.assertEqual(db.execute("SELECT MAX(v) FROM t").fetchone(), (None,))
            db.executemany("INSERT INTO t VALUES(?)", [("A",), ("Z",), (None,), ("b",)])
            self.assertEqual(db.execute("SELECT MAX(v) FROM t").fetchone(), ("b",))

    def test_06_union_all_retains_multiplicity_and_null(self):
        with sqlite3.connect(":memory:") as db:
            db.executescript("CREATE TABLE a(v TEXT); CREATE TABLE b(v TEXT);")
            db.executemany("INSERT INTO a VALUES(?)", [("UK",), ("UK",), (None,)])
            db.executemany("INSERT INTO b VALUES(?)", [("UK",), (None,)])
            all_rows = db.execute("SELECT v FROM a UNION ALL SELECT v FROM b").fetchall()
            distinct_rows = db.execute("SELECT v FROM a UNION SELECT v FROM b").fetchall()
            self.assertEqual(len(all_rows), 5)
            self.assertEqual(all_rows.count(("UK",)), 3)
            self.assertEqual(all_rows.count((None,)), 2)
            self.assertEqual(len(distinct_rows), 2)

    def test_07_union_all_column_arity(self):
        with sqlite3.connect(":memory:") as db:
            with self.assertRaises(sqlite3.OperationalError):
                db.execute("SELECT 1,2 UNION ALL SELECT 3").fetchall()

    def test_08_any_equality_filter_as_exists(self):
        # SQLite does not implement comparison quantified ANY; this tests a
        # reviewer EXISTS rewrite under WHERE-filter semantics, not native ANY.
        with sqlite3.connect(":memory:") as db:
            db.executescript("CREATE TABLE products(id INTEGER); CREATE TABLE items(product_id INTEGER, quantity INTEGER);")
            db.executemany("INSERT INTO products VALUES(?)", [(1,), (2,), (3,)])
            db.executemany("INSERT INTO items VALUES(?,?)", [(2,10), (2,10), (1,2), (None,10)])
            actual = db.execute("""SELECT p.id FROM products p WHERE EXISTS
                (SELECT 1 FROM items i WHERE i.product_id=p.id AND i.quantity=10)
                ORDER BY p.id""").fetchall()
            self.assertEqual(actual, [(2,)])

    def test_09_any_null_only_and_empty_are_not_true(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE vals(v INTEGER)")
            self.assertEqual(db.execute("SELECT EXISTS(SELECT 1 FROM vals WHERE v=5)").fetchone(), (0,))
            db.execute("INSERT INTO vals VALUES(NULL)")
            self.assertEqual(db.execute("SELECT EXISTS(SELECT 1 FROM vals WHERE v=5)").fetchone(), (0,))
            db.execute("INSERT INTO vals VALUES(5)")
            self.assertEqual(db.execute("SELECT EXISTS(SELECT 1 FROM vals WHERE v=5)").fetchone(), (1,))

    def test_10_all_empty_is_vacuously_true_in_where_filter(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE vals(v INTEGER)")
            self.assertEqual(db.execute(
                "SELECT NOT EXISTS(SELECT 1 FROM vals WHERE v>=5 OR v IS NULL)").fetchone(), (1,))
            self.assertEqual(db.execute("SELECT EXISTS(SELECT 1 FROM vals WHERE v<5)").fetchone(), (0,))

    def test_11_all_with_null_is_not_true(self):
        # NOT EXISTS(v>=5 OR v IS NULL) captures WHERE-level TRUE for 5>ALL(v)
        # but is not an exact scalar 3-valued-logic rewrite of native ALL.
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE vals(v INTEGER)")
            db.executemany("INSERT INTO vals VALUES(?)", [(1,), (3,)])
            check = "SELECT NOT EXISTS(SELECT 1 FROM vals WHERE v>=5 OR v IS NULL)"
            self.assertEqual(db.execute(check).fetchone(), (1,))
            db.execute("INSERT INTO vals VALUES(NULL)")
            self.assertEqual(db.execute(check).fetchone(), (0,))
            db.execute("DELETE FROM vals WHERE v IS NULL")
            db.execute("INSERT INTO vals VALUES(6)")
            self.assertEqual(db.execute(check).fetchone(), (0,))

    def test_12_sqlite_varchar_length_is_not_mysql_limit(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE t(v VARCHAR(3))")
            db.execute("INSERT INTO t VALUES('long')")
            self.assertEqual(db.execute("SELECT v FROM t").fetchone(), ("long",))

    def test_13_sqlite_explicit_length_check_enforces_limit(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE t(v TEXT CHECK(length(v)<=3))")
            db.execute("INSERT INTO t VALUES('abc')")
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO t VALUES('abcd')")

    def test_14_drop_database_is_unsupported_and_no_destructive_run(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE keep_me(v INTEGER)")
            with self.assertRaises(sqlite3.OperationalError):
                db.execute("DROP DATABASE testDB")
            self.assertEqual(db.execute("SELECT COUNT(*) FROM keep_me").fetchone(), (0,))

if __name__ == "__main__":
    unittest.main(verbosity=2)
