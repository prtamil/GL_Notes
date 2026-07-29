# 11. Radius Neighborhood

## Mental Model

Lessons 9 and 10 each hard-coded one answer to "what is near me". A **radius neighborhood** makes the answer a parameter:

> every cell within distance **R** of `(r, c)`.

Two knobs, not one:

- **R** — how far.
    
- **The metric** — what "far" means.
    

The metric decides the *shape*, and there are three worth knowing:

```text
Chebyshev R=2        Manhattan R=2        Euclidean R=3
max(|dr|,|dc|)<=R    |dr|+|dc| <= R       dr²+dc² <= R²

  # # # # #            . . # . .          . . . # . . .
  # # # # #            . # # # .          . # # # # # .
  # # · # #            # # · # #          . # # # # # .
  # # # # #            . # # # .          # # # · # # #
  # # # # #            . . # . .          . # # # # # .
                                          . # # # # # .
     square              diamond          . . . # . . .
                                                disc
```

And the payoff that makes this the last lesson of the section:

|Metric|R|Is exactly|
|---|---|---|
|Manhattan|1|4-Neighborhood (lesson 9)|
|Chebyshev|1|8-Neighborhood (lesson 10)|

**Lessons 9 and 10 are this lesson with R pinned to 1.** Write the general version once and the special cases fall out.

---

## Relationship to Cognitive Verb

```text
Reach
   ↓
Radius Neighborhood
```

Related verbs:

- Reach within
    
- Cover an area
    
- Influence / affect nearby
    
- Blur / spread
    
- Query around a point
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Build offsets|all cells within R|nested `range(-R, R+1)` + a metric test|
|Chebyshev test|square|`max(abs(dr), abs(dc)) <= R`|
|Manhattan test|diamond|`abs(dr) + abs(dc) <= R`|
|Euclidean test|disc|`dr*dr + dc*dc <= R*R`|
|Precompute|reuse per cell|build the table once, outside the loop|
|Square block|Chebyshev shortcut|`[row[c-R:c+R+1] for row in m[r-R:r+R+1]]`|
|Ring only|shell at exactly R|`== R` instead of `<= R`|
|Cumulative sum|large R, fast|prefix sums (lesson 27)|
|Spread from many|distance transform|multi-source BFS with `deque`|
|Falloff|weight by distance|`weight(d)` over the offsets|

---

## Common Uses

- Blur / sharpen with a configurable kernel radius
    
- Area-of-effect in games (explosions, auras, spell range)
    
- Movement range for a unit in a tactics game
    
- Proximity and spatial queries on a grid
    
- Dilation and erosion with a structuring element
    
- Heat / influence maps
    
- Density estimation on a raster
    
- Signal coverage and range checks
    
- Collision broad-phase on a uniform grid
    

---

## Hidden Interview Problems

- Image smoothing with radius k
    
- Count points within distance k of a target
    
- Maximum sum of a (2R+1)×(2R+1) submatrix
    
- Distance to nearest obstacle for every cell
    
- Number of cells reachable in k moves
    
- Bomb / explosion blast radius
    
- Cells covered by at least one tower
    
- Shortest distance in a grid with k-step jumps
    

---

## Recognition Clues

If you hear...

- "within distance k..."
    
- "radius..."
    
- "blast / blur / aura / range..."
    
- "all cells nearby..."
    
- "reachable in at most k moves..."
    
- "k-step neighborhood..."
    

...think **Radius Neighborhood**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Unit|One cell + everything within distance R|
|Parameters|R (distance) and metric (shape)|
|Count — Chebyshev|`(2R+1)² - 1`|
|Count — Manhattan|`2R(R+1)`|
|Count — Euclidean|no closed form; count it|
|Time Complexity|O(R²) per cell, O(rows × cols × R²) per sweep|
|Space Complexity|O(R²) for the offset table|
|Common Domains|Images, games, simulation, GIS|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from collections import deque

m = [[1,  2,  3,  4,  5],
     [6,  7,  8,  9,  10],
     [11, 12, 13, 14, 15],
     [16, 17, 18, 19, 20],
     [21, 22, 23, 24, 25]]

