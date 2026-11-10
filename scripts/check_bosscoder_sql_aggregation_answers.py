"""Read-only Bosscoder Aggregation audit: replay immutable archived SQLite SQL.

Ten source-displayed sample input/output checks, ten independent synthetic
fixtures, one intentionally documented mismatch. Not official Academy grading.
"""
import hashlib
import re
import sqlite3
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/("99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/"
"1.Bosscoder Academy - foundational notes and Assignments/4. Aggregation")
PINS={
1:("1.Sql Immediate Food Delivery I.md","eff5f3b8094b2d1c1cb4a771dc49c14882fc8c27"),
2:("2.Sql The Latest Login In 2020.md","8967014e3acb5f71b46a4002f92e64efd06406df"),
3:("3.Sql Find Total Time Spent By Each Employee.md","38146e67620ba1a0088fb829b3c80816cf333cb9"),
4:("4.Sql Find Immediate Delivery Ii.md","69946e42d6a3704e34e874c1324f26079d146478"),
5:("5.Sql Game Play Analysis.md","02fdd44648241aa0009cd1edc6fd78baf430f98a"),
6:("6.Sql Monthly Transactions I.md","2e9d96928270ff20d3b38c925e6e5c7b1c571249"),
7:("7.Sql Game Play Analysis Ii.md","567a3298f79617ca622b919a6c1f565ecba7e2bb"),
8:("8.Sql Warehouse Manager.md","98807c304fbd887950015dbdd57a4ac0e7737c79"),
9:("9.Sql Customer Placing The Largest Number Of Orders.md","5e184772f2bf05f988efca3b45a74026f69e2bbb"),
10:("10.Sql Project Employees I.md","d979eb43a499f990ed2596d319ef9444aa87500e")}
DDL={
1:"CREATE TABLE Delivery(delivery_id INT,customer_id INT,order_date TEXT,customer_pref_delivery_date TEXT);",
2:"CREATE TABLE Logins(user_id INT,time_stamp TEXT);",
3:"CREATE TABLE Employees(emp_id INT,event_day TEXT,in_time INT,out_time INT);",
4:"CREATE TABLE Delivery(delivery_id INT,customer_id INT,order_date TEXT,customer_pref_delivery_date TEXT);",
5:"CREATE TABLE Activity(player_id INT,device_id INT,event_date TEXT,games_played INT);",
6:"CREATE TABLE Transactions(id INT,country TEXT,state TEXT,amount INT,trans_date TEXT);",
7:"CREATE TABLE Activity(player_id INT,device_id INT,event_date TEXT,games_played INT);",
8:"CREATE TABLE Warehouse(name TEXT,product_id INT,units INT); CREATE TABLE Products(product_id INT,product_name TEXT,Width INT,Length INT,Height INT);",
9:"CREATE TABLE Orders(order_number INT,customer_number INT);",
10:"CREATE TABLE Project(project_id INT,employee_id INT); CREATE TABLE Employee(employee_id INT,name TEXT,experience_years INT);"}
# Rows are transcribed independently from each ORIGINAL public Markdown question.
SAMPLES={
1:({"Delivery":[(1,1,"2019-08-01","2019-08-02"),(2,5,"2019-08-02","2019-08-02"),(3,1,"2019-08-11","2019-08-11"),(4,3,"2019-08-24","2019-08-26"),(5,4,"2019-08-21","2019-08-22"),(6,2,"2019-08-11","2019-08-13")]},[(33.33,)]),
2:({"Logins":[(6,"2020-06-30 15:06:07"),(6,"2021-04-21 14:06:06"),(6,"2019-03-07 00:18:15"),(8,"2020-02-01 05:10:53"),(8,"2020-12-30 00:46:50"),(2,"2020-01-16 02:49:50"),(2,"2019-08-25 07:59:08"),(14,"2019-07-14 09:00:00"),(14,"2021-01-06 11:59:59")]},[(6,"2020-06-30 15:06:07"),(8,"2020-12-30 00:46:50"),(2,"2020-01-16 02:49:50")]),
3:({"Employees":[(1,"2020-11-28",4,32),(1,"2020-11-28",55,200),(1,"2020-12-03",1,42),(2,"2020-11-28",3,33),(2,"2020-12-09",47,74)]},[("2020-11-28",1,173),("2020-12-03",1,41),("2020-11-28",2,30),("2020-12-09",2,27)]),
4:({"Delivery":[(1,1,"2019-08-01","2019-08-02"),(2,2,"2019-08-02","2019-08-02"),(3,1,"2019-08-11","2019-08-12"),(4,3,"2019-08-24","2019-08-24"),(5,3,"2019-08-21","2019-08-22"),(6,2,"2019-08-11","2019-08-13"),(7,4,"2019-08-09","2019-08-09")]},[(50.0,)]),
5:({"Activity":[(1,2,"2016-03-01",5),(1,2,"2016-03-02",6),(2,3,"2017-06-25",1),(3,1,"2016-03-02",0),(3,4,"2018-07-03",5)]},[(0.33,)]),
6:({"Transactions":[(121,"US","approved",1000,"2018-12-18"),(122,"US","declined",2000,"2018-12-19"),(123,"US","approved",2000,"2019-01-01"),(124,"DE","approved",2000,"2019-01-07")]},[("2018-12","US",2,1,3000,1000),("2019-01","DE",1,1,2000,2000),("2019-01","US",1,1,2000,2000)]),
7:({"Activity":[(1,2,"2016-03-01",5),(1,2,"2016-05-02",6),(2,3,"2017-06-25",1),(3,1,"2016-03-02",0),(3,4,"2018-07-03",5)]},[(1,"2016-03-01"),(2,"2017-06-25"),(3,"2016-03-02")]),
8:({"Warehouse":[("LCHouse1",1,1),("LCHouse1",2,10),("LCHouse1",3,5),("LCHouse2",1,2),("LCHouse2",2,2),("LCHouse3",4,1)],
"Products":[(1,"LC-TV",5,50,40),(2,"LC-KeyChain",5,5,5),(3,"LC-Phone",2,10,10),(4,"LC-T-Shirt",4,10,20)]},[("LCHouse1",12250),("LCHouse2",20250),("LCHouse3",800)]),
9:({"Orders":[(1,1),(2,2),(3,3),(4,3)]},[(3,)]),
10:({"Project":[(1,1),(1,2),(1,3),(2,1),(2,4)],"Employee":[(1,"Khaled",3),(2,"Ali",2),(3,"John",1),(4,"Doe",2)]},[(1,2.0),(2,2.5)])}
# Distinct from source examples: independently authored edge and boundary data.
SYNTHETIC={
1:({"Delivery":[(1,1,"2020-01-01","2020-01-01"),(2,1,"2020-02-01","2020-02-02"),(3,2,"2020-03-01","2020-03-01"),(4,3,"2020-03-02","2020-03-03")]},[(50.0,)]),
2:({"Logins":[(1,"2019-12-31 23:59:59"),(1,"2020-01-01 00:00:00"),(1,"2020-12-31 23:59:59"),(1,"2021-01-01 00:00:00"),(2,"2020-06-10 01:02:03"),(3,"2021-01-01 00:00:00")]},[(1,"2020-12-31 23:59:59"),(2,"2020-06-10 01:02:03")]),
3:({"Employees":[(1,"2020-01-01",1,3),(1,"2020-01-01",4,10),(1,"2020-01-02",5,8),(2,"2020-01-01",20,30)]},[("2020-01-01",1,8),("2020-01-02",1,3),("2020-01-01",2,10)]),
4:({"Delivery":[(1,1,"2020-01-01","2020-01-02"),(2,1,"2020-01-05","2020-01-05"),(3,2,"2020-01-02","2020-01-02"),(4,3,"2020-01-01","2020-01-01"),(5,3,"2020-02-01","2020-02-02"),(6,4,"2020-01-03","2020-01-04")]},[(50.0,)]),
5:({"Activity":[(1,1,"2020-01-01",0),(1,2,"2020-01-02",2),(2,1,"2020-01-03",2),(2,1,"2020-01-05",3),(3,1,"2020-12-31",0),(3,2,"2021-01-01",1),(4,2,"2020-03-01",0),(4,2,"2020-03-03",3)]},[(0.5,)]),
6:({"Transactions":[(1,"US","approved",100,"2020-01-01"),(2,"US","declined",200,"2020-01-31"),(3,"DE","declined",80,"2020-01-03"),(4,"US","approved",300,"2020-02-01")]},[("2020-01","US",2,1,300,100),("2020-01","DE",1,0,80,0),("2020-02","US",1,1,300,300)]),
7:({"Activity":[(1,2,"2020-01-04",0),(1,3,"2020-01-07",5),(2,2,"2020-01-01",1),(2,3,"2020-01-02",2),(3,2,"2020-01-03",7)]},[(1,"2020-01-04"),(2,"2020-01-01"),(3,"2020-01-03")]),
8:({"Warehouse":[("A",1,1),("A",2,2),("B",2,3)],"Products":[(1,"A",2,3,4),(2,"B",1,1,5)]},[("A",34),("B",15)]),
9:({"Orders":[(1,10),(2,20),(3,20),(4,20),(5,30),(6,30)]},[(20,)]),
10:({"Project":[(1,1),(1,2),(2,1),(2,3)],"Employee":[(1,"A",1),(2,"B",2),(3,"C",7)]},[(1,1.5),(2,4.0)])}
def archived_sql(i):
    name,sha=PINS[i]
    data=(BASE/name).read_bytes()
    assert hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()==sha,(i,name)
    txt=data.decode("utf-8")
    for marker in ("## Question and image","## Schema","## My solution — SQLite","## My solution — SQL Server","## Official solution","Solved (recorded)","UNRATED"):
        assert marker in txt,(i,marker)
    section=txt.split("## My solution — SQLite",1)[1].split("## My solution — SQL Server",1)[0]
    fence=chr(96)*3
    queries=re.findall(re.escape(fence)+r"sql\s*\n(.*?)"+re.escape(fence),section,re.S)
    assert queries,(i,name)
    return queries[0]
