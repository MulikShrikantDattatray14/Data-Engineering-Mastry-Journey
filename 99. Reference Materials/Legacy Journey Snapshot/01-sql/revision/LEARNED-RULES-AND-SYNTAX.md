# SQL — General Rules, Syntax & Lessons Learned

A living, cross-day revision reference for **new insights explicitly identified by the learner during independent SQL practice**. Keep source links and question IDs. Do not confuse a newly learned rule with an entire topic being mastered.

## SQL-R001 — NULL comparisons and WHERE filtering

**First learned:** 2026-11-06 · Day 1 · Slot 1 · Q1 (paid Maharashtra orders)  
**Category:** SQL filtering · NULL · three-valued logic  
**Type:** General SQL rule  
**Source:** [Original Q1, first attempt, and review](../../10-learning-journal/sessions/2026-11-06/slot-01-sql.md)

### Learner's recorded takeaway (verbatim)

```text
Your condition amount > 1000 evaluates to UNKNOWN when amount is NULL. Since WHERE retains only rows whose condition is TRUE, order 104 is excluded automatically.

You do not need an additional amount IS NOT NULL condition for this query.
```

### Reusable rule / syntax

For a regular SQL comparison such as `amount > 1000`, a `NULL` input produces **UNKNOWN**, not TRUE. A `WHERE` clause filters out both FALSE and UNKNOWN. Therefore, **the predicate alone excludes NULL values** in this situation; adding `AND amount IS NOT NULL` would be redundant.

```sql
SELECT order_id, amount
FROM orders
WHERE amount > 1000;
```

If instead the goal is to **explicitly find missing amounts**, use:

```sql
SELECT order_id
FROM orders
WHERE amount IS NULL;
```

**Boundary:** This applies to ordinary comparison predicates; do not generalize that *every* SQL expression automatically excludes NULL, because `IS NULL` and other operators/functions have different behavior.

**Practice outcome:** Q1 independently solved and reviewed; rule noted for spaced revision. No PNP question or topic mastery automatically credited.

---

## Future entries

Add each new student-submitted learning point here with a stable rule ID, date, slot, question, original wording, validated general rule, representative syntax, a caveat if needed, and a link to the exact question archive. Optional: student may explicitly say **No new learning** and continue without creating an entry.


## SQL-R002 — Mandatory conditions across OR branches

**Date:** 2026-11-06 | **Day 1 Slot 1 Q2** | **Category:** SQL Boolean logic / NULL / WHERE
**Learner explicitly confirmed after review:** Q2's explanation is important new learning.
**Question:** [Q2 session and both learner attempts](../../10-learning-journal/sessions/2026-11-06/slot-01-sql.md)

### Rule
SQL evaluates the **entire WHERE expression**. AND needs both conditions TRUE; OR needs at least one TRUE. AND has higher precedence than OR unless parentheses specify another grouping.

For this expression:

```sql
WHERE (status = 'paid' AND state = 'Maharashtra')
   OR amount > 2000
```

A paid Maharashtra row with NULL amount passes: the first branch is TRUE, the second is UNKNOWN, and TRUE OR UNKNOWN is TRUE.

**If a requirement must apply to every OR branch, group the OR alternatives and place the mandatory condition outside with AND:**

```sql
WHERE ((status = 'paid' AND state = 'Maharashtra') OR amount > 2000)
  AND amount IS NOT NULL
```

This syntax works in SQLite and SQL Server. The student originally repeated IS NOT NULL within both branches; that correction was valid, while this grouped version is shorter. WHERE only retains TRUE, not FALSE or UNKNOWN.

**Recall:** Would a paid row with NULL amount pass `status = 'paid' OR amount > 2000`?

**Source:** [Verified expected vs actual Q2](../practice/verified-results/2026-11-06-q01-q02.md). Learner requested this new learning **after** previously choosing No for Q2; this later explicit request overrides No. No extra course problem completion is credited.


## SQL-R003 — Check syntax and requirements before submitting

**Date:** 2026-11-06 · Day 1 · Slot 1 · Q3  
**Classification:** Practice habit / submission checklist, with related syntax reminder  
**Source:** [Q3 original attempted query and review](../../10-learning-journal/sessions/2026-11-06/slot-01-sql.md)

