"""Read-only, SHA-pinned audit of 12 Bosscoder SQL CTE source records.

Replays 10 *historical* SQLite answers on retyped original displayed samples
and separate independently designed fixtures; verifies two PENDING records.
No official Academy grading, no new student solutions, no SQL Server execution.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/5. CTEs"
)
FILES = {
    1: ("1.Sql Queries Quality And Percentage.md", "a5ee7282960fbb86c654d4a89b46540d1bb12d44"),
    2: ("2.Sql Percentage Of Users Attended A Contest.md", "0fd1561811bb1c7f77a61367ff4b14e5ef5e6ec2"),
    3: ("3.Sql Confirmation Rate.md", "8ccedc146de91260e81309e1045a712d04c88e46"),
    4: ("4.Sql Students And Examinations.md", "76bbaab89933fb374e2dfbd9db25838d90ab8fef"),
    5: ("5.Sql Find Immediate Delivery Ii.md", "c5013d78468d75f7f7b8ff32530bc8fdd9e3b13b"),
    6: ("6.Sql Customers Who Bought A And B But Not C.md", "90724715a11e01dcb4611c2dff172bdef3e7dc23"),
    7: ("7.Sql Team Total In Football Tournaments.md", "52dc34fd6aaaf1f4d4ad753474d7a37fc7e9b5e8"),
    8: ("8.Sql Evaluate Boolean Expressions.md", "6f999394e9e55a10503716d19daf6065066fb9e4"),
    9: ("9.Sql Number Of Calls Between Two Persons.md", "8dda1a83b87f6bbaf640f6ba809902af59467f48"),
    10: ("10.Sql Countries Where You Can Safely Invest In.md", "f325cdb01a66b2c73d1df0cbd091c3042786e298"),
    11: ("11.Sql Find The Quiet Students In All Exams.md", "33bcc994e5900bdca9c407ab3545e7e337c5f2db"),
    12: ("12.Sql Report Contiguous Dates.md", "e22b6a934769222df8458e7b2ed80ecce6b133fc"),
}
DDL = {
    1: "CREATE TABLE Queries(query_name TEXT,result TEXT,position INTEGER,rating INTEGER);",
    2: "CREATE TABLE Users(user_id INTEGER,user_name TEXT); CREATE TABLE Register(contest_id INTEGER,user_id INTEGER);",
    3: "CREATE TABLE Signups(user_id INTEGER,time_stamp TEXT); CREATE TABLE Confirmations(user_id INTEGER,time_stamp TEXT,action TEXT);",
    4: "CREATE TABLE Students(student_id INTEGER,student_name TEXT); CREATE TABLE Subjects(subject_name TEXT); CREATE TABLE Examinations(student_id INTEGER,subject_name TEXT);",
    5: "CREATE TABLE Delivery(delivery_id INTEGER,customer_id INTEGER,order_date TEXT,customer_pref_delivery_date TEXT);",
    6: "CREATE TABLE Customers(customer_id INTEGER,customer_name TEXT); CREATE TABLE Orders(order_id INTEGER,customer_id INTEGER,product_name TEXT);",
    7: "CREATE TABLE Teams(team_id INTEGER,team_name TEXT); CREATE TABLE Matches(match_id INTEGER,host_team INTEGER,guest_team INTEGER,host_goals INTEGER,guest_goals INTEGER);",
    8: "CREATE TABLE Variables(name TEXT,value INTEGER); CREATE TABLE Expressions(left_operand TEXT,operator TEXT,right_operand TEXT);",
    9: "CREATE TABLE Calls(from_id INTEGER,to_id INTEGER,duration INTEGER);",
    10: "CREATE TABLE Person(id INTEGER,name TEXT,phone_number TEXT); CREATE TABLE Country(name TEXT,country_code TEXT); CREATE TABLE Calls(caller_id INTEGER,callee_id INTEGER,duration INTEGER);",
}
# These inputs and expected results were independently retyped from the
# *displayed public archive question samples*, not copied from learner queries.
SAMPLES = {
    1: ({"Queries": [
        ("Dog","Golden Retriever",1,5),("Dog","German Shepherd",2,5),
        ("Dog","Mule",200,1),("Cat","Shirazi",5,2),
        ("Cat","Siamese",3,3),("Cat","Sphynx",7,4)
    ]}, [("Cat",0.66,33.33),("Dog",2.50,33.33)]),
    2: ({"Users": [(6,"Alice"),(2,"Bob"),(7,"Alex")],
         "Register": [(215,6),(209,2),(208,2),(210,6),(208,6),(209,7),
                      (209,6),(215,7),(208,7),(210,2),(207,2),(210,7)]},
        [(208,100.0),(209,100.0),(210,100.0),(215,66.67),(207,33.33)]),
    3: ({"Signups": [(3,"2020-03-21"),(7,"2020-01-04"),(2,"2020-07-29"),(6,"2020-12-09")],
         "Confirmations": [(3,"2021-01-06","timeout"),(3,"2021-07-14","timeout"),
                           (7,"2021-06-12","confirmed"),(7,"2021-06-13","confirmed"),
                           (7,"2021-06-14","confirmed"),(2,"2021-01-22","confirmed"),
                           (2,"2021-02-28","timeout")]},
        [(2,0.5),(3,0.0),(6,0.0),(7,1.0)]),
    4: ({"Students": [(1,"Alice"),(2,"Bob"),(13,"John"),(6,"Alex")],
         "Subjects": [("Math",),("Physics",),("Programming",)],
         "Examinations": [(1,"Math"),(1,"Physics"),(1,"Programming"),
                          (2,"Programming"),(1,"Physics"),(1,"Math"),
                          (13,"Math"),(13,"Programming"),(13,"Physics"),
                          (2,"Math"),(1,"Math")]},
        [(1,"Alice","Math",3),(1,"Alice","Physics",2),(1,"Alice","Programming",1),
         (2,"Bob","Math",1),(2,"Bob","Physics",0),(2,"Bob","Programming",1),
         (6,"Alex","Math",0),(6,"Alex","Physics",0),(6,"Alex","Programming",0),
         (13,"John","Math",1),(13,"John","Physics",1),(13,"John","Programming",1)]),
    5: ({"Delivery": [(1,1,"2019-08-01","2019-08-02"),(2,2,"2019-08-02","2019-08-02"),
                     (3,1,"2019-08-11","2019-08-12"),(4,3,"2019-08-24","2019-08-24"),
                     (5,3,"2019-08-21","2019-08-22"),(6,2,"2019-08-11","2019-08-13"),
                     (7,4,"2019-08-09","2019-08-09")]},[(50.0,)]),
    6: ({"Customers": [(1,"Daniel"),(2,"Diana"),(3,"Elizabeth"),(4,"Jhon")],
         "Orders": [(10,1,"A"),(20,1,"B"),(30,1,"D"),(40,1,"C"),
                    (50,2,"A"),(60,3,"A"),(70,3,"B"),(80,3,"D"),(90,4,"C")]},
        [(3,"Elizabeth")]),
    7: ({"Teams": [(10,"Leetcode FC"),(20,"NewYork FC"),(30,"Atlanta FC"),
                   (40,"Chicago FC"),(50,"Toronto FC")],
         "Matches": [(1,10,20,3,0),(2,30,10,2,2),(3,10,50,5,1),
                     (4,20,30,1,0),(5,50,30,1,0)]},
        [(10,"Leetcode FC",7),(20,"NewYork FC",3),(50,"Toronto FC",3),
         (30,"Atlanta FC",1),(40,"Chicago FC",0)]),
    8: ({"Variables": [("x",66),("y",77)],
         "Expressions": [("x",">","y"),("x","<","y"),("x","=","y"),
                         ("y",">","x"),("y","<","x"),("x","=","x")]},
        [("x",">","y","false"),("x","<","y","true"),("x","=","y","false"),
         ("y",">","x","true"),("y","<","x","false"),("x","=","x","true")]),
    9: ({"Calls": [(1,2,59),(2,1,11),(1,3,20),(3,4,100),
                   (3,4,200),(3,4,200),(4,3,499)]},
        [(1,2,2,70),(1,3,1,20),(3,4,4,999)]),
    10: ({"Person": [(3,"Jonathan","051-1234567"),(12,"Elvis","051-7654321"),
                     (1,"Moncef","212-1234567"),(2,"Maroua","212-6523651"),
                     (7,"Meir","972-1234567"),(9,"Rachel","972-0011100")],
          "Country": [("Peru","051"),("Israel","972"),("Morocco","212"),
                      ("Germany","049"),("Ethiopia","251")],
          "Calls": [(1,9,33),(2,9,4),(1,2,59),(3,12,102),(3,12,330),
                    (12,3,5),(7,9,13),(7,1,3),(9,7,1),(1,7,7)]},[("Peru",)]),
}
# Separate auditor-authored boundary cases. They do NOT represent source sample
# or official platform evidence; keys and schema promises are respected.
SYNTHETIC = {
    1: ({"Queries": [("Alpha","a",1,1),("Alpha","a",1,1),
                     ("Alpha","b",2,5),("Beta","z",4,4)]},
        [("Alpha",1.50,66.67),("Beta",1.0,0.0)]),
    2: ({"Users": [(1,"A"),(2,"B"),(3,"C"),(4,"D")],
         "Register": [(10,1),(10,2),(11,2),(11,3),(12,4)]},
        [(10,50.0),(11,50.0),(12,25.0)]),
    3: ({"Signups": [(1,"2020-01-01"),(2,"2020-01-02"),(3,"2020-01-03")],
         "Confirmations": [(2,"2021-01-01","confirmed"),(2,"2021-01-02","timeout"),
                           (2,"2021-01-03","timeout"),(3,"2021-02-01","confirmed")]},
        [(1,0.0),(2,0.33),(3,1.0)]),
    4: ({"Students": [(2,"B"),(1,"A")],
         "Subjects": [("X",),("Y",),("Z",)],
         "Examinations": [(1,"X"),(1,"X"),(1,"Z")]},
        [(1,"A","X",2),(1,"A","Y",0),(1,"A","Z",1),
         (2,"B","X",0),(2,"B","Y",0),(2,"B","Z",0)]),
    5: ({"Delivery": [(1,1,"2020-01-01","2020-01-01"),
                     (2,1,"2020-02-01","2020-02-01"),
                     (3,2,"2020-01-01","2020-01-02"),
                     (4,2,"2020-02-01","2020-02-01"),
                     (5,3,"2020-01-03","2020-01-04")]},[(33.33,)]),
    6: ({"Customers": [(1,"A"),(2,"B"),(3,"C"),(4,"D"),(5,"E")],
         "Orders": [(1,1,"A"),(2,1,"B"),(3,1,"C"),
                    (4,2,"A"),(5,2,"B"),(6,2,"A"),
                    (7,3,"A"),(8,4,"A"),(9,4,"B"),(10,5,"B")]},
        [(2,"B"),(4,"D")]),
    7: ({"Teams": [(1,"A"),(2,"B"),(3,"C"),(4,"D")],
         "Matches": [(1,1,2,2,1),(2,2,3,0,0)]},
        [(1,"A",3),(2,"B",1),(3,"C",1),(4,"D",0)]),
    8: ({"Variables": [("a",-1),("b",0),("c",0)],
         "Expressions": [("a","<","b"),("b","=","c"),("c",">","a"),
                         ("a",">","b")]},
        [("a","<","b","true"),("b","=","c","true"),
         ("c",">","a","true"),("a",">","b","false")]),
    9: ({"Calls": [(5,1,5),(1,5,10),(5,1,5),(2,3,7)]},
        [(1,5,3,20),(2,3,1,7)]),
    10: ({"Person": [(1,"A","001-1234567"),(2,"B","001-7654321"),
                      (3,"C","002-1234567"),(4,"D","002-7654321")],
          "Country": [("AA","001"),("BB","002")],
          "Calls": [(1,2,100),(3,4,5),(1,3,10)]},[("AA",)]),
}
ORDERED = {1,2,3,4,5,6,7}
def source(i):
    name, pin = FILES[i]
    b = (BASE/name).read_bytes()
    actual = hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    assert actual == pin, (i,actual,pin)
    s = b.decode("utf-8")
    assert "## Question and image" in s and "## Schema" in s and "UNRATED" in s
    if i >= 11:
        assert "NOT SOLVED YET" in s and "Pending — solve this question first." in s
        assert "## Official solution" in s
        return None
    assert "Solved (recorded)" in s and "## My solution — SQLite" in s
    sec = s.split("## My solution — SQLite",1)[1].split("## My solution — SQL Server",1)[0]
    found = re.findall(r"(?m)^" + chr(96)*3 + r"sql\s*\n(.*?)^"+chr(96)*3+r"\s*$",sec,re.S|re.M)
    assert found, (i,name)
    return found[0].strip()
def replay(i,sql,rows):
    con=sqlite3.connect(":memory:")
    try:
        con.executescript(DDL[i])
        for name, data in rows.items():
            if data:
                con.executemany("INSERT INTO "+name+" VALUES ("+
                                ",".join("?" for _ in data[0])+")",data)
        return con.execute(sql).fetchall()
    finally:
        con.close()
def check(i,sql,case,tier):
    rows,expected=case
    actual=replay(i,sql,rows)
    if i in ORDERED:
        assert actual==expected,(i,tier,actual,expected)
    else:
        assert sorted(actual,key=repr)==sorted(expected,key=repr),(i,tier,actual,expected)
    print("CTE %02d %s: PASS" % (i,tier))
def main():
    assert set(FILES)==set(range(1,13))
    assert set(SAMPLES)==set(SYNTHETIC)==set(range(1,11))
    for i in range(1,13):
        sql=source(i)
        if sql is None:
            print("CTE %02d source hash/pending-status: PASS (NO learner execution)"%i)
            continue
        check(i,sql,SAMPLES[i],"retyped-source-sample")
        check(i,sql,SYNTHETIC[i],"auditor-synthetic")
        if i==1:
            # Original statement does not specify query_name NOT NULL.
            # A GROUP BY creates NULL group, but two CTEs JOIN using "="
            # discard it. This is a counterexample, NOT a passed case.
            actual=replay(1,sql,{"Queries":[(None,"x",1,5)]})
            assert actual==[],actual
            assert actual != [(None,5.0,0.0)]
            print("CTE 01 KNOWN DIVERGENCE: nullable query_name drops its group")
    print("Pinned 12 sources; 10 source samples + 10 independent fixtures passed;"
          " 2 pending unchanged; 1 demonstrated nullable-name divergence;"
          " 0 official grades or new independent learner solutions.")
if __name__=="__main__":
    main()
