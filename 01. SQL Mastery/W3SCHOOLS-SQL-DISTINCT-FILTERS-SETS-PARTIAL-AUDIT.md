# W3Schools SQL DISTINCT / filters / ordering / EXISTS / UNION — partial independent source audit

**Inspected 13 November 2026.** This ledger is auditor-only. Eight live **official W3Schools lesson bodies** were inspected individually and contrasted with nine *existing* local reference, Bosscoder, and canonical notes. It does not reproduce copyrighted lessons, claim source-editor submissions, or change learner progress.

## Independent external page inspections

| Live primary page, separately read | Relevant demonstrated contract and local cross-source relation | Tested reviewer-only boundary / unresolved acceptance |
|---|---|---|
| [SELECT DISTINCT](https://www.w3schools.com/sql/sql_distinct.asp) | DISTINCT returns unique projected rows; COUNT(DISTINCT column) counts unique non-NULL expressions. Canonical Advanced SELECT and original Bosscoder Intro note cover DISTINCT. | A NULL city is *one distinct row* but **not counted** by COUNT(DISTINCT city); DISTINCT of two columns differs from DISTINCT of one. No W3 editor output authenticated. |
| [WHERE](https://www.w3schools.com/sql/sql_where.asp) | Boolean predicate filters input rows before grouping; compare selected numeric/text conditions to canonical Basics/Advanced SELECT. | NOT(unknown comparison) is still unknown, excluded by WHERE. NULL score is not automatically zero. |
| [ORDER BY](https://www.w3schools.com/sql/sql_orderby.asp) | ASC/DESC and multiple sort keys; covered by canonical Advanced SELECT/Sorting and original Bosscoder. | Equal scores need deterministic final ID tie-break; explicit CASE can order NULL last independently of dialect defaults. |
| [LIKE](https://www.w3schools.com/sql/sql_like.asp) | % (0+) and _ (exactly one) characters. Canonical Strings/Patterns warns against treating LIKE as email validation. | ASCII case handling varies with engine/collation; SQLite fixture matches 'a%' against upper/lower ASCII. ESCAPE literal underscore tested separately; NULL text does not match. |
| [IN](https://www.w3schools.com/sql/sql_in.asp) | Literal set and IN(subquery) are covered by original Bosscoder Intro and canonical Subqueries. | Official page also shows NOT IN(subquery) for no-orders; **conditional NULL poisoning** if subquery contains a NULL. In synthetic fixture, 'Tokyo' NOT IN a set with NULL is UNKNOWN, while correlated NOT EXISTS is TRUE. Not an authenticated site-answer failure. |
| [BETWEEN](https://www.w3schools.com/sql/sql_between.asp) | Numeric/text/date range is inclusive at both ends; cross-reference canonical Advanced SELECT and time-bound pitfalls. | Synthetic ISO timestamp at 2026-07-31 23:59:59 is excluded by date-only upper bound '2026-07-31' in SQLite, whereas half-open interval includes it. The website's date-only example may use date-only schema; do **not** declare site error. |
| [EXISTS](https://www.w3schools.com/sql/sql_exists.asp) | TRUE on any subquery row; page's correlated Supplier/Product relationship resembles canonical Subqueries and original Bosscoder Intro. | One customer with two matching orders still returns once in outer customer grain. Omitting correlation can turn a local predicate into a global all/none test. |
| [UNION](https://www.w3schools.com/sql/sql_union.asp) | Combines compatible projections, deduplicates entire rows; UNION ALL preserves duplicate rows. Original Bosscoder Intro includes both. | Synthetic NULL/duplicate fixtures give 4 distinct values versus 7 bag rows. Column-count mismatch errors. Type affinity and collations vary by dialect. |

Official sites were read through their rendered text content; **not** their interactive editors or quizzes. Website content can change after the date above. No actual official exercise output or grade was retrieved.

## Immutable local sources individually compared

All entries below are **original Git blob SHA-1 values on main at inspection**; the read-only test calculates Git's `blob <size>\\0<bytes>` identity and refuses to run if any of these local files drift.

| Existing local source (relative repository path) | Git blob SHA-1 | Relation |
|---|---|---|
| `99. Reference Materials/W3SCHOOLS-TOPICS.md` | `c6328c2eb420f47e5585026a7bf3c0a4e41be720` | Selected-topic external URL index, not content corpus |
| `01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md` | `d181dd73f96b1f2b7327600e290d52e9fd59a976` | basic projection and WHERE |
| `01. SQL Mastery/01. Advanced SELECT/0. Foundation Notes.md` | `1ed1077d492a3bd9db25018650b5c1f3cae1371f` | SELECT/DISTINCT/IN/BETWEEN/LIKE/order |
| `01. SQL Mastery/03. Sorting and Grouping/0. Foundation Notes.md` | `5cf690cb6ca5942795fe332aa447bbf77e14232e` | ordering/aggregation grain |
| `01. SQL Mastery/06. Subqueries/0. Foundation Notes.md` | `0414dd556eb4e327d45971763eb91e3730a6ce09` | IN, EXISTS and NOT IN/NULL |
| `01. SQL Mastery/08. SQL Strings and Patterns/0. Foundation Notes.md` | `63649bd6ad3a44449873136d90d3bbb2c724dbab` | LIKE, NULL, case/collation |
| `01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md` | `af9cc8d5d47e0279fe0d8b0f9276b700ce496888` | unknown values |
| `01. SQL Mastery/BOSSCODER-SELECT-FOUNDATION-INDEPENDENT-AUDIT.md` | `787d8e1a6fb0dc23f530902f359853fd262c9a23` | earlier original Bosscoder 16-fence checks, not newly re-executed |
| `01. SQL Mastery/BOSSCODER-SUBQUERIES-INDEPENDENT-AUDIT.md` | `4a3bc13d132d1cd246c5d1c3e7255871f124087d` | earlier original Bosscoder subquery attempt audit, not re-graded |

**Index coverage detail:** The existing selected-topic W3Schools reference index visibly includes LIKE, IN and EXISTS; it does **not** include DISTINCT, WHERE, ORDER BY, BETWEEN or UNION. This is a **source-to-concept URL-index gap**, not proof of missing canonical teaching material, because original Bosscoder Intro and Advanced SELECT cover these. Preserve the archived index without rewriting it; record scope here. Do not equate source indexing with independent statement inspection.

## Executable evidence

Read-only checker: [`scripts/check_w3schools_sql_filter_patterns_set_cross_source.py`](../scripts/check_w3schools_sql_filter_patterns_set_cross_source.py). A nine-file exact-blob guard plus **11 independent reviewer fixtures** (12 unittest methods) exercise the topics and edge policies. No original W3School program, provider data, official answer key or student SQL was executed by this checker. SQLite `LIKE` ASCII case behavior, flexible types and NULL sorting must not be projected onto PostgreSQL/MySQL/SQL Server without dialect-specific replays.

Evidence classification: **8 official page statements inspected; 9 local files compared and immutable SHA-pinned; auditor-authored synthetic SQLite checks** only. **0 official site answers verified; 0 learner independently solved**. The local checks do not establish mastery.

## Blockers and preservation rules

- The website editor, quizzes, grading and full Northwind/provider dataset have not been independently executed; primary page prose and local source comparisons are not an answer key.
- The original Advanced SQL MySQL PDF, PNP 100 SQL PDF/full dataset, Python mentorship original PDF, Bosscoder primary PDFs, full DE material, privacy/licensing review and final cross-source audit remain separately unresolved.
- Prior bounded PNP P-series supplied-key replay tally **94/205** unique questions is unchanged by W3Schools tests. This tranche gives no A/P/X official answer or learner completion.
- Source archives, historical learner attempts/progress, canonical foundation notes and ChatGPT Library learner-study record remain unchanged. GitHub learning sync is deferred until complete independent signoff and passing CI. Keep GitHub Issue #1 **OPEN** and do not notify completion.
