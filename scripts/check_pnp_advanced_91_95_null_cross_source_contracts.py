#!/usr/bin/env python3
"""Read-only A091-A095 NULL cross-question reviewer checks; NOT provider or learner answers."""
import hashlib
import re
import sqlite3
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/2.PNP- foundations and practice/11. NULL Logic"
)
PINS = {
    "A091": "8b8d8dd763bfe3455a96b2b030874813baa640e7",
    "A092": "01e258132caf62d9de02ea1a8abf364ab99e21a0",
    "A093": "70d5ceadc9fa1c6e105a80624f40656e52cf2bc3",
    "A094": "c3c7571909e4be539c95f83e6e0be50d6c85e8a6",
    "A095": "dc3eb037dbae6341c974185fd9c5baf6df794698",
}

def original(sid):
    matches = list(BASE.glob(sid + ". *.md"))
    if len(matches) != 1:
        raise AssertionError((sid, "missing or duplicate archived source", matches))
    raw = matches[0].read_bytes()
    digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if digest != PINS[sid]:
        raise AssertionError((sid, "original Git blob mismatch", digest))
    return raw.decode("utf-8")

def database(ddl, table, rows):
    db = sqlite3.connect(":memory:")
    db.executescript(ddl)
    if rows:
        q = ",".join("?" * len(rows[0]))
        db.executemany("INSERT INTO " + table + " VALUES (" + q + ")", rows)
    return db

