# Lecture 2: No-Skip Concept Audit

**Status:** Fully inventoried, not yet practiced or mastered. Both PNP and Bosscoder evidence are required when relevant.

## Pattern exercises
- [ ] One-row pattern; fixed-size rectangle; N-by-M matrix
- [ ] Increasing stair; reverse stair
- [ ] Centered pyramid; diamond
- [ ] Hollow square and boundary-only printing
- [ ] Explain nested loops, print(end=...), newlines and complexity

## Lists
- [ ] Empty, integer, string and mixed lists
- [ ] Properties: ordered, mutable, dynamic, duplicates, indexed, mixed, nesting, slicing, iterable, comprehensions
- [ ] Methods: append, insert, remove, pop, clear, sort, reverse, count, extend
- [ ] len built-in, sorted versus sort; state and mutation effects

## Strings
- [ ] Single, double and triple-quoted text, immutability, order, indexing and iteration
- [ ] Concatenation, repetition, membership, iteration
- [ ] len
- [ ] Case: upper, lower, title, capitalize, swapcase
- [ ] Search: find, rfind, index, count
- [ ] Validation: isalpha, isdigit, isalnum, isspace, isupper, islower
- [ ] Trim/replace: strip, lstrip, rstrip, replace
- [ ] Split/join: split, join
- [ ] Alignment: center, ljust, rjust, zfill
- [ ] Formatting: format, f-strings
- [ ] Classroom string exercise 1: rotation
- [ ] Classroom string exercise 2: first nonrepeating character
- [ ] Classroom string exercise 3: longest palindromic substring
- [ ] Classroom string exercise 4: isomorphic strings
- [ ] Classroom string exercise 5: subsequence

## Tuples
- [ ] Ordered, immutable, indexed, duplicates
- [ ] Creation with parentheses or commas; single-element comma
- [ ] count, index with optional boundaries
- [ ] len, max, min, tuple conversion
- [ ] Nested tuples and iteration
- [ ] Modern comparisons vs obsolete cmp

## Sets
- [ ] Unique elements, literal/constructor and arbitrary ordering
- [ ] add, remove, discard, pop, copy
- [ ] union, intersection, difference, symmetric difference

## Dictionaries
- [ ] Creation with literals and dict()
- [ ] Unique keys, mapping access, mutable updates
- [ ] Python 3.7+ insertion ordering

## Corrections / review flags
- List-method sample outputs in the original notebook can disagree with adjacent comments because the same list is mutated across cells; use isolated examples.
- Python 3 no longer has built-in cmp().
- Dictionary insertion order is guaranteed in modern Python.
- Set pop does not promise which element is removed.
- Repeated string.count inside a loop can be less efficient than a frequency-table approach; discuss *after* the learner attempts the string exercise.

## PNP alignment
- Patterns -> PDF pp. 12–13, 24
- Lists -> pp. 14, 28
- Strings -> pp. 8, 27 and later coding patterns
- Tuples/sets -> pp. 15, 28
- Dict -> pp. 16, 29

## Review workflow
- [ ] Demonstrate each concept with original runnable Python
- [ ] Attempt the five classroom string problems independently
- [ ] Attempt every distinct graded assignment when its source is confirmed
- [ ] Review correctness/edge cases/complexity
- [ ] Record actual date and GitHub evidence; do not pre-mark complete

**Academy Lecture 2 graded assignment set:** All four user-supplied screenshots have been verified and their unsolved practice statements recorded in [assignments/README.md](assignments/README.md). The four tasks remain pending independent Python solutions. PDF-to-GitHub page mapping is in [pdf-source-audit.md](pdf-source-audit.md).