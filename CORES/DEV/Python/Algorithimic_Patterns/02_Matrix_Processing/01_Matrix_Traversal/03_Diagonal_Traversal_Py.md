# 3. Diagonal Traversal

## Mental Model

Diagonal traversal visits cells where the **row and column indices change together**. The most common diagonal is the **main diagonal**, running from the top-left to the bottom-right.

Rows and columns are contiguous runs. A diagonal isn't. It's a **relationship between coordinates**.

That relationship maps straight onto `enumerate` in Python: walk the rows and let the **row number double as the column index**.

---

## Relationship to Cognitive Verb

```text
Trace
   ↓
Diagonal Traversal
```

Related verbs:

- Trace a diagonal
    
- Follow a diagonal
    
- Scan diagonally
    
- Visit matching coordinates
    
- Compare corresponding positions
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Main diagonal|`(0,0) → (n,n)`|`enumerate`, `range`|
|Offset diagonal|above/below main|`enumerate` with `i + k`|
|Collect diagonal|build sequence|list comprehension|
|Reduce diagonal|sum/product|`sum`, `math.prod`|
|Indexed traversal|explicit `(r,c)`|`zip(range(n), range(n))`|
|Group all diagonals|bucket by `c - r`|`collections.defaultdict`|

---

## Common Uses

- Matrix trace
    
- Identity matrix checks
    
- Symmetric matrix algorithms
    
- Tic-Tac-Toe winner detection
    
- Image edge detection
    
- Dynamic programming tables
    
- Game board evaluation
    
- Computer vision
    

---

## Hidden Interview Problems

- Print the main diagonal
    
- Sum the diagonal
    
- Product of diagonal elements
    
- Check identity matrix
    
- Check symmetry
    
- Difference between diagonals
    
- Diagonal averages
    
- Traverse all diagonals
    

---

## Recognition Clues

If you hear...

- "top-left to bottom-right..."
    
- "main diagonal..."
    
- "matching row and column..."
    
- "where row equals column..."
    
- "principal diagonal..."
    

...think **Diagonal Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Diagonal|
|Direction|Top-Left → Bottom-Right|
|Coordinate Rule|`row == col`|
|Time Complexity|O(min(rows, cols))|
|Space Complexity|O(1) extra|
|Common Domains|Linear algebra, games, graphics|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from collections import defaultdict
from math import prod

m = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]

# ============================================
# The one idiom to remember
#
#   [row[i] for i, row in enumerate(m)]
#
# enumerate gives the row number;
# reuse it as the column index.  row == col.

[row[i] for i, row in enumerate(m)]     # => [1, 5, 9]

# ============================================
# Main diagonal

[row[i] for i, row in enumerate(m)]     # => [1, 5, 9]

[m[i][i] for i in range(len(m))]        # index form — same result

# non-square safe
n = min(len(m), len(m[0]))
[m[i][i] for i in range(n)]             # => [1, 5, 9]

# ============================================
# Sum of main diagonal (the "trace")

sum(row[i] for i, row in enumerate(m))          # => 15

# ============================================
# Product of main diagonal

prod(row[i] for i, row in enumerate(m))         # => 45

# ============================================
# Row/Column coordinate pairs

list(zip(range(3), range(3)))           # => [(0, 0), (1, 1), (2, 2)]

# ============================================
# Access using coordinate pairs

[m[r][c] for r, c in zip(range(3), range(3))]   # => [1, 5, 9]

# ============================================
# Offset diagonal (one above)

k = 1
[row[i + k] for i, row in enumerate(m) if 0 <= i + k < len(row)]
# => [2, 6]

# ============================================
# Offset diagonal (one below)

k = -1
[row[i + k] for i, row in enumerate(m) if 0 <= i + k < len(row)]
# => [4, 8]

# ============================================
# One helper covers every offset
#
#   k > 0  -> above the main diagonal
#   k = 0  -> the main diagonal
#   k < 0  -> below the main diagonal

def diagonal(m, k=0):
    return [row[i + k] for i, row in enumerate(m) if 0 <= i + k < len(row)]

diagonal(m)          # => [1, 5, 9]
diagonal(m, 1)       # => [2, 6]
diagonal(m, -1)      # => [4, 8]

# ============================================
# Anti-diagonal, for contrast (see lesson 4)

[row[len(row) - 1 - i] for i, row in enumerate(m)]      # => [3, 5, 7]

# ============================================
# Difference between the two diagonals

sum(diagonal(m)) - sum(row[len(row) - 1 - i] for i, row in enumerate(m))
# => 0

# ============================================
# Check identity matrix
#
# read it as the rule itself: 1 on the diagonal, 0 off it

def is_identity(m):
    return all(cell == (r == c)
               for r, row in enumerate(m)
               for c, cell in enumerate(row))

is_identity([[1, 0], [0, 1]])           # => True
is_identity(m)                          # => False

# ============================================
# Check symmetry (m == its transpose)

def is_symmetric(m):
    return all(list(row) == list(col) for row, col in zip(m, zip(*m)))

is_symmetric([[1, 2], [2, 1]])          # => True
is_symmetric(m)                         # => False

# ============================================
# Traverse ALL diagonals
#
# Every cell on the same diagonal shares the same  c - r.
# Bucket by that key and the diagonals fall out.

diagonals = defaultdict(list)
for r, row in enumerate(m):
    for c, cell in enumerate(row):
        diagonals[c - r].append(cell)

[diagonals[k] for k in sorted(diagonals)]

# =>
# [[7], [4, 8], [1, 5, 9], [2, 6], [3]]
#   ^-2   ^-1     ^0 main    ^1     ^2

# ============================================
# Compare

# Row traversal          row i, all columns
# Column traversal       all rows, column c
# Diagonal traversal     row i, column i          (c - r constant)
# Anti-diagonal          row i, column n-1-i      (c + r constant)

# ============================================
# Generic pattern

[m[i][i] for i in range(min(len(m), len(m[0])))]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|main diagonal|`[row[i] for i, row in enumerate(m)]`|
|trace (sum)|`sum(row[i] for i, row in enumerate(m))`|
|product|`prod(row[i] for i, row in enumerate(m))`|
|offset diagonal|`row[i + k]`, guarded by bounds|
|anti-diagonal|`row[len(row) - 1 - i]`|
|coordinate pairs|`zip(range(n), range(n))`|
|all diagonals|bucket by `c - r`|

---

## Key Insight

**A diagonal is defined by a coordinate relationship, not by physical storage.** The main diagonal follows the simple rule:

```text
(row, col)

(0,0)
(1,1)
(2,2)
(3,3)
...
```

Any time the **row index and column index climb together**, you're on the main diagonal. It shows up constantly in linear algebra, board games, image processing and dynamic programming.

The Python version of that rule: **`enumerate` gives you the row index, so use it twice.** And as soon as you want *all* the diagonals rather than one, stop indexing and start grouping — **each diagonal is a single value of `c - r`**.

---
