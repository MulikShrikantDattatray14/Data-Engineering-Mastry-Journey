#!/usr/bin/env python3
"""Read-only, SHA-pinned cross-source SQL semantics checks (reviewer fixtures only).

W3Schools pages were independently read 2026-11-13; this script does NOT access
or run the external editors or assert any official exercise answers or learner work.
"""
import hashlib
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "99. Reference Materials/W3SCHOOLS-TOPICS.md": "c6328c2eb420f47e5585026a7bf3c0a4e41be720",
    "01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md": "d181dd73f96b1f2b7327600e290d52e9fd59a976",
    "01. SQL Mastery/02. Joins/0. Foundation Notes.md": "61d952c98f02a62c6591caaedf5c02cf0b43e3b1",
    "01. SQL Mastery/03. Sorting and Grouping/0. Foundation Notes.md": "5cf690cb6ca5942795fe332aa447bbf77e14232e",
    "01. SQL Mastery/04. Aggregation/0. Foundation Notes.md": "7dcd722be94284602dd17e316dca9ce096954c33",
    "01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md": "af9cc8d5d47e0279fe0d8b0f9276b700ce496888",
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/2. Joins/0. Foundation Notes.md": "b65b32c17a8c35a3130a3164799c307bc02dbf17",
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/2. Joins/0. Foundation Notes.md": "4130c69922d653b8f2c033e028d91a56d098fe5f",
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/3. Sorting and Grouping/0. Foundation Notes.md": "6beb99ba1b26edccb42d1087ea76e3e0b61a20b1",
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/11. NULL Logic/0. Foundation Notes.md": "7ba0d8943a74ca0ae2d967c2ea982e4df3af917a",
}
PAGES = (
    "sql_select.asp", "sql_null_values.asp", "sql_join.asp",
    "sql_join_inner.asp", "sql_join_left.asp", "sql_groupby.asp",
    "sql_having.asp", "sql_count.asp",
)


