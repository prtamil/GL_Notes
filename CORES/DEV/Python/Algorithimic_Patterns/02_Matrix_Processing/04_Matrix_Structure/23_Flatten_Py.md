# 23. Flatten

## Mental Model

Reshape re-cut the tape. Flatten **removes the cuts entirely**.

```text
[[1, 2, 3],
 [4, 5, 6]]     ->     [1, 2, 3, 4, 5, 6]

     2 x 3                    6
```

It's the limiting case of lesson 22, `reshape(m, 1, n)` without the wrapping list, and the simplest operation in the section. It matters far more than its difficulty suggests, for one reason:

> **Flattening is not a transformation you apply. It is the layout the matrix already had.**

In memory, `[[1,2,3],[4,5,6]]` *is* `1 2 3 4 5 6` with a row length attached. Row-major order is why `m[r][c]` works, why row traversal is cache-friendly (lesson 1), why a 180° rotation is just the reversed flat list (lesson 18), and why reshape is nearly free.

So what this lesson is really about is the **index correspondence** between the two views:

```text
   i  =  r * cols + c              2D -> 1D
 r, c  =  divmod(i, cols)          1D -> 2D
```

Learn that pair and you can treat any matrix as a flat array whenever it suits you — which is often, because every 1D tool in Python then applies.

---

## Relationship to Cognitive Verb

```text
Unfold
   ↓
Flatten
```

Related verbs:

- Unfold
- Linearise
- Serialise
- Lay out end to end
- Collapse to a sequence

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Flatten|the standard way|`[x for row in m for x in row]`|
|Lazily|no list built|`itertools.chain.from_iterable(m)`|
|The trap|quadratic|`sum(m, [])` — avoid|
|Flat index|2D → 1D|`i = r * cols + c`|
|Coordinates|1D → 2D|`r, c = divmod(i, cols)`|
|With positions|index and value|`enumerate(chain.from_iterable(m))`|
|Column-major|the other order|`[x for row in zip(*m) for x in row]`|
|Deeply nested|irregular depth|recursive generator with `yield from`|
|Hashable form|dict key, set member|`tuple(flat(m))`|
|Back to 2D|the inverse|`reshape` (lesson 22)|

---

## Common Uses

- Serialising a grid to a file or over a network
- Hashing or comparing whole matrices
- Feeding a matrix to a 1D algorithm (`sorted`, `Counter`, `max`)
- Feature vectors for machine learning
- Memoising a board state
- Image data as a byte stream
- Computing global statistics
- Random sampling from a grid

---

## Hidden Interview Problems

- Flatten a 2D array
- Flatten a nested list of arbitrary depth
- Convert between flat index and (row, col)
- Find the k-th element in row-major order
- Search a sorted matrix as if it were one array
- Kth smallest element in a matrix
- Serialise / deserialise a grid
- Detect duplicate boards in a game

---

## Recognition Clues

If you hear...

- "flatten..."
- "as a single list..."
- "treat the matrix as one array..."
- "the k-th element in row-major order..."
- "serialise the grid..."
- "binary search the matrix..."

...think **Flatten**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D → 1D|
|Coordinate rule|`i = r * cols + c`|
|Inverse rule|`r, c = divmod(i, cols)`|
|Shape|`rows × cols → rows * cols`|
|Linear order|**Preserved** — it *is* the linear order|
|Involution|No — the inverse is `reshape`|
|Information lost|The shape. Keep `cols` or you cannot get back|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(rows × cols), or O(1) with a lazy iterator|
|Common Domains|Serialisation, ML, hashing, 1D algorithms|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from itertools import chain
from collections import Counter

m = [[1, 2, 3],
     [4, 5, 6]]                 # 2 x 3

rows, cols = len(m), len(m[0])

# ============================================
# The one idiom to remember
#
# Read it left to right, exactly like nested for loops.

def flat(m):
    return [x for row in m for x in row]

flat(m)                                 # => [1, 2, 3, 4, 5, 6]

# the loop order is OUTER first, then INNER — the same
# order you would write them as statements:
#   for row in m:
#       for x in row:

# ============================================
# The lazy version — for big matrices

list(chain.from_iterable(m))            # => [1, 2, 3, 4, 5, 6]

