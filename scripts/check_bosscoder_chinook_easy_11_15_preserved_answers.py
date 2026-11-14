#!/usr/bin/env python3
"""Source-pinned historical easy Q11-Q15; bounded SQLite only, not provider grading."""
import hashlib
import re
import sqlite3
import unittest
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/"
    "1.Bosscoder Academy - foundational notes and Assignments/A. PNP easy"
)
PINS = {
    11: ("11.Show each customer's assigned support rep.md", "91deb496495d7067269f76fbe58642bc0364582f"),
    12: ("12.Total revenue by product category.md", "4b7e2994a1f12834f20aefffde5551e9e65ae066"),
    13: ("13.Top 10 products by units sold.md", "7b7bdf97f3cd01912b116fd9df04401e975c3b49"),
    14: ("14.Freight cost summary by shipping country.md", "e18bd6e015d9d0c9fcfe5d8e87a95d62b5456422"),
    15: ("15.Order roster with customer and employee names.md", "df09e79d5850e76e1c8774d71e355ce797fec748"),
}

def original(n):
    name, pin = PINS[n]
    raw = (BASE / name).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert blob == pin, (name, blob)
    doc = raw.decode("utf-8")
    assert "Solved (recorded): 2026-10-13" in doc, name
    return doc

def sql(n, heading):
    doc = original(n)
    section = re.search(r"^## " + re.escape(heading) + r"\s*\n(.*?)(?=^## |\Z)", doc, re.M | re.S)
    assert section, (n, heading, "missing heading")
    fence = re.search(r"`{3}sql\s*\n(.*?)\n`{3}", section.group(1), re.S)
    assert fence, (n, heading, "missing SQL block")
    return fence.group(1).strip()

def replay(n, create, inserts):
    db = sqlite3.connect(":memory:")
    try:
        db.executescript(create)
        for insert, rows in inserts:
            db.executemany(insert, rows)
        mine = db.execute(sql(n, "My solution — SQLite")).fetchall()
        attributed = db.execute(sql(n, "Official solution")).fetchall()
        return mine, attributed
    finally:
        db.close()