class CrossSourceSqlSemantics(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript("""
            CREATE TABLE Customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
            INSERT INTO Customers VALUES (1,'Asha'),(2,'Ravi'),(3,'Tara'),(4,'Uma');
            CREATE TABLE Orders(id INTEGER PRIMARY KEY, customer_id INTEGER,
                                status TEXT, amount INTEGER);
            INSERT INTO Orders VALUES
                (10,1,'paid',100),(11,1,'pending',NULL),(15,1,'pending',500),
                (12,2,'paid',50),(13,2,'paid',20),(14,NULL,'paid',5);
            CREATE TABLE Metrics(id INTEGER, grp TEXT, amount INTEGER);
            INSERT INTO Metrics VALUES
                (1,'A',10),(2,'A',NULL),(3,'A',10),
                (4,'B',20),(5,'B',NULL),(6,NULL,99);
        """)

    def tearDown(self):
        self.db.close()

    def rows(self, statement):
        return self.db.execute(statement).fetchall()

    def test_00_exact_archived_source_pins_and_external_reference_index(self):
        for path, want in PINS.items():
            with self.subTest(path=path):
                data = (ROOT / path).read_bytes()
                actual = hashlib.sha1(
                    b"blob " + str(len(data)).encode() + b"\0" + data
                ).hexdigest()
                self.assertEqual(actual, want)
        reference = (ROOT / "99. Reference Materials/W3SCHOOLS-TOPICS.md").read_text()
        for page in PAGES:
            with self.subTest(page=page):
                self.assertIn("https://www.w3schools.com/sql/" + page, reference)

    def test_01_select_projects_requested_columns_and_order_is_explicit(self):
        self.assertEqual(self.rows(
            "SELECT name FROM Customers WHERE id IN (1,3) ORDER BY id"
        ), [("Asha",), ("Tara",)])

    def test_02_sql_null_uses_is_null_not_equality(self):
        self.assertEqual(self.rows("SELECT id FROM Orders WHERE amount = NULL"), [])
        self.assertEqual(self.rows("SELECT id FROM Orders WHERE amount IS NULL"), [(11,)])
        self.assertEqual(self.rows("SELECT NULL = 0, NULL = NULL"), [(None, None)])

    def test_03_inner_join_excludes_unmatched_and_fans_out(self):
        self.assertEqual(self.rows("""
            SELECT c.id, o.id FROM Customers c
            JOIN Orders o ON c.id = o.customer_id ORDER BY c.id, o.id
        """), [(1,10),(1,11),(1,15),(2,12),(2,13)])

    def test_04_left_join_preserves_unmatched_not_one_row_per_customer(self):
        self.assertEqual(self.rows("""
            SELECT c.id, o.id FROM Customers c
            LEFT JOIN Orders o ON c.id=o.customer_id ORDER BY c.id,o.id
        """), [(1,10),(1,11),(1,15),(2,12),(2,13),(3,None),(4,None)])

    def test_05_left_join_on_predicate_vs_where(self):
        kept = self.rows("""
            SELECT c.id,o.id FROM Customers c LEFT JOIN Orders o
            ON c.id=o.customer_id AND o.status='paid'
            ORDER BY c.id,o.id
        """)
        filtered = self.rows("""
            SELECT c.id,o.id FROM Customers c LEFT JOIN Orders o
            ON c.id=o.customer_id
            WHERE o.status='paid' ORDER BY c.id,o.id
        """)
        self.assertEqual(kept, [(1,10),(2,12),(2,13),(3,None),(4,None)])
        self.assertEqual(filtered, [(1,10),(2,12),(2,13)])

    def test_06_anti_join_requires_non_nullable_right_match_identifier(self):
        correct = self.rows("""
            SELECT c.id FROM Customers c LEFT JOIN Orders o
            ON c.id=o.customer_id WHERE o.id IS NULL ORDER BY c.id
        """)
        wrong = self.rows("""
            SELECT DISTINCT c.id FROM Customers c LEFT JOIN Orders o
            ON c.id=o.customer_id WHERE o.amount IS NULL ORDER BY c.id
        """)
        self.assertEqual(correct, [(3,),(4,)])
        self.assertEqual(wrong, [(1,),(3,),(4,)])

    def test_07_where_before_group_by_and_having_after(self):
        self.assertEqual(self.rows("""
            SELECT customer_id,SUM(amount) FROM Orders
            WHERE status='paid' GROUP BY customer_id
            HAVING SUM(amount) >= 80 ORDER BY customer_id
        """), [(1,100)])
        self.assertEqual(self.rows("""
            SELECT customer_id,SUM(amount) FROM Orders
            WHERE customer_id=1 GROUP BY customer_id
        """), [(1,600)])

    def test_08_count_star_column_distinct_and_null_group(self):
        self.assertEqual(self.rows("""
            SELECT COUNT(*),COUNT(amount),COUNT(DISTINCT amount) FROM Metrics
        """), [(6,4,3)])
        groups = self.rows("""
            SELECT grp,COUNT(*),COUNT(amount) FROM Metrics GROUP BY grp
        """)
        self.assertEqual({key:(all_rows,known) for key,all_rows,known in groups},
                         {"A":(3,2),"B":(2,1),None:(1,1)})

    def test_09_joined_count_star_includes_null_extended_rows(self):
        self.assertEqual(self.rows("""
            SELECT COUNT(*),COUNT(o.id),COUNT(o.amount) FROM Customers c
            LEFT JOIN Orders o ON c.id=o.customer_id
        """), [(7,5,4)])

    def test_10_distinct_row_values_not_grouped_counts(self):
        self.assertEqual(self.rows("SELECT DISTINCT status FROM Orders ORDER BY status"),
                         [("paid",),("pending",)])
        self.assertEqual(self.rows("""
            SELECT status,COUNT(*) FROM Orders GROUP BY status ORDER BY status
        """), [("paid",4),("pending",2)])

    def test_11_grouped_empty_input_differs_from_global_aggregate(self):
        self.db.execute("CREATE TABLE EmptyGroup(grp TEXT, amount INTEGER)")
        self.assertEqual(self.rows("SELECT COUNT(*),SUM(amount) FROM EmptyGroup"),
                         [(0,None)])
        self.assertEqual(self.rows("""
            SELECT grp,COUNT(*) FROM EmptyGroup GROUP BY grp
        """), [])

    def test_12_null_in_not_in_poisoning_is_extra_pnp_caveat(self):
        self.db.executescript("""
            CREATE TABLE FilterValue(v INTEGER);
            INSERT INTO FilterValue VALUES (1),(NULL);
        """)
        self.assertEqual(self.rows("SELECT 5 NOT IN (SELECT v FROM FilterValue)"),
                         [(None,)])
        self.assertEqual(self.rows("""
            SELECT NOT EXISTS (SELECT 1 FROM FilterValue WHERE v=5)
        """), [(1,)])


if __name__ == "__main__":
    print("AUDITOR-ONLY SQLite runtime", sqlite3.sqlite_version)
    unittest.main(verbosity=2)
