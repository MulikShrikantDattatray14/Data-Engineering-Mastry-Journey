# PDF cross-check — Lecture 03: Functional Programming

**Source:** Learner-supplied `Functional Programming .ipynb - Colab.pdf` (42 PDF pages, reviewed 2026-11-06).
**Result:** All principal PDF topic groups have matching independent public chapters. Specific source cautions and tracker corrections are below. **Student mastery and assignments remain pending.**

## PDF page-to-GitHub comparison

| PDF pages | Source subject area | Existing learning chapter |
|---|---|---|
| 1–12 | FP introduction, characteristics, ten benefits, FP vs imperative vs OOP across state, code structure, abstraction, testing, concurrency and use cases | [Chapter](01-functional-foundations.md) |
| 12–22 | def, positional/keyword/default/variadic parameters, returns, scope, nested functions, recursion, docstrings, annotations; pure/impure functions, first-class/higher-order functions | [Chapter](02-functions-and-purity.md) |
| 23–31 | lambda expression restrictions, conditional lambda, loop capture, preprocess use cases, decorators, parameterized decorators, staticmethod/classmethod/property | [Chapter](03-lambdas-and-decorators.md) |
| 32–36 | map single/multiple iterables, laziness, partial, filter of sequences/objects and zip pairs | [Chapter](04-map-filter-zip-reduce.md) |
| 37–42 | zip iterable combinations versus zipfile archives, reduce with accumulator/initializer and combinations | [Chapter](04-map-filter-zip-reduce.md) |

## Cautions and mismatches confirmed during PDF verification
- Source `list(mapped)[:10]` materializes all elements before slicing: genuine laziness requires limited iteration (e.g. islice).
- Functional programming in Python is an approach rather than an immutability-enforcing language restriction.
- The previous audit inaccurately states that 10 graded MCQs were not received; screenshots were already provided. Correct the tracker language.

## Changes or additional review requirements
- PDF end-page `zipfile` versus iterable `zip` confirmed as two separate topics; already included in the relevant chapter.

## Not an assignment submission

- [ ] Learner reviews every source-aligned topic and independently reruns relevant Python exercises.
- [ ] Learner completes the corresponding Bosscoder graded assignments later.
- [ ] We verify first attempts, pitfalls and edge cases before checking mastery boxes.

**No graded assignment solutions or MCQ answer keys supplied in this audit.**
