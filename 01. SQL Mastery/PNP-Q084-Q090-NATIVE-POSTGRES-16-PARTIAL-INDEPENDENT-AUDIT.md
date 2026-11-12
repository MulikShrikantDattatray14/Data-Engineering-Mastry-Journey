# PNP Q084/Q090 — native PostgreSQL 16 replay, independent partial audit

**12 November 2026 · NOT FINAL AUDIT SIGNOFF**

## Source identity and evidence levels

The original question records were independently read and checked against their preserved Git blob identities:

| Task | Immutable original question Git blob | Original supplied PostgreSQL key |
|---|---|---|
| P084 / Q84 — State/shipper delivery ROLLUP | `e019aa308f9726e1328a44e24e89c7c4db677701` | `7912c8e676621c513e0b635a40c6ee299404676e` |
| P090 / Q90 — Orders column completeness | `1fa536155bfc0115c796ae7c740d0b23dff851f7` | `7912c8e676621c513e0b635a40c6ee299404676e` |

These original Markdown files include the scenario, complete task text, supplied illustrative sample/output and schema plus unchanged `NOT SOLVED YET` and `Pending` learner/official-solution placeholders. The referenced PDF page numbers (Q84 pp.160–162; Q90 pp.178–180) are **attributions, not independently rendered PDF parity**. The supplier SQL is a preserved *supplied key*, **not** a provider-authenticated official grade.

New read-only [native checker](../scripts/check_pnp_84_90_native_postgres.py) verifies original Git blob SHA-1 identities, extracts the two exact archived SQL sections without SQL translation, connects to a PostgreSQL **16.15** service (`server_version_num=160015`), and executes the actual `ROLLUP`, `GROUPING`, `MAX(COUNT(*)) OVER`, `LATERAL (VALUES...)`, `FILTER`, date subtraction and native `::date` / `::text`. Both tasks use transaction-scoped disposable `TEMP` tables (`ON COMMIT DROP`) with auditor fixtures; no source repository tables, original datasets, learner attempts or progress are modified. This materially improves upon the earlier, explicitly limited SQLite reconstructions.

## Independently checked outcomes — original SQL executed natively

| Task | Test group | Evidence/outcome |
|---|---|---|
| Q084 | Source six-order CA/Swift/Slow illustration | **PASS:** 4 ROLLUP rows, Swift 5 orders/2.00 days; Slow 1/NULL; state and grand totals 6/2.33. Row values compared without assuming an unpublished sort requirement. |
| Q084 | NULL ShipDate, otherwise delivered | **KNOWN CONTRACT GAP REPRODUCED:** archived key counts missing ShipDate as delivered; grand total 2 and Slow detail row appear. Task specifies valid order → ship → delivery sequence; missing ShipDate policy requires provider clarification/correction. |
| Q084 | Missing State versus literal `Unknown` state | **CONDITIONAL IDENTITY GAP REPRODUCED:** key coalesces both to `Unknown` *before* GROUP BY, merging two distinct state categories into a single shipper cell of count 2. |
| Q084 | Empty delivered orders | **PASS / zero-input behavior observed:** native ROLLUP returns one grand-total row with count 0 and NULL average. No provider answer guarantee claimed. |
| Q090 | Source two-order/8-column illustration | **PASS:** eight ordered rows; PaymentID 50% overall and 0% recent; ShipperID, ShipDate and DeliveryDate 50% overall and 100% recent; distinct values match. |
| Q090 | Independent Jan-31 anchored 30-day boundary | **PASS:** 2026-01-01 excluded, 2026-01-02 included; PaymentID 2/3 missing overall and 1/2 recent (66.67% / 50.00%); ShipDate 66.67% / 100.00%. |
| Q090 | One order with NULL OrderDate | **PASS / undefined denominator observed:** eight column rows; OrderDate 100% null overall and NULL for all recent percentages, because no latest dated order exists. |
| Q090 | Empty Orders | **KNOWN TASK-SHAPE GAP REPRODUCED:** original query returns **zero rows**, although source asks for one row per each of eight Orders columns. Expected behavior on empty inputs and undefined percentage denominator is not specified. |

**Run provenance:** New [GitHub Actions job](../.github/workflows/validate-learning.yml) uses a disposable `postgres:16` service and isolated Python `psycopg[binary]==3.2.10`. First native CI run [43271148618](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43271148618) FAILED on an *auditor harness* API error (`psycopg.Connection` lacks `executemany`); corrected **only** the checker by using `cursor.executemany` in commit `08d896fb4c4378c5de462e65b110953045ba1be9`. Corrected [native run 43271295901](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43271295901) independently logged all eight test outcomes and exact original SQL execution. The entire workflow and final documentation-head CI require separate final verification: **do not use this ledger alone as proof of complete repository audit or final CI success**.

## Conservative reconciliation

- **Indexed:** P084 and P090 belong to the 205 P/A/X source records.
- **Statement inspected:** both original question bodies, examples and schemas independently checked; content hashes pinned.
- **Synthetic/native test executed:** eight groups executed on PostgreSQL 16 using the original archived key, with three documented contract/identity issues (Q084 missing ship date, Q084 Unknown state collision, Q090 empty dataset output). Known failure reproduction is not a contract pass.
- **Official answer verified:** **NO**. No provider-authenticated answer, original rendered PDF parity or full original Commerce Dataset v2 output validation.
- **Learner independently solved:** **NO**. Both historical learner records remain Pending/NOT SOLVED YET, unchanged.
- **Legacy conservative 94/205 bounded *clean* source-key replay tally:** **unchanged**, because Q084/Q090 have reproduced output-contract gaps. Native execution capability is now evidenced separately for these two IDs, but cannot certify the total task semantics.
- **Still open:** source-provider resolution of three contract cases; original PDF, ZIP and full Commerce dataset parity; MySQL/SQL Server cross-dialect policy where relevant; outstanding P089/P091/P093/P100 (and others) semantic/native gates; A/X official-source limitations; mentorship/Bosscoder/W3Schools/other DE and source-to-concept/licensing/privacy review; final verified comprehensive CI. GitHub Issue #1 **must remain OPEN**, and the separate ChatGPT Library learner-study record **must remain UNSYNCED** until complete signoff and final CI.
