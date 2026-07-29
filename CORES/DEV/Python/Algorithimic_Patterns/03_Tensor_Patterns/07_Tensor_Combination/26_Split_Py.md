# 26. Split

## Mental Model

The inverse of lessons 24 and 25. Cut one tensor into several **along an axis**.

```text
w  (4, 3)

np.split(w, 2, axis=0)   ->  two  (2, 3) pieces
np.split(w, 3, axis=1)   ->  three (4, 1) pieces
```

Two ways to say where the cuts go:

- **A count.** `np.split(w, 2)` divides into 2 equal parts and **raises** if the axis doesn't divide evenly.
    
- **A list of indices.** `np.split(xs, [3, 7])` cuts *before* positions 3 and 7, giving you three pieces of whatever sizes.
    

`np.array_split` is the forgiving version of the count form. It accepts an uneven division and spreads the remainder around.

And here's the property that sets this apart from the rest of the section:

> **Split returns views.**

Concatenate and stack have to allocate, because two buffers can't become one for free. Splitting is the opposite. Every piece is a contiguous or strided window into the *original* buffer, so it's just slicing (lesson 8) and it costs nothing. Write to a piece and you've written to the original.

---

## Relationship to Cognitive Verb

```text
Divide
   ↓
Split
```

Related verbs:

- Divide
- Cut into pieces
- Partition
- Chunk
- Break apart

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Equal parts|must divide evenly|`np.split(t, n, axis=k)`|
|Uneven parts|remainder distributed|`np.array_split(t, n, axis=k)`|
|Explicit cut points|any sizes|`np.split(t, [i, j], axis=k)`|
|Rows (2-D)|shortcut|`np.vsplit(t, n)`|
|Columns (2-D)|shortcut|`np.hsplit(t, n)`|
|Into single slices|one per position|`list(t)` — or `np.moveaxis` first|
|Manual batching|explicit control|`[t[i:i+b] for i in range(0, n, b)]`|
|The inverse|put it back|`np.concatenate(pieces, axis=k)`|
|Check it's free|views|`np.shares_memory(t, pieces[0])`|

---

## Common Uses

- Mini-batching a dataset
- Train / validation / test splits
- Separating channels of an image
- Splitting a concatenated feature vector back into parts
- Dividing work across workers
- Chunking a long sequence into windows
- Separating a packed `(Q, K, V)` projection

---

## Hidden Interview Problems

- Split an array into n equal parts
- Split a dataset at given proportions
- Divide a matrix into row blocks
- Chunk a list into batches of size k
- Explain the difference between `split` and `array_split`
- Reassemble the pieces

---

## Recognition Clues

If you hear...

- "divide into n parts..."
- "mini-batches of size..."
- "train/test split..."
- "separate the channels..."
- "chunk the sequence..."

...think **Split**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Returns|A **list** of arrays|
|Rank of each piece|**Unchanged**|
|`split(t, n)`|Equal parts; **raises** if not divisible|
|`array_split(t, n)`|Uneven allowed; earlier pieces get the extras|
|`split(t, [i, j])`|Cuts *before* those indices|
|Out-of-range index|Yields an **empty** piece, no error|
|Memory|**Views** — free, and they alias|
|Inverse|`np.concatenate(pieces, axis=k)`|
|Common Domains|Batching, data splits, channel separation|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember

import numpy as np

w = np.arange(12).reshape(4, 3)
w
# => array([[ 0,  1,  2],
#           [ 3,  4,  5],
#           [ 6,  7,  8],
#           [ 9, 10, 11]])

[p.shape for p in np.split(w, 2, axis=0)]       # => [(2, 3), (2, 3)]
[p.tolist() for p in np.split(w, 2, axis=0)]
# => [[[0, 1, 2], [3, 4, 5]],
#     [[6, 7, 8], [9, 10, 11]]]

[p.shape for p in np.split(w, 3, axis=1)]       # => [(4,1), (4,1), (4,1)]
#
# the pieces keep the RANK. Splitting a (4,3) into 3
# along axis 1 gives three (4,1) matrices — not three
# (4,) vectors. Use `list(t.T)` or squeeze if you want
# the axis gone.

# ============================================
# split demands an EXACT division

try:
    np.split(w, 3, axis=0)
except ValueError as e:
    print(e)
