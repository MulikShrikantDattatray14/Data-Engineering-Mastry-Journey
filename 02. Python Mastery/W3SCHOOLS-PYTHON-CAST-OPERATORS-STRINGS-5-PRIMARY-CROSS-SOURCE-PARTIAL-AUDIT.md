# W3Schools casting, operators, string slicing, modification, formatting — five-page primary comparison (PARTIAL)

**Audit date:** 15 November 2026. **Scope:** independently opened five *actual* hosted W3Schools Python lesson bodies and compared their shown examples/explanations against four unchanged mentor companion lessons (PDF references pp.7–10). This is *source statement inspection*, **not** authenticated W3 editor output/grading, a newly solved learner task, original mentor PDF rendered-page parity, or an official answer key. Earlier primary W3 Python inspections covered 31 distinct URLs. These five add **five distinct hosted lesson URLs (36 total)**, but overlap familiar Python fundamentals; **do not count them as five new unique concepts or learner completions.**

## Page-by-page, independently read primary content

| Official hosted lesson | Original mentorship companion | Inspection and precise boundary |
|---|---|---|
| [Python Casting](https://www.w3schools.com/python/python_casting.asp) | Lesson 03 *Numbers and maths*, PDF p.7; Lesson 06 *Input and output*, PDF p.10 | Hosted `int(2.8)`, `int("3")`, `float("4.2")`, `str(3.0)` examples agree with companion conversion primer. Reviewer separately checks **negative truncation toward zero**, **invalid integer text**, thousands commas, and nonfinite amounts. Converting a string to numeric is *not* the same as validating a business-money field. |
| [Python Operators](https://www.w3schools.com/python/python_operators.asp) | Lesson 03, p.7; Lesson 05 *True False and comparisons*, p.9 | Hosted lesson introduces arithmetic, assignment, comparisons, logical, identity, membership and bitwise categories. Original lessons also explain `//` and `%`, `is None`, truthiness and operator precedence. Synthetic reviewer checks negative divisors, `and/or` operand values, short-circuit behavior, comparison versus identity, and misgrouped refund-policy conditions; no source provider grading inferred. |
| [Slicing Strings](https://www.w3schools.com/python/python_strings_slicing.asp) | Lesson 04 *Strings - working with text*, p.8 | W3 demonstrates end-exclusive `[2:5]`, omitted boundaries and negative indexes. The preserved mentor includes `[:4]`, `[4:]`, `[-1]` and `len`. Reviewer extends only the boundary analysis to empty/out-of-range slices, negative steps, indexing exceptions and combining Unicode code points; **one user-perceived character need not be one code point**. |
| [Modify Strings](https://www.w3schools.com/python/python_strings_modify.asp) | Lesson 04, p.8 | Primary examples `upper()`, `lower()`, `strip()`, `replace()` and `split(",")` match companion exercises. `strip()` strips ends only and string methods return **new values**. `split(",")` is not correct for a CSV field containing a quoted comma. Distinguish `casefold()` from simple lowercase when normalizing multilingual keys. |
| [Format Strings](https://www.w3schools.com/python/python_strings_format.asp) | Lesson 04, p.8; Lesson 06, p.10 | Live page demonstrates string+number TypeError and `f"price {price:.2f}"`, expressions in placeholders and mentions `str.format`. Mentor shows field widths, zero-pad, thousands separator and percentages; separate linked [String Formatting](https://www.w3schools.com/python/python_string_formatting.asp) is **another hosted URL** already indexed in original. Reviewer verifies formatting outputs and highlights **rendered `.2f` is a presentation rule, not exact financial arithmetic**; use `Decimal` plus an explicit rounding policy. |

## Immutable originals and evidence tiers

The [read-only 16-method checker](../scripts/check_w3schools_python_cast_operators_strings_5_primary_cross_source.py) pins the **native Git blob SHA-1** of four original archived Markdown companions, verifies their PDF page references and earlier W3 upstream citations (casting/operators and alternate strings/formatting), and runs 15 independently authored Python semantic/reviewer boundary cases:

| Unmodified original source path under `99. Reference Materials/Original Mastery Snapshot/2. Python Mastry/1. Python from Zero/` | Git blob SHA |
|---|---|
| `03. Numbers and maths.md` | `1e0079262aadcdfa1c92a15dd5575fc5a52a9113` |
| `04. Strings - working with text.md` | `efd9df91f7af2cb988eb406a1982350243dfc11a` |
| `05. True False and comparisons.md` | `810c49664e586b951295e03a8672938b241cbc74` |
| `06. Input and output.md` | `abeee9779392bbd199e73ef30d35cddae73d0611` |

All four *companion lesson bodies* have been individually retrieved and read from the current original archive. Existing mentorship example replay coverage is **not incremented** by these *new reviewer-written* cases.

- **Indexed:** all five W3 hosted page URLs identified; four unchanged original lesson files already in the archive.
- **Statement inspected:** five actual hosted W3 teaching bodies and four original companion lessons individually inspected.
- **Original source integrity checked:** four Git blob hashes pinned in the checker; repository test must pass before claiming SHA verification in CI.
- **Synthetic/reviewer test passed:** requires exact final-main GitHub Actions job logs showing 16/16 checker methods `ok`, and both workflow jobs passing; until that inspection, *pending*. Tests are pure local Python behavior, not W3 interactive/editor or authentic instructor-graded outputs.
- **Official answer verified:** **0 new**.
- **Learner independently solved:** **0 new** (historical completions are unaffected).
- **Mastery demonstrated:** **none newly established**.

**Outstanding blockers:** W3 hosted editor/grade and original PDF rendered pages; full Python/Bosscoder/W3/DE scope; all 205 PNP SQL original/provider/dataset/native execution requirements (**94/205 conservative clean supplied-key replay unchanged**); public archive distribution rights and embedded-binary PII review; final concept mapping; original provider datasets and exact expected outputs. GitHub Issue #1 must remain **OPEN**. Do not alter original source archives, historic attempts/progress, or active canonical foundation notes during this review. ChatGPT Library `/Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md` plus later practice remain **UNSYNCED** with GitHub until independent full audit signoff and a separate post-learning-sync CI.
