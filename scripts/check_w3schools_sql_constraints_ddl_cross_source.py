"""Read-only audit: 8 W3Schools SQL DDL/constraint lessons versus pinned local sources.

Auditor-authored SQLite fixtures only; no original provider answers or learner grades.
"""
import hashlib
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
 "99. Reference Materials/W3SCHOOLS-TOPICS.md":"c6328c2eb420f47e5585026a7bf3c0a4e41be720",
 "01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md":"d181dd73f96b1f2b7327600e290d52e9fd59a976",
 "01. SQL Mastery/02. Joins/0. Foundation Notes.md":"61d952c98f02a62c6591caaedf5c02cf0b43e3b1",
 "01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md":"af9cc8d5d47e0279fe0d8b0f9276b700ce496888",
 "01. SQL Mastery/14. Data Quality and Deduplication/0. Foundation Notes.md":"f19d2b0340649f2e481ac62705d9c28dd87ce761",
 "01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md":"d2743783106fe64ca087b39216184a87e97d1a8c",
 "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/0. SQL basics/0. Foundation Notes.md":"073c87bebb2d7c72cca97e970a06de965a87abe5",
}
URLS = tuple("https://www.w3schools.com/sql/sql_"+s+".asp" for s in (
 "create_table","constraints","notnull","unique","primarykey","foreignkey","check","default"))

def db():
    c=sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys=ON")
    return c

