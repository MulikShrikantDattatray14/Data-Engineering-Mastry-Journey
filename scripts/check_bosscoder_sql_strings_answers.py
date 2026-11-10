"""Read-only audit: 13 archived Bosscoder SQL strings/patterns/clause problems.

Replays the EXACT saved historical SQLite statements, never replaces learner SQL.
Fixtures are auditor-retyped example inputs and independent synthetic datasets.
Q05 uses an explicitly supplied Python REGEXP UDF: SQLite has no native REGEXP.
Inconsistent source sample outputs are reconciled to the stated input/contract
and NOT claimed as screenshot-exact or official Academy grading.
"""
import hashlib
import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / (
    "99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/"
    "1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/"
    "8. Advance string functions, regex and clause"
)
FILES = {
    0: ("0. Foundation Notes.md", "4e751596e99b178aa398e52ce189df2f0a3ca8cf"),
    1: ("1.Sql Patients With A Condition.md", "4b4b10207e42c96d6e98a6ee30f8ca7ce5407f91"),
    2: ("2.Sql Fix Names In A Table.md", "2d9a490090da16e25cac91371f7e4e8ee4c8d66a"),
    3: ("3.Sql Group Sold Products By The Date.md", "107565a243de042e063ed73f9c0f92d2d4dd5c50"),
    4: ("4.Sql Queries Quality And Percentage.md", "3e8fdc394a4272dc1c217444558252ca90807b41"),
    5: ("5.Sql Find Users With Valid E-Mails.md", "0100969d533b023b49f2d2e690410e1b21c870b2"),
    6: ("6.Sql List The Products Ordered In A Period.md", "0a8bfafa37806634af80853806b7d5fda4f5b819"),
    7: ("7.Sql List The Products Ordered In A Period.md", "817e62e99ca2d6bc3ebbe8f6bd9e214227399a6a"),
    8: ("8.Sql Group Sold Products By The Date.md", "142e92e1ff46caca38ce082412ea8d65f6b2eb8b"),
    9: ("9.Sql Patients With Condition.md", "3244eae2d2ab4ed902530447dabd3755b4168271"),
    10: ("10.Sql Japanese Cities Attributes.md", "1eb487b7556c19a2e6cb56fe71cfb69121c5b218"),
    11: ("11.Sql Higher Than Seventy Five Marks.md", "31dac52af42625c62340f834bbcd69d9a4b5ea98"),
    12: ("12.Sql Weather Observation Stations.md", "042c37f548a5ba2d3fe8f93678df6249280884d8"),
    13: ("13.Sql Weather Observation Station Ii.md", "854c64da3fe349d941a1ed420f2597e8edcb8123"),
}
DDL = {
    1: "CREATE TABLE Patients(patient_id INTEGER PRIMARY KEY, patient_name TEXT, conditions TEXT);",
    2: "CREATE TABLE Users(user_id INTEGER PRIMARY KEY, name TEXT);",
    3: "CREATE TABLE Activities(sell_date TEXT,product TEXT);",
    4: "CREATE TABLE Queries(query_name TEXT,result TEXT,position INTEGER,rating INTEGER);",
    5: "CREATE TABLE Users(user_id INTEGER PRIMARY KEY,name TEXT,mail TEXT);",
    6: ("CREATE TABLE Products(product_id INTEGER PRIMARY KEY,product_name TEXT,product_category TEXT);"
        "CREATE TABLE Orders(product_id INTEGER,order_date TEXT,unit INTEGER);"),
    7: ("CREATE TABLE Products(product_id INTEGER PRIMARY KEY,product_name TEXT,product_category TEXT);"
        "CREATE TABLE Orders(product_id INTEGER,order_date TEXT,unit INTEGER);"),
    8: "CREATE TABLE Activities(sell_date TEXT,product TEXT);",
    9: "CREATE TABLE Patients(patient_id INTEGER PRIMARY KEY, patient_name TEXT, conditions TEXT);",
    10: "CREATE TABLE CITY(ID INTEGER PRIMARY KEY,NAME TEXT,COUNTRYCODE TEXT,DISTRICT TEXT,POPULATION INTEGER);",
    11: "CREATE TABLE STUDENTS(ID INTEGER PRIMARY KEY,Name TEXT,Marks INTEGER);",
    12: "CREATE TABLE STATION(ID INTEGER PRIMARY KEY,CITY TEXT,STATE TEXT,LAT_N REAL,LONG_W REAL);",
    13: "CREATE TABLE STATION(ID INTEGER PRIMARY KEY,CITY TEXT,STATE TEXT,LAT_N REAL,LONG_W REAL);",
}
patients = [(1,"Daniel","YFEV COUGH"),(2,"Alice",""),(3,"Bob","DIAB100 MYOP"),
            (4,"George","ACNE DIAB100"),(5,"Alain","DIAB201")]
