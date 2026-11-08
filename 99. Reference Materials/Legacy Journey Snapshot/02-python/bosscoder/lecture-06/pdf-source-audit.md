# PDF cross-check — Lecture 06: NumPy

**Source:** Learner-supplied `Numpy.ipynb - Colab.pdf` (26 PDF pages, reviewed 2026-11-06).
**Result:** All principal PDF topic groups have matching independent public chapters. Specific source cautions and tracker corrections are below. **Student mastery and assignments remain pending.**

## PDF page-to-GitHub comparison

| PDF pages | Source subject area | Existing learning chapter |
|---|---|---|
| 1–8 | NumPy motivation, array creation, dimensions, ndarray versus Python list, reshape/-1/flatten/sort | [Chapter](01-arrays-creation-and-shapes.md) |
| 9–16 | basic/advanced/Boolean/multidimensional indexing, mutations, arithmetic, mean/minimum/maximum/standard deviation | [Chapter](02-indexing-and-computing.md) |
| 16–24 | transpose, concatenate, stacking, split, expand_dims, squeeze, vector/matrix arithmetic, determinant, broadcasting, sine/cosine | [Chapter](03-manipulation-broadcasting.md) |
| 25–26 | structured dtypes, named fields, sorting by field and numeric min/max | [Chapter](04-structured-arrays.md) |

## Cautions and mismatches confirmed during PDF verification
- `np.add(a, b, c)` uses c as an `out` parameter, not an ignored extra array; the source explanation is incorrect.
- Flatten creates a copy, while ravel can return a view; the MCQ specifically tests the aliasing effect.
- NumPy division by zero commonly produces a warning plus inf/nan under default float settings; same-shape requirement also has broadcasting exceptions.

## Changes or additional review requirements
- All major PDF sections and end-page structured arrays confirmed present.

## Not an assignment submission

- [ ] Learner reviews every source-aligned topic and independently reruns relevant Python exercises.
- [ ] Learner completes the corresponding Bosscoder graded assignments later.
- [ ] We verify first attempts, pitfalls and edge cases before checking mastery boxes.

**No graded assignment solutions or MCQ answer keys supplied in this audit.**
