# Part 3 — Data Visualisation with Matplotlib and Seaborn

## Why charts matter for Data Engineering
Graphs help spot missing periods, skewed distributions, unusual outliers and changes in data quality. Your academy lecture demonstrates chart construction; in production DE, the goal is often investigating or communicating a metric rather than producing decorative dashboards.

## Matplotlib basics
Matplotlib's `pyplot` interface provides charts and axes; the lecture uses `plt.scatter`, `plt.plot`, `plt.hist`, labeling, titles and `plt.show()`.

```python
import matplotlib.pyplot as plt

dates = [1,2,3,4]
volume = [100,130,120,150]
plt.plot(dates, volume, label='Rows processed')
plt.title('Daily ingestion volume')
plt.xlabel('Day')
plt.ylabel('Rows')
plt.legend(loc='best')
plt.show()
```

## Chart families from the lecture
| Chart | Best use | Covered API |
|---|---|---|
| Scatter | Relationship among two variables | `plt.scatter(x,y)` |
| Line | Numeric/time-series progression | `plt.plot(x,y)` |
| Histogram | One-variable distribution | `plt.hist(values)` |
| Bar | Compare category quantities | `plt.bar(...)` / `sns.barplot(...)` |
| Pie | Parts of a whole with few categories | `plt.pie(...)` |
| Box | Median, quartiles, spread/outliers | `plt.boxplot(...)` |
| Heatmap | Matrix magnitudes/correlations | `sns.heatmap(...)` |
| Violin | Distribution and density per group | `sns.violinplot(...)` |
| Pair plot | Pairwise variables and diagonal distributions | `sns.pairplot(...)` |

## Matplotlib extra features
- `c=` and `s=` vary scatter-point color and size; `plt.colorbar()` can show the numeric color scale.
- Multiple `plt.plot(...)` calls can overlay series on one axes.
- `plt.legend(loc='best')` selects a position based on the plotted artists rather than always using a fixed corner.
- `fig, axes = plt.subplots(2,1)` creates two vertical axes, so the first and second can hold different chart types.

```python
fig, axes = plt.subplots(2, 1)
axes[0].plot([1,2,3], [2,4,3])
axes[1].bar(['A','B'], [8,5])
fig.tight_layout()
plt.show()
```

## Seaborn examples
Seaborn provides data-aware plotting functions on top of Matplotlib and commonly accepts Pandas DataFrames with named `x`, `y`, `hue`, and `data` arguments. The lecture uses scatter, line and bar examples, and later heatmap, violin and pair plots.

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

metrics = pd.DataFrame({'stage':['extract','transform','load','load'], 'seconds':[5,8,3,4]})
sns.barplot(data=metrics, x='stage', y='seconds')
plt.title('Pipeline stage durations')
plt.show()
```

Seaborn statistical charts can **aggregate data** (for example, `barplot` estimates a statistic for each category) rather than simply plotting every original row. Read chart defaults and verify whether aggregation or uncertainty intervals are appropriate.

## Advanced plots
```python
data = pd.DataFrame({'x':[1,2,3,4], 'y':[4,2,6,3], 'group':['a','a','b','b']})
sns.scatterplot(data=data, x='x', y='y', hue='group')
plt.show()
```
Other class demonstrations use `sns.heatmap(data, annot=True)`, `sns.violinplot(...)`, and `sns.pairplot(...)`. Independently recreate each on a synthetic dataset, without relying on an internet-hosted `tips` or `iris` download.

## Box-plot interpretation
The median and quartiles summarize the distribution; the interquartile range is Q3-Q1. In common conventions whiskers stop at observations within a multiple (often 1.5× IQR) rather than necessarily reaching the absolute minimum/maximum; farther points are plotted as outliers. Definitions and options should be stated explicitly.

## Caution about class example data
The source uses a `tips.csv` file containing fields including payer name, card number and payment identifiers. Do **not** commit real personal/payment details into a public learning repository. Use entirely synthetic transaction records and no sensitive identifiers.

## Practice checklist
- [ ] Produce one labeled scatter and one colored/scaled scatter.
- [ ] Plot two line series and an individual histogram.
- [ ] Use Matplotlib titles, axes labels, legends and colorbar.
- [ ] Produce line, pie, bar, box, heatmap, violin and pair plots using new data.
- [ ] Compare Seaborn scatterplot, lineplot and barplot on labeled DataFrames.
- [ ] Explain what axes, `hue`, `loc='best'` and `subplots(2,1)` do.
- [ ] Explain why one might choose each chart to validate a pipeline.

**Status:** Source topics documented; independent practice not yet assessed.