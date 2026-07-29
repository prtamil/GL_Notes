# 2. Column Traversal

## Mental Model

Column traversal processes one complete column at a time before moving to the next column.

Columns aren't **stored contiguously** in a row-major matrix the way rows are, so reading a column means visiting the same index in every row.

One idiom dominates this whole pattern in Python: **`zip(*m)`**. It turns columns into rows, and after that every row-traversal tool works untouched.

---

## Relationship to Cognitive Verb

```text
Visit
   ↓
Column Traversal
```

Related verbs:

- Visit each column
    
- Scan vertically
    
- Process column-by-column
    
- Aggregate columns
    
- Analyze vertical slices
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Iterate columns|process each column|`for col in zip(*m)`|
|Transform columns|modify every column|`[f(col) for col in zip(*m)]`|
|Reduce columns|summarize columns|`map(sum, zip(*m))`|
|Index columns|need column number|`enumerate(zip(*m))`|
|Extract column|get one column|`[row[c] for row in m]`|
|Transpose first|convert columns to rows|`zip(*m)` / `[list(c) for c in zip(*m)]`|
|Ragged rows|rows of unequal length|`itertools.zip_longest`|

---

## Common Uses

- Spreadsheet column totals
    
- Database field analysis
    
- Image vertical scans
    
- Sudoku column validation
    
- Feature extraction in machine learning
    
- Histogram computation
    
- Sensor readings over time
    
- Vertical projections
    

---

## Hidden Interview Problems

- Sum every column
    
- Maximum per column
    
- Find empty columns
    
- Validate Sudoku columns
    
- Detect identical columns
    
- Normalize each column
    
- Count values per column
    
- Compute column averages
    

---

## Recognition Clues

If you hear...

- "for every column..."
    
- "scan vertically..."
    
- "column totals..."
    
- "analyze each field..."
    
- "process top to bottom..."
    

...think **Column Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Column|
|Order|Top → Bottom, Left → Right|
|Cache Friendly|Usually No (row-major layouts)|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (streaming)|
|Common Domains|Tables, images, spreadsheets|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from itertools import zip_longest
from statistics import mean

m = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]

# ============================================
# The one idiom to remember
#
#   zip(*m)  ->  columns, as tuples
#
# The * unpacks rows into separate arguments,
# so zip pairs them up index-by-index.

list(zip(*m))

# =>
# [(1, 4, 7),
#  (2, 5, 8),
#  (3, 6, 9)]

# ============================================
# Visit every column

for col in zip(*m):
    print(col)

# =>
# (1, 4, 7)
# (2, 5, 8)
# (3, 6, 9)

# ============================================
# Extract a single column

[row[1] for row in m]           # => [2, 5, 8]

list(zip(*m))[1]                # => (2, 5, 8)  — same thing

# ============================================
# Sum every column

[sum(col) for col in zip(*m)]   # => [12, 15, 18]

list(map(sum, zip(*m)))         # point-free

# ============================================
# Maximum in each column

[max(col) for col in zip(*m)]   # => [7, 8, 9]

# ============================================
# Average of each column

[mean(col) for col in zip(*m)]  # => [4, 5, 6]

[sum(col) / len(col) for col in zip(*m)]    # without statistics

# ============================================
# Access column index

[{"column": c, "values": col} for c, col in enumerate(zip(*m))]

# =>
# [{'column': 0, 'values': (1, 4, 7)},
#  {'column': 1, 'values': (2, 5, 8)},
#  {'column': 2, 'values': (3, 6, 9)}]

# ============================================
# Transpose (columns become rows)

[list(col) for col in zip(*m)]

# =>
# [[1, 4, 7],
#  [2, 5, 8],
#  [3, 6, 9]]

# ============================================
# After transpose, process columns like rows

[sum(row) for row in zip(*m)]   # => [12, 15, 18]

# every row recipe now works — max, filter, enumerate, ...

# ============================================
# Filter columns

[col for col in zip(*m) if sum(col) > 13]   # => [(2, 5, 8), (3, 6, 9)]

# ============================================
# Column with the largest sum

max(zip(*m), key=sum)                       # => (3, 6, 9)

max(range(len(m[0])), key=lambda c: sum(row[c] for row in m))   # => 2

# ============================================
# Validate columns (Sudoku-style: no duplicates)

all(len(set(col)) == len(col) for col in zip(*m))       # => True

# ============================================
# Detect identical columns

cols = list(zip(*m))
len(set(cols)) < len(cols)                  # => False (all distinct)

# ============================================
# Normalize each column (each column sums to 1)

[[x / sum(col) for x in col] for col in zip(*m)]

# => (rounded for display)
# [[0.083, 0.333, 0.583],
#  [0.133, 0.333, 0.533],
#  [0.167, 0.333, 0.5]]

# ============================================
# Ragged rows — zip stops at the shortest!

ragged = [[1, 2, 3], [4, 5], [6, 7, 8]]

list(zip(*ragged))                          # => [(1, 4, 6), (2, 5, 7)]  <- 3rd column LOST

list(zip_longest(*ragged, fillvalue=0))     # => [(1, 4, 6), (2, 5, 7), (3, 0, 8)]

# ============================================
# Compare

# Row traversal
[f(row) for row in matrix]

# Column traversal
[f(col) for col in zip(*matrix)]

# One column by index
[row[c] for row in matrix]

# Treat columns as rows
[list(col) for col in zip(*matrix)]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|every column|`for col in zip(*m)`|
|every column, numbered|`enumerate(zip(*m))`|
|one column|`[row[c] for row in m]`|
|one number per column|`[sum(col) for col in zip(*m)]`|
|transpose|`[list(c) for c in zip(*m)]`|
|the best column|`max(zip(*m), key=sum)`|
|ragged rows|`zip_longest(*m, fillvalue=0)`|

---

## Key Insight

**A column is just a vertical sequence.** Python matrices are lists of rows, so column traversal means **pulling the same index out of every row**. Better still, **transpose first with `zip(*m)`** and reuse every row-processing pattern from the previous lesson.

Two things worth burning in:

- `zip(*m)` gives you **tuples**, not lists. Only wrap it in `list(...)` when you actually need to mutate.
    
- `zip` **stops at the shortest row** and drops data on ragged input without saying anything. The moment rows might differ in length, switch to `itertools.zip_longest`.
    

---
