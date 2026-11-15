#!/usr/bin/env python3
"""PARTIAL native MySQL 8 auditor-created tests for archived PNP A091-A095.

Read-only with respect to sources, learner history and canonical content.
Creates/drops only disposable tables in the Actions MySQL 'audit' database.
Synthetic fixtures are NOT provider answers, graded submissions or mastery.
"""
import hashlib
import itertools
import os
import re
import unittest
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
               "1. SQL Mastry/2.PNP- foundations and practice/11. NULL Logic")
PINS = {
    "A091": "8b8d8dd763bfe3455a96b2b030874813baa640e7",
    "A092": "01e258132caf62d9de02ea1a8abf364ab99e21a0",
    "A093": "70d5ceadc9fa1c6e105a80624f40656e52cf2bc3",
    "A094": "c3c7571909e4be539c95f83e6e0be50d6c85e8a6",
    "A095": "dc3eb037dbae6341c974185fd9c5baf6df794698",
}


def original(sid):
    paths = list(BASE.glob(sid + ". *.md"))
    if len(paths) != 1:
        raise AssertionError((sid, "source is missing or duplicated", paths))
    raw = paths[0].read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if sha != PINS[sid]:
        raise AssertionError((sid, "original source has changed", sha))
    return raw.decode("utf-8")


