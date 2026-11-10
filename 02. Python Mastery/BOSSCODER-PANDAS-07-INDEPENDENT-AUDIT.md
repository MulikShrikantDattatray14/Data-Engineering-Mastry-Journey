# Independent primary-source audit — Bosscoder Python Lecture 07: pandas & visualisation

**Audit date:** 10 November 2026. **This is source evaluation, not learner coursework or Academy grading.**

## Evidence tiers / source privacy

- **Primary original:** User-supplied *private* `Pandas and Data Visualisation - Colab.pdf`, **21/21 pages** independently examined as extracted text and rendered-page contact sheet, including output figures and the nearly empty last page. **1,391,458 bytes; SHA-256 `eee04ef762e45a9bf82952a885516a336e377edbe61e8676f3beb996f679fd15`.** File stays in the private user Library, **not** GitHub; do not publish the linked notebook or its original `tips.csv` financial/payer fields.
- **Original PDF-selected execution:** **40 locally passing, auditor-reconstructed behavior/state/structure assertions** across examples on pp.2–10 and 16–20, on **pandas 2.2.3 / NumPy 2.3.5 / matplotlib 3.10.8 / Seaborn 0.13.2**. The count includes a clearly **synthetic CSV round-trip**, and plotting checks use synthetic inputs rather than source `tips.csv`/downloaded Seaborn datasets. Several checks are **API behavior**, not literal screenshot-output comparisons. **NOT** the original private `.ipynb` executed cell-by-cell, nor chart pixel-for-pixel parity, official answer grading, or student completion.
- **Immutable archived *public Journey-derived* notes:** Individually opened and inspected all three note chapters, containing **6 + 7 + 4 = 17 Python code fences**. Their original Git **blob SHA-1** values are pinned by `scripts/check_bosscoder_pandas_07_notes.py`; the runner executes **all 17** in source-chapter sequence, asserts selected stdout/state behavior and **four** chart-structure contracts. This is a **different** evidence category from the private-PDF 40 local checks.
- **Ten screenshot-derived Academy question records:** Individually inspected `q01.md`–`q10.md`, their statements, code examples, four displayed options, exact immutable source hashes and **pending/unverified** learner/grade fields. Pinned CI validates all ten **without attempting, answering, grading, revealing option keys, or changing any original assignment**. Q01 genuinely contains duplicated options; this is preserved.
- **Auditor-synthetic boundaries:** Seven distinct local passing checks, replayed in CI, cover duplicate index labels/reindex failure, label versus position slices, join multiplication/validation, null groups and transform shape, invalid/tz-aware dates, CSV/JSONL/SQLite round-trip, and headless lineplot structure. **Not** original PDF example or an Academy key.
- **CI gate:** The private original PDF and private dataset **cannot** be exercised by public GitHub Actions. Treat the public-note/MCQ/synthetic step as passed only after verifying a successful exact-HEAD run. Do not call the audit complete even when this step passes.

## Original source page-by-page observation (the displayed document, not the notebook cells)

| PDF page | Independently observed content | Verification and caveat |
|---:|---|---|
| 1 | Agenda, pandas/NumPy positioning, installation, Series and custom index constructors | Text and render read; notebook output shows pandas **2.2.2**, not a portable version guarantee |
| 2 | Series labeled output, DataFrame constructors, DataFrame print, `Index` and columns | Original Series and DataFrame values reconstructed; **source claim that Index ensures unique labels is false** |
| 3 | `head`, `tail`, `info` with five employees | Checked first/last/non-null behavior; memory/dtype repr version-dependent |
| 4 | `describe`, `loc`, `iloc`, single-condition filter | Checked described mean and age filter; keep explicit label/position distinction |
| 5 | Three Boolean filters in one notebook cell; `isin`, inclusive `between`, string methods | Reconstructed actual outcomes; displayed output is the **last expression's result**, not separate printed outputs for all three Boolean expressions |
| 6 | `query`; new/drop/rename/reindex columns; null filling/deletion; multiple-key and different-key merges | Tested source-literal queries and join keys; examples rely on earlier mutable notebook `df` state |
| 7 | Suffix merges, `concat` both axes, group mean and whole-group `filter` | Validated reconstructions; `concat(axis=1)` aligns on index, not arbitrary primary keys |
| 8 | Date conversions, `.dt` components, `Timedelta`, I/O overview | Original visible date outputs tested; production parsing/timezones need explicit policy |
| 9 | CSV, Excel, JSON, SQL read/write snippets | Source refers to **missing external files/engine**; only a *separately labeled* synthetic CSV I/O contract run. JSON-lines writes need corresponding `read_json(lines=True)` |
| 10 | Vectorized arithmetic, numeric downcast, dtype-at-read, early filter, in-place drop | Original arithmetic/downcast checked; `inplace=True` does **not** prove lower peak memory and missing placeholder column/path cannot run verbatim |
| 11 | Matplotlib install/output, external `tips.csv` metadata and initial categorical scatter | Full source render checked; **244-row dataset with payer/card/payment fields** absent from private runner and unsafe to republish |
| 12 | Colored/sized scatter and `colorbar`, original chart images | Visuals inspected; exact figure pixels and external `tips.csv` not reproduced |
| 13 | Two-series line plot and histogram | Render inspected; **line chart labels horizontal axis “Day” while source plots positional index**, a misleading label |
| 14 | Seaborn dependency/output and first scatter example | Render/source code read; calling with a `data` DataFrame is common but not universally required when arrays are supplied |
| 15 | Seaborn `hue` scatter and `lineplot` using externally loaded tips | Source-generated plots visually checked, external data not recovered/replayed |
| 16 | Seaborn barplot and start of generic matplotlib line chart | Figure inspected; barplot can aggregate data, rather than preserving each row as a bar |
| 17 | Completed line and pie examples | Locally reproduced line coordinates and four pie wedges; no image-pixel parity claimed |
| 18 | Box/IQR/whiskers explanation, code and first heatmap example | Locally checked box artist structure; original 25-number source array transcribed |
| 19 | Heatmap continuation, violin plot description and source code | Locally checked synthetic heatmap annotations and synthetic violin artists; violin source uses external data |
| 20 | Seaborn violin warning screenshot, `pairplot` of externally loaded iris | Source **FutureWarning: palette without hue** observed; synthetic pairplot structure checked; no original iris plot pixel reproduction |
| 21 | Last displayed page nearly blank, with footer | Visually checked, not counted as an extra executable example |

