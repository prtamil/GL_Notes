# 5. Spiral Traversal

## Mental Model

Spiral traversal visits a matrix by **walking around its boundary, then shrinking inward layer by layer** until every cell has been visited.

Instead of thinking in terms of rows or columns, think in terms of **nested rectangles (layers or rings)**.

Python offers a second mental model that is far easier to memorize than four moving boundaries: **take the top row, rotate what's left, repeat.** The spiral falls out of the rotation.

---

## Relationship to Cognitive Verb

```text
Peel
   ↓
Spiral Traversal
```

Related verbs:

- Peel layers
    
- Walk around the boundary
    
- Traverse in a spiral
    
- Visit concentric rings
    
- Shrink inward
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Clockwise spiral|outer → inner|peel + rotate with `zip(*m)`|
|Counter-clockwise|reverse direction|spiral of the transpose|
|Layer traversal|process one ring|four boundary variables in a `while`|
|Spiral generation|fill matrix|spiral the **coordinates**, then assign|
|Boundary shrinking|move edges inward|`top`, `bottom`, `left`, `right`|
|Turn on collision|direction vectors|`(d + 1) % 4` over `[(0,1),(1,0),(0,-1),(-1,0)]`|

> Unlike row or diagonal traversal, spiral traversal is **stateful**. Python gives you two ways to handle that state: carry it explicitly in four boundary variables, or make it disappear by rotating the matrix.

---

## Common Uses

- Matrix printing
    
- UI animations
    
- Robot navigation
    
- Image scanning
    
- Game map exploration
    
- CNC/Laser tool paths
    
- Puzzle generation
    
- Memory-efficient visualization
    

---

## Hidden Interview Problems

- Print matrix in spiral order
    
- Fill matrix in spiral order
    
- Spiral Matrix I / II
    
- Traverse concentric layers
    
- Rotate matrix layer-by-layer
    
- Count spiral rings
    
- Spiral search
    

---

## Recognition Clues

If you hear...

- "spiral..."
    
- "clockwise..."
    
- "outer layer..."
    
- "ring..."
    
- "move inward..."
    
- "peel the matrix..."
    

...think **Spiral Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Layer (Ring)|
|Direction|Usually Clockwise|
|Coordinate Rule|Shrinking boundaries|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (excluding output)|
|Common Domains|Graphics, robotics, interview problems|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

