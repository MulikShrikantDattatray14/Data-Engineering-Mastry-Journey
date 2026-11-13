# W3Schools SQL operators, patterns, copying, comments and administration — partial audit, 2026-11-14

**Evidence tiers:** 8 official W3Schools lessons individually statement inspected; 8 local source files read and immutable Git-blob-pinned; 14 independent local reviewer SQLite fixtures passed; one additional immutable source/index guard requires GitHub CI. **No official editor answer, independent learner submission, course grade or mastery is verified.** This is a provenance and semantics audit, not a copy of provider coursework.

## Official lessons individually inspected

| Primary source | Inspected contract and reviewer finding | Limits / cross-source mapping |
|---|---|---|
| [SQL Operators](https://www.w3schools.com/sql/sql_operators.asp) | Lists arithmetic, comparison, logical, compound and bitwise operators. Integer division and NULL comparisons can change output. | Bosscoder Basics and current Advanced SELECT cover corresponding primitives. Auditor tested SQLite integer vs decimal division; not proof of engine-independent results. |
| [SQL Wildcards](https://www.w3schools.com/sql/sql_wildcards.asp) | Percent means zero or more characters and underscore exactly one. Official page flags bracket and other special patterns as dialect-specific. | Bosscoder Intro/Advanced SELECT and current Strings warn SQLite LIKE bracket syntax differs; literal wildcard escaping tested. |
| [SQL SELECT INTO](https://www.w3schools.com/sql/sql_select_into.asp) | Makes a NEW table; tutorial cautions keys/indexes/NOT NULL may not transfer; WHERE 1=0 creates empty table schema. | This T-SQL style syntax fails in SQLite. Auditor used CREATE TABLE AS SELECT only as a limited SQLite analogue; copied rows do not imply constraints. |
| [SQL INSERT INTO SELECT](https://www.w3schools.com/sql/sql_insert_into_select.asp) | Appends selected source data to an EXISTING target; explicit target columns matter. | SQL Basics/Data Quality concepts. **Primary-source example ambiguity:** the lesson presents copying all columns Suppliers into Customers, yet its displayed Suppliers and Customers tables have different column counts; the example cannot be validated against the displayed schemas without further schema evidence. |
| [Stored Procedures](https://www.w3schools.com/sql/sql_stored_procedures.asp) | Illustrates SQL Server CREATE, EXEC, DROP PROCEDURE and parameter passing. | SQLite rejects SQL Server procedure syntax; generic compilation/performance improvement claims require workload and actual engine evidence. No SQL Server execution. |
| [SQL Comments](https://www.w3schools.com/sql/sql_comments.asp) | Single line dash-dash and block slash-star comments, with product qualifications. | SQLite synthetic tests verified comments ignored by parser but marker text within quoted string is data. |
| [BACKUP DATABASE](https://www.w3schools.com/sql/sql_backup_db.asp) | Explicitly SQL Server full and differential backups; differential needs a prior full backup. | SQLite rejects BACKUP DATABASE T-SQL; copying a table is not a verified restorable DB backup. No SQL Server backup/restore run. |
| [CREATE DATABASE](https://www.w3schools.com/sql/sql_create_db.asp) | CREATE DATABASE and administrative privileges; SQL Server catalog listing example. | SQLite does not implement this CREATE DATABASE form. No native database administrator privileges verified. |

This batch adds **eight distinct official lesson bodies** to 48 previously inspected = **56 directly inspected W3 SQL lesson pages**, NOT a complete W3Schools syllabus. The deliberately selected W3 link index does not contain any of these exact eight URLs. An absent selected link is not proven lost content or a learner completion.

## Directly inspected preserved local sources and Git blob SHA-1 pins

1. W3 index: 99. Reference Materials/W3SCHOOLS-TOPICS.md — c6328c2eb420f47e5585026a7bf3c0a4e41be720
2. SQL Basics: 01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md — d181dd73f96b1f2b7327600e290d52e9fd59a976
3. Advanced SELECT: 01. SQL Mastery/01. Advanced SELECT/0. Foundation Notes.md — 1ed1077d492a3bd9db25018650b5c1f3cae1371f
4. Strings: 01. SQL Mastery/08. SQL Strings and Patterns/0. Foundation Notes.md — 63649bd6ad3a44449873136d90d3bbb2c724dbab
5. Data Quality: 01. SQL Mastery/14. Data Quality and Deduplication/0. Foundation Notes.md — f19d2b0340649f2e481ac62705d9c28dd87ce761
6. Analytics: 01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md — d2743783106fe64ca087b39216184a87e97d1a8c
7. Original Bosscoder Basics: 99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/0. SQL basics/0. Foundation Notes.md — 073c87bebb2d7c72cca97e970a06de965a87abe5
8. Original Bosscoder Intro and Advanced Select: 99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/1. Intro to SQL and Advanced Select/0. Foundation Notes.md — 4951b326f4ac526140a0dcb517051f787c7b1970

These eight local records were directly read, not merely listed. Some database administration topics have only adjacent original/foundation coverage; their full original practical implementations or grading were NOT established.

## Test boundaries and remaining work

[Reviewer-only checker](../scripts/check_w3schools_sql_operators_copy_admin_cross_source.py) has 15 tests: 1 eight-file immutable Git blob/index guard and 14 auditor-authored in-memory SQLite fixtures. The synthetic fixtures cover arithmetic precedence/NULL, integer division, percent/underscore/escaped/bracket patterns, SQL Server SELECT INTO incompatibility, SQLite CTAS constraints and empty schema, INSERT SELECT column alignment and duplicate-key atomicity, stored-procedure syntax incompatibility, comment parsing, SQL Server backup syntax incompatibility, and CREATE DATABASE incompatibility. The 14 semantic tests passed in a local isolated SQLite run. Full 15-method CI must be independently checked on the exact resulting main SHA.

**Still NOT verified:** original W3Schools editor grading and exact demo schema, SQL Server native execution/backup recovery, MySQL/Oracle/PostgreSQL parity, native course answer keys, original PNP commerce data or original Python mentorship PDF, licensing/privacy, full source-to-concept audit and final signoff. Conservative PNP SQL supplied-key replay count remains **94/205**. Keep GitHub Issue #1 OPEN. Preserve original archives, learner records and canonical foundations. The separate ChatGPT Library learner-study record and later practice remain UNSYNCED until after complete independent audit signoff and separate successful post-sync CI.