class ConstraintAudit(unittest.TestCase):
    def test_01_archive_sha_and_selected_index_gaps(self):
        for path,sha in SOURCES.items():
            with self.subTest(path=path):
                data=(ROOT/path).read_bytes()
                self.assertEqual(hashlib.sha1(("blob "+str(len(data))+"\0").encode()+data).hexdigest(),sha)
        index=(ROOT/"99. Reference Materials/W3SCHOOLS-TOPICS.md").read_text(encoding="utf-8")
        for url in URLS:
            self.assertNotIn(url,index)
    def test_02_create_table_columns_empty(self):
        c=db()
        c.execute("CREATE TABLE People(id INTEGER PRIMARY KEY, name TEXT NOT NULL, age INTEGER)")
        self.assertEqual([(x[1],x[2]) for x in c.execute("PRAGMA table_info(People)")],
                         [("id","INTEGER"),("name","TEXT"),("age","INTEGER")])
        self.assertEqual(c.execute("SELECT COUNT(*) FROM People").fetchone()[0],0)
    def test_03_not_null_insert_update_but_blank_string_allowed(self):
        c=db(); c.execute("CREATE TABLE P(id INTEGER PRIMARY KEY,name TEXT NOT NULL)")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO P(id) VALUES (1)")
        c.execute("INSERT INTO P VALUES (1,'')")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("UPDATE P SET name=NULL")
        self.assertEqual(c.execute("SELECT name FROM P").fetchone()[0],"")
    def test_04_unique_known_duplicates_and_two_nulls(self):
        c=db(); c.execute("CREATE TABLE U(id INTEGER PRIMARY KEY,email TEXT UNIQUE)")
        c.executemany("INSERT INTO U VALUES (?,?)",[(1,None),(2,None),(3,"a@x")])
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO U VALUES (4,'a@x')")
        self.assertEqual(c.execute("SELECT COUNT(*) FROM U").fetchone()[0],3)
    def test_05_composite_primary_key_and_not_null_without_rowid(self):
        c=db(); c.execute("CREATE TABLE L(oid INTEGER,n INTEGER,qty INTEGER,PRIMARY KEY(oid,n)) WITHOUT ROWID")
        c.execute("INSERT INTO L VALUES(1,1,3)"); c.execute("INSERT INTO L VALUES(1,2,4)")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO L VALUES(1,1,5)")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO L VALUES(NULL,3,5)")
        self.assertEqual(c.execute("SELECT SUM(qty) FROM L").fetchone()[0],7)
    def test_06_sqlite_integer_primary_key_null_auto_number(self):
        c=db(); c.execute("CREATE TABLE T(id INTEGER PRIMARY KEY,code TEXT)")
        c.execute("INSERT INTO T VALUES(NULL,'made')")
        self.assertEqual(c.execute("SELECT id FROM T").fetchone()[0],1)
    def test_07_foreign_key_orphan_blocked_and_restricted_parent(self):
        c=db(); c.executescript("CREATE TABLE P(id INTEGER PRIMARY KEY);"
                                "CREATE TABLE C(id INTEGER PRIMARY KEY,pid INTEGER REFERENCES P(id));")
        c.execute("INSERT INTO P VALUES (1)"); c.execute("INSERT INTO C VALUES(10,1)")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO C VALUES(11,2)")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("DELETE FROM P WHERE id=1")
        self.assertEqual(c.execute("SELECT COUNT(*) FROM P").fetchone()[0],1)
    def test_08_foreign_key_default_off_and_explicit_cascade(self):
        off=sqlite3.connect(":memory:")
        off.execute("CREATE TABLE P(id INTEGER PRIMARY KEY)")
        off.execute("CREATE TABLE C(pid INTEGER REFERENCES P(id))")
        off.execute("INSERT INTO C VALUES(999)")
        self.assertEqual(off.execute("PRAGMA foreign_keys").fetchone()[0],0)
        self.assertEqual(off.execute("PRAGMA foreign_key_check").fetchall(),[("C",1,"P",0)])
        c=db(); c.executescript("CREATE TABLE P(id INTEGER PRIMARY KEY);"
                                 "CREATE TABLE C(pid INTEGER REFERENCES P(id) ON DELETE CASCADE);")
        c.execute("INSERT INTO P VALUES(1)"); c.execute("INSERT INTO C VALUES(1)")
        c.execute("DELETE FROM P WHERE id=1")
        self.assertEqual(c.execute("SELECT COUNT(*) FROM C").fetchone()[0],0)
    def test_09_check_false_rejected_but_null_unknown_allowed(self):
        c=db(); c.execute("CREATE TABLE A(age INTEGER CHECK(age>=18))")
        c.execute("INSERT INTO A VALUES(NULL)"); c.execute("INSERT INTO A VALUES(18)")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO A VALUES(17)")
        c.execute("CREATE TABLE B(age INTEGER NOT NULL CHECK(age>=18))")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO B VALUES(NULL)")
        self.assertEqual(c.execute("SELECT COUNT(*) FROM A").fetchone()[0],2)
    def test_10_default_omitted_vs_explicit_null(self):
        c=db(); c.execute("CREATE TABLE L(id INTEGER PRIMARY KEY,city TEXT DEFAULT 'Sandnes')")
        c.execute("INSERT INTO L(id) VALUES(1)"); c.execute("INSERT INTO L VALUES(2,NULL)")
        self.assertEqual(c.execute("SELECT city FROM L ORDER BY id").fetchall(),[("Sandnes",),(None,)])
        c.execute("CREATE TABLE R(id INTEGER PRIMARY KEY,city TEXT NOT NULL DEFAULT 'Sandnes')")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO R VALUES(1,NULL)")
    def test_11_create_table_as_select_loses_key_and_unique(self):
        c=db(); c.execute("CREATE TABLE U(id INTEGER PRIMARY KEY,email TEXT UNIQUE NOT NULL)")
        c.execute("INSERT INTO U VALUES(1,'a@x')")
        c.execute("CREATE TABLE Copy AS SELECT id,email FROM U")
        c.execute("INSERT INTO Copy VALUES(1,'a@x')"); c.execute("INSERT INTO Copy VALUES(NULL,NULL)")
        self.assertEqual(c.execute("SELECT COUNT(*) FROM Copy").fetchone()[0],3)
        self.assertTrue(all(x[5]==0 for x in c.execute("PRAGMA table_info(Copy)")))
    def test_12_composite_unique_null_pairs(self):
        c=db(); c.execute("CREATE TABLE I(a INTEGER,b INTEGER,UNIQUE(a,b))")
        c.executemany("INSERT INTO I VALUES (?,?)",[(1,None),(1,None),(1,2),(2,2)])
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO I VALUES(1,2)")
        self.assertEqual(c.execute("SELECT COUNT(*) FROM I").fetchone()[0],4)
    def test_13_failed_multirow_insert_atomic(self):
        c=db(); c.execute("CREATE TABLE S(id INTEGER PRIMARY KEY,qty INTEGER NOT NULL CHECK(qty>=0))")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("INSERT INTO S VALUES(1,5),(2,-1),(3,2)")
        self.assertEqual(c.execute("SELECT COUNT(*) FROM S").fetchone()[0],0)
    def test_14_nullable_foreign_key_and_parent_update_restricted(self):
        c=db(); c.executescript("CREATE TABLE P(id INTEGER PRIMARY KEY);"
                                "CREATE TABLE C(id INTEGER PRIMARY KEY,pid INTEGER REFERENCES P(id));")
        c.execute("INSERT INTO C VALUES(1,NULL)"); c.execute("INSERT INTO P VALUES(4)")
        c.execute("INSERT INTO C VALUES(2,4)")
        with self.assertRaises(sqlite3.IntegrityError): c.execute("UPDATE P SET id=5 WHERE id=4")
        self.assertEqual(c.execute("SELECT id FROM P").fetchall(),[(4,)])

if __name__=="__main__":
    unittest.main(verbosity=2)
