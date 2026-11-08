# Day 1 — Slot 01: SQL Foundations & PNP Practice

**Study date:** November 6, 2026 (Asia/Kolkata)  
**Status:** Q1–Q8 tutor diagnostics reviewed; 4 independently correct/corrected (Q1, Q2, Q7, Q8). PNP source reattempts still pending  
**Actual start/end and verified focus minutes:** Not recorded  
**Goal:** Rebuild accurate foundations, use independent queries to demonstrate fluency, then revisit the existing PNP SQL 205-question bank without duplicating solutions.

## Lesson 1A — How a SELECT query thinks

### Why it matters to Data Engineering
A Data Engineer uses SQL not merely to display rows, but to select clean records for data transformations, validate incoming batches and build reliable aggregations. A simple filtering mistake can silently include cancelled, null or out-of-range records in a production metric.

### Core concepts to demonstrate
- `SELECT`: choose output columns; `FROM`: choose a table or relation.
- `WHERE`: keep rows satisfying a condition. Understand `=`, `<>`, `>`, `>=`, `<`, `<=`.
- Boolean logic: `AND` requires both conditions, `OR` either condition; use parentheses to make mixed conditions explicit.
- SQL `NULL` represents an absent/unknown value, not a normal value you can compare with `=`. `IS NULL` and `IS NOT NULL` are the appropriate checks.
- SQL filtering uses three-valued logic: TRUE, FALSE, UNKNOWN. A `WHERE` clause retains only TRUE.
- `ORDER BY` controls sort order; `LIMIT` (PostgreSQL) limits returned rows. A relational result is not guaranteed to have a particular order without explicit ordering.
- We will revisit joins, aggregation, duplicate amplification and multi-concept SQL after these foundations are validated.

### Dialect for this practice
Use **PostgreSQL** syntax in the interactive lesson, so examples and LIMIT/NULL behavior are unambiguous. We can compare SQL Server TOP and other dialects separately later.

## First independent diagnostic: Q1 — Paid Maharashtra orders

You are given an `orders` table:

| order_id | customer_id | status | amount | state |
|---:|---:|---|---:|---|
| 101 | 1 | paid | 1200 | Maharashtra |
| 102 | 2 | paid | 500 | Karnataka |
| 103 | 3 | cancelled | 2200 | Maharashtra |
| 104 | 1 | paid | NULL | Maharashtra |
| 105 | 4 | paid | 1800 | Maharashtra |
| 106 | 5 | pending | 2600 | Maharashtra |

**Your task:** Write one PostgreSQL query returning only `order_id` and `amount` for rows whose `status` is `'paid'`, `state` is `'Maharashtra'`, and `amount` is strictly greater than `1000`. Sort by `amount` descending. Do not hardcode order IDs or answers. Explain why a missing amount must not be included.

**Student's original first attempt (preserved exactly, no formatting edits):**

```sql
SELECT order_id , amount
FROM orders
WHERE status = 'paid' and  state = 'Maharashtra' and amount > 1000
order by amount desc
```

**Review:** 5/5 explicit query requirements satisfied. Valid PostgreSQL SQL. `WHERE` checks paid orders, Maharashtra, and amount strictly greater than 1000. `ORDER BY amount DESC` yields order 105 (1800), then order 101 (1200). For order 104, comparison `NULL > 1000` is UNKNOWN, and `WHERE` only retains TRUE. Extra `IS NOT NULL` is unnecessary. Keyword capitalization / line breaks are optional style choices only; student's original retained.

**Learner-confirmed new learning (submitted after Q1 review):** The learner identified the following explanation as their new takeaway, not as a separately authored pre-review answer. It is saved verbatim under the learning entry below.

**Completion credit:** One original tutor diagnostic question reviewed correct; this is **not** a new PNP source ID, not a full slot completion, and not a mastered SQL module.

## Remaining Slot 1 sequence (not yet studied)
1. Q1 complete; Q2/Q3 variants to check `AND`/`OR`, operator precedence, `IS NULL`, and sorting.
2. Short diagnostic on joins and multiplicative duplicates.
3. Reattempt 6–10 selected previously solved PNP SQL questions. Original source questions stay in [Repository 2](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry).
4. If rapid and accurate, begin pending PNP IDs `A016`, `P009`, `P013`, `P014`. No new IDs are credited before actual review.

## Progress and revision log
- Actual focused minutes: Unverified
- First attempted query: Q1 submitted and reviewed correct (5/5 requirements)
- SQL source IDs verified today: None
- Errors and important insights: No query errors found; distinguish unknown results of NULL comparisons from TRUE; learner-confirmed NULL/WHERE takeaway recorded separately after feedback
- Next revision: Pending

**Rule:** Log each original student submission before corrections. Lesson documentation does not equal reviewed mastery.

## Question 2 — AND/OR precedence and NULL diagnostics (awaiting learner)

Using the **same orders table** from Q1, write one PostgreSQL query that returns `order_id`, `status`, `state`, and `amount` for:

- **Either** all `'paid'` orders from `'Maharashtra'` **or** all orders with `amount > 2000`, regardless of state or status.
- Exclude any order with a `NULL` amount.
- Sort by `order_id` ascending.

**Requirement:** Use correct parentheses to make the intended logical grouping explicit. Do not hardcode IDs. In your own words, explain which operator would otherwise take precedence between `AND` and `OR`, and why order 104 must be excluded.

**Student's original first attempt (preserved verbatim, including spaces):**

```sql
SELECT order_id, status, state, amount
FROM orders
WHERE  (status ='paid' and state='Maharashtra') or  amount > 2000 
order by order_id
```

**Student's original reasoning (verbatim):**

> Excludes all orders where amount is NULL need not to be handled seperately as where handles that properly where is excludes this automatically .. this thing i learned from question-1

**Review:** 4 of 5 requirements satisfied. The query's `(status='paid' AND state='Maharashtra') OR amount > 2000` admits order 104: the first group is TRUE despite `amount > 2000` being UNKNOWN. The separate universal exclusion of NULL amounts is missing. `ORDER BY order_id` correctly sorts ascending by default. Expected qualifying IDs after fixing the predicate: 101, 103, 105, 106. This is a **reviewed unsuccessful first attempt**, with independent revision pending.

### SQL Server (T-SQL) — assistant translation of the ORIGINAL attempt (same unresolved logic error)

```sql
SELECT order_id, status, state, amount
FROM orders
WHERE (status = 'paid' AND state = 'Maharashtra')
   OR amount > 2000
ORDER BY order_id;
```

**Important:** This is a dialect-equivalent translation of the learner's *original attempt* and **does not fix the NULL problem**. The corrected SQLite and T-SQL solutions will be saved only after the student independently revises the SQLite query. Do not attribute T-SQL to the student.

