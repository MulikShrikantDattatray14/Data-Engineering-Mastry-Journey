#!/usr/bin/env python3
"""Bounded original-blob-pinned Q16-20 historical SQL pairs; no provider grading."""
import hashlib
import re
import sqlite3
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/"
    "1. SQL Mastery/1. SQL Mastry/"
    "1.Bosscoder Academy - foundational notes and Assignments/A. PNP easy"
)
PINS = {
    16: ("16.Product catalog with category and supplier.md", "f5617c7dd481e4a406aab58b6675c36d9658ae70"),
    17: ("17.Split contact names into first and last.md", "3fdd67a67c3e91ae64cf4a693b21ef96adfe2950"),
    18: ("18.Vowel-initial companies with uppercased country.md", "9dfbee2deb4a517e052b547cf6e8fded35235e83"),
    19: ("19.Customer counts per region with NULLs labeled.md", "105db98e7af41ed952872499ea651a50b38da050"),
    20: ("20.Build employee display names.md", "399a64aecb99b9b51a34d9ee347ebab4c9c0fa15"),
}

def original(n):
    filename, pin = PINS[n]
    raw = (BASE / filename).read_bytes()
    actual = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert actual == pin, (filename, actual, pin)
    doc = raw.decode("utf-8")
    assert "Solved (recorded): 2026-10-13" in doc, filename
    return doc

def sql(n, heading):
    doc = original(n)
    section = re.search(r"^## " + re.escape(heading) + r"\s*\n(.*?)(?=^## |\Z)", doc, re.M | re.S)
    assert section, (n, heading, "missing heading")
    fence = re.search(r"\x60{3}sql\s*\n(.*?)\n\x60{3}", section.group(1), re.S)
    assert fence, (n, heading, "missing SQL block")
    return fence.group(1).strip()

def replay(n, schema, inserts, case_sensitive_like=False):
    con = sqlite3.connect(":memory:")
    try:
        if case_sensitive_like:
            con.execute("PRAGMA case_sensitive_like=ON")
        con.executescript(schema)
        for insert, values in inserts:
            con.executemany(insert, values)
        mine = con.execute(sql(n, "My solution — SQLite")).fetchall()
        attributed = con.execute(sql(n, "Official solution")).fetchall()
        return mine, attributed
    finally:
        con.close()

