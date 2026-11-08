# Part 3 — Control Flow, Loops and Classroom Exercise Practice

## 1. Conditional execution

`if`, `elif` and `else` let a program choose between paths. Indentation determines a block's scope.

```python
temperature = 28
if temperature < 15:
    category = 'cold'
elif temperature < 30:
    category = 'moderate'
else:
    category = 'hot'
print(category)
```

Only the first true branch runs in a single if/elif/else chain. Nested conditions are useful but should not hide inconsistent or overlapping boundaries. Test exact endpoints and the values immediately around them.

### Decision-making classroom topics to revisit

- [ ] The provided numeric-cube classification exercise: reason from its written requirement before trusting the demonstration code.
- [ ] The time-of-day greeting exercise: test all stated ranges and the conflicting boundary at hour 9.
- [ ] Explain when nested conditions are needed and when a flat `elif` chain is clearer.

**Important:** The original lecture example about taking a number's *cube* has a discrepancy between the written description and its shown arithmetic. We will diagnose it when the learner attempts the problem, not reproduce an incorrect worked answer.

## 2. `for` loops and `range`

Python's `for` iterates over an iterable. `range(start, stop, step)` excludes `stop`, similar to slice bounds.

```python
for record_id in range(101, 105):
    print(record_id)

for status in ['paid', 'pending', 'cancelled']:
    print(status.upper())
```

Use nested loops when each outer item requires checking several inner items. Be aware that a nested loop can be substantially more expensive than a single loop.

## 3. `while` loops

Use `while` when repetition depends on a condition rather than stepping through a known collection.

```python
retry_count = 0
while retry_count < 3:
    print('Attempt', retry_count + 1)
    retry_count += 1
```

A loop must either change the condition or deliberately exit. Otherwise it may run forever.

## 4. `break` and `continue`

```python
for item in [2, -1, 4, 0, 9]:
    if item == 0:
        break          # stop the whole loop
    if item < 0:
        continue       # skip this iteration
    print(item)
```

**Loop `else`:** Unlike `if/else`, a `for`/`while` loop's `else` runs when the loop finishes normally without a `break`. This was present in the supplied lecture syntax and should not be missed.

```python
items = ['done', 'done', 'pending']
for item in items:
    if item == 'failed':
        print('Failure detected')
        break
else:
    print('No failures found')
```

## 5. Recursion — related assignment prerequisite

The class notes' primary factorial practice uses loops, but the separately supplied Bosscoder factorial assignment **explicitly requires recursion**. We will teach recursive function calls and base cases before that assignment, without publishing its answer.

```python
def countdown(n):
    if n <= 0:
        return 'finished'
    return countdown(n - 1)

print(countdown(3))
```

This is a generic recursion demonstration, not the factorial assignment solution. Recursion uses call-stack space, and CPython enforces a recursion-depth limit; large inputs may require special discussion after attempting the relevant question.

## 6. Classroom practice inventory — work independently

These are short, independently worded prompts corresponding to the classroom's coverage, deliberately without full answers.

| # | Practice objective | Key skill |
|---|---|---|
| 1 | Create typed variables and display a formatted sentence | Binding, conversions |
| 2 | Show local and global scopes in functions | Scope |
| 3 | Try chained assignment, unpacking, deletion and catching `NameError` | Names and exceptions |
| 4 | Inspect Python keywords and check reserved names | Standard library |
| 5 | Read text input, convert valid numeric data, and handle invalid input | I/O and conversion |
| 6 | Predict arithmetic/comparison/assignment/logical/bitwise/identity outputs | Operators |
| 7 | Solve seven substring-slicing variations | Indexing/slicing |
| 8 | Classify a numeric expression using if/else and a completion message | Conditions |
| 9 | Classify hours of the day without off-by-one errors | Branch boundaries |
| 10 | Find primes in a small interval using nested loops | Loops and divisibility |
| 11 | Reverse the decimal digits of an integer | While loops |
| 12 | Compute factorial through a for loop | Repetition/accumulator |
| 13 | Compute factorial through a while loop | Repetition/accumulator |
| 14 | Decide whether a sequence is a palindrome using repeated comparisons | Loops/string indexing |
| 15 | Explain which statements execute after a `break` | Control flow |
| 16 | Implement a sentinel input loop with an early stop and skip conditions | `break`/`continue` |

These classroom exercises are **not the same as the 12 separately graded Bosscoder assignments**. Both inventories are tracked; assignment answers remain pending.

## 7. Data Engineering mini-practice (original)

Use a list of simple synthetic order records and produce a one-line status summary without external libraries.

```python
orders = [
    {'id': 1, 'status': 'paid', 'amount': 450},
    {'id': 2, 'status': 'pending', 'amount': 300},
    {'id': 3, 'status': 'paid', 'amount': 150},
]

# Your task: design your own loop/conditional to summarize the records.
# Do not overwrite the source records.
```

## 8. Final concept checkpoint

- [ ] Explain all operator categories and the difference between `is` and `==`.
- [ ] Predict and test slicing with negative indices, a step and out-of-range bounds.
- [ ] Explain what makes a `for` loop terminate and how a `while` loop can fail to terminate.
- [ ] Give an example where `break` changes whether loop `else` runs.
- [ ] Compare an iterative and recursive approach conceptually, without solving the graded assignment.
- [ ] Complete the matching PNP practice and [Bosscoder assignment queue](../python-refresher-1-coverage.md).

**Status:** Practice targets published, no exercises or graded assignments marked solved.
