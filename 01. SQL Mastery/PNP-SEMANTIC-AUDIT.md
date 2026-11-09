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

 
## Sorting and Grouping statement audit — 2026-11-09

The **13 original PNP Sorting and Grouping Markdown source questions** were individually opened and their task, source output contract, illustrative sample rows, schema, and unanswered status inspected. Total **47/205 distinct PNP task statements inspected** (25 JOIN, 13 Sorting/Grouping, 9 other topic questions). This is *not* verification of 47 official/learner answers. All 13 records still have pending original learner/official answer blocks, which were not filled or treated as mastery.

| ID | Source task and verified risk | Remaining boundary |
|---|---|---|
| A016 | Departments with AVG(salary) **strictly > 50,000** and headcount **>= 5**; NULL salary affects AVG differently than employee count. | Text/illustrative case inspected; headcount/NULL policy and official SQL unchecked. |
| A017 | Descending revenue by product category; sample calculates each order-line qty × order-line unit price, *not current catalog price*. | Text and sample checked; unmatched category policy and official SQL pending. |
| A018 | Monthly **distinct** buyers, excluding canceled orders first; repeated customer purchases counted once. | Text inspected; synthetic SQLite duplicate/canceled/NULL-buyer regression passed. |
| A021 | Weekday with **most orders** (not most revenue); actual weekday mapping depends on date/dialect. | Monday/Tuesday sample checked; source tie and timezone policy unspecified. |
| A025 | Customers with orders in *both* 2025 and 2026, not two orders within one year. | Text/sample inspected; no official execution. |
| A039 | Products with **more than 10 different customers**, regardless of repeat order/line count. | Text inspected; synthetic SQLite 11 distinct vs 10-plus-repeat buyer regression passed. |
| P009 | Count each distinct **raw stored** Category.Active and Payments.Allowed value, including NULL; preserve source_table and flag_column labels. | Text/sample inspected; synthetic SQLite NULL/count regression passed; mixed-storage-type rendering ambiguity remains. |
| P013 | States with **>=5** customers, missing states displayed as Unknown; order by descending count, state. | Source example checked; blank/whitespace handling not defined. |
| P014 | Orders and stored order value per **observed** 2025 month; missing February absent in illustrative expected output. | Synthetic SQLite half-open ISO timestamp and missing-month regression passed. |
| P021 | Five highest customer *positions*, **including all ties at fifth**; missing customer directory name is Unknown customer. | Six-way source tie sample checked; adversarial fixture confirms RANK fifth cutoff and demonstrates DENSE_RANK would include too many. |
| P022 | Orders with **more than eight OrderDetails rows**, separately COUNT(DISTINCT ProductID) and SUM(Quantity). | Nine rows / eight products in source sample; synthetic fixture passed quantity and line-count separation. |
| P025 | Group signups by year and calendar quarter; NULL date produces **one NULL/NULL group, sorted last**. | Source April and NULL examples checked; synthetic SQLite quarter boundary and NULL ordering passed. |
| P050 | Ten or more **distinct numeric CategoryID values** bought across all lines; comma-separated IDs *numerically ordered*, separately count distinct orders. | Source 10-category example checked; synthetic SQLite duplicate-line, category-10 sorting and multiple-order regression passed. |

[Eight reviewer-authored SQLite grouping regressions](../scripts/check_pnp_grouping_cases.py) are run locally and in CI. They assert underlying grouping pitfalls using **synthetic data**, not the archived official PDF answers, unattempted learner SQL, or the actual whole source dataset. No exercise completion credit follows.

