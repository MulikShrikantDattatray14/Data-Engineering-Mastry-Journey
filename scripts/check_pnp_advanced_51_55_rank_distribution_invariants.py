#!/usr/bin/env python3
"""Partial PNP A051-A055 cross-question audit; read-only SQLite reviewer tests.

All queries and oracles here are auditor-authored, NOT supplier MySQL keys,
historical learner submissions, authentic PDF output, or official grading.
"""
import hashlib
import itertools
import sqlite3
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/"
    "9. Windowing Functions"
)
PINS = {
    "A051": ("A051. Show ROW_NUMBER, RANK and DENSE_RANK together and explain the diff.md",
             "2593dee4fa58352b31442c2a49bdcb149fd30010"),
    "A052": ("A052. Rank employees by salary inside each department.md",
             "1580cbe5bd7a7de498021483be39e67e49c5da72"),
    "A053": ("A053. The highest-paid employee per department, ties broken by earliest.md",
             "2415e2fb39c673626f3fc803d37d6964703ca6ac"),
    "A054": ("A054. Percentile position of each salary within the company.md",
             "aee8087b885167e552415ab48df1c9aaa9e1d84c"),
    "A055": ("A055. Share of employees earning at or below each salary.md",
             "8c8c4d7ead577f786ab77919f6c04bc0798a7344"),
}
DDL = """CREATE TABLE employees (
    emp_id INTEGER PRIMARY KEY, dept_id INTEGER,
    salary INTEGER, hire_date TEXT
);"""
WINDOW = """SELECT emp_id,dept_id,salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC,emp_id) AS row_no,
    RANK() OVER (ORDER BY salary DESC) AS rank_no,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_no,
    PERCENT_RANK() OVER (ORDER BY salary ASC) AS percentile,
    CUME_DIST() OVER (ORDER BY salary ASC) AS cumulative,
    RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS dept_rank
FROM employees ORDER BY emp_id"""
TOP = """WITH ranked AS (
SELECT emp_id,dept_id,salary,hire_date,
 ROW_NUMBER() OVER (
   PARTITION BY dept_id ORDER BY salary DESC,hire_date ASC,emp_id
 ) AS rn
FROM employees
) SELECT dept_id,emp_id,salary FROM ranked WHERE rn=1
ORDER BY dept_id"""

def connection(rows):
    con = sqlite3.connect(":memory:")
    con.executescript(DDL)
    con.executemany("INSERT INTO employees VALUES (?,?,?,?)", rows)
    return con

def windows(rows):
    with connection(rows) as con:
        return con.execute(WINDOW).fetchall()

def top(rows):
    with connection(rows) as con:
        return con.execute(TOP).fetchall()

