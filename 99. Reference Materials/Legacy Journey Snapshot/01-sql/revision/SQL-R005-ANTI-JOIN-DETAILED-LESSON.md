# SQL-R005 — Anti-Join Pattern: Detailed Beginner-to-Practical Lesson

**Date learned:** November 6, 2026 · Day 1 / Slot 1 / Q6  
**Status:** Learner explicitly identified anti-joins as **important new learning** after Q6.  
**Related work:** [Q6 original attempt, review, and follow-up](../../10-learning-journal/sessions/2026-11-06/slot-01-sql.md) · [Progressive Q6 walkthrough](../practice/verified-results/2026-11-06-q06-walkthrough.md)  
**Dialects:** Original practice in **SQLite**; companion reference syntax in **SQL Server (T-SQL)**.  
**Attribution:** This is an assistant-authored explanation of the reviewed tutor question, **not** an official PNP answer key, and **not** an independently written student solution.

## 1. Why do we need an anti-join?

An ordinary JOIN helps answer **“Which rows have a match?”**

An anti-join answers **“Which rows do *not* have a match meeting a particular condition?”**

Examples in Data Engineering:
- Customers **without a paid order**.
- Invoices **without a successful payment**.
- Source events **not yet present in a processed-events table**.
- Products **without any inventory movement**.

> **Core idea:** The question asks whether **zero qualifying matching rows exist**, not whether at least one *nonqualifying* row exists.

## 2. Our consistent Q6 sample

`customers`

| customer_id | customer_name |
|---:|---|
| 1 | Asha |
| 2 | Ravi |
| 3 | Neha |
| 4 | Kabir |

`orders`

| order_id | customer_id | status |
|---:|---:|---|
| 201 | 1 | paid |
| 202 | 1 | pending |
| 203 | 2 | cancelled |
| 204 | 3 | paid |

**Question:** Find customers with **no paid orders at all**. This includes people with only cancelled/pending orders **and** people with zero orders. Return `customer_id`, `customer_name`, ordered by ID.

## 3. Why the first Q6 attempt was wrong

**Learner's original SQLite submission — unchanged:**

```sql
SELECT c.customer_id , c.customer_name
FROM customers AS c
inner join orders as o on  ( c.customer_id = o.customer_id )and status!='paid'
order by c.customer_id asc
```

The condition `status != 'paid'` asks **“Does this customer have at least one non-paid order?”** It does *not* ask **“Does this customer have zero paid orders?”**

- **Asha** has paid **and** pending orders. The pending row satisfies `status != 'paid'`, so the original query incorrectly returns Asha.
- **Ravi** has only a cancelled order. He is correctly included.
- **Neha** has a paid order. She is excluded.
- **Kabir** has **no orders**, so INNER JOIN drops him entirely, even though he must qualify.

**Original SQLite result:** (1, Asha), (2, Ravi).  
**Expected result:** (2, Ravi), (4, Kabir).

## 4. Build the answer progressively

### Stage A — Begin with every customer

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

**4 rows.** Starting with all customers ensures that Kabir is not lost before the test.

### Stage B — LEFT JOIN all matching order rows

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

**5 rows.** LEFT JOIN preserves all customers, but a customer with *multiple matching orders* produces *multiple rows*. For Kabir, who matches nothing, SQL produces one row whose right-table columns are NULL.

### Stage C — Only PAID orders should count as matches

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

**4 rows.** The `ON` condition now means two checks are required for a match: customer IDs must match **AND** the order must be paid.

- Asha's 201 qualifies; 202 doesn't.
- Ravi's 203 has the correct customer ID but **wrong status**, so none of his orders qualify. Ravi still appears due to LEFT JOIN, but the right-table columns are NULL.
- Neha's 204 qualifies.
- Kabir has no order; he appears with NULLs as well.

**Critical distinction:** A NULL right-side match can mean **no orders exist** or **orders exist but none satisfy the full ON condition**.

### Stage D — Keep only customers with no paid match

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

**2 rows.** Because only paid orders were eligible to match, a NULL `o.order_id` means **no paid match exists**. We test a right-side column that cannot be NULL for a genuine matching order, such as the primary key.

## 5. The reusable general rule

To find left-table entities with **no right-table row satisfying condition X**:

