# Part 4 — map(), filter(), zip(), ZIP Archives and reduce()

## 1. map(): lazy transformation
map(function, iterable, ...) returns an iterator applying a function to elements. With multiple iterables it stops at the shortest. It is lazy: values are computed when consumed.

```python
raw = ['5', '10', '15']
numbers = map(int, raw)
print(next(numbers))   # first converted number
print(list(numbers))  # remaining numbers; iterator is consumed

paired = map(lambda a, b: a + b, [1, 2, 3], [10, 20])
print(list(paired))
```

**Important:** `list(mapped)[:10]` constructs the **entire** list before slicing; it does not limit computation to ten elements. For lazy sampling, use `itertools.islice(mapped, 10)`.

## 2. functools.partial and composition
```python
from functools import partial

def scale(factor, value):
    return factor * value

double = partial(scale, 2)
print(list(map(double, [3, 4, 5])))
```

Functional pipelines can chain transformations; readability often improves with named functions and intermediate variables rather than deeply nested map/filter/reduce.

## 3. filter(): lazy selection
`filter(predicate, iterable)` retains values for which the predicate is truthy. It takes **one iterable** (not several direct iterables), but that iterable may come from `zip()`.

```python
records = [{'id': 1, 'ok': True}, {'id': 2, 'ok': False}]
accepted = filter(lambda row: row['ok'], records)
print(list(accepted))

names = ['Asha', 'Neel', 'Ria']
ages = [25, 17, 31]
adults = filter(lambda pair: pair[1] >= 18, zip(names, ages))
print(list(adults))
```

Can also filter objects by their attributes, as in the source lesson. Test that your predicate is defined for every expected input.

## 4. Chaining map/filter/reduce
```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]
filtered = filter(lambda value: value > 2, numbers)
transformed = map(lambda value: value * 10, filtered)
result = reduce(lambda total, value: total + value, transformed, 0)
print(result)
```

Try implementing the same pipeline as a loop or comprehension and compare readability, complexity and memory.

## 5. zip() combines iterables
```python
fields = ['id', 'status', 'amount']
values = [101, 'paid', 499]
print(list(zip(fields, values)))

short = list(zip([1, 2, 3], ['a', 'b']))
print(short) # stops at shorter iterable
```

With three iterables, each result is a three-item tuple. On modern Python, `zip(..., strict=True)` can detect mismatched lengths; ordinary zip silently stops at the shortest.

### Unzip via star-unpacking
```python
rows = [('east', 2), ('west', 3)]
regions, counts = zip(*rows)
print(regions, counts)
```

Empty input requires care: unpacking the empty result into two variables fails.

## 6. ZIP archive files are different from zip()
The lecture covers **two distinct topics** with similar names: the zip built-in (combining iterables) and archive files handled with the `zipfile` module.

```python
from pathlib import Path
from zipfile import ZipFile

Path('demo.txt').write_text('hello', encoding='utf-8')
with ZipFile('sample.zip', 'w') as archive:
    archive.write('demo.txt')

with ZipFile('sample.zip', 'r') as archive:
    print(archive.namelist())
    print(archive.read('demo.txt').decode('utf-8'))
```

The classroom notes also demonstrate walking a directory with `os.walk`, writing relative paths into an archive, extracting members with `extract()` and `extractall()`, and listing archive names with `namelist()`. Independently recreate those exercises. Do not extract untrusted archives without validating paths and contents; archive extraction can overwrite or escape intended directories if handled unsafely.

## 7. reduce(): cumulative aggregation
`functools.reduce(function, iterable, initializer?)` combines items with a two-argument function. With an initializer it begins from that value. Without one, an empty iterable raises TypeError.

```python
from functools import reduce

factors = [2, 3, 4]
product = reduce(lambda acc, value: acc * value, factors, 1)
print(product)
```

The source includes cumulative addition, maximum selection, string concatenation and an initializer example. Solve those as classroom exercises independently. Prefer `sum()`, `max()`, `str.join()` or a plain loop when clearer and more efficient.

## 8. Data Engineering comparison
- `map` transforms records; `filter` selects records; `zip` pairs related streams; `reduce` aggregates.
- All three `map`, `filter` and `zip` produce lazy iterators in Python 3.
- Materializing an iterator with `list()` consumes memory proportional to its output.
- Streaming an iterator can reduce memory use, but downstream code must not assume it can traverse the same iterator twice.
- A source-to-target ETL pipeline usually benefits from separate pure transformations and isolated I/O operations.

## No-answer practice prompts
- [ ] Demonstrate map with named and lambda functions and with two iterables.
- [ ] Revisit a lazy map iterator before and after consuming its first value.
- [ ] Use partial to configure a reusable mapper.
- [ ] Filter numeric records, then zip two related sources and filter paired values.
- [ ] Filter custom object instances based on a field.
- [ ] Compare a map/filter/reduce chain with clear imperative code.
- [ ] Zip three iterables, handle unequal lengths and unzip pairs.
- [ ] Create a ZIP archive, list it, selectively extract a safe member, and explain traversal risks.
- [ ] Recreate cumulative sum, maximum, joining strings and seeded reduction.

**Status:** No graded assignment solutions included; mastery pending.