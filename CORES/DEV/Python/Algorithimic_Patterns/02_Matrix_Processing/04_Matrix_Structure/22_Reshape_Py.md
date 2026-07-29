# 22. Reshape

## Mental Model

Lessons 16–21 moved cells to new **positions**. Reshape leaves the cells in exactly the order they were already in and only changes how they're **grouped into rows**.

```text
[[1, 2, 3],        flatten        [[1, 2],
 [4, 5, 6]]   ->  1 2 3 4 5 6  ->  [3, 4],
                                   [5, 6]]
    2 x 3          the tape         3 x 2
```

The mental model is a **tape**. A matrix is really one long sequence of cells laid out row by row, and the row boundaries are just where you chose to cut. Reshape re-cuts the tape.

Two rules follow straight away, and together they're the whole lesson:

- **The linear order never changes.** `flat(reshape(m, h, w)) == flat(m)`, always.
    
- **The cell count has to match.** `h * w` must equal `rows * cols`, or there's no answer.
    

Here's the comparison that makes it click. Both of these turn a `2×3` into a `3×2`, and they give you **different matrices**:

```text
reshape(m, 3, 2)      transpose(m)
  [[1, 2],              [[1, 4],
   [3, 4],               [2, 5],
   [5, 6]]               [3, 6]]

  re-cuts the tape      re-orders the tape
```

Same shape, different content. If you ever confuse the two, run that example.

---

## Relationship to Cognitive Verb

```text
Regroup
   ↓
Reshape
```

Related verbs:

- Regroup
- Re-chunk
- Change dimensions
- Rewrap
- Redistribute into rows

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Flatten first|the tape|`[x for row in m for x in row]`|
|Cut into rows|regroup|`[flat[i:i+w] for i in range(0, len(flat), w)]`|
|Validate|refuse bad shapes|`h * w == rows * cols`|
|Infer a dimension|the `-1` trick|`h = n // w`|
|Legal shapes|all divisors|`[(h, n//h) for h in range(1, n+1) if n % h == 0]`|
|To a single row|`1 × n`|`[flat]`|
|To a single column|`n × 1`|`[[x] for x in flat]`|
|Chunk a 1D list|the same cut|`[xs[i:i+n] for i in range(0, len(xs), n)]`|
|Grouper|drops remainder|`zip(*[iter(xs)] * n)`|
|Column-major reshape|the other order|reshape the transpose, transpose back|

---

## Common Uses

- Flattening an image into a feature vector, and back
- Batching a stream of records into fixed-size groups
- Converting between tensor layouts
- Laying out a 1D array as a grid for display
- Turning a list of pixels into a bitmap
- Splitting a long sequence into fixed-width lines
- Neural network input preparation
- Serialising and deserialising grids

---

## Hidden Interview Problems

- Reshape the Matrix (LeetCode 566)
- Convert a 1D array into a 2D array with given dimensions
- Chunk a list into groups of n
- Check whether a reshape is possible
- Print a list as a grid of fixed width
- Convert between flat index and (row, col)
- Split a string into fixed-length lines

---

## Recognition Clues

If you hear...

- "reshape into r × c..."
- "same elements, different dimensions..."
- "group into rows of n..."
- "convert 1D to 2D..."
- "batch these into groups of..."
- "lay it out as a grid..."

...think **Reshape**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D → 2D (or 1D ↔ 2D)|
|Coordinate rule|`flat_index` preserved; `(r,c) = divmod(i, cols)` re-derived|
|Shape|`rows × cols → h × w`|
|Constraint|`h * w == rows * cols`|
|Linear order|**Preserved** — this is the defining property|
|Involution|No — but reshaping back to the original shape restores it|
|In place|Not meaningfully — the row structure is rebuilt|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(rows × cols)|
|Common Domains|ML tensors, images, batching, display|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

m = [[1, 2, 3],
     [4, 5, 6]]                 # 2 x 3, six cells

s = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]                 # 3 x 3

flat = lambda m: [x for row in m for x in row]

flat(m)                                 # => [1, 2, 3, 4, 5, 6]

# ============================================
# The one idiom to remember
#
#   flatten, then cut every w cells
#
# Reshape is not one operation — it is lesson 23
# followed by a slice loop.

def reshape(m, h, w):
    xs = flat(m)
    if len(xs) != h * w:
        raise ValueError(f"cannot reshape {len(xs)} into {h}x{w}")
    return [xs[i:i+w] for i in range(0, len(xs), w)]

reshape(m, 3, 2)
# =>
# [[1, 2],
#  [3, 4],
#  [5, 6]]

reshape(m, 1, 6)                        # => [[1, 2, 3, 4, 5, 6]]
reshape(m, 6, 1)                        # => [[1], [2], [3], [4], [5], [6]]
reshape(m, 2, 3) == m                   # => True   a no-op

# ============================================
# Reshape is NOT transpose
#
# Both turn a 2x3 into a 3x2. They are different.

def transpose(m): return [list(r) for r in zip(*m)]

reshape(m, 3, 2)
# => [[1, 2], [3, 4], [5, 6]]

transpose(m)
# => [[1, 4], [2, 5], [3, 6]]

reshape(m, 3, 2) == transpose(m)        # => False

# the difference, stated precisely:
flat(reshape(m, 3, 2)) == flat(m)       # => True    order kept
flat(transpose(m)) == flat(m)           # => False   order changed

flat(transpose(m))                      # => [1, 4, 2, 5, 3, 6]
#
# THIS is the dividing line of the whole section.
# Lessons 16-21 rearrange the tape. Reshape re-cuts it.

# ============================================
# The constraint is absolute

try:
    reshape(m, 4, 2)
except ValueError as e:
    print(e)                            # cannot reshape 6 into 4x2

# and the legal shapes are exactly the divisor pairs
n = len(flat(m))                        # => 6
[(h, n // h) for h in range(1, n + 1) if n % h == 0]
# => [(1, 6), (2, 3), (3, 2), (6, 1)]
#
# a prime number of cells has only two possible shapes.
# Choosing 12 or 16 cells over 13 is why array sizes in
# real code are so often highly composite.

# ============================================
# Inferring a dimension — the -1 convention
#
# Every array library lets you leave one axis to be
# computed. It is just a division.

def reshape_auto(m, h=-1, w=-1):
    xs = flat(m)
    n = len(xs)
    if h == -1:
        h = n // w
    if w == -1:
        w = n // h
    return reshape(m, h, w)

reshape_auto(m, -1, 2)                  # => [[1, 2], [3, 4], [5, 6]]
reshape_auto(m, 2, -1)                  # => [[1, 2, 3], [4, 5, 6]]
#
# "-1" means "you work it out". Only one axis may be -1,
# for the obvious reason.

# ============================================
# 1D <-> 2D, the two directions

xs = [1, 2, 3, 4, 5, 6]

# 1D -> 2D: cut every w
[xs[i:i+3] for i in range(0, len(xs), 3)]
# => [[1, 2, 3], [4, 5, 6]]

# 2D -> 1D: that's lesson 23
flat(m)                                 # => [1, 2, 3, 4, 5, 6]

# the pair is a round trip
reshape([xs], 2, 3)                     # => [[1, 2, 3], [4, 5, 6]]
flat(reshape([xs], 2, 3)) == xs         # => True

# ============================================
# The grouper, and why it is not the same
#
# The zip-of-iterators trick chunks a list too, but it
# SILENTLY DROPS a short final group.

ys = [1, 2, 3, 4, 5, 6, 7]

[ys[i:i+3] for i in range(0, len(ys), 3)]
# => [[1, 2, 3], [4, 5, 6], [7]]        keeps the remainder

list(zip(*[iter(ys)] * 3))
# => [(1, 2, 3), (4, 5, 6)]             the 7 is GONE
#
# reshape() refuses a bad size loudly; the grouper
# discards quietly. Know which behaviour you want.
# (Same distinction as ragged tiles in lesson 13.)

# ============================================
# Column-major reshape
#
# Python and reshape() are row-major: the tape runs
# left-to-right, top-to-bottom. To fill columns first,
# reshape the transposed order and transpose back.

def reshape_colmajor(m, h, w):
    return transpose(reshape(transpose(m), w, h))

reshape(m, 3, 2)
# => [[1, 2], [3, 4], [5, 6]]           fills rows first

reshape_colmajor(m, 3, 2)
# => [[1, 5], [4, 3], [2, 6]]           fills columns first
#
# Fortran, MATLAB and R default to column-major; C,
# Python and most image formats are row-major. When
# data crosses that boundary, this is the conversion.

# ============================================
# Practical: batching a stream of records

records = list(range(1, 11))            # 10 items
batch = 4

[records[i:i+batch] for i in range(0, len(records), batch)]
# => [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10]]
#
# the last batch is short — that is usually correct for
# batching and wrong for reshaping. Same code, different
# contract.

# ============================================
# Practical: laying a flat list out for display

pixels = list(range(1, 13))

def as_grid(xs, w):
    rows = [xs[i:i+w] for i in range(0, len(xs), w)]
    return "\n".join(" ".join(f"{x:>3}" for x in row) for row in rows)

print(as_grid(pixels, 4))
#   1   2   3   4
#   5   6   7   8
#   9  10  11  12

print(as_grid(pixels, 6))
#   1   2   3   4   5   6
#   7   8   9  10  11  12
#
# same data, one parameter, a completely different
# picture. That is reshape in one line.

# ============================================
# Compare

# same cells, new POSITIONS  -> lessons 16-21
transpose(m)                            # order changes

# same cells, new GROUPING   -> this lesson
reshape(m, 3, 2)                        # order preserved

# same cells, NO grouping    -> lesson 23
flat(m)

# the invariant that separates them:
flat(reshape(m, 3, 2)) == flat(m)       # => True
flat(transpose(m))     == flat(m)       # => False
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|reshape|flatten, then `[xs[i:i+w] for i in range(0, n, w)]`|
|the legality check|`h * w == rows * cols`|
|an inferred axis|`n // other`|
|all valid shapes|the divisor pairs of `n`|
|1D → 2D|cut every `w`|
|2D → 1D|lesson 23|
|to keep a short last group|the slice loop|
|to drop a short last group|`zip(*[iter(xs)]*n)`|
|column-major|transpose, reshape swapped, transpose back|
|the difference from transpose|reshape **preserves** the flat order|

---

## Key Insight

**A matrix is a tape with cuts in it. Reshape moves the cuts; it never moves the cells.**

That single property is the whole contract, and it is testable in one line:

```python
flat(reshape(m, h, w)) == flat(m)       # always True
flat(transpose(m))     == flat(m)       # False
```

Everything else follows. The cell count is conserved, so `h * w` must equal `rows * cols` — reshape cannot invent or discard data, and the set of legal shapes is exactly the divisor pairs of `n`. One axis can be left as `-1` because a division recovers it. And reshaping back to the original dimensions is always an exact round trip.

Three practical things:

1. **Reshape and transpose are not interchangeable**, even when they produce the same shape. `2×3 → 3×2` has two different answers, and the wrong one is a silent data corruption rather than a crash.
    
2. **Loud versus quiet on a bad fit.** `reshape` should raise; the `zip(*[iter(xs)]*n)` grouper silently drops the remainder; the slice loop silently keeps a short group. All three are useful — choose deliberately, exactly as with ragged tiles in lesson 13.
    
3. **Row-major is a convention, not a law.** Python, C and most image formats fill rows first; Fortran, MATLAB and R fill columns first. Data crossing that boundary needs `transpose → reshape → transpose`, and forgetting it produces output that looks plausible and is scrambled.
    

---

## Reshape vs the Rest

|Operation|Cells|Order on the tape|Shape|
|---|---|---|---|
|**Transpose / rotate / flip**|same|**changed**|swapped or preserved|
|**Reshape**|same|**preserved**|changed|
|**Flatten**|same|**preserved**|`R × C → R*C`|

```text
  the tape:  1 2 3 4 5 6

  reshape  ->  cut it differently      1 2 | 3 4 | 5 6
  transpose->  reorder it              1 4 2 5 3 6
  flatten  ->  stop cutting            1 2 3 4 5 6
```

> **Mental shift:** the rest of this section asks *"where does each cell go?"*. Reshape asks *"where do the row breaks go?"*, and the cells never move at all. That's why reshape is nearly free in real array libraries: it changes the metadata, not the memory.
