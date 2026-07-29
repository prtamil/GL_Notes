# 5. Axis Iteration

## Mental Model

Part 2 walked a matrix row by row. The tensor version asks a sharper question first: **which axis are you walking?**

```text
t.shape = (2, 3, 4)

for sub in t          ->  2 sub-tensors of shape (3, 4)
```

A plain `for` loop over a tensor always walks **axis 0**, and each step hands you a sub-tensor of **rank one lower**. That's all the built-in behaviour there is. There's no `for sub in t along axis 1`.

To walk a different axis, bring it to the front:

```python
np.moveaxis(t, 1, 0)        # axis 1 becomes axis 0
```

and iterate that instead. It costs nothing, because `moveaxis` returns a **view** — just a permutation of strides (lesson 4).

```text
for sub in t                       ->  2 x (3, 4)
for sub in np.moveaxis(t, 1, 0)    ->  3 x (2, 4)
for sub in np.moveaxis(t, 2, 0)    ->  4 x (2, 3)
```

But the honest headline of this whole section is a warning:

> **In part 3, iterating is usually the wrong answer.**

A Python `for` loop over an array pays interpreter overhead per element. Measured on this machine, summing a million-element array with a loop took **0.197 s** against **0.0007 s** for `.sum()` — roughly **280× slower** for identical output. Loop over an axis when the *body* is genuinely per-slice logic. When the body is arithmetic, use an axis argument instead.

---

## Relationship to Cognitive Verb

```text
Walk
  ↓
Axis Iteration
```

Related verbs:

- Walk along
- Step through slices
- Take each sub-tensor
- Loop a dimension
- Visit each sample

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Iterate axis 0|the default|`for sub in t`|
|Iterate axis k|move it first|`for sub in np.moveaxis(t, k, 0)`|
|With an index|position too|`enumerate(t)`|
|Two tensors together|paired|`zip(a, b)`|
|How many steps|count|`t.shape[0]` — or `len(t)`|
|Collapse to a list of vectors|last axis kept|`t.reshape(-1, t.shape[-1])`|
|Rebuild after looping|re-join|`np.stack(results)`|
|Reverse|backwards|`t[::-1]`|
|Every k-th|stride|`t[::k]`|
|**Instead of looping**|vectorise|`t.sum(axis=k)`, broadcasting|

---

## Common Uses

- Processing each image in a batch
- Per-sample logic that cannot be vectorised (I/O, branching, external calls)
- Iterating time steps in a sequence model
- Writing each slice of a volume to disk
- Progress reporting over a batch
- Pairing inputs with labels
- Per-channel operations that need different treatment each channel

---

## Hidden Interview Problems

- Iterate over the slices of a 3D array along a given axis
- Apply a function to each 2D slice of a 3D array
- Sum each sub-tensor along axis 0
- Process a batch one sample at a time
- Reverse the order of slices
- Explain why `for x in t` gives matrices, not numbers

---

## Recognition Clues

If you hear...

- "for each image in the batch..."
- "process each slice..."
- "one sample at a time..."
- "along the time axis..."
- "for every channel..."

...think **Axis Iteration**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Default axis|**0**, always — there is no other built-in|
|Step yields|A sub-tensor of rank `ndim - 1`|
|Step count|`t.shape[0]`|
|Other axes|`np.moveaxis(t, k, 0)` first|
|`moveaxis` cost|**Free** — returns a view|
|Sub-tensors|Views — writing through them writes the original|
|Speed|~2 orders of magnitude slower than a vectorised call|
|Prefer instead|`axis=` arguments, broadcasting|
|Common Domains|Batching, ML training loops, I/O|

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
#   for sub in t     walks AXIS 0
#
# and each step is a tensor of rank one lower.

[sub.shape for sub in t]    # => [(3, 4), (3, 4)]
len(list(t))                # => 2      == t.shape[0]

t[0]
# => array([[ 0,  1,  2,  3],
#           [ 4,  5,  6,  7],
#           [ 8,  9, 10, 11]])
#
# note what you do NOT get: numbers. Iterating a rank-3
# tensor yields matrices. Part 2's `for row in m` yielded
# lists for the same reason — one axis peels off per loop.

