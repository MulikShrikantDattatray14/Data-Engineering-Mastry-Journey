# SQL Logical Query Processing Order

This is the logical order in which SQL clauses are evaluated. The database optimizer may use a different physical execution plan while preserving the same result.

## Core logical order

| Step | Clause | Purpose |
|---:|---|---|
| 1 | `FROM` / `JOIN` / `ON` | Identifies source tables and combines matching rows. |
| 2 | `WHERE` | Filters individual rows before grouping. |
| 3 | `GROUP BY` | Combines the remaining rows into groups. |
| 4 | `HAVING` | Filters groups after aggregation. |
| 5 | `SELECT` | Calculates and names the output columns and expressions. |
| 6 | `DISTINCT` | Removes duplicate output rows. |
| 7 | `ORDER BY` | Sorts the result. Select-list aliases are normally available here. |
| 8 | Row limiting | Returns only the requested portion of the ordered result. The syntax depends on the SQL dialect. |

A useful memory pattern is:

```text
FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```

## SQLite

SQLite limits the final result with `LIMIT` and optionally skips rows with `OFFSET`.

```sql
SELECT column_name
FROM table_name
WHERE condition
GROUP BY column_name
HAVING aggregate_condition
ORDER BY column_name
LIMIT 10 OFFSET 20;
```

Relevant order:

```text
FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT/OFFSET
```

## SQL Server

SQL Server can restrict rows with `TOP` or paginate an ordered result with `OFFSET ... FETCH`.

### `TOP`

```sql
SELECT TOP 10 column_name
FROM table_name
ORDER BY column_name;
```

Although `TOP` is written next to `SELECT`, it limits the result after the query has formed and ordered the qualifying rows. Use `ORDER BY` when the required top rows must be deterministic.

### `OFFSET / FETCH`

```sql
SELECT column_name
FROM table_name
ORDER BY column_name
OFFSET 20 ROWS
FETCH NEXT 10 ROWS ONLY;
```

`OFFSET / FETCH` requires `ORDER BY` in SQL Server.

Relevant order:

```text
FROM → ON/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → TOP or OFFSET/FETCH
```

## Important consequences

### `WHERE` versus `HAVING`

`WHERE` filters rows before grouping:

```sql
WHERE activity_date >= '2019-06-28'
```

`HAVING` filters groups using aggregate results:

```sql
HAVING COUNT(student) >= 5
```

Using `GROUP BY` does not automatically require `HAVING`.

### Column aliases

A select-list alias is created during the `SELECT` phase. It can normally be used in `ORDER BY`, which is processed later:

```sql
SELECT SUM(Total) AS Revenue
FROM Invoice
ORDER BY Revenue DESC;
```

Aliases are generally unavailable in `WHERE`, which is processed before `SELECT`. Alias support in `GROUP BY` and `HAVING` varies by database, so repeating the underlying expression is more portable.

### Aggregates

`WHERE` cannot directly filter an aggregate such as `COUNT(*)` because grouping has not happened yet. Use `HAVING`:

```sql
SELECT class
FROM Courses
GROUP BY class
HAVING COUNT(*) >= 5;
```

### Window functions

Window functions are evaluated after row filtering and grouping, as part of producing the selected result. They calculate across rows without collapsing those rows into one result per group.

```sql
SUM(Revenue) OVER (ORDER BY Month)
```

A window-function result normally cannot be referenced directly in `WHERE` because `WHERE` is evaluated earlier. Use a CTE or subquery when that result must be filtered.

## SQLite and SQL Server row-limiting comparison

| Requirement | SQLite | SQL Server |
|---|---|---|
| First 10 rows | `LIMIT 10` | `TOP 10` |
| Skip 20, return 10 | `LIMIT 10 OFFSET 20` | `OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY` |
| Deterministic top rows | Use `ORDER BY` | Use `ORDER BY` |

## References supplied with the learning note

- [SQL Order of Execution Explained](https://datawithsarah.com/post/sql-order-of-execution-explained/)
- [SQL Server Logical Query Processing](https://www.sqlservercentral.com/blogs/sql-server-logical-query-processing)
- [SQL Execution Order Explained](https://www.stratascratch.com/blog/sql-execution-order-explained)
