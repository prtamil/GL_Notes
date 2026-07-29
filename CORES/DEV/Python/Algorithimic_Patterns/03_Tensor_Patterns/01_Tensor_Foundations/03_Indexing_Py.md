# 3. Indexing

## Mental Model

Indexing is how you reach **one element**, or more usefully **one sub-tensor**.

One rule organises everything:

> **Each integer index consumes one axis.**

```text
t              shape (2, 3, 4)     rank 3
t[0]           shape (3, 4)        rank 2   — a matrix
t[0][1]        shape (4,)          rank 1   — a vector
t[0][1][2]     shape ()            rank 0   — a scalar
```

You don't have to consume them all. **Partial indexing is the normal case.** `t[0]` isn't an error for giving one index where three were expected; it's the first `(3,4)` block.

The syntax difference from nested lists is tiny and matters enormously:

```text
nested[0][1][2]     three separate lookups     (lists)
t[0, 1, 2]          ONE lookup, a tuple key    (arrays)
```

`t[0][1][2]` works too and gives the same value, but it creates two throwaway intermediate views along the way. `t[0, 1, 2]` is a single operation, and it's the form that lets you mix integers with slices:

```text
t[0, :, 1]      axis 0 fixed, axis 1 all, axis 2 fixed
```

That mixing is what indexing is really for. An integer *selects and removes* an axis; a slice *keeps* it. `t[0]` has rank 2; `t[0:1]` has rank 3.

---

## Relationship to Cognitive Verb

```text
Reach
  ↓
Indexing
```

Related verbs:

- Reach
- Select
- Pick out
- Drill down
- Address

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|One element|full index|`t[i, j, k]`|
|Nested-list style|chained|`t[i][j][k]` — works, but slower|
|Sub-tensor|partial index|`t[i]`, `t[i, j]`|
|From the end|negative|`t[-1, -1, -1]`|
|Mix with slices|keep some axes|`t[0, :, 1]`|
|All remaining axes|ellipsis|`t[..., 0]`|
|Keep the axis|slice, don't index|`t[0:1]` vs `t[0]`|
|Every index|enumerate positions|`np.ndindex(*t.shape)`|
|Index a nested list|by a tuple|fold: `for i in idx: n = n[i]`|
|Assign|write through|`t[0, 1, 2] = 99`|

---

## Common Uses

- Picking one image out of a batch
- Extracting a channel from an image
- Selecting a time slice from a sequence
- Reading a single feature across all samples
- Setting or updating specific entries
- Walking every position of an n-D grid
- Slicing a sub-volume out of a 3D scan

---

## Hidden Interview Problems

- Access an element in an arbitrarily nested list by an index tuple
- Extract a channel / row / column from a 3D array
- Iterate over all indices of an n-dimensional array
- Convert a flat index to a multi-index and back
- Select every k-th element along a chosen axis
- Explain the difference between `t[0]` and `t[0:1]`

---

## Recognition Clues

If you hear...

- "the i-th image..."
- "channel 0..."
- "element at position (i, j, k)..."
- "the first sample in the batch..."
- "keep the dimension..."
- "all of the remaining axes..."

...think **Indexing**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Integer index|Consumes one axis — rank drops by 1|
|Slice index|Keeps the axis — rank unchanged|
|`t[i, j]`|One lookup with a tuple key|
|`t[i][j]`|Two lookups, an intermediate view|
|Negative|Counts from the end of that axis|
|Ellipsis `...`|"All remaining axes", expands to `:`s|
|Basic indexing|Returns a **view** — shares memory|
|Out of range|Raises `IndexError` — no silent wrap|
|Common Domains|Everywhere|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np

t = np.arange(24).reshape(2, 3, 4)
nested = t.tolist()

t.shape                     # => (2, 3, 4)

# ============================================
# The one idiom to remember
#
#   each integer index consumes one axis

t[0]
# => array([[ 0,  1,  2,  3],
#           [ 4,  5,  6,  7],
#           [ 8,  9, 10, 11]])
t[0].shape                  # => (3, 4)     a matrix

t[0][1]                     # => array([4, 5, 6, 7])
t[0][1].shape               # => (4,)       a vector

t[0][1][2]                  # => 6
np.ndim(t[0][1][2])         # => 0          a scalar

