# 27. Tile and Repeat

## Mental Model

Both replicate data. They differ in **what** they replicate, and the difference is the entire lesson:

```text
r = [1, 2, 3]

np.tile(r, 2)     ->  [1, 2, 3, 1, 2, 3]      the whole array, twice
np.repeat(r, 2)   ->  [1, 1, 2, 2, 3, 3]      each element, twice
```

```text
tile:    A B C  A B C        blocks side by side
repeat:  A A  B B  C C       each item duplicated in place
```

`tile` is concatenating an array with itself. `repeat` is stretching it elementwise. On a 2-D image the two produce visibly different pictures — `tile` gives you a 2×2 mosaic of the original, `repeat` gives you the original at double resolution.

And both are the *materialised* version of something you have already seen for free:

> `np.tile(r, (3, 1))` and `np.broadcast_to(r, (3, 3))` hold the same values — but tile **allocates** and broadcast_to is a **stride-0 view** (lesson 17).

So the real decision is usually not "tile or repeat" but "do I need a real copy at all?" If the replicated array is only going to be read — added, multiplied, compared — broadcasting already did it, for free.

---

## Relationship to Cognitive Verb

```text
Replicate
    ↓
Tile and Repeat
```

Related verbs:

- Replicate
- Duplicate
- Stretch
- Upsample
- Pave

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Whole array, n times|blocks|`np.tile(a, reps)`|
|Each element, n times|in place|`np.repeat(a, n, axis=k)`|
|Per-element counts|variable|`np.repeat(a, [n0, n1, ...], axis=k)`|
|Repeat, flattened|no axis|`np.repeat(a, n)` — **drops the shape**|
|Upsample 2× in 2-D|nearest neighbour|`repeat` on both axes|
|A mosaic|pattern|`np.tile(a, (2, 2))`|
|**Without copying**|read-only|`np.broadcast_to(a, shape)`|
|Equivalent to tile|explicit|`np.concatenate([a] * n, axis=k)`|
|Reps shorter than rank|left-padded with 1s|`np.tile(a, 2)` ≡ `np.tile(a, (1, 2))`|

---

## Common Uses

- Nearest-neighbour upsampling of an image or mask
- Building a repeating texture or checkerboard
- Expanding a per-sample value to per-timestep
- Duplicating rows to match class weights
- Creating test data with a known pattern
- Materialising a broadcast when you need to write to it
- Paving a small kernel across a grid

---

## Hidden Interview Problems

- Upsample a matrix by a factor of 2
- Repeat each row n times
- Build a repeating tile pattern
- Duplicate elements with per-element counts
- Explain the difference between `tile` and `repeat`
- Explain when to use `broadcast_to` instead

---

## Recognition Clues

If you hear...

- "repeat each element..."
- "duplicate the rows..."
- "upsample / nearest neighbour..."
- "tile the pattern..."
- "expand to match..."

...think **Tile and Repeat**.

---

## Pattern Summary

|Property|`np.tile`|`np.repeat`|
|---|---|---|
|Replicates|the **whole array**|each **element**|
|Argument|`reps` per axis|a count, plus `axis`|
|Rank|can **increase**|unchanged (unless `axis=None`)|
|No axis given|reps left-padded with 1s|**flattens** the result|
|Variable counts|no|**yes** — a list per element|
|Equivalent to|`concatenate([a]*n, axis=k)`|elementwise stretch|
|Memory|**copy**|**copy**|
|Free alternative|`np.broadcast_to`|—|

---

## Python Recipe Book

