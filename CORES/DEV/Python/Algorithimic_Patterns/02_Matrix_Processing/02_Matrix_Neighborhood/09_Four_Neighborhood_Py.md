# 9. 4-Neighborhood (Von Neumann)

## Mental Model

Traversal asks *"what order do I visit cells in?"*. Neighborhood asks a completely different question: **"given one cell, which cells touch it?"**

The 4-neighborhood — the **Von Neumann neighborhood** — is the strictest answer: the cells sharing an **edge** with `(r, c)`.

```text
      (r-1, c)
         N
(r, c-1) W  ·  E (r, c+1)
         S
      (r+1, c)
```

Diagonals do **not** count. You cannot reach a diagonal neighbor without passing through one of these four, which is exactly why this neighborhood defines **Manhattan distance 1**.

In Python the pattern is always the same three moves:

1. A table of **offsets** — `(-1,0), (1,0), (0,-1), (0,1)`.
    
2. **Add** them to your cell.
    
3. **Filter** the ones that fell off the grid.
    

Everything else in this lesson is a variation on avoiding step 3.

---

## Relationship to Cognitive Verb

```text
Touch
   ↓
4-Neighborhood
```

Related verbs:

- Touch
    
- Look around
    
- Step (one move)
    
- Adjacent to
    
- Border on
    
- Reach directly
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Offset table|the four directions|`((-1,0),(1,0),(0,-1),(0,1))`|
|Apply offsets|candidate cells|`[(r+dr, c+dc) for dr, dc in N4]`|
|Bounds check|stay on the grid|`0 <= r < rows and 0 <= c < cols`|
|Neighbor values|cells, not coords|`m[r][c] for r, c in neighbors(...)`|
|Bounds-free grid|dict instead of list|`g.get((r, c))`|
|Bounds-free grid|sentinel border|pad with an extra ring|
|Wrap around|torus / Pac-Man|`(r+dr) % rows`|
|Count matching|"how many neighbors are X"|`sum(...)` over a generator|
|Spread outward|BFS / flood fill|`collections.deque`|
|Compact coords|one number per cell|`complex(r, c)`, dirs `±1, ±1j`|

---

## Common Uses

- Flood fill / paint bucket
    
- Maze solving (no diagonal moves)
    
- Shortest path on a grid (BFS)
    
- Island / region counting
    
- Image erosion and dilation
    
- Cellular automata (Von Neumann rules)
    
- Rot / fire / water spreading simulations
    
- Tile-based games with 4-way movement
    
- Percolation and connectivity
    

---

## Hidden Interview Problems

- Number of Islands
    
- Flood Fill
    
- Rotting Oranges
    
- Shortest Path in Binary Matrix (4-way variant)
    
- Surrounded Regions
    
- Pacific Atlantic Water Flow
    
- Walls and Gates
    
- 01 Matrix (distance to nearest zero)
    
- Count cells that are local minima
    

---

## Recognition Clues

If you hear...

- "adjacent cells..."
    
- "up, down, left, right..."
    
- "connected horizontally or vertically..."
    
- "you may move one step..."
    
- "cells that share a side..."
    
- "spreads to neighboring cells..."
    

...think **4-Neighborhood**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Unit|One cell + its edge-adjacent cells|
|Neighbor count|4 interior, 3 edge, 2 corner|
|Distance metric|Manhattan (`abs(dr) + abs(dc) == 1`)|
|Symmetry|Mutual — if A sees B, B sees A|
|Time Complexity|O(1) per cell, O(rows × cols) per sweep|
|Space Complexity|O(1) extra (O(cells) for BFS)|
|Common Domains|Games, images, simulations, graphs|

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
# The offset table — write it once, reuse forever
#
# Order is N, S, W, E. Any order works; be consistent
# so your outputs are reproducible.

N4 = ((-1, 0), (1, 0), (0, -1), (0, 1))

# ============================================
# The one idiom to remember
#
#   offsets  ->  add  ->  filter out-of-bounds

def in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols

def neighbors4(r, c, rows, cols):
    return [(r + dr, c + dc) for dr, dc in N4
            if in_bounds(r + dr, c + dc, rows, cols)]

neighbors4(1, 1, rows, cols)    # => [(0, 1), (2, 1), (1, 0), (1, 2)]

# ============================================
# The grid boundary is the whole difficulty

neighbors4(0, 0, rows, cols)    # => [(1, 0), (0, 1)]           corner: 2
neighbors4(0, 1, rows, cols)    # => [(1, 1), (0, 0), (0, 2)]   edge:   3
neighbors4(1, 1, rows, cols)    # 4 neighbors                   interior

# ============================================
# Neighbor VALUES rather than coordinates

