# Python mentorship Foundations lessons 01–05 — original code/output and data contract audit (PARTIAL)

**15 November 2026.** Independently reopened the five immutable **original Mastery archive companion Markdown lessons**, their explicitly printed output blocks and the source 15-order CSV. These are Part 2 lessons, cross-referenced by the companions to *Python for Data Engineering Notes* PDF pages **25–29**. The PDF **rendered original pages have not been independently opened**, so no PDF visual parity or provider-solution/grade claim follows from these companions.

| Companion source (PDF page attribution) | Original Git blob SHA | Archived original Python code/output blocks | Scope |
|---|---|---:|---|
| 01. Six-step coding-question approach (25) | `2a176fd611ed9ec50dc8873927b56c349be0651a` | 3 | Delivered totals by customer, 15-row supplied CSV with Decimal sorting and separate function example |
| 02. Names, objects, mutability (26) | `0e8557654df4677b9bd58c05921b7338cd336203` | 4 | Equality vs identity, shared mutable default arguments, deep/shallow copy and integer rebinding |
| 03. Numbers, strings, dates (27) | `91de7da6ba563322381b46dce78a2ebcb2ce7e61` | 4 | Decimal vs binary float, negative floor/truncation, UTF-8 and normalized strings, India-local aware dates |
| 04. Lists, tuples, sets, Big-O (28) | `15e912de271e31108a3fabf7e0abab63ff522f3d` | 3 | Sorted/sort, keyed row sorting, set reconciliation, hashable tuples |
| 05. Dictionaries, defaultdict, Counter (29) | `7d372ee509f2e539c8cfa0c8bdcc87a50909edce` | 5 | Existing-None vs missing dictionary keys, grouping, counting, dictionary union and insertion order |

The linked archived CSV `python_de_dataset/orders.csv` is independently pinned to Git blob `2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2`. Direct source inspection shows 15 rows: 12 delivered, 2 cancelled, 1 returned. All the source printed outputs are **companion-published examples**, not answers authenticated against the original PDF renderer, and not exercises newly solved by the learner.

## Independent evidence method

- [Read-only Python checker](../scripts/check_python_foundations_01_05_source_examples.py) hashes all five immutable archived Markdown files and source CSV, verifies page number attributions, and pairs all **19 original literal `~~~python` examples** with each successive printed `~~~text` output, running each example in an isolated temporary directory with original CSV copied in **without modifying the archive**.
- 20 named unittest methods include five page-level archived literal code/output replay groups, full 15-row Decimal CSV oracle, shared mutable defaults, copy aliasing, rounding, negative integer division, UTF-8/CSV delimiter handling, timezone and naive/aware date guards, sort stability, hashability, dictionary lookup and insertion-order duplicate-key behavior, and **243** synthetic status-sequence combinations against a separately calculated brute-force group-total oracle. Test counts are **method counts**, not newly audited official questions.
- Semantic limitations to preserve: companion `row.get('city', 'Unknown')` does not replace a stored `None`; dict comprehension silently keeps the last duplicate customer ID; temporary date `replace(tzinfo=...)` is an assertion of source clock region, not proof a clock was already in that region; `round` versus `Decimal` business rounding; CSV row values not guaranteed numeric/clean; delivered status normalization/negative refunds; large-file streaming and source data versioning. These are reviewer observations, not proof of defects in authenticated provider keys.
- **Status tiers:** *indexed* already; five Markdown *statements and examples inspected directly* in this audit; *synthetic tests passed* ONLY after independent named-method CI log inspection; *original PDF visually checked*: no; *official provider answers verified*: zero new; *learner independently solved*: zero new; *mastery*: zero.
- Remaining global blockers: original PDF binary rendered pages 25–29 and full source-parity; authenticated graded answers and provider datasets; all 205 PNP SQL supplied-answer/parity (conservative **94/205** verified remains unchanged); remaining Python, Bosscoder, W3Schools and other DE, source-to-concept completeness, public licensing and binary privacy review. Issue #1 **must stay OPEN**.
- The separate ChatGPT Library learner-study record and subsequent interactive practice remain **UNSYNCED with GitHub** pending full independent audit signoff, then separate post-audit learning-note synchronization and its own CI.

## CI status

The new reviewer was committed as `0cc469120ee555255a4d86604ad105e3ddf16d66`; CI integration at `6b2694468de0ecfaf499344333e9979a398b89eb` started [Actions run 43705100520](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43705100520). **Do not mark any of its 20 tests as PASS until the named CI methods actually complete**. Any first-run failures must be disclosed and attributed to the tested code or reviewer as evidence shows, without modifying original archives.

## Independently verified first reviewer-enabled CI

[Actions run 43705100520](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43705100520) **completed SUCCESS** for exact workflow-head `6b2694468de0ecfaf499344333e9979a398b89eb`. Decoded actual validation job `132784380991`: all **20 individually named PreservedFiveLessons methods** displayed `... ok`, `Ran 20 tests in 0.196s`, `OK`. The five source-page methods collectively executed **all 19 untouched archived code snippets** and matched their respective archived printed output blocks, including the 15-row CSV-backed sample. Separate native PostgreSQL **18/18** and MySQL **9/9** job steps passed; full general validation **145/145** steps passed, without failures/skips. This is Markdown companion output parity, **not** original PDF rendered parity, provider grading or learner work.

This appended documentation itself produces a new SHA and requires an independent final **exact-head** CI check. The original five companion source blobs, historical learner records and canonical foundation notes were not modified.
