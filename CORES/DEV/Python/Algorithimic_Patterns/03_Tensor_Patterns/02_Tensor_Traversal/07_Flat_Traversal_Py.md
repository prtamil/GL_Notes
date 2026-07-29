# 7. Flat Traversal

## Mental Model

The last granularity: forget the shape entirely and walk the tensor as **one long sequence**.

```text
shape (2, 3, 4)   ->   0 1 2 3 4 5 6 7 8 ... 23
```

Lesson 4 established that this is not a transformation at all — it is what the tensor already **is** in memory. Flat traversal just stops pretending there is nesting.

```python
t.ravel()       # a 1-D view — no copy when possible
t.flat          # an iterator over the same
```

Two things make this lesson more than "call `.ravel()`".

**First, order.** Row-major (C) order means the *last* index varies fastest, and that is what `ravel()` gives you by default. `order='F'` reverses the priority. On a `(2,3,4)` those are genuinely different sequences.

**Second — and this is the subtle one — "flat" is ambiguous once views exist.** A transposed array has a *logical* order (what its shape says) and a *memory* order (what the buffer holds). They are no longer the same:

```text
tr = t.transpose(2,1,0)

tr.ravel()            -> 0, 12, 4, 16, ...     logical order (may copy)
np.nditer(tr)         -> 0,  1, 2,  3, ...     memory order (never copies)
```

Both are "iterating flat". They visit the same 24 values in different sequences. Knowing which one a function gives you is the difference between correct and subtly wrong.

---

## Relationship to Cognitive Verb

```text
Linearise
    ↓
Flat Traversal
```

Related verbs:

- Linearise
- Flatten
- Stream the buffer
- Read end to end
- Forget the shape

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Flat view|no copy when possible|`t.ravel()`|
|Flat copy|always independent|`t.flatten()`|
|Flat iterator|no array built|`t.flat`|
|Index it directly|flat indexing|`t.flat[i]`|
|Column-major|Fortran order|`t.ravel(order='F')`|
|Memory order|whatever the strides say|`t.ravel(order='K')`, `np.nditer(t)`|
|Flat → coordinates|convert|`np.unravel_index(i, shape)`|
|Coordinates → flat|convert|`np.ravel_multi_index(idx, shape)`|
|Nested lists|comprehension|`[x for a in n for b in a for x in b]`|
|Back to shape|the inverse|`flat.reshape(shape)`|

---

## Common Uses

- Serialising a tensor to a file or over a network
- Hashing or comparing whole tensors
- Applying a 1-D algorithm (`sort`, `bisect`, `Counter`)
- Feeding a flat feature vector to a model
- Converting between flat and multi-dimensional indices
- Global statistics regardless of shape
- Interfacing with C or GPU buffers that expect contiguous data

---

## Hidden Interview Problems

- Flatten an n-dimensional array
- Convert a flat index to a multi-index and back
- Find the k-th element in row-major order
- Binary search a sorted n-D array
- Serialise and deserialise a tensor
- Explain the difference between `ravel` and `flatten`
- Explain why iteration order differs after a transpose

---

## Pattern Summary

|Property|Value|
|---|---|
|Result rank|1 — always|
|Length|`t.size`|
|Default order|C / row-major — last index fastest|
|`ravel()`|A **view** when contiguous, a copy otherwise|
|`flatten()`|**Always** a copy|
|`t.flat`|An iterator (`flatiter`), builds nothing|
|`nditer`|**Memory** order, not logical order|
|Information lost|The shape — keep it to reverse the operation|
|Time Complexity|O(1) for a view, O(size) for a copy|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np

t = np.arange(24).reshape(2, 3, 4)
nested = t.tolist()

# ============================================
# The one idiom to remember
#
#   t.ravel()      flat, and free when it can be

t.ravel()
# => array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11,
#           12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23])

t.ravel().shape             # => (24,)
np.shares_memory(t, t.ravel())          # => True    a VIEW

# ============================================
# ravel vs flatten vs flat — three different things

np.shares_memory(t, t.ravel())          # => True    view when possible
np.shares_memory(t, t.flatten())        # => False   always a copy

type(t.flat).__name__                   # => 'flatiter'
[int(x) for x in list(t.flat)[:5]]      # => [0, 1, 2, 3, 4]
#
#   ravel()    an ARRAY, usually a view
#   flatten()  an ARRAY, always a copy
#   .flat      an ITERATOR — no array is built at all

