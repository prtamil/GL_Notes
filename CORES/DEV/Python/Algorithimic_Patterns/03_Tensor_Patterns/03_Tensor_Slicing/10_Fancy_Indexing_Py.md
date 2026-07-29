# 10. Fancy Indexing

## Mental Model

Slicing takes **regular** blocks: a start, a stop, a step. Fancy indexing takes **arbitrary** ones. You hand it a list of positions and it gathers exactly those.

```text
m[[0, 2]]           rows 0 and 2
m[[2, 0, 2]]        row 2, row 0, row 2 again  — reorder and repeat
```

Two properties follow straight away, and slicing can do neither: **any order** you like, and **duplicates**.

The rule that really matters, though, is what happens with **more than one index array**:

```text
m[[0, 1], [1, 2]]   ->  [m[0,1], m[1,2]]  ->  array([1, 6])
```

They **pair up elementwise**. That's not the sub-matrix at rows 0–1, columns 1–2. Everyone expects a sub-matrix the first time and everyone is wrong. The index arrays get zipped, not crossed. If you want the cross product, ask for it explicitly:

```python
m[np.ix_([0, 1], [1, 2])]       # the 2x2 sub-matrix
```

And the third property, which this section has been building toward:

> **Fancy indexing returns a copy, not a view.**

It has no choice. The gathered elements are scattered through memory, so no `shape`/`strides` pair can describe them. There's nothing to make a view *of*. That reverses the aliasing rule from lessons 8 and 9.

---

## Relationship to Cognitive Verb

```text
Gather
   ↓
Fancy Indexing
```

Related verbs:

- Gather
- Pick these ones
- Reorder
- Sample
- Look up by index

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Select rows|by a list|`m[[0, 2]]`|
|Reorder|permutation|`m[[2, 0, 1]]`|
|Repeat|duplicates allowed|`m[[0, 0, 0]]`|
|Paired positions|elementwise|`m[rows, cols]`|
|Cross product|the sub-matrix|`m[np.ix_(rows, cols)]`|
|Function form|explicit axis|`np.take(m, idx, axis=0)`|
|Per-row gather|different index per row|`np.take_along_axis(m, idx, axis=1)`|
|Result shape|follows the index|`m[idx]` has `idx.shape + m.shape[1:]`|
|Shuffle|random permutation|`m[np.random.permutation(len(m))]`|
|Accumulate duplicates|`+=` won't work|`np.add.at(a, idx, v)`|

---

## Common Uses

- Selecting a mini-batch by index
- Shuffling a dataset
- Applying a permutation
- Reordering by `argsort`
- Embedding lookup (rows of a table by token id)
- Gathering the top-k elements
- Building a lookup / palette mapping
- Sampling with replacement (bootstrap)

---

## Hidden Interview Problems

- Select rows of a matrix by an index list
- Reorder an array by a permutation
- Gather elements at given coordinates
- Sort a matrix's rows by a key column
- Take the top-k values along an axis
- Explain why `a[[0,1],[1,2]]` is not a sub-matrix
- Count occurrences with duplicate indices

---

## Recognition Clues

If you hear...

- "select these specific rows..."
- "in this order..."
- "shuffle / permute / sample..."
- "look up by id..."
- "gather..."
- "top-k..."

...think **Fancy Indexing**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Index type|A list or array of **integers**|
|Order|Arbitrary — duplicates allowed|
|One index array|Selects along axis 0 by default|
|Several index arrays|**Zipped elementwise**, not crossed|
|Cross product|`np.ix_(...)`|
|Result shape|Index shape + the remaining axes|
|Returns|A **copy** — never a view|
|Broadcasting|Index arrays broadcast against each other|
|Duplicate `+=`|Applies **once**; use `np.add.at`|
|Common Domains|ML batching, embeddings, sorting, sampling|

---

## Python Recipe Book

