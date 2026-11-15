# Bosscoder Python Refresher-2 — original lecture examples and pending-assignment contracts (PARTIAL)

**Review date:** 15 November 2026. **Scope:** the *preserved user-summarized GitHub Markdown companions*, not the originally shared 11-page Academy PDF/screenshots, which were not independently accessible in this run. This evidence does not imply any graded assignment was completed or checked by the Academy.

## Exact independent sources

| Preserved original source | Git blob SHA-1 | What was directly inspected |
| --- | --- | --- |
| `lecture-02/01-patterns-and-nested-loops.md` | `0cdb98ea14fb53ee0dcc0fbe20e810d3de178bbe` | Full chapter; five actual Python example fences |
| `lecture-02/02-lists-and-strings.md` | `fb88fbd9bfa142fca6fc48b03638c21b5fa307fa` | Full chapter; four actual Python example fences |
| `lecture-02/03-tuples-sets-dictionaries.md` | `0177eb35b9a3c8440407e9da17fd913185e227ff` | Full chapter; four actual Python example fences |
| `lecture-02/assignments/README.md` | `5d16545ba612c210fd46ea560e20753edb3e6468` | All four pending/unsolved entries, no learner solution |
| `lecture-02/assignments/q01-alphabet-triangle.md` | `ad53f8699c8f15a9b6e5f8ce0742a3001c3f046f` | Alphabet triangle statement, examples, 1–10 input bound |
| `lecture-02/assignments/q02-inverted-star-triangle.md` | `8f154967ea2c4615347818dba135c3988ab0e4ee` | Descending-star triangle statement, examples, 1–10 bound |
| `lecture-02/assignments/q03-hollow-square.md` | `7a1be61fc9ca0ade2e14647f951f9b335a88f3a1` | Hollow-square statement, examples, 1–10 bound |
| `lecture-02/assignments/q04-132-pattern.md` | `107db65ad457f4fac5ba0d0c0216b5fed744bf5a` | Strict i<j<k and nums[i]<nums[k]<nums[j], n up to 200,000 |

All paths above are relative to `99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/`. SHA checks use the full Git blob format and **fail closed if an original archive file changes**. Original PDF/screenshot binary parity has **not** been independently checked here.

## Executable original-lecture-fence review

The [read-only reviewer](../scripts/check_bosscoder_python_refresher_02_lecture_and_pending_grading_contracts.py) extracts **the original 13 unchanged code fences** directly from the three immutable chapters and runs each in an isolated Python namespace while capturing stdout. Output expectations were independently transcribed from the literal code; these three companion chapters do **not** publish output-fence keys.

| Chapter | Original Python fences | Independently asserted output behavior |
| --- | ---: | --- |
| Patterns / nested loops | 5 | 3×4 rectangle, paired ascending/descending stairs, centered height-four pyramid, height-three diamond, four-by-four hollow square; spaces and newlines byte checked |
| Lists and strings | 4 | Index/slice plus append, nine mutating list operations in source order (independent namespace), string repetition and character iteration, trim/lower/split/join, search positions, classification and text formatting |
| Tuples, sets and dictionaries | 4 | Count/index/min/max/conversion, tuple iteration, all four set operations and insertion-ordered dictionary rendering; **set display order deliberately ignored** while exact members are checked |

The checker separately inspects the four preserved assignment statements and sample contracts without writing graded solutions. For Q01–Q03, its **auditor-authored** shape invariants cover input bounds 1–10 (row sizes, total stars, border-only stars). For Q04, a deliberately cubic **tiny-input-only reviewer oracle** checks the three provided true/false examples, strict/order counterexamples and **363 generated small tuples**, including equality under positive affine transformations. This does **not** supply or benchmark the O(n) approach needed for the 200,000-element constraint and is **not** a learner answer, platform submission, official key or completed exercise.

The reviewer also checks two documented Python pitfalls: Python 3 has no built-in `cmp`, and a tuple containing a mutable list can change indirectly and cannot be hashed. Every exercise remains pending independent learner work. Original notes explicitly identify notebook-state-dependent list-output discrepancies: replaying each standalone code fence in a fresh scope does **not** certify the unprovided original notebook state.

## Evidence categories and remaining work

- **Indexed/source inspected:** three chapter Markdown companions; four pending assignment texts and their index, all eight anchored to observed Git blobs.
- **Original companion code runtime:** 13/13 verbatim Python fences covered by direct output assertions; the set examples are compared semantically rather than assuming stable printed ordering. This is **not** a replay of the original Academy PDF/notebook.
- **Synthetic reviewer-only semantics:** Q01–Q03 shapes for all ten legal sizes, plus Q04 finite oracle and counterexamples. No claim of external grader/platform acceptance.
- **Authenticated official answer verified:** **0/4** for these graded assignments.
- **Learner independently solved/reviewed:** **0/4**, unchanged. **Mastery credited:** zero.
- **Blocked/unverified:** user-shared Academy original PDF/screenshots and Colab state not available as independently readable original files in this run; genuine learner submissions and Academy grader hidden tests unavailable. A source-summarized problem statement cannot substitute for authentic PDF/page-image parity. Native performance at n=200,000, official key equivalence, and other Bosscoder exercises still require independent work.
- **No source mutations:** original archives, learner attempts/progress, canonical Python/SQL foundations and separate ChatGPT Library learner evidence remain unchanged. The Library study log is **UNSYNCED** until completed independent Issue #1 audit signoff and separate post-sync CI.

This ledger contributes a **bounded lecture-example/output replay and pending-assignment contract audit**, not global four-source completion. **Keep GitHub Issue #1 OPEN.**
