# NumPy Indexing, Sorting, Arithmetic and Statistics

## 1. Indexing families
**Basic indexing** includes integers, slices and multidimensional row/column notation. Negative positions count from the end. Basic slicing often creates a view. **Advanced integer indexing** selects indices in an array and typically makes a copy. **Boolean indexing** filters items according to a mask and also returns a copy for selection.

```python
import numpy as np
grid = np.array([[11, 12, 13], [21, 22, 23], [31, 32, 33]])
print(grid[0, 1])            # scalar
print(grid[1:, 1:])          # submatrix
print(grid[[2, 0], [1, 1]])  # selected positions
print(grid[grid > 20])       # filter
```

The lecture also covers modifying elements with a single index, slice assignment, 3D indexing and combining slices with integer index arrays.

```python
batch = np.arange(6)
batch[1:3] = [80, 90]
batch[batch > 80] = 0
print(batch)
```

## 2. Sorting
`np.sort(a)` ordinarily returns a sorted copy, whereas `a.sort()` sorts in place. Arrays can contain numbers, strings or booleans. Sort along the requested axis and test what happens in multiple dimensions.

```python
values = np.array([8, 3, 5])
copy_sorted = np.sort(values)
print(copy_sorted, values)
```

## 3. Vectorized arithmetic
For compatible shapes, `+`, `-`, `*`, `/` apply **element-wise**. NumPy also exposes `np.add`, `subtract`, `multiply`, `divide`. Matrix multiplication is different (`@` or `np.matmul`).

```python
x = np.array([10, 20, 30])
y = np.array([2, 4, 5])
print(x + y, x - y, x * y, x / y)
```

**Source correction:** In the source, `np.add(a,b,c)` is described as ignoring c. That third positional argument is actually the optional `out` array in the ufunc signature; it may be mutated to receive the result. We must learn this difference rather than repeat the misleading explanation.

**Division nuance:** floating-point division by zero usually issues a runtime warning and yields `inf`/`nan` under NumPy's default settings; behavior depends on dtype and `np.seterr`, so it is not always an immediate Python exception.

## 4. Statistics and pairwise comparisons
- `np.mean(arr, axis=...)`: arithmetic mean
- `np.std(arr, axis=...)`: standard deviation (default `ddof=0`)
- `np.min(arr)`, `np.max(arr)`: reductions across values
- `np.minimum(x,y)`, `np.maximum(x,y)`: **element-wise** pairwise functions

```python
values = np.array([[2, 4], [6, 8]])
print(np.mean(values), np.mean(values, axis=0))
print(np.std(values), np.min(values), np.max(values))
print(np.minimum(values, 5), np.maximum(values, 5))
```

## 5. Precision, missing values and types
Floating-point calculations can involve rounding. `float32` and `float64` have different precision/memory characteristics. For robust DE validation, decide how NaN and infinite values should be treated.

## Independent review
- [ ] Basic, negative, sliced, advanced integer and Boolean indexing
- [ ] Index into 2D and 3D values; combine indexing strategies
- [ ] Modify a single item, slice and mask-selected items
- [ ] Contrast np.sort and ndarray.sort
- [ ] Explain element-wise versus matrix multiplication
- [ ] Explain mean, std, min, max, minimum and maximum
- [ ] Revisit ufunc `out` parameter and divide-by-zero caveats

**Status:** No academy MCQ answers provided.
