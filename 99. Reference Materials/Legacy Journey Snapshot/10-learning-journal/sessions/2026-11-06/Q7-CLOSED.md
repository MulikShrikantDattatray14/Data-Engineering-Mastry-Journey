# Q7 — Question-closing GitHub checkpoint

**Date:** 2026-11-06 (Asia/Kolkata)  
**Status:** Reviewed and closed for transition to Q8. Q7 is tutor-authored practice, not a PNP question.  
**Primary dialect:** SQLite; **secondary reference dialect:** SQL Server / T-SQL (not separately executed).

## Two approaches and honest outcome

| Approach | Learner-authored outcome | Review status |
|---|---|---|
| Subquery using NOT IN | Inner query corrected and returned 14; outer query returned exactly the expected five account IDs and columns, but omitted required ORDER BY | **Filtering correct; sorting requirement not guaranteed** |
| LEFT JOIN anti-join | Built progressively, corrected ON/WHERE logic, revised final projection and added ORDER BY | **Final corrected SQLite query met all requirements** (5 expected rows, 3 columns, ascending) |

## Archived evidence

- [Full Q7 original student thinking, SQL revisions, output/error reviews and final queries](slot-01-sql.md)
- [Q7 progressive lesson: NOT IN, LEFT JOIN, actual intermediate SQLite results and general anti-join rules](../../../01-sql/revision/SQL-R006-Q7-ANTI-JOIN-AND-SUBQUERY-DETAILED-LESSON.md)
- [Learning rules bank (SQL-R001–SQL-R006)](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md)
- [Earlier Q6 anti-join fundamentals](../../../01-sql/revision/SQL-R005-ANTI-JOIN-DETAILED-LESSON.md)

## Learner-confirmed new learning (verbatim)

```text
anti join pattern was a importnant and new concept for me ..so save all those concept notes that were taught me here
```

**High-priority generalized learning:** For an anti-join, match **qualifying** rows in ON, then select left rows missing a qualifying match with WHERE on a non-nullable right-side key IS NULL. Do not mistake a nonqualifying individual payment for proof that no qualifying payment exists. Distinguish RIGHT-side NULLs caused by no qualifying match from NULL data in an actual source row. Other Q7 lessons: NOT IN with nullable subquery results, explicit output columns, mandatory ORDER BY, one-to-many row duplication, validating actual output.

## Scope and integrity

- **Question-closing commit:** This file records Q7's reviewed final state, created after saving the full lesson, revision-bank entry and dated slot record.
- **Mastery:** Not automatically marked mastered; independently corrected final anti-join succeeded on one fixture. Future mixed practice needed.
- **PNP progress:** No new PNP question ID credited.
- **Q8:** Not yet started. Proceed only after remote verification of this commit.

The GitHub connector commits this content **directly to the remote default branch**. There is no separate local unpushed commit.
