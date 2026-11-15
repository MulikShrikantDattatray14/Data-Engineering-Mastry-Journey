# PNP Q079/Q080 — original supplied SQL on native PostgreSQL 16 (PARTIAL)

**Audit date:** 16 November 2026. These two PNP foundation questions were **already indexed and statement-inspected**, and their original supplier SQL had been replayed in a separate SQLite compatibility reviewer. This record adds **unchanged-source native PostgreSQL** execution, bounded validation and conditional data-quality policy checks. No newly authenticated official answers, independently completed learner exercises, or mastery.

## Primary source identities and tiers

| Source | Unchanged Git blob |
|---|---|
| Preserved original PNP Q079, `9. Windowing Functions/P079. At which order does a customer cross 10,000 in spend.md` | `8446d5ea1b09182909e452ce05b4c62141f6bdb4` |
| Preserved original PNP Q080, `6. SubQueries/P080. Sub-category repurchase rate within 90 days.md` | `49c42503bdf27ed5369854f47011360329e6ab45` |
| Bundled provider-attributed PostgreSQL reference key, `Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql` | `7912c8e676621c513e0b635a40c6ee299404676e` |
| Original dataset load script, `Source Materials/PrepNPlaced_SQL_100_v2/data/load_dataset_v2.sql` | `3787743252d29268c67c491d6a2eb47c1757c35b` |
| Dataset README, `Source Materials/PrepNPlaced_SQL_100_v2/README.md` | `eb75fac446057899effefcb10029ff2048674ea2` |
| Instructor planted-data-issues source | `6f4da61474880372a6e269b17ffc7958350541e6` |

All paths above are relative to `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/`. Source questions attribute Q079 to PDF pp.148–150 and Q080 to pp.151–153. Actual rendered original PDF page parity remains **unverified**. Both preserved question files retain **NOT SOLVED YET**, both dialect-specific learner solutions **Pending**, and official display **Pending**. The bundled source-key query is not authenticated provider grading.

[Read-only native reviewer](../scripts/check_pnp_q079_q080_native_postgres_retention.py) verifies all three question/key blob SHA values, extracts the **original unchanged** Q79/Q80 `WITH ...` statements, and executes against disposable transaction-scoped PostgreSQL 16 temporary tables. It contains **15 reviewer methods** (two provenance/runtime checks, two original examples and eleven bounded synthetic/conditional cases). Outcomes below describe independently inspected source semantics, and their native-runtime outcomes must be distinguished until exact-head CI confirms them.

## Individual source-contract checks and expected outcomes

**Q079: first order reaching cumulative spend 10,000**

- Original four-order illustrative source example: customer 10 crosses on order 3, 2026-01-10, nine calendar days after first, with running spend 10,000; customer 20 never crosses.
- The original reference query uses `ORDER BY OrderDate, OrderID` for deterministic same-day order rank; window `SUM(COALESCE(amount,0))` and `DISTINCT ON (CustomerID)` select the **first chronological crossing**, not the latest crossing. Synthetic tests include same-date out-of-input order IDs, refunds after a crossing, NULL order amounts and excluded NULL customer/date rows. Whether negative refunds should reverse a previously granted loyalty tier is a **business-policy question**, not adjudicated by a passing SQL test.
- SQL replay here is only a test of the attributed reference query on synthetic data; no original Commerce v2-wide result set was independently compared to the source PDF.

**Q080: within-90-days sub-category repurchase**

- Original illustrative source: 30 Tea buyers on 2026-01-01, six later-day repeats on 2026-01-20, latest overall order on 2026-04-15; output is Tea: 30 buyers, six repeaters, 20.00%.
- Distinct `(CustomerID, Sub_Category, OrderDate)` purchase days prevent duplicate order lines and same-day extra orders from falsely counting as later-day repurchases. Date `+ 90` is inclusive, day 91 excluded; first purchase on the 90-day-before-anchor cutoff is eligible, following day excluded. A later purchase in a **different sub-category** does not count as a repeat of the original one.
- **Reproduced conditional NULL sub-category flaw to test on native engine:** the original `GROUP BY` places all 30 real buyers in a NULL sub-category, but the `repeaters` existence check uses `later.Sub_Category = e.Sub_Category`. SQL `NULL = NULL` is UNKNOWN, so even 30 genuinely returning customers are reported as **0** repeaters. This is a **source/query data-quality-policy gap**, not proof the actual dataset has such NULL sub-categories.
- **Conditional missing identity:** the source SQL groups and counts a NULL `CustomerID` as an eligible buyer, even though no identifiable person exists. The original provider's load script defines `Orders.CustomerID INT` **without NOT NULL/FK**, and transforms blank staging IDs using `NULLIF(customerid, '')::int`; thus the database schema permits NULL identities. **Whether the actual CSV contains NULL CustomerID remains unverified**, so this is a feasible schema-level caveat, not a proven population defect.
- The source provider's README says customer, order, supplier and courier data were generated but the 22,088-product catalogue names/brands/prices originate from a real store; **redistribution/license rights have not been independently verified**. This provenance warrants continued public-content rights review, not a claim of infringement.

## Verification categories and blockers

| Category | Result |
|---|---|
| Original files indexed | Yes, previously |
| Original Q079/Q080 statements individually inspected | Yes, previously and reconfirmed |
| Original unchanged supplier SQL executed on native PostgreSQL | Pending exact-sha Actions result at first authoring; verify reviewer step and logs before updating |
| Original bounded displayed-output match | Pending exact-sha native replay; previous SQLite compatibility check already existed |
| Conditional counterexamples | Reviewer-authored fixtures; do not label as original dataset failures |
| Authenticated official/provider graded answer | **No** |
| Learner independently solved | **No** |
| Original PDF visual parity and complete original eight-table CSV replay | **No** |

**Required follow-up:** independently inspect exact-head GitHub Actions status and all named reviewer tests; reconcile any failure without changing archived source/answers. Independently load and validate the entire original eight-CSV Commerce v2 schema, NULL counts and Q079/Q080 original full-result outputs; render/check source PDF pp.148–153; seek authenticated provider policy for missing identities/sub-categories and full original answer grading. Complete other PNP/Python/Bosscoder/W3Schools/DE, licensing/PII and source-to-concept checks. Keep GitHub Issue #1 **OPEN**. Conservative clean supplied-key coverage stays **94/205** (these two are not newly unique). The Library learner-study record and later study stay **UNSYNCED** with GitHub until full signoff plus separate post-sync CI. Original sources, historical attempts, progress and canonical notes must remain untouched.