# ============================================
# Walking a different axis
#
# There is no `for sub in t along axis 1`. Move the axis
# to the front and iterate normally.

[sub.shape for sub in np.moveaxis(t, 1, 0)]     # => [(2,4), (2,4), (2,4)]
[sub.shape for sub in np.moveaxis(t, 2, 0)]     # => [(2,3)] * 4

np.moveaxis(t, 1, 0).shape                      # => (3, 2, 4)
np.moveaxis(t, 2, 0).shape                      # => (4, 2, 3)

# and it is FREE — a view, not a rearrangement:
np.shares_memory(t, np.moveaxis(t, 1, 0))       # => True

# each slice is what you would have written by hand:
np.array_equal(np.moveaxis(t, 1, 0)[0], t[:, 0, :])     # => True
np.array_equal(np.moveaxis(t, 2, 0)[0], t[:, :, 0])     # => True

np.moveaxis(t, 1, 0)[0]
# => array([[ 0,  1,  2,  3],
#           [12, 13, 14, 15]])
#    "row 0 of every block"

np.moveaxis(t, 2, 0)[0]
# => array([[ 0,  4,  8],
#           [12, 16, 20]])
#    "column 0 of every block"

# ============================================
# What the loop is doing — nested lists
#
# Axis 0 is free because it is the outer list. Any other
# axis needs a rebuild, which is exactly the work
# moveaxis avoids by permuting strides instead.

[nested[i] for i in range(len(nested))] == nested       # => True   axis 0, free

def axis1_slices(n):
    return [[n[i][j] for i in range(len(n))] for j in range(len(n[0]))]

axis1_slices(nested)
# => [[[0, 1, 2, 3], [12, 13, 14, 15]],
#     [[4, 5, 6, 7], [16, 17, 18, 19]],
#     [[8, 9, 10, 11], [20, 21, 22, 23]]]

axis1_slices(nested) == np.moveaxis(t, 1, 0).tolist()   # => True
#
# the nested version allocates three new lists of lists.
# moveaxis touches nothing.

# ============================================
# With an index, and in pairs

[(i, int(sub.sum())) for i, sub in enumerate(t)]
# => [(0, 66), (1, 210)]

a = np.arange(6).reshape(2, 3)
b = np.arange(6, 12).reshape(2, 3)

[(x.tolist(), y.tolist()) for x, y in zip(a, b)]
# => [([0, 1, 2], [6, 7, 8]),
#     ([3, 4, 5], [9, 10, 11])]
#
# zip over tensors pairs their axis-0 slices — exactly
# how you iterate inputs alongside labels.

# ============================================
# The flatten-the-front trick
#
# "Do something with every vector along the last axis",
# whatever the rank in front of it.

t.reshape(-1, t.shape[-1]).shape        # => (6, 4)

t.reshape(-1, t.shape[-1]).tolist()
# => [[0, 1, 2, 3],
#     [4, 5, 6, 7],
#     [8, 9, 10, 11],
#     [12, 13, 14, 15],
#     [16, 17, 18, 19],
#     [20, 21, 22, 23]]

len(t.reshape(-1, t.shape[-1]))         # => 6
#
# 2*3 = 6 vectors of length 4. This is the standard way
# to treat "all the feature vectors" uniformly without
# caring whether the batch is (N,) or (N, T) or (N, H, W).

# ============================================
# Sub-tensors are VIEWS
#
# The loop variable is not a copy — writing through it
# writes the original.

t2 = np.arange(24).reshape(2, 3, 4)
for sub in t2:
    sub[0, 0] = -1

t2[:, 0, 0]                 # => array([-1, -1])
#
# useful when deliberate, a bug when not. `sub.copy()`
# if you need independence. (Lesson 4.)

# ============================================
# Rebuilding after a loop
#
# If the loop produces one result per slice, stack them
# back into a tensor rather than keeping a list.

results = [sub.sum(axis=1) for sub in t]        # list of (3,) arrays
np.stack(results).shape                         # => (2, 3)

np.array_equal(np.stack(results), t.sum(axis=2))    # => True
#
# ...and the right-hand side is the version to write.
# Which brings us to the point of the lesson.

# ============================================
# WHY YOU USUALLY SHOULD NOT LOOP
#
# Same answer, two orders of magnitude apart.

