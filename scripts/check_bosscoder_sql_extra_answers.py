"""Read-only source-hash-pinned Bosscoder SQL Extra Problems audit.

Six ORIGINAL archived SQLite learner queries are extracted and replayed unchanged
on six retyped displayed samples and six independently designed edge fixtures.
No independent learner completions, official answers or Academy grades inferred.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/7. Extra Problems"
)
FILES = {
    1: ("1.Sql Top Travellers.md", "67f2afab73dc12cfbe96f57cd7cc447b138f4039"),
    2: ("2.Sql Grand Slam Titles.md", "9f8ccaa6794ae8aa84af10dabf8fbce794795676"),
    3: ("3.Sql Customer Who Visited But Did Not Make Any Transactions.md",
        "2a665c1e0b273fff6537e0794437778ae08ecb38"),
    4: ("4.Sql Average Time Of Process Per Machine.md", "c408d6613da0b918a01de48d05eb6d03f15b585e"),
    5: ("5.Sql Managers With At Least 5 Direct Reports.md", "6ae47f312ccef8534992074eff7b0399f0c33a82"),
    6: ("6.Sql Average Selling Price.md", "1c770799a5a5c10dd2f213cf3407406364f2c69d"),
    0: ("0. Foundation Notes.md", "36180fadb344b88b9e7096f36802fcf49272ccff"),
}
DDL = {
    1: ("CREATE TABLE Users(id INTEGER PRIMARY KEY,name TEXT);"
        "CREATE TABLE Rides(id INTEGER PRIMARY KEY,user_id INTEGER,distance INTEGER);"),
    2: ("CREATE TABLE Players(player_id INTEGER PRIMARY KEY,player_name TEXT);"
        "CREATE TABLE Championships(year INTEGER PRIMARY KEY,Wimbledon INTEGER,Fr_open INTEGER,"
        "US_open INTEGER,Au_open INTEGER);"),
    3: ("CREATE TABLE Visits(visit_id INTEGER PRIMARY KEY,customer_id INTEGER);"
        "CREATE TABLE Transactions(transaction_id INTEGER PRIMARY KEY,visit_id INTEGER,amount INTEGER);"),
    4: ("CREATE TABLE Activity(machine_id INTEGER,process_id INTEGER,activity_type TEXT,"
        "timestamp REAL, PRIMARY KEY(machine_id,process_id,activity_type));"),
    5: ("CREATE TABLE Employee(id INTEGER PRIMARY KEY,name TEXT,department TEXT,managerId INTEGER);"),
    6: ("CREATE TABLE Prices(product_id INTEGER,start_date TEXT,end_date TEXT,price INTEGER,"
        "PRIMARY KEY(product_id,start_date,end_date));"
        "CREATE TABLE UnitsSold(product_id INTEGER,purchase_date TEXT,units INTEGER);"),
}
# Manually retyped from each archived ORIGINAL problem statement's displayed table.
# Expected results are from stated requirements; 'any order' answers compared as multisets.
SAMPLES = {
    1: ({"Users": [(1,"Alice"),(2,"Bob"),(3,"Alex"),(4,"Donald"),(7,"Lee"),
                    (13,"Jonathan"),(19,"Elvis")],
         "Rides": [(1,1,120),(2,2,317),(3,3,222),(4,7,100),(5,13,312),
                   (6,19,50),(7,7,120),(8,19,400),(9,7,230)]},
        [("Elvis",450),("Lee",450),("Bob",317),("Jonathan",312),
         ("Alex",222),("Alice",120),("Donald",0)]),
    2: ({"Players": [(1,"Nadal"),(2,"Federer"),(3,"Novak")],
         "Championships": [(2018,1,1,1,1),(2019,1,1,2,2),(2020,2,1,2,2)]},
        [(1,"Nadal",7),(2,"Federer",5)]),
    3: ({"Visits": [(1,23),(2,9),(4,30),(5,54),(6,96),(7,54),(8,54)],
         "Transactions": [(2,5,310),(3,5,300),(9,5,200),(12,1,910),(13,2,970)]},
        [(54,2),(30,1),(96,1)]),
    4: ({"Activity": [(0,0,"start",.712),(0,0,"end",1.520),
                     (0,1,"start",3.140),(0,1,"end",4.120),
                     (1,0,"start",.550),(1,0,"end",1.550),
                     (1,1,"start",.430),(1,1,"end",1.420),
                     (2,0,"start",4.100),(2,0,"end",4.512),
                     (2,1,"start",2.500),(2,1,"end",5.000)]},
        [(0,.894),(1,.995),(2,1.456)]),
    5: ({"Employee": [(101,"John","A",None),(102,"Dan","A",101),
                      (103,"James","A",101),(104,"Amy","A",101),
                      (105,"Anne","A",101),(106,"Ron","B",101)]},[("John",)]),
    6: ({"Prices": [(1,"2019-02-17","2019-02-28",5),
                    (1,"2019-03-01","2019-03-22",20),
                    (2,"2019-02-01","2019-02-20",15),
                    (2,"2019-02-21","2019-03-31",30)],
         "UnitsSold": [(1,"2019-02-25",100),(1,"2019-03-01",15),
                       (2,"2019-02-10",200),(2,"2019-03-22",30)]},
        [(1,6.96),(2,16.96)]),
}
# Different fixtures constructed to expose grain, role, key, temporal and arithmetic edge cases.
SYNTHETIC = {
    1: ({"Users": [(1,"Ana"),(2,"Ana"),(3,"Cy"),(4,"Dee"),(5,"Ela")],
         "Rides": [(1,1,5),(2,1,10),(3,2,6)]},
        [("Ana",15),("Ana",6),("Cy",0),("Dee",0),("Ela",0)]),
    2: ({"Players": [(1,"Same"),(2,"Same"),(3,"C"),(4,"Zero")],
         "Championships": [(2020,1,1,2,3),(2021,3,3,3,3)]},
        [(1,"Same",2),(2,"Same",1),(3,"C",5)]),
    3: ({"Visits": [(1,10),(2,10),(3,11),(4,11),(5,12),(6,12)],
         "Transactions": [(1,1,0),(2,1,7),(3,3,50),(4,4,0)]},
        [(10,1),(12,2)]),
    4: ({"Activity": [(0,0,"start",1.0),(0,0,"end",1.0),
                     (0,1,"start",0.0),(0,1,"end",4.0),
                     (0,2,"start",5.0),(0,2,"end",7.0),
                     (1,0,"start",0.0),(1,0,"end",3.333)]},
        [(0,2.0),(1,3.333)]),
    5: ({"Employee": [(101,"John","A",None),(108,"John","B",None),
                      (200,"E","A",None),(1,"a","A",101),(2,"b","A",101),
                      (3,"c","A",101),(4,"d","A",101),(5,"e","B",101),
                      (6,"f","A",108),(7,"g","A",108),(8,"h","A",108),
                      (9,"i","A",108),(10,"j","A",108),
                      (11,"k","A",200),(12,"l","A",200),(13,"m","A",200),
                      (14,"n","A",200)]},
        [("John",),("John",)]),
    6: ({"Prices": [(1,"2020-01-01","2020-01-10",5),
                    (1,"2020-01-11","2020-01-31",20),
                    (2,"2020-01-01","2020-01-31",10),
                    (3,"2020-01-01","2020-01-31",7),
                    (4,"2020-01-01","2020-01-31",42)],
         "UnitsSold": [(1,"2020-01-10",2),(1,"2020-01-11",1),
                       (1,"2020-01-11",1),(3,"2020-01-20",3),
                       (4,"2020-01-20",0)]},
        [(1,12.5),(2,0),(3,7),(4,0)]),
}
def source_text(i):
    name,pin=FILES[i]
    raw=(BASE/name).read_bytes()
    git_blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    assert git_blob==pin, ("ORIGINAL ARCHIVE CHANGED",i,git_blob,pin)
    return raw.decode("utf-8")

def source_query(i):
    src=source_text(i)
    assert "## Question and image" in src and "## Schema" in src
    assert "Solved (recorded)" in src
    assert "## Official solution\n\nNot provided for this practice set." in src
    assert ("MEDIUM" if i==2 else "UNRATED") in src
    part=src.split("## My solution — SQLite",1)[1].split("## My solution — SQL Server",1)[0]
    if "### Step-by-step explanation" in part:
        part=part.split("### Step-by-step explanation",1)[0]
    matches=re.findall(r"(?ms)^"+chr(96)*3+r"sql\s*\n(.*?)^"+chr(96)*3+r"\s*$",part)
    assert len(matches)==1,(i,"expected exactly ONE historical final SQLite query",len(matches))
    return matches[0].strip()

def execute(i,sql,fixture):
    con=sqlite3.connect(":memory:")
    try:
        con.executescript(DDL[i])
        for table,rows in fixture.items():
            if rows:
                con.executemany("INSERT INTO "+table+" VALUES ("+
                                ",".join("?" for _ in rows[0])+")",rows)
        return con.execute(sql).fetchall()
    finally:
        con.close()

def assert_result(i,sql,case,tier):
    fixture,expected=case
    actual=execute(i,sql,fixture)
    # 1 is ordered by distance DESC, then name ASC; other problems explicitly
    # accept any ordering. Duplicate identical rows MUST be retained.
    if i==1:
        assert actual==expected,(i,tier,actual,expected)
    else:
        assert sorted(actual)==sorted(expected),(i,tier,actual,expected)
    print("Extra Problems %02d preserved SQLite %s: PASS"%(i,tier))

def main():
    assert set(FILES)==set(range(7))
    assert set(DDL)==set(SAMPLES)==set(SYNTHETIC)==set(range(1,7))
    src0=source_text(0)
    for title in ("Keep entities with zero activity","Combine several roles with UNION ALL",
                  "Find facts with no matching child","Pair related rows with a self join",
                  "Count direct reports","Match date ranges before a weighted average"):
        assert title in src0,("missing foundation section",title)
    for i in range(1,7):
        sql=source_query(i)
        assert_result(i,sql,SAMPLES[i],"retyped-original-sample")
        assert_result(i,sql,SYNTHETIC[i],"independent-synthetic")
    print("7 original Git blob pins validated; 6 original SQL statements checked; "
          "6 source-retyped samples + 6 independent synthetic fixtures PASSED; "
          "0 Academy official keys/grades, 0 new learner completions. "
          "SQL Server parity, all provider hidden datasets and licensing still unverified.")
if __name__=="__main__":
    main()