**Expected-result explanation:** The first Boolean branch can be TRUE even when amount is NULL; WHERE keeps rows whose entire predicate is TRUE, not all rows with a non-NULL amount.

**Optional post-question new-learning prompt:** Ask Yes/No after the revised query is reviewed; if Yes, capture the exact learner text and link to revision bank.

**Archive rule:** Record next answer exactly before providing corrections.

## Optional post-question learning capture — Q1 (learner-submitted)

**Asked-for workflow:** After every future practice submission and its review, ask **“Any new learning from this question?”** with a Yes/No choice. No is valid, optional, and requires no further response. If Yes, collect learner-authored text and save it both in the session archive and the relevant subject-level rule/syntax revision reference; avoid rewriting the learner's text. Any new insight must remain associated with its date, slot, question and source.

**Q1 — Learner's exact reported takeaway:**

> Your condition `amount > 1000` evaluates to `UNKNOWN` when `amount` is `NULL`. Since `WHERE` retains only rows whose condition is `TRUE`, order 104 is excluded automatically.
>
> You do not need an additional `amount IS NOT NULL` condition for this query.

**Classification:** General rule / SQL syntax / three-valued logic.  
**Cross-topic revision reference:** [SQL-R001 — NULL comparisons and WHERE](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).  
**Q1 review:** Correct query; explanation originally supplied in feedback, subsequently explicitly selected by learner as a new learning.

**Tracking:** Rule recorded, no change to PNP SQL question totals or mastery counts.


### Q1 learning — resubmitted exact wording

```text
Your condition amount > 1000 evaluates to UNKNOWN when amount is NULL. Since WHERE retains only rows whose condition is TRUE, order 104 is excluded automatically.

You do not need an additional amount IS NOT NULL condition for this query.
```

This entry reproduces the learner's subsequent submission exactly; the original formatted entry above is retained for history.

## SQL dialect correction — user preference

From this point onward the student solves every SQL problem **in SQLite**. Following an independent attempt and review, save the original SQLite solution *unchanged* and an assistant-created **SQL Server (T-SQL)** translation. The earlier references to PostgreSQL describe the initial plan and are **superseded**. Do not create PostgreSQL solution versions.

### Q1 SQLite: original student solution (verbatim)

```sql
SELECT order_id , amount
FROM orders
WHERE status = 'paid' and  state = 'Maharashtra' and amount > 1000
order by amount desc
```

### Q1 SQL Server (T-SQL): assistant-converted after student review

```sql
SELECT order_id, amount
FROM orders
WHERE status = 'paid'
  AND state = 'Maharashtra'
  AND amount > 1000
ORDER BY amount DESC;
```

This particular original query is syntactically valid in both dialects; the second version is a readability formatting of the same logic, **not a second learner-authored attempt**. Q2 first and revised SQLite attempts have been preserved, with its reviewed SQL Server translation below.

## Q2 — Learner's revised SQLite solution (verbatim)

```sql
SELECT order_id, status, state, amount
FROM orders
WHERE  (status ='paid' and state='Maharashtra' and amount is not null ) or  (amount > 2000 and amount is not null)
order by order_id
```

**Review:** 5/5 requirements. Both branches reject NULL amounts, logical grouping is explicit, and `ORDER BY order_id` sorts ascending. Correct rows: 101, 103, 105, 106. The `amount IS NOT NULL` check in the second OR branch is redundant given `amount > 2000`, but not incorrect. Original first attempt and its 4/5 review remain preserved above.

### SQL Server / T-SQL — assistant-converted after successful learner revision

```sql
SELECT order_id, status, state, amount
FROM orders
WHERE
    (status = 'paid'
     AND state = 'Maharashtra'
     AND amount IS NOT NULL)
    OR
    (amount > 2000
     AND amount IS NOT NULL)
ORDER BY order_id ASC;
```

**Learning-capture response:** `No new learning to record.` No new rule is added to the centralized SQL revision bank. The correction is retained in this session review.

**Source completion credit:** Q2 is an original tutor diagnostic, not an additional PNP SQL ID. Focus time and complete slot mastery have not been verified.

## Question 3 — LEFT JOIN and missing records (unattempted)

### Tables

`customers`:

| customer_id | customer_name |
|---:|---|
| 1 | Asha |
| 2 | Ravi |
| 3 | Neha |
| 4 | Kabir |

`orders`:

| order_id | customer_id | status |
|---:|---:|---|
| 201 | 1 | paid |
| 202 | 1 | pending |
| 203 | 2 | cancelled |
| 204 | 3 | paid |

**Task:** Write a SQLite query returning `customer_id`, `customer_name`, and `order_id` for **every customer, including customers with no orders**. For each customer, return their matching orders as separate rows, sorted by `customer_id` and then `order_id` ascending. Do not filter by order status.

**Student SQLite attempt:** Submitted and reviewed below; original SQL hit a syntax error at `sort`. Reference query and expected versus actual output documented below.

## Verified SQLite execution and reference-solution archive (Q1 and Q2)

Actual SQLite output, required expected output, comparison tables, and separately labeled SQLite + SQL Server reference solutions are documented in [the Q1–Q2 verification file](../../../01-sql/practice/verified-results/2026-11-06-q01-q02.md). Q1 matched immediately; Q2 initial query had an extra NULL-amount order 104, and Q2 corrected query matched. Original attempts above remain unchanged. Q3 was subsequently attempted and reviewed; see its detailed execution evidence and reference query below.


## Q2 — Learner-confirmed new learning (subsequent update)

After reviewing the Q2 explanation, the learner explicitly requested that its lesson be saved as important **new learning from Q2**, superseding the earlier optional response of "No new learning to record."

**Saved concept:** SQL evaluates the complete WHERE expression; AND takes precedence over OR; TRUE OR UNKNOWN evaluates TRUE; therefore an amount-NULL row may pass via another OR branch. To enforce NULL exclusion for all alternatives, group the OR clauses and append AND amount IS NOT NULL to the whole group. Avoid repeating mandatory filters unnecessarily.

**Permanent learning reference:** [SQL-R002 — Mandatory conditions across OR branches](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).

This is a learner-approved takeaway from the prior tutor explanation, not a student-authored solution or a new PNP question completion.

## Q3 — Student submission, executed result, reference solutions

**Question status:** First attempt reviewed; syntax error identified; student independent revised submission not yet received.

### Original learner SQLite submission (exactly preserved)

```sql
SELECT c.customer_id, c.customer_name, o.order_id
FROM customers as c
left join  orders as o on   c.customer_id = o.customer_id
sort by c.customer_id,  o.order_id asc 
```

