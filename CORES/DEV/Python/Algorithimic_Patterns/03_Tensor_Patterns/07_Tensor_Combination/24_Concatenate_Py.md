# 24. Concatenate

## Mental Model

Join tensors **along an axis that already exists**. That axis grows, every other axis has to match exactly, and the rank stays put.

```text
a  (2, 3)
b  (2, 3)

concatenate([a, b], axis=0)  ->  (4, 3)      the 2s added
concatenate([a, b], axis=1)  ->  (2, 6)      the 3s added
```

The rule in one line:

> **All shapes must be identical except on the join axis, where the sizes add.**

That's stricter than it sounds. `(2,3)` and `(2,4)` can be joined on axis 1 (`3+4=7`) but not on axis 0, because 3 ≠ 4. Arrays of *different rank* can't be joined at all — a `(2,3)` and a `(3,)` need the vector promoted to `(1,3)` first.

Two things set this apart from everything in the last few sections:

- **It always copies.** The result is a new buffer. There's no stride trick that makes two separate allocations look contiguous, so every combination in this section allocates.
    
- **The `*stack` shortcuts change behaviour depending on rank.** `np.vstack` on two 1-D arrays gives you a `(2,3)` matrix, while `np.concatenate` gives a `(6,)` vector. Convenient, and a real source of bugs.
    

---

## Relationship to Cognitive Verb

```text
Join
  ↓
Concatenate
```

Related verbs:

- Join
- Append
- Glue end to end
- Extend along
- Merge

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Join on an axis|the general form|`np.concatenate([a, b], axis=k)`|
|Join and flatten|no axis|`np.concatenate([a, b], axis=None)`|
|Rows (2-D)|shortcut|`np.vstack` — but see the 1-D caveat|
|Columns (2-D)|shortcut|`np.hstack`|
|Columns from vectors|1-D → columns|`np.column_stack`|
|Promote rank first|to match|`v[None, :]` (lesson 9)|
|Many arrays|one call|pass the whole list|
|Growing a result|**don't** concatenate in a loop|collect, then concatenate once|
|Add a *new* axis|different operation|`np.stack` (lesson 25)|

---

## Common Uses

- Appending a batch of new samples to a dataset
- Joining features along the channel axis
- Building a long sequence from segments
- Merging train and validation splits
- Adding a bias column to a design matrix
- Assembling tiles back into an image
- Combining results computed in chunks

---

## Hidden Interview Problems

- Concatenate two matrices vertically and horizontally
- Append a column of ones to a matrix
- Merge a list of arrays into one
- Explain why `vstack` differs from `concatenate` on 1-D input
- Join arrays of different shapes along a compatible axis
- Explain why concatenating in a loop is quadratic

---

## Recognition Clues

If you hear...

- "append to..."
- "join / merge / combine along..."
- "add these rows / columns..."
- "extend the sequence..."
- "stack them vertically..."

...think **Concatenate**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Rank|**Unchanged**|
|Join axis|Sizes **add**|
|Other axes|Must match **exactly**|
|Different ranks|Not allowed — promote first|
|`axis=None`|Flattens everything into rank 1|
|Returns|A **copy** — always|
|Empty arrays|Allowed, if the other axes match|
|Time Complexity|O(total size)|
|In a loop|O(n²) — collect first|
|Common Domains|Data assembly, batching, feature engineering|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember

import numpy as np

a = np.arange(6).reshape(2, 3)
b = np.arange(6, 12).reshape(2, 3)

np.concatenate([a, b], axis=0)
# => array([[ 0,  1,  2],
#           [ 3,  4,  5],
#           [ 6,  7,  8],
#           [ 9, 10, 11]])
np.concatenate([a, b], axis=0).shape        # => (4, 3)   2+2

np.concatenate([a, b], axis=1)
# => array([[ 0,  1,  2,  6,  7,  8],
#           [ 3,  4,  5,  9, 10, 11]])
np.concatenate([a, b], axis=1).shape        # => (2, 6)   3+3

# rank never changes:
a.ndim, np.concatenate([a, b]).ndim         # => (2, 2)

# any number of arrays, one call:
c = np.arange(100, 106).reshape(2, 3)
np.concatenate([a, b, c], axis=0).shape     # => (6, 3)

