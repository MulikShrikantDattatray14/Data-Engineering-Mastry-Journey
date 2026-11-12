#!/usr/bin/env python3
"""Source-pinned, READ-ONLY Q093 duplicate-submission audit.

Execute the archived PostgreSQL answer in SQLite with precisely asserted,
local compatibility substitutions; assert the original illustration and
independent cases. Reproduce source/key contradictions without correcting
source data, grading an official answer, or claiming learner completion.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCE = BASE / "14. Data Quality and Deduplication/P093. Possible duplicate order submissions.md"
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
SOURCE_SHA = "2b53cdb94d64cb19581be48c9af6f0a8670b72c2"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
REVIEW = "Review: send same-basket pairs to support"
CLEAR = "No duplicate submissions"


def git_blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def replace_exact(sql, old, new):
    assert sql.count(old) == 1, ("source SQL changed", old, sql.count(old))
    return sql.replace(old, new)


def extract_and_adapt():
    assert git_blob(SOURCE) == SOURCE_SHA, "original P093 source changed"
    assert git_blob(KEY) == KEY_SHA, "original PostgreSQL supplied key changed"
    source = SOURCE.read_text(encoding="utf-8")
    for marker in ("# PNP Q093.", "same_day_pairs", "same_basket_pairs",
                   "same_amount_pairs", "exact_copies", "NOT SOLVED YET",
                   "## Schema", "## Official solution", "Pending"):
        assert marker in source, f"missing Q093 source marker: {marker}"
    full_key = KEY.read_text(encoding="utf-8")
    hit = re.search(r"(?ms)^-- Q93\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", full_key)
    assert hit, "Q93 missing from original supplied key"
    sql = hit.group(1).strip()
    assert sql.startswith("WITH product_lines AS (") and sql.endswith(";")
    assert "JOIN signatures AS sg" in sql and "WHERE sg.basket_known" in sql
    sql = replace_exact(
        sql,
        "STRING_AGG(pl.ProductID::text || 'x' || pl.quantity::text, '|'\n"
        "                      ORDER BY pl.ProductID)",
        "SORTED_BASKET_AGG(pl.ProductID, pl.quantity)")
    sql = replace_exact(sql, "BOOL_AND(pl.is_known)", "MIN(pl.is_known)")
    sql = replace_exact(
        sql,
        "(a.Total_Order_Amount, a.PaymentID, a.ShipperID)\n"
        "               IS NOT DISTINCT FROM\n"
        "           (b.Total_Order_Amount, b.PaymentID, b.ShipperID)",
        "(a.Total_Order_Amount IS b.Total_Order_Amount\n"
        "            AND a.PaymentID IS b.PaymentID\n"
        "            AND a.ShipperID IS b.ShipperID)")
    for unsupported in ("::text", "STRING_AGG(", "BOOL_AND(", "IS NOT DISTINCT FROM"):
        assert unsupported not in sql, unsupported
    print("PASS Q093 exact immutable question and supplied-key blob identity")
    print("SCOPE Q093 only SQLite-compatible ORDERED aggregate, BOOL_AND and row-null-safe equality emulations")
    return sql


class SortedBasketAggregate:
    def __init__(self):
        self.lines = []

    def step(self, product_id, quantity):
        self.lines.append((product_id, quantity))

    def finalize(self):
        if not self.lines:
            return None
        values = sorted(self.lines, key=lambda item: (item[0] is None, item[0] or 0))
        return "|".join(f"{pid}x{qty}" for pid, qty in values)


def execute(sql, orders, details):
    db = sqlite3.connect(":memory:")
    try:
        db.create_aggregate("SORTED_BASKET_AGG", 2, SortedBasketAggregate)
        db.execute("CREATE TABLE Orders(OrderID INT, CustomerID INT, OrderDate TEXT,"
                   "Total_Order_Amount NUMERIC, PaymentID INT, ShipperID INT)")
        db.execute("CREATE TABLE OrderDetails(OrderDetailID INT, OrderID INT,"
                   "ProductID INT, Quantity INT)")
        if orders:
            db.executemany("INSERT INTO Orders VALUES(?,?,?,?,?,?)", orders)
        if details:
            db.executemany("INSERT INTO OrderDetails VALUES(?,?,?,?)", details)
        result = db.execute(sql).fetchall()
        assert len(result) == 1, result
        return result[0]
    finally:
        db.close()


def check(sql, orders, details, expected, label):
    got = execute(sql, orders, details)
    assert got == expected, f"{label}: got {got!r}, expected {expected!r}"
    print(f"PASS Q093 {label}: {got!r}")


def main():
    sql = extract_and_adapt()
    check(sql,
          [(1, 10, "2026-01-01", 20, 5, 7),
           (2, 10, "2026-01-01", 20, 5, 7)],
          [(1, 1, 101, 2), (2, 2, 101, 2)],
          (1, 1, 1, 1, REVIEW),
          "original two-order illustrated output")
    check(sql,
          [(1, 10, "2026-01-01", 20, 5, 7),
           (2, 10, "2026-01-01", 25, 5, 7),
           (3, 10, "2026-01-01", 20, 5, 7),
           (4, 10, "2026-01-02", 20, 5, 7),
           (5, 11, "2026-01-01", 20, 5, 7)],
          [(1, 1, 101, 2), (2, 2, 101, 2), (3, 3, 102, 1),
           (4, 4, 101, 2), (5, 5, 101, 2)],
          (3, 1, 1, 0, REVIEW),
          "independent three-pair basket/amount/customer/day separation")
    check(sql, [], [], (0, 0, 0, 0, CLEAR), "empty source")
    check(sql,
          [(1, 10, "2026-01-01", 20, 5, 7),
           (2, 10, "2026-01-01", 20, 5, 7)],
          [(1, 1, 101, 2)],
          (0, 0, 0, 0, CLEAR),
          "KNOWN SPEC GAP: missing basket silently drops same-day header pair")
    check(sql,
          [(1, 10, "2026-01-01", 20, 5, 7),
           (2, 10, "2026-01-01", 20, 5, 7)],
          [(1, 1, 101, None), (2, 2, 101, None)],
          (0, 0, 0, 0, CLEAR),
          "KNOWN SPEC GAP: unknown quantity drops same-day header pair")
    check(sql,
          [(1, 10, "2026-01-01", None, 5, 7),
           (2, 10, "2026-01-01", None, 5, 7)],
          [(1, 1, 101, 2), (2, 2, 101, 2)],
          (1, 1, 0, 1, REVIEW),
          "KNOWN NULL SEMANTICS: exact_copies=1 while same_amount_pairs=0")
    assert execute(sql, [(1, 10, "2026-01-01", 20, 5, 7),
                         (2, 10, "2026-01-01", 20, 5, 7)],
                   [(1, 1, 101, 2)])[:4] != (1, 0, 1, 0)
    print("PARTIAL Q093: 3 bounded passed examples plus 3 captured diagnostics;"
          " key's pre-filter contradicts source's all same-day-pair denominator."
          " No native PostgreSQL, PDF parity, official grade or learner solve.")


if __name__ == "__main__":
    main()