[m[r][c] for r, c in neighbors4(1, 1, rows, cols)]     # => [2, 10, 5, 7]

sum(m[r][c] for r, c in neighbors4(1, 1, rows, cols))  # => 24

# ============================================
# Never write `m[r-1][c]` without a guard
#
# Negative indices are LEGAL in Python — they wrap to
# the other end of the list instead of raising.

m[-1][0]        # => 13, silently the bottom row, not an error
                # this is the #1 grid bug in Python

# ============================================
# Escape hatch 1: a dict grid
#
# Missing keys stand in for "off the grid", so the
# bounds check disappears into .get()

g = {(r, c): v for r, row in enumerate(m) for c, v in enumerate(row)}

def neighbors4_dict(g, r, c):
    return [(r + dr, c + dc) for dr, dc in N4 if (r + dr, c + dc) in g]

neighbors4_dict(g, 0, 0)                        # => [(1, 0), (0, 1)]

[g.get((0 + dr, 0 + dc)) for dr, dc in N4]      # => [None, 5, None, 2]

# ============================================
# Escape hatch 2: a sentinel border
#
# Pad the matrix with one extra ring, then every real
# cell is interior and no bounds check is ever needed.

def pad(m, fill=0):
    width = len(m[0]) + 2
    return ([[fill] * width]
            + [[fill, *row, fill] for row in m]
            + [[fill] * width])

p = pad(m)

# real cell (r, c) now lives at (r+1, c+1)
[p[1 + dr][1 + dc] for dr, dc in N4]            # => [0, 5, 0, 2]

# ============================================
# Escape hatch 3: wrap around (torus)
#
# No edges at all — every cell has exactly 4 neighbors.

def neighbors4_wrap(r, c, rows, cols):
    return [((r + dr) % rows, (c + dc) % cols) for dr, dc in N4]

neighbors4_wrap(0, 0, rows, cols)   # => [(3, 0), (1, 0), (0, 3), (0, 1)]

# ============================================
# Complex numbers as coordinates
#
# A cell is one number, a direction is one number,
# and "step" is plain addition.

DIRS = (-1, 1, -1j, 1j)             # up, down, left, right

def neighbors4_complex(z, rows, cols):
    return [z + d for d in DIRS
            if 0 <= (z + d).real < rows and 0 <= (z + d).imag < cols]

neighbors4_complex(complex(1, 1), rows, cols)
# => [1j, (2+1j), (1+0j), (1+2j)]
#    read as (0,1), (2,1), (1,0), (1,2)

# ============================================
# Count neighbors satisfying a predicate

grid = [[0, 1, 0],
        [1, 1, 0],
        [0, 0, 1]]

def count4(grid, r, c, value=1):
    return sum(grid[nr][nc] == value
               for nr, nc in neighbors4(r, c, len(grid), len(grid[0])))

count4(grid, 1, 1)                  # => 2   (up and left are 1)

# the whole map of counts
[[count4(grid, r, c) for c in range(3)] for r in range(3)]
# =>
# [[2, 1, 1],
#  [1, 2, 2],
#  [1, 2, 0]]

# ============================================
# Local minimum / maximum

def is_local_min(m, r, c):
    return all(m[r][c] < m[nr][nc]
               for nr, nc in neighbors4(r, c, len(m), len(m[0])))

is_local_min(m, 0, 0)               # => True   (1 beats 2 and 5)
is_local_min(m, 1, 1)               # => False

# ============================================
# Smoothing — replace each cell by its neighborhood mean
#
# The cell itself is usually included; note that edge
# cells average over fewer neighbors.

def smooth(m):
    rows, cols = len(m), len(m[0])
    def mean(r, c):
        cells = [(r, c), *neighbors4(r, c, rows, cols)]
        return sum(m[i][j] for i, j in cells) / len(cells)
    return [[mean(r, c) for c in range(cols)] for r in range(rows)]

smooth([[0, 0, 0],
        [0, 9, 0],
        [0, 0, 0]])
# =>
# [[0.0,  2.25, 0.0 ],
#  [2.25, 1.8,  2.25],
#  [0.0,  2.25, 0.0 ]]
#
# the 9 leaks to its 4 neighbours and nowhere else —
# the corners stay 0.0 because they are not adjacent

# ============================================
# BFS — the reason this neighborhood exists
#
# The neighborhood function IS the graph. Swap it for
# neighbors8 and the same BFS solves a different problem.

def bfs(m, start):
    rows, cols = len(m), len(m[0])
    dist = {start: 0}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        for nb in neighbors4(r, c, rows, cols):
            if nb not in dist:
                dist[nb] = dist[(r, c)] + 1
                queue.append(nb)
    return dist

