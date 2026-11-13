# Advanced SQL A001/A004/A005/A010 — preserved historical-answer native PostgreSQL partial audit (13 November 2026)

**State: PARTIAL; bounded independent regression evidence, not official PDF-answer authentication.** This audit is strictly about *previously recorded* historical learner SQL plus separately provider-attributed SQL quoted inside preserved Markdown. It creates **no** new independent learner completion or mastery. The [checker](../scripts/check_pnp_advanced_historical_01_04_05_10_native_postgres.py) loads both exact SQL code fences directly from four SHA-pinned original source files. It executes the unmodified SQL on disposable native PostgreSQL 16 tables with *independently asserted*, not source-PDF-provided, expected results. It does not edit those sources, study records, or canonical foundations.

## Immutable original Markdown anchors and evidence levels

| Archived ID | Original Git blob SHA-1 | Historical learner status | SQL queries compared | Explicitly limited evidence |
|---|---|---|---|---|
| A001 | `0b9306e594b206fd99612baff55d2f28a53060dd` | SOLVED recorded 2026-10-27 | Learner `LEFT JOIN + COUNT(e.emp_id)`; provider-attributed `LEFT JOIN + COUNT(e.emp_id)` with different projection | Source statement & two snippets inspected; bounded synthetic execution after CI; **not independently authenticated PDF key** |
| A004 | `eb5d2da2b0ba565a913599ca5137d9cb33599693` | SOLVED recorded 2026-10-27 | Learner NULL-filtered `NOT IN`; attributed left anti-join | Source statement & snippets inspected; bounded synthetic execution after CI, not official authentication |
| A005 | `dac439085707ed03c458bfd8fae06a9455131559` | SOLVED recorded 2026-10-27 | Learner NULL-filtered `NOT IN`; attributed `NOT EXISTS` | Source statement & snippets inspected; bounded synthetic execution after CI, not official authentication |
| A010 | `8443513ecb9e95928d475f636011d63c01f1fcf5` | SOLVED recorded 2026-10-28 | Learner employee/manager self-join; attributed self-join | Source statement & snippets inspected; bounded synthetic execution after CI, not official authentication |

All four have locally authored sample input/output tables, explicitly *not* separate source-PDF sample data. PDF p.2–4 rendering, exact original attributed-answer parity, complete original dataset parity, MySQL 8 and SQL Server runs are **not established**.

## Native PostgreSQL 16 fixture design — 12 independent groups

Each fixture starts fresh isolated TEMP tables and asserts the two archived queries separately against expected row tuples, ignoring row ordering because the saved SQL does not demand `ORDER BY`. Differences in projections are **not** concealed: A001 learner emits `dept_id,dept_name,employee_count` while attributed output emits `dept_name,emp_cnt`; A005 learner returns only order ID while attributed SQL returns ID plus amount; A010 learner returns employee ID/name while attributed SQL returns employee name/salary and manager name/salary.

| ID | Original illustrative scenario | Independent adverse/boundary scenario | Empty/absence scenario |
|---|---|---|---|
| A001 | Sales 2; Support 0 | duplicate department *names* across distinct IDs; orphan and NULL employee department IDs; counts kept separate by ID | no department rows, orphan employee |
| A004 | Mira with no order | duplicated matching orders, unmatched customers, a NULL foreign-key order, an orphan order, and NULL customer name | both source tables empty |
| A005 | delivered unpaid order 11 | duplicated payments, NULL payment FK, orphan payment, unpaid zero/NULL-amount delivered orders, excluded lower-case delivered and non-delivered statuses | no orders or payments |
| A010 | Bela above manager Asha | salary equality; NULL salaries; orphan manager; multi-hop manager chain; self-manager equal salary | empty employee table |

**Pre-existing status:** A004/A005 source snippets had already passed eight bounded SQLite fixtures in `check_pnp_advanced_01_10_sources.py`; this check adds **native PostgreSQL** and different projection-aware assertions. A001/A010 also had earlier independent SQLite replays. No unique P/A/X ID is newly indexed or historical status updated.

**Open semantics:** A001 identical department names yield distinguishable rows only in the learner projection; the attributed projection lacks `dept_id`. A005 explicit case-sensitive `status='DELIVERED'` native PostgreSQL behavior does not establish equivalence to a MySQL table with case-insensitive collation. A004 NULL FK handling assumes non-NULL customer primary keys. A010 NULL or unknown managers are excluded by inner join; output columns differ. The exact original PDF statements, schema constraints, collations, full data and provider-answer provenance require independent signoff. A passing synthetic probe must **not** be promoted to official-answer verification, and prior historical SOLVED badges must not be represented as newly independently solved exercises.

**CI verification (verified code/workflow head, not final documentation head):** At exact workflow commit `dd7f0109b575e1d4f77e06a86f027d552ebff326`, [GitHub Actions run 43352330752](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43352330752) completed **SUCCESS**. Independently inspected native job `131646118269` step #14 and decoded logs: original SHA pins, PostgreSQL `server_version_num=160016`, and **12/12 PASS** fixture groups for both *unmodified* archived snippet projections. Both jobs concluded SUCCESS. [Documentation-head run 43352429403](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43352429403) was separately requested at `baa4c2569ad38d66d8fbfa2b20ca0d2e39e14d81`; final additional documentation commits require their own exact-head CI verification. This proves only bounded tests, **not** complete source audit or independent official-answer authentication. **Full 205-source audit and separate post-audit Library learning sync remain OPEN/DEFERRED.**
