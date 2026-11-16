#!/usr/bin/env python3
"""Independent PNP Q087/Q088 original-key native PostgreSQL + full Commerce v2 audit.

Read-only immutable source verification; synthetic cases plus ALL eight original
Commerce v2 CSVs. Executes archived supplier-attributed SQL unchanged in
disposable PostgreSQL 16 TEMP tables. No provider grading or learner mastery.
No individual customer/record rows printed or copied into the repository.
"""
import csv
import hashlib
import os
import re
import unittest
from collections import Counter
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice")
SOURCE_ROOT = BASE / "Source Materials/PrepNPlaced_SQL_100_v2"
KEY = SOURCE_ROOT / "sql/all_100_solutions.sql"
Q87 = BASE / ("14. Data Quality and Deduplication/"
              "P087. Referential integrity audit across all seven relationships.md")
Q88 = BASE / "14. Data Quality and Deduplication/P088. Date validity audit.md"
PINS = {
    KEY: "7912c8e676621c513e0b635a40c6ee299404676e",
    Q87: "28bed1fe1c7d2e6c4c92e68f6a619a6fb2780e02",
    Q88: "52c73f3594668d77afbe679b25a84997fb3ced59",
    SOURCE_ROOT / "data/load_dataset_v2.sql": "3787743252d29268c67c491d6a2eb47c1757c35b",
}
FILES = {
    "Suppliers": ("6a1eb9e7b570d301714bb049a928261afcabcc20", 18),
    "Products": ("61c11d7f65434aa38a90ef581acb1256515c3d7d", 22088),
    "Category": ("b355b85ddce21146a792aa1bde71b153d1b7d42b", 12),
    "Shippers": ("6c2a327c240c5454e9ed7f22d142529238563493", 10),
    "Payments": ("5986647cdc1fc087d84774de1bca875235d19f1c", 10),
    "Customers": ("bbb2995f0758fe5012197b8c71d897c1aca5c65f", 5072),
    "Orders": ("307acc9ad2f85a79d7637a7958ffd62f2a8fa594", 46438),
    "OrderDetails": ("ddd2fc4d61ca4cc17a49e3dd19440716f07416ae", 168567),
}
# Only columns needed by the unchanged supplier SQL; preserves loader's date policy.
COLUMNS = {
    "Suppliers": ("SupplierID",),
    "Products": ("ProductID", "CategoryID"),
    "Category": ("CategoryID",),
    "Shippers": ("ShipperID",),
    "Payments": ("PaymentID",),
    "Customers": ("CustomerID", "DateEntered"),
    "Orders": ("OrderID", "CustomerID", "PaymentID", "ShipperID",
               "OrderDate", "ShipDate", "DeliveryDate"),
    "OrderDetails": ("OrderDetailID", "OrderID", "ProductID", "SupplierID"),
}
DDL = {
    "Suppliers": "SupplierID int PRIMARY KEY",
    "Products": "ProductID int PRIMARY KEY, CategoryID int",
    "Category": "CategoryID int PRIMARY KEY",
    "Shippers": "ShipperID int PRIMARY KEY",
    "Payments": "PaymentID int PRIMARY KEY",
    "Customers": "CustomerID int PRIMARY KEY, DateEntered date",
    "Orders": ("OrderID int PRIMARY KEY, CustomerID int, PaymentID int, "
               "ShipperID int, OrderDate date, ShipDate date, DeliveryDate date"),
    "OrderDetails": ("OrderDetailID int PRIMARY KEY, OrderID int, "
                     "ProductID int, SupplierID int"),
}
RELATIONS = (
    ("Products.CategoryID -> Category", "Products", "CategoryID", "Category"),
    ("Orders.CustomerID -> Customers", "Orders", "CustomerID", "Customers"),
    ("Orders.PaymentID -> Payments", "Orders", "PaymentID", "Payments"),
    ("Orders.ShipperID -> Shippers", "Orders", "ShipperID", "Shippers"),
    ("OrderDetails.OrderID -> Orders", "OrderDetails", "OrderID", "Orders"),
    ("OrderDetails.ProductID -> Products", "OrderDetails", "ProductID", "Products"),
    ("OrderDetails.SupplierID -> Suppliers", "OrderDetails", "SupplierID", "Suppliers"),
)
RULES = (
    ("Order date missing", "error"),
    ("Shipped before ordered", "error"),
    ("Delivered before shipped", "error"),
    ("Delivered before ordered", "error"),
    ("Delivered with no ship date", "error"),
    ("Ordered before customer sign-up", "warning"),
    ("Delivered after 7-day promise", "warning"),
    ("Not shipped 14+ days after order", "warning"),
    ("Customer sign-up date missing", "warning"),
)


