# NumPy Fundamentals: Arrays, Types, Dimensions and Reshaping

## 1. What NumPy does
NumPy provides the homogeneous, multidimensional **ndarray**, optimized numerical operations, vectorized arithmetic and linear algebra. It is widely used by Pandas and scientific tooling. Unlike general Python lists, ndarray values normally share a fixed data type (`dtype`) and dimensions described by `shape`.

```python
import numpy as np
values = np.array([4, 8, 12])
print(values.shape, values.ndim, values.dtype, values.size)
```

## 2. Creating 1D, 2D and 3D arrays
A vector can have shape (3,), a 2D matrix shape (2, 3), and a collection of matrices shape (2, 3, 4). Dimensions are axes; distinguish axis count from total element count.

```python
one = np.array([2, 4, 6])
two = np.array([[1, 2, 3], [4, 5, 6]])
three = np.arange(24).reshape(2, 3, 4)
print(one.shape, two.shape, three.shape)
```

Arrays can be constructed from lists or tuples. A Python list such as `[0] * n` is **not** a NumPy array, though it is a common fixed-size list initialization pattern.

## 3. Array creation functions
| API | Purpose |
|---|---|
| np.array(sequence) | Create array from compatible nested sequences |
| np.zeros(shape, dtype=...) | Filled with zero |
| np.ones(shape, dtype=...) | Filled with one |
| np.full(shape, value) | Filled with specified value |
| np.arange(start, stop, step) | Evenly spaced step-based values, stop excluded |
| np.linspace(start, stop, num) | Specified count of evenly spaced values, endpoints normally included |

```python
print(np.zeros((2, 3), dtype=int))
print(np.ones((1, 4)))
print(np.full((2, 2), 7))
print(np.arange(2, 11, 2))
print(np.linspace(0, 1, 5))
```

**Type nuance:** defaults can produce floating-point arrays; predicting `dtype` requires considering the function, provided values and environment. For cross-platform tests specify `dtype` when important.

## 4. Reshape and unknown dimensions
`reshape` changes shape without changing number of elements. Product of target dimensions must match array size. One `-1` may request NumPy to infer a size.

```python
ids = np.arange(12)
matrix = ids.reshape(3, 4)
cube = ids.reshape(2, 3, 2)
inferred = ids.reshape(2, -1)
print(matrix.shape, cube.shape, inferred.shape)
```

Reshaping need not create an independent copy. Check whether changes to a view could affect its base before mutating.

## 5. Flattening
`ndarray.flatten()` returns a **copy** as a 1D array; `ravel()` often returns a **view** when possible (not always).

```python
matrix = np.arange(6).reshape(2, 3)
flat_copy = matrix.flatten()
flat_copy[0] = 999
print(matrix[0, 0])
```

## Your turn
- [ ] Create list/tuple-derived ndarrays and explain their inferred dtypes
- [ ] Build vectors, matrices and 3D arrays; verify shapes and element counts
- [ ] Compare zeros, ones, full, arange and linspace
- [ ] Reshape with explicit dimensions and inferred dimension
- [ ] Predict when reshape and ravel may share storage; compare with flatten
- [ ] Explain why dtype affects memory and accuracy

**Status:** Source concepts documented; practice pending.
