# Part 2 — Python Functions, Purity and Higher-Order Thinking

## 1. Define, call and return
Define a function with def and indentation. Calling executes its body; return gives a value to the caller. When a function reaches the end without returning, it returns None.
```python
def describe_status(status):
    return f'Status: {status}'

print(describe_status('paid'))
```

## 2. All parameter and argument types from the lecture
```python
def describe_order(order_id, region='unknown'):
    return f'{order_id}: {region}'

print(describe_order(101))                   # positional + default
print(describe_order(region='west', order_id=102))  # keyword

def total_amount(*amounts):
    return sum(amounts)                      # variable positional arguments

def metadata(**properties):
    return dict(properties)                  # variable keyword arguments

print(total_amount(10, 20, 30))
print(metadata(source='api', status='ok'))
```

A common pitfall is a mutable default list/dictionary. Use None as a sentinel and create a fresh collection when needed.

## 3. Scope, nested functions and closures
```python
rate = 2

def make_multiplier(factor):
    def multiply(value):
        return factor * value              # remembers outer factor
    return multiply

triple = make_multiplier(3)
print(triple(5))
```

A local name is scoped to the function. A nested function can close over variables from its enclosing function. Rebinding a module-level name inside a function requires a global declaration, which is often best avoided in reusable transformations.

## 4. Recursion and the base case
```python
def count_down(n):
    if n <= 0:
        return 'done'
    return count_down(n - 1)

print(count_down(3))
```

Recursion needs a base case, progress toward it, and an awareness of call-stack limits. The academy's separately graded factorial question remains **unanswered** until the learner attempts it.

## 5. Docstrings and type annotations
```python
def format_row(row_id: int, status: str) -> str:
    '''Format one record for readable logs.'''
    return f'{row_id}:{status}'

print(format_row.__doc__)
print(format_row.__annotations__)
```

Type annotations improve documentation and tooling but usually do not enforce types at runtime without additional validation.

## 6. Pure versus impure functions
```python
def add_tax(amount, rate):
    return amount * (1 + rate)

processed = 0
def record_progress():
    global processed
    processed += 1
    return processed
```

The first function is pure for ordinary numeric inputs; the second modifies external state and is impure. The supplied notes also feature pure-style arithmetic, concatenation, new-list creation, filtering, recursive Fibonacci and GCD examples. Reimplement those independently during practice rather than copying the original lesson's implementations.

Purity means both determinism and no observable side effects. Printing, logging, writing a file, sending requests and mutating an input collection are side effects. Real ETL needs side effects at controlled boundaries.

## 7. First-class functions and higher-order functions
Functions can be stored in variables and dictionaries, passed into other functions and returned from functions.
```python
def uppercase(value):
    return value.upper()

def apply(transform, value):
    return transform(value)

functions = {'upper': uppercase, 'strip': str.strip}
print(apply(functions['upper'], 'paid'))
print(apply(functions['strip'], ' paid '))
```

A higher-order function accepts or returns a function. Functions-as-values are useful for interchangeable validators, parsers and transformations.

## 8. Composition
```python
def clean(value):
    return value.strip()

def normalize(value):
    return value.lower()

def process(value):
    return normalize(clean(value))

print(process('  PAID  '))
```

## Checkpoints
- [ ] Demonstrate positional, keyword and default arguments, *args and **kwargs.
- [ ] Show return versus print, None when no return, and the mutable default trap.
- [ ] Explain local/global/nested scope and closures.
- [ ] Write a small recursive function with a base case.
- [ ] Add a docstring and annotations and explain their limitations.
- [ ] Identify pure/impure functions and their side effects.
- [ ] Pass, store and return a function; compose two transformations.

**Status:** Source concepts mapped; practice pending.