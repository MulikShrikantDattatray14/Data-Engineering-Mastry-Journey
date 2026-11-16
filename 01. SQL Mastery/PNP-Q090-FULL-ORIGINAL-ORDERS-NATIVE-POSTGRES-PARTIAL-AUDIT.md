# PNP Q090 — complete original Orders.csv, independent eight-column profile differential (PARTIAL)

**Date:** 16 November 2026. **State:** partial audit, original provider answer **not** independently authenticated, original PDF rendering still pending, learner's archived solution **Pending**. CI result must be independently verified at the exact workflow SHA; implementation and test names alone are not execution evidence.

## Independently reopened and preserved original contracts

| Original read-only evidence | Immutable Git blob | Interpretation |
|---|---|---|
| `P090. Column-by-column completeness profile of Orders.md` | `1fa536155bfc0115c796ae7c740d0b23dff851f7` | Source task says exactly eight rows in schema/table order, with total/null/recent-null/distinct counts; illustrated Jan 2026 two-order sample |
| `sql/all_100_solutions.sql` | `7912c8e676621c513e0b635a40c6ee299404676e` | Preserved Q90 attributed supplier PostgreSQL SELECT, **not** an authenticated provider grading record |
| `data/load_dataset_v2.sql` | `3787743252d29268c67c491d6a2eb47c1757c35b` | Orders primary key, nullable other columns, `NUMERIC(12,2)`, source date parsing `DD-MM-YYYY` |
| `data/Orders.csv` | `307acc9ad2f85a79d7637a7958ffd62f2a8fa594` | Full original **46,438-row** CSV, rather than a sample or rebuilt synthetic file |

The original source question attributes itself to PDF question 90, pp. 178–180, but PDF pages and an actual independently signed provider answer were **not** visually authenticated. Its archived learner SQLite, SQL Server, and Official solution placeholders remain **Pending**; no learner-submission evaluation or mastery inference is authorized.

## Independent method and exact scope

[New nine-test reviewer](../scripts/check_pnp_q090_native_postgres_full_orders.py) first validates the four Git blob identities and unchanged original learner status. It reads *every* `Orders.csv` data row with the eight original headers, independently converts the three date fields from DD-MM-YYYY, four ID fields to integers, and the amount to `Decimal` under the original loader's `NUMERIC(12,2)` contract. It creates a disposable transaction-scoped PostgreSQL 16 TEMP table with matching columns and primary key, inserts all **46,438** untouched CSV observations through COPY, and runs the exact supplier-attributed SQL section **without SQL translation or changes**. No original source file or canonical foundation note is edited.

An independent Python implementation then calculates, for **each of eight original columns**, number of records, NULL count, NULL percent at 2 dp, distinct non-NULL values and a separate **30-day denominator** relative to the latest non-NULL OrderDate. The recent-window predicate is strictly `OrderDate > MAX(OrderDate)-30 days`, not wall-clock time. The reviewer compares PostgreSQL output **row-by-row, including table-column order**, with these independently produced Python results. It additionally repeats the source two-order illustration, tests an exact Jan 1 versus Jan 2 cutoff, two decimal spellings of the same amount, missing IDs, negative amount, NULL-only date anchor and an empty-table boundary. Its console output publishes only safe aggregate column counts, percentages, distinct counts and recent slice size; never any customer row, address or PII.

**Already reproduced by the earlier independent native reviewer:** with `Orders` empty, the source-supplied query produces **zero** rows instead of one result row per each of the eight columns. That is a genuine empty-input output-shape gap; an undefined percentage policy needs supplier clarification. Even if all eight **nonempty** CSV profile rows match the independent Python computation, the whole Q090 task is **not** unconditionally passing, and its official grade remains unknown.

## Evidentiary tier and unresolved gates

- **Indexed:** yes, previously one of the 205 P/A/X original source records; no new unique source ID.
- **Statement inspected:** yes, preserved original Q090 text, schema and illustrative output, unchanged source key and loader.
- **Synthetic/source-data execution:** reviewer designed to run the **original** SQL natively on **both** fixtures and full source Orders.csv. Treat this as *pending* until exact-head GitHub Actions evidence is checked. It is not a provider-authenticated official answer.
- **Official answer verified:** no, original provider grade and PDF visual parity unavailable.
- **Learner independently solved:** no, historical NOT SOLVED YET/Pending untouched.

**Open beyond Q090:** unresolved empty-table output contract, complete provider PDF/source reconciliation, remaining PNP SQL source/key semantics across all 205, Python mentorship, Bosscoder, W3Schools, other DE, PDF/ZIP/CSV image licensing and PII, plus whole-repository source-to-concept signoff. Conservative clean distinct supplied-key count stays **94/205**, without crediting Q090's known gap. [GitHub Issue #1](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/issues/1) must remain **OPEN**. The ChatGPT Library learning record `/Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md` and later interactive learning remain **UNSYNCED** until separate audit and post-sync CI gates.
