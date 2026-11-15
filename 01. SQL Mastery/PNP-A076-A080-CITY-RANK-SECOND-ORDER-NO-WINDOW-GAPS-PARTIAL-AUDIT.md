# PNP Advanced A076–A080 — original-source semantics and bounded differential review (PARTIAL, 15 November 2026)

## Scope and provenance

Independently reopened and read all five preserved original Markdown records below, including full task, seven-table schema, PDF source attribution, archive-authored illustrative input/output, and unchanged **NOT SOLVED YET** / learner SQLite **Pending** / learner SQL Server **Pending** / displayed official **Pending** fields. Original Git blob SHAs were matched to current Git tree and pinned in [read-only checker](../scripts/check_pnp_advanced_76_80_ranking_gap_source_contracts.py). Each was previously **indexed and statement-inspected** in the A071–A080 tranche: **zero new distinct inspected questions**. PDF page numbers are archive attributions, not independent rendered-PDF verification.

| ID and source page attribution | Original immutable Git blob | Archived illustration reproduced by reviewer | Unresolved vendor semantics |
|---|---|---|---|
| A076 top two customers by city spend, p.15 | 6b87c321406a65cdcdc346a81fe554877da20752 | Delhi 4=40; Pune 1=100 and 2=80 | Order amount vs item/payment grain, status/refunds, no-order customers, NULL city, ties and ordering |
| A077 second newest order per customer, p.15 | 3851825388394342b08a04c3b8c7ce11fdd80c91 | Customer 10 second ID 2, 2026-01-05, amount 20; single-order customer excluded | Same-time ties, NULL and offset-aware timestamps, second row vs second distinct date, cancellations |
| A078 top three salaries per dept without window function, p.15 | 77c072224bf2f069b2468f2f299e7ca75f86f0d8 | Dept 10 employees 1/2/3 salary 100/90/80 and dept 20 employee 5 salary 60 | Three employees vs three distinct salary levels, ties, NULL salary/dept and performance; reviewer chooses top **three distinct salary levels** using correlated COUNT DISTINCT, not a provider key |
| A079 whole latest order per customer with no CTE, p.15 | 390c1f009ed8cc0c101a047f32e74946bdf6c644 | Latest order 2 (cust 10, delivered, amount 20) and 3 (cust 20, pending, amount 30) | Tie-break, NULL/offset timestamp and status; reviewer uses derived ROW_NUMBER with no CTE |
| A080 missing order ID ranges, p.16 | b3741537d5ed13dd50ba5df11023ed7db542a60e | Existing 1,2,5,8 => missing (3,4) and (6,7) | Bounds, duplicates, NULL/negative IDs, integer overflow; reviewer returns only internal gaps between observed min and max |

## Verification levels

- **Indexed:** five IDs already present in 205-question source index; zero new source IDs credited.
- **Statement inspected:** original Markdown text, local illustration and pending historical fields read with immutable blob check. Original Advanced PDF pp.15–16 rendered content remains **unverified**.
- **Illustration replay / synthetic:** [18-method read-only checker](../scripts/check_pnp_advanced_76_80_ranking_gap_source_contracts.py) contains one immutable-source/pending-state guard, five archived Markdown illustrative fixtures, five reviewer policy/boundary probes, five independent Python-oracle differential sweeps (**81 city/spend + 256 second-order dates + 256 salary levels + 256 full latest-row dates + 256 subset/gap fixtures = 1,105 synthetic combinations**) and two tie/bounds probes. Auditor-authored SQLite SQL only. Exact matching-current-main GitHub Actions logs must be inspected before claiming passing methods.
- **Official answer verified:** zero newly authenticated supplier MySQL 8 answers, grading or expected rows. Conservative original supplier-key replay remains **94/205** overall.
- **Learner independently solved:** zero new independently completed learner questions or mastery. Historical fields remain unchanged.

## Outstanding and preservation guard

Original PDF rendered pp.15–16, full supplier datasets, official MySQL8 SQL/output and provider grading are not authenticated. Reviewer tie, NULL, cancellation and id-domain choices are explicitly **hypotheses**, not supplier answer defects. Full 205-question PNP semantics/keys, remaining mentorship Python/Bosscoder/W3Schools/other DE content, licensing/privacy and source-to-concept signoff are incomplete. No original archive, historical learner attempt/progress or canonical foundation note may change. Keep GitHub Issue #1 OPEN.

ChatGPT Library /Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md and later interactive learner evidence remain **UNSYNCED with GitHub** until independent full audit signoff and successful CI; only then compare canonical notes, make separate minimal study-sync commits and verify separate post-sync CI.
