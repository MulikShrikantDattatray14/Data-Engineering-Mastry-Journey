# Lists and Strings — Complete Operations and Challenges

## Lists
Python lists are ordered, mutable, allow duplicates, mixed types and nesting, can grow and shrink, and support indexing, slicing, iteration and list comprehensions.

```python
orders = [101, 102, 101]
orders.append(103)
print(orders[0], orders[-1], orders[:2])
squared = [i * i for i in range(4)]
```

## Every list method in the lecture
| Method | Meaning | Important note |
|---|---|---|
| append(x) | Add one item at the end | In-place, returns None |
| insert(i,x) | Insert at index | Shifts later positions |
| remove(x) | Remove first matching value | ValueError if absent |
| pop(i) | Remove and return by index, or last item | IndexError for empty/invalid index |
| clear() | Remove everything | In-place |
| sort() | Sort in place | Returns None |
| reverse() | Reverse current order | Does not sort |
| count(x) | Count occurrences | Returns integer |
| extend(iterable) | Append each element of iterable | Distinct from append(list) |

len(list) is a built-in function; sorted(list) creates a new sorted list. To compare behavior fairly, start each method example from a fresh list—previous notebook cells can change outputs.

```python
fruits = ['pear', 'apple', 'pear']
fruits.append('melon')
fruits.insert(1, 'kiwi')
print(fruits.count('pear'))
fruits.remove('pear')
removed = fruits.pop()
fruits.extend(['plum', 'date'])
fruits.sort()
fruits.reverse()
print(removed, fruits)
fruits.clear()
print(fruits)
```

## Strings
Strings are immutable, ordered, indexed sequences of Unicode text. They support concatenation (+), repetition (*), membership (in/not in) and iteration.

```python
label = 'Order' + ' ' + 'Ready'
print(label * 2, 'Ready' in label)
for ch in 'ETL':
    print(ch)
```

## Every string function family in the lecture
| Area | Methods/functions |
|---|---|
| Length | len(text) |
| Case | upper, lower, title, capitalize, swapcase |
| Search | find, rfind, index, count |
| Validation | isalpha, isdigit, isalnum, isspace, isupper, islower |
| Trim/replace | strip, lstrip, rstrip, replace |
| Split/join | split, join |
| Alignment | center, ljust, rjust, zfill |
| Formatting | format, f-strings |

```python
raw = '  paid,Pending,PAID  '
status = [v.strip().lower() for v in raw.split(',')]
print('|'.join(status))
print('abcABC'.swapcase())
print('banana'.find('na'), 'banana'.rfind('na'))
print('A42'.isalnum(), '42'.isdigit(), '  '.isspace())
print('7'.zfill(4), 'x'.center(5, '.'))
print('rows={}'.format(3), f'rows={3}')
```

Important subtleties: find returns -1 if missing, index raises ValueError; strip(chars) removes any specified edge characters, not an exact substring; strings are immutable.

## Five classroom string exercises (solutions withheld)
- [ ] Determine whether one string is a rotation of another
- [ ] Find the first non-repeating character
- [ ] Find a longest palindromic substring
- [ ] Check whether two strings are isomorphic via a one-to-one mapping
- [ ] Check whether one string is a subsequence of another (not necessarily adjacent)

Write examples, edge cases, independent Python code, and complexity explanations for each. The lecture contains worked examples, but these notes deliberately avoid posting the exact source answers.

## Data Engineering context
Strings help parse CSV-like data, normalize identifiers, validate event attributes, and clean incoming records. Lists are useful for small in-memory batches, but large-scale data needs better memory-aware tools.