**Original explanation (verbatim):**

> as it asks for every customer, i kept customer table on left

### Execution test

Ran the original query against an actual in-memory SQLite database containing the exact four customers and four orders from Q3. The attempted SQLite query returned:

```text
OperationalError: near "sort": syntax error
```

**Expected output:**

| customer_id | customer_name | order_id |
|---:|---|---:|
| 1 | Asha | 201 |
| 1 | Asha | 202 |
| 2 | Ravi | 203 |
| 3 | Neha | 204 |
| 4 | Kabir | NULL |

**Actual original-query output:** No rows returned (SQLite refused to execute the query). This is an execution error, not an empty result set. Cause: SQL sorting keyword is `ORDER BY`, not `SORT BY`. Join type and ON condition are correct.

### Assistant-verified SQLite reference query (executed)

```sql
SELECT c.customer_id, c.customer_name, o.order_id
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
ORDER BY c.customer_id, o.order_id ASC;
```

**Actual output from executing reference:** (1,Asha,201), (1,Asha,202), (2,Ravi,203), (3,Neha,204), (4,Kabir,NULL). Matches expected output.

### Assistant-converted SQL Server (T-SQL) reference query (not SQL Server executed)

```sql
SELECT c.customer_id, c.customer_name, o.order_id
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
ORDER BY c.customer_id, o.order_id ASC;
```

**Review:** Correct JOIN design, one syntax mistake; not scored as first-attempt execution success. Preserve a future learner revised attempt separately if submitted.

**Optional post-question new learning:** Await learner Yes/No. No new rule entered without explicit learner confirmation.

**Course tracking:** Q3 is original tutor-created practice, not a new PNP question ID or module mastery.


## Q3 — Learner-confirmed new learning (verbatim)

**Student's original reflection:**

```text
yeah i know it should not be sort by but its should be order by ..i did this mistake bcz i didnt recheck question before submitting . i hurried while submitting , so my learning is i should not hurry.
```

**Classification:** Submission discipline / pre-submit checklist (not a new JOIN concept). The learner knew `ORDER BY` but rushed and entered `SORT BY`. Reread the question, scan syntax, and execute/check results before submitting.

**Cumulative rules reference:** [SQL-R003](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).

**Tracking:** No new source question ID credited; Q3 original attempt and error remain preserved.

## Question 4 — INNER JOIN and filtering (first SQLite attempt reviewed)

Use the same four-customer and four-order sample as Q3.

**Task:** Return `customer_name`, `order_id`, and `status` for **only orders with status `'paid'`**. Sort by `order_id` ascending. Customers without a paid order must not appear, and each paid order should appear as its own row. Use an explicit JOIN and do not hardcode names or order IDs.

**Original learner SQLite query:** Submitted, preserved below.  
**Expected vs actual execution:** SQLite syntax error at `0.status`.  
**Reference SQLite and SQL Server solutions:** Preserved below after review.  
**Optional new-learning capture:** Awaiting learner Yes/No.

## Q4 — Original submission, SQLite execution and reviewed reference

**Original SQLite query — exact learner submission (unaltered):**

```sql
SELECT c.customer_name, o.order_id, 0.status
FROM customers AS c
join  orders as o on  c.customer_id=o.customer_id
where o.status = 'paid'
order by o.order_id asc
```

**Learner's original reasoning — verbatim:**

```text
i used inner join to Excludes customers without paid orders.

if i use left join... it will take all the customers
```

**Expected output:**

| customer_name | order_id | status |
|---|---:|---|
| Asha | 201 | paid |
| Neha | 204 | paid |

**Actual original-query execution against sample SQLite database:** `OperationalError: unrecognized token: "0.status"` — statement rejected, **no result set**; not an empty result table.

**Diagnosis:** The third selected expression uses digit `0` rather than letter `o` in the alias `o.status`. Other clauses correctly join customers and orders on customer_id, filter status='paid', and sort order_id ascending. The learner's INNER JOIN rationale was partly incomplete: INNER JOIN excludes rows with no matching order; the WHERE predicate specifically removes matching non-paid orders. A LEFT JOIN with this WHERE would also discard customers lacking a paid matching order.

### Assistant-verified reference — SQLite (executed)

```sql
SELECT c.customer_name, o.order_id, o.status
FROM customers AS c
INNER JOIN orders AS o
    ON c.customer_id = o.customer_id
WHERE o.status = 'paid'
ORDER BY o.order_id ASC;
```

**Executed reference output:** (Asha, 201, paid); (Neha, 204, paid). Both match expected.

### Assistant-created SQL Server T-SQL reference (not executed under SQL Server)

```sql
SELECT c.customer_name, o.order_id, o.status
FROM customers AS c
INNER JOIN orders AS o
    ON c.customer_id = o.customer_id
WHERE o.status = 'paid'
ORDER BY o.order_id ASC;
```

**Learner correction:** Not yet separately submitted; original preserved, reference is **not learner-authored**.

**Optional post-question learning:** Awaiting learner reply, Yes with exact reflection or No.

**Tracking:** Tutor diagnostic Q4 reviewed, but original query did not execute. No new PNP source credit.

## Q4 — Learner-confirmed learning (verbatim)

```text
same learning as previous question, i hurried up without rechecking,
```

**Category:** Submission discipline. Connects to existing [SQL-R003](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md), not a new rule. This was a later reflection, not the original written reasoning.

## Question 5 — LEFT JOIN with selective matching (reviewed original attempt)

The following tables are unchanged from Q3/Q4:

**customers:** (1,Asha), (2,Ravi), (3,Neha), (4,Kabir)  
**orders:** (201,1,paid), (202,1,pending), (203,2,cancelled), (204,3,paid)

**Task:** Return `customer_id`, `customer_name`, `order_id` and `status` for **every customer**, but attach **only paid orders**. Keep customers with no paid orders as rows with NULL order_id and NULL status. If a customer has multiple paid orders, show each matching paid order. Sort first by customer_id, then order_id, ascending. Use an explicit JOIN. No hardcoding.

**Original SQLite submission:** Recorded verbatim below.  
**Expected and actual:** Executed in SQLite; 2 missing rows.  
**Reference SQLite and T-SQL:** Recorded below following review.  
**New learning:** Awaiting optional response.

## Q5 — Original attempt, executed comparison, and reference queries

### Learner's first SQLite query (verbatim, including whitespace)

```sql
SELECT c.customer_id, c.customer_name, o.order_id, o.status
FROM customers AS c
left join  orders as o  on  c.customer_id = o.customer_id
where o.status='paid'
order by c.customer_id , o.order_id asc
```

### Learner's original reasoning (verbatim)

