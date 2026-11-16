# PNP Q087 and Q088 — original supplier SQL and all-eight-CSV native PostgreSQL replay (PARTIAL)

**Date:** 16 November 2026. **Audit level:** immutable original statement inspection + original-key native PostgreSQL fixture replay + independent row-based whole-source comparison *only when the linked current-head CI passes*. This record is **not a completed four-source audit, provider-official grading, authenticated PDF visual parity, or independent learner coursework**.

## Original source identities and contract

| Record | Git blob identity | Scope |
| --- | --- | --- |
| P087: Referential integrity audit across all seven relationships | `28bed1fe1c7d2e6c4c92e68f6a619a6fb2780e02` | Original preserved `14. Data Quality and Deduplication/P087...` statement, sample and pending learner sections, attributed PDF pp.169–171 |
| P088: Date validity audit | `52c73f3594668d77afbe679b25a84997fb3ced59` | Original statement, nine required rules/zero rows, original sample and pending sections, attributed PDF pp.171–174 |
| Supplier-attributed PostgreSQL `all_100_solutions.sql` | `7912c8e676621c513e0b635a40c6ee299404676e` | Q87 and Q88 sections run **unchanged** |
| Original PostgreSQL loader | `3787743252d29268c67c491d6a2eb47c1757c35b` | Source DD-MM-YYYY order dates and three sign-up date formats |

[Read-only source-pinned native reviewer](../scripts/check_pnp_q087_q088_native_postgres_full_commerce.py). It reads the eight full original archived Commerce v2 CSVs, verifies each Git blob and declared row total (Suppliers **18**, Products **22,088**, Category **12**, Shippers **10**, Payments **10**, Customers **5,072**, Orders **46,438**, OrderDetails **168,567**), then projects **only** the columns used by Q087 and Q088 into disposable **transaction-scoped TEMP PostgreSQL 16 tables** with primary-key indexes. The untouched attributed Q087/Q088 SQL is executed, and returned rows are compared to independently calculated Python reference outputs from those same original records. This is a substantive **full-original-data comparison** if CI passes, not only a few synthetic rows or official answer attribution.

Q087 checks all seven relationship counts, NULL foreign keys, non-NULL missing-parent counts and distinct ascending first-five orphan-key samples, preserving duplicate child rows. Q088 checks all nine rule counts against source day calculations and customer signup lookup, 2-decimal violation percentages, source-order rule labels and first-five violated IDs. Python parses order dates as DD-MM-YYYY and the three sign-up formats from the archived loader; any previously unrecognized malformed date will be an explicit reviewer failure requiring investigation, not silent normalization. The reviewer does not publish source person-level rows, original CSV copies or individual example IDs.

## Preserved source data pins

| File | Git blob |
| --- | --- |
| Suppliers.csv | `6a1eb9e7b570d301714bb049a928261afcabcc20` |
| Products.csv | `61c11d7f65434aa38a90ef581acb1256515c3d7d` |
| Category.csv | `b355b85ddce21146a792aa1bde71b153d1b7d42b` |
| Shippers.csv | `6c2a327c240c5454e9ed7f22d142529238563493` |
| Payments.csv | `5986647cdc1fc087d84774de1bca875235d19f1c` |
| Customers.csv | `bbb2995f0758fe5012197b8c71d897c1aca5c65f` |
| Orders.csv | `307acc9ad2f85a79d7637a7958ffd62f2a8fa594` |
| OrderDetails.csv | `ddd2fc4d61ca4cc17a49e3dd19440716f07416ae` |

## Independent fixture cases and known contractual gaps

- Q087 original source example with supplier ID 999 orphan; duplicates, NULL child keys and five-key sample cap; empty source tables must produce **seven zero rows**.
- Q088 original single shipped-before-order date example; nine different error/warning cases; 7-day and 14-day boundaries; latest **recorded OrderDate** anchor rather than wall-clock date; missing-customer signup lookup policy; empty dataset.
- **Known Q088 source/key mismatch (already reproduced in the earlier SQLite-translated checker):** when both `Orders` and `Customers` are empty, the supplied query yields **zero rows**, not the nine fixed zero-count rule rows the question explicitly requests. When Customers is empty but Orders has records, Q088 rule 9 also disappears. A native execution should confirm, not double-count, this pre-existing gap.
- There is no provider-issued verified grade for either query, and the preserved original `My solution`/ `Official solution` Markdown sections are `Pending` / `NOT SOLVED YET`. The original text-PDF pages have not been independently rendered/visually compared in this run. A source-backed supplied key is **not** automatically an authenticated provider official solution.

## Evidence-level gate and status

- **Indexed** and **statement inspected**: both records already previously counted; do not increase distinct inspected-question total.
- **Synthetic test passed**: await independent execution logs from the exact matching repository main commit. Q088's known zero-rule mismatch is a *reproduced contract failure*, not a passing source contract.
- **Full original-source output checked**: only after CI demonstrates complete-row agreement with the independent Python reference for both Q087 and Q088 on all eight source CSVs; no new `official answer verified` tally is awarded from this alone.
- **Official answer verified**: **NO**, the answer file is supplier-attributed only; independent provider authentication absent.
- **Learner independently solved**: **NO**; historical learner attempts/progress remain unchanged.
- **Conservative supplied-key clean replay tally:** previously **94/205**; no automatic increase from the two previously inspected questions or a Q088 known contract failure.
- **CI and scope:** exact-main workflow/job/log verification and Git compare are still required after test and documentation commits; do not mark completed merely because a workflow started.
- **Unresolved globally:** original PDF page visual/parity, full 205-question contract/output review and source-provided answers, Bosscoder SQL/Python and mentorship, W3Schools, other DE curriculum, licensing/PII, final all-source concept/integrity signoff. **Issue #1 stays OPEN.** Pending ChatGPT Library learner-study record and later study remain **UNSYNCED** until the complete independent audit and separately successful post-sync CI.
