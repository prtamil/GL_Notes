# 8. Basic Slicing

## Mental Model

Lesson 3 reached elements with integers. Slicing reaches **rectangular sub-blocks** — and the syntax is Python's familiar `start:stop:step`, once per axis.

```text
t[ 0:2 , 1:3 , ::2 ]
   ────   ────  ────
   axis0  axis1 axis2
```

Each position in the bracket controls one axis, independently. An axis you do not mention is taken whole.

The rule that ties it to lesson 3:

> **An integer consumes an axis. A slice keeps it.**

```text
t[0]        (2,3,4) -> (3,4)      integer: axis gone
t[0:1]      (2,3,4) -> (1,3,4)    slice: axis kept, size 1
```

Same data, different rank. That distinction is the single most common source of shape errors downstream.

And the property that makes slicing cheap — and occasionally dangerous:

> **Basic slicing returns a view.**

No data is copied. Lesson 4 explained why: a slice is a new `shape`, a new `strides` and an offset into the *same* buffer. `t[:, :, ::2]` doesn't skip elements by moving them; it doubles the stride. `t[::-1]` makes the stride **negative**. Both are free, and both write through to the original.

---

## Relationship to Cognitive Verb

```text
Carve
  ↓
Basic Slicing
```

Related verbs:

- Carve out
- Take a block
- Crop
- Subsample
- Restrict a range

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Range on one axis|a band|`t[:, 1:3, :]`|
|Whole axis|everything|`:`|
|Every k-th|stride|`t[..., ::2]`|
|Reverse|negative step|`t[::-1]`|
|Keep the axis|size-1 slice|`t[0:1]` not `t[0]`|
|Mix with integers|drop some axes|`t[0, 1:, 2:]`|
|Crop a border|trim each side|`t[1:-1, 1:-1]`|
|Programmatic axis|build the tuple|`slice(None)` in a list|
|Assign to a block|write in place|`t[:, 0, :] = -1`|
|Independence|force a copy|`.copy()`|

---

## Common Uses

- Cropping images and volumes
- Extracting a channel range or a time window
- Downsampling by taking every k-th element
- Removing a border
- Splitting a batch into train / validation
- Reversing along an axis
- Writing into a sub-region of a buffer
- Sliding-window offsets (`t[:-1]` vs `t[1:]`)

---

## Hidden Interview Problems

- Extract a sub-block of a 3D array
- Crop a border of width k
- Downsample an array by 2 along each axis
- Reverse a tensor along a given axis
- Compute differences between adjacent slices
- Explain why `t[0]` and `t[0:1]` differ
- Explain why modifying a slice changed the original

---

## Recognition Clues

If you hear...

- "the first n samples..."
- "crop / trim / window..."
- "every other element..."
- "rows 2 through 5..."
- "reverse the order along..."
- "keep the dimension..."

...think **Basic Slicing**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Syntax|`start:stop:step`, once per axis|
|Unmentioned axes|Taken whole|
|Integer|Consumes the axis (rank − 1)|
|Slice|Keeps the axis|
|Result|A **view** — shares memory|
|Out of range|Clips silently; never raises|
|Empty result|Legal — a size-0 axis|
|Negative step|Negative stride; still a view|
|Time Complexity|O(1) — metadata only|
|Common Domains|Images, signals, batching, cropping|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np

t = np.arange(24).reshape(2, 3, 4)

# ============================================
# The one idiom to remember
#
#   one slice per axis, comma separated

t[:, 1:3, :].shape          # => (2, 2, 4)

t[:, 1:3, :]
# => array([[[ 4,  5,  6,  7],
#            [ 8,  9, 10, 11]],
#
#           [[16, 17, 18, 19],
#            [20, 21, 22, 23]]])
#
# axis 0 whole, axis 1 rows 1-2, axis 2 whole.

# trailing axes may be omitted:
np.array_equal(t[:, 1:3], t[:, 1:3, :])         # => True
np.array_equal(t[:], t)                         # => True

# ============================================
# THE RANK RULE — integer vs slice

t[0].shape                  # => (3, 4)     integer: axis CONSUMED
t[0:1].shape                # => (1, 3, 4)  slice: axis KEPT

# both select the same numbers. Only the rank differs,
# and that is what breaks the next function in the chain.
# When you need to keep a batch dimension of size 1, use
# a slice — or `t[None, 0]` (lesson 9).