class NativeNULLSemantics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("MYSQL_DATABASE") != "audit" or os.environ.get("MYSQL_USER") != "audit":
            raise RuntimeError("Refuse to run outside disposable Actions audit database/user")
        cls.db = pymysql.connect(
            host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            database="audit", user="audit", password=os.environ["MYSQL_PASSWORD"],
            charset="utf8mb4", autocommit=True,
        )
        with cls.db.cursor() as c:
            c.execute("SELECT VERSION()")
            version = c.fetchone()[0]
        if not version.startswith("8.0."):
            raise RuntimeError("Expected native MySQL 8.0, received " + version)
        print("Native MySQL " + version + " using disposable audit schema", flush=True)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def execute(self, sql, args=None):
        with self.db.cursor() as c:
            c.execute(sql, args)
            if c.description:
                return c.fetchall()
            return c.rowcount

    def insert(self, table, rows):
        if not rows:
            return
        placeholders = ",".join(["%s"] * len(rows[0]))
        with self.db.cursor() as c:
            c.executemany("INSERT INTO " + table + " VALUES (" + placeholders + ")", rows)

    def setUp(self):
        for table in ("employees", "customer_contacts", "stage", "target", "order_items"):
            self.execute("DROP TABLE IF EXISTS " + table)
        self.execute("CREATE TABLE employees(emp_id INT PRIMARY KEY, manager_id INT NULL, salary DECIMAL(10,2) NULL) ENGINE=InnoDB")
        self.execute("CREATE TABLE customer_contacts(cust_id INT PRIMARY KEY, work_phone VARCHAR(80) NULL, mobile VARCHAR(80) NULL, email VARCHAR(80) NULL) ENGINE=InnoDB")
        self.execute("CREATE TABLE stage(id INT PRIMARY KEY, batch_code VARCHAR(20) NULL) ENGINE=InnoDB")
        self.execute("CREATE TABLE target(id INT PRIMARY KEY, batch_code VARCHAR(20) NULL) ENGINE=InnoDB")
        self.execute("CREATE TABLE order_items(item_id INT PRIMARY KEY, discount DECIMAL(10,2) NULL) ENGINE=InnoDB")

    def tearDown(self):
        for table in ("employees", "customer_contacts", "stage", "target", "order_items"):
            self.execute("DROP TABLE IF EXISTS " + table)

    def test_01_original_five_blobs_and_historical_pending(self):
        for sid in PINS:
            with self.subTest(question=sid):
                body = original(sid)
                self.assertIn("NOT SOLVED YET", body)
                self.assertIn("PDF p. 18", body)
                self.assertIn("### Sample input and expected output (illustrative)", body)
                self.assertIn("## My solution — SQLite\n\nPending.", body)
                self.assertIn("## My solution — SQL Server\n\nPending.", body)
                self.assertIn("## Official solution\n\nPending", body)

    def test_02_a091_exact_archived_sql_native_mysql(self):
        match = re.search(r"```sql\n(.*?)\n```", original("A091"), re.S)
        self.assertIsNotNone(match)
        sql = match.group(1)
        self.assertIn("COUNT(DISTINCT manager_id)", sql)
        for managers in ([], [None,None], [None,1,1,2], [0,0,-1,2,2]):
            with self.subTest(managers=managers):
                self.execute("DELETE FROM employees")
                self.insert("employees", [(i+1,m,None) for i,m in enumerate(managers)])
                nonnull = [m for m in managers if m is not None]
                self.assertEqual(self.execute(sql)[0],
                                 (len(managers),len(nonnull),len(set(nonnull))))

    def test_03_a091_source_illustration_three_counts(self):
        self.insert("employees", [(1,None,None),(2,1,None),(3,1,None),(4,2,None)])
        self.assertEqual(self.execute("""SELECT COUNT(*),COUNT(manager_id),
                                          COUNT(DISTINCT manager_id)
                                        FROM employees""")[0], (4,3,2))

    def test_04_a092_source_illustration_native_null_last(self):
        self.insert("employees", [(1,None,None),(2,None,100),(3,None,50)])
        result = self.execute("SELECT emp_id FROM employees ORDER BY salary DESC, emp_id")
        self.assertEqual([r[0] for r in result], [2,3,1])

    def test_05_a092_explicit_null_sort_and_equal_salary_ties(self):
        self.insert("employees", [(1,None,None),(2,None,50),(3,None,50),
                                   (4,None,-5),(5,None,None),(6,None,0)])
        implicit = self.execute("SELECT emp_id FROM employees ORDER BY salary DESC,emp_id")
        explicit = self.execute("SELECT emp_id FROM employees ORDER BY salary IS NULL,salary DESC,emp_id")
        ascending = self.execute("SELECT emp_id FROM employees ORDER BY salary ASC,emp_id")
        self.assertEqual(implicit, explicit)
        self.assertEqual([r[0] for r in implicit], [2,3,6,4,1,5])
        self.assertEqual([r[0] for r in ascending][:2], [1,5])

    def test_06_a093_archived_contact_preference_and_fallback(self):
        self.insert("customer_contacts", [
            (1,"555-0101","555-0201","ana@example.com"),
            (2,None,"555-0202","ben@example.com"),
            (3,None,None,"cy@example.com"), (4,None,None,None)])
        got = self.execute("""SELECT cust_id,COALESCE(work_phone,mobile,email,'no contact')
                              FROM customer_contacts ORDER BY cust_id""")
        self.assertEqual(got, ((1,"555-0101"),(2,"555-0202"),
                               (3,"cy@example.com"),(4,"no contact")))

    def test_07_a093_empty_and_whitespace_not_null_native(self):
        self.insert("customer_contacts", [(1,"","555","x@a"),(2,"   ","666","x@b"),
                                            (3,None,"",None)])
        raw = self.execute("""SELECT cust_id,COALESCE(work_phone,mobile,email,'no contact')
                              FROM customer_contacts ORDER BY cust_id""")
        usable = self.execute("""SELECT cust_id,COALESCE(NULLIF(TRIM(work_phone),''),
                              NULLIF(TRIM(mobile),''),NULLIF(TRIM(email),''),'no contact')
                              FROM customer_contacts ORDER BY cust_id""")
        self.assertEqual(raw, ((1,""),(2,"   "),(3,"")))
        self.assertEqual(usable, ((1,"555"),(2,"666"),(3,"no contact")))

    def test_08_a094_archived_null_safe_join_illustration(self):
        self.insert("stage", [(1,None),(2,"A")])
        self.insert("target", [(10,None),(20,"A")])
        got = self.execute("""SELECT s.id,t.id FROM stage s JOIN target t
                              ON s.batch_code <=> t.batch_code ORDER BY s.id,t.id""")
        self.assertEqual(got, ((1,10),(2,20)))

    def test_09_a094_native_null_safe_vs_ordinary_equality(self):
        self.insert("stage", [(1,None),(2,"A"),(3,None)])
        self.insert("target", [(10,None),(20,"A"),(30,None)])
        safe = self.execute("""SELECT s.id,t.id FROM stage s JOIN target t
                               ON s.batch_code <=> t.batch_code ORDER BY s.id,t.id""")
        ordinary = self.execute("""SELECT s.id,t.id FROM stage s JOIN target t
                                   ON s.batch_code = t.batch_code ORDER BY s.id,t.id""")
        self.assertEqual(len(safe), 5)
        self.assertEqual(ordinary, ((2,20),))

    def test_10_a094_undefined_one_to_one_join_cardinality(self):
        self.insert("stage", [(1,None),(2,None),(3,"B"),(4,"B")])
        self.insert("target", [(10,None),(20,None),(30,None),(40,"B")])
        got = self.execute("""SELECT COUNT(*) FROM stage s JOIN target t
                              ON s.batch_code <=> t.batch_code""")[0][0]
        self.assertEqual(got, 8)  # 2 x 3 NULL matches, 2 x 1 B matches

    def test_11_a095_original_illustration_decimal_averages(self):
        self.insert("order_items", [(1,10),(2,None),(3,20)])
        got = self.execute("""SELECT AVG(discount),SUM(discount)/COUNT(*),
                              SUM(discount)/NULLIF(COUNT(discount),0)
                              FROM order_items""")[0]
        self.assertEqual(tuple(float(x) for x in got), (15.,10.,15.))

    def test_12_a095_empty_and_all_null_no_divide_by_zero(self):
        sql = """SELECT COUNT(*),COUNT(discount),AVG(discount),
                 SUM(discount)/NULLIF(COUNT(discount),0) FROM order_items"""
        self.assertEqual(self.execute(sql)[0], (0,0,None,None))
        self.insert("order_items", [(1,None),(2,None)])
        self.assertEqual(self.execute(sql)[0], (2,0,None,None))

    def test_13_a095_fractional_and_missing_as_zero_policies(self):
        self.insert("order_items", [(1,1),(2,None),(3,2)])
        got = self.execute("""SELECT AVG(discount),SUM(discount)/COUNT(*),
                              AVG(COALESCE(discount,0)) FROM order_items""")[0]
        self.assertEqual(tuple(float(x) for x in got), (1.5,1.0,1.0))

    def test_14_a091_243_synthetic_manager_oracles(self):
        for values in itertools.product((None,1,2),repeat=5):
            self.execute("DELETE FROM employees")
            self.insert("employees", [(i+1,v,None) for i,v in enumerate(values)])
            actual = self.execute("""SELECT COUNT(*),COUNT(manager_id),
                             COUNT(DISTINCT manager_id) FROM employees""")[0]
            clean = [v for v in values if v is not None]
            self.assertEqual(actual,(5,len(clean),len(set(clean))))

    def test_15_a093_64_distinct_synthetic_contact_oracles(self):
        kinds = (None,""," A ","B")
        for i,values in enumerate(itertools.product(kinds,repeat=3)):
            self.execute("DELETE FROM customer_contacts")
            self.insert("customer_contacts", [(1,*values)])
            result = self.execute("""SELECT COALESCE(work_phone,mobile,email,'no contact')
                                     FROM customer_contacts""")[0][0]
            expected = next((x for x in values if x is not None),"no contact")
            self.assertEqual(result,expected,(i,values))

    def test_16_a094_256_synthetic_bag_join_oracles(self):
        kinds = (None,"A","B","")
        for keys in itertools.product(kinds,repeat=4):
            self.execute("DELETE FROM stage")
            self.execute("DELETE FROM target")
            self.insert("stage", [(1,keys[0]),(2,keys[1])])
            self.insert("target", [(10,keys[2]),(20,keys[3])])
            actual = self.execute("""SELECT s.id,t.id FROM stage s JOIN target t
                    ON s.batch_code <=> t.batch_code ORDER BY s.id,t.id""")
            expected = tuple((i+1,j+10) for i in range(2) for j in (0,10)
                             if keys[i] == keys[2 + j//10])
            self.assertEqual(actual, expected, keys)


if __name__ == "__main__":
    unittest.main(verbosity=2)
