# Part 2 — Pandas Cleaning, Joins, Grouping, Dates, I/O and Performance

## Manipulate columns and rows
```python
import pandas as pd
df = pd.DataFrame({'id':[1,2,3], 'amount':[100,None,300], 'region':['west','east','west']})
df['tax_estimate'] = df['amount'] * .1
df = df.rename(columns={'amount':'gross_amount'})
print(df.drop(columns=['tax_estimate']))
print(df.reindex([0,1,2,3]))
```
New columns can derive from vectorized expressions; `drop` removes selected columns/rows, `rename` changes labels, `reindex` aligns to requested labels and can add missing rows. Prefer reassignment or documented mutation to avoid confusion about in-place state.

## Missing data
```python
print(df.isna().sum())
print(df['gross_amount'].fillna(0))
print(df.dropna(subset=['gross_amount']))
```
`fillna` substitutes missing values; `dropna` discards rows/columns with missing data according to its parameters. Replacing unknown amounts with zero changes business meaning—use it only if the source contract permits. Keep original, cleaned and rejected row counts for auditability.

## Merge versus concatenate
```python
orders = pd.DataFrame({'id':[1,2,3], 'region':['w','e','w']})
payments = pd.DataFrame({'payment_order_id':[1,2], 'amount':[25,40]})
joined = orders.merge(payments, left_on='id', right_on='payment_order_id', how='left')
print(joined)
```
Class notes also cover merging on multiple keys and using suffixes when non-key columns overlap. A merge is a **key-based join** (as in SQL) and can duplicate rows when keys are non-unique. `concat(axis=0)` stacks rows; `concat(axis=1)` aligns horizontally by index labels rather than joining on arbitrary keys.

```python
first = pd.DataFrame({'id':[1,2]})
second = pd.DataFrame({'id':[3]})
print(pd.concat([first, second], ignore_index=True))
```

## GroupBy and filtering groups
```python
sales = pd.DataFrame({'region':['west','east','west','east'], 'amount':[10,20,30,40]})
print(sales.groupby('region')['amount'].agg(['sum','mean','count','min','max']))
print(sales.groupby('region').filter(lambda g: len(g) >= 2))
sales['region_avg'] = sales.groupby('region')['amount'].transform('mean')
```
GroupBy expresses split → apply → combine. Aggregation reduces records per group, group `filter` retains or rejects entire groups, and `transform` produces an aligned result matching source-row count. This distinction is essential for SQL-style window computations.

## Dates and time
```python
events = pd.DataFrame({'occurred_at':['2026-11-05 10:20:00','2026-11-06 12:30:00']})
events['occurred_at'] = pd.to_datetime(events['occurred_at'])
events['year'] = events['occurred_at'].dt.year
events['month'] = events['occurred_at'].dt.month
events['day'] = events['occurred_at'].dt.day
events['next_day'] = events['occurred_at'] + pd.Timedelta(days=1)
```
Real pipeline timestamps need explicit timezone decisions and invalid-date handling. Avoid mixing local-naive and aware timestamps unintentionally.

## Input/output file types from the lecture
| Source | Read | Write |
|---|---|---|
| CSV | `pd.read_csv(path)` | `df.to_csv(path, index=False)` |
| Excel | `pd.read_excel(path, sheet_name=...)` | `df.to_excel(path, index=False)` |
| JSON | `pd.read_json(path)` | `df.to_json(path, orient='records', lines=True)` |
| SQL | `pd.read_sql(query_or_table, engine)` | `df.to_sql(table, engine, if_exists=..., index=False)` |

The classroom notes also mention Parquet as a tabular format. In practice, `pd.read_parquet` and `df.to_parquet` are useful once a compatible engine is installed. JSON Lines should be read with the matching `lines=True` setting, rather than blindly treating all JSON files alike.

**Do not execute examples referring to missing `data.csv`, `data.xlsx`, or a SQLite database without providing those resources.** For data pipelines, record schema, source path, row counts and failures; SQL `if_exists='replace'` can destroy existing tables and should not be copied into production blindly.

## Performance: vectorization and memory
```python
data = pd.DataFrame({'qty':[2,3,4], 'unit_price':[10.0,20.0,15.0]})
data['total'] = data['qty'] * data['unit_price']
data['qty'] = pd.to_numeric(data['qty'], downcast='integer')
print(data.memory_usage(deep=True))
```
Use vectorized columns instead of Python row loops when possible, downcast only if safe, specify dtypes on file reads, filter early, and avoid unnecessary intermediate copies. In-place APIs are not universally more memory-efficient; benchmark rather than assuming. A DataFrame `sum()` and NumPy array `sum()` can differ in null/nullable dtype behavior, so performance comparisons require realistic tests.

## Practice
- [ ] Add, drop, rename and reindex columns/rows on synthetic data.
- [ ] Compare fillna and dropna while preserving business meaning.
- [ ] Write joins on one and multiple keys, mismatched key names and overlapping columns.
- [ ] Compare concat(axis=0) to concat(axis=1) and identify index alignment.
- [ ] Demonstrate GroupBy sum/mean/count/min/max, filter and transform.
- [ ] Parse timestamps, extract date parts, add/subtract Timedelta.
- [ ] Read/write CSV, Excel, JSON, SQL, and explore Parquet as extension.
- [ ] Implement a vectorized transformation and check dtype/memory changes.

**All practice pending; no MCQ solutions revealed.**