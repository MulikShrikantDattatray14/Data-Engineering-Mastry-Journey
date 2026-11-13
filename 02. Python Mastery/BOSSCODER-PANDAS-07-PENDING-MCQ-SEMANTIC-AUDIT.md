# Bosscoder pandas Lecture-07 MCQ Q01–Q10 semantic audit — PARTIAL

**Independent review: 13 November 2026.** This audit concerns ten preserved *public Journey-derived paraphrases* of private Bosscoder Academy questions. It is NOT authentication of the Academy screenshots, a correct-option list, learner participation or official grading. The [read-only source-pinned checker](../scripts/check_bosscoder_pandas_07_pending_mcq_semantics.py) verifies the original Git blob hashes, four original choices, original Pending learner status and bounded behavior. Previously audited [21-page PDF and teaching notes](BOSSCODER-PANDAS-07-INDEPENDENT-AUDIT.md) and [17 public-note code fences](../scripts/check_bosscoder_pandas_07_notes.py) are separate evidence.

| Q | Original derivative Git blob SHA-1 | Independent statement/output check and limitation |
|---:|---|---|
| 01 | ba6627cc4500c4193f19d286e3774c1b8c080333 | Literal stored forward-fill code replay; five positional labels checked. **Archived options 1 and 3 are identical**, so option-position authentication remains ambiguous. |
| 02 | b0810b24d1d62515d3579f4a9fc99e585ef4e26f | Literal label-inclusive loc source code replay; independently compared to exclusive iloc slice. |
| 03 | 1469fcb14bd69ee230f67b66dfef1d0fbc201e4e | Literal per-column apply(max-min) replay; independent all-missing-column fixture. |
| 04 | fbbdf5790b18a85028e2d11c2de7be038efb98d3 | Literal groupby transform mean replay; synthetic null-group default versus dropna=False boundary. |
| 05 | 2a3aaed9911130cbcaf2cc0aeff97781933515ff | Literal dropna/reset_index replay; checked fresh index and float coercion. |
| 06 | 178900492e03848e7d03e1e76b29f2c9a2c7413c | **Not independently runnable standalone:** original snippet has undefined df; no dtype, size, NumPy backing, benchmark protocol, platform or rubric. Reviewer numeric fixture only checks equality, **not speed winner**. |
| 07 | 1fec8f9c921a1dfd1c2bbe5f69829fcf3f23f462 | Literal pyplot legend(best) executed headlessly; inspected legend artist and location code; no fixed pixel placement guarantee. |
| 08 | 317614bb14da79e16f5dba88b82c096664488ccb | Stored Seaborn lineplot executed **with injected earlier-notebook pandas alias**; independent isolated execution raises missing-pd NameError. Line artist coordinates checked, not original plot pixels. |
| 09 | 6795c608475326184f022fc3cbd739dec5dc190a | Stored two-row subplot executed **with injected earlier-notebook plt alias**; isolated NameError independently observed. Vertical axes and artists checked. |
| 10 | 40791f4b593e59d07640372e348f92676e6ae307 | Stored DataFrame bar-chart executed **with injected earlier-notebook pd alias**; isolated NameError observed. Three bars, heights and labels checked. |

**Evidence taxonomy:** All ten were already **indexed**; all ten statements/code/options and status fields are now **individually inspected** and Git-blob-pinned. CI execution, if independently green, establishes only **derived-code output verification and reviewer-created synthetic test passes**. Official Academy answers verified: **NO**. Learner independently solved: **NO**. Platform grades: **UNVERIFIED**. No option has been assigned, no historical student attempt or progress changed and no canonical foundation chapter rewritten.

**Blocking provenance:** Public records are screenshot paraphrases, not private original Academy question screenshots. Original PDF/notebook order, private data and plotting pixels are unavailable in GitHub CI. The duplicated first question options and under-specified performance question cannot be resolved from this derived archive. Missing imports are documented notebook-context dependencies rather than silently modified archived source.

**Open whole-audit scope:** 205 PNP source SQL original PDF/dataset/official parity, Python mentorship complete original output parity, remaining Bosscoder and W3Schools sources, other DE subjects, global integrity/source-to-concept and licensing/privacy signoff remain outstanding. Issue #1 stays OPEN. The separate ChatGPT Library learner-study record and later interactive practice remain UNSYNCED with GitHub until full signoff and separate post-sync CI.
