# PDF cross-check — Lecture 04: Modules, Errors and Exceptions

**Source:** Learner-supplied `Modules, Error and Exceptions.ipynb - Colab.pdf` (15 PDF pages, reviewed 2026-11-06).
**Result:** All principal PDF topic groups have matching independent public chapters. Specific source cautions and tracker corrections are below. **Student mastery and assignments remain pending.**

## PDF page-to-GitHub comparison

| PDF pages | Source subject area | Existing learning chapter |
|---|---|---|
| 1–5 | module types, benefits, custom .py modules/imports, packages and __init__.py, __name__ main guard, standard-library modules | [Chapter](01-modules-and-packages.md) |
| 6–8 | local/enclosing/global/built-in namespaces, nonlocal, LEGB lookup, shadowing | [Chapter](02-namespaces-and-scope.md) |
| 8–11 | syntax, indentation, runtime, logical errors, off-by-one examples | [Chapter](03-errors-and-exceptions.md) |
| 11–15 | try/except, user-defined exceptions, multiple handlers, else, finally, BaseException hierarchy, raising exceptions, classmethod cameo | [Chapter](03-errors-and-exceptions.md) |

## Cautions and mismatches confirmed during PDF verification
- Some exported PDF text omits double underscores in magic names; valid syntax uses `__init__.py`, `__name__`, `__main__`.
- Namespace packages can exist without `__init__.py`.
- Coroutine and ExitStack questions are drawn from the assessment screenshots, not core PDF lessons; they are clearly labeled advanced assessment prerequisites.

## Changes or additional review requirements
- Source page-to-note mapping added; all major PDF outline headings represented.

## Not an assignment submission

- [ ] Learner reviews every source-aligned topic and independently reruns relevant Python exercises.
- [ ] Learner completes the corresponding Bosscoder graded assignments later.
- [ ] We verify first attempts, pitfalls and edge cases before checking mastery boxes.

**No graded assignment solutions or MCQ answer keys supplied in this audit.**