```text
i chose left join because of this below reuirements in the question:

Includes every customer, even if they have no paid orders.



Shows only paid orders in the order-related columns.



For customers without paid orders, returns NULL for order_id and status.



If a customer has multiple paid orders, shows each paid order separately.
```

### Reproducible sample

`customers`: (1,Asha), (2,Ravi), (3,Neha), (4,Kabir).  
`orders`: (201,1,paid), (202,1,pending), (203,2,cancelled), (204,3,paid).

### Expected output

| customer_id | customer_name | order_id | status |
|---:|---|---:|---|
| 1 | Asha | 201 | paid |
| 2 | Ravi | NULL | NULL |
| 3 | Neha | 204 | paid |
| 4 | Kabir | NULL | NULL |

### Actual SQLite output (executed on the sample tables with learner's *exact* first query)

| customer_id | customer_name | order_id | status |
|---:|---|---:|---|
| 1 | Asha | 201 | paid |
| 3 | Neha | 204 | paid |

**Mismatch:** Missing Ravi (2) and Kabir (4). The query is valid SQLite and runs without syntax errors, but its WHERE `o.status='paid'` eliminates non-paid and unmatched rows after the LEFT JOIN, defeating the requirement to retain every customer.

### SQLite reference solution — assistant-authored and executed

```sql
SELECT c.customer_id, c.customer_name, o.order_id, o.status
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
   AND o.status = 'paid'
ORDER BY c.customer_id, o.order_id ASC;
```

**Actual executed reference output:** (1, Asha, 201, paid), (2, Ravi, NULL, NULL), (3, Neha, 204, paid), (4, Kabir, NULL, NULL). Matches all expected rows.

### SQL Server (T-SQL) reference — assistant-converted, not executed in SQL Server

```sql
SELECT c.customer_id, c.customer_name, o.order_id, o.status
FROM customers AS c
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
   AND o.status = 'paid'
ORDER BY c.customer_id, o.order_id ASC;
```

**Explanation:** `ON` chooses matching paid orders while retaining each left-side customer; `WHERE` after the join would discard customer rows with no paid order. Do not attribute either reference block to the learner.

**Reviewed status:** Original query attempted and compared; logic incorrect for two unmatched customers. No independently revised SQLite submission yet. No PNP source ID earned.

**Optional new learning from Q5:** Awaiting learner Yes/No and their exact wording if Yes.

## Q5 — Learner-confirmed new learning

**Learner's exact takeaway (verbatim):**

```text
filters the joined result after the JOIN.

For Ravi, the matching order is cancelled, so it is removed. For Kabir, there is no matching order, so o.status is NULL, and the condition evaluates to UNKNOWN. That row is removed too.

The crucial distinction:
- ON controls which orders match each customer during the JOIN.
- WHERE filters the rows that remain after the JOIN.
```

**Generalized concept:** `LEFT JOIN ... ON ... AND right_table_condition` preserves all left rows while limiting matches. A null-rejecting right-table filter in `WHERE`, e.g. `WHERE o.status = 'paid'`, filters joined rows and may remove otherwise-preserved customers. Specific exceptions exist; e.g. `WHERE o.order_id IS NULL` can be used to identify unmatched customers.

**Centralized reference:** [SQL-R004 — LEFT JOIN ON versus WHERE](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md). The student chose this takeaway after review; their original Q5 answer is preserved separately.

## Question 6 — Customers without paid orders (original attempt reviewed)

Use the same Q5 tables: customers (1 Asha, 2 Ravi, 3 Neha, 4 Kabir); orders (201,1,paid), (202,1,pending), (203,2,cancelled), (204,3,paid).

**Task:** In SQLite, return `customer_id` and `customer_name` for customers who have **no paid orders at all**, including customers who have only pending/cancelled orders and customers who have no orders. Sort by `customer_id` ascending. Do not hardcode IDs or names. Use a JOIN-based approach.

**Student first attempt:** Submitted; exact attempt, expected/actual comparison and reference answers documented below.
**After review:** Run actual SQLite query; show expected vs actual; preserve learner's answer, an assistant-verified SQLite reference, and assistant-converted T-SQL reference; offer optional new-learning Yes/No.

## Q6 — Original attempted SQLite query, execution and reviewed references

**Status:** Original attempt reviewed, incorrect result. Learner revision and optional learning pending.

### Original SQLite query — learner-authored, unchanged

```sql
SELECT c.customer_id , c.customer_name
FROM customers AS c
inner join orders as o on  ( c.customer_id = o.customer_id )and status!='paid'
order by c.customer_id asc
```

### Original explanation — learner-authored, unchanged

```text
i dont need to know to each  customers , so not using left join

and used inner join to get only those customers who have no paid orders at all.
```

### Sample dataset
`customers`: (1,Asha), (2,Ravi), (3,Neha), (4,Kabir).  
`orders`: (201,1,paid), (202,1,pending), (203,2,cancelled), (204,3,paid).

**Expected output:**

| customer_id | customer_name |
|---:|---|
| 2 | Ravi |
| 4 | Kabir |

**Actual output: executed original SQLite query**

| customer_id | customer_name |
|---:|---|
| 1 | Asha |
| 2 | Ravi |

**Difference:** Extra Asha; missing Kabir. The `INNER JOIN` condition finds customers with *any non-paid order*, not customers having *zero paid orders*. Asha has both a paid and pending order, so the submitted query wrongly includes her. Kabir has no order, so the INNER JOIN drops him. SQLite executed without error; an unqualified `status` is unambiguous in this schema, but `o.status` is recommended.

### SQLite reference solution — assistant-authored and executed

```sql
SELECT c.customer_id, c.customer_name
FROM customers AS c
LEFT JOIN orders AS o
  ON c.customer_id = o.customer_id AND o.status = 'paid'
WHERE o.order_id IS NULL
ORDER BY c.customer_id ASC;
```

**Actual reference execution:** (2,Ravi), (4,Kabir) — matches expected. Join to *paid orders only*, then keep rows where the matching right-side primary key is NULL (no paid match). This is an anti-join pattern.

### SQL Server (T-SQL) reference — assistant-converted, not executed in SQL Server

```sql
SELECT c.customer_id, c.customer_name
FROM customers AS c
LEFT JOIN orders AS o
  ON c.customer_id = o.customer_id AND o.status = 'paid'
WHERE o.order_id IS NULL
ORDER BY c.customer_id ASC;
```

**Important:** Reference solutions are not learner submissions or academy official keys. No PNP course question ID credited.

**Post-question learning:** Await optional Yes/No from learner.

## Q6 — Learner-confirmed comprehensive new learning

**Original learner request (verbatim):**

```text
there is lot of learn from this question ... include all those things that got wrong here as the  new learning
```