class HistoricalEasySixteenThroughTwenty(unittest.TestCase):
    def test_01_original_git_blob_identity_all_three_archived_sql_sections(self):
        for n in PINS:
            with self.subTest(question=n):
                self.assertIn("## Question and image", original(n))
                for heading in ("My solution — SQLite", "My solution — SQL Server", "Official solution"):
                    self.assertTrue(sql(n, heading))

    def test_02_q16_source_illustration_three_product_catalog(self):
        a,b = replay(16,
            "CREATE TABLE Categories(CategoryID INT,CategoryName TEXT);"
            "CREATE TABLE Suppliers(SupplierID INT,CompanyName TEXT);"
            "CREATE TABLE Products(ProductID INT,ProductName TEXT,CategoryID INT,SupplierID INT);", [
            ("INSERT INTO Categories VALUES (?,?)", [(1,"Beverages"),(2,"Food")]),
            ("INSERT INTO Suppliers VALUES (?,?)", [(1,"Harbor Supply"),(2,"Hill Supply")]),
            ("INSERT INTO Products VALUES (?,?,?,?)", [(1,"Tea",1,2),(2,"Bread",2,1),(3,"Coffee",1,1)])])
        expected=[("Bread","Food","Harbor Supply"),("Coffee","Beverages","Harbor Supply"),("Tea","Beverages","Hill Supply")]
        self.assertEqual((a,b),(expected,expected))

    def test_03_q16_missing_fk_and_nonunique_supplier_key_violate_one_row_premise(self):
        a,b = replay(16,
            "CREATE TABLE Categories(CategoryID INT,CategoryName TEXT);"
            "CREATE TABLE Suppliers(SupplierID INT,CompanyName TEXT);"
            "CREATE TABLE Products(ProductID INT,ProductName TEXT,CategoryID INT,SupplierID INT);", [
            ("INSERT INTO Categories VALUES (?,?)", [(1,"Food")]),
            ("INSERT INTO Suppliers VALUES (?,?)", [(1,"Supply A"),(1,"Supply B")]),
            ("INSERT INTO Products VALUES (?,?,?,?)", [(1,"Good",1,1),(2,"No category",999,1),(3,"No supplier",1,88)])])
        expected=[("Good","Food","Supply A"),("Good","Food","Supply B")]
        self.assertEqual((a,b),(expected,expected))
        self.assertEqual(len(a),2)

    def test_04_q17_source_split_example_and_customer_id_order(self):
        a,b = replay(17, "CREATE TABLE Customers(CustomerID TEXT,ContactName TEXT);", [
            ("INSERT INTO Customers VALUES (?,?)", [("C","Liam Fox"),("A","Maria Anders"),("B","Ana Diaz")])])
        expected=[("A","Maria Anders","Maria","Anders"),("B","Ana Diaz","Ana","Diaz"),("C","Liam Fox","Liam","Fox")]
        self.assertEqual((a,b),(expected,expected))

    def test_05_q17_missing_or_multiple_separator_are_outside_prompt_guarantee(self):
        a,b = replay(17, "CREATE TABLE Customers(CustomerID TEXT,ContactName TEXT);", [
            ("INSERT INTO Customers VALUES (?,?)", [("A","Ada"),("B","Mary Ann Smith"),("C",None)])])
        expected=[("A","Ada","","Ada"),("B","Mary Ann Smith","Mary","Ann Smith"),("C",None,None,None)]
        self.assertEqual((a,b),(expected,expected))

    def test_06_q18_source_ascii_default_like_illustration(self):
        a,b = replay(18,"CREATE TABLE Customers(CustomerID TEXT,CompanyName TEXT,Country TEXT);", [
            ("INSERT INTO Customers VALUES (?,?,?)", [("A","Acme","India"),("E","elm Works","France"),("I","Indigo","Brazil"),("O","oak Shop","Canada"),("U","Union Goods","Germany"),("B","Beta","Spain")])])
        expected=[("Acme","INDIA"),("Indigo","BRAZIL"),("Union Goods","GERMANY"),("elm Works","FRANCE"),("oak Shop","CANADA")]
        self.assertEqual((a,b),(expected,expected))

    def test_07_q18_case_sensitive_like_exposes_trailing_space_pattern_bug(self):
        a,b = replay(18,"CREATE TABLE Customers(CompanyName TEXT,Country TEXT);", [
            ("INSERT INTO Customers VALUES (?,?)", [("elm Works","France"),("Union Goods","Germany"),("Epsilon","Canada"),("umbrella","Italy"),("Acme","India")])],case_sensitive_like=True)
        self.assertEqual(a,[("Acme","INDIA"),("Epsilon","CANADA"),("umbrella","ITALY")])
        self.assertEqual(b,[("Acme","INDIA"),("Epsilon","CANADA"),("Union Goods","GERMANY"),("elm Works","FRANCE"),("umbrella","ITALY")])
        self.assertNotEqual(a,b)

    def test_08_q19_source_null_unknown_coalescing_example(self):
        a,b = replay(19,"CREATE TABLE Customers(CustomerID TEXT,Region TEXT);", [
            ("INSERT INTO Customers VALUES (?,?)", [("A","East"),("B",None),("C","West"),("D","East"),("E",None),("F","Unknown")])])
        expected=[("Unknown",3),("East",2),("West",1)]
        self.assertEqual((a,b),(expected,expected))

    def test_09_q19_nullable_customer_id_changes_count_but_not_region_group(self):
        a,b = replay(19,"CREATE TABLE Customers(CustomerID TEXT,Region TEXT);", [
            ("INSERT INTO Customers VALUES (?,?)", [("1","East"),("2",None),(None,None),("4","Unknown"),("5","")])])
        self.assertEqual(a,[("Unknown",2),("",1),("East",1)])
        self.assertEqual(b,[("Unknown",3),("",1),("East",1)])
        self.assertNotEqual(a,b)

    def test_10_q20_source_employee_display_name_example(self):
        a,b = replay(20,"CREATE TABLE Employees(EmployeeID INT,TitleOfCourtesy TEXT,FirstName TEXT,LastName TEXT);", [
            ("INSERT INTO Employees VALUES (?,?,?,?)", [(3,"Dr.","Mira","Patel"),(1,"Ms.","Nancy","Davolio"),(2,"Mr.","Andrew","Fuller")])])
        expected=[(1,"Ms. Nancy Davolio"),(2,"Mr. Andrew Fuller"),(3,"Dr. Mira Patel")]
        self.assertEqual((a,b),(expected,expected))

    def test_11_q20_null_propagation_and_whitespace_source_input_boundaries(self):
        a,b = replay(20,"CREATE TABLE Employees(EmployeeID INT,TitleOfCourtesy TEXT,FirstName TEXT,LastName TEXT);", [
            ("INSERT INTO Employees VALUES (?,?,?,?)", [(1,"Ms.","Nancy","Davolio"),(2,None,"Ana","Lee"),(3,"Dr.","","Mills"),(4,"Mr."," John","Smith")])])
        expected=[(1,"Ms. Nancy Davolio"),(2,None),(3,"Dr.  Mills"),(4,"Mr.  John Smith")]
        self.assertEqual((a,b),(expected,expected))

if __name__=="__main__":
    unittest.main(verbosity=2)
