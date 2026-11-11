# Independent Bosscoder SQL Sorting and Grouping foundation audit — 11 November 2026

## Provenance and evidence boundary

Original unchanged archived [Sorting and Grouping foundation chapter](<../99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/3. Sorting and Grouping/0. Foundation Notes.md>) was individually read in full: source Git blob SHA-1 **`11deb453f5249389014ac450fa1e3d6089b118dc`**. It has 10 numbered sections, practice links, and 15 language-tagged SQL fences: 13 executable SQLite SELECT/CTE teaching examples with 13 separately displayed result tables, one SQL Server `TOP (2)` translation (not executed), and one complete original scratch-schema/insert setup.

The [read-only SHA-pinned checker](../scripts/check_bosscoder_sql_grouping_foundation.py) extracts **the unchanged SQL** directly from that archive, runs its complete final setup only in a disposable SQLite memory database, and tests all 13 SELECT/CTE fences against the **13 original printed result tables independently retyped by the auditor**, retaining their printed sort order and SQL NULL as Python `None`. It then runs six **separate auditor-authored** semantic boundary groups. All statement and output claims are strictly limited to this exact source, engine and fixture; this is **not** a certified Academy grader, source-distributed hidden dataset, SQL Server engine, learner submission, or independent mastery.

This is a **foundation-teaching-example** audit, separate from the already documented [11 Bosscoder Sorting/Grouping assignment records](BOSSCODER-GROUPING-INDEPENDENT-AUDIT.md). Those previously archived recorded learner statuses and the original files are untouched. There are **zero newly solved coursework assignments**.

## Complete original teaching-fence ledger

| Original fence (all in archive order) | Source-visible contract independently transcribed / checker assertion | Evidence class |
| ---: | --- | --- |
| 01 | Exclude unknown amount; sort amount descending then order_id ascending: **6 rows** (100 ×4, 50, 20; IDs 1,4,6,7,2,3). | Printed-source output replay |
| 02 | Sort/limit to **exactly two** rows: `(1,100),(4,100)` (not all tied maximum orders). | Printed-source output replay |
| 03 | SQL Server `TOP (2)` alternative has corresponding source syntax, but **no SQL Server runtime verification**. | Syntax inventoried only |
| 04 | Explicit NULL-last sort: known amounts 20,50,100 ×4 followed by **two SQL NULL values**. | Printed-source output replay |
| 05 | CASE business-priority sort: pending #5/#8, paid #1/#2/#4/#6/#7, returned #3. | Printed-source output replay |
| 06 | Group one row/customer: counts 3,2,2,1; sums 170,100,200,NULL; averages 56.67,100,100,NULL. | Printed-source output replay |
| 07 | Composite customer/product keys: **six distinct ordered groups** including customer 1/product 10 count 2. | Printed-source output replay |
| 08 | COUNT(*) vs COUNT(product_id) vs COUNT(DISTINCT product_id) per customer, including repeated products. | Printed-source output replay |
| 09 | Distinct two-column pair count **6**, via derived `SELECT DISTINCT`, not ID string concatenation. | Printed-source output replay |
| 10 | Row-filter `status='paid'` precedes group HAVING sum ≥150; customers 1=150 and 3=200. | Printed-source output replay |
| 11 | Join/group on unique customer_id **and** name: both distinct Anas retained with totals 150 and 200. | Printed-source output replay |
| 12 | Find every earliest-day order per product, retaining both tied product-10 rows #1 and #4; product 20 #6. | Printed-source output replay |
| 13 | Paid purchases cover all 2 catalog products: customers 1 and 3, after catalog JOIN. | Printed-source output replay |
| 14 | Two paid product flags AND absence of returned event: customer 3 only. | Printed-source output replay |
| 15 | Original `CREATE TABLE`/`INSERT` setup: **4 Customers, 2 Products, 8 Orders**; executed in memory, never persisted. | Source data setup execution |

The checker labels its SQLite SELECT examples 01–13 by **SQL-SELECT ordinal**, since source fence 03 is SQL Server only and fence 15 is setup. The table above instead uses the archive's **all-language fence ordinal**. Both numbering schemes are explicitly distinguishable and do not double-count.

## Six independent synthetic boundary groups (NOT printed source answers)

