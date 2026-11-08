# Bosscoder Python Refresher 1 — Detailed No-Skip Coverage Audit

**Status:** Lecture notes inspected, each covered subtopic and classroom exercise inventoried. **Study/mastery: pending.**
**Source:** User-supplied Bosscoder Python Refresher 1 class notes (original private class content not reproduced in this public repo).
**Purpose:** Cross-check **every distinct concept** during PNP Python Study Mode, prevent duplicate lessons, and preserve original student attempts for review. The academy assignment is a separate exercise track.

## A. Introduction and Python data types
- [ ] Python as a high-level programming language; readability and abstraction
- [ ] Interpreted execution mental model and the distinction from compiled implementations (avoid overgeneralizing)
- [ ] Data types and `type()`
- [ ] Numeric `int`, `float`, `complex` and `j` imaginary suffix
- [ ] Boolean `bool`, `True`, `False`
- [ ] Sequence `str`, `list`, `tuple`: indexing, mutability/immutability
- [ ] Collection `set`: uniqueness and ordering assumptions
- [ ] Immutable `frozenset`
- [ ] Mapping `dict`: unique keys, key/value access
- [ ] Binary `bytes`: byte sequences vs text strings

## B. Variables, assignment, naming, and keywords
- [ ] Variables and name binding to Python objects
- [ ] Naming rules: permitted characters, first character, case sensitivity, keyword restrictions
- [ ] Local variable inside function
- [ ] Global variable and reading a global
- [ ] `global` declaration when rebinding globals inside a function
- [ ] Multiple assignment: chained assignment and tuple unpacking
- [ ] `del` on names, what happens on subsequent access, `NameError`
- [ ] Python reserved keywords and `help('keywords')`
- [ ] `keyword.kwlist` and `keyword.iskeyword()`

## C. Inputs, operators, and conversion
- [ ] `input()` returns a text value; output with `print()`
- [ ] Explicit conversion of user input with `int()` and invalid input handling
- [ ] Arithmetic: `+`, `-`, `*`, `/`, `%`, `**`, `//`
- [ ] Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`
- [ ] Assignment: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `**=`, `//=`
- [ ] Logical operations: `and`, `or`, `not`
- [ ] Bitwise operations: `&`, `|`, `^`, `~`, `<<`, `>>`
- [ ] Membership: `in`, `not in`
- [ ] Identity: `is`, `is not`, distinguishing identity from value equality
- [ ] Implicit conversion: mixed integer and floating-point arithmetic
- [ ] Explicit `int()`, `float()`, `str()`, `list()`, `tuple()`, `set()`, `dict()`, `bool()`
- [ ] Type-conversion pitfalls: truncation, truthiness, invalid casts

## D. Indexing, slicing, and decisions
- [ ] Slice form `[start:stop:step]`
- [ ] Start included / stop excluded
- [ ] Positive indexing and negative indexing
- [ ] Stepped slicing and reversing with a negative step
- [ ] Out-of-range slicing, and how it differs from out-of-range indexing
- [ ] `if`, `else`, `elif`, indentation and execution flow
- [ ] Nested conditionals; comparison chains and boundary tests

## E. Loops and loop control
- [ ] `for ... in` with iterable objects
- [ ] `range()` and endpoint behavior
- [ ] Nested `for` loops
- [ ] `while` with state updates and loop termination
- [ ] `break` and which statements after break execute
- [ ] `continue` and skipped processing
- [ ] Loop `else` semantics when a break does/does not occur (mentioned in the lecture syntax)

## F. Every classroom exercise/example to attempt independently
- [ ] First variable/print example using name, age and height
- [ ] Local-scope function computing and printing a sum
- [ ] Global rebinding example
- [ ] Chained and unpacked assignments; deletion and resulting NameError
- [ ] Keyword inspection via Python module
- [ ] Input and input conversion examples
- [ ] Arithmetic, comparison, augmented assignment and Boolean operator outputs
- [ ] Bitwise/membership/identity demonstrations and explanation
- [ ] Implicit and explicit conversion examples
- [ ] Slicing challenge on the supplied `datastructures` string: seven parts (extract first part, negative suffix, middle substring, stepped characters, last three, reverse, oversized negative start)
- [ ] Numeric **cube classification** against a threshold, then completion message
- [ ] Time-of-day categorization with specified ranges; test at boundaries
- [ ] Nested-loop prime numbers in a specified interval
- [ ] Reverse integer digits using while loop
- [ ] Factorial using for loop
- [ ] Factorial using while loop
- [ ] Palindrome check using for loop
- [ ] Break demo that stops at a specified counter and compares printed output
- [ ] Repeated input/continue/break exercise: stop sentinel, ignore divisible values, otherwise print square

## G. Important class-note discrepancies to test, not silently repeat
- The *cube* task's shown example appears to multiply by 3 rather than calculate a third power. Verify the mathematical requirement during review; **no solution included here**.
- The time-of-day task and supplied code appear to disagree at the 9 o'clock boundary. Confirm expected behavior with tests rather than copying the sample condition.
- The `is` comparison of small integers in notes may appear to work due to object reuse; never present this as a reliable numeric equality check.
- The glossary's description of Python `dict` ordering and of Python being interpreted is simplified; clarify the relevant modern behavior in the interactive explanation.
- `for ... else` and `while ... else` appear in syntax examples; they should be explicitly explained even though the lecture's main exercises emphasize break/continue.

## H. Bosscoder assignment set (separate from classroom exercises)
- [Q01 — Even/Odd](assignments/refresher-1-q01-even-odd.md) — **Pending independent attempt**
- [Q02 — Leap Year](assignments/refresher-1-q02-leap-year.md) — **Pending independent attempt**
- [Q03 — Maximum Integer](assignments/refresher-1-q03-maximum-integer.md) — **Pending independent attempt**
- More assignment questions: awaiting user sharing; platform displays a 12-question set, but only these three problem statements have been supplied so far.

## I. Study Mode rule and audit process
1. Teach from the corresponding PNP Python lesson; use this checklist as a second-source coverage audit.
2. Before marking the concept mastered, verify all matching Lecture 1 bullets and runnable demonstrations, not just the PNP headline.
3. Ask the learner to independently attempt the associated Bosscoder assignment; do not supply solutions without an attempted answer or explicit request.
4. Review correctness, boundary cases, time/space complexity and lessons learned.
5. Link reviewed evidence and mastery status in the learning repository; keep academy attendance/solved status separate.
6. If a holiday session covers multiple topics, advance the queue without skipping any checklist item.

**Audit status: All listed material is mapped; every checkbox remains unchecked until real study or review.**