t[0, 1:, 2:].shape          # => (2, 2)     one int, two slices
t[0, 1:, 2:]
# => array([[ 6,  7],
#           [10, 11]])

(t[0, 1:, 2:].ndim, t[0:1, 1:, 2:].ndim)        # => (2, 3)

# ============================================
# Step — subsampling, for free

t[:, :, ::2].shape          # => (2, 3, 2)

t[:, :, ::2]
# => array([[[ 0,  2],
#            [ 4,  6],
#            [ 8, 10]],
#
#           [[12, 14],
#            [16, 18],
#            [20, 22]]])
#
# nothing was copied or moved. Look at the strides:

t.strides                   # => (96, 32, 8)
t[:, :, ::2].strides        # => (96, 32, 16)
#
# the innermost step doubled from 8 to 16 bytes. That IS
# the subsampling. Lesson 4's point, made concrete.

# ============================================
# Reverse — a negative stride

t[::-1].shape               # => (2, 3, 4)
t[::-1][0]
# => array([[12, 13, 14, 15],
#           [16, 17, 18, 19],
#           [20, 21, 22, 23]])      the second block, now first

t[:, :, ::-1][0, 0]         # => array([3, 2, 1, 0])

t[::-1].strides             # => (-96, 32, 8)
#
# a NEGATIVE stride. Reversal is free and still a view —
# unlike part 2's `m[::-1]`, which at least copied the
# outer list. Here nothing is copied at all.

np.shares_memory(t, t[::-1])                    # => True

# ============================================
# Out of range clips; empty is legal

t[0:99].shape               # => (2, 3, 4)      clipped, no error
t[5:9].shape                # => (0, 3, 4)      empty, still rank 3
t[5:9].size                 # => 0
#
# same behaviour as Python lists (part 2, lesson 24):
# an out-of-range INDEX raises, an out-of-range SLICE
# silently returns less. A size-0 axis is a valid shape
# and most operations handle it — but `.max()` on it
# raises, so check `.size` before reducing.

# ============================================
# EVERY basic slice is a VIEW

np.shares_memory(t, t[:, 1:3, :])       # => True
np.shares_memory(t, t[:, :, ::2])       # => True
np.shares_memory(t, t[::-1])            # => True

c = np.arange(24).reshape(2, 3, 4)
v = c[0, 1:3]
v[0, 0] = 99
c[0, 1, 0]                  # => 99      the original changed
#
# this is the aliasing trap from part 2 lesson 21, now
# the default for every slice. If you need independence:
#
#   safe = t[0, 1:3].copy()

# ============================================
# Assignment into a block

a = np.arange(24).reshape(2, 3, 4)
a[:, 0, :] = -1
a[0]
# => array([[-1, -1, -1, -1],
#           [ 4,  5,  6,  7],
#           [ 8,  9, 10, 11]])

b = np.arange(24).reshape(2, 3, 4)
b[0, 1:3, 1:3] = 0
b[0]
# => array([[ 0,  1,  2,  3],
#           [ 4,  0,  0,  7],
#           [ 8,  0,  0, 11]])
#
# the right-hand side broadcasts to fill the block
# (lesson 17). A scalar fills everything.

# ============================================
# Programmatic slicing — build the index tuple
#
# When the AXIS is a variable, you cannot write the
# colons literally. Use slice objects.

def axis_slice(t, axis, sl):
    idx = [slice(None)] * t.ndim        # all colons
    idx[axis] = sl                      # replace one
    return t[tuple(idx)]

axis_slice(t, 1, slice(1, 3)).shape             # => (2, 2, 4)
np.array_equal(axis_slice(t, 1, slice(1, 3)), t[:, 1:3, :])     # => True

axis_slice(t, 2, slice(0, 2)).shape             # => (2, 3, 2)
#
#   slice(None)        is  :
#   slice(1, 3)        is  1:3
#   slice(None,None,2) is  ::2
#
# and the tuple() matters — a LIST index means fancy
# indexing (lesson 10), which is a different operation.

s = (slice(None), slice(1, 3), slice(None, None, 2))
np.array_equal(t[s], t[:, 1:3, ::2])            # => True

# ============================================
# What nested lists cannot do
#
# Python lists slice one level at a time.

