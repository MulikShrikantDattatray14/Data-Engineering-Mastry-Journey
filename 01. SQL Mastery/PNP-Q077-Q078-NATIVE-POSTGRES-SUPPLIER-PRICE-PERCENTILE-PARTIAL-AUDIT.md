# PNP Q077/Q078 — native PostgreSQL 16 original-key replay and boundary forensics (PARTIAL)

**Audit date:** 16 November 2026. Q077/Q078 are **previously indexed, statement-inspected and bounded SQLite-compatibility replayed** in [the existing reviewer](../scripts/check_pnp_77_80_source_answers.py). This pass adds **unchanged original supplier SQL on actual PostgreSQL 16** and new conditional data-quality boundaries. It does **not** increase the count of unique PNP questions, authenticated provider answers, learner independent completions or mastery.

## Exact original-source identities

| Evidence | Original immutable Git blob |
|---|---|
| `2. Joins/P077. Single-source products and the value at risk.md` | `22d728c1686886684dcea80381b71303aed52056` |
| `9. Windowing Functions/P078. Expensive within their sub-category but selling below its median.md` | `c8baea659a6c96edd55d0eed03b805907d05a681` |
| `Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql` | `7912c8e676621c513e0b635a40c6ee299404676e` |

All paths above are under `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/`. The archived statements attribute Q077 to supplier PDF pp.144–146 and Q078 to pp.146–148. **Original rendered PDF parity remains unverified**. Both question files still display **NOT SOLVED YET**, learner solutions **Pending** in both dialects and official solution **Pending**. The bundled PostgreSQL SQL is a *provider-attributed answer key*; it is not independently authenticated provider grading.

## Method and granular claims

[Read-only PostgreSQL reviewer](../scripts/check_pnp_q077_q078_native_postgres_supplier_price_percentile.py) Git-blob-pins both exact original question files and the original key, extracts the unmodified `-- Q77.` and `-- Q78.` statements, creates disposable PostgreSQL transaction-scoped TEMP tables, executes the unaltered `WITH` queries and asserts exact result rows. This differs from the prior SQLite exercise, which translated `PERCENTILE_CONT` and casts. The new reviewer contains **15 named tests** (two source/runtime guards, two source illustrations, eleven boundary checks). **A successful reviewer establishes bounded synthetic execution only; it does not inspect the full Commerce v2 CSV or supply the official result set.**

### Q077 — sole supplier and list-price share

- **Original illustration inspected:** one eligible 101/Keyboard line source; value 20 of total 70 (28.57%). Products 102 (two suppliers) and 103 (one NULL supplier) excluded.
- **Original SQL contract:** `COUNT(DISTINCT SupplierID)=1` and `COUNT(*) FILTER (WHERE SupplierID IS NULL)=0`. Repeated lines from the same supplier do not disqualify the product; a single NULL supplier line does. **Excluded products' list-price amounts correctly remain in the overall denominator**, not just the single-supplier numerator.
- **Conditional orphan/missing catalogue data:** an order line may have ProductID absent from `Products`. The original LEFT JOIN retains it with `Unknown product`, a **NULL list-price value and NULL percentage**. That line contributes no value to `SUM` and cannot be valued without an original catalogue price. A missing supplier dimension row gets `Unknown supplier` and country `Unknown` even when SupplierID is present. These are expected fallback mechanics, **not evidence of real CSV orphans**.
- **Zero total list value:** numerator value 0 is reported, while `NULLIF(total_value,0)` produces an undefined (NULL) percentage. The task does not establish a policy of returning 0% for this denominator. No-supplier/no-order-line inputs yield no result.
- **Outstanding:** actual original CSV foreign-key/null/price/quantity population, duplicate product/supplier primary-key constraints and financial policy on missing prices or negative quantities.

### Q078 — price percentile rank vs product-unit median

- **Original illustration inspected:** 20 Hair care products with increasing price 1–20; first 19 sell ten units each; premium product 20 sells zero. Result is product 20, `price_pct_rank=1.00`, `units_sold=0`, median 10.
- **Native `PERCENT_RANK()` tie semantics:** when products 19 and 20 share the highest price, both return approximately `0.95` rather than `1.00` and can satisfy the premium/low-sales filter. A 19-product sub-category is excluded by the explicit minimum; an all-tied 20-product category has percentile rank zero for every item.
- **Conditional source-contract ambiguity — missing price:** the archived task requires sub-categories with **at least 20 products**, and asks that the median count every product including zero sellers. The supplied query first removes `Sale_Price IS NULL` rows in `scored`, then computes `COUNT(*) OVER` and the median **only among priced products**. With **20 listed products and one NULL-priced product**, it judges the sub-category to have 19 products and excludes all candidates, even though 20 are listed. The affected missing-price policy and whether these rows can exist in the original CSV remain **unverified**. This is a *conditional contract discrepancy*, not proof of an actual dataset defect or provider-grading error.
- **Conditional missing sub-category:** the original query intentionally excludes `Sub_Category IS NULL`, so it cannot price-rank those products even if 20 such listings exist. No source policy defines these as a separate group. When all products have zero units, the median is zero and none is strictly below it.
- **Outstanding:** original Commerce v2 price completeness, exact PDF statement parity, authenticated supplier ranking/NULL policy, and full-data output verification.

## Evidence tiers and current gate

| Tier | Result |
|---|---|
| Source indexed | Previously yes; no new count |
| Original Q077/Q078 Markdown statements independently inspected | Yes, rechecked |
| Bundled supplier SQL text identified and hash pinned | Yes, previously; unchanged |
| Native PostgreSQL 16 execution of the unmodified supplier SQL | **Requires exact-head CI review before final PASS claim** |
| Bounded original illustration and counterexample assertions | Reviewer created; do not claim successful until named CI tests confirm |
| Authenticated official answer/output validation | **No** |
| Learner independently solved / mastery | **No / No** |
| Original PDF rendered-page and eight-source-CSV full-data parity | **No / No** |

**Still open:** no edit to any original archive, historical learner attempt/status, or canonical foundation; retain Issue #1 OPEN. Conservative supplied-key count **94/205 remains unchanged**. Separate ChatGPT Library learner-study evidence and subsequent practice must remain **UNSYNCED to GitHub** until complete independent audit, exact-main CI signoff, then a separate learner-sync review and post-sync passing CI. Also unresolved: remaining PNP/Python/Bosscoder/W3Schools/DE full source-to-concept reviews and public course-content rights/PII clearance.