1. **Group identity / NULL-only amounts:** two separate customers named `Same` must stay separate; a customer with only NULL amounts has COUNT(*)=1 but SUM/AVG=NULL. Replayed the archived grouped and identity queries.
2. **Event grain vs distinct composite pairs:** repeated events don't add new unique pairs; distinct-pair query also correctly distinguishes `(customer_id,product_id)=(1,23)` and `(12,3)` which a naive concatenation could collide.
3. **Required-product coverage + empty catalog:** two paid buyers cover both catalog SKUs, whereas deleting the catalog yields no group rows in the source query. That is a documented scope **limitation** for an interpretation requiring vacuous coverage of every customer, not an unexpected checker pass.
4. **Negative evidence in HAVING:** adding a returned event with a NULL amount excludes one previously valid customer when the original conditional-HAVING query is replayed; pre-filtering returns with WHERE would be incorrect.
5. **Earliest-date ties across entities:** both earliest orders of one product must survive; an unrelated product with the same date must not be joined into that product's result.
6. **Deterministic ORDER BY/NULL last:** independent 7-order data yields an exact two-row top-N tie boundary and an explicit NULL-last ordered list.

All six groups are auditor-authored; they cannot establish official Academy correctness or coverage of all possible constraints. The chapter explicitly notes that its paid-order grouping approach for "all products" does not return every customer when the catalog is empty, and that deciding an empty-set interpretation requires a different starting population. This caveat is preserved, not silently 'fixed' in the original.

## Official W3Schools topical comparisons (reviewed 11 November 2026)

- [ORDER BY](https://www.w3schools.com/sql/sql_orderby.asp): shared ascending/descending and multi-key ordering, but original Bosscoder chapter adds the explicit NULL-last CASE flag, tied-limit distinction and SQL Server TOP dialect caveat.
- [SELECT DISTINCT](https://www.w3schools.com/sql/sql_distinct.asp): shared deduplication and COUNT(DISTINCT); Bosscoder chapter additionally demonstrates safe counting of **composite** distinct pairs by derived table and warns about concatenation collisions.
- [COUNT](https://www.w3schools.com/sql/sql_count.asp): W3Schools distinguishes COUNT(*), COUNT(column) and COUNT(DISTINCT); original chapter illustrates duplicate product events and SQL NULL-only aggregate groups.
- [GROUP BY](https://www.w3schools.com/sql/sql_groupby.asp): both group after filtering and aggregate by group; the archived chapter explicitly distinguishes entity ID vs duplicated display name and pair-group grain.
- [HAVING](https://www.w3schools.com/sql/sql_having.asp): both distinguish row-level WHERE and aggregate HAVING; the archived chapter adds a source-visible A-and-B-but-not-returned conditional SUM pattern that must not discard disqualifying events early.

Only the concepts and source examples from these five official public tutorial pages are compared; we do **not** claim exhaustive W3Schools curriculum parity, nor copy any W3Schools lesson content. The W3Schools pages are references; they are **not** Academy grading keys.

## Integrity / limitations / open signoff

- **Source inspected:** one immutable full chapter + all 15 language-tagged SQL fences and printed output tables.
- **Source-output verified under SQLite:** 13 unchanged SELECT/CTE fences on source's literal setup, checked against 13 manually reconstructed original printouts. Source setup is one separate executed SQL fence.
- **Synthetic semantic checks:** six independent fixture groups. **Official Academy answer/grade verified:** none. **SQL Server runtime verified:** none. **New learner independently solved:** none.
- No hidden Academy datasets, live notebook cell-state, SQL Server native collations, physical SQL execution plans, or provider grades were available for this source review. The source `ORDER BY`/LIMIT clauses are checked for the displayed SQLite output only, not projected to every dialect.
- The public archived chapter and original 11 assignment files have not been rewritten. All original 744 files and historical learner attempts/progress remain protected by the existing repository validation. Neither canonical SQL/Python notes nor pending study records are touched.
- **Full Issue #1 remains open**: 205 PNP SQL official answer/dataset verification, remaining Bosscoder foundation teaching examples, Academy notebook/provider grading, private mentorship original 80-page PDF parity, W3Schools remaining source comparisons, native other-DE runtime evidence, licensing/privacy clearance, final concept coverage/integrity signoff, and **post-audit-only learning sync** are still outstanding. Even passing this checker and whole-workflow CI will not close Issue #1.
