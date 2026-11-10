#!/usr/bin/env python3
"""Read-only independent regression for four archived Bosscoder Recursive CTE problems.

Evidence tiers: archived statement inspected, source-displayed sample reconstructed,
and auditor-synthetic SQLite boundary fixtures. None is an official Academy grade,
official hidden dataset, or new independent learner solution.
"""
from datetime import date, timedelta
from pathlib import Path
import hashlib
import re
import sqlite3

BASE = (
    Path(__file__).resolve().parents[1]
    / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/"
    "10. Recursive CTE"
)
FILES = {
    1: ("1.Sql All People Report To The Given Manager.md",
        "af88997dbe15879d97716d9e248f248620149acf"),
    2: ("2.Sql Find The Subtasks That Did Not Execute.md",
        "ae515f19c09762151c2280ac3ef6164a63dab777"),
    3: ("3.Sql Find The Quiet Students In All Exams.md",
        "3f2970c88cda01b00c1783d7745874f9b4d50144"),
    4: ("4.Sql Report Contiguous Dates.md",
        "d96e923067b83b2669f8441c7ad89c802506ad33"),
}
NOTES_SHA = "5191aa001ad600adcff797ca990433b3364b9a27"
DDL = {
    1: "CREATE TABLE Employees (employee_id INT PRIMARY KEY, employee_name TEXT, manager_id INT);",
    2: """CREATE TABLE Tasks(task_id INT PRIMARY KEY, subtasks_count INT);
           CREATE TABLE Executed(task_id INT, subtask_id INT, PRIMARY KEY(task_id,subtask_id));""",
    3: """CREATE TABLE Student(student_id INT PRIMARY KEY, student_name TEXT);
           CREATE TABLE Exam(exam_id INT, student_id INT, score INT,
                             PRIMARY KEY(exam_id,student_id));""",
    4: """CREATE TABLE Failed(fail_date TEXT PRIMARY KEY);
           CREATE TABLE Succeeded(success_date TEXT PRIMARY KEY);""",
}


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode()
                        + b"\0" + data).hexdigest()


def check_original(path, sha):
    data = path.read_bytes()
    assert blob_sha(data) == sha, ("ARCHIVED SOURCE MODIFIED", str(path),
                                    blob_sha(data), sha)
    return data.decode("utf-8")


def archived_queries(n):
    filename, expected_sha = FILES[n]
    source = check_original(BASE / filename, expected_sha)
    assert "## Question and image" in source and "## Schema" in source
    assert "Solved (recorded)" in source and "UNRATED" in source
    assert "## My solution — SQLite" in source and "## My solution — SQL Server" in source
    official = source.split("## Official solution", 1)[1]
    if n == 1:
        assert "The supplied classroom notes give this solution:" in official
        # Lecture-labeled source text, NOT an independently graded Academy answer.
    else:
        assert "No official solution was supplied for this question." in official
    sqlite_part = source.split("## My solution — SQLite", 1)[1].split(
        "## My solution — SQL Server", 1
    )[0]
    variants = []
    for name, part in (
        ("Nonrecursive CTE", sqlite_part.split(
            "### Solution 1 — Nonrecursive CTE", 1)[1].split(
            "### Solution 2 — Recursive CTE", 1)[0]),
        ("Recursive CTE", sqlite_part.split(
            "### Solution 2 — Recursive CTE", 1)[1]),
    ):
        match = re.search(r"(?m)^" + chr(96)*3
                          + r"sql\s*\n([\s\S]*?)^" + chr(96)*3 + r"\s*$",
                          part)
        assert match, (n, name, "no preserved solution SQL block")
        query = match.group(1).strip()
        assert query.upper().startswith("WITH "), (n, name, query[:40])
        variants.append((name, query))
    assert len(variants) == 2
    return variants


SAMPLES = {
    1: (
        {"Employees": [(1, "Boss", 1), (3, "Alice", 3), (2, "Bob", 1),
                       (4, "Daniel", 2), (7, "Luis", 4), (8, "Jhon", 3),
                       (9, "Angela", 8), (77, "Robert", 1)]},
        [(2,), (4,), (7,), (77,)]
    ),
    2: (
        {"Tasks": [(1, 3), (2, 2), (3, 4)],
         "Executed": [(1, 2), (3, 1), (3, 2), (3, 3), (3, 4)]},
        [(1, 1), (1, 3), (2, 1), (2, 2)]
    ),
    3: (
        {"Student": [(1, "Daniel"), (2, "Jade"), (3, "Stella"),
                     (4, "Jonathan"), (5, "Will")],
         "Exam": [(10, 1, 70), (10, 2, 80), (10, 3, 90), (20, 1, 80),
                  (30, 1, 70), (30, 3, 80), (30, 4, 90),
                  (40, 1, 60), (40, 2, 70), (40, 4, 80)]},
        [(2, "Jade")]
    ),
    4: (
        {"Failed": [("2018-12-28",), ("2018-12-29",),
                    ("2019-01-04",), ("2019-01-05",)],
         "Succeeded": [("2018-12-30",), ("2018-12-31",),
                       ("2019-01-01",), ("2019-01-02",),
                       ("2019-01-03",), ("2019-01-06",)]},
        [("succeeded", "2019-01-01", "2019-01-03"),
         ("failed", "2019-01-04", "2019-01-05"),
         ("succeeded", "2019-01-06", "2019-01-06")]
    ),
}


