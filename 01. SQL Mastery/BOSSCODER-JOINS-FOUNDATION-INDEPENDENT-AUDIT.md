# Independent Bosscoder SQL Joins foundation audit — 11 November 2026

## Primary source and evidence boundary

Independently inspected the entire untouched archived [Joins Foundation Notes](<../99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/2. Joins/0. Foundation Notes.md>), Git blob SHA-1 **`b65b32c17a8c35a3130a3164799c307bc02dbf17`**. Inspected all **11 main numbered teaching sections**, the optional scratch-data section, the original displayed input/output tables and **20 SQL code fences**. Exactly **19** are executable original teaching SELECT/CTE queries with a displayed **Result** table; one last fence is the original scratch schema/inserts. This review is **different from** the existing [12 archived Joins assignment source audit](BOSSCODER-JOINS-INDEPENDENT-AUDIT.md); the two pending original assignments #04/#05 remain pending.

The [read-only, source-hash-pinned checker](../scripts/check_bosscoder_sql_joins_foundation.py) reads the source without writing to it, executes the original schema and inserts in disposable SQLite, asserts counts for eight sample tables, and replays **all 19 unmodified teaching queries**, comparing the ordered rows to **19 separately transcribed archived printed output tables**. SQL NULLs use typed `None` in expected rows; the checker does not silently equate SQL NULL to the text 'NULL'. RIGHT and FULL OUTER JOIN examples require SQLite **3.39.0+**; the checker fails explicitly rather than crediting unsupported executions. This is **not** a live SQL Server execution, an Academy grader, a private notebook, or an official solution to any assignment.

## One-by-one original sample contracts

| Fence | Original archived teaching example | Printed sample result independently reconstructed |
| ---: | --- | --- |
| 01 | Customers ordered by ID | 4 rows Ada, Ben, Cara, Dev |
| 02 | Orders ordered by ID | 4 rows: 101–104, last with SQL NULL customer ID |
| 03 | INNER JOIN | 3 order rows: Ada ×2 and Ben ×1 |
| 04 | LEFT JOIN | 5 rows incl. unmatched Cara and Dev as NULL |
| 05 | COUNT(*) vs COUNT(order_id) | four customers; no-order counts differ 1 vs 0 |
| 06 | RIGHT JOIN | four orders including unassigned #104 |
| 07 | FULL OUTER JOIN | six rows: 3 matched, 2 customer-only, 1 order-only |
| 08 | Older-SQLite FULL emulation via UNION ALL | same six join events with customer IDs, including #104 |
| 09 | Paid-order predicate in ON | four customers preserved; 2 paid matched |
| 10 | Paid-order predicate in WHERE | only Ada and Ben |
| 11 | EXISTS semijoin | Ada and Ben once each |
| 12 | NOT EXISTS anti-join | Cara and Dev |
| 13 | LEFT JOIN anti-match on non-null key | Cara and Dev |
| 14 | CROSS JOIN channels × two customers | four customer/channel pairs |
| 15 | Employee self-join on manager | Asha(NULL), Ben(Asha), Cara(Asha), Dara(Ben) |
| 16 | Composite order+line join | three lines matched to correct notes |
| 17 | Inclusive tier/date range join | Bronze, Silver, Gold; #104 NULL tier |
| 18 | Direct two-child join fan-out | order 101 produces four line×payment rows |
| 19 | Preaggregate child CTEs before join | four orders, totals 30/30, 0/0, 40/40, 0/0 |
| 20 | Original optional CREATE TABLE/INSERT setup | eight original disposable sample tables; not an answer/output SELECT |

Each result comparison is bounded to the archived chapter's **printed input and output**, not an independently obtained Academy dataset. Fences 6–7 were evaluated only in SQLite with supported RIGHT/FULL syntax, not on SQL Server. Prose and troubleshooting advice were statement-inspected, not converted into imaginary executable source questions.

## Five independent synthetic counterexample groups

These are **auditor-authored** examples, separate from the nineteen original displayed samples: (S1) a NULL child identifier poisons `NOT IN` but `NOT EXISTS` correctly retains nonbuyers; (S2) moving a paid filter between `ON` and `WHERE` changes the preserved parents; (S3) omitting line_number from a composite join doubles matches from 2 to 4; (S4) overlapping effective-date tiers create two matches for one event and require an unspecified business policy; (S5) two identical legitimate line amounts × two payments create 4 joined rows, summed line amount 40 rather than 20, while `SUM(DISTINCT)` incorrectly returns 10. Passing these groups verifies **these synthetic fixtures only**, not a provider answer key.

## W3Schools and canonical comparison

Four distinct official public W3Schools pages were opened and compared on 11 November 2026: [SQL Joins](https://www.w3schools.com/sql/sql_join.asp) correctly classifies INNER/LEFT/RIGHT/FULL preservation; [SQL LEFT JOIN](https://www.w3schools.com/sql/sql_join_left.asp) (or [LEFT JOIN keyword reference](https://www.w3schools.com/sql/sql_ref_left_join.asp)) confirms NULL-extended unmatched rows; [SQL FULL JOIN](https://www.w3schools.com/sql/sql_Join_full.asp) describes preservation from either side; [SQL EXISTS operator](https://www.w3schools.com/sql/sql_exists.asp) describes a boolean existence test. These source concepts agree at the stated level; their illustrative engines are **not** proof of universal dialect support. W3Schools alone does not certify SQLite `RIGHT/FULL` portability, or the chapter's advanced grain/tier/fan-out rules. This is **four pages checked**, not the whole W3Schools topic list.

The existing [canonical Joins Foundation](<02. Joins/0. Foundation Notes.md>) already explains INNER/LEFT, anti-match, ON/WHERE and join multiplication, with specific PNP grain, product-coverage and pair-counting examples. The original Joins chapter is more detailed about RIGHT/FULL fallback, EXISTS vs NOT IN with NULL, typed COUNT differences, composite keys, temporal effective-date joins, and concrete two-child preaggregation. Whether those are covered throughout *other* canonical topics remains to be verified in final unique-concept review; **no canonical learner notes modified** during the audit.

## Status and unresolved blockers

**Indexed:** one full archived teaching chapter. **Statement/content inspected:** 11 numbered sections, scratch setup, 20 code fences and 19 printed result tables. **Original source-displayed output verified (SQLite):** 19 contracts *only if the new CI checker passes*. **Synthetic tests:** five independent groups *only if CI passes*. **Authenticated Academy official answer keys/grades verified:** 0. **SQL Server runtime verification:** 0. **New learner independently solved course exercises:** 0. Old archival 'Solved (recorded)' and genuinely unsolved assignment statuses remain exactly as found.

Open gaps: source licensing/right to republish third-party assets, Academy notebook environment and official platform answers/grades, complete PNP 205 original dataset and official-key output verification, rendered Python mentorship PDF parity and graded original Python materials, remaining W3Schools topics, true Spark/cloud/ETL runtime, comprehensive distinct-source-to-concept mapping and final current-head CI signoff. A green fixture run is only *scoped regression evidence*, not complete audit signoff. **Keep GitHub Issue #1 open and the separate Library learning sync deferred; never overwrite the original archive or learner progress.**
