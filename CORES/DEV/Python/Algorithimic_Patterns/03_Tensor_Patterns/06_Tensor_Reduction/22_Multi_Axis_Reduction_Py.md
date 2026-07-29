# 22. Multi-Axis Reduction

## Mental Model

`axis=` takes a **tuple**. Every listed axis is deleted from the shape at once.

```text
t.shape = (2, 3, 4)

t.sum(axis=(1, 2))  ->  (2,)        both 3 and 4 gone
t.sum(axis=(0, 1))  ->  (4,)
t.sum(axis=(0, 2))  ->  (3,)
```

That's "collapse the spatial dimensions", "total over batch and time", "global average pooling" — one call, no intermediate array.

Two properties make this better than reducing one axis at a time:

- **Order doesn't matter.** `axis=(1,2)` and `axis=(2,1)` are the same thing, because all the axes go in one pass.
    
- **The axis numbers keep meaning what they said.** This is the real reason. Reducing one at a time **renumbers** whatever's left:

```text
t.sum(axis=0)            ->  (3, 4)      old axis 1 is now axis 0
t.sum(axis=0).sum(axis=1)   ==   t.sum(axis=(0, 2))     NOT (0, 1)
```

Read that twice. Once axis 0 is gone, the second `.sum(axis=1)` is talking about the *old axis 2*. Chained reductions shift under your feet without warning, and what you get back is a perfectly valid array holding the wrong statistic.

One deeper caution: **not every reduction composes.** Sums and maxima do — a sum of sums is a sum. Means only compose when the groups are the same size, and standard deviations never compose at all.

---

## Relationship to Cognitive Verb

```text
Collapse Many
     ↓
Multi-Axis Reduction
```

Related verbs:

- Collapse several
- Total over a region
- Pool
- Aggregate jointly
- Flatten and fold

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Several axes|a tuple|`t.sum(axis=(1, 2))`|
|Everything|the default|`t.sum()` or `axis=None`|
|Negative|from the end|`t.sum(axis=(-2, -1))`|
|Keep the slots|for broadcasting|`t.sum(axis=(1,2), keepdims=True)`|
|Adjacent axes|equivalent|`t.reshape(N, -1).sum(axis=1)`|
|Non-adjacent|move them together first|`np.moveaxis(...)` then reshape|
|Global pooling|spatial collapse|`img.mean(axis=(2, 3))`|
|Dataset statistics|all but the channel|`img.mean(axis=(0, 2, 3))`|
|Programmatic|build the tuple|`tuple(range(1, t.ndim))`|

---

## Common Uses

- Global average pooling in a CNN
- Per-sample loss from a per-pixel loss
- Dataset mean and std per channel
- Summing over height and width
- Totalling over batch and time
- Any-of / all-of across several dimensions
- Collapsing everything except one axis of interest

---

## Hidden Interview Problems

- Compute the mean over the spatial dimensions of an image batch
- Sum a tensor over all axes but one
- Compute per-channel dataset statistics
- Explain why chained reductions renumber the axes
- Reduce over a set of axes given at runtime
- Explain when a mean of means is wrong

---

## Recognition Clues

If you hear...

- "over height and width..."
- "global average pooling..."
- "per-channel statistics over the dataset..."
- "all axes except..."
- "total across batch and time..."

...think **Multi-Axis Reduction**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Argument|A tuple of axes|
|Shape rule|Deletes **every** listed entry|
|Rank|Drops by `len(axis)`|
|Order|Irrelevant — `(1,2) == (2,1)`|
|Negative axes|Allowed and mixable|
|`keepdims`|Every reduced axis becomes a 1|
|Equivalent to|Reshape-then-reduce, **if** the axes are adjacent|
|Chained reduction|**Renumbers** the remaining axes|
|Composability|`sum`/`max` always; `mean` if equal-sized; `std` never|
|Common Domains|CNNs, pooling, dataset statistics|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember
#
#   axis takes a TUPLE; every listed axis is deleted

import numpy as np

t = np.arange(24).reshape(2, 3, 4)

t.sum(axis=(1, 2))          # => array([ 66, 210])
t.sum(axis=(1, 2)).shape    # => (2,)          one total per block

t.sum(axis=(0, 1))          # => array([60, 66, 72, 78])
t.sum(axis=(0, 2))          # => array([ 60,  92, 124])
t.sum(axis=(0, 1, 2))       # => 276
t.sum(axis=(0, 1, 2)) == t.sum()                # => True

