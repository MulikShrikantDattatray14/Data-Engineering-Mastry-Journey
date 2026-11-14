#!/usr/bin/env python3
"""Read-only audit of archived Python mentorship fixture files. No official grades."""
import csv, json, subprocess, unittest
from pathlib import Path
from datetime import date
from decimal import Decimal, InvalidOperation
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[1]
ARCH = Path("99. Reference Materials/Original Mastery Snapshot/2. Python Mastry")
DATA = ROOT / ARCH / "python_de_dataset"
PINS = {
 "python_de_dataset/employees.csv": "08d2330cc9dab1530d6ff8e896211f7867438e4b",
 "python_de_dataset/logins.csv": "e5669aa40eb3a08569355351eaa1c4f6e35a556d",
 "python_de_dataset/order_items.csv": "072bd904c499ce5547049eb8ba0fc2dd4c071cd0",
 "python_de_dataset/orders.csv": "2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2",
 "python_de_dataset/orders_dirty.csv": "e36bedf1e6b9b5ef2582b007440c92ccf9fda83a",
 "python_de_dataset/products.csv": "c5beff443efbdc3cd73376cd721334fa0bf43d8b",
 "python_de_dataset/snapshot_day1.csv": "12043a47a749ea54c89ae2becb509e22c991b399",
 "python_de_dataset/snapshot_day2.csv": "3966cea9b4f16dd9a7ac0da6d4beff201a60c7a1",
 "python_de_dataset/customers.json": "d6125fce237e7f7e3193667946d1eb117cd19db0",
 "2. Python Foundations/09. Files CSV JSON JSON Lines and paths.md": "54e71278f26aa0d2847363e4860cbac98b1caaa7",
 "5. Coding Round Patterns/11. Validation and snapshot differences.md": "aa3ae4081c26bf16ea221a28c552535be53abefe",
 "6. Python for Data Engineering/04. Build an idempotent ETL pipeline.md": "fc859b44748d06318f2d0bdb4ae36266715253e7",
 "6. Python for Data Engineering/05. Testing and data quality.md": "05b4ff35d2666ef5908237686f2a517dd718301a",
}
SCHEMAS = {
 "employees.csv": ("emp_id,name,dept,manager_id,salary,hire_date",9),
 "logins.csv": ("user_id,login_date",12),
 "order_items.csv": ("order_id,product_id,qty,unit_price",24),
 "orders.csv": ("order_id,customer_id,order_date,status,amount",15),
 "orders_dirty.csv": ("order_id,customer_id,order_date,status,amount",7),
 "products.csv": ("product_id,product_name,category,price",8),
 "snapshot_day1.csv": ("customer_id,name,city",8),
 "snapshot_day2.csv": ("customer_id,name,city",8),
}
def read_csv(name):
    with (DATA/name).open(encoding="utf-8",newline="") as f:
        r=csv.DictReader(f)
        assert r.fieldnames==SCHEMAS[name][0].split(","),name
        values=list(r)
    assert all(None not in item and all(v is not None for v in item.values())
               for item in values),name
    return values

def errors(row):
    result=[]
    if not row["customer_id"].strip(): result.append("customer_missing")
    try: date.fromisoformat(row["order_date"])
    except ValueError: result.append("invalid_date")
    if row["status"].strip().lower() not in ("delivered","cancelled","returned"):
        result.append("status_not_allowed")
    try:
        if Decimal(row["amount"])<=0: result.append("amount_nonpositive")
    except InvalidOperation: result.append("amount_nonnumeric")
    return result