L = [[[0, 1], [2, 3]], [[4, 5], [6, 7]]]

L[0][0:1]                   # => [[0, 1]]       fine
# L[:, 0]                   -> TypeError: list indices must be
#                              integers or slices, not tuple
#
# to slice a nested list on axis 1 you must rebuild it:
[row[0:1] for row in L[0]]  # => [[0], [2]]
#
# NumPy slices every axis in one expression, and returns
# a view rather than a new list. This is the practical
# reason tensor code stops using nested lists.

# ============================================
# Two idioms worth memorising

# crop a border of width 1 (part 2, lesson 8)
t[:, 1:-1, 1:-1].shape      # => (2, 1, 2)

# adjacent differences along an axis
d = t[1:] - t[:-1]          # pairs consecutive slices
d.shape                     # => (1, 3, 4)
np.array_equal(d, np.diff(t, axis=0))           # => True
#
# `t[1:] - t[:-1]` is part 1's pairwise, vectorised.

# ============================================
# Compare

t[0]                # integer      -> rank 2,  view
t[0:1]              # slice        -> rank 3,  view
t[:, 1:3, ::2]      # per-axis     -> view
t[..., 0]           # ellipsis     -> view     (lesson 9)
t[:, None]          # newaxis      -> view     (lesson 9)
t[[0, 1]]           # integer LIST -> COPY     (lesson 10)
t[t > 5]            # boolean mask -> COPY     (lesson 11)

np.shares_memory(t, t[:, 1:3])          # => True
np.shares_memory(t, t[[0, 1]])          # => False
#
# the dividing line of this whole section: slices,
# integers, ellipsis and newaxis are "basic indexing"
# and give views. Arrays and masks are "advanced
# indexing" and give copies.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a sub-block|`t[a:b, c:d, e:f]`|
|a whole axis|`:`|
|to keep an axis|`t[0:1]`, not `t[0]`|
|every k-th|`::k`|
|reversal|`::-1` — a negative stride, still free|
|a border removed|`t[1:-1, 1:-1]`|
|adjacent differences|`t[1:] - t[:-1]`|
|a variable axis|`slice(None)` in a list, then `tuple()`|
|independence|`.copy()` — slices are views|

---

## Key Insight

**Basic slicing is metadata arithmetic, not data movement.** A slice produces a new `shape`, a new `strides` and an offset into the same buffer:

```text
t[:, :, ::2]    strides (96,32,8) -> (96,32,16)     step twice as far
t[::-1]         strides (96,32,8) -> (-96,32,8)     step backwards
```

Nothing is copied, which is why cropping, subsampling and reversing a gigabyte-sized array are all O(1) — and why writing through any of them changes the original.

Three rules carry most of the value:

1. **Integer consumes, slice keeps.** `t[0]` is rank 2; `t[0:1]` is rank 3. When a downstream function expects a fixed rank, this is the difference between working and raising.
    
2. **Slices clip, indices raise.** `t[0:99]` returns everything; `t[99]` raises. Inherited from Python lists, and it means an off-by-one in a slice fails silently.
    
3. **Every basic slice aliases.** `v = t[0, 1:3]; v[0,0] = 99` writes into `t`. Use `.copy()` when you need independence — and note that lessons 10 and 11 behave *oppositely*, which is worth memorising rather than deriving.
    

The idiom to take away for real code: when the axis is a **variable**, build the index tuple with `slice(None)` rather than trying to write colons dynamically — and remember to call `tuple()` on it, because a list index means something else entirely.

---

## The Slicing Section

|Lesson|Index type|Returns|
|---|---|---|
|**8 Basic Slicing**|slices, integers|**view**|
|9 Ellipsis and newaxis|`...`, `None`|**view**|
|10 Fancy Indexing|integer arrays|**copy**|
|11 Boolean Masking|boolean arrays|**copy**|

```text
  basic indexing     ──►  view   (shape + strides + offset)
  advanced indexing  ──►  copy   (gathers scattered elements)
```

> **Mental shift:** part 2's slicing was `row[c:c+k]` — one axis at a time, always producing new lists. Here every axis is sliced in one expression and nothing is built. Once you internalise that a slice is free and shared, the question stops being "is this fast enough?" and becomes "did I mean to alias that?"
