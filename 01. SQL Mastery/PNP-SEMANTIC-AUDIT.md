# PNP SQL — Targeted Source Semantics and Regression Audit

**Scope (2026-11-09):** This is a **focused technical audit**, not a claim that all 205 indexed PNP questions were independently solved or exhaustively code-tested. The original task statements and their learner-answer status remain unmodified in the [PNP problem index](PNP-PROBLEM-INDEX.md). The entire source inventory is preserved separately.

## Source-specific questions inspected

| ID | Source requirement or important edge case | Verification state |
|---|---|---|
| A002 | Second highest **distinct** salary without `LIMIT` or window functions; duplicate salaries and fewer than two distinct non-NULL values matter | Question text checked; learner solution pending |
| A003 | Third highest **distinct** salary, ties collapsed; missing third distinct rank must have an explicit policy | Question text checked; learner solution pending |
| A004 | Customers who never ordered; nullable order customer IDs make bare `NOT IN` unsafe | Source learner answer preserved; NULL anti-join regression fixture executed |
| A005 | Delivered orders with no payment; official SQL uses `NOT EXISTS` and returns **order ID plus amount**, while the learner's saved solution returns **ID only** per illustrative expected output | Source/answer contract discrepancy documented; learner record unchanged; anti-join NULL fixture executed |
| P001 | Brand directory: `TRIM`, blank rejection, deduplication and alphabetical sorting; missing and whitespace brands excluded | Previously verified learner reattempt; no new solve credited |
| P004 | Label invalid emails; `CASE` precedence and NULL labels; `LIKE` pattern is a simplified requirement, **not RFC-compliant email validation** | Previously verified learner reattempt; no new solve credited |
| P043 | Month-to-date totals: last three **calendar** months based on latest order; first aggregate **all orders per calendar day**, then window-sum partitioned by month | Source inspected; same-day duplicate/MTD SQLite regression fixture executed; source learner solution pending |
| P058 | Exactly one latest order per customer; same-day ties broken by **highest OrderID**, unknown customer fallback and final ordering | Source inspected; deterministic tie-break SQLite fixture executed; learner solution pending |
| P069 | Growth across consecutive **active** quarters of the latest year; Q1→Q2→Q4 qualifies if strictly increasing, whereas Q1→Q2 decline fails | Source inspected; active-quarter `LAG` SQLite fixture executed; learner solution pending |
| P074 | Compare latest amount with average **earlier** orders only, at least three prior non-NULL amounts, latest 90-day cutoff relative to **latest date in the data**; beware average including latest and zero denominator | Source and example inspected; no full query/output audit yet; learner solution pending |
| X001 | Rated product share by category, including products referencing a missing Category row; rated means non-NULL Rating, not positive Rating | Source and illustrative output inspected; no independent learner solution; bundle has no official answer key |

These eleven IDs span advanced SQL, basic PNP, windows, dates and extra questions. They are **11/205 source-question texts inspected**, not **11/205 verified solutions**. Some were previously solved in the source; those remain historical records, not newly earned credit.

## Runnable isolated semantics checks

The stdlib-only script [`scripts/check_sql_semantic_edge_cases.py`](../scripts/check_sql_semantic_edge_cases.py), also part of GitHub Actions, uses disposable SQLite in-memory tables to assert four key behaviors:

1. A `NOT IN` subquery containing a `NULL` returns no expected unmatched customers, while a correlated `NOT EXISTS` preserves them.
2. Latest order ties resolve deterministically by descending date **then descending order ID**.
3. Multiple orders on one day are **aggregated before** the month-to-date running sum, which restarts each month.
4. Comparing **active** quarterly spend uses a previous active row even when calendar quarters are skipped.

**Boundaries:** Those are standalone verified principles, not executions of each exact PNP official solution. The SQL Server translations and all remaining SQL source-specific outputs are not certified through this script.

## Additional failure patterns to test across the remaining PNP inventory

- `LEFT JOIN` filters in `WHERE` accidentally remove unmatched rows; moving qualified predicates into `ON` can preserve them.
- Joining order lines with multiple payments can multiply fact values; aggregate each one-to-many side at the **intended grain** first.
- `ROW_NUMBER`, `RANK` and `DENSE_RANK` answer different tie questions.
- `COUNT(*)` counts rows; `COUNT(column)` ignores NULL; `COUNT(DISTINCT ...)` de-duplicates non-NULL values.
- Date predicates should use half-open ranges when timestamps contain times, and avoid conflating missing months with zero values.
- Safe percentage calculations require denominator checks and explicit null/unknown policies.
- Use explicit final `ORDER BY`; an internal CTE or window ordering does not guarantee result display order.
- SQL dialect differences matter: SQLite, SQL Server and MySQL syntax are not interchangeable.

