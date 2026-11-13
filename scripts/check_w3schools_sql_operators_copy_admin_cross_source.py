#!/usr/bin/env python3
"""Reviewer-only W3Schools SQL source identity and SQLite semantics, NOT official answers."""
import hashlib
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    '99. Reference Materials/W3SCHOOLS-TOPICS.md': 'c6328c2eb420f47e5585026a7bf3c0a4e41be720',
    '01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md': 'd181dd73f96b1f2b7327600e290d52e9fd59a976',
    '01. SQL Mastery/01. Advanced SELECT/0. Foundation Notes.md': '1ed1077d492a3bd9db25018650b5c1f3cae1371f',
    '01. SQL Mastery/08. SQL Strings and Patterns/0. Foundation Notes.md': '63649bd6ad3a44449873136d90d3bbb2c724dbab',
    '01. SQL Mastery/14. Data Quality and Deduplication/0. Foundation Notes.md': 'f19d2b0340649f2e481ac62705d9c28dd87ce761',
    '01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md': 'd2743783106fe64ca087b39216184a87e97d1a8c',
    '99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/0. SQL basics/0. Foundation Notes.md': '073c87bebb2d7c72cca97e970a06de965a87abe5',
    '99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/1. Intro to SQL and Advanced Select/0. Foundation Notes.md': '4951b326f4ac526140a0dcb517051f787c7b1970',
}
URLS = {
    'operators': 'https://www.w3schools.com/sql/sql_operators.asp',
    'wildcards': 'https://www.w3schools.com/sql/sql_wildcards.asp',
    'select_into': 'https://www.w3schools.com/sql/sql_select_into.asp',
    'insert_select': 'https://www.w3schools.com/sql/sql_insert_into_select.asp',
    'stored_procedures': 'https://www.w3schools.com/sql/sql_stored_procedures.asp',
    'comments': 'https://www.w3schools.com/sql/sql_comments.asp',
    'backup': 'https://www.w3schools.com/sql/sql_backup_db.asp',
    'create_database': 'https://www.w3schools.com/sql/sql_create_db.asp',
}

