# 11. Boolean Masking

## Mental Model

The last way to index: not by *position* but by **condition**.

```text
t > 15          a bool tensor, same shape as t
t[t > 15]       the elements where it is True
```

A comparison on a tensor is **elementwise** — it returns a whole tensor of `True`/`False`, not a single answer. That mask is then a valid index, and indexing with it selects exactly the cells that passed.

Two consequences define the pattern:

- **The result is rank 1.** A mask over a `(2,3,4)` tensor can select any subset of cells, and an arbitrary subset has no shape. So it flattens.

```text
t.shape          (2, 3, 4)
t[t > 15].shape  (8,)          — always rank 1
```

- **It is a copy.** Same reason as lesson 10: the selected cells are scattered, so no stride pattern can describe them.

And one Python-level trap that catches everyone exactly once:

> **Use `&`, `|`, `~` — never `and`, `or`, `not`.**

Python's boolean keywords call `bool()` on their operands, and `bool()` of a multi-element array is undefined. `(t > 5) and (t < 10)` raises `ValueError: The truth value of an array with more than one element is ambiguous`. The bitwise operators work elementwise, which is what you want — and they bind tighter than comparison, so **every clause needs parentheses**.

---

## Relationship to Cognitive Verb

```text
Filter
   ↓
Boolean Masking
```

Related verbs:

- Filter
- Select where
- Keep matching
- Test elementwise
- Condition on

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Build a mask|elementwise test|`t > 15`|
|Select|apply it|`t[t > 15]`|
|Combine|and / or / not|`&`, `|`, `~` — **with parentheses**|
|Count|how many|`int(mask.sum())`|
|Any / all|reduce to one bool|`mask.any()`, `mask.all()`|
|Per axis|counts by group|`mask.sum(axis=k)`|
|Positions|where are they|`np.argwhere(mask)` / `np.nonzero(mask)`|
|Replace|conditional value|`np.where(mask, a, b)`|
|Assign|write where true|`t[mask] = 0`|
|Mask one axis|keep the rank|`t[:, mask1d, :]`|

---

## Common Uses

- Filtering outliers or invalid values
- Clipping and thresholding
- Selecting a class from labelled data
- Replacing NaNs
- Counting how many cells satisfy a condition
- Applying a rule only where it holds
- Segmentation masks in images
- Conditional statistics

---

## Hidden Interview Problems

- Count elements greater than a threshold
- Replace all negatives with zero
- Find the coordinates of all matching cells
- Filter rows by a condition on one column
- Clip values into a range
- Compute the mean of positive values only
- Explain why `(a > 1) and (a < 5)` raises

---

## Recognition Clues

If you hear...

- "all values greater than..."
- "where the condition holds..."
- "filter out..."
- "replace every negative with..."
- "how many are..."
- "only the valid entries..."

...think **Boolean Masking**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Mask|A bool tensor, same shape as the target|
|`t[mask]`|**Rank 1**, however many axes went in|
|Length|`int(mask.sum())`|
|Returns|A **copy**|
|Combining|`&`, `|`, `~` — **not** `and`, `or`, `not`|
|Parentheses|Required — bitwise ops bind tighter than `<`|
|1-D mask on one axis|Keeps the rank|
|Assignment|Writes through: `t[mask] = v`|
|Shape-preserving form|`np.where(mask, a, b)`|
|Common Domains|Data cleaning, images, statistics|

---

## Python Recipe Book

