"""Independent, READ-ONLY source audit of 14 archived Bosscoder SQL Windowing exercises.

Historical SQLite queries are extracted from the immutable original Markdown,
never replaced by an auditor answer. Fixture results are NOT official Academy
grades, provider hidden tests, or newly solved learner submissions.
Q11 source displays non-zero-padded timestamps that SQLite date() cannot parse:
the passing replay normalizes only the test input and a separate diagnostic
reproduces the original displayed-input failure explicitly.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/"
    "9. Windowing Functions"
)
FILES = {
    0: ("0. Foundation Notes.md", "eabe347630704b6a4992afb6b94d81f13b3775cc"),
    1: ("1.Sql Last Person To Fit In The Bus.md", "8ee704974094d62828d1782acc8d573a9a5e90e9"),
    2: ("2.Sql Restaurant Growth.md", "f97aff8a07d32460bbb203a99cc4c25ae9adb4d7"),
    3: ("3.Sql Department Top Three Salaries.md", "b7e79558b8674e1eee9e92aa2ee2334bf32c56d7"),
    4: ("4.Sql Second Highest Salary.md", "56bf930cee33714be8de2330fe17ef82beab85fe"),
    5: ("5.Sql Highest Grade For Each Student.md", "e63a4bef38c5c33b73efa3914eb61c8d665b185c"),
    6: ("6.Sql The Most Recent Orders For Each Product.md", "86c956fe4edadb7a18f15433b4d51981a5c98f2a"),
    7: ("7.Sql Find The Start And End Number Of Continuous Ranges.md", "e850d30fdd4a68b6e504844226343573cea80ca4"),
    8: ("8.Sql Biggest Window Between Visits.md", "f07ed483a86e3e969bd96b25baff116b50983cc2"),
    9: ("9.Sql Apples And Oranges.md", "dec79da7b7ed5a7a5957d463e29f76d093454837"),
    10: ("10.Sql Consecutive Available Seats.md", "a8b10c7477c9b6638849ea1c5a7a2b34b5095099"),
    11: ("11.Sql Maximum Transaction Each Day.md", "680b5f291cc4d54d196412c28ce6f448f5bf6e24"),
    12: ("12.Sql Project Employees III.md", "13ce8353885c2e64dab595591f49ec2cb5c5433e"),
    13: ("13.Sql The Most Frequently Ordered Product For Each Customer.md", "914682e16daf546013f31bea4f77c8a3722f0efa"),
    14: ("14.Sql Shortest Distance In A Line.md", "f70ac6a7cfef67dcadb9929f3fcb14b237c29a12"),
}
DDL = {
    1: "CREATE TABLE Queue(person_id INTEGER PRIMARY KEY,person_name TEXT,weight INT,turn INT UNIQUE);",
    2: "CREATE TABLE Customer(customer_id INT,name TEXT,visited_on TEXT,amount INT,PRIMARY KEY(customer_id,visited_on));",
    3: "CREATE TABLE Employee(id INT PRIMARY KEY,name TEXT,salary INT,departmentId INT);CREATE TABLE Department(id INT PRIMARY KEY,name TEXT);",
    4: "CREATE TABLE Employee(id INT PRIMARY KEY,salary INT);",
    5: "CREATE TABLE Enrollments(student_id INT,course_id INT,grade INT,PRIMARY KEY(student_id,course_id));",
    6: "CREATE TABLE Customers(customer_id INT PRIMARY KEY,name TEXT);CREATE TABLE Orders(order_id INT PRIMARY KEY,order_date TEXT,customer_id INT,product_id INT);CREATE TABLE Products(product_id INT PRIMARY KEY,product_name TEXT,price INT);",
    7: "CREATE TABLE Logs(log_id INT PRIMARY KEY);",
    8: "CREATE TABLE user_visits(user_id INT,visit_date TEXT);",
    9: "CREATE TABLE Sales(sale_date TEXT,fruit TEXT,sold_num INT,PRIMARY KEY(sale_date,fruit));",
    10: "CREATE TABLE Cinema(seat_id INT PRIMARY KEY,free INT);",
    11: "CREATE TABLE Transactions(transaction_id INT PRIMARY KEY,day TEXT,amount INT);",
    12: "CREATE TABLE Project(project_id INT,employee_id INT,PRIMARY KEY(project_id,employee_id));CREATE TABLE Employee(employee_id INT PRIMARY KEY,name TEXT,experience_years INT);",
    13: "CREATE TABLE Customers(customer_id INT PRIMARY KEY,name TEXT);CREATE TABLE Orders(order_id INT PRIMARY KEY,order_date TEXT,customer_id INT,product_id INT);CREATE TABLE Products(product_id INT PRIMARY KEY,product_name TEXT,price INT);",
    14: "CREATE TABLE Point(x INT PRIMARY KEY);",
}
customers = [(1,"Winston"),(2,"Jonathan"),(3,"Annabelle"),(4,"Marwan"),(5,"Khaled")]
products = [(1,"keyboard",120),(2,"mouse",80),(3,"screen",600),(4,"hard disk",450)]
orders6 = [(1,"2020-07-31",1,1),(2,"2020-07-30",2,2),(3,"2020-08-29",3,3),
           (4,"2020-07-29",4,1),(5,"2020-06-10",1,2),(6,"2020-08-01",2,1),
           (7,"2020-08-01",3,1),(8,"2020-08-03",1,2),(9,"2020-08-07",2,3),
           (10,"2020-07-15",1,2)]
# Q13's original order 7 is (3,3), unlike the Q06 example's (3,1).
# They are independent primary-source tables and must NOT share that row.
orders13 = [(*row[:3],3) if row[0] == 7 else row for row in orders6]
sales9 = [("2020-05-01","apples",10),("2020-05-01","oranges",8),
          ("2020-05-02","apples",15),("2020-05-02","oranges",15),
          ("2020-05-03","apples",20),("2020-05-03","oranges",0),
          ("2020-05-04","apples",15),("2020-05-04","oranges",16)]
# Expected rows are written from the statement's contract/input, NOT from executing
# the learner SQL; source display output is checked separately against the prompt.
SAMPLES = {
    1: ({"Queue":[(5,"Alice",250,1),(4,"Bob",175,5),(3,"Alex",350,2),
                 (6,"John Cena",400,3),(1,"Winston",500,6),(2,"Marie",200,4)]},
        [("John Cena",)]),
    2: ({"Customer":[(1,"Jhon","2019-01-01",100),(2,"Daniel","2019-01-02",110),
        (3,"Jade","2019-01-03",120),(4,"Khaled","2019-01-04",130),
        (5,"Winston","2019-01-05",110),(6,"Elvis","2019-01-06",140),
        (7,"Anna","2019-01-07",150),(8,"Maria","2019-01-08",80),
        (9,"Jaze","2019-01-09",110),(1,"Jhon","2019-01-10",130),
        (3,"Jade","2019-01-10",150)]},
        [("2019-01-07",860,122.86),("2019-01-08",840,120.0),
         ("2019-01-09",840,120.0),("2019-01-10",1000,142.86)]),
    3: ({"Employee":[(1,"Joe",85000,1),(2,"Henry",80000,2),(3,"Sam",60000,2),
                   (4,"Max",90000,1),(5,"Janet",69000,1),(6,"Randy",85000,1),
                   (7,"Will",70000,1)],"Department":[(1,"IT"),(2,"Sales")]},
        [("IT","Max",90000),("IT","Joe",85000),("IT","Randy",85000),
         ("IT","Will",70000),("Sales","Henry",80000),("Sales","Sam",60000)]),
    4: ({"Employee":[(1,100),(2,200),(3,300)]},[(200,)]),
    5: ({"Enrollments":[(2,2,95),(2,3,95),(1,1,90),(1,2,99),
                       (3,1,80),(3,2,75),(3,3,82)]},
        [(1,2,99),(2,2,95),(3,3,82)]),
    6: ({"Customers":customers,"Products":products,"Orders":orders6},
        [("keyboard",1,6,"2020-08-01"),("keyboard",1,7,"2020-08-01"),
         ("mouse",2,8,"2020-08-03"),("screen",3,3,"2020-08-29")]),
    7: ({"Logs":[(1,),(2,),(3,),(7,),(8,),(10,)]},[(1,3),(7,8),(10,10)]),
    8: ({"user_visits":[(1,"2020-11-28"),(1,"2020-10-20"),(1,"2020-12-03"),
                       (2,"2020-10-05"),(2,"2020-12-09"),(3,"2020-11-11")]},
        [(1,39),(2,65),(3,51)]),
    9: ({"Sales":sales9},[("2020-05-01",2),("2020-05-02",0),
                        ("2020-05-03",20),("2020-05-04",-1)]),
    10: ({"Cinema":[(1,1),(2,0),(3,1),(4,1),(5,1)]},[(3,),(4,),(5,)]),
    # The PDF/archived example uses 2021-4-3 and 2021-4-28; DATE() returns
    # NULL for those strings in SQLite. This is a NORMALIZED fixture only.
    11: ({"Transactions":[(8,"2021-04-03 15:57:28",57),
                         (9,"2021-04-28 08:47:25",21),
                         (1,"2021-04-29 13:28:30",58),
                         (5,"2021-04-28 16:39:59",40),
                         (6,"2021-04-29 23:39:28",58)]},
        [(1,),(5,),(6,),(8,)]),
    12: ({"Project":[(1,1),(1,2),(1,3),(2,1),(2,4)],
          "Employee":[(1,"Khaled",3),(2,"Ali",2),(3,"John",3),(4,"Doe",2)]},
         [(1,1),(1,3),(2,1)]),
    13: ({"Customers":[(1,"Alice"),(2,"Bob"),(3,"Tom"),(4,"Jerry"),(5,"John")],
          "Products":products,"Orders":orders13},
         [(1,2,"mouse"),(2,1,"keyboard"),(2,2,"mouse"),(2,3,"screen"),
          (3,3,"screen"),(4,1,"keyboard")]),
    14: ({"Point":[(-1,),(0,),(2,)]},[(1,)]),
}
SYNTHETIC = {
    1: ({"Queue":[(1,"ExactlyFull",1000,1),(2,"DoesNotFit",1,2)]},
        [("ExactlyFull",)]),
    2: ({"Customer":[(1,"A","2024-02-27",10),(1,"A","2024-02-28",20),
        (1,"A","2024-02-29",30),(1,"A","2024-03-01",40),
        (2,"B","2024-03-01",5),(1,"A","2024-03-02",50),
        (1,"A","2024-03-03",60),(1,"A","2024-03-04",70),
        (1,"A","2024-03-05",80)]},
        [("2024-03-04",285,40.71),("2024-03-05",355,50.71)]),
    3: ({"Department":[(1,"IT"),(2,"Sales"),(3,"Empty")],
         "Employee":[(1,"Alice",100,1),(2,"Bob",90,1),(3,"Eve",90,1),
                     (4,"Carl",80,1),(5,"Dana",70,1),(6,"Z",500,2),(7,"Y",400,2)]},
        [("IT","Alice",100),("IT","Bob",90),("IT","Eve",90),
         ("IT","Carl",80),("Sales","Z",500),("Sales","Y",400)]),
    4: ({"Employee":[(1,500),(2,500),(3,200),(4,200)]},[(200,)]),
    5: ({"Enrollments":[(10,5,88),(10,3,88),(10,7,60),(20,2,70)]},
        [(10,3,88),(20,2,70)]),
    6: ({"Customers":[(1,"A"),(2,"B")],
         "Products":[(1,"same",10),(2,"same",20),(3,"never",30)],
         "Orders":[(1,"2024-01-01",1,1),(2,"2024-01-02",1,1),
                   (3,"2024-01-02",2,1),(4,"2023-12-31",2,2)]},
        [("same",1,2,"2024-01-02"),("same",1,3,"2024-01-02"),
         ("same",2,4,"2023-12-31")]),
    7: ({"Logs":[(-3,),(-2,),(0,),(1,),(5,),(10,),(11,),(12,)]},
        [(-3,-2),(0,1),(5,5),(10,12)]),
    8: ({"user_visits":[(1,"2020-12-30"),(2,"2020-12-01"),
                       (2,"2020-12-10"),(3,"2020-12-31"),
                       (3,"2020-12-31")]},[(1,2),(2,22),(3,1)]),
    9: ({"Sales":[("2020-01-01","apples",0),("2020-01-01","oranges",5),
                 ("2020-01-02","apples",20),("2020-01-02","oranges",3)]},
        [("2020-01-01",-5),("2020-01-02",17)]),
    10: ({"Cinema":[(1,1),(2,1),(4,1),(5,0),(6,1),(7,1)]},
         [(1,),(2,),(6,),(7,)]),
    11: ({"Transactions":[(1,"2021-05-01 10:01:00",10),
                         (2,"2021-05-01 11:01:00",10),
                         (3,"2021-05-02 12:01:00",1),
                         (4,"2021-05-02 13:01:00",0)]},[(1,),(2,),(3,)]),
    12: ({"Project":[(1,1),(1,2),(2,2),(3,3),(3,4)],
          "Employee":[(1,"A",0),(2,"B",0),(3,"C",10),(4,"D",9)]},
         [(1,1),(1,2),(2,2),(3,3)]),
    13: ({"Customers":[(1,"A"),(2,"B"),(3,"Never")],
          "Products":[(1,"Alpha",10),(2,"Beta",20)],
          "Orders":[(1,"2023-01-01",1,1),(2,"2023-01-02",1,1),
                    (3,"2023-01-03",1,2),(4,"2023-02-01",2,1),
                    (5,"2023-02-02",2,2)]},
         [(1,1,"Alpha"),(2,1,"Alpha"),(2,2,"Beta")]),
    14: ({"Point":[(-100,),(-99,),(0,),(20,)]},[(1,)]),
}
def text(i):
    name,pin=FILES[i]
    data=(BASE/name).read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    assert actual == pin, ("original archive modified",i,actual,pin)
    return data.decode("utf-8")

def query(i):
    source=text(i)
    assert "## Question and image" in source and "## Schema" in source
    assert "## My solution — SQLite" in source and "## Official solution" in source
    assert "Solved (recorded)" in source and "UNRATED" in source
    # Each of these source records ends with Pending, rather than an official key.
    official=source.split("## Official solution",1)[1]
    assert "Pending" in official, ("official provenance changed",i)
    section=source.split("## My solution — SQLite",1)[1].split(
        "## My solution — SQL Server",1)[0]
    match=re.search(r"(?ms)^"+chr(96)*3+r"sql\s*\n(.*?)^"+chr(96)*3+r"\s*$",section)
    assert match, ("saved SQLite answer not found",i)
    return match.group(1).strip()

def execute(i,sql,dataset):
    con=sqlite3.connect(":memory:")
    try:
        con.executescript(DDL[i])
        for table,rows in dataset.items():
            if rows:
                con.executemany("INSERT INTO "+table+" VALUES ("+
                                ",".join("?" for _ in rows[0])+")",rows)
        return con.execute(sql).fetchall()
    finally:
        con.close()

def check_fixture(i,sql,case,name):
    dataset,expected=case
    actual=execute(i,sql,dataset)
    assert actual==expected, (i,name,"actual",actual,"expected",expected)

def known_input_discrepancies(queries):
    # This is a NEGATIVE test, not a passing test of the source's raw example.
    raw={"Transactions":[(8,"2021-4-3 15:57:28",57),
        (9,"2021-4-28 08:47:25",21),(1,"2021-4-29 13:28:30",58),
        (5,"2021-4-28 16:39:59",40),(6,"2021-4-29 23:39:28",58)]}
    observed=execute(11,queries[11],raw)
    assert observed==[(1,),(6,)],("Q11 raw example behavior changed",observed)
    assert observed!=SAMPLES[11][1], "Q11 raw example unexpectedly matched"
    # Conditional Q09 source contract: no guarantee that every date has both
    # fruit categories. A one-fruit day is omitted by the archived LEAD query.
    one_fruit=execute(9,queries[9],{"Sales":[("2020-06-01","apples",5)]})
    assert one_fruit==[],("Q09 missing-fruit behavior changed",one_fruit)
    # Q04 still has the documented aggregate one-row NULL fallback.
    check_fixture(4,queries[4],({"Employee":[(1,100)]},[(None,)]),
                  "one distinct salary fallback")

def main():
    foundation=text(0)
    assert "ROW_NUMBER" in foundation and "LAG" in foundation and "NTILE" in foundation
    queries={i:query(i) for i in range(1,15)}
    for i in range(1,15):
        check_fixture(i,queries[i],SAMPLES[i],"source-retyped input")
        check_fixture(i,queries[i],SYNTHETIC[i],"auditor-synthetic fixture")
        print("PASS",f"{i:02d}",FILES[i][0],"(source-derived + synthetic)")
    known_input_discrepancies(queries)
    print("PASS 15/15 original hashes; 14/14 source-derived fixtures "
          "(Q11 timestamps normalized); 14/14 independent synthetic; "
          "Q04 NULL fallback; Q11 raw timestamp failure and "
          "Q09 absent-fruit conditional discrepancy explicitly reproduced")
    print("NOT verified: Academy official answers/grades, hidden datasets, "
          "native SQL Server, all original foundation examples or new learner mastery")

if __name__ == "__main__":
    main()
