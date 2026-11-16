#!/usr/bin/env python3
"""Read-only whole-CSV source/instructor cross-audit for PNP Commerce v2.

Inspect the original eight full CSVs, original loader and original instructor
planted-issues key. Assertions explicitly compare many published claims with
independent row-level calculations; they do not grade learner work or certify
the provider's 100 answers, source PDF visuals, or redistribution rights.
No records/PII are printed: output contains aggregate counts and source hashes.
"""
import collections
import csv
from datetime import datetime, timedelta
import hashlib
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
               "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/"
               "Source Materials/PrepNPlaced_SQL_100_v2")
DATA = BASE / "data"
PINS = {
    "Suppliers.csv": ("6a1eb9e7b570d301714bb049a928261afcabcc20", 18),
    "Products.csv": ("61c11d7f65434aa38a90ef581acb1256515c3d7d", 22088),
    "Category.csv": ("b355b85ddce21146a792aa1bde71b153d1b7d42b", 12),
    "Shippers.csv": ("6c2a327c240c5454e9ed7f22d142529238563493", 10),
    "Payments.csv": ("5986647cdc1fc087d84774de1bca875235d19f1c", 10),
    "Customers.csv": ("bbb2995f0758fe5012197b8c71d897c1aca5c65f", 5072),
    "Orders.csv": ("307acc9ad2f85a79d7637a7958ffd62f2a8fa594", 46438),
    "OrderDetails.csv": ("ddd2fc4d61ca4cc17a49e3dd19440716f07416ae", 168567),
}
OTHER_PINS = {
    "README.md": (BASE / "README.md", "eb75fac446057899effefcb10029ff2048674ea2"),
    "load_dataset_v2.sql": (DATA / "load_dataset_v2.sql",
                            "3787743252d29268c67c491d6a2eb47c1757c35b"),
    "planted_issues.md": (BASE / "instructor/planted_issues.md",
                           "6f4da61474880372a6e269b17ffc7958350541e6"),
}
HEADERS = {
    "Suppliers.csv": "SupplierID,CompanyName,Address,City,State,PostalCode,Country,Phone,Email",
    "Products.csv": "ProductID,Product,CategoryID,Sub_Category,Brand,Sale_Price,Market_Price,Type,Rating",
    "Category.csv": "CategoryID,CategoryName,Active",
    "Shippers.csv": "ShipperID,CompanyName,Phone",
    "Payments.csv": "PaymentID,PaymentType,Allowed",
    "Customers.csv": "CustomerID,FirstName,LastName,City,State,Country,PostalCode,Phone,Email,DateEntered",
    "Orders.csv": "OrderID,CustomerID,PaymentID,OrderDate,ShipperID,Total_Order_Amount,ShipDate,DeliveryDate",
    "OrderDetails.csv": "OrderDetailID,OrderID,ProductID,Quantity,SupplierID",
}
PK = {"Suppliers.csv": "SupplierID", "Products.csv": "ProductID",
      "Category.csv": "CategoryID", "Shippers.csv": "ShipperID",
      "Payments.csv": "PaymentID", "Customers.csv": "CustomerID",
      "Orders.csv": "OrderID", "OrderDetails.csv": "OrderDetailID"}


def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def ident(s):
    return int(s) if s not in ("", None) else None


def number(s):
    return float(s) if s not in ("", None) else None


def day(s):
    return datetime.strptime(s, "%d-%m-%Y").date() if s else None


