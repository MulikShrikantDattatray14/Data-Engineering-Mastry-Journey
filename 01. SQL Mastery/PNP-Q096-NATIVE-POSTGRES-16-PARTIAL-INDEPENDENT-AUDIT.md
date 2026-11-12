# PNP Q096: original slow report vs supplied key — native PostgreSQL 16 independent audit (PARTIAL)

**Date:** 13 November 2026. Auditor-owned evidence only; not a learner answer, authenticated supplier grade, original-data performance signoff or modification of source archives.

## Independently inspected preserved sources

- Original question: Original Mastery Snapshot / 1. SQL Mastery / 1. SQL Mastry / 2.PNP- foundations and practice / 15. Analytics and Performance / P096. Make a slow order report sargable and index it.md. Git blob **bcee556369e0af953521ec9ec1b8be96d71986e2**. The Markdown cites original 100 SQL Interview Questions PDF, Q096 pages 196–199. Its historical NOT SOLVED YET learner badge, SQLite/SQL Server Pending solutions and official-display Pending remain unchanged.
- Original bundled PostgreSQL key: same preserved PNP root / Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql, Q96 section. Git blob **7912c8e676621c513e0b635a40c6ee299404676e**. Both SHA pins enforced at runtime.
- Source task: rewrite date TO_CHAR and correlated line subqueries for indexed access, preserve every result row and sorted order, propose indexes and provide EXPLAIN. Output uses latest month implied by source SQL MAX(OrderDate), order amount at least 2000, counts of OrderDetails rows and COALESCE SUM(Quantity), sorted by amount descending then OrderID.
- Supplied key: half-open month bounds via DATE_TRUNC/MAX(OrderDate); LEFT JOIN OrderDetails, grouped counts and units. It includes **no index DDL or EXPLAIN plan**, so that explicit task requirement remains unfulfilled by the bundled key. The prose says current month although both archived SQL statements derive latest-data month: reporting-as-of policy unresolved.

## Unmodified native PostgreSQL execution: five independently asserted groups

The [source-pinned read-only Q096 checker](../scripts/check_pnp_96_native_postgres.py) extracts the entire original slow SQL and entire supplied key **without any dialect substitutions**, executes both inside the same transaction-scoped PostgreSQL TEMP-table fixtures, and checks exact ordered tuples against independent expected rows. No historical learner attempts, progress, canonical foundations or source archives were edited.

| Fixture | Observed native outcome | Status |
|---|---|---|
| Original three-order December example | Two ordered rows: order 2 has zero items/units; order 1 has 2 items, 3 units | **PASS** slow == key == printed source example |
| Independent February boundary, NULL amounts/dates/quantities, negative and multiple-line quantities | Two ordered rows: order 4 (3 items, 6 units), order 8 (2 items, 5 units); excludes January and 1999 amount | **PASS** exact source SQL equality and independently expected tuples |
| Latest data month with no qualifying orders | March qualifying orders followed by low-value April orders yields zero rows | **PASS** source equality; open source-as-of policy |
| Empty Orders and OrderDetails | Zero rows | **PASS** |
| Reviewer-only 18,000 Orders and 9,000 OrderDetails with actual native EXPLAIN | Both source SQL statements return **33 identical ordered rows**; before reviewer indexes default key-plan indexes []; after reviewer-created Orders(OrderDate,OrderID) and OrderDetails(OrderID), default key plan uses **idx_q096_orderdate** and **idx_q096_detail_order**. Independent half-open date-range query also uses idx_q096_orderdate | **PASS**, real PostgreSQL plan observation on synthetic data, NOT production benchmark or index DDL supplied by original answer |

**Code-head CI independently verified:** commit **9e69aa6d960222c76cd697a5f13c8c970823c3f7** passed [GitHub Actions run 43331808387](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43331808387), **94/94 general** validation steps and **14/14 native PostgreSQL** job steps successful (no failures or skips). The decoded native job **131578088790** confirms PostgreSQL server_version_num **160016**, immutable source hashes, four bounded fixtures, the 33-row synthetic comparison, and named PostgreSQL planner indexes. No original-Commerce-v2 dataset run or EXPLAIN ANALYZE performance benchmark was done.

## Evidence tiers and open gates

- **Indexed:** yes, one of the original 205 distinct P/A/X IDs.
- **Statement inspected:** yes, original source question/starter/sample/schema and bundled key individually inspected and pinned.
- **Synthetic test passed:** yes, four bounded native fixture groups and fifth reviewer-generated native EXPLAIN demonstration; these are not full-dataset parity or a provider grade.
- **Official answer verified:** **NO.** The bundled supplier key is not a provider-authenticated grading result and does not itself provide the task's index proposals or EXPLAIN.
- **Learner independently solved:** **NO.** Original NOT SOLVED YET / Pending status preserved.

**Outstanding:** original PDF render parity, original full Commerce Dataset v2 output/performance, explicit index proposal/provider plan and latest-month business-policy reconciliation, provider-authenticated correctness, other SQL semantics, all 205 source-to-answer/full-data checks, Python mentorship, Bosscoder Python/SQL lectures and pending assignments, W3Schools, other DE subject runtimes, integrity/licensing/privacy and final comprehensive signoff.

Q096's earlier bounded SQLite replay was already counted. Conservative clean supplied-key replay tally **remains 94/205**, not 95; native synthetic evidence does not double-count an ID or grant mastery. **Issue #1 stays OPEN.** Separate ChatGPT Library learner-study record and later learner logs remain **UNSYNCED** pending full independent audit and final comprehensive CI plus separately checked post-audit learning commits.
