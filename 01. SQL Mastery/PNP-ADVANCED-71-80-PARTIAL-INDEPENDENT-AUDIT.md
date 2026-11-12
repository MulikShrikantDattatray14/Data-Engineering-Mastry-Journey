# A071–A080 — partial independent preserved-source and bounded SQLite audit

**Date:** 2026-11-12. **Scope:** 10 individually read original Markdown records from the immutable `99. Reference Materials/Original Mastery Snapshot/` archive. The original provider PDF *attributions* (Advanced SQL 100 Query Questions, Vol. 1, pp.14–16) are not equivalent to reading or validating original PDF answer pages. The original Markdown samples are *locally illustrated*, not supplier input/output datasets. **No original archive or learner progress is edited.**

**Status vocabulary:** `indexed` = path/ID recorded; `statement inspected` = task + sample + schema + original learner field inspected and original Git blob pinned; `synthetic test passed` = reviewer SQL replay against a bounded declared SQLite fixture; `official answer verified` = *no* for every ID; `learner independently solved` = *no new evidence*, all ten original records remain `NOT SOLVED YET` and `Pending`. CI checker: [`scripts/check_pnp_advanced_71_80_sources.py`](../scripts/check_pnp_advanced_71_80_sources.py). Tests run locally in the repository's GitHub Actions CI; record exact final commit and CI outcome separately in Issue #1 only after checking it.

| ID | Preserved original Git blob SHA | PDF page attribution | Individually inspected statement | Bounded auditor-only fixtures implemented | Still unresolved |
|---|---|---:|---|---|---|
| A071 | `7b0a26b7a6a6343fd45bac299c1094f377642c90` | 14 | Department payroll salary share | illustrative 40/60/80; zero-payroll and NULL salary | NULL/zero denominator, employee with missing department |
| A072 | `8c4a92cfaba2acb7e7235ba03c2fafdeb110c3bb` | 14 | Median salary in MySQL | even 40/60/80/100; odd count with NULL ignored | even/odd policy, NULL exclusion, empty set, decimal midpoint |
| A073 | `f54d3676e0a921fa7a9caaf71bbd3fce461f7c62` | 14 | Top 20 percent customer spend | 5 customers; 6 customers with tied spend and ceiling rounding | ties, ceil/floor rule, customers with no orders, order status |
| A074 | `100e4cfc4e2a90e3911f17ad25dede61ff30d1b4` | 15 | Top 3 products by category revenue | archived 5-product illustration; ties and unsold products | product ties, join grain, discounts, returns, orphan items |
| A075 | `df907567f01bead61ff67afa5845aa5a7bf32dd5` | 15 | Latest payment per order | three local payments; same timestamp and NULL timestamp | unpaid orders, tie policy, payment status absent |
| A076 | `6b87c321406a65cdcdc346a81fe554877da20752` | 15 | Top 2 customers per city | local Delhi/Pune sample; tied spend and no-order city | rank versus row-number, city NULL, no-order inclusion |
| A077 | `3851825388394342b08a04c3b8c7ce11fdd80c91` | 15 | Second newest order per customer | local 4 orders; same-day tie and single-order exclusion | ties, null dates, canceled orders, order versus distinct date |
| A078 | `77c072224bf2f069b2468f2f299e7ca75f86f0d8` | 15 | Top 3 distinct salary bands without window function | local five employees; three bands with tied salaries | ties can return over three employees, NULL salaries, equal-department semantics |
| A079 | `390c1f009ed8cc0c101a047f32e74946bdf6c644` | 15 | Latest order whole row without CTE | local example; same-day tie, NULL-date rule | whether derived-table window qualifies as no CTE, ties, no-order customers |
| A080 | `b3741537d5ed13dd50ba5df11023ed7db542a60e` | 16 | Missing order ID ranges | 1/2/5/8 local illustration; duplicate IDs and multiple gaps | scope min-max only, duplicates, negative IDs, NULL values |

Each row is **statement inspected** and *implemented* for two reviewer-only SQLite fixture groups. The checker asserts original Git blob identity, the source question number/page label, shared schema, local sample marker, original NOT SOLVED YET flag, both learner query Pending fields and the official answer Pending field. A synthetic fixture pass, if observed in CI, is not proof of MySQL equivalence, original PDF answer correctness, grading, independent coursework or mastery. No official SQL answer was extracted or substituted.

## Distinct source limitations

A078 is stored under `6. SubQueries`, and A080 under `13. Gaps and Islands`; A071–A077/A079 are under `9. Windowing Functions`. These are one-to-one source records, not 10 contiguous files under a single directory. A072's synthetic median ignores NULL; A073 rounds up to include at least one of 1–5 customers and breaks ties by customer ID; A078 implements **top three distinct salary values**, potentially more than three employees; A079 uses a no-CTE derived-table window function; A080 searches gaps **between** observed min/max IDs only. All are disclosed reviewer assumptions, pending PDF/provider comparison. Engine-specific `MEDIAN` availability and Windows/MySQL portability are *not* claimed.

## Remaining acceptance gaps

Original PDF answer/page parity, original MySQL 8 runtime, full source datasets and expected results, learner-authored answer evidence, ambiguous ranking/tie and NULL/status policies, A081–A100/X001–X005, seven outstanding P-series native/semantic checks, Python/Bosscoder/W3Schools/Data Engineering source-to-concept, licensing/privacy and final comprehensive CI still require independent signoff. Preserve conservative P-series source-key replay tally **93/205** (these reviewer A-series cases do not count). The separate Library learning journal is NOT synchronized until complete independent audit and final passing CI. Issue #1 stays open.
