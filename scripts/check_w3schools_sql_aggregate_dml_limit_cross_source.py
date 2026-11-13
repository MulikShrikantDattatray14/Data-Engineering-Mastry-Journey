#!/usr/bin/env python3
"""Read-only, source-pinned reviewer audit of eight live W3Schools SQL lessons.

Inspected 2026-11-13: MIN, SUM, AVG, aliases, INSERT, UPDATE, DELETE,
and TOP/LIMIT/FETCH. Only independently authored SQLite fixtures run here;
no W3Schools editor exercise, official key, provider data or learner submission.
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
    "01. SQL Mastery/03. Sorting and Grouping/0. Foundation Notes.md": "5cf690cb6ca5942795fe332aa447bbf77e14232e",
    "01. SQL Mastery/04. Aggregation/0. Foundation Notes.md": "7dcd722be94284602dd17e316dca9ce096954c33",
    "01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md": "d2743783106fe64ca087b39216184a87e97d1a8c",
    "01. SQL Mastery/BOSSCODER-AGGREGATION-INDEPENDENT-AUDIT.md": "e3f283154e533254f22372d18d2886c8d8c2aeb9",
}

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

class ReviewerOnlySqlLessons(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")

    def tearDown(self):
        self.db.close()

    def rows(self, sql):
        return self.db.execute(sql).fetchall()

    def test_00_pinned_local_sources_unchanged(self):
        for path, expected in PINS.items():
            with self.subTest(source=path):
                self.assertEqual(blob_sha((ROOT / path).read_bytes()), expected)

    def test_01_min_ignores_null_and_collates_text(self):
        self.db.executescript("""
            CREATE TABLE t(n REAL, word TEXT);
            INSERT INTO t VALUES (NULL,'z'), (12,'b'), (-2,'a'), (7,NULL);
        """)
        self.assertEqual(self.rows("SELECT MIN(n), MIN(word), MAX(n) FROM t"), [(-2.0,'a',12.0)])
        self.assertEqual(self.rows("SELECT MIN(n) FROM t WHERE n>100"), [(None,)])

    def test_02_sum_avg_skip_null_and_return_null_for_no_values(self):
        self.db.executescript("""
            CREATE TABLE t(v REAL);
            INSERT INTO t VALUES (10),(NULL),(30),(0);
        """)
        self.assertEqual(self.rows("SELECT SUM(v), AVG(v), COUNT(v), COUNT(*) FROM t"),
                         [(40.0, 40.0/3, 3, 4)])
        self.assertEqual(self.rows("SELECT SUM(v), AVG(v), COUNT(v), COUNT(*) FROM t WHERE v>100"),
                         [(None,None,0,0)])
        self.assertEqual(self.rows("SELECT AVG(v) FROM t WHERE v IS NULL"), [(None,)])

    def test_03_sum_expression_null_and_zero_policy(self):
        self.db.executescript("""
            CREATE TABLE lines(qty INTEGER, price REAL);
            INSERT INTO lines VALUES (2,10),(3,NULL),(NULL,8),(0,12);
        """)
        self.assertEqual(self.rows("SELECT SUM(qty*price), SUM(COALESCE(qty*price,0)) FROM lines"),
                         [(20.0,20.0)])
        self.assertEqual(self.rows("SELECT COUNT(*), COUNT(qty*price) FROM lines"), [(4,2)])

    def test_04_grouped_sum_min_max_avg_have_group_grain(self):
        self.db.executescript("""
            CREATE TABLE sale(category TEXT, amount REAL);
            INSERT INTO sale VALUES ('A',10),('A',20),('A',NULL),('B',50),('B',NULL);
        """)
        self.assertEqual(self.rows("""
            SELECT category,MIN(amount),SUM(amount),AVG(amount),COUNT(*),COUNT(amount)
            FROM sale GROUP BY category ORDER BY category
        """), [('A',10.0,30.0,15.0,3,2),('B',50.0,50.0,50.0,2,1)])

    def test_05_aliases_change_output_labels_not_base_schema(self):
        self.db.execute("CREATE TABLE customers(customer_id INTEGER, name TEXT)")
        self.db.execute("INSERT INTO customers VALUES (1,'Anu')")
        cur = self.db.execute('SELECT customer_id AS id, name AS "Customer name" FROM customers AS c')
        self.assertEqual([d[0] for d in cur.description], ['id','Customer name'])
        self.assertEqual(cur.fetchall(),[(1,'Anu')])
        self.assertEqual([r[1] for r in self.db.execute("PRAGMA table_info(customers)")],
                         ['customer_id','name'])

    def test_06_insert_explicit_columns_default_null_and_generated_key(self):
        self.db.executescript("""
            CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT NOT NULL,
                                   city TEXT DEFAULT 'unknown', nickname TEXT);
            INSERT INTO customers(name) VALUES ('A');
            INSERT INTO customers(name,city) VALUES ('B','Pune'),('C','Mumbai');
        """)
        self.assertEqual(self.rows("SELECT id,name,city,nickname FROM customers ORDER BY id"),
                         [(1,'A','unknown',None),(2,'B','Pune',None),(3,'C','Mumbai',None)])
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO customers(city) VALUES ('Delhi')")
        self.assertEqual(self.rows("SELECT COUNT(*) FROM customers"), [(3,)])

    def test_07_insert_without_column_names_depends_on_position(self):
        self.db.executescript("""
            CREATE TABLE t(id INTEGER, name TEXT);
            INSERT INTO t VALUES (10,'A');
            INSERT INTO t(name,id) VALUES ('B',20);
        """)
        self.assertEqual(self.rows("SELECT id,name FROM t ORDER BY id"),[(10,'A'),(20,'B')])
        with self.assertRaises(sqlite3.OperationalError):
            self.db.execute("INSERT INTO t VALUES ('missing id')")
        self.assertEqual(self.rows("SELECT COUNT(*) FROM t"),[(2,)])

    def test_08_update_with_where_changes_only_selected_rows(self):
        self.db.executescript("""
            CREATE TABLE stock(id INT PRIMARY KEY, qty INT);
            INSERT INTO stock VALUES (1,1),(2,2),(3,3);
            UPDATE stock SET qty=qty+10 WHERE id IN (1,3);
        """)
        self.assertEqual(self.rows("SELECT id,qty FROM stock ORDER BY id"),[(1,11),(2,2),(3,13)])
        self.db.execute("UPDATE stock SET qty=0")
        self.assertEqual(self.rows("SELECT qty FROM stock ORDER BY id"),[(0,),(0,),(0,)])

    def test_09_delete_where_scope_and_unqualified_delete(self):
        self.db.executescript("""
            CREATE TABLE items(id INT, status TEXT);
            INSERT INTO items VALUES (1,'keep'),(2,'remove'),(3,'keep');
            DELETE FROM items WHERE status='remove';
        """)
        self.assertEqual(self.rows("SELECT id FROM items ORDER BY id"),[(1,),(3,)])
        self.db.execute("DELETE FROM items")
        self.assertEqual(self.rows("SELECT COUNT(*) FROM items"),[(0,)])
        self.assertEqual(self.rows("SELECT name FROM sqlite_master WHERE name='items'"),[('items',)])

    def test_10_rollback_protects_bulk_update_and_delete(self):
        self.db.execute("CREATE TABLE t(id INT, val INT)")
        self.db.commit()
        self.db.execute("INSERT INTO t VALUES (1,10),(2,20)")
        self.db.commit()
        self.db.execute("UPDATE t SET val=0")
        self.db.execute("DELETE FROM t")
        self.assertEqual(self.rows("SELECT COUNT(*) FROM t"),[(0,)])
        self.db.rollback()
        self.assertEqual(self.rows("SELECT id,val FROM t ORDER BY id"),[(1,10),(2,20)])

    def test_11_limit_requires_explicit_total_order_on_ties(self):
        self.db.executescript("""
            CREATE TABLE products(id INT PRIMARY KEY, price INT);
            INSERT INTO products VALUES (7,90),(4,90),(2,100),(8,90),(9,NULL);
        """)
        self.assertEqual(self.rows("""
            SELECT id FROM products WHERE price IS NOT NULL
            ORDER BY price DESC,id ASC LIMIT 3
        """),[(2,),(4,),(7,)])
        with self.assertRaises(sqlite3.OperationalError):
            self.db.execute("SELECT TOP 2 id FROM products").fetchall()
        # SQL Server TOP is not SQLite; this is a deliberate dialect limitation.

    def test_12_join_fanout_can_corrupt_order_amount_sum(self):
        self.db.executescript("""
            CREATE TABLE orders(id INT, total INT);
            CREATE TABLE order_lines(order_id INT, line_id INT);
            INSERT INTO orders VALUES (1,500),(2,100);
            INSERT INTO order_lines VALUES (1,1),(1,2),(1,3),(2,4);
        """)
        self.assertEqual(self.rows("SELECT SUM(total) FROM orders"),[(600,)])
        self.assertEqual(self.rows("""
            SELECT SUM(o.total) FROM orders o
            JOIN order_lines l ON l.order_id=o.id
        """),[(1600,)])
        self.assertEqual(self.rows("""
            SELECT SUM(o.total) FROM orders o
            WHERE EXISTS(SELECT 1 FROM order_lines l WHERE l.order_id=o.id)
        """),[(600,)])

    def test_13_avg_subquery_ignores_null_and_selects_above_mean(self):
        self.db.executescript("""
            CREATE TABLE products(id INT, price REAL);
            INSERT INTO products VALUES (1,10),(2,30),(3,NULL),(4,20);
        """)
        self.assertEqual(self.rows("""
            SELECT id FROM products
            WHERE price > (SELECT AVG(price) FROM products)
            ORDER BY id
        """),[(2,)])
        self.assertEqual(self.rows("SELECT AVG(price) FROM products"),[(20.0,)])

if __name__ == "__main__":
    unittest.main(verbosity=2)
