# Part 1 — Pandas Fundamentals, Series, DataFrames and Filtering

## Why pandas?
pandas is a Python library for labeled/tabular data manipulation. A DataFrame resembles a spreadsheet or SQL table: columns can have different dtypes and rows have index labels. For a Data Engineer, pandas is useful for small- to medium-sized batches, validating files and prototyping transformations. It is not automatically a substitute for a distributed data engine.

## Installation and imports
Install in a terminal or notebook environment with `python -m pip install pandas`; import with `import pandas as pd`. The academy notebook used pandas 2.2.2; record your own version when behavior may differ.

```python
import pandas as pd
print(pd.__version__)
```

## Series: one-dimensional labeled data
```python
amounts = pd.Series([80, 120, 50], index=['a', 'b', 'c'], name='amount')
print(amounts.loc['b'])
print(amounts.iloc[0])
```
Series have an index and a dtype; missing values and extension dtypes can affect representation. Do not assume index labels must be unique: pandas permits duplicate labels in many operations, though this can complicate reindexing.

## DataFrame: rows and named columns
```python
orders = pd.DataFrame({'order_id':[101,102,103], 'region':['west','east','west'], 'amount':[80,120,50]})
print(orders[['order_id','amount']])
print(orders.loc[0, 'region'])
print(orders.iloc[1, 2])
```
Create DataFrames from dictionaries or list-of-lists (with `columns=[...]`). Use `df.index` and `df.columns` to inspect labels. Compared with SQL, pandas indexes are not necessarily database primary keys.

## Inspection: head, tail, info, describe
| Operation | Use |
|---|---|
| `head(n)` | Preview first rows (default 5) |
| `tail(n)` | Preview last rows (default 5) |
| `info()` | Non-null counts, column types and memory summary |
| `describe()` | Summary statistics of eligible columns |

```python
print(orders.head(2))
print(orders.tail(1))
orders.info()
print(orders.describe())
```

## Label vs position selection
`loc` uses labels; `iloc` uses integer positions. Label slices with `.loc` typically include the terminal label, while positional `.iloc` slicing excludes the stop index. Index labels can be strings or numbers and may be out of positional order.

```python
by_id = orders.set_index('order_id')
print(by_id.loc[101:102])
print(orders.iloc[0:2])
```

## Filtering — every classroom style
```python
df = pd.DataFrame({'name':['Asha','Neel','Amit'], 'age':[24,31,37], 'salary':[500,900,750]})
print(df[df['age'] > 30])
print(df[(df['age'] > 25) & (df['salary'] >= 750)])
print(df[(df['age'] < 30) | (df['name'] == 'Amit')])
print(df[~df['name'].isin(['Neel'])])
print(df[df['age'].between(24, 31)])
print(df[df['name'].str.contains('A', regex=False)])
print(df[df['name'].str.startswith('N')])
print(df[df['name'].str.endswith('t')])
print(df.query('age > 30'))
```
Use parentheses around each Boolean condition combined with `&`, `|`, or `~`; do not replace these vectorized operators with Python's scalar `and`/`or`. String operations may require handling nulls (e.g. `.str.contains(..., na=False)`). `between()` includes endpoints by default.

## Common confusion
Filtering produces a subset, while reindexing to new labels can introduce missing values. Do not treat `reindex` as merely selecting an existing slice.

## Active recall and independent practice
- [ ] Create labeled Series and different DataFrame constructors.
- [ ] Explain `Index` and column labels; verify whether duplicates are allowed.
- [ ] Compare `loc` and `iloc` on non-sequential string labels.
- [ ] Predict head/tail/info/describe results.
- [ ] Implement all five filtering styles from the class notes.
- [ ] Explain and test SQL WHERE versus pandas filtering behavior with missing data.

**Status:** Only original notes added; no graded answers or mastery.