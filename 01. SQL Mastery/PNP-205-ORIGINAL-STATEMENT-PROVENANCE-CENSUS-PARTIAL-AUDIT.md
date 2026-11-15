# PNP SQL — independent 205-file original-statement provenance census (PARTIAL)

**15 November 2026. Evidence tier: archival source-text structural inspection, NOT 205 semantic or supplier-answer verifications.** This audit reopens all **205 original preserved Markdown question records** independently of the previously written topic index. It does **not** render source PDF pages, authenticate PDF-to-Markdown sentence equivalence, execute all 205 supplier SQL solutions, validate grading, or award a single independent learner solve.

## Scope and reproducible source checks

The new [read-only 10-method reviewer](../scripts/check_pnp_205_original_statement_provenance_census.py) follows all 205 index links to their physical original Git source files, individually reads each original file's bytes and textual contract, and checks:

1. **205 unique physical Git blobs and source paths**, exactly **P001–P100 (100), A001–A100 (100), X001–X005 (5)**. All links remain inside the Original Mastery Snapshot. This is a stronger structural statement check than merely finding the topic index, but not line-by-line provider comparison.
2. Original family/number in each `# PNP Qnnn`, `# Advanced Qnnn` or `# Extra Qnnn` heading; **205 matching headings**.
3. Every record has a **nonempty original `**Task.**` statement** and a question heading, plus a sample-input/output section, schema, learner-solution section, and official-solution section. The presence of a sample does **not** establish that it is a source-provided supplier example.
4. Family-specific provenance: **P** cites the 100 SQL Interview Questions, **A** cites Advanced SQL 100 Query Questions and explains source dialect MySQL 8, **X** cites the original bundle README and expressly has **no supplied answer key**. The original index, P PDF and A PDF source blobs are immutable SHA-pinned (index `e407ada6…`, P source PDF `65b9eab3…`, A source PDF `d9788de7…`).
5. A/X original difficulty metadata is marked **estimated**, not masquerading as a supplier-assigned grade. Source examples are explicitly distinguished from grading. Historical index statuses are read but **not changed or inferred from tests**.

The source records' *index status labels* reconcile as **6 verified reattempt**, **14 previously solved baseline**, **185 indexed/pending independent verification**. These are historical **index labels**, *not* 20 newly independently demonstrated learner solves, and not proof of mastering 205 questions. The supplied-key replay total is separately and conservatively **94/205**, unchanged by these structural checks. Different status counts measure different things.

## Actual independently observed code-head CI

[GitHub Actions run 43720228334](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43720228334), head `de55f7707ac96dd7d45f7f7728c92c149e9c1fce`, **completed SUCCESS**. The original-source census validation job log (job `132830402815`) explicitly reports **all ten named `StructuralOriginalStatementCensus` methods passed**, `Ran 10 tests`, `OK`, and prints the exact 6+14+185 archived index-status breakdown. This audit also reuses the independently existing full-archive preservation and source-inventory checks, but its **own ten tests only establish structural fidelity and provenance classification**. All original files and prior learner work remain untouched.

The successful code-head workflow is **not** automatically evidence of later new documentation-HEAD CI. Check the exact live `main` SHA after this ledger and the additive migration-status entry are committed, and independently check validation, PostgreSQL, MySQL jobs and the new census log again.

## Still blocked; required stronger independent verification

- Render and visually compare *actual original PDF* pages for P001–P100 and A001–A100, compare precise statement meaning, constraints, columns and any supplier answer with each Markdown record. The original binary PDF is Git-SHA-pinned but binary identity is **not visual/content parity**. Direct raw PDF retrieval was disabled during this run; cannot claim original page parity.
- For 100 P keys, distinguish authenticated provider SQL and dataset from reviewer synthetic fixture SQL. Existing conservative supplied-key success is **94/205**, with exact unresolved problem/policy cases in Issue #1. For A, archived mention of an answer in MySQL PDF is **not authenticated provider replay**. For X, the original README expressly supplies **no official key**.
- Complete manually reasoned per-question semantics and answer/output checks where original evidence exists; compare W3Schools/Bosscoder/Python/DE source material, complete source-to-concept crosswalk, full rights/PII/binary distribution and license audit.
- Preserve source archives, historical learner solutions and all canonical notes. **No interactive-study-derived GitHub changes.** ChatGPT Library pending learning record `/Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md` and later practice remain **UNSYNCED**, gated on audit-wide signoff and separate post-sync CI.

**Disposition:** Source indexed = previously. All **205 original Markdown task-bearing records structurally read** = independently checked in this new census. Statement *meaning* vs original PDFs = **not established**. Synthetic-test/pass for these **structural** checks = ten methods, **not 205 SQL result checks**. Official answers and independently solved coursework = **no new evidence**. **GitHub Issue #1 must remain OPEN; no overall signoff.**
