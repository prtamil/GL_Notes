# Part 3 — Tensor Patterns

# 1. Shape and Rank

## Mental Model

A tensor is an **n-dimensional array**, and two numbers describe it completely:

- **Rank** (`ndim`) — how many indices it takes to reach an element.
    
- **Shape** — how far each index can go, as a tuple with one entry per axis.
    

```text
rank 0   scalar   5                    shape ()
rank 1   vector   [1, 2, 3]            shape (3,)
rank 2   matrix   [[1,2],[3,4]]        shape (2, 2)
rank 3   cube     [[[...]]]            shape (2, 3, 4)
```

The shape tuple is the most useful object in this whole part of the course. **Rank is its length, size is its product**, and every operation in part 3 is described by what it does to that tuple:

```text
(2, 3, 4)   ndim = 3      size = 2*3*4 = 24
 ↑  ↑  ↑
 |  |  └── axis 2, innermost
 |  └───── axis 1
 └──────── axis 0, outermost
```

In nested lists, **rank is nesting depth** and **shape is the length at each level**. That is the whole correspondence, and it is why `len(t) == t.shape[0]` — `len` only ever sees the outermost list.

One requirement separates a tensor from a nested list: it must be **rectangular**. Every sublist at a given depth must have the same length. Ragged data is not a tensor and NumPy will refuse it.

---

## Relationship to Cognitive Verb

```text
Describe
   ↓
Shape and Rank
```

Related verbs:

- Describe
- Measure
- Characterise
- State the dimensions
- Check the form

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Rank|how many axes|`t.ndim`|
|Shape|size of each axis|`t.shape`|
|Element count|total cells|`t.size`|
|Outer length|first axis only|`len(t)`|
|Element type|homogeneous|`t.dtype`|
|Bytes|memory used|`t.nbytes`, `t.itemsize`|
|Shape from nested lists|derive it|walk `len(x)` while `isinstance(x, list)`|
|Rank from nested lists|derive it|count the nesting levels|
|Rectangularity check|is it a tensor?|recursive length check|
|Reshape|same size, new shape|`t.reshape(...)`, `-1` infers one axis|

---

## Common Uses

- Validating input dimensions before a computation
- Debugging shape mismatches (most tensor bugs)
- Batching: turning `(H, W)` into `(N, H, W)`
- Describing model inputs and outputs
- Choosing which axis an operation should act on
- Converting between data layouts
- Memory estimation

---

## Hidden Interview Problems

- Determine the dimensions of a nested list
- Validate that a nested list is rectangular
- Compute the total number of elements
- Check whether two tensors can be broadcast
- Reshape a flat list into given dimensions
- Find the rank of an arbitrarily nested structure
- Detect a ragged array

---

## Recognition Clues

If you hear...

- "n-dimensional..."
- "the shape is..."
- "batch of images..."
- "rank / order of the tensor..."
- "dimensions don't match..."
- "how many elements..."

...think **Shape and Rank**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Rank|`len(shape)` — number of axes|
|Shape|A tuple, one entry per axis|
|Size|`prod(shape)`|
|Rank 0|Shape `()`, size **1** — a scalar is not empty|
|`len(t)`|`shape[0]` only — never the total|
|Requirement|Rectangular; ragged data is not a tensor|
|Element type|Homogeneous — one `dtype` for the whole array|
|Time Complexity|O(1) to read shape; O(rank) to derive from lists|
|Common Domains|ML, scientific computing, images, video|

---

## Python Recipe Book