The learner requested that **all** misconceptions in the Q6 review be included. Detailed review is stored at [SQL-R005 — Anti-join and absence of qualifying matches](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md). Topics include: distinguishing non-paid rows from absence of paid rows, INNER JOIN eliminating no-order customers, LEFT JOIN with qualifying ON predicate plus right-side IS NULL, row-versus-customer level logic, NULL UNKNOWN semantics, aliases, and mixed-status / no-order edge cases. Marked high priority for interleaved practice.

## Question 7 — Interleaved practice: orders, risk holds, and NULL (unattempted)

Two new SQLite tables:

**accounts**

| account_id | account_name | region |
|---:|---|---|
| 11 | Cedar | West |
| 12 | Delta | North |
| 13 | Orion | West |
| 14 | Maple | South |
| 15 | Nova | West |
| 16 | Luna | North |

**payments**

| payment_id | account_id | status | amount |
|---:|---:|---|---:|
| 501 | 11 | settled | 900 |
| 502 | 11 | pending | 300 |
| 503 | 12 | failed | 1500 |
| 504 | 13 | settled | NULL |
| 505 | 14 | settled | 1800 |
| 506 | 15 | failed | 400 |
| 507 | 15 | pending | 600 |

**Task:** Return `account_id`, `account_name` and `region` for accounts that have **no settled payment with a non-NULL amount greater than 1000**. All accounts must be considered, including those with no payments, non-settled payments, and settled payments with NULL or low amounts. Sort by `account_id` ascending. Use a JOIN-based SQLite query; no hardcoded account IDs, and do not use aggregation, a subquery or `NOT EXISTS` in this question.

**Why this task:** Interleave Q1's NULL comparisons, Q2's Boolean grouping, Q5's ON/WHERE, Q6's anti-match, and Q3/Q4's syntax/requirements checklist.

**Learner's original SQLite attempt and reasoning:** Pending.
**Expected result and SQLite reference/T-SQL translation:** Hidden until first attempt. Save attempts unmodified; execute and compare actual vs expected after submission.

## Q6 — Progressive reference explanation

The learner requested detailed justification for every reference solution, including a single dataset carried through all stages and the resulting **actual SQLite output after each step**. The complete Q6 tutorial has now been committed here: [Step-by-step Q6 walkthrough](../../../01-sql/practice/verified-results/2026-11-06-q06-walkthrough.md). It covers 4 stages (all customers → all LEFT JOIN matches → paid-only matches in ON → missing paid matches in WHERE), detailed output tables, anti-join reasoning, error analysis, and SQLite/T-SQL references. The Q7 answer remains unrevealed pending the learner's attempt.

## Q6 follow-up understanding check — LEFT JOIN multiple qualifying matches

**Prompt:** Ravi (customer_id 2) has orders 203 (cancelled), 205 (paid), and 206 (paid). With `LEFT JOIN orders AS o ON c.customer_id = o.customer_id AND o.status = 'paid'`, how many result rows does Ravi produce?

**Learner's answer (verbatim):** `2 rows, orders 205 and 206.`

**Review:** Correct. The cancelled order 203 does not match the ON predicate. Both paid orders match independently and produce two rows: (Ravi, 205, paid) and (Ravi, 206, paid). No extra NULL-extended row is generated because at least one qualifying right-side match exists.

**Evidence classification:** One correct follow-up reasoning check on JOIN multiplicity. This is not a new PNP SQL problem or proof of complete anti-join mastery. Q7 remains unattempted.


## Q6 — Dedicated anti-join lesson

The learner explicitly confirmed anti-joins are major new learning. See the [detailed SQL-R005 tutorial](../../../01-sql/revision/SQL-R005-ANTI-JOIN-DETAILED-LESSON.md), covering the reason for anti-joins, the original mistake, progressive queries with output tables, multiple matches, NULL cases, SQLite and T-SQL references, and practical applications. Q7 remains unattempted.

## Q7 — Student-led incremental coding workflow adopted

The learner requested Q7 onward follow a slow, stepwise interactive process: they explain **what they plan to do and why**, write a **partial SQLite query**, inspect its **actual SQLite output**, and then choose the next step. There is no upfront final-solution form. Each step's original input, output/error and review will be recorded separately in the dated slot journal. When the student declares the query finished, a separate final submission will be evaluated and compared with expected output. Assistant reference solutions and SQL Server translations remain hidden until then. **Q7 not yet attempted** at the time of this rule change.


## Q7 — Student-led Step 1: Inner subquery identification (in progress)

**Student-submitted original partial SQLite query (verbatim):**

```sql
select account_id
from payments
where status='status' and amount>=1000
```

**Actual SQLite execution:** This query executed against the Q7 payments sample dataset without syntax error and returned **zero rows** (empty result set), with one selected column `account_id`.

**Review:** Table `payments`, column `account_id`, and AND combination are appropriate for the intended first step. Two filtering issues: `status='status'` compares against literal text `status`, which appears in no row; target status should be the qualifying value specified in the question. `amount>=1000` includes amounts equal to 1000, whereas the problem requires strictly greater than 1000. The original submission has been preserved before any learner revision.

**Step 1 status:** Needs independent correction by learner; not completed. The outer query and final Q7 solution remain withheld. This is an intermediate GitHub preservation commit, **not** the Q7 question-closing commit.


### Q7 Step 1 — Student's independent corrected SQLite query

**Learner's revised query, verbatim:**

```sql
select account_id
from payments
where status='settled' and amount>1000
```

**Actual SQLite execution:** Ran this exact query in an in-memory SQLite database with the Q7 `payments` fixture (payment_id 501–507). Returned:

| account_id |
|---:|
| 14 |

**Expected for this partial step:** Account 14 only, because only its settled payment of 1800 has amount strictly greater than 1000. `amount > 1000` yields UNKNOWN for NULL, so an explicit IS NOT NULL check isn't necessary for this filter. Result matched expected. The student independently corrected the earlier literal `'status'` and `>=1000` errors.

**Status:** Step 1 successfully completed and reviewed. This is an intermediate preservation commit; full Q7 and Step 2 remain pending. Do not reveal the outer query or closing solution before the learner's independent attempt.


## Q7 — Subquery approach: final learner submission and execution

**Original full SQLite submission (verbatim):**

```sql
select account_id , account_name, region
from accounts 
where account_id  not in (


select account_id
from payments
where status='settled' and amount>1000
)
```

**SQLite fixture:** Accounts 11 Cedar/West, 12 Delta/North, 13 Orion/West, 14 Maple/South, 15 Nova/West, 16 Luna/North; payments 501–507 from the Q7 prompt. Executed exactly this SQL in SQLite.

