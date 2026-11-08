# Q6 — Full progressive walkthrough: customers with no paid orders

**Day 1 · Slot 1 · 2026-11-06 (Asia/Kolkata)**  
**Student original attempt and error review:** [Slot archive](../../../10-learning-journal/sessions/2026-11-06/slot-01-sql.md)  
**Revision rule:** [SQL-R005 — anti-join](../../revision/LEARNED-RULES-AND-SYNTAX.md)

**Solution status:** Assistant-verified reference answer, **not** an official PNP/Bosscoder answer key. SQLite intermediate results were executed using the sample tables. SQL Server equivalent is syntax-validated conceptually but **not executed** in a SQL Server engine. Student's first submission remains unchanged in the slot archive.

## Problem and business intent

Return the customer ID and name of every customer with **zero paid orders**. Customers with only non-paid orders and customers with no orders are both valid. Sort by customer ID ascending.

## Reproducible SQLite fixture

```sql
CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, customer_name TEXT);
CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, status TEXT);
INSERT INTO customers VALUES (1,'Asha'),(2,'Ravi'),(3,'Neha'),(4,'Kabir');
INSERT INTO orders VALUES (201,1,'paid'),(202,1,'pending'),(203,2,'cancelled'),(204,3,'paid');
```

## Why the student's first approach wasn't equivalent

The original used an INNER JOIN with `status != 'paid'`. That tests whether each customer **has a non-paid order**, which is different from whether each customer **has no paid orders**. Asha has a paid order and a pending order, so the original mistakenly included her. Kabir has zero order rows, so INNER JOIN dropped him. The original SQLite result was `(1,Asha),(2,Ravi)`; the required result is `(2,Ravi),(4,Kabir)`.

## Step 1 — Establish the full left-side population

```sql
SELECT c.customer_id, c.customer_name
FROM customers AS c
ORDER BY c.customer_id;
```

| customer_id | customer_name |
|---:|---|
| 1 | Asha |
| 2 | Ravi |
| 3 | Neha |
| 4 | Kabir |

**4 rows.** Start from all customers so no-order customers aren't accidentally removed before evaluating them.

## Step 2 — Match all orders using LEFT JOIN

```sql
SELECT c.customer_id, c.customer_name, o.order_id, o.status
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
ORDER BY c.customer_id, o.order_id;
```

| customer_id | customer_name | order_id | status |
|---:|---|---:|---|
| 1 | Asha | 201 | paid |
| 1 | Asha | 202 | pending |
| 2 | Ravi | 203 | cancelled |
| 3 | Neha | 204 | paid |
| 4 | Kabir | NULL | NULL |

**5 rows.** Asha appears twice because two orders match; Kabir is retained with NULL order columns because LEFT JOIN preserves unmatched left rows. This is why a join can increase row count.

## Step 3 — Match **only paid** orders, but retain every customer

```sql
SELECT c.customer_id, c.customer_name, o.order_id, o.status
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
   AND o.status = 'paid'
ORDER BY c.customer_id, o.order_id;
```

| customer_id | customer_name | order_id | status |
|---:|---|---:|---|
| 1 | Asha | 201 | paid |
| 2 | Ravi | NULL | NULL |
| 3 | Neha | 204 | paid |
| 4 | Kabir | NULL | NULL |

**4 rows.** An `ON` predicate controls which right-side rows count as a match. Ravi's cancelled order is ignored for matching, so Ravi is now an unmatched left row; Kabir remains unmatched as before. Both get NULLs. Asha and Neha have paid matches.

## Step 4 — Select customers with no paid match

```sql
SELECT c.customer_id, c.customer_name
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
   AND o.status = 'paid'
WHERE o.order_id IS NULL
ORDER BY c.customer_id ASC;
```

| customer_id | customer_name |
|---:|---|
| 2 | Ravi |
| 4 | Kabir |

**2 rows.** `WHERE o.order_id IS NULL` removes every customer with a paid match (Asha, Neha), leaving only customers without one. Because `order_id` is a non-NULL primary key, it is safe to use as an indicator of an unmatched right row.

### Query decision rationale

- **LEFT JOIN**, not INNER JOIN: keep customers with zero orders.
- **`o.status = 'paid'` in ON**, not `WHERE`: make only qualifying paid rows count as matches; retain unmatched customers.
- **`o.order_id IS NULL` in WHERE**: detect missing qualifying matches, not individual non-paid rows.
- **`ORDER BY c.customer_id`**: meet output-order requirements.
- **Only two selected columns**: follow requested output shape; include additional right-table columns temporarily when teaching to inspect the intermediate state.

### Reusable SQL rule (SQLite and SQL Server)

For an entity set A and matching records B, to find entities **without any B row satisfying condition X**, use:

```sql
SELECT a.entity_id
FROM entities AS a
LEFT JOIN records AS b
  ON a.entity_id = b.entity_id
 AND /* qualifying condition X on b */
WHERE b.non_nullable_key IS NULL;
```

This is the **anti-join** pattern. Assumes `b.non_nullable_key` cannot be NULL for a real match. An equivalent alternative in many cases is `NOT EXISTS`, to be studied separately.

### SQL Server (T-SQL) reference, not SQL Server-executed

```sql
SELECT c.customer_id, c.customer_name
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
   AND o.status = 'paid'
WHERE o.order_id IS NULL
ORDER BY c.customer_id ASC;
```

### How this will be taught in future reviewed questions

For each **attempted and reviewed** problem, record: problem requirements → why this technique → dataset fixture → intermediate query → **actual output at each step** → business interpretation → final SQLite reference → SQL Server reference → original student's query/output differences → generalized rules and edge cases → optional new learning. Do not publish solutions or outputs to future unattempted practice prompts.