```python
# ============================================
# The running example — 2 x 3 x 4
#
# All three dimensions DIFFER on purpose. With a 2x2x2
# an axis bug is invisible; with 2x3x4 every mistake
# shows up as a wrong shape immediately.

import numpy as np
from math import prod

t = np.arange(24).reshape(2, 3, 4)

t
# => array([[[ 0,  1,  2,  3],
#            [ 4,  5,  6,  7],
#            [ 8,  9, 10, 11]],
#
#           [[12, 13, 14, 15],
#            [16, 17, 18, 19],
#            [20, 21, 22, 23]]])
#
# read it as: 2 blocks, each 3 rows of 4 columns.

nested = t.tolist()
# => [[[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]],
#     [[12, 13, 14, 15], [16, 17, 18, 19], [20, 21, 22, 23]]]

# ============================================
# The one idiom to remember
#
#   t.shape
#
# Everything else is derived from it.

t.shape                     # => (2, 3, 4)
t.ndim                      # => 3          == len(t.shape)
t.size                      # => 24         == prod(t.shape)

t.size == prod(t.shape)     # => True
t.ndim == len(t.shape)      # => True

# ============================================
# len() is NOT the size — a very common slip

len(t)                      # => 2      the FIRST axis only
t.size                      # => 24     every element

len(t) == t.shape[0]        # => True
#
# len() cannot see past the outer list. On a 2x3x4 it
# returns 2. If you want the element count, say .size.

# ============================================
# Deriving shape from nested lists
#
# Walk down the first element, recording lengths.
# Depth is rank; the lengths are the shape.

def shape_of(x):
    s = []
    while isinstance(x, list):
        s.append(len(x))
        x = x[0]
    return tuple(s)

shape_of(nested)            # => (2, 3, 4)
shape_of(nested) == t.shape # => True

def rank_of(x):
    n = 0
    while isinstance(x, list):
        n += 1
        x = x[0]
    return n

rank_of(nested)             # => 3
#
# this is exactly what NumPy does when you call
# np.array() on a nested list — and why it only looks
# at x[0] to guess, then validates the rest.

# ============================================
# The ranks, in order

np.array(5).shape           # => ()         rank 0, a scalar
np.array(5).ndim            # => 0
np.array(5).size            # => 1          <- ONE element, not zero

np.array([1, 2, 3]).shape           # => (3,)       rank 1
np.array([[1,2,3],[4,5,6]]).shape   # => (2, 3)     rank 2
np.array([[[1,2],[3,4]]]).shape     # => (1, 2, 2)  rank 3
np.zeros((2,3,4,5)).shape           # => (2,3,4,5)  rank 4

# note (3,) — the trailing comma is Python tuple syntax,
# not a typo. (3) is the integer 3; (3,) is a 1-tuple.

# ============================================
# A tensor must be RECTANGULAR

try:
    np.array([[1, 2, 3], [4, 5]])
except ValueError as e:
    print(e)
# setting an array element with a sequence. The requested
# array has an inhomogeneous shape after 1 dimensions...
#
# ragged data is not a tensor. Pad it, or keep a list of
# arrays — but you cannot have one array.

def is_rect(x):
    if not isinstance(x, list) or not x:
        return True
    if isinstance(x[0], list):
        n = len(x[0])
        return all(isinstance(e, list) and len(e) == n and is_rect(e) for e in x)
    return all(not isinstance(e, list) for e in x)

is_rect(nested)                     # => True
is_rect([[1, 2, 3], [4, 5]])        # => False   different lengths
is_rect([[1, 2], [3, [4]]])         # => False   mixed depth
#
# note shape_of() would happily return (2, 3) for the
# ragged list — it only looks at x[0]. Deriving a shape
# and VALIDATING a shape are different jobs.

# ============================================
# One dtype for the whole array
#
# A tensor is homogeneous. Mixed input gets coerced to
# the type that holds everything.

np.array([1, 2, 3]).dtype           # => dtype('int64')
np.array([1, 2.5, 3]).dtype         # => dtype('float64')   int promoted
np.array([True, 2]).dtype           # => dtype('int64')     bool promoted
np.array([1, "a"]).dtype            # => dtype('<U21')      everything -> string!
#
# that last one is the trap: one stray string turns your
# numeric array into text, silently, and arithmetic then
# fails somewhere far away.

t.dtype                             # => dtype('int64')
t.itemsize                          # => 8      bytes per element
t.nbytes                            # => 192    == size * itemsize
#
# itemsize is dtype-dependent: int32 would give 4 and
# nbytes 96. Never hard-code 8.

# ============================================
# Reshape — the size must be conserved

t.reshape(4, 6).shape       # => (4, 6)     24 == 4*6
t.reshape(24).shape         # => (24,)
t.reshape(2, 2, 3, 2).shape # => (2, 2, 3, 2)

try:
    t.reshape(5, 5)
except ValueError as e:
    print(e)
# cannot reshape array of size 24 into shape (5,5)

# -1 means "work this one out"
t.reshape(2, -1).shape      # => (2, 12)
t.reshape(-1, 4).shape      # => (6, 4)
#
# only ONE axis may be -1, for the obvious reason.
# (Lesson 12 covers reshape properly.)

# ============================================
# Reading a shape in context
#
# The numbers are meaningless without a convention.
# State it, in a comment or a variable name.

batch = np.zeros((32, 3, 224, 224))     # N, C, H, W
batch.shape                             # => (32, 3, 224, 224)
#
#   32   images in the batch
#    3   colour channels
#  224   height
#  224   width
#
# the SAME numbers as (32, 224, 224, 3) mean a different
# layout (NHWC). Shape tells you the sizes; only the
# convention tells you the meaning. This is lesson 2.

# ============================================
# Compare — ranks 1, 2, 3

v = np.array([1, 2, 3])                 # (3,)
m = np.array([[1, 2, 3], [4, 5, 6]])    # (2, 3)

v.shape, v.ndim, v.size     # => ((3,),     1, 3)
m.shape, m.ndim, m.size     # => ((2, 3),   2, 6)
t.shape, t.ndim, t.size     # => ((2,3,4),  3, 24)
#
# part 1 lived at rank 1, part 2 at rank 2, and this
# part leaves the rank open. Nothing else changes.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the shape|`t.shape` — a tuple, one entry per axis|
|the rank|`t.ndim` == `len(t.shape)`|
|the element count|`t.size` == `prod(t.shape)`|
|**not** the element count|`len(t)` — that's `shape[0]` only|
|shape from nested lists|walk `len(x)` while it's a list|
|to know it's a real tensor|check it's rectangular, not just deep|
|bytes|`t.nbytes` == `size * itemsize`|
|a shape with one axis unknown|`-1`|
|to know what the axes mean|a comment — the shape won't tell you|

---

## Key Insight

**The shape tuple is the type of a tensor.** Rank is its length, size is its product, and every operation in part 3 is best understood as a transformation of it:

```text
reshape      (2,3,4) -> (4,6)        same size, new grouping
transpose    (2,3,4) -> (4,3,2)      same axes, reordered
sum(axis=1)  (2,3,4) -> (2,4)        one axis removed
stack        (2,3,4) -> (5,2,3,4)    one axis added
```

Learn to predict the output shape *before* running the code and most tensor bugs disappear, because most tensor bugs are shape bugs that surface three functions later.

Three things worth fixing in memory:

1. **`len(t)` is `shape[0]`, not `size`.** It cannot see past the outermost axis. On a `(2,3,4)` it returns `2`.
    
2. **Rank 0 has size 1.** A scalar array has shape `()` — an empty tuple, whose product is 1. It is a container of one element, not an empty one.
    
3. **Rectangular, and one dtype.** Ragged nesting is not a tensor at all, and mixed types get coerced — `np.array([1, "a"])` silently becomes an array of *strings*, which then fails somewhere unrelated.
    

And the discipline that pays for itself: **a shape does not carry meaning.** `(32, 3, 224, 224)` and `(32, 224, 224, 3)` hold identical data under different conventions. Write the convention down.

---

## The Foundations Section

|Lesson|Question|
|---|---|
|**1 Shape and Rank**|*How big is it, in each direction?*|
|2 Axes|*Which direction is which, and what does "along" mean?*|
|3 Indexing|*How do I reach one element, or a sub-tensor?*|
|4 Strides|*Where does it actually live in memory?*|

```text
  shape  ──►  axes  ──►  indexing  ──►  strides
  "how big"   "which"    "reach it"     "where in memory"
```

> **Mental shift:** part 1 had one length, part 2 had two. Once there are `n` of them, the sizes stop being something you hold in your head and become an object you inspect: `t.shape`. Print it constantly. It's the fastest debugger you have in this part of the course.