class CrossSourceAudit(unittest.TestCase):
    def test_01_all_thirteen_original_source_git_hashes(self):
        for path,expected in PINS.items():
            with self.subTest(path=path):
                got=subprocess.check_output(["git","hash-object","--",str(ARCH/path)],
                                             cwd=ROOT,text=True).strip()
                self.assertEqual(got,expected)
    def test_02_all_eight_csv_headers_and_row_counts(self):
        for name,(_,n) in SCHEMAS.items():
            with self.subTest(source=name): self.assertEqual(len(read_csv(name)),n)
        with (DATA/"customers.json").open(encoding="utf-8") as f:
            customers=json.load(f)
        self.assertEqual(len(customers),8)
        self.assertEqual(len(set(x["customer_id"] for x in customers)),8)
    def test_03_all_15_original_order_amounts_reconcile_with_24_lines(self):
        headers=read_csv("orders.csv"); lines=read_csv("order_items.csv")
        sums=defaultdict(lambda:Decimal(0))
        for r in lines: sums[r["order_id"]]+=Decimal(r["unit_price"])*int(r["qty"])
        self.assertEqual(set(sums),set(r["order_id"] for r in headers))
        for h in headers:
            with self.subTest(order=h["order_id"]):
                self.assertEqual(sums[h["order_id"]],Decimal(h["amount"]))
        self.assertEqual(sum(sums.values()),Decimal("23268"))
    def test_04_original_cross_file_foreign_keys_and_manager_graph(self):
        with (DATA/"customers.json").open(encoding="utf-8") as f:
            customers=set(str(r["customer_id"]) for r in json.load(f))
        orders=read_csv("orders.csv"); lines=read_csv("order_items.csv")
        self.assertEqual(len(set(o["order_id"] for o in orders)),len(orders))
        self.assertTrue(set(o["customer_id"] for o in orders)<=customers)
        self.assertTrue(set(r["order_id"] for r in lines)<=set(o["order_id"] for o in orders))
        self.assertTrue(set(r["product_id"] for r in lines)<=
                        set(p["product_id"] for p in read_csv("products.csv")))
        staff={r["emp_id"]:r for r in read_csv("employees.csv")}
        self.assertEqual([i for i,r in staff.items() if not r["manager_id"]],["1"])
        for emp in staff:
            seen={emp}; current=staff[emp]
            while current["manager_id"]:
                parent=current["manager_id"]
                self.assertIn(parent,staff)
                self.assertNotIn(parent,seen)
                seen.add(parent); current=staff[parent]
    def test_05_original_status_dates_and_two_distinct_amount_totals(self):
        orders=read_csv("orders.csv")
        self.assertEqual(Counter(r["status"] for r in orders),
                         {"delivered":12,"cancelled":2,"returned":1})
        for r in orders:
            date.fromisoformat(r["order_date"])
            self.assertGreater(Decimal(r["amount"]),0)
        delivered=sum((Decimal(r["amount"]) for r in orders
                       if r["status"]=="delivered"),Decimal(0))
        self.assertEqual(delivered,Decimal("18972"))
        # No official finance recognition policy established by these figures.
    def test_06_seven_original_dirty_rows_and_normalized_acceptance(self):
        dirty=read_csv("orders_dirty.csv")
        self.assertEqual({r["order_id"]:errors(r) for r in dirty},{
            "116":["amount_nonpositive"],"117":["customer_missing"],
            "118":["invalid_date"],"119":["status_not_allowed"],
            "120":["amount_nonnumeric"],"121":[],"122":[]})
        self.assertEqual(dirty[-1]["status"].strip().lower(),"delivered")
    def test_07_two_original_snapshots_one_add_remove_two_changes(self):
        before=read_csv("snapshot_day1.csv"); after=read_csv("snapshot_day2.csv")
        a={r["customer_id"]:r for r in before}
        b={r["customer_id"]:r for r in after}
        self.assertEqual(len(a),len(before)); self.assertEqual(len(b),len(after))
        self.assertEqual(set(b)-set(a),{"9"})
        self.assertEqual(set(a)-set(b),{"8"})
        changed={k:(a[k]["city"],b[k]["city"]) for k in a.keys()&b.keys()
                 if a[k]!=b[k]}
        self.assertEqual(changed,{"4":("Bengaluru","Pune"),
                                  "6":("","Chennai")})
    def test_08_four_source_companions_are_same_read_printed_contracts(self):
        def lesson(rel): return (ROOT/ARCH/rel).read_text(encoding="utf-8")
        p33=lesson("2. Python Foundations/09. Files CSV JSON JSON Lines and paths.md")
        p68=lesson("5. Coding Round Patterns/11. Validation and snapshot differences.md")
        p72=lesson("6. Python for Data Engineering/04. Build an idempotent ETL pipeline.md")
        p73=lesson("6. Python for Data Engineering/05. Testing and data quality.md")
        self.assertIn("101 delivered 1198.00",p33)
        self.assertIn("good: [('121', 'delivered'), ('122', 'delivered')]",p68)
        self.assertIn("inserts: ['9'] deletes: ['8']",p68)
        self.assertIn("table_rows=2",p72)
        self.assertIn("orders_dirty.csv -> FAIL",p73)
        self.assertIn("order_date",p73) # p73 only asks learner to add date validation.
    def test_09_reviewer_only_join_price_and_multifault_counterexamples(self):
        source=next(r for r in read_csv("orders.csv") if r["order_id"]=="101")
        lines=[r for r in read_csv("order_items.csv") if r["order_id"]=="101"]
        self.assertEqual(len(lines),2)
        self.assertEqual(Decimal(source["amount"])*len(lines),Decimal("2396"))
        self.assertEqual(sum(Decimal(r["unit_price"])*int(r["qty"]) for r in lines),
                         Decimal("1198"))
        simulated_price={"1":Decimal("999"),"5":Decimal("399")}
        self.assertEqual(sum(simulated_price[r["product_id"]]*int(r["qty"])
                             for r in lines),Decimal("1398"))
        fake={"order_id":"999","customer_id":"","order_date":"2025-02-30",
              "status":" shipped ","amount":"abc"}
        self.assertEqual(errors(fake),["customer_missing","invalid_date",
                                       "status_not_allowed","amount_nonnumeric"])
        original=read_csv("snapshot_day1.csv")
        duplicate=[*original,{**original[0],"city":"REVIEWER_ONLY"}]
        self.assertEqual(len(duplicate),9)
        self.assertEqual(len({r["customer_id"]:r for r in duplicate}),8)

if __name__=="__main__": unittest.main(verbosity=2)