```python
# ============================================
# The running examples

import numpy as np

m = np.arange(12).reshape(3, 4)
# => array([[ 0,  1,  2,  3],
#           [ 4,  5,  6,  7],
#           [ 8,  9, 10, 11]])

t = np.arange(24).reshape(2, 3, 4)

# ============================================
# The one idiom to remember
#
#   m[[list of positions]]

m[[0, 2]]
# => array([[ 0,  1,  2,  3],
#           [ 8,  9, 10, 11]])
m[[0, 2]].shape             # => (2, 4)

# arbitrary order, and repeats are fine:
m[[2, 0, 2]]
# => array([[ 8,  9, 10, 11],
#           [ 0,  1,  2,  3],
#           [ 8,  9, 10, 11]])

m[[0, 0, 0]].shape          # => (3, 4)      longer than the input!
#
# slicing can never do either of those. That is the
# whole reason fancy indexing exists.

# ============================================
# IT IS A COPY

np.shares_memory(m, m[[0, 2]])          # => False

# compare with lesson 8:
np.shares_memory(m, m[0:2])             # => True
#
# a slice is a stride pattern; a gather is a new buffer.
# The elements picked by [2, 0, 2] are not evenly spaced
# and appear more than once — no (shape, strides) pair
# can describe that, so NumPy allocates.
#
# consequence: writing to the RESULT does nothing to the
# original. But `m[[0,2]] = 0` (assigning to the INDEX
# EXPRESSION) does write — see below.

# ============================================
# THE GOTCHA: several index arrays ZIP, not cross

m[[0, 1], [1, 2]]           # => array([1, 6])
#
# it computed [m[0,1], m[1,2]] — the pairs (0,1) and
# (1,2). Two elements, not a 2x2 block.

[m[0, 1], m[1, 2]]          # => [1, 6]      the same thing

# what most people mean the first time:
m[np.ix_([0, 1], [1, 2])]
# => array([[1, 2],
#           [5, 6]])
m[np.ix_([0, 1], [1, 2])].shape                 # => (2, 2)

np.array_equal(m[np.ix_([0, 1], [1, 2])], m[0:2, 1:3])      # => True
#
# np.ix_ reshapes the index arrays so they broadcast
# into a grid — it is `[:, None]` and `[None, :]` from
# lesson 9, applied for you.
#
# Rule of thumb:
#   m[rows, cols]           -> one element per PAIR
#   m[np.ix_(rows, cols)]   -> the full sub-grid

# ============================================
# The result shape follows the INDEX shape

idx = np.array([[0, 1],
                [2, 0]])
idx.shape                   # => (2, 2)

m[idx].shape                # => (2, 2, 4)
#
#   index shape (2,2)  +  remaining axes of m  (4,)
#
m[idx]
# => array([[[ 0,  1,  2,  3],
#            [ 4,  5,  6,  7]],
#
#           [[ 8,  9, 10, 11],
#            [ 0,  1,  2,  3]]])
#
# a rank-2 index over a rank-2 array gives rank 3. The
# general rule: result.shape == idx.shape + m.shape[1:]

# on a rank-3 tensor:
t[[1, 0]].shape             # => (2, 3, 4)   just reordered blocks
t[[0, 1], [0, 2]]
# => array([[ 0,  1,  2,  3],
#           [20, 21, 22, 23]])
t[[0, 1], [0, 2]].shape     # => (2, 4)
#
# pairs again: (0,0) and (1,2), each leaving axis 2 whole.

# ============================================
# Index arrays broadcast against each other

r = np.array([[0], [1]])            # (2, 1)
c = np.array([1, 2, 3])             # (3,)

m[r, c].shape               # => (2, 3)
m[r, c]
# => array([[1, 2, 3],
#           [5, 6, 7]])
#
#   (2,1) and (3,) broadcast to (2,3), then zip.
#
# this is exactly what np.ix_ automates — and it shows
# that "zip" and "cross" are the same operation once
# the index shapes are right. Lesson 17 makes the rule
# explicit.

# ============================================
# The function forms

np.take(m, [0, 2], axis=0)
# => array([[ 0,  1,  2,  3],
#           [ 8,  9, 10, 11]])
np.array_equal(np.take(m, [0, 2], axis=0), m[[0, 2]])       # => True
#
# np.take names the axis, so it is clearer than
# bracket syntax when the axis is not 0 or is a variable.

# take_along_axis: a DIFFERENT index per row
order = m.argsort(axis=1)[:, ::-1]      # descending order per row
order
# => array([[3, 2, 1, 0],
#           [3, 2, 1, 0],
#           [3, 2, 1, 0]])

np.take_along_axis(m, order, axis=1)
# => array([[ 3,  2,  1,  0],
#           [ 7,  6,  5,  4],
#           [11, 10,  9,  8]])
#
# each row is reordered by its OWN index row. This is the
# standard partner to argsort/argmax — trying to do it
# with plain fancy indexing means building the row
# indices by hand.

# ============================================
# Assignment DOES write through
#
# The result is a copy, but assigning to the index
# expression modifies the original.

d = np.arange(12).reshape(3, 4)
d[[0, 2]] = 0
d
# => array([[0, 0, 0, 0],
#           [4, 5, 6, 7],
#           [0, 0, 0, 0]])

e = np.arange(12).reshape(3, 4)
e[[0, 1], [1, 2]] = -1
e
# => array([[ 0, -1,  2,  3],
#           [ 4,  5, -1,  7],
#           [ 8,  9, 10, 11]])
#
# the pairing rule applies to assignment too: (0,1) and
# (1,2), two elements.

# ============================================
# THE OTHER GOTCHA: duplicate indices with +=

f = np.zeros(5, dtype=int)
f[[0, 0, 0]] += 1
f                           # => array([1, 0, 0, 0, 0])
#
# ONE, not three. `a[idx] += 1` is really
# `a[idx] = a[idx] + 1`: it gathers a copy, adds 1 to
# every element of the copy, then scatters it back.
# Position 0 is written three times with the same value.

g = np.zeros(5, dtype=int)
np.add.at(g, [0, 0, 0], 1)
g                           # => array([3, 0, 0, 0, 0])
#
# np.add.at accumulates in place, one index at a time.
# Use it for histograms, scatter-add, and anything where
# indices can repeat. (np.bincount is often faster still.)

# ============================================
# Practical: a mini-batch, and a shuffle

data = np.arange(20).reshape(10, 2)         # 10 samples
batch_idx = [3, 7, 1, 3]                    # duplicates OK
data[batch_idx].shape                       # => (4, 2)

rng = np.random.default_rng(0)
perm = rng.permutation(len(data))
shuffled = data[perm]
shuffled.shape                              # => (10, 2)
np.array_equal(shuffled[np.argsort(perm)], data)            # => True
#
# argsort of the permutation is its inverse — the
# standard way to undo a shuffle.

# ============================================
# Practical: embedding lookup

table = np.arange(15).reshape(5, 3)         # 5 tokens, 3 features
tokens = np.array([0, 4, 4, 2])
table[tokens].shape                         # => (4, 3)
#
# this IS what an embedding layer does. Fancy indexing
# on axis 0, with duplicates expected.

# ============================================
# Compare

m[0:2]              # slice        -> view,  regular block
m[[0, 2]]           # index list   -> COPY,  arbitrary rows
m[[0,1], [1,2]]     # two lists    -> COPY,  ZIPPED pairs
m[np.ix_([0,1],[1,2])]  # ix_      -> COPY,  cross product
np.take(m, [0,2], axis=0)           # named axis
np.take_along_axis(m, idx, axis=1)  # per-row indices
m[m > 5]            # boolean      -> COPY  (lesson 11)

[np.shares_memory(m, x) for x in (m[0:2], m[[0, 2]])]       # => [True, False]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|specific rows|`m[[0, 2]]`|
|a reorder or a repeat|a list index — slicing can't|
|**pairs** of coordinates|`m[rows, cols]` — they **zip**|
|a **sub-grid**|`m[np.ix_(rows, cols)]`|
|a named axis|`np.take(m, idx, axis=k)`|
|a different index per row|`np.take_along_axis(m, idx, axis=k)`|
|to undo a shuffle|`argsort(perm)`|
|to accumulate with duplicates|`np.add.at` — **not** `+=`|
|to remember the result rank|`idx.shape + m.shape[1:]`|
|independence|you already have it — this is a copy|

---

## Key Insight

**Fancy indexing gathers scattered elements, so it must allocate.** That single fact explains everything that distinguishes it from lessons 8 and 9:

```text
m[0:2]      regular  ->  describable by strides  ->  view
m[[2,0,2]]  arbitrary ->  not describable        ->  copy
```

Two behaviours surprise nearly everyone, and both are worth memorising rather than deriving:

1. **Multiple index arrays zip; they do not cross.** `m[[0,1], [1,2]]` is `[m[0,1], m[1,2]]` — two elements, not a 2×2 block. For the block, `np.ix_` reshapes the indices so they broadcast into a grid, which is `[:, None]` and `[None, :]` from lesson 9 applied automatically.
    
2. **`a[idx] += 1` applies once per position, even with duplicate indices.** It expands to gather → add → scatter, so writing to position 0 three times just stores the same value three times. `np.add.at(a, idx, 1)` accumulates properly. This silently produces wrong histograms.
    

One more asymmetry to keep straight: **the result is a copy, but assignment still writes through.** `m[[0,2]]` gives you a new array, yet `m[[0,2]] = 0` modifies `m`. The copy is made when you *read* the expression; assignment is a separate scatter operation.

The result shape is worth stating as a formula, because it is not obvious at rank 3+:

```text
result.shape == idx.shape + m.shape[1:]
```

A `(2,2)` index over a `(3,4)` array gives `(2,2,4)`.

---

## Fancy vs Basic Indexing

|Aspect|Basic (8, 9)|Fancy (10)|
|---|---|---|
|Index type|slices, ints, `...`, `None`|integer arrays|
|Order|ascending, regular step|**arbitrary**|
|Duplicates|impossible|**allowed**|
|Result|**view**|**copy**|
|Result size|≤ input|can be **larger**|

```text
  slice  ──►  a window onto the same memory
  gather ──►  a new array of the elements you named
```

> **Mental shift:** slicing asks *"which contiguous region?"*, and the answer always fits in three numbers per axis. Fancy indexing asks *"which elements, in what order?"*. That's an arbitrary question with an arbitrary answer, which is why it costs a copy and why it can hand back more data than it was given.
