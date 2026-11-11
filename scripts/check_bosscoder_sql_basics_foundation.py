#!/usr/bin/env python3
"""Read-only, hash-pinned verification of two archived Bosscoder SQL Basics notes.

SQL Server syntax examples and placeholder fragments are inventoried but
are never claimed to have been executed against SQL Server.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
BASE = ("99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
        "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/"
        "0. SQL basics/")
FILES = (
    ("0. Foundation Notes.md", "073c87bebb2d7c72cca97e970a06de965a87abe5", 15),
    ("SQL Logical Query Processing Order.md", "f5aee78c235bc3b5f25b82ae302a1f44d52950ef", 8),
)

def original_fences(name, expected_sha, expected_count):
    raw = (ROOT / BASE / name).read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert actual == expected_sha, f"Archived source changed: {name}: {actual}"
    fence = chr(96) * 3
    regex = r"(?m)^" + fence + r"sql\s*\n(.*?)^" + fence + r"[ \t]*$"
    result = re.findall(regex, raw.decode("utf-8-sig"), re.DOTALL | re.MULTILINE)
    assert len(result) == expected_count, (name, "SQL fences", len(result))
    return [block.strip() for block in result]

def run(conn, source):
    # Deliberately only for these SHA-pinned fences with no semicolons in strings.
    result = None
    for item in source.split(";"):
        statement = item.strip()
        if not statement:
            continue
        cursor = conn.execute(statement)
        if statement.upper().startswith("SELECT"):
            result = cursor.fetchall()
    return result

def check():
    base = original_fences(*FILES[0])
    logical = original_fences(*FILES[1])
    assert base[14].startswith("CREATE TABLE Suppliers (")
    assert base[5] == "PRAGMA foreign_keys = ON;"
    assert base[9].startswith("BEGIN TRANSACTION;")
    assert base[10].startswith("ROLLBACK;")
    assert base[11].startswith("CREATE VIEW AvailableProducts AS")
    assert base[13].startswith("CREATE INDEX idx_products_category")
    for block, prefix in zip(logical, (
        "SELECT column_name", "SELECT TOP 10", "SELECT column_name",
        "WHERE activity_date", "HAVING COUNT(student)",
        "SELECT SUM(Total) AS Revenue", "SELECT class", "SUM(Revenue) OVER"
    )):
        assert block.startswith(prefix), (prefix, block[:80])

    conn = sqlite3.connect(":memory:", isolation_level=None)
    run(conn, base[5])                  # Connection setting before DML.
    assert conn.execute("PRAGMA foreign_keys").fetchone() == (1,)
    run(conn, base[14])                 # Source puts optional setup last.
    contracts = (
        (0, [(1, "Pen", "Stationery", 200, 10, 1),
             (2, "Notebook", "Stationery", 500, 0, 1),
             (3, "Mug", "Home", 800, None, 2),
             (4, "Bottle", "Home", 800, 5, 2),
             (5, "Pen", "Stationery", 200, 20, None)]),
        (1, [(3, "Mug", None)]),
        (2, [(1, "Pen", 10), (4, "Bottle", 5), (5, "Pen", 20)]),
        (3, [(1, "Pen", 2.0), (2, "Notebook", 5.0)]),
        (4, [("Stationery", 3)]),
    )
    for number, expected in contracts:
        assert run(conn, base[number]) == expected, f"Basics source fence {number + 1}"
    assert run(conn, base[6]) == [(1, "Pen", 5, None)]
    assert run(conn, base[7]) == [(0,)]
    run(conn, base[8])
    assert conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='ScratchItems'").fetchone() == (0,)
    assert run(conn, base[9]) == [(1, 99)]
    assert run(conn, base[10]) == [(1, 10)]
    assert run(conn, base[11]) is None
    assert run(conn, base[12]) == [(1, "Pen", 10), (4, "Bottle", 5), (5, "Pen", 20)]
    assert run(conn, base[13]) is None
    assert conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name='idx_products_category'"
    ).fetchone() == (1,)

    # Independent auditor-created boundaries; not provider answer checks.
    assert conn.execute("SELECT COUNT(*) FROM Products WHERE stock = NULL").fetchone() == (0,)
    assert conn.execute("SELECT COUNT(*) FROM Products WHERE stock IS NULL").fetchone() == (1,)
    try:
        conn.execute("INSERT INTO Products VALUES (6,'Invalid','Other',100,-1,1)")
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("CHECK unexpectedly accepts negative stock")
    try:
        conn.execute("INSERT INTO Products VALUES (6,'Invalid','Other',100,1,999)")
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("FOREIGN KEY unexpectedly accepts orphan")
    conn.execute("INSERT INTO Products VALUES (6,'Unknown','Other',100,NULL,NULL)")
    assert conn.execute("SELECT stock FROM Products WHERE product_id=6").fetchone() == (None,)
    conn.close()

    other = sqlite3.connect(":memory:", isolation_level=None)
    other.executescript(
        "CREATE TABLE Invoice (Total INTEGER);"
        "INSERT INTO Invoice VALUES (10),(15),(50);"
        "CREATE TABLE Courses (class TEXT);"
        "INSERT INTO Courses VALUES ('A'),('A'),('A'),('A'),('A'),"
        "('B'),('B'),('B'),('B'),('C'),('C'),('C'),('C'),('C'),('C');"
    )
    assert run(other, logical[5]) == [(75,)]
    assert set(run(other, logical[6])) == {("A",), ("C",)}
    other.close()
    print("PASS: both original file hashes; 15 Basics SQL source fences run/classified; "
          "10 source-displayed result contracts replayed; 8 logical-order SQL fences "
          "classified, two runnable SQLite examples executed and six placeholders/"
          "SQL Server/fragments inventory-only; four synthetic SQLite boundary groups. "
          "Not SQL Server verified, Academy graded, or learner solved.")

if __name__ == "__main__":
    check()
