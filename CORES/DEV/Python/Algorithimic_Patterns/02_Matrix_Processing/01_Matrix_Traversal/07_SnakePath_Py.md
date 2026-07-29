# 7. Snake Traversal

## Mental Model

Snake traversal visits the matrix in a **single continuous path** by traversing one row left→right, the next row right→left, and so on.

Unlike the general Zigzag pattern, Snake traversal emphasizes **path continuity**—the traversal ends one row exactly where the next row begins, like a snake moving across the matrix.

The Python code looks almost identical to zigzag. What changes is what you *ask of it*: with snake you care about the **path**, so the useful recipes are about coordinates, continuity, and index↔position math.

---

## Relationship to Cognitive Verb

```text
Serpentine
      ↓
Snake Traversal
```

Related verbs:

- Snake through
    
- Wind through
    
- Weave
    
- Serpentine
    
- Sweep continuously
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Row snake|alternate rows|`enumerate` + `[::-1]`|
|Column snake|alternate columns|`zip(*m)` + `[::-1]`|
|Continuous path|flatten traversal|`itertools.chain.from_iterable`|
|Alternating step|direction per line|`itertools.cycle([1, -1])`|
|Indexed snake|preserve coordinates|snake a matrix of `(r, c)` pairs|
|Verify continuity|adjacent steps only|`itertools.pairwise`|
|Index ↔ position|LED strips, buffers|`divmod`|

---

## Common Uses

- Robot vacuum paths
    
- CNC and 3D printer toolpaths
    
- Agricultural field coverage
    
- Image raster acquisition
    
- LED matrix animations
    
- Warehouse robots
    
- Autonomous vehicles
    
- Terrain scanning
    

---

## Hidden Interview Problems

- Print matrix in snake order
    
- Flatten matrix serpentine style
    
- Alternate row traversal
    
- Robot coverage path
    
- Raster scan optimization
    
- Continuous matrix walk
    
- Boustrophedon traversal
    

---

## Recognition Clues

If you hear...

- "snake through..."
    
- "serpentine..."
    
- "continuous path..."
    
- "lawn mower pattern..."
    
- "back-and-forth without lifting..."
    

...think **Snake Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Traversal Unit|Row (usually)|
|Direction|Alternating|
|Primary Goal|Continuous path|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) extra (excluding output)|
|Common Domains|Robotics, graphics, automation|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from itertools import chain, cycle, pairwise

