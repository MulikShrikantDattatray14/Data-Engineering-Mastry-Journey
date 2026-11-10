# Independent Bosscoder SQL Intro / Advanced SELECT audit — 2026-11-10

**Scope:** the 13 physically archived SQL assignment records under
[`Original Mastery Snapshot / SQL / Bosscoder / 1. Intro to SQL and Advanced Select`](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/1.%20SQL%20Mastery/1.%20SQL%20Mastry/1.Bosscoder%20Academy%20-%20foundational%20notes%20and%20Assignments/1.%20Intro%20to%20SQL%20and%20Advanced%20Select/).
Read the preserved statement, schema, sample, previously recorded SQLite answer(s),
SQL Server conversion and visible official-solution field **for each of the 13**.
Every record is historically marked `SOLVED / UNRATED` with a recorded date of
2026-10-26. **Preservation of that historical label is not a new independent solve,
an Academy grade, or an audit-certified official answer.**

## Strict evidence boundary

- **Indexed:** all 13 appear in `BOSSCODER-PROBLEM-INDEX.md`.
- **Statement inspected:** 13/13 archived Markdown records, individually read and pinned by their original Git blob SHA-1.
- **Archived learner SQL replayed on SQLite:** the selected final query **directly extracted from each immutable Markdown record**, rather than rewritten in a test, is exercised by [this checker](../scripts/check_bosscoder_sql_intro_answers.py). Each local test dataset reconstructs visible sample rows and adds auditor boundary rows. Successful execution is an **archived-solution synthetic/sample-fixture pass**, **not** the course's private full dataset or independent 2026-11-10 learner answer.
- **Visible supplied handout answer:** entries 1–5 have an `Official solution` block labeled as supplied from a handout in the archive. This identifies source-attributed text, **not independently validated Academy grading**. Entries 6–13 explicitly say no official solution supplied. Do not promote these to `official answer verified` without independent authoritative original data.
- **Historical learner completion:** prior repository `SOLVED` badges and answer text remain exactly as recorded; **zero new independently solved assignments credited** by this audit.
- **SQL Server:** documented conversion code was reviewed visually, **not executed on a SQL Server instance**. No dialect parity signoff.

## Record-by-record inspection

| # | Source title | Original blob SHA-1 prefix | Exact-source SQLite test/edge check | Open semantic/provenance note |
|---:|---|---|---|---|
| 1 | Positive revenue this year | `ff4daccb` | 2021/year, positive/negative/zero | Historical title says “this year” but prompt explicitly says **2021**; do not substitute current year. Handout text visible, no grader. |
| 2 | Special bonus | `76353239` | odd/even IDs, M-prefix, salary, ordered output | Selects preserved **Solution 3** final Boolean multiplication; SQLite-specific, SQL Server conversion is `CASE`. `NULL` name/salary would need defined policy. Handout text visible, no grader. |
| 3 | Binary tree node type | `0d4685de` | root/inner/leaf, required numeric sort | Archived chosen answer guards `NOT IN` against `NULL` parent; assumes a valid single-root tree. Handout text visible, no grader. |
| 4 | Rearrange product stores | `e9fc3eb7` | 3-store unpivot, missing values, valid zero price, store sort | `UNION ALL` preserves product-store pairs; order of products **within** one store unspecified. Handout text visible, no grader. |
| 5 | Triangle classification | `04c688af` | four sample types, equality, degenerate/zero/negative sides | Checks impossibility before equal-side branches; undefined `NULL` inputs not independently resolved. Handout text visible, no grader. |
| 6 | Recyclable and low-fat products | `2e0a2f4b` | two `Y` flags required | Official answer **not supplied**; no platform grading. |
| 7 | Japanese city attributes | `8b453dd2` | 2 Japanese cities, all 5 source columns | Chooses preserved **Solution 2** explicit column list, valid only for the supplied 5-column schema; no official answer supplied. |
| 8 | Revising SELECT | `84a72a91` | USA filtering, `>100000`, exact-boundary exclusion | The >100000 condition is strict; no official answer supplied. |
| 9 | Referee exclusion | `e6351695` | both non-2 referees and `NULL` referees | `!=2` alone excludes missing referees; saved `OR IS NULL` required. No official answer supplied. |
| 10 | Big countries | `3dc19a0c` | `OR`, exact area and population thresholds | Both thresholds inclusive (`>=`); no official answer supplied. |
| 11 | Self article views | `c308a31d` | duplicate views, `DISTINCT`, ascending IDs | Source rows may duplicate; required output per author. No official answer supplied. |
| 12 | Invalid tweets | `6d646e35` | length 15 vs 16; trailing space included | Original SQLite `LENGTH` correct in shown fixture; saved SQL Server `LEN(content + '.') - 1` adaptation **not executed on SQL Server**. No official answer supplied. |
| 13 | Customers never ordering | `9a6574ac` | normal anti-membership sample plus injected `NULL` child key | **Observed logical mismatch:** source's `NOT IN` returns **no rows** when `Orders.customerId` includes `NULL`, even though Henry/Max have no order. Schema calls it an FK but does not state NOT NULL. See below. No official answer supplied. |

### Source discrepancy: question 13 — nullable foreign key

The archived historical answer is `WHERE id NOT IN (SELECT customerId FROM Orders)`.
For original sample `Orders.customerId = (3, 1)` it returns Henry and Max correctly.
For the separately created valid-looking fixture `Orders.customerId = (3, 1, NULL)`,
SQLite's three-valued logic makes `id NOT IN (3, 1, NULL)` UNKNOWN for
nonmatching IDs. **Observed result is empty**, rather than Henry and Max.
The checker asserts the discrepancy is still reproducible; this **does not
mean the nullable-case answer passed the written contract**.

Resolution requires verifying whether the actual provider question *guarantees*
`Orders.customerId IS NOT NULL`. If yes, record that original schema guarantee
and restrict the concern to hypothetical out-of-contract data. Otherwise the
historical solution has a genuine edge-case failure; safe future teaching uses
a clearly labeled `NOT EXISTS` or an explicitly `NULL`-filtered subquery.
**Do not rewrite the learner's archived original attempt.**

## Canonical concept crosswalk / unresolved coverage

- `01. SQL Mastery/00. SQL Basics`: keys, output grain, predicate basics.
- `01. SQL Mastery/01. Advanced SELECT`: `WHERE` with `AND/OR`, strict
  boundaries, `CASE`, `DISTINCT`, `ORDER BY`; source examples 1–3, 5–12.
- `01. SQL Mastery/11. NULL Logic`: `IS NULL`, `NOT IN` poison (3, 9, 13),
  valid zero value (4); assess whether specific anti-membership warning is
  already explicitly covered before editing a canonical chapter.
- `01. SQL Mastery/02. Joins` and source-specific `UNION ALL` row reshaping:
  examples 4 and 13; a link/index is **not** proof of full canonical parity.
- `01. SQL Mastery/08. SQL Strings and Patterns`: count character length,
  preserve trailing spaces across dialects (12).

**Remains:** Original platform/handout statement fidelity independently against
course platform; missing official key and full sample/hidden datasets where
not supplied; SQL Server live execution; additional edge schemas; 12 other
Bosscoder SQL topic groups/assignments; all other audit tracks, licensing and
final exact-head CI. Preserve the 744 original source files, historical
attempts/progress, and separate ChatGPT Library pending learning journal.
**Audit Issue #1 remains open; this batch does not authorize learning-sync.**