# order is irrelevant:
np.array_equal(t.sum(axis=(1, 2)), t.sum(axis=(2, 1)))          # => True

# negative axes work and can be mixed:
np.array_equal(t.sum(axis=(-2, -1)), t.sum(axis=(1, 2)))        # => True

# ============================================
# THE TRAP: chained reductions RENUMBER the axes

t.sum(axis=0).shape         # => (3, 4)
#
# the old axis 1 is now axis 0, and the old axis 2 is
# now axis 1. Everything shifted left.

t.sum(axis=0).sum(axis=0)   # => array([60, 66, 72, 78])
np.array_equal(t.sum(axis=0).sum(axis=0), t.sum(axis=(0, 1)))   # => True
#     "axis 0 then axis 0"  ==  axes (0, 1) of the ORIGINAL

t.sum(axis=0).sum(axis=1)   # => array([ 60,  92, 124])
np.array_equal(t.sum(axis=0).sum(axis=1), t.sum(axis=(0, 2)))   # => True
#     "axis 0 then axis 1"  ==  axes (0, 2) of the ORIGINAL
#
# So if you meant "reduce axes 0 and 1" and wrote
#
#     t.sum(axis=0).sum(axis=1)
#
# you reduced axes 0 and 2. It returns a perfectly valid
# array of the wrong statistic. Use the tuple form and
# the numbers always mean what they say.

# reducing from the RIGHT avoids the shift, if you must chain:
np.array_equal(t.sum(axis=2).sum(axis=1), t.sum(axis=(1, 2)))   # => True
#
# ...because deleting a later axis never renumbers an
# earlier one. But the tuple is clearer than relying on
# that.

# ============================================
# Equivalent to reshape-then-reduce — for ADJACENT axes

t.reshape(2, -1).sum(axis=1)                    # => array([ 66, 210])
np.array_equal(t.reshape(2, -1).sum(axis=1), t.sum(axis=(1, 2)))    # => True
#
# merging axes 1 and 2 into one (lesson 13) and reducing
# it is the same as reducing both. That is what NumPy
# does internally.

# for NON-adjacent axes you must bring them together:
np.array_equal(np.moveaxis(t, 1, 0).reshape(3, -1).sum(axis=1),
               t.sum(axis=(0, 2)))                              # => True
#
# move axis 1 to the front, then axes 0 and 2 of the
# original are adjacent and can be merged. `axis=(0,2)`
# saves you from writing this.

# ============================================
# keepdims puts back EVERY collapsed slot

t.sum(axis=(1, 2)).shape                        # => (2,)
t.sum(axis=(1, 2), keepdims=True).shape         # => (2, 1, 1)
#
# so the per-sample total broadcasts straight back:
(t / t.sum(axis=(1, 2), keepdims=True)).sum(axis=(1, 2))        # => [1., 1.]

# ============================================
# THE APPLICATION: global pooling and dataset stats

img = np.arange(2*3*4*4, dtype=float).reshape(2, 3, 4, 4)   # N, C, H, W

# global average pooling — collapse H and W, keep N and C
img.mean(axis=(2, 3)).shape                     # => (2, 3)
img.mean(axis=(2, 3), keepdims=True).shape      # => (2, 3, 1, 1)
#
# the keepdims form is what you subtract for instance
# normalisation; the flat form is what you feed a
# classifier head.

# per-channel statistics over the WHOLE dataset —
# collapse everything except the channel axis
img.mean(axis=(0, 2, 3)).shape                  # => (3,)
#
# this is the line that computes the normalisation
# constants for an image dataset. Note it reduces axes
# 0, 2 and 3 — non-adjacent, and trivial with a tuple.

# programmatically, "all axes but one":
keep = 1
axes = tuple(i for i in range(img.ndim) if i != keep)
axes                                            # => (0, 2, 3)
img.mean(axis=axes).shape                       # => (3,)

# ============================================
# WHICH REDUCTIONS COMPOSE?
#
# sum and max always do: a sum of sums is a sum.

np.array_equal(t.sum(axis=2).sum(axis=1), t.sum(axis=(1, 2)))   # => True
np.array_equal(t.max(axis=2).max(axis=1), t.max(axis=(1, 2)))   # => True

# mean composes only when the groups are EQUAL-SIZED:
np.allclose(t.mean(axis=(1, 2)), t.mean(axis=1).mean(axis=1))   # => True
#   (here every group has the same size, so it works)

# with unequal groups it does NOT:
a = np.array([1., 2., 3., 4., 5., 6.])
groups = [a[:4], a[4:]]                         # sizes 4 and 2