activities = [("2020-05-30","Headphone"),("2020-06-01","Pencil"),
              ("2020-06-02","Mask"),("2020-05-30","Basketball"),
              ("2020-06-01","Bible"),("2020-06-02","Mask"),
              ("2020-05-30","T-Shirt")]
products = [(1,"Leetcode Solutions","Book"),(2,"Jewels of Stringology","Book"),
            (3,"HP","Laptop"),(4,"Lenovo","Laptop"),(5,"Leetcode Kit","T-shirt")]
orders = [(1,"2020-02-05",60),(1,"2020-02-10",70),(2,"2020-01-18",30),
          (2,"2020-02-11",80),(3,"2020-02-17",2),(3,"2020-02-24",3),
          (4,"2020-03-01",20),(4,"2020-03-04",30),(4,"2020-03-04",60),
          (5,"2020-02-25",50),(5,"2020-02-27",50),(5,"2020-03-01",50)]
station_or = [(1,"ABC","CA",10,20),(2,"DEF","TX",15,25),
              (3,"BOSTON","MA",20,30),(4,"CHICAGO","IL",30,40),(5,"AUSTIN","TX",25,35)]
station_and = [(1,"Seattle","WA",47.6,-122.3),(2,"Austin","TX",30.3,-97.7),
               (3,"Chicago","IL",41.8,-87.6),(4,"Boston","MA",42.4,-71.1),
               (5,"Orlando","FL",28.5,-81.3)]
# Sample expected values obey the actual archived INPUT and written requirement.
# Q03/Q08 printed output writes "T-shirt" but input says "T-Shirt".
# Q05 printed result omits user_id 6 (david69@bosscoderacademy.com) even though valid.
SAMPLES = {
    1: ({"Patients":patients},[(3,"Bob","DIAB100 MYOP"),(4,"George","ACNE DIAB100")]),
    2: ({"Users":[(1,"aLice"),(2,"bOB")]},[(1,"Alice"),(2,"Bob")]),
    3: ({"Activities":activities},[("2020-05-30",3,"Basketball,Headphone,T-Shirt"),
                                  ("2020-06-01",2,"Bible,Pencil"),("2020-06-02",1,"Mask")]),
    4: ({"Queries":[("Dog","Golden Retriever",1,5),("Dog","German Shepherd",2,5),
                   ("Dog","Mule",200,1),("Cat","Shirazi",5,2),("Cat","Siamese",3,3),
                   ("Cat","Sphynx",7,4)]},
        [("Dog",2.5,33.33),("Cat",0.66,33.33)]),
    5: ({"Users":[(1,"Winston","winston@bosscoderacademy.com"),(2,"Jonathan","jonathanisgreat"),
                  (3,"Annabelle","bella-@bosscoderacademy.com"),
                  (4,"Sally","sally.come@bosscoderacademy.com"),
                  (5,"Marwan","quarz#2020@bosscoderacademy.com"),
                  (6,"David","david69@bosscoderacademy.com"),
                  (7,"Shapiro",".shapo@bosscoderacademy.com")]},
        [(1,"Winston","winston@bosscoderacademy.com"),
         (3,"Annabelle","bella-@bosscoderacademy.com"),
         (4,"Sally","sally.come@bosscoderacademy.com"),
         (6,"David","david69@bosscoderacademy.com")]),
    6: ({"Products":products,"Orders":orders},
        [("Leetcode Solutions",130),("Leetcode Kit",100)]),
    7: ({"Products":products,"Orders":orders},
        [("Leetcode Solutions",130),("Leetcode Kit",100)]),
    8: ({"Activities":activities},[("2020-05-30",3,"Basketball,Headphone,T-Shirt"),
                                  ("2020-06-01",2,"Bible,Pencil"),("2020-06-02",1,"Mask")]),
    9: ({"Patients":patients},[(3,"Bob","DIAB100 MYOP"),(4,"George","ACNE DIAB100")]),
    10: ({"CITY":[(1,"Tokyo","JPN","Tokyo",9000000),
                 (2,"New York","USA","New York",8400000),
                 (3,"Paris","FRA","Île-de-France",2100000)]},
         [(1,"Tokyo","JPN","Tokyo",9000000)]),
    11: ({"STUDENTS":[(1,"Ashley",81),(2,"Samantha",75),
                     (4,"Julia",76),(3,"Belvet",84)]},
         [("Ashley",),("Julia",),("Belvet",)]),
    12: ({"STATION":station_or},[("ABC",),("DEF",),("BOSTON",),("CHICAGO",),("AUSTIN",)]),
    13: ({"STATION":station_and},[("Boston",)]),
}
edge_patients = [(1,"False","XDIAB100"),(2,"Match1","DIAB1"),
                 (3,"Match2","COUGH DIAB100"),(4,"Other","DIAB201"),
                 (5,"Match3","DIAB199 FEVER"),(6,"No","CODIAB100")]
