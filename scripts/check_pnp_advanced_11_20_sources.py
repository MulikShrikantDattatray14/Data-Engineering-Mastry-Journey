#!/usr/bin/env python3
"""Read-only, source-pinned A011-A020 audit; only A012/A014 saved SQL is executed.

The preserved Markdown is NOT rewritten. A012/A014 excerpts are historical
learner and provider-attributed snippets, not newly authored learner answers.
Successful SQLite fixtures are not official PDF parity or MySQL verification.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
PINS = {
    "A011": ("2. Joins/A011. List all pairs of colleagues in the same department, without mirro.md", "fb8226a93e2b3fa12e98b32bc29d13747157114c"),
    "A012": ("2. Joins/A012. Managers with three or more direct reports.md", "0ae54085049ef49de5aeb1e6f5e8614e2f9e50c0"),
    "A013": ("2. Joins/A013. Customers who bought product 101 but never product 202.md", "fbe7edcdc1b633e1574ca54cf538653a757cc522"),
    "A014": ("2. Joins/A014. Employees who manage nobody (the leaves of the org tree).md", "638cb50c24be32c94818a26285a45664ccd756df"),
    "A015": ("9. Windowing Functions/A015. Show each employee next to their department average, without colla.md", "6140bffe76e4aaecec6fd28005aa0bc47ab842df"),
    "A016": ("3. Sorting and Grouping/A016. Departments where the average salary tops 50,000 and headcount is.md", "362737f84e5ee2b6fecb67ba74ec1e112a6010f3"),
    "A017": ("3. Sorting and Grouping/A017. Revenue by product category, highest first.md", "183466f25cf4a1d4d81674d70d06c9e0411ba09e"),
    "A018": ("3. Sorting and Grouping/A018. Monthly count of distinct buyers, cancelled orders excluded.md", "3d32fe4d91a33e305e91e486ebe8b1b9dd270a14"),
    "A019": ("4. Aggregation/A019. Category revenue with a grand-total row at the bottom.md", "82fccf042cbe4093ffc65c9af78ceb2ee07e6223"),
    "A020": ("4. Aggregation/A020. Average order value per customer, only for customers with 3+ order.md", "f3b7856077cf2ca55e7727e2bc51bd8450cc8cc8"),
}
HISTORICALLY_SOLVED = {"A012", "A014"}

def read_sources():
    sources = {}
    for sid, (rel, sha) in PINS.items():
        data = (BASE / rel).read_bytes()
        blob_sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert blob_sha == sha, f"{sid}: preserved original blob has changed"
        source = data.decode("utf-8")
        assert source.startswith(f"# Advanced Q{sid[1:]}. "), sid
        for heading in ("## Question and image", "### Sample input and expected output",
                        "## Schema", "## My solution — SQLite", "## Official solution"):
            assert heading in source, (sid, heading)
        if sid in HISTORICALLY_SOLVED:
            assert "Solved (recorded): 2026-10-28" in source, sid
            assert "![SOLVED]" in source, sid
        else:
            assert "NOT SOLVED YET" in source, sid
            assert "## My solution — SQLite\n\nPending." in source, sid
            assert "## Official solution\n\nPending until" in source, sid
        sources[sid] = source
    print("PASS: 10 original A011-A020 Git blobs intact; 2 historical solved, 8 pending")
    return sources

def extract(source, heading):
    pieces = source.split(heading + "\n", 1)
    assert len(pieces) == 2, f"missing {heading}"
    section = pieces[1].split("\n## ", 1)[0]
    query = re.search(r"(?ms)^\x60\x60\x60sql[ \t]*\n(.*?)^\x60\x60\x60", section)
    assert query, f"no archived SQL under {heading}"
    return query.group(1).strip()

def assert_rows(actual, expected, label):
    assert sorted(actual, key=repr) == sorted(expected, key=repr), (
        f"{label}: got {actual!r}; wanted {expected!r}")

def exercise(sid, learner, attributed, rows, expected_learner, expected_key, label):
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE employees(emp_id INTEGER PRIMARY KEY, emp_name TEXT, manager_id INTEGER)")
        db.executemany("INSERT INTO employees VALUES(?,?,?)", rows)
        assert_rows(db.execute(learner).fetchall(), expected_learner,
                    f"{sid} {label} historical learner SQL")
        assert_rows(db.execute(attributed).fetchall(), expected_key,
                    f"{sid} {label} quoted provider-attributed SQL")
    print(f"PASS {sid} {label}: original archived snippets (SQLite only)")

def main():
    s = read_sources()
    l12 = extract(s["A012"], "## My solution — SQLite")
    a12 = extract(s["A012"], "## Official solution")
    l14 = extract(s["A014"], "## My solution — SQLite")
    a14 = extract(s["A014"], "## Official solution")
    assert "COUNT(e.emp_id)" in l12 and "HAVING COUNT(e.emp_id) >= 3" in l12
    assert "COUNT(*)" in a12 and "HAVING COUNT(*) >= 3" in a12
    assert "NOT IN" in l14 and "IS NOT NULL" in l14
    assert "NOT EXISTS" in a14

    exercise("A012", l12, a12,
             [(1,"Asha",None),(2,"Bela",1),(3,"Chitra",1),(4,"Dev",1),(5,"Esha",2)],
             [(1,3)], [(1,"Asha",3)], "archived 3-report illustration")
    exercise("A012", l12, a12,
             [(10,"Boss",None),(11,"One",10),(12,"Two",10),(13,"Three",10),
              (14,"Four",10),(15,"OrphanOne",99),(16,"OrphanTwo",99),
              (17,"OrphanThree",99),(18,"Root",None),(19,"Solo",18)],
             [(10,4)], [(10,"Boss",4)],
             "4-report threshold and 3 orphan-manager references")
    exercise("A012", l12, a12,
             [(1,"Root",None),(2,"A",1),(3,"B",1),(4,"Other",None)],
             [], [], "two reports below threshold")
    exercise("A012", l12, a12, [], [], [], "empty employees")

    exercise("A014", l14, a14,
             [(1,"Asha",None),(2,"Bela",1),(3,"Chitra",1)],
             [(2,"Bela"),(3,"Chitra")],
             [(2,"Bela"),(3,"Chitra")], "archived leaves illustration")
    exercise("A014", l14, a14,
             [(1,"Asha",None),(2,"Bela",1),(3,"Chitra",1),(4,"Dev",1),
              (5,"Esha",2),(6,None,None),(7,"Orphan",999),(8,"Self",8)],
             [(3,"Chitra"),(4,"Dev"),(5,"Esha"),(6,None),(7,"Orphan")],
             [(3,"Chitra"),(4,"Dev"),(5,"Esha"),(6,None),(7,"Orphan")],
             "NULL names, orphan managers, self-manager and multiple roots")
    exercise("A014", l14, a14,
             [(9,"Alone",None),(10,"Solo",None)],
             [(9,"Alone"),(10,"Solo")], [(9,"Alone"),(10,"Solo")],
             "all employees are leaves")
    exercise("A014", l14, a14, [], [], [], "empty employees")
    print("PARTIAL: 8 SQLite fixture groups across A012/A014; A011/A013/A015-A020 "
          "statement inspected only. Provider PDF/source-grade authentication, "
          "native MySQL/SQL Server, full datasets and new learner mastery NOT verified.")

if __name__ == "__main__":
    main()