# ============================================
# The rule: everything must match EXCEPT the join axis

d = np.arange(8).reshape(2, 4)
a.shape, d.shape                            # => ((2, 3), (2, 4))

np.concatenate([a, d], axis=1).shape        # => (2, 7)   3+4, axis 0 both 2

try:
    np.concatenate([a, d], axis=0)
except ValueError as e:
    print(str(e)[:75])
# all the input array dimensions except for the concatenation axis must
#
# joining on axis 0 would need axis 1 to agree — 3 vs 4.

# ============================================
# Ranks must match too

v = np.arange(3)                            # (3,)

try:
    np.concatenate([a, v])
except ValueError as e:
    print(str(e)[:60])
# all the input arrays must have same number of dimensions

np.concatenate([a, v[None, :]], axis=0).shape           # => (3, 3)
#
# promote the vector to a 1-row matrix first (lesson 9).
# This is the single most common concatenate error, and
# `v[None, :]` is the fix.

# ============================================
# axis=None flattens everything

np.concatenate([a, b], axis=None)
# => array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11])
np.concatenate([a, b], axis=None).shape     # => (12,)
#
# useful for "just glue all the numbers together",
# and shape-agnostic — the inputs need not match at all.

# ============================================
# IT ALWAYS COPIES

np.shares_memory(a, np.concatenate([a, b]))             # => False
#
# unavoidable: `a` and `b` live in separate buffers, and
# no (shape, strides) pair can span two allocations. This
# is the first section since lesson 8 where nothing is
# free — combination costs O(total size), every time.

# ============================================
# On rank 3 it is the same rule

t = np.arange(24).reshape(2, 3, 4)

np.concatenate([t, t], axis=0).shape        # => (4, 3, 4)
np.concatenate([t, t], axis=1).shape        # => (2, 6, 4)
np.concatenate([t, t], axis=2).shape        # => (2, 3, 8)
np.concatenate([t, t], axis=-1).shape       # => (2, 3, 8)
#
# axis=-1 is the portable spelling for "the feature /
# channel axis" (lesson 2).

# ============================================
# THE *stack SHORTCUTS — and the 1-D trap

x1 = np.array([1, 2, 3])
x2 = np.array([4, 5, 6])

np.concatenate([x1, x2])            # => array([1, 2, 3, 4, 5, 6])    (6,)
np.vstack([x1, x2])
# => array([[1, 2, 3],
#           [4, 5, 6]])                                              (2, 3)
#
# SAME INPUT, DIFFERENT RANK. On 1-D input `vstack`
# promotes each array to a row first — it is really
# "stack as rows", not "concatenate on axis 0".

np.vstack([x1, x2]).shape != np.concatenate([x1, x2]).shape     # => True

np.hstack([x1, x2])                 # => array([1, 2, 3, 4, 5, 6])
#   hstack on 1-D concatenates, because for 1-D the
#   "horizontal" axis IS axis 0. So vstack promotes and
#   hstack does not. That asymmetry is the trap.

# on 2-D input they behave as you would expect:
np.array_equal(np.vstack([a, b]), np.concatenate([a, b], axis=0))   # => True
np.array_equal(np.hstack([a, b]), np.concatenate([a, b], axis=1))   # => True

# and column_stack is the one that reads correctly for
# building columns out of vectors:
np.column_stack([x1, x2])
# => array([[1, 4],
#           [2, 5],
#           [3, 6]])
np.column_stack([x1, x2]).shape     # => (3, 2)

np.dstack([x1, x2]).shape           # => (1, 3, 2)    depth — rarely wanted
#
# RULE OF THUMB: use `np.concatenate(..., axis=k)` and
# say which axis. The shortcuts save four characters and
# behave differently by rank.

# ============================================
# Empty arrays are legal

e = np.zeros((0, 3))
np.concatenate([a, e], axis=0).shape        # => (2, 3)
#
# a size-0 axis concatenates cleanly, which makes
# "start with an empty array and append" work — even
# though you should not do that (see below).

# ============================================
# NEVER CONCATENATE IN A LOOP
#
# Each call allocates a whole new buffer and copies
# everything so far. Appending n arrays costs O(n^2).

