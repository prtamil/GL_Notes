# 29. Coordinate Grid

## Mental Model

Lesson 28 generated one specific matrix. This lesson generates the **general case**: put the coordinates themselves in the cells, or anything computed from them.

```text
f(r, c) = (r, c)

[[(0,0), (0,1), (0,2), (0,3)],
 [(1,0), (1,1), (1,2), (1,3)],
 [(2,0), (2,1), (2,2), (2,3)]]
```

That looks almost useless until you see what it is for. A coordinate grid is the **input** to every other generated matrix:

```python
[[f(r, c) for c in range(cols)] for r in range(rows)]
```

Change `f` and you get a distance field, a gradient, a ring, a triangle, an identity matrix, a checkerboard. Lessons 28 and 30 are this template with `f = int(r == c)` and `f = (r + c) % 2`. **This is the pattern; they are instances.**

Two uses beyond generating pictures make it worth its own lesson:

- **Separated axis grids** — a grid of row numbers and a grid of column numbers, which is what `meshgrid` produces in every array library. Vectorised code builds these instead of looping.
    
- **A probe for transforms.** Run a coordinate grid through `rot90` and each cell tells you *where it came from*. It turns lessons 16–21 from something you reason about into something you can read off.
    

---

## Relationship to Cognitive Verb

```text
Parameterise
     ↓
Coordinate Grid
```

Related verbs:

- Parameterise
- Map coordinates to values
- Sample a function
- Lay out a field
- Index the space

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Coordinate grid|pairs in cells|`[[(r,c) for c in ...] for r in ...]`|
|Generic generator|any rule|`[[f(r,c) for c in ...] for r in ...]`|
|Row grid|`r` broadcast|`[[r]*cols for r in range(rows)]`|
|Column grid|`c` broadcast|`[list(range(cols)) for _ in range(rows)]`|
|Flat index grid|row-major numbering|`r * cols + c` (lesson 23)|
|All pairs, flat|iteration order|`itertools.product(range(rows), range(cols))`|
|Distance field|from a point|`abs`, `max`, `math.hypot`|
|Gradient|a ramp|`c / (cols - 1)`|
|Predicate mask|0/1 shapes|`int(condition)`|
|Fill from a sequence|reshape|`[xs[i:i+w] for i in range(0, n, w)]`|
|Probe a transform|see where cells go|apply the transform to a coordinate grid|

---

## Common Uses

- Generating test data with known structure
- Distance fields and radial gradients
- Procedural textures and terrain
- Shader-style per-pixel functions
- `meshgrid` for vectorised computation
- Sampling a mathematical function over a region
- Building masks (circles, rings, triangles, borders)
- Debugging and visualising transforms
- Coordinate system conversions

---

## Hidden Interview Problems

- Generate a matrix where `m[i][j] = i * j` (a times table)
- Build a spiral-numbered matrix
- Generate a distance-to-nearest-border matrix
- Create a matrix of the first n² integers
- Fill a matrix diagonally
- Generate Pascal's triangle as a matrix
- Build a multiplication or addition table
- Construct a matrix from a formula

---

## Recognition Clues

If you hear...

- "generate a matrix where m[i][j] = ..."
- "build a grid of coordinates..."
- "distance from the centre..."
- "a gradient / ramp / field..."
- "meshgrid..."
- "create a test matrix..."

...think **Coordinate Grid**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Rule|`f(r, c)` — anything|
|Shape|`rows × cols`, independent of `f`|
|Cell type|Whatever `f` returns — tuple, int, float, str|
|Generality|Lessons 28 and 30 are special cases|
|Time Complexity|O(rows × cols × cost of `f`)|
|Space Complexity|O(rows × cols)|
|Common Domains|Graphics, simulation, testing, scientific computing|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember

import math
from itertools import product

def generate(rows, cols, f):
    return [[f(r, c) for c in range(cols)] for r in range(rows)]

# note the loop order: r OUTSIDE, c INSIDE. That is what
# makes row 0 the first row. Swapping them silently
# transposes the result.

# ============================================
# The coordinate grid itself

def coords(rows, cols):
    return [[(r, c) for c in range(cols)] for r in range(rows)]

coords(3, 4)
# =>
# [[(0,0), (0,1), (0,2), (0,3)],
#  [(1,0), (1,1), (1,2), (1,3)],
#  [(2,0), (2,1), (2,2), (2,3)]]

# ============================================
# Separated axes — the meshgrid idea
#
# Two grids, one holding r everywhere, one holding c.
# Array libraries build these so that `R + C` computes
# r+c for every cell without a Python loop.

def rowgrid(rows, cols):
    return [[r] * cols for r in range(rows)]

def colgrid(rows, cols):
    return [list(range(cols)) for _ in range(rows)]

rowgrid(3, 4)
# =>
# [[0, 0, 0, 0],
#  [1, 1, 1, 1],
#  [2, 2, 2, 2]]

