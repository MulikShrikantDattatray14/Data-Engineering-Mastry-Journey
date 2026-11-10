# Independent Bosscoder SQL Joins archive audit — 10 November 2026

## Provenance and limits

Individually inspected the **12 original archived Markdown assignment/problem files** in `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/2. Joins/`, including each source problem statement, output requirements, schema, preserved learner answer/pending state, and supplied official-solution field. The archive is preserved **unchanged**. This review is **not** direct access to the Academy grader, original private lecture executable environment, unseen datasets, or official answer keys. A "Solved (recorded)" badge documents an old archived status, **not a new learner attempt**, independent mastery or newly awarded score.

The read-only executable checker `scripts/check_bosscoder_sql_joins_answers.py` pins every source file by Git blob SHA-1 (not a PDF SHA-256), extracts the **exact** historical SQLite answer for the ten records that contain one, and tests on an independent in-memory fixture. The two genuinely pending assignments are checked for their unchanged pending state, not answered. Every fixture is **auditor-created** and is not a preserved platform dataset. Query order is compared only where required by the source prompt.

| # | Original archived problem | Statement/source inspection and historical status | Auditor fixture / observed semantic boundary |
| ---: | --- | --- | --- |
| 01 | Combine Two Tables | Inspected; recorded solved; source includes an equivalent lecture `LEFT JOIN` | Every person survives; orphan Address excluded; two addresses for a person yield two rows; absent addresses are SQL NULL. |
| 02 | Replace Employee ID With The Unique Identifier | Inspected; recorded solved; equivalent official lecture join included | Composite mapping key allows multiple `EmployeeUNI` rows for same `id`; LEFT JOIN repeats the employee, missing mapping is NULL. Source statement implies employee row but does not prescribe a selection rule for multiple IDs. |
| 03 | Product Sales Analysis I | Inspected; recorded solved; lecture official answer uses `INNER JOIN` | Archived `LEFT JOIN` retains a sale with an orphan product as a NULL product name; the source lecture query omits it. Foreign-key-valid original data hides this difference, so **official equivalence is conditional**, not certified for unconstrained fixtures. `price` is per-unit, not quantity-weighted revenue. |
| 04 | Sales Person | Inspected; **pending/unanswered** | Must include salespeople with no RED-company orders; **no original learner SQLite submission** to replay. Do not create one or award completion. |
| 05 | Delete Duplicate Emails | Inspected; **pending/unanswered** | Task requires mutation with smallest-`id` survivor, not just listing rows. No archived learner SQL to execute. Destructive `DELETE` should only ever be run on a disposable fixture if tested later. |
| 06 | Students And Examinations | Inspected; recorded solved; source lecture's alternative SQL has dialect/ambiguity caveats | Full student × subject grid retained, repeat attendance counted, no attendance = zero. Saved correlated-subquery answer works on an additional independently constructed grid. Source lecture's shown query has ambiguous unqualified `ORDER BY student_id` in SQLite and implicit CROSS JOIN / permissive grouping semantics; do not silently certify it as portable SQL Server. |
| 07 | African Cities | Inspected; recorded solved; no official SQL shown | Join only CITY.COUNTRYCODE=COUNTRY.CODE where continent is Africa; unmatched country codes do not count. |
| 08 | Average Population Each Continent | Inspected; recorded solved; no official SQL shown | City-weighted population average (not average of country averages), truncation of nonnegative fractional result by CAST; orphan city excluded. Negative populations are not valid domain fixtures, where CAST would differ from mathematical floor. |
| 09 | The Problem (The Report) | Inspected; recorded solved; no official SQL shown | Inclusive grade boundaries, grade descending, qualified name sorting for 8–10, mark sorting for 1–7. **Semantic discrepancy:** saved query returns the literal text `'NULL'`, **not SQL NULL**, for hidden low-grade names. The synthetic replay expects that *observed saved behavior* while flagging this as **not equivalent to a typed SQL NULL result** if that is required by the platform. No silent rewrite of historical answer. |
| 10 | Ollivander Inventory | Inspected; recorded solved; no official SQL shown | Non-evil wand only; minimum coins by **power and age**; power-desc, age-desc ordering. An equal-cost tie is not uniquely broken by prompt, so full tie-row/grader equivalence remains unknown. |
| 11 | Rising Temperature | Inspected; recorded solved; official SQL pending | Calendar-day adjacency including leap day; a warmer row after a missing calendar date cannot count as "yesterday." SQLite `date(..., '+1 day')` is dialect-specific; SQL Server conversion is separate evidence. |
| 12 | Seller With No Sales | Inspected; recorded solved; official SQL pending | No-sale sellers and sellers with only 2019/2021 sales retained; inclusive 2020-01-01, exclusive 2021-01-01 boundaries; NULL seller IDs in 2020 orders are ignored, preventing `NOT IN` poisoning. |

## Verification tiers

- **Indexed / statement inspected:** **12/12** original Bosscoder SQL Join records, original Git blob hashes pinned in the checker.
- **Historical learner answer present:** **10/12** saved SQLite SQL blocks; archive status is "Solved (recorded)" and "Unrated", not independent new credit.
- **Synthetic SQL fixture:** ten saved historical queries, one targeted fixture each; a passing run certifies those **specific input/output contracts only**.
- **Missing archived learner answer:** #04 and #05, both deliberately still **Pending / Not Solved Yet**.
- **Official answer supplied:** #01, #02, #03 and #06 include lecture-attributed SQL text, with important #03/#06 semantic caveats; other files explicitly have no supplied official key or mark it pending. Merely inspecting an attributed query is **not** platform confirmation.
- **Official full-source dataset, original platform grader, all variants and learner independently solved:** **not verified**. No new learner progress or mastery credited.

## Unresolved and follow-up

Investigate #03 whether foreign-key integrity is guaranteed by the actual Academy grader; #02 whether multiple employee mappings are permitted in real inputs; #06 official lecture query's SQL dialect and ambiguity; #09 text `'NULL'` versus SQL `NULL`; #10 tied least-cost wands. Verify both pending assignments only when genuine learner evidence exists. Original full dataset and any official answer sheets remain missing. A green CI on the new checker does not resolve those gaps, or other PNP SQL (205 statements inspected, **not** 205 official answers), Python mentorship PDF parity, Academy assignments, DE runtime, licensing and final source-to-concept signoff.

**Preservation and sync gate:** Do not modify original 744 archived files, historical learner attempts, live progress JSON or canonical notes for interactive-study activity while Issue #1 is open. Keep ChatGPT Library pending study records separate and **UNSYNCED** until full independent audit signoff and successful final CI.
