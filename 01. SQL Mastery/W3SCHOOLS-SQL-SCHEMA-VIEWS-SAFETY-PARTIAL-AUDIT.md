# W3Schools SQL schema / views / safety — independent partial audit

**2026-11-13.** Individually read **eight distinct official W3Schools SQL lesson bodies** and **seven preserved repository documents**. Prior ledgers account for 40 other distinct inspected SQL lessons; cumulative inspected SQL pages: **48**, not a complete syllabus audit. This document links, rather than reproduces, copyrighted teaching content. No graded answer or learner mastery is claimed.

## Primary-source-by-primary-source verification

| Independently read official page | Verified teaching contract and independent boundary | Original/local cross-source comparison |
|---|---|---|
| [DROP TABLE](https://www.w3schools.com/sql/sql_drop_table.asp) | DROP removes both object and data; IF EXISTS supports absent objects; TRUNCATE removes records while retaining table definition. | Archived Bosscoder Basics distinguishes DELETE, TRUNCATE and DROP. SQLite reviewer reproduces DROP versus DELETE and **SQLite's TRUNCATE syntax rejection**, not other engines' TRUNCATE result. |
| [ALTER TABLE](https://www.w3schools.com/sql/sql_alter.asp) | ADD/DROP/RENAME columns, modify types and constraints; MODIFY/ALTER COLUMN are dialect-specific. | Archived Bosscoder Basics includes ALTER ADD, canonical Basics covers constraints. SQLite reviewer checks ADD to existing rows and RENAME/DROP, **not** native vendor type/constraint changes. |
| [CREATE INDEX](https://www.w3schools.com/sql/sql_create_index.asp) | Ordinary and UNIQUE indexes; duplicates allowed by nonunique indexes; composite indexes; index read/write tradeoff, engine-specific DROP INDEX syntax. | Canonical Dates and Analytics cover index-friendly filters. Reviewer confirms SQLite index catalog, duplicate behavior and NULL handling. No real workload plan/cost timing or vendor portability proven. |
| [AUTO INCREMENT](https://www.w3schools.com/sql/sql_autoincrement.asp) | MySQL AUTO_INCREMENT, SQL Server IDENTITY, Access AUTOINCREMENT and Oracle sequence variations. | Canonical and archived Basics explain PKs, not portable auto-key generation. Reviewer establishes only **SQLite** INTEGER PRIMARY KEY rowid-reuse versus AUTOINCREMENT distinction. |
| [Dates](https://www.w3schools.com/sql/sql_dates.asp) | Date/time types, formats and nonmidnight time portion affect predicates; dialect-specific functions. | Canonical Dates explicitly uses half-open intervals. Synthetic ISO-text rows distinguish Jan 31 23:59:59 from Feb 1 00:00:00; no original W3 data, typed timestamp/timezone/DST verified. |
| [Views](https://www.w3schools.com/sql/sql_view.asp) | Create/query/drop virtual views; ALTER VIEW (SQL Server) versus CREATE OR REPLACE (MySQL/Oracle) described. | Archived Bosscoder Basics covers views. SQLite view reflects underlying table changes and DROP VIEW leaves base table; native provider view alteration and source sample data untested. |
| [SQL Injection](https://www.w3schools.com/sql/sql_injection.asp) | Untrusted input concatenated into SQL alters query meaning; always-true predicates and unsafe batches illustrated. | Only isolated, non-destructive in-memory SQLite toy data uses `OR 1=1` compared with bound values. No production exploit, learner assignment or official grader. |
| [Prepared Statements](https://www.w3schools.com/sql/sql_prepared_statements.asp) | Separate query template and data bindings; reusability and injection protection; official illustration is PHP/MySQL. | SQLite `?` placeholders treat user values as data. Identifiers cannot be bound as values. **No PHP/MySQL server-side prepared execution authenticated**. |

## Original repository evidence and SHA-1 pins

All seven documents were directly read and their Git blob SHA-1 values independently retrieved. The new checker recomputes the SHA from `blob <byte-length>\\0<bytes>` on the exact full checkout.

| Source record | Git blob SHA-1 |
|---|---|
| `99. Reference Materials/W3SCHOOLS-TOPICS.md` | `c6328c2eb420f47e5585026a7bf3c0a4e41be720` |
| `01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md` | `d181dd73f96b1f2b7327600e290d52e9fd59a976` |
| `01. SQL Mastery/12. Dates and Time/0. Foundation Notes.md` | `0061f75fe5977679acdcf11ae8dda92fbd762143` |
| `01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md` | `d2743783106fe64ca087b39216184a87e97d1a8c` |
| `01. SQL Mastery/14. Data Quality and Deduplication/0. Foundation Notes.md` | `f19d2b0340649f2e481ac62705d9c28dd87ce761` |
| `01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md` | `af9cc8d5d47e0279fe0d8b0f9276b700ce496888` |
| `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/0. SQL basics/0. Foundation Notes.md` | `073c87bebb2d7c72cca97e970a06de965a87abe5` |

The intentionally *selected-topic* index includes exact CREATE INDEX and Views URLs; the other six URLs are absent there. This is a **six-link selection gap**, not evidence that original lessons are missing. Canonical Dates directly links the W3 Dates page separately. Neither index nor canonical foundation notes was modified.

## Reviewer test and evidence tiers

New read-only runner: [`scripts/check_w3schools_sql_schema_views_safety_cross_source.py`](../scripts/check_w3schools_sql_schema_views_safety_cross_source.py). **14 unittest methods**: one immutable seven-blob SHA plus two-linked/six-unlinked selected-index guard, and **13 distinct synthetic SQLite memory-database fixtures**: DELETE/DROP, IF EXISTS, TRUNCATE rejection, ALTER ADD/RENAME/DROP, indexes and UNIQUE NULL, SQLite identity reuse, half-open date boundaries, base-table/view relationship, unsafe string-concatenation contrast, and parameter-as-data binding. The 13 reviewer fixtures passed in a separate local scratch Python runtime. Only exact-head GitHub Actions success can certify the full pin-and-test checker and full regression; see Issue #1 for its verified CI status.

- **Indexed:** two links selected, six not selected (not deleted course content).
- **Statement inspected:** eight actual official pages and seven directly read Git-blob-pinned originals.
- **Synthetic test passed:** 13 local fixtures; exact-head CI to confirm all 14.
- **Official answer verified:** **0 new** W3 editor/quiz official answers, hosted outputs or grades.
- **Learner independently solved:** **0 new** genuine learner submissions; **0 mastery** claims.

## Open gates

Hosted W3 editor, original schema/output and official keys, cross-engine ALTER/identity/TRUNCATE/prepared syntax and result parity, full 205 PNP source PDF/full commerce dataset and remaining supplied-key semantics (prior conservative **94/205** clean replay, unchanged), remaining mentorship Python original PDF and Bosscoder/other W3/DE source checks, whole-repo licensing/privacy and source-to-concept integrity signoff, and final exact-head comprehensive CI remain outstanding. **Issue #1 stays OPEN.** The separate ChatGPT Library pending learner study record plus later work remain **UNSYNCED to GitHub**, pending full independent audit signoff and then distinct post-sync CI. Archived original and historical learner attempts/status are unchanged.