colgrid(3, 4)
# =>
# [[0, 1, 2, 3],
#  [0, 1, 2, 3],
#  [0, 1, 2, 3]]
#
# note rowgrid uses [r]*cols — safe, because ints are
# immutable. The aliasing trap of lesson 28 is only
# about repeating a LIST.

# ============================================
# The flat index grid — lesson 23, made visible

def indexgrid(rows, cols):
    return [[r * cols + c for c in range(cols)] for r in range(rows)]

indexgrid(3, 4)
# =>
# [[0, 1,  2,  3 ],
#  [4, 5,  6,  7 ],
#  [8, 9,  10, 11]]

[divmod(i, 4) for i in (0, 5, 11)]      # => [(0,0), (1,1), (2,3)]
#
# printing this grid is the fastest way to convince
# yourself that row-major indexing is r*cols + c

# ============================================
# All positions as a flat sequence

list(product(range(2), range(3)))
# => [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]
#
# product() with the ROW range first gives row-major
# order — the same order as the nested comprehension.

# ============================================
# Arithmetic fields

generate(4, 4, lambda r, c: r + c)
# =>
# [[0, 1, 2, 3],
#  [1, 2, 3, 4],
#  [2, 3, 4, 5],
#  [3, 4, 5, 6]]      also: Manhattan distance from (0,0)

generate(4, 4, lambda r, c: r * c)
# =>
# [[0, 0, 0, 0],
#  [0, 1, 2, 3],
#  [0, 2, 4, 6],
#  [0, 3, 6, 9]]      a times table

# ============================================
# Distance fields — the three metrics of lesson 11
#
# Same centre, same code, different metric.

generate(5, 5, lambda r, c: max(abs(r-2), abs(c-2)))        # Chebyshev
# =>
# [[2, 2, 2, 2, 2],
#  [2, 1, 1, 1, 2],
#  [2, 1, 0, 1, 2],
#  [2, 1, 1, 1, 2],
#  [2, 2, 2, 2, 2]]      concentric squares

generate(5, 5, lambda r, c: round(math.hypot(r-2, c-2), 1)) # Euclidean
# =>
# [[2.8, 2.2, 2.0, 2.2, 2.8],
#  [2.2, 1.4, 1.0, 1.4, 2.2],
#  [2.0, 1.0, 0.0, 1.0, 2.0],
#  [2.2, 1.4, 1.0, 1.4, 2.2],
#  [2.8, 2.2, 2.0, 2.2, 2.8]]
#
# lesson 11 asked "which cells are within R?"; this
# asks "how far is every cell?" — the field, not the ball.

# ============================================
# Masks — a predicate makes a shape

generate(5, 5, lambda r, c: int((r-2)**2 + (c-2)**2 <= 4))  # disc
# =>
# [[0, 0, 1, 0, 0],
#  [0, 1, 1, 1, 0],
#  [1, 1, 1, 1, 1],
#  [0, 1, 1, 1, 0],
#  [0, 0, 1, 0, 0]]

generate(5, 5, lambda r, c: int(abs(r-2) + abs(c-2) <= 2))  # diamond
# => identical — at R=2 the Euclidean disc and the
#    Manhattan diamond are the same 13 cells (lesson 11)

generate(5, 5, lambda r, c: int(max(abs(r-2), abs(c-2)) == 2))   # ring
# =>
# [[1, 1, 1, 1, 1],
#  [1, 0, 0, 0, 1],
#  [1, 0, 0, 0, 1],
#  [1, 0, 0, 0, 1],
#  [1, 1, 1, 1, 1]]      the boundary of lesson 8

generate(5, 5, lambda r, c: int(r in (0,4) or c in (0,4)))       # border
# => the same ring — two spellings of "on the edge"

generate(4, 4, lambda r, c: int(c >= r))                         # triangular
# =>
# [[1, 1, 1, 1],
#  [0, 1, 1, 1],
#  [0, 0, 1, 1],
#  [0, 0, 0, 1]]

generate(5, 5, lambda r, c: int(r == c or r + c == 4))           # an X
# =>
# [[1, 0, 0, 0, 1],
#  [0, 1, 0, 1, 0],
#  [0, 0, 1, 0, 0],
#  [0, 1, 0, 1, 0],
#  [1, 0, 0, 0, 1]]

# ============================================
# Gradients — divide by the span, not the count

generate(3, 6, lambda r, c: round(c / 5, 2))
# =>
# [[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
#  [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
#  [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]]
#
# cols-1 == 5, not cols == 6. Dividing by cols never
# reaches 1.0 — the standard off-by-one in ramps.

# ============================================
# THE DEBUGGING USE: probe a transform
#
# Run a coordinate grid through any transform from
# lessons 16-21 and read off exactly where cells moved.

cg = coords(2, 3)
cg
# =>
# [[(0,0), (0,1), (0,2)],
#  [(1,0), (1,1), (1,2)]]

