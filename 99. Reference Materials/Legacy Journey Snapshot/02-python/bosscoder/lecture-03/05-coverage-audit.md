# Bosscoder Functional Programming Lecture 3 — Exhaustive Coverage Audit

**Source:** User-provided Functional Programming lecture notes. The supplied PDF contains 42 pages; coverage has been cross-checked against it. This checklist tracks its subject coverage; explanations are independently authored rather than copied.
**Status:** Documentation mapped, **all learning and exercise checks initially pending**. All ten graded MCQ screenshots were received and indexed; none was solved or reviewed.

## Foundations, properties and paradigms
- [ ] What FP is; declarative versus imperative thinking
- [ ] Pure functions, determinism, no observable side effects
- [ ] Immutability, referential transparency
- [ ] First-class and higher-order functions
- [ ] Function composition
- [ ] Recursion and base cases
- [ ] All ten listed benefits: modularity/reuse, immutability, purity, declarative code, concurrency, reliability, readability, abstraction, testability, functional mindset
- [ ] FP vs imperative vs OOP: core concepts
- [ ] FP vs imperative vs OOP: state management
- [ ] FP vs imperative vs OOP: code structure
- [ ] FP vs imperative vs OOP: abstractions
- [ ] FP vs imperative vs OOP: concurrency/parallelism
- [ ] FP vs imperative vs OOP: testing/debugging
- [ ] FP vs imperative vs OOP: learning curves and use cases
- [ ] FP vs imperative vs OOP: real-world examples

## Functions and purity
- [ ] Define a function with `def`
- [ ] Call a function, interpret return and default None
- [ ] Positional arguments
- [ ] Keyword arguments
- [ ] Default arguments
- [ ] `*args` and `**kwargs`
- [ ] Function scope (local/global)
- [ ] Nested functions and closures
- [ ] Recursion
- [ ] Docstrings and `__doc__`
- [ ] Function annotations and `__annotations__`
- [ ] Pure versus impure example and external state
- [ ] Pure example categories: arithmetic, string concatenation, new-list creation, filtering, Fibonacci, GCD
- [ ] Pure-function benefits and limitations for file/API/database I/O
- [ ] Functions as values: assign, pass, return, store in dictionaries
- [ ] Higher-order examples with map, filter, reduce, closures, lambdas

## Lambda
- [ ] Lambda syntax and single-expression limitation
- [ ] Comparison with `def` (readability, reuse, statements)
- [ ] List of lambdas in comprehension and default-argument capture
- [ ] Conditional expression in lambda
- [ ] Lambda with filter
- [ ] Lambda with map
- [ ] Data preprocessing, feature engineering, sorting/aggregation use cases

## Decorators
- [ ] Decorator function, wrapper and replacement process
- [ ] `@decorator` versus manual decoration
- [ ] Before/after behavior, arguments and return values
- [ ] Parameterized decorator factory
- [ ] `functools.wraps` / metadata preservation
- [ ] `@staticmethod`
- [ ] `@classmethod`
- [ ] `@property`
- [ ] `@property` setter and validation

## Map and filter
- [ ] `map` basic syntax, named function, lambda
- [ ] Map across multiple iterables
- [ ] Map object to list conversion
- [ ] Lazy evaluation and one-pass iterator
- [ ] `functools.partial` with map
- [ ] Chaining map with filter and reduce
- [ ] `filter` syntax, named function, lambda
- [ ] Filtering numeric and text records
- [ ] Filtering multiple fields via `zip`
- [ ] Filtering custom objects
- [ ] Chaining filter with map and reduce

## zip and ZIP archive operations
- [ ] `zip` pairs elements of equal-length inputs
- [ ] Unequal lengths stop at shortest by default
- [ ] `zip` three or more inputs
- [ ] `zip(*pairs)` unzips pairs
- [ ] `zipfile.ZipFile` creates an archive
- [ ] Archive multiple individual files
- [ ] Archive a directory with `os.walk` and relative paths
- [ ] List archive members using `namelist`
- [ ] Extract one file and all files; path safety
- [ ] Distinguish ZIP archive operations from `zip()` iterator

## reduce
- [ ] Import `reduce` from `functools` and explain accumulator
- [ ] Reduce with named binary function
- [ ] Reduce with lambda
- [ ] Reduce for maximum of values
- [ ] Reduce for joining text
- [ ] Reduce with initializer and empty input
- [ ] Compare reduce against sum/max/join/loops
- [ ] Complexity, laziness and memory considerations

## Source accuracy and review flags
- [ ] The lecture claims FP favors immutability; clarify that Python allows mutable values even in functional-style code.
- [ ] The source's `list(mapped)[:10]` illustration **materializes all results first** rather than evaluating just ten. Use `itertools.islice` to demonstrate truly limited consumption.
- [ ] `filter()` accepts one iterable, but `zip` can combine several sources beforehand.
- [ ] `zip()` over iterables and `zipfile` archives are separate unrelated APIs.
- [ ] Recursion cannot safely replace all loops at arbitrary Python recursion depth.
- [ ] Decorators may discard return values or metadata if written carelessly; review both.
- [ ] `reduce` without initializer on empty input fails; map/filter/zip iterators are consumed as traversed.

## Integrated PNP mapping
| Lecture 3 coverage | PNP Python course |
|---|---|
| Core functions, scope, recursion | pp. 18–19, 31 |
| Modules, docstrings, annotations | pp. 20, 31 |
| Iterators, map/filter/zip, functools, sorting | pp. 35–36 |
| Decorators and wrappers | p. 38 |
| Data processing and ETL transformation design | Later Data Engineering Python section |

## Student completion protocol
- [ ] Study the corresponding PNP concept and match all Bosscoder subpoints
- [ ] Predict outputs and run new examples
- [ ] Reimplement classroom demonstrations independently
- [ ] Attempt the 10 already supplied Bosscoder graded MCQs independently, in Python only
- [ ] Discuss errors, correctness, complexity, side effects and performance
- [ ] Save reviewed notes/attempts and actual completion date to the central tracker

**Important:** Full documentation coverage ≠ mastery. All these boxes remain unmarked until real study evidence is reviewed.

## PDF verification

- [42-page Functional Programming PDF cross-check](pdf-source-audit.md) confirms page-group coverage and source-specific cautions.
- The academy assignment set has been received; it is **not** completed.
