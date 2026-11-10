"""Read-only replay of archived Bosscoder Sorting/Grouping SQLite answers.

Evidence: 11 individually inspected, immutable archived Markdown problem records,
11 auditor-created SQLite fixtures, four retyped archived sample input/output
checks, plus second recorded answer on #04. No Academy grader or learner credit.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/3. Sorting and Grouping"
PINS = {
    1: ("1.Sql Number Of Unique Subjects Taught By Each Teacher.md", "a750e3a3329afce2255360da02de3c37e3c5c5e8"),
    2: ("2.Sql Classes With At Least 5 Students.md", "328cb856f0331d6dbc04cb3767edec1b92f9257e"),
    3: ("3.Sql User Activity For The Past 30 Days.md", "9ac59e7d3216aef612bef269153ac6764c94ceb4"),
    4: ("4.Sql Product Sales Analysis 3.md", "c79d2c14b8ebcd9a6824e5bca78f3980097ba410"),
    5: ("5.Sql Customers Who Bought All Products.md", "f387593e105cd82bb8f50939ad1897fbcaa2f465"),
    6: ("6.Sql Daily Leads And Partners.md", "18e724518be0d7076574b71af6ef3fb22b431afc"),
    7: ("7.Sql Bank Account Summary.md", "b5548d06e3817241413eff3d0f5ab66669d5c72e"),
    8: ("8.Sql Duplicate Emails.md", "11f5d49cb4c8e8bacb407da34415888cab71d95f"),
    9: ("9.Sql Actors And Directors Who Cooperated At Least Three Times.md", "8c75c51584f8a9fd42b9bb4684e40b3cdc835159"),
   10: ("10.Sql Customer Order Frequency.md", "c1080c0fa5ab1b40700ec197be00bf41fefdbf1e"),
   11: ("11.Sql Friendly Movies Streamed Last Month.md", "8c8da5fb1b5df7f82e55c41be87a7a7a8fbc019c"),
}
# Expected rows are independently calculated, not from official hidden datasets.
# The shape is setup SQL, expected rows. Unordered problems are compared as
# multisets; an ORDER BY in the learner SQL alone does not make ordering required.
FIXTURES = {
  1: ("""CREATE TABLE Teacher(teacher_id INT, subject_id INT, dept_id INT);
INSERT INTO Teacher VALUES (1,2,3),(1,2,4),(1,3,3),(2,1,1);""",
      [(1,2),(2,1)]),
  2: ("""CREATE TABLE Courses(student TEXT,class TEXT);
INSERT INTO Courses VALUES
('A','Math'),('B','Math'),('C','Math'),('D','Math'),('E','Math'),
('F','Physics'),('G','Physics'),('H','Physics'),('I','Physics'),('J','Physics'),('K','Physics'),
('L','English'),('M','English'),('N','English'),('O','English');""",
      [('Math',),('Physics',)]),
  3: ("""CREATE TABLE Activity(user_id INT,session_id INT,activity_date TEXT,activity_type TEXT);
INSERT INTO Activity VALUES
(1,1,'2019-06-27','open_session'),
(1,1,'2019-06-28','open_session'),(1,1,'2019-06-28','scroll_down'),
(2,2,'2019-06-28','open_session'),(2,2,'2019-06-28','open_session'),
(3,3,'2019-07-27','send_message'),(4,4,'2019-07-28','open_session');""",
      [('2019-06-28',2),('2019-07-27',1)]),
  4: ("""CREATE TABLE Sales(sale_id INT,product_id INT,year INT,quantity INT,price INT);
INSERT INTO Sales VALUES (1,100,2008,10,50),(2,100,2008,2,51),
(3,100,2009,9,55),(4,200,2011,1,10),(5,200,2010,4,12),
(6,200,2010,3,13);""",
      [(100,2008,10,50),(100,2008,2,51),(200,2010,4,12),(200,2010,3,13)]),
  5: ("""CREATE TABLE Customer(customer_id INT, product_key INT);
CREATE TABLE Product(product_key INT PRIMARY KEY);
INSERT INTO Product VALUES (5),(6),(7);
INSERT INTO Customer VALUES (1,5),(1,6),(1,7),(1,7),(2,5),(2,6),
(3,5),(3,6),(3,7);""", [(1,),(3,)]),
  6: ("""CREATE TABLE DailySales(date_id TEXT,make_name TEXT,lead_id INT,partner_id INT);