d = bfs(m, (0, 0))
[[d[(r, c)] for c in range(cols)] for r in range(rows)]
# =>
# [[0, 1, 2, 3],
#  [1, 2, 3, 4],
#  [2, 3, 4, 5],
#  [3, 4, 5, 6]]
#
# on an open grid BFS distance == Manhattan distance;
# walls are what make it interesting

# ============================================
# Flood fill — BFS that refuses to cross a colour change

def flood_fill(grid, start, new):
    rows, cols = len(grid), len(grid[0])
    out = [list(row) for row in grid]
    old = out[start[0]][start[1]]
    if old == new:
        return out
    queue = deque([start])
    out[start[0]][start[1]] = new
    while queue:
        r, c = queue.popleft()
        for nr, nc in neighbors4(r, c, rows, cols):
            if out[nr][nc] == old:
                out[nr][nc] = new
                queue.append((nr, nc))
    return out

flood_fill([[1, 1, 0],
            [1, 0, 0],
            [0, 0, 1]], (0, 0), 7)
# =>
# [[7, 7, 0],
#  [7, 0, 0],
#  [0, 0, 1]]
#
# the bottom-right 1 survives — diagonals don't connect

# ============================================
# Count connected regions (islands)

def islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen, count = set(), 0
    for r, c in ((r, c) for r in range(rows) for c in range(cols)):
        if grid[r][c] != 1 or (r, c) in seen:
            continue
        count += 1
        queue = deque([(r, c)])
        seen.add((r, c))
        while queue:
            cr, cc = queue.popleft()
            for nb in neighbors4(cr, cc, rows, cols):
                if grid[nb[0]][nb[1]] == 1 and nb not in seen:
                    seen.add(nb)
                    queue.append(nb)
    return count

islands([[1, 1, 0],
         [1, 0, 0],
         [0, 0, 1]])                # => 2

# ============================================
# All edges of the grid graph
#
# Count each pair once by looking only right and down.

def edges(rows, cols):
    return [((r, c), (r + dr, c + dc))
            for r in range(rows) for c in range(cols)
            for dr, dc in ((0, 1), (1, 0))
            if in_bounds(r + dr, c + dc, rows, cols)]

len(edges(rows, cols))              # => 24

rows * (cols - 1) + cols * (rows - 1)   # => 24, the arithmetic

# ============================================
# 4-neighborhood IS Manhattan distance 1

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

all(manhattan((1, 1), nb) == 1 for nb in neighbors4(1, 1, rows, cols))  # => True

# ============================================
# Compare

# every cell                   -> traversal (lessons 1-8)
[(r, c) for r in range(rows) for c in range(cols)]

# cells touching one cell      -> this lesson
neighbors4(r, c, rows, cols)

# ...plus diagonals            -> Moore (lesson 10)
# ...within distance R         -> Radius (lesson 11)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the four directions|`((-1,0),(1,0),(0,-1),(0,1))`|
|a neighbor|`(r + dr, c + dc)`|
|to stay on the grid|`0 <= r < rows and 0 <= c < cols`|
|no bounds check|dict grid + `.get`, or a padded ring|
|no edges at all|`% rows`, `% cols`|
|"how many neighbors are X"|`sum(g[nr][nc] == X for nr, nc in ...)`|
|to spread outward|`deque` + `neighbors4`|
|one number per cell|`complex(r, c)`, dirs `±1, ±1j`|

---

## Key Insight

**A neighborhood function turns a matrix into a graph.**

```text
offsets  ->  add  ->  filter
```

Once you have `neighbors4(r, c)`, every grid algorithm you know is a *generic graph algorithm* with that one function plugged in — BFS, DFS, flood fill, connected components, shortest path. None of them mention rows or columns.

That is why this pattern is worth isolating: **swap the neighborhood, keep the algorithm.** Replace `neighbors4` with `neighbors8` and BFS suddenly allows diagonal movement; replace it with a radius function and it becomes a blur. The algorithm never changes.

The Python-specific warning: `m[r-1][c]` does not raise when `r == 0`. It silently wraps to the last row. **The bounds check is not optional** — or use a dict grid, where "off the grid" is just a missing key.

---

## Von Neumann vs Moore

|Pattern|Core Idea|
|---|---|
|**4-Neighborhood (Von Neumann)**|Cells sharing an **edge**. Manhattan distance 1.|
|**8-Neighborhood (Moore)**|Cells sharing an edge **or a corner**. Chebyshev distance 1.|

```text
Von Neumann          Moore
   . N .             D N D
   W · E             W · E
   . S .             D S D
```

> **Mental shift:** the two neighborhoods differ only in the offset table. Every function in this lesson works unchanged with the 8-direction table — which is exactly what lesson 10 does.
