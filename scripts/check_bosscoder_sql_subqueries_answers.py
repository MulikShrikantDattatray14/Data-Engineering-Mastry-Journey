"""Read-only source-hash-pinned audit of six archived Bosscoder SQL SubQueries.

Evidence tiers: six retyped question samples (one archive sample conflicts with
its own ORDER BY instruction), six independent synthetic cases, and a
*known conditional divergence* case. Original recorded learner SQL is replayed
unchanged; official Academy grades and new learner solves are NOT claimed.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/6. SubQueries"
)
FILES = {
    1: ("1.Sql Students With Invalid Departments.md", "b5d577f6eb87307678ad0c7a0cd452f73827cecb"),
    2: ("2.Sql Employees Who Manager Has Left The Company.md", "b1c29c534f8713e8081f059f78598d0ea08c37b6"),
    3: ("3.Sql Exchange Seats.md", "086804660f60fbdaf845ba0b22a7239a13359641"),
    4: ("4.Sql Movie Ratings.md", "87423acd02db9e35f7b3c683b72d0fdc5e595338"),
    5: ("5.Sql Friend Requests Ii Who Has The Most Friends.md", "ed89cbc071439ff325b76434a4d6c1259754c0f7"),
    6: ("6.Sql Investments In 2016.md", "41bb01f14e6e7038b70158fc1588a5d9da1883ac"),
}
DDL = {
    1: "CREATE TABLE Departments(id INTEGER PRIMARY KEY,name TEXT);"
       "CREATE TABLE Students(id INTEGER PRIMARY KEY,name TEXT,department_id INTEGER);",
    2: "CREATE TABLE Employees(employee_id INTEGER PRIMARY KEY,name TEXT,manager_id INTEGER,salary INTEGER);",
    3: "CREATE TABLE Seat(id INTEGER PRIMARY KEY,student TEXT);",
    4: "CREATE TABLE Movies(movie_id INTEGER PRIMARY KEY,title TEXT);"
       "CREATE TABLE Users(user_id INTEGER PRIMARY KEY,name TEXT UNIQUE);"
       "CREATE TABLE MovieRating(movie_id INTEGER,user_id INTEGER,rating INTEGER,created_at TEXT,"
       "PRIMARY KEY(movie_id,user_id));",
    5: "CREATE TABLE RequestAccepted(requester_id INTEGER,accepter_id INTEGER,accept_date TEXT,"
       "PRIMARY KEY(requester_id,accepter_id));",
    6: "CREATE TABLE Insurance(pid INTEGER PRIMARY KEY,tiv_2015 REAL,tiv_2016 REAL,lat REAL NOT NULL,lon REAL NOT NULL);",
}
# Samples manually retyped from all six archived problem statements, independently
# of their saved solutions. #01 source's displayed order is WRONG relative to its
# explicit ORDER BY id ASC: expected below honors the contract, not that typo.
SAMPLES = {
    1: ({"Departments":[(1,"Electrical Engineering"),(7,"Computer Engineering"),
                        (13,"Bussiness Administration")],
         "Students":[(23,"Alice",1),(1,"Bob",7),(5,"Jennifer",13),(2,"John",14),
                     (4,"Jasmine",77),(3,"Steve",74),(6,"Luis",1),(8,"Jonathan",7),
                     (7,"Daiana",33),(11,"Madelynn",1)]},
        [(2,"John"),(3,"Steve"),(4,"Jasmine"),(7,"Daiana")]),
    2: ({"Employees":[(3,"Mila",9,60301),(12,"Antonella",None,31000),
                     (13,"Emery",None,67084),(1,"Kalel",11,21241),
                     (9,"Mikaela",None,50937),(11,"Joziah",6,28485)]},[(11,)]),
    3: ({"Seat":[(1,"Abbot"),(2,"Doris"),(3,"Emerson"),(4,"Green"),
                (5,"Jeames")]},
        [(1,"Doris"),(2,"Abbot"),(3,"Green"),(4,"Emerson"),(5,"Jeames")]),
    4: ({"Movies":[(1,"Avengers"),(2,"Frozen 2"),(3,"Joker")],
         "Users":[(1,"Daniel"),(2,"Monica"),(3,"Maria"),(4,"James")],
         "MovieRating":[(1,1,3,"2020-01-12"),(1,2,4,"2020-02-11"),
                        (1,3,2,"2020-02-12"),(1,4,1,"2020-01-01"),
                        (2,1,5,"2020-02-17"),(2,2,2,"2020-02-01"),
                        (2,3,2,"2020-03-01"),(3,1,3,"2020-02-22"),
                        (3,2,4,"2020-02-25")]},
        [("Daniel",),("Frozen 2",)]),
    5: ({"RequestAccepted":[(1,2,"2016/06/03"),(1,3,"2016/06/08"),
                            (2,3,"2016/06/08"),(3,4,"2016/06/09")]},[(3,3)]),
    6: ({"Insurance":[(1,10,5,10,10),(2,20,20,20,20),
                     (3,10,30,20,20),(4,10,40,40,40)]},[(45.0,)]),
}
# Separately designed cases testing stated key, threshold, date, tie and role rules.
SYNTHETIC = {
    1: ({"Departments":[(1,"A"),(3,"B")],
         "Students":[(1,"valid1",1),(2,"orphan",9),(3,"no enrollment",None),
                     (4,"valid3",3)]},[(2,"orphan")]),
    2: ({"Employees":[(1,"manager",None,70000),(2,"orphan-low",999,29999),
                     (3,"no-manager",None,20000),(4,"equal",999,30000),
                     (5,"active-low",1,29999),(6,"orphan-equal",888,30000)]},[(2,)]),
    3: ({"Seat":[(1,"A"),(2,"B"),(3,"C"),(4,"D")]},
        [(1,"B"),(2,"A"),(3,"D"),(4,"C")]),
    4: ({"Movies":[(1,"Alpha"),(2,"Beta"),(3,"Gamma")],
         "Users":[(1,"Zoe"),(2,"Amy"),(3,"Lee")],
         "MovieRating":[(1,1,3,"2020-02-29"),(2,1,5,"2020-03-01"),
                        (1,2,5,"2020-02-01"),(2,2,1,"2020-02-29"),
                        (3,3,4,"2020-01-31")]},
        [("Amy",),("Alpha",)]),
    5: ({"RequestAccepted":[(1,2,"2020-01-01"),(1,3,"2020-01-02"),
                            (1,4,"2020-01-03"),(2,3,"2020-01-04")]},[(1,3)]),
    6: ({"Insurance":[(1,10,12.50,1,1),(2,10,7.55,2,2),
                     (3,20,200,2,2),(4,30,5.25,3,3),
                     (5,30,4.33,4,4),(6,30,1,4,4)]},[(17.75,)]),
}
def source_queries(i):
    name, pin=FILES[i]
    b=(BASE/name).read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    assert actual==pin,(i,"ORIGINAL ARCHIVE CHANGED",actual,pin)
    t=b.decode("utf-8")
    assert "## Question and image" in t and "## Schema" in t
    assert "Solved (recorded)" in t and "UNRATED" in t
    assert "## Official solution\n\nNot provided for this practice set." in t
    section=t.split("## My solution — SQLite",1)[1].split("## My solution — SQL Server",1)[0]
    section=section.split("### Step-by-step explanation",1)[0]
    sqls=re.findall(r"(?ms)^"+chr(96)*3+r"sql\s*\n(.*?)^"+chr(96)*3+r"\s*$",section)
    assert len(sqls)==(2 if i==5 else 1),(i,"incorrect saved query count",len(sqls))
    return [s.strip() for s in sqls]

def replay(i,sql,fixtures):
    con=sqlite3.connect(":memory:")
    try:
        con.executescript(DDL[i])
        for table, rows in fixtures.items():
            if rows:
                con.executemany("INSERT INTO "+table+" VALUES ("+
                                ",".join("?" for _ in rows[0])+")",rows)
        return con.execute(sql).fetchall()
    finally:
        con.close()

def check(i,sqls,case,tier):
    fixtures, expected=case
    for k, sql in enumerate(sqls,1):
        result=replay(i,sql,fixtures)
        assert result==expected,(i,k,tier,result,expected)
        print("SubQueries %02d %s saved answer %d: PASS"%(i,tier,k))

def main():
    assert set(FILES)==set(DDL)==set(SAMPLES)==set(SYNTHETIC)==set(range(1,7))
    assert sqlite3.sqlite_version_info >= (3,39,0),("FULL OUTER JOIN needs SQLite 3.39+",sqlite3.sqlite_version)
    for i in range(1,7):
        sqls=source_queries(i)
        check(i,sqls,SAMPLES[i],"retyped-source-sample")
        check(i,sqls,SYNTHETIC[i],"independent-synthetic")
        if i==5:
            # The (requester_id,accepter_id) key permits inverse-direction pairs.
            # If friendships are unique undirected edges, this is a conditional
            # mismatch; the source does not explicitly prohibit both directions.
            case={"RequestAccepted":[(1,2,"2020-01-01"),(2,1,"2020-01-02"),
                                     (1,3,"2020-01-03")]}
            for idx, sql in enumerate(sqls,1):
                result=replay(i,sql,case)
                assert result==[(1,3)] and result!=[(1,2)],(idx,result)
                print("SubQueries 05 saved answer %d: KNOWN CONDITIONAL DIVERGENCE "
                      "(inverse edges counted twice; expected unique friends 2)"%idx)
    print("6 preserved source hashes; 6 retyped samples + 6 synthetic cases across "
          "7 historical queries each tier; 1 conditional reciprocal-edge divergence; "
          "1 archived sample ordering contradiction; 0 official Academy keys/grades "
          "and 0 new independent learner solves.")
if __name__=="__main__":
    main()
