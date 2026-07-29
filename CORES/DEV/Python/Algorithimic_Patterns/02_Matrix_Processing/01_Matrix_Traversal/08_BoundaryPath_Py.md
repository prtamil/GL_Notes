# 8. Boundary Traversal

## Mental Model

Boundary traversal visits **only the outer border** of a matrix, ignoring all interior cells.

Unlike spiral traversal, which repeatedly peels inward, boundary traversal processes **exactly one ring**—the outermost perimeter.

Python gives you two completely different ways to say "the border", and picking the right one is most of the lesson:

- **A walk** — four slices in order, when you need the perimeter as a *path*.
    
- **A predicate** — `r in (0, rows-1) or c in (0, cols-1)`, when you only need the *cells*.
    

---

## Relationship to Cognitive Verb

```text
Outline
    ↓
Boundary Traversal
```

Related verbs:

- Outline
    
- Trace the border
    
- Walk the perimeter
    
- Follow the edge
    
- Visit the frame
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Top edge|first row|`m[0]`|
|Bottom edge|last row|`m[-1]`|
|Left edge|first column|`[row[0] for row in m]`|
|Right edge|last column|`[row[-1] for row in m]`|
|Clockwise boundary|complete border|four slices, concatenated|
|Counter-clockwise|reverse order|`[b[0]] + b[:0:-1]`|
|Border cells only|no ordering needed|`r in (0, rows-1) or c in (0, cols-1)`|
|Interior|everything else|`[row[1:-1] for row in m[1:-1]]`|
|Rotate the border|shift along the ring|`collections.deque.rotate`|

---

## Common Uses

- Image border detection
    
- Frame rendering
    
- Map boundaries
    
- Collision boundaries
    
- Grid visualization
    
- Maze entrances
    
- Geographic borders
    
- UI outlines
    

---

## Hidden Interview Problems

- Print matrix boundary
    
- Sum boundary elements
    
- Count perimeter cells
    
- Draw rectangular border
    
- Rotate boundary elements
    
- Compare boundary values
    
- Boundary maximum/minimum
    
- Extract matrix frame
    

---

## Recognition Clues

If you hear...

- "outer boundary..."
    
- "border..."
    
- "perimeter..."
    
- "frame..."
    
- "outer ring only..."
    

...think **Boundary Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Outer Boundary|
|Direction|Usually Clockwise|
|Coordinate Rule|First/Last row or column|
|Time Complexity|O(rows + cols)|
|Space Complexity|O(1) extra|
|Common Domains|Graphics, maps, UI, games|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from collections import deque

