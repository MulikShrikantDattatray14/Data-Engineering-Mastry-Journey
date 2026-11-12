# PNP Q093: source-key double-submission denominator discrepancy — PARTIAL independent audit (12 Nov 2026)

## Evidence/provenance and classification

- **Indexed:** P093 exists in the 205-ID P/A/X catalog. **Statement inspected:** original archive \`99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/14. Data Quality and Deduplication/P093. Possible duplicate order submissions.md\`, immutable Git blob \`2b53cdb94d64cb19581be48c9af6f0a8670b72c2\`. Individually inspected business scenario, pair definition, order/header and order-detail schema, two-order example, five-column expected output, PDF pp.186–189 attribution **only**, and all historical \`NOT SOLVED YET\` / \`Pending\` learner/official fields.
- **Supplied key inspected:** archived \`Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql\` Git blob \`7912c8e676621c513e0b635a40c6ee299404676e\`; read entire Q93 source query from \`-- Q93.\` through the next question boundary. This is the bundled provider-attributed PostgreSQL key, **not independent provider-authenticated grade**.
- **Bounded synthetic test:** read-only [source-identity-pinned Q093 checker](<../scripts/check_pnp_93_source_pairs.py>) extracts original SQL, adapting exactly the ordered \`STRING_AGG\` to numeric-product-sorted aggregate, \`BOOL_AND\` to MIN(bool), and three-field \`IS NOT DISTINCT FROM\` to SQLite \`IS\` comparisons. The source's joins, filters, pair generation, aggregates, and verdict expression are preserved, not replaced by a reviewer solution. Checks one original illustrated row, a three-pair independent source, an empty dataset, and three deliberately reproduced NULL/missing-basket diagnostics. **Only count it as CI-validated once exact-SHA job logs confirm the new step passed.**
- **Official answer verified:** **NO**; original rendered PDF parity, native PostgreSQL result, full Commerce v2 dataset, provider grading and independent source approval unavailable in this tranche. **Learner independently solved:** **NO**; retained original historical unsolved and Pending states. Not a learner-study sync.

## Findings: task population vs supplied query

The **original task** demands the total number of *every pair* of orders placed by one customer on one \`OrderDate\`, even where a basket cannot be evaluated. The **supplied query** inner-joins \`Orders\` to \`signatures\` and applies \`WHERE sg.basket_known\` **before** generating \`same_day_pairs\`; it therefore removes header pairs involving orders without \`OrderDetails\`, orders with NULL \`Quantity\`, or NULL \`ProductID\`. These are exactly the kinds of data-quality cases this control may be expected to see.

| Bounded evidence case | Source statement expected in principle | Supplied key observed in SQLite with asserted adaptations | Contract status |
|---|---|---|---|
| Source illustration: two customer-10 same-day orders, same product 101 x2, equal amount/payment/shipper | \`(pairs=1, basket=1, amount=1, exact=1)\` | \`(1,1,1,1)\` | **PASS** on original example |
| Synthetic: customer 10 has three same-day orders, two same-basket but differing amounts; a separate day and customer excluded | \`(3,1,1,0)\` | \`(3,1,1,0)\` | **PASS** on bounded intact baskets |
| Empty input | 0 counts, no-review verdict | 0 counts, no-review verdict | **PASS** |
| Two same-day orders, one has **no lines**; amounts equal | \`same_day_pairs=1, same_amount_pairs=1\`, basket match undecidable | \`same_day_pairs=0, same_amount_pairs=0\` | **REPRODUCED DENOMINATOR DISCREPANCY** |
| Two same-day orders, both lines have **NULL Quantity**; amounts equal | \`same_day_pairs=1, same_amount_pairs=1\`, basket match undecidable | \`same_day_pairs=0, same_amount_pairs=0\` | **REPRODUCED DENOMINATOR DISCREPANCY** |
| Two same-day orders with matching baskets, both amount NULL, equal payment/shipper | NULL-amount equality policy needs provider confirmation | \`same_basket_pairs=1, same_amount_pairs=0, exact_copies=1\` | **REPRODUCED SEMANTIC INCONSISTENCY; policy open** |

Additional open interpretations: where two empty baskets should count as identical; customer/date NULL handling; distinction between payment method vs \`PaymentID\`; identity of duplicate line rows after product grouping; and how support Step 10's row-level list should relate to a control that emits only summary counts.

## Remaining gates / integrity

Native PostgreSQL 16 run of the unaltered query, actual source PDF pp.186–189, complete original dataset and authenticated provider output may alter the grading assessment. Validate a revised denominator policy with provider before suggesting modifications to archived answer. Q084 native ROLLUP and Q089/Q090/Q099/Q100 and the other known P-series gaps still require final verification. Previous **93/205 conservative passing supplied-key count is unchanged:** a checker that successfully reproduces a spec contradiction does **not** make Q093 a passed output-contract verification.

Auditor-controlled checker, new evidence ledger, workflow, and additive status log only; preserve all source archives, historical learner work, canonical foundation notes, and deferred ChatGPT Library learner record unchanged. Issue #1 remains OPEN pending independent entire-source audit, privacy/licensing review, cross-source concept signoff, and final comprehensive CI.

---

## Native PostgreSQL 16.15 addendum — 13 November 2026 (PARTIAL)

**New independent scope:** [exact original Q093 supplier-key native runner](../scripts/check_pnp_93_native_postgres.py) reads and Git-blob-pins the archived question `2b53cdb94d64cb19581be48c9af6f0a8670b72c2` and supplier Q1–Q100 key `7912c8e676621c513e0b635a40c6ee299404676e`, extracts untouched Q93 SQL, and executes **native** `STRING_AGG ORDER BY`, `BOOL_AND`, row-wise `IS NOT DISTINCT FROM` and FILTER aggregates on PostgreSQL 16.15 (server version `160015`). All data and tables are disposable PostgreSQL TEMP fixtures; this makes no mutations to archived records, learning progress or canonical notes.

**Independently inspected native logs:** [Actions run 43289920993](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43289920993) native job **SUCCESS**, with six fixture groups:
- Original illustrated two-order pair `(same_day_pairs=1, basket=1, amount=1, exact=1)` PASS.
- Independent three same-day pairs across five orders `(3,1,1,0)` PASS; day/customer isolation preserved.
- Empty Orders `(0,0,0,0)` PASS.
- Same-day equal header pair with **one absent OrderDetails row** yields `(0,0,0,0)` (**source contract denominator discrepancy reproduced**, expected header pair count is 1).
- Two same-day equal-amount orders with **NULL Quantity** yield `(0,0,0,0)` (**denominator discrepancy reproduced**).
- Matching baskets and NULL amounts yield `(pairs=1,basket=1,amount=0,exact=1)` (**NULL equality policy inconsistency reproduced**).

**Material conclusion:** these three previously SQLite-derived source/key divergences are now reproduced directly by the **unmodified** supplier PostgreSQL key, not an adapter. The `JOIN signatures` and `WHERE sg.basket_known` prefilter discards order pairs for the requested all-orders denominator. In contrast, native row-wise null-safe equality counts NULL-header exact copies while `=` does not count NULL amounts. Requires provider/business semantics, original PDF pp.186–189 and full dataset parity; **not** an authenticated official answer failure or a learner completion.

**Evidence tiers:** indexed YES; statement/key inspected YES; bounded native synthetic fixture checks PASSED for samples and discrepancies; official answer verified **NO**; learner independently solved **NO**. Original Pending badges/attempts preserved. The conservative **94/205** clean source-key tally remains unchanged, Issue #1 OPEN, pending Library learning record UNSYNCED until complete audit and comprehensive final CI.
