# W3Schools SQL DDL and Constraints — Independent Partial Cross-Source Audit

**2026-11-13 | Evidence tier: live primary-page statement inspected; seven preserved local blobs independently inspected and pinned; synthetic SQLite fixtures authored and locally exercised. No official answer or learner credit.**

## Source-by-source primary-page inspection

| Primary W3Schools lesson | Independently inspected contract and comparison / pitfall |
|---|---|
| [CREATE TABLE](https://www.w3schools.com/sql/sql_create_table.asp) | Column types and constraints in CREATE TABLE; CREATE TABLE AS SELECT copies selected rows, but SQLite reviewer confirms it does **not** preserve PRIMARY KEY, UNIQUE or NOT NULL constraints. The canonical SQL Basics note explicitly shows CREATE TABLE with keys. |
| [Constraints](https://www.w3schools.com/sql/sql_constraints.asp) | Overview of NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY, CHECK, DEFAULT and indexes; this overview is **not** proof of a provider graded exercise. Bosscoder original Basics and canonical Basics both contain constraint examples. |
| [NOT NULL](https://www.w3schools.com/sql/sql_notnull.asp) | Missing/explicit NULL insert and update are prohibited; empty string is **not** NULL and remains permitted by NOT NULL alone. Vendor-specific ALTER syntax is shown on primary page but **not** executed. |
| [UNIQUE](https://www.w3schools.com/sql/sql_unique.asp) | Column/composite uniqueness; multiple UNIQUE constraints may coexist. SQLite permits multiple NULL entries in a UNIQUE column and in NULL-containing composite pairs; **do not generalize to all SQL vendors**. |
| [PRIMARY KEY](https://www.w3schools.com/sql/sql_primarykey.asp) | One PK constraint per table, optionally composite; checked duplicate composite keys on WITHOUT ROWID. SQLite INTEGER PRIMARY KEY has rowid auto-number behavior when given NULL; not an authenticated cross-dialect result. |
| [FOREIGN KEY](https://www.w3schools.com/sql/sql_foreignkey.asp) | Child rows must reference eligible parent keys; reviewer distinguishes orphan insert, restricted parent delete/update, nullable references, explicit CASCADE. SQLite requires PRAGMA foreign_keys=ON per connection (canonical Basics notes this). |
| [CHECK](https://www.w3schools.com/sql/sql_check.asp) | Illustrated age >=18 condition. Important **three-valued logic nuance**: in SQLite, CHECK fails on FALSE/0 but passes on NULL/UNKNOWN; combine CHECK with NOT NULL for required age. The site's simplified TRUE/FALSE prose does not spell out this NULL case. |
| [DEFAULT](https://www.w3schools.com/sql/sql_default.asp) | Omitted column receives its default; explicit NULL does not substitute default. MySQL CURRENT_DATE() and SQL Server GETDATE() examples are dialect-specific and **not** cross-engine verified. |

## Exact local source byte pins (Git blob SHA-1)

| Local source / historical status | Pinned blob |
|---|---|
| 99. Reference Materials/W3SCHOOLS-TOPICS.md | c6328c2eb420f47e5585026a7bf3c0a4e41be720 |
| 01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md | d181dd73f96b1f2b7327600e290d52e9fd59a976 |
| 01. SQL Mastery/02. Joins/0. Foundation Notes.md | 61d952c98f02a62c6591caaedf5c02cf0b43e3b1 |
| 01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md | af9cc8d5d47e0279fe0d8b0f9276b700ce496888 |
| 01. SQL Mastery/14. Data Quality and Deduplication/0. Foundation Notes.md | f19d2b0340649f2e481ac62705d9c28dd87ce761 |
| 01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md | d2743783106fe64ca087b39216184a87e97d1a8c |
| 99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/0. SQL basics/0. Foundation Notes.md | 073c87bebb2d7c72cca97e970a06de965a87abe5 |

All seven archived/canonical records were read, compared for grain, constraint semantics and original learner-credit boundaries. The primary W3 pages are live external content and are **not** content-SHA pinned; their URLs and the dated inspection are recorded. None of these eight exact URLs is in the *selected-topic* W3Schools link index, but related teaching already exists in both the archived Bosscoder and canonical SQL notes. Eight selected-index link gaps do **not** mean eight lost lessons.

## Reviewer-only regression scope

Runner: scripts/check_w3schools_sql_constraints_ddl_cross_source.py. **14 unittest methods:** (1) immutable seven-blob SHA and eight selected-index omissions guard; (2–14) thirteen independent SQLite memory-DB fixtures. Locally, all 13 semantic methods passed; source blob guard must be run in the full repository checkout by GitHub Actions, not the isolated scratch working directory. Test content: table metadata and emptiness, NOT NULL insert/update, UNIQUE and composite NULL behavior, composite PK, SQLite INTEGER PRIMARY KEY auto-number, FK enabled/disabled and cascade, CHECK unknown truth value, omitted DEFAULT vs NULL, CREATE TABLE AS missing constraints, statement-level rollback and nullable FK with restricted parent updates.

**Potentially misleading source interpretations found:** W3 CREATE TABLE 'copy' section does not promise schema parity; SQLite CTAS loses constraints. NOT NULL does not reject blanks; DEFAULT does not replace explicit NULL; CHECK(age >=18) alone permits NULL under SQLite; native FK checks are disabled by default in some SQLite connections; SQL UNIQUE NULL and ALTER TABLE capabilities vary by vendor. These are *reviewer-generated counterexamples*, not confirmed official-source answer defects.

## Evidence tiers and unfinished signoff

- **Indexed:** selected W3 index is intentionally incomplete for eight URLs; canonical concepts exist, and no source or learner archive was altered.
- **Statement inspected:** eight individual W3 live pages plus seven Git-blob-pinned local files (not merely URL listing).
- **Synthetic test passed:** only when the exact CI head has completed successfully; isolated local semantics were exercised separately.
- **Official answer verified:** zero newly; live W3 quiz/try-it editor, course rubrics, official keys, original full demo schemas and provider-side execution were not authenticated.
- **Learner independently solved:** zero newly; no mastery, score or study time inferred.
- **Open gates:** original PNP SQL PDF/full commerce schema and remaining 205-question answer/output parity (prior conservative supplied-key replay 94/205), mentorship primary PDF and Bosscoder originals/grade parity, remaining W3 and DE sources, licensing/privacy, final source-to-concept proof and final CI. GitHub Issue #1 stays OPEN. Separate ChatGPT Library learning record and later learner work remain UNSYNCED pending full audit signoff and separate post-sync CI.