### Learner's exact reflection (verbatim)

```text
yeah i know it should not be sort by but its should be order by ..i did this mistake bcz i didnt recheck question before submitting . i hurried while submitting , so my learning is i should not hurry.
```

### Reusable reminder

The learner **knew** the correct SQL keyword but rushed and wrote `SORT BY`. In both SQLite and SQL Server, the sorting clause is `ORDER BY`, not `SORT BY`.

**20-second pre-submit check:**
1. Reread the required columns, filters, joins, sorting, and unmatched-row behavior.
2. Scan the query for invalid syntax, especially `ORDER BY` and aliases.
3. Run the query when possible and compare its actual output to the expected rows before submitting.

This records a learner-identified process mistake, **not** a new JOIN misconception or a PNP completion.

---

### Q4 reinforcement — same learner-identified habit (2026-11-06)

**Original Q4 reflection, verbatim:**

```text
same learning as previous question, i hurried up without rechecking,
```

The Q4 original query mistakenly used the digit `0` in `0.status` rather than the letter `o` from the orders alias. The learner explicitly connected this to rushing, the same preventable behavior identified in Q3. This is an additional **Q4 occurrence of SQL-R003**, not a new rule.

**Q4 source:** [Day 1 Slot 1 Q4](../../10-learning-journal/sessions/2026-11-06/slot-01-sql.md).


## SQL-R004 — LEFT JOIN: ON versus WHERE filtering

**Date:** 2026-11-06 · Day 1 · Slot 1 · Q5  
**Category:** Join semantics / filtering / NULL  
**Related attempt:** [Q5 original query, expected vs actual, and corrections](../../10-learning-journal/sessions/2026-11-06/slot-01-sql.md)

### Exact learner-chosen takeaway (verbatim)

```text
filters the joined result after the JOIN.

For Ravi, the matching order is cancelled, so it is removed. For Kabir, there is no matching order, so o.status is NULL, and the condition evaluates to UNKNOWN. That row is removed too.

The crucial distinction:
- ON controls which orders match each customer during the JOIN.
- WHERE filters the rows that remain after the JOIN.
```

### Generalized rule (assistant explanation)

**With an outer join, choose WHERE a right-table filter is placed based on whether unmatched left-table rows must survive.**

- A right-table predicate in the `ON` clause controls **which right rows match**, while `LEFT JOIN` still preserves every left row by supplying NULLs when no match qualifies.
- A right-table predicate in the `WHERE` clause filters **the completed joined rows**. A condition such as `WHERE o.status = 'paid'` rejects NULL-extended rows (`UNKNOWN`) and non-paid matches (`FALSE`), so customers without paid orders disappear.
- **If you need every customer but only paid order details**, place `o.status = 'paid'` in `ON`. **If you need only customers with paid orders**, put that condition in `WHERE` (or use INNER JOIN appropriately).

```sql
-- Preserve all customers; attach only paid orders
SELECT c.customer_id, c.customer_name, o.order_id
FROM customers AS c
LEFT JOIN orders AS o
  ON c.customer_id = o.customer_id
 AND o.status = 'paid';
```

**Nuance:** This is not a universal claim that `WHERE` always turns a LEFT JOIN into INNER JOIN. It applies to NULL-rejecting right-table conditions such as `o.status = 'paid'`. Conditions like `WHERE o.order_id IS NULL` deliberately select unmatched rows instead. SQL logical processing considers JOIN/ON before WHERE.

**SQLite and SQL Server:** The demonstrated syntax and behavior apply to both. This is a new confirmed learning entry, not a new PNP question completion.


### Q5 — High-priority learning (learner explicitly reaffirmed)

**Priority:** High — learner reports making this type of error previously, so revisit in mixed questions.

**Learner-selected explanation (verbatim as pasted, including table formatting):**

~~~text
## The generalized rule

When using `LEFT JOIN`, the placement of a filter determines whether unmatched left-table records are preserved.

|   |
| - |

Place the filter in

|   |
| - |

What it does

|   |
| - |

