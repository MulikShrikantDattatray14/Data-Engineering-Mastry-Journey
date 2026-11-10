"""Replay immutable Bosscoder SQL Joins learner records on independent SQLite fixtures.

Evidence tiers: twelve archived source statements/records read and hash-pinned;
ten exact historical SQLite queries run on auditor-synthetic datasets; two
assignments remain explicitly pending. No platform grades or learner credit.
"""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/2. Joins"
PINS = [
    ("1.Sql Combine Two Tables.md", "606ecd9dd3288fabed5f2ba378f44cc44ace8568"),
    ("2.Sql Replace Employee ID With The Unique Identifier.md", "c2aac167cf70456d30bd326a036d0e7d6174091d"),
    ("3.Sql Product Sales Analysis I.md", "b45acc8bcc15268fbe48fe97e15ecf4c4fe66850"),
    ("4.Sql Sales Person.md", "6838deac30e856fb547987b4bfff8ad830b550fe"),
    ("5.Sql Delete Duplicate Emails.md", "39aaeec72fc3c592b3720ecdd25656902afecb7b"),
    ("6.Sql Students And Examinations.md", "533402e26beb665afea81a37b927e3e8cc96b504"),
    ("7.Sql African Cities.md", "a2e2de9c41b0ef72cfa9fa4f9c17121de629af46"),
    ("8.Sql Average Population Each Continent.md", "ed1de8c2f0a4cf8613f3bbb6b2520c91edb6a90b"),
    ("9.Sql The Problem.md", "3e4b7adaeaa6ef160d942ea88b4eaa57b8eee9b1"),
    ("10.Sql Ollivander Inventory.md", "b276ce64c77d4e1fbdf1c5f27179a068aa6b7d44"),
    ("11.Sql Rising Temperature.md", "3f2cabeae85975191d1daea0c14977a1952b55c4"),
    ("12.Sql Seller With No Sales.md", "6d3779e56636dfe19c5684389a964b049d965ae0"),
]

# Each expected result was independently predicted for the constructed fixture.
# Not the original platform dataset, not an Academy-supplied official key.
CASES = {
    1: ("""CREATE TABLE Person(personId INTEGER,lastName TEXT,firstName TEXT);
CREATE TABLE Address(addressId INTEGER,personId INTEGER,city TEXT,state TEXT);
INSERT INTO Person VALUES (1,'Wang','Allen'),(2,'Alice','Bob'),(3,'Ray','Dana');
INSERT INTO Address VALUES (1,2,'New York','NY'),(2,999,'Orphan','XX'),(3,2,'Boston','MA');""",
        [('Allen','Wang',None,None),('Bob','Alice','New York','NY'),('Bob','Alice','Boston','MA'),('Dana','Ray',None,None)]),
    2: ("""CREATE TABLE Employees(id INTEGER,name TEXT);
CREATE TABLE EmployeeUNI(id INTEGER,unique_id INTEGER);
INSERT INTO Employees VALUES (1,'Alice'),(2,'Bob'),(3,'Carol');
INSERT INTO EmployeeUNI VALUES (2,12),(2,13),(3,20);""",
        [(None,'Alice'),(12,'Bob'),(13,'Bob'),(20,'Carol')]),
    3: ("""CREATE TABLE Sales(sale_id INTEGER,product_id INTEGER,year INTEGER,quantity INTEGER,price INTEGER);
CREATE TABLE Product(product_id INTEGER,product_name TEXT);
INSERT INTO Sales VALUES (1,100,2008,10,50),(2,100,2009,1,100),(3,999,2010,3,200);
INSERT INTO Product VALUES (100,'Nokia'),(300,'Unsold');""",
        [('Nokia',2008,50),('Nokia',2009,100),(None,2010,200)]),
    6: ("""CREATE TABLE Students(student_id INTEGER,student_name TEXT);
CREATE TABLE Subjects(subject_name TEXT);
CREATE TABLE Examinations(student_id INTEGER,subject_name TEXT);
INSERT INTO Students VALUES (1,'Ada'),(2,'Bea');
INSERT INTO Subjects VALUES ('Math'),('English');
INSERT INTO Examinations VALUES (1,'Math'),(1,'Math'),(2,'English');""",
        [(1,'Ada','English',0),(1,'Ada','Math',2),(2,'Bea','English',1),(2,'Bea','Math',0)]),
    7: ("""CREATE TABLE CITY(ID INTEGER,NAME TEXT,COUNTRYCODE TEXT);
CREATE TABLE COUNTRY(CODE TEXT,CONTINENT TEXT);
INSERT INTO CITY VALUES (1,'Lagos','NGA'),(2,'Mumbai','IND'),(3,'Orphan','ZZZ');
INSERT INTO COUNTRY VALUES ('NGA','Africa'),('IND','Asia');""",
        [('Lagos',)]),
    8: ("""CREATE TABLE CITY(ID INTEGER,COUNTRYCODE TEXT,POPULATION INTEGER);
CREATE TABLE COUNTRY(CODE TEXT,CONTINENT TEXT);
INSERT INTO CITY VALUES (1,'N1',10),(2,'N2',11),(3,'E1',2),(4,'ZZZ',1000);
INSERT INTO COUNTRY VALUES ('N1','Africa'),('N2','Africa'),('E1','Europe');""",
        [('Africa',10),('Europe',2)]),
    9: ("""CREATE TABLE Students(ID INTEGER,Name TEXT,Marks INTEGER);
CREATE TABLE Grades(Grade INTEGER,Min_Mark INTEGER,Max_Mark INTEGER);
INSERT INTO Grades VALUES (7,60,69),(8,70,79),(9,80,89),(10,90,100);
INSERT INTO Students VALUES (1,'Amy',80),(2,'Zed',88),(3,'Bela',70),(4,'Eve',60),(5,'Ernie',69),(6,'Nora',100);""",
        [('Nora',10,100),('Amy',9,80),('Zed',9,88),('Bela',8,70),('NULL',7,60),('NULL',7,69)]),
    10: ("""CREATE TABLE Wands(id INTEGER,code INTEGER,coins_needed INTEGER,power INTEGER);
CREATE TABLE Wands_Property(code INTEGER,age INTEGER,is_evil INTEGER);
INSERT INTO Wands_Property VALUES (1,20,0),(2,20,0),(3,10,0),(4,99,1);
INSERT INTO Wands VALUES (1,1,30,5),(2,2,20,5),(3,2,25,5),(4,3,5,5),(5,4,1,10),(6,1,15,4),(7,1,10,5);""",
        [(7,20,10,5),(4,10,5,5),(6,20,15,4)]),
    11: ("""CREATE TABLE Weather(id INTEGER,recordDate TEXT,temperature INTEGER);
INSERT INTO Weather VALUES (1,'2020-02-28',10),(2,'2020-02-29',20),
(3,'2020-03-02',50),(4,'2020-03-03',60);""",
        [(2,),(4,)]),
    12: ("""CREATE TABLE Seller(seller_id INTEGER,seller_name TEXT);
CREATE TABLE Orders(order_id INTEGER,sale_date TEXT,seller_id INTEGER);
INSERT INTO Seller VALUES (1,'A'),(2,'B'),(3,'C'),(4,'D');
INSERT INTO Orders VALUES (1,'2019-12-31',1),(2,'2020-01-01',2),
(3,'2020-12-31',3),(4,'2021-01-01',1),(5,'2020-06-01',NULL);""",
        [('A',),('D',)]),
}
ORDERED = {6, 9, 10, 12}
PENDING = {4, 5}


