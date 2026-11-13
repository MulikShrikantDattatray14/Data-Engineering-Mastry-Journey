# W3Schools SQL aggregate, alias, write operations and row-limit cross-source audit (PARTIAL)

**Independent inspection:** 13 November 2026. **Eight distinct live official W3Schools lesson bodies read**, compared to **seven individually inspected, Git-blob-pinned local source/canonical records**. The preceding W3Schools SQL audit ledgers had 24 distinct lesson pages; this nonoverlapping tranche brings the verified *live-page-inspected* tally to **32**, **not** a complete W3Schools syllabus audit. Nothing here marks a learner exercise complete.

## Live primary pages: actual contracts versus local evidence

| Official primary lesson independently inspected | Relevant observed statement/limitations | Preserved local cross-source comparison |
|---|---|---|
| [MIN](https://www.w3schools.com/sql/sql_min_max.asp) | The currently served page is titled **SQL MIN() Function**; returns smallest selected numeric/text/date value and supports GROUP BY. **Do not count this page as a separate MAX page**, despite URL containing `min_max`. | Canonical Aggregation note discusses SUM/AVG/COUNT; grouped MIN boundaries are supplementary reviewer fixtures. The standalone W3 MAX lesson was **not** inspected in this tranche. |
| [SUM](https://www.w3schools.com/sql/sql_sum.asp) | SUM ignores NULL, permits WHERE, GROUP BY and expressions, including joined price × quantity. | Canonical Aggregation warns that joins multiply source rows and that SUM over no non-NULL inputs yields NULL; Bosscoder aggregation ledger previously found original learner SQL nullable-country divergence #06. W3 lesson's example is not evidence that every order-to-product join has a matching product or that an order header can be summed after line join. |
| [AVG](https://www.w3schools.com/sql/sql_avg.asp) | AVG ignores NULL, supports WHERE, GROUP BY and above-average scalar subquery. | Canonical notes distinguish row mean from unit-weighted mean, require denominator clarity and guard empty populations. The reviewer executes a different synthetic higher-than-mean query; no provider demo output authenticated. |
| [Aliases](https://www.w3schools.com/sql/sql_alias.asp) | AS names output columns or table aliases; W3 examples distinguish SQL Server's string-concatenation `+` and MySQL's `CONCAT`. | Canonical projection/grouping material uses aliases; auditor verifies labels don't rename base columns. No live SQL Server/MySQL execution or cross-dialect concat parity established. |
| [INSERT INTO](https://www.w3schools.com/sql/sql_insert.asp) | Explicit column list vs all-column positional insertion; omitted fields may have defaults/NULL; multirow VALUES. W3 example shows an auto-numbered CustomerID omitted from inserted values. | Canonical Basics provides PRIMARY KEY, NOT NULL and transaction framing. Reviewer-created SQLite table explicitly defines INTEGER PRIMARY KEY and default; this **does not validate the undocumented actual W3 demo table definition**. Source page's auto-number display cannot establish arbitrary database schema or all-dialect identity behavior. |
| [UPDATE](https://www.w3schools.com/sql/sql_update.asp) | SET changes matching rows; omitting WHERE updates every row. | Canonical Basics warns about selected modifications. Synthetic WHERE and unconditional UPDATE are separately verified; use transactions/row-count checks before real production changes. |
| [DELETE](https://www.w3schools.com/sql/sql_delete.asp) | Deletes matching rows; no WHERE removes **all table rows** while table definition remains. | Canonical Basics maps DELETE to row removal. Reviewer contrasts scoped vs unconditional DELETE with rollback; these tests never operate on preserved original or user tables. |
| [SELECT TOP / LIMIT / FETCH FIRST](https://www.w3schools.com/sql/sql_top.asp) | TOP for SQL Server/Access, LIMIT for MySQL, FETCH FIRST for Oracle examples; sorted top-N requires ORDER BY. | Canonical Advanced SELECT explicitly notes LIMIT versus TOP and stable tie-breakers; PNP P002 fixed top-ten semantics are previously reviewed. SQLite TOP is deliberately rejected; **SQL Server/Oracle execution is not established**. TOP PERCENT is also not translated here. |

### Exact local source byte pins used by the read-only checker

These Git SHA-1s are checked by recomputing `SHA1("blob " + length + "\\0" + original bytes)` before any synthetic SQLite queries. They pin archival/learning-document bytes, **not external W3Schools page versions**.

| Read-only local path | Git blob SHA-1 | Role |
|---|---|---|
| `99. Reference Materials/W3SCHOOLS-TOPICS.md` | `c6328c2eb420f47e5585026a7bf3c0a4e41be720` | Selected topic index (not full source) |
| `01. SQL Mastery/00. SQL Basics/0. Foundation Notes.md` | `d181dd73f96b1f2b7327600e290d52e9fd59a976` | Keys, constraints, safe writes |
| `01. SQL Mastery/01. Advanced SELECT/0. Foundation Notes.md` | `1ed1077d492a3bd9db25018650b5c1f3cae1371f` | TOP/LIMIT and fixed-N tie rules |
| `01. SQL Mastery/03. Sorting and Grouping/0. Foundation Notes.md` | `5cf690cb6ca5942795fe332aa447bbf77e14232e` | Group grain, HAVING, ordering |
| `01. SQL Mastery/04. Aggregation/0. Foundation Notes.md` | `7dcd722be94284602dd17e316dca9ce096954c33` | NULL aggregates, weight, grain |
| `01. SQL Mastery/15. Analytics and Performance/0. Foundation Notes.md` | `d2743783106fe64ca087b39216184a87e97d1a8c` | Fan-out and performance |
| `01. SQL Mastery/BOSSCODER-AGGREGATION-INDEPENDENT-AUDIT.md` | `e3f283154e533254f22372d18d2886c8d8c2aeb9` | Previous original Bosscoder samples, separate synthetic checks and a reproducible NULL anomaly |

**Index discrepancy:** None of these eight *individual* W3Schools page URLs appears in the selected-topic `W3SCHOOLS-TOPICS.md` index. The canonical SQL notes do cover most relevant conceptual material. This is an eight-link **selected-index coverage gap**, **not** proof that eight concepts or source files were lost. Original index and canonical notes remain untouched.

## Reviewer-only runtime evidence and counterexamples

Read-only checker: [`scripts/check_w3schools_sql_aggregate_dml_limit_cross_source.py`](../scripts/check_w3schools_sql_aggregate_dml_limit_cross_source.py). The 14 `unittest` methods comprise **one seven-blob archive integrity guard plus thirteen distinct auditor-authored SQLite fixture checks** for MIN/text/empty groups, SUM/AVG NULL denominators, SUM(expression), group aggregates, aliases, partial/multirow/positional INSERT, NOT NULL rollback, scoped/unscoped UPDATE and DELETE, rollback after accidental bulk mutations, TOP-vs-LIMIT dialect difference and deterministic tie-breaking, join fanout, and above-average subquery.

Two important **counterexamples**, not provider answer failures:

1. A NULL quantity or price makes a line-level product expression NULL, so `SUM(quantity * price)` skips the line. Replacing missing values by zero may produce the same sum on a populated case but changes the unknown-data meaning and the no-data result.
2. An order worth 500 with three joined lines, plus a one-line order worth 100, gives 600 from the original order header grain but 1600 if the order header total is naively summed **after** the join. This is a grain error, not an error in W3's example of summing **line** extended price.

No W3Schools live editor query or dataset was run. Even a green CI run means **local source-pinned reviewer synthetics passed**, NOT live W3Schools exercise correctness, official answer verification, learner-submitted solutions, or independent mastery. The archived Bosscoder record status and previous PNP SQL conservative 94/205 supplied-key replay tally remain unchanged.

## Evidentiary boundaries and open gates

- **Indexed** = selected topic links or indexed local material; **statement inspected** = eight live lesson bodies and seven local byte-pinned records; **synthetic test passed** = only after CI independently confirms the added checker on exact head.
- **Official answer verified:** none newly, none implicitly established from W3 site sample pages. **Learner independently solved:** none newly. No grade, question attempt, or study duration inferred.
- **Unresolved:** site editor exercise results and current dataset/actual table definitions; SQL Server TOP/Oracle FETCH/native MySQL DML-dialect parity; W3Schools remaining lessons including separate MAX; all original PNP PDFs/full original commerce dataset and remaining SQL source contracts; Python mentorship PDF and broader Bosscoder/DE comparisons; source-to-concept completeness, preservation and license/privacy signoff.
- This is an **additive, partial, read-only reviewer investigation**. Original archive, learners' historical attempts/progress and canonical notes must remain intact. Issue #1 must stay OPEN. The separate ChatGPT Library pending learner-study record and later study are **NOT SYNCED TO GITHUB** before complete independent audit signoff and final comprehensive CI.