import time

big = np.arange(1_000_000, dtype=np.int64)

s = time.perf_counter()
total = 0
for x in big:
    total += int(x)
loop = time.perf_counter() - s

s = time.perf_counter()
total2 = int(big.sum())
vec = time.perf_counter() - s

total == total2             # => True    both 499999500000
round(loop, 4)              # => 0.1974  seconds
round(vec, 6)               # => 0.000696
int(loop / vec)             # => 283
#
# (measured on this machine; the exact ratio varies, the
# order of magnitude does not.)
#
# Every element pays Python interpreter overhead in the
# loop. `.sum()` runs one C loop over a contiguous buffer.
#
# Loop over an axis when the BODY is genuinely per-slice:
# saving each image to disk, calling an external API,
# branching on a per-sample condition. When the body is
# arithmetic, there is an axis argument for it.

# ============================================
# The vectorised replacements for common loops

# "sum each slice"          -> lesson 20
[int(sub.sum()) for sub in t]           # => [66, 210]
t.sum(axis=(1, 2)).tolist()             # => [66, 210]     same, faster

# "scale each slice"        -> lesson 17
np.stack([sub * 2 for sub in t]).shape  # => (2, 3, 4)
(t * 2).shape                           # => (2, 3, 4)     same, faster

# "max of each slice"
[int(sub.max()) for sub in t]           # => [11, 23]
t.max(axis=(1, 2)).tolist()             # => [11, 23]

# ============================================
# Compare

for sub in t: pass                      # axis 0     -> rank-2 slices
for sub in np.moveaxis(t, 1, 0): pass   # axis 1     -> rank-2 slices
for idx, v in np.ndenumerate(t): pass   # every cell -> lesson 6
for v in t.flat: pass                   # every cell -> lesson 7
t.sum(axis=0)                           # no loop    -> lesson 20
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|to iterate|`for sub in t` — always axis 0|
|another axis|`np.moveaxis(t, k, 0)` first — it's free|
|the step count|`t.shape[0]`|
|an index too|`enumerate(t)`|
|inputs with labels|`zip(x, y)`|
|every last-axis vector|`t.reshape(-1, t.shape[-1])`|
|to rebuild|`np.stack(results)`|
|independence in the body|`sub.copy()` — slices are views|
|**speed**|don't loop; pass `axis=`|

---

## Key Insight

**A `for` loop over a tensor walks axis 0 and peels off one rank per step.** There is no built-in way to iterate another axis, so the idiom is to permute first:

```python
for sub in np.moveaxis(t, k, 0):
    ...
```

which is free, because `moveaxis` only reorders strides (lesson 4).

The larger point is when *not* to do this. Part 1 and part 2 were written in Python loops because the data was small and the loop *was* the algorithm. From rank 3 upward the data is usually large enough that the interpreter overhead dominates — measured here at **~280× for a million-element sum**. The rule of thumb:

- **Loop** when the body is per-slice *logic* — writing a file, calling a service, branching on a condition, printing progress.
    
- **Don't loop** when the body is arithmetic. There is an `axis=` argument, a broadcast, or a ufunc for it, and it will be shorter as well as faster.
    

Two smaller things that bite:

1. **The loop variable is a view.** `for sub in t: sub[0,0] = -1` modifies `t`. Deliberate sometimes, a bug often.
    
2. **Iterating yields sub-tensors, not scalars.** On a rank-3 tensor you get matrices. If you wanted numbers you wanted lesson 6 or 7.
    

---

## The Traversal Section

|Lesson|Each step gives you|Order|
|---|---|---|
|**5 Axis Iteration**|a **sub-tensor** (rank − 1)|along one chosen axis|
|6 Nested Traversal|a **coordinate + value**|logical, row-major|
|7 Flat Traversal|a **value**|buffer order|

```text
   05   ▢ ▢          slices        rank-1-lower pieces
   06   (i,j,k) → v  cells         with their addresses
   07   v v v v      cells         raw, in memory order
```

> **Mental shift:** part 2 asked *in what order do I visit cells?*, and every answer was a loop. Part 3 asks *which axis?* first, and then usually answers "don't loop at all". The traversal patterns here are for the cases where you genuinely have to, and the next two lessons cover the other two granularities.