**Actual output in the sample execution (in returned order):**

| account_id | account_name | region |
|---:|---|---|
| 11 | Cedar | West |
| 12 | Delta | North |
| 13 | Orion | West |
| 15 | Nova | West |
| 16 | Luna | North |

**Expected row values:** Same five rows, ordered by account_id ascending.

**Review:** All five expected rows were present, none extra, and the sample happened to be emitted ascending. The subquery's qualifying IDs are (14); the outer NOT IN correctly excludes this value. **Important qualification:** The user's query has no `ORDER BY account_id ASC`; ascending output is **not guaranteed** under SQLite/SQL Server SQL semantics, so the explicit sort requirement is not fully satisfied despite the matching observed output. Await a learner-authored correction to guarantee sort order. Also, `NOT IN` may fail to behave as intended if the subquery contains a NULL account_id; the current qualifying result is non-NULL.

**Progressive explanation:**
1. All accounts from `accounts`: six rows (11 Cedar, 12 Delta, 13 Orion, 14 Maple, 15 Nova, 16 Luna).
2. Inner qualifying filter: `status='settled' AND amount>1000` produces only `account_id=14`.
3. Outer NOT IN eliminates 14, leaving 11,12,13,15,16. Current sample output is ascending by coincidence, not guaranteed without ORDER BY.

**Assistant-formatted SQL Server/T-SQL equivalent of the submitted logical filter (not executed in SQL Server):**

```sql
SELECT account_id, account_name, region
FROM accounts
WHERE account_id NOT IN (
    SELECT account_id
    FROM payments
    WHERE status = 'settled'
      AND amount > 1000
);
```

**Study status:** Subquery row selection verified; ordering requirement requires an independent addition by student. LEFT JOIN anti-join approach is pending. Do not create a Q7 closing commit or mark full Q7 complete yet; this is an intermediate GitHub preservation commit.

## Q7 LEFT JOIN approach — Step 1 reasoning and first partial query

**Original student reasoning (verbatim):**

```text
i will use left join and keep accounts table on left as question asks me to have - all accounts that have never received a settled payment greater than ₹1,000.
```

**Review of reasoning:** Valid starting point: LEFT JOIN with accounts on the left preserves accounts with no matching payments. Additional qualifying predicates and anti-match detection are still future steps.

**Student's first partial SQLite query (verbatim):**

```sql
select
from accounts 
left join payments  on accounts.account_id = payments.account_id
```

**Executed in SQLite** against the Q7 six-account/seven-payment fixture. Actual result: `OperationalError: near "from": syntax error`. **No output table** was returned; this is not an empty successful result. SQLite requires at least one selected expression or column after SELECT. The LEFT JOIN table order and account_id matching condition themselves are correct.

**Step status:** Awaiting independent correction of the SELECT list; do not proceed to Step 2 or reveal the final query yet. Keep Q7 question-closing commit pending until both approaches and optional new learning are complete. This is an intermediate preservation commit.


### Q7 LEFT JOIN Step 1 — Independent revised SQLite query and real execution

**Student's corrected partial query, verbatim:**

```sql
select accounts.account_id , accounts.account_name, accounts.region
from accounts 
left join payments  on accounts.account_id = payments.account_id
```

**Actual execution:** Ran exact SQL using SQLite against Q7's 6-row `accounts` and 7-row `payments` tables. The SQLite engine returned **8 rows** in the following observed order (not guaranteed without ORDER BY):

| account_id | account_name | region |
|---:|---|---|
| 11 | Cedar | West |
| 11 | Cedar | West |
| 12 | Delta | North |
| 13 | Orion | West |
| 14 | Maple | South |
| 15 | Nova | West |
| 15 | Nova | West |
| 16 | Luna | North |

**Review:** Valid SQLite syntax and correct LEFT JOIN keys. Accounts 11 and 15 each have two matching payment rows, producing repeated account columns; account 16 has no payment match but remains due to LEFT JOIN. The student's SELECT projects only columns from `accounts`, so NULL payment values are **not visible in this result**. In a diagnostic query selecting payment fields, Luna's right-side fields would be NULL, but that was not this submitted query's output. No filter, sorting, or final anti-match evaluation has yet been performed, by design.

**Step status:** Step 1 reviewed correct and preserved. Await student's Step 2 reasoning **before** asking them to write a new SQL query. Q7 question-closing commit remains pending; this is an incremental save.

## Q7 LEFT JOIN approach — Step 2: inspect matched payment columns

**Learner's exact Step 2 SQLite query:**

```sql
select accounts.account_id , accounts.account_name, accounts.region, payments.status, payments.amount
from accounts 
left join payments  on accounts.account_id = payments.account_id
```

**Learner's intent:** Show output after adding payment status and amount to the existing LEFT JOIN, so the matching payment details and NULLs are visible. Review approved as an exploratory step; no filtering introduced yet.

**Actual execution:** SQLite in-memory database with the six Q7 accounts and seven Q7 payments. Exact submitted SQL executed successfully. Returned eight rows, in this observed order (not guaranteed without ORDER BY):

| account_id | account_name | region | status | amount |
|---:|---|---|---|---:|
| 11 | Cedar | West | pending | 300 |
| 11 | Cedar | West | settled | 900 |
| 12 | Delta | North | failed | 1500 |
| 13 | Orion | West | settled | NULL |
| 14 | Maple | South | settled | 1800 |
| 15 | Nova | West | failed | 400 |
| 15 | Nova | West | pending | 600 |
| 16 | Luna | North | NULL | NULL |

**Review:** Cedar and Nova each show two matched payment rows. Orion's amount NULL belongs to a real settled payment; Luna has no payment row, hence null-extended status and amount. The distinction between a NULL *field in a real match* and *no match* matters for anti-join reasoning. Step 2 is a correct exploratory projection, not a complete solution. There is no ORDER BY or payment qualification yet.

**Next:** Ask for learner's Step 3 thinking only; no pre-supplied SQL or final query. Q7 closing commit is deferred until both approaches are completed and reviewed.


## Q7 LEFT JOIN Step 3 — Original and revised thinking

### Earlier Step 3, original SQLite query

```sql
select accounts.account_id , accounts.account_name, accounts.region, payments.status, payments.amount
from accounts 
left join payments  on accounts.account_id = payments.account_id
where status !='settled' and amount <=1000
```

**Actual SQLite result recorded in the session review:** Three rows: (11, Cedar, West, pending, 300), (15, Nova, West, failed, 400), and (15, Nova, West, pending, 600). This evaluates non-settled, low-amount individual payment rows, not absence of qualifying payments. Missing Delta, Orion, and Luna from the expected final set; Nova appears twice.