float(a.mean())                                 # => 3.5    the true mean
float(np.mean([g.mean() for g in groups]))      # => 4.0    mean of means
#
# the small group is over-weighted. A mean of means is
# only the mean when the groups are the same size —
# which is exactly why `axis=(1,2)` is safer than
# chaining `.mean()` calls whose group sizes you have
# to reason about.

# std NEVER composes, even with equal groups:
round(float(t.std()), 4)                        # => 6.9222
round(float(t.std(axis=(1, 2)).mean()), 4)      # => 3.4521
not np.isclose(t.std(), t.std(axis=(1, 2)).mean())              # => True
#
# the per-block stds miss the variation BETWEEN blocks.
# Compute std over all the axes you actually want, in
# one call. This is the strongest argument for the tuple
# form: it is not just tidier, it is sometimes the only
# correct spelling.

# ============================================
# Boolean reductions take tuples too

(t > 10).sum(axis=(1, 2))                       # => array([ 1, 12])
(t > 10).any(axis=(1, 2))                       # => array([ True,  True])
(t > 10).all(axis=(1, 2))                       # => array([False,  True])
#
# "does this sample contain any / only large values" —
# a per-sample predicate from a per-element test.

# ============================================
# Compare

t.sum(axis=1)                   # one axis     -> (2, 4)
t.sum(axis=(1, 2))              # two axes     -> (2,)
t.sum(axis=(1, 2), keepdims=True)   #           -> (2, 1, 1)
t.sum()                         # all axes     -> scalar
t.sum(axis=0).sum(axis=1)       # chained      -> (0, 2), NOT (0, 1)

[t.sum(axis=1).shape,
 t.sum(axis=(1, 2)).shape,
 t.sum(axis=(1, 2), keepdims=True).shape,
 np.shape(t.sum())]
# => [(2, 4), (2,), (2, 1, 1), ()]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|several axes|`axis=(i, j)` — a tuple|
|all but one|`tuple(i for i in range(ndim) if i != keep)`|
|global pooling|`img.mean(axis=(2, 3))`|
|dataset per-channel stats|`img.mean(axis=(0, 2, 3))`|
|the slots kept|`keepdims=True` — every one becomes a 1|
|**not** to chain|chained reductions **renumber** the axes|
|to chain anyway|reduce from the **right** first|
|a correct std|one call over all the axes — it never composes|
|a correct mean|the tuple form, unless groups are equal-sized|

---

## Key Insight

**Give `axis` a tuple and every listed axis is deleted in one pass** — order-independent, and the numbers refer to the *original* shape throughout.

That last part is the reason to prefer it, and the trap it avoids is genuinely nasty:

```python
t.sum(axis=0).sum(axis=1)   ==   t.sum(axis=(0, 2))     # not (0, 1)
```

After the first reduction the axes shift left, so the second `axis=1` means the old axis 2. Nothing raises; you get a well-shaped array of a statistic you did not ask for. Reducing from the right (`axis=2` then `axis=1`) happens to be safe, because deleting a later axis never renumbers an earlier one — but the tuple form says what you mean and needs no such reasoning.

The deeper point is about **composability**:

|Reduction|Composes?|
|---|---|
|`sum`, `max`, `min`, `any`, `all`|**always** — a sum of sums is a sum|
|`mean`|only when the groups are **equal-sized**|
|`std`, `var`, `median`|**never**|

A mean of means over unequal groups over-weights the small ones — `3.5` versus `4.0` in the worked example. And a mean of per-block standard deviations gives `3.45` where the true value is `6.92`, because it discards the variation *between* blocks. When you want a statistic over several axes, reduce over all of them **in one call**. For `std` that is not a style preference; it is the only correct spelling.

---

## One Axis vs Several

|Form|Shape|Notes|
|---|---|---|
|`t.sum(axis=1)`|`(2, 4)`|one axis deleted|
|`t.sum(axis=(1, 2))`|`(2,)`|both deleted, one pass|
|`t.sum(axis=1).sum(axis=1)`|`(2,)`|**same result here** — but by accident of renumbering|

```text
   tuple form:   axes named against the ORIGINAL shape
   chained:      axes renumber after every step
```

> **Mental shift:** part 2's reductions were always "per row" or "per column": one axis, no ambiguity. Once you have four axes, "reduce the spatial dimensions" names *two* of them, and the tuple is how you say that. Getting comfortable writing `axis=(0, 2, 3)` is what lets you compute a dataset statistic in one line instead of a chain you have to re-derive every time you read it.