edge_activities = [("2020-01-02","Zoo"),("2020-01-01","apple"),
                   ("2020-01-01","Banana"),("2020-01-01","Banana"),
                   ("2020-01-02","Alpha"),("2020-01-02","Zoo")]
edge_products = [(10,"Alpha","X"),(11,"Zulu","X"),(12,"NoSale","X"),(13,"Carry","X")]
edge_orders = [(10,"2020-02-01",50),(10,"2020-02-29",50),
               (11,"2020-02-10",100),(13,"2020-01-31",110)]
edge_stations = [(1,"Oslo","AA",1,1),(2,"Austin","BB",2,2),
                 (3,"Chicago","CC",3,3),(4,"Boston","DD",4,4),
                 (5,"Aea","EE",5,5),(6,"Boston","FF",6,6),(7,"Bryn","GG",7,7)]
SYNTHETIC = {
    1: ({"Patients":edge_patients},[(2,"Match1","DIAB1"),
                                  (3,"Match2","COUGH DIAB100"),
                                  (5,"Match3","DIAB199 FEVER")]),
    2: ({"Users":[(3,"a"),(1,"mArY"),(4,"q"),(2,"BOB")]},
        [(1,"Mary"),(2,"Bob"),(3,"A"),(4,"Q")]),
    3: ({"Activities":edge_activities},[("2020-01-01",2,"Banana,apple"),
                                       ("2020-01-02",2,"Alpha,Zoo")]),
    4: ({"Queries":[("X","a",1,5),("X","b",2,1),("Y","c",4,4)]},
        [("X",2.75,50.0),("Y",1.0,0.0)]),
    5: ({"Users":[(1,"A","a@bosscoderacademy.com"),
                  (2,"B","b_.-9@bosscoderacademy.com"),
                  (3,"C","2bad@bosscoderacademy.com"),
                  (4,"D","x#y@bosscoderacademy.com"),
                  (5,"E","a@bosscoderacademy.com.evil"),
                  (6,"F","z@leetcode.com")]},
        [(1,"A","a@bosscoderacademy.com"),
         (2,"B","b_.-9@bosscoderacademy.com")]),
    6: ({"Products":edge_products,"Orders":edge_orders},
        [("Alpha",100),("Zulu",100)]),
    7: ({"Products":edge_products,"Orders":edge_orders},
        [("Zulu",100),("Alpha",100)]),
    8: ({"Activities":edge_activities},[("2020-01-01",2,"Banana,apple"),
                                       ("2020-01-02",2,"Alpha,Zoo")]),
    9: ({"Patients":edge_patients},[(2,"Match1","DIAB1"),
                                  (3,"Match2","COUGH DIAB100"),
                                  (5,"Match3","DIAB199 FEVER")]),
    10: ({"CITY":[(1,"Kyoto","JPN","Kansai",500),
                 (2,"Tokyo","JPN","Kanto",900),(3,"Osaka","jpn","Kansai",600),
                 (4,"LA","USA","CA",1000)]},
         [(1,"Kyoto","JPN","Kansai",500),(2,"Tokyo","JPN","Kanto",900)]),
    11: ({"STUDENTS":[(1,"Bobby",80),(2,"Robby",80),
                      (3,"Andy",75),(4,"Abby",100),(5,"Sally",90)]},
         [("Bobby",),("Robby",),("Abby",),("Sally",)]),
    12: ({"STATION":edge_stations},
         [("Austin",),("Chicago",),("Boston",),("Bryn",)]),
    13: ({"STATION":edge_stations},[("Boston",),("Bryn",)]),
}
# These prompts explicitly require an output ordering, independently of fixture insertion order.
ORDERED = {2,3,7,8,9,11}