m = [[1,  2,  3,  4],
     [5,  6,  7,  8],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

rows, cols = len(m), len(m[0])

# ============================================
# The four edges — slicing says them directly

list(m[0])                          # top    => [1, 2, 3, 4]

[row[-1] for row in m]              # right  => [4, 8, 12, 16]

list(m[-1])                         # bottom => [13, 14, 15, 16]

[row[0] for row in m]               # left   => [1, 5, 9, 13]

# note: these OVERLAP at the corners — see the walk below

# ============================================
# The one idiom to remember
#
#   top, right, bottom-reversed, left-reversed
#
# Each edge after the first drops the corner the
# previous edge already visited. That's what the
# slices m[1:-1] and m[-2:0:-1] are doing.

def boundary(m):
    if len(m) == 1:
        return list(m[0])                   # single row
    if len(m[0]) == 1:
        return [row[0] for row in m]        # single column
    return (list(m[0])                      # top,    left -> right
            + [row[-1] for row in m[1:-1]]  # right,  top  -> bottom
            + list(m[-1])[::-1]             # bottom, right -> left
            + [row[0] for row in m[-2:0:-1]])   # left, bottom -> top

boundary(m)
# => [1, 2, 3, 4, 8, 12, 16, 15, 14, 13, 9, 5]

# ============================================
# Edge cases it has to survive

boundary([[1, 2, 3]])               # => [1, 2, 3]       single row
boundary([[1], [2], [3]])           # => [1, 2, 3]       single column
boundary([[1]])                     # => [1]             single cell
boundary([[1, 2], [3, 4]])          # => [1, 2, 4, 3]    no interior

# ============================================
# Counter-clockwise
#
# Keep the same starting corner, walk the ring backwards.

b = boundary(m)
[b[0], *b[:0:-1]]
# => [1, 5, 9, 13, 14, 15, 16, 12, 8, 4, 3, 2]

# ============================================
# The OTHER model: a predicate
#
# When you only need the border CELLS — sum, count,
# max, filter — ordering is wasted work. Ask instead:
# "is this cell on an edge?"

def on_border(r, c, rows, cols):
    return r in (0, rows - 1) or c in (0, cols - 1)

[cell
 for r, row in enumerate(m)
 for c, cell in enumerate(row)
 if on_border(r, c, rows, cols)]

# => [1, 2, 3, 4, 5, 8, 9, 12, 13, 14, 15, 16]
#    row-major order, NOT perimeter order — and that's fine

# ============================================
# Boundary sum / max / min

sum(boundary(m))                    # => 102

max(boundary(m))                    # => 16
min(boundary(m))                    # => 1

# the predicate form gives the same totals
sum(cell
    for r, row in enumerate(m)
    for c, cell in enumerate(row)
    if on_border(r, c, rows, cols))                 # => 102

# ============================================
# Count perimeter cells
#
# Don't walk it — the count is arithmetic.
# Every corner would be counted twice, hence -4.

len(boundary(m))                                    # => 12

2 * (rows + cols) - 4                               # => 12

# ============================================
# The interior (everything the boundary is not)

[row[1:-1] for row in m[1:-1]]

# =>
# [[6, 7],
#  [10, 11]]

# ============================================
# Extract the frame (border kept, interior blanked)

[[cell if on_border(r, c, rows, cols) else 0
  for c, cell in enumerate(row)]
 for r, row in enumerate(m)]

# =>
# [[1,  2,  3,  4],
#  [5,  0,  0,  8],
#  [9,  0,  0,  12],
#  [13, 14, 15, 16]]

# ============================================
# Draw a rectangular border

def frame(rows, cols, edge="#", fill="."):
    return [[edge if on_border(r, c, rows, cols) else fill
             for c in range(cols)]
            for r in range(rows)]

print("\n".join("".join(row) for row in frame(4, 6)))

# ######
# #....#     (4 rows x 6 cols)
# #....#
# ######

# ============================================
# The PATH, not the values
#
# boundary() works on a matrix of anything — hand it
# coordinates and you get the perimeter route.

def boundary_coords(rows, cols):
    return boundary([[(r, c) for c in range(cols)] for r in range(rows)])

boundary_coords(4, 4)[:5]
# => [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)]

# ============================================
# Rotate boundary elements
#
# Read the ring, deque.rotate it, write it back.

def rotate_boundary(m, k=1):
    coords = boundary_coords(len(m), len(m[0]))
    values = deque(m[r][c] for r, c in coords)
    values.rotate(k)
    out = [list(row) for row in m]
    for (r, c), value in zip(coords, values):
        out[r][c] = value
    return out

rotate_boundary(m)
# =>
# [[5,  1,  2,  3],
#  [9,  6,  7,  4],
#  [13, 10, 11, 8],
#  [14, 15, 16, 12]]

# ============================================
# Compare boundary values

boundary(m) == boundary(m)[::-1]        # => False  (not a palindrome ring)

set(boundary(m)) & set(range(1, 5))     # => {1, 2, 3, 4}

# ============================================
# Compare

# Entire matrix
[x for row in m for x in row]

# Boundary only, as a path
boundary(m)

# Boundary only, as cells
[cell for r, row in enumerate(m) for c, cell in enumerate(row)
      if on_border(r, c, rows, cols)]

# Boundary, repeated inward  ->  that's Spiral (lesson 5)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the perimeter path|top, right, bottom `[::-1]`, left `[::-1]`|
|drop repeated corners|`m[1:-1]` and `m[-2:0:-1]`|
|just the border cells|`r in (0, rows-1) or c in (0, cols-1)`|
|perimeter count|`2 * (rows + cols) - 4`|
|the interior|`[row[1:-1] for row in m[1:-1]]`|
|the route|`boundary()` over `(r, c)` pairs|
|shift the ring|`deque.rotate`|
|counter-clockwise|`[b[0], *b[:0:-1]]`|

---

## Key Insight

Boundary traversal is simply walking around the **perimeter** of the matrix.

```text
Top Edge
    ↓
Right Edge
    ↓
Bottom Edge
    ↓
Left Edge
```

The traversal always consists of the same four logical segments:

1. Top row
    
2. Right column
    
3. Bottom row (reverse)
    
4. Left column (reverse)
    

Unlike **Spiral Traversal**, you **stop after one complete circuit**.

The Python lesson underneath it: **corners are the whole difficulty.** Four naive edges give you 4 duplicated cells, which is exactly why the perimeter count is `2*(rows+cols) - 4` and why each slice after the top starts one cell in. If ordering doesn't matter, sidestep the problem entirely with the predicate — a cell is on the border when its row or its column is first or last.

---

## Boundary vs Spiral

|Pattern|Core Idea|
|---|---|
|**Boundary Traversal**|Visit the **outer border once**.|
|**Spiral Traversal**|Visit the outer border, **shrink the boundaries**, then repeat until the center is reached.|

Think of boundary traversal as:

```text
One Ring
```

and spiral traversal as:

```text
Ring 1
   ↓
Ring 2
   ↓
Ring 3
   ↓
...
```

> **Mental shift:** Boundary traversal is a **single perimeter walk**, whereas spiral traversal is **repeated boundary traversal with shrinking boundaries**.

In code the relationship is literal — spiral is boundary in a loop:

```python
def spiral(m):
    out = []
    while m:
        out += boundary(m)                  # one ring
        m = [row[1:-1] for row in m[1:-1]]  # shrink to the interior
    return out
```

Same `boundary()` from this lesson, plus the interior slice. **Lesson 8 is lesson 5 with the loop removed.**

---
