# 13. Flatten / Ravel

## Mental Model

Lesson 7 flattened so it could **iterate**. This lesson flattens to **restructure**, and the useful framing isn't "make it 1-D". It's this:

> **Flattening is merging adjacent axes.**

```text
(2, 3, 4)  ->  merge all      ->  (24,)
(2, 3, 4)  ->  merge 1 and 2  ->  (2, 12)
(2, 3, 4)  ->  merge 0 and 1  ->  (6, 4)
```

Full flattening is just the case where you merge *every* axis. Partial flattening — keep the batch, collapse everything else — is the one you'll actually write, over and over:

```python
t.reshape(t.shape[0], -1)       # (N, everything else)
t.reshape(-1, t.shape[-1])      # (everything else, C)
```

Merging is a reshape, so the same two rules hold: the **flat order is preserved** and the size is conserved.

There's one constraint, though, that only shows up once you have three or more axes:

> **Only adjacent axes can be merged.**

`(2, 3, 4)` can become `(6, 4)` or `(2, 12)`, but you can't merge axis 0 with axis 2 by reshaping, because they aren't neighbours on the tape. You have to **transpose first**, and that costs you a copy.

And the three spellings differ in one way worth knowing cold: `ravel()` is a view when it can be, `flatten()` is always a copy, `reshape(-1)` is a view when it can be.

---

## Relationship to Cognitive Verb

```text
Collapse
   ↓
Flatten / Ravel
```

Related verbs:

- Collapse
- Merge axes
- Linearise
- Fold together
- Squash

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Flatten, cheap|view when possible|`t.ravel()`|
|Flatten, safe|always a copy|`t.flatten()`|
|Flatten, explicit|same as ravel|`t.reshape(-1)`|
|Keep the first axis|batch flatten|`t.reshape(t.shape[0], -1)`|
|Keep the last axis|to vectors|`t.reshape(-1, t.shape[-1])`|
|Merge a range|adjacent only|`t.reshape(*before, prod(mid), *after)`|
|Split back|the inverse|`t.reshape(*before, a, b, *after)`|
|Non-adjacent axes|must reorder first|`transpose(...)` then `reshape(...)`|
|Memory order|never copies|`t.ravel(order='K')`|
|Column-major|Fortran|`t.ravel(order='F')`|

---

## Common Uses

- Flattening a feature map before a dense layer
- Merging batch and time axes to run a per-step op once
- Collapsing spatial dimensions for a global statistic
- Turning a volume into a feature vector
- Serialising to a file
- Preparing data for a 1-D algorithm
- Reshaping between `(N, T, C)` and `(N*T, C)` for a linear layer

---

## Hidden Interview Problems

- Flatten an n-dimensional array
- Flatten all but the first dimension
- Merge two axes of a tensor
- Split an axis back into two
- Explain `ravel` vs `flatten`
- Explain why merging non-adjacent axes needs a transpose
- Reconstruct the original shape after flattening

---

## Recognition Clues

If you hear...

- "flatten..."
- "collapse the last two dimensions..."
- "(N, -1)..."
- "merge batch and time..."
- "one long vector per sample..."
- "reshape to 2-D for the linear layer..."

...think **Flatten / Ravel**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Operation|Merge one or more **adjacent** axes|
|Full flatten|Merge all → `(size,)`|
|Flat order|**Preserved**|
|`ravel()`|View when contiguous, copy otherwise|
|`flatten()`|**Always** a copy|
|`reshape(-1)`|Same as `ravel()`|
|Non-adjacent axes|Impossible — transpose first (costs a copy)|
|Information lost|The shape — store it to reverse|
|Time Complexity|O(1) as a view, O(size) as a copy|

---

## Python Recipe Book