class CrossSourceReviewer(unittest.TestCase):
    def test_01_pinned_sources_and_selected_index(self):
        for path, sha in PINS.items():
            with self.subTest(path=path):
                data = (ROOT / path).read_bytes()
                actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                self.assertEqual(actual, sha)
        index = (ROOT / '99. Reference Materials/W3SCHOOLS-TOPICS.md').read_text()
        for topic, url in URLS.items():
            with self.subTest(topic=topic):
                self.assertNotIn(url, index)

    def test_02_operator_precedence_and_null_unknown(self):
        with sqlite3.connect(':memory:') as c:
            self.assertEqual(c.execute('SELECT 2+3*4, (2+3)*4, NULL=3, 3<>4').fetchone(), (14,20,None,1))

    def test_03_integer_division_and_zero_guard(self):
        with sqlite3.connect(':memory:') as c:
            self.assertEqual(c.execute('SELECT 5/2, 5.0/2, 5.0/NULLIF(0,0)').fetchone(), (2,2.5,None))

    def test_04_percent_and_underscore_are_distinct(self):
        with sqlite3.connect(':memory:') as c:
            c.executescript("CREATE TABLE names(name TEXT); INSERT INTO names VALUES('A'),('Ab'),('Abc'),('Ax'),('Ba'),(NULL);")
            self.assertEqual(c.execute("SELECT name FROM names WHERE name LIKE 'A_' ORDER BY name").fetchall(), [('Ab',),('Ax',)])
            self.assertEqual(c.execute("SELECT name FROM names WHERE name LIKE 'A%' ORDER BY name").fetchall(), [('A',),('Ab',),('Abc',),('Ax',)])

    def test_05_escaped_wildcard_matches_literal(self):
        with sqlite3.connect(':memory:') as c:
            c.executescript("CREATE TABLE tags(t TEXT); INSERT INTO tags VALUES('10%'),('100'),('10_'),('10a');")
            self.assertEqual(c.execute("SELECT t FROM tags WHERE t LIKE '10!%' ESCAPE '!'").fetchall(), [('10%',)])
            self.assertEqual(c.execute("SELECT t FROM tags WHERE t LIKE '10!_' ESCAPE '!'").fetchall(), [('10_',)])

    def test_06_bracket_like_is_not_portable(self):
        with sqlite3.connect(':memory:') as c:
            c.executescript("CREATE TABLE names(n TEXT); INSERT INTO names VALUES('Ada'),('Ema'),('Zed');")
            self.assertEqual(c.execute("SELECT n FROM names WHERE n LIKE '[AE]%' ORDER BY n").fetchall(), [])
            self.assertEqual(c.execute("SELECT n FROM names WHERE n GLOB '[AE]*' ORDER BY n").fetchall(), [('Ada',),('Ema',)])

    def test_07_select_into_sqlserver_syntax_rejected_by_sqlite(self):
        with sqlite3.connect(':memory:') as c:
            c.executescript("CREATE TABLE src(id INTEGER PRIMARY KEY, code TEXT NOT NULL); INSERT INTO src VALUES(1,'A');")
            with self.assertRaises(sqlite3.OperationalError):
                c.execute('SELECT * INTO dest FROM src')
            self.assertIsNone(c.execute("SELECT name FROM sqlite_master WHERE name='dest'").fetchone())

    def test_08_sqlite_ctas_rows_but_not_keys_or_notnull(self):
        with sqlite3.connect(':memory:') as c:
            c.executescript("CREATE TABLE src(id INTEGER PRIMARY KEY, code TEXT NOT NULL); INSERT INTO src VALUES(1,'A'); CREATE TABLE dest AS SELECT * FROM src;")
            self.assertEqual(c.execute('SELECT * FROM dest').fetchall(), [(1,'A')])
            self.assertEqual([(x[1],x[3],x[5]) for x in c.execute('PRAGMA table_info(dest)')], [('id',0,0),('code',0,0)])

    def test_09_select_into_empty_schema_emulation(self):
        with sqlite3.connect(':memory:') as c:
            c.executescript("CREATE TABLE src(id INT, name TEXT); INSERT INTO src VALUES(1,'x'); CREATE TABLE copy AS SELECT * FROM src WHERE 1=0;")
            self.assertEqual(c.execute('SELECT COUNT(*) FROM copy').fetchone(), (0,))
            self.assertEqual([x[1] for x in c.execute('PRAGMA table_info(copy)')], ['id','name'])

    def test_10_insert_select_maps_explicit_columns(self):
        with sqlite3.connect(':memory:') as c:
            c.executescript("CREATE TABLE src(code TEXT, qty INT); INSERT INTO src VALUES('a',3),('b',7); CREATE TABLE target(id INTEGER PRIMARY KEY, qty INT, code TEXT); INSERT INTO target VALUES(10,1,'old'); INSERT INTO target(qty,code) SELECT qty,code FROM src WHERE qty>4;")
            self.assertEqual(c.execute('SELECT id,qty,code FROM target ORDER BY id').fetchall(), [(10,1,'old'),(11,7,'b')])

    def test_11_insert_select_duplicate_pk_rollback(self):
        with sqlite3.connect(':memory:') as c:
            c.executescript('CREATE TABLE src(id INT); INSERT INTO src VALUES(1),(2); CREATE TABLE target(id INT PRIMARY KEY); INSERT INTO target VALUES(2);')
            with self.assertRaises(sqlite3.IntegrityError):
                c.execute('INSERT INTO target SELECT id FROM src')
            self.assertEqual(c.execute('SELECT id FROM target').fetchall(), [(2,)])

    def test_12_sqlserver_procedure_syntax_not_sqlite(self):
        with sqlite3.connect(':memory:') as c:
            with self.assertRaises(sqlite3.OperationalError):
                c.execute('CREATE PROCEDURE find_orders AS SELECT 1;')

    def test_13_comments_ignored_but_literals_preserved(self):
        with sqlite3.connect(':memory:') as c:
            self.assertEqual(c.execute("SELECT 1 /* add */ + 2 -- comment\n").fetchone(), (3,))
            self.assertEqual(c.execute("SELECT '-- not a comment', '/* literal */'").fetchone(), ('-- not a comment','/* literal */'))

    def test_14_sqlserver_backup_syntax_not_sqlite(self):
        with sqlite3.connect(':memory:') as c:
            with self.assertRaises(sqlite3.OperationalError):
                c.execute("BACKUP DATABASE testDB TO DISK = 'backup.bak'")

    def test_15_create_database_syntax_not_sqlite(self):
        with sqlite3.connect(':memory:') as c:
            with self.assertRaises(sqlite3.OperationalError):
                c.execute('CREATE DATABASE analytics')

if __name__ == '__main__':
    unittest.main(verbosity=2)
