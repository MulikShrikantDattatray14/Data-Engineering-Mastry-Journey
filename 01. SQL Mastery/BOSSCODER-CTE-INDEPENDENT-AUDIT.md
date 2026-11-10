# Bosscoder SQL — CTE tranche: independent archive and SQLite replay audit

**Scope:** 11 November 2026 (India), 12 original archived Bosscoder SQL CTE Markdown questions. This ledger examines preserved source statements and historical recorded answers. **It does not grant a new learner solve, Academy grade, official answer equivalence, or source-provider permission.**

## Evidence and immutable source

Read all 12 originals under `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/5. CTEs/`. Git blob SHA-1 values in `scripts/check_bosscoder_sql_cte_answers.py` are asserted against the exact *bytes* before replay. Each replay loads the **first original archived SQLite solution fence** verbatim; it does not execute a newly authored surrogate query. The two still-unsolved records are checked as immutable pending statements only.

| # | Archived problem | Source Git blob SHA-1 | Source-specific contract independently inspected | Test tier / limitation |
| ---: | --- | --- | --- | --- |
| 01 | Queries Quality And Percentage | `a5ee7282960fbb86c654d4a89b46540d1bb12d44` | Average `rating/position`, duplicates count, percentage rating <3, two-decimal rounding and ascending name | Displayed sample + duplicate-weighting synthetic replay; **nullable `query_name` divergence** below |
| 02 | Percentage Of Users Attended A Contest | `0fd1561811bb1c7f77a61367ff4b14e5ef5e6ec2` | Global Users denominator, registration numerator, descending percent/ascending ID tie order | Displayed sample + percentage tie and partial-registration synthetic; join presumes registrations refer to real users |
| 03 | Confirmation Rate | `8ccedc146de91260e81309e1045a712d04c88e46` | All signups, confirmed/total requested, zero for no confirmation requests, ordered IDs | Displayed sample + zero/one-third/all-approved synthetic |
| 04 | Students And Examinations | `76bbaab89933fb374e2dfbd9db25838d90ab8fef` | Cartesian Student × Subject, duplicate attendance counted, missing exams count zero, ID/name/subject grain | Displayed 12-row example + duplicate-and-unattended six-row synthetic |
| 05 | Find Immediate Delivery II | `c5013d78468d75f7f7b8ff32530bc8fdd9e3b13b` | Unique first order per customer is **explicitly guaranteed**; preferred date = order date; customer denominator | Displayed 50% sample + 33.33% first-order-only synthetic |
| 06 | Customers Who Bought A And B But Not C | `90724715a11e01dcb4611c2dff172bdef3e7dc23` | A and B required, C excluded, duplicates tolerated, no orders excluded, ascending customer ID | Displayed sample + multiple A, C and missing-product synthetic |
| 07 | Team Total In Football Tournaments | `52dc34fd6aaaf1f4d4ad753474d7a37fc7e9b5e8` | Three/win, one/draw, zero/loss, both sides of matches, teams with no matches, tie by ID | Displayed sample + synthetic loss/draw/idle-team replay |
| 08 | Evaluate Boolean Expressions | `6f999394e9e55a10503716d19daf6065066fb9e4` | Both operand-key joins, 3 allowed operators, textual true/false; input expressions are unique | Displayed sample + negative/zero/equality synthetic; result row order **not requested** |
| 09 | Number Of Calls Between Two Persons | `8dda1a83b87f6bbaf640f6ba809902af59467f48` | Undirected pair `person1 < person2`, counts duplicates, sums both call directions | Displayed duplicate-row sample + reverse-call/duplicate synthetic; result row order **not requested** |
| 10 | Countries Where You Can Safely Invest In | `f325cdb01a66b2c73d1df0cbd091c3042786e298` | Phone-prefix country mapping retains leading zeros; call counted once at each endpoint; country mean strictly greater than global mean | Displayed Peru sample + within/across-country synthetic; no asserted output order |
| 11 | Find The Quiet Students In All Exams | `33bcc994e5900bdca9c407ab3545e7e337c5f2db` | Must take an exam; must never be highest **or** lowest in any exam; tied extrema count; single-student exam is extreme | **Statement inspected, immutable pending record checked. No archived solution or replay, and no Academy grade.** |
| 12 | Report Contiguous Dates | `e22b6a934769222df8458e7b2ed80ecce6b133fc` | 2019 date bounds; coalesce **consecutive** same-state days; 2018 sample days excluded; ordered interval starts | **Statement inspected, immutable pending record checked. No archived solution or replay, and no Academy grade.** |

