# Lecture 7 — Pandas and Data Visualisation

**Source scope:** The complete user-supplied Bosscoder Pandas and Data Visualisation notebook (940 parsed lines) plus 10 MCQ screenshots.
**Authorship:** Original beginner-friendly study explanations and fresh demonstrations, not a verbatim republication of class materials.
**Documentation:** Organized. **Practice/mastery:** Not assessed. **MCQs:** 0/10 attempted/reviewed.

## Study chapters
1. [Pandas structures, inspection, selection and filtering](01-pandas-fundamentals.md)
2. [Cleaning, merging, grouping, dates, IO and performance](02-pandas-transformations-and-io.md)
3. [Matplotlib, Seaborn and chart selection](03-data-visualisation.md)
4. [Full no-skip source audit, error checks and PNP mapping](04-coverage-audit.md)
5. [All ten graded MCQs — four choices each, no answers](assignments/README.md)

## Learning protocol
PNP Mentorship's Python sequence is primary. Study each concept once, check every relevant Bosscoder class-note point, then independently complete the matching classroom exercise and graded MCQ. All calculations, experiments and explanations are in Python. Keep the original attempt, reviewed mistakes, and real completion dates separate from documentation status.

## Coverage in one view
Introduction and installation; Series, DataFrame and Index; head/tail/info/describe; label and positional selection; conditional/isin/between/string/query filters; add/drop/rename/reindex; fillna/dropna; merge/concat/groupby/filter/transform; datetime parts and timedelta; CSV, Excel, JSON and SQL IO; vectorization and memory; Matplotlib and Seaborn plots; line, scatter, histogram, bar, pie, box, heatmap, violin and pair plots.

## Extra accuracy checks
The source suggests indices must always have unique labels; pandas permits duplicate labels in many cases. Some notebook examples reuse mutated DataFrames and can fail depending on execution order. A comparison between Series.sum() and ndarray.sum() can depend on datatype and missing-data semantics, not just raw speed. Those are flagged in the audit, not silently attributed to the class notebook.

**Agreement:** No MCQ answer keys, solutions, or hidden option indicators in the public practice material.