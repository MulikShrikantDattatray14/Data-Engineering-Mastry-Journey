#!/usr/bin/env python3
"""Read-only source-hash-pinned SQLite audit of Bosscoder Intro/Advanced SELECT notes.

This audits printed chapter examples; NOT provider grading, SQL Server
execution, learner answers, or official dataset verification.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
          "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/"
          "1. Intro to SQL and Advanced Select/0. Foundation Notes.md")
EXPECTED_BLOB = "4951b326f4ac526140a0dcb517051f787c7b1970"

# Manually transcribed from the 16 displayed source-result tables.
# These are chapter examples, NOT official Academy exercise answer keys.
DISPLAYED = [
    [(1, "Alice", "Berlin"), (2, "Bob", "London"), (3, "Amir", "Paris"),
     (4, "Clara", "Berlin"), (5, "Sam", "London"), (6, "Arjun", "Berlin"),
     (7, "Mira", "Rome")],
    [("Pen", 20)],
    [(1, "Alice", "Berlin"), (4, "Clara", "Berlin"), (6, "Arjun", "Berlin")],
    [(4, "Clara"), (6, "Arjun")],
    [(1, "Alice"), (2, "Bob"), (4, "Clara"), (5, "Sam"), (6, "Arjun")],
    [(2, "Bob"), (3, "Amir"), (5, "Sam"), (7, "Mira")],
    [(1, "Alice", "Germany"), (2, "Bob", "UK"), (4, "Clara", "Germany"),
     (5, "Sam", "UK"), (6, "Arjun", "Germany")],
    [("Pen", 10), ("Notebook", 15), ("Mug", 20)],
    [(1, "Alice"), (3, "Amir"), (6, "Arjun")],
    [("Berlin",), ("London",), ("Paris",), ("Rome",)],
    [(4, "Clara", "Berlin"), (6, "Arjun", "Berlin"), (1, "Alice", "Berlin"),
     (5, "Sam", "London"), (2, "Bob", "London"), (3, "Amir", "Paris"),
     (7, "Mira", "Rome")],
    [("Berlin",), ("London",), ("Madrid",), ("Paris",), ("Rome",)],
    [("Berlin",), ("Berlin",), ("Berlin",), ("Berlin",), ("London",),
     ("London",), ("Madrid",), ("Paris",), ("Rome",), ("Rome",)],
    [("Mug",)],
    [("Pen", "Available"), ("Notebook", "Sold out"),
     ("Mug", "Unknown"), ("Bag", "Available")],
    [("Bag", 25), ("Mug", 20)],
]


def check():
    raw = SOURCE.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert blob == EXPECTED_BLOB, f"Original source blob changed: {blob}"
    fence = chr(96) * 3
    pattern = r"(?m)^" + fence + r"(sql|sqlserver)[ \t]*\n(.*?)^" + fence + r"[ \t]*$"
    blocks = re.findall(pattern, raw.decode("utf-8-sig"), re.DOTALL | re.MULTILINE)
    assert len(blocks) == 18, f"Expected 18 source code fences, got {len(blocks)}"
    assert [lang for lang, _ in blocks] == (["sql"] * 16 + ["sqlserver", "sql"])
    assert len(DISPLAYED) == 16
    assert blocks[16][1].strip().startswith("SELECT TOP (2) ")
    assert blocks[17][1].strip().startswith("CREATE TABLE Customers (")

    conn = sqlite3.connect(":memory:")
    conn.executescript(blocks[17][1])  # Exact archived scratch setup.
    assert conn.execute("SELECT COUNT(*) FROM Customers").fetchone() == (7,)
    assert conn.execute("SELECT COUNT(*) FROM Suppliers").fetchone() == (3,)
    assert conn.execute("SELECT COUNT(*) FROM Products").fetchone() == (4,)
    for index, ((lang, query), expected) in enumerate(zip(blocks[:16], DISPLAYED), 1):
        assert lang == "sql"
        result = conn.execute(query.strip()).fetchall()
        assert result == expected, f"Source SELECT example {index:02}: {result!r} != {expected!r}"
    conn.close()

    # Synthetic cases written separately by the auditor; source examples
    # above remain completely unchanged. Do not count as displayed samples.
    test = sqlite3.connect(":memory:")
    test.executescript("""
        CREATE TABLE Customers (customer_id INTEGER, city TEXT, country TEXT, name TEXT);
        INSERT INTO Customers VALUES
        (1,'Berlin','Germany','Al'), (2,'London','UK','aL'),
        (3,'London',NULL,NULL), (4,'Berlin','Germany','A'),
        (5,'London','UK','z'), (6,'Paris',NULL,'Other');
        CREATE TABLE Products (product_id INTEGER, price INTEGER, stock INTEGER);
        INSERT INTO Products VALUES
        (1,9,NULL),(2,10,0),(3,20,5),(4,21,8),(5,NULL,NULL);
        CREATE TABLE Suppliers (city TEXT);
        INSERT INTO Suppliers VALUES ('Berlin'),('Berlin'),('Rome');
    """)
    # 1. AND > OR, with and without parentheses.
    assert test.execute("""
        SELECT customer_id FROM Customers
        WHERE city='Berlin' OR city='London' AND customer_id > 4
        ORDER BY customer_id
    """).fetchall() == [(1,), (4,), (5,)]
    assert test.execute("""
        SELECT customer_id FROM Customers
        WHERE (city='Berlin' OR city='London') AND customer_id > 4
        ORDER BY customer_id
    """).fetchall() == [(5,)]
    # 2. BETWEEN includes endpoints, excludes NULL/outside boundaries.
    assert test.execute("""
        SELECT product_id FROM Products WHERE price BETWEEN 10 AND 20
        ORDER BY product_id
    """).fetchall() == [(2,), (3,)]
    # 3. NULL is neither equal nor unequal to Germany in WHERE.
    assert test.execute("""
        SELECT customer_id FROM Customers WHERE NOT country='Germany'
        ORDER BY customer_id
    """).fetchall() == [(2,), (5,)]
    assert test.execute("""
        SELECT customer_id FROM Customers WHERE country IS NULL
        ORDER BY customer_id
    """).fetchall() == [(3,), (6,)]
    # 4. UNION DISTINCT vs UNION ALL must differ when duplicates exist.
    assert test.execute("""
        SELECT city FROM Customers UNION SELECT city FROM Suppliers ORDER BY city
    """).fetchall() == [("Berlin",), ("London",), ("Paris",), ("Rome",)]
    assert test.execute("""
        SELECT city FROM Customers UNION ALL SELECT city FROM Suppliers
    """).fetchall().__len__() == 9
    # 5. Deterministic limit when price ties; NULL placement is dialect-specific.
    test.execute("INSERT INTO Products VALUES (6,20,3)")
    assert test.execute("""
        SELECT product_id FROM Products WHERE price IS NOT NULL
        ORDER BY price DESC, product_id ASC LIMIT 3
    """).fetchall() == [(4,), (3,), (6,)]
    # 6. SQLite's default LIKE ASCII case-insensitivity; other collations differ.
    assert test.execute("""
        SELECT customer_id FROM Customers WHERE name LIKE 'a%'
        ORDER BY customer_id
    """).fetchall() == [(1,), (2,), (4,)]
    test.close()

    print("PASS: original Intro/Advanced SELECT source blob unchanged; 18/18 "
          "fences inventoried (16 original SQLite queries replayed against "
          "16 displayed tables; one original setup executed; one SQL Server "
          "TOP example inventoried only); six synthetic SQLite boundary "
          "groups passed. NOT Academy official grading, original exercise "
          "answers, SQL Server runtime, or new learner completion.")


if __name__ == "__main__":
    check()
