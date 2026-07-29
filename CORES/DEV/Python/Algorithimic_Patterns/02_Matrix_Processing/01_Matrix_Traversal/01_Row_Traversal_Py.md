# Part 2 — Matrix Patterns

# 1. Row Traversal

## Mental Model

A matrix is often treated as a collection of rows. Row traversal means processing one complete row at a time before moving to the next.

This is the most natural traversal order because most programming languages store 2D arrays in **row-major order**, making it cache-friendly and easy to reason about.

In Python a matrix is usually a `list[list[int]]`, so **a row is just a list** — every 1D tool you already know (`sum`, `max`, comprehensions, `itertools`) applies directly to it.

---

## Relationship to Cognitive Verb

```text
Visit
   ↓
Row Traversal
```

Related verbs:

- Visit each row
    
- Process row-by-row
    
- Scan rows
    
- Iterate rows
    
- Aggregate rows
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Iterate rows|process each row|`for row in m`|
|Transform rows|modify every row|list comprehension, `map`|
|Filter rows|keep matching rows|comprehension with `if`, `filter`|
|Reduce rows|summarize rows|`sum`, `max`, `min`, `functools.reduce`|
|Index rows|need row number|`enumerate`|
|Nested traversal|visit every cell|nested `for`, double comprehension|
|Flatten cells|treat matrix as 1D|`itertools.chain.from_iterable`|
|Pair rows|compare adjacent rows|`itertools.pairwise`|
|Destructure rows|match row shape|`match` / `case` (3.10+)|

---

## Common Uses

- Spreadsheet processing
    
- CSV tables
    
- Database result sets
    
- Image scanlines
    
- Tile maps
    
- Heatmaps
    
- Neural network weight matrices
    
- Matrix printing
    
- Row statistics
    

---

## Hidden Interview Problems

- Sum each row
    
- Maximum value per row
    
- Count occurrences in each row
    
- Detect empty rows
    
- Normalize every row
    
- Find row with largest sum
    
- Validate Sudoku rows
    
- Compress rows
    

---

## Recognition Clues

If you hear...

- "for every row..."
    
- "each record..."
    
- "scan line by line..."
    
- "process one row at a time..."
    
- "calculate row totals..."
    

...think **Row Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Row|
|Order|Left → Right, Top → Bottom|
|Cache Friendly|Yes (row-major layouts)|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (typically)|
|Common Domains|Images, tables, grids|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from itertools import chain, pairwise
from functools import reduce

m = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]

# ============================================
# Visit every row

for row in m:
    print(row)

# ============================================
# Transform every row

[[x + 1 for x in row] for row in m]

# =>
# [[2, 3, 4],
#  [5, 6, 7],
#  [8, 9, 10]]

# ============================================
# Sum every row

[sum(row) for row in m]        # => [6, 15, 24]

list(map(sum, m))              # same thing, point-free

# ============================================
# Maximum in each row

[max(row) for row in m]        # => [3, 6, 9]

# ============================================
# Count elements satisfying a condition

[sum(1 for x in row if x % 2 == 0) for row in m]   # => [1, 2, 1]

# sum() over booleans works too — True is 1
[sum(x % 2 == 0 for x in row) for row in m]        # => [1, 2, 1]

# ============================================
# Access row index

[{"row": i, "sum": sum(row)} for i, row in enumerate(m)]

# =>
# [{'row': 0, 'sum': 6},
#  {'row': 1, 'sum': 15},
#  {'row': 2, 'sum': 24}]

# ============================================
# Nested traversal (row then cell)

for row in m:
    for cell in row:
        print(cell)

# with both coordinates
for i, row in enumerate(m):
    for j, cell in enumerate(row):
        print(i, j, cell)

# flatten first, then visit — itertools.chain is the workhorse
for cell in chain.from_iterable(m):
    print(cell)

# ============================================
# Same using a comprehension

[cell * 2 for row in m for cell in row]
# => [2, 4, 6, 8, 10, 12, 14, 16, 18]

# read it left-to-right exactly like the nested for loops above

# ============================================
# Reduce across rows

sum(map(sum, m))                                   # => 45

reduce(lambda acc, row: acc + sum(row), m, 0)      # explicit fold

# ============================================
# Filter rows

[row for row in m if sum(row) > 10]     # => [[4, 5, 6], [7, 8, 9]]

# ============================================
# Detect empty rows

[i for i, row in enumerate(m) if not row]          # => []

any(not row for row in m)                          # => False

# ============================================
# Row with the largest sum

max(m, key=sum)                                    # => [7, 8, 9]

max(range(len(m)), key=lambda i: sum(m[i]))        # index instead of row

# ============================================
# Normalize every row (each row sums to 1)

[[x / total for x in row] for row in m if (total := sum(row))]

# => (rounded for display)
# [[0.167, 0.333, 0.5],
#  [0.267, 0.333, 0.4],
#  [0.292, 0.333, 0.375]]

# ============================================
# Validate rows (Sudoku-style: no duplicates)

all(len(set(row)) == len(row) for row in m)        # => True

# ============================================
# Compare adjacent rows — pairwise (3.10+)

[sum(b) - sum(a) for a, b in pairwise(m)]          # => [9, 9]

# ============================================
# Structural pattern matching on rows (3.10+)

def describe(row):
    match row:
        case []:                 return "empty"
        case [x]:                return f"single {x}"
        case [first, *_, last]:  return f"{first}..{last}"

[describe(row) for row in m]    # => ['1..3', '4..6', '7..9']

# ============================================
# Compare

# Row traversal
[f(row) for row in matrix]

# Cell traversal
[f(cell) for row in matrix for cell in row]
chain.from_iterable(matrix)          # lazy flatten

# Row reduction
[sum(row) for row in matrix]         # any op: max, min, len, ...

# Whole matrix reduction
sum(map(sum, matrix))
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|every row|`for row in m`|
|every row, transformed|`[f(row) for row in m]`|
|every row, numbered|`enumerate(m)`|
|every cell|`for row in m for cell in row`|
|every cell, flat|`chain.from_iterable(m)`|
|one number per row|`[sum(row) for row in m]`|
|one number for all|`sum(map(sum, m))`|
|the best row|`max(m, key=sum)`|

---

### Key Insight

**A row is the 2D equivalent of a sequence.** Most row-based algorithms simply apply familiar 1D sequence patterns (`sum`, `max`, `filter`, comprehensions, `itertools`) independently to each row before combining results if needed.

In Python this is literal, not just an analogy: `m[i]` *is* a `list`, so nothing new has to be learned to process it — the only new decision is **whether you loop over rows or over flattened cells**.