INSERT INTO DailySales VALUES
('2020-12-07','toyota',0,1),('2020-12-07','toyota',0,2),
('2020-12-07','toyota',0,2),('2020-12-07','honda',1,1),
('2020-12-07','honda',2,1),('2020-12-08','toyota',3,3);""",
      [('2020-12-07','toyota',1,2),('2020-12-07','honda',2,1),('2020-12-08','toyota',1,1)]),
  7: ("""CREATE TABLE Users(account INT PRIMARY KEY,name TEXT);
CREATE TABLE Transactions(trans_id INT,account INT,amount INT,transacted_on TEXT);
INSERT INTO Users VALUES (1,'A'),(2,'B'),(3,'C'),(4,'D');
INSERT INTO Transactions VALUES (1,1,7000,'2020-01-01'),(2,1,3000,'2020-01-02'),
(3,2,10001,'2020-01-03'),(4,3,-1000,'2020-01-01'),(5,3,12002,'2020-01-04');""",
      [('B',10001),('C',11002)]),
  8: ("""CREATE TABLE Person(id INT PRIMARY KEY,email TEXT NOT NULL);
INSERT INTO Person VALUES (1,'a@b.com'),(2,'b@b.com'),(3,'a@b.com'),
(4,'x@y.com'),(5,'b@b.com'),(6,'b@b.com');""",
      [('a@b.com',),('b@b.com',)]),
  9: ("""CREATE TABLE ActorDirector(actor_id INT,director_id INT,timestamp INT PRIMARY KEY);
INSERT INTO ActorDirector VALUES (1,1,0),(1,1,1),(1,1,2),(1,2,3),
(1,2,4),(2,1,5),(2,1,6),(2,1,7);""",
      [(1,1),(2,1)]),
 10: ("""CREATE TABLE Customers(customer_id INT,name TEXT,country TEXT);
CREATE TABLE Product(product_id INT,description TEXT,price INT);
CREATE TABLE Orders(order_id INT,customer_id INT,product_id INT,order_date TEXT,quantity INT);
INSERT INTO Customers VALUES (1,'A','US'),(2,'B','US'),(3,'C','US'),(4,'D','US');
INSERT INTO Product VALUES (10,'A',100),(20,'B',99),(30,'C',1);
INSERT INTO Orders VALUES
(1,1,10,'2020-06-01',1),(2,1,10,'2020-07-31',1),
(3,2,20,'2020-06-01',1),(4,2,10,'2020-07-01',2),
(5,3,10,'2020-06-30',1),(6,3,20,'2020-07-31',1),
(7,4,10,'2020-06-30',1),(8,4,10,'2020-07-31',1),
(9,4,10,'2020-08-01',10);""", [(1,'A'),(4,'D')]),
 11: ("""CREATE TABLE TVProgram(program_date TEXT,content_id INT,channel TEXT);
CREATE TABLE Content(content_id TEXT,title TEXT,Kids_content TEXT,content_type TEXT);
INSERT INTO Content VALUES ('1','Aladdin','Y','Movies'),('2','Aladdin','Y','Movies'),
('3','Not for Kids','N','Movies'),('4','Friendly Series','Y','Series'),
('5','Z','Y','Movies'),('6','Outside','Y','Movies');
INSERT INTO TVProgram VALUES
('2020-06-01 00:00',1,'A'),('2020-06-20 10:30',2,'B'),
('2020-06-22 12:00',3,'A'),('2020-06-25 16:30',4,'A'),
('2020-06-30 23:59',5,'B'),('2020-07-01 00:00',6,'A');""",
      [('Aladdin',),('Z',)]),
}
# Four independently reconstructed archive-displayed samples (different tier
# from auditor synthetic fixtures). Sample inputs are small and deterministic.
SAMPLES = {
  1: ("""CREATE TABLE Teacher(teacher_id INT,subject_id INT,dept_id INT);
INSERT INTO Teacher VALUES (1,2,3),(1,2,4),(1,3,3),(2,1,1),(2,2,1),(2,3,1),(2,4,1);""",
      [(1,2),(2,4)]),
  2: ("""CREATE TABLE Courses(student TEXT,class TEXT);