**Do not modify the user's `My solution` sections or official-answer visibility just because a reviewer can derive another query.** Full source-to-concept comparison, all 205 individual execution checks and accurate completion records remain independent outstanding tasks.

## Join-question source audit extension — 2026-11-09

The following **12 additional** original question files were opened and their **task requirements, illustrative source-file examples, sample output contracts and pending learner-answer state** reviewed. This brings the *distinct inspected statement IDs* in this document to **23/205** (11 earlier + 12 here); **none** of these 12 unsolved exercises was credited as answered. Advanced-volume question texts do not supply source sample rows; their archived Markdown examples are explicitly *illustrative*, not official expected outputs.

| ID | Source contract / subtle case verified from preserved question text | Status of independent answer/output verification |
|---|---|---|
| A006 | MySQL FULL OUTER JOIN emulation; preserve unmatched customers **and** unmatched orders, including orphan and NULL keys, without doubling matched rows. | Task/sample read; additional SQLite fixture passed; original MySQL official answer not executed. |
| A008 | Complete date × category grid with missing combinations; date source and aggregate measures are **not defined** in source. | Task/sample read; cross-join concept mapped; source answer not executed. |
| A009 | Non-equi product-to-price-band join; quoted sample assumes half-open `[min,max)` intervals, **not source-mandated** price boundaries. | Task/sample read; boundary/overlap contract still needs actual source solution review. |
| A011 | Same-department colleague pairs only once, no reflexive or mirrored rows; NULL department policy worth testing. | Task/sample read; not independently answered. |
| A013 | Bought 101 **at least once** but 202 **never**, across all orders for a customer, not merely the same order. | Task/sample read; not independently answered. |
| P027 | AOV grouped by customer State (including Unknown for missing/unmatched); at least ten orders; AOV denominator counts only **orders with a non-NULL total** whereas displayed orders includes all. | Prompt/output contract read; full data/output validation pending. |
| P029 | Shipper order-value **one row per order** versus order-line quantity totals; unmatched or blank shipper rolled into Unknown. | Prompt/output contract read; isolated fan-out vs preaggregation SQLite fixture passed; full source answer pending. |
| P038 | Inactive-category products that sold in the **latest calendar year present in Orders**, not current system year; last order date and only that year's units. | Prompt/output contract read; no full query executed. |
| P039 | Four category states (empty, products but none sold, some unsold, all sold), full Category inventory, per-product sold flag and total units; action ordering. | Prompt/output contract read; isolated category-status SQLite fixture passed; full source answer pending. |
| P046 | Self-pairs with same non-NULL Brand and Sub_Category, cheaper-to-pricier once, price ratio >=2, handle zero denominator/ties explicitly. | Prompt/output contract read; source SQL Server/MySQL variants not verified. |
| P053 | First-ever order **within 0–30 calendar days inclusive from signup**; never-ordered customers remain in denominator; do not count later orders after an early out-of-range first order. | Prompt/output contract read; full query/data execution pending. |
| P070 | Different subcategories bought together counted **once per order** (even with multiple line items), unordered alphabetical pair, ten highest **including ties at tenth**. | Prompt/output contract read; isolated repeated-line/pair-count SQLite fixture passed; full top-ten-with-ties test still pending. |

**Executable scope:** The separate [PNP join regression fixture](../scripts/check_pnp_join_cases.py) passes four standalone SQLite tests for A006 (full join emulation), P029 (order-grain fan-out), P039 (four categories / duplicate line rows), and P070 (unordered pairs deduplicated per order). CI executes this file on pushes. These are **reviewer-generated, source-aligned synthetic fixtures**, not the original exercises' independently submitted answers and not complete validation of official PDFs or datasets.

**Coverage remaining:** **182 source question statements** not inspected in these two targeted reviews; all **205** original answers/outputs still require source-specific signoff at the required level, including previously solved records. W3Schools, Bosscoder and other DE-domain audits remain open. Do not change the learner tracker or official-answer visibility from this review.


## Previously saved JOIN answers and remaining source question — 2026-11-09 follow-up

