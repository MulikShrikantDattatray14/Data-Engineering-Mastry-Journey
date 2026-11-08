# Part 1 — Functional Programming Foundations

## 1. What does functional programming mean?
Functional programming (FP) organizes computation around functions and transformations of values, favoring immutability, predictable outputs and small composable units. Python supports FP alongside imperative and object-oriented styles; it does not enforce purity.

An **imperative** approach describes steps and usually modifies state. A **functional** approach emphasizes expressions and composing transformations. An **object-oriented** approach groups data and behavior in objects. Real Python programs often mix these approaches intentionally.

```python
# Imperative: updates a local accumulator
amounts = [100, 250, 75]
total = 0
for amount in amounts:
    total += amount

# More declarative: delegates iteration to a built-in
total_2 = sum(amounts)
print(total, total_2)
```

Neither version is inherently wrong. Prefer clarity, testability, performance, and an appropriate abstraction.

## 2. Functional characteristics
| Characteristic | Meaning | Practical benefit |
|---|---|---|
| Pure functions | Same inputs lead to same result with no observable side effects | Easy to unit test |
| Immutability | Avoid in-place changes of shared data | Fewer accidental mutations |
| First-class functions | Pass, return, store functions like other objects | Flexible reusable design |
| Higher-order functions | Accept or return functions | Encode common transformation patterns |
| Composition | Combine small operations | Clear, layered pipelines |
| Recursion | Break problem into smaller instances | Useful for trees/hierarchies |
| Declarative style | Emphasize desired outcome | Communicate intent |

### Recursion is not a universal replacement for loops
The classroom notes present recursion as central to FP. In practical Python, recursion can be useful but Python does not guarantee tail-call optimization and recursion depth is limited. For large flat datasets, loops, iterators, built-ins and vectorized operations are often more appropriate.

## 3. Ten benefits from the lecture — with realistic caveats
1. **Modularity and reuse:** small transformations can be reused independently.
2. **Immutability:** prevents unintended modification of shared objects.
3. **Pure functions:** make outcomes more predictable.
4. **Declarative code:** can reduce distracting control-flow details.
5. **Concurrency/parallelism:** no shared mutation reduces some race risks; this alone does not make any workload automatically parallel or faster.
6. **Reduced bugs and reliability:** fewer hidden state dependencies.
7. **Readability/maintenance:** simple, named operations help; giant lambda chains can hurt.
8. **Abstraction:** higher-order functions express recurring patterns.
9. **Testability:** input/output assertions are straightforward for pure functions.
10. **Functional thinking:** model work as transformations through stages.

## 4. FP vs imperative vs OOP — all comparison dimensions
| Dimension | FP | Imperative | OOP |
|---|---|---|---|
| Core focus | Functions and values | Commands/steps | Classes and objects |
| State | Favors immutable data | Often mutable local/global state | Encapsulated object state |
| Code structure | Small composable functions | Loops, statements, procedures | Methods and classes |
| Abstraction | Composition, higher-order functions | Procedures, control flow | Interfaces and polymorphism |
| Concurrency | Shared-state avoidance helps | Explicit coordination may be needed | Object state requires coordination |
| Testing | Pure outputs easy to isolate | Hidden state may complicate tests | Fixtures and mock objects may be needed |
| Learning/use cases | Transformations, analytics | Scripting, automation | Complex stateful systems |
| Example | Transform/clean records | Process a file with a loop | Represent a configured extractor |

## 5. Data Engineering example
Consider an ingestion pipeline: **parse → normalize → validate → load**. Parsing, normalizing and validation can often be pure transformations. Writing data to a warehouse is inherently an external side effect. Separate those concerns to make the transformation logic independently testable.

## Independent review questions
- [ ] Explain purity versus deterministic output.
- [ ] Explain why immutability can help in concurrently executed transformations.
- [ ] Give a case where a simple loop is better than map/filter/reduce.
- [ ] Contrast FP, imperative, and OOP across all eight dimensions above.
- [ ] Explain why reading from a database is not a pure operation.

**Status:** Notes documented; no mastery credit.