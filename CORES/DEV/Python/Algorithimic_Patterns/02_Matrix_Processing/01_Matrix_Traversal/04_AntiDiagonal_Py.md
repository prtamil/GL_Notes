# 4. Anti-Diagonal Traversal

## Mental Model

Anti-diagonal traversal visits cells where the **row index increases while the column index decreases**. It follows the diagonal from the **top-right corner** to the **bottom-left corner**.

Like the main diagonal, this is defined by a **coordinate relationship**, not by how the matrix is stored.

Python has a shortcut that makes this almost free: **negative indexing**. Counting from the right is built into the language, so `row[-1 - i]` walks the anti-diagonal without any `n` in sight.

---

## Relationship to Cognitive Verb

```text
Trace
   ↓
Anti-Diagonal Traversal
```

Related verbs:

- Trace the opposite diagonal
    
- Follow the reverse diagonal
    
- Scan diagonally
    
- Visit mirrored coordinates
    
- Compare opposite corners
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Main anti-diagonal|`(0,n-1) → (n-1,0)`|`enumerate` + negative index|
|Offset anti-diagonal|adjacent diagonals|bucket by `r + c`|
|Collect anti-diagonal|build sequence|list comprehension|
|Reduce anti-diagonal|sum/product|`sum`, `math.prod`|
|Indexed traversal|explicit `(r,c)`|`zip(range(n), reversed(range(n)))`|
|Group all anti-diagonals|bucket by `r + c`|`collections.defaultdict`|
|Mirror the matrix|reuse main-diagonal code|`[row[::-1] for row in m]`|

---

## Common Uses

- Tic-Tac-Toe winner detection
    
- Matrix symmetry checks
    
- Image processing
    
- Dynamic programming
    
- Chess and board games
    
- Computer vision
    
- Heatmap analysis
    
- Matrix puzzles
    

---

## Hidden Interview Problems

- Print the anti-diagonal
    
- Sum the anti-diagonal
    
- Compare both diagonals
    
- Check X-patterns
    
- Difference of diagonal sums
    
- Find diagonal maximum
    
- Detect anti-diagonal symmetry
    
- Traverse all anti-diagonals
    

---

## Recognition Clues

If you hear...

- "top-right to bottom-left..."
    
- "secondary diagonal..."
    
- "opposite diagonal..."
    
- "reverse diagonal..."
    
- "mirror diagonal..."
    

...think **Anti-Diagonal Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Anti-Diagonal|
|Direction|Top-Right → Bottom-Left|
|Coordinate Rule|`row + col == n - 1` (square matrix)|
|Time Complexity|O(min(rows, cols))|
|Space Complexity|O(1) extra|
|Common Domains|Games, graphics, linear algebra|

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

n = len(m)

# ============================================
# The one idiom to remember
#
#   [row[-1 - i] for i, row in enumerate(m)]
#
# Row 0 takes the LAST cell, row 1 the second-to-last, ...
# Negative indexing counts from the right for you,
# so no `n` and no off-by-one arithmetic.

[row[-1 - i] for i, row in enumerate(m)]        # => [3, 5, 7]

# ============================================
# Main anti-diagonal — three ways to say it

[row[-1 - i] for i, row in enumerate(m)]        # negative index (preferred)

[row[~i] for i, row in enumerate(m)]            # ~i is exactly -1 - i

[m[i][n - 1 - i] for i in range(n)]             # explicit arithmetic

# =>  all three: [3, 5, 7]

# ============================================
# Sum of anti-diagonal

sum(row[-1 - i] for i, row in enumerate(m))     # => 15

# ============================================
# Product of anti-diagonal

prod(row[-1 - i] for i, row in enumerate(m))    # => 105

# ============================================
# Coordinate pairs

list(zip(range(n), reversed(range(n))))         # => [(0, 2), (1, 1), (2, 0)]

# ============================================
# Access using coordinate pairs

[m[r][c] for r, c in zip(range(n), reversed(range(n)))]     # => [3, 5, 7]

# ============================================
# Mirror trick — reuse ALL your main-diagonal code
#
# Flip every row left-to-right, and the anti-diagonal
# becomes the main diagonal.

flipped = [row[::-1] for row in m]

# =>
# [[3, 2, 1],
#  [6, 5, 4],
#  [9, 8, 7]]

