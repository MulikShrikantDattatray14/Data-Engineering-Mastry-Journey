# Eight additional official W3Schools SQL pages — partial primary-source comparison

**Inspected:** 14 November 2026. **Evidence tiers:** 8 official page bodies **statement inspected**, 8 preserved local notes/index/source files **directly inspected and SHA-pinned**; 14 read-only tests (one eight-source integrity guard, thirteen **auditor-created SQLite boundaries**) requiring actual CI PASS; **zero official W3 editor answers authenticated; zero new learner independently solved; zero mastery awarded**. These eight pages are distinct from the prior 56 page bodies, yielding **64 distinct W3 SQL pages inspected**, not full curriculum/lesson completion.

| Directly read official page | Primary-source claim / teaching intent | Cross-source and verification boundary |
|---|---|---|
| [Introduction](https://www.w3schools.com/sql/sql_intro.asp) | SQL data access/manipulation; relational tables | Existing canonical SQL Basics and original Bosscoder SQL foundations already introduce rows, columns and keys; reviewer checks read-only SELECT, not Northwind dataset |
| [Syntax](https://www.w3schools.com/sql/sql_syntax.asp) | Statements, table and rows, semicolon separator | SQL Basics / Advanced SELECT examples; reviewer executes disposable multiple statements, not hosted site editor |
| [MAX()](https://www.w3schools.com/sql/sql_max.asp) | Largest numeric/text/date value | Existing Aggregation primer covers aggregates and NULL; reviewer checks numeric NULL skip, empty table NULL, and SQLite text collation; dialect collation still unverified |
| [UNION ALL](https://www.w3schools.com/sql/sql_union_all.asp) | Append SELECT result sets without removing duplicates; same projected column count | Original Bosscoder + CTE/Advanced SELECT notes; reviewer checks duplicate and NULL multiplicity and arity error, not the original Northwind data |
| [ANY](https://www.w3schools.com/sql/sql_any_all.asp) | Quantified predicate is TRUE when at least one comparison succeeds | Reviewer only tests a bounded correlated EXISTS *filter-equivalence* for equality/NULL; SQLite has no native `= ANY` quantified comparison. Original provider SQL not executed |
| [ALL](https://www.w3schools.com/sql/sql_all.asp) | Quantified predicate for all comparison values | Reviewer checks WHERE-filter truth for empty, valid and NULL-containing sets using NOT EXISTS + NULL guard. Not a complete scalar three-valued logic or dialect equivalence proof |
| [DROP DATABASE](https://www.w3schools.com/sql/sql_drop_db.asp) | Destructive DDL with privilege requirement | No database drop performed; SQLite in-memory dialect rejection checked, live DB permissions and recovery **not** tested. Distinguish DROP TABLE already inspected earlier |
| [Data Types](https://www.w3schools.com/sql/sql_datatypes.asp) | Vendor-specific MySQL 8.4 / SQL Server / Access numeric, text and dates | Original Bosscoder and SQL Basics identify SQLite flexible affinity; synthetic VARCHAR-length and explicit CHECK counterexample is **not native MySQL/SQL Server/Access parity** |

## Immutable original and local note comparisons

The eight files below were directly read from GitHub and their exact Git blob SHA-1 identities are asserted in the [read-only checker](../scripts/check_w3schools_sql_intro_quantifiers_types_cross_source.py):

| Source | Git blob SHA |
|---|---|
| `99. Reference Materials/W3SCHOOLS-TOPICS.md` | `c6328c2eb420f47e5585026a7bf3c0a4e41be720` |
| `01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md` | `d181dd73f96b1f2b7327600e290d52e9fd59a976` |
| `01. SQL Mastery/01. Advanced SELECT/0. Foundation Notes.md` | `1ed1077d492a3bd9db25018650b5c1f3cae1371f` |
| `01. SQL Mastery/04. Aggregation/0. Foundation Notes.md` | `7dcd722be94284602dd17e316dca9ce096954c33` |
| `01. SQL Mastery/05. CTEs/0. Foundation Notes.md` | `2716dfc5913b21468e1ffe19d05fc4876cc99d0d` |
| `01. SQL Mastery/11. NULL Logic/0. Foundation Notes.md` | `af9cc8d5d47e0279fe0d8b0f9276b700ce496888` |
| `01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md` | `d2743783106fe64ca087b39216184a87e97d1a8c` |
| `99. Reference Materials/Original Mastery Snapshot/1. SQL Mastery/1. SQL Mastry/1.Bosscoder Academy - foundational notes and Assignments/0. SQL basics/0. Foundation Notes.md` | `073c87bebb2d7c72cca97e970a06de965a87abe5` |

**Index coverage:** all eight exact lesson URLs are absent from the deliberately selected-topic W3 reference list. These are *link selection omissions* only; their concepts have overlapping canonical/source explanations. No teaching files or source indexes were edited to avoid user-interactive learning sync or unverified consolidation. This ledger cites original URLs without reproducing copyrighted lessons.

**Open blockers:** hosted exercises and outcomes, true original W3 demo dataset, native quantified `ANY/ALL` SQL, NULL scalar semantics and cross-dialect datatype enforcement; remaining W3/PNP/Bosscoder/mentorship/DE sources, original PDFs/full CSVs, licensing/privacy, and final audit-wide source-to-concept/integrity signoff. Conservative PNP supplied-key replay remains **94/205**, unchanged. Historical learner attempts/status and Library pending sync remain untouched. **Keep Issue #1 OPEN; no audit-completion notice.**
