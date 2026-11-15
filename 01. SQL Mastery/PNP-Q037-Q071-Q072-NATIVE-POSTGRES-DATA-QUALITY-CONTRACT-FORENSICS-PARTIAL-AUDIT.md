# PNP Q037, Q071 and Q072 — independent native PostgreSQL source-key forensics (PARTIAL)

**Date:** 16 November 2026. **Scope:** preserved PNP Foundation PDF-derived question statements and the separate supplied PostgreSQL answer-key archive. This is an **additional native-engine and integrity edge-case layer** on top of earlier SQLite source-key/quality fixtures. It is **not three newly discovered questions or newly unique supplied answers**. Original archives, historical learner attempts and canonical notes remain unmodified.

## Independently checked immutable sources and evidence tier

| Original input | Git blob SHA | Evidence tier |
|---|---|---|
| P037 statement, attributed to PDF pp.63–65 | 13de904886a87807a7c8ea3dc6efe0a6b538c670 | Indexed, original statement inspected |
| P071 statement, attributed to PDF pp.130–132 | d2cae3c82004124d3fe445ea5b65eb664b0ff952 | Indexed, original statement inspected |
| P072 statement, attributed to PDF pp.132–134 | 62250373aafa5402aa879a731f4fafe40165a7f4 | Indexed, original statement inspected |
| Bundled supplied PostgreSQL key, all_100_solutions.sql | 7912c8e676621c513e0b635a40c6ee299404676e | Supplier SQL exists, unmodified key replay targeted on native PostgreSQL 16 synthetic fixtures |

Each original question record still explicitly reads NOT SOLVED YET; learner SQLite and SQL Server sections Pending; official display section Pending. Source PDF pages were **not** visually revalidated this pass. Earlier source-pinned Q033–Q040 and Q065–Q072 SQLite supplied-key reviewers already included these IDs, as did general data-quality checks. No old evidence is counted twice.

**Read-only executable reviewer:** [Native PostgreSQL Q037/Q071/Q072 original-key forensics](../scripts/check_pnp_q037_q071_q072_native_postgres_forensic.py). It hashes all four preserved inputs, extracts **exact original SQL** (no dialect translation), tests source-illustrative rows and reviewer-created cases in disposable PostgreSQL 16 temporary tables, and explicitly checks independent orphan/NULL diagnostics. It neither submits official answers nor modifies source records.

## Independent statement/answer contract findings

### Q037 — payment-allowlist report is not a complete foreign-key integrity proof

The original scenario says Allowed='No' but its illustration uses Y/N; supplied SQL intentionally accepts trimmed, uppercased 1, TRUE, T, Y, YES, rejecting NO, blanks and NULL. Original three-method illustration; multi-order header value; unknown/blank flags; and NULL header amounts are covered.

**Critical synthetic counterexample:** Orders has an 80-value order referencing nonexistent PaymentID=999, while Payments includes only allowed and unused disallowed methods. The unmodified source SQL displays zero violations. A separate auditor-only anti-join returns the orphan order. The original task explicitly requests *one row per Payments method*, so these rows are not a literal answer-format violation; the report alone nevertheless **cannot prove all order payment references are valid**. FK constraints or a separate orphan audit are needed before claiming quarterly completeness. This is a documented policy/integrity limitation, not an authenticated supplier-answer defect.

### Q071 — deterministic email deduplication but registration date uncertainty

Source requires lowercasing and trimming Email, excluding blank and NULL, keeping earliest DateEntered with lower CustomerID as tie breaker. Replay covers its original four-row illustration plus synthetic case/space, missing email and same-date IDs. The supplier key explicitly orders DateEntered NULLS LAST: for three matching accounts with dates NULL, 2026-01-01, NULL, the dated ID 2 survives. That is a consistent **supplier policy**, not independent proof a NULL registration was later. Production merges need an approved unknown-date handling decision. Dialect collation/Unicode and original customer PII are not audited here.

### Q072 — destructive consolidation cannot be justified with unknown keys, suppliers or quantities

Original source wants every repeated (OrderID,ProductID) line, its 1-based position, count, quantity and either split/keep or consolidate first/remove rest. Replayed its original four-line example.

- **Unknown supplier:** Source uses COUNT(DISTINCT SupplierID), which excludes NULL. A supplier 7 plus NULL therefore recommends consolidate/remove; even two NULL suppliers recommend consolidation. That is not proof these units came from the same supplier.
- **NULL group keys:** GROUP BY finds repeated rows where OrderID or ProductID is NULL, but equality joins back to the grouped key lose the entire group from the reported result. Actual Commerce v2 NOT NULL/PK constraints need independent confirmation before assessing business impact.
- **NULL quantities:** SUM ignores unknown quantity. A pair with NULL and 5 yields total 5 and remove instruction, even though complete quantity is not known. Such destructive cleanup requires a separate validation gate.
- Three non-NULL same-supplier lines correctly sort by OrderDetailID, with first line absorbing a total of 60.

These are **synthetic source-key contract probes**, not authenticated provider grader results or independently solved learner coursework.

## CI evidence, scope and remaining blockers

The 15-method native PostgreSQL 16 reviewer has two provenance/runtime checks, four Q037 checks, three Q071 checks and six Q072 checks. **Its integration commit and latest documentation-head require independent exact-SHA GitHub Actions checking before any PASS is claimed.** All fixture rows are tiny auditor-controlled inputs, not original Commerce v2 datasets. New distinct supplied-key verification count **does not increase**: conservative supplied-key tally remains **94/205**. Zero new authenticated official answers, independent learner submissions or mastery.

**Still OPEN:** original PNP PDF rendered-page parity and original full dataset constraints/output; other 205-question semantic checks, Academy/provider grades, the remaining Python/Bosscoder/W3Schools/DE syllabus, public redistribution rights, PII/binary scans and comprehensive source-to-concept/integrity signoff. GitHub Issue #1 remains OPEN.

**Post-audit learning-sync gate:** the independent ChatGPT Library record at /Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md and later learner study remain UNSYNCED from GitHub until fully independently signed-off audit, passing audit CI and separate learning-sync plus CI. This audit did not modify any interactive study records.