def archived_sql(number: int, name: str, expected_blob: str) -> str | None:
    data = (BASE / name).read_bytes()
    git_blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\\0" + data).hexdigest()
    assert git_blob == expected_blob, (number, name, git_blob, expected_blob)
    page = data.decode("utf-8")
    assert "## Question and image" in page and "## Schema" in page, name
    section = page.split("## My solution — SQLite", 1)[1].split("## My solution — SQL Server", 1)[0]
    if number in PENDING:
        assert "NOT SOLVED YET" in page and "Pending your final solution." in section
        assert chr(96)*3 + "sql" not in section, name
        return None
    assert "SOLVED" in page and "Solved (recorded):" in page
    return section.split(chr(96)*3 + "sql", 1)[1].split(chr(96)*3, 1)[0].strip()


def main() -> None:
    assert len(PINS) == 12 and len(CASES) == 10 and set(CASES) == set(range(1, 13)) - PENDING
    for number, (name, blob_sha) in enumerate(PINS, 1):
        query = archived_sql(number, name, blob_sha)
        if query is None:
            print(f"Bosscoder Joins {number:02d}/12: original pending record unchanged; no learner/official solve awarded")
            continue
        setup, expected = CASES[number]
        with sqlite3.connect(":memory:") as db:
            db.executescript(setup)
            got = db.execute(query).fetchall()
        if number in ORDERED:
            assert got == expected, (number, name, got, expected)
        else:
            assert sorted(got, key=repr) == sorted(expected, key=repr), (number, name, got, expected)
        print(f"Bosscoder Joins {number:02d}/12: exact archived SQLite answer / synthetic fixture PASS")
    print("Known discrepancy: #09 emits TEXT 'NULL' instead of SQL NULL for hidden names.")
    print("Known divergence: #03 retains missing product lookup rows; supplied lecture inner join omits them.")
    print("12 archived records pinned; 10 historical answer fixtures PASS; 2 pending; no Academy grade/learner completion.")


if __name__ == "__main__":
    main()
