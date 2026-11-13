# Bosscoder NumPy Lecture-06 — twelve pending MCQs: independent reviewer semantic audit

**Audit date:** 2026-11-13. **Scope:** all 12 archived, screenshot-derived *paraphrases* from `99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-06/assignments/`. This is **not** private Academy screenshot-to-answer parity or learner assessment.

## Evidence tiers and source integrity

- **Indexed:** 12/12 MCQ records existed prior to this tranche.
- **Statement inspected:** 12/12 derivative public question prompts, concept tags, displayed four-option sections and original *Pending / Unverified* history each read independently. Immutable Git blob IDs are pinned in [the read-only 13-method reviewer checker](../scripts/check_bosscoder_numpy_06_pending_mcq_semantics.py).
- **Synthetic tested:** 12 distinct auditor-authored NumPy behavior methods plus a 12-source/status/hash guard. These model the *topic* and stress meaningful boundaries; they do **not** execute the original unseen Academy screenshot code. CI status must be verified against the exact workflow-enabled commit.
- **Official answer verified:** **NO (0/12)** — original private screenshot programs, authenticated Academy answer keys, grader/hidden tests and learner platform submissions have not been provided as reproducible input.
- **Learner independently solved:** **NO new credit (0/12 existing tracker reviews)** — no saved original learner selections. Historical 0/12 reviewed remains unchanged; no mastery or duration inferred.
- The 26-page original NumPy PDF has its own separately documented auditor reconstruction of 33 source-visible contracts. It is **not** these twelve MCQ programs. [Prior PDF evidence](BOSSCODER-NUMPY-06-INDEPENDENT-AUDIT.md).

## Per-question immutable source and boundary evidence

| ID | Original public derivative blob SHA-1 | Individually inspected prompt | Auditor-only executable contract / limitations |
|---|---|---|---|
| Q01 | `61b02ca73bd1e3a0722dfe3fdfb58cf6ddea9f08` | Integer/float inference from array constructors | Default integer *width* is platform-dependent; float defaults to 64-bit. Explicit int32 and mixed-number coercion modeled; screenshot's constructor values absent. |
| Q02 | `5654018fb5d3f4de542b997e81ab67dd2014590d` | `zeros` and `ones_like` with dtype | Reviewer `(2,3)` array yields integer ones, whereas no dtype override retains float; exact original constructor unverified. |
| Q03 | `4c776db42ce60d310def064e062d6f243b374294` | Reshape eight values with inferred dimension | `(2,-1,2)` shape and contents asserted; invalid size and two `-1` dimensions reject. |
| Q04 | `d9d901e3aed521e2a8956d87827d3d12f1672007` | `ravel` and source mutation | Contiguous `ravel` shares memory; negative-stride view may yield a copied `ravel`. Unqualified “ravel always views” would be wrong. |
| Q05 | `48e3d40f69891342ef883fbd209a78d19db2d7b6` | `np.sort` result vs original | Function creates a sorted result without mutating original; ndarray `.sort()` mutates in place. |
| Q06 | `0ca931a6cacc044a1897454919d016cb63367435` | Parity-based Boolean masking and assignment | Fancy-mask selection copies; masked assignment mutates source. Independent `0..5` fixture. |
| Q07 | `9827c7cbe0b0ebe6ae3fb2dccf91771d5f6bcc87` | Reordered integer-array indexing | Order preserved `[3,1,2,0]`; result does not alias original; out-of-range index raises. |
| Q08 | `6d7d65662d42784278f56a94acd281869ea0bfdc` | Final matrix rows / reverse columns | Bounded `3x4` slice output and shared-memory mutation asserted. |
| Q09 | `bb8fcb06c9a957347657a9d6ab3e2cbbc74e267d` | Elementwise vector multiply vs `@` | Product `[4,10,18]` vs scalar `32`; 2-D operands instead yield `(1,1)` output. |
| Q10 | `4e3d5dc6d658a8462344bc06e8daec2df2bbd3d8` | Vector broadcasting over matrix | Explicit integer `2x3` scenario and incompatible `(2,)` boundary; *default* `np.ones` creates **float**, which can conflict with implied integer rendering in options. Original dtype code missing. |
| Q11 | `30ae521de20e6a463f3aaae570226afffed59a45` | `vstack/hstack` with 1-D arrays | `(2,2)` vs `(4,)` shapes; 2-D stacks grow existing axes, not necessarily new dimension. |
| Q12 | `40377a8acd5cd2651e41d877a64b32455589592f` | Structured name/age, string and mean | `S3` yields `b'Amy'`, `U3` yields `'Amy'`; numeric mean 27.5 modeled. Original dtype missing and determines correct presentation. |

## Distinct failure/ambiguity outcomes

- **Source originals unchanged; synthetic boundary tests only** — no claimed failure of an Academy official answer.
- **Q01:** exact integer bit width cannot safely be inferred from an omitted constructor/environment (e.g. int32 vs int64).
- **Q04:** the derivative MCQ may assume C-contiguous input; ravel does not *universally* promise a view.
- **Q10:** original `np.ones(..., dtype=...)` syntax is missing. Printed integer choices cannot establish original output dtype.
- **Q12:** bytes-vs-Unicode string behavior depends on original structured dtype field definition. Original exact expression is omitted.
- Across **all Q01–Q12**, public records explicitly say to consult private screenshots for exact code/options/values; they are not primary evidence for authentic Academy grading.

## Source-to-concept, licensing, preservation and next work

- Topics map to preserved lecture-06 chapters `01-arrays-creation-and-shapes.md` (Q01–Q04), `02-indexing-and-computing.md` (Q05–Q08), `03-manipulation-broadcasting.md` (Q09–Q11), `04-structured-arrays.md` (Q12), and the existing canonical NumPy Foundations. This is a *bounded per-question crosswalk*, not full global source-to-concept signoff.
- No private screenshot/PDF content, original archive files, historical learner attempts/progress or canonical foundation notes modified; only audit-owned checker/ledger/workflow/status touched by this tranche.
- Original Academy screenshots, execution state, official keys, platform grading and privacy/distribution permission remain blockers. Request only authorized verification; do not copy private proprietary course content into the public repo.
- The source-proven PNP SQL bounded supplier-key tally remains **94/205** clean unique IDs, **unchanged** by this NumPy work. Full SQL PDF/dataset parity, remaining Python/Bosscoder/W3Schools/DE source checks and final licensing/integrity signoff remain pending.
- GitHub Issue #1 stays **OPEN**. The separate ChatGPT Library learner-study record `/Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md` plus later interactive practice are **UNSYNCED with GitHub** until the independent full audit, final CI, and separate post-sync validation. No new independent coursework or mastery is claimed.
