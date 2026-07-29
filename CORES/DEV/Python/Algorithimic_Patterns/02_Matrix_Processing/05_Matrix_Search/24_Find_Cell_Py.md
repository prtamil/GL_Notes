# 24. Find Cell

## Mental Model

Every pattern so far processed the *whole* matrix. Search asks a narrower question:

> **Where is it?**

```text
[[1, 2, 3],
 [4, 5, 6],     find 5  ->  (1, 1)
 [7, 8, 9]]     find 99 ->  None
```

The answer is a **coordinate, or nothing** — and both halves of that matter. A search that finds nothing is the normal case, not an error, so the shape of the code is always *"return the position, or a sentinel."*

Three levels of search, distinguished entirely by what you know about the data:

|What you know|Cost|Technique|
|---|---|---|
|Nothing|O(rows × cols)|scan, stop at the first hit|
|Rows and columns sorted|O(rows + cols)|**staircase** from a corner|
|Fully sorted in row-major|O(log(rows × cols))|binary search on the flat index|

The unsorted scan is the one you write most; the staircase is the one interviews are about; the binary search is lesson 23's `divmod` doing real work.

And the Python detail that catches everyone: **there is no 2D `.index()`, and `x in m` does not mean what you want.** `5 in m` asks whether `5` is one of the *rows*.

---

## Relationship to Cognitive Verb

```text
Locate
   ↓
Find Cell
```

Related verbs:

- Locate
- Look up
- Search for
- Where is
- Detect presence

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|First match|stop early|`next(gen, None)`|
|All matches|every position|comprehension over `enumerate` × 2|
|Presence only|yes / no|`any(...)` over a generator|
|Universal test|all cells|`all(...)`|
|Count|how many|`sum(pred(v) for ...)`|
|Best cell|argmax / argmin|`max(positions, key=...)`|
|First per row|one answer per row|`next((c for c, v in enumerate(row) if ...), None)`|
|Sorted rows + columns|staircase|start at a corner, step in|
|Fully sorted|binary search|`divmod(mid, cols)`|
|Dict grid|value → position|invert the dict|

---

## Common Uses

- Locating the player, target or goal in a grid
- Finding an empty cell (Sudoku solvers, board games)
- Looking up a value in a sorted table
- Detecting whether a pattern is present
- Finding the brightest or darkest pixel
- Grid-based collision queries
- Locating the entry point of a maze
- Validating that a value exists before using it

---

## Hidden Interview Problems

- Search a 2D Matrix (LeetCode 74, fully sorted)
- Search a 2D Matrix II (LeetCode 240, staircase)
- Find the first empty cell
- Find all occurrences of a value
- Find the position of the maximum
- Find a peak element in a matrix
- Check if a matrix contains a value
- Kth smallest element in a sorted matrix

---

## Recognition Clues

If you hear...

- "find the position of..."
- "does the matrix contain..."
- "locate the first..."
- "search this sorted matrix..."
- "return the coordinates..."
- "return -1 if not found..."

...think **Find Cell**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Question|Where is a cell satisfying a predicate?|
|Answer|A coordinate, or a sentinel (`None` / `(-1,-1)`)|
|Unsorted|O(rows × cols), early exit on the first hit|
|Row+column sorted|O(rows + cols) staircase|
|Row-major sorted|O(log(rows × cols)) binary search|
|Space Complexity|O(1)|
|Common Domains|Games, tables, images, solvers|

---

## Python Recipe Book

```python
# ============================================
# Basic matrices

import bisect

m = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]

rows, cols = len(m), len(m[0])

# ============================================
# The one idiom to remember
#
#   next(generator, default)
#
# A generator is lazy, so it STOPS at the first match.
# The default is what makes "not found" a value rather
# than an exception.

def find(m, target):
    return next(((r, c) for r, row in enumerate(m)
                        for c, v in enumerate(row) if v == target), None)

find(m, 5)                          # => (1, 1)
find(m, 1)                          # => (0, 0)
find(m, 99)                         # => None
#
# without the `None`, `next()` raises StopIteration on a
# miss — almost never what you want.

# ============================================
# Predicates, not just equality
#
# Passing a function instead of a value costs nothing
# and covers every variant of the problem.

def find_by(m, pred):
    return next(((r, c) for r, row in enumerate(m)
                        for c, v in enumerate(row) if pred(v)), None)

find_by(m, lambda v: v % 2 == 0)    # => (0, 1)   first even
find_by(m, lambda v: v > 7)         # => (2, 1)   first over 7
find_by(m, lambda v: v == 0)        # => None     no empty cell

# ============================================
# All matches

def find_all(m, pred):
    return [(r, c) for r, row in enumerate(m)
                   for c, v in enumerate(row) if pred(v)]

find_all(m, lambda v: v % 2 == 0)   # => [(0,1), (1,0), (1,2), (2,1)]
len(find_all(m, lambda v: v % 2 == 0))              # => 4

# counting alone doesn't need the positions:
sum(v % 2 == 0 for row in m for v in row)           # => 4

# ============================================
# THE PYTHON TRAP: `in` searches rows, not cells

5 in m[1]                           # => True    5 is in row 1
5 in m                              # => False   5 is not a ROW

[row for row in [[1, 2], [3, 4]] if 3 in row]       # => [[3, 4]]
#
# `x in m` compares x against each ROW LIST. It is not
# an error and it is not what you meant. There is also
# no m.index(x) for a 2D list.
#
# the correct membership test:
any(v == 5 for row in m for v in row)               # => True

# ============================================
# Presence and universality

any(v > 8 for row in m for v in row)        # => True
all(v > 0 for row in m for v in row)        # => True
#
# both short-circuit — `any` stops at the first True,
# `all` at the first False. Same early exit as next().

# ============================================
# Best cell — argmax over positions
#
# max() on the values loses the location. Iterate
# positions and use key= to look the value up.

max(((r, c) for r in range(rows) for c in range(cols)),
    key=lambda p: m[p[0]][p[1]])            # => (2, 2)

min(((r, c) for r in range(rows) for c in range(cols)),
    key=lambda p: m[p[0]][p[1]])            # => (0, 0)

max(v for row in m for v in row)            # => 9   value only

# ============================================
# One answer per row

[next((c for c, v in enumerate(row) if v % 2 == 0), None) for row in m]
# => [1, 0, 1]
#
# the column of the first even number in each row

# ============================================
# SORTED: the staircase search
#
# When every row is sorted left-to-right AND every
# column top-to-bottom, start at the TOP-RIGHT corner.
# From there, each comparison eliminates a whole row or
# a whole column:
#
#   too big   -> everything below in this column is bigger  -> go left
#   too small -> everything left in this row is smaller     -> go down

sm = [[1,  4,  7,  11],
      [2,  5,  8,  12],
      [3,  6,  9,  16],
      [10, 13, 14, 17]]

def staircase(m, target):
    r, c = 0, len(m[0]) - 1             # top-right
    while r < len(m) and c >= 0:
        v = m[r][c]
        if v == target:
            return (r, c)
        if v > target:
            c -= 1                      # discard this column
        else:
            r += 1                      # discard this row
    return None

staircase(sm, 5)                    # => (1, 1)
staircase(sm, 16)                   # => (2, 3)
staircase(sm, 1)                    # => (0, 0)
staircase(sm, 17)                   # => (3, 3)
staircase(sm, 15)                   # => None

# the path it walks, for 5:
# [(0,3), (0,2), (0,1), (1,1)]      4 steps, not 16
#
# O(rows + cols). The bottom-left corner works too, with
# the comparisons swapped. The top-left and bottom-right
# corners DO NOT work — from those, both directions move
# the same way and no comparison eliminates anything.

# ============================================
# FULLY SORTED: binary search on the flat index
#
# If the matrix reads as one sorted sequence in
# row-major order, it IS a sorted list. Use lesson 23's
# divmod to convert the midpoint back to (r, c).

rm = [[1,  3,  5 ],
      [7,  9,  11],
      [13, 15, 17]]

def bsearch(m, target):
    rows, cols = len(m), len(m[0])
    lo, hi = 0, rows * cols - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        r, c = divmod(mid, cols)        # flat index -> coordinates
        v = m[r][c]
        if v == target:
            return (r, c)
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return None

bsearch(rm, 11)                     # => (1, 2)
bsearch(rm, 1)                      # => (0, 0)
bsearch(rm, 17)                     # => (2, 2)
bsearch(rm, 12)                     # => None
#
# no flattening, no copy — divmod does the work.

# or lean on the standard library, if a copy is fine:
flat = [x for row in rm for x in row]
i = bisect.bisect_left(flat, 11)    # => 5
divmod(i, len(rm[0]))               # => (1, 2)

# ============================================
# Know which sortedness you have
#
# sm  rows sorted, columns sorted, but NOT row-major
#     sorted overall (row 1 starts at 2, row 0 ends at 11)
# rm  fully sorted in row-major order
#
# bsearch on sm would be WRONG. staircase on rm is
# correct but slower than binary search. Check the
# guarantee before choosing the algorithm.

# ============================================
# Dict grids — search by inverting

g = {(r, c): v for r, row in enumerate(m) for c, v in enumerate(row)}

next((k for k, v in g.items() if v == 5), None)      # => (1, 1)

# for repeated lookups, invert once:
where = {v: k for k, v in g.items()}
where[5]                            # => (1, 1)
#
# O(n) to build, O(1) per query. Worth it from the
# second lookup onward. (Duplicate values collide —
# use a defaultdict(list) if that matters.)

# ============================================
# Compare

# find ONE cell               -> this lesson
find(m, 5)

# find all cells with a value -> this lesson
find_all(m, lambda v: v == 5)

# find all connected GROUPS   -> lesson 25
# expand ONE group from here  -> lesson 26
#
# 24 answers "where"; 25 and 26 answer "what is
# connected to what" — and they need a neighborhood
# function (lessons 9-11), which this lesson does not.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|first match|`next(gen, None)`|
|all matches|comprehension over double `enumerate`|
|presence|`any(v == x for row in m for v in row)`|
|**not**|`x in m` — that searches rows|
|the best cell|`max(positions, key=lambda p: m[p[0]][p[1]])`|
|sorted rows **and** columns|staircase from the **top-right**|
|fully sorted|binary search + `divmod(mid, cols)`|
|repeated lookups|invert into `{value: position}`|
|"not found"|a default, not an exception|

---

## Key Insight

**A search returns a position or nothing, and the code should say so.** `next(generator, None)` is the whole pattern: the generator makes it lazy so it stops at the first hit, and the default turns a miss into a value instead of a `StopIteration`.

Everything else is a question of **what you are allowed to assume**:

```text
nothing known      ->  scan               O(rows * cols)
rows + cols sorted ->  staircase          O(rows + cols)
row-major sorted   ->  binary search      O(log(rows * cols))
```

The staircase deserves the attention it gets. Starting at the **top-right** is not arbitrary — it is the only corner (along with bottom-left) where the two directions disagree, so every comparison eliminates an entire row or an entire column. From the top-left, "too small" and "too big" both point inward and nothing is ruled out. And picking the wrong algorithm for your sortedness is a correctness bug, not a performance one: `bsearch` on a merely row-and-column-sorted matrix silently returns wrong answers.

The Python trap is worth repeating because it fails *quietly*: **`5 in m` is `False` even when 5 is in the matrix**, because `in` compares against each row list. There is no 2D `.index()`. Write the generator.

---

## The Search Section

|Lesson|Question|Needs a neighborhood?|Answer|
|---|---|---|---|
|24 Find Cell|*Where is it?*|no|one coordinate|
|25 Connected Components|*How many groups?*|yes|a partition of the grid|
|26 Flood Fill|*What connects to this?*|yes|one region|

```text
  24  point query        ·
  25  global partition   ▣ ▣ ▣   all regions at once
  26  local expansion    ◉ ──►   one region from a seed
```

> **Mental shift:** lesson 24 treats the matrix as a **bag of cells** — position is just where the answer happens to be. Lessons 25 and 26 treat it as a **graph**, where adjacency is the whole point. That is why they need `neighbors4` from lesson 9 and this one does not.
