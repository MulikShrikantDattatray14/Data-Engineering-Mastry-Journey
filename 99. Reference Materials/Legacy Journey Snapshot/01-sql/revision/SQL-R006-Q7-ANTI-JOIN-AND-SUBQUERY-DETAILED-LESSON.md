# SQL-R006 — Q7: Anti-Join vs. NOT IN, with progressive SQLite outputs

**Study date:** 2026-11-06 · Day 1 / Slot 1 / Question 7  
**Priority:** HIGH — learner explicitly identified anti-joins as important, new learning.  
**Source:** [Q7 chronological original attempts and reviews](../../10-learning-journal/sessions/2026-11-06/slot-01-sql.md) · [Related Q6 anti-join fundamentals](SQL-R005-ANTI-JOIN-DETAILED-LESSON.md)  
**Status:** Two SQLite solution approaches reviewed; LEFT JOIN final submission verified complete; original NOT IN version returned correct rows but omitted required explicit ordering. These are *tutor-authored practice/reference notes*, not an official PNP answer key.

## 1. Learner's exact new-learning statement

```text
anti join pattern was a importnant and new concept for me ..so save all those concept notes that were taught me here
```

This is copied verbatim. The lesson below expands the concepts covered with the learner during Q7.

## 2. Understand the task before coding

Find accounts with **no payment satisfying BOTH** `status = 'settled'` and `amount > 1000`. A settled payment of exactly 1000 is insufficient. A NULL amount is not known to exceed 1000. Accounts without any payments must remain.

### Input fixture (SQLite)

```sql
CREATE TABLE accounts (account_id INTEGER PRIMARY KEY, account_name TEXT, region TEXT);
CREATE TABLE payments (payment_id INTEGER PRIMARY KEY, account_id INTEGER, status TEXT, amount INTEGER);
INSERT INTO accounts VALUES
(11,'Cedar','West'),(12,'Delta','North'),(13,'Orion','West'),
(14,'Maple','South'),(15,'Nova','West'),(16,'Luna','North');
INSERT INTO payments VALUES
(501,11,'settled',900),(502,11,'pending',300),
(503,12,'failed',1500),(504,13,'settled',NULL),
(505,14,'settled',1800),(506,15,'failed',400),
(507,15,'pending',600);
```

**Required result (ordered):**

| account_id | account_name | region |
|---:|---|---|
| 11 | Cedar | West |
| 12 | Delta | North |
| 13 | Orion | West |
| 15 | Nova | West |
| 16 | Luna | North |

Only Maple has a qualifying payment. Cedar: settled 900 too low; Delta: 1500 but failed; Orion: settled but NULL amount; Nova: failed/pending; Luna: no payments.

## 3. Approach A — Student-led subquery / NOT IN

### Stage A1: Identify *qualifying* account IDs

The first attempt used `status='status' AND amount>=1000`; it yielded zero rows, because the text literal `'status'` wasn't an actual payment status and `>=` was not strictly greater.

The learner independently corrected the inner query to:

```sql
select account_id
from payments
where status='settled' and amount>1000
```

**Actual SQLite output:**

| account_id |
|---:|
| 14 |

It is Maple's settled payment of 1800.

### Stage A2: Exclude the qualifying account IDs from the accounts table

**Student's final original subquery submission, preserved verbatim:**

```sql
select account_id , account_name, region
from accounts 
where account_id  not in (


select account_id
from payments
where status='settled' and amount>1000
)
```

**Actual SQLite returned rows:** Cedar, Delta, Orion, Nova, Luna (IDs 11, 12, 13, 15, 16). This is correct **set membership and row selection** on the sample, and includes Luna because the outer query starts from `accounts`.

**Important qualification:** Without `ORDER BY account_id ASC`, SQL does not *guarantee* the required order, even though SQLite happened to emit those rows ascending. Thus the submitted subquery version met the filtering requirement but not the explicit ordering requirement.

**SQLite reference (assistant-authored, after learner submission):**

