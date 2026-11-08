# Python Mastry

> **Quick revision / canonical foundation notes:** [Open numbered Python foundation folders](<0. Foundation Notes/README.md>). Each topic has one concise `0. Foundation Notes.md` with beginner explanations, runnable examples and JavaScript comparisons. The full 80-page PDF and existing detailed lessons below remain unchanged as source references; **no new practice question files or source-completion credit are created by these notes**.


A continuous path through all 80 pages of the [original Python for Data Engineering PDF](<Source/1793477658005.pdf>). Its 7 parts contain 76 lesson, practice, and revision entries. The [Start Here notes](<00. Start Here.md>) cover the opening pages and introduce the store dataset used throughout.

The PDF is the main source. These notes explain its concepts with small original examples and expected output. Relevant [W3Schools Python topics](https://www.w3schools.com/python/) appear at the end of matching lessons, with direct source links. The 36 topics you first supplied remain in Part 1; later lessons add relevant W3Schools extensions.

## Start here

1. Read [Start Here](<00. Start Here.md>) for the data files, planted edge cases, and interview context.
2. Follow Parts 1–7 in order, or use the index below to return to a topic.
3. Run the code, change one value, predict the result, and then try each **Your turn** prompt.

| Part | Focus | PDF pages | Entries | Open |
|---:|---|---:|---:|---|
| 1 | Python from Zero | 5–24 | 20 | [Part 1 index](<1. Python from Zero/README.md>) |
| 2 | Python Foundations | 25–34 | 10 | [Part 2 index](<2. Python Foundations/README.md>) |
| 3 | Advanced Python | 35–40 | 6 | [Part 3 index](<3. Advanced Python/README.md>) |
| 4 | DSA and Complexity | 41–57 | 17 | [Part 4 index](<4. DSA and Complexity/README.md>) |
| 5 | Coding Round Patterns | 58–68 | 11 | [Part 5 index](<5. Coding Round Patterns/README.md>) |
| 6 | Python for Data Engineering | 69–74 | 6 | [Part 6 index](<6. Python for Data Engineering/README.md>) |
| 7 | Practice Prep Flow and Revision | 75–80 | 6 | [Part 7 index](<7. Practice Prep Flow and Revision/README.md>) |

## Run and edit code

The [companion dataset ZIP](<Source/Python_Dataset_DE.zip>) is saved unchanged, and its [extracted files](<python_de_dataset/README.md>) are ready for the examples. Run code from this `2. Python Mastry` folder so paths such as `python_de_dataset/orders.csv` resolve.

Open [Start Practice.cmd](<Start Practice.cmd>) on Windows, or run `python practice_runner.py` from this folder. Click **Run and edit this example** above a Python code block. The playground keeps the original lesson code untouched and saves your separate draft for each part, lesson, and snippet in your browser. **Restore original** resets only the editable copy. Existing Part 1 drafts retain their prior browser keys.

Parts 1–5 use the standard library. For the runnable pandas and testing examples in Parts 6–7, install [the listed packages](<requirements-practice.txt>) into the Python environment used by the runner: `python -m pip install -r requirements-practice.txt`. The local setup used here already has them. PySpark, Airflow, and live HTTP examples need separate packages or services; the relevant lessons label those examples and provide local runnable companions where possible.

## Complete topic index

### Part 1: [Python from Zero](<1. Python from Zero/README.md>)

Start with values, decisions, collections, functions, files, and a sales report.

| # | Topic | PDF page |
|---:|---|---:|
| 01 | [Your first Python program](<1. Python from Zero/01. Your first Python program.md>) | [p. 5](<Source/1793477658005.pdf#page=5>) |
| 02 | [Variables and names](<1. Python from Zero/02. Variables and names.md>) | [p. 6](<Source/1793477658005.pdf#page=6>) |
| 03 | [Numbers and maths](<1. Python from Zero/03. Numbers and maths.md>) | [p. 7](<Source/1793477658005.pdf#page=7>) |
| 04 | [Strings: working with text](<1. Python from Zero/04. Strings - working with text.md>) | [p. 8](<Source/1793477658005.pdf#page=8>) |
| 05 | [True, False, and comparisons](<1. Python from Zero/05. True False and comparisons.md>) | [p. 9](<Source/1793477658005.pdf#page=9>) |
| 06 | [Input and output](<1. Python from Zero/06. Input and output.md>) | [p. 10](<Source/1793477658005.pdf#page=10>) |
| 07 | [Making decisions: if, elif, else](<1. Python from Zero/07. Making decisions.md>) | [p. 11](<Source/1793477658005.pdf#page=11>) |
| 08 | [Loops part 1: for and range](<1. Python from Zero/08. Loops part 1 - for and range.md>) | [p. 12](<Source/1793477658005.pdf#page=12>) |
| 09 | [Loops part 2: while, break, continue](<1. Python from Zero/09. Loops part 2 - while break continue.md>) | [p. 13](<Source/1793477658005.pdf#page=13>) |
| 10 | [Lists: ordered collections](<1. Python from Zero/10. Lists - ordered collections.md>) | [p. 14](<Source/1793477658005.pdf#page=14>) |
| 11 | [Tuples and sets](<1. Python from Zero/11. Tuples and sets.md>) | [p. 15](<Source/1793477658005.pdf#page=15>) |
| 12 | [Dictionaries: key and value](<1. Python from Zero/12. Dictionaries - key and value.md>) | [p. 16](<Source/1793477658005.pdf#page=16>) |
| 13 | [Which data structure?](<1. Python from Zero/13. Which data structure.md>) | [p. 17](<Source/1793477658005.pdf#page=17>) |
| 14 | [Functions: reusable steps](<1. Python from Zero/14. Functions - reusable steps.md>) | [p. 18](<Source/1793477658005.pdf#page=18>) |
| 15 | [Functions part 2: a mini pipeline](<1. Python from Zero/15. Functions part 2 - mini pipeline.md>) | [p. 19](<Source/1793477658005.pdf#page=19>) |
| 16 | [Modules, packages and pip](<1. Python from Zero/16. Modules packages and pip.md>) | [p. 20](<Source/1793477658005.pdf#page=20>) |
| 17 | [Reading errors without panic](<1. Python from Zero/17. Reading errors.md>) | [p. 21](<Source/1793477658005.pdf#page=21>) |
| 18 | [Files: read and write](<1. Python from Zero/18. Files - read and write.md>) | [p. 22](<Source/1793477658005.pdf#page=22>) |
| 19 | [Mini project: monthly sales report](<1. Python from Zero/19. Mini project - monthly sales report.md>) | [p. 23](<Source/1793477658005.pdf#page=23>) |
| 20 | [Practice set 0: first steps](<1. Python from Zero/20. Practice set 0 - first steps.md>) | [p. 24](<Source/1793477658005.pdf#page=24>) |

### Part 2: [Python Foundations](<2. Python Foundations/README.md>)

Reason about mutability, Python traps, files, and a six-step solving approach.

| # | Topic | PDF page |
|---:|---|---:|
| 01 | [The 6-step approach to any coding question](<2. Python Foundations/01. The 6-step approach to any coding question.md>) | [p. 25](<Source/1793477658005.pdf#page=25>) |
| 02 | [Names objects and mutability](<2. Python Foundations/02. Names objects and mutability.md>) | [p. 26](<Source/1793477658005.pdf#page=26>) |
| 03 | [Numbers strings and dates](<2. Python Foundations/03. Numbers strings and dates.md>) | [p. 27](<Source/1793477658005.pdf#page=27>) |
| 04 | [Lists tuples sets and Big-O](<2. Python Foundations/04. Lists tuples sets and Big-O.md>) | [p. 28](<Source/1793477658005.pdf#page=28>) |
| 05 | [Dicts defaultdict and Counter](<2. Python Foundations/05. Dicts defaultdict and Counter.md>) | [p. 29](<Source/1793477658005.pdf#page=29>) |
| 06 | [Loops comprehensions and unpacking](<2. Python Foundations/06. Loops comprehensions and unpacking.md>) | [p. 30](<Source/1793477658005.pdf#page=30>) |
| 07 | [Functions scope and closures](<2. Python Foundations/07. Functions scope and closures.md>) | [p. 31](<Source/1793477658005.pdf#page=31>) |
| 08 | [Errors exceptions and context managers](<2. Python Foundations/08. Errors exceptions and context managers.md>) | [p. 32](<Source/1793477658005.pdf#page=32>) |
| 09 | [Files CSV JSON JSON Lines and paths](<2. Python Foundations/09. Files CSV JSON JSON Lines and paths.md>) | [p. 33](<Source/1793477658005.pdf#page=33>) |
| 10 | [Practice set 1 foundations](<2. Python Foundations/10. Practice set 1 foundations.md>) | [p. 34](<Source/1793477658005.pdf#page=34>) |

### Part 3: [Advanced Python](<3. Advanced Python/README.md>)

Build lazy and reusable pipelines with classes, decorators, and concurrency.

| # | Topic | PDF page |
|---:|---|---:|
| 01 | [Iterators and generators](<3. Advanced Python/01. Iterators and generators.md>) | [p. 35](<Source/1793477658005.pdf#page=35>) |
| 02 | [itertools functools and sorting](<3. Advanced Python/02. itertools functools and sorting.md>) | [p. 36](<Source/1793477658005.pdf#page=36>) |
| 03 | [Classes and dataclasses](<3. Advanced Python/03. Classes and dataclasses.md>) | [p. 37](<Source/1793477658005.pdf#page=37>) |
| 04 | [Decorators and context managers](<3. Advanced Python/04. Decorators and context managers.md>) | [p. 38](<Source/1793477658005.pdf#page=38>) |
| 05 | [Concurrency threads processes and asyncio](<3. Advanced Python/05. Concurrency threads processes and asyncio.md>) | [p. 39](<Source/1793477658005.pdf#page=39>) |
| 06 | [Practice set 2 advanced](<3. Advanced Python/06. Practice set 2 advanced.md>) | [p. 40](<Source/1793477658005.pdf#page=40>) |

### Part 4: [DSA and Complexity](<4. DSA and Complexity/README.md>)

Learn core data structures, algorithms, and how to state their cost.

| # | Topic | PDF page |
|---:|---|---:|
| 01 | [Big-O in plain words](<4. DSA and Complexity/01. Big-O in plain words.md>) | [p. 41](<Source/1793477658005.pdf#page=41>) |
| 02 | [Space complexity](<4. DSA and Complexity/02. Space complexity.md>) | [p. 42](<Source/1793477658005.pdf#page=42>) |
| 03 | [Time versus space trade-offs](<4. DSA and Complexity/03. Time versus space trade-offs.md>) | [p. 43](<Source/1793477658005.pdf#page=43>) |
| 04 | [What Python operations cost](<4. DSA and Complexity/04. What Python operations cost.md>) | [p. 44](<Source/1793477658005.pdf#page=44>) |
| 05 | [Arrays and strings with two pointers](<4. DSA and Complexity/05. Arrays and strings with two pointers.md>) | [p. 45](<Source/1793477658005.pdf#page=45>) |
| 06 | [Hashing](<4. DSA and Complexity/06. Hashing.md>) | [p. 46](<Source/1793477658005.pdf#page=46>) |
| 07 | [Sliding windows](<4. DSA and Complexity/07. Sliding windows.md>) | [p. 47](<Source/1793477658005.pdf#page=47>) |
| 08 | [Stacks and queues](<4. DSA and Complexity/08. Stacks and queues.md>) | [p. 48](<Source/1793477658005.pdf#page=48>) |
| 09 | [Linked lists](<4. DSA and Complexity/09. Linked lists.md>) | [p. 49](<Source/1793477658005.pdf#page=49>) |
| 10 | [Binary search](<4. DSA and Complexity/10. Binary search.md>) | [p. 50](<Source/1793477658005.pdf#page=50>) |
| 11 | [Sorting](<4. DSA and Complexity/11. Sorting.md>) | [p. 51](<Source/1793477658005.pdf#page=51>) |
| 12 | [Recursion and backtracking](<4. DSA and Complexity/12. Recursion and backtracking.md>) | [p. 52](<Source/1793477658005.pdf#page=52>) |
| 13 | [Trees with DFS and BFS](<4. DSA and Complexity/13. Trees with DFS and BFS.md>) | [p. 53](<Source/1793477658005.pdf#page=53>) |
| 14 | [Graphs and pipeline DAGs](<4. DSA and Complexity/14. Graphs and pipeline DAGs.md>) | [p. 54](<Source/1793477658005.pdf#page=54>) |
| 15 | [Heaps and greedy choices](<4. DSA and Complexity/15. Heaps and greedy choices.md>) | [p. 55](<Source/1793477658005.pdf#page=55>) |
| 16 | [Dynamic programming basics](<4. DSA and Complexity/16. Dynamic programming basics.md>) | [p. 56](<Source/1793477658005.pdf#page=56>) |
| 17 | [Practice set 3: DSA](<4. DSA and Complexity/17. Practice set 3 - DSA.md>) | [p. 57](<Source/1793477658005.pdf#page=57>) |

### Part 5: [Coding Round Patterns](<5. Coding Round Patterns/README.md>)

Practise all 18 record-processing patterns on the supplied store data.

| # | Topic | PDF page |
|---:|---|---:|
| 01 | [Hear the coding pattern in the question](<5. Coding Round Patterns/01. The 18-pattern map.md>) | [p. 58](<Source/1793477658005.pdf#page=58>) |
| 02 | [Count first, then choose the top K (P1 and P2)](<5. Coding Round Patterns/02. Frequency count and top K.md>) | [p. 59](<Source/1793477658005.pdf#page=59>) |
| 03 | [Group baskets and keep the latest record (P3 and P4)](<5. Coding Round Patterns/03. Grouping and latest-record deduplication.md>) | [p. 60](<Source/1793477658005.pdf#page=60>) |
| 04 | [Rolling windows and pre-sorted streams (P5 and P6)](<5. Coding Round Patterns/04. Windows and sorted streams.md>) | [p. 61](<Source/1793477658005.pdf#page=61>) |
| 05 | [Flatten dictionaries; explode lists of records (P7)](<5. Coding Round Patterns/05. Flatten nested JSON.md>) | [p. 62](<Source/1793477658005.pdf#page=62>) |
| 06 | [Split sessions and find consecutive streaks (P8 and P9)](<5. Coding Round Patterns/06. Sessions and streaks.md>) | [p. 63](<Source/1793477658005.pdf#page=63>) |
| 07 | [Parse messy logs and keep the skipped lines (P10)](<5. Coding Round Patterns/07. Parse logs.md>) | [p. 64](<Source/1793477658005.pdf#page=64>) |
| 08 | [Merge time intervals; join files with a lookup (P11 and P12)](<5. Coding Round Patterns/08. Intervals and hash joins.md>) | [p. 65](<Source/1793477658005.pdf#page=65>) |
| 09 | [Read big files in chunks; retry transient failures (P13 and P14)](<5. Coding Round Patterns/09. Chunking and retries.md>) | [p. 66](<Source/1793477658005.pdf#page=66>) |
| 10 | [Pull every page; cache repeated lookups (P15 and P16)](<5. Coding Round Patterns/10. Pagination and LRU caching.md>) | [p. 67](<Source/1793477658005.pdf#page=67>) |
| 11 | [Quarantine bad rows and compare snapshots (P17 and P18)](<5. Coding Round Patterns/11. Validation and snapshot differences.md>) | [p. 68](<Source/1793477658005.pdf#page=68>) |

### Part 6: [Python for Data Engineering](<6. Python for Data Engineering/README.md>)

Use pandas, SQLite, ETL, tests, and larger-scale workflow ideas.

| # | Topic | PDF page |
|---:|---|---:|
| 01 | [Pandas essentials, mapped to SQL](<6. Python for Data Engineering/01. Pandas essentials mapped to SQL.md>) | [p. 69](<Source/1793477658005.pdf#page=69>) |
| 02 | [Pandas results can be wrong without an error](<6. Python for Data Engineering/02. Pandas pitfalls and speed.md>) | [p. 70](<Source/1793477658005.pdf#page=70>) |
| 03 | [Load, query, transact and upsert with Python](<6. Python for Data Engineering/03. Python and databases.md>) | [p. 71](<Source/1793477658005.pdf#page=71>) |
| 04 | [Build a small ETL pipeline you can rerun](<6. Python for Data Engineering/04. Build an idempotent ETL pipeline.md>) | [p. 72](<Source/1793477658005.pdf#page=72>) |
| 05 | [Test the code and check the data](<6. Python for Data Engineering/05. Testing and data quality.md>) | [p. 73](<Source/1793477658005.pdf#page=73>) |
| 06 | [Move from pandas to PySpark, then schedule with Airflow](<6. Python for Data Engineering/06. From pandas to PySpark and Airflow.md>) | [p. 74](<Source/1793477658005.pdf#page=74>) |

### Part 7: [Practice Prep Flow and Revision](<7. Practice Prep Flow and Revision/README.md>)

Solve interview sets and review concepts, complexity, and preparation.

| # | Topic | PDF page |
|---:|---|---:|
| 01 | [Interview set: Python coding for data engineering](<7. Practice Prep Flow and Revision/01. Interview set - Python coding.md>) | [p. 75](<Source/1793477658005.pdf#page=75>) |
| 02 | [Interview set: pandas and data wrangling](<7. Practice Prep Flow and Revision/02. Interview set - pandas.md>) | [p. 76](<Source/1793477658005.pdf#page=76>) |
| 03 | [Concept questions with short answers](<7. Practice Prep Flow and Revision/03. Concept questions.md>) | [p. 77](<Source/1793477658005.pdf#page=77>) |
| 04 | [Complexity cheat sheet](<7. Practice Prep Flow and Revision/04. Complexity cheat sheet.md>) | [p. 78](<Source/1793477658005.pdf#page=78>) |
| 05 | [The preparation flow: ten weeks from zero to interviews](<7. Practice Prep Flow and Revision/05. Ten-week preparation flow.md>) | [p. 79](<Source/1793477658005.pdf#page=79>) |
| 06 | [Final revision sheet and the last 48 hours](<7. Practice Prep Flow and Revision/06. Final revision sheet.md>) | [p. 80](<Source/1793477658005.pdf#page=80>) |

## Source and navigation

- [Original 80-page PDF](<Source/1793477658005.pdf>) and [dataset ZIP](<Source/Python_Dataset_DE.zip>) are retained unchanged.
- [Dataset run guide](<python_de_dataset/README.md>) explains the supplied CSV, JSON, JSON Lines, and log files.
- Each part has its own index. Each numbered lesson links to its neighbouring lessons and source PDF page.
- [Part 1 W3Schools topic map](<1. Python from Zero/README.md#w3schools-topics-inside-the-lessons>) lists the 36 originally requested Python tutorial topics.
