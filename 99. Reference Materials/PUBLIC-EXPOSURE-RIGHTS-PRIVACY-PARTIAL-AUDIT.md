# Partial public-source preservation, licensing provenance and credential-marker review

**Review date:** 14 November 2026. **Scope:** GitHub public repository `MulikShrikantDattatray14/Data-Engineering-Mastry-Journey` at baseline `b816f428a08fc9bb9a740899b43969e6e296c7d0`. This is an **independent, bounded repository-rights/privacy review**, not approval to republish paid/course-origin documents, a legal opinion, an exhaustive personal-data scan, or comprehensive audit signoff.

## Evidence independently inspected

1. GitHub repository metadata reports **public** visibility. The complete Git tree was directly enumerated: 1,020 tracked blobs, including **744 original archived files**: **552 Original Mastery** and **192 Legacy Journey**. The preserved `SOURCE-INVENTORY.json` maps original and destination names, byte sizes and Git blob SHA. Original archive bytes are checked by the new read-only reviewer against all 744 manifest entries, not modified.
2. Four original source PDFs are publicly tracked: Advanced SQL 100-question volume (1,654,592 bytes, blob `d9788de757020c4290a5e4f3ada778252f74e889`); two identically hashed PNP SQL 100-question PDF copies (3,185,404 bytes each, blob `65b9eab3cf82e363f072dd317a7c963f03503b95`); Python mentorship source (488,120 bytes, blob `90f8abc8a0bf4c865a6b545938a2b285204a008e`). Identical binary duplicates are **not** two independently authenticated source editions.
3. Binary/structured original material additionally includes **two ZIP files, one XLSX, 16 CSV, 15 PNG and 15 JPG**. The checker verifies file counts and basic magic bytes for ZIP/XLSX and PDFs, but **does not** decode the ZIP contents, scan images for personal information, or validate PDF rights.
4. Exactly one tracked `LICENSE`/NOTICE-like file was found: [the historical Legacy Journey MIT license](<Legacy Journey Snapshot/LICENSE>), blob `d0d01053e2ae3d7e9879d8d3a2a81e36482cb9aa`. **No root LICENSE or vendor-specific redistribution authorization is evidenced in the tracked repository.** The old MIT notice is not sufficient evidence that PNP, Bosscoder or other third-party content may be publicly redistributed. It is **not** proof that permissions do not exist elsewhere; obtain and document them before rights signoff.
5. [SOURCE-COVERAGE-MATRIX.md](SOURCE-COVERAGE-MATRIX.md) and [root README](../README.md) attribute Bosscoder, PNP Mentorship, W3Schools, ChatGPT. **Attribution does not substitute for a license or express authorization.** `99. Reference Materials/README.md` describes physical preservation of 552+192 originals. However, `SOURCE-INVENTORY.json` still contains an older *pinned submodule / not duplicated* summary even though physical Git-tree entries exist. That is a **stale provenance summary**, not a missing archived file; reconcile derived inventory metadata separately without changing original sources.
6. New source-boundary checker [scripts/check_archive_public_rights_and_credential_boundaries.py](../scripts/check_archive_public_rights_and_credential_boundaries.py) tests seven independent assertions: two archive counts, 744-entry exact hash/size/path consistency, four PDF blob checks and duplicate identity, binary-format inventory, limited historic-license scope, high-confidence private-key/PAT/AWS access-key signatures in original plaintext files, and attribution text. **No text-secret finding from these specific signatures is equivalent to proving no PII, no credentials, or permitted publication.**

## Evidence classifications and unresolved decisions

| Category | Finding | Proof tier |
| --- | --- | --- |
| 744 original records | Archive path/hash/size guard added (CI result must be checked) | Indexed and independently integrity-tested, **not** semantic verification |
| Four source PDFs | Names, bytes, SHA and exact identical duplicate pair reviewed | Binary integrity only; **not** original page/image text parity or license permission |
| Legacy MIT notice | One historical own notice found, no tracked root or provider grant | Rights provenance **unverified** |
| Publicly exposed paid-course-origin files | GitHub public tree includes PNP PDFs/Bosscoder-labelled notes | Public exposure confirmed; **permission unknown**, do not allege infringement |
| High-confidence secret marker regex | Read-only scan for key block/PAT/AWS patterns | Narrow automated screen, **not** full PII/secrets audit |
| PNP SQL answers | Previous conservative 94/205 replay unaffected | **No new official key authenticated** |
| Learner status | Original Solved/Pending markers untouched | **No new independently solved coursework or mastery** |

**Blockers to record in Issue #1:** obtain redistribution rights / clear allowed public vs private distribution for PNP/Bosscoder and any imported vendor data; inspect complete contents of original PDFs, ZIPs, screenshots and structured datasets for privacy and licensing before final publication clearance; audit canonical derivative text for potentially copied proprietary excerpts; reconcile stale generated inventory summary; continue native source/answer/output parity, all 205 SQL question keys, mentorship/Bosscoder/W3/DE concept checks. These are **open**, not cleared by a green workflow.

**Repository safety:** Only additive reviewer script and this ledger, validation workflow and status/Issue #1 are permitted changes. Preserve original archive, historical student attempts/progress and current canonical foundation notes exactly. Separate ChatGPT Library study log and subsequent interactions remain **UNSYNCED** until full audit signoff and post-sync CI.