m = [[1,  2,  3,  4],
     [5,  6,  7,  8],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

# ============================================
# The one idiom to remember
#
#   reverse every other row, then flatten.
#
# Same as zigzag — but here the point is that
# the result is ONE unbroken path.

def snake(m):
    return [x for i, row in enumerate(m) for x in row[::(-1) ** i]]

snake(m)
# => [1, 2, 3, 4, 8, 7, 6, 5, 9, 10, 11, 12, 16, 15, 14, 13]

# ============================================
# The itertools version — direction as a cycle
#
#   cycle([1, -1])  hands out  1, -1, 1, -1, ...
#   and that value IS the slice step.

def snake(m):
    return list(chain.from_iterable(row[::step] for row, step in zip(m, cycle([1, -1]))))

snake(m)
# => [1, 2, 3, 4, 8, 7, 6, 5, 9, 10, 11, 12, 16, 15, 14, 13]

# ============================================
# Visit cells

for i, row in enumerate(m):
    for cell in row[::(-1) ** i]:
        print(cell)

# ============================================
# Snake by columns

snake([list(col) for col in zip(*m)])
# => [1, 5, 9, 13, 14, 10, 6, 2, 3, 7, 11, 15, 16, 12, 8, 4]

# ============================================
# Generic serpentine
#
# Works on any sequence of sequences — rows, columns,
# levels, buckets.

def serpentine(lines):
    return [x for i, line in enumerate(lines) for x in line[::(-1) ** i]]

serpentine(m)                   # rows
serpentine(zip(*m))             # columns (tuples slice fine)

# ============================================
# The PATH, not the values
#
# Snake a matrix of coordinates and you get the
# route a robot / print head actually travels.

rows, cols = len(m), len(m[0])

path = snake([[(r, c) for c in range(cols)] for r in range(rows)])

path[:6]
# => [(0, 0), (0, 1), (0, 2), (0, 3), (1, 3), (1, 2)]

# ============================================
# Prove the continuity
#
# Every consecutive pair must be ONE step apart.
# This is the whole reason snake exists.

def is_continuous(path):
    return all(abs(r1 - r2) + abs(c1 - c2) == 1 for (r1, c1), (r2, c2) in pairwise(path))

is_continuous(path)                     # => True

# a plain raster scan is NOT continuous
raster = [(r, c) for r in range(rows) for c in range(cols)]
is_continuous(raster)                   # => False

# ============================================
# Why robots care — total travel distance

def travel(path):
    return sum(abs(r1 - r2) + abs(c1 - c2) for (r1, c1), (r2, c2) in pairwise(path))

travel(path)                            # => 15   (one step per move)
travel(raster)                          # => 24   (3 wasted carriage returns)

# on a 4x4 that's 60% extra movement, and it grows with width

# ============================================
# Index <-> position, without building the path
#
# This is the LED-strip / flat-buffer problem:
# cell (r, c) lives at which index of the snake?

def snake_index(r, c, cols):
    return r * cols + (c if r % 2 == 0 else cols - 1 - c)

def snake_position(k, cols):
    r, offset = divmod(k, cols)
    return r, offset if r % 2 == 0 else cols - 1 - offset

snake_index(1, 3, 4)                    # => 4     row 1 STARTS at column 3
snake_position(4, 4)                    # => (1, 3)

# they are exact inverses
all(snake_position(snake_index(r, c, cols), cols) == (r, c)
    for r in range(rows) for c in range(cols))          # => True

# ============================================
# Fill in snake order (boustrophedon numbering)

def snake_fill(rows, cols):
    grid = [[0] * cols for _ in range(rows)]
    for k, (r, c) in enumerate(snake([[(r, c) for c in range(cols)] for r in range(rows)]), start=1):
        grid[r][c] = k
    return grid

snake_fill(3, 4)
# =>
# [[1,  2,  3,  4],
#  [8,  7,  6,  5],
#  [9,  10, 11, 12]]

# ============================================
# Snake is its own inverse
#
# Applying it twice restores the original order.

flat = snake(m)
restored = snake([flat[i:i + cols] for i in range(0, len(flat), cols)])

restored == [x for row in m for x in row]       # => True

# ============================================
# Compare

# Normal (raster)          Snake
# 1  2  3  4               1  2  3  4
# 5  6  7  8               8  7  6  5
# 9  10 11 12              9  10 11 12
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|snake order|`row[::(-1) ** i]`, then flatten|
|the itertools form|`zip(m, cycle([1, -1]))`|
|the route|snake a matrix of `(r, c)` pairs|
|prove continuity|`pairwise` + Manhattan distance `== 1`|
|travel cost|`sum` of those distances|
|index → cell|`divmod(k, cols)`, flip odd rows|
|undo a snake|apply snake again|

---

## Key Insight

Snake traversal optimizes for a **continuous movement path**.

```text
→→→→
←←←←
→→→→
←←←←
```

Notice that the endpoint of one row is the starting point of the next:

```text
1 → 2 → 3 → 4
              ↓
5 ← 6 ← 7 ← 8
↓
9 → 10 → 11 → 12
```

There is **no jump back to the beginning of the next row**. This is why robots, printers, scanners, and CNC machines often use snake traversal—it minimizes unnecessary movement.

In Python that claim is one line you can actually run:

```python
all(abs(r1 - r2) + abs(c1 - c2) == 1 for (r1, c1), (r2, c2) in pairwise(path))
```

`pairwise` walks consecutive steps; Manhattan distance `1` means "moved to a neighbour, never teleported." A raster scan fails this test, a snake passes it — and the difference showed up above as 24 units of travel versus 15.

---

## Zigzag vs Snake

These two patterns are closely related but emphasize different ideas:

|Pattern|Core Idea|
|---|---|
|**Zigzag**|Alternate the direction of each traversal unit (rows, columns, or diagonals).|
|**Snake**|Follow one continuous serpentine path through the matrix, usually by alternating rows.|

Think of it this way:

```text
Zigzag
========
Focus:
Alternating Direction

Snake
========
Focus:
Continuous Path
```

Every row-based snake traversal is a **zigzag**, but not every zigzag traversal is a **snake** (for example, JPEG's diagonal zigzag is not a snake path).

That last claim is testable with the same one-liner — the diagonal zigzag from lesson 6 jumps between diagonals, so `is_continuous` returns `False` for it and `True` for the row snake. **The code is nearly identical; the property is not.**

---
