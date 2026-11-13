# Direct upstream-source Git tree parity and stale inventory metadata correction (PARTIAL)

**Checked:** 14 November 2026. **Final commit / CI:** see [GitHub Issue #1](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/issues/1) and the associated GitHub Actions run. **Evidence tier:** independently inspected two original upstream Git trees, source archive paths and SHA, local Git tree identity; no PDF content/official-answer/learner/licensing/privacy signoff.

## Independent source-to-source comparison

Read both **original source Git repositories** using the GitHub Git trees and commit endpoints (not only the new repository's self-reported manifest). Each original tree was untruncated. Compared every original `path => Git blob SHA` against the 744 manifest entries, then separately compared their expected copied paths with the current unified repository Git tree. Found zero missing, extra or SHA-mismatched source files.

| Origin and exact snapshot | Original root tree SHA | Original blob files | Manifest paths matching original Git tree | Copied archive tree SHA |
| --- | --- | ---: | ---: | --- |
| [Data-Engineering-Mastry commit bef07ec3](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/tree/bef07ec3e20825eb8e29bd9afc9f6d7ad8c77e3a) | `8a3c3bfb7b26588fceb13bf04b9af2fdee7df46e` | **552** | **552/552** | `8a3c3bfb7b26588fceb13bf04b9af2fdee7df46e` |
| [data-engineering-journey commit 92666943](https://github.com/MulikShrikantDattatray14/data-engineering-journey/tree/92666943f5d6a223db496d4fbdc7017f195d682d) | `63b9330dcc63b6f8bfbd9ddad7a5be0bb845439e` | **192** | **192/192** | `63b9330dcc63b6f8bfbd9ddad7a5be0bb845439e` |
| **Combined** | independent snapshots | **744** | **744/744** | two exact copy subtrees |

The current unified repository source-archive subtrees have precisely the same Git tree SHAs as those upstream commits; this is stronger than checking a manifest file alone because Git tree identity covers every file path, mode, content and nested directory. The Mastery origin's **present-day main branch is not substituted** for its pinned archived source commit; the verification uses the original inventory's `bef07ec3...` baseline. The separate Journey commit was observed directly at that source repository's main when checked on 14 November; no claim is made about the historical date when individual learner attempts were authored.

## Concrete derived-metadata correction

The prior [SOURCE-INVENTORY.json](SOURCE-INVENTORY.json) Git blob `c2e03d2d9de254165806c39dc6a37fdb353fed23` still claimed **"pinned submodule"** and **"not duplicated"**, and counted `mastery_submodule_files: 552`. That narrative was stale even though all 744 `entries` already used `native_copy_sha_verified` and were correct. Replaced **only the top-level verification narrative and that obsolete summary key**, now `mastery_sha_verified: 552`. Entry paths, original filenames, byte sizes, Git blob SHA, source provenance fields and status records remain identical.

Added [read-only offline Git tree/provenance regression checker](../../scripts/check_upstream_archive_tree_provenance.py) for the two exact upstream tree SHA values, all 744 physical copied paths, accurate summary, and manifest source/method consistency. CI's source SHA guard must pass on the final commit. **A successful current CI does not prove that the remote source repos will remain unchanged**, so these source references are commit-pinned instead of relying on mutable upstream main.

## Still explicitly NOT established

- No claim that any of the 205 PNP SQL question statements, original PDFs, full datasets, Bosscoder coursework or Python mentorship exercises are semantically fully verified merely because archived bytes match.
- No new official answer authenticated, no provider grade, no independent learner completion and no mastery award.
- **No third-party redistribution authorization or full PII/privacy clearance**: public course-origin PDF/ZIP/CSV/image review and lawful public distribution remain open. Byte identity is not permission.
- Final source-to-concept coverage, actual teaching/output checks, unresolved keyed SQL discrepancies and source-authoritative grading remain pending.
- ChatGPT Library learning record and subsequent interactive learner sessions remain strictly **UNSYNCED** until independent full audit signoff and subsequent separately verified CI.

**Preservation policy:** original Mastery/Journey source archive subtrees and all historical learner statuses remain unchanged. This is a scoped provenance/metadata repair only, not a study-session sync or audit completion.