```python
# ============================================
# The running examples

import numpy as np

t = np.arange(24).reshape(2, 3, 4)
m = np.arange(12).reshape(3, 4)

# ============================================
# The one idiom to remember
#
#   a comparison gives a MASK; the mask indexes

(t > 15).shape              # => (2, 3, 4)      same shape as t
(t > 15).dtype              # => dtype('bool')

t[t > 15]                   # => array([16, 17, 18, 19, 20, 21, 22, 23])
t[t > 15].shape             # => (8,)
t[t > 15].ndim              # => 1
#
# rank 3 in, rank 1 out. An arbitrary subset of cells
# has no rectangular shape, so the result is flat —
# and the positions are lost unless you ask for them
# separately (np.argwhere, below).

np.shares_memory(t, t[t > 15])          # => False      a COPY

# ============================================
# THE PYTHON TRAP: and / or / not do not work

try:
    (t > 5) and (t < 10)
except ValueError as e:
    print(e)
# The truth value of an array with more than one element is ambiguous.
#
# `and` calls bool() on its left operand. bool() of a
# 24-element array is undefined — should it be True if
# any element is, or all? NumPy refuses to guess.

t[(t > 5) & (t < 10)]       # => array([6, 7, 8, 9])
t[(t < 2) | (t > 21)]       # => array([ 0,  1, 22, 23])
t[~(t > 2)]                 # => array([0, 1, 2])
#
#   &   elementwise and
#   |   elementwise or
#   ~   elementwise not

# PARENTHESES ARE MANDATORY.
#
#   t > 5 & t < 10
#
# parses as  t > (5 & t) < 10  — & binds tighter than >.
# It either raises or, worse, silently computes
# something else. Always wrap each comparison.

# ============================================
# Counting and testing — no indexing needed

int((t > 15).sum())         # => 8      True counts as 1
bool((t > 15).any())        # => True
bool((t > 15).all())        # => False

# per-axis counts (lesson 2's axis rule, on a bool array)
(t > 10).sum(axis=(1, 2))   # => array([ 1, 12])
#   block 0 has one value over 10; block 1 has all twelve

(t > 10).sum(axis=2)
# => array([[0, 0, 1],
#           [4, 4, 4]])
#   how many per row
#
# summing a bool array is the vectorised replacement for
# part 2's `sum(1 for ... if ...)` counting loops.

# ============================================
# Positions — when you need the coordinates

np.where(t > 20)
# => (array([1, 1, 1]), array([2, 2, 2]), array([1, 2, 3]))
#
# a TUPLE of index arrays, one per axis — read down the
# columns: (1,2,1), (1,2,2), (1,2,3).
# It is directly usable as an index: t[np.where(t>20)]

np.argwhere(t > 20).tolist()
# => [[1, 2, 1], [1, 2, 2], [1, 2, 3]]
#
# one ROW per match — usually what you actually want to
# read. np.nonzero is a synonym for the one-argument
# np.where.

# ============================================
# np.where with three arguments — shape-preserving
#
# This is the important variant: instead of extracting
# matching cells, it CHOOSES between two values and
# keeps the shape.

np.where(t > 20, 1, 0)[1]
# => array([[0, 0, 0, 0],
#           [0, 0, 0, 0],
#           [0, 1, 1, 1]])

np.where(t > 20, 20, t)[1]
# => array([[12, 13, 14, 15],
#           [16, 17, 18, 19],
#           [20, 20, 20, 20]])
#
# an upper clip. Both branches broadcast, so either can
# be a scalar or a full tensor.
#
#   t[t > 20]                 -> extract, rank 1
#   np.where(t > 20, a, b)    -> choose, same shape
#
# reach for `where` whenever the output must stay the
# same shape as the input.

# ============================================
# A 1-D mask on ONE axis keeps the rank
#
# This is the exception to "masking flattens".

mask1 = np.array([True, False, True])       # length 3 == t.shape[1]

t[:, mask1, :].shape        # => (2, 2, 4)      still rank 3
t[:, mask1, :]
# => array([[[ 0,  1,  2,  3],
#            [ 8,  9, 10, 11]],
#
#           [[12, 13, 14, 15],
#            [20, 21, 22, 23]]])
#
# rows 0 and 2 of every block. Because the mask covers
# exactly one axis, the selection IS rectangular, so the
# shape survives.

m[np.array([True, False, True])]
# => array([[ 0,  1,  2,  3],
#           [ 8,  9, 10, 11]])
#
# this is the standard "filter rows by a condition" form:
m[m[:, 0] > 2]              # rows whose first column exceeds 2
# => array([[ 4,  5,  6,  7],
#           [ 8,  9, 10, 11]])
#
# `m[:, 0] > 2` is a length-3 mask over axis 0 — the row
# filter of every dataframe library, in one expression.

# ============================================
# Assignment through a mask

h = np.arange(24).reshape(2, 3, 4)
h[h > 20] = 0
h[1]
# => array([[12, 13, 14, 15],
#           [16, 17, 18, 19],
#           [20,  0,  0,  0]])

i = np.arange(24).reshape(2, 3, 4)
i[i % 2 == 0] *= -1
i[0]
# => array([[  0,   1,  -2,   3],
#           [ -4,   5,  -6,   7],
#           [ -8,   9, -10,  11]])
#
# unlike lesson 10's duplicate-index problem, `mask +=`
# is safe: a boolean mask cannot select the same cell
# twice, so there is nothing to accumulate wrongly.

# ============================================
# The pure-Python equivalent

nested = t.tolist()
[x for a1 in nested for a2 in a1 for x in a2 if x > 15]
# => [16, 17, 18, 19, 20, 21, 22, 23]

[x for a1 in nested for a2 in a1 for x in a2 if x > 15] == t[t > 15].tolist()
# => True
#
# a flatten plus a filter — which is exactly why the
# NumPy result is rank 1. The comprehension makes the
# flattening visible; the mask hides it.

# ============================================
# Practical: conditional statistics

data = np.array([1.0, -2.0, 3.0, np.nan, 5.0])

valid = ~np.isnan(data)
valid                       # => array([True, True, True, False, True])
data[valid].mean()          # => 1.75
np.nanmean(data)            # => 1.75      the built-in shortcut

pos = data[valid][data[valid] > 0]
pos                         # => array([1., 3., 5.])
#
# note np.isnan and NOT `data == np.nan`, which is
# always False — NaN does not equal itself.
float(np.nan == np.nan)     # => 0.0       i.e. False

# ============================================
# Compare — the four index types

t[0:2]              # slice        -> view,   rank kept
t[..., 0]           # ellipsis     -> view,   rank 2
t[[0, 1]]           # int array    -> COPY,   rank kept
t[t > 15]           # bool mask    -> COPY,   rank 1
t[:, mask1, :]      # 1-D mask     -> COPY,   rank kept
np.where(t > 15, t, 0)          # no indexing -> same shape

[np.shares_memory(t, x) for x in (t[0:2], t[[0, 1]], t[t > 15])]
# => [True, False, False]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a mask|any elementwise comparison|
|the matching values|`t[mask]` — always rank 1|
|**and / or / not**|`&`, `|`, `~` — never the keywords|
|to not get bitten|parentheses around **every** comparison|
|a count|`int(mask.sum())`|
|counts per group|`mask.sum(axis=k)`|
|the coordinates|`np.argwhere(mask)`|
|to keep the shape|`np.where(mask, a, b)`|
|to filter rows|`m[m[:, 0] > 2]`|
|NaN handling|`~np.isnan(x)` — `== np.nan` is always False|

---

## Key Insight

**A comparison on a tensor is elementwise, so it yields a mask rather than an answer** — and that mask is itself a valid index.

The two structural facts follow from one observation: an arbitrary subset of cells is not rectangular.

```text
t[t > 15]   ->  rank 1    (no shape can describe the subset)
            ->  a copy    (no strides can describe it either)
