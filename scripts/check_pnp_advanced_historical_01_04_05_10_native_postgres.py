#!/usr/bin/env python3
"""Bounded native PostgreSQL checks of FOUR preserved historical Advanced SQL answers.

Read-only to repository: executes exactly the archived learner SQLite and
provider-attributed MySQL SQL snippets on disposable PostgreSQL 16 tables.
No official PDF parity, independent learner verification, or new mastery claim.
"""
import hashlib
import os
import re
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/2. Joins")
SOURCES = {
    "A001": ("A001. Count employees per department, keeping departments that have none.md",
             "0b9306e594b206fd99612baff55d2f28a53060dd"),
    "A004": ("A004. List customers who have never placed an order.md",
             "eb5d2da2b0ba565a913599ca5137d9cb33599693"),
    "A005": ("A005. Find delivered orders that have no payment row.md",
             "dac439085707ed03c458bfd8fae06a9455131559"),
    "A010": ("A010. Find every employee who earns more than their own manager.md",
             "8443513ecb9e95928d475f636011d63c01f1fcf5"),
}


def load_queries():
    queries = {}
    for sid, (filename, pinned) in SOURCES.items():
        data = (BASE / filename).read_bytes()
        actual = hashlib.sha1(
            b"blob " + str(len(data)).encode() + b"\0" + data
        ).hexdigest()
        assert actual == pinned, f"{sid}: archived Git source changed"
        content = data.decode("utf-8")
        assert content.startswith(f"# Advanced Q{sid[1:]}. ")
        assert "![SOLVED]" in content and "Solved (recorded):" in content
        assert "## Question and image" in content and "## Official solution" in content
        pair = []
        for heading in ("## My solution — SQLite", "## Official solution"):
            assert heading + "\n" in content, (sid, heading)
            section = content.split(heading + "\n", 1)[1].split("\n## ", 1)[0]
            found = re.search(r"(?m)^" + r"\x60\x60\x60" + r"sql[ \t]*\n(.*?)^\x60\x60\x60", section, re.S | re.M)
            assert found, (sid, heading, "no archived query")
            pair.append(found.group(1).strip())
        queries[sid] = pair
        print(f"PIN {sid} {actual}: historical SOLVED badge preserved; "
              "two different archived answer projections extracted")
    return queries


def checked(actual, expected, sid, label, variant):
    assert sorted(actual, key=repr) == sorted(expected, key=repr), (
        f"{sid} {label} {variant}: actual {actual!r}; expected {expected!r}")


def case(sid, label, queries, ddl, rows, expected_learner, expected_attributed):
    # New connection => new TEMP tables; nothing writes to original repository
    # or persistent DB tables. Every fixture uses independent expected rows.
    with psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "audit"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
    ) as conn:
        with conn.cursor() as cur:
            for statement in ddl:
                cur.execute(statement)
            for table, cols, entries in rows:
                if entries:
                    slots = ", ".join(["%s"] * len(cols))
                    cur.executemany(
                        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({slots})",
                        entries,
                    )
            cur.execute(queries[0])
            learner = cur.fetchall()
            cur.execute(queries[1])
            attributed = cur.fetchall()
            checked(learner, expected_learner, sid, label, "learner")
            checked(attributed, expected_attributed, sid, label, "provider-attributed")
        conn.rollback()
    print(f"PASS {sid} {label}: archived learner + attributed keys; "
          f"{len(expected_learner)} learner rows / {len(expected_attributed)} "
          "attributed rows")


DEPARTMENTS = [
    "CREATE TEMP TABLE departments (dept_id INTEGER PRIMARY KEY, dept_name TEXT)",
    "CREATE TEMP TABLE employees (emp_id INTEGER PRIMARY KEY, dept_id INTEGER)",
]
CUSTOMERS = [
    "CREATE TEMP TABLE customers (cust_id INTEGER PRIMARY KEY, cust_name TEXT)",
    "CREATE TEMP TABLE orders (order_id INTEGER PRIMARY KEY, cust_id INTEGER)",
]
PAYMENTS = [
    "CREATE TEMP TABLE orders (order_id INTEGER PRIMARY KEY, status TEXT, amount NUMERIC)",
    "CREATE TEMP TABLE payments (payment_id INTEGER PRIMARY KEY, order_id INTEGER)",
]
STAFF = [
    "CREATE TEMP TABLE employees (emp_id INTEGER PRIMARY KEY, emp_name TEXT, "
    "manager_id INTEGER, salary NUMERIC)",
]


