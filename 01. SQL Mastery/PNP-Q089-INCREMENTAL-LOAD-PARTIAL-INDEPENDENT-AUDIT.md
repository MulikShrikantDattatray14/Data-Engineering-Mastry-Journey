# PNP Q089 — independent source-seed/watermark audit (PARTIAL; 12 November 2026)

## Source provenance and immutable historical status

Original P089 task: Original Mastery Snapshot / PNP foundations and practice / Data Quality and Deduplication / P089. Incremental load with a watermark and lookback.md, Git blob dc820d26afb08381d923f2cd215a0d64297a8d91. The original task, all four illustrated source Orders, three illustrated target rows, action counts, schema, 21-day lookback, NULL OrderDate treatment and PDF pp.175–177 attribution were individually read. Historical NOT SOLVED YET and all learner/official Pending fields were preserved.

Original supplied PostgreSQL key: Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql, Git blob 7912c8e676621c513e0b635a40c6ee299404676e. The original Q89 section has a temporary target, a seed based on MAX(source OrderDate) minus 14 days, then the 21-day target watermark batch, a NULL-safe ON CONFLICT DO UPDATE, RETURNING action attribution, and an ordered three-action report.

## Bounded independent execution

The read-only source-pinned checker at scripts/check_pnp_89_source_incremental.py extracts the original seed INSERT...SELECT and batch/watermark CTEs, and executes them on isolated SQLite databases after strictly asserted PostgreSQL date-syntax substitutions. SQLite cannot execute the PostgreSQL data-modifying CTE and RETURNING chain: the checker instead uses a clearly identified Python model for row mutation, NULL-safe comparison, action attribution and load timestamps. This is NOT native key execution, official answer verification or learner work.

Four bounded fixture groups passed:
1. The exact task illustration with explicitly seeded target: inserted=1, updated=1, unchanged=1; rerun 0/0/3. Existing unchanged timestamp sentinels remain intact.
2. Using the supplied key's OWN 14-day-back seed on those same four source records yields a target containing only order 4. The original batch then gives modeled inserted=3, updated=0, unchanged=1, not the task's illustrated 1/1/1. This is a reproduced mismatch of archived demo seed assumptions, not proof that the keyed UPSERT logic is wrong.
3. Independent target watermark 2026-01-22: Jan-01 included, Dec-31 excluded, NULL dates included; 2 inserts, 1 update, 2 unchanged, then rerun 0/0/5. No-op timestamp unchanged.
4. Empty Orders: modeled inserted=0, updated=0, unchanged=0.

Initial exact-head script CI: commit 517385c554c3d2558afb43b0cfa3ce4cccb6e1bd, Actions run 43258093063, all 94/94 validation job steps successful. Decoded job logs independently show each of the four checks and the 3/0/1 mismatch. A separate final documentation-head CI is required before marking this audit tranche's GitHub validation final.

## Classification and unresolved gates

Indexed: yes, one of 100 original P-source questions in 205 overall P/A/X IDs. Statement inspected: yes, original task and supplied key read and blob SHA-pinned. Synthetic test passed: yes, four bounded cases for extracted seed/batch with separately modeled updates; NOT a whole-source PostgreSQL pass. Official answer verified: NO, no provider grade/PDF parity/native PostgreSQL/full Commerce v2 data validation. Learner independently solved or mastered: NO, original NOT SOLVED YET/Pending unchanged.

Original PostgreSQL temp-table, INSERT ON CONFLICT, RETURNING and side-effect timestamp semantics still require an isolated native database transaction, provider/PDF reconciliation, and full-dataset rerun/late-arrival checks. The differing 14-day automatic seed vs explicitly illustrated previous-target state remains unresolved. Conservative passing P-series supplied-key replay tally remains 94/205 (94 of the 100 P IDs), NOT increased by the modeled Q089 checks. Q084/Q090/Q091/Q093/Q100 and other previously documented SQL gates, Python/Bosscoder/W3Schools/other DE, licensing/privacy and source-to-concept signoff remain open.

Issue #1 remains OPEN. Post-audit learner study evidence in the separate ChatGPT Library record /Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md remains UNSYNCED with GitHub until full independent signoff and final comprehensive CI; no original archive, historical attempt/progress or canonical foundation notes were changed.
