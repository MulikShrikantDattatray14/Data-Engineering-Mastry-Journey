#!/usr/bin/env python3
"""Read immutable archived Bosscoder Intro SQL learner answers and run SQLite fixtures.

All fixtures are reviewer-reconstructed from visible samples plus boundary rows.
No claim of official platform grading, proprietary dataset parity, or new solves.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / ("99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
              "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/"
              "1. Intro to SQL and Advanced Select")
PINS = [
    ("1.Sql Find Customers With Positive Revenue This Year.md", "ff4daccbae10d314223aaf2ca9f079701e7674db"),
    ("2.Sql Calculate Special Bonus.md", "763532394ecb9fc40b0589f5e2e11aea7115ab2e"),
    ("3.Sql Binary Tree Nodes.md", "0d4685de9da53529619a1d2d34ffdf4cce66862d"),
    ("4.Sql Rearrange Products Table.md", "e9fc3eb77fb62858a2fa131a30bd94a189215372"),
    ("5.Sql Type Of Triangle.md", "04c688afc86a05985404531cb19beb13b72f5db4"),
    ("6.Sql Recyclable And Low Fat Products.md", "2e0a2f4b22a05ab2e74ee5418dac8ed656a21b96"),
    ("7.Sql Japanese Cities Attributes.md", "8b453dd21d0f4007d460b89f08dd610a71527318"),
    ("8.Sql Revising The Select Query.md", "84a72a915e646a7f591de76d162b86b5da8be0fb"),
    ("9.Sql Find Customer Referee.md", "e6351695cab18bfc36bd799adecd07eb335fac57"),
    ("10.Sql Big Countries.md", "3dc19a0ca467fc1cf9e3f1d47fcf322bd21c1399"),
    ("11.Sql Article Views I.md", "c308a31dc3a235a2da348ebdf23209dac8d5c98e"),
    ("12.Sql Invalid Tweets.md", "6d646e35bfd2269838646fbc9951e35cb168e6ac"),
    ("13.Sql Customers Who Never Order.md", "9a6574ac1fb7dec0b1d92302f425c2a25a3e4b94"),
]

def query_from_archive(i, name, expected_hash):
    raw = (SRC / name).read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    assert sha == expected_hash, (name, "original archive changed", sha)
    body = raw.decode("utf-8").split("## My solution — SQLite", 1)[1]
    body = body.split("## My solution — SQL Server", 1)[0]
    if i == 2:
        body = body.split("### Solution 3 — Boolean multiplication (my final query)", 1)[1]
    if i == 7:
        body = body.split("### Solution 2 — Name each column (my final query)", 1)[1]
    mark = re.escape(chr(96) * 3)
    match = re.search(mark + r"sql\s*\n(.*?)" + mark, body, flags=re.S | re.I)
    assert match, (name, "archived SQL answer missing")
    return match.group(1).strip()

# SQLite statement fixtures: source-sample rows + independently designed boundaries.
# Expected results are auditor decisions from the written prompts, not grader data.
CASES = [
('''CREATE TABLE Customers(customer_id INT,year INT,revenue INT);
INSERT INTO Customers VALUES (1,2018,50),(1,2021,30),(2,2021,-50),(3,2018,10),(4,2021,20),(5,2021,0);''', [(1,), (4,)]),
('''CREATE TABLE Employees(employee_id INT,name TEXT,salary INT);
INSERT INTO Employees VALUES (2,'Meir',3000),(3,'Michael',3800),(7,'Addilyn',7400),
(8,'Juan',6100),(9,'Kannon',7700),(11,'Molly',100),(13,'Zelda',550);''', [(2,0),(3,0),(7,7400),(8,0),(9,7700),(11,0),(13,550)]),
('''CREATE TABLE BST(N INT,P INT);
INSERT INTO BST VALUES (1,2),(3,2),(6,8),(9,8),(2,5),(8,5),(5,NULL);''', [(1,'Leaf'),(2,'Inner'),(3,'Leaf'),(5,'Root'),(6,'Leaf'),(8,'Inner'),(9,'Leaf')]),
('''CREATE TABLE Products(product_id INT,store1 INT,store2 INT,store3 INT);
INSERT INTO Products VALUES (0,95,100,105),(1,70,NULL,80),(2,NULL,0,NULL);''', [(0,'store1',95),(1,'store1',70),(0,'store2',100),(2,'store2',0),(0,'store3',105),(1,'store3',80)]),
('''CREATE TABLE TRIANGLES(A INT,B INT,C INT);
INSERT INTO TRIANGLES VALUES (20,20,23),(20,20,20),(20,21,22),(13,14,30),(0,0,0),(1,2,3),(-1,2,3);''',
 [('Isosceles',),('Equilateral',),('Scalene',),('Not A Triangle',),('Not A Triangle',),('Not A Triangle',),('Not A Triangle',)]),
('''CREATE TABLE Products(product_id INT,low_fats TEXT,recyclable TEXT);
INSERT INTO Products VALUES (0,'Y','N'),(1,'Y','Y'),(2,'N','Y'),(3,'Y','Y'),(4,'N','N');''', [(1,), (3,)]),
('''CREATE TABLE CITY(ID INT,NAME TEXT,COUNTRYCODE TEXT,DISTRICT TEXT,POPULATION INT);
INSERT INTO CITY VALUES (1,'Tokyo','JPN','Tokyo',9000000),(2,'New York','USA','New York',8400000),
(3,'Paris','FRA','Ile de France',2100000),(4,'Osaka','JPN','Osaka',2000000);''',
 [(1,'Tokyo','JPN','Tokyo',9000000),(4,'Osaka','JPN','Osaka',2000000)]),
('''CREATE TABLE CITY(ID INT,NAME TEXT,COUNTRYCODE TEXT,DISTRICT TEXT,POPULATION INT);
INSERT INTO CITY VALUES (1,'New York','USA','New York',8008278),(2,'Los Angeles','USA','California',3694820),
(3,'Chicago','USA','Illinois',2896016),(4,'Toronto','CAN','Ontario',3000000),
(5,'Houston','USA','Texas',1953631),(6,'Boundary','USA','X',100000),(7,'Small','USA','X',99999);''',
 [(1,'New York','USA','New York',8008278),(2,'Los Angeles','USA','California',3694820),
 (3,'Chicago','USA','Illinois',2896016),(5,'Houston','USA','Texas',1953631)]),
('''CREATE TABLE Customer(id INT,name TEXT,referee_id INT);
INSERT INTO Customer VALUES (1,'Will',NULL),(2,'Jane',NULL),(3,'Alex',2),
(4,'Bill',NULL),(5,'Zack',1),(6,'Mark',2);''', [('Will',),('Jane',),('Bill',),('Zack',)]),
('''CREATE TABLE World(name TEXT,continent TEXT,area INT,population INT,gdp INT);
INSERT INTO World VALUES ('Afghanistan','Asia',652230,25500100,20343000000),
('Albania','Europe',28748,2831741,12960000000),('Algeria','Africa',2381741,37100000,188681000000),
('Andorra','Europe',468,78115,3712000000),('Angola','Africa',1246700,20609294,100990000000),
('AreaEdge','X',3000000,1,0),('PopulationEdge','X',1,25000000,0);''',
 [('Afghanistan',25500100,652230),('Algeria',37100000,2381741),
 ('AreaEdge',1,3000000),('PopulationEdge',25000000,1)]),
('''CREATE TABLE Views(article_id INT,author_id INT,viewer_id INT,view_date TEXT);
INSERT INTO Views VALUES (1,3,5,'2019-08-01'),(1,3,6,'2019-08-02'),
(2,7,7,'2019-08-01'),(2,7,6,'2019-08-02'),(4,7,1,'2019-07-22'),
(3,4,4,'2019-07-21'),(3,4,4,'2019-07-21');''', [(4,), (7,)]),
('''CREATE TABLE Tweets(tweet_id INT,content TEXT);
INSERT INTO Tweets VALUES (1,'Let us Code'),(2,'More than fifteen chars are here!'),
(3,'123456789012345'),(4,'123456789012345 '),(5,'short');''', [(2,), (4,)]),
('''CREATE TABLE Customers(id INT,name TEXT); CREATE TABLE Orders(id INT,customerId INT);
INSERT INTO Customers VALUES (1,'Joe'),(2,'Henry'),(3,'Sam'),(4,'Max');
INSERT INTO Orders VALUES (1,3),(2,1);''', [('Henry',), ('Max',)]),
]

def main():
    assert len(PINS) == len(CASES) == 13
    for index, ((name, sha), (setup, wanted)) in enumerate(zip(PINS, CASES), start=1):
        sql = query_from_archive(index, name, sha)
        with sqlite3.connect(":memory:") as connection:
            connection.executescript(setup)
            actual = connection.execute(sql).fetchall()
            assert sorted(actual) == sorted(wanted), (index, name, actual, wanted)
            if index in (2, 3, 11):
                assert actual == wanted, (index, name, "required ORDER BY", actual)
            if index == 4:
                assert [r[1] for r in actual] == sorted(r[1] for r in actual), (index, "store sort")
            if index == 13:
                connection.execute("INSERT INTO Orders VALUES (3,NULL)")
                poisoned = connection.execute(sql).fetchall()
                assert poisoned == [], (index, "known NULL-sensitive NOT IN discrepancy", poisoned)
        print(f"Bosscoder Intro {index:02d}/13: archived answer SQLite fixture PASS")
    print("Observed known source limitation: #13 NOT IN returns no customers if Orders.customerId contains NULL.")
    print("13/13 archived answer fixtures passed; this is not platform grading, official data, or new learner mastery.")

if __name__ == "__main__":
    main()