def source_text(i):
    name,pin=FILES[i]
    raw=(BASE/name).read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    assert actual==pin,("ORIGINAL ARCHIVE BLOB HASH CHANGED",i,actual,pin)
    return raw.decode("utf-8")

def original_query(i):
    src=source_text(i)
    assert "## Question and image" in src and "## My solution — SQLite" in src
    assert "Solved (recorded)" in src and "## Official solution" in src
    assert ("Not provided for this practice set." in src
            or "Class-provided reference solution" in src)
    part=src.split("## My solution — SQLite",1)[1].split("## My solution — SQL Server",1)[0]
    # Only the FIRST fence after the original solution heading is the final saved query.
    # Long later teaching examples are never substituted for a learner's saved answer.
    m=re.search(r"(?ms)^"+chr(96)*3+r"sql\s*\n(.*?)^"+chr(96)*3+r"\s*$",part)
    assert m,("historical SQLite solution fence not found",i)
    return m.group(1).strip()

def run_query(i, sql, fixture):
    con=sqlite3.connect(":memory:")
    try:
        con.executescript(DDL[i])
        if i==5:
            # SQLite REGEXP is intentionally NOT built in; emulate documented
            # ASCII regular expression search via Python for THIS source case.
            con.create_function("regexp",2,
                lambda pattern,value: int(bool(re.search(pattern,value)))
                if value is not None and pattern is not None else None)
        for table, rows in fixture.items():
            if rows:
                con.executemany("INSERT INTO "+table+" VALUES ("+
                                ",".join("?" for _ in rows[0])+")",rows)
        return con.execute(sql).fetchall()
    finally:
        con.close()

def assert_fixture(i,sql,case,label):
    data,expected=case
    actual=run_query(i,sql,data)
    if i in ORDERED:
        assert actual==expected,(i,label,"ordered mismatch",actual,expected)
    else:
        assert sorted(actual)==sorted(expected),(i,label,"multiset mismatch",actual,expected)
    print("Bosscoder strings %02d original saved SQL %s: PASS"%(i,label))

def known_source_discrepancies():
    # 3/8 source screenshot spells T-shirt in output but T-Shirt in supplied input:
    # output is NOT exactly replayed, even though original SQL preserves data.
    assert "T-Shirt" in source_text(3) and "T-shirt" in source_text(3)
    assert "T-Shirt" in source_text(8) and "T-shirt" in source_text(8)
    # Q05 source includes David's valid bosscoderacademy address but output omits him.
    assert "david69@bosscoderacademy.com" in source_text(5)
    # Q04 has nullable query_name in schema; its saved join omits the NULL group,
    # and COUNT(query_name) is zero. Do not award an unconditional result PASS.
    sql=original_query(4)
    observed=run_query(4,sql,{"Queries":[(None,"match",1,5)]})
    assert observed==[(None,None,None)],("unexpected NULL-query-name diagnostic",observed)
    print("KNOWN SOURCE/CONTRACT LIMITATIONS: #03/#08 T-Shirt case, #05 omitted "
          "valid source user, #04 NULL query_name undercount reproduced; "
          "not labelled as source screenshot or universal semantic passes.")

def main():
    assert set(FILES)==set(range(14))
    assert set(DDL)==set(SAMPLES)==set(SYNTHETIC)==set(range(1,14))
    foundation=source_text(0)
    assert "LIKE and GLOB" in foundation and "Regular expressions" in foundation
    for i in range(1,14):
        sql=original_query(i)
        assert_fixture(i,sql,SAMPLES[i],"retyped-source-input / contract-expected")
        assert_fixture(i,sql,SYNTHETIC[i],"independent-synthetic")
    known_source_discrepancies()
    print("14/14 original Git-blob SHA pins verified; 13 historical SQLite statements "
          "inspected, 13 source-retyped plus 13 synthetic fixtures passed under "
          "the stated contract (Q05 uses Python REGEXP UDF). "
          "0 platform grades/official hidden-key verification; 0 new learner completions.")
if __name__=="__main__":
    main()
