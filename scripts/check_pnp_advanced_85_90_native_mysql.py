#!/usr/bin/env python3
"""Independent PARTIAL native MySQL 8 A085-A090 reviewer.

Runs only in disposable GitHub Actions MySQL audit database.
This is NOT a supplier answer, learner attempt, or production deletion.
"""
import collections
import hashlib
import itertools
import os
import re
import unittest
from pathlib import Path

import pymysql

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
               "1. SQL Mastry/2.PNP- foundations and practice/14. Data Quality and Deduplication")
PINS = {
    "A085": "3d7d0259231887892bd70f70cd017333ccda7001",
    "A086": "bb228c4f897bd6b93d25de198cd3f9bd3fc033eb",
    "A087": "d701707e2810e2d9065f2bb362e35f8310a5d8ba",
    "A088": "4426613948ef36cf4d5d7bf67e5e4eca3cc0ea4e",
    "A089": "b93db48be869c37c1b28b47b70d755ca87bd4666",
    "A090": "c8f9f650232f532b202677d8cfd75f0eda4d041f",
}
DELETE_DUPLICATES = """DELETE p FROM payments AS p
 JOIN payments AS keep_row
   ON p.order_id <=> keep_row.order_id
  AND p.paid_at <=> keep_row.paid_at
  AND p.payment_id > keep_row.payment_id"""
DUPLICATE_COUNTS = """SELECT COUNT(*), COALESCE(SUM(n-1),0) FROM (
 SELECT order_id, paid_at, COUNT(*) AS n FROM payments
 GROUP BY order_id,paid_at HAVING COUNT(*)>1
) AS duplicate_groups"""
ORIGINAL_COLUMNS = ("payment_id", "order_id", "paid_at", "amount")

def original(sid):
    paths = list(BASE.glob(sid + ". *.md"))
    assert len(paths) == 1, (sid, paths)
    raw = paths[0].read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert sha == PINS[sid], (sid, sha, PINS[sid])
    return raw.decode("utf-8")

class MySQLSourceContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "127.0.0.1"),
            port=int(os.getenv("MYSQL_PORT", "3306")),
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"],
            database=os.environ["MYSQL_DATABASE"],
            autocommit=True,
            charset="utf8mb4",
        )
        with cls.db.cursor() as c:
            c.execute("SELECT VERSION()")
            cls.version = c.fetchone()[0]
        assert cls.version.startswith("8.0."), "This checker requires actual MySQL 8.0, got " + cls.version
        print("Verified disposable native MySQL server:", cls.version, flush=True)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        with self.db.cursor() as c:
            c.execute("DROP TABLE IF EXISTS payments")
            c.execute("""CREATE TABLE payments (
              payment_id BIGINT NOT NULL PRIMARY KEY,
              order_id BIGINT NULL, paid_at DATETIME NULL,
              amount DECIMAL(10,2) NULL
            ) ENGINE=InnoDB""")
            c.execute("DROP TABLE IF EXISTS customer_snapshots")

    def insert(self, rows):
        if rows:
            with self.db.cursor() as c:
                c.executemany("INSERT INTO payments(payment_id,order_id,paid_at,amount) VALUES(%s,%s,%s,%s)", rows)

    def fetch(self, sql):
        with self.db.cursor() as c:
            c.execute(sql)
            return c.fetchall()

    def execute(self, sql):
        with self.db.cursor() as c:
            return c.execute(sql)

    def ids(self):
        return [r[0] for r in self.fetch("SELECT payment_id FROM payments ORDER BY payment_id")]

    def test_01_all_six_source_blobs_and_unsolved_fields(self):
        for sid in PINS:
            with self.subTest(sid=sid):
                s = original(sid)
                self.assertIn("# Advanced Q" + sid[1:] + ".", s)
                self.assertIn("PDF p. 17", s)
                self.assertIn("NOT SOLVED YET", s)
                self.assertIn("## My solution — SQLite\n\nPending.", s)
                self.assertIn("## My solution — SQL Server\n\nPending.", s)
                self.assertIn("## Official solution\n\nPending", s)

    def test_02_a088_unchanged_archived_delete_raises_native_mysql_1093(self):
        s = original("A088")
        match = re.search(r"(?s)\x60{3}sql\s*(.*?)\x60{3}", s)
        self.assertIsNotNone(match)
        original_sql = match.group(1).strip()
        self.assertIn("SELECT MIN(payment_id)", original_sql)
        self.insert([(1,10,"2026-01-01 09:00:00",50),
                     (2,10,"2026-01-01 09:00:00",50),
                     (3,20,"2026-01-02 09:00:00",20)])
        try:
            self.execute(original_sql)
        except pymysql.MySQLError as e:
            self.assertEqual(e.args[0], 1093, ("Expected MySQL Error 1093", e.args))
        else:
            self.fail("Expected native MySQL 8.0 error 1093 from archived A088 SQL")
        self.assertEqual(self.ids(), [1,2,3])

    def test_03_a088_reviewer_self_join_repair_local_illustration(self):
        self.insert([(1,10,"2026-01-01 09:00:00",50),
                     (2,10,"2026-01-01 09:00:00",50),
                     (3,20,"2026-01-02 09:00:00",20)])
        self.assertEqual(self.execute(DELETE_DUPLICATES), 1)
        self.assertEqual(self.ids(), [1,3])

    def test_04_a085_original_archive_illustrative_duplicate_group(self):
        self.insert([(1,10,"2026-01-01 09:00:00",50),
                     (2,10,"2026-01-01 09:00:00",50),
                     (3,10,"2026-01-02 09:00:00",20)])
        result=self.fetch("""SELECT order_id,paid_at,COUNT(*) FROM payments
                            GROUP BY order_id,paid_at HAVING COUNT(*)>1""")
        self.assertEqual(len(result), 1)
        self.assertEqual((result[0][0],str(result[0][1]),result[0][2]),
                         (10,"2026-01-01 09:00:00",2))

    def test_05_a089_original_archive_illustrative_two_groups_three_extras(self):
        self.insert([(1,10,"2026-01-01 09:00:00",None),
                     (2,10,"2026-01-01 09:00:00",None),
                     (3,10,"2026-01-01 09:00:00",None),
                     (4,20,"2026-01-02 09:00:00",None),
                     (5,20,"2026-01-02 09:00:00",None)])
        self.assertEqual(self.fetch(DUPLICATE_COUNTS)[0], (2,3))

    def test_06_a087_null_safe_comparison_vs_ordinary_equality(self):
        self.insert([(1,None,None,1),(2,None,None,2),
                     (3,10,None,3),(4,10,None,4)])
        self.assertEqual(self.fetch(DUPLICATE_COUNTS)[0], (2,2))
        self.assertEqual(self.fetch("""SELECT COUNT(*) FROM payments p JOIN payments k
                 ON p.order_id=k.order_id AND p.paid_at=k.paid_at
                AND p.payment_id>k.payment_id""")[0], (0,))
        self.assertEqual(self.execute(DELETE_DUPLICATES),2)
        self.assertEqual(self.ids(), [1,3])

    def test_07_a087_deletion_is_idempotent_on_disposable_table(self):
        self.insert([(1,10,"2026-01-01",5),(2,10,"2026-01-01",5),
                     (3,10,"2026-01-02",6),(4,20,"2026-01-01",7)])
        self.assertEqual(self.execute(DELETE_DUPLICATES),1)
        self.assertEqual(self.execute(DELETE_DUPLICATES),0)
        self.assertEqual(self.ids(),[1,3,4])

    def test_08_a087_transaction_rollback_restores_deleted_rows(self):
        self.insert([(1,10,"2026-01-01",5),(2,10,"2026-01-01",6),
                     (3,20,"2026-02-01",7)])
        self.execute("START TRANSACTION")
        try:
            self.assertEqual(self.execute(DELETE_DUPLICATES),1)
            self.assertEqual(self.ids(),[1,3])
        finally:
            self.execute("ROLLBACK")
        self.assertEqual(self.ids(),[1,2,3])

    def test_09_a086_earliest_per_order_local_illustration(self):
        self.insert([(1,10,"2026-01-02 09:00",50),
                     (2,10,"2026-01-01 09:00",20),
                     (3,20,"2026-01-03 09:00",30)])
        self.assertEqual(self.fetch("""SELECT payment_id FROM (
                SELECT payment_id,ROW_NUMBER() OVER(
                  PARTITION BY order_id ORDER BY paid_at,payment_id) AS rn
                FROM payments) ranked WHERE rn=1 ORDER BY payment_id"""),((2,),(3,)))

    def test_10_a086_null_paid_at_changes_earliest_policy(self):
        self.insert([(1,10,None,10),(2,10,"2026-01-01",20)])
        first_default=self.fetch("""SELECT payment_id FROM (
           SELECT payment_id,ROW_NUMBER() OVER(
             PARTITION BY order_id ORDER BY paid_at,payment_id) rn
           FROM payments) t WHERE rn=1""")[0][0]
        first_nonnull=self.fetch("""SELECT payment_id FROM (
           SELECT payment_id,ROW_NUMBER() OVER(
             PARTITION BY order_id ORDER BY (paid_at IS NULL),paid_at,payment_id) rn
           FROM payments) t WHERE rn=1""")[0][0]
        self.assertEqual((first_default,first_nonnull),(1,2))

    def test_11_a090_local_illustration_on_extra_unprovided_relation(self):
        self.execute("""CREATE TABLE customer_snapshots (
             cust_id INT, updated_at DATETIME, version INT, value VARCHAR(32)
        ) ENGINE=InnoDB""")
        with self.db.cursor() as c:
            c.executemany("""INSERT INTO customer_snapshots VALUES(%s,%s,%s,%s)""",[
                (1,"2026-01-01",1,"old A"),
                (1,"2026-02-01",1,"newer A"),
                (1,"2026-02-01",2,"newest A"),
                (2,"2026-01-15",4,"old B"),
                (2,"2026-03-01",1,"new B")])
        got=self.fetch("""SELECT cust_id,value FROM (
            SELECT cust_id,value,ROW_NUMBER() OVER(
            PARTITION BY cust_id ORDER BY updated_at DESC, version DESC) rn
            FROM customer_snapshots) s WHERE rn=1 ORDER BY cust_id""")
        self.assertEqual(got,((1,"newest A"),(2,"new B")))

    def test_12_a090_unresolved_exact_updated_at_version_ties(self):
        self.execute("""CREATE TABLE customer_snapshots (
             cust_id INT, updated_at DATETIME, version INT, value VARCHAR(32)
        ) ENGINE=InnoDB""")
        self.execute("""INSERT INTO customer_snapshots VALUES
          (1,'2026-02-01',2,'X'),(1,'2026-02-01',2,'Y')""")
        count=self.fetch("""SELECT COUNT(*) FROM customer_snapshots WHERE
                  cust_id=1 AND updated_at='2026-02-01' AND version=2""")[0][0]
        winner=self.fetch("""SELECT value FROM (
          SELECT value, ROW_NUMBER() OVER (
          PARTITION BY cust_id ORDER BY updated_at DESC,version DESC) rn
          FROM customer_snapshots) ranked WHERE rn=1""")[0][0]
        self.assertEqual(count,2)
        self.assertIn(winner,("X","Y"))  # no unsupported deterministic winner claim

    def test_13_a085_a089_a087_243_python_oracle_combinations(self):
        kinds=[(10,"2026-01-01"),(10,None),(None,None)]
        for n,keys in enumerate(itertools.product(kinds,repeat=5)):
            with self.subTest(case=n):
                self.execute("TRUNCATE TABLE payments")
                rows=[(i+1,key[0],key[1],1) for i,key in enumerate(keys)]
                self.insert(rows)
                counts=collections.Counter(keys)
                want_groups=sum(v>1 for v in counts.values())
                want_extra=sum(v-1 for v in counts.values() if v>1)
                self.assertEqual(self.fetch(DUPLICATE_COUNTS)[0],(want_groups,want_extra))
                self.assertEqual(self.execute(DELETE_DUPLICATES),want_extra)
                self.assertEqual(self.ids(),sorted(min(i+1 for i,key in enumerate(keys) if key==k)
                                                   for k in counts))
                self.assertEqual(self.execute(DELETE_DUPLICATES),0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
