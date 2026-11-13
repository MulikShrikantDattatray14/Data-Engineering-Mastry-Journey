#!/usr/bin/env python3
"""Reviewer-only W3Schools SQL source identity and SQLite semantics; NOT official answers."""
import hashlib
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "99. Reference Materials/W3SCHOOLS-TOPICS.md": "c6328c2eb420f47e5585026a7bf3c0a4e41be720",
    "01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md": "d181dd73f96b1f2b7327600e290d52e9fd59a976",
    "01. SQL Mastery/12. Dates and Time/0. Foundation Notes.md": "0061f75fe5977679acdcf11ae8dda92fbd762143",
    "01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md": "d2743783106fe64ca087b39216184a87e97d1a8c",
    "01. SQL Mastery/14. Data Quality and Deduplication/0. Foundation Notes.md": "f19d2b0340649f2e481ac62705d9c28dd87ce761",
    "01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md": "af9cc8d5d47e0279fe0d8b0f9276b700ce496888",
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/0. SQL basics/0. Foundation Notes.md": "073c87bebb2d7c72cca97e970a06de965a87abe5",
}
URLS = {
    "drop": "https://www.w3schools.com/sql/sql_drop_table.asp",
    "alter": "https://www.w3schools.com/sql/sql_alter.asp",
    "index": "https://www.w3schools.com/sql/sql_create_index.asp",
    "identity": "https://www.w3schools.com/sql/sql_autoincrement.asp",
    "dates": "https://www.w3schools.com/sql/sql_dates.asp",
    "view": "https://www.w3schools.com/sql/sql_view.asp",
    "injection": "https://www.w3schools.com/sql/sql_injection.asp",
    "prepared": "https://www.w3schools.com/sql/sql_prepared_statements.asp",
}
def db():
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys=ON")
    return c

