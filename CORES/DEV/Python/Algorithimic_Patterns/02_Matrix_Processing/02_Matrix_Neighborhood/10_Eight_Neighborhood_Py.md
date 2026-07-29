# 10. 8-Neighborhood (Moore)

## Mental Model

The **Moore neighborhood** is the 4-neighborhood plus the four diagonals — every cell that shares an **edge or a corner** with `(r, c)`.

```text
(r-1,c-1) (r-1,c) (r-1,c+1)
(r,  c-1)    ·    (r,  c+1)
(r+1,c-1) (r+1,c) (r+1,c+1)
```

Two mental models, and both are worth carrying:

- **Eight offsets.** A king's move in chess; Chebyshev distance 1.
    
- **A 3×3 block minus its center.** This is the one that generalizes — it turns the neighborhood into a *window*, which is what convolution, blurring and Game of Life actually operate on.
    

The second model is why Moore, not Von Neumann, is the default in image processing and cellular automata: it is the natural 3×3 stencil, and in Python you can take it with **slicing** instead of an offset loop.

---

## Relationship to Cognitive Verb

```text
Surround
   ↓
8-Neighborhood
```

Related verbs:

- Surround
    
- Encircle
    
- Look all around
    
- Touch (including corners)
    
- Ring / halo
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Build the offsets|all 8 directions|`product((-1,0,1), repeat=2)` minus `(0,0)`|
|Compose from parts|4-way + diagonals|`N4 + DIAG`|
|Apply offsets|candidate cells|`[(r+dr, c+dc) for dr, dc in N8]`|
|Bounds check|stay on the grid|`0 <= r < rows and 0 <= c < cols`|
|As a window|3×3 block|`[row[c-1:c+2] for row in m[r-1:r+2]]`|
|Block sum|neighborhood total|`sum(map(sum, block)) - m[r][c]`|
|Count matching|live neighbors|`sum(...)` over a generator|
|Padded grid|no bounds check|one sentinel ring, then plain slicing|
|Wrap around|torus|`(r+dr) % rows`|
|Distance metric|Chebyshev|`max(abs(dr), abs(dc))`|

---

## Common Uses

- Conway's Game of Life and most cellular automata
    
- Minesweeper adjacency counts
    
- Image convolution, blurring, sharpening
    
- Edge detection (Sobel, Laplacian)
    
- Erosion and dilation (morphology)
    
- 8-way connected component labelling
    
- Pathfinding with diagonal movement
    
- Chess king moves
    
- Terrain and heightmap smoothing
    

---

## Hidden Interview Problems

- Game of Life (in place, one pass)
    
- Minesweeper reveal / adjacent mine counts
    
- Number of Islands with diagonal connectivity
    
- Shortest Path in Binary Matrix (8-way BFS)
    
- Max sum of a 3×3 block
    
- Image smoothing (average of surrounding cells)
    
- Count cells surrounded entirely by ones
    
- Detect local maxima in a heightmap
    

---

## Recognition Clues

If you hear...

- "surrounding cells..."
    
- "including diagonals..."
    
- "all eight directions..."
    
- "the 3×3 around it..."
    
- "adjacent mines..."
    
- "a king may move..."
    
- "neighbouring pixels..."
    

...think **8-Neighborhood**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Unit|One cell + its 3×3 surroundings|
|Neighbor count|8 interior, 5 edge, 3 corner|
|Distance metric|Chebyshev (`max(abs(dr), abs(dc)) == 1`)|
|Symmetry|Mutual — if A sees B, B sees A|
|Time Complexity|O(1) per cell, O(rows × cols) per sweep|
|Space Complexity|O(1) extra (O(cells) for a full sweep copy)|
|Common Domains|Images, automata, games, terrain|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from itertools import product

