# Day 1 · Slot 1 — Remote GitHub checkpoint before Q7

**Date:** 2026-11-06 · **Study dialect:** SQLite (student) + SQL Server / T-SQL (assistant references)  
**Checkpoint:** Q1–Q6 reviewed and archived. Q7 is **not started**, and its answers are not included.  
**GitHub write method:** The connected GitHub API creates commits directly on the remote default branch; these are already published commits, not unpushed local working-tree changes.

## Material verified available in this repository

- [Full chronological Slot 1 archive](slot-01-sql.md): Q1–Q6 original SQLite submissions and reasoning, reviews, reference query comparisons, learner-confirmed insights, Q6 follow-up answer, and the planned but unanswered Q7.
- [SQL learning bank](../../../01-sql/revision/LEARNED-RULES-AND-SYNTAX.md): five substantive cumulative learning rules (SQL-R001 through SQL-R005), including reinforced submission discipline and high-priority outer joins/anti-joins.
- [Detailed anti-join tutorial](../../../01-sql/revision/SQL-R005-ANTI-JOIN-DETAILED-LESSON.md): Q6 progressive working example, row counts, match behavior, edge cases, and use cases.
- [Q1–Q2 comparison and reference solution archive](../../../01-sql/practice/verified-results/2026-11-06-q01-q02.md).
- [Q6 progressive output walkthrough](../../../01-sql/practice/verified-results/2026-11-06-q06-walkthrough.md).
- [Session archive policy](../../SESSION-ARCHIVE-POLICY.md): exact original attempts, independently run SQLite comparisons when possible, tutor references vs official keys, optional new-learning capture, and student-led incremental Q7 onward.

## Honest question status

| Question | First attempt | Review outcome | Independent correction or concept evidence |
|---|---|---|---|
| Q1 | Correct SQL | Reviewed correct | Yes: independently correct query |
| Q2 | Incorrect NULL edge case | Reviewed and corrected | Yes: submitted independently revised SQL |
| Q3 | Invalid `SORT BY` syntax | Reviewed; reference provided | No independently revised final query recorded |
| Q4 | Invalid `0.status` token | Reviewed; reference provided | No independently revised final query recorded |
| Q5 | LEFT JOIN right-side WHERE filter loses rows | Reviewed; reference provided | No independently revised final query recorded |
| Q6 | INNER JOIN on non-paid rows is not an anti-match | Reviewed; reference provided | Correct oral check on multiple qualifying matches; no independently revised full SQL recorded |

**PNP practice source IDs newly completed this session:** 0 verified.  
**Actual focused minutes:** Not recorded.  
**Q7:** A fresh payments anti-match challenge; learner will explain and code one intermediate SQLite step at a time, inspect actual output, and submit the complete answer only at the end.

## Commit/push rule from now onward

When a question has been reviewed, learner learning captured or skipped, and its evidence recorded, make a **closing GitHub commit** before introducing the next problem. The closing commit message should mention the question number and whether it was correctly solved or only reviewed. The GitHub API commits directly to the remote repository, so a successful API write is already published; there is no separate local push. Don't mark a question mastered because its reference answer was published.

**Scope:** Only `MulikShrikantDattatray14/data-engineering-journey` is edited. The PNP source repo `Data-Engineering-Mastry` remains untouched.
