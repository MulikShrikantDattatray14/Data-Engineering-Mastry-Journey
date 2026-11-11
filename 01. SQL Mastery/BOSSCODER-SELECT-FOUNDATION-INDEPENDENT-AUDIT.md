# Bosscoder Intro to SQL / Advanced SELECT — independent foundation audit

**11 November 2026.** Preserved primary source [archived Foundation Notes](<../99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/1. Intro to SQL and Advanced Select/0. Foundation Notes.md>); immutable Git blob **`4951b326f4ac526140a0dcb517051f787c7b1970`**. All 11 topic sections, source-defined scratch schema and 18 original `sql`/`sqlserver` fenced blocks independently read. **No authenticated Academy answer key, grade, original Colab/dataset parity, or new learner completion is inferred.**

The [source-hash-pinned executable audit](../scripts/check_bosscoder_sql_select_foundation.py) reads the untouched original bytes, verifies their Git blob hash and original 18-fence order, runs the original setup in an in-memory SQLite database, and compares each of the **16 original SQLite query fences** against **16 individually transcribed printed output tables**. The 17th fence is SQL Server `TOP (2)`, inventoried only; the 18th fence is source scratch DDL/DML, executed (seven Customers, three Suppliers, four Products).

## Original teaching-example ledger

| Original fence | Contract independently inspected and reconstructed |
| --- | --- |
| 01 SELECT columns | Customer IDs 1–7 and 7 original rows |
| 02 projection with arithmetic | Pen, double_price 20 |
| 03 WHERE city | Berlin: IDs 1,4,6 |
| 04 AND | Germany + ID > 1: Clara, Arjun |
| 05 OR | Berlin/London: IDs 1,2,4,5,6 |
| 06 NOT | Not Germany: IDs 2,3,5,7 in source data |
| 07 IN | Germany/UK: IDs 1,2,4,5,6 |
| 08 BETWEEN | Inclusive 10/15/20: Pen, Notebook, Mug |
| 09 LIKE | Alice, Amir, Arjun |
| 10 DISTINCT | Four cities: Berlin, London, Paris, Rome |
| 11 two-key ORDER BY | Clara, Arjun, Alice, Sam, Bob, Amir, Mira |
| 12 UNION | Five distinct cities incl. Madrid |
| 13 UNION ALL | Ten total cities incl. Berlin ×4 and London/Rome ×2 |
| 14 IS NULL | Mug's unknown stock |
| 15 CASE | Available, Sold out, Unknown, Available for four Products |
| 16 ORDER BY / LIMIT | Bag 25, Mug 20 |
| 17 SQL Server TOP | One original dialect-specific fence, **not executed** |
| 18 CREATE TABLE / INSERT | Original chapter's scratch setup **executed**, no learner answer |

The chapter also provides non-fenced prose illustrations of AND/OR precedence, LIKE wildcard patterns, date bounds, INTERSECT/EXCEPT, dialect differences and NULLIF/COALESCE. These were **read**, not falsely claimed as executable original SQL fences. All 16 printed output-table contracts reproduced in SQLite with original sample rows only once the checker passes CI.

## Distinct auditor-created synthetic checks

Six separate synthetic SQLite groups (not original displayed outputs, not official answers): (1) precedence with and without parentheses, (2) BETWEEN with 9/10/20/21 and NULL bounds, (3) three-valued WHERE and IS NULL, (4) UNION deduplication versus UNION ALL duplicate preservation, (5) top-N deterministic tie-breaking on equal prices, and (6) SQLite default ASCII-case-insensitive LIKE on mixed-case names. The last property is not promised for arbitrary SQL Server collations. These checks are not an Academy grade.

## Source-to-canonical and W3Schools comparison

The present [canonical Advanced SELECT foundation](<01. Advanced SELECT/0. Foundation Notes.md>) already covers SELECT/WHERE, IN/BETWEEN, LIKE, DISTINCT, CASE, NULL, UNION/UNION ALL, deterministic LIMIT/TOP, logical clause order, price and time boundaries. The archived chapter provides more explicit customer/product row tables, original multi-operator precedence contrast, complete-row DISTINCT nuance, stock/CASE behavior, UNION count proof and a SQL Server TOP fence. Scope differences are **not** proof of absent concepts across all other chapters. No canonical notes were changed while the full audit remains open.

Four official W3Schools webpages were opened and topically compared on **11 November 2026** (not copied or reproduced): [SELECT](https://www.w3schools.com/sql/sql_select.asp) agrees on projection; [WHERE](https://www.w3schools.com/sql/sql_where.asp) on row filtering and comparisons; [LIKE](https://www.w3schools.com/sql/sql_like.asp) on percentage/underscore wildcards, with SQLite collation cautions; and [UNION](https://www.w3schools.com/sql/sql_union.asp) on distinct vs ALL duplicates. This is **4 checked topic pages**, not a complete W3Schools corpus audit.

**Evidence tiers:** indexed 1 chapter; statement/source inspected 11 sections/18 fences; original printed output comparisons 16; original setup 1; synthetic SQLite boundary groups 6; original SQL Server runtime 0; authenticated Academy official exercise answer/grade 0; newly independently solved learner exercise 0. No source source/output discrepancy in the 16 in-contract SQLite examples; prose examples and SQL Server equivalence remain outside the executable scope.

**Unresolved:** original provider rights/authorship and licensing/privacy; platform grades/Colab equivalence; PNP 205 original official-answer/dataset/dialect results; other untested SQL foundation examples and answer variants; Python original PDF rendered/graded parity; additional W3Schools pages; real DE Spark/cloud/orchestration runtimes; final source-to-concept and full CI signoff. All 744 original archives, historical learner attempts/progress, existing canonical foundations and separate Library study record remain unchanged.
