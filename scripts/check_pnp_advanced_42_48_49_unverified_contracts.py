#!/usr/bin/env python3
"""Independent PARTIAL source-pinned audit of PNP A042, A048, A049.

No provider MySQL answer, historical learner SQL, grader, or original PDF is
executed here. The SQL below is auditor-authored SQLite on disposable data.
Reports potential contract-policy gaps, not official answer correctness.
"""
import hashlib
import itertools
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice"
PINS = {
    "A042": ("5. CTEs/A042. Compare every department average against the company average in on.md", "2b7bbd8e917f2c75f91410868eedc4dde818f78f", 9),
    "A048": ("10. Recursive CTE/A048. Print the full reporting path of every employee up to the top.md", "ad946a1b825a46f064f0d6304b68b116bf0c887c", 10),
    "A049": ("10. Recursive CTE/A049. How deep does the org chart go.md", "761046ba33b6c5c3b1b3e1e93e12cb58c37d7998", 10),
}

EMPLOYEES_DDL = """CREATE TABLE employees(
    emp_id INTEGER PRIMARY KEY,
    emp_name TEXT,
    dept_id INTEGER,
    manager_id INTEGER,
    salary REAL
);"""

# Window calculations consume employee salaries before collapsing departments.
# This is NOT proof of a single physical table scan by any SQL engine.
DEPARTMENT_QUERY = """
WITH values_per_employee AS (
    SELECT emp_id,dept_id,salary,
           AVG(salary) OVER (PARTITION BY dept_id) AS department_mean,
           AVG(salary) OVER () AS company_mean
    FROM employees
), per_department AS (
    SELECT dept_id,MAX(department_mean) AS department_mean,
           MAX(company_mean) AS company_mean
    FROM values_per_employee GROUP BY dept_id
)
SELECT dept_id,department_mean,company_mean,
       department_mean-company_mean AS difference
FROM per_department ORDER BY dept_id;
"""

# Rooted-only traversal: missing managers/cyclic unrooted components are not
# resolved and therefore cannot justify the word "every" in A048.
ROOTED_QUERY = """
WITH RECURSIVE rooted(emp_id,path,visited,depth) AS (
    SELECT emp_id,CAST(emp_id AS TEXT),'|'||emp_id||'|',0
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.emp_id,r.path||' > '||e.emp_id,
           r.visited||e.emp_id||'|',r.depth+1
    FROM employees e JOIN rooted r ON e.manager_id=r.emp_id
    WHERE r.depth<128 AND instr(r.visited,'|'||e.emp_id||'|')=0
)
SELECT emp_id,path,depth FROM rooted ORDER BY emp_id;
"""


def open_fixture(rows=()):
    connection = sqlite3.connect(":memory:")
    connection.executescript(EMPLOYEES_DDL)
    connection.executemany("INSERT INTO employees VALUES (?,?,?,?,?)", rows)
    return connection


def rooted(rows):
    with open_fixture(rows) as db:
        return db.execute(ROOTED_QUERY).fetchall()


def dept(rows):
    with open_fixture(rows) as db:
        return db.execute(DEPARTMENT_QUERY).fetchall()