```sql
SELECT a.account_id, a.account_name, a.region
FROM accounts AS a
WHERE a.account_id NOT IN (
    SELECT p.account_id
    FROM payments AS p
    WHERE p.status = 'settled'
      AND p.amount > 1000
)
ORDER BY a.account_id ASC;
```

The same form is valid T-SQL. SQL Server execution has not been claimed.

### NOT IN and NULL: an important production caveat

If the subquery could return `NULL` as an `account_id`, `NOT IN` may evaluate to UNKNOWN for otherwise qualifying outer IDs, causing unexpected omissions. On this fixture, the subquery returns only non-NULL ID 14. A `NOT EXISTS` anti-semi-join is often easier to reason about for nullable subquery results. That variant is a future topic, not part of the learner's original submission.

## 4. Approach B — Student-led LEFT JOIN anti-join

### Stage B1: Keep all accounts and JOIN payments

The learner selected accounts as the left table. The first SQL attempt omitted all selected columns and failed: `OperationalError: near "from": syntax error`. After independent correction:

```sql
select accounts.account_id , accounts.account_name, accounts.region
from accounts 
left join payments  on accounts.account_id = payments.account_id
```

**Actual SQLite output:** eight rows, because Cedar and Nova each have two matching payment rows; Luna stays as an unmatched account. Only account columns were selected, so payment NULLs were not visible.

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

### Stage B2: See payment-side columns and multiplicity

The learner added `payments.status, payments.amount`. Now the actual joined data shows two rows for Cedar and Nova, Orion's existing NULL amount and Luna's unmatched NULL status/amount.

| account_id | status | amount |
|---:|---|---:|
| 11 | pending | 300 |
| 11 | settled | 900 |
| 12 | failed | 1500 |
| 13 | settled | NULL |
| 14 | settled | 1800 |
| 15 | failed | 400 |
| 15 | pending | 600 |
| 16 | NULL | NULL |

No `ORDER BY` was present; these rows are shown in the observed display sequence, not a guaranteed ordering.

### Stage B3: Important mistakes — filtering individual *nonqualifying* rows

The learner first attempted:

```sql
where status !='settled' and amount <=1000
```

**Actual SQLite output:** (11, Cedar, pending, 300), (15, Nova, failed, 400), (15, Nova, pending, 600). Delta, Orion and Luna were missing. A single nonqualifying payment does not prove *zero qualifying payments*, and `WHERE` discards NULL-extended unmatched rows when predicates evaluate to UNKNOWN.

Moving the same inverse conditions to `ON` kept all accounts but *still matched the wrong class of payments*. Maple's qualifying payment then looked like a missing match. This is the repeated high-priority conceptual trap: **to find who has NONE of X, first join to X, not to NOT-X**.

### Stage B4: Qualify right-table matches in ON

The learner independently corrected the JOIN to match only settled payments with amount >1000:

```sql
select accounts.account_id , accounts.account_name, accounts.region, payments.status, payments.amount
from accounts 
left join payments  on accounts.account_id = payments.account_id
and status ='settled' and amount >1000
```

**Actual SQLite intermediate output:**

| account_id | account_name | region | status | amount |
|---:|---|---|---|---:|
| 11 | Cedar | West | NULL | NULL |
| 12 | Delta | North | NULL | NULL |
| 13 | Orion | West | NULL | NULL |
| 14 | Maple | South | settled | 1800 |
| 15 | Nova | West | NULL | NULL |
| 16 | Luna | North | NULL | NULL |

**Why:** The entire ON predicate is true only for Maple's 1800 settled payment. Every account survives the LEFT JOIN; a NULL right-side match means no payment satisfied all ON conditions. Orion has an actual payment whose amount is NULL, but that payment does *not* satisfy the qualifying predicate.

### Stage B5: Filter to missing *qualifying* matches using WHERE

The learner initially put `amount IS NULL AND status IS NULL` in ON alongside `amount >1000` and `status='settled'`. The combined predicates cannot all be TRUE, so all six accounts remained as unmatched rows. The learner then moved the NULL checks into WHERE, correctly separating *what matches* from *which joined rows remain*.

**Student's final independently corrected SQLite anti-join solution, preserved verbatim:**