### Revised Step 3 query supplied for reasoning review (verbatim)

```sql
select accounts.account_id , accounts.account_name, accounts.region, payments.status, payments.amount
from accounts 
left join payments  on accounts.account_id = payments.account_id
and status !='settled' and amount <=1000
```

**Review of reasoning only:** Moving right-side conditions to ON helps preserve the left accounts. However, matching non-settled low-amount payments is still conceptually the inverse of the intended qualifying payments. Maple, whose settled payment of 1800 is qualifying, would not match this predicate and would be retained as an unmatched left row. No corrected SQL is shown to the student; await revised reasoning before next code step.

**Status:** Q7 incomplete, closing commit pending.


## Q7 LEFT JOIN — Step 3 corrected intermediate SQLite query (executed)

**Learner's exact submitted query (verbatim):**

```sql
select accounts.account_id , accounts.account_name, accounts.region
from accounts 
left join payments  on accounts.account_id = payments.account_id
and status ='settled' and amount >1000
```

**Actual execution:** Ran the exact query in SQLite against Q7's six `accounts` and seven `payments` rows. Successful execution, six rows (observed order; no ORDER BY guarantee):

| account_id | account_name | region |
|---:|---|---|
| 11 | Cedar | West |
| 12 | Delta | North |
| 13 | Orion | West |
| 14 | Maple | South |
| 15 | Nova | West |
| 16 | Luna | North |

**Review:** The `ON` clause correctly restricts matches to settled payments with amount greater than 1000, leaving account 14 (Maple) as the only account with a qualifying payment match in this sample. Every left-side account remains due to `LEFT JOIN`. The user projects only `accounts` fields, so NULL-extended payment fields are not visible in the actual result; they should not be presented as actual selected output. Account 14 remains, so this step is correct as an intermediate join, not the completed anti-join answer.

**Status:** Step 3 reviewed; Step 4 reasoning is next. Q7 closing commit remains pending until both approaches are completed and reviewed.


## Q7 LEFT JOIN — Step 4 inspecting payment-side columns

**Learner's exact query:**

```sql
select accounts.account_id , accounts.account_name, accounts.region, payments.status, payments.amount
from accounts 
left join payments  on accounts.account_id = payments.account_id
and status ='settled' and amount >1000
```

**Executed against the original Q7 sample in SQLite. Expected intermediate JOIN output and actual output match:**

| account_id | account_name | region | status | amount |
|---:|---|---|---|---:|
| 11 | Cedar | West | NULL | NULL |
| 12 | Delta | North | NULL | NULL |
| 13 | Orion | West | NULL | NULL |
| 14 | Maple | South | settled | 1800 |
| 15 | Nova | West | NULL | NULL |
| 16 | Luna | North | NULL | NULL |

**Review:** Six rows. Only Maple has a qualifying joined payment, as shown by non-null payment columns. Other accounts have no payment match satisfying both status='settled' and amount>1000, so LEFT JOIN preserves them with null-extended right-side fields. Orion has a real payment with a NULL amount, but that payment is not a qualifying match. No ORDER BY, so presentation order not guaranteed. Current result is an exploratory stage, not the final account list.

**Next:** Learner explains the filtering step in their own words, then writes its SQLite query. No final reference query pre-revealed. Closing Q7 commit remains pending until both approaches and review are complete.


## Q7 LEFT JOIN — Step 5 repeated reasoning attempt (executed)

**Learner's exact SQLite query:**

```sql
select accounts.account_id , accounts.account_name, accounts.region, payments.status, payments.amount
from accounts 
left join payments  on accounts.account_id = payments.account_id
and status ='settled' and amount >1000 and amount is null and status is null
```

**SQLite execution verified in the Q7 fixture:** Six rows, each with NULL status and NULL amount:

| account_id | account_name | region | status | amount |
|---:|---|---|---|---:|
| 11 | Cedar | West | NULL | NULL |
| 12 | Delta | North | NULL | NULL |
| 13 | Orion | West | NULL | NULL |
| 14 | Maple | South | NULL | NULL |
| 15 | Nova | West | NULL | NULL |
| 16 | Luna | North | NULL | NULL |

**Expected final account IDs:** 11, 12, 13, 15, 16. The actual query contains extra account 14 and two extra selected columns. The ON clause is impossible to satisfy: `amount>1000 AND amount IS NULL` cannot be TRUE, nor can `status='settled' AND status IS NULL`. Thus every account is retained by LEFT JOIN as unmatched, including Maple. This query is an intermediate failed attempt, not the completed Q7 result. Await learner's distinction between match conditions (ON) and post-join filtering (WHERE), without providing their final query.


## Q7 LEFT JOIN — Step 5 conceptual correction (reviewed, not executed)

**Learner's explicit selection:** `WHERE` for identifying qualifying matches (incorrect as a conceptual label; the student's actual query does use ON for qualifying matches).

**Learner's exact proposed query (review-only, not executed in this review):**

```sql
select accounts.account_id , accounts.account_name, accounts.region, payments.status, payments.amount
from accounts 
left join payments  on accounts.account_id = payments.account_id
and status ='settled' and amount >1000 where 
amount is null and status is null
```

**Reasoning review:** Meaningful progress: ON restricts matching to settled payments with amount >1000; WHERE checks NULL-extended right-side fields to select accounts with no qualifying matches. For the specific Q7 fixture, the NULL checks are sufficient since any qualifying matched row has non-NULL status and amount. For robust anti-match detection, prefer testing a non-nullable payment key. The submitted query still includes extra right-side columns and no explicit ORDER BY; full output requirements not yet complete. No actual execution claimed for this Step 5 proposal. Student should independently finalize it. Q7 closing commit still pending.


## Q7 LEFT JOIN — learner's final first submission (independent)

**Verbatim SQLite query:**

```sql
select accounts.account_id , accounts.account_name, accounts.region, payments.status, payments.amount
from accounts 
left join payments  on accounts.account_id = payments.account_id
and status ='settled' and amount >1000 where 
amount is null and status is null
order by accounts.account_id  asc
```

**SQLite execution:** Executed this exact query against the original Q7 fixture with 6 accounts and 7 payments, returning five rows sorted by account_id:

| account_id | account_name | region | status | amount |
|---:|---|---|---|---:|
| 11 | Cedar | West | NULL | NULL |
| 12 | Delta | North | NULL | NULL |
| 13 | Orion | West | NULL | NULL |
| 15 | Nova | West | NULL | NULL |
| 16 | Luna | North | NULL | NULL |

**Expected final output:** The same five accounts and order, but only three columns: `account_id`, `account_name`, `region`. **Diff:** Two extra selected columns (`status`, `amount`); no missing/extra account rows.

