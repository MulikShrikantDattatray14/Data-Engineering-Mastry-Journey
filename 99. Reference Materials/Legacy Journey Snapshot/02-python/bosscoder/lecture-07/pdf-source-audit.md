# PDF cross-check — Lecture 07: Pandas and Data Visualisation

**Source:** Learner-supplied `Pandas and Data Visualisation - Colab.pdf` (21 PDF pages, reviewed 2026-11-06).
**Result:** All principal PDF topic groups have matching independent public chapters. Specific source cautions and tracker corrections are below. **Student mastery and assignments remain pending.**

## PDF page-to-GitHub comparison

| PDF pages | Source subject area | Existing learning chapter |
|---|---|---|
| 1–5 | Series, DataFrame, Index; inspection, .loc/.iloc, condition/isin/between/str/query filters | [Chapter](01-pandas-fundamentals.md) |
| 6–10 | add/drop/rename/reindex, missing values, joins, concat, groupby, dates, CSV/Excel/JSON/SQL I/O, vectorization and memory optimization | [Chapter](02-pandas-transformations-and-io.md) |
| 11–16 | Matplotlib scatter/line/histogram; Seaborn scatter, line and bar | [Chapter](03-data-visualisation.md) |
| 17–21 | line, pie, boxplot, heatmap, violin and pair plots | [Chapter](03-data-visualisation.md) |

## Cautions and mismatches confirmed during PDF verification
- Pandas Index labels are not always unique, contrary to a simplistic sentence in the source.
- Classroom Pandas operations depend on prior notebook mutation; independent examples should reset state.
- The source demo's tips data includes payer/card-number-like fields; never commit such details to public GitHub.
- Seaborn source output warns against palette without hue in a future version; note that chart APIs are version-sensitive.

## Changes or additional review requirements
- PDF confirms class notebook's visualization families; no major section omitted.

## Not an assignment submission

- [ ] Learner reviews every source-aligned topic and independently reruns relevant Python exercises.
- [ ] Learner completes the corresponding Bosscoder graded assignments later.
- [ ] We verify first attempts, pitfalls and edge cases before checking mastery boxes.

**No graded assignment solutions or MCQ answer keys supplied in this audit.**