```python
# ============================================
# The running examples

import numpy as np

t = np.arange(24).reshape(2, 3, 4)
q = np.arange(2*3*4*5).reshape(2, 3, 4, 5)

# ============================================
# The three spellings

t.ravel().shape             # => (24,)
t.flatten().shape           # => (24,)
t.reshape(-1).shape         # => (24,)

np.array_equal(t.ravel(), t.flatten())          # => True
np.array_equal(t.ravel(), t.reshape(-1))        # => True

# identical values, different memory behaviour:
np.shares_memory(t, t.ravel())                  # => True    view
np.shares_memory(t, t.flatten())                # => False   COPY
np.shares_memory(t, t.reshape(-1))              # => True    view
#
#   ravel()      cheap; may alias
#   flatten()    safe; always allocates
#   reshape(-1)  same as ravel, reads as "one axis"
#
# use flatten() only when you specifically need
# independence — otherwise it is a wasted copy.

# ============================================
# ...and "when it can be" means CONTIGUOUS

tr = t.transpose(2, 1, 0)
np.shares_memory(tr, tr.ravel())                # => False   had to copy
np.shares_memory(tr, tr.ravel(order='K'))       # => True    memory order
#
# ravel() promises LOGICAL order. On a transposed view
# that is not the buffer order, so it allocates. order='K'
# takes whatever the strides give and never copies —
# fine for sums, wrong when the sequence matters
# (lesson 7).

# ============================================
# The one idiom to remember
#
#   flattening is MERGING ADJACENT AXES

t.shape                     # => (2, 3, 4)

t.reshape(6, 4).shape       # => (6, 4)      merged axes 0 and 1
t.reshape(2, 12).shape      # => (2, 12)     merged axes 1 and 2
t.reshape(24).shape         # => (24,)       merged all three
#
# 2*3 = 6 and 3*4 = 12. That is the whole operation:
# replace a run of axes with their product.

# ============================================
# The two partial flattens you will write constantly

# keep the batch, collapse everything else
t.reshape(t.shape[0], -1).shape             # => (2, 12)
t.reshape(2, -1)
# => array([[ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11],
#           [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]])
#
# one row per sample. This is the line before a dense
# layer, and `t.shape[0]` keeps it rank-agnostic.

# keep the feature axis, collapse everything before it
t.reshape(-1, t.shape[-1]).shape            # => (6, 4)
#
# one row per position. `(N, T, C) -> (N*T, C)` is how
# you apply a linear layer to every time step at once
# instead of looping.

# ============================================
# Merging an arbitrary RANGE of adjacent axes

def merge_axes(a, start, end):
    """Merge axes start..end (inclusive) into one."""
    s = a.shape
    return a.reshape(s[:start] + (int(np.prod(s[start:end+1])),) + s[end+1:])

q.shape                             # => (2, 3, 4, 5)

merge_axes(q, 1, 2).shape           # => (2, 12, 5)      3*4
merge_axes(q, 0, 2).shape           # => (24, 5)         2*3*4
merge_axes(q, 2, 3).shape           # => (2, 3, 20)      4*5

# and the inverse:
def split_axis(a, axis, sizes):
    """Split one axis into several; prod(sizes) must match."""
    s = a.shape
    return a.reshape(s[:axis] + tuple(sizes) + s[axis+1:])

split_axis(merge_axes(q, 1, 2), 1, (3, 4)).shape        # => (2, 3, 4, 5)
np.array_equal(split_axis(merge_axes(q, 1, 2), 1, (3, 4)), q)       # => True
#
# merge then split is a perfect round trip, because
# neither touches the tape order.

# ============================================
# THE CONSTRAINT: only ADJACENT axes merge
#
# (2, 3, 4) can become (6, 4) or (2, 12).
# It cannot become "(8, 3)" meaning axes 0 and 2 merged,
# because those two are not neighbours on the tape.

t.reshape(8, 3).shape       # => (8, 3)
#
# ...that call SUCCEEDS, and it is not what you meant.
# It merely re-cut the same tape into 8 groups of 3. It
# did NOT pair axis 0 with axis 2.

# to genuinely merge axes 0 and 2, bring them together:
t.transpose(0, 2, 1).reshape(2*4, 3).shape              # => (8, 3)
np.array_equal(t.reshape(8, 3), t.transpose(0, 2, 1).reshape(8, 3))
# => False
#
# same shape, different data — lesson 12's warning again.
# And the transpose makes the array non-contiguous, so
# THAT reshape copies:
np.shares_memory(t, t.transpose(0, 2, 1).reshape(8, 3)) # => False

# ============================================
# Practical: the (N, T, C) pattern

x = np.arange(2*5*3).reshape(2, 5, 3)       # N=2 sequences, T=5 steps, C=3
x.shape                                     # => (2, 5, 3)

flat = x.reshape(-1, x.shape[-1])
flat.shape                                  # => (10, 3)
#
# now a (3, 8) weight matrix applies to all 10 positions
# with one matmul:
W = np.ones((3, 8))
out = (flat @ W).reshape(*x.shape[:-1], -1)
out.shape                                   # => (2, 5, 8)
#
# merge -> operate -> split back. The shape prefix
# `x.shape[:-1]` is what makes the restore rank-agnostic.

# ============================================
# Flattening discards the shape

flat = t.ravel()
flat.shape                                  # => (24,)
flat.reshape(2, 3, 4).shape                 # => (2, 3, 4)
np.array_equal(flat.reshape(2, 3, 4), t)    # => True
#
# 24 values are equally (24,), (4,6), (2,12) or (2,3,4).
# Store the shape with the data — same warning as part 2
# lesson 23, and the reason `x.shape` is captured before
# the flatten in the pattern above.

# ============================================
# The pure-Python equivalent, and why it stops scaling

nested = t.tolist()
[x for a in nested for b in a for x in b][:6]   # => [0, 1, 2, 3, 4, 5]
#
# correct, rank-3-only, and it builds a new list. The
# rank-agnostic version is the recursion from lesson 6.
# NumPy's version usually allocates nothing at all.

# ============================================
# Compare

t.ravel()                       # merge ALL axes      -> view
t.flatten()                     # merge ALL axes      -> copy
t.reshape(2, -1)                # merge axes 1..end   -> view
t.reshape(-1, 4)                # merge axes 0..-2    -> view
merge_axes(q, 1, 2)             # merge a range       -> view
t.transpose(0,2,1).reshape(8,3) # non-adjacent        -> COPY

# all of these preserve the flat order:
np.array_equal(t.reshape(2, -1).ravel(), t.ravel())     # => True
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|flatten cheaply|`t.ravel()` or `t.reshape(-1)`|
|flatten with independence|`t.flatten()`|
|one row per sample|`t.reshape(t.shape[0], -1)`|
|one row per position|`t.reshape(-1, t.shape[-1])`|
|to merge a range|replace it with `prod(sizes)`|
|to split it back|replace the size with its factors|
|non-adjacent axes merged|`transpose` first — and pay the copy|
|never to copy|`order='K'` (memory order)|
|to restore the shape|capture `x.shape` **before** flattening|

---

## Key Insight

**Flattening is merging adjacent axes, and full flattening is just the extreme case.** Once you see it that way, the whole family is one operation with a parameter:

```text
(2,3,4) -> (24,)      merge 0..2
        -> (6,4)      merge 0..1
        -> (2,12)     merge 1..2
