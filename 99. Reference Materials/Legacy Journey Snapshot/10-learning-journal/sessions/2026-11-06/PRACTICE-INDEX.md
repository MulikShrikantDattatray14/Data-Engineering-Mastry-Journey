# November 6, 2026 — Day 1: SQL practice and revision index

**Mission:** Data Engineering / Day 1 / Slot 1. **All entries are tutor-created interactive practice, NOT additional PNP source completions.**  
**Archive:** [Original questions, student queries, reasoning, actual SQLite outputs, revisions and references](slot-01-sql.md).  
**Rules bank:** [General SQL rules SQL-R001–R007](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).

## Progress checkpoint

- **Questions attempted and reviewed:** 8 of 8 tutor-authored foundation diagnostic questions.
- **Independent success after allowed revisions:** 4 (Q1, Q2, Q7, Q8).
- **Correct first attempt:** 1 (Q1).
- **Reviewed, further independent full-query correction needed:** Q3, Q4, Q5, Q6.
- **New PNP source question completions:** 0 verified.
- **Actual focused minutes:** Not recorded. No artificial study-time credit.

## Q1

**Problem:** Paid orders in Maharashtra above 1000, sorted highest amount first.  
**Topics:** SELECT, WHERE, AND, NULL comparisons, ORDER BY.  
**Outcome:** Correct on first independent attempt.  
**New learning:** [SQL-R001 — NULL comparison yields UNKNOWN and WHERE retains TRUE](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).  
**Full question and evidence:** [Q1, learner's original SQLite submission and review](slot-01-sql.md).  
**Expected vs actual and reviewed SQLite/T-SQL references:** [Q1 executed comparison](../../../01-sql/practice/verified-results/2026-11-06-q01-q02.md).

## Q2

**Problem:** Paid Maharashtra orders OR orders amount above 2000, excluding NULL amounts.  
**Topics:** AND/OR precedence, parentheses, NULL, global filters.  
**Outcome:** First attempt wrongly included a NULL-amount order; learner independently corrected SQL and review passed.  
**New learning:** [SQL-R002 — mandatory filter after a grouped OR](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).  
**Full question and evidence:** [Q2 first/revised student queries](slot-01-sql.md).  
**Expected vs actual and reviewed references:** [Q2 execution comparison](../../../01-sql/practice/verified-results/2026-11-06-q01-q02.md).

## Q3

**Problem:** Show every customer and each order, including customers with no orders.  
**Topics:** LEFT JOIN, key matching, one-to-many duplicates, missing matches, ORDER BY.  
**Outcome:** JOIN reasoning correct; first query failed because of `SORT BY` instead of `ORDER BY`. Reviewed reference provided; no independent corrected full query recorded.  
**New learning:** [SQL-R003 — recheck syntax and requirements before submitting](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).  
**Full problem, execution error and references:** [Q3 in the original study archive](slot-01-sql.md).

## Q4

**Problem:** Find paid orders with the corresponding customer's name.  
**Topics:** INNER JOIN, JOIN keys, filtering paid orders, SQL aliases, sorting.  
**Outcome:** JOIN logic right; `0.status` instead of `o.status` caused syntax error. No independent corrected full query recorded.  
**New learning:** [SQL-R003 reinforced — slow down and double-check aliases](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).  
**Full problem, original submission and references:** [Q4 study archive](slot-01-sql.md).

## Q5

**Problem:** Keep every customer while showing only qualifying paid orders.  
**Topics:** LEFT JOIN, filter placement in ON vs WHERE, NULL-extended rows.  
**Outcome:** Original filter placed in WHERE dropped two customers; reviewed reference supplied, without a separately corrected full student query.  
**Important learning:** [SQL-R004 — LEFT JOIN ON vs WHERE with examples](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).  
**Full problem, original query and expected-vs-actual:** [Q5 study archive](slot-01-sql.md).

## Q6

**Problem:** Find customers with zero paid orders, including those with non-paid orders or no orders.  
**Topics:** Anti-join, row-level vs account-level negatives, LEFT JOIN ON, right-side IS NULL, duplicates.  
**Outcome:** INNER JOIN with non-paid predicate gave wrong entities; reviewed, no independent corrected full query. Learner correctly answered an additional join-multiplicity check.  
**Important learning:** [SQL-R005 — fully worked anti-join chapter](../../../01-sql/revision/SQL-R005-ANTI-JOIN-DETAILED-LESSON.md).  
**Actual output after each SQL step:** [Q6 progressive walkthrough](../../../01-sql/practice/verified-results/2026-11-06-q06-walkthrough.md).  
**Original student query and review:** [Q6 study archive](slot-01-sql.md).

## Q7

**Problem:** List accounts having no settled payment exceeding 1000, including no-payment accounts.  
**Topics:** LEFT JOIN anti-join, ON vs WHERE, three-valued NULL logic, NOT IN, subqueries, duplicate matches, precise projection, explicit ordering.  
**Outcome:** Independently corrected LEFT JOIN query returned the exact 5 expected rows, 3 columns, ordered ascending. The separate NOT IN attempt filtered correctly but omitted required ORDER BY.  
**Important new learning:** [SQL-R006 — detailed Q7 anti-join and subquery walkthrough](../../../01-sql/revision/SQL-R006-Q7-ANTI-JOIN-AND-SUBQUERY-DETAILED-LESSON.md).  
**Complete original step-by-step queries and outputs:** [Q7 in full session archive](slot-01-sql.md).  
**Verified question-closing checkpoint:** [Q7-CLOSED](Q7-CLOSED.md).


## Q8

**Problem:** Find vendors with no qualifying delivered amount >1000 when the vendor is West or service is express, including vendors without deliveries.  
**Topics:** LEFT JOIN anti-join; qualifying `ON` predicates; nested AND/OR; NULL handling; one-to-many matching; correct left-side ID projection and ordering.  
**Outcome:** Final learner-authored SQLite query independently corrected and verified: exactly 5 rows, 3 columns and ascending vendor IDs; *not correct on first attempt*. Stepwise intermediate outputs: unfiltered JOIN 10 rows; qualifying LEFT JOIN 8 rows; anti-match 5 rows.  
**Exact learner insight:** `anti join pattern concept`.  
**Full original question and input/output plus original student attempts, executed progressive SQLite review and assistant T-SQL reference:** [Q8 complete record](../../../study-records/2026-11-06/Q8-vendors-without-qualifying-deliveries.md).  
**Revision rule:** [SQL-R007 — Q8 transfer and left-side IDs](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md).  
**PNP credit:** Zero — original tutor diagnostic.

## Next steps

**Q8 independently corrected and verified.** After Q8, the original Slot 1 target also includes reattempting 6–10 previously solved PNP SQL questions; no such new reattempt credit has been verified. Each future date gets the same per-question and per-concept revision links.

**Integrity:** Reviewed is not necessarily correct; a correct reference solution isn't the learner's own solution; a GitHub commit isn't automatically a source assignment or mastered topic.
