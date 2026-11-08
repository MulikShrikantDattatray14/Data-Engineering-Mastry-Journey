# Part 4 — DSA and Complexity

[Python master index](<../README.md>) | [Part 3](<../3. Advanced Python/README.md>) | [Original PDF](<../Source/1793477658005.pdf#page=41>)

This part follows **pages 41–57** of the 80-page mentor PDF in order. Start with growth and memory, then learn the data structures and algorithms used in coding rounds. The store's orders, events, employees and pipeline tasks keep the examples connected. Each lesson has a short explanation, runnable code, expected output, and exercises.

Open [Start Practice.cmd](<../Start Practice.cmd>) or run the local practice runner from the Python folder. The **▶ Run and edit this example** links open an editable copy of each snippet while preserving its original.

## Topic index

| # | Topic | PDF page |
|---:|---|---:|
| 01 | [Big-O in plain words](<01. Big-O in plain words.md>) | 41 |
| 02 | [Space complexity](<02. Space complexity.md>) | 42 |
| 03 | [Time versus space trade-offs](<03. Time versus space trade-offs.md>) | 43 |
| 04 | [What Python operations cost](<04. What Python operations cost.md>) | 44 |
| 05 | [Arrays and strings with two pointers](<05. Arrays and strings with two pointers.md>) | 45 |
| 06 | [Hashing](<06. Hashing.md>) | 46 |
| 07 | [Sliding windows](<07. Sliding windows.md>) | 47 |
| 08 | [Stacks and queues](<08. Stacks and queues.md>) | 48 |
| 09 | [Linked lists](<09. Linked lists.md>) | 49 |
| 10 | [Binary search](<10. Binary search.md>) | 50 |
| 11 | [Sorting](<11. Sorting.md>) | 51 |
| 12 | [Recursion and backtracking](<12. Recursion and backtracking.md>) | 52 |
| 13 | [Trees with DFS and BFS](<13. Trees with DFS and BFS.md>) | 53 |
| 14 | [Graphs and pipeline DAGs](<14. Graphs and pipeline DAGs.md>) | 54 |
| 15 | [Heaps and greedy choices](<15. Heaps and greedy choices.md>) | 55 |
| 16 | [Dynamic programming basics](<16. Dynamic programming basics.md>) | 56 |
| 17 | [Practice set 3: DSA — Q16–Q20](<17. Practice set 3 - DSA.md>) | 57 |

## Quick pattern guide

| When the question says… | First consider |
|---|---|
| “Input grew ten times” | Big-O time and extra space |
| “Find a pair” on sorted values | Two pointers |
| “Have I seen this?” | Set or dictionary |
| “Longest or shortest contiguous run” | Sliding window, if its rule is monotonic |
| “Most recent unmatched item” | Stack |
| “First item waiting in line” | Queue with deque |
| “First at or after” in sorted data | Lower-bound binary search |
| “Dependencies before tasks” | Topological sort |
| “Best k while streaming” | Size-k heap |
| “Same subproblem repeats” | Dynamic programming |

## Sources and practice

The [original PDF](<../Source/1793477658005.pdf#page=41>) supplies the chapter order and core examples. Matching lessons include original extensions linked to the relevant [W3Schools Python DSA tutorial](https://www.w3schools.com/python/python_dsa.asp). The five source practice problems are in Lesson 17 with answers hidden until you open them. For file examples, use the [supplied dataset](<../python_de_dataset/README.md>).

[Begin Part 4](<01. Big-O in plain words.md>) | [Python master index](<../README.md>)