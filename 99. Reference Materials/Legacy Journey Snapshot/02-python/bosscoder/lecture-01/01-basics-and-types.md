# Part 1 — Introduction, Data Types, Variables and Keywords

## 1. What is Python?

Python is a general-purpose, high-level programming language with readable syntax. It lets us express instructions without managing registers or explicit memory allocation in typical application code. For Data Engineering it is useful for extracting records from APIs, validating files, running transformations, automating recurring jobs and testing pipelines.

Python is usually described as an *interpreted* language. A useful refinement: the commonly used CPython implementation first compiles source into bytecode, then executes it using its virtual machine. So the phrase 'interpreted = reads each source line and directly executes it' is a simplified introductory model.

```python
print('Hello, data engineering!')
```

Compare with JavaScript: both languages are dynamically typed, but their syntax, object model, module systems and handling of truthiness are different.

## 2. Values and their types

A **value** is an object holding information; its type describes supported operations. Python uses `type()` to inspect the type of an object.

```python
examples = [42, 3.5, 2 + 4j, True, 'orders', [1, 2], (1, 2),
            {1, 2}, frozenset([1, 2]), {'status': 'ok'}, b'raw']
for value in examples:
    print(repr(value), type(value).__name__)
```

| Group | Python type | Meaning | Important property |
|---|---|---|---|
| Numeric | `int` | Whole number | Arbitrary-size integers (subject to memory) |
| Numeric | `float` | Floating-point approximation | Not reliable for exact monetary arithmetic |
| Numeric | `complex` | Real + imaginary (`j`) | Useful for specialized math |
| Boolean | `bool` | `True` or `False` | A subtype of `int`, but conceptually logical |
| Sequence | `str` | Unicode text | Immutable |
| Sequence | `list` | Ordered collection | Mutable, duplicates allowed |
| Sequence | `tuple` | Ordered collection | Immutable |
| Set | `set` | Unique hashable elements | Mutable, no guaranteed order |
| Set | `frozenset` | Unique hashable elements | Immutable |
| Mapping | `dict` | Key–value mapping | Mutable, keys unique, insertion order preserved |
| Binary | `bytes` | Sequence of byte values | Immutable; unlike Unicode `str` |

### Lists, tuples and dictionaries in context

```python
order_ids = [101, 102, 101]             # list allows repeated values
coordinate = (18.52, 73.85)            # tuple groups fixed fields
distinct_ids = set(order_ids)           # unique values, no order guarantee
row = {'order_id': 101, 'amount': 500}  # mapping, keys are unique
row['status'] = 'paid'                   # dictionary can be updated
print(len(order_ids), len(distinct_ids), row)
```

**Python ↔ JS:** a Python `list` resembles a JS array in many basic uses; a `dict` resembles an object or `Map`, but the behavior and APIs differ. A Python set is not a list with duplicates removed while retaining a guaranteed order.

### Bytes vs strings

```python
text = 'café'
encoded = text.encode('utf-8')
print(type(text).__name__, type(encoded).__name__)
print(encoded.decode('utf-8'))
```

Data Engineering connection: receiving file bytes from a network or object store and decoding them correctly is critical for reliable ingestion.

## 3. Variables are names bound to objects

```python
customer = 'Asha'
age = 28
print(customer, age)

a = b = c = 10               # chained assignment
x, y = 3, 7                 # unpacking
x, y = y, x                 # swap values
print(a, b, c, x, y)
```

Names may start with a letter or underscore and continue with letters, numbers or underscores. Python identifiers are case sensitive (`score` and `Score` are different); reserved keywords cannot be used as names. Use descriptive `snake_case` for variables.

**Mutation matters:** two names can refer to the same mutable object.

```python
first = [1, 2]
second = first
second.append(3)
print(first)  # [1, 2, 3]
```

## 4. Local vs global names

```python
status = 'pending'

def describe_order():
    local_id = 101
    print(local_id, status)  # reads the global name

describe_order()

def set_status():
    global status             # explicitly rebinds module-level name
    status = 'paid'

set_status()
print(status)
```

Prefer function parameters and return values over changing global variables in production scripts because mutable shared state makes testing harder.

## 5. Deleting names

```python
record_count = 5
del record_count
try:
    print(record_count)
except NameError:
    print('The name is no longer defined')
```

`del` removes a binding or item; it does not universally guarantee immediate destruction of an underlying object if other references still exist.

## 6. Python keywords

```python
import keyword
print(keyword.iskeyword('for'))
print(keyword.iskeyword('order_id'))
print(len(keyword.kwlist))
```

The keyword list can evolve between versions. Use `keyword.kwlist` or `help('keywords')` to inspect the running interpreter rather than memorizing a fixed count.

## 7. Inputs and outputs

```python
raw = input('How many orders? ')
try:
    count = int(raw)
    print(f'Processing {count} orders')
except ValueError:
    print('Enter a valid whole number')
```

`input()` returns a **string**. Explicit conversion is required for numeric arithmetic. `print()` displays output; `return` sends a value from a function to its caller.

## Active recall (solve without scrolling back)

1. Why does changing `second` in the shared-list example affect `first`?
2. Which data structures above preserve order, allow duplicates and support mutation?
3. Explain the difference between text and byte data using one file example.
4. What happens when a local name shadows a global name?
5. Why is `keyword.iskeyword()` safer than hard-coding the number of reserved keywords?

**Status:** Explanation published; practice and mastery unchecked.
