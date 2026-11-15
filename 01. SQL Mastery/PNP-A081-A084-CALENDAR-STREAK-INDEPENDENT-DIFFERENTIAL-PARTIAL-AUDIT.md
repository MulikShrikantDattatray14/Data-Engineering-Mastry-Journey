# PNP Advanced A081–A084 — independently bounded calendar / ID streak differential audit (PARTIAL)

**Audit date:** 15 November 2026. **Scope:** Reopened all four preserved original archived Markdown question bodies and the related original P065 month-streak source. This supplements, rather than increases, the already `statement inspected` A081–A090 corpus and does not confer learner credit.

## Individually inspected source statements and provenance

| ID | Preserved original Git blob | Source contract and illustrative rows | Unresolved supplier/data policies |
| --- | --- | --- | --- |
| A081 | `e55eab41df5a04044c62b7294a1eb27c91a4eda2` | Collapse each customer's distinct ordering dates to start/end streaks; archived illustrative customer 10 Jan 1–2 and Jan 4; customer 20 Feb 1 | Cancellation/return statuses, timestamp zone, malformed or NULL dates, inclusion of zero-order customers, native MySQL date treatment |
| A082 | `e731eacbf70559c37d324b1cd84a1f859d694bdc` | Longest ordering streak in **distinct days**, not orders; archived illustration cust 10=3 days, cust 20=2 | Missing orders/customers, canceled dates, invalid date handling, ties if subsequent start/end fields requested |
| A083 | `d4baa6518ee90522ac5a5a24368980015d965ecd` | Customers ordering in at least three **consecutive calendar months**; illustration cust 10 qualifies, cust 20 has missing February | Multiple orders in a month, year rollover, fiscal-vs-calendar periods, returned rows for inactive customers |
| A084 | `33d010d698baa4b2f0b891d602aedc226c349017` | Compact consecutive `seat_bookings.id` ranges; source illustration IDs 1,2,3,7,8,10 become (1,3),(7,8),(10,10) | `seat_bookings` is **absent** from the seven-table shared schema; duplicates, nulls, integer domain, native MySQL table DDL unavailable |
| P065 (cross-source) | `a7b40c93d66c2fa77e188081f41b91b91a581155` | Longest monthly streak per customer with start/end, **top ten including tenth-place ties**, and most recent on same-length runs | Different source `Orders` schema and output/grain from A083; not equivalent tasks or interchangeable answers |

All four A-series records attribute their source to *Advanced SQL 100 Query Questions, Vol. 1*, **PDF p.16**. That attribution was read in the preserved Markdown; the **actual rendered PDF p.16 and original MySQL 8 answers were not accessed/verified**. The samples above are explicitly labeled *illustrative* in the archived Markdown and must not be promoted to supplier-provided expected datasets.

## New independent bounded execution evidence

[New isolated reviewer](../scripts/check_pnp_advanced_81_84_day_month_id_differential.py) imports the pre-existing **auditor-authored** SQLite fixture queries in `scripts/check_pnp_advanced_81_90_sources.py`, rather than inventing an alleged official MySQL answer. There are **17 named unittest methods**: one immutable-source/pending-state check for five archives; four archived local illustrations; **2,008 synthetic combinations** compared against independently authored Python standard-library oracles (**243 A081 + 243 A082 + 729 A083 + 729 A084 + 64 A081↔A082 cross-invariants**); and eight additional policy, leap-year, duplicate, NULL, negative-ID, invalid-date, timezone and cross-task probes. Test method and combination counts are **not** question or learner completion counts.

**Specific synthetic counterexample:** with `order_date='not-a-date'`, a reviewer SQLite `date(order_date)` expression becomes NULL, but the existing prefilter `order_date IS NOT NULL` lets it through. The A081 reviewer can emit the phantom (cust 1, NULL, NULL) interval; A082 can give an invalid-only customer a streak of 1. A validation policy or post-cast NULL filter is necessary *if malformed dates are possible*, but there is no verified supplier contract for malformed rows. Likewise, offset-bearing timestamps may normalize to a different UTC date in SQLite; native MySQL `DATETIME`/`TIMESTAMP` parity must not be inferred.

The reviewer tests are **synthetic SQLite**, not the supplier's full commerce dataset, source official answers, native MySQL 8 execution, provider grading, or a student's independent solve. A084's `seat_bookings` table is locally synthesized and not a verified source schema. The A083 vs P065 comparison explicitly prevents merging a Boolean eligibility question with a top-ten ranked streak-duration question.

## Evidence grades and gating

- **Indexed**: all five IDs were indexed before this run; **zero new unique identifiers**.
- **Statement inspected**: original Markdown and local illustrations individually reread with immutable Git-blob references; source PDF rendered-page parity **unverified**.
- **Synthetic test passed**: **do not claim PASS until the exact-main GitHub Actions run and each new reviewer result is checked**.
- **Official answer verified**: **zero new**; conservative independent supplied-key replay remains **94/205**, unchanged.
- **Learner independently solved**: **zero new**; all four Advanced originals explicitly retain **NOT SOLVED YET** and SQLite/SQL Server/official placeholders Pending.
- **Integrity and licensing**: no redistribution rights, complete PII screening, PDF parity or final audit signoff is established by these checks.

Still outstanding: verified visual source PDF p.16 and corresponding MySQL answers/datasets, supplier interpretation of bad/tied/NULL dates and table schema, complete PNP 205-question output parity, remaining Python mentorship/Bosscoder/W3Schools/other DE source material and source-to-concept mapping, full licensing/privacy clearance and full independent signoff. **Issue #1 must stay OPEN.**

**Preservation/learning sync:** audit-owned checker, ledger, CI and status documentation only; original course archives, historical learner attempts/progress and canonical foundations unchanged. ChatGPT Library pending-study record `/Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md` and later interactive learning are **UNSYNCED with GitHub** until full independent audit signoff and separate post-sync CI.
