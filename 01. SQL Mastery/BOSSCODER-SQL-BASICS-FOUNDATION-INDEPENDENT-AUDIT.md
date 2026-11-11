# Bosscoder SQL Basics — independent source-fence audit

**11 November 2026 — source inspected and SQLite tested; NOT Academy verified or learner mastered.**

Two archived files were individually read in `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/0. SQL basics/`. Their presence in the archive does not authenticate an Academy answer key.

| Preserved original file | Git blob SHA pinned in CI | Content |
| --- | --- | --- |
| `0. Foundation Notes.md` | `073c87bebb2d7c72cca97e970a06de965a87abe5` | 15 original SQLite SQL fences; ten printed result tables; constraints, transactions, view, index |
| `SQL Logical Query Processing Order.md` | `f5aee78c235bc3b5f25b82ae302a1f44d52950ef` | Eight original SQL fences, of which two are complete SQLite-compatible examples |

[Independent source-reading checker](../scripts/check_bosscoder_sql_basics_foundation.py) reads immutable archived source bytes at runtime and rejects unexpected Git blob hashes or fence counts. It tests source examples in disposable SQLite memory, without altering original Markdown or claiming SQL Server runtime verification.

## Every original SQL fence (in document order)

| Source and fence | Evidence and precise classification |
| --- | --- |
| Basics 01 | Original SELECT *, all five original Products rows reproduced, including two Pen rows, NULL stock and nullable supplier |
| Basics 02 | Original IS NULL returns only Mug, ID 3 |
| Basics 03 | Original stock > 0 returns IDs 1, 4, 5 in stated order |
| Basics 04 | Original integer-cents arithmetic yields numeric 2.0 and 5.0, equal to printed 2 and 5 (not proof of client formatting) |
| Basics 05 | Original WHERE/GROUP/HAVING yields Stationery count 3 |
| Basics 06 | Original SQLite-only PRAGMA enables FK checks for connection; explicitly not portable to SQL Server |
| Basics 07 | Original CREATE/INSERT/UPDATE/ALTER/SELECT sequence yields ScratchItems row (1, Pen, 5, NULL) |
| Basics 08 | Original DELETE/COUNT yields zero remaining rows |
| Basics 09 | Original DROP removes ScratchItems from sqlite_master |
| Basics 10 | Original BEGIN/UPDATE/SELECT yields (1,99) within same open transaction |
| Basics 11 | Original ROLLBACK/SELECT restores (1,10) in same connection |
| Basics 12 | Original CREATE VIEW succeeds; this is not a materialized-view test |
| Basics 13 | Original SELECT view produces three positive-stock source rows |
| Basics 14 | Original CREATE INDEX appears in sqlite_master; this does not prove optimizer usage |
| Basics 15 | Original optional Suppliers/Products DDL + five-row INSERT executed first as setup (source prints setup last) |
| Logical 01 | SQLite GROUP/HAVING/LIMIT is a placeholder template, not runnable as published |
| Logical 02 | SQL Server TOP query is inventoried, not SQL Server executed |
| Logical 03 | SQL Server OFFSET/FETCH query is inventoried, not SQL Server executed |
| Logical 04 | WHERE date comparison is a fragment |
| Logical 05 | HAVING COUNT fragment, no FROM/GROUP |
| Logical 06 | Original complete Invoice SUM alias ORDER BY query runs with auditor-synthetic (10,15,50) data; output 75 |
| Logical 07 | Original complete Courses GROUP/HAVING query runs on auditor data A×5, B×4, C×6; result set {A,C}, no order claim |
| Logical 08 | Window SUM OVER is an expression fragment, not a complete query |

**Test tiers:** All **15/15** original Basics SQL fences executed or effect-checked, including initial schema setup, connection PRAGMA and index/view DDL. **10/10** source-displayed output tables were manually transcribed as expected rows and checked against the unchanged original SQL, with numeric 2 vs 2.0 treated as equivalent. All **8/8** Logical Order SQL fences individually inventoried; **two complete source queries** run in SQLite using synthetic input; **six fragments/dialect-specific templates not executable as published** and not marked as runtime passes.

Four distinct auditor-synthetic groups were checked: SQL NULL comparison against IS NULL; rejected negative stock by CHECK; rejected orphan foreign key with FK enforcement explicitly on; and accepted/preserved actual NULL stock and supplier IDs. These are **not original course answers**. No source-output divergence was observed for the tested in-contract SQLite examples. SQL Server syntax behavior, all prose claims, official grader equivalence and runtime performance were not established.

## Cross-source teaching comparison

Read the current canonical [SQL Basics foundation](<00. SQL Basics/0. Foundation Notes.md>). Grain, table relationships, primary/foreign keys, elementary SELECT/DML, NULL, integrity constraints, FK enforcement and transaction purpose are already present. The original archive additionally illustrates candidate/composite key distinctions, CHECK/DEFAULT/UNIQUE NULL nuances, ALTER/DROP, explicit ROLLBACK before/after, views/indexes, and clause-order examples in greater depth. This is a **source-to-concept difference in this canonical chapter**, not proof that these details are absent from all other chapters. No canonical notes were altered, no duplication added and no interactive study-session record was imported.

**Do not conflate:** indexed (2 source files) ≠ source inspected (23 code fences) ≠ source result replay (10 literal-display contracts) ≠ synthetic tests (4 boundaries plus 2 demonstration datasets) ≠ official answer verified (**0**) ≠ learner independently solved (**0**). Neither foundation file contains newly graded Academy assignments.

**Unresolved before global signoff:** SQL Server executable equivalence, original provider authorship/rights, full Academy grading/notebook evidence, exhaustive PNP 205 official answer/dataset/dialect checks, other source fence coverage, W3Schools official page-by-page comparison, original Python PDF parity, DE cloud/Spark runtime evidence, full source-to-concept and licensing/privacy review, final latest-head CI. All original source archives, historical learner progress and separate ChatGPT Library study evidence remain untouched.