**Provenance:** All 10 historical solved items carry *Solved (recorded)/UNRATED*. Each of those ten original `## Official solution` sections explicitly says **“Not provided for this practice set.”** The original two pending records remain *NOT SOLVED YET/UNRATED*, with pending solution and pending official-answer placeholders. Neither the original source files nor the status metadata were modified.

## Executable evidence and failure boundary

`scripts/check_bosscoder_sql_cte_answers.py` independently reconstructs the **10 source-displayed input/output samples** (full table rows, not merely expected numbers), and authors **10 different synthetic boundary fixtures**. SQLite directly executes the **unchanged preserved first historical SQLite SQL fence** for each of the 20 comparisons. Table rows are compared either in the statement's required order or as unordered row collections where sorting was not specified. These local execution results are distinct from an original LeetCode/Academy grader, hidden datasets, SQL Server runtime, or all possible edge cases.

**Known counterexample (01):** The original #01 question lists `query_name` as `varchar` but does **not explicitly forbid NULL**. A single `Queries(query_name=NULL, result='x', position=1, rating=5)` creates a NULL group in both aggregate CTEs; their final `INNER JOIN ... ON Quality.query_name = Poor_quality_percentage.query_name` discards the group because `NULL = NULL` is unknown. Observed preserved query output: **no rows**, whereas group-preserving expected semantics would return **(NULL, 5.0, 0.0)**. The checker positively asserts the observed discrepancy **as a divergence, never as PASS**. If original provider assumptions implicitly disallow NULL names, resolving the contract requires authoritative confirmation; do not silently rewrite the historical learner query.

**Source/dialect boundaries:** #02 joins `Register` to `Users`, and the original source does not explicitly declare `Register.user_id` a foreign key. It excludes orphan registration rows rather than treating them as valid registrations; whether those are allowed is not independently resolved. #05 relies legitimately on an explicit unique-first-order guarantee. #10's SQL uses a disjunctive endpoint join: a call entirely inside one country appears twice in the local mean (one per participant), as required by the displayed explanation; SQL Server portability and integer/text-affinity corner cases remain untested. No original Academy hidden test, official key, or platform grade was available for any of the 12.

## Boundaries and audit gate

- **Indexed:** 12/12 files present; existing group inventory retained.
- **Statement inspected:** 12/12 individual questions, schemas, inputs, expected displayed outputs and saved statuses independently read.
- **Historical solution executed against retyped source output / synthetic fixtures:** 10/10 historical queries each on both fixture tiers, subject to **one separate known nullable-name divergence**.
- **Official answer/provider grading verified:** 0/12.
- **New independent learner solutions/mastery:** 0/12; #11/#12 expressly remain pending.
- **Untouched:** Original 744-source archive, old Journey attempts, canonical foundations, current learning progress, private PDFs.
- **Still pending at repository scale:** Exact original Python mentorship PDF visual and graded parity, remaining Bosscoder SQL source groups, W3Schools-provider comparisons, PNP 205 official answer/dataset/dialect outputs, private Academy notebook/grades, real DE cloud/Spark/orchestration execution, end-to-end source-to-concept/visual-code coverage, privacy and licensing approval and final independent sign-off.

**Learning-sync gate:** The separate ChatGPT Library study evidence (beginning `/Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md`) remains **UNSYNCED**; no interactive-study content was edited in GitHub. Full audit sign-off and *exact final-head* green CI are prerequisites, not met by this tranche alone.
