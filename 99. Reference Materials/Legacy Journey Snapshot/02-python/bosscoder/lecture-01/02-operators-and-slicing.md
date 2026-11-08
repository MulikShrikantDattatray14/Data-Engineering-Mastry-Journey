# Part 2 — Operators, Type Conversion and Slicing

## 1. Arithmetic operators

These work on numbers (although `+` and `*` have additional meanings for some collections).

```python
left, right = 17, 5
print(left + right)   # 22: addition
print(left - right)   # 12: subtraction
print(left * right)   # 85: multiplication
print(left / right)   # 3.4: true division
print(left // right)  # 3: floor division
print(left % right)   # 2: remainder
print(left ** right)  # exponentiation
```

**Watch the negative-number case:** Python's `//` rounds toward negative infinity, and `%` is consistent with that floor-division rule. Do not casually assume it truncates toward zero.

## 2. Comparison operators

```python
amount, limit = 1200, 1000
print(amount == limit)   # equality
print(amount != limit)   # inequality
print(amount > limit)
print(amount < limit)
print(amount >= limit)
print(amount <= limit)
```

Comparison results are Boolean. Comparisons may be chained (`0 <= amount <= 10000`) instead of using repeated `and` operations.

## 3. Assignment and augmented assignment

```python
count = 8
count += 2
count -= 1
count *= 3
count /= 2           # `/=` typically changes numeric result to float
count %= 5
count **= 2
count //= 2
print(count)
```

Predict the type and value after each line, not just the final value.

## 4. Logical operators: and, or, not

```python
delivered = True
paid = False
print(delivered and paid)
print(delivered or paid)
print(not paid)
```

In Python, `and` and `or` return an operand, not always a Boolean. Example: `'' or 'unknown'` evaluates to `'unknown'`. They also short-circuit, which matters when a second expression is expensive or unsafe.

## 5. Bitwise operators

Bitwise operations work with binary representations of integers. They are different from logical `and` and `or`.

```python
x, y = 6, 3     # binary 110 and 011
print(x & y)    # AND bits
print(x | y)    # OR bits
print(x ^ y)    # XOR bits
print(~x)       # invert bits, equivalent to -x - 1
print(x << 1)   # shift left
print(x >> 1)   # shift right
```

Review each bit position independently. For a data-engineering context, bitmasks can sometimes encode flags, though they are less central than Python's data collections.

## 6. Membership operators

```python
allowed = {'paid', 'shipped'}
print('paid' in allowed)
print('cancelled' not in allowed)
```

`in` asks whether an item belongs to a collection. Dictionary membership checks **keys**, not values. Lists and sets can differ substantially in membership lookup costs.

## 7. Identity versus equality

```python
values = [10, 20]
same_contents = [10, 20]
alias = values
print(values == same_contents)  # equal contents
print(values is same_contents)  # distinct objects
print(values is alias)          # same object
```

`==` compares values, while `is` compares object identity. Small integers or interned strings may be reused as an implementation detail: never write numeric equality checks with `is`. Identity checks are appropriate for a singleton such as `None` (`if item is None:`).

## 8. Type conversion

**Implicit conversion:** for example, arithmetic involving an integer and a float usually produces a float.

```python
print(5 + 2.5)
print(type(5 + 2.5).__name__)
```

**Explicit conversions:**

```python
print(int('42'))
print(float('12.75'))
print(str(123))
print(list('abc'))
print(tuple([1, 2]))
print(set([1, 1, 2]))
print(dict([('a', 10), ('b', 20)]))
print(bool('False'))   # nonempty string -> True
```

`int(9.9)` truncates toward zero rather than rounding to the nearest integer. `int('9.9')` raises `ValueError`. Converting an empty string with `bool('')` yields False; a nonempty string such as `'False'` is truthy.

Data Engineering connection: incoming CSV columns often arrive as strings and need safe parsing, validation, and type conversion before loading.

## 9. Indexing and slicing

Syntax: `sequence[start:stop:step]`. `start` is included, `stop` is excluded; step defaults to 1.

```python
word = 'pipeline'
print(word[0])       # first character
print(word[-1])      # last character
print(word[0:4])     # first four
print(word[2:])      # skip first two
print(word[::2])     # every second character
print(word[::-1])    # reversed string
print(word[-100:])   # slicing safely clamps the start
```

An invalid single index may raise `IndexError`, while many overshooting slices simply return a smaller slice. `step=0` is invalid. Slices also work on lists and tuples.

### Practice prompts (new variations, not graded Bosscoder answers)

1. For `text = 'dataplatform'`, predict four different slices before running them.
2. Explain the difference between `is` and `==` using two distinct lists with identical elements.
3. Show a negative integer where `/`, `//` and `%` illustrate floor division.
4. Convert a list of strings `['17', '0', 'abc']` to integers, retaining information about invalid rows.
5. Predict the result of every augmented assignment in the example.

**Status:** Independent notes ready; topic mastery and original assignment practice pending.
