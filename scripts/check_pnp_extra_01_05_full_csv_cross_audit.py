#!/usr/bin/env python3
"""Independent full original Commerce v2 CSV X001-X005 cross-check (PARTIAL).

Compare earlier auditor-authored SQLite queries to a separate Python oracle over
ALL original rows. This is not an official answer (the README says none exists),
not a learner attempt, and not native PostgreSQL/MySQL parity. Read-only.
"""
import collections
import csv
import hashlib
import math
import sqlite3
import statistics
import unittest
from pathlib import Path

from check_pnp_extra_01_05_sources import SQL, inspect as inspect_question_sources

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ("99. Reference Materials/Original Mastery Snapshot/"
                 "1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/"
                 "Source Materials/PrepNPlaced_SQL_100_v2")
DATA = SOURCE / "data"
PINS = {
    "Products.csv": ("61c11d7f65434aa38a90ef581acb1256515c3d7d", 22088),
    "OrderDetails.csv": ("ddd2fc4d61ca4cc17a49e3dd19440716f07416ae", 168567),
    "Category.csv": ("b355b85ddce21146a792aa1bde71b153d1b7d42b", 12),
    "load_dataset_v2.sql": ("3787743252d29268c67c491d6a2eb47c1757c35b", None),
}
SCHEMA = """
CREATE TABLE Products(ProductID INTEGER,Product TEXT,CategoryID INTEGER,
                      Sub_Category TEXT,Brand TEXT,Rating REAL);
CREATE TABLE Category(CategoryID INTEGER,CategoryName TEXT);
CREATE TABLE OrderDetails(OrderDetailID INTEGER,ProductID INTEGER,Quantity INTEGER);
"""

def blob_sha(b):
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def nullable_text(s):
    return s if s != "" else None

def nullable_int(s):
    return int(s) if s not in (None, "") else None

def nullable_float(s):
    return float(s) if s not in (None, "") else None