m = [[1,  2,  3,  4],
     [5,  6,  7,  8],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

# ============================================
# The one idiom to remember
#
#   take the top row,
#   rotate the rest counter-clockwise,
#   repeat.
#
# After rotating, the "next" edge of the spiral
# is always sitting on top again.

def spiral(m):
    out = []
    while m:
        out += list(m[0])                   # take the top row
        m = [*zip(*m[1:])][::-1]            # rotate the rest CCW
    return out

spiral(m)
# => [1, 2, 3, 4, 8, 12, 16, 15, 14, 13, 9, 5, 6, 7, 11, 10]

# ============================================
# Why the rotation works
#
#   zip(*rest)          transpose
#   [...][::-1]         flip vertically
#   together            = rotate counter-clockwise

rest = m[1:]

# =>
# [[5,  6,  7,  8],
#  [9,  10, 11, 12],
#  [13, 14, 15, 16]]

[*zip(*rest)][::-1]

# =>
# [(8, 12, 16),      <- the right edge, now on top
#  (7, 11, 15),
#  (6, 10, 14),
#  (5,  9, 13)]

# ============================================
# Same idea as a recursive one-liner

def spiral(m):
    return [*m[0], *spiral([*zip(*m[1:])][::-1])] if m else []

spiral(m)
# => [1, 2, 3, 4, 8, 12, 16, 15, 14, 13, 9, 5, 6, 7, 11, 10]

# ============================================
# Counter-clockwise
#
# A CCW spiral is just a CW spiral of the transpose.

def spiral_ccw(m):
    return spiral([*zip(*m)])

spiral_ccw(m)
# => [1, 5, 9, 13, 14, 15, 16, 12, 8, 4, 3, 2, 6, 10, 11, 7]

# ============================================
# The four boundaries (the explicit model)

top, bottom = 0, len(m) - 1
left, right = 0, len(m[0]) - 1

# ============================================
# Top edge

[m[top][c] for c in range(left, right + 1)]         # => [1, 2, 3, 4]

# ============================================
# Right edge

[m[r][right] for r in range(top + 1, bottom + 1)]   # => [8, 12, 16]

# ============================================
# Bottom edge (reversed)

[m[bottom][c] for c in range(right - 1, left - 1, -1)]      # => [15, 14, 13]

# ============================================
# Left edge (reversed)

[m[r][left] for r in range(bottom - 1, top, -1)]            # => [9, 5]

# ============================================
# Complete first ring

ring = ([m[top][c] for c in range(left, right + 1)] +
        [m[r][right] for r in range(top + 1, bottom + 1)] +
        [m[bottom][c] for c in range(right - 1, left - 1, -1)] +
        [m[r][left] for r in range(bottom - 1, top, -1)])

# => [1, 2, 3, 4, 8, 12, 16, 15, 14, 13, 9, 5]

# ============================================
# Shrink boundaries

top, bottom, left, right = top + 1, bottom - 1, left + 1, right - 1

# ============================================
# Full boundary implementation
#
# Shrink each edge the moment you finish walking it,
# and re-check before the two reversed edges —
# that guard is what makes single rows/columns safe.

def spiral_bounds(m):
    if not m or not m[0]:
        return []
    top, bottom = 0, len(m) - 1
    left, right = 0, len(m[0]) - 1
    out = []
    while top <= bottom and left <= right:
        out += [m[top][c] for c in range(left, right + 1)]
        top += 1
        out += [m[r][right] for r in range(top, bottom + 1)]
        right -= 1
        if top <= bottom:
            out += [m[bottom][c] for c in range(right, left - 1, -1)]
            bottom -= 1
        if left <= right:
            out += [m[r][left] for r in range(bottom, top - 1, -1)]
            left += 1
    return out

spiral_bounds(m)
# => [1, 2, 3, 4, 8, 12, 16, 15, 14, 13, 9, 5, 6, 7, 11, 10]

spiral_bounds([[1, 2, 3]])          # => [1, 2, 3]        single row
spiral_bounds([[1], [2], [3]])      # => [1, 2, 3]        single column

# ============================================
# Ring by ring (keep the layers separate)

def rings(m):
    out = []
    while m:
        out.append(list(m[0]))
        m = [*zip(*m[1:])][::-1]
    return out

# careful: that peels EDGES, not rings — four peels make one ring

def concentric(m):
    layers, edges = [], rings(m)
    while edges:
        layers.append([x for edge in edges[:4] for x in edge])
        edges = edges[4:]
    return layers

concentric(m)
# => [[1, 2, 3, 4, 8, 12, 16, 15, 14, 13, 9, 5],
#     [6, 7, 11, 10]]

# ============================================
# Count spiral rings

rows, cols = len(m), len(m[0])
(min(rows, cols) + 1) // 2              # => 2

# ============================================
# Spiral the COORDINATES, not the values
#
# spiral() works on a matrix of anything —
# so hand it (r, c) pairs and you get the path itself.

coords = spiral([[(r, c) for c in range(cols)] for r in range(rows)])

coords[:5]
# => [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3)]

# ============================================
# Fill a matrix in spiral order (Spiral Matrix II)
#
# Now that you have the path, filling is just enumerate.

def spiral_fill(n):
    grid = [[0] * n for _ in range(n)]
    path = spiral([[(r, c) for c in range(n)] for r in range(n)])
    for value, (r, c) in enumerate(path, start=1):
        grid[r][c] = value
    return grid

spiral_fill(3)
# =>
# [[1, 2, 3],
#  [8, 9, 4],
#  [7, 6, 5]]

# ============================================
# Direction vectors (turn when you hit something)
#
# Use this when the shape is irregular or cells get
# blocked — it generalizes where boundaries don't.

def spiral_walk(m):
    rows, cols = len(m), len(m[0])
    seen = [[False] * cols for _ in range(rows)]
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]      # right, down, left, up
    r = c = d = 0
    out = []
    for _ in range(rows * cols):
        out.append(m[r][c])
        seen[r][c] = True
        dr, dc = moves[d]
        if not (0 <= r + dr < rows and 0 <= c + dc < cols and not seen[r + dr][c + dc]):
            d = (d + 1) % 4                          # turn right
            dr, dc = moves[d]
        r, c = r + dr, c + dc
    return out

spiral_walk(m)
# => [1, 2, 3, 4, 8, 12, 16, 15, 14, 13, 9, 5, 6, 7, 11, 10]

# ============================================
# Compare

# Row / column / diagonal    one coordinate formula, stateless
# Spiral                     four moving boundaries, OR peel + rotate
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|spiral order|`out += m[0]; m = [*zip(*m[1:])][::-1]`|
|the rotation|transpose + flip = rotate CCW|
|counter-clockwise|`spiral([*zip(*m)])`|
|explicit control|`top`/`bottom`/`left`/`right` in a `while`|
|the path, not the values|spiral a matrix of `(r, c)` pairs|
|fill in spiral order|`enumerate(path, start=1)`|
|ring count|`(min(rows, cols) + 1) // 2`|
|irregular shapes|direction vectors, `(d + 1) % 4`|

---

## Key Insight

Unlike previous traversal patterns, spiral traversal is **not defined by a simple coordinate formula**.

Instead, it maintains **four moving boundaries**:

```text
top
bottom
left
right
```

Each iteration performs the same cycle:

```text
Top Edge
    ↓
Right Edge
    ↓
Bottom Edge
    ↓
Left Edge
    ↓
Shrink Boundaries
    ↓
Repeat
```

You can think of spiral traversal as **peeling an onion**: process the outermost ring, remove it conceptually, then repeat on the smaller inner matrix.

> **Mental shift:** The fundamental unit is no longer a row, column, or diagonal—it is a **layer (ring)**.

**The Python shortcut:** you can trade all four boundaries for a rotation.

```text
take the top row
rotate the rest counter-clockwise
repeat
```

Because `[*zip(*rest)][::-1]` rotates, the edge you need next is *always the top row again* — the state lives in the matrix instead of in your variables. Reach for the boundary version when you must not copy the matrix or you need the indices; reach for peel-and-rotate when you need to write it correctly from memory under pressure.

---