1. Start from the left table containing all entities to consider.
2. `LEFT JOIN` the right table, placing **X inside ON** along with the key equality.
3. Use `WHERE right_table.non_nullable_key IS NULL` to keep entities with **zero qualifying matches**.

General shape (illustrative pseudocode, not directly executable):

```sql
SELECT a.entity_id
FROM entities AS a
LEFT JOIN records AS b
  ON a.entity_id = b.entity_id
 AND <qualifying condition X>
WHERE b.non_nullable_key IS NULL;
```

**Important:** A right-table column that can legitimately be NULL in matching rows would make the check unreliable. Choose a non-nullable key.

## 6. Related JOIN concepts and pitfalls

### Does LEFT JOIN always yield one row per customer?

No. It yields **one row per matching right-table record**, or **one NULL-extended row** when there are zero qualifying right-table matches.

### What if Ravi later gets order 205 (paid)?

Under `ON ... AND o.status = 'paid'`, Ravi's result becomes `(Ravi, 205, paid)` rather than NULL.

### What if Ravi has two paid orders, 205 and 206, and one cancelled order 203?

Ravi produces **two rows** in the Stage C join, one for order 205 and one for 206. The cancelled order does not match. There is **no extra NULL row**, because at least one match exists.

The learner independently answered this multiple-paid-order check correctly.

### Why not put `o.status = 'paid'` in WHERE?

```sql
LEFT JOIN orders AS o ON c.customer_id = o.customer_id
WHERE o.status = 'paid'
```

A `WHERE` predicate filters **after the JOIN**. For Ravi's cancelled row the condition is FALSE; for Kabir's NULL row it is UNKNOWN; both disappear. This would *find people who have paid orders*, not the people who do not.

### Why `WHERE o.order_id IS NULL` is different

It deliberately retains the unmatched right-side rows, because `IS NULL` is TRUE for NULL keys. Don't generalize that every WHERE clause always removes unmatched rows.

### What if the status itself is NULL?

Ordinary comparisons such as `NULL = 'paid'` and `NULL != 'paid'` evaluate to UNKNOWN, so the row doesn't qualify as a paid match. An account with only such orders still qualifies as having no paid order.

### Duplicate or mixed-status orders?

A customer can have one paid row and many non-paid rows. The mere presence of non-paid rows does **not** prove that no paid row exists. Think across **all orders for the customer**, not individual rows.

## 7. SQL Server (T-SQL) version

The reviewed SQLite solution above is also valid SQL Server T-SQL:

```sql
SELECT c.customer_id, c.customer_name
FROM customers AS c
LEFT JOIN orders AS o
  ON c.customer_id = o.customer_id
 AND o.status = 'paid'
WHERE o.order_id IS NULL
ORDER BY c.customer_id ASC;
```

**Execution statement:** The Q6 query and its intermediate steps were checked with SQLite. The SQL Server version is an assistant-authored equivalent; no separate SQL Server execution is claimed.

## 8. Quick revision: two different questions

| Business question | Logical meaning |
|---|---|
| Customers who **have at least one cancelled order** | One cancelled order exists, even if they also have a paid order |
| Customers who **have no paid orders** | **Zero paid rows** exist across all their orders |

The same customer can satisfy **both** statements. They are not opposites.

## 9. Data Engineering application

Suppose an ingestion pipeline tracks incoming `source_events` and a `processed_events` table. To find source events that have **not been processed successfully**, match only successful processing records in `ON`, then keep unmatched events using a non-nullable processing-record key in `WHERE ... IS NULL`.

When processing records may be duplicated or huge, also learn to evaluate `NOT EXISTS`, appropriate indexes, and execution plans later; this lesson focuses first on correctness.

## 10. Retrieval and practice plan

- **Q7:** New payments/account dataset to apply the same anti-match reasoning plus NULL and filters — **solution deliberately withheld until the learner submits**.
- **Later:** Mix anti-join with `AND`/`OR` grouping, NULL, repeated matches, no rows, and ON/WHERE placement.
- **Before every submission:** Recheck requirement, aliases, syntax, and actual output.

### One-line memory hook

**“For NONE of X: LEFT JOIN only X in ON, then look for a missing right-side key in WHERE.”**

This is a learning/revision note, **not** a claim that the whole topic is mastered.
