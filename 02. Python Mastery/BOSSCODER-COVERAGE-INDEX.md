# Bosscoder Python — Seven-Lecture Source Index

The original Bosscoder lecture audits, teaching notes, exercises and assignment trackers are **copied and hash-verified in the Journey archive**. This is a navigation index, not a claim that every lecture assignment has been solved.

| Lecture | Topic | Notes | PDF coverage audit | Assignment tracking |
|---:|---|---|---|---|
| 1 | Python Refresher 1 | [Notes](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-01/README.md) | [Page-by-page audit](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-01/pdf-source-audit.md) | [View lecture folder](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-01/) |
| 2 | Python Refresher 2 | [Notes](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-02/README.md) | [Page-by-page audit](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-02/pdf-source-audit.md) | [View lecture folder](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-02/) |
| 3 | Functional Programming | [Notes](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-03/README.md) | [Page-by-page audit](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-03/pdf-source-audit.md) | [View lecture folder](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-03/) |
| 4 | Modules, Namespaces and Exceptions | [Notes](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-04/README.md) | [Page-by-page audit](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-04/pdf-source-audit.md) | [View lecture folder](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-04/) |
| 5 | Object-Oriented Programming | [Notes](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-05/README.md) | [Page-by-page audit](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-05/pdf-source-audit.md) | [View lecture folder](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-05/) |
| 6 | NumPy | [Notes](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-06/README.md) | [Page-by-page audit](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-06/pdf-source-audit.md) | [View lecture folder](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-06/) |
| 7 | Pandas and Data Visualization | [Notes](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-07/README.md) | [Page-by-page audit](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-07/pdf-source-audit.md) | [View lecture folder](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/lecture-07/) |

**Master audit:** [Seven original PDFs and 148-page verification index](../99.%20Reference%20Materials/Legacy%20Journey%20Snapshot/02-python/bosscoder/README-PDF-VERIFICATION-2026-11-06.md).

## Integration rules

1. For each concept, compare Bosscoder's unique explanation with PNP mentorship and official W3Schools; merge only missing details into **one** canonical `0. Foundation Notes.md`.
2. Apply JavaScript comparisons when they improve your understanding, especially for mutability, closures, iterators, promises/async versus Python counterparts, and list/dict/set behaviors.
3. Do not duplicate Bosscoder lecture contents inside the foundation notes. Preserve source links to full teaching notes.
4. Keep assignment question identity and all answer options when applicable, but do not add solution explanations before an independent attempt; verified assignments get their own properly documented solution records.
5. The current Python Study Mode checkpoint is Lesson 13A (sets), which is still unanswered. Course content presence is not mastery.

## Canonical chapter crosswalk — source-topic verification (2026-11-09)

The archived seven lecture PDF audits were compared at the **topic-outline level** with the canonical learning notes. The canonical links below are the *single study location* for their main concepts; source lessons retain fuller examples and all assignment question identities.

| Lecture | Canonical learning chapters | Unique caveat / remaining work |
|---|---|---|
| 01 Refresher 1 | [Basics](<00.%20Python%20Basics/0.%20Foundation%20Notes.md>), [Operators](<01.%20Operators%20and%20Decisions/0.%20Foundation%20Notes.md>), [Loops](<02.%20Loops/0.%20Foundation%20Notes.md>), [Lists](<03.%20Lists%20and%20Slicing/0.%20Foundation%20Notes.md>) | Source cube demonstration multiplies by 3; explicit boundary conditions override ambiguous classroom phrasing; bitwise operators and loop-else still require detailed practice |
| 02 Refresher 2 | [Loops](<02.%20Loops/0.%20Foundation%20Notes.md>), [Lists](<03.%20Lists%20and%20Slicing/0.%20Foundation%20Notes.md>), [Tuples and Sets](<04.%20Tuples%20and%20Sets/0.%20Foundation%20Notes.md>), [Dictionaries](<05.%20Dictionaries%20and%20Grouping/0.%20Foundation%20Notes.md>) | Python 2 `cmp(tuple1,tuple2)` does not exist in Python 3; check original notebook mutation state; nested-loop pattern assignments ungraded |
| 03 Functional Programming | [Functions](<06.%20Functions%20and%20Reuse/0.%20Foundation%20Notes.md>), [Comprehensions](<08.%20Comprehensions%20and%20Unpacking/0.%20Foundation%20Notes.md>), [Advanced Patterns](<12.%20Advanced%20Python%20Patterns/0.%20Foundation%20Notes.md>) | `list(map(...))[:10]` materializes entire iterator; use `itertools.islice` to remain lazy; graded lambda/closure questions pending |
| 04 Modules and Exceptions | [Modules and Files](<07.%20Modules%20and%20Files/0.%20Foundation%20Notes.md>), [Functions and Scope](<06.%20Functions%20and%20Reuse/0.%20Foundation%20Notes.md>) | Namespace packages can exist without `__init__.py`; distinguish `Exception` from `BaseException` and avoid catching system-exit signals |
| 05 OOP | [Object-Oriented Python](<16.%20Object%20Oriented%20Python/0.%20Foundation%20Notes.md>), [Advanced Patterns](<12.%20Advanced%20Python%20Patterns/0.%20Foundation%20Notes.md>) | `_name` convention and `__name` mangling are not security; `@classmethod` and diamond MRO need distinct explanations |
| 06 NumPy | [NumPy Foundations](<17.%20NumPy%20Foundations/0.%20Foundation%20Notes.md>), [pandas](<10.%20Pandas%20for%20Data%20Engineering/0.%20Foundation%20Notes.md>) | `np.add(a,b,c)` writes to output `c`; `flatten` copies, `ravel` may view; broadcasting and structured dtype nuances |
| 07 Pandas and Visualisation | [pandas](<10.%20Pandas%20for%20Data%20Engineering/0.%20Foundation%20Notes.md>), [Visualisation](<18.%20Data%20Visualisation/0.%20Foundation%20Notes.md>) | Pandas Index need not be unique; plots and plotting warnings are version dependent; never publish source private data |

**Evidence boundary:** This completes a **seven-lecture topic-to-canonical mapping**, not a line-by-line execution of all 148 source PDF pages, a confirmation of every lecture exercise's output, or any learner-graded assignment. Detailed original PDF cross-check files remain the authority on lecture coverage.