[t.ndim, t[0].ndim, t[0][1].ndim, np.ndim(t[0][1][2])]
# => [3, 2, 1, 0]
#
# one index, one axis. Every time.

# ============================================
# Tuple indexing — the array form

t[0, 1, 2]                  # => 6
t[0][1][2] == t[0, 1, 2]    # => True

t[1, 2, 3]                  # => 23     the last element
t[-1, -1, -1]               # => 23     same, from the end

# the two forms differ in COST, not result:
#
#   t[0][1][2]   builds t[0], then t[0][1], then reads
#   t[0, 1, 2]   one lookup with the tuple (0, 1, 2)
#
# and only the tuple form can mix in slices.

# nested lists do NOT accept a tuple:
try:
    nested[0, 1, 2]
except TypeError as e:
    print(e)
# list indices must be integers or slices, not tuple
#
# for a nested list you fold the index tuple by hand:
def get(n, idx):
    for i in idx:
        n = n[i]
    return n

get(nested, (1, 2, 3))      # => 23
get(nested, (1, 2, 3)) == t[1, 2, 3]        # => True

# ============================================
# Mixing integers and slices
#
# THIS is what tuple indexing is for. An integer drops
# its axis; a colon keeps it.

t[0, :, 1]                  # => array([1, 5, 9])
#   axis 0 fixed at 0, axis 1 all three, axis 2 fixed at 1
#   result rank 1 — two axes consumed by integers

t[:, 0, :]
# => array([[ 0,  1,  2,  3],
#           [12, 13, 14, 15]])
t[:, 0, :].shape            # => (2, 4)
#   "row 0 of every block"

t[:, :, 0].shape            # => (2, 3)
#   "column 0 of every block"

# ============================================
# Ellipsis — "all the remaining axes"
#
# ... expands to as many `:` as needed. Use it when you
# care about one end of the shape and not the rank.

t[..., 0]
# => array([[ 0,  4,  8],
#           [12, 16, 20]])
t[..., 0].shape             # => (2, 3)
t[..., 0] is not None and np.array_equal(t[..., 0], t[:, :, 0])      # => True

t[0, ...].shape             # => (3, 4)     same as t[0]

# the point: t[..., 0] means "index the LAST axis" on an
# array of ANY rank. t[:, :, 0] hard-codes rank 3 and
# breaks the moment a batch dimension is added — the
# same portability argument as axis=-1 in lesson 2.

# ============================================
# THE RANK TRAP: integer vs slice

t[0].shape                  # => (3, 4)     integer: axis GONE
t[0:1].shape                # => (1, 3, 4)  slice: axis KEPT, size 1

# both select the same data. Only the rank differs.
#
# This bites when a downstream operation expects a fixed
# rank. `t[0:1]` (or `t[None, 0]`, lesson 16) is how you
# keep a batch dimension of size 1 rather than losing it.

np.array_equal(t[0], t[0:1][0])         # => True   same values

# ============================================
# Out of range raises — unlike part 2's slicing

try:
    t[2, 0, 0]
except IndexError as e:
    print(e)
# index 2 is out of bounds for axis 0 with size 2
#
# but a SLICE past the end silently clips, exactly like
# a list:
t[0:99].shape               # => (2, 3, 4)
#
# index -> raises; slice -> clips. Same split as Python
# lists, and the same trap: an out-of-range slice gives
# you fewer elements rather than an error.

# ============================================
# Basic indexing returns a VIEW

sub = t[0]
np.shares_memory(t, sub)    # => True

t2 = np.arange(24).reshape(2, 3, 4)
v = t2[0]
v[0, 0] = 99
t2[0, 0, 0]                 # => 99     the ORIGINAL changed
#
# this is the tensor version of lesson 21's aliasing
# trap. If you need independence: t[0].copy().
# (Fancy indexing, lesson 10, copies instead.)

# ============================================
# Assignment through an index

t3 = np.arange(24).reshape(2, 3, 4)

t3[0, 1, 2] = 99            # one element
t3[1] = 0                   # a whole (3,4) block — broadcast
t3[:, 0, :] = -1            # row 0 of every block

t3[0]
# => array([[-1, -1, -1, -1],
#           [ 4,  5, 99,  7],
#           [ 8,  9, 10, 11]])
#
# the left-hand side can be any index expression, and
# the right-hand side broadcasts to fit (lesson 17).