rows, cols = len(m), len(m[0])

# ============================================
# The metric IS the shape
#
# Three predicates, three neighborhoods. Everything
# else in this lesson is shared.

METRICS = {
    "chebyshev": lambda dr, dc, R: max(abs(dr), abs(dc)) <= R,   # square
    "manhattan": lambda dr, dc, R: abs(dr) + abs(dc) <= R,       # diamond
    "euclidean": lambda dr, dc, R: dr * dr + dc * dc <= R * R,   # disc
}

# euclidean compares SQUARES — no sqrt, no float error

# ============================================
# The offset table, generalized
#
# Build it ONCE. Rebuilding it inside a per-cell loop
# is the usual reason a blur is slow.

def offsets(R, metric="chebyshev"):
    inside = METRICS[metric]
    return tuple((dr, dc)
                 for dr in range(-R, R + 1)
                 for dc in range(-R, R + 1)
                 if (dr, dc) != (0, 0) and inside(dr, dc, R))

# ============================================
# R = 1 gives back lessons 9 and 10

len(offsets(1, "manhattan"))        # => 4    Von Neumann
len(offsets(1, "chebyshev"))        # => 8    Moore
len(offsets(1, "euclidean"))        # => 4    a disc of radius 1 is a plus

offsets(1, "manhattan")
# => ((-1, 0), (0, -1), (0, 1), (1, 0))

# ============================================
# The shapes diverge as R grows

[len(offsets(R, "chebyshev")) for R in (1, 2, 3)]   # => [8, 24, 48]
[len(offsets(R, "manhattan")) for R in (1, 2, 3)]   # => [4, 12, 24]
[len(offsets(R, "euclidean")) for R in (1, 2, 3)]   # => [4, 12, 28]

# the closed forms
[(2 * R + 1) ** 2 - 1 for R in (1, 2, 3)]           # => [8, 24, 48]
[2 * R * (R + 1)      for R in (1, 2, 3)]           # => [4, 12, 24]
# euclidean has none — you count it

# ============================================
# See the shape

def show(R, metric):
    off = set(offsets(R, metric))
    return "\n".join(
        " ".join("·" if (dr, dc) == (0, 0)
                 else "#" if (dr, dc) in off
                 else "."
                 for dc in range(-R, R + 1))
        for dr in range(-R, R + 1))

print(show(2, "manhattan"))
# . . # . .
# . # # # .
# # # · # #
# . # # # .
# . . # . .

# ============================================
# Same three moves as always: add, then filter

def in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols

def neighbors(r, c, rows, cols, off):
    return [(r + dr, c + dc) for dr, dc in off
            if in_bounds(r + dr, c + dc, rows, cols)]

off = offsets(1, "manhattan")
neighbors(2, 2, rows, cols, off)    # => [(1, 2), (2, 1), (2, 3), (3, 2)]

off2 = offsets(2, "manhattan")
len(neighbors(2, 2, rows, cols, off2))      # => 12   fully interior
len(neighbors(0, 0, rows, cols, off2))      # => 5    clipped at the corner

# ============================================
# The ring — exactly R, not within R
#
# One character changes: <= becomes ==.

def ring(R, metric="chebyshev"):
    inside = METRICS[metric]
    return tuple((dr, dc)
                 for dr in range(-R, R + 1)
                 for dc in range(-R, R + 1)
                 if inside(dr, dc, R) and not inside(dr, dc, R - 1))

len(ring(2, "chebyshev"))           # => 16   the 5x5 border
len(ring(2, "manhattan"))           # => 8    the diamond's edge

# and the balls are the rings stacked
sum(len(ring(k, "chebyshev")) for k in (1, 2))      # => 24 == len(offsets(2))

# ============================================
# Chebyshev has a shortcut: it is a square block
#
# max(0, ...) is mandatory — r-R may go negative and
# a negative slice start reads from the far end.

