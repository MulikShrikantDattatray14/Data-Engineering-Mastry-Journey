# Migration control / preservation checklist

## Existing sources (immutable during migration)

1. [Data-Engineering-Mastry](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry) — 552 files / ~29.07 MB at initial tree inventory. Includes SQL Bosscoder, PNP content, original PDF/ZIP/CSV/XLSX assets, Python 80-page source PDF, and 76 Python source-aligned lesson entries. All 552 original source files remain unchanged in the old repository, which is pinned here as a Git submodule at `99. Reference Materials/Original Mastery Repository`.
2. [data-engineering-journey](https://github.com/MulikShrikantDattatray14/data-engineering-journey) — 192 files / ~0.98 MB at initial tree inventory. Includes study history, dashboard, plans, progress JSON, Bosscoder lecture source-audit notes and reviewed work. All 192 files are copied into `99. Reference Materials/Legacy Journey Snapshot/` and SHA-verified against the original.
3. [W3Schools Python](https://www.w3schools.com/python/) and [W3Schools SQL](https://www.w3schools.com/sql/): external official source links only, not scraped/copied lesson pages.
4. ChatGPT Study Mode: verified concepts and original corrections; keep concise novel learning in canonical note, detailed attempts in separate evidence.

## Non-destructive migration rules

- Never delete, overwrite, rename, or force-push the source repositories as part of initial migration.
- Preserve binary materials byte-for-byte, and record old→new paths and SHA/size before declaring migration complete.
- Link to existing source-backed files; never create a second lengthy conceptual explanation simply because another course taught it.
- Do not mark an originally provided Bosscoder/PNP question solved without independent submitted code and verified review.
- Verify every original file has either an untouched resident copy or a verified archived snapshot and a traceable mapping.
- The study progress record must retain real progress only, no invented work on Diwali Nov 7–8.
- Complete source-to-topic coverage auditing for SQL, Python 80-page PDF, seven Bosscoder lecture PDFs, and W3Schools before any “nothing missed” certification.

## Next migration gates

- [x] Both source trees inventoried.
- [x] Staging branch created in existing repository (original main untouched).
- [x] All 192 Journey files snapshotted, with exact path/blob SHA reconciliation (192/192).
- [ ] Every canonical topic linked/mapped to all four sources and unique gaps merged (eight Python canonical foundation chapters, SQL Joins/NULL and one progressive PNP P006 example are published; exhaustive content deduplication remains outstanding).
- [ ] Full functional links, code snippets and visual checks (new repository notes and source hashes checked; complete lesson audits pending).
- [x] New public `Data-Engineering-Mastry-Journey` repository created by user and populated with unified topic notes, inventories, the 192-file Journey archive, and a pinned Mastery source submodule.
- [ ] User-approved final switchover after verification.

## Integrity result


## Current new-repository transfer result

- **Journey archive:** 192/192 files are copied into this repository and their Git blob SHAs match the originals exactly.
- **Original Mastery:** all 552 source files remain in the original repository, now linked here as a Git submodule pinned to commit `bef07ec3e20825eb8e29bd9afc9f6d7ad8c77e3a`. Binary PDFs/ZIPs are accessible through that submodule but are **not physically copied** into this repository's Git object store.
- **Subject indexes:** 205 distinct PNP SQL question IDs, Bosscoder SQL problem index, all 80 Python mentorship pages, seven Bosscoder lecture audits, and 36 official W3Schools Python topic links now have navigation pages.
- **Conceptual consolidation:** eight initial Python foundation chapters, SQL Joins/NULL, and one detailed SQL P006 solution are canonical examples. Comprehensive four-source content reconciliation is **not yet certified**.

## Latest quality gates

- **Automated validation:** [most recent passing repository integrity run](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/workflows/validate-learning.yml). It checks the 192 copied Journey Git blob hashes, the fixed original-Mastery submodule SHA, 76 mentorship lesson pages, 205 unique PNP SQL IDs, canonical progress data and relative Markdown links.
- **Canonical progress:** `10. Learning Progress/daily-progress.json` is now the active tracker read by `docs/index.html`. The original historical JSON remains immutable in the Legacy Journey Snapshot.
- **Four-source concept mapping:** [Source Coverage Matrix](<99. Reference Materials/SOURCE-COVERAGE-MATRIX.md>) now distinguishes concept-specific source links from verified mastery and flags remaining gaps.
- **Open migration completion tracker:** [Issue #1](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/issues/1) records the remaining topic audits, link/output verification, PDF/submodule durability decision and final source coverage. **This repository is not certified fully consolidated.**

## Dashboard intentionally discontinued

The user opted out of any dashboard feature. The active `docs/` site and `.github/workflows/deploy-pages.yml` have been withdrawn from the working tree. GitHub Pages does not need to be enabled. Historic dashboard assets in the immutable Legacy Journey Snapshot remain preserved as reference only. The canonical learning progress record is `10. Learning Progress/daily-progress.json`, complemented by GitHub Markdown notes and ChatGPT Study Mode accountability.

## New canonical content review

- [x] Published eight additional concise SQL concept foundations with source preservation links and testable sample tables.
- [x] Independently checked eight associated SQL example outputs against SQLite (SELECT, grouping, aggregates, CTEs, correlated subqueries, strings, windows, recursive CTE).
- [x] Published four more Python source-aligned conceptual reference chapters (comprehensions, generators, pandas, idempotent ETL/data quality), not labeled as completed Study Mode work.
- [x] Added original visual diagrams for SQL grouping and cumulative window totals.
- [ ] Finish detailed per-source line and exercise auditing. Existence of notes does not prove all distinct source nuances were consolidated.
