# PNP Q097/Q098 — independently inspected source keys and native PostgreSQL 16.16 audit (PARTIAL)

**13 November 2026.** Read-only, additive auditor evidence. **Not a completed learner exercise, provider-issued official grade, original-commerce-dataset acceptance test, or final audit signoff.**

## Original source records and immutable provenance

| ID | Archived original source and question | Git blob SHA | Supplied answer-key provenance | Historical learner status |
|---|---|---|---|---|
| P097 | `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/9. Windowing Functions/P097. What do customers buy on their second order.md`; [original PDF](<../99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/Source Materials/Updated_100_SQL_Interview_Questions.pdf>) pp.199–203 *as attributed by archived markdown; rendered PDF parity not checked* | `9bf349ac0fe866697d481d3206ecd4598ec3c76e` | Q97 exact PostgreSQL SQL section in `.../Source Materials/PrepNPlaced_SQL_100_v2/sql/all_100_solutions.sql`, blob `7912c8e676621c513e0b635a40c6ee299404676e` | `NOT SOLVED YET`, both My solution fields `Pending`, official display `Pending` |
| P098 | `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/15. Analytics and Performance/P098. Category association rules support, confidence, lift.md`; original PDF pp.203–206 *attribution only* | `526ba18093580b581cb8ef5442a2ce31b222f3fd` | Q98 exact SQL from same pinned supplier key blob | `NOT SOLVED YET`, learner and official display `Pending` |

The separately archived PostgreSQL key is **supplier-provided solution material**, not a verified provider grade or a record that the learner solved it. Both question records are in the 205-ID P/A/X index; index membership alone proves neither correctness nor mastery. No original archive, learner file, progress record or canonical note was modified.

## Native checker: unmodified original supplied SQL (not SQLite or translated SQL)

[Source SHA-pinned read-only checker](../scripts/check_pnp_97_98_native_postgres.py) extracts both full SQL statements from the preserved key by Q97/Q98 heading. It checks both original question SHA values and common answer-key SHA, enforces source and historical Pending markers, and executes *the unmodified original SQL* under PostgreSQL **16.16** (`server_version_num=160016`). Every fixture uses fresh transaction-scoped PostgreSQL TEMP tables. In-memory/temporary synthetic data are auditor-authored, not source Commerce Dataset v2.

| Source ID | Independently checked fixture | Native observed output and independently asserted expectation | Interpretation |
|---|---|---|---|
| Q097 | Original 3-order first/second-category sample | `Audio → Home: 1, 50.00%`; `Audio → No second order: 1, 50.00%` | **PASS** original illustrated values and ordered rows |
| Q097 | Independent dominant-category equal-value tie, missing line items, unmatched product and absent second-order boundary | Four groups: `Audio/Home 1/50.00`; `Audio/No line items 1/50.00`; `No line items/No line items 1/100.00`; `Unmapped/No second order 1/100.00` | **PASS** bounded exact output, including key's tie and no-lines rules |
| Q097 | Genuine category named `No second order` in a second order, beside a different customer's actual missing second order | Source returns a *single* `Audio / No second order / 2 / 100.00%` group, merging two logically different paths | **REPRODUCED LABEL COLLISION**: needs reserved sentinel/display-identity policy, not official-answer failure certification |
| Q097 | A customer with a NULL-date earlier order and one valid-date order | Source excludes NULL-date order, treating the valid-date order as first: `Home / No second order / 1 / 100.00%` | **REPRODUCED INPUT POLICY**: chronological order of NULL-dated history unspecified by task |
| Q097 | Empty Orders and lines | Zero rows | **PASS** empty boundary |
| Q098 | Original 4-basket, two-category illustrated input | `Audio → Home` and `Home → Audio`, each `2 / 50.00% / 66.67% / 0.889` | **PASS** original ordered output |
| Q098 | Independent repeated item rows, two Home products in same basket, unmatched CategoryID, directed rule ranking | `Unmapped→Audio 1/20/100/1.250`, `Audio→Unmapped 1/20/25/1.250`, `Home→Audio 2/40/66.67/0.833`, `Audio→Home 2/40/50/0.833` | **PASS** deduplicated basket/category membership, rule direction and ordering |
| Q098 | OrderDetails containing unmatched ProductIDs, including an orphan-product-only order | Orphan-product-only order entirely omitted from 3-basket denominator; `Audio↔Home` each `1 / 33.33% / 50.00% / 0.750` | **REPRODUCED DENOMINATOR / JOIN POLICY**: `JOIN Products` drops unmapped product lines and excluded-only orders despite task's broad "each order as basket" phrasing; requires source-provider clarification |
| Q098 | 50 baskets, just one category pair | Both directed rules emitted, support `2.00%`; Home→Audio confidence `100%`, Audio→Home `2%`, lift `1.000` | **PASS** inclusive threshold and tie sorting |
| Q098 | 51 baskets, same one pair | Zero rules; 1/51 falls below 2% | **PASS** strict subthreshold filter |
| Q098 | No eligible basket rows | Zero results | **PASS** empty denominator boundary |

All **11** individually asserted groups passed the expected behavior of *original source SQL*. Counterexample-regression passes **document conditional source contract limitations**, and do not mean that the source key fulfills every interpretation of the task.

## GitHub Actions evidence

- Code/workflow commit `1aaa8f66e049b63e0e4b91a4151a32f3530d33f5`: [GitHub Actions run 43334914213](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43334914213) completed **SUCCESS** on exactly that SHA. Independently read Actions job summaries: **94/94 general validation steps and 15/15 native PostgreSQL steps successful**, zero failed/skipped.
- Independently decoded native job `131588542845`: original statement/key pin checks; PostgreSQL `160016`; **5 Q097 and 6 Q098** fixture groups explicitly logged PASS; both counterexample and original-sample outputs reproduced. The test is bounded, not an exhaustive 205-question integration.
- Documentation-commit exact-main CI must be verified separately before describing current main as CI-passing.

## Evidence tier and remaining gates

- **Indexed:** Q097 and Q098 present among 205 original P/A/X records.
- **Statement inspected:** each original question, supplied-key Q section, schema/illustrations/printed output and historical Pending markers separately examined and blob-pinned.
- **Synthetic test passed:** yes, original unmodified supplied PostgreSQL queries on the eleven disposable native fixture groups above; known source-contract counterexamples explicitly distinguished.
- **Official answer verified:** **NO** provider-authenticated output/grade, original rendered PDF parity, complete Commerce Dataset v2 parity or source acceptance of sentinel/missing-product policies.
- **Learner independently solved:** **NO**; both original learner answers remain Pending.

**Remaining:** original PDF/source-archive question/answer/render parity and complete v2 data execution, Q097 sentinel collision and NULL-date policy, Q098 basket denominator/unmatched product policy, other P/A/X source correctness and existing discrepancies, Bosscoder/Python mentorship/W3Schools/non-SQL Data Engineering audits, cross-source uniqueness/integrity, privacy/licensing and final audited CI signoff. The conservative clean bounded supplied-key tally **remains 94/205** because Q097/Q098 were already previously executed via the indexed SQLite checker, and this native rerun does not create new IDs or resolve remaining acceptance gaps. Issue #1 remains **OPEN**. Separate ChatGPT Library learner-study record and later sessions remain **UNSYNCED to GitHub** until full audit signoff and final CI; no interactive-study edits were made.