Opened the **11 additional archived PNP JOIN markdown source files** below, comparing each problem statement, schema, sample, recorded learner SQL (when present), and supplied official SQL (when visible). This closes the **25/25 JOIN *statement inspection*** subset, not their full dataset/official-answer signoff. Ten already-solved source records remain historically solved; P077 remains explicitly unsolved.

| ID | Inspected contract and source-to-learner difference | Review evidence / remaining limitation |
|---|---|---|
| A001 | Preserve empty departments: count non-NULL employee IDs after LEFT JOIN, not COUNT(*). Source projects department name; saved query additionally gives ID. | Archived learner and MySQL official SQL read; small independent fixture covers zero employees and an orphan employee. |
| A010 | Self-join employees to **their actual manager**; strictly greater salary, not equal, no missing manager. Official output includes both salaries and manager; saved output gives employee ID/name. | Both SQL blocks read; independent fixture includes ties, unknown manager and NULL salary. |
| A012 | Count **direct** reports only; require an existing manager row, and apply HAVING >= 3. Official projects manager name as well. | Both SQL blocks read; independent fixture includes two valid managers and a missing manager referenced by three employees. |
| A014 | Employees with no reports; saved NOT IN filters NULL manager IDs explicitly, unlike unsafe bare NOT IN; official uses NOT EXISTS. | Both SQL blocks read; independent fixture includes NULL and nonexistent manager references. |
| P015 | All categories, including empty, must remain; count product ID, then sort count ascending / ID ascending. | Saved and official SQL read; synthetic fixture includes empty and unmatched product reference. |
| P016 | December 2025 only, known customer, clean name/city, chronological order; saved strftime filter is logically aligned on SQLite-supported ISO timestamps but differs from official sargable half-open date range. | Saved and official SQL read; fixture covers month boundaries, time component, unknown customer and NULL last name. |
| P017 | Inclusive seven **calendar dates** based on dataset maximum (not current clock), retaining missing payment/shipper names as Unknown; newest order/date tie. | Both SQL blocks read; fixture includes sixth-day boundary, earlier exclusion, NULL and invalid references. |
| P018 | 90 calendar dates inclusive through latest order date, even for customers without *any* orders; join filter belongs in ON, not WHERE. Saved SQLite name concatenation yields NULL if either name part is NULL, whereas official CONCAT_WS skips NULL: document this output discrepancy without rewriting learner answer. | Both SQL blocks read; fixture tests 89-day boundary and never-ordered customer; incomplete-name behavior not declared verified. |
| P019 | Group at ProductID grain, sum quantities, count order lines, count distinct orders. Saved LEFT JOIN retains nonexistent ProductIDs from order details; source official INNER JOIN excludes four known orphan ProductIDs. | Both SQL blocks read; independent fixture tests duplicate order lines and unknown ProductID; official-vs-learner discrepancy remains unresolved policy. |
| P026 | All category records including unsold ones, while preserving unmatched line/product references as Unmapped or Unknown product, distinct order counts, NULL unknown list price. Saved FULL OUTER JOIN handles no-sale categories, whereas published official LEFT JOIN starts at lines and omits no-sale categories; SQLite 3.39+ required. | Both SQL blocks and illustrative expectations read; independent fixture covers five line rows, empty category and unmatched references. |
| P077 | Across all order lines, exactly one **nonblank SupplierID** for each qualifying ProductID; product value divided by *all products'* list-price value, not just qualifying products. A missing supplier-directory row gets Unknown supplier/country, not automatically disqualified. | Original question/sample read; archived learner answer and official answer are intentionally hidden/pending. No solution was generated, tested or credited. |

New source-linked CI script [check_pnp_archived_join_answers.py](../scripts/check_pnp_archived_join_answers.py) **executes the literal saved SQLite answer block** from each of the 10 already-solved archived files on reviewer-created, isolated SQLite fixture data, and asserts exact output rows (except unordered queries compared as sets). These are **synthetic regression checks** and are *not* whole-dataset evaluation, a new independent learner solve, or official-answer verification; variants and other SQL dialects still need checking. The script refuses to fabricate missing answers. The 11 newly reviewed IDs bring the distinct targeted source-question statements to **34/205**; **171 source statements remain without targeted inspection**. JOIN group statement reading is **25/25**, while exact source-dataset outputs, ambiguity decisions and official solutions require further signoff.
