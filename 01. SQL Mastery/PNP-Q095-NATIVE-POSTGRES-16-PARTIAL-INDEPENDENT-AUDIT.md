# PNP Q095 original faulty query and supplier key — native PostgreSQL 16 independent audit (PARTIAL)

**Audit date:** 13 November 2026. This additive evidence is auditor-owned, not a replacement of source files, provider-authenticated grading, or learner completion.

## Exact preserved-source inspection

- Original question path: 99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/14. Data Quality and Deduplication/P095. Debug a revenue-by-category query that gives wrong numbers.md. **Git blob 6556470a667af5ddb73e9adce81e65bb4331cb3b**.
- Supplied PostgreSQL answer path: under same source base, Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql, **Git blob 7912c8e676621c513e0b635a40c6ee299404676e**, original Q95 block. Both original blob hashes are guarded at executable runtime.
- Inspected task: report for the latest full calendar year, one row per category including zero sales, distinct category orders, quantity-times-list-price value, absent category as Unmapped, ascending list-price value. Starting intentionally faulty query must be debugged with row-count/total checks.
- Source-to-concept connections: fact/header vs line grain; join fan-out; COUNT versus COUNT DISTINCT; LEFT/FULL JOIN and missing categories; nullable sale price; half-open annual date bounds; display-label vs true grouping identity.
- Archived status remains **NOT SOLVED YET**, SQLite/SQL Server attempts and official-solution display **Pending**. No source files, learner history, or canonical foundations were modified. Original PDF pp.193–196 and Commerce Dataset v2 parity are attribution/pending checks, not independently verified here.

## Source-extracted original queries / native fixtures

[Read-only checker](../scripts/check_pnp_95_native_postgres.py) extracts BOTH the preserved intentionally faulty starter SQL and the supplier correction unmodified, then runs them under native PostgreSQL 16 using transaction-scoped disposable TEMP tables. Its checks cover four fixture groups:

| Group | Expected observation in checker | Category |
|---|---|---|
| Original two-category illustration | Corrected Home/0/0, Unmapped/1/5, Audio/1/20; intentionally bad source starter returns only Audio/1/25, omitting zero category and Unmapped and using header revenue | Original illustrative data / deliberately broken starter |
| Independent Jan/Dec, missing IDs, NULL price, duplicate category labels | Corrected (Audio,0,0), (Empty,0,0), (Unmapped,2,14), (Home,1,21), (Audio,2,50); excludes 2025-12-31 and includes 2026-01-01 and 2026-12-31, deduplicates multiple lines per order | Reviewer synthetic boundary |
| Empty Orders, all-unmapped sales, NULL-price line | Empty produces catalog zero rows; no Category still yields Unmapped/1/16; nullable price line coexists with Audio/1/6 | Reviewer synthetic boundary |
| Two same-order line items, label collision | Intentionally bad starter Audio/2/200 vs corrected Audio/1/50; category literally named Unmapped and missing-category bucket both appear as displayed Unmapped rows (values 5 and 7) | Reproduced starter fault + conditional semantic ambiguity |

The source correction does not provide the requested written, exhaustive fault-by-fault row-count / total explanation. The conditional duplicate-name/Unmapped-label identity collisions require provider/business uniqueness policy and are not authenticated official-answer failures.

**Execution confirmation gate:** Initial ledger lists asserted outcomes, not an independently confirmed native run; examine exact-commit Actions result, PostgreSQL version, SHA pins and native logs before marking fixture execution passed.

## Evidence levels and unfinished gates

- **Indexed:** yes, part of preserved 205 P/A/X questions.
- **Statement inspected:** yes, original Q095 statement, schema, sample, status, starter and supplier SQL individually read.
- **Synthetic test passed:** only after independently reviewing the native CI results and decoded logs.
- **Official answer verified:** NO; the supplied key is not authenticated provider grading.
- **Learner independently solved:** NO; the source remains NOT SOLVED YET / Pending.

Do not automatically increase the conservative 94/205 clean bounded supplied-key replay count based on a discrepancy/conditional replay. Original rendered PDF, full original data, all other source-to-concept/semantic gaps, Python mentorship, Bosscoder, W3Schools, other Data Engineering, privacy/licensing, final audit and comprehensive CI signoff remain. Issue #1 stays OPEN; separate ChatGPT Library pending study evidence remains UNSYNCED with GitHub until full signoff.