def block(m, r, c, R):
    return [row[max(0, c - R):c + R + 1]
            for row in m[max(0, r - R):r + R + 1]]

block(m, 2, 2, 1)
# =>
# [[7,  8,  9 ],
#  [12, 13, 14],
#  [17, 18, 19]]

block(m, 0, 0, 2)
# =>
# [[1,  2,  3 ],
#  [6,  7,  8 ],
#  [11, 12, 13]]      clipped, only 9 of the 25 cells exist

# ============================================
# Sum / mean over a radius — a blur with a knob

def blur(m, R=1, metric="chebyshev"):
    rows, cols = len(m), len(m[0])
    off = offsets(R, metric)                    # once, not per cell
    def mean(r, c):
        cells = [(r, c), *neighbors(r, c, rows, cols, off)]
        return sum(m[i][j] for i, j in cells) // len(cells)
    return [[mean(r, c) for c in range(cols)] for r in range(rows)]

blur(m, 1)
# =>
# [[4,  4,  5,  6,  7 ],
#  [6,  7,  8,  9,  9 ],
#  [11, 12, 13, 14, 14],
#  [16, 17, 18, 19, 19],
#  [19, 19, 20, 21, 22]]

# bigger R, flatter result — the whole point of the parameter
blur(m, 2)
# =>
# [[7,  7,  8,  8,  9 ],
#  [9,  10, 10, 11, 11],
#  [12, 12, 13, 13, 14],
#  [14, 15, 15, 16, 16],
#  [17, 17, 18, 18, 19]]
#
# R=1 still ranges 4..22; R=2 has collapsed to 7..19.
# The center cell (13) never moves — it is the mean already.

# ============================================
# Weighted falloff — near cells count more
#
# The offset table plus a weight function IS a kernel.

def falloff(m, r, c, R=2):
    rows, cols = len(m), len(m[0])
    total = 0.0
    for dr, dc in offsets(R, "euclidean"):
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc, rows, cols):
            d = (dr * dr + dc * dc) ** 0.5
            total += m[nr][nc] / (1 + d)
    return round(total, 2)

falloff(m, 2, 2)                    # => 64.87

# ============================================
# Area of effect — mark every cell a blast touches

def blast(rows, cols, center, R, metric="euclidean"):
    off = offsets(R, metric)
    hit = {center, *neighbors(*center, rows, cols, off)}
    return "\n".join("".join("#" if (r, c) in hit else "."
                             for c in range(cols))
                     for r in range(rows))

print(blast(9, 9, (4, 4), 3))
# .........
# ....#....
# ..#####..
# ..#####..
# .#######.
# ..#####..
# ..#####..
# ....#....
# .........
#
# 29 cells. R has to reach 3 before a disc stops
# looking like a diamond — at R=2 the euclidean and
# manhattan balls are the SAME 12 cells.

# ============================================
# Dilation — grow every marked cell by R
#
# Union of the radius neighborhoods of all marks.
# (Morphology calls the offset table a structuring element.)

def dilate(grid, R, metric="chebyshev"):
    rows, cols = len(grid), len(grid[0])
    off = offsets(R, metric)
    marked = {(r, c) for r in range(rows) for c in range(cols) if grid[r][c]}
    grown = set(marked)
    for r, c in marked:
        grown.update(neighbors(r, c, rows, cols, off))
    return [[int((r, c) in grown) for c in range(cols)] for r in range(rows)]

dilate([[0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]], 1, "manhattan")
# =>
# [[0, 0, 0, 0, 0],
#  [0, 0, 1, 0, 0],
#  [0, 1, 1, 1, 0],
#  [0, 0, 1, 0, 0],
#  [0, 0, 0, 0, 0]]

# ============================================
# Distance transform — R for every cell at once
#
# Don't loop radii. Multi-source BFS labels every cell
# with its distance to the nearest source in one pass.
# The neighborhood you step with picks the metric:
# 4-way -> Manhattan, 8-way -> Chebyshev.

