# Day 1 — Slot 02: Python interactive fundamentals

**Study date:** 2026-11-06 (Asia/Kolkata). **Session paused after Lesson 12B; next: Lesson 13A, sets.**
**Status:** Guided concepts and independent exercises reviewed in conversation; not yet verified against PNP source PDF pages 1–8. Actual focused minutes and Python PDF pages: **not logged / 0 verified**.

## Concepts practiced in order

| Lesson | Work and review | Session result |
|---|---|---|
| 1–2 | `int`, `str`, `type()`, variables and dynamic typing | Output predictions correct conceptually |
| 3 | Type conversions `str()`, `int()`, `float()` | 3/3 conceptually correct; exact `<class 'float'>` formatting corrected |
| 4 | Arithmetic including `/`, `//`, `%`, `**` | Basics correct; negative modulo remains a revision item |
| 5 | Comparison operators, type mismatch and conversions | First attempt 1/4; retry 4/4 |
| 6 | `and`, `or`, `not` | 4/4 correct |
| 7 | `if`, `elif`, `else`, colons and indentation | Independent status classifier corrected and reviewed |
| 8 | `range()`, direct `for` iteration, sum accumulator | `range` retry correct; both direct iteration and index-loop solutions constructed |
| 9 | `while`, threshold and safe list boundaries | Independent program corrected; all four stated test cases passed |
| 10 | `break`, `continue`, nested indentation | Independent program corrected; expected total 700 |
| 11 | Lists vs JS arrays, `append`, `len`, clean sales, slicing | Sales-cleaning exercise correct; slicing eventually 4/4, repeated step revisions needed |
| 12 | Tuples, indexing, immutability, list-to-tuple conversion | Final independent tuple construction and output accepted |
| 13 | Sets and uniqueness | Explanations given; **Question 13A not answered, not complete** |

These are **ChatGPT-guided exercise reviews**, not formal source-PDF completions, Bosscoder assignments or measured focus time. The actual PDF pp. 1–8, string coverage, setup and source drills must still be checked before credit.

## Selected independent student submissions and corrections

### Lesson 7B — transaction classification (final independent submission)

```python
amount = 750
status = "SUCCESS"

if status != "SUCCESS":
    print("Failed")
elif amount >= 1000:
    print("High value")
else :
    print("Regular")
```

Reviewed correct for sample `Regular` and failed/successful boundary cases. Initial submitted version omitted `:` after `else`.

### Lesson 8C — accumulator (two final independent approaches)

```python
transactions = [100, 250, 300, 150, 200]
total = 0

for i in transactions:
    total = total + i

print(total)
```

Output: `1000`. Learner additionally proposed independent index-based loop:

```python
for i in range(len(transactions)):
    total=total + transactions[i]
```

This also totals `1000` **when run with a freshly reset total**. Earlier learner attempts incorrectly used `range(transactions)` and `range(int(transactions))`.

### Lesson 9B — while loop (final learner condition)

```python
transactions = [200, 350, 500, 400, 100]
total = 0
i = 0

while total < 1000 and i <= len(transactions)-1:
    total = total + transactions[i]
    i = i + 1

print("Total:", total)
print("Transactions processed:", i)
```

Output on given data: `Total: 1050`, `Transactions processed: 3`. Reviewed on empty, below-target and exact-1000 cases. Multiple preceding attempts used `total <= 1000` or an out-of-bounds index.

### Lesson 10B — skip negatives and break at zero (final learner submission)

```python
transactions = [150, -20, 300, -10, 250, 0, 400]
total = 0

for i in transactions:
    if i < 0:
        continue
    elif i == 0:
        break
    else:
        total = total + i

print(total)
```

Expected and reviewed output `700`. Previous submissions contained missing colons, assignment `=` instead of equality `==`, and inconsistent indentation.

### Lesson 11B — sales data cleaning (independent final)

```python
sales = [1200, 1500, -300, 1800, 0, 2200]
cleaned_sales = []

for i in sales:
    if( i > 0):
        cleaned_sales.append(i)

print(cleaned_sales)
print(len(cleaned_sales))
```

Output: `[1200, 1500, 1800, 2200]` then `4`. Input list stays unmodified. Review covered empty/all-invalid and duplicate cases.

### Lesson 11D — final slices, derived from successive learner corrections

```python
sales = [100, 200, 300, 400, 500, 600, 700]
first_three = sales[0:3]
last_three = sales[-3::]
every_second = sales[::2]
reversed_sales = sales[::-1]
```

Expected: first three, last three, every second from index 0, reverse all. Learner independently corrected `sales[-1:-3]`, `sales[1::2]`, `sales[1::1]`, `sales[::1]` before arriving at `sales[::2]`. Full values matched exercise expected; source list remains unchanged.

### Lesson 12B — tuple immutable update (final independent solution)

```python
transaction = (101, "SUCCESS", 2500, "INR")

print(transaction[0])
print(transaction[2])
print(transaction[len(transaction)-1])
print(len(transaction))

updated_transaction = []

for i in transaction:
    if i == 2500:
        updated_transaction.append(3000)
    else:
        updated_transaction.append(i)

updated_transaction=(tuple(updated_transaction))
print(updated_transaction)
```

Expected outputs: `101`, `2500`, `INR`, `4`, `(101, 'SUCCESS', 3000, 'INR')`. New variable is now a tuple; original tuple unchanged. Follow-up revision: replacing by field index is more reliable than replacing every value equal to `2500`.

## Outstanding revision / continuation

- **Revision list:** negative modulo; `range()` exclusive stop and step; safe loop termination and index boundaries; indentation/colons/equality operator; slicing (especially negative steps); tuple immutability/field-position changes.
- **Exact next question:** Lesson **13A**, Python sets: `ids = {10,20,30,20,10}`; `ids.add(40)`; `ids.add(30)`; predict `len(ids)`, `20 in ids`, `50 in ids`. No answer submitted yet.
- **Source work still pending:** verify official Python PDF pages 1–8 and associated exercises, cover program setup, strings and input/output gaps, and record actual completed source pages (currently 0/8).
- **Learner's order instruction:** Resume at **09:00 IST on November 7**. First close **November 6's remaining backlog across Slots 2 and 4 (plus any outstanding mandatory day review)**. Only then begin the November 7 targets across all four slots. This is a plan, **not evidence of future attendance or completion**.

[Slot 4 follow-up](slot-04-python.md) · [Nov 6 session index](README.md) · [Progress data](../../../progress/daily-progress.json)


## Diwali holiday schedule update — November 8, 2026

The learner confirmed **no study on November 7 or November 8** because of Diwali holidays. The previously planned November 7 at 09:00 IST restart is **superseded**. Resume on **November 9, 2026**, from the unchanged first unanswered task: **Python Slot 2, Lesson 13A (sets)**. Close the remaining November 6 Slot 2 and Slot 4 backlog (plus mandatory review) first; then tackle November 7 and November 8 pending targets, and only afterwards start the November 9 targets. No holiday completion credit or retroactive attendance is claimed. See [daily tracker](../../../progress/daily-progress.json).