```

All of them are reshapes, so all of them **preserve the flat order** and are free on contiguous data.

Three things to hold on to:

1. **The adjacency constraint is real, and it fails silently.** `t.reshape(8, 3)` succeeds on a `(2,3,4)` tensor, but it did not merge axis 0 with axis 2 — it merely re-cut the tape. To genuinely pair non-adjacent axes you must `transpose` first, which reorders the tape *and* costs a copy.
    
2. **`ravel` and `reshape(-1)` are views; `flatten` always copies.** Reach for `flatten()` only when you need independence, otherwise it is a wasted allocation.
    
3. **Capture the shape before you flatten.** The merge → operate → split-back pattern (`x.reshape(-1, C) @ W` then `.reshape(*x.shape[:-1], -1)`) is how a per-position operation runs in one matmul instead of a loop, and it only works if you kept the prefix.
    

---

## Flatten vs Reshape

|Operation|What it does|Typical spelling|
|---|---|---|
|**Reshape**|any regrouping|`t.reshape(4, 6)`|
|**Flatten**|merge adjacent axes|`t.reshape(N, -1)`|

Flatten is a **special case** of reshape, not a different mechanism — which is why `t.reshape(-1)` and `t.ravel()` are the same call.

```text
   reshape:  move any cuts
   flatten:  remove some cuts        (a strict subset)
```

> **Mental shift:** at rank 2, "flatten" meant exactly one thing: go to 1-D. From rank 3 up it's a dial. How many axes do you want to fold together? Most real tensor plumbing is that dial set to "collapse everything except the batch" or "collapse everything except the features".
