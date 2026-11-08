# Structured NumPy Arrays — Records with Named Fields

The supplied lecture ends with structured arrays: an ndarray with named fields and a potentially different dtype per field. These are useful when a compact table-like representation is appropriate, although pandas and Arrow are often more convenient for real Data Engineering workflows.

## Creating a structured dtype

```python
import numpy as np

schema = np.dtype([
    ("order_id", np.int64),
    ("region", "U12"),
    ("amount", np.float64),
])
orders = np.array([
    (101, "west", 420.0),
    (102, "north", 210.5),
], dtype=schema)

print(orders.dtype.names)
print(orders["region"])
print(orders["amount"].mean())
```

Every row follows the same field names and field dtypes. A string field such as `"U12"` has a fixed character-width specification; distinguish it from byte-string dtypes such as `"S3"`.

## Field operations

```python
print(np.sort(orders, order="amount"))
print(orders["amount"].min(), orders["amount"].max())
```

The lecture demonstrates named-field creation, sorting by name/age, and minimum/maximum age. Try the equivalent with synthetic order records after understanding the source demonstrations.

## Cautions

- Structured records are not ordinary Python dictionaries.
- Ordering the structured array by a field is different from sorting just that field in isolation.
- `np.min`/`np.max` applied to a selected numeric field returns a scalar reduction, unlike `np.minimum`/`np.maximum` pairwise comparisons.
- Fixed-length string dtypes may truncate longer values; schema design matters.

## Classroom checks

- [ ] Define structured dtype with text, integer and floating-point fields.
- [ ] Create multiple records with a shared schema.
- [ ] Index a named field.
- [ ] Sort by two different field names.
- [ ] Find min and max numeric-field values.
- [ ] Explain when structured arrays are useful and when columnar DataFrames are more suitable.

**Status:** Notes complete, learner attempts pending. No academy MCQ answers.