m = [[1,  2,  3,  4],
     [5,  6,  7,  8],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

rows, cols = len(m), len(m[0])

# ============================================
# The offset table — don't type eight tuples, generate them

N8 = tuple((dr, dc) for dr, dc in product((-1, 0, 1), repeat=2)
           if (dr, dc) != (0, 0))

N8
# => ((-1,-1), (-1,0), (-1,1),
#     ( 0,-1),         ( 0,1),
#     ( 1,-1), ( 1,0), ( 1,1))
#
# note the shape: reading order around the center

# ============================================
# Or compose it from the parts you already know

N4   = ((-1, 0), (1, 0), (0, -1), (0, 1))
DIAG = ((-1, -1), (-1, 1), (1, -1), (1, 1))

set(N4 + DIAG) == set(N8)           # => True

# ============================================
# Same three moves as lesson 9 — only the table changed

def in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols

def neighbors8(r, c, rows, cols):
    return [(r + dr, c + dc) for dr, dc in N8
            if in_bounds(r + dr, c + dc, rows, cols)]

neighbors8(1, 1, rows, cols)
# => [(0,0), (0,1), (0,2), (1,0), (1,2), (2,0), (2,1), (2,2)]

# ============================================
# Corners and edges lose more neighbors than in 4-way

len(neighbors8(1, 1, rows, cols))   # => 8   interior
len(neighbors8(0, 1, rows, cols))   # => 5   edge
len(neighbors8(0, 0, rows, cols))   # => 3   corner

neighbors8(0, 0, rows, cols)        # => [(0,1), (1,0), (1,1)]

# ============================================
# Neighbor values

[m[r][c] for r, c in neighbors8(1, 1, rows, cols)]
# => [1, 2, 3, 5, 7, 9, 10, 11]

sum(m[r][c] for r, c in neighbors8(1, 1, rows, cols))   # => 48

# ============================================
# The OTHER model: a 3x3 window
#
# Slicing takes the block directly — no offset loop.
# max(0, ...) is mandatory: c-1 == -1 would slice from
# the far end of the row instead of clamping.

def block3(m, r, c):
    return [row[max(0, c - 1):c + 2] for row in m[max(0, r - 1):r + 2]]

block3(m, 1, 1)
# =>
# [[1, 2, 3],
#  [5, 6, 7],
#  [9, 10, 11]]

block3(m, 0, 0)
# =>
# [[1, 2],
#  [5, 6]]      the block clips at the border

# ============================================
# Neighborhood sum via the window
#
# Sum the block, subtract the center. One line, no bounds
# logic, and it is how you would write a convolution.

def around(m, r, c):
    return sum(map(sum, block3(m, r, c))) - m[r][c]

around(m, 1, 1)                     # => 48   matches the offset version

# ============================================
# Padding makes the window uniform
#
# With one sentinel ring every real cell has a full 3x3.

def pad(m, fill=0):
    width = len(m[0]) + 2
    return ([[fill] * width]
            + [[fill, *row, fill] for row in m]
            + [[fill] * width])

p = pad(m)

# real (0,0) lives at (1,1) and now has 8 neighbors, 5 of them 0
[row[0:3] for row in p[0:3]]
# =>
# [[0, 0, 0],
#  [0, 1, 2],
#  [0, 5, 6]]

# ============================================
# Count neighbors satisfying a predicate

grid = [[0, 1, 0],
        [1, 1, 0],
        [0, 0, 1]]

def count8(g, r, c, value=1):
    return sum(g[nr][nc] == value
               for nr, nc in neighbors8(r, c, len(g), len(g[0])))

count8(grid, 1, 1)                  # => 3
count8(grid, 0, 0)                  # => 3

[[count8(grid, r, c) for c in range(3)] for r in range(3)]
# =>
# [[3, 2, 2],
#  [2, 3, 3],
#  [2, 3, 1]]
#
# compare with the 4-way map in lesson 9 — every count
# here is >= the 4-way one, never smaller

# ============================================
# Minesweeper — the canonical Moore problem

mines = [[0, 1, 0],
         [0, 0, 0],
         [1, 0, 1]]

def minefield(mines):
    rows, cols = len(mines), len(mines[0])
    def cell(r, c):
        if mines[r][c]:
            return "*"
        return str(sum(mines[nr][nc]
                       for nr, nc in neighbors8(r, c, rows, cols)))
    return [[cell(r, c) for c in range(cols)] for r in range(rows)]

print("\n".join("".join(row) for row in minefield(mines)))
# 1*1
# 232
# *2*

# ============================================
# Game of Life — the whole rule in two lines
#
#   born   : dead cell with exactly 3 live neighbors
#   survive: live cell with 2 or 3 live neighbors

def life_step(g):
    rows, cols = len(g), len(g[0])
    def live(r, c):
        return sum(g[nr][nc] for nr, nc in neighbors8(r, c, rows, cols))
    return [[int(live(r, c) == 3 or (g[r][c] and live(r, c) == 2))
             for c in range(cols)]
            for r in range(rows)]

blinker = [[0, 0, 0],
           [1, 1, 1],
           [0, 0, 0]]

life_step(blinker)
# =>
# [[0, 1, 0],
#  [0, 1, 0],
#  [0, 1, 0]]

life_step(life_step(blinker)) == blinker    # => True, period 2

# note: a NEW grid is built. Reading and writing the same
# grid in one pass is the classic Game of Life bug.

# ============================================
# Smoothing / box blur — the 3x3 mean

def blur(m):
    rows, cols = len(m), len(m[0])
    def mean(r, c):
        block = block3(m, r, c)
        cells = [x for row in block for x in row]
        return sum(cells) // len(cells)
    return [[mean(r, c) for c in range(cols)] for r in range(rows)]

blur(m)
# =>
# [[3,  4,  5,  5 ],
#  [5,  6,  7,  7 ],
#  [9,  10, 11, 11],
#  [11, 12, 13, 13]]
#
# this is a 3x3 convolution with a uniform kernel — see lesson 15.
# Note the result is pulled DOWN near the right and bottom:
# those blocks are clipped, so they average fewer, smaller
# values. Border handling is a real decision, not a detail —
# pad with zeros, clamp to the edge, or wrap.

# ============================================
# Local maximum over the full 3x3

def is_peak(m, r, c):
    return all(m[r][c] > m[nr][nc]
               for nr, nc in neighbors8(r, c, len(m), len(m[0])))

is_peak(m, 3, 3)                    # => True   (16 is the corner max)
is_peak(m, 1, 1)                    # => False

# ============================================
# Diagonal connectivity changes the answer
#
# The same grid has 3 regions under 4-way rules and
# 1 region under 8-way rules.

from collections import deque

def regions(grid, neighbors):
    rows, cols = len(grid), len(grid[0])
    seen, count = set(), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 1 or (r, c) in seen:
                continue
            count += 1
            queue = deque([(r, c)])
            seen.add((r, c))
            while queue:
                cr, cc = queue.popleft()
                for nb in neighbors(cr, cc, rows, cols):
                    if grid[nb[0]][nb[1]] == 1 and nb not in seen:
                        seen.add(nb)
                        queue.append(nb)
    return count

def neighbors4(r, c, rows, cols):
    return [(r + dr, c + dc) for dr, dc in N4
            if in_bounds(r + dr, c + dc, rows, cols)]

staircase = [[1, 0, 0],
             [0, 1, 0],
             [0, 0, 1]]

regions(staircase, neighbors4)      # => 3
regions(staircase, neighbors8)      # => 1
#
# same algorithm, same data, different neighborhood.
# This is the entire point of isolating the pattern.

# ============================================
# Chebyshev distance — what "8-neighborhood" means formally

def chebyshev(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

all(chebyshev((1, 1), nb) == 1 for nb in neighbors8(1, 1, rows, cols))  # => True

# a king moves to every cell at Chebyshev distance 1

# ============================================
# Wrap around (torus) — every cell gets all 8

def neighbors8_wrap(r, c, rows, cols):
    return [((r + dr) % rows, (c + dc) % cols) for dr, dc in N8]

len(neighbors8_wrap(0, 0, rows, cols))      # => 8

# ============================================
# Compare

# edge-adjacent only        -> Von Neumann (lesson 9)
[(r + dr, c + dc) for dr, dc in N4]

# edge or corner            -> this lesson
[(r + dr, c + dc) for dr, dc in N8]

# the 3x3 block itself      -> a window (lessons 12-15)
[row[c-1:c+2] for row in m[r-1:r+2]]

# any distance R            -> Radius (lesson 11)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the eight directions|`product((-1,0,1), repeat=2)` minus `(0,0)`|
|to build them from parts|`N4 + DIAG`|
|the 3×3 block|`[row[c-1:c+2] for row in m[r-1:r+2]]`|
|the block, safely|clamp with `max(0, c-1)` or pad the grid|
|the neighborhood sum|`sum(map(sum, block)) - m[r][c]`|
|live-neighbor count|`sum(g[nr][nc] for nr, nc in neighbors8(...))`|
|"is it adjacent"|`max(abs(dr), abs(dc)) == 1`|
|diagonal connectivity|swap `neighbors4` → `neighbors8`|

---

## Key Insight

**Moore is Von Neumann plus the diagonals — and every function you wrote in lesson 9 works unchanged.** The offset table is the only thing that differs, which is precisely why the neighborhood belongs in its own function: `regions(grid, neighbors4)` and `regions(grid, neighbors8)` are the same algorithm answering different questions.

The second insight is the one that carries forward:

```text
8-neighborhood  ==  3x3 block  -  center
```

Once you see the neighborhood as a **window**, slicing replaces the offset loop, `sum(map(sum, block))` replaces the guarded generator, and the step to convolution is no step at all — a blur is this block with weights.

Two Python traps live here:

- `m[r-1:r+2]` with `r == 0` slices from `-1`, giving you the **last** row. Clamp with `max(0, r-1)` or pad the grid.
    
- In Game of Life, build a **new** grid. Mutating in place makes later cells read already-updated neighbors.
    

---

## Von Neumann vs Moore

|Pattern|Neighbors|Metric|Typical Home|
|---|---|---|---|
|**4-Neighborhood**|4|Manhattan|mazes, flood fill, grid BFS|
|**8-Neighborhood**|8|Chebyshev|automata, images, king moves|

```text
Von Neumann          Moore
   . N .             D N D
   W · E             W · E
   . S .             D S D
```

> **Mental shift:** Von Neumann asks *"can I step there?"*. Moore asks *"what is around me?"* — and "around me" is a 3×3 window, which is why Moore leads into windows and convolution while Von Neumann leads into graphs and paths.