class PNPUnverifiedCTEAveragesAndReporting(unittest.TestCase):
    def test_01_three_immutable_source_blobs_and_pending_markers(self):
        for qid,(rel,want,page) in PINS.items():
            data=(BASE/rel).read_bytes()
            actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            self.assertEqual(actual,want,qid)
            body=data.decode("utf-8")
            self.assertTrue(body.startswith("# Advanced Q"+qid[1:]+"."))
            self.assertIn("question "+str(int(qid[1:]))+", PDF p. "+str(page),body)
            self.assertIn("NOT SOLVED YET",body)
            for heading in ("## My solution — SQLite\n\nPending.",
                            "## My solution — SQL Server\n\nPending.",
                            "## Official solution\n\nPending until"):
                self.assertIn(heading,body,qid)
        self.assertEqual(set(PINS),{"A042","A048","A049"})

    def test_02_A042_retyped_archived_illustrative_rows(self):
        actual=dept([(1,"A",10,None,40000),(2,"B",10,None,60000),
                     (3,"C",20,None,80000)])
        self.assertEqual(actual,[(10,50000.0,60000.0,-10000.0),
                                 (20,80000.0,60000.0,20000.0)])

    def test_03_A042_employees_weight_company_mean_not_dept_mean(self):
        actual=dept([(1,"A",10,None,10),(2,"B",10,None,10),
                     (3,"C",20,None,100)])
        self.assertEqual(actual,[(10,10.0,40.0,-30.0),
                                 (20,100.0,40.0,60.0)])
        self.assertNotEqual(actual[0][2],55.0)

    def test_04_A042_null_salaries_do_not_enter_mean_denominator(self):
        actual=dept([(1,"A",10,None,100),(2,"B",10,None,None),
                     (3,"C",20,None,200),(4,"D",30,None,None)])
        self.assertEqual(actual,[(10,100.0,150.0,-50.0),
                                 (20,200.0,150.0,50.0),
                                 (30,None,150.0,None)])

    def test_05_A042_unassigned_department_is_a_separate_group(self):
        actual=dept([(1,"A",None,None,10),(2,"B",None,None,30),
                     (3,"C",20,None,20)])
        self.assertEqual(actual,[(None,20.0,20.0,0.0),(20,20.0,20.0,0.0)])

    def test_06_A042_empty_employee_relation_has_no_department_rows(self):
        self.assertEqual(dept([]),[])

    def test_07_A048_retyped_original_reporting_path_illustration(self):
        actual=rooted([(1,"CEO",None,None,None),(5,"Mira",None,1,None),
                       (6,"Ana",None,5,None)])
        self.assertEqual(actual,[(1,"1",0),(5,"1 > 5",1),(6,"1 > 5 > 6",2)])

    def test_08_A049_retyped_original_max_depth_illustration(self):
        result=rooted([(1,"CEO",None,None,None),(5,"Mira",None,1,None),
                       (6,"Ana",None,5,None),(7,"Dan",None,1,None)])
        self.assertEqual(max(row[2] for row in result),2)

    def test_09_multiple_roots_and_disconnected_orphan_are_not_all_employees(self):
        rows=[(1,"Root",None,None,None),(2,"Child",None,1,None),
              (10,"Other root",None,None,None),(11,"Other",None,10,None),
              (99,"Orphan",None,1234,None)]
        result=rooted(rows)
        self.assertEqual(result,[(1,"1",0),(2,"1 > 2",1),(10,"10",0),
                                 (11,"10 > 11",1)])
        self.assertEqual({r[0] for r in rows}-{r[0] for r in result},{99})

    def test_10_disconnected_cycles_and_self_reference_are_not_rooted(self):
        rows=[(1,"Root",None,None,None),(2,"Child",None,1,None),
              (5,"CycleA",None,6,None),(6,"CycleB",None,5,None),
              (7,"Self",None,7,None)]
        result=rooted(rows)
        self.assertEqual(result,[(1,"1",0),(2,"1 > 2",1)])
        self.assertEqual({r[0] for r in rows}-{r[0] for r in result},{5,6,7})

    def test_11_root_query_does_not_invent_zero_depth_for_empty_org(self):
        with open_fixture() as db:
            result=db.execute("WITH paths AS ("+ROOTED_QUERY.split("WITH RECURSIVE ")[1].split("SELECT emp_id,path,depth")[0]+
                              "SELECT 1) SELECT 1").fetchall() if False else db.execute("SELECT MAX(emp_id) FROM employees").fetchall()
        self.assertEqual(rooted([]),[])
        self.assertEqual(result,[(None,)])

    def test_12_prefix_overlap_1_11_111_and_duplicate_names_are_safe(self):
        result=rooted([(1,"Same",None,None,None),(11,"Same",None,1,None),
                       (111,"Same",None,11,None)])
        self.assertEqual(result,[(1,"1",0),(11,"1 > 11",1),
                                 (111,"1 > 11 > 111",2)])

    def test_13_long_valid_chain_depth_is_edges_not_number_of_people(self):
        rows=[(i,str(i),None,i-1 if i>1 else None,None) for i in range(1,82)]
        result=rooted(rows)
        self.assertEqual(len(result),81)
        self.assertEqual(result[-1][0],81)
        self.assertEqual(result[-1][2],80)
        self.assertEqual(result[-1][1].split(" > "),[str(i) for i in range(1,82)])

    def test_14_reviewer_depth_cap_is_truncation_not_correct_full_tree(self):
        rows=[(i,str(i),None,i-1 if i>1 else None,None) for i in range(1,132)]
        result=rooted(rows)
        self.assertEqual(len(result),129)
        self.assertEqual(result[-1][0],129)
        self.assertEqual(result[-1][2],128)
        self.assertNotIn(131,{r[0] for r in result})

    def test_15_exhaustive_small_acyclic_forests_against_python_oracle(self):
        # 5 nodes with parent either NULL or a lower ID: 1*2*3*4*5=120 forests.
        n=0
        for parents in itertools.product(*(tuple([None]+list(range(1,i))) for i in range(1,6))):
            rows=[(i,str(i),None,parents[i-1],None) for i in range(1,6)]
            actual=rooted(rows)
            expected=[]
            for i in range(1,6):
                chain=[i]
                cur=parents[i-1]
                while cur is not None:
                    chain.append(cur)
                    cur=parents[cur-1]
                path=" > ".join(map(str,reversed(chain)))
                expected.append((i,path,len(chain)-1))
            self.assertEqual(actual,expected,parents)
            n+=1
        self.assertEqual(n,120)

    def test_16_duplicate_emp_ids_rejected_only_under_reviewer_PK_fixture(self):
        with open_fixture([(1,"A",None,None,None)]) as db:
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO employees VALUES (?,?,?,?,?)",
                           (1,"B",None,None,None))


if __name__=="__main__":
    unittest.main(verbosity=2)
