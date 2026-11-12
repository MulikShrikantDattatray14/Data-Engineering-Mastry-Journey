# PNP Q091 cohort LTV — independently reproduced source/key conflict (PARTIAL, 12 November 2026)

## Immutable original sources inspected

- Original task: `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/12. Dates and Time/P091. Cumulative value per customer by cohort (LTV curve).md`, **Git blob `cf11e56982938b3227f711e00534237f88d451aa`**. Individually inspected its task, four source sample orders, two displayed cohort rows, table schema, original PDF pp.180–184 attribution, `NOT SOLVED YET` badge and intact SQLite/SQL Server/official Pending sections.
- Original supplied PostgreSQL answer key: `.../Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql`, **Git blob `7912c8e676621c513e0b635a40c6ee299404676e`**. Independently read **the exact `-- Q91.` supplied-key section**, not a reconstructed official answer.
- Source-to-concept: calendar-quarter acquisition cohorts, customer first-order month, observed months versus most recent observed full month, per-cohort customer denominators and cumulative offsets 0/3/6/12. The canonical Dates and Time foundation already describes cohort observation maturity. **No canonical note or historic learner record was edited** in this audit.

## What independent execution established

Read-only [source-pinned Q091 checker](../scripts/check_pnp_91_source_cohort.py) extracts the actual preserved Q91 SQL at execution time. It validates both immutable Git blob hashes and the archived pending statuses; translates only PostgreSQL `DATE_TRUNC`, date + interval arithmetic, `EXTRACT`, integer cast and `generate_series` to narrowly asserted SQLite expressions. It **preserves the supplied CTEs, grouping, windows, cohort maturity filter and final answer logic**. It fails closed on changed source syntax. This is date-adapted source-key replay on in-memory synthetic SQLite, **not native PostgreSQL 16 execution or complete original Commerce v2 data**.

| Fixture | Source/derived input | Observed supplied-key result | Status |
|---|---|---|---|
| Original four-order, two-cohort source illustration | January 2025 customer has Jan/Apr 2025 + Jan 2026 orders; January 2026 customer has Jan 2026 order; last order Jan 31, 2026 | 2025-Q1 `(1,100,150,150,NULL)`; 2026-Q1 `(1,NULL,NULL,NULL,NULL)` for count, m0/m3/m6/m12 | **Reproduced source/key discrepancy**, not a passed task-output contract |
| Independently extended anchor at Jan 31, 2027 | Same source rows plus a third customer's January 2027 order | 2025-Q1 `(1,100,150,150,200)`; 2026-Q1 `(1,80,80,80,NULL)`; 2027-Q1 all maturity values NULL | **Synthetic fixture passed** |
| Empty Orders | No rows | No cohorts/rows, not fictitious results | **Boundary fixture passed** |
| Source provenance and status | Immutable question/key blobs; Pending learner/official markers | All assertions passed | **Source identity/status passed** |

**Material contradiction:** The original source sample says **2025-Q1 m12 = 200** and **2026-Q1 m0 = 80**. The actual supplied query's maturity test is `cohort_quarter + 2 months + month_offset months <= last_full_month`. With `last_full_month = 2026-01-01`, it declares both values immature (`NULL`). The checker explicitly asserts that *only these two cells* of the source illustration differ from the SQL result, rather than quietly changing the expected values to make the example pass. The source task's policy for partial cohort maturity and worst-case quarter-member first-order month needs authoritative reconciliation before answer signoff.

## CI and integrity evidence

- Initial workflow-head [run 43219978178](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43219978178) **failed** at the newly introduced guard because the supplied key contains **three** occurrences of `DATE_TRUNC('quarter', fo.first_month)::date` (SELECT/GROUP BY/order offsets), not the auditor's initial expectation of two. This was **an auditor test assertion**, not an original SQL/source defect; the original archive was not changed.
- Correction commit `1dbef9787e2a6054256b317ca62c680fa28eb6d1` changed only that expected occurrence count. [GitHub Actions run 43220181672](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43220181672) at that exact SHA **completed success: all 90 validation steps passed**, zero failed/skipped. Independently read decoded job logs confirming original blob/status PASS, two source-output mismatches reproduced, separate later-anchor fixture PASS and empty-input PASS. Subsequent documentation commits require their own exact-head CI confirmation.

## Explicit independent-evidence tier and remaining blockers

**Indexed:** yes, Q091 exists in 205 source-question inventory. **Statement inspected:** yes, question and source key inspected independently. **Synthetic test passed:** yes, bounded original-key date translation with source mismatch and two boundary checks. **Official answer verified:** **NO**; the actual source/key contradicts its sample, and no native PostgreSQL/provider-grade/full-dataset parity. **Learner independently solved:** **NO**; preserved Pending records.

Do not inflate the conservative 93/205 bounded source-key verification tally: a reproduced **failing source contract** is not a verified correct official output. Other Q084/Q089/Q090/Q093/Q099/Q100 native/semantic issues, source-PDF actual page parity, full provider datasets, other Python/Bosscoder/W3Schools/DE material, cross-source concept coverage, licensing/privacy and audit-wide CI/signoff remain unresolved. Keep [Issue #1](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/issues/1) open and **do not sync the separate ChatGPT Library learner-study record** until complete audit acceptance and successful final CI.
