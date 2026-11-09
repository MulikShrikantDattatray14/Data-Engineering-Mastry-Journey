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