**Reasoning review:** The learner independently achieved correct anti-join matching: ON accepts payment matches only where status='settled' and amount>1000; WHERE amount IS NULL AND status IS NULL keeps rows with no qualifying match; explicit ORDER BY is correct. The two NULL checks are sufficient for this particular data and ON predicates, though using a non-nullable right-side key is the more robust/general anti-join convention. The selection must be reduced to the three required columns for exact output compliance. Preserve the unaltered original. Await learner's amended final projection; do not mark Q7 fully completed or create the question-closing commit yet.

**Reference/learning:** Both approaches and the comparison will be reviewed in a progressive walkthrough after final output validation. GitHub closing commit and optional new-learning capture still pending.


## Q7 — Final LEFT JOIN student revision: output verified

**Original revised SQLite query, preserved verbatim:**

```sql
select accounts.account_id , accounts.account_name, accounts.region
from accounts 
left join payments  on accounts.account_id = payments.account_id
and status ='settled' and amount >1000 where 
amount is null and status is null
order by accounts.account_id  asc
```

**Verified execution environment:** SQLite against the original six account and seven payment rows, including Orion's NULL amount and Luna's lack of payments.

**Actual SQLite result:**

| account_id | account_name | region |
|---:|---|---|
| 11 | Cedar | West |
| 12 | Delta | North |
| 13 | Orion | West |
| 15 | Nova | West |
| 16 | Luna | North |

**Expected result:** Exactly these five rows and three columns, in account_id ascending order. **All 5 expected rows, 0 extra rows, 0 missing rows; column projection and ORDER BY now correct.**

**Why it works:** The LEFT JOIN's ON condition requires matching account ID, settled status, and amount > 1000. In this sample only Maple's payment 505 qualifies. Other accounts are preserved with NULL right-side columns. The student's WHERE tests amount IS NULL and status IS NULL, which is sufficient here because qualifying right-side rows must have non-NULL values for both columns. Checking a non-nullable right-side primary key is generally clearer and more robust for missing matches. The SELECT now returns just requested account columns, with explicit ascending sort.

**Status:** Final LEFT JOIN approach verified correct on sample. The previous query with extra output columns remains intact as its original attempt. Q7 subquery approach's original submission produced correct IDs but omitted ORDER BY, which remains a separate noted caveat. Await optional new-learning review and then a distinct **Q7 question-closing commit** before advancing to Q8.


## Q7 — Learner-confirmed new learning and final status (reviewed)

**Learner's exact statement (verbatim):**

```text
anti join pattern was a importnant and new concept for me ..so save all those concept notes that were taught me here
```

**Learning classification:** SQL-R006, high-priority anti-join and subquery comparison, including ON vs WHERE, three-valued NULL logic, no qualifying row vs nonqualifying row, RIGHT-side non-nullable key detection, row multiplicity, and required projection and ordering.

**Full Q7 reference lesson:** [Detailed Q7 anti-join / NOT IN guide](../../../01-sql/revision/SQL-R006-Q7-ANTI-JOIN-AND-SUBQUERY-DETAILED-LESSON.md). **Cross-day revision index:** [SQL-R006 in learned rules](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).

### Q7 two-approach completion review

- **Subquery / NOT IN:** Learner identified qualifying account IDs and submitted a complete query returning all five correct accounts and three columns; **did not use ORDER BY**, so required ascending order is not guaranteed. **Status: correct filtering; ordering requirement unmet in the submitted version.** A formatted assistant reference with ORDER BY appears in detailed notes, not misattributed to the learner.
- **LEFT JOIN anti-join:** Learner progressed from incorrect WHERE filters and contradictory predicates to the qualifying ON clause and missing-match WHERE condition, then independently removed extra output columns and added ORDER BY. Verified on SQLite fixture: exact expected five accounts, three columns, ascending order. **Status: independently corrected; final sample requirements met.**
- **Transfer/mastery:** One successful corrected anti-join on a known fixture supports progress but doesn't prove generalized mastery. The next mixed question will test transfer.
- **PNP source IDs newly completed:** None verified. Q7 is tutor-authored practice.

**Workflow:** This Q7 record and revision bank are ready for a distinct question-closing GitHub commit. Do not open Q8 before that remote commit is verified.


---

## Q8 — Vendors Without Qualifying Deliveries (finished diagnostic)

**Date:** 2026-11-06 · **Outcome:** student independently corrected final SQLite answer; exact expected five vendors, three columns and ascending sort. Q8 is a **tutor-authored diagnostic**, not PNP source practice. No actual focused-minutes total was recorded.

**Complete Q8 evidence, input/output and progression:** [Original question and final detailed SQLite/T-SQL review](../../../study-records/2026-11-06/Q8-vendors-without-qualifying-deliveries.md). This linked record contains every submitted learner SQLite step and its actual results/errors: ambiguous `vendor_id`, trailing SELECT comma, unfiltered LEFT JOIN (10 rows), qualification predicates in ON (8 rows), unmatched right-side vendor ID filter (5 rows with extra columns), wrong right-side vendor ID selection (five NULL IDs), final left-side ID selection and ORDER BY (five correct rows).

**Learner's final SQLite query (verbatim):**

```sql
select v.vendor_id, v.vendor_name, v.region
from vendors as v
left join deliveries as d on v.vendor_id=d.vendor_id and d.status='delivered' and d.amount > 1000 and (v.region = 'West' or d.service='express')
where d.vendor_id is null
order by v.vendor_id asc
```

**Actual executed final output:**

| vendor_id | vendor_name | region |
|---:|---|---|
| 1 | Atlas | West |
| 2 | Birch | North |
| 4 | Drift | South |
| 5 | Ember | North |
| 8 | Haven | East |

**User response to optional new-learning prompt:** Yes.

**Learner's exact insight:**

```text
anti join pattern concept
```

**New revision entry:** [SQL-R007 — Q8 anti-join transfer, NULLs, left-side projection and ordering](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md). Revisited earlier SQL-R005 and R006 concepts in a new business scenario.

**Review integrity:** Q1–Q8 all reviewed, 4 independently correct/corrected (Q1, Q2, Q7, Q8), 1 correct first try (Q1). Q3–Q6 still require independent corrected solutions. Q8 successfully completed only after learner-authored revisions, so it is not a first-try pass or evidence of universal mastery. New PNP source IDs: zero; Python source pages: zero. Follow-up source practice and focus-time logging remain outstanding.

**GitHub cross-repo Q8 mirror:** [Data Engineering Mastry Q8 record](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/Q8-vendors-without-qualifying-deliveries.md).

**Question-closing commits:** To be recorded in the separate Q8 closing checkpoint after final repository verification.