# and the sharing is observable:
a = np.arange(24).reshape(2, 3, 4)
a.ravel()[5] = 88
a[0, 1, 1]                  # => 88     wrote through

b = np.arange(24).reshape(2, 3, 4)
b.flatten()[5] = 77
b[0, 1, 1]                  # => 5      unchanged — you edited a copy
#
# `x.flatten()[i] = v` is a silent no-op. It is one of
# the most confusing bugs in NumPy because nothing raises.

c = np.arange(24).reshape(2, 3, 4)
c.flat[0] = 99
c[0, 0, 0]                  # => 99     .flat assigns in place

# ============================================
# Flat indexing without building anything

int(t.flat[23])                         # => 23
[int(t.flat[i]) for i in (0, 5, 23)]    # => [0, 5, 23]
#
# .flat[i] reads one element by flat index — no
# intermediate array, unlike t.ravel()[i].

# ============================================
# The pure-Python version — part 2's lesson 23

[x for a1 in nested for a2 in a1 for x in a2][:6]
# => [0, 1, 2, 3, 4, 5]

[x for a1 in nested for a2 in a1 for x in a2] == t.ravel().tolist()     # => True
#
# ...but note it hard-codes rank 3. The rank-agnostic
# version is the recursion from lesson 6.

# ============================================
# ORDER: C vs F
#
# C order: the LAST index varies fastest.
# F order: the FIRST index varies fastest.

t.ravel(order='C')[:8]      # => array([0, 1, 2, 3, 4, 5, 6, 7])
t.ravel(order='F')[:8]      # => array([ 0, 12,  4, 16,  8, 20,  1, 13])

t.ravel(order='F').tolist()
# => [0, 12, 4, 16, 8, 20, 1, 13, 5, 17, 9, 21,
#     2, 14, 6, 18, 10, 22, 3, 15, 7, 19, 11, 23]
#
# read the F sequence: axis 0 first (0 -> 12), then
# axis 1 (0 -> 4), then axis 2. Exactly backwards.

# F order is the same as flattening the full transpose:
np.array_equal(t.ravel(order='F'), t.T.ravel())         # => True
t.T.shape                                               # => (4, 3, 2)
#
# `.T` reverses ALL axes on a rank-n array — not just
# the last two. On rank 3 it is transpose(2,1,0).
#
# This is part 2 lesson 22's row-major/column-major
# distinction, unchanged. Fortran, MATLAB and R default
# to F; Python, C and image formats default to C.

# ============================================
# THE SUBTLE PART: logical order vs memory order
#
# After a transpose, "flat" has two meanings.

tr = t.transpose(2, 1, 0)
tr.shape                    # => (4, 3, 2)

tr.ravel()[:8]              # => array([ 0, 12,  4, 16,  8, 20,  1, 13])
#   LOGICAL order — what tr's shape says it contains.
#   The buffer is not in this order, so this COPIES:
np.shares_memory(tr, tr.ravel())        # => False

tr.ravel(order='K')[:8]     # => array([0, 1, 2, 3, 4, 5, 6, 7])
tr.ravel(order='A')[:8]     # => array([0, 1, 2, 3, 4, 5, 6, 7])
#   MEMORY order — the buffer as it actually lies.

[int(x) for x in list(np.nditer(tr))[:8]]
# => [0, 1, 2, 3, 4, 5, 6, 7]
#   nditer also walks MEMORY order by default.

[int(x) for x in np.nditer(tr)] == tr.ravel().tolist()      # => False
#
# Same 24 values, two different sequences. If you only
# need a sum or a count, memory order is faster and the
# answer is identical. If the ORDER matters — writing to
# a file, comparing sequences, reshaping — you want
# ravel()'s logical order and must accept the copy.
#
#   order='C'  logical, row-major        (default)
#   order='F'  logical, column-major
#   order='K'  whatever the strides say  (never copies)

# on a contiguous array the distinction vanishes:
np.array_equal(t.ravel(), t.ravel(order='K'))               # => True

# ============================================
# Flat index <-> coordinates
#
# The pair from lesson 4, which is what makes flat
# traversal reversible.

[tuple(int(x) for x in np.unravel_index(i, t.shape)) for i in (0, 5, 23)]
# => [(0, 0, 0), (0, 1, 1), (1, 2, 3)]

[int(np.ravel_multi_index(idx, t.shape))
 for idx in [(0, 0, 0), (0, 1, 1), (1, 2, 3)]]