## Source problems and actionable distinctions

1. **Incorrect/oversimplified original source claims:** Labelled pandas indexes are *not necessarily unique*, and `Series` with `object` dtype can contain mixed Python objects despite the blanket “only one type” sentence. Use `.loc` versus `.iloc` rather than relying on ambiguous integer-key access for non-integer indices.
2. **Notebook-cell state / displayed-output confusion:** PDF p5 combines three standalone filtered DataFrame expressions but displays a single last-expression result. Later cleaning/renaming snippets depend on which `df` is current; fresh local fixtures were used, not asserted original cell-order parity.
3. **External data/blockers:** `data.csv`, `data.xlsx`, `data.json`, SQLite `database.db`, `tips.csv`, and Seaborn download-dependent datasets are not part of the inspected private PDF bytes. The public repository must not contain the source sample's payer/card-number columns/data. Original chart pixel equivalence and Excel/SQL source-file output remain **not verified**.
4. **Meaning differences:** GroupBy `mean` and `filter` differ from per-row `transform` (the latter is present in archived notes/MCQ Q04); duplicate-key merges change row grain; pandas `groupby` normally drops NULL keys; `sns.barplot` summarizes values by category; `df.to_sql(...if_exists="replace")` would overwrite an actual table.
5. **Version-sensitive details:** Seaborn p20 `palette` deprecation warning and Matplotlib chart output may change. External PDF reports Pandas 2.2.2, NumPy 2.0.2, Matplotlib 3.10.0 and Seaborn 0.13.2; the **local** selected contract tests used versions above, while **CI** uses pinned pandas 2.3.3, matplotlib 3.10.8, Seaborn 0.13.2 and a NumPy 2.x install. This is compatibility sampling, not all-version certification.
6. **Evidence quality:** Source page text/render was read in full, but exact source `.ipynb` cell order/hidden state, original platform screenshot choices/grades, external dataset content and image-by-image reproducibility are not available in this scope.

## Archived question inventory — status evidence, not answer verification

| Source q | Subject; original Git blob SHA-1 | Learner / official outcome |
|---:|---|---|
| 01 | Series forward-fill/reindex; `ba6627cc4500c4193f19d286e3774c1b8c080333` | Four options, includes duplicate option; Pending / Unverified |
| 02 | label-inclusive `.loc` slice; `b0810b24d1d62515d3579f4a9fc99e585ef4e26f` | Pending / Unverified |
| 03 | `apply` min/max span; `1469fcb14bd69ee230f67b66dfef1d0fbc201e4e` | Pending / Unverified |
| 04 | GroupBy `transform` mean; `fbbdf5790b18a85028e2d11c2de7be038efb98d3` | Pending / Unverified |
| 05 | `dropna().reset_index`; `2a3aaed9911130cbcaf2cc0aeff97781933515ff` | Pending / Unverified |
| 06 | `Series.sum` vs `values.sum` speed; `178900492e03848e7d03e1e76b29f2c9a2c7413c` | Pending; no timing guarantee |
| 07 | Matplotlib legend `loc='best'`; `1fec8f9c921a1dfd1c2bbe5f69829fcf3f23f462` | Pending / Unverified |
| 08 | Seaborn lineplot; `317614bb14da79e16f5dba88b82c096664488ccb` | Pending / Unverified |
| 09 | 2×1 subplot layout; `6795c608475326184f022fc3cbd739dec5dc190a` | Pending / Unverified |
| 10 | pandas `plot(kind='bar')`; `40791f4b593e59d07640372e348f92676e6ae307` | Pending / Unverified |

## Canonical teaching crosswalk

Already compared [pandas for Data Engineering](<10. Pandas for Data Engineering/0. Foundation Notes.md>) and [Data Visualisation](<18. Data Visualisation/0. Foundation Notes.md>) against the PDF and [archived Lecture-07 notes](<../99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-07/README.md>). Their existing source links, unique-index caveat, figure families, external-dataset privacy warning, merge cardinality, plotting aggregation and row-grain warnings capture the major practical distinctions. **No duplicate foundation chapter needed** and **no learner-interaction content synced**. This tranche did not reverify W3Schools pages; prior provider comparisons remain separate evidence.

## Remain open

The private executable original `.ipynb` and original actual CSV/JSON/Excel/SQL files; exact displayed figure pixels/output per cell; source notebook state order and source-specific runtime version; the original Academy grader/attempts for all ten MCQs; other W3Schools and DE-domain pages/examples; source licensing/privacy signoff; all **205 PNP SQL original official-answer/dataset/dialect** checks; original mentorship PDF full-render parity; audit-wide final CI and Issue #1 signoff. **Never mark 10 MCQs solved or Lecture 07 mastered because the public note checker passes.**

**Preservation/sync boundary:** This audit adds only an external evidence ledger plus CI checker/workflow/status. The existing **744 original archives, private Academy PDF, learner-history Markdown and active progress JSON remain untouched**. The separate pending user Library learning record stays **UNSYNCED with GitHub** until the *whole* independent audit and final CI signoff.
