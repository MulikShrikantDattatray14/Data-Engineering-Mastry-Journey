# PNP P100 monthly KPI scorecard — independent source/key partial audit (12 November 2026)

## Immutable source and evidence tiers

- **Question statement inspected:** Original preserved P100 question under 99. Reference Materials / Original Mastery Snapshot / 1. SQL Mastery / 1. SQL Mastry / 2.PNP- foundations and practice / 15. Analytics and Performance. Original Git blob **1c6b25889256fa585ef272b581a676a98759e555**. Inspected the requested eight KPIs, the 2026-12-28 five-order example, original PDF pp.210–213 **attribution only**, Orders/OrderDetails schema, NOT SOLVED YET and learner/official solution fields **Pending**. These are not learner completions.
- **Supplied PostgreSQL key inspected:** Original bundled all_100_solutions.sql Q100 block, Git blob **7912c8e676621c513e0b635a40c6ee299404676e**. Archive key is not a provider-graded answer or a learner-submitted solution.
- **Read-only runtime checker:** [P100 original-key checker](../scripts/check_pnp_100_source_kpis.py) checks both immutable Git blobs, extracts the **original** PostgreSQL SQL from the pinned answer key, and performs explicitly asserted SQLite compatibility adaptations: dates, casts, numeric date difference, LEAST and correlated LATERAL VALUES presentation. The business CTEs, original period_units INNER JOIN, KPI filters and comparisons stay source-derived. This is bounded SQLite-adapted **synthetic replay**, not native PostgreSQL or official output verification.

## Question-level findings

1. **Label contradiction:** the archived P100 illustrative output labels KPI 7 **On-time delivery**, whereas the supplied answer's literal KPI label is **On-time delivery (<= 7 days)**. Numerical rows may match, but exact output names do not. Do not silently overwrite either original.
2. **Missing line items cause all eight KPIs to vanish:** the supplied key computes period_units by INNER JOINing Orders with OrderDetails and INNER JOINs those period units into aggregated KPIs. If valid header orders exist in either month without any associated lines, that period is excluded from KPIs and the final latest/prior JOIN produces **no scorecard rows**, despite count/order-value/active-customer metrics still being computable. Both missing-prior and missing-latest cases are checked independently.
3. **No prior-month orders:** the supplied key produces no rows for a latest month that has orders and a prior month that has none. The question does not prescribe exactly how to render percentages and money with zero denominators; policy requires clarification before a corrected solution is approved.
4. **NULL Quantity vs missing rows:** a matching line whose Quantity is NULL leaves the report present with Units NULL, contrasting with fully missing OrderDetails that erase the report. This deserves separate data-quality policy.

## Five narrow test groups

| Group | Expected observed behavior | Audit tier |
|---|---|---|
| Original five-order source sample | Eight numerical KPIs and November 1–28 versus December 1–28 windows; source/key seventh-label divergence | Original illustration numerics, **not exact output label match** |
| Missing OrderDetails in either period | Zero rows, contrary to the requested eight KPI output when orders exist | **Known key defect reproduced**, not correct business answer |
| February 28 / March 31 and invalid early delivery | Prior month capped at February 28; invalid delivery excluded; eight KPI rows | Synthetic boundary |
| Latest-only month and empty Orders | No output for latest-only/prior-empty; empty Orders produce no rows | Unresolved zero-comparison policy |
| Existing lines with NULL Quantity | Eight metric rows survive, Units NULL | Synthetic NULL boundary |

Checker fixture PASS claims require exact-commit GitHub Actions confirmation. Deliberately passing tests of **known source-key failures** do not count as provider correctness.

## Remaining and preservation

P100 remains **partial** pending native PostgreSQL, authentic PDF and full Commerce v2 dataset parity, exact label policy, absent line/no-prior treatment and final reviewed correction. The existing conservative tally **94/205 source IDs with bounded passing P-series key tests must not increase for P100**, because it exposes nonconforming outcomes; this does not represent 94 authenticated official solutions or learner solves. Other P-series gates, A/X source-answer verification, Python mentorship, Bosscoder, W3Schools, other Data Engineering curriculum, privacy/licensing and full source-to-concept signoff remain open. Original source archives, historical learner attempts/progress, foundation notes and learner completion flags are untouched. Issue #1 stays **OPEN**. Separate ChatGPT Library pending study record remains **UNSYNCED** until independently completed full audit and final comprehensive green CI.

---

## Native PostgreSQL 16.15 independent addendum — 13 November 2026

**Source provenance and preserved history:** Re-inspected immutable P100 statement Git blob `1c6b25889256fa585ef272b581a676a98759e555` and original 100-key PostgreSQL SQL Git blob `7912c8e676621c513e0b635a40c6ee299404676e`. The historical archived badge still says **NOT SOLVED YET**; learner and purported official-solution fields in the question record remain **Pending**. Supplier ZIP SQL is a *supplied source answer*, not a provider-marked learner solution.

**Independent execution advancement:** [Native P100 checker](../scripts/check_pnp_100_native_postgres.py) SHA-guards both source blobs and extracts Q100 unmodified. It executes the original PostgreSQL SQL on disposable `CREATE TEMP TABLE ... ON COMMIT DROP` fixtures. No SQLite translations, no canonical notes, no original archive writes. [Native GitHub Actions execution 43299631570](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43299631570), native job ID `131467009050`: independently inspected decoded logs showing PostgreSQL `server_version_num=160015` and all five groups below. The code-head run's full other-job conclusion and later documentation-head CI require separate confirmation.

| Original-key native fixture | Observed output / audit meaning |
|---|---|
| Original five orders, Nov/Dec 1–28 | Eight numerical KPI values, percent changes and both windows agree with source illustration; seventh literal KPI name differs: expected `On-time delivery`, key yields `On-time delivery (<= 7 days)` |
| Missing OrderDetails in prior **or** latest period | Reproduced **zero** returned KPI rows even though `Orders` contains order headers in both periods; source INNER JOIN removes an entire period |
| Latest orders but no prior-month orders; also empty Orders | Both yield **zero** KPI rows; for latest-only the task's desired no-prior baseline rendering remains unspecified |
| Feb 28 / Mar 31 with delivery preceding OrderDate | Eight rows, correct capped windows; erroneous pre-order delivery excluded from on-time denominator |
| Matching OrderDetails rows with NULL Quantity | Eight KPI rows remain, but Units prior/latest are NULL; distinguish from fully missing detail rows |

**Evidence tiers:** P100 is `indexed`, `statement individually inspected`, and `original supplied SQL native synthetic-tested`, with the original sample numerical values matched and **three output/contract gaps reproduced** (label, missing details, no-prior display policy). This is **not** official-answer verified; no learner independently solved it; no mastery or duration can be inferred. Even successful negative regressions do **not** make P100 a clean full-task answer. The conservative 94/205 clean bounded supplied-key tally must stay unchanged.

**Remaining:** Provider PDF pp.210–213 *rendered* parity and complete source Commerce Dataset v2, exact business policy for missing detail rows / absent prior period / null-unit semantics, corrective answer review, all other SQL source-key gaps, Bosscoder, Python mentorship, W3Schools, other DE subjects, source-to-concept provenance, privacy/licensing and comprehensive audit-wide CI/signoff. Issue #1 stays OPEN. The separate ChatGPT Library learner record and later study evidence remain **UNSYNCED** until full audit signoff plus final green CI. Original archives, history and canonical notes were not modified.
