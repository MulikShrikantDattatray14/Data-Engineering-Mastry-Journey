# SQL Lesson 01 — SELECT, WHERE and ORDER BY

**Status:** Theory introduced; learner practice pending review.
**Dialect:** PostgreSQL-style SQL.

## Why learn this?
Filtering and selecting records are foundational skills for extracting, checking and transforming data in pipelines.

## Example data
Table: `orders`

| order_id | customer | region | amount |
|---:|---|---|---:|
| 101 | Amit | West | 1200 |
| 102 | Priya | South | 800 |
| 103 | Rahul | West | 2000 |
| 104 | Neha | North | 500 |
| 105 | Amit | West | 700 |

## Core clauses
- `FROM` identifies the input table.
- `WHERE` keeps rows that satisfy a condition.
- `SELECT` chooses the output columns and expressions.
- `ORDER BY` sorts rows; `DESC` means highest to lowest.

## Worked example
```sql
SELECT customer, region, amount
FROM orders
WHERE amount > 1000
ORDER BY amount DESC;
```

Expected result: Rahul/West/2000 followed by Amit/West/1200.

## Logical processing order
We write `SELECT → FROM → WHERE → ORDER BY`, but a simplified logical order is `FROM → WHERE → SELECT → ORDER BY`. The database optimizer may choose a different physical plan.

## Frequent mistakes
- Use `=` for SQL equality, not JavaScript's `===`.
- Single-quote string literals such as `'West'`.
- `> 1000` excludes exactly 1000; `>= 1000` includes it.
- Without `ORDER BY`, SQL does not guarantee row ordering.
- `NULL` has special comparison behavior; covered later.

## Self-check
Ask: Which table? Which rows? Which columns? Which order?

## Practice status
The first challenge filters West-region orders over 1000 and sorts descending. Original attempt, review and corrected solution will be linked after completion.

## Data Engineering connection
This pattern underlies source-data filtering, ingestion checks and cleaning steps.