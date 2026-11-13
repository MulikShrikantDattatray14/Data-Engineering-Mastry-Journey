# W3Schools SQL RIGHT/FULL/SELF JOIN, CASE, COALESCE, AND/OR/NOT — partial independent audit

**Date independently inspected:** 13 November 2026. **Scope:** eight additional live official W3Schools SQL lesson bodies, compared with seven immutable local source/learner-safe files. This is an **auditor-only evidence ledger**. It neither reproduces the site's copyright-protected lessons nor executes W3Schools Try It/editor/quiz answers. With the earlier two eight-page batches, **24 distinct live W3Schools SQL lesson pages** have been read; this is **not** total W3Schools coverage.

## Eight individual live lesson inspections and conditional comparisons

| Official primary page inspected | Source contract individually checked | Independent local distinction and reviewer boundary |
|---|---|---|
| [RIGHT JOIN](https://www.w3schools.com/sql/sql_join_right.asp) | Preserves all right-table records, supplying NULL left columns for unmatched right records. | Canonical Joins explains direction. SQLite checker swaps table order and executes equivalent LEFT JOIN on synthetic customers/orders; unmatched customer references and NULL foreign keys remain visible. This is not an execution of original W3 query. |
| [FULL OUTER JOIN](https://www.w3schools.com/sql/sql_join_full.asp) | Preserves matched and both-side unmatched rows; join cardinality may increase. | Original PNP Advanced A006 explicitly requires **MySQL emulation**: LEFT part UNION ALL right-only part on a nonnullable matched-left key. Synthetic checker verifies duplicates, unmatched/orphan/NULL foreign keys and one empty side. W3 lesson's syntax is **not portable to MySQL**; no native MySQL/provider dataset was executed here. |
| [Self Join](https://www.w3schools.com/sql/sql_join_self.asp) | Two aliases of one relation; site's same-city example uses inequality and generates both pair orientations. | PNP Advanced A011 requires **no mirrored colleague pairs**: inequality alone is insufficient. Synthetic self-join yields six directed combinations for three colleagues versus three unique pairs with `a.id < b.id`. The W3 example isn't wrong: its contract differs. |
| [CASE](https://www.w3schools.com/sql/sql_case.asp) | Ordered WHEN branches use the first true result; absent ELSE defaults to NULL. | Canonical NULL foundation already distinguishes CASE labels from WHERE filtering. Synthetic overlapping bands show precedence, boundaries and missing-price ELSE behavior. W3 editor output not authenticated. |
| [COALESCE and dialect-specific NULL functions](https://www.w3schools.com/sql/sql_isnull.asp) | COALESCE chooses first non-NULL argument; IFNULL/ISNULL/NVL differ by database. | Canonical NULL note specifies first nonblank usable contact via NULLIF(TRIM(...),'') before COALESCE. Reviewer confirms blank strings survive plain COALESCE; NULL multiplication differs from explicit zero substitution. SQLite fixture does not verify MySQL, Oracle or SQL Server specific functions. |
| [AND](https://www.w3schools.com/sql/sql_and.asp) | A conjunction filters when all conditions are TRUE. | Independent fixture contrasts unparenthesized OR/AND with explicit grouping; SQL's three-valued NULL logic still applies. |
| [OR](https://www.w3schools.com/sql/sql_or.asp) | A disjunction filters when any condition is TRUE. | The same fixture verifies SQL AND binds more tightly than OR in SQLite; parenthesize when business intent requires a different grouping. |
| [NOT](https://www.w3schools.com/sql/sql_not.asp) | Negates predicates in WHERE; site shows NOT equality and related NOT forms. | Synthetic NULL-country row is excluded by `NOT country='Spain'`, because NOT UNKNOWN remains UNKNOWN, not TRUE. Explicit `OR country IS NULL` is needed to include unknown country. This qualifies the site's simple informal wording; it is not a provider-answer failure. |

**Source discrepancy explicitly recorded:** Direct address `https://www.w3schools.com/sql/sql_join_cross.asp` returned HTTP **404** at inspection and was **not** counted as an inspected official lesson. Existing PNP A008 cross-join source and canonical notes remain separate; do not invent a W3Schools page URL or count its content as checked.

## Exact immutable local source blob pins

The reviewer checker independently verifies Git's blob SHA-1 (computed over `blob <byte-length>\0<file bytes>`) before running its synthetic fixtures. These entries are the original preserved bytes, not reconstructed provider answers.

| Local source | Exact Git blob SHA-1 | Coverage relation |
|---|---|---|
| `99. Reference Materials/W3SCHOOLS-TOPICS.md` | `c6328c2eb420f47e5585026a7bf3c0a4e41be720` | Selected external-URL topic index, **not** proof of complete content |
| `01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md` | `d181dd73f96b1f2b7327600e290d52e9fd59a976` | Predicates and logical filters |
| `01. SQL Mastery/02. Joins/0. Foundation Notes.md` | `61d952c98f02a62c6591caaedf5c02cf0b43e3b1` | JOIN grain and PNP A006/A011 pair pattern |
| `01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md` | `af9cc8d5d47e0279fe0d8b0f9276b700ce496888` | CASE, COALESCE, UNKNOWN and blank normalization |
| `01. SQL Mastery/PNP-ADVANCED-PENDING-A002-A003-A006-A007-A008-A009-NATIVE-POSTGRES-PARTIAL-AUDIT.md` | `4871597413dc98e4c7300a7070c9b218a9b3aa19` | Earlier bounded native PostgreSQL reviewer assessment, **not re-executed** by this ledger |
| `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/2. Joins/A006. MySQL has no FULL OUTER JOIN. Emulate one between customers and or.md` | `20e4460e715ec53fd41f063e1368fa3753f2a0fd` | Archived original A006 problem, both learner implementations Pending |
| `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/2.PNP- foundations and practice/2. Joins/A011. List all pairs of colleagues in the same department, without mirro.md` | `fb8226a93e2b3fa12e98b32bc29d13747157114c` | Archived original A011 statement, original learner solution Pending |

**Index-to-content mismatch:** The selected-topic W3Schools index links CASE but does not separately list RIGHT JOIN, FULL JOIN, Self Join, COALESCE/IFNULL, AND, OR or NOT. The canonical foundations do cover many of those concepts; the absent source URL rows are an **index incompleteness**, not proof that a learner never studied them or that source content is missing. Do not alter the index or canonical notes while the audit is open.

## Executable evidence and acceptance tiers

Reviewer-only checker: [`scripts/check_w3schools_sql_outer_self_case_boolean_cross_source.py`](../scripts/check_w3schools_sql_outer_self_case_boolean_cross_source.py). Its **12 unittest methods** comprise **one seven-blob integrity guard plus eleven independently authored SQLite fixture methods**: directional outer joins; full-outer UNION ALL preserving bags, NULLs and empty side; self-join pair orientation; CASE first-match/ELSE; COALESCE blanks and arithmetic; AND/OR operator grouping; NOT/UNKNOWN; LEFT JOIN ON-versus-WHERE; right-only anti-join nullable-column hazard.

**Acceptance labels:** `indexed`: selected W3 link present only for CASE among this eight-page tranche; `statement inspected`: eight official live page bodies individually inspected; `synthetic test passed`: **12/12 source-pinned reviewer methods PASS on code/ledger/workflow SHA `24d63ace98df45e537bff5d02d0d587c71908542`** ([Actions 43446106473](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43446106473): 105/105 general and 18/18 native PostgreSQL steps succeeded, zero failures/skips; decoded validation job `131955844979` shows all 12 methods); `official answer verified`: **none**; `learner independently solved`: **none**. This checker does **not** execute original W3Schools provider datasets/editors, original PNP MySQL keys, student answers, or native PostgreSQL syntax. It must not be used as official grading or mastery evidence.

## Blocking conditions / cross-source and preservation status

- W3Schools hosted editor, exercises, quizzes, exact sample databases and grading remain unverified; no full screenshot/source-parity signoff.
- Original PNP Advanced PDF/MySQL reference answers and all provider datasets are not authenticated by these SQLite tests; A006/A011 source archives explicitly say historical learner work pending. Synthetic fixture results cannot change learner status or the **94/205 conservative PNP supplied-key replay tally**.
- Cross-dialect FULL and RIGHT JOIN behavior (MySQL, SQL Server, PostgreSQL) is outside this particular runner; SQLite transformed equivalents verify set/bag semantics only. The previously recorded native PostgreSQL tasks are separate evidence, not recertified in this pass.
- Complete PNP SQL/Python mentorship/Bosscoder/W3Schools/other DE sources, licensing/privacy and global source-to-concept checks remain unresolved. Archive originals, learner attempts/progress, canonical notes and separate ChatGPT Library pending learning record remain unchanged. **Keep GitHub Issue #1 open and do not perform learning sync or send user completion notice.**