# ============================================
# Walking every index
#
# np.ndindex is the n-dimensional version of the nested
# for loops from part 2.

list(np.ndindex(*t.shape))[:5]
# => [(0,0,0), (0,0,1), (0,0,2), (0,0,3), (0,1,0)]

len(list(np.ndindex(*t.shape)))         # => 24
#
# row-major order: the LAST index varies fastest, which
# is the same ordering as part 2's row-major flatten and
# the reason it matches t.ravel() (lesson 4).

all(t[idx] == t.ravel()[i]
    for i, idx in enumerate(np.ndindex(*t.shape)))      # => True

# the pure-Python equivalent, for reference:
from itertools import product
list(product(range(2), range(3), range(4)))[:5]
# => [(0,0,0), (0,0,1), (0,0,2), (0,0,3), (0,1,0)]
#
# but if you are writing this loop over a real array,
# you almost certainly want a vectorised operation
# instead — see lessons 17 and 20.

# ============================================
# Compare

t[0]                # integer      -> rank 2, view
t[0:1]              # slice        -> rank 3, view
t[0, 1]             # two integers -> rank 1
t[0, :, 1]          # mixed        -> rank 1
t[..., 0]           # ellipsis     -> rank 2, any input rank
t[[0, 1]]           # a LIST       -> fancy indexing, a COPY (lesson 10)
t[t > 10]           # a mask       -> boolean indexing, a COPY (lesson 11)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the rule|each integer index consumes one axis|
|one element|`t[i, j, k]` — one lookup, not three|
|a sub-tensor|`t[i]` — partial indexing is normal|
|to mix fixed and free axes|`t[0, :, 1]`|
|the last axis, any rank|`t[..., 0]`|
|to **keep** an axis|`t[0:1]`, not `t[0]`|
|an independent copy|`.copy()` — basic indexing is a view|
|every position|`np.ndindex(*t.shape)`|
|to index a nested list|fold the tuple: `for i in idx: n = n[i]`|

---

## Key Insight

**Each integer index consumes one axis; each slice keeps it.** That one sentence predicts the rank of every indexing expression you will ever write:

```text
t[0]        (2,3,4) -> (3,4)        integer eats axis 0
t[0:1]      (2,3,4) -> (1,3,4)      slice keeps it
t[0, :, 1]  (2,3,4) -> (3,)         two integers, one slice
t[..., 0]   (2,3,4) -> (2,3)        ellipsis fills the middle
```

Three things to carry:

1. **`t[i, j, k]` is one lookup, `t[i][j][k]` is three.** They agree in value, but only the tuple form can mix integers with slices — and that mixing is the whole point of array indexing.
    
2. **Prefer `...` and negative axes over hard-coded positions.** `t[..., 0]` indexes the last axis at any rank; `t[:, :, 0]` breaks the day someone prepends a batch dimension. Same argument as `axis=-1`.
    
3. **Basic indexing returns a view.** `v = t[0]; v[0,0] = 99` writes into `t`. This is part 2's `m[::-1]` aliasing trap generalised — and the fix is the same, `.copy()`. Note that fancy and boolean indexing behave *oppositely* (they copy), which is a genuine inconsistency worth memorising rather than deriving.
    

One smaller asymmetry, inherited straight from Python lists: **an out-of-range index raises, an out-of-range slice clips.** `t[2]` on a size-2 axis raises `IndexError`; `t[0:99]` silently returns everything.

---

## Indexing vs Slicing

|Form|Consumes the axis?|Returns|Covered in|
|---|---|---|---|
|`t[0]`|yes — rank drops|view|this lesson|
|`t[0:1]`|no — size-1 axis|view|lesson 8|
|`t[..., 0]`|yes, on the last axis|view|lesson 9|
|`t[[0, 2]]`|no — reorders|**copy**|lesson 10|
|`t[t > 5]`|flattens to rank 1|**copy**|lesson 11|

> **Mental shift:** in part 2 you indexed with `m[r][c]` and that was the end of it. From rank 3 upward, indexing turns into a small language. Integers, slices, ellipsis, lists and masks all live in the same brackets, and each does something different to the rank *and* to whether you get a view or a copy. Section 03 covers the rest; this lesson is the half you'll use every day.
