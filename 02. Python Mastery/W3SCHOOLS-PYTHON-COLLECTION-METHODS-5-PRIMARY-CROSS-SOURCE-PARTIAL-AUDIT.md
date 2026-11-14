# W3Schools Python string/list/comprehension/dict/set methods: five primary pages (PARTIAL)

**Inspected:** 15 November 2026. Independently opened each of five *actual* W3Schools hosted page bodies and read five unchanged original mentorship companion lessons from the archived Python from Zero material (PDF references pp.8,14–17). These are concept comparisons, not the original PDF rendered-page inspection, W3 editor submissions, hosted answer keys, or learner progress. Earlier primary W3 Python inspection covered **36 distinct URLs**; these five additional URLs are distinct, bringing the count of directly **statement-inspected hosted W3 pages to 41**. Many concepts overlap existing teaching and earlier source replays.

## Independently inspected source-by-source comparisons

| Hosted primary page | Preserved mentor source | Actual teaching statement and audit finding |
| --- | --- | --- |
| [String Methods](https://www.w3schools.com/python/python_strings_methods.asp) | L04 *Strings – working with text*, PDF p.8 | W3 states string operations yield a new value and enumerates \`find\`, \`index\`, \`casefold\`, \`strip\`, \`replace\`. The original companion includes stripping/lowercasing, changing case, replacing, split/join and text example outputs. Reviewer distinguishes \`find\` missing sentinel \`-1\` from \`index\` raising \`ValueError\`, Unicode casefold behavior, and preserved original inputs. |
| [List Methods](https://www.w3schools.com/python/python_lists_methods.asp) | L10 *Lists – ordered collections*, PDF p.14 | W3 lists \`append/extend/insert/remove/pop/sort/copy\`. The mentor shows in-place list mutations and correctly warns that \`list.sort()\` returns \`None\` rather than a sorted replacement. Reviewer probes first-occurrence removal, absent-value exceptions, shallow copies and sort vs sorted. |
| [List Comprehension](https://www.w3schools.com/python/python_lists_comprehension.asp) | L10 p.14 and L13 p.17 | W3 shows filtering \`[x for x in fruits if "a" in x]\` and expression-level \`[x if ... else ... for x in fruits]\`, two distinct policies. Original L10 shows filtered amounts in an actual saved example. Reviewer reproduces the two outcomes, input preservation and single-use generator exhaustion. |
| [Dictionary Methods](https://www.w3schools.com/python/python_dictionaries_methods.asp) | L12 *Dictionaries – key and value*, PDF p.16, and L13 p.17 | **Literal teaching-text discrepancy:** hosted method table describes \`items()\`, \`keys()\` and \`values()\` as returning a "list". In Python 3 these return **live dictionary view objects**, respectively \`dict_items\`, \`dict_keys\`, \`dict_values\`, not \`list\`; \`list(d.items())\` materializes a separate list. Original L12 explicitly uses \`list(prices.keys())\` and \`list(prices.values())\`, a correct distinction. Synthetic runtime checks also expose views updating on added keys and iteration failing on dictionary size changes. This is a **W3 wording imprecision**, not an error in the original mentor example or an authenticated W3 exercise answer. |
| [Set Methods](https://www.w3schools.com/python/python_sets_methods.asp) | L11 *Tuples and sets*, PDF p.15, and L13 p.17 | W3 lists \`difference\`, \`difference_update\`, \`discard\`, \`remove\`, set operators. Original L11 shows actual saved set union/intersection/difference outputs with sorted deterministic display. Reviewer distinguishes copying vs in-place update, \`discard\` vs \`remove\` on missing values, unhashable members, and \`True\`/1 equivalence. Set iteration order remains unspecified. |

## Original-source identity and scope

The [read-only 16-method checker](../scripts/check_w3schools_python_collection_methods_5_primary_cross_source.py) independently pins the **native Git blob SHA** of each original source, checks the associated written PDF-page reference, and replays eight **source-published** fenced Python/output pairs in the unchanged archive (two each from L04, L10, L11 and L12). These are existing mentor teaching examples, **not new independent learner solutions or new unique examples beyond earlier mentorship replay audits**.

| Unmodified source file under \`99. Reference Materials/Original Mastery Snapshot/2. Python Mastry/1. Python from Zero/\` | SHA-1 Git blob |
| --- | --- |
| \`04. Strings - working with text.md\` | \`efd9df91f7af2cb988eb406a1982350243dfc11a\` |
| \`10. Lists - ordered collections.md\` | \`bc2b6ec4ec0b77409570b19044e7ade55a51e961\` |
| \`11. Tuples and sets.md\` | \`3a2788bfc668b3a1ebe5bfd6f58f8fc8c9bfcb2e\` |
| \`12. Dictionaries - key and value.md\` | \`3602334cd9cc779f89eface11b82f844954068a8\` |
| \`13. Which data structure.md\` | \`1142a434f0bda23d683eaf2de5176a4c13020438\` |

Of 16 test methods, one protects source identities/references, four replay original archival examples, and eleven are **auditor-authored synthetic Python boundary probes**. These do not reproduce W3 hosted editor state, verify original provider question grading, prove mentorship PDF image fidelity, or demonstrate independent learner completion. Original source files, learner attempts/progress and canonical notes must stay untouched during this source audit.

## Evidence levels and blockers

- **Indexed:** five hosted URLs plus five preserved companion file paths.
- **Statement inspected:** all five hosted page bodies and five saved mentor companions; not official answers.
- **Synthetic test passed:** *pending matching-head CI evidence* until actual workflow logs show all 16 methods successful. Original-source example replay is tracked distinctly from eleven newly authored synthetic tests.
- **Official answer verified:** **0 new**.
- **Learner independently solved:** **0 new**; no historical learner status may be rewritten.
- **Mastery established:** **0 new**.

Outstanding global work: original PDF rendered-page checks; authenticated W3 editors, full PNP 205 official source/dataset/answer/output/native parity (conservative clean supplied-key replay **94/205 unchanged**), remaining Bosscoder/Python/W3/Data Engineering materials, full licensing/PII binary review, exhaustive source-to-concept reconciliation, final global CI. Keep [Issue #1](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/issues/1) **OPEN**. ChatGPT Library \`/Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md\` plus later learner study remain **UNSYNCED** until independent full-audit signoff and separate post-sync CI.
