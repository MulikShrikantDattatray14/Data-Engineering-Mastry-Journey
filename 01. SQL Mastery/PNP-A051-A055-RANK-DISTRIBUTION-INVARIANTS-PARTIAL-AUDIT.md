# PNP Advanced A051–A055 — source-pinned rank/distribution invariants (15 November 2026)

**PARTIAL INDEPENDENT AUDIT — NOT FINAL SOURCE/PDF OR OFFICIAL-KEY SIGNOFF.** Reopened five *already indexed and previously statement-inspected* Advanced PNP original archived question files (Advanced SQL 100 Query Questions Vol. 1, PDF p.11, stated upstream dialect MySQL 8). This work creates **no newly counted question IDs**. All five original records still display NOT SOLVED YET, both learner solution fields Pending, and official solution Pending. Their displayed samples are explicitly **archive-authored illustrations**, not independently authenticated provider PDF rows, supplier SQL, learner submissions, or grades.

## Exact sources

All five originals are under: 99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/9. Windowing Functions/.

| ID | Original Git blob SHA | Reopened requirement and newly reviewed policy |
|---|---|---|
| A051 | 2593dee4fa58352b31442c2a49bdcb149fd30010 | ROW_NUMBER, RANK, DENSE_RANK: salary peers share RANK/DENSE_RANK despite deterministic emp_id tie-breaking for row numbers. Adding emp_id to RANK's window ordering destroys salary-peer groups. |
| A052 | 1580cbe5bd7a7de498021483be39e67e49c5da72 | Rank salary within each department, independently restarting per department, including rank gaps. SQLite partitions all NULL dept_id rows together; provider policy unresolved. |
| A053 | 2415e2fb39c673626f3fc803d37d6964703ca6ac | Highest salary per department with earliest hire tie-break. Reviewer adds emp_id for same-day ties. SQLite sorts NULL hire dates before actual dates when ascending; policy unknown. |
| A054 | aee8087b885167e552415ab48df1c9aaa9e1d84c | Ascending PERCENT_RANK: percentile position is (RANK - 1)/(N - 1) for N > 1. A singleton or all-peer group yields zero. |
| A055 | 8c8c4d7ead577f786ab77919f6c04bc0798a7344 | Ascending CUME_DIST includes all equal-salary peers at or below salary; singleton and all-peers return one, unlike PERCENT_RANK. |

## Verification design and semantic findings

The new [read-only verifier](../scripts/check_pnp_advanced_51_55_rank_distribution_invariants.py) defines **16 unittest checks**: one rechecks all five original blob hashes, identifiers, PDF page references and unchanged Pending history; four retype the source-author's A051–A055 illustrated outputs (five separate source illustrations); and an independent arithmetic/set-count Python oracle checks **1,296 four-person input combinations**, comprising 81 salary sequences × 16 department sequences. Reviewer-authored SQLite SQL for ROW_NUMBER, RANK, DENSE_RANK, per-department RANK, PERCENT_RANK and CUME_DIST must agree with the oracle. Other tests distinguish singleton and all-peer distributions, NULL dept and salary policies, erroneous rank tie-breaks, CUME_DIST versus ROWS-based running counts, and A053 NULL hire/duplicate-date choices.

**New bounded counterexamples:** adding emp_id inside RANK's ORDER BY incorrectly separates salary peers; CUME_DIST is not row-count-so-far divided by N when ties exist; leaving NULL salaries in the distribution alters PERCENT_RANK and CUME_DIST denominators; SQLite's ascending NULL hire date precedes valid hire dates, which can choose a missing-date employee over a genuinely earliest known hire. These are **reviewer SQL findings**, not provider-grader failures or learner completions.

## Evidence levels, preservation and blockers

- **Indexed:** already known for all five, not incremented.
- **Statement inspected:** these five original archives reopened, blob-pinned; no newly unique question IDs.
- **Synthetic test passed:** only after this checker and named results are independently confirmed in a matching-head GitHub Actions job log; test design alone is not CI evidence.
- **Official answer verified:** zero new; original supplier MySQL SQL, native MySQL 8 execution, authenticated dataset and original rendered PDF p.11 parity remain unchecked.
- **Learner independently solved:** zero new; original Pending records unchanged. **Mastery:** zero new.

This repeats neither earlier per-question fixture credit nor the conservative PNP supplied-key replay tally, which remains **94/205**. Full 205 original semantics and vendor/official output parity, further Python/Bosscoder/W3Schools/DE material, licensing/privacy clearance and source-to-concept signoff are incomplete. Preserve all original archive files, historical learner attempts/progress and canonical foundation notes. **Issue #1 stays OPEN.** ChatGPT Library pending learner-study record /Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md and later practice remain **UNSYNCED with GitHub**, gated on full independent audit signoff and separate post-sync CI.