```python
# ============================================
# The one difference to remember

import numpy as np

r = np.array([1, 2, 3])

np.tile(r, 2)               # => array([1, 2, 3, 1, 2, 3])
np.repeat(r, 2)             # => array([1, 1, 2, 2, 3, 3])
#
#   tile    the sequence, again
#   repeat  each item, again
#
# if you remember nothing else from this lesson,
# remember those two outputs.

# ============================================
# tile: reps is per-axis

np.tile(r, (2, 1))
# => array([[1, 2, 3],
#           [1, 2, 3]])          2 copies down, 1 across

np.tile(r, (2, 2))
# => array([[1, 2, 3, 1, 2, 3],
#           [1, 2, 3, 1, 2, 3]])
np.tile(r, (2, 2)).shape        # => (2, 6)

# reps SHORTER than the rank are left-padded with 1s:
a = np.arange(6).reshape(2, 3)
np.tile(a, 2).shape                             # => (2, 6)
np.array_equal(np.tile(a, 2), np.tile(a, (1, 2)))               # => True
#
# `np.tile(a, 2)` tiles the LAST axis, not the first —
# a frequent surprise. Write the full tuple.

# reps LONGER than the rank add new axes:
np.tile(a, (2, 1, 1)).shape                     # => (2, 2, 3)
#
# so tile can raise the rank; repeat cannot.

np.tile(a, (2, 1))
# => array([[0, 1, 2],
#           [3, 4, 5],
#           [0, 1, 2],
#           [3, 4, 5]])          the whole matrix, stacked

np.tile(a, (1, 2))
# => array([[0, 1, 2, 0, 1, 2],
#           [3, 4, 5, 3, 4, 5]])

# and tiling along one axis IS self-concatenation:
np.array_equal(np.tile(a, (2, 1)), np.concatenate([a, a], axis=0))   # => True

# ============================================
# repeat: a count, and an axis

np.repeat(a, 2, axis=0)
# => array([[0, 1, 2],
#           [0, 1, 2],
#           [3, 4, 5],
#           [3, 4, 5]])          each ROW duplicated in place

np.repeat(a, 2, axis=1)
# => array([[0, 0, 1, 1, 2, 2],
#           [3, 3, 4, 4, 5, 5]])  each COLUMN duplicated in place

# compare with tile on the same axis:
np.array_equal(np.repeat(a, 2, axis=0), np.tile(a, (2, 1)))     # => False
#
#   repeat(axis=0):  row0 row0 row1 row1
#   tile((2,1)):     row0 row1 row0 row1
#
# the elements are the same; the ORDER is not.

# WITHOUT an axis, repeat flattens:
np.repeat(a, 2)                 # => array([0,0,1,1,2,2,3,3,4,4,5,5])
np.repeat(a, 2).shape           # => (12,)
#
# it does not preserve the shape. Always pass `axis=`
# unless you want a flat result.

# ============================================
# repeat accepts PER-ELEMENT counts — tile cannot

np.repeat(r, [1, 2, 3])         # => array([1, 2, 2, 3, 3, 3])

np.repeat(a, [1, 2], axis=0)
# => array([[0, 1, 2],
#           [3, 4, 5],
#           [3, 4, 5]])          row 0 once, row 1 twice
#
# this is how you oversample a class, or expand
# variable-length groups. The count list must have one
# entry per element along the axis.

# ============================================
# THE APPLICATION: upsampling vs mosaicking

img = np.array([[1, 2],
                [3, 4]])

# nearest-neighbour 2x upsample — repeat BOTH axes
np.repeat(np.repeat(img, 2, axis=0), 2, axis=1)
# => array([[1, 1, 2, 2],
#           [1, 1, 2, 2],
#           [3, 3, 4, 4],
#           [3, 3, 4, 4]])
#    the same picture, twice the size

# a 2x2 mosaic — tile
np.tile(img, (2, 2))
# => array([[1, 2, 1, 2],
#           [3, 4, 3, 4],
#           [1, 2, 1, 2],
#           [3, 4, 3, 4]])
#    four copies of the picture
#
# SAME SHAPE (4,4), completely different result. This is
# the clearest demonstration of the distinction — if you
# ever forget which is which, upsample a 2x2.

# ============================================
# ...BUT CHECK WHETHER YOU NEED THE COPY AT ALL

np.array_equal(np.tile(r, (3, 1)), np.broadcast_to(r, (3, 3)))  # => True

np.shares_memory(r, np.tile(r, (3, 1)))                 # => False   copy
np.shares_memory(r, np.broadcast_to(r, (3, 3)))         # => True    view

np.tile(r, (1000, 1)).nbytes                            # => 24000
np.broadcast_to(r, (1000, 3)).base.nbytes               # => 24
#
# a thousand-fold difference. `broadcast_to` is a
# stride-0 view (lesson 17): the "copies" are the same
# memory.
#
# Use broadcast_to when the result is READ-ONLY —
# which covers every arithmetic use:
#
#   a + np.tile(b, (n, 1))      wasteful
#   a + b                       broadcasting already does it
#
# Use tile when you need to WRITE to the copies, or when
# a library demands a real contiguous array.

# ============================================
# On rank 3

t = np.arange(24).reshape(2, 3, 4)

np.tile(t, (2, 1, 1)).shape         # => (4, 3, 4)
np.repeat(t, 2, axis=0).shape       # => (4, 3, 4)
np.repeat(t, 2, axis=2).shape       # => (2, 3, 8)
#
# same shapes for the first two, different ordering —
# tile gives block0 block1 block0 block1, repeat gives
# block0 block0 block1 block1.

# ============================================
# Practical: expand a per-sample value to per-timestep

per_sample = np.array([10, 20])                 # one value per sample
T = 3

np.repeat(per_sample[:, None], T, axis=1)
# => array([[10, 10, 10],
#           [20, 20, 20]])
#
# ...but if you are only going to add it, don't:
seq = np.arange(6).reshape(2, 3)
seq + per_sample[:, None]
# => array([[10, 11, 12],
#           [23, 24, 25]])
#
# broadcasting again. The explicit repeat is only needed
# when the expanded array must exist in its own right.

# ============================================
# Compare

np.tile(a, (2, 1))              # whole array, stacked    -> (4, 3)
np.repeat(a, 2, axis=0)         # each row, doubled       -> (4, 3)
np.concatenate([a, a], axis=0)  # == tile((2,1))          -> (4, 3)
np.stack([a, a])                # a NEW axis              -> (2, 2, 3)
np.broadcast_to(a, (2, 2, 3))   # a new axis, FREE        -> (2, 2, 3)

[np.tile(a, (2, 1)).shape,
 np.repeat(a, 2, axis=0).shape,
 np.stack([a, a]).shape,
 np.broadcast_to(a, (2, 2, 3)).shape]
# => [(4, 3), (4, 3), (2, 2, 3), (2, 2, 3)]
#
# the last two agree in shape; only one of them allocates.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the whole array again|`np.tile(a, reps)`|
|each element again|`np.repeat(a, n, axis=k)`|
|to remember which|upsample a 2×2: `repeat` doubles the picture, `tile` makes four|
|per-element counts|`np.repeat(a, [n0, n1], axis=k)`|
|the shape preserved|pass `axis=` to `repeat` — it flattens without one|
|`tile` on the first axis|write the **full tuple**; a bare int hits the last axis|
|**no copy**|`np.broadcast_to` — or just let broadcasting do it|
|a real writable copy|`tile`, or `np.broadcast_to(...).copy()`|

---

## Key Insight

**`tile` replicates the array; `repeat` replicates the elements.**

```text
tile:    A B C  A B C
repeat:  A A  B B  C C
```

The 2×2 upsample is the clearest test case: `repeat` on both axes gives the same picture at double resolution, `tile` gives a 2×2 mosaic. Identical shapes, completely different data, and neither raises.

Three secondary points:

1. **`repeat` takes per-element counts; `tile` does not.** `np.repeat(a, [1, 2], axis=0)` keeps row 0 once and row 1 twice — the tool for oversampling a class or expanding variable-length groups.
    
2. **Watch the argument shapes.** `np.tile(a, 2)` left-pads the reps, so it tiles the *last* axis — write the full tuple. And `np.repeat(a, 2)` without an axis **flattens** the result.
    
3. **Ask whether you need a copy at all.** `np.tile(r, (1000,1))` allocates 24,000 bytes; `np.broadcast_to(r, (1000,3))` is a stride-0 view over 24. Every arithmetic use — adding, scaling, comparing — is already handled by broadcasting (lesson 17). Materialise only when you must *write* to the result, or when a library requires a contiguous array.
    

That third point is the one that matters in real code: `a + np.tile(b, (n, 1))` and `a + b` compute the same thing, and only one of them allocates.

---

## The Combination Section, Complete

|Lesson|Operation|Rank|Memory|
|---|---|---|---|
|24 Concatenate|join on an existing axis|unchanged|copy|
|25 Stack|join on a **new** axis|**+1**|copy|
|26 Split|divide along an axis|unchanged|**view**|
|**27 Tile / Repeat**|join with itself|unchanged (tile can raise it)|copy|

```text
                 ┌── existing axis  ──►  24 concatenate
   join      ────┤
                 └── new axis       ──►  25 stack

   divide    ────────────────────────►  26 split       (free)

                 ┌── whole array    ──►  27 tile
   replicate ────┤
                 └── each element   ──►  27 repeat
```

The memory story is the section's real theme: **joining costs, dividing is free.** Concatenate, stack and tile must allocate, because separate buffers cannot be described by one stride pattern. Split is slicing, so it costs nothing. And `broadcast_to` sits outside the table entirely — replication with no memory at all, which is why lesson 17 comes before this one.

> **Mental shift:** parts 1 and 2 joined things with `+` and `extend`, and the only question was order. At rank 3+ every join needs an axis, every axis choice changes the meaning, and the same operation can be free or expensive depending on whether you actually need the bytes. "Which axis, and do I need a copy?" is the whole of tensor combination.
