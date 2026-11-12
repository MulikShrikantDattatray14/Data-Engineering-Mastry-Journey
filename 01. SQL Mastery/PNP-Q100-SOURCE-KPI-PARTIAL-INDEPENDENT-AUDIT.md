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
