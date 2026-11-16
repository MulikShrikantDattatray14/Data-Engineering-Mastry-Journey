# PNP Q091 — full original Commerce Orders cohort-LTV differential (PARTIAL)

**Independent audit:** 16 November 2026. **Status:** Not signed off; exact-head CI, source PDF visual parity, provider grading, full 205-question checks and licensing/privacy remain separate gates. This ledger is an audit-only addition, **not** new learner content or an official answer.

## Reopened preserved original evidence (not only an index)

| Read-only source | Git blob SHA | What it establishes |
|---|---|---|
| `12. Dates and Time/P091. Cumulative value per customer by cohort (LTV curve).md` | `cf11e56982938b3227f711e00534237f88d451aa` | Actual task/schema, source-supplied four-order illustration, quarter cohort contract; historical `NOT SOLVED YET`, SQLite/SQL Server `Pending`, official `Pending` |
| `Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql` | `7912c8e676621c513e0b635a40c6ee299404676e` | Actual unchanged supplier-attributed PostgreSQL Q91 section; **not** authenticated provider grading |
| `Source Materials/PrepNPlaced_SQL_100_v2/data/load_dataset_v2.sql` | `3787743252d29268c67c491d6a2eb47c1757c35b` | Native `Orders` typed schema, `NUMERIC(12,2)`, `OrderDate` parsed `DD-MM-YYYY` |
| `Source Materials/PrepNPlaced_SQL_100_v2/data/Orders.csv` | `307acc9ad2f85a79d7637a7958ffd62f2a8fa594` | Original source record population, **46,438** orders; the auditor never overwrites it |

Previously documented [source/key contradiction](PNP-Q091-SOURCE-COHORT-DISCREPANCY-PARTIAL-AUDIT.md) remains: the illustrated 2025-Q1 m12 of 200 and 2026-Q1 m0 of 80 are **NULL** in the source-supplied SQL when the maximum observed order is 2026-01-31. The key's maturity gate requires the *entire acquisition quarter* plus the requested offset to have elapsed; the illustration instead credits the January entrants. Earlier native PostgreSQL fixtures reproduced this mismatch; no provider ruling has resolved the intended cohort maturity interpretation.

## New, independent full-original-data review

[Read-only reviewer](../scripts/check_pnp_q091_full_original_orders_cohort.py) is intentionally different from the earlier [bounded four-case native reviewer](../scripts/check_pnp_91_native_postgres.py). It validates the **four original Git blob identities** and the unchanged learner Pending fields, reads **every** source `Orders.csv` row, converts each `DD-MM-YYYY` date and nullable amount without changing original source rows, and loads only `OrderID, CustomerID, OrderDate, Total_Order_Amount` to a **transaction-scoped PostgreSQL 16 TEMP table**. It runs the **unaltered** Q91 supplier SQL, with no SQLite translation, rewritten COALESCE or repaired maturity gate.

A **separately coded Python date/Decimal oracle** computes first order by customer, acquisition calendar quarter, non-NULL customer denominator, month offset buckets 0–12, cumulative values through 0/3/6/12 and the **supplier policy** for quarter-end last-observed *full* month. It uses `Decimal` and half-away-from-zero two-place rounding (PostgreSQL `numeric` behavior). It independently distinguishes **key-output parity** from **question-contract correctness**: even an exact match for full original data cannot make the two contradictory illustrated cells pass or authenticate a supplier grade. It avoids printing individual purchase or customer records; diagnostic output is aggregate quarterly counts and curves only.

Nine bounded/source-data tests are defined: immutable blobs and historical state; native PG16 version; the source four-row **two-cell mismatch**; exact full-original-row cohort differential, including ordered aggregate tuples and summed cohort denominators; actual last-date/full-month maturity policy; month-end boundary; same-month multiorder/negative/rounding semantics; NULL amounts/customers/dates and empty dataset; pending learner/official fields. **A committed test is not independently a passed test.** Read final native workflow logs and match the tested SHA to live main before claiming execution PASS.