def replay(i,query,rows):
    con=sqlite3.connect(":memory:")
    try:
        con.executescript(DDL[i])
        for table,data in rows.items():
            if data:
                placeholders=",".join("?" for _ in data[0])
                con.executemany("INSERT INTO "+table+" VALUES ("+placeholders+")",data)
        return con.execute(query).fetchall()
    finally:
        con.close()
def check(i,query,data,tier):
    rows,expected=data
    found=replay(i,query,rows)
    if i==3:
        assert found==expected,(i,tier,found,expected)
    else:
        assert sorted(found,key=repr)==sorted(expected,key=repr),(i,tier,found,expected)
    print(f"Aggregation {i:02d} {tier}: PASS")
def main():
    assert set(PINS)==set(SAMPLES)==set(SYNTHETIC)==set(range(1,11))
    for i in range(1,11):
        sql=archived_sql(i)
        check(i,sql,SAMPLES[i],"retyped-source-sample")
        check(i,sql,SYNTHETIC[i],"auditor-synthetic")
        if i==6:
            # Deliberate expected divergence: nullable country is not forbidden
            # by archived schema. SQL NULL does not join to SQL NULL.
            observed=replay(6,sql,{"Transactions":[(1,None,"approved",80,"2020-01-03")]})
            assert observed==[("2020-01",None,1,0,80,0)],observed
            assert observed!=[("2020-01",None,1,1,80,80)]
            print("Aggregation 06 KNOWN DIVERGENCE: nullable country undercounts approved metrics")
    print("10 immutable statements/answers pinned; 10 displayed samples + 10 synthetic fixtures passed; 1 documented divergence. 0 official Academy grades; 0 new learner completions.")
if __name__=="__main__":
    main()
