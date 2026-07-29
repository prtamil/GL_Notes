# 26. Flood Fill

## Mental Model

The paint bucket. Click a cell; every cell of the **same colour** reachable from it becomes the new colour. Everything else is untouched.

```text
seed = (1, 1), new = 2

[[1, 1, 1],          [[2, 2, 2],
 [1, 1, 0],    ->     [2, 2, 0],
 [1, 0, 1]]           [2, 0, 1]]

                      the lone 1 at (2,2) survives —
                      it is not reachable without
                      crossing a 0
```

Where lesson 25 partitions the *whole grid*, this expands **one region from one seed**. That difference — global sweep versus local expansion — is the entire distinction between the two lessons, and it is why lesson 25 is literally this function in a loop.

The mechanics are the same graph search as lesson 25, with two additions that only matter here:

- **A colour you are replacing.** The frontier is defined by "still equal to the *old* colour", which is a moving target because you are overwriting it as you go.
    
- **The `old == new` guard.** If the new colour equals the old one, the marking step stops marking anything, cells are re-enqueued forever, and the loop never terminates. It is the classic bug in this pattern, and it costs one line to prevent.
    

---

## Relationship to Cognitive Verb

```text
Spread
   ↓
Flood Fill
```

Related verbs:

- Spread
- Paint / fill
- Propagate
- Infect
- Pour outward

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Fill from a seed|the whole thing|`deque` + replace matching neighbours|
|The guard|avoid an infinite loop|`if old == new: return`|
|DFS variant|stack instead of queue|`list` + `.pop()`|
|Copy vs in place|non-destructive|`[row[:] for row in g]`|
|Neighborhood|4-way or 8-way|`N4` / `N8` (lessons 9-10)|
|Region size|count, don't paint|`seen` set, return `len(seen)`|
|Scanline fill|fewer stack pushes|fill whole row spans at a time|
|Boundary fill|stop at a border colour|test `!= border` instead of `== old`|
|Multi-source|several seeds at once|seed the queue with all of them|
|Mark visited|no colour to overwrite|a `seen` set, as in lesson 25|

---

## Common Uses

- Paint bucket in image editors
- Minesweeper's empty-area reveal
- Selecting a region by colour ("magic wand")
- Filling enclosed areas in vector art
- Territory capture in Go / Reversi
- Water and lava spreading in games
- Detecting enclosed regions
- Removing a background colour
- Map region colouring

---

## Hidden Interview Problems

- Flood Fill (LeetCode 733)
- Number of Islands (as the inner step)
- Surrounded Regions (LeetCode 130)
- Max Area of Island
- Pacific Atlantic Water Flow
- Rotting Oranges (multi-source)
- Number of Enclaves
- Colouring a border

---

## Recognition Clues

If you hear...

- "paint bucket / fill tool..."
- "replace the connected region..."
- "starting from this cell..."
- "spread outward until..."
- "reveal the empty area..."
- "everything reachable from the seed..."

...think **Flood Fill**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D, treated as a graph|
|Question|What is connected to *this* cell, and repaint it|
|Input|A grid, a seed, a new value|
|Edges|Defined by the neighborhood (4-way or 8-way)|
|Engine|BFS, DFS, or scanline|
|Termination guard|`old == new` must return early|
|Time Complexity|O(rows × cols) worst case|
|Space Complexity|O(rows × cols) for the frontier|
|Common Domains|Graphics, games, image editing|

---

## Python Recipe Book

