# PNP Q001–Q008: preserved supplied-key provenance and bounded result audit

**Date:** 11 November 2026. **Scope:** Eight original archived Q001–Q008 Markdown records, **unchanged saved learner SQL**, and the separate archived `Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql` (PostgreSQL 16). The latter is a *supplied answer-key archive*, **not independently authenticated live official grading**. The Markdown sample rows explicitly say **illustrative**, not original provider PDF/data-load output.

## Independent source and evidence ledger

The [read-only regression script](../scripts/check_pnp_first_eight_source_answers.py) pins **eight original Git blob hashes**, plus supplied-key blob `7912c8e676621c513e0b635a40c6ee299404676e`. For each question it checks that the exact SQL excerpt in the preserved **Official solution** section matches the archived answer-key SQL (whitespace-normalized only), extracts the untouched **My solution — SQLite** query, and compares its actual SQLite result against independently transcribed illustrative input and output tuples. The script adds eight *separate auditor-created* edge datasets, not misdescribed as provider inputs.

| ID | Original blob SHA-1 | Independently tested contract | Supplied-key / limitation |
|---|---|---|---|
| P001 | `6daaa2d1453dbaaf28ff43278d45ea0a339b3601` | Blank/NULL brands removed, trim + dedupe + sort; independently synthetic whitespace variants | **Confirmed key/source-contract discrepancy:** archived key filters `TRIM(p.Brand)` but **selects and DISTINCTs raw `p.Brand`**. Source illustrative `'Nike'` and `' Nike '` produce **two** key rows, while requested cleaned directory has one. This is an official-*key archive* bug/ambiguity, **not a passing sample check**. Source and key retained. |
| P002 | `2c33c20b483675b6b73cec8da609b89e391af09d` | 10 fixed slots, exclude NULL (retain zero), deterministic ID tie boundary; synthetic 12-way tie | Exact original SQLite learner and archived supplied-key SQLite-compatible queries agree on bounded fixtures. |
| P003 | `2260186b5eb5dba4b6eeb9d9bbe6cf4c4a3ffa76` | Alternate metro spellings, case/whitespace normalization, retained display capitalization | Archived key sorts by raw-case `TRIM(City)`, while saved learner sort is `LOWER(TRIM(City))`; synthetic mixed-case result order differs (`BENGALURU` vs `Bangalore`). **Case/collation order policy requires clarification**; no official provider run. |
| P004 | `a79ad97c4bc4417a3c24ae094bf37218a7570cb3` | NULL/blank, embedded spaces, shape check and CASE issue precedence; valid address excluded | Archived pattern is **basic shape only**, not RFC email validation. Saved query and supplied-key query agree on checked fixtures. |
| P005 | `ebebd5c3755712ab9ff69676269eb69be574578f` | Inclusive Jan-1/exclusive Apr-1, exact datetime boundaries, final ordered output | Supplied key uses PostgreSQL `DATE '...'` syntax; **translated** literal spelling for SQLite diagnostic only. No original PostgreSQL execution or full dataset assertion. |
| P006 | `777dcceccf731128d314c4dbdb7905c0369c8d6c` | Full price including zero, exclude missing prices and actual discounts, stable top-N | Supplied key uses PostgreSQL `::text`; **translated** cast for SQLite diagnostic only. No original PostgreSQL execution. |
| P007 | `da19af9f18ffb044c2ef52e7329dceff740e0e81` | Zero/NULL MRP → two NULL metrics; negative discount stays negative; descending percentage | Supplied key adds ProductID tie break but saved learner only sorts percentage: **equal-percentage tie order is not guaranteed** by saved SQL. SQLite numeric display `20.0` does not imply two-decimal text formatting. |
| P008 | `a7821e2ffaa2dca14311e87f2faa042350ad3705` | `199.99`, `200`, `699.50`, `700`, NULL, negative price | Saved CASE and supplied-key CASE label these bounded inputs identically. Negative price handling follows source thresholds; no data-validation policy inferred. |

## Evidence tiers; do not combine these counts

- **Indexed:** 8/8, already part of the full 205-question index.
- **Original statement and preserved saved query inspected:** 8/8; source archive and historical learner status remain unchanged (`Solved (recorded)` means historical evidence, **not new independent learner work**).
- **Source illustrative fixtures replayed:** 8/8 archived *saved learner SQLite queries* compared against **eight manually transcribed illustrative expected outputs**. This tests saved code on bounded examples, **not all original PDF/Dataset v2 rows**.
- **Supplied-key excerpt provenance:** 8/8 Markdown excerpts match the separately archived PostgreSQL key, based on pinned copies. **0 live-provider-verified grades**.
- **Supplied-key sample comparison:** 7/8 outputs agree under bounded SQLite diagnostics; **Q001 fails** because raw-brand distinction contradicts the illustrative cleaned output. Two of the seven (Q005, Q006) required *explicit PostgreSQL-to-SQLite syntax translations*, not native PostgreSQL execution.
- **Independent synthetic edge groups:** 8 (one per ID), distinct from the eight illustrative source fixtures. Key Q003 ordering difference is reproduced. **Zero new learner attempts, solves, grades or mastery** claimed.

## Reconciliation and pending gates

These eight records have previously appeared in the index and in source-specific semantic audits; this adds an **independent supplied-key provenance fence and exact unchanged-query illustrative-output replays**, rather than counting them as newly discovered questions. Q001's discrepancy is a concrete example of why merely finding the supplied answer key does not certify semantic correctness. P003 mixed-case sorting and P007 equal-percentage ties require source policy/provider clarification; do not edit official keys or previous learner attempts without permission.

**Still open:** original PostgreSQL 16 execution against the provided full dataset; independent verification of all original provider outputs and official keys for other PNP IDs; PDF question-by-question rendered text parity; Bosscoder provider grading/notebook state; remaining mentorship PDF/lecture details; W3Schools concept comparisons; real data-engineering runtimes; legal/privacy/redistribution checks; complete source-to-concept signoff. This *bounded checker* must pass on the **exact final repository HEAD** in GitHub Actions; successful scoped CI is not full audit signoff. Keep Issue #1 open and **defer all ChatGPT Library learning-sync edits until the full independently evidenced audit passes**.
