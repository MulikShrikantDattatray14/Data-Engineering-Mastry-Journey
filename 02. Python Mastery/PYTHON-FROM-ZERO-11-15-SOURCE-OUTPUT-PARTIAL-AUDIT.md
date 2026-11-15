# Original Python-from-Zero lessons 11–15: independent source/output audit (PARTIAL)

15 November 2026. Independently opened the five untouched original Python-from-Zero Markdown companion sources attributed to *Python for Data Engineering Notes*, original PDF pages 15–19. **This is not visual verification of the PDF.** Previously indexed and partly checked material is not credited as newly mastered.

| Archived lesson | Source Git blob SHA-1 | Python/output fences | Inspected semantics |
|---|---|---:|---|
| 11. Tuples and sets, p15 | 3a2788bfc668b3a1ebe5bfd6f58f8fc8c9bfcb2e | 5 / 5 | Unpacking, set operations, hashability |
| 12. Dictionaries, p16 | 3602334cd9cc779f89eface11b82f844954068a8 | 7 / 7 | CRUD, get, None, grouping, insertion order |
| 13. Which data structure, p17 | 1142a434f0bda23d683eaf2de5176a4c13020438 | 3 / 2 | Benchmark, order-preserving dedup, unordered set display |
| 14. Functions, p18 | cb497c2660c6e3ae34b330f372ef087fa3550d4b | 6 / 6 | Defaults, return, local scope, deliberate NameError |
| 15. Mini pipeline, p19 | abf9377580230db87cc4632ae933478e89bc4df2 | 6 / 4 | Parse/filter/summarize, sort key, varargs, dirty data |

**Read-only executable reviewer:** [scripts/check_python_from_zero_lessons_11_15_source_contracts.py](../scripts/check_python_from_zero_lessons_11_15_source_contracts.py). Verifies all five pinned original Git blobs, 27 source Python fences, 24 source output fences, **22 deterministic archived printout cases** (11:5; 12:7; 13:1; 14:5; 15:4), the **one intentionally failing NameError**, and the **two variable-output original examples** (benchmark numbers, unordered set display). Some original intermediate pipeline blocks are definitions and are replayed together; they are not independently printed results. Also tests 243 reviewer-created status combinations against a separate count/sum oracle plus tuple, dictionary, set, zip, monetary and dirty-data boundaries.

**Source-specific findings:** The original benchmark reports one hardware-specific sample timing, not a universal performance guarantee. Original set list/print order is intentionally unpredictable. Original NameError is an expected instructional error, not a defective lesson. Original mini-pipeline has no explicit invalid monetary input exception policy; float NaN is admitted, duplicate order IDs are counted twice and binary floats are not an authenticated monetary accounting policy. The source's plural string says '1 orders' for a one-item call; verification replays it without silently correcting archived content.

**Evidence tiers:** Indexed = yes, already covered. Statement inspected = all five companions. Published code/output replay = only when named CI test logs pass. Synthetic test passed = reviewer-only once CI proves it. Original PDF rendered = no. Official authenticated answer verified = **0 new**. Learner independently solved = **0 new**. Mastery = **0**. Companion W3School examples do not authenticate hosted W3 editor answers or course grade reports.

**Unresolved blockers:** Source PDF pages 15–19 not rendered from binary (earlier GitHub connector binary retrieval failed), original provider keys/grades and live datasets not verified, remaining PNP 205 SQL original/output checks, further Python/Bosscoder/W3/DE material, global source-to-concept integrity and redistribution rights / privacy review. PNP conservative verified supplier-key replay remains **94/205**. Issue #1 stays OPEN.

**Preservation:** Only auditor-owned new checker, ledger, validation workflow and additive MIGRATION-STATUS text are within scope; no preserved archive, learner attempt/progress or canonical foundation editing. ChatGPT Library learning record /Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md and later study remain UNSYNCED with GitHub until completed independent audit signoff and separate post-sync CI.

## CI signoff

Final exact-current-main GitHub Actions jobs, all named reviewer methods and Git history preservation comparison require independent inspection; a preexisting passing CI run cannot establish new checker success.