def blob(path):
    raw = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def key_sql(n):
    original = KEY.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^-- Q" + str(n) + r"\. [^\n]*\n(.*?)(?=^-- Q\d+\.|\Z)", original)
    assert match, "original Q" + str(n) + " key missing"
    sql = match.group(1).strip()
    assert sql.startswith("WITH ") and sql.endswith(";")
    return sql


def connect():
    return psycopg.connect(
        host=os.environ.get("PGHOST", "127.0.0.1"),
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ.get("PGDATABASE", "audit"),
        user=os.environ.get("PGUSER", "audit"),
        password=os.environ.get("PGPASSWORD", "audit"),
        autocommit=True)


def prepared(raw, column):
    if raw in ("", None):
        return None
    if column in ("OrderDate", "ShipDate", "DeliveryDate"):
        return datetime.strptime(raw, "%d-%m-%Y").date()
    if column == "DateEntered":
        # Exact three source loader patterns; unmatched text becomes SQL NULL.
        for pattern, fmt in (
            (r"\d{4}/\d{2}/\d{2}", "%Y/%m/%d"),
            (r"\d{2}-\d{2}-\d{4}", "%d-%m-%Y"),
            (r"\d{4}-\d{2}-\d{2}", "%Y-%m-%d"),
        ):
            if re.fullmatch(pattern, raw):
                return datetime.strptime(raw, fmt).date()
        return None
    return int(raw)


def original_csv():
    parsed = {}
    for name, (pin, count) in FILES.items():
        path = SOURCE_ROOT / "data" / (name + ".csv")
        assert blob(path) == pin, "original CSV drift: " + name
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == count, (name, len(rows), count)
        assert all(set(COLUMNS[name]).issubset(row) for row in rows)
        parsed[name] = [tuple(prepared(row[c], c) for c in COLUMNS[name]) for row in rows]
    return parsed


def run_native(fixtures, q):
    with connect() as conn, conn.transaction():
        for name, definition in DDL.items():
            conn.execute("CREATE TEMP TABLE " + name + " (" + definition + ") ON COMMIT DROP")
        for name, rows in fixtures.items():
            if not rows:
                continue
            # COPY is much faster than 250k single-row INSERTs, and all writes
            # are to ephemeral private TEMP tables inside this transaction.
            with conn.cursor() as cur:
                with cur.copy("COPY " + name + " (" + ", ".join(COLUMNS[name]) +
                              ") FROM STDIN") as copy:
                    for row in rows:
                        copy.write_row(row)
        return conn.execute(key_sql(q)).fetchall()


def expected87(src):
    keys = {name: {row[0] for row in src.get(name, ())} for name in FILES}
    out = []
    for label, child, col, parent in RELATIONS:
        ix = COLUMNS[child].index(col)
        vals = [r[ix] for r in src.get(child, ())]
        missing = [x for x in vals if x is not None and x not in keys[parent]]
        sample = ", ".join(map(str, sorted(set(missing))[:5])) if missing else None
        out.append((label, len(vals), sum(v is None for v in vals), len(missing), sample))
    return out