def distance_map(grid, step=offsets(1, "manhattan")):
    rows, cols = len(grid), len(grid[0])
    dist = {(r, c): 0
            for r in range(rows) for c in range(cols) if grid[r][c]}
    queue = deque(dist)
    while queue:
        r, c = queue.popleft()
        for nb in neighbors(r, c, rows, cols, step):
            if nb not in dist:
                dist[nb] = dist[(r, c)] + 1
                queue.append(nb)
    return [[dist.get((r, c), -1) for c in range(cols)] for r in range(rows)]

distance_map([[1, 0, 0, 0, 0],
              [0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0],
              [0, 0, 0, 0, 1]])
# =>
# [[0, 1, 2, 3, 4],
#  [1, 2, 3, 4, 3],
#  [2, 3, 4, 3, 2],
#  [3, 4, 3, 2, 1],
#  [4, 3, 2, 1, 0]]
#
# O(cells), not O(cells × R²)

# ============================================
# "Is B within R of A" — don't build a neighborhood at all

def within(a, b, R, metric="chebyshev"):
    return METRICS[metric](a[0] - b[0], a[1] - b[1], R)

within((2, 2), (4, 4), 2, "chebyshev")      # => True
within((2, 2), (4, 4), 2, "manhattan")      # => False   distance is 4

# a membership test is O(1); enumerating the ball is O(R²)

# ============================================
# Compare

# distance 1, edges only          -> lesson 9
offsets(1, "manhattan")

# distance 1, edges + corners     -> lesson 10
offsets(1, "chebyshev")

# distance R, any shape           -> this lesson
offsets(R, metric)

# a fixed block that SLIDES       -> lessons 12-15
[row[c:c+k] for row in m[r:r+k]]

# every cell's radius sum, fast   -> prefix sums, lesson 27
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a square|`max(abs(dr), abs(dc)) <= R`|
|a diamond|`abs(dr) + abs(dc) <= R`|
|a disc|`dr*dr + dc*dc <= R*R`|
|the offsets|nested `range(-R, R+1)` + the test|
|speed|build the table **once**, outside the loop|
|the shell only|`== R` instead of `<= R`|
|a square block fast|`[row[max(0,c-R):c+R+1] for row in m[max(0,r-R):r+R+1]]`|
|every cell's distance|multi-source BFS, not a per-cell radius|
|just a yes/no|test the metric directly, skip the ball|

---

## Key Insight

**Radius is the generalization the first two lessons were special cases of.**

```text
offsets(R, metric)  ->  add  ->  filter
```

Same three moves as lesson 9. The only new idea is that the offset table is now *computed* rather than typed, from two parameters:

- **R** decides how big.
    
- **The metric decides the shape** — square, diamond, or disc. Choosing it is a modelling decision, not a detail: Chebyshev says a diagonal step is as cheap as a straight one, Manhattan says it costs two, Euclidean says it costs √2.
    

Three practical Python lessons live in this pattern:

1. **Hoist the table.** `offsets(R)` inside the per-cell loop recomputes O(R²) tuples for every one of the rows × cols cells. Build it once.
    
2. **Clamp your slices.** `m[r-R:r+R+1]` silently wraps when `r < R`. Use `max(0, r-R)`.
    
3. **Know when not to enumerate.** "Is B within R of A" is one metric test. "How far is every cell from the nearest source" is one BFS. Only "give me the cells around this one" actually needs the ball.
    

---

## The Neighborhood Section in One Table

|Lesson|Neighborhood|Offsets|Metric|Leads to|
|---|---|---|---|---|
|9|Von Neumann|4|Manhattan ≤ 1|graphs, BFS, flood fill|
|10|Moore|8|Chebyshev ≤ 1|automata, images, 3×3 windows|
|11|Radius|`f(R)`|any, ≤ R|blur, area of effect, distance maps|

```text
Von Neumann  ─┐
              ├─→  Radius (R, metric)
Moore        ─┘
```

> **Mental shift:** traversal answered *"in what order?"*; neighborhood answers *"who is near?"*. Fix the shape and slide it instead of centring it on a cell, and you have the next section — **windows**.
