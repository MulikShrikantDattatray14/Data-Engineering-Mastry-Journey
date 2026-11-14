# Python mentorship ETL source contracts — independent, bounded audit (14 November 2026)

**PARTIAL: no provider PDF parity, native cloud/Spark/Airflow run, official grade or learner completion.** This is a read-only source review of the original Python mentorship companion pages 71–74 and the archived 15-order CSV. The full five-blob preservation guard is in scripts/check_python_mentorship_etl_p71_74_contracts.py; the source files themselves were not changed.

| Archived source | Original Git blob SHA-1 | Independently inspected evidence |
|---|---|---|
| Python DE lesson 03, PDF-attributed p.71 | 02af93e471c9f933274981230981102c72e76d69 | In-memory SQLite, parameter-binding versus unsafe f-string, transaction rollback, UPSERT; demonstration not production credentials |
| Lesson 04, p.72 | fc859b44748d06318f2d0bdb4ae36266715253e7 | Read unchanged complete first Python snippet; one-day extract, generator transform, delete/reload in one SQLite transaction, CLI/log behavior |
| Lesson 05, p.73 | 05b4ff35d2666ef5908237686f2a517dd718301a | Status normalization and positive-amount checks are separate examples, NOT invoked by lesson 04's main/load |
| Lesson 06, p.74 | 17b999bcc639f184c5ca7bac4c3a325d4d05e763 | Optional Spark code depends on a runtime; Airflow DAG explicitly raises NotImplementedError at warehouse load. Syntax/source inspected only, no real Spark/Airflow execution |
| orders.csv | 2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2 | Original 15 rows including order 114 on April 20 and 115 on April 28; source-pinned exact sample for runner |

## Independently executable contracts (11 tests, if CI passes)

1. Five immutable source hashes, p73 quality function presence, p74 explicit warehouse placeholder.
2. Execute original full p72 first Python code fence unchanged against a temporary copy of the real archived CSV; assert all three documented log lines exactly.
3–4. Source extract exact-date filter and transform int/float/status behavior.
5. Day rerun with changed amount replaces old row, no duplicate.
6. Duplicate primary key after a delete and first successful insert causes transaction rollback, restoring old row.
7. A malformed amount during the generator/executemany iteration rolls back already attempted deletion and insertion.
8. Different-day row with an already-used global order_id fails primary key constraint; earlier day survives. Source presumes global order_id uniqueness; it does not support changing an existing order's date by day-delete alone.
9. Source p72 transform/load accepts negative amounts and unknown statuses, while source p73 to_amount rejects the former and normalize_status flags the latter; quality gate is NOT wired into p72 load.
10. A day absent from the input yields zero new rows and leaves different-day rows untouched (it can still delete existing rows for its *own* day).
11. Source CLI's deliberately caught argparse SystemExit prints code 2 but subprocess exits 0; this is documentation example behavior, not actual scheduler failure signaling.

These checks are synthetic independent boundaries except for the unchanged full-source p72 example and its real CSV. Passing them must not be translated into proof of full original PDF output fidelity, production pipeline idempotence under concurrent writers, malformed dates, native Spark/Airflow execution, external provider answer or learner mastery.

## Open semantics and blocked full signoff

- The p72 sample does not call p73 validation. Negative/nonpositive values, unknown statuses and invalid calendar dates can enter its SQLite table unless an upstream guard is added. No canonical foundation edit was made based on interactive learner sessions.
- Date-partition deletion plus global order_id PRIMARY KEY assumes a stable order/date mapping; a cross-day move conflicts rather than updating an existing row. Missing expected files and empty reruns require a fail-closed policy to avoid accidental partition deletion.
- p71 injection example intentionally interpolates raw input to demonstrate the risk; production guidance is to bind parameters. The p74 Spark window needs a native Spark runtime, while its Airflow code deliberately leaves warehouse integration unimplemented.
- Exact visual PDF pages, provider-authorized redistribution, original production/source datasets, remaining SQL key parity and broader DE content remain open. Maintain distinctions: indexed / statement inspected / source example replayed / synthetic test passed / official answer verified / independently solved.

**Preservation and learning separation:** only this ledger, additive migration status, a read-only checker and CI workflow are authorized modifications; preserve all 744 source files and all historical learner progress. The ChatGPT Library pending-study record remains UNSYNCED until whole-audit signoff and a new post-sync CI.