class PNPAdvancedRankDistributionCrossCheck(unittest.TestCase):
    def test_01_source_blob_sha_and_pending_state_five(self):
        self.assertEqual(len(PINS),5)
        for qid,(filename,sha) in PINS.items():
            data=(BASE/filename).read_bytes()
            actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            self.assertEqual(actual,sha,qid)
            body=data.decode("utf-8")
            for token in (
                "# Advanced Q"+qid[1:]+".",
                "question "+str(int(qid[1:]))+", PDF p. 11",
                "### Sample input and expected output (illustrative)",
                "NOT SOLVED YET",
                "## My solution — SQLite\n\nPending.",
                "## My solution — SQL Server\n\nPending.",
                "## Official solution\n\nPending until",
            ):
                self.assertIn(token,body,qid)

    def test_02_A051_original_archived_illustration_retyped(self):
        rows=[(1,10,100,None),(2,10,90,None),(3,10,90,None),(4,10,80,None)]
        got=windows(rows)
        self.assertEqual([(r[0],r[3],r[4],r[5]) for r in got],
                         [(1,1,1,1),(2,2,2,2),(3,3,2,2),(4,4,4,3)])

    def test_03_A052_original_department_reset_illustration_retyped(self):
        rows=[(1,10,100,None),(2,10,90,None),(3,10,90,None),(4,20,80,None)]
        self.assertEqual([(r[0],r[6]) for r in windows(rows)],
                         [(1,1),(2,2),(3,2),(4,1)])

    def test_04_A053_original_earliest_hire_tie_illustration_retyped(self):
        rows=[(1,10,100,"2020-01-01"),(2,10,100,"2019-01-01"),
              (3,20,80,"2021-01-01")]
        self.assertEqual(top(rows),[(10,2,100),(20,3,80)])

    def test_05_A054_original_percent_rank_illustration_retyped(self):
        rows=[(1,10,40000,None),(2,10,60000,None),(3,10,80000,None)]
        self.assertEqual([(r[0],r[6]) for r in windows(rows)],
                         [(1,0.0),(2,0.5),(3,1.0)])

    def test_06_A055_original_cume_dist_illustration_retyped(self):
        rows=[(1,10,40000,None),(2,10,60000,None),
              (3,10,60000,None),(4,10,80000,None)]
        self.assertEqual([(r[0],r[7]) for r in windows(rows)],
                         [(1,0.25),(2,0.75),(3,0.75),(4,1.0)])

    def test_07_salary_tie_peers_and_stable_row_numbers_are_distinct(self):
        rows=[(3,5,99,None),(1,5,99,None),(2,5,99,None)]
        got=windows(rows)
        self.assertEqual([(r[0],r[3],r[4],r[5]) for r in got],
                         [(1,1,1,1),(2,2,1,1),(3,3,1,1)])

    def test_08_singleton_percent_rank_zero_cume_dist_one(self):
        r=windows([(10,5,600,None)])[0]
        self.assertEqual((r[4],r[5],r[6],r[7]),(1,1,0.0,1.0))

    def test_09_exhaustive_1296_four_person_nonnull_sql_vs_python_oracle(self):
        count=0
        for salaries in itertools.product((10,20,30),repeat=4):
            for depts in itertools.product((1,2),repeat=4):
                rows=[(i+1,depts[i],salaries[i],None) for i in range(4)]
                actual=windows(rows)
                for r in actual:
                    emp,dep,sal,rn,rank,dense,percent,cume,dep_rank=r
                    i=emp-1
                    higher=sum(s>sal for s in salaries)
                    lower=sum(s<sal for s in salaries)
                    lower_equal=sum(s<=sal for s in salaries)
                    distinct_higher=len({s for s in salaries if s>sal})
                    dep_higher=sum(s>sal and d==dep for s,d in zip(salaries,depts))
                    expected_rn=1+sum((s>sal or (s==sal and j<i))
                                      for j,s in enumerate(salaries))
                    self.assertEqual((rn,rank,dense,dep_rank),
                        (expected_rn,higher+1,distinct_higher+1,dep_higher+1))
                    self.assertAlmostEqual(percent,lower/3)
                    self.assertAlmostEqual(cume,lower_equal/4)
                count+=1
        self.assertEqual(count,3**4*2**4)

    def test_10_unassigned_department_NULL_forms_one_partition_in_sqlite(self):
        rows=[(1,None,100,None),(2,None,100,None),
              (3,None,20,None),(4,10,50,None)]
        self.assertEqual([(r[0],r[8]) for r in windows(rows)],
                         [(1,1),(2,1),(3,3),(4,1)])

    def test_11_null_salary_policy_changes_percentile_and_cume_denominators(self):
        rows=[(1,10,None,None),(2,10,10,None),(3,10,20,None)]
        got=windows(rows)
        self.assertEqual([(r[0],r[6],r[7]) for r in got],
                         [(1,0.0,1/3),(2,0.5,2/3),(3,1.0,1.0)])
        excluded=windows([r for r in rows if r[2] is not None])
        self.assertEqual([(r[0],r[6],r[7]) for r in excluded],
                         [(2,0.0,0.5),(3,1.0,1.0)])

    def test_12_adding_emp_id_to_rank_window_destroys_salary_peers(self):
        rows=[(1,10,100,None),(2,10,90,None),(3,10,90,None)]
        with connection(rows) as con:
            broken=con.execute(
                "SELECT emp_id,RANK() OVER (ORDER BY salary DESC,emp_id)"
                " FROM employees ORDER BY emp_id").fetchall()
        self.assertEqual(broken,[(1,1),(2,2),(3,3)])
        self.assertEqual([(r[0],r[4]) for r in windows(rows)],
                         [(1,1),(2,2),(3,2)])

    def test_13_cume_dist_is_not_rows_running_share_with_ties(self):
        rows=[(1,10,10,None),(2,10,20,None),
              (3,10,20,None),(4,10,30,None)]
        with connection(rows) as con:
            running=con.execute(
                "SELECT emp_id,ROW_NUMBER() OVER (ORDER BY salary,emp_id)/4.0 "
                "FROM employees ORDER BY emp_id").fetchall()
        self.assertEqual(running,[(1,0.25),(2,0.5),(3,0.75),(4,1.0)])
        self.assertEqual([(r[0],r[7]) for r in windows(rows)],
                         [(1,0.25),(2,0.75),(3,0.75),(4,1.0)])

    def test_14_A053_equal_salary_and_hire_date_uses_reviewer_emp_id_tie(self):
        rows=[(9,10,100,"2020-01-01"),(2,10,100,"2020-01-01"),
              (7,20,40,"2018-01-01")]
        self.assertEqual(top(rows),[(10,2,100),(20,7,40)])

    def test_15_A053_NULL_hire_date_sorts_before_valid_date_in_sqlite(self):
        rows=[(1,10,100,None),(2,10,100,"2010-01-01")]
        self.assertEqual(top(rows),[(10,1,100)])
        with connection(rows) as con:
            qualified=con.execute(
                "SELECT emp_id FROM employees ORDER BY "
                "salary DESC,(hire_date IS NULL),hire_date,emp_id LIMIT 1"
            ).fetchall()
        self.assertEqual(qualified,[(2,)])

    def test_16_A053_NULL_salary_and_NULL_department_policy_unresolved(self):
        rows=[(1,None,None,"2020-01-01"),(2,None,None,"2019-01-01"),
              (3,20,80,"2022-01-01")]
        self.assertEqual(top(rows),[(None,2,None),(20,3,80)])
        self.assertEqual(top([]),[])

if __name__=="__main__":
    unittest.main(verbosity=2)