```sql
select accounts.account_id , accounts.account_name, accounts.region
from accounts 
left join payments  on accounts.account_id = payments.account_id
and status ='settled' and amount >1000 where 
amount is null and status is null
order by accounts.account_id  asc
```

**Actual SQLite output:** exactly 5 rows, 3 expected columns and ascending order: Cedar 11, Delta 12, Orion 13, Nova 15, Luna 16. Maple is excluded.

**Why this succeeds:** ON specifies qualifying payment matches; WHERE keeps only accounts whose matching right-side payment columns are NULL. In this fixture, matched rows must have non-NULL `status='settled'` and `amount>1000`, so checking both for NULL identifies lack of a match correctly.

### Robust reference pattern (assistant-verified concept, not student's original code)

A generally clearer NULL test checks the non-nullable right-side payment identifier:

```sql
SELECT a.account_id, a.account_name, a.region
FROM accounts AS a
LEFT JOIN payments AS p
  ON a.account_id = p.account_id
 AND p.status = 'settled'
 AND p.amount > 1000
WHERE p.payment_id IS NULL
ORDER BY a.account_id ASC;
```

This is valid in SQLite and SQL Server/T-SQL. The key needs to be guaranteed non-NULL for real matched rows. No separate SQL Server execution is claimed.

## 5. Generalized rules learned across Q5, Q6 and Q7

1. **ON = which right rows qualify as matches**; **WHERE = which joined rows remain**. This distinction is crucial for outer joins.
2. With **LEFT JOIN**, unmatched left-side entities survive with NULL right-side values. But a NULL-rejecting WHERE condition can remove them.
3. **Anti-join:** Match *qualifying* rows in ON, then detect the **absence** of a qualifying right-side match via `WHERE right.non_nullable_key IS NULL`.
4. Finding **one nonqualifying row** doesn't imply **no qualifying rows** across an entity's entire history. Check the entity-level question.
5. **NULL three-valued logic:** `NULL > 1000` is UNKNOWN, not TRUE. But `IS NULL` tests absence directly.
6. `AND` combines requirements: `status='settled' AND amount>1000`. Test exact thresholds (`>` versus `>=`).
7. One-to-many LEFT JOIN results may repeat left-table fields. Don't confuse row multiplicity with distinct entities.
8. Select only required columns; `ORDER BY` must be explicit when output order is specified. Actual observed sorted output without ORDER BY is not a guarantee.
9. **NOT IN** and **anti-join** may solve similar absence problems but differ in NULL sensitivity; understand assumptions and avoid premature universal claims.
10. Test edge cases: no payments, low settled amount, high failed amount, NULL amount, multiple statuses for an account, multiple qualifying rows, and exact boundary amount.

## 6. Common questions and answers

**Why match qualifying payments first if we want accounts with no qualifying payments?** Because the absence check needs to ask whether X *exists*. First make X the only eligible matching class; then find entities with no X match.

**Does `LEFT JOIN` always return one row per account?** No. If an account has several qualifying right-side rows, it can produce multiple joined rows. If none qualify, one NULL-extended row remains.

**Why could the right-side columns be NULL even when account has payments?** Because the ON predicate may reject all of its payments. A missing **qualifying match** is different from no payment records at all.

**Could `WHERE p.amount IS NULL` be unsafe in other joins?** Yes if a real matched record might have NULL amount. Use a guaranteed non-nullable matched key like `p.payment_id` for a reliable anti-match indicator.

**Where does this help Data Engineers?** Unprocessed events, failed ingestion reconciliation, orders without completed shipping, users without qualifying transactions, or records with no successful downstream counterpart.

## 7. Revision plan and mastery evidence

**Learner's exact new-learning statement** is preserved above. Q7 LEFT JOIN was independently corrected to match all expected output, and is marked *reviewed correct on this fixture*. The original Q7 subquery filtered correctly but omitted `ORDER BY` and should not be marked 100% requirements-complete. Next challenge should interleave this rule with different datasets and edge cases instead of memorizing the Q7 solution.

**Memory cue:** **To find NONE of X, join only X, then test whether the qualifying match is absent.**