class Reviewer(unittest.TestCase):
    def test_01_source_pins_and_selected_index(self):
        for path, sha in PINS.items():
            with self.subTest(path=path):
                data = (ROOT / path).read_bytes()
                self.assertEqual(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest(), sha)
        index = (ROOT / "99. Reference Materials/W3SCHOOLS-TOPICS.md").read_text()
        for topic, url in URLS.items():
            with self.subTest(topic=topic):
                self.assertEqual(url in index, topic in {"index", "view"})

    def test_02_delete_vs_drop(self):
        with db() as c:
            c.executescript("CREATE TABLE t(id INT PRIMARY KEY); INSERT INTO t VALUES(1); DELETE FROM t;")
            self.assertEqual(c.execute("SELECT COUNT(*) FROM t").fetchone(), (0,))
            self.assertEqual(c.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='t'").fetchone(), (1,))
            c.execute("DROP TABLE t")
            self.assertEqual(c.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='t'").fetchone(), (0,))

    def test_03_drop_if_exists(self):
        with db() as c:
            c.execute("DROP TABLE IF EXISTS missing")
            c.execute("DROP TABLE IF EXISTS missing")
            with self.assertRaises(sqlite3.OperationalError):
                c.execute("DROP TABLE missing")

    def test_04_sqlite_has_no_truncate(self):
        with db() as c:
            c.executescript("CREATE TABLE t(id INTEGER PRIMARY KEY); INSERT INTO t VALUES(1),(2);")
            with self.assertRaises(sqlite3.OperationalError):
                c.execute("TRUNCATE TABLE t")
            c.execute("DELETE FROM t")
            self.assertEqual(c.execute("PRAGMA table_info(t)").fetchone()[1], "id")
            self.assertEqual(c.execute("SELECT COUNT(*) FROM t").fetchone(), (0,))

    def test_05_alter_add_preserves_existing_rows(self):
        with db() as c:
            c.executescript("CREATE TABLE t(id INT); INSERT INTO t VALUES(7);")
            c.execute("ALTER TABLE t ADD COLUMN email TEXT")
            self.assertEqual(c.execute("SELECT * FROM t").fetchone(), (7,None))

    def test_06_alter_rename_drop(self):
        with db() as c:
            c.executescript("CREATE TABLE t(id INT, obsolete TEXT); INSERT INTO t VALUES(8,'old');")
            c.execute("ALTER TABLE t RENAME COLUMN id TO customer_id")
            c.execute("ALTER TABLE t DROP COLUMN obsolete")
            self.assertEqual(c.execute("SELECT customer_id FROM t").fetchone(), (8,))
            self.assertEqual([x[1] for x in c.execute("PRAGMA table_info(t)")], ["customer_id"])

    def test_07_nonunique_index_allows_duplicates(self):
        with db() as c:
            c.executescript("CREATE TABLE t(id INT,city TEXT); CREATE INDEX ix_city ON t(city);")
            c.executemany("INSERT INTO t VALUES(?,?)", [(1,"Pune"),(2,"Pune")])
            self.assertEqual(c.execute("SELECT COUNT(*) FROM t WHERE city='Pune'").fetchone(), (2,))
            self.assertIn("ix_city", [x[1] for x in c.execute("PRAGMA index_list(t)")])

    def test_08_unique_index_sqlite_null_counterexample(self):
        with db() as c:
            c.executescript("CREATE TABLE t(code TEXT); CREATE UNIQUE INDEX ux ON t(code);")
            c.execute("INSERT INTO t VALUES('a')")
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute("INSERT INTO t VALUES('a')")
            c.execute("INSERT INTO t VALUES(NULL)")
            c.execute("INSERT INTO t VALUES(NULL)")
            self.assertEqual(c.execute("SELECT COUNT(*) FROM t").fetchone(), (3,))

    def test_09_sqlite_rowid_reuse_vs_autoincrement(self):
        with db() as c:
            c.executescript("CREATE TABLE a(id INTEGER PRIMARY KEY); CREATE TABLE b(id INTEGER PRIMARY KEY AUTOINCREMENT);")
            for name in ("a","b"):
                c.execute(f"INSERT INTO {name} DEFAULT VALUES")
                c.execute(f"DELETE FROM {name} WHERE id=1")
                c.execute(f"INSERT INTO {name} DEFAULT VALUES")
            self.assertEqual(c.execute("SELECT id FROM a").fetchone(), (1,))
            self.assertEqual(c.execute("SELECT id FROM b").fetchone(), (2,))

    def test_10_half_open_date_boundary(self):
        with db() as c:
            c.execute("CREATE TABLE t(id INT, occurred TEXT)")
            c.executemany("INSERT INTO t VALUES(?,?)", [(1,"2025-01-31 23:59:59"),(2,"2025-02-01 00:00:00"),(3,"2025-01-01 00:00:00")])
            self.assertEqual(c.execute("SELECT id FROM t WHERE occurred >= '2025-01-01' AND occurred < '2025-02-01' ORDER BY id").fetchall(),[(1,),(3,)])
            self.assertEqual(c.execute("SELECT id FROM t WHERE occurred='2025-01-31'").fetchall(),[])

    def test_11_view_tracks_base_changes(self):
        with db() as c:
            c.executescript("CREATE TABLE products(id INT,price INT); INSERT INTO products VALUES(1,10),(2,50); CREATE VIEW expensive AS SELECT id FROM products WHERE price>30;")
            self.assertEqual(c.execute("SELECT * FROM expensive").fetchall(),[(2,)])
            c.execute("UPDATE products SET price=60 WHERE id=1")
            self.assertEqual(c.execute("SELECT id FROM expensive ORDER BY id").fetchall(),[(1,),(2,)])

    def test_12_drop_view_keeps_table(self):
        with db() as c:
            c.executescript("CREATE TABLE base(id INT); CREATE VIEW v AS SELECT id FROM base; DROP VIEW v;")
            self.assertEqual(c.execute("SELECT type FROM sqlite_master WHERE name='base'").fetchone(),("table",))
            self.assertIsNone(c.execute("SELECT type FROM sqlite_master WHERE name='v'").fetchone())

    def test_13_bound_values_block_or_tautology(self):
        with db() as c:
            c.executescript("CREATE TABLE users(id INT); INSERT INTO users VALUES(105),(106);")
            value = "105 OR 1=1"
            self.assertEqual(c.execute("SELECT id FROM users WHERE id="+value).fetchall(),[(105,),(106,)])
            self.assertEqual(c.execute("SELECT id FROM users WHERE id=?", (value,)).fetchall(),[])

    def test_14_bind_parameters_are_not_identifiers(self):
        with db() as c:
            c.executescript("CREATE TABLE events(id INT); INSERT INTO events VALUES(1);")
            with self.assertRaises(sqlite3.OperationalError):
                c.execute("SELECT COUNT(*) FROM ?",("events",))
            self.assertEqual(c.execute("SELECT ? FROM events",("id",)).fetchone(),("id",))
            self.assertEqual(c.execute("SELECT id FROM events WHERE id=?",(1,)).fetchone(),(1,))

if __name__ == "__main__":
    unittest.main(verbosity=2)
