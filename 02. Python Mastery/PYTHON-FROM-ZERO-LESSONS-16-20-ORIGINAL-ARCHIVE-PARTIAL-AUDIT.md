# Python from Zero L16–L20 original-source cross-check — PARTIAL

**Scope and evidence classes (14 November 2026).** This is a fresh check of five already archived *companion Markdown* lessons linked respectively to mentorship PDF pages 20–24, not proof of native PDF page-image parity. It is source verification, not an interactive-study update. The original source archive and its historical attempts/progress are unchanged. W3Schools example snippets copied into archived lessons are treated only as *archived companion snippets*; the live W3Schools pages/editor and assessment/grading have **not** been independently reauthenticated in this check.

## Source identification independently retrieved from the existing archive

All five original Git blob identities were directly observed on GitHub and independently guarded by the source-run checker (Git's blob-header SHA-1, **not** plain-file SHA-1):

| Lesson; claimed original PDF page | Archived source | Git blob SHA | Original content inspected |
| --- | --- | --- | --- |
| L16; p.20 | \`1. Python from Zero/16. Modules packages and pip.md\` | \`2002d657a4bb52dcd1e369a9083dfd1d7b5c37eb\` | Standard library imports, seeded random sample, custom module creation, \`__main__\` and subprocess run, companion W3 import/date/pip/environment |
| L17; p.21 | \`17. Reading errors.md\` | \`9159ef47b425806d4622584284b1a145543f5222\` | Actual \`ZeroDivisionError\`, guarded mean, invalid-number accumulation, \`repr\`/assert, W3 try/except/finally |
| L18; p.22 | \`18. Files - read and write.md\` | \`d47356de0ec044cc16cd61377535266af3a3c50f\` | Small practice CSV, supplied dataset line count, delivered revenue, append and pathlib, archived JSON example |
| L19; p.23 | \`19. Mini project - monthly sales report.md\` | \`30992048e800aa0aaf8e8940546993d5b48be366\` | Exact \`read_orders\`/\`month_of\`/\`build_report\`/\`print_report\` code and printed four-month results |
| L20; p.24 | \`20. Practice set 0 - first steps.md\` | \`5c5ee4773abcf2b797bd08d46a6a6421388b0962\` | Five *already-published source answer* snippets: FizzBuzz, extremes, case-insensitive words, palindrome, status percentages |

Full paths are prefixed by \`99. Reference Materials/Original Mastery Snapshot/2. Python Mastry/\`.

**Pinned actual source fixtures:** \`python_de_dataset/orders.csv\` \`2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2\`; \`customers.json\` \`d6125fce237e7f7e3193667946d1eb117cd19db0\`; \`events.jsonl\` \`975c007a68c336007023a9ebd92ba82f02a6b7c3\`.

## Executable independent tests

The [12-test read-only replay checker](../scripts/check_python_from_zero_lessons_16_20_source_contracts.py) extracts the *literal original Python fences* from these SHA-guarded source Markdown files and executes them in **throwaway temporary directories**. It places source CSV/JSON/JSONL copies in those directories as needed, never running the teaching snippets in any archive or canonical foundation folder. The twelve test methods cover:

1. Five source and three fixture blob identities.
2. L16 standard-library and source-printed output, seeded random sample.
3. L16 source-built \`helpers\`/\`tool\` with \`__main__\` import-vs-direct execution, and archived W3 alias-import example.
4. L17 intentional original division-by-zero traceback, then source guard output.
5. L17 source \`ValueError\` collection, dynamic type/DEBUG output and archived try/except/finally snippet.
6. L18 original small-file creation/read/streamed delivered totals.
7. L18 original complete orders.csv first/last/header/15 rows versus independent \`csv.DictReader\` and \`Decimal\` revenue and status oracle.
8. L18 source write/append/path behavior and archived JSON serialization sample.
9. L19 actual original project source end-to-end on original full 15 orders, compared with the **exact source-printed report**: Jan 1,994 (2), Feb 2,847 (2), Mar 7,291 (4), Apr 6,840 (4), grand total 18,972.
10. L19 independent Python \`Decimal\` month/count/revenue/max oracle, plus exact original three-row mini fixture.
11. L20 all **five source-published** practice answer snippets and their printed expected output, explicitly *not* new user answers.
12. Synthetic *reviewer-only* dirty-data boundaries: quoted comma parsed incorrectly by the basic \`split(',')\` file reader; impossible month accepted as a seven-character bucket; negative-only group retains \`best=0\`; and an all-nonletter palindrome is vacuously \`True\`.

**Pass/fail accounting:** Test-code creation or local assertion alone is not evidence of GitHub Actions completion. Verify the exact final main-commit validation job logs, run's head SHA and all 12 method names before recording PASS. CI integration is in \`.github/workflows/validate-learning.yml\`. Native cloud Python runtime, the original PDF's **rendered page content**, W3Schools hosted exercise grading, all Bosscoder lecture/assignment originals, full course/provider solution parity and any independent learner responses remain outstanding.

## Source-conditional risks and scope limits

- L19's deliberate beginner parser is correct on the supplied simple 15-row CSV, but a quoted comma in a real CSV or a short record is not handled by \`split(',')\`/\`zip\`. \`csv.DictReader\` is an auditor oracle, **not a replacement or learner submission**.
- Month keys are produced by slicing the first seven characters, not date validation; an invalid \`2025-99\` month is grouped without an exception. \`best\` initialized to \`0.0\` does not report the greatest negative amount if all delivered amounts are negative. Neither flaw occurs in the original supplied 15 rows.
- L17 catches expected \`ValueError\`; a different failure type is not silently caught. It does not constitute production-ready numeric-validity policy; \`float('nan')\` is not rejected merely by \`float()\`.
- L20's \`is_palindrome\` returns \`True\` on input with **no letters**, since the cleaned empty string equals its reverse; the problem statement does not define a policy for that case.
- The L19 proposed *city reporting* and *cancellation rate* tasks are **learner exercises, not solved** by this audit. No study-session learner work was changed or promoted to an independent completion.
- Archive source's \`127.0.0.1:8765\` run-and-edit links are local demo shortcuts; they do not prove a publicly hosted runner exists.

**Preservation + signoff:** Only audit-owned new checker/ledger, additive CI and append-only MIGRATION-STATUS updates are authorized. Original archives, historical learner attempts and canonical foundation notes remain out of scope. No new official answers, learner independent completions or mastery are awarded. Other original PNP sources and 94/205 conservative supplied-key replay remain unchanged; licensing/privacy and final source-to-concept integrity remain outstanding. **Issue #1 stays OPEN**. Separate ChatGPT Library learner-study material stays **UNSYNCED with GitHub** until full independent audit signoff and a separately verified post-sync CI.