def expected88(src):
    customers = dict(src.get("Customers", ()))
    orders = src.get("Orders", ())
    order_ix = {n:i for i,n in enumerate(COLUMNS["Orders"])}
    max_date = max((row[order_ix["OrderDate"]] for row in orders
                    if row[order_ix["OrderDate"]] is not None), default=None)
    violated = [[] for _ in RULES]
    for row in orders:
        d = dict(zip(COLUMNS["Orders"], row))
        oid, ordered, shipped, delivered = (
            d["OrderID"], d["OrderDate"], d["ShipDate"], d["DeliveryDate"])
        joined = customers.get(d["CustomerID"])
        flags = (
            ordered is None,
            ordered is not None and shipped is not None and shipped < ordered,
            shipped is not None and delivered is not None and delivered < shipped,
            ordered is not None and delivered is not None and delivered < ordered,
            delivered is not None and shipped is None,
            ordered is not None and joined is not None and ordered < joined,
            ordered is not None and delivered is not None and (delivered - ordered).days > 7,
            ordered is not None and max_date is not None and
                shipped is None and delivered is None and (max_date - ordered).days >= 14,
        )
        for i, flag in enumerate(flags):
            if flag:
                violated[i].append(oid)
    for cid, dateentered in src.get("Customers", ()):
        if dateentered is None:
            violated[8].append(cid)
    result = []
    for i,(label,severity) in enumerate(RULES):
        checked = len(orders) if i < 8 else len(customers)
        # The original supplied SQL omits groups with zero checked records,
        # although the question explicitly requests nine zero-filled rows.
        if not checked:
            continue
        hits = violated[i]
        pct = (Decimal(100) * Decimal(len(hits)) / Decimal(checked)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)
        result.append((i + 1, label, severity, checked, len(hits), pct,
                       sorted(hits)[:5] if hits else None))
    return result


def sample87():
    return {
        "Category": [(1,)], "Products": [(101,1)], "Customers": [(10,None)],
        "Payments": [(20,)], "Shippers": [(30,)],
        "Orders": [(100,10,20,30,None,None,None)],
        "OrderDetails": [(1,100,101,999)], "Suppliers": [(7,)]
    }


def sample88():
    from datetime import date
    return {
        "Customers": [(10, date(2026,1,1))],
        "Orders": [
            (1,10,None,None,date(2026,1,2),date(2026,1,1),date(2026,1,5)),
            (2,10,None,None,date(2026,1,20),None,None)]
    }