def synthetic_cases():
    # Q1: real three-level descent; exclude self-managed head, disconnected
    # self-cycle and unrelated branch. Do not assign a new learner solution.
    q1 = (
        {"Employees": [(1, "Boss", 1), (2, "First", 1),
                       (3, "Second", 2), (4, "Third", 3),
                       (5, "Unmanaged", None), (6, "Other", 6),
                       (7, "Other report", 6), (8, "Direct", 1)]},
        [(2,), (3,), (4,), (8,)]
    )
    # Q2: inclusive 20 limit, missing all, none missing, and only the
    # endpoints executed. Expected values derived from an independent set.
    complete = {(11, 1), (12, 1), (12, 20), (13, 1), (13, 2)}
    tasks = [(11, 2), (12, 20), (13, 2), (14, 3)]
    expected2 = sorted((tid, v) for tid, maximum in tasks
                       for v in range(1, maximum + 1)
                       if (tid, v) not in complete)
    assert len(expected2) == 22 and expected2[0] == (11, 2)
    assert (12, 19) in expected2 and (12, 20) not in expected2
    q2 = ({"Tasks": tasks, "Executed": sorted(complete)}, expected2)
    # Q3: multiple middle scores, tied top scores, lone exam (both
    # minimum and maximum), and no-exam student. Both quiet students
    # must have at least one attempt and no extreme anywhere.
    q3 = (
        {"Student": [(1, "Quiet"), (2, "Max in one exam"), (3, "Min"),
                     (4, "Tied middle"), (5, "Solo"), (6, "Absent"),
                     (7, "Tied max")],
         "Exam": [(100, 1, 80), (100, 2, 100), (100, 3, 60),
                  (100, 4, 80), (100, 7, 100), (200, 1, 50),
                  (200, 2, 90), (200, 3, 10), (200, 4, 50),
                  (300, 5, 99)]},
        [(1, "Quiet"), (4, "Tied middle")]
    )
    # Q4: complete 365-day year: exercise >100-recursion behavior in
    # SQLite, a state switch, and an end-of-year boundary.
    day = date(2019, 1, 1)
    failed, succeeded = [], []
    while day <= date(2019, 12, 31):
        target = failed if date(2019, 3, 1) <= day <= date(2019, 3, 31) else succeeded
        target.append((day.isoformat(),))
        day += timedelta(days=1)
    failed.append(("2018-12-31",))
    succeeded.append(("2020-01-01",))
    assert len(failed) == 32 and len(succeeded) == 335
    q4 = (
        {"Failed": failed, "Succeeded": succeeded},
        [("succeeded", "2019-01-01", "2019-02-28"),
         ("failed", "2019-03-01", "2019-03-31"),
         ("succeeded", "2019-04-01", "2019-12-31")]
    )
    return {1: q1, 2: q2, 3: q3, 4: q4}


def replay(n, query, rows):
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(DDL[n])
        for table, records in rows.items():
            if records:
                marks = ",".join("?" * len(records[0]))
                connection.executemany(
                    "INSERT INTO " + table + " VALUES (" + marks + ")", records
                )
        return connection.execute(query).fetchall()
    finally:
        connection.close()


def check(n, variants, case, label):
    rows, expected = case
    for name, query in variants:
        actual = replay(n, query, rows)
        assert actual == expected, (
            f"Recursive CTE Q{n:02} / {name} / {label}",
            f"actual {actual!r}", f"expected {expected!r}"
        )
        print(f"Recursive CTE Q{n:02} {name}: {label} PASS "
              f"({len(expected)} rows)")


def main():
    assert set(FILES) == set(SAMPLES) == set(DDL) == {1, 2, 3, 4}
    foundation = check_original(BASE / "0. Foundation Notes.md", NOTES_SHA)
    for term in ("anchor", "UNION ALL", "SQL Server", "MAXRECURSION", "cycle"):
        assert term.lower() in foundation.lower(), ("foundation structure", term)
    synthetics = synthetic_cases()
    for n in range(1, 5):
        saved = archived_queries(n)
        check(n, saved, SAMPLES[n], "retyped-source-sample")
        check(n, saved, synthetics[n], "independent-synthetic")
    # Diagnostic beyond the explicit 3-level domain in Q1: verify cap
    # behavior only, do not describe as an in-contract correctness grade.
    beyond = {"Employees": [(1, "Boss", 1), (2, "A", 1), (3, "B", 2),
                            (4, "C", 3), (5, "D", 4)]}
    for name, query in archived_queries(1):
        assert replay(1, query, beyond) == [(2,), (3,), (4,)], name
        print(f"Recursive CTE Q01 {name}: depth-4 out-of-contract cap diagnostic PASS")
    print("Integrity: 5 pinned immutable sources; 4 retyped samples + "
          "4 independent synthetic groups; 8 saved query variants each tier; "
          "2 separate out-of-contract depth-cap diagnostics; "
          "1 classroom-labeled source answer not platform graded; "
          "3 records without supplied official answers; "
          "0 verified Academy grades; 0 new independently solved learner exercises.")


if __name__ == "__main__":
    main()