# => [0, 5, 23]

all(np.ravel_multi_index(np.unravel_index(i, t.shape), t.shape) == i
    for i in range(24))                                     # => True

# ============================================
# Why bother: 1-D tools on n-D data

sorted(t.ravel())[-3:]                  # => [21, 22, 23]
int(t.ravel().max())                    # => 23
int(sum(t.flat))                        # => 276
int(t.sum())                            # => 276     the fast way

# hashing a tensor — arrays are unhashable, tuples are not
key = tuple(t.ravel().tolist())
len(key)                                # => 24
#
# same requirement as part 2's lesson 23. Add the shape
# if two tensors could flatten identically:
key2 = (t.shape, tuple(t.ravel().tolist()))

# ============================================
# The inverse — flatten discards the shape

flat = t.ravel()
flat.reshape(2, 3, 4).shape             # => (2, 3, 4)
np.array_equal(flat.reshape(2, 3, 4), t)                    # => True
#
# 24 values are equally a (24,), (2,12), (4,6), (2,3,4)
# or (2,2,3,2). Store the shape alongside the data or
# the round trip is guesswork.

# ============================================
# Compare — the three traversal granularities

[s.shape for s in t]                            # lesson 5: sub-tensors
list(np.ndenumerate(t))[:2]                     # lesson 6: coords + values
t.ravel()[:2]                                   # this lesson: values

# all three agree on order:
[t[idx] for idx in np.ndindex(*t.shape)] == t.ravel().tolist()      # => True

# and all three are usually the wrong tool:
t.sum(axis=(1, 2))                              # lesson 20 — no traversal
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|flat, cheap|`t.ravel()`|
|flat, guaranteed independent|`t.flatten()`|
|flat, no array built|`t.flat`|
|one element by flat index|`t.flat[i]`|
|column-major|`order='F'`|
|memory order, never a copy|`order='K'` or `np.nditer`|
|flat index → coordinates|`np.unravel_index(i, shape)`|
|coordinates → flat index|`np.ravel_multi_index(idx, shape)`|
|the shape back|store it — flattening discards it|
|**not** to write|`x.flatten()[i] = v` — edits a copy, silently|

---

## Key Insight

**Flattening is not a transformation — it is the tensor's actual memory layout, made visible.** Lesson 4 established that; this lesson is about the two things that complicate it.

**Order.** C order (last index fastest) is the default and matches `np.ndindex`, `np.ndenumerate` and part 2's flatten. F order reverses the priority and equals `t.T.ravel()` — note that `.T` reverses *all* axes at rank 3+, not just the last two.

**Logical versus memory order.** Once views exist, "flat" is ambiguous:

```text
tr.ravel()        0, 12, 4, 16, ...     what the SHAPE says   (copies here)
np.nditer(tr)     0,  1, 2,  3, ...     what the BUFFER holds (never copies)
```

They agree on contiguous data and diverge after a transpose. Use memory order for order-independent work (sums, counts, maxima) and logical order whenever the sequence itself matters.

Three practical rules:

1. **`ravel` is a view, `flatten` is a copy, `.flat` is an iterator.** Pick by whether you need sharing, safety, or neither.
    
2. **`x.flatten()[i] = v` does nothing** and raises nothing. Use `x.flat[i] = v` or `x.ravel()[i] = v`.
    
3. **Flattening discards the shape.** 24 values are equally `(24,)`, `(4,6)` or `(2,3,4)` — store the shape with the data.
    

---

## The Traversal Section, Complete

|Lesson|Each step yields|Order|Rank-agnostic|
|---|---|---|---|
|5 Axis Iteration|a sub-tensor (rank − 1)|along one axis|via `moveaxis`|
|6 Nested Traversal|a coordinate **and** a value|row-major|via `ndindex`|
|**7 Flat Traversal**|a value|row-major, or memory|inherently|

```text
        peel one axis   ──►  05   ▢ ▢
  t  ─┤ peel all axes   ──►  06   (i,j,k) → v
        peel the shape  ──►  07   v v v v v ...
```

All three visit the same cells in the same order — verified. They differ only in **how much structure survives each step**.

> **Mental shift:** part 2's traversal section was eight lessons about *order*, because at rank 2 the interesting question was which path you took through the grid. At rank n the interesting question is which *granularity* you want — slices, cells-with-addresses, or raw values — and the answer is usually "none of them, use an axis argument". Traversal in part 3 is the escape hatch, not the default.