class CommerceV2FullOriginalDataAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = {}
        cls.raw = {}
        for name, (pin, size) in PINS.items():
            raw = (DATA / name).read_bytes()
            assert blob_sha(raw) == pin, f"original {name} source byte drift"
            reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
            assert reader.fieldnames == HEADERS[name].split(","), name
            rows = list(reader)
            assert len(rows) == size, (name, len(rows), size)
            assert all(None not in row for row in rows), f"{name} malformed CSV width"
            cls.records[name] = rows
            cls.raw[name] = raw
        for name, (path, pin) in OTHER_PINS.items():
            assert blob_sha(path.read_bytes()) == pin, f"{name} source drift"
        cls.s = cls.records["Suppliers.csv"]
        cls.p = cls.records["Products.csv"]
        cls.c = cls.records["Category.csv"]
        cls.sh = cls.records["Shippers.csv"]
        cls.pay = cls.records["Payments.csv"]
        cls.cu = cls.records["Customers.csv"]
        cls.o = cls.records["Orders.csv"]
        cls.d = cls.records["OrderDetails.csv"]
        cls.keys = {name: {ident(row[PK[name]]) for row in rows}
                    for name, rows in cls.records.items()}

    def test_01_all_eight_complete_original_csv_and_three_primary_metadata_blobs(self):
        self.assertEqual(len(PINS), 8)
        for name, (pin, expected_rows) in PINS.items():
            with self.subTest(name=name):
                self.assertEqual(blob_sha(self.raw[name]), pin)
                self.assertEqual(len(self.records[name]), expected_rows)
                self.assertEqual(len(self.keys[name]), expected_rows,
                                 "duplicate source primary IDs")
        for name, (path, pin) in OTHER_PINS.items():
            with self.subTest(name=name):
                self.assertEqual(blob_sha(path.read_bytes()), pin)
        loader = OTHER_PINS["load_dataset_v2.sql"][0].read_text()
        for name in PINS:
            self.assertIn("FROM '" + name + "'", loader)
        original_readme = OTHER_PINS["README.md"][0].read_text()
        self.assertIn("The 8 tables", original_readme)
        print("8/8 complete original CSVs; 11/11 source blob pins; all IDs unique")

    def test_02_category_actual_missing_reference_and_unlisted_active_flags(self):
        category = self.keys["Category.csv"]
        missing = [r for r in self.p if ident(r["CategoryID"]) not in category]
        self.assertEqual(len(missing), 40)
        self.assertEqual({ident(r["CategoryID"]) for r in missing}, {5012})
        self.assertEqual(sum(ident(r["CategoryID"]) == 5013 for r in self.p), 0)
        flags = collections.Counter(r["Active"] for r in self.c)
        self.assertEqual(sum(flags.values()), 12)
        self.assertEqual(set(flags), {"Yes", "No", "Y", "1", "yes", "Yes ", "0"})
        print("Category: 40 products orphan to absent 5012; 5013 no products; raw flag variants:", sorted(flags.items()))

    def test_03_products_issues_direct_full_catalogue_checks(self):
        p = self.p
        sale_below = sum(number(r["Market_Price"]) is not None and
                         number(r["Sale_Price"]) is not None and
                         number(r["Market_Price"]) < number(r["Sale_Price"])
                         for r in p)
        market_zero = sum(number(r["Market_Price"]) == 0 for r in p)
        sale_missing = sum(r["Sale_Price"] == "" for r in p)
        brand_blank = sum(not r["Brand"].strip() for r in p)
        trailing_name = sum(r["Product"] != r["Product"].strip() for r in p)
        rating_missing = sum(r["Rating"] == "" for r in p)
        nonzero_below = sum(number(r["Market_Price"]) is not None and
                            number(r["Market_Price"]) > 0 and
                            number(r["Sale_Price"]) is not None and
                            number(r["Market_Price"]) < number(r["Sale_Price"])
                            for r in p)
        actual = (sale_below, market_zero, sale_missing,
                  brand_blank, trailing_name, rating_missing)
        # Instructor calls 12 rows "Market_Price below Sale_Price" and separately
        # 6 rows price=0. But its literal WHERE market < sale returns 18,
        # because those six zero-market rows overlap; count nonzero separately.
        self.assertEqual(actual, (18, 6, 4, 10, 8, 4360))
        self.assertEqual(nonzero_below, 12)
        print("Products actual market<sale 18 (including six zero markets); nonzero market<sale 12; other issue counts:", actual)

    def test_04_suppliers_duplicate_emails_countries_and_unused_source_ids(self):
        by_name = collections.Counter(r["CompanyName"].strip().casefold() for r in self.s)
        duplicate_extras = sum(n - 1 for n in by_name.values() if n > 1)
        self.assertEqual(duplicate_extras, 1)
        self.assertEqual([ident(r["SupplierID"]) for r in self.s
                          if not r["Email"]], [4])
        self.assertEqual([ident(r["SupplierID"]) for r in self.s
                          if r["Email"] and "." not in r["Email"].split("@")[-1]], [16])
        self.assertEqual({r["Country"] for r in self.s if "india" in r["Country"].lower()},
                         {"India", "INDIA", "india "})
        used = {ident(r["SupplierID"]) for r in self.d if r["SupplierID"]}
        self.assertIn(17, self.keys["Suppliers.csv"] - used)
        print("Suppliers: one duplicate normalized company name, one missing email, one missing domain suffix, supplier 17 unused")

    def test_05_payment_allowlist_original_rows_and_actual_orders(self):
        method_by_id = {ident(r["PaymentID"]): r for r in self.pay}
        self.assertEqual(collections.Counter(r["Allowed"] for r in self.pay),
                         collections.Counter({"Yes": 7, "No": 2, "N": 1}))
        self.assertEqual(method_by_id[8]["PaymentType"], "Pay Later")
        self.assertEqual(method_by_id[8]["Allowed"], "No")
        self.assertEqual(method_by_id[10]["Allowed"], "N")
        switched_off = sum(ident(r["PaymentID"]) == 8 and
                           day(r["OrderDate"]) is not None and
                           day(r["OrderDate"]) >= datetime(2025, 7, 1).date()
                           for r in self.o)
        self.assertEqual(switched_off, 12)
        print("Payments: 7 Yes, 2 No, 1 N; Pay Later on/after 2025-07-01 orders:", switched_off)

    def test_06_shippers_unused_and_actual_orphan_count(self):
        actual_ids = {ident(r["ShipperID"]) for r in self.o if r["ShipperID"]}
        never_used = self.keys["Shippers.csv"] - actual_ids
        self.assertEqual(never_used, {9, 10})
        missing = sum(not r["ShipperID"] for r in self.o)
        orphan = [r for r in self.o if r["ShipperID"] and
                  ident(r["ShipperID"]) not in self.keys["Shippers.csv"]]
        self.assertEqual((missing, len(orphan)), (25, 3))
        self.assertEqual({ident(r["ShipperID"]) for r in orphan}, {11})
        print("Shippers: unused source IDs 9/10; 25 NULL and 3 orphan order shipper references (ID 11)")

    def test_07_customer_email_gaps_and_no_order_accounts(self):
        raw_space = sum(" " in r["Email"] for r in self.cu)
        emails_with_space = sum(" " in r["Email"].strip() for r in self.cu)
        ordered = {ident(r["CustomerID"]) for r in self.o if r["CustomerID"]}
        never_ordered = self.keys["Customers.csv"] - ordered
        norm = collections.Counter(r["Email"].strip().casefold()
                                   for r in self.cu if r["Email"].strip())
        duplicate_groups = sum(v > 1 for v in norm.values())
        duplicate_extras = sum(v - 1 for v in norm.values() if v > 1)
        # WHERE Email LIKE '% %' in source key also counts edge-padding.
        # Distinguish 3 internal-space values from 38 with ANY literal space.
        self.assertEqual((raw_space, emails_with_space), (38, 3))
        self.assertEqual(len(never_ordered), 647)
        print("Customers: 38 raw-space emails, of which 3 have internal spaces; never ordered:", len(never_ordered),
              "normalized-email duplicate groups:", duplicate_groups,
              "extra accounts:", duplicate_extras,
              "(72 instructor label not yet assigned to group-vs-row semantics)")

    def test_08_order_fk_and_header_quality_counts(self):
        count = lambda pred: sum(bool(pred(r)) for r in self.o)
        missing_pay = count(lambda r: not r["PaymentID"])
        missing_ship = count(lambda r: not r["ShipperID"])
        orphan_cust = count(lambda r: r["CustomerID"] and
                            ident(r["CustomerID"]) not in self.keys["Customers.csv"])
        empty_total = count(lambda r: not r["Total_Order_Amount"])
        zero_total = count(lambda r: number(r["Total_Order_Amount"]) == 0)
        actual = missing_pay, missing_ship, orphan_cust, empty_total, zero_total
        self.assertEqual(actual, (20, 25, 8, 5, 4))
        print("Orders: NULL payment, NULL shipper, unknown customer, NULL total, zero total:", actual)

    def test_09_order_lines_actual_unmatched_keys_and_quantities(self):
        bad_order = sum(r["OrderID"] and ident(r["OrderID"]) not in self.keys["Orders.csv"]
                        for r in self.d)
        bad_product = sum(r["ProductID"] and ident(r["ProductID"]) not in self.keys["Products.csv"]
                          for r in self.d)
        bad_supplier = sum(r["SupplierID"] and ident(r["SupplierID"]) not in self.keys["Suppliers.csv"]
                           for r in self.d)
        empty_quantity = sum(not r["Quantity"] for r in self.d)
        zero_quantity = sum(r["Quantity"] == "0" for r in self.d)
        self.assertEqual((bad_order, bad_product, bad_supplier, empty_quantity, zero_quantity),
                         (12, 15, 5, 10, 5))
        used_orders = {ident(r["OrderID"]) for r in self.d if r["OrderID"]}
        no_lines = self.keys["Orders.csv"] - used_orders
        self.assertEqual(len(no_lines), 10)
        print("OrderDetails: orphan order/product/supplier, NULL/zero qty, headers with zero lines:",
              (bad_order, bad_product, bad_supplier, empty_quantity, zero_quantity, len(no_lines)))

    def test_10_actual_shipping_date_contradictions_and_late_unshipped(self):
        shipped_first = sum(bool(day(r["ShipDate"]) and day(r["OrderDate"]) and
                                 day(r["ShipDate"]) < day(r["OrderDate"]))
                            for r in self.o)
        delivered_first = sum(bool(day(r["DeliveryDate"]) and day(r["ShipDate"]) and
                                   day(r["DeliveryDate"]) < day(r["ShipDate"]))
                              for r in self.o)
        delivered_unshipped = sum(r["DeliveryDate"] and not r["ShipDate"] for r in self.o)
        self.assertEqual((shipped_first, delivered_first, delivered_unshipped),
                         (12, 9, 6))
        last_order = max(day(r["OrderDate"]) for r in self.o if r["OrderDate"])
        cutoff = last_order - timedelta(days=14)
        old_unshipped = sum(bool(not r["ShipDate"] and day(r["OrderDate"]) and
                                 day(r["OrderDate"]) <= cutoff) for r in self.o)
        self.assertEqual(old_unshipped, 320)
        print("Orders: ship before order, deliver before ship, deliver without ship, 14-day cutoff unshipped:",
              (shipped_first, delivered_first, delivered_unshipped, old_unshipped))

    def test_11_actual_line_duplicate_grouping_under_instructor_stated_keys(self):
        groups = collections.Counter((r["OrderID"], r["ProductID"],
                                      r["Quantity"], r["SupplierID"]) for r in self.d)
        extra = sum(n - 1 for n in groups.values() if n > 1)
        groups_with_duplicates = sum(n > 1 for n in groups.values())
        self.assertEqual(extra, 60)
        print("OrderDetails exact-field duplicate extra lines:", extra,
              "duplicate groups:", groups_with_duplicates)

    def test_12_independent_instructor_key_scope_and_read_only_disclosure(self):
        key = OTHER_PINS["planted_issues.md"][0].read_text()
        for snippet in ("| Products | CategoryID 5012", "| Orders | ShipperID 11",
                        "| OrderDetails | Lines whose SupplierID",
                        "| Customers | Duplicate accounts:",
                        "| Orders | Duplicate submissions:"):
            self.assertIn(snippet, key)
        self.assertIn("Nothing else is cleaned", OTHER_PINS["load_dataset_v2.sql"][0].read_text())
        self.assertIn("Deliberately messy", OTHER_PINS["README.md"][0].read_text())
        print("Instructor assertions checked independently; no official answer or learner completion credited")


if __name__ == "__main__":
    unittest.main(verbosity=2)