class HistoricalEasyElevenThroughFifteen(unittest.TestCase):
    def test_01_five_original_git_blobs_and_three_saved_sql_sections(self):
        for n in PINS:
            with self.subTest(question=n):
                self.assertIn("## Question and image", original(n))
                for heading in ("My solution — SQLite", "My solution — SQL Server", "Official solution"):
                    self.assertTrue(sql(n, heading))

    def test_02_q11_example_one_customer_one_rep_and_sorted_names(self):
        actual = replay(11,
            "CREATE TABLE Customer(CustomerId INT,FirstName TEXT,LastName TEXT,SupportRepId INT);"
            "CREATE TABLE Employee(EmployeeId INT,FirstName TEXT,LastName TEXT);", [
            ("INSERT INTO Customer VALUES (?,?,?,?)", [(1,"Zoe","Clark",2),(2,"Ana","Diaz",1),(3,"Ben","Ali",2)]),
            ("INSERT INTO Employee VALUES (?,?,?)", [(1,"Erin","Cole"),(2,"Liam","Gray")])])
        expected = [("Ana Diaz","Erin Cole"),("Ben Ali","Liam Gray"),("Zoe Clark","Liam Gray")]
        self.assertEqual(actual, (expected, expected))

    def test_03_q11_missing_rep_and_duplicate_names_are_boundary_not_full_roster(self):
        mine, key = replay(11,
            "CREATE TABLE Customer(CustomerId INT,FirstName TEXT,LastName TEXT,SupportRepId INT);"
            "CREATE TABLE Employee(EmployeeId INT,FirstName TEXT,LastName TEXT);", [
            ("INSERT INTO Customer VALUES (?,?,?,?)", [(1,"Sam","Lee",1),(2,"Sam","Lee",1),(3,"Orphan","Missing",99),(4,"Null","Rep",None)]),
            ("INSERT INTO Employee VALUES (?,?,?)", [(1,"Kira","Jones")])])
        self.assertEqual(Counter(mine), Counter([("Sam Lee","Kira Jones")]*2))
        self.assertEqual(Counter(mine), Counter(key))
        self.assertEqual(len(mine), 2)  # Synthetic input has four customers.

    def test_04_q12_original_illustration_net_discount_revenue(self):
        mine, key = replay(12,
            'CREATE TABLE "Order Details"(OrderID INT,ProductID INT,UnitPrice REAL,Quantity INT,Discount REAL);'
            'CREATE TABLE Products(ProductID INT,ProductName TEXT,CategoryID INT);'
            'CREATE TABLE Categories(CategoryID INT,CategoryName TEXT);', [
            ("INSERT INTO Categories VALUES (?,?)", [(1,"Beverages"),(2,"Food")]),
            ("INSERT INTO Products VALUES (?,?,?)", [(1,"Tea",1),(2,"Coffee",1),(3,"Bread",2)]),
            ('INSERT INTO "Order Details" VALUES (?,?,?,?,?)', [(101,1,10,2,0.1),(102,1,10,3,0),(102,2,20,1,0.25),(103,3,5,4,0)])])
        expected = [("Beverages",63.0),("Food",20.0)]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)

    def test_05_q12_distinct_category_ids_with_same_name_disagree(self):
        mine, key = replay(12,
            'CREATE TABLE "Order Details"(OrderID INT,ProductID INT,UnitPrice REAL,Quantity INT,Discount REAL);'
            'CREATE TABLE Products(ProductID INT,CategoryID INT);'
            'CREATE TABLE Categories(CategoryID INT,CategoryName TEXT);', [
            ("INSERT INTO Categories VALUES (?,?)", [(1,"Shared"),(2,"Shared")]),
            ("INSERT INTO Products VALUES (?,?)", [(10,1),(20,2)]),
            ('INSERT INTO "Order Details" VALUES (?,?,?,?,?)', [(101,10,10,1,0),(102,20,20,1,0)])])
        self.assertEqual(Counter(mine), Counter([("Shared",20.0),("Shared",10.0)]))
        self.assertEqual(key, [("Shared",30.0)])
        # CategoryID uniqueness alone does not ensure CategoryName uniqueness.

    def test_06_q13_original_illustration_top_ten_and_tied_tenth(self):
        mine, key = replay(13,
            'CREATE TABLE "Order Details"(OrderID INT,ProductID INT,Quantity INT);'
            'CREATE TABLE Products(ProductID INT,ProductName TEXT);', [
            ("INSERT INTO Products VALUES (?,?)", list(enumerate(["Tea","Coffee","Bread","Milk","Rice","Beans","Juice","Pasta","Salt","Sugar","Water"],1))),
            ('INSERT INTO "Order Details" VALUES (?,?,?)', [(101,1,15),(102,1,5),(103,2,18),(104,3,16),
            (105,4,14),(106,5,12),(107,6,10),(108,7,8),(109,8,6),(110,9,4),(111,10,2),(112,11,2)])])
        expected = [("Tea",20),("Coffee",18),("Bread",16),("Milk",14),("Rice",12),
                    ("Beans",10),("Juice",8),("Pasta",6),("Salt",4),("Sugar",2)]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)

    def test_07_q13_same_product_name_different_ids_not_equivalent(self):
        mine, key = replay(13,
            'CREATE TABLE "Order Details"(OrderID INT,ProductID INT,Quantity INT);'
            'CREATE TABLE Products(ProductID INT,ProductName TEXT);', [
            ("INSERT INTO Products VALUES (?,?)", [(1,"Widget"),(2,"Widget"),(3,"Solo")]),
            ('INSERT INTO "Order Details" VALUES (?,?,?)', [(1,1,4),(2,2,6),(3,3,1)])])
        self.assertEqual(mine, [("Widget",6),("Widget",4),("Solo",1)])
        self.assertEqual(key, [("Widget",10),("Solo",1)])

    def test_08_q14_original_example_counts_sums_averages_and_tie_sort(self):
        mine, key = replay(14, "CREATE TABLE Orders(OrderID INT,ShipCountry TEXT,Freight REAL);", [
            ("INSERT INTO Orders VALUES (?,?,?)", [(1,"Brazil",10.5),(2,"Brazil",20.0),(3,"Canada",30.5),(4,"India",5.0)])])
        expected = [("Brazil",2,30.5,15.25),("Canada",1,30.5,30.5),("India",1,5.0,5.0)]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)

    def test_09_q14_null_freight_denominator_diverges(self):
        mine, key = replay(14, "CREATE TABLE Orders(OrderID INT,ShipCountry TEXT,Freight REAL);", [
            ("INSERT INTO Orders VALUES (?,?,?)", [(1,"Brazil",10.0),(2,"Brazil",None),(3,"Brazil",20.0),(4,"India",None)])])
        self.assertEqual(mine, [("Brazil",3,30.0,10.0),("India",1,None,None)])
        self.assertEqual(key, [("Brazil",3,30.0,15.0),("India",1,None,None)])

    def test_10_q14_integer_affinity_division_changes_average(self):
        mine, key = replay(14, "CREATE TABLE Orders(OrderID INT,ShipCountry TEXT,Freight INTEGER);", [
            ("INSERT INTO Orders VALUES (?,?,?)", [(1,"USA",1),(2,"USA",2)])])
        self.assertEqual(mine, [("USA",2,3.0,1.0)])
        self.assertEqual(key, [("USA",2,3.0,1.5)])
        # Native Northwind Freight datatype may differ: this is an adversarial SQLite fixture.

    def test_11_q15_original_example_order_roster(self):
        mine, key = replay(15,
            'CREATE TABLE Customers(CustomerID TEXT,CompanyName TEXT);'
            'CREATE TABLE Orders(OrderID INT,CustomerID TEXT,EmployeeID INT);'
            'CREATE TABLE Employees(EmployeeID INT,FirstName TEXT,LastName TEXT);', [
            ("INSERT INTO Customers VALUES (?,?)", [("ALFA","Alpha Foods"),("BETA","Beta Stores")]),
            ("INSERT INTO Orders VALUES (?,?,?)", [(103,"ALFA",2),(101,"BETA",1),(102,"ALFA",1)]),
            ("INSERT INTO Employees VALUES (?,?,?)", [(1,"Nancy","Davolio"),(2,"Andrew","Fuller")])])
        expected = [(101,"Beta Stores","Nancy Davolio"),(102,"Alpha Foods","Nancy Davolio"),(103,"Alpha Foods","Andrew Fuller")]
        self.assertEqual(mine, expected)
        self.assertEqual(key, expected)

    def test_12_q15_orphan_orders_dropped_by_both_inner_joins(self):
        mine, key = replay(15,
            'CREATE TABLE Customers(CustomerID TEXT,CompanyName TEXT);'
            'CREATE TABLE Orders(OrderID INT,CustomerID TEXT,EmployeeID INT);'
            'CREATE TABLE Employees(EmployeeID INT,FirstName TEXT,LastName TEXT);', [
            ("INSERT INTO Customers VALUES (?,?)", [("A","Alpha")]),
            ("INSERT INTO Orders VALUES (?,?,?)", [(1,"A",5),(2,"B",5),(3,"A",999)]),
            ("INSERT INTO Employees VALUES (?,?,?)", [(5,"N","Z")])])
        self.assertEqual(mine, [(1,"Alpha","N Z")])
        self.assertEqual(key, mine)
        self.assertEqual(len(mine), 1)  # Three input orders, only one satisfies both joins.

if __name__ == "__main__":
    unittest.main(verbosity=2)