`ON`

|   |
| - |

Restricts which right-table rows can match, while preserving all left-table rows

|   |
| - |

`WHERE`

|   |
| - |

Filters the final joined rows, potentially removing left-table records

### Scenario 1 — Keep every customer, attach only paid orders
```
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
   AND o.status = 'paid'
```

All customers remain, including those without paid orders.

### Scenario 2 — Return only customers with paid orders
```
LEFT JOIN orders AS o
    ON c.customer_id = o.customer_id
WHERE o.status = 'paid'
```

Customers without paid orders disappear.

Important nuance: Not every `WHERE` condition removes unmatched records. For example, `WHERE o.order_id IS NULL` can specifically identify customers with no matching orders.

This rule works in SQLite and SQL Server.
~~~

**Clean review index (without changing the original above):**

| Filter location | Effect |
|---|---|
| `ON` (right-table filter) | Limits qualifying matches; unmatched left rows remain under LEFT JOIN |
| `WHERE` (right-table NULL-rejecting filter) | Filters joined results; may remove unmatched left rows |

**Retrieval checkpoints:** Revisit in Q6 (no qualifying match), later multi-condition JOINs, and mixed review with NULL, OR grouping, and syntax checking. First require independent attempts; do not expose solution keys before attempts.


## SQL-R005 — Find records with NO qualifying matches (anti-join)

**Date:** 2026-11-06 | **Day 1, Slot 1, Q6**  
**Priority:** High — user asked to capture all mistakes and all associated concepts.
**Source:** [Original Q6 attempt, actual vs expected results, and reference queries](../../10-learning-journal/sessions/2026-11-06/slot-01-sql.md)

### Learner's exact request (verbatim)

```text
there is lot of learn from this question ... include all those things that got wrong here as the  new learning
```

### What went wrong and what to learn

1. **“Has a non-paid order” is not “has no paid orders.”** `o.status != 'paid'` checks *individual order rows*. A customer with one paid and one pending order still has a pending row; that doesn't prove there are zero paid orders. Q6 incorrectly included Asha for this reason.
2. **INNER JOIN drops left rows with no right-side match.** A customer with no orders at all (Kabir) disappears in an INNER JOIN. Q6 required such customers, so INNER JOIN was inappropriate for this approach.
3. **Formulate absence as an anti-match.** Start with every customer using `LEFT JOIN`; make only paid orders eligible to match in `ON`; then select customers with *no qualifying paid match* using `WHERE o.order_id IS NULL`. Choose a right-side column known to be non-NULL for matched rows, ideally a non-nullable key.
4. **ON versus WHERE matters.** `ON o.status = 'paid'` narrows the matched right-side orders without removing customers. `WHERE o.status != 'paid'` removes unmatched NULL-extended records and filters individual non-paid rows, which isn't a “never paid” test.
5. **SQL NULL and three-valued logic.** For unmatched rows, right-side values are `NULL`; `NULL != 'paid'` is `UNKNOWN`, not TRUE, so the original predicate doesn't keep unmatched customers.
6. **A row-level test is not an entity-level negative condition.** To assert that an entity has *no* matching qualifying rows, reason across all rows belonging to that entity. A single nonqualifying row doesn't rule out other qualifying rows.
7. **Always test mixed-status and zero-row edge cases.** Asha has both paid and pending orders; Kabir has no orders. They are deliberately necessary test cases for detecting this bug.
8. **Qualify column names.** `o.status` is clearer than bare `status` and avoids ambiguity when more tables have a column of the same name.
9. **Verify actual vs expected output before calling the solution correct.** Original returned Asha/Ravi; expected Ravi/Kabir. A successfully executing query can still be logically wrong.

### Reference pattern — SQLite and SQL Server

```sql
SELECT c.customer_id, c.customer_name
FROM customers AS c
LEFT JOIN orders AS o
  ON c.customer_id = o.customer_id
 AND o.status = 'paid'
WHERE o.order_id IS NULL
ORDER BY c.customer_id ASC;
```

This is an **anti-join pattern**; Q6's reference query was reviewed after the student's attempt, not an original student solution. Its syntax is valid in SQLite and T-SQL; do not claim independent T-SQL execution.

