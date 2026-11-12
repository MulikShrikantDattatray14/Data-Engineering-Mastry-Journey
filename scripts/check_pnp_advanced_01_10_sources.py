#!/usr/bin/env python3
"""Source-hash-pinned A001-A010 partial audit; never grants learner credit.

Executes actual preserved A004/A005 learner SQLite SQL and their archived
provider-attributed MySQL SQL on independent SQLite fixtures. Other A IDs are
inspected/pinned only; their pending answers are NOT synthesized or tested.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
# Immutable source Markdown, NOT current canonical notes or progress.
PINS = {
    "A001": ("2. Joins/A001. Count employees per department, keeping departments that have none.md", "0b9306e594b206fd99612baff55d2f28a53060dd"),
    "A002": ("6. SubQueries/A002. Second highest salary, no LIMIT and no window function.md", "d797abb456ebf1a35ad4ade88c345170c997043c"),
    "A003": ("9. Windowing Functions/A003. Third highest distinct salary, ties collapsed.md", "3d93fdfbec83c68a495dee74e044b24fb0470004"),
    "A004": ("2. Joins/A004. List customers who have never placed an order.md", "eb5d2da2b0ba565a913599ca5137d9cb33599693"),
    "A005": ("2. Joins/A005. Find delivered orders that have no payment row.md", "dac439085707ed03c458bfd8fae06a9455131559"),
    "A006": ("2. Joins/A006. MySQL has no FULL OUTER JOIN. Emulate one between customers and or.md", "20e4460e715ec53fd41f063e1368fa3753f2a0fd"),
    "A007": ("6. SubQueries/A007. Product IDs that exist in products but were never ordered — set-op.md", "92d491023d8184e85e1732f4122b967e31575d52"),
    "A008": ("2. Joins/A008. Build a complete date × category grid so empty combinations still.md", "668f755b58b74935d9be1b7f6e2f635b713b4ec8"),
    "A009": ("2. Joins/A009. Bucket every product into a price band using a non-equi join.md", "6bcfa001f4a28934d4e06d277463eb242822a4de"),
    "A010": ("2. Joins/A010. Find every employee who earns more than their own manager.md", "8443513ecb9e95928d475f636011d63c01f1fcf5"),
}
SOLVED_BASELINE = {"A001", "A004", "A005", "A010"}

def read_sources():
    sources = {}
    for sid, (rel, pinned) in PINS.items():
        data = (BASE / rel).read_bytes()
        sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert sha == pinned, f"{sid}: original source archive changed"
        content = data.decode("utf-8")
        assert content.startswith(f"# Advanced Q{sid[1:]}. "), sid
        for token in ("## Question and image", "### Sample input and expected output",
                      "## Schema", "## My solution — SQLite", "## Official solution"):
            assert token in content, (sid, token)
        if sid in SOLVED_BASELINE:
            assert "Solved (recorded):" in content and "## Official solution\n" in content
        else:
            assert "NOT SOLVED YET" in content
            assert "## My solution — SQLite\n\nPending." in content
            assert "## Official solution\n\nPending until" in content
        sources[sid] = content
    print("PASS: 10 original Advanced A001-A010 Markdown sources pinned; "
          "4 historical solved baselines, 6 pending source records unchanged")
    return sources

def extract(source, heading):
    section = source.split(heading + "\n", 1)
    assert len(section) == 2, heading
    section = section[1].split("\n## ", 1)[0]
    match = re.search(r"(?m)^" + re.escape(chr(96) * 3) +
                      r"sql[ \t]*\n(.*?)^" + re.escape(chr(96) * 3), section, re.S | re.M)
    assert match, f"{heading}: archived SQL absent, not inventing a query"
    return match.group(1).strip()

def checked(actual, expected, label):
    assert sorted(actual, key=repr) == sorted(expected, key=repr), (
        f"{label}: actual={actual!r}, expected={expected!r}")

def a004(learner, attributed, customers, orders, expected, label):
    with sqlite3.connect(":memory:") as db:
        db.executescript("""
          CREATE TABLE customers(cust_id INTEGER PRIMARY KEY, cust_name TEXT);
          CREATE TABLE orders(order_id INTEGER PRIMARY KEY, cust_id INTEGER);
        """)
        db.executemany("INSERT INTO customers VALUES (?,?)", customers)
        db.executemany("INSERT INTO orders VALUES (?,?)", orders)
        got_learner = db.execute(learner).fetchall()
        got_attributed = db.execute(attributed).fetchall()
        checked(got_learner, expected, f"A004 {label} learner")
        checked(got_attributed, expected, f"A004 {label} provider-attributed")
        print(f"PASS A004 {label}: {len(expected)} expected unmatched customers; "
              "both archived snippets, SQLite only")

def a005(learner, attributed, orders, payments, expected, label):
    with sqlite3.connect(":memory:") as db:
        db.executescript("""
          CREATE TABLE orders(order_id INTEGER PRIMARY KEY, status TEXT, amount REAL);
          CREATE TABLE payments(payment_id INTEGER PRIMARY KEY, order_id INTEGER);
        """)
        db.executemany("INSERT INTO orders VALUES (?,?,?)", orders)
        db.executemany("INSERT INTO payments VALUES (?,?)", payments)
        got_learner = db.execute(learner).fetchall()
        got_attributed = db.execute(attributed).fetchall()
        checked(got_attributed, expected, f"A005 {label} provider-attributed")
        checked(got_learner, [(order_id,) for order_id, _ in expected],
                f"A005 {label} learner projected IDs")
        print(f"PASS A005 {label}: {len(expected)} delivered unpaid orders; "
              "projected ID equality, SQLite only")

def main():
    s = read_sources()
    learner4 = extract(s["A004"], "## My solution — SQLite")
    attributed4 = extract(s["A004"], "## Official solution")
    learner5 = extract(s["A005"], "## My solution — SQLite")
    attributed5 = extract(s["A005"], "## Official solution")
    assert "cust_id IS NOT NULL" in learner4 and "LEFT JOIN orders" in attributed4
    assert "order_id IS NOT NULL" in learner5 and "NOT EXISTS" in attributed5
    a004(learner4, attributed4, [(1, "Asha"), (2, "Mira")], [(10, 1)],
         [(2, "Mira")], "archive illustration")
    a004(learner4, attributed4,
         [(1, "Asha"), (2, "Mira"), (3, "Uma"), (4, None)],
         [(10, 1), (11, 1), (12, None), (13, 999)],
         [(2, "Mira"), (3, "Uma"), (4, None)],
         "duplicate matches / NULL foreign key / orphan")
    a004(learner4, attributed4, [(5, "Alia")], [], [(5, "Alia")],
         "all customers unmatched")
    a004(learner4, attributed4, [], [], [], "both tables empty")
    a005(learner5, attributed5,
         [(10, "DELIVERED", 300), (11, "DELIVERED", 250), (12, "PLACED", 0)],
         [(100, 10)], [(11, 250.0)], "archive illustration")
    a005(learner5, attributed5,
         [(10, "DELIVERED", 200), (11, "DELIVERED", None),
          (12, "DELIVERED", 0), (13, "PLACED", 10),
          (14, "delivered", 10), (15, None, 10)],
         [(101, 10), (102, 10), (103, None), (104, 999)],
         [(11, None), (12, 0.0)],
         "duplicate payments / NULL FK / orphan / status / zero")
    a005(learner5, attributed5,
         [(20, "DELIVERED", 150), (21, "PLACED", 300)], [],
         [(20, 150.0)], "no payments")
    a005(learner5, attributed5, [], [], [], "both tables empty")
    print("PARTIAL only: eight bounded fixture groups for historical A004/A005; "
          "A001/A010 existing independent tests retained; A002/A003/A006-A009 "
          "statement inspected but no invented answers. Provider PDF parity, "
          "MySQL 8/SQL Server, full original data, grades, new learner solutions "
          "and mastery NOT verified.")

if __name__ == "__main__":
    main()