# array split does not result in an equal division
#
# 4 rows into 3 pieces has no equal answer, so it
# refuses. That strictness is a feature — it catches a
# dataset whose size you assumed.

# array_split accepts it and distributes the remainder:
[p.shape for p in np.array_split(w, 3, axis=0)] # => [(2,3), (1,3), (1,3)]
[len(p) for p in np.array_split(np.arange(10), 3)]      # => [4, 3, 3]
#
# earlier pieces get the extra elements. Sizes differ by
# at most 1.

# ============================================
# Explicit cut points — a LIST of indices

[p.tolist() for p in np.split(np.arange(10), [3, 7])]
# => [[0, 1, 2], [3, 4, 5, 6], [7, 8, 9]]
[p.shape for p in np.split(np.arange(10), [3, 7])]
# => [(3,), (4,), (3,)]
#
# cuts BEFORE index 3 and BEFORE index 7 — the same
# convention as slicing. n indices give n+1 pieces.

# out-of-range indices give EMPTY pieces, not errors:
[p.shape for p in np.split(np.arange(5), [2, 99])]      # => [(2,), (3,), (0,)]
#
# so a proportional split cannot crash on a short array;
# it just returns something empty. Check `.size` if an
# empty piece would be a problem downstream.

# ============================================
# IT RETURNS VIEWS — the only free operation here

parts = np.split(w, 2, axis=0)
np.shares_memory(w, parts[0])                   # => True

pw = w.copy()
ps = np.split(pw, 2, axis=0)
ps[0][0, 0] = 99
pw[0, 0]                                        # => 99      wrote through
#
# splitting is just slicing (lesson 8), so nothing is
# copied. Note the asymmetry across this section:
#
#   concatenate / stack   ->  COPY   (must allocate)
#   split                 ->  VIEW   (just slicing)
#
# if the pieces must be independent, `.copy()` them.

# ============================================
# The 2-D shortcuts

np.array_equal(np.vsplit(w, 2)[0], np.split(w, 2, axis=0)[0])   # => True
np.array_equal(np.hsplit(w, 3)[0], np.split(w, 3, axis=1)[0])   # => True
#
# vsplit is axis 0, hsplit is axis 1. Unlike vstack /
# hstack (lesson 24), these have no 1-D surprise — but
# naming the axis is still clearer.

# ============================================
# On rank 3, the same rule

t = np.arange(24).reshape(2, 3, 4)

[p.shape for p in np.split(t, 3, axis=1)]       # => [(2,1,4)] * 3
[p.shape for p in np.split(t, 2, axis=2)]       # => [(2,3,2)] * 2

# ============================================
# The round trip

np.array_equal(np.concatenate(np.split(w, 2, axis=0), axis=0), w)   # => True
#
# split then concatenate is the identity, on the same
# axis. And note what STACK would do instead:
np.stack(np.split(w, 2, axis=0)).shape          # => (2, 2, 3)
#
# concatenate puts the pieces back; stack makes them a
# new dimension (lesson 25).

# ============================================
# THE APPLICATION: mini-batching
#
# Two spellings, and they differ in how the remainder
# is handled.

data = np.arange(20).reshape(10, 2)             # 10 samples

# array_split: BALANCED — sizes differ by at most 1
[b.shape for b in np.array_split(data, 4)]      # => [(3,2), (3,2), (2,2), (2,2)]

# slicing: FIXED size, with a short final batch
[data[i:i+3].shape for i in range(0, 10, 3)]    # => [(3,2), (3,2), (3,2), (1,2)]
#
#   "4 batches"          -> array_split   3,3,2,2
#   "batches of 3"       -> slicing       3,3,3,1
#
# these answer different questions. Training loops
# usually want the second (a fixed batch size), and
# often drop the short final batch:
[data[i:i+3] for i in range(0, len(data) - 3 + 1, 3)]   # 3 full batches
#
# the slicing form also composes with shuffling
# (lesson 10) — permute the indices, then slice.

# ============================================
# Practical: proportional dataset split

n = len(data)
train_end = int(0.6 * n)                        # => 6
val_end   = int(0.8 * n)                        # => 8

train, val, test = np.split(data, [train_end, val_end])
train.shape, val.shape, test.shape              # => ((6,2), (2,2), (2,2))
train.shape[0] + val.shape[0] + test.shape[0]   # => 10
#
# cumulative CUT POINTS, not proportions — a common
# off-by-one is passing [0.6, 0.2] instead.