```python
# ============================================
# Setup

from collections import deque

N4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
N8 = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
           if (dr, dc) != (0, 0))

def nbrs(r, c, rows, cols, dirs=N4):
    return [(r + dr, c + dc) for dr, dc in dirs
            if 0 <= r + dr < rows and 0 <= c + dc < cols]

img = [[1, 1, 1],
       [1, 1, 0],
       [1, 0, 1]]

# ============================================
# The one idiom to remember
#
# Read the seed's colour, then spread to every
# neighbour that still has it — repainting as you go.
# The repaint IS the visited-marker: an already-filled
# cell no longer equals `old`, so it is never re-queued.

def flood_fill(g, seed, new, dirs=N4):
    rows, cols = len(g), len(g[0])
    out = [row[:] for row in g]             # don't mutate the caller's grid
    sr, sc = seed
    old = out[sr][sc]
    if old == new:                          # THE GUARD — see below
        return out
    q = deque([seed])
    out[sr][sc] = new
    while q:
        r, c = q.popleft()
        for nr, nc in nbrs(r, c, rows, cols, dirs):
            if out[nr][nc] == old:
                out[nr][nc] = new           # paint on ENQUEUE
                q.append((nr, nc))
    return out

flood_fill(img, (1, 1), 2)
# =>
# [[2, 2, 2],
#  [2, 2, 0],
#  [2, 0, 1]]

flood_fill(img, (0, 0), 2)          # same region, different seed
# =>
# [[2, 2, 2],
#  [2, 2, 0],
#  [2, 0, 1]]                       identical result

flood_fill(img, (2, 2), 3)          # the isolated cell
# =>
# [[1, 1, 1],
#  [1, 1, 0],
#  [1, 0, 3]]                       only itself

# ============================================
# THE GUARD — why `old == new` must return early
#
# Painting a cell is what marks it visited. If new == old,
# painting changes nothing, so `out[nr][nc] == old` stays
# true forever and neighbours re-enqueue each other
# without end. The loop does not terminate.

flood_fill(img, (1, 1), 1) == img   # => True, and it RETURNS
#
# delete the guard and this call hangs. It is the single
# most common bug in LeetCode 733.

# ============================================
# Connectivity changes what "connected" means

diag = [[1, 0, 1],
        [0, 1, 0],
        [1, 0, 1]]

flood_fill(diag, (1, 1), 2)         # 4-way
# =>
# [[1, 0, 1],
#  [0, 2, 0],
#  [1, 0, 1]]      the centre is alone

flood_fill(diag, (1, 1), 2, N8)     # 8-way
# =>
# [[2, 0, 2],
#  [0, 2, 0],
#  [2, 0, 2]]      the whole X is one region
#
# same grid, same seed, one argument — 1 cell or 5.

# ============================================
# Measure without painting
#
# When you want the AREA, not a recoloured grid, use a
# `seen` set instead of overwriting. This also works
# when there is no colour to write (read-only input).

def fill_size(g, seed, dirs=N4):
    rows, cols = len(g), len(g[0])
    sr, sc = seed
    old = g[sr][sc]
    seen, q = {seed}, deque([seed])
    while q:
        r, c = q.popleft()
        for nb in nbrs(r, c, rows, cols, dirs):
            if g[nb[0]][nb[1]] == old and nb not in seen:
                seen.add(nb)
                q.append(nb)
    return len(seen)

fill_size(img, (1, 1))              # => 6
fill_size(img, (2, 2))              # => 1
fill_size(diag, (1, 1))             # => 1
fill_size(diag, (1, 1), N8)         # => 5
#
# no guard needed here — the `seen` set does the marking,
# so there is no colour to collide with.

# ============================================
# DFS instead of BFS

def flood_fill_dfs(g, seed, new, dirs=N4):
    rows, cols = len(g), len(g[0])
    out = [row[:] for row in g]
    sr, sc = seed
    old = out[sr][sc]
    if old == new:
        return out
    stack = [seed]
    out[sr][sc] = new
    while stack:
        r, c = stack.pop()                  # <- the only change
        for nr, nc in nbrs(r, c, rows, cols, dirs):
            if out[nr][nc] == old:
                out[nr][nc] = new
                stack.append((nr, nc))
    return out

flood_fill_dfs(img, (1, 1), 2) == flood_fill(img, (1, 1), 2)    # => True
#
# identical result, different visit order. And note this
# is ITERATIVE — a recursive flood fill dies on a large
# region (Python's recursion limit is 1000; a 100x100
# region is 10,000 cells).

# ============================================
# Scanline fill — the version graphics code uses
#
# Instead of pushing one cell at a time, fill a whole
# horizontal RUN, then push only the rows above and
# below it. Far fewer stack operations on wide regions.

def flood_fill_scanline(g, seed, new):
    rows, cols = len(g), len(g[0])
    out = [row[:] for row in g]
    sr, sc = seed
    old = out[sr][sc]
    if old == new:
        return out
    stack = [seed]
    while stack:
        r, c = stack.pop()
        if out[r][c] != old:
            continue                        # already filled by a run
        left = c
        while left > 0 and out[r][left - 1] == old:
            left -= 1
        right = c
        while right < cols - 1 and out[r][right + 1] == old:
            right += 1
        for x in range(left, right + 1):    # paint the whole run
            out[r][x] = new
        for nr in (r - 1, r + 1):           # seed the rows either side
            if 0 <= nr < rows:
                for x in range(left, right + 1):
                    if out[nr][x] == old:
                        stack.append((nr, x))
    return out

big = [[1, 1, 1, 1, 0],
       [1, 0, 0, 1, 1],
       [1, 1, 0, 0, 1],
       [0, 1, 1, 1, 1]]

flood_fill_scanline(big, (0, 0), 9)
# =>
# [[9, 9, 9, 9, 0],
#  [9, 0, 0, 9, 9],
#  [9, 9, 0, 0, 9],
#  [0, 9, 9, 9, 9]]

flood_fill_scanline(big, (0, 0), 9) == flood_fill(big, (0, 0), 9)   # => True
flood_fill_scanline(img, (1, 1), 2) == flood_fill(img, (1, 1), 2)   # => True
#
# same answer, and 4-connected only — the run-based
# structure assumes horizontal adjacency, so there is no
# 8-way version of this optimisation.

# ============================================
# Boundary fill — the other question
#
# Flood fill asks "is this cell still the OLD colour?".
# Boundary fill asks "is this cell NOT the border?" —
# it pours into a region of mixed colours and stops only
# at a wall. This is how a paint bucket fills an outlined
# shape whose interior is not uniform.

def boundary_fill(g, seed, new, border):
    rows, cols = len(g), len(g[0])
    out = [row[:] for row in g]
    q, seen = deque([seed]), {seed}
    while q:
        r, c = q.popleft()
        if out[r][c] == border or out[r][c] == new:
            continue
        out[r][c] = new
        for nb in nbrs(r, c, rows, cols):
            if nb not in seen and out[nb[0]][nb[1]] != border:
                seen.add(nb)
                q.append(nb)
    return out

room = [[8, 8, 8, 8, 8],
        [8, 0, 0, 0, 8],
        [8, 0, 8, 0, 8],
        [8, 0, 0, 0, 8],
        [8, 8, 8, 8, 8]]

boundary_fill(room, (1, 1), 5, border=8)
# =>
# [[8, 8, 8, 8, 8],
#  [8, 5, 5, 5, 8],
#  [8, 5, 8, 5, 8],
#  [8, 5, 5, 5, 8],
#  [8, 8, 8, 8, 8]]
#
# the interior pillar at (2,2) is border-coloured, so
# the fill flows around it and leaves it standing

# ============================================
# Multi-source — seed the queue with everything
#
# One change: start with many cells in the queue instead
# of one. This is "Rotting Oranges", fire spread, and
# multi-source distance maps (lesson 11).

def flood_multi(g, seeds, new, dirs=N4):
    rows, cols = len(g), len(g[0])
    out = [row[:] for row in g]
    q = deque()
    for sr, sc in seeds:
        if out[sr][sc] != new:
            olds = out[sr][sc]
            out[sr][sc] = new
            q.append(((sr, sc), olds))
    while q:
        (r, c), old = q.popleft()
        for nr, nc in nbrs(r, c, rows, cols, dirs):
            if out[nr][nc] == old:
                out[nr][nc] = new
                q.append(((nr, nc), old))
    return out

flood_multi(img, [(0, 0), (2, 2)], 7)
# =>
# [[7, 7, 7],
#  [7, 7, 0],
#  [7, 0, 7]]
#
# both regions filled in one pass

# ============================================
# Compare

# where is ONE cell        -> lesson 24    no neighborhood needed
# ONE region from a seed   -> this lesson  local expansion
# ALL regions at once      -> lesson 25    this, in a loop

def count_components(g):
    work, n = [row[:] for row in g], 0
    for r in range(len(work)):
        for c in range(len(work[0])):
            if work[r][c] == 1:
                n += 1
                work = flood_fill(work, (r, c), -n)
    return n
#
# verified: on lesson 25's grid this returns 5, matching
# len(components(g)). Lesson 25 is this function's body
# with a shared `seen` set instead of repainting.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|flood fill|`deque`, repaint neighbours still equal to `old`|
|**not to hang**|`if old == new: return` — the guard|
|the visited marker|the repaint itself|
|the area, not the paint|a `seen` set, return `len(seen)`|
|diagonal spread|pass `N8`|
|speed on wide regions|scanline — fill runs, push rows|
|to stop at a wall|boundary fill: test `!= border`|
|many seeds|put them all in the queue first|
|**not** recursion|10,000 cells vs a 1,000-frame limit|

---

## Key Insight

**In flood fill, the repaint *is* the visited-marker.** That is the elegant part and the dangerous part at once. You do not need a separate `seen` set, because a cell that has been painted no longer matches `old` and can never be enqueued again.

Which is exactly why the guard is mandatory:

```python
if old == new:
    return out
```

When the new colour equals the old one, painting marks nothing, `out[nr][nc] == old` stays true forever, and neighbours re-enqueue each other without end. One line, and it is the difference between a correct function and a hang.

Three more things worth carrying:

1. **Iterative, always.** A recursive flood fill is the prettiest version and it dies on real input — 10,000 cells in a 100×100 region against Python's 1,000-frame recursion limit.
    
2. **Connectivity is a modelling decision, not a detail.** On the X-shaped grid, the same seed fills 1 cell with `N4` and 5 with `N8`.
    
3. **Fill versus measure are different functions.** If you want the area, use a `seen` set and never touch the grid — that version needs no guard and works on read-only input.
    

And the relationship that closes the section: **lesson 25 is this function in a loop.** Sweep every cell, flood from each one not yet claimed, and you have every component. A local operation plus an outer scan that guarantees coverage — the same pairing as boundary and spiral back in lesson 8.

---

## The Search Section Complete

|Lesson|Question|Starts from|Explores|Answer|
|---|---|---|---|---|
|24 Find Cell|*Where is it?*|the whole grid|until the first hit|one coordinate|
|25 Connected Components|*How many groups?*|every cell|**all** regions|a partition|
|26 Flood Fill|*What connects here?*|one seed|**one** region|that region|

```text
                       ┌── 24  bag of cells    (no adjacency)
  search the grid  ────┤
                       └── 25, 26  a graph     (adjacency is everything)
                              │
                              ├── 26  expand from a seed      (the primitive)
                              └── 25  = 26 at every cell      (the sweep)
```

> **Mental shift:** lesson 24 treats the matrix as a container and asks *where*. Lessons 25 and 26 treat it as a graph and ask *what reaches what* — which is why they both reduce to BFS the moment you have `neighbors4` from lesson 9. Search, in a grid, is nearly always graph search wearing a coordinate system.