def rot90(m):
    return [list(r) for r in zip(*m[::-1])]

rot90(cg)
# =>
# [[(1,0), (0,0)],
#  [(1,1), (0,1)],
#  [(1,2), (0,2)]]
#
# read it as: the cell now at [0][1] originally held
# (0,0). So (0,0) -> (0,1). Check against lesson 17's
# rule (r,c) -> (c, rows-1-r) with rows=2:
#   (0,0) -> (0, 1)   ok
#   (0,2) -> (2, 1)   ok
#   (1,0) -> (0, 0)   ok
#
# This is how to settle "is it clockwise or
# counter-clockwise?" in five seconds instead of
# staring at numbers that look plausible either way.

def flip_h(m):
    return [row[::-1] for row in m]

flip_h(cg)
# =>
# [[(0,2), (0,1), (0,0)],
#  [(1,2), (1,1), (1,0)]]      only c changed — correct

# ============================================
# Filling from an existing sequence
#
# When the values come from data rather than a formula,
# this is lesson 22's reshape.

xs = list(range(1, 13))
[xs[i:i+4] for i in range(0, 12, 4)]
# =>
# [[1,  2,  3,  4 ],
#  [5,  6,  7,  8 ],
#  [9,  10, 11, 12]]

# and a constant grid — with the comprehension, always:
[[0] * 3 for _ in range(2)]         # => [[0,0,0], [0,0,0]]

# ============================================
# Compare — the whole section is one template

n = 4
generate(n, n, lambda r, c: (r, c))         # this lesson
generate(n, n, lambda r, c: int(r == c))    # lesson 28, identity
generate(n, n, lambda r, c: (r + c) % 2)    # lesson 30, checkerboard
generate(n, n, lambda r, c: r * n + c)      # lesson 23, flat index
generate(n, n, lambda r, c: max(abs(r-2), abs(c-2)))    # lesson 11, radius

generate(n, n, lambda r, c: int(r == c)) == [[int(r == c) for c in range(n)]
                                             for r in range(n)]     # => True
#
# 28 and 30 are not different patterns. They are this
# comprehension with a named f.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|any generated matrix|`[[f(r,c) for c in range(cols)] for r in range(rows)]`|
|coordinates in cells|`f = lambda r, c: (r, c)`|
|meshgrid|a row grid and a column grid, separately|
|the flat index|`r * cols + c`|
|all positions flat|`product(range(rows), range(cols))`|
|a distance field|`max(abs(...))`, `abs+abs`, or `math.hypot`|
|a shape|`int(condition)` — the predicate is the mask|
|a ramp to exactly 1.0|divide by `cols - 1`|
|to check a transform|run it on a coordinate grid and read it off|

---

## Key Insight

**A coordinate grid is not a matrix you want — it is the argument to every matrix you want.**

```text
[[f(r, c) for c in range(cols)] for r in range(rows)]
```

That comprehension is the entire generation section. `f = int(r == c)` gives lesson 28. `f = (r + c) % 2` gives lesson 30. `f = max(abs(r-cr), abs(c-cc))` gives lesson 11's Chebyshev field. `f = r*cols + c` gives lesson 23's row-major index. Learning to reach for the template rather than the instance is the point.

Three practical things:

1. **Loop order is `r` outside, `c` inside.** Swap them and you silently get the transpose — a bug that produces a valid-looking matrix of the wrong shape.
    
2. **A predicate is a mask.** `int(condition)` turns any geometric statement into a 0/1 grid, which is why discs, rings, borders, triangles and diagonals are all one line. And `int()` on a bool is what makes it terse.
    
3. **Use it to debug transforms.** This is the genuinely underused trick: apply `rot90` to a grid of `(r, c)` pairs and every cell reports where it came from. Direction bugs in lessons 17 and 19 are invisible on symmetric data and instantly visible here.
    

One numerical detail worth internalising: a gradient across `cols` cells divides by **`cols - 1`**, not `cols`, or it never reaches the endpoint.

---

## Coordinate Grid vs the Rest

|Lesson|What it does with `(r, c)`|
|---|---|
|1–8 Traversal|chooses an **order** to visit them|
|9–11 Neighborhood|chooses which are **near** one of them|
|12–15 Windows|chooses a **rectangle** of them|
|16–21 Structure|**moves** each to a new `(r, c)`|
|22–23 Layout|**regroups** them without moving|
|24–26 Search|**finds** one, or groups of them|
|27 Prefix Sum|**precomputes** over all prefixes of them|
|**29 Coordinate Grid**|**turns them into values** — the source, not the consumer|

```text
  every other lesson:   matrix  ──►  answer
  generation:           f(r,c)  ──►  matrix
```

> **Mental shift:** the rest of the course treats `(r, c)` as an address for looking something up. Generation treats it as an **input** — the matrix is a function sampled over a rectangle. Once that clicks, "write a matrix where `m[i][j] = ...`" stops being a puzzle and becomes transcription.
