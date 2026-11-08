# Nested Loops and Pattern Printing

## Why this matters
Nested loops teach row/column reasoning. The outer loop chooses a row, and the inner loop decides the characters printed inside it. In Data Engineering, we avoid unnecessary nested scans on big data, so learn to reason about their cost.

## Basic rectangle
```python
rows, columns = 3, 4
for r in range(rows):
    for c in range(columns):
        print('#', end='')
    print()
```
Each iteration of the outer loop creates one row. The inner loop prints four markers, and the final print starts a new row.

## Staircases
```python
size = 4
for row in range(1, size + 1):
    print('#' * row)

for row in range(size, 0, -1):
    print('#' * row)
```
The increasing staircase has 1, 2, 3, 4 symbols; the decreasing staircase goes in reverse. The last argument of range is excluded.

## Pyramid
```python
height = 4
for row in range(1, height + 1):
    spaces = height - row
    marks = 2 * row - 1
    print(' ' * spaces + '^' * marks)
```
Each row has fewer leading spaces and an odd number of symbols.

## Diamond
```python
height = 3
for row in range(1, height + 1):
    print(' ' * (height - row) + '^' * (2 * row - 1))
for row in range(height - 1, 0, -1):
    print(' ' * (height - row) + '^' * (2 * row - 1))
```
The center row is printed only once.

## Hollow square
```python
n = 4
for i in range(n):
    for j in range(n):
        border = i == 0 or j == 0 or i == n - 1 or j == n - 1
        print('#' if border else ' ', end='')
    print()
```

## All original class pattern challenges to attempt yourself
- [ ] Single-row star pattern
- [ ] Fixed 3-by-5 rectangle
- [ ] N-by-M rectangle driven by inputs
- [ ] Staircase with increasing stars
- [ ] Reverse staircase
- [ ] Centered pyramid
- [ ] Diamond with upper and lower halves
- [ ] Hollow square
- [ ] Explain outputs and complexity for every shape

An N-by-M printed rectangle takes O(N*M) output work; staircases and similarly sized patterns typically take O(N²). This does not make all nested loops inherently inefficient—cost depends on required output.

**No graded assignment solutions included.**