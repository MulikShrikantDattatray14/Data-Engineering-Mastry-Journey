# NumPy Lecture 6 — Complete No-Skip Audit

**Source:** User-shared NumPy notebook and 12 graded MCQ screenshots. All listed class concepts mapped, none marked mastered. These are original public revision notes, not copied class material.

When an MCQ tests a topic not emphasized in PNP, include it before that assignment. Learn each concept once, then use Bosscoder for verification.

## Basics and creation

- [ ] What NumPy does and why efficient numerical arrays matter
- [ ] Import as np; ndarray, shape, ndim, size and dtype
- [ ] 1D, 2D, 3D arrays and axes
- [ ] Create array from list and tuple; distinguish list initialization
- [ ] zeros, ones, full, arange and linspace, inferred dtype

## Reshaping and sorting

- [ ] Reshape 1D to 2D and 3D
- [ ] Reshape to 1D and infer one -1 dimension
- [ ] Flatten copy versus reshape/ravel view possibility
- [ ] np.sort numerical, alphabetical and Boolean arrays

## Indexing

- [ ] Basic indexing and negative positions
- [ ] Slicing with step
- [ ] Advanced integer array indexing
- [ ] Boolean masks and filtering
- [ ] In-place modifications by index, slice and mask
- [ ] 2D, 3D and mixed indexing

## Arithmetic and statistics

- [ ] Elementwise add, subtract, multiply and divide
- [ ] np.add out parameter and source's misleading third argument example
- [ ] Mean along axes
- [ ] Minimum and maximum: pairwise versus reductions
- [ ] Standard deviation and dtype precision
- [ ] Divide by zero, inf/nan and error handling

## Manipulation

- [ ] Transpose
- [ ] Concatenate axis 0 and axis 1
- [ ] Stacking, vstack and hstack
- [ ] Split, hsplit and vsplit
- [ ] expand_dims and squeeze

## Linear algebra and broadcasting

- [ ] Vector addition/subtraction/scalar multiplication/dot product
- [ ] Matrix creation, addition, subtraction
- [ ] Matrix multiplication with dot and @
- [ ] Matrix transpose and determinant
- [ ] Broadcasting compatible shapes from trailing dimensions
- [ ] Scalar, vector, row/column and outer-product broadcasting
- [ ] Vectorized sine/cosine plotting with Matplotlib

## Structured arrays

- [ ] Structured dtype with mixed named fields
- [ ] Create and inspect record arrays
- [ ] Sort records by named fields
- [ ] Min and max selected numeric field

## Important source clarifications

- np.add(a, b, c) treats c as the optional output array, rather than simply ignoring c.
- np.ndarray.flatten() produces a copy; ravel()/reshape()/basic slicing may share memory. Advanced indexing commonly creates a copy.
- Array dimensionality and broadcasting shape rules determine which operations can run.
- np.sort returns an array; .sort() operates in place.
- Floating-point division by zero does not necessarily raise the same exception as scalar Python integer division.
- A Python list initialized with [0]*size is not a NumPy ndarray.
- Default numeric dtype may vary by API/platform; specify dtype when reproducibility is necessary.
- Structured array fixed-length string fields can differ from regular Python text values.

## Assessment contract

- [ ] Predict output before running code.
- [ ] Submit all 12 Bosscoder NumPy MCQs independently, without answer hints.
- [ ] Review each solution and edge case only after student submission.
- [ ] Record mistakes, applied exercises and actual mastery progress.

**Status:** Coverage documented, not mastered.