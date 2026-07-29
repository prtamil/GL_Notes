# 25. Connected Components

## Mental Model

Lesson 24 found *one cell*. This one finds **every group of cells that touch each other**, and reports the whole partition.

```text
[[1, 1, 0, 0, 1],          [[1, 1, 0, 0, 2],
 [1, 0, 0, 1, 1],           [1, 0, 0, 2, 2],
 [0, 0, 1, 0, 0],   ->      [0, 0, 3, 0, 0],
 [1, 1, 0, 0, 1]]           [4, 4, 0, 0, 5]]

    the grid                 five components, labelled
```

The move that makes this tractable is the one from lesson 9:

> **A neighborhood function turns a matrix into a graph.**

Once `neighbors4(r, c)` exists, "connected component" stops being a grid problem and becomes the standard graph problem. The algorithm is three lines of idea:

```text
for every unvisited cell that qualifies:
    flood outward from it, marking everything reachable
    that reach-set is one component
```

Two decisions produce all the variants, and neither is about the algorithm:

- **Which neighborhood?** 4-connectivity and 8-connectivity give *different answers on the same grid* — the example above has 5 components under `N4` and 3 under `N8`.
    
- **What counts as "same"?** Equal to a target value (islands), or merely equal to each other (colour regions).
    

---

## Relationship to Cognitive Verb

```text
Group
   ↓
Connected Components
```

Related verbs:

- Group
- Cluster
- Partition into regions
- Label
- Segment

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|The outer loop|every unvisited cell|nested `range` + a `seen` set|
|Flood outward|one component|`collections.deque` (BFS)|
|Same, stack|DFS|a plain `list` with `.pop()`|
|Visited set|avoid re-visiting|`set` of `(r, c)` tuples|
|Neighborhood|the graph edges|`neighbors4` / `neighbors8` (lessons 9-10)|
|Count only|how many regions|`len(components(g))`|
|Label map|component id per cell|write the index back into a grid|
|Sizes|area of each|`len(comp)`, or `Counter` on the labels|
|Largest|biggest region|`max(comps, key=len)`|
|Alternative engine|merge as you go|union-find (disjoint set)|
|Region perimeter|border length|count neighbours outside the component|

---

## Common Uses

- Counting islands on a map
- Image segmentation and blob detection
- Finding contiguous regions of colour
- Detecting clusters in a grid of sensors
- Minesweeper's empty-area reveal
- Level design: reachable areas of a map
- Checking a maze is fully connected
- Counting enclosed rooms
- Percolation and connectivity analysis

---

## Hidden Interview Problems

- Number of Islands (LeetCode 200)
- Max Area of Island (LeetCode 695)
- Number of Distinct Islands
- Surrounded Regions (LeetCode 130)
- Island Perimeter (LeetCode 463)
- Number of Closed Islands
- Count Sub Islands
- Making a Large Island
- Number of Provinces

---

## Recognition Clues

If you hear...

- "how many islands / groups / regions..."
- "connected cells..."
- "clusters of..."
- "the largest contiguous area..."
- "label each region..."
- "are all the cells reachable from each other..."

...think **Connected Components**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D, treated as a graph|
|Question|What is the partition into connected groups?|
|Edges|Defined by the neighborhood (4-way or 8-way)|
|Engine|BFS, DFS, or union-find|
|Answer|A list of components, or a label per cell|
|Time Complexity|O(rows × cols) — every cell enqueued once|
|Space Complexity|O(rows × cols) for `seen` and the queue|
|Key invariant|Mark cells **when enqueued**, not when dequeued|
|Common Domains|Images, maps, games, clustering|

---

## Python Recipe Book

```python
# ============================================
# Setup — the neighborhood is the graph

from collections import deque, Counter

N4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
N8 = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
           if (dr, dc) != (0, 0))

def nbrs(r, c, rows, cols, dirs=N4):
    return [(r + dr, c + dc) for dr, dc in dirs
            if 0 <= r + dr < rows and 0 <= c + dc < cols]

g = [[1, 1, 0, 0, 1],
     [1, 0, 0, 1, 1],
     [0, 0, 1, 0, 0],
     [1, 1, 0, 0, 1]]

# ============================================
# The one idiom to remember
#
#   outer loop over every cell
#   + BFS from each unvisited qualifying cell
#   + a shared `seen` set across the whole run
#
# The shared `seen` is what makes it O(cells) instead of
# O(cells^2): each cell is enqueued exactly once, ever.

def components(g, dirs=N4, target=1):
    rows, cols = len(g), len(g[0])
    seen, out = set(), []
    for r in range(rows):
        for c in range(cols):
            if g[r][c] != target or (r, c) in seen:
                continue
            comp, q = [], deque([(r, c)])
            seen.add((r, c))                    # mark on ENQUEUE
            while q:
                cr, cc = q.popleft()
                comp.append((cr, cc))
                for nb in nbrs(cr, cc, rows, cols, dirs):
                    if g[nb[0]][nb[1]] == target and nb not in seen:
                        seen.add(nb)            # ...here too
                        q.append(nb)
            out.append(comp)
    return out

comps = components(g)

len(comps)                          # => 5
# [(0,0), (1,0), (0,1)]
# [(0,4), (1,4), (1,3)]
# [(2,2)]
# [(3,0), (3,1)]
# [(3,4)]

[len(x) for x in comps]             # => [3, 3, 1, 2, 1]
max(len(x) for x in comps)          # => 3
max(comps, key=len)                 # => [(0,0), (1,0), (0,1)]

# ============================================
# THE bug: marking on dequeue instead of enqueue
#
# If you only add to `seen` when you pop, a cell can be
# pushed by several neighbours before it is processed.
# The queue fills with duplicates and the work becomes
# exponential in the worst case. Mark it the moment you
# push it.

# ============================================
# Connectivity changes the answer

len(components(g, N4))              # => 5
len(components(g, N8))              # => 3

[sorted(x) for x in components(g, N8)]
# => [[(0,0), (0,1), (1,0)],
#     [(0,4), (1,3), (1,4), (2,2), (3,0), (3,1)],
#     [(3,4)]]
#
# under 8-connectivity the lone cell at (2,2) bridges
# three separate 4-components into one. Same grid, same
# algorithm, one argument — and the count drops from 5
# to 3. Always state which connectivity a problem means.

# ============================================
# The label map — a component id per cell
#
# Often more useful than the list of lists: it is a
# matrix again, so every earlier lesson applies to it.

def label(g, dirs=N4, target=1):
    rows, cols = len(g), len(g[0])
    lab = [[0] * cols for _ in range(rows)]
    for i, comp in enumerate(components(g, dirs, target), start=1):
        for r, c in comp:
            lab[r][c] = i
    return lab

label(g)
# =>
# [[1, 1, 0, 0, 2],
#  [1, 0, 0, 2, 2],
#  [0, 0, 3, 0, 0],
#  [4, 4, 0, 0, 5]]

label(g, N8)
# =>
# [[1, 1, 0, 0, 2],
#  [1, 0, 0, 2, 2],
#  [0, 0, 2, 0, 0],
#  [2, 2, 0, 0, 3]]

Counter(x for row in label(g) for x in row if x)
# => Counter({1: 3, 2: 3, 4: 2, 3: 1, 5: 1})
#
# the label map turns "size of each component" into a
# one-line Counter

# ============================================
# DFS instead of BFS — one word different
#
# deque + popleft() -> BFS (breadth first)
# list  + pop()     -> DFS (depth first)
#
# For components it makes NO difference to the answer,
# only to the visit order. Use BFS when you also want
# distances; use DFS when you don't.

def components_dfs(g, dirs=N4, target=1):
    rows, cols = len(g), len(g[0])
    seen, out = set(), []
    for r in range(rows):
        for c in range(cols):
            if g[r][c] != target or (r, c) in seen:
                continue
            comp, stack = [], [(r, c)]
            seen.add((r, c))
            while stack:
                cr, cc = stack.pop()            # <- the only change
                comp.append((cr, cc))
                for nb in nbrs(cr, cc, rows, cols, dirs):
                    if g[nb[0]][nb[1]] == target and nb not in seen:
                        seen.add(nb)
                        stack.append(nb)
            out.append(comp)
    return out

len(components_dfs(g)) == len(comps)                        # => True
sorted(map(sorted, components_dfs(g))) == sorted(map(sorted, comps))
# => True

# ============================================
# Do NOT use recursive DFS on a large grid
#
# Python's default recursion limit is 1000. A single
# 100x100 region has 10,000 cells, so a recursive flood
# hits RecursionError long before it finishes.

import sys
sys.getrecursionlimit()             # => 1000
100 * 100                           # => 10000   cells in a small image
#
# the iterative stack above has no such limit. This is
# the single most common reason grid solutions that
# "work on the sample" crash on the real input.

# ============================================
# Union-find — the other engine
#
# Instead of exploring outward, union every adjacent
# pair and let the groups fall out. Worth knowing when
# edges arrive over time and you cannot flood.

def components_uf(g, dirs=N4, target=1):
    rows, cols = len(g), len(g[0])
    par = {(r, c): (r, c)
           for r in range(rows) for c in range(cols) if g[r][c] == target}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]                # path compression
            x = par[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            par[ra] = rb

    for (r, c) in list(par):
        for nb in nbrs(r, c, rows, cols, dirs):
            if nb in par:
                union((r, c), nb)

    groups = {}
    for k in par:
        groups.setdefault(find(k), []).append(k)
    return list(groups.values())

len(components_uf(g))                                       # => 5
sorted(map(sorted, components_uf(g))) == sorted(map(sorted, comps))
# => True
#
# same answer. BFS is simpler and faster for a static
# grid; union-find wins when cells are ADDED over time
# ("Making a Large Island", dynamic connectivity).

# ============================================
# Regions of equal value, not of a target value
#
# Drop the `target` and compare each cell to its own
# region's value. Now every cell belongs to exactly one
# region and the whole grid is partitioned.

col = [[1, 1, 2],
       [1, 2, 2],
       [3, 3, 2]]

def regions_by_value(g, dirs=N4):
    rows, cols = len(g), len(g[0])
    seen, out = set(), []
    for r in range(rows):
        for c in range(cols):
            if (r, c) in seen:
                continue
            v = g[r][c]
            comp, q = [], deque([(r, c)])
            seen.add((r, c))
            while q:
                cr, cc = q.popleft()
                comp.append((cr, cc))
                for nb in nbrs(cr, cc, rows, cols, dirs):
                    if g[nb[0]][nb[1]] == v and nb not in seen:
                        seen.add(nb)
                        q.append(nb)
            out.append((v, comp))
    return out

[(v, sorted(cc)) for v, cc in regions_by_value(col)]
# => [(1, [(0,0), (0,1), (1,0)]),
#     (2, [(0,2), (1,1), (1,2), (2,2)]),
#     (3, [(2,0), (2,1)])]

len(regions_by_value(col))          # => 3
#
# this is image segmentation in twenty lines

# ============================================
# Perimeter of a component
#
# Count the neighbour slots that leave the component —
# either off the grid, or onto a different value.

def perimeter(g, comp):
    rows, cols = len(g), len(g[0])
    cells, p = set(comp), 0
    for r, c in comp:
        for dr, dc in N4:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) not in cells:
                p += 1
    return p

[perimeter(g, x) for x in comps]    # => [8, 8, 4, 6, 4]
#
# a single isolated cell has perimeter 4; each internal
# adjacency removes 2. Perimeter is always even.

# ============================================
# Compare

# where is ONE cell                -> lesson 24
next(((r,c) for r,row in enumerate(g) for c,v in enumerate(row) if v==1), None)

# ALL groups, at once              -> this lesson
components(g)

# ONE group, from a seed           -> lesson 26
# ...and lesson 26 in a loop IS this lesson:
#
#   for every unvisited cell:
#       flood_fill from it
#
# the outer double loop plus a shared `seen` is the
# only thing lesson 25 adds to lesson 26.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|all components|outer double loop + BFS + a **shared** `seen`|
|to avoid quadratic blowup|mark `seen` **on enqueue**, not on dequeue|
|BFS|`deque` + `popleft()`|
|DFS|`list` + `pop()`|
|**not** recursion|a 100×100 region blows the 1000-frame limit|
|diagonal connectivity|pass `N8` instead of `N4`|
|sizes|`Counter` over the label map|
|the biggest region|`max(comps, key=len)`|
|dynamic connectivity|union-find, not BFS|

---

## Key Insight

**Connected components is not a grid algorithm — it is the standard graph algorithm with `neighbors4` plugged in.** The grid contributes nothing but the edge list, which is why the same twenty lines solve islands, colour segmentation, cluster detection and reachability by changing one argument.

Three things carry the weight:

1. **The shared `seen` set across the whole run.** It is what makes the outer loop free: the double `for` visits every cell, but each cell is only ever *explored* once, so the total is O(rows × cols) rather than O(cells²).
    
2. **Mark on enqueue, not on dequeue.** A cell reachable from four neighbours will be pushed four times if you only mark it when popped. The queue bloats and the complexity degrades. This is the most common performance bug in the pattern.
    
3. **Iterative, not recursive.** Python's default recursion limit is 1000; a modest 100×100 region has 10,000 cells. Recursive flood fill passes the sample input and dies on the real one. Use `deque` or a list stack.
    

And the modelling point that changes answers rather than speed: **4-connectivity and 8-connectivity are different questions.** The worked grid has 5 components one way and 3 the other, because a single diagonal cell bridges three regions. When a problem says "connected", find out which one it means before writing code.

---

## Components vs Flood Fill

|Pattern|Starts from|Explores|Returns|
|---|---|---|---|
|**Connected Components**|every cell|**all** regions|a partition of the grid|
|**Flood Fill**|one seed|**one** region|the region containing the seed|

```text
Connected Components          Flood Fill

  ▣ ▣ · ▣                       ◉ ◉ · ·
  ▣ · · ▣    all groups          ◉ · · ·   one group,
  · ▣ ▣ ·    at once             · · · ·   from the seed
```

The relationship is literal — components is flood fill in a loop:

```python
def count_components(g):
    n = 0
    for r in range(len(g)):
        for c in range(len(g[0])):
            if g[r][c] == 1:
                n += 1
                g = flood_fill(g, (r, c), -n)   # lesson 26
    return n
```

Verified on the worked grid: `5`, the same as `len(components(g))`.

> **Mental shift:** lesson 26 is the primitive — *expand from here*. Lesson 25 is the sweep that applies it everywhere and never repeats itself. Exactly as lesson 5's spiral was lesson 8's boundary in a loop, this is that pairing again: a local operation, plus an outer scan that guarantees full coverage.
