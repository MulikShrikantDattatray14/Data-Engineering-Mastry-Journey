# Bosscoder Python Refresher-1 pending Q02/Q10/Q11/Q12 — bounded semantic audit (2026-11-13)

**Audit classification: PARTIAL, reviewer-only.** This ledger inspects four independently saved, paraphrased assignment statements (not the private original Academy screenshots or authenticated hidden tests). No archived assignment, answer, historical attempt/progress or canonical foundation notes were changed. The checker is separate from any learner solution.

## Individual immutable sources and acceptance contract

| Pending archive | Git blob SHA-1 independently read | Stated domain and samples | Evidence tier |
| --- | --- | --- | --- |
| [Q02 leap year](<../99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/assignments/refresher-1-q02-leap-year.md>) | `12e283590b5a17fe3adfb8ff90e04c7b2444c2f3` | Gregorian integer year **1700–9000** inclusive; 2000→True, 2017→False | Archived statement inspected + synthetic reviewer model; learner Pending |
| [Q10 recursive factorial](<../99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/assignments/refresher-1-q10-factorial-recursion.md>) | `d4c9f2cde6e9b3954bf16a6f6a99a701578167ec` | Explicit recursion, **1–10000** inclusive; 2→2, 5→120 | Archived statement inspected + synthetic reviewer model; learner Pending |
| [Q11 reverse positive integer](<../99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/assignments/refresher-1-q11-reverse-integer.md>) | `a76c70d01531821c6801ac8c20f4f74c8e5c0035` | **1–10000** inclusive; 25→52, 71→17 | Archived statement inspected + synthetic reviewer model; learner Pending |
| [Q12 Armstrong number](<../99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/assignments/refresher-1-q12-armstrong-number.md>) | `4067fa0f0f82b158d7813b3fa64c7c70adea460c` | **1–10000** inclusive; 371→True, 71→False | Archived statement inspected + synthetic reviewer model; learner Pending |

The files retain **original attempt Pending, review Pending, platform verification Unverified, mastery Pending**. The independently read archive hashes are pinned in [the isolated reviewer checker](../scripts/check_bosscoder_refresher_01_pending_semantics.py).

## Independent bounded semantics and counterexample

The checker tests **four** original record identities and six explicit `unittest` methods. It does not execute an Academy-supplied solution or learner answer. It tests **all 7,301** Q02 allowed years against Python stdlib `calendar.isleap` (including century/400 exceptions); **all 10,000** Q11 allowed positive integers against independent text-reversal; and **all 10,000** Q12 allowed positive integers against independent string-digit power-sum. For Q12, the expected 16 positives in the allowed domain are 1–9, 153, 370, 371, 407, 1634, 8208 and 9474. Q10's straightforward recursive reviewer model matches `math.factorial` for **1–200**.

**Material unresolved Q10 acceptance/runtime conflict independently reproduced:** an isolated CPython subprocess with an explicit **1,000** recursion depth limit raises `RecursionError` for a straightforward recursive call on **N=10,000**. In contrast, the mathematical `10000!` is an integer with **35,660 decimal digits** (computed using `math.factorial` with the display-digit limit disabled for the probe). This is an actual environment-dependent size/stack concern in the paraphrased assignment, **not proof the Academy's hidden judge fails**, and not a license to silently change the requested recursive algorithm or stated constraint. Clarification needed on Academy's actual recursion limit, return/output serialization and accepted implementation contract. Python 3.11+ integer-to-decimal string conversion limits can pose an additional platform-dependent issue when printing/displaying such a value; no Academy runner access exists.

**Local standalone verification:** five of the six script test methods ran successfully in a disposable Python runtime, including the exhaustive bound checks and isolated recursion probe. The sixth, source-pin/inventory method, requires the GitHub checkout and was intentionally not counted as a passing local test. **CI on the exact final GitHub commit must establish the full six-test result**. No official answers/grades or new learner independently solved tasks were inferred.

## Still open

- The private Bosscoder platform, original screenshots/PDF, official solution code and hidden grading/format checks are not independently available to repository CI. The present four records are paraphrased summaries rather than authenticated originals.
- The remaining eight Refresher-1 assignments still require comparable independently evidenced contract checks, and source-to-concept parity needs final review.
- This is not a course completion or mastery assessment. Full PNP SQL 205-source parity, Python mentorship, remaining Bosscoder lessons/assignments, W3Schools, runtime Data Engineering, licensing/privacy and full source-to-concept signoff remain outstanding. **Keep Issue #1 OPEN.**
- The separate ChatGPT Library pending learner-study record and later learner work remain **UNSYNCED to GitHub** until full independent audit signoff and separately verified post-sync CI.
