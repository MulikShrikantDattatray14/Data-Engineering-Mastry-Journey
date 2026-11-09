# Python mentorship source-output audit — PDF pages 5–10

**Independent run:** 2026-11-09. **Evidence level:** preserved source snippet inspected and executable snippet/output check. **Not** a completed mentorship exercise, independent learner attempt, official W3Schools validation, or whole-PDF signoff.

The original six companion Markdown source files in [the hash-preserved snapshot](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/) were fetched individually and examined. The new [runtime checker](../scripts/check_mentorship_python_pages_05_10.py) parses each archived Run/edit-linked Python code block, checks its paired text output, and executes the **source code itself** in isolated local Python processes with bounded timeout. It asserts a complete, unique contiguous snippet inventory per lesson, so omitted examples fail the check.

| PDF page | Archived companion lesson | Original Git blob SHA (unchanged) | Snippets | Notes |
|---:|---|---|---:|---|
| 5 | [01. Your first Python program](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/01.%20Your%20first%20Python%20program.md) | `5fd194caa2280c436371fb94cee97f1ee4c5f5fb` | 12 | #3 intentionally raises `NameError`; #6 intentionally raises `IndentationError`. Checked exception *type*, not traceback line numbers that depend on runner. |
| 6 | [02. Variables and names](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/02.%20Variables%20and%20names.md) | `798106aadd2458a8a8f416dca0225a29c080fa0e` | 7 | #4 intentionally raises `NameError`. |
| 7 | [03. Numbers and maths](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/03.%20Numbers%20and%20maths.md) | `1e0079262aadcdfa1c92a15dd5575fc5a52a9113` | 8 | #6 uses `random.randrange(1,10)` but prints only a guaranteed in-range Boolean. Tested printed Boolean, **not** an RNG seed or exact random value. |
| 8 | [04. Strings - working with text](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/04.%20Strings%20-%20working%20with%20text.md) | `efd9df91f7af2cb988eb406a1982350243dfc11a` | 8 | #3 references `status` assigned by #2; supplied **only that documented prior status** and verified the published result. As a standalone process #3 would raise `NameError`. |
| 9 | [05. True False and comparisons](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/05.%20True%20False%20and%20comparisons.md) | `810c49664e586b951295e03a8672938b241cbc74` | 6 | Exact printed values checked (including truthiness and bitwise operations). |
| 10 | [06. Input and output](../99.%20Reference%20Materials/Original%20Mastery%20Snapshot/2.%20Python%20Mastry/1.%20Python%20from%20Zero/06.%20Input%20and%20output.md) | `abeee9779392bbd199e73ef30d35cddae73d0611` | 7 | #2 and #7 need supplied stdin; #7 displays **terminal-echoed** input in the published text, whereas captured stdin has no echo. |

**Total:** 48/48 linked archived example records inventoried and exercised through explicit source-aligned assertions. Three intentional error cases were checked as expected exceptions, one case was run with an explicitly recorded prior variable, and two were supplied input. The plain examples' printed outputs matched their corresponding archival output texts when comparing trailing end-of-line spaces only; the two interactive examples have special evidence below. **This is not 48 independent practice solutions.**

## Real discrepancies and interpretation (not silently altered)

1. **PDF p.10, Lesson 06 snippet #2 — extra blank line in displayed output.** With stdin `Meera`, `3`, `249`, the archived code executes `input("Price per item: ")`, then `print()`, then the greeting. Captured stdout is:
   `Your name: How many items? Price per item: \nHi Meera, your total is 747.00\n`.
   The archived displayed text contains **two** newline characters after `Price per item:` (a visually empty line). Because the last `input` prompt doesn't itself end with `\\n`, `print()` adds **one** newline, not two. The checker asserts both the actual behavior and the source's distinct claimed output. **Source defect remains in original archive; treat its displayed whitespace as inaccurate.** No learner activity or official grader result inferred.
2. **PDF p.10, Lesson 06 snippet #7 — input echo presentation, not an algorithm failure.** Captured non-TTY stdout for stdin `3` is `Quantity: Units: 3\n`, while the archived transcript shows `Quantity: 3\nUnits: 3`. A real interactive terminal may echo the typed `3` and Enter. Both are consistent with `input` returning string `"3"` and successful conversion. The checker verifies both separately; it does **not** claim byte-identical terminal transcript.
3. **PDF p.8, Lesson 04 snippet #3 — stateful example.** The code is not self-contained unless the previous snippet's `status` exists. Verify in sequence or set the same value. Do not market it as an independent standalone snippet.
4. **Error examples:** Python interpreter versions and launcher filenames change traceback formatting. Checks assert exception class rather than full error-message bytes.

## Coverage boundary and next steps

- Only the 48 source-linked Python examples in archived **PDF pp. 5–10** are covered by this executable check, plus their accompanying text. This does **not** validate every passage of the source PDF image itself or all standalone exercises; additional non-linked examples may still exist.
- The 80-page mentorship original, all 76 lesson companions, Bosscoder, W3Schools official live pages, graded answers, the rest of the repository and licensing remain outside this runtime signoff.
- Continue with mentorship pages 11–19 source code/output verification; then file/CSV, advanced, pandas/ETL and larger-data checks. Record contradictions and dependencies; preserve original answers.
- [Issue #1](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/issues/1) stays **OPEN**; no post-audit Library learning sync until independently full audit + final CI.

**Verification tool:** `python3 scripts/check_mentorship_python_pages_05_10.py`. The GitHub Actions workflow runs it on every push. A green run proves the declared assertions for **that commit**, not overall mastery or complete course correctness.