class OriginalNULLCrossSourceReviewer(unittest.TestCase):
    def test_01_five_immutable_source_contracts_and_pending_status(self):
        for sid in PINS:
            with self.subTest(sid=sid):
                body = original(sid)
                self.assertIn("NOT SOLVED YET", body)
                self.assertIn("PDF p. 18", body)
                self.assertIn("### Sample input and expected output (illustrative)", body)
                self.assertIn("## My solution — SQLite\n\nPending.", body)
                self.assertIn("## My solution — SQL Server\n\nPending.", body)
                self.assertIn("## Official solution\n\nPending", body)
        for sid, missing_relation in (("A093", "customer_contacts"), ("A094", "stage"), ("A095", "discount")):
            self.assertIn(missing_relation, original(sid))

    def test_02_a091_execute_exact_archived_query_on_independent_rows(self):
        original_sql = re.search(r"```sql\n(.*?)\n```", original("A091"), re.S).group(1)
        self.assertIn("COUNT(DISTINCT manager_id)", original_sql)
        for rows in (
            [],
            [(1, None), (2, None)],
            [(1, None), (2, 10), (3, 10), (4, 20), (5, 0)],
            [(1, 2), (2, 3), (3, 2)]
        ):
            with self.subTest(rows=rows), database("CREATE TABLE employees(emp_id INT,manager_id INT);", "employees", rows) as db:
                nonnull = [m for _, m in rows if m is not None]
                expected = (len(rows), len(nonnull), len(set(nonnull)))
                got = tuple(db.execute(original_sql).fetchone())
                self.assertEqual(got, expected)

    def test_03_a092_desc_nulls_last_and_stable_tie_boundary(self):
        rows = [(1, None), (2, 50), (3, 50), (4, -5), (5, None), (6, 0)]
        with database("CREATE TABLE employees(emp_id INT,salary INT);", "employees", rows) as db:
            explicit = db.execute(
                "SELECT emp_id FROM employees ORDER BY salary IS NULL,salary DESC,emp_id"
            ).fetchall()
            inherent = db.execute(
                "SELECT emp_id FROM employees ORDER BY salary DESC,emp_id"
            ).fetchall()
            self.assertEqual([v[0] for v in explicit], [2, 3, 6, 4, 1, 5])
            self.assertEqual(explicit, inherent)
        with database("CREATE TABLE employees(emp_id INT,salary INT);", "employees", [(9, None), (7, None)]) as db:
            self.assertEqual(db.execute("SELECT emp_id FROM employees ORDER BY salary DESC,emp_id").fetchall(), [(7,), (9,)])

    def test_04_a093_first_nonnull_is_not_first_usable(self):
        rows = [(1, "", "123", "a@b"), (2, "  ", "456", "b@c"),
                (3, None, "", "c@d"), (4, None, None, None),
                (5, "  789  ", "000", "e@f")]
        ddl = "CREATE TABLE customer_contacts(cust_id INT,work_phone TEXT,mobile TEXT,email TEXT);"
        with database(ddl, "customer_contacts", rows) as db:
            raw = db.execute(
                "SELECT COALESCE(work_phone,mobile,email,'no contact') FROM customer_contacts ORDER BY cust_id"
            ).fetchall()
            cleaned = db.execute(
                "SELECT COALESCE(NULLIF(TRIM(work_phone),''),NULLIF(TRIM(mobile),''),"
                "NULLIF(TRIM(email),''),'no contact') FROM customer_contacts ORDER BY cust_id"
            ).fetchall()
            self.assertEqual([v[0] for v in raw], ["", "  ", "", "no contact", "  789  "])
            self.assertEqual([v[0] for v in cleaned], ["123", "456", "c@d", "no contact", "789"])

    def test_05_a094_null_safe_join_python_oracle_and_bag_fanout(self):
        left = [(1, None), (2, None), (3, "A"), (4, "B"), (5, "B")]
        right = [(10, None), (11, None), (12, None), (13, "B"), (14, "X")]
        db = sqlite3.connect(":memory:")
        try:
            db.executescript("CREATE TABLE stage(id INT,k TEXT); CREATE TABLE target(id INT,k TEXT);")
            db.executemany("INSERT INTO stage VALUES (?,?)", left)
            db.executemany("INSERT INTO target VALUES (?,?)", right)
            sql_eq = "SELECT s.id,t.id FROM stage s JOIN target t ON s.k=t.k ORDER BY s.id,t.id"
            sql_safe = "SELECT s.id,t.id FROM stage s JOIN target t ON s.k IS t.k ORDER BY s.id,t.id"
            sql_or = ("SELECT s.id,t.id FROM stage s JOIN target t ON "
                      "(s.k=t.k OR (s.k IS NULL AND t.k IS NULL)) ORDER BY s.id,t.id")
            oracle = sorted((sid, tid) for sid, sk in left for tid, tk in right
                            if sk == tk)
            ordinary = sorted((sid, tid) for sid, sk in left for tid, tk in right
                              if sk is not None and tk is not None and sk == tk)
            self.assertEqual(db.execute(sql_safe).fetchall(), oracle)
            self.assertEqual(db.execute(sql_or).fetchall(), oracle)
            self.assertEqual(db.execute(sql_eq).fetchall(), ordinary)
            self.assertEqual(len(oracle), 8)  # six NULL pairs plus two B pairs
        finally:
            db.close()

    def test_06_a095_missing_discount_and_all_null_denominators(self):
        query = ("SELECT AVG(discount),SUM(discount)*1.0/NULLIF(COUNT(*),0),"
                 "SUM(discount)*1.0/NULLIF(COUNT(discount),0),"
                 "AVG(COALESCE(discount,0)),COUNT(*) FROM order_items")
        for discounts, expected in (
            ([], (None, None, None, None, 0)),
            ([None, None], (None, None, None, 0.0, 2)),
            ([10, None, 20], (15.0, 10.0, 15.0, 10.0, 3)),
            ([1, None, 2], (1.5, 1.0, 1.5, 1.0, 3)),
        ):
            with self.subTest(discounts=discounts), database(
                "CREATE TABLE order_items(discount INT);",
                "order_items", [(v,) for v in discounts]
            ) as db:
                self.assertEqual(db.execute(query).fetchone(), expected)
        with database("CREATE TABLE order_items(discount INT);", "order_items", [(1,), (2,)]) as db:
            self.assertEqual(db.execute("SELECT SUM(discount)/COUNT(*) FROM order_items").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT AVG(discount) FROM order_items").fetchone()[0], 1.5)

    def test_07_cross_question_join_fanout_changes_count_star_and_avg(self):
        db = sqlite3.connect(":memory:")
        try:
            db.executescript("CREATE TABLE stage(id INT,k TEXT,discount REAL);"
                             "CREATE TABLE target(id INT,k TEXT);")
            db.executemany("INSERT INTO stage VALUES (?,?,?)", [(1, None, 10), (2, None, 20), (3, "A", 100)])
            db.executemany("INSERT INTO target VALUES (?,?)", [(11, None), (12, None), (13, None), (14, "A")])
            source = db.execute("SELECT COUNT(*),AVG(discount) FROM stage").fetchone()
            joined = db.execute("SELECT COUNT(*),COUNT(DISTINCT s.id),AVG(s.discount) "
                                "FROM stage s JOIN target t ON s.k IS t.k").fetchone()
            self.assertEqual(source, (3, 130/3))
            self.assertEqual(joined, (7, 3, 190/7))
            self.assertNotEqual(source[1], joined[2])
        finally:
            db.close()

if __name__ == "__main__":
    unittest.main(verbosity=2)