## Exact evidence-tier boundaries

**Indexed:** already yes, Q091 one of original 205. **Statement inspected:** yes, original task, schema, illustration, supplier key and loader individually reopened with immutable pins. **Synthetic test passed:** this new suite requires its own CI proof; earlier native Q091 bounded tests have been verified separately. **Actual-source output verified:** pending final run evidence. **Official answer verified:** **NO** (both contradictory source example and no authenticated provider grading). **Learner independently solved:** **NO**; original pending fields are preserved. **Mastery:** **NO**.

Do **not** increment the conservative distinct clean PNP supplier-key count (**94/205**) for repeat inspection or for a mismatch. Original PDF pp.180–184 not rendered, complete 205 SQL output/semantics, Python mentorship, Bosscoder Python/SQL lectures/assignments, W3Schools, other DE, rights/PII and complete source-to-concept final signoff remain open. [GitHub Issue #1](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/issues/1) must stay **OPEN**. The separate ChatGPT Library `/Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md` plus later practice are **UNSYNCED** until independent full-audit signoff plus a **separate successful post-sync CI**.


## Direct native CI log evidence: original whole-Orders result (16 November 2026)

The *implementation/workflow-head* [Actions 43810020879](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43810020879) **completed/success** at exact SHA `f562df52892843fbfe48c2c31bbc7cd4d9050cd2`. Independently decoded its PostgreSQL job `133109394073`: **all nine named `Q091FullCommerceCohortReview` tests `ok`, `Ran 9 tests`, `OK`**, including the entire 46,438-row differential, historical Pending guard, original illustration contradiction, native PG version and bounded data-quality edge cases. The job log says **12 quarterly cohorts**, **4,427 unique non-NULL dated customers** across them, first cohort 2023-01-01, last 2025-10-01. Latest source order 2025-12-28; supplier last fully observed month computes to 2025-11-01.

**Exact matching original-source tuples (unaltered PostgreSQL Q91 SQL = independently coded Python Decimal oracle for the *supplier maturity policy*):**

| Acquisition quarter | Customers | m0 | m3 | m6 | m12 |
|---|---:|---:|---:|---:|---:|
| 2023-Q1 | 203 | 2895.27 | 7424.71 | 11414.38 | 19553.06 |
| 2023-Q2 | 126 | 2110.10 | 6849.02 | 10981.25 | 16357.10 |
| 2023-Q3 | 138 | 1936.66 | 7087.96 | 10611.94 | 15786.41 |
| 2023-Q4 | 206 | 1835.81 | 5513.52 | 8064.22 | 12722.01 |
| 2024-Q1 | 220 | 2369.60 | 6719.33 | 10720.40 | 17021.09 |
| 2024-Q2 | 228 | 2368.85 | 6388.72 | 10073.38 | 15306.44 |
| 2024-Q3 | 301 | 1725.03 | 6657.23 | 10204.10 | 15939.99 |
| 2024-Q4 | 445 | 2164.06 | 6971.86 | 10227.62 | NULL |
| 2025-Q1 | 464 | 2144.52 | 6392.78 | 10129.42 | NULL |
| 2025-Q2 | 501 | 2103.59 | 6416.20 | NULL | NULL |
| 2025-Q3 | 591 | 2215.92 | NULL | NULL | NULL |
| 2025-Q4 | 1004 | NULL | NULL | NULL | NULL |

All twelve original-key rows matched independent reference row-for-row, but this **does not resolve** the two original illustrated source contract discrepancies. The youngest 2025-Q4 cohort's m0 is NULL under the unchanged source supplier's **entire-quarter** maturity rule; do not silently label that a provider mistake or confuse that policy with each customer's independently acquired-month maturity. The first **tested** implementation head passed; any **later** documentation/status main SHA still needs its own exact-head complete CI verification. Actual-source output test **PASS**, *official answer verified* **NO**, *learner independently solved* **NO**, clean distinct key tally **94/205 unchanged**.