# BAD:
#   out = np.empty((0, 3))
#   for chunk in chunks:
#       out = np.concatenate([out, chunk])      # copies everything, n times

# GOOD:
chunks = [np.full((2, 3), i) for i in range(4)]
out = np.concatenate(chunks, axis=0)
out.shape                                   # => (8, 3)
#
# collect into a Python list — appending to a list IS
# cheap — then concatenate once. Same lesson as building
# strings with `+=` versus `''.join`.

# ============================================
# Practical: add a bias column

X = np.arange(6, dtype=float).reshape(3, 2)
ones = np.ones((len(X), 1))
np.concatenate([ones, X], axis=1)
# => array([[1., 0., 1.],
#           [1., 2., 3.],
#           [1., 4., 5.]])
#
# note `np.ones((len(X), 1))` — a (3,1) COLUMN, not a
# (3,) vector, so the ranks match.

# ============================================
# Compare

np.concatenate([a, b], axis=0)      # existing axis -> (4, 3), rank 2
np.stack([a, b], axis=0)            # NEW axis      -> (2, 2, 3), rank 3
np.split(np.concatenate([a, b]), 2) # the inverse   -> lesson 26
np.tile(a, (2, 1))                  # repeat itself -> lesson 27

np.array_equal(np.tile(a, (2, 1)), np.concatenate([a, a], axis=0))  # => True
#
# tiling along one axis IS concatenating an array with
# itself. Lesson 27 makes that precise.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|to join on an existing axis|`np.concatenate([...], axis=k)`|
|the rule|everything matches **except** the join axis|
|to join a vector to a matrix|promote it: `v[None, :]`|
|columns from 1-D arrays|`np.column_stack`|
|**not** to be surprised|`vstack` promotes 1-D, `hstack` does not|
|to glue all the numbers|`axis=None`|
|to build up a result|collect in a **list**, concatenate **once**|
|a *new* axis instead|`np.stack` (lesson 25)|

---

## Key Insight

**Concatenation grows an axis that already exists, so the rank never changes and every other axis must match exactly.** That single rule predicts both the output shape and every error you will get:

```text
(2,3) + (2,3) on axis 0  ->  (4,3)      ok
(2,3) + (2,4) on axis 1  ->  (2,7)      ok — axis 0 agrees
(2,3) + (2,4) on axis 0  ->  ERROR      axis 1 disagrees
(2,3) + (3,)             ->  ERROR      different ranks
```

Two practical points carry most of the value:

1. **Prefer `np.concatenate(..., axis=k)` to the `*stack` shortcuts.** On 2-D input `vstack` and `hstack` do what you expect, but on **1-D** input `vstack` promotes each array to a row — `(2,3)` — while `concatenate` and `hstack` produce a `(6,)` vector. Same call, different rank, depending on the input. Naming the axis removes the ambiguity.
    
2. **Never concatenate in a loop.** Each call allocates a fresh buffer and copies everything accumulated so far, making n appends O(n²). Collect into a Python list and concatenate once — the same reasoning as `''.join` over repeated `+=`.
    

And a structural observation worth noting: **this is the first section since lesson 8 where nothing is free.** Reshape, transpose, slicing and broadcasting were all views. Combination genuinely allocates, because two separate buffers cannot be described by one stride pattern.

---

## The Combination Section

|Lesson|Operation|Rank|Memory|
|---|---|---|---|
|**24 Concatenate**|join on an existing axis|unchanged|copy|
|25 Stack|join on a **new** axis|**+1**|copy|
|26 Split|the inverse of both|unchanged / −1|**view**|
|27 Tile / Repeat|join with itself|unchanged|copy|

```text
   concatenate:  (2,3) + (2,3)  ->  (4,3)      an axis GROWS
   stack:        (2,3) + (2,3)  ->  (2,2,3)    an axis APPEARS
```

> **Mental shift:** part 1 joined sequences with `+`, and part 2 concatenated rows with slicing. At rank 3 and up, "join along which axis?" has more than two answers, and the difference between *growing* an axis and *creating* one becomes a decision you have to make out loud. That's exactly what the next lesson covers.
