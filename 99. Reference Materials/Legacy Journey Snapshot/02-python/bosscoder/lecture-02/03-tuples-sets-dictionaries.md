# Tuples, Sets, Dictionaries

## Tuples
Tuples are ordered, immutable sequences; duplicates are allowed. Parentheses are conventional, but the comma makes a tuple. One element needs a trailing comma.

```python
location = (18.52, 73.85)
only_one = (42,)
values = (2, 4, 2, 5)
print(values.count(2), values.index(5))
print(len(values), min(values), max(values), tuple([1, 2]))
```

Tuple index(value, start, stop) supports optional range limits and raises ValueError if absent. Tuples can nest and can hold mutable objects; tuple immutability does not make nested lists immutable.

```python
nested = ((1, 'paid'), (2, 'pending'))
for identifier, status in nested:
    print(identifier, status)
```

Note: the class notes mention cmp(tuple1, tuple2), which is not a Python 3 built-in. Use valid comparisons such as (1, 2) < (1, 3) where elements are comparable.

## Sets
A set stores unique hashable elements and does not promise a particular order.

```python
source = {1, 2, 3}
destination = {3, 4}
print(source | destination) # union
print(source & destination) # intersection
print(source - destination) # difference
print(source ^ destination) # symmetric difference
```

Use add(x) to include an item, remove(x) to delete or raise KeyError, discard(x) to safely delete an absent value, pop() to remove an arbitrary element, and copy() for a shallow copy. The empty set is set(), not {}.

## Dictionaries
Dictionaries are mutable maps from unique hashable keys to values. Modern Python (3.7+) guarantees insertion order for dictionary iteration.

```python
customer = {'name': 'Asha', 'age': 25}
customer['city'] = 'Pune'
customer['age'] = 26
also = dict(name='Asha', age=26)
print(customer, also)
```

The supplied Lecture 2 ends after dictionary creation and basic properties. Deeper methods (get, items, defaultdict, Counter) are covered later in the PNP PDF, not falsely attributed to this lecture.

## Independent questions
- [ ] Create one-element and nested tuples
- [ ] Use count and index including search boundaries
- [ ] Explain why a tuple containing a list can indirectly change
- [ ] Convert list to tuple and compare tuples
- [ ] Demonstrate set add/remove/discard/pop/copy safely
- [ ] Compare union, intersection, difference and symmetric difference
- [ ] Create dictionaries in two ways; demonstrate updates and insertion order
- [ ] Describe practical deduplication and source/target reconciliation examples