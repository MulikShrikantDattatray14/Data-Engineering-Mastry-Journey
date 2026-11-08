# Lecture 7 — Full Source Coverage Audit

**Scope:** Bosscoder Pandas and Data Visualisation source notebook plus all ten supplied MCQs.
**Status:** Topics documented, not yet practiced or mastered. All boxes start unchecked.
**PNP is primary:** Map these to the corresponding Python data-processing, Pandas, ETL and analytics topics without forcing redundant lectures.

## Introduction and structures

- [ ] Install pandas and import pd; relation to NumPy
- [ ] Series, custom labels, positional and label selection
- [ ] DataFrame from dictionary and nested rows
- [ ] Index and columns metadata; uniqueness caveat
- [ ] df.head, tail, info and describe

## Selection and filtering

- [ ] loc labels and inclusive slices; iloc positions and exclusive slices
- [ ] Single/multiple Boolean conditions with parentheses
- [ ] isin, between inclusive edges
- [ ] str.contains, startswith, endswith
- [ ] query with SQL-like string

## Modification and cleaning

- [ ] Add and drop derived columns
- [ ] rename columns and index; reindex rows
- [ ] fillna and dropna; null meaning
- [ ] DataFrame mutation, chaining and source state

## Advanced transformations

- [ ] Merge on multiple keys
- [ ] Merge with left_on/right_on
- [ ] Merge overlap suffixes
- [ ] Concatenate rows and columns; index alignment
- [ ] GroupBy mean/sum/count/min/max
- [ ] Group filtering
- [ ] GroupBy transform and output shape

## Dates and I/O

- [ ] pd.to_datetime and .dt.year/month/day
- [ ] Timedelta addition and subtraction
- [ ] Read CSV/Excel/JSON and SQL
- [ ] Write CSV/Excel/JSON and SQL
- [ ] Parquet discussion in source overview, optional extension
- [ ] Data source path, JSON Lines and safe SQL replace behavior

## Performance

- [ ] Vectorized DataFrame arithmetic
- [ ] Downcast with to_numeric
- [ ] Read CSV specifying dtype
- [ ] Avoid needless copies; assess inplace operations
- [ ] Filter early, inspect memory

## Matplotlib

- [ ] scatter with labels/titles, c and s, colorbar
- [ ] line chart, multiple line series
- [ ] histogram
- [ ] legend loc best
- [ ] subplots rows/columns and plot types

## Seaborn and additional visualizations

- [ ] Seaborn scatterplot and hue
- [ ] Seaborn lineplot and barplot; aggregation caveat
- [ ] Line and pie charts
- [ ] Box plot and IQR/whiskers
- [ ] Heatmap with annotations
- [ ] Violin plot with distribution
- [ ] Pairplot with diagonal/off-diagonal cells

## Important source review flags
- Source says pandas Index ensures unique labels: labels may in fact be duplicated; some APIs disallow ambiguous reindexing.
- An example uses pd.Series indexing notation for both labels and positions: favor explicit loc/iloc to avoid ambiguity.
- GroupBy transform returns values aligned to original rows, unlike aggregate.
- Notebook reuses mutated DataFrames; examples may require controlled reinitialization before replay.
- Avoid blanket speed claims comparing Series.sum and ndarray.sum: dtype, NA and version are material.
- The lecture includes demo columns resembling payer names and card numbers. Use synthetic data and never publish real financial identifiers.
- The source's plotting examples assume external tips/iris datasets or files exist; our notes use synthetic reproducible data.

## Learning and assessment agreement
- [ ] Show standalone Python examples for every technique.
- [ ] Run source-equivalent classroom tasks without copying original answers.
- [ ] Solve all ten Bosscoder MCQs yourself; four original choices provided in question files.
- [ ] Only after student submission, review why the chosen answer is correct or incorrect.
- [ ] Log date, source, code, mistakes, and verified skill mastery on GitHub.

**PNP integration:** Python foundations (files, data parsing, pandas), SQL analogies (joins, groupby, window-like transform), later ETL reliability and performance.

**Documentation complete does not mean mastery complete.**
## PDF source verification

- [21-page Pandas/Data Visualisation PDF cross-check](pdf-source-audit.md) confirms the original chart demonstrations, file handling and notebook-version warnings.
- The source's Seaborn violin example warns about a future `palette` without `hue` deprecation; we will use version-appropriate plotting syntax when practicing.
