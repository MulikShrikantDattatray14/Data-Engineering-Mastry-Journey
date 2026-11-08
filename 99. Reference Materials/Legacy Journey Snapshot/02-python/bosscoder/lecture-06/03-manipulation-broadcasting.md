# NumPy Manipulation, Vectors, Matrices and Broadcasting

## 1. Array manipulation APIs
- `reshape`: change axes while preserving number of elements
- `flatten`: produce 1D copy
- `.T` or `transpose`: swap/reorder axes, usually a view
- `concatenate`: join arrays along an **existing** axis
- `stack`: join arrays along a **new** axis
- `vstack` and `hstack`: convenient joins whose behavior depends on input ranks
- `split`, `hsplit`, `vsplit`: divide by axis or boundaries
- `expand_dims`: add singleton dimension
- `squeeze`: remove singleton dimensions

```python
import numpy as np
left = np.array([[1, 2], [3, 4]])
right = np.array([[5, 6], [7, 8]])
print(left.T)
print(np.concatenate((left, right), axis=0).shape)
print(np.concatenate((left, right), axis=1).shape)
print(np.stack((left, right), axis=0).shape)
print(np.vstack((left, right)).shape, np.hstack((left, right)).shape)
print(np.split(np.arange(8), 4))
print(np.hsplit(np.arange(8).reshape(2,4), 2))
print(np.vsplit(np.arange(8).reshape(4,2), 2))
print(np.expand_dims(np.arange(3), axis=0).shape)
print(np.squeeze(np.ones((1, 3, 1))).shape)
```

## 2. Vector and matrix calculations
Vector addition, subtraction and scalar multiplication are usually element-wise. `np.dot` on two 1D vectors yields a scalar dot product. On matrices, `@` and `np.matmul` implement matrix multiplication, not element-wise multiplication.

```python
v = np.array([1, 3, 5])
w = np.array([2, 4, 6])
print(v+w, v-w, 3*v, np.dot(v,w))
A = np.array([[1, 2], [3, 4]])
B = np.array([[2, 0], [1, 2]])
print(A * B)   # element-wise
print(A @ B)   # matrix product
print(np.linalg.det(A))
```

Numerical determinants may display tiny floating-point error rather than an exact integer.

## 3. Broadcasting: the shape-matching rules
Broadcasting combines compatible shapes without manually repeating the smaller input. Compare dimensions **from right to left**; each pair must be equal or have one dimension equal to 1. Missing leading dimensions behave as 1. The output shape takes the larger compatible size on each axis.

```python
sales = np.array([[10, 20, 30], [40, 50, 60]])
per_product_fee = np.array([1, 2, 3])
print(sales + per_product_fee)
```

Shapes (2,3) and (3,) are compatible; (2,3) and (2,) cannot be added directly without reshaping to (2,1).

```python
per_store_fee = np.array([7, 9]).reshape(2, 1)
print(sales + per_store_fee)
```

The source also demonstrates scalar broadcasting, outer-product calculation, broadcasting against a transpose, and the shape-changing effect of reshaping a vector into a column.

## 4. Trigonometric visualisation
The lecture creates arrays of x-coordinates and applies `np.sin`/`np.cos`, then uses Matplotlib to plot them. The key NumPy idea is **vectorized functions on arrays**, not mastering plotting aesthetics.

## 5. Concept checks
- [ ] Explain axis=0 versus axis=1 on a matrix
- [ ] Predict every resulting shape of stack, vstack, hstack, concatenate, hsplit, vsplit
- [ ] Explain add/remove singleton dimensions
- [ ] Compare dot product, element-wise multiplication and `@`
- [ ] Determine when broadcasting works, fails or requires reshape
- [ ] Reproduce a vectorized sine/cosine example in a separate practice script

**Status:** Original examples prepared; practice pending.