def run():
    queries = load_queries()
    with psycopg.connect(
        host=os.getenv("PGHOST", "127.0.0.1"),
        dbname=os.getenv("PGDATABASE", "audit"),
        port=os.getenv("PGPORT", "5432"),
        user=os.getenv("PGUSER", "audit"),
        password=os.getenv("PGPASSWORD", "audit"),
    ) as db:
        with db.cursor() as cur:
            cur.execute("SHOW server_version_num")
            version = int(cur.fetchone()[0])
            assert version // 10000 == 16, f"unexpected server version {version}"
            print(f"PostgreSQL native server_version_num={version}")

    case("A001", "archived illustrative sample", queries["A001"], DEPARTMENTS,
         [("departments", ("dept_id", "dept_name"),
           [(1, "Sales"), (2, "Support")]),
          ("employees", ("emp_id", "dept_id"),
           [(11, 1), (12, 1)])],
         [(1, "Sales", 2), (2, "Support", 0)],
         [("Sales", 2), ("Support", 0)])
    case("A001", "duplicate names / orphan and NULL employee dept", queries["A001"],
         DEPARTMENTS,
         [("departments", ("dept_id", "dept_name"),
           [(1, "Ops"), (2, "Ops"), (3, "No staff")]),
          ("employees", ("emp_id", "dept_id"),
           [(1, 1), (2, 1), (3, 2), (4, 999), (5, None)])],
         [(1, "Ops", 2), (2, "Ops", 1), (3, "No staff", 0)],
         [("Ops", 2), ("Ops", 1), ("No staff", 0)])
    case("A001", "empty department table", queries["A001"], DEPARTMENTS,
         [("departments", ("dept_id", "dept_name"), []),
          ("employees", ("emp_id", "dept_id"), [(1, 99)])], [], [])

    case("A004", "archived illustrative sample", queries["A004"], CUSTOMERS,
         [("customers", ("cust_id", "cust_name"), [(1, "Asha"), (2, "Mira")]),
          ("orders", ("order_id", "cust_id"), [(10, 1)])],
         [(2, "Mira")], [(2, "Mira")])
    case("A004", "duplicates / orphan / NULL foreign key", queries["A004"],
         CUSTOMERS,
         [("customers", ("cust_id", "cust_name"),
           [(1, "Asha"), (2, "Mira"), (3, "Uma"), (4, None)]),
          ("orders", ("order_id", "cust_id"),
           [(10, 1), (11, 1), (12, None), (13, 999)])],
         [(2, "Mira"), (3, "Uma"), (4, None)],
         [(2, "Mira"), (3, "Uma"), (4, None)])
    case("A004", "empty tables", queries["A004"], CUSTOMERS,
         [("customers", ("cust_id", "cust_name"), []),
          ("orders", ("order_id", "cust_id"), [])], [], [])

    case("A005", "archived illustrative sample", queries["A005"], PAYMENTS,
         [("orders", ("order_id", "status", "amount"),
           [(10, "DELIVERED", 300), (11, "DELIVERED", 250), (12, "PLACED", 0)]),
          ("payments", ("payment_id", "order_id"), [(100, 10)])],
         [(11,)], [(11, 250)])
    case("A005", "duplicate/NULL payment and case/zero/null amount", queries["A005"],
         PAYMENTS,
         [("orders", ("order_id", "status", "amount"),
           [(10, "DELIVERED", 200), (11, "DELIVERED", None),
            (12, "DELIVERED", 0), (13, "PLACED", 10),
            (14, "delivered", 10), (15, None, 10)]),
          ("payments", ("payment_id", "order_id"),
           [(101, 10), (102, 10), (103, None), (104, 999)])],
         [(11,), (12,)], [(11, None), (12, 0)])
    case("A005", "empty tables", queries["A005"], PAYMENTS,
         [("orders", ("order_id", "status", "amount"), []),
          ("payments", ("payment_id", "order_id"), [])], [], [])

    case("A010", "archived illustrative sample", queries["A010"], STAFF,
         [("employees", ("emp_id", "emp_name", "manager_id", "salary"),
           [(1, "Asha", None, 100000), (2, "Bela", 1, 120000),
            (3, "Chitra", 1, 90000)])],
         [(2, "Bela")], [("Bela", 120000, "Asha", 100000)])
    case("A010", "equal salary / NULL / orphan / chained managers", queries["A010"],
         STAFF,
         [("employees", ("emp_id", "emp_name", "manager_id", "salary"),
           [(1, "Root", None, 100000), (2, "Equal", 1, 100000),
            (3, "Higher", 1, 100001), (4, "Lower", 1, 90000),
            (5, "Orphan", 999, 120000), (6, "Unknown", 1, None),
            (8, "NoSalary", None, None), (9, "ToNoSalary", 8, 150000),
            (10, "Self", 10, 100000), (11, "Next", 3, 150000)])],
         [(3, "Higher"), (11, "Next")],
         [("Higher", 100001, "Root", 100000),
          ("Next", 150000, "Higher", 100001)])
    case("A010", "empty staff table", queries["A010"], STAFF,
         [("employees", ("emp_id", "emp_name", "manager_id", "salary"), [])], [], [])
    print("PARTIAL: 12 bounded native PostgreSQL 16 fixture groups; "
          "archived answer SQL unmodified. Provider attribution in Markdown "
          "is NOT independent PDF authentication; no full dataset, MySQL 8 "
          "or SQL Server runtime, new learner solves, grades, or mastery.")


if __name__ == "__main__":
    run()
