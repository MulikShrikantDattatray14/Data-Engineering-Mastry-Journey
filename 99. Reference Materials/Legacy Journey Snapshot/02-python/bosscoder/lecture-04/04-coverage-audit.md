# Lecture 4 — Complete Source Coverage Audit

**Source:** Bosscoder user-supplied 'Modules, Error and Exceptions' lecture notes. **Coverage mapped, mastery pending**. Original academy notebook is not copied verbatim into this public repository.

## Module fundamentals
- [ ] Definition and purpose of Python modules, code reusability, organization and namespaces
- [ ] Module sources: Python-written, compiled extension, built-in
- [ ] Create custom `.py` module with function(s) and constant; import into second file
- [ ] Differentiate `import module` from `from module import name`
- [ ] Packages and `__init__.py`; mention namespace package nuance
- [ ] `__name__ == '__main__'` direct execution vs import
- [ ] Standard library inventory: os, sys, math, random, time, datetime, json, pickle, re, csv, collections

## Namespaces and scopes
- [ ] Namespace concept and purpose
- [ ] Local names and function lifetime
- [ ] Enclosing names and nested functions
- [ ] Global/module names and reading globals
- [ ] Built-in namespace
- [ ] `nonlocal` keyword and outer scope mutation
- [ ] LEGB resolution precedence with local, enclosing, global and built-ins
- [ ] Recreate example printing values from three distinct nested scopes

## Errors
- [ ] Syntax errors, including missing colon / invalid assignment syntax
- [ ] Indentation errors
- [ ] Runtime exception examples: out-of-range list access and missing file
- [ ] Logical errors and off-by-one indexing
- [ ] Distinguish parse-time, run-time and wrong-result behavior

## Exceptions
- [ ] What is an exception and why handling is needed
- [ ] `try` and specific `except`
- [ ] Bare except example plus dangers of catching too broadly
- [ ] Custom exception class inheriting from `Exception`
- [ ] Multiple `except` branches with ValueError/ZeroDivisionError
- [ ] `else` executes on successful try
- [ ] `finally` cleanup and limitations
- [ ] `BaseException` hierarchy and subclasses: SystemExit, KeyboardInterrupt, GeneratorExit, Exception, ArithmeticError, AttributeError, ValueError
- [ ] Intentionally `raise` exception from validation
- [ ] Final example of a classmethod and how it relates to earlier lecture's built-in decorators
- [ ] Summarize behavior of try/except/else/finally

## Additional skills indicated by 11 assessment screenshots (beyond core lecture outline)
- [ ] Async coroutine exception handling
- [ ] Nested try/except/finally output order
- [ ] Combining specific exception types in an except clause
- [ ] `contextlib.ExitStack` for managing multiple contexts
- [ ] Exception chaining and `__cause__`
- [ ] Exception propagation through nested function calls

## Review accuracy
- The lecture's explanatory prose sometimes omits underscores around `__init__.py`, `__name__` and `__main__`; preserve the valid Python syntax in original notes.
- Python namespace packages can exist without `__init__.py`.
- Python's standard library includes modules with varied implementation types, so 'built-in' should not describe the whole standard library.
- `finally` is for normal language-level cleanup, not a guarantee if the process is forcibly terminated.
- Distinguish a class note's intended concept from new topics introduced by an assignment.

## Source mapping
- PNP Python PDF: p. 20 (modules/packages), p. 21 (errors), p. 31 (scope), p. 32 (exceptions/context management).
- PNP Data Engineering extensions: robust ETL, source parsing, error quarantine and logging.

## Student protocol
- [ ] Verify each concept with a runnable Python example
- [ ] Reimplement classroom examples independently
- [ ] Solve all 11 Bosscoder graded MCQs only after the learner attempts them
- [ ] Review reasoning, exceptions and Python semantics
- [ ] Record completion date and evidence link; do not infer mastery from merely publishing notes

**Status: every box pending until practice is reviewed.**