# chain doesn't build anything until consumed:
next(chain.from_iterable(m))            # => 1
sum(chain.from_iterable(m))             # => 21   no intermediate list

# ============================================
# The one to avoid
#
# sum(m, []) works and reads nicely. It is also O(n^2):
# it builds a new list for every row concatenation.

sum(m, [])                              # => [1, 2, 3, 4, 5, 6]
#
# fine for 3 rows, disastrous for 30,000. Use the
# comprehension or chain. This is the flatten equivalent
# of building a string with += in a loop.

# ============================================
# THE INDEX CORRESPONDENCE
#
# This is the actual content of the lesson.

#   2D -> 1D
[(r, c, r * cols + c) for r in range(rows) for c in range(cols)]
# => [(0,0,0), (0,1,1), (0,2,2),
#     (1,0,3), (1,1,4), (1,2,5)]

#   1D -> 2D
[divmod(i, cols) for i in range(rows * cols)]
# => [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]

# and they agree:
xs = flat(m)
[xs[r * cols + c] for r in range(rows) for c in range(cols)]
# => [1, 2, 3, 4, 5, 6]

all(m[r][c] == xs[r * cols + c]
    for r in range(rows) for c in range(cols))          # => True

# divmod is the built-in for this — it returns the
# quotient and remainder together, which is exactly
# (row, column).

# ============================================
# Why it matters: 1D algorithms on 2D data
#
# Once flat, everything you know about sequences works.

sorted(flat(m), reverse=True)           # => [6, 5, 4, 3, 2, 1]
max(flat(m))                            # => 6
sum(flat(m))                            # => 21
Counter(flat([[1, 2], [2, 3]]))         # => Counter({2: 2, 1: 1, 3: 1})

# find a value's COORDINATES via the flat index
i = flat(m).index(5)
i                                       # => 4
divmod(i, cols)                         # => (1, 1)
m[1][1]                                 # => 5

# ============================================
# Binary search a row-sorted matrix as one array
#
# The classic use. A sorted matrix IS a sorted list
# under row-major order — divmod converts back.

import bisect

sm = [[1,  3,  5 ],
      [7,  9,  11],
      [13, 15, 17]]

def search(sm, target):
    w = len(sm[0])
    xs = flat(sm)                       # or index arithmetically, no copy
    i = bisect.bisect_left(xs, target)
    if i < len(xs) and xs[i] == target:
        return divmod(i, w)
    return None

search(sm, 11)                          # => (1, 2)
search(sm, 12)                          # => None
#
# O(log n) over the whole matrix, no 2D reasoning needed

# ============================================
# Hashing a matrix — lists are unhashable

key = tuple(flat(m))
key                                     # => (1, 2, 3, 4, 5, 6)

seen = {key}
tuple(flat(m)) in seen                  # => True

# for a set of board states, this is the standard key.
# Same requirement as counting patches in lesson 14.

# nested tuples keep the shape:
tuple(map(tuple, m))                    # => ((1, 2, 3), (4, 5, 6))

# ============================================
# Row-major vs column-major

flat(m)                                 # => [1, 2, 3, 4, 5, 6]

[x for row in zip(*m) for x in row]     # => [1, 4, 2, 5, 3, 6]
#
# flattening the TRANSPOSE gives column-major order.
# Two valid linearisations of the same matrix; row-major
# is Python's, and the one every earlier lesson assumed.

# ============================================
# Flatten of a 180 rotation is the reversed flat list
#
# The identity from lesson 18, stated in this lesson's
# language. It works because a half turn reverses both
# axes, which in row-major order is simply "backwards".

rot180 = lambda m: [row[::-1] for row in m[::-1]]

flat(rot180(m)) == flat(m)[::-1]        # => True

# try it with rot90 and it fails — no other symmetry has
# such a simple linear form
rot90 = lambda m: [list(r) for r in zip(*m[::-1])]
flat(rot90(m))                          # => [4, 1, 5, 2, 6, 3]

# ============================================
# Deep flatten — irregular nesting
#
# The comprehension only removes ONE level. For unknown
# depth you need recursion.

nested = [[1, [2, 3]],
          [4, [5, [6]]]]

[x for row in nested for x in row]
# => [1, [2, 3], 4, [5, [6]]]           still nested!

def deep_flatten(x):
    for e in x:
        if isinstance(e, list):
            yield from deep_flatten(e)
        else:
            yield e

list(deep_flatten(nested))              # => [1, 2, 3, 4, 5, 6]
#
# `yield from` is what makes this readable. Note it also
# flattens strings-of-lists correctly only because we
# test for `list` specifically — testing for "iterable"
# would recurse into strings forever.

# ============================================
# The inverse is reshape — and it needs the width

xs = flat(m)                            # => [1, 2, 3, 4, 5, 6]
[xs[i:i+cols] for i in range(0, len(xs), cols)] == m     # => True
#
# flatten DISCARDS the shape. Keep `cols` alongside the
# flat data or the round trip is impossible: the same
# six numbers are a valid 1x6, 2x3, 3x2 and 6x1.

# ============================================
# Compare — the whole section in five lines

flat(m)                                 # 2D -> 1D, order preserved
[xs[i:i+w] for i in range(0, len(xs), w)]   # 1D -> 2D, order preserved
[list(r) for r in zip(*m)]              # order CHANGED (transpose)
[row[::-1] for row in m[::-1]]          # order REVERSED (rot180)
[row[::-1] for row in m]                # order changed per row (flip_h)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|flatten|`[x for row in m for x in row]`|
|flatten lazily|`chain.from_iterable(m)`|
|**not** to flatten|`sum(m, [])` — it's O(n²)|
|2D → flat index|`i = r * cols + c`|
|flat index → 2D|`divmod(i, cols)`|
|a hashable matrix|`tuple(flat(m))`|
|column-major|flatten `zip(*m)`|
|arbitrary depth|recursive generator + `yield from`|
|to get the matrix back|`reshape` — and you must still know `cols`|

---

## Key Insight

**Flatten is not a transformation — it is the matrix's actual memory layout, made visible.**

A `list[list[int]]` is row-major: cell `(r, c)` sits at position `r * cols + c` in one continuous sequence. Everything in this course has quietly depended on that:

- Row traversal is fast because it reads memory in order (lesson 1).
    
- A 180° rotation is the reversed flat list, because reversing both axes *is* reading backwards (lesson 18).
    
- Reshape is nearly free, because it only changes where you pretend the row breaks are (lesson 22).
    

So the thing to actually carry away is the **index pair**:

```text
   i  =  r * cols + c
 r, c  =  divmod(i, cols)
```

With it you can drop into 1D whenever 1D is easier — binary-search a sorted matrix in `O(log n)`, hash a board state, `Counter` the values, `sorted` the whole grid — and convert back with one `divmod`.

Three Python specifics:

1. **`sum(m, [])` is quadratic.** It reads beautifully and it re-copies the accumulated list once per row. Use the comprehension, or `chain.from_iterable` when you want laziness.
    
2. **The comprehension removes exactly one level.** Irregular nesting needs a recursive generator with `yield from`.
    
3. **Flatten discards the shape.** Six numbers are equally a `1×6`, `2×3`, `3×2` or `6×1`. Store the width with the data, or the round trip is guesswork.
    

---

## The Structure Section Complete

|Lesson|Operation|Shape|Flat order|
|---|---|---|---|
|16|Transpose|swaps|changed|
|17|Rotate 90°|swaps|changed|
|18|Rotate 180°|preserved|**reversed**|
|19|Rotate 270°|swaps|changed|
|20|Flip horizontal|preserved|changed|
|21|Flip vertical|preserved|changed|
|22|Reshape|changed|**preserved**|
|23|Flatten|`R×C → R*C`|**preserved**|

```text
                  ┌── change POSITIONS ──►  16-21   (the 8 symmetries, D4)
  the same cells ─┤
                  └── change GROUPING  ──►  22-23   (the same tape, re-cut)
```

Two families, one dividing line: **does the flat order change?**

```python
flat(transpose(m)) == flat(m)       # False -> a symmetry
flat(reshape(m, 3, 2)) == flat(m)   # True  -> a layout change
```

> **Mental shift:** every operation in this section is a function from `(r, c)` to a new `(r, c)`, or equivalently a permutation of the flat index. Write that function down and the code writes itself. Try to reason from the picture and you'll get the direction backwards. Pictures are for checking; coordinate rules are for building.