def load_rows(name):
    with (DATA / name).open("r", encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        assert rd.fieldnames is not None, name
        expected_fields = {
            "Products.csv": ("ProductID", "Product", "CategoryID", "Sub_Category", "Brand", "Rating"),
            "OrderDetails.csv": ("OrderDetailID", "ProductID", "Quantity"),
            "Category.csv": ("CategoryID", "CategoryName"),
        }[name]
        assert set(expected_fields).issubset(set(rd.fieldnames)), (name, rd.fieldnames)
        rows = list(rd)
        assert all(None not in row for row in rows), name
    assert len(rows) == PINS[name][1], (name, len(rows), PINS[name][1])
    return rows

class OriginalFullDatasetCrossAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = {name: (DATA / name).read_bytes() for name in PINS}
        cls.source_rows = {n: load_rows(n) for n in ("Products.csv", "OrderDetails.csv", "Category.csv")}
        cls.products = [
            (int(r["ProductID"]), r["Product"], nullable_int(r["CategoryID"]),
             nullable_text(r["Sub_Category"]), nullable_text(r["Brand"]),
             nullable_float(r["Rating"]))
            for r in cls.source_rows["Products.csv"]
        ]
        cls.details = [
            (int(r["OrderDetailID"]), nullable_int(r["ProductID"]),
             nullable_int(r["Quantity"]))
            for r in cls.source_rows["OrderDetails.csv"]
        ]
        cls.categories = [
            (int(r["CategoryID"]), r["CategoryName"])
            for r in cls.source_rows["Category.csv"]
        ]
        cls.db = sqlite3.connect(":memory:")
        cls.db.executescript(SCHEMA)
        cls.db.executemany("INSERT INTO Products VALUES(?,?,?,?,?,?)", cls.products)
        cls.db.executemany("INSERT INTO OrderDetails VALUES(?,?,?)", cls.details)
        cls.db.executemany("INSERT INTO Category VALUES(?,?)", cls.categories)
        cls.by_id = {p[0]:p for p in cls.products}
        cls.category_map = dict(cls.categories)
        cls.units = collections.Counter()
        cls.referenced = set()
        for _, pid, qty in cls.details:
            cls.referenced.add(pid)
            if pid is not None:
                cls.units[pid] += qty or 0
        cls.results = {sid:cls.db.execute(query).fetchall() for sid,query in SQL.items()}
    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_immutable_source_blobs_and_readme_counts(self):
        inspect_question_sources()  # also checks five original X prompts + original README hashes
        for name,(pin,n) in PINS.items():
            with self.subTest(name=name):
                self.assertEqual(blob_sha(self.raw[name]), pin)
                if n is not None:
                    self.assertEqual(len(self.source_rows[name]),n)
        self.assertEqual(len(self.by_id),len(self.products),"duplicate ProductID not modeled by prior reviewer SQL")
        self.assertEqual(len(self.category_map),len(self.categories),"duplicate CategoryID would multiply join rows")
        self.assertIn("CREATE TABLE Products",self.raw["load_dataset_v2.sql"].decode())
        print("PASS pinned 5 X sources + README + 4 raw loader/CSV blobs; row counts 22088/168567/12")

    def test_02_x001_all_real_category_rated_shares(self):
        groups=collections.defaultdict(lambda:[0,0])
        for pid,product,cat,sub,brand,rating in self.products:
            groups[cat][0]+=1
            groups[cat][1]+=rating is not None
        rows={cat:(label,n,k,pct) for cat,label,n,k,pct in self.results["X001"]}
        self.assertEqual(set(rows),set(groups))
        for cat,(n,k) in groups.items():
            label,count,rated,percent=rows[cat]
            self.assertEqual(label,self.category_map.get(cat))
            self.assertEqual((count,rated),(n,k))
            self.assertLessEqual(abs(percent-100.0*k/n),0.0051)
        self.assertEqual(sum(g[0] for g in groups.values()),len(self.products))
        print("PASS X001 full CSV category/NULL-key shares:",len(groups),"groups")

    def test_03_x002_all_real_brand_rated_thresholds(self):
        groups=collections.defaultdict(list)
        for _,_,cat,sub,brand,rating in self.products:
            if rating is not None:
                groups[brand].append(rating)
        expected={b:vals for b,vals in groups.items() if len(vals)>=20}
        actual={brand:(count,avg) for brand,count,avg in self.results["X002"]}
        self.assertEqual(set(actual),set(expected))
        for brand,ratings in expected.items():
            count,avg=actual[brand]
            self.assertEqual(count,len(ratings))
            self.assertLessEqual(abs(avg-math.fsum(ratings)/len(ratings)),0.0051)
        self.assertTrue(all(len(v)>=20 for v in expected.values()))
        print("PASS X002 full CSV rated-count threshold:",len(expected),"eligible brand groups")

    def test_04_x003_full_subcategory_rating_vs_median_units(self):
        by_sub=collections.defaultdict(list)
        for pid,name,cat,sub,brand,rating in self.products:
            by_sub[sub].append((pid,name,rating,self.units[pid]))
        expected={}
        for sub,items in by_sub.items():
            ratings=[r for _,_,r,_ in items if r is not None]
            if not ratings:
                continue
            avg=sum(ratings)/len(ratings)  # separate direct Python reference
            med=statistics.median(units for _,_,_,units in items)
            for pid,name,rating,units in items:
                if rating is not None and rating>avg and units<med:
                    expected[pid]=(name,rating,units)
        actual={pid:(name,rating,units) for pid,name,rating,units in self.results["X003"]}
        self.assertEqual(set(actual),set(expected))
        for pid in expected:
            self.assertEqual(actual[pid],expected[pid])
        print("PASS X003 full CSV medians incl unsold products:",len(by_sub),"subcategories,",len(actual),"qualified products")

    def test_05_x004_all_real_rating_bands_and_zero_sales(self):
        bands=collections.defaultdict(list)
        for pid,name,cat,sub,brand,rating in self.products:
            b=("unrated" if rating is None else
               "below 3" if rating<3 else
               "3 to below 4" if rating<4 else "4 and above")
            bands[b].append(self.units[pid])
        actual={name:(count,avg) for name,count,avg in self.results["X004"]}
        self.assertEqual(set(actual),set(bands))
        for band,values in bands.items():
            n,avg=actual[band]
            self.assertEqual(n,len(values))
            self.assertLessEqual(abs(avg-sum(values)/len(values)),0.0051)
        self.assertEqual(sum(len(v) for v in bands.values()),len(self.products))
        print("PASS X004 full CSV per-product band denominator:", {b:len(v) for b,v in sorted(bands.items())})

    def test_06_x005_all_real_rated_never_ordered(self):
        expected={pid:(name,rating) for pid,name,cat,sub,brand,rating in self.products
                  if rating is not None and pid not in self.referenced}
        actual={pid:(name,rating) for pid,name,rating in self.results["X005"]}
        self.assertEqual(actual,expected)
        print("PASS X005 full CSV rated product anti-join:",len(actual),"rated products without details")

    def test_07_cross_question_denominators_and_integrity(self):
        total_rated=sum(r is not None for *_,r in self.products)
        self.assertEqual(sum(row[3] for row in self.results["X001"]),total_rated)
        self.assertEqual(sum(row[2] for row in self.results["X001"]),len(self.products))
        self.assertEqual(sum(row[1] for row in self.results["X004"]),len(self.products))
        per_brand=collections.Counter(p[4] for p in self.products if p[5] is not None)
        self.assertEqual(sum(row[1] for row in self.results["X002"]),
                         sum(n for n in per_brand.values() if n>=20))
        self.assertLessEqual(len(self.results["X005"]),total_rated)
        self.assertTrue(all(row[2] is not None for row in self.results["X003"]))
        missing_details=sum(pid not in self.by_id for _,pid,_ in self.details)
        print("PASS X cross-denominator controls; full CSV orphan detail rows:",missing_details,
              "(not silently rewritten or interpreted as official dataset-cleanliness proof)")

if __name__=="__main__":
    unittest.main(verbosity=2)