INSERT INTO Courses VALUES ('A','Math'),('B','English'),('C','Math'),('D','Biology'),
('E','Math'),('F','Computer'),('G','Math'),('H','Math'),('I','Math');""",
      [('Math',)]),
  3: ("""CREATE TABLE Activity(user_id INT,session_id INT,activity_date TEXT,activity_type TEXT);
INSERT INTO Activity VALUES
(1,1,'2019-07-20','open_session'),(1,1,'2019-07-20','scroll_down'),
(1,1,'2019-07-20','end_session'),(2,4,'2019-07-20','open_session'),
(2,4,'2019-07-21','send_message'),(2,4,'2019-07-21','end_session'),
(3,2,'2019-07-21','open_session'),(3,2,'2019-07-21','send_message'),
(3,2,'2019-07-21','end_session'),(4,3,'2019-06-25','open_session'),
(4,3,'2019-06-25','end_session');""",
      [('2019-07-20',2),('2019-07-21',2)]),
 10: ("""CREATE TABLE Customers(customer_id INT,name TEXT,country TEXT);
CREATE TABLE Product(product_id INT,description TEXT,price INT);
CREATE TABLE Orders(order_id INT,customer_id INT,product_id INT,order_date TEXT,quantity INT);
INSERT INTO Customers VALUES (1,'Winston','USA'),(2,'Jonathan','Peru'),(3,'Moustafa','Egypt');
INSERT INTO Product VALUES (10,'LC Phone',300),(20,'LC T-Shirt',10),(30,'LC Book',45),(40,'LC Keychain',2);
INSERT INTO Orders VALUES (1,1,10,'2020-06-10',1),(2,1,20,'2020-07-01',1),
(3,1,30,'2020-07-08',2),(4,2,10,'2020-06-15',2),(5,2,40,'2020-07-01',10),
(6,3,20,'2020-06-24',2),(7,3,30,'2020-06-25',2),(9,3,30,'2020-05-08',3);""",
      [(1,'Winston')]),
}
# Prompt requires ordering for #3 #5 #8 #9 #10; for other fixtures
# multiset comparisons avoid treating unspecified tie order as a correctness bug.
ORDERED = {1, 3, 5, 8, 9, 11}

def archived_sql(number: int) -> list[str]:
    filename, expected_sha = PINS[number]
    data = (BASE / filename).read_bytes()
    observed_sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    assert observed_sha == expected_sha, (number, filename, observed_sha)
    page = data.decode("utf-8")
    assert "## Question and image" in page and "## Schema" in page
    assert "Solved (recorded)" in page and "UNRATED" in page
    section = page.split("## My solution — SQLite", 1)[1].split("## My solution — SQL Server", 1)[0]
    fence = chr(96) * 3
    queries = re.findall(re.escape(fence) + r"sql\s*\n(.*?)" + re.escape(fence), section, re.S)
    assert queries, (number, filename)
    # The first fenced query is the historical final answer. #04 also includes
    # a saved alternative; replay both, no new answer created.
    return [queries[0]] + ([queries[1]] if number == 4 else [])

def replay(query: str, setup: str) -> list[tuple]:
    with sqlite3.connect(":memory:") as conn:
        conn.executescript(setup)
        return conn.execute(query).fetchall()

def check(number: int, query: str, setup: str, expected: list[tuple], tier: str) -> None:
    observed = replay(query, setup)
    if number in ORDERED:
        assert observed == expected, (number, tier, observed, expected)
    else:
        assert sorted(observed, key=repr) == sorted(expected, key=repr), (number, tier, observed, expected)

def main() -> None:
    assert set(PINS) == set(FIXTURES) == set(range(1, 12))
    for number in range(1, 12):
        queries = archived_sql(number)
        for alternative, query in enumerate(queries, 1):
            check(number, query, *FIXTURES[number], "synthetic")
            print(f"Sorting/Grouping {number:02d}/11 solution {alternative}: immutable archived SQL + independent synthetic fixture PASS")
            if number in SAMPLES:
                check(number, query, *SAMPLES[number], "source displayed sample")
                print(f"Sorting/Grouping {number:02d}/11 solution {alternative}: retyped archived displayed sample PASS")
    assert len(SAMPLES) == 4
    print("11 original source records SHA-pinned; 12 archived-SQL synthetic executions (#04 twice), 5 source-sample executions (#04 not sampled); 0 official Academy platform grades; 0 new learner credits.")

if __name__ == "__main__":
    main()