[row[i] for i, row in enumerate(flipped)]       # => [3, 5, 7]

# ============================================
# Offset anti-diagonal
#
# Every anti-diagonal is one value of  r + c.
#   s = n - 1  ->  the main anti-diagonal
#   s < n - 1  ->  inward, toward the top-left
#   s > n - 1  ->  inward, toward the bottom-right

def anti_diagonal(m, s):
    return [row[s - i] for i, row in enumerate(m) if 0 <= s - i < len(row)]

anti_diagonal(m, n - 1)      # => [3, 5, 7]   main
anti_diagonal(m, n - 2)      # => [2, 4]      one inward
anti_diagonal(m, n)          # => [6, 8]      the other side
anti_diagonal(m, 0)          # => [1]         top-left corner

# ============================================
# Both diagonals at once (the "X")

main = [row[i] for i, row in enumerate(m)]          # => [1, 5, 9]
anti = [row[-1 - i] for i, row in enumerate(m)]     # => [3, 5, 7]

# ============================================
# Difference of diagonal sums

abs(sum(main) - sum(anti))                          # => 0

# ============================================
# Maximum on the anti-diagonal

max(row[-1 - i] for i, row in enumerate(m))         # => 7

# ============================================
# Check an X-pattern
#
# every cell on either diagonal is X, everything else is not

def is_x(grid, mark="X"):
    n = len(grid)
    return all((cell == mark) == (r == c or r + c == n - 1)
               for r, row in enumerate(grid)
               for c, cell in enumerate(row))

is_x([["X", ".", "X"],
      [".", "X", "."],
      ["X", ".", "X"]])                             # => True

# ============================================
# Detect anti-diagonal symmetry
#
# mirror across the anti-diagonal:  m[r][c] == m[n-1-c][n-1-r]

def anti_symmetric(m):
    n = len(m)
    return all(m[r][c] == m[n - 1 - c][n - 1 - r]
               for r in range(n) for c in range(n))

anti_symmetric([[1, 2, 3],
                [4, 5, 2],
                [6, 4, 1]])                         # => True

anti_symmetric(m)                                   # => False

# ============================================
# Traverse ALL anti-diagonals
#
# Same trick as lesson 3, but the key is  r + c  instead of  c - r.

diags = defaultdict(list)
for r, row in enumerate(m):
    for c, cell in enumerate(row):
        diags[r + c].append(cell)

[diags[s] for s in sorted(diags)]

# =>
# [[1], [2, 4], [3, 5, 7], [6, 8], [9]]
#   ^0    ^1      ^2 main    ^3     ^4

# ============================================
# Compare

# Main diagonal        m[i][i]          c - r  constant
# Anti-diagonal        m[i][-1 - i]     c + r  constant

# ============================================
# Generic pattern (works on non-square too)

[m[i][len(m[i]) - 1 - i] for i in range(min(len(m), len(m[0])))]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|anti-diagonal|`[row[-1 - i] for i, row in enumerate(m)]`|
|the terse version|`row[~i]`|
|sum / product|`sum(...)` / `prod(...)` over the same generator|
|coordinate pairs|`zip(range(n), reversed(range(n)))`|
|reuse main-diagonal code|flip rows: `[row[::-1] for row in m]`|
|one specific anti-diagonal|cells where `r + c == s`|
|all anti-diagonals|bucket by `r + c`|

---

## Key Insight

An anti-diagonal follows the simple coordinate rule:

```text
(row, col)

(0, n-1)
(1, n-2)
(2, n-3)
...
(n-1, 0)
```

Equivalently, in a square matrix:

```text
row + col = n - 1
```

Notice the contrast with the main diagonal:

|Traversal|Coordinate Rule|Python|
|---|---|---|
|Main Diagonal|`row == col`|`row[i]`|
|Anti-Diagonal|`row + col == n - 1`|`row[-1 - i]`|

The anti-diagonal is essentially the **mirror image** of the main diagonal. Whenever one index increases while the other decreases, you're traversing an anti-diagonal.

Two Python-specific takeaways:

- **Negative indexing already means "from the right."** `row[-1 - i]` (or `row[~i]`) expresses the rule with no `n` and no chance of an off-by-one.
    
- **You never need two sets of diagonal code.** Flip every row with `row[::-1]` and every main-diagonal recipe you already know works on the anti-diagonal unchanged.
    

---
