#!/usr/bin/env python3
"""Read-only, source-hash-pinned PNP Q081-Q088 inspection and bounded Q081/Q082/Q085/Q086 key replay.

All eight original statements and corresponding supplied-key sections are inspected.
Only four key queries execute on two SQLite fixture groups each. Q086's source-order
discrepancy is ASSERTED AS A FAILURE OF THE TASK CONTRACT, not awarded a pass.
No provider-authenticated official answer, native PostgreSQL parity, original
commerce-dataset parity or independent learner completion is implied.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/2.PNP- foundations and practice"
)
KEY = BASE / "Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql"
KEY_SHA = "7912c8e676621c513e0b635a40c6ee299404676e"
SOURCES = {
    81: ("12. Dates and Time/P081. Year-to-date vs same period last year.md", "054faf9e755d6f7212a7c8906be5165aa922abf8"),
    82: ("9. Windowing Functions/P082. Each customer's favourite category.md", "b12c819076c2418c805dd88a020278c3007a85e0"),
    83: ("15. Analytics and Performance/P083. Underperforming sub-categories in the last six months.md", "b1339a417e6f47b85792b43d45f32edf32f281ad"),
    84: ("4. Aggregation/P084. Delivery time by state and shipper with subtotals.md", "e019aa308f9726e1328a44e24e89c7c4db677701"),
    85: ("12. Dates and Time/P085. Win-back customers returning after 180+ days.md", "36e53c1398e4c533961c84b661fe501615a34033"),
    86: ("14. Data Quality and Deduplication/P086. Reconcile order headers with order lines.md", "6ef60c84817d83962ef24d77f301b9ad8b962f93"),
    87: ("14. Data Quality and Deduplication/P087. Referential integrity audit across all seven relationships.md", "28bed1fe1c7d2e6c4c92e68f6a619a6fb2780e02"),
    88: ("14. Data Quality and Deduplication/P088. Date validity audit.md", "52c73f3594668d77afbe679b25a84997fb3ced59"),
}
DDL = {
    81: ["Orders(OrderID INT, OrderDate TEXT, Total_Order_Amount NUMERIC)"],
    82: ["Orders(OrderID INT, CustomerID INT, OrderDate TEXT)",
         "OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT, Quantity INT)",
         "Products(ProductID INT, CategoryID INT)",
         "Category(CategoryID INT, CategoryName TEXT)"],
    85: ["Orders(OrderID INT, CustomerID INT, OrderDate TEXT, Total_Order_Amount NUMERIC)"],
    86: ["Orders(OrderID INT, PaymentID INT, Total_Order_Amount NUMERIC)",
         "Payments(PaymentID INT, PaymentType TEXT)",
         "Products(ProductID INT, Sale_Price NUMERIC)",
         "OrderDetails(OrderDetailID INT, OrderID INT, ProductID INT, Quantity INT)"],
}

def git_blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def swap(sql, before, after, occurrences=1):
    assert sql.count(before) == occurrences, f"key excerpt drift: {before[:65]} count={sql.count(before)}"
    return sql.replace(before, after)

def extract(key, n):
    m = re.search(rf"(?ms)^-- Q{n}\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", key)
    assert m, f"missing supplied Q{n} query"
    sql = m.group(1).strip()
    assert sql.startswith("WITH ") and sql.endswith(";"), n
    return sql

def sqlite_key(n, sql):
    if n == 81:
        sql = swap(sql, "MAX(o.OrderDate)::date", "DATE(MAX(o.OrderDate))")
        sql = swap(sql, "(DATE_TRUNC('year', a.ytd_end) - INTERVAL '1 year')::date",
                   "DATE(a.ytd_end, 'start of year', '-1 year')")
        sql = swap(sql, "DATE_TRUNC('year', a.ytd_end)::date",
                   "DATE(a.ytd_end, 'start of year')")
        # SQLite shifts Feb-29 backward a year to Mar-01, while PostgreSQL clamps to Feb-28.
        sql = swap(sql, "(a.ytd_end - INTERVAL '1 year')::date",
                   "(CASE WHEN SUBSTR(a.ytd_end, 6, 5) = '02-29' "
                   "THEN DATE(a.ytd_end, '-1 year', '-1 day') "
                   "ELSE DATE(a.ytd_end, '-1 year') END)")
        sql = swap(sql, "pr.ytd_end + 1", "DATE(pr.ytd_end, '+1 day')", 3)
        sql = swap(sql, "pr.prior_ytd_end + 1",
                   "DATE(pr.prior_ytd_end, '+1 day')", 2)
    if n == 85:
        sql = swap(sql, "MAX(o.OrderDate)::date", "DATE(MAX(o.OrderDate))")
        sql = swap(sql, "s.OrderDate - s.previous_order_date",
                   "CAST(julianday(s.OrderDate) - julianday(s.previous_order_date) AS INTEGER)", 2)
        sql = swap(sql, "(b.last_day - INTERVAL '1 year')::date + 1",
                   "DATE((CASE WHEN SUBSTR(b.last_day, 6, 5) = '02-29' "
                   "THEN DATE(b.last_day, '-1 year', '-1 day') "
                   "ELSE DATE(b.last_day, '-1 year') END), '+1 day')")
    if n == 86:
        # SQLite cannot use DISTINCT with STRING_AGG's explicit separator;
        # comma-containing payment type values are outside the bounded fixtures.
        sql = swap(sql, "STRING_AGG(DISTINCT cl.PaymentType, ', ')",
                   "REPLACE(GROUP_CONCAT(DISTINCT cl.PaymentType), ',', ', ')")
    for unsupported in ("::date", "::numeric", "INTERVAL '", "DATE_TRUNC(",
                        "STRING_AGG(", "PERCENTILE_CONT(", "ROLLUP ("):
        assert unsupported not in sql, f"unadapted dialect feature {n}: {unsupported}"
    return sql

def run(n, sql, rows, expected, label):
    db = sqlite3.connect(":memory:")
    try:
        for definition in DDL[n]:
            db.execute("CREATE TABLE " + definition)
        for table, table_rows in rows.items():
            if table_rows:
                db.executemany("INSERT INTO " + table + " VALUES (" +
                               ",".join("?" for _ in table_rows[0]) + ")", table_rows)
        actual = db.execute(sql).fetchall()
        assert actual == expected, f"Q{n} {label}: actual={actual!r} expected={expected!r}"
        print(f"PASS Q{n} {label}: {len(actual)} rows")
    finally:
        db.close()

def q81():
    return [
        ({"Orders":[(1,"2023-01-10",100),(2,"2023-03-01",200),
                    (3,"2024-01-10",150),(4,"2024-02-29",150)]},
         [("2024-01-01","2024-02-29","2023-01-01","2023-02-28",2,300,1,100,200.0)],
         "archived leap-day illustration"),
        ({"Orders":[(1,"2025-01-01",100),(2,"2025-07-10",150),
                    (3,"2025-07-11",1000),(4,"2026-01-01",200),
                    (5,"2026-07-10",300)]},
         [("2026-01-01","2026-07-10","2025-01-01","2025-07-10",2,500,2,250,100.0)],
         "independent YTD upper-bound exclusion"),
    ]

def q82():
    return [
        ({"Category":[(1,"Audio"),(2,"Home")],
          "Products":[(101,1),(102,2)],
          "Orders":[(1,10,"2026-01-01")],
          "OrderDetails":[(1,1,101,2),(2,1,102,1)]},
         [(10,"Audio",2,66.67)], "archived illustration"),
        ({"Category":[(1,"Alpha"),(2,"Beta")],
          "Products":[(101,1),(102,2),(103,999)],
          "Orders":[(1,10,"2026-01-01"),(2,10,"2026-01-02"),
                    (4,20,"2026-01-03")],
          "OrderDetails":[(1,1,101,5),(2,1,102,2),(3,2,102,3),
                          (4,4,103,3),(5,4,101,1)]},
         [(10,"Beta",5,50.0),(20,"Unmapped",3,75.0)],
         "independent order-count tie-break and unmapped category"),
    ]

def q85():
    return [
        ({"Orders":[(1,10,"2025-01-01",100),(2,10,"2025-07-01",80),
                    (3,20,"2025-06-01",50),(4,20,"2025-07-01",60)]},
         [(10,"2025-01-01","2025-07-01",181,80)],
         "archived illustration"),
        ({"Orders":[(1,10,"2024-12-31",100),(2,10,"2025-07-01",80),
                    (3,10,"2026-01-01",200),(4,10,"2026-07-01",300),
                    (5,30,"2026-01-01",60),(6,30,"2026-06-30",70),
                    (7,40,None,900)]},
         [(10,"2025-07-01","2026-01-01",184,200),
          (30,"2026-01-01","2026-06-30",180,70),
          (10,"2026-01-01","2026-07-01",181,300)],
         "independent 180-day inclusive, repeated win-back, lookback cutoff"),
    ]

KEY_STATUS_ORDER = [
    "Exact match", "Discount 5%", "Discount 10%", "Discount 12%",
    "Discount 15%", "Other shortfall", "Header above lines",
    "Header zero or NULL", "Header without lines",
    "Lines without header", "Lines with NULL OrderID",
]
SOURCE_STATUS_ORDER = [
    "Lines with NULL OrderID", "Lines without header", "Header without lines",
    "Header zero or NULL", "Exact match", "Discount 5%",
    "Discount 10%", "Discount 12%", "Discount 15%",
    "Other shortfall", "Header above lines",
]

def q86():
    sample_rows = {"Products":[(101,10)], "OrderDetails":[(1,1,101,2)],
                   "Payments":[(10,"Card")], "Orders":[(1,10,20)]}
    sample = [(s, int(s=="Exact match"), 20 if s=="Exact match" else 0,
               20 if s=="Exact match" else 0, 0,
               "Card" if s=="Exact match" else None) for s in KEY_STATUS_ORDER]
    varied_rows = {
        "Products":[(101,10)],
        "Payments":[(10,"Card"),(20,"Cash")],
        "Orders":[(1,10,100),(2,10,90),(3,10,0),(4,20,120),
                  (5,20,10),(6,20,200)],
        "OrderDetails":[(1,1,101,10),(2,2,101,10),(3,3,101,1),
                        (4,4,101,10),(5,5,101,2),
                        (6,999,101,3),(7,None,101,4)],
    }
    by_status = {
        "Exact match":(1,100,100,0,"Card"),
        "Discount 10%":(1,90,100,10,"Card"),
        "Other shortfall":(1,10,20,10,"Cash"),
        "Header above lines":(1,120,100,20,"Cash"),
        "Header zero or NULL":(1,0,10,10,"Card"),
        "Header without lines":(1,200,0,200,"Cash"),
        "Lines without header":(1,0,30,30,None),
        "Lines with NULL OrderID":(0,0,40,40,None),
    }
    varied = [(s, *by_status.get(s,(0,0,0,0,None))) for s in KEY_STATUS_ORDER]
    return [(sample_rows,sample,"archived row-values illustration (not source ordering)"),
            (varied_rows,varied,"independent 8-status cases (not source ordering)")]

def main():
    assert sqlite3.sqlite_version_info >= (3,39,0), "SQLite FULL OUTER JOIN required"
    assert git_blob(KEY) == KEY_SHA, "archived supplied-key blob changed"
    key = KEY.read_text(encoding="utf-8")
    extracted = {}
    for n,(rel,pin) in SOURCES.items():
        path = BASE / rel
        assert git_blob(path) == pin, f"Q{n} original source blob changed"
        source = path.read_text(encoding="utf-8")
        for marker in (f"# PNP Q{n:03d}.", "NOT SOLVED YET",
                       "### Sample input and expected output",
                       "## Schema", "## Official solution", "Pending"):
            assert marker in source, f"Q{n} missing source marker {marker}"
        extracted[n] = extract(key,n)
        print(f"INSPECTED Q{n}: source SHA pinned; supplied-key excerpt isolated; learner pending")
    # These are source-level risks, not independently executed contract failures.
    assert "GROUP BY cat.CategoryName, p.Sub_Category" in extracted[83]
    assert "o.ShipDate IS NULL" in extracted[84]
    assert "VALUES (1, 'Exact match')" in extracted[86]
    assert "ARRAY_AGG" in extracted[87]
    assert "CROSS JOIN LATERAL" in extracted[88]

    for n,fixture in ((81,q81),(82,q82),(85,q85),(86,q86)):
        adapted = sqlite_key(n, extracted[n])
        for rows,expected,label in fixture():
            run(n,adapted,rows,expected,label)
    assert KEY_STATUS_ORDER != SOURCE_STATUS_ORDER
    assert extracted[86].index("VALUES (1, 'Exact match')") < extracted[86].index("(11, 'Lines with NULL OrderID')")
    print("KNOWN Q086 SOURCE-ORDER CONTRACT FAILURE: supplied key returns Exact match first, "
          "but source requires Lines with NULL OrderID first. 11 statuses are returned; "
          "row values only are regression-tested.")
    print("PARTIAL audit: eight statements/keys inspected; four extracted keys replayed "
          "on four archived illustrations plus four independent synthetic groups. "
          "Q083/Q084/Q087/Q088 not executed. Provider grading, native PostgreSQL, "
          "full original dataset and independent learner mastery unverified.")

if __name__ == "__main__":
    main()