```

Which makes the 1-D case the interesting exception. `t[:, mask1, :]` masks exactly one axis, so the selection *is* rectangular and the rank survives — that form is how row filtering works, and it is worth distinguishing from the flattening form.

Three things to fix in memory:

1. **`&`, `|`, `~` — never `and`, `or`, `not`.** The keywords call `bool()` on an array and raise. And because the bitwise operators bind *tighter* than comparisons, `t > 5 & t < 10` parses as `t > (5 & t) < 10`. **Parenthesise every clause.**
    
2. **`np.where` has two jobs.** One argument gives you positions; three arguments choose between values and keep the shape. When the output must stay the same shape as the input, `where` is the tool — not masking.
    
3. **Summing a mask counts it.** `int((t > 15).sum())` replaces every counting loop from parts 1 and 2, and `mask.sum(axis=k)` gives counts per group for free.
    

Unlike lesson 10, **`t[mask] += 1` is safe** — a boolean mask cannot select the same cell twice, so there are no duplicates to lose.

---

## The Slicing Section, Complete

|Lesson|Index|Rank|Memory|
|---|---|---|---|
|8 Basic Slicing|`a:b:c`, ints|kept / reduced|**view**|
|9 Ellipsis, newaxis|`...`, `None`|kept / increased|**view**|
|10 Fancy Indexing|integer arrays|index shape + rest|**copy**|
|**11 Boolean Masking**|bool arrays|**1** (or kept, if 1-D)|**copy**|

```text
                     ┌── basic     ──►  view    describable by strides
  t[ something ]  ───┤
                     └── advanced  ──►  copy    scattered elements
```

The dividing line is a single question: **can the selection be described by a shape and a stride?** A slice can, so it is a window onto the same memory. A gather or a filter cannot, so it must allocate.

> **Mental shift:** part 2 filtered with comprehensions — `[x for row in m for x in row if x > 15]` — which flattened as a side effect of how the loops were written. NumPy flattens for a deeper reason: the result genuinely has no shape. Once you see masking as "filter, therefore flatten, therefore copy", the rank-1 result stops being surprising and `np.where` becomes the obvious alternative when you need the shape back.