Cross-source check: current W3Schools [GROUP BY](https://www.w3schools.com/sql/sql_groupby.asp) and [HAVING](https://www.w3schools.com/sql/sql_having.asp) lesson pages were independently reviewed. Their introductory aggregation/group-filter concepts are already covered by this repository's canonical foundation, so they were linked rather than copied. The source-specific tie, nullable flag and quarter/sorted-list caveats were added only to that one foundation.

**Still pending:** **158** uninspected PNP source statements; full official/dataset/learner-answer verification of **all 205** questions; detailed Python/Bosscoder/W3Schools and Data Engineering topic audits, complete runnable examples and public-course licensing signoff. Original sources and learner progress unchanged.


## Aggregation source-question statement audit — 2026-11-09

**Evidence boundary:** Opened the **20 individual original-archive PNP Aggregation Markdown problem records** linked from the [205-question index](PNP-PROBLEM-INDEX.md). Read their task contracts, schemas, illustrative input/output and unsolved/official-answer markers. These preserved records cite two original PDFs, but this pass **did not independently execute the PDF's official answers or compare against a complete original dataset**. All 20 archived learner/official blocks remain **Pending**; no problem was solved or credited.

| ID | Source-specific contract or failure mode actually inspected | Status and remaining verification |
|---|---|---|
| A019 | Category line revenue = SUM(qty × order-line unit_price), plus a **grand-total row last**; a NULL category and a category literally named Total can collide with a naive label. | Archived prompt and illustrative 20+30=50 arithmetic read. No independent original PDF/official ROLLUP check; policy for missing product/category still open. |
| A020 | Average **order.amount** per cust_id only when COUNT(order rows) **>=3**; do not average joined item rows. | Three-order sample average 20 reviewed. NULL amount and customer-without-orders decisions need source confirmation; official SQL pending. |
| A022 | Conditional pivot: per-customer counts by order status (illustration: completed, cancelled). Pivot output shape depends on fixed status columns; not one row per status. | Example (customer 10 has 1+1, customer 20 has 1+0) inspected. Unknown statuses and never-ordered customers unspecified. |
| A023 | Category revenue for **2025 and 2026 separately** using order-line qty × unit_price; include zero for category-year with no lines where group survives. | Audio 10/15 and Home 5/0 illustrative outputs read. Missing category/unknown year and original MySQL answer not checked. |
| A024 | Cancellation percentage = cancelled order count / **all order rows per customer** × 100; use a non-integer numerator. | 1 of 2 = 50%, 0 of 1 = 0% sample inspected. Case/NULL status and no-order customers need contract decision. |
| A026 | Unpivot exactly three metrics (delivered, cancelled, placed) from **cust_summary**, retaining one row per metric and cust_id. That table **does not exist in the supplied seven-table shared schema**. | Structural source gap confirmed; only illustrative schema/rows exist. Cannot certify full dataset output or official solution without original extra relation. |
| A027 | First and last **order dates per customer** and difference in days; single order lifespan = 0, not 1. | Jan 1–Jan 11 => 10 days and same-day => 0 sample reviewed. Timestamp/null-date semantics and official MySQL answer pending. |
| P010 | Single whole-table row: COUNT orders, DISTINCT ordering CustomerID, SUM order amount, AVG order amount 2dp, MIN/MAX order dates. Source says cancellations/refunds not represented. | Three-row sample 3 orders, 2 customers, 600 total, 200 AOV inspected. Empty table/NULL amount formatting not verified against official. |
| P011 | Products LEFT JOIN OrderDetails: report **rows_after_join**, matched **sale_lines**, distinct **listed_products**, distinct **products_sold**, percentage sold. Unsold products each create a NULL-extended joined row. | Three products, three matched lines => four joined rows, two sold; standalone reviewer SQLite fixture **passed** including an orphan line. No full dataset official answer signoff. |
| P012 | Per CategoryID count products, min/max/average Sale_Price, count exact Sale_Price=Market_Price, AVG each product's valid discount percentage; no usable Market_Price excluded from discount AVG. | 80/100 and 100/100 => 10% simple average checked from sample; zero/NULL market price and integer division remain to test. |
| P035 | Per shipper late >7 **calendar days** from order to delivery, valid delivered denominator, undelivered and invalid-date counts separately, unmatched/NULL shippers under Unknown. | FastShip 1 late of 2 valid => 50%, 1 undelivered, 1 invalid inspected. Boundary at day 7, invalid/missing overlap, official SQL unchecked. |
| P036 | Monthly **wide-form** six named payment-method counts, with all other types (including EMI/Pay Later) and absent payment rows in other_or_unknown; total_orders independent of match. | Jan 3 orders, Feb 2 sample inspected. Invalid PaymentID, NULL date and possible duplicate Payments need authoritative handling. |
| P047 | Brand must have **>=3 listed catalogue products**, whether sold or not; count distinct sold products, sum units and Quantity × current Sale_Price; missing Brand grouped Unbranded. | Nova three listed, two sold illustrative sample read; independent reviewer fixture **passed** for sales-line fan-out, unsold catalogue and NULL brand. Literal brand 'Unbranded' collision and source dataset checks open. |
| P048 | Discount band full price, (0,10], (10,25], >25, Unknown market zero/NULL; **unsold products retained** and affect per-product mean. | Five-product sample including zero-sale >25% and invalid market reviewed. Negative discount if Sale_Price > Market_Price is unspecified, not silently decided. |
| P051 | For each order **with lines**, distinct non-NULL SupplierID determines zero/one/two/three-plus-known-supplier bucket; percentages use total distinct orders with lines. | Four equally sized buckets in sample; **reviewer SQLite fixture passed**, including an order with known and NULL supplier. Unresolved data-quality policy for mixed NULL/known supplier IDs. |
| P052 | Shipper averages from **valid order <= ship <= delivery**, split dispatch and transit; excluded-order count must remain visible, unknown shippers retained. | FastShip sample 2+2=4 days and one excluded; reviewer read output contract. Original answer and timezone/invalid-null cases pending. |
| P054 | For valid Market_Price>0 and Sale_Price<=Market_Price, compute **simple average across products**, **unit-weighted average across sold units** and total units. Unsold valid products influence simple but not weighted average. | Source 10% and 50%, weights 1 and 3 => 30% vs 40%. Independent reviewer SQLite fixture **passed** with an extra unsold product and invalid-price row; original dataset/official SQL pending. |
| P055 | Latest year = YEAR(MAX(Orders.OrderDate)) **from the dataset**, not today's calendar year; compare it with previous year by category and allow Unmapped category. YoY NULL if previous value zero. | 2024 Drinks 20, 2025 Drinks 30 => 50%, Snacks prior 0 => NULL example reviewed. Source has no full dataset execution evidence. |
| P059 | Roll up **per order first**: sum Quantity and count distinct ProductID, then AVG each measure by OrderDate month. Ignore orders with zero lines in all basket averages and report measured order count. | Jan two orders => avg 3 units and 1.5 products; Feb empty order excluded. Reviewer synthetic fixture **passed** with duplicate product lines; official answer unchecked. |
| P084 | Valid delivered dates only; group by state×shipper, state subtotal and grand total, each with order count. Hide average for **<5 valid orders per output group** while retaining count, and distinguish missing state from subtotal labels. | CA five 2-day Swift and one 4-day Slow => subtotal 14/6=2.33, Slow cell NULL. Independent synthetic fixture **passed** for count thresholds and weighted grand totals; source PDF official SQL pending. |

**Executable evidence:** [Six independent SQLite aggregation fixtures](../scripts/check_pnp_aggregation_cases.py) directly test the documented pitfalls for P011, P047, P051, P054, P059 and P084 on reviewer-created data. Those tests passed locally and are included in CI; they do **not** execute the original official SQL, certify the full source dataset, or substitute for independent learner submissions.

**Coverage after this pass:** **67/205 distinct PNP source statements inspected** = the previous 47 plus these 20, with **138 uninspected**. All **20/20 Aggregation statements** have text-level review; **205/205 individual full answer/dataset signoffs are *not* yet certified**. Python/Bosscoder/W3Schools, other DE domains and licensing signoff remain open. Preserve archives and user progress unchanged.