class PNPQ087Q088OriginalFullSourceAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for p,sha in PINS.items():
            assert blob(p) == sha, "original immutable source drift: " + str(p)
        for p,n in ((Q87,87),(Q88,88)):
            s = p.read_text(encoding="utf-8")
            for mark in (f"# PNP Q{n:03d}.", "NOT SOLVED YET",
                         "## Official solution\n\nPending", "## Schema",
                         "### Sample input and expected output"):
                assert mark in s, (n,mark)
        for term in ("ARRAY_AGG(DISTINCT ck.fk_value", "FILTER (WHERE ck.fk_value"):
            assert term in key_sql(87), term
        for term in ("CROSS JOIN LATERAL", "o.DeliveryDate::date - o.OrderDate::date > 7",
                     "a.max_order_date::date - o.OrderDate::date >= 14"):
            assert term in key_sql(88), term

    def test_01_native_postgresql_16(self):
        with connect() as conn:
            v = int(conn.execute("SHOW server_version_num").fetchone()[0])
        self.assertTrue(160000 <= v < 170000, v)

    def test_02_immutable_source_ledger_and_historical_pending(self):
        self.assertEqual(len(PINS), 4)
        self.assertEqual(len(FILES), 8)
        self.assertEqual(len(RELATIONS), 7)
        self.assertEqual(len(RULES), 9)

    def test_03_q087_original_seven_relationship_illustration(self):
        rows = run_native(sample87(), 87)
        self.assertEqual(rows, expected87(sample87()))
        self.assertEqual(rows[-1], ("OrderDetails.SupplierID -> Suppliers", 1, 0, 1, "999"))

    def test_04_q087_duplicates_nulls_and_orphan_samples(self):
        fixture = sample87()
        fixture["Products"] += [(102,None), (103,99)]
        fixture["Orders"] += [(101,None,999,None,None,None,None)]
        fixture["OrderDetails"] += [(2,777,999,900),(3,777,999,900),
                                   (4,778,None,901),(5,779,101,902),
                                   (6,780,101,903),(7,781,101,904),
                                   (8,782,101,905)]
        self.assertEqual(run_native(fixture,87), expected87(fixture))
        self.assertEqual(run_native(fixture,87)[-1][-1], "900, 901, 902, 903, 904")

    def test_05_q087_all_empty_still_seven_zero_rows(self):
        self.assertEqual(run_native({},87), expected87({}))
        self.assertEqual(len(run_native({},87)),7)

    def test_06_q088_original_nine_rule_illustration(self):
        rows = run_native(sample88(),88)
        self.assertEqual(rows, expected88(sample88()))
        self.assertEqual(rows[1][4:6], (1,Decimal("50.00")))

    def test_07_q088_independent_all_nine_rule_types(self):
        from datetime import date
        fixture = {
            "Customers":[(10,date(2026,1,10)),(11,None)],
            "Orders":[
                (1,10,None,None,None,None,None),
                (2,10,None,None,date(2026,1,1),date(2025,12,31),date(2026,1,20)),
                (3,11,None,None,date(2026,1,20),None,date(2026,1,21)),
                (4,10,None,None,date(2026,2,20),None,None),
                (5,10,None,None,date(2026,2,1),None,None),
                (6,10,None,None,date(2026,1,19),date(2026,1,22),date(2026,1,18))]
        }
        rows = run_native(fixture,88)
        self.assertEqual(rows,expected88(fixture))
        self.assertEqual([r[4] for r in rows],[1]*9)

    def test_08_q088_seven_day_boundary_is_warning_only_after_day_eight(self):
        from datetime import date
        fixture = {"Customers":[(1,date(2025,1,1))],
                   "Orders":[(1,1,None,None,date(2026,1,1),date(2026,1,1),date(2026,1,8)),
                             (2,1,None,None,date(2026,1,1),date(2026,1,1),date(2026,1,9))]}
        rows = run_native(fixture,88)
        self.assertEqual(rows,expected88(fixture))
        self.assertEqual(rows[6][4:],(1,Decimal("50.00"),[2]))

    def test_09_q088_fourteen_day_anchor_is_latest_order_not_wall_clock(self):
        from datetime import date
        fixture = {"Customers":[(1,date(2026,1,1))],
                   "Orders":[(1,1,None,None,date(2026,1,1),None,None),
                             (2,1,None,None,date(2026,1,14),None,None),
                             (3,1,None,None,date(2026,1,15),None,None)]}
        rows = run_native(fixture,88)
        self.assertEqual(rows,expected88(fixture))
        self.assertEqual(rows[7][4:],(1,Decimal("33.33"),[1]))

    def test_10_q088_missing_customer_does_not_invent_signup_violation(self):
        from datetime import date
        fixture = {"Orders":[(1,999,None,None,date(2026,1,1),None,None)]}
        rows = run_native(fixture,88)
        self.assertEqual(rows,expected88(fixture))
        self.assertEqual(rows[5][4],0)
        self.assertEqual(len(rows),8)  # rule 9 disappears when no Customers

    def test_11_q088_empty_orders_customers_contradicts_nine_zero_rule_contract(self):
        rows = run_native({},88)
        self.assertEqual(rows,[])
        self.assertNotEqual(len(rows),9)  # Known supplier-query gap, not reviewer PASS of task

    def test_12_actual_eight_immutable_CSVs_versus_independent_q087_counts(self):
        data = original_csv()
        self.assertEqual(run_native(data,87), expected87(data))
        self.assertEqual(len(run_native(sample87(),87)),7)
        self.__class__.whole_data = data
        self.__class__.whole_q87_ok = True
        print("Q087 full 8-CSV original key: seven rows vs independent reference counts PASS")

    def test_13_actual_eight_immutable_CSVs_versus_independent_q088_rules(self):
        data = getattr(self.__class__,"whole_data",None)
        if data is None:
            data = original_csv()
        rows = run_native(data,88)
        reference = expected88(data)
        self.assertEqual(rows,reference)
        self.assertEqual(len(rows),9)
        print("Q088 full 8-CSV original key: nine rules vs independent date reference PASS")

    def test_14_original_claims_not_provider_grading_or_learner_completion(self):
        for q in (Q87,Q88):
            s = q.read_text(encoding="utf-8")
            self.assertIn("## My solution — SQLite\n\nPending.",s)
            self.assertIn("## My solution — SQL Server\n\nPending.",s)
            self.assertIn("## Official solution\n\nPending",s)


if __name__=="__main__":
    unittest.main(verbosity=2)