# ============================================
# Practical: unpacking a packed projection
#
# Transformers compute Q, K and V in one matmul and
# then split the result.

qkv = np.arange(2 * 12).reshape(2, 12)          # (batch, 3*d) with d=4
q, k, v = np.split(qkv, 3, axis=1)
q.shape, k.shape, v.shape                       # => ((2,4), (2,4), (2,4))
q
# => array([[ 0,  1,  2,  3],
#           [12, 13, 14, 15]])
#
# and they are views, so the split costs nothing.
np.shares_memory(qkv, q)                        # => True

# ============================================
# Splitting into single slices

list(w)                                         # 4 arrays of shape (3,)
[p.shape for p in list(w)]                      # => [(3,), (3,), (3,)  ...]
#
# `list(t)` peels axis 0 and DROPS it (lesson 5), while
# `np.split(t, len(t))` keeps it:
[p.shape for p in np.split(w, 4, axis=0)]       # => [(1,3)] * 4
#
# both are views; they differ only in rank.

# ============================================
# Compare

np.split(w, 2, axis=0)          # equal parts, raises if uneven
np.array_split(w, 3, axis=0)    # uneven allowed
np.split(w, [1, 3], axis=0)     # explicit cut points
list(w)                         # peel axis 0, rank drops
[w[i:i+2] for i in range(0, 4, 2)]      # manual, full control

# every one of these is a VIEW:
[np.shares_memory(w, p[0]) for p in
 (np.split(w, 2), np.array_split(w, 3), np.split(w, [1, 3]))]       # => [True]*3
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|n equal parts|`np.split(t, n, axis=k)` — raises if uneven|
|n parts, any sizes|`np.array_split(t, n, axis=k)`|
|cuts at specific places|`np.split(t, [i, j], axis=k)`|
|batches of a fixed size|slicing: `t[i:i+b]`|
|n balanced batches|`np.array_split(t, n)`|
|a train/val/test split|cumulative **cut points**|
|to put it back|`np.concatenate(pieces, axis=k)`|
|independent pieces|`.copy()` — splits are views|
|the rank dropped|`list(t)`, not `np.split`|

---

## Key Insight

**Split is the only operation in this section that is free, because it is slicing.** Concatenate and stack must allocate — two separate buffers cannot be described by one stride pattern. Splitting goes the other way: each piece is already a window into the existing buffer.

```text
concatenate / stack  ->  COPY
split                ->  VIEW  (and it aliases)
```

The three forms answer different questions, and choosing wrongly is the usual mistake:

|Call|Means|
|---|---|
|`np.split(t, n)`|"exactly n equal parts" — **raises** otherwise|
|`np.array_split(t, n)`|"n parts, balanced" — sizes differ by ≤ 1|
|`np.split(t, [i, j])`|"cut here and here" — cut points, not sizes|

For batching, note that `np.array_split(data, 4)` gives sizes `3,3,2,2` while `[data[i:i+3] for i in range(0, 10, 3)]` gives `3,3,3,1`. The first answers *"how many batches?"*, the second *"how big is a batch?"* — and training loops almost always want the second.

Two smaller points: **out-of-range cut indices produce empty pieces rather than errors**, so a proportional split silently degrades on short input; and `list(t)` drops the axis while `np.split(t, len(t))` keeps it as size 1 — both views, different ranks.

---

## The Inverse Table

|Operation|Inverse|
|---|---|
|`np.concatenate(pieces, axis=k)`|`np.split(t, n, axis=k)`|
|`np.stack(items, axis=0)`|`list(t)`|
|`np.stack(items, axis=k)`|`list(np.moveaxis(t, k, 0))`|

```text
   split       ──►  pieces  ──►  concatenate   (same axis, round trip)
   list(t)     ──►  items   ──►  stack         (rank down, then up)
```

> **Mental shift:** part 1 chunked a list with slicing and part 2 tiled a matrix with `range(0, n, k)`. Both still work, and both are still right when you want a *fixed size*. What `split` adds is the other question, *"into how many?"*, plus the guarantee that the pieces are views. That's what makes splitting a packed tensor into Q, K and V cost nothing at all.
