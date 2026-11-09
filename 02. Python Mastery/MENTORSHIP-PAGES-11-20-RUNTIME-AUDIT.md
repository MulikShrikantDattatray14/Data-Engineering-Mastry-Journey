# Mentorship Python companion example audit — source PDF pages 11–20

**2026-11-09; evidence tier: original archived companion source individually inspected and runnable check authored.** Each linked code block and printed text was read; checker runs the **original** archived Python snippets, not user submissions. Confirm actual CI results at final commit. Not a full original PDF image/lecture/exercise or mastery signoff.

| PDF page | Archived source lesson | Preserved blob SHA | Linked snippets | Inspected contract |
|---:|---|---|---:|---|
| 11 | [07. Making decisions](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/07.%20Making%20decisions.md) | 2db16f4f3ff4f909bb7b7404cd54556772bf210f | 7 | If/elif, nested checks, match cases and guards (Python >=3.10). |
| 12 | [08. Loops part 1 - for and range](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/08.%20Loops%20part%201%20-%20for%20and%20range.md) | 68150cbef1e85eb81dac8af1d00a927bec7d0ba4 | 7 | for, exclusive range stop, enumerate, iter/next and handled StopIteration. |
| 13 | [09. Loops part 2 - while break continue](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/09.%20Loops%20part%202%20-%20while%20break%20continue.md) | 4f511d8624dac0911d9681d8cd37e6a1a65edb91 | 6 | while, break, continue, retry and loop else. |
| 14 | [10. Lists - ordered collections](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/10.%20Lists%20-%20ordered%20collections.md) | bc2b6ec4ec0b77409570b19044e7ade55a51e961 | 5 | mutation, sorting, slicing and nested lists. |
| 15 | [11. Tuples and sets](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/11.%20Tuples%20and%20sets.md) | 3a2788bfc668b3a1ebe5bfd6f58f8fc8c9bfcb2e | 5 | tuple unpacking, singleton tuple, unique sets, sorted set operations. |
| 16 | [12. Dictionaries - key and value](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/12.%20Dictionaries%20-%20key%20and%20value.md) | 3602334cd9cc779f89eface11b82f844954068a8 | 7 | dictionary order and keys, formatting, aggregation and None. |
| 17 | [13. Which data structure](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/13.%20Which%20data%20structure.md) | 1142a434f0bda23d683eaf2de5176a4c13020438 | 3 | #1 timing is variable; check True/True and output format. #3 unordered set presentation: compare members. |
| 18 | [14. Functions - reusable steps](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/14.%20Functions%20-%20reusable%20steps.md) | cb497c2660c6e3ae34b330f372ef087fa3550d4b | 6 | #4 deliberate NameError; check exception class, not traceback. |
| 19 | [15. Functions part 2 - mini pipeline](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/15.%20Functions%20part%202%20-%20mini%20pipeline.md) | abf9377580230db87cc4632ae933478e89bc4df2 | 6 | #3 and #4 supply definitions for #5: not standalone. #6 '1 orders' grammar issue. |
| 20 | [16. Modules packages and pip](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/16.%20Modules%20packages%20and%20pip.md) | 2002d657a4bb52dcd1e369a9083dfd1d7b5c37eb | 9 | #2/3, #4/5, #7/8 module pairs; #6 scratch-file child process; #1 seeded random. |
| **Total** | **10 independently inspected companion source files** | — | **61** | **61 runtime checks; validate on CI** |

The [runnable source checker](../scripts/check_mentorship_python_pages_11_20.py) asserts contiguous unique linked-snippet IDs and executes each original example in a fresh interpreter with scratch workspace and bounded time. It compares displayed outputs, except documented non-portable behaviors.

## Findings and exceptions

1. **PDF page 17 #1:** timing output is machine-dependent; asserted True/True membership and timing **format**, not a benchmark guarantee. No fixed displayed text is supplied.
2. **Page 17 #3:** original illustrative order of set members is **not guaranteed** by Python. Compare members, not particular set iteration order; this is a source presentation caveat, not a wrong result.
3. **Page 18 #4:** intentional NameError for a function-local variable accessed globally, checked by exception class.
4. **Page 19 #3–5:** the displayed mini-pipeline is deliberately split into rows, parser and summary. #5 is context dependent; test only after both preceding source snippets. #6 emits '1 orders', a grammatical rough edge that does match code.
5. **Page 20 #2–3, #4–5 and #7–8:** example module/import pairs require real temporary source files and working-directory import. **#4 deliberately prints 'running the tool' when executed directly, even though it has no displayed transcript; importing tool.py in #5 must not print.** The first CI checker mistakenly assumed #4 had no output and failed; corrected checker tests both direct-run and import semantics. #6 creates and invokes modules/child Python in a temporary directory; no original archive path is written. #1 seeded-random output is tested in CI.
6. Six source examples lack a fixed printed transcript because they declare definitions, or print live timings. Never invent an official result for an absent transcript.

## Evidence boundary and follow-up

Only 61 **source-linked companion snippets** across original PDF pages 11–20 are covered by this checker; together with [pages 5–10](MENTORSHIP-PAGES-05-10-RUNTIME-AUDIT.md), there are **109 linked examples across pages 5–20**, *subject to actual CI results*. This does **not** establish original PDF page-image signoff, any unlinked exercise/graded Bosscoder assignment, W3Schools official lesson validation or learner-independent completion.

Still open: mentorship pages 21–80 runtime examples and page-level checking, Bosscoder SQL/Python lectures and exercises, all 205 original SQL answer/dataset validations where available, W3Schools, DE-domain sources, integrity/licensing and final source-to-concept audit. Issue #1 stays open; no learner progress GitHub sync before full independent signoff and green latest-head CI.