### Practice reinforcement

Use future interleaved questions to contrast (a) at least one qualifying row, (b) at least one nonqualifying row, and (c) no qualifying row. Mix in previous Q1 NULL, Q2 AND/OR grouping, Q5 ON/WHERE placement, and Q3/Q4 careful submission checks. Do not leak answers to unattempted questions.

---


### Dedicated detailed lesson — Anti-join (SQL-R005)

The learner explicitly highlighted the anti-join pattern as a major *new* concept, so it has a full separate tutorial: [SQL-R005 — Detailed anti-join lesson](SQL-R005-ANTI-JOIN-DETAILED-LESSON.md). It explains the Q6 data, original reasoning mistake, each SQL stage and its actual intermediate results, what happens with 0/1/multiple matches, NULL handling, when ON versus WHERE matters, T-SQL equivalence and Data Engineering applications. Mark this for high-priority retrieval practice. Q7 remains unanswered.


## SQL-R006 — Q7 anti-join consolidation (high priority)

**Date:** 2026-11-06 · Day 1 · Slot 1 · Q7. The learner explicitly called the anti-join pattern important, unfamiliar new learning and asked that all taught concepts be saved.

**Exact learner statement (verbatim):**

```text
anti join pattern was a importnant and new concept for me ..so save all those concept notes that were taught me here
```

**Detailed lesson:** [SQL-R006 — Q7 full progression, intermediate SQLite outputs, NOT IN and anti-join](SQL-R006-Q7-ANTI-JOIN-AND-SUBQUERY-DETAILED-LESSON.md).

**Generalized rule:** To find entities with **no qualifying matches**, start with all entities, LEFT JOIN only rows meeting the qualifying condition via ON, then use WHERE on a **non-nullable right-side key IS NULL** to retain absent matches. Never confuse a nonqualifying *row* with absence of all qualifying rows for the entity. Beware of NULLs in NOT IN, extra selected columns, and omitted ORDER BY. Use this rule in later mixed retrieval questions.

**Evidence:** Q7 final student LEFT JOIN matched all five expected rows and the three required columns in ascending order. Student's NOT IN version filtered correctly but omitted explicit ORDER BY. No PNP source ID credit is inferred.


## SQL-R007 — Q8 anti-join transfer and selecting left-side IDs

**Date:** 2026-11-06 · Day 1 · Slot 1 · Q8 (Vendors Without Qualifying Deliveries).  
**Learner's *exact* new learning (verbatim):**

```text
anti join pattern concept
```

**Evidence:** The student independently repaired the Q8 JOIN query, with `d.status='delivered'`, `d.amount>1000`, and `(v.region='West' OR d.service='express')` inside the LEFT JOIN `ON`, followed by `WHERE d.vendor_id IS NULL` and a left-table `v.vendor_id` selection and sort. The final SQLite execution matched all five expected vendors (1, 2, 4, 5, 8), with correct columns, no duplicates and ascending IDs, **after multiple independent corrections**, not on first attempt.

**General rule (assistant-authored):** To find entities with **no qualifying right-side records**, preserve all left-side entities with `LEFT JOIN`; place the matching criteria in `ON`; check a guaranteed non-NULL right-side identifier for NULL in `WHERE`. For final projection and sorting, use the **left-side entity key**, because right-side keys are NULL on the anti-matched rows. In this fixture, `d.vendor_id IS NULL` works; when available prefer a non-nullable right-side primary key (`d.delivery_id IS NULL`).

**Key transfer details:** Parentheses around the OR alternative prevent logic leakage; `NULL > 1000` does not match; multiple nonqualifying deliveries do not disqualify a vendor; multiple qualifying deliveries still cause the vendor to be excluded. An explicitly sorted output is mandatory when order is required.

**Full independently authored SQL, input and output, executed progressive review, and SQL Server reference:** [Q8 — complete reviewed question](../../study-records/2026-11-06/Q8-vendors-without-qualifying-deliveries.md).

**Integrity:** Tutor-created Q8, zero new PNP source credit. One successful corrected fixture is evidence of learning, not generalized mastery.
