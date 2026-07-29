# 2. Axes

## Mental Model

An **axis is a position in the shape tuple.** That is the whole definition, and everything else follows from it.

```text
shape = (2, 3, 4)
         ↑  ↑  ↑
    axis 0  1  2
```

Axis 0 is the **outermost** — the one `len()` sees, the one a plain `for` loop walks. Axis `ndim-1` is the **innermost** — the one whose elements sit next to each other in memory.

The phrase that does the real work is **"along an axis"**:

> To operate *along axis k*, vary index `k` and hold every other index fixed.

```text
t[i][j][k]  with shape (2, 3, 4)

along axis 0   ->  t[·][j][k]   2 values, for each fixed (j, k)
along axis 1   ->  t[i][·][k]   3 values, for each fixed (i, k)
along axis 2   ->  t[i][j][·]   4 values, for each fixed (i, j)
```

And the consequence you use constantly: **a reduction along axis `k` deletes entry `k` from the shape.**

```text
(2, 3, 4).sum(axis=0)  ->  (3, 4)      the 2 is gone
(2, 3, 4).sum(axis=1)  ->  (2, 4)      the 3 is gone
(2, 3, 4).sum(axis=2)  ->  (2, 3)      the 4 is gone
```

If you can predict which number disappears, you can predict every reduction, and you never need to reason about the nested brackets.

Two more facts worth having in reflex memory: **negative axes count from the right** (`axis=-1` is always the innermost, whatever the rank), and **a shape carries no meaning** — `(32, 3, 224, 224)` is only "NCHW" because a convention says so.

---

## Relationship to Cognitive Verb

```text
Orient
   ↓
Axes
```

Related verbs:

- Orient
- Choose a direction
- Work along
- Fix the others
- Name the dimension

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Reduce along an axis|collapse it|`t.sum(axis=k)`|
|Several axes|collapse many|`t.sum(axis=(0, 2))`|
|Everything|full reduction|`t.sum()` — `axis=None`|
|Innermost axis|whatever the rank|`axis=-1`|
|Outermost axis|the first|`axis=0`|
|Iterate axis 0|the default|`for sub in t`|
|Iterate another axis|bring it to the front|`np.moveaxis(t, k, 0)`|
|Which axis vanishes|predict the shape|drop entry `k` from the tuple|
|Reorder axes|permute|`t.transpose(...)`|
|Keep the rank|size-1 placeholder|`keepdims=True`|

---

## Common Uses

- Per-sample statistics in a batch (`axis=0`)
- Per-feature statistics (`axis=-1`)
- Normalising along a chosen direction
- Channel-wise operations on images
- Collapsing spatial dimensions (`axis=(2, 3)`)
- Time-series reduction over a time axis
- Converting between NCHW and NHWC layouts
- Softmax over the class axis

---

## Hidden Interview Problems

- Sum a 3D array along each axis
- Compute the mean over the spatial dimensions of an image batch
- Normalise each row / column / channel
- Transpose an image batch between layouts
- Find the per-sample maximum
- Reduce all axes but one
- Explain why `axis=0` and `axis=1` give different shapes

---

## Recognition Clues

If you hear...

- "along the ... axis"
- "per row / per column / per channel / per sample"
- "collapse the time dimension"
- "average over height and width"
- "for each image in the batch"
- "the last dimension"

...think **Axes**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Axis|A position in the shape tuple|
|Axis 0|Outermost — what `len()` and `for` see|
|Axis `-1`|Innermost — adjacent in memory|
|"Along axis k"|Vary index `k`, hold the rest fixed|
|Reduction effect|Deletes entry `k` from the shape|
|Negative axes|`axis=-1` ≡ `axis=ndim-1`|
|Multiple axes|`axis=(i, j)` — a tuple|
|`axis=None`|Reduce everything to a scalar|
|Common Domains|ML, images, signals, statistics|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np

t = np.arange(24).reshape(2, 3, 4)
nested = t.tolist()

t.shape                     # => (2, 3, 4)
#                                 ↑  ↑  ↑
#                            axis 0  1  2

# ============================================
# The one idiom to remember
#
#   axis=k  means  "vary index k, hold the others"
#
# and the shape loses entry k.

t.sum(axis=0).shape         # => (3, 4)     lost the 2
t.sum(axis=1).shape         # => (2, 4)     lost the 3
t.sum(axis=2).shape         # => (2, 3)     lost the 4

# predict it without running anything:
[tuple(s for i, s in enumerate(t.shape) if i != a) for a in (0, 1, 2)]
# => [(3, 4), (2, 4), (2, 3)]

# ============================================
# What each one actually computes

t.sum(axis=0)
# => array([[12, 14, 16, 18],
#           [20, 22, 24, 26],
#           [28, 30, 32, 34]])
#
# element [j][k] = t[0][j][k] + t[1][j][k]
# e.g. [0][0] = 0 + 12 = 12

t.sum(axis=1)
# => array([[12, 15, 18, 21],
#           [48, 51, 54, 57]])
#
# element [i][k] = t[i][0][k] + t[i][1][k] + t[i][2][k]
# e.g. [0][0] = 0 + 4 + 8 = 12

t.sum(axis=2)
# => array([[ 6, 22, 38],
#           [54, 70, 86]])
#
# element [i][j] = sum of the 4 innermost values
# e.g. [0][0] = 0 + 1 + 2 + 3 = 6

t.sum()                     # => 276    axis=None, everything

# ============================================
# What the library is doing — nested lists
#
# Note the pattern: the summed index is the one inside
# sum(), and the surviving indices become the loops.

def sum_axis0(n):
    I, J, K = len(n), len(n[0]), len(n[0][0])
    return [[sum(n[i][j][k] for i in range(I))     # i is consumed
             for k in range(K)] for j in range(J)] # j, k survive

def sum_axis1(n):
    I, J, K = len(n), len(n[0]), len(n[0][0])
    return [[sum(n[i][j][k] for j in range(J))     # j is consumed
             for k in range(K)] for i in range(I)] # i, k survive

def sum_axis2(n):
    I, J, K = len(n), len(n[0]), len(n[0][0])
    return [[sum(n[i][j][k] for k in range(K))     # k is consumed
             for j in range(J)] for i in range(I)] # i, j survive

sum_axis0(nested) == t.sum(axis=0).tolist()        # => True
sum_axis1(nested) == t.sum(axis=1).tolist()        # => True
sum_axis2(nested) == t.sum(axis=2).tolist()        # => True

sum_axis0(nested)
# => [[12, 14, 16, 18], [20, 22, 24, 26], [28, 30, 32, 34]]
#
# three near-identical functions, differing only in
# WHICH index moves into the sum. `axis=k` is a
# parameter for exactly that choice — which is why you
# should never write these loops by hand.

# ============================================
# Negative axes — count from the right
#
# axis=-1 is the innermost REGARDLESS of rank, which
# makes it the portable way to say "the feature axis".

np.array_equal(t.sum(axis=-1), t.sum(axis=2))       # => True
np.array_equal(t.sum(axis=-3), t.sum(axis=0))       # => True

# on a rank-2 array, axis=-1 is axis 1; on rank-5 it is
# axis 4. Code written with -1 keeps working when a
# batch dimension is added in front. Code written with
# an absolute axis number silently breaks.

# ============================================
# Several axes at once

t.sum(axis=(0, 1))          # => array([60, 66, 72, 78])
t.sum(axis=(0, 1)).shape    # => (4,)      both 2 and 3 removed

t.sum(axis=(1, 2)).shape    # => (2,)
t.sum(axis=(0, 1, 2))       # => 276       same as t.sum()

# ============================================
# Iteration always walks axis 0

[sub.shape for sub in t]    # => [(3, 4), (3, 4)]
len(list(t))                # => 2
#
# `for sub in t` gives you 2 matrices of shape (3,4).
# There is no built-in way to loop another axis — you
# move it to the front first:

[sub.shape for sub in np.moveaxis(t, 1, 0)]         # => [(2,4), (2,4), (2,4)]
[sub.shape for sub in np.moveaxis(t, 2, 0)]         # => [(2,3)] * 4
#
# (moveaxis is lesson 15; it returns a view, so this
# costs nothing.)

# ============================================
# Axes have no built-in meaning — write it down
#
# The canonical image-batch layouts use the same four
# numbers to mean different things.

img = np.zeros((2, 3, 32, 32))          # N, C, H, W
img.shape                               # => (2, 3, 32, 32)
img.shape[0]                            # => 2    N, batch size
img.shape[1]                            # => 3    C, colour channels

# "average each channel over the image" = collapse H, W
img.mean(axis=(2, 3)).shape             # => (2, 3)      N, C

# convert NCHW -> NHWC by permuting axes
img.transpose(0, 2, 3, 1).shape         # => (2, 32, 32, 3)
#
# read transpose(0,2,3,1) as "the new axis order is
# old-0, old-2, old-3, old-1". Nothing moves in memory;
# only the interpretation changes (lesson 14).
#
# NCHW is PyTorch's default, NHWC is TensorFlow's. A
# model fed the wrong one does not crash — it trains
# badly. Shape alone cannot catch it.

# ============================================
# A practical habit: normalise along a named axis

x = np.arange(12, dtype=float).reshape(3, 4)    # 3 samples, 4 features

x.mean(axis=0).shape        # => (4,)   per-FEATURE mean, over samples
x.mean(axis=1).shape        # => (3,)   per-SAMPLE mean, over features
#
# these are completely different statistics and both
# run without error. The shape is the only clue, which
# is why `axis=` should always be written explicitly —
# never rely on the default.

# ============================================
# Compare

t.sum(axis=0)               # collapse the outermost
t.sum(axis=-1)              # collapse the innermost
t.sum(axis=(0, 1))          # collapse two
t.sum()                     # collapse all

t.sum(axis=1).shape         # => (2, 4)     rank drops by 1
t.sum(axis=1, keepdims=True).shape          # => (2, 1, 4)   rank kept
#
# keepdims is lesson 21, and it is the single most
# useful flag in this part — it keeps shapes aligned
# for broadcasting.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the definition of an axis|a position in `shape`|
|"along axis k"|vary index `k`, hold the rest|
|the output shape|delete entry `k` from the tuple|
|the innermost axis, any rank|`axis=-1`|
|the batch axis|`axis=0`|
|to collapse several|`axis=(i, j)`|
|to loop a non-zero axis|`np.moveaxis(t, k, 0)` first|
|to keep the rank|`keepdims=True`|
|to know what an axis means|a comment — shape won't say|

---

## Key Insight

**An axis is a position in the shape tuple, and a reduction deletes that position.**

```text
(2, 3, 4)  --sum(axis=1)-->  (2, 4)
```

That rule is enough to predict the output of every reduction, stack, split and transpose in part 3 without thinking about brackets. Predicting the shape *before* you run the code is the core skill this section is building, because a wrong `axis=` almost never raises — it produces a valid array of the wrong shape, and the error surfaces somewhere else entirely.

Three practical consequences:

1. **Write `axis=` explicitly, always.** `x.mean(axis=0)` (per-feature) and `x.mean(axis=1)` (per-sample) are different statistics, both legal, and the default is neither of them — `mean()` collapses everything.
    
2. **Prefer `axis=-1` for "the innermost".** It survives someone adding a batch dimension in front; an absolute axis number does not.
    
3. **Only axis 0 is iterable.** `for sub in t` walks the outermost axis and there is no alternative — to loop another, `np.moveaxis(t, k, 0)` it to the front first, which is free because it returns a view.
    

And the failure this section cannot protect you from: **shapes carry sizes, not meanings.** `(32, 3, 224, 224)` is NCHW only by convention; hand it to code expecting NHWC and nothing raises — the model simply learns nothing. Name your axes in comments, or use a library with named axes.

---

## Axes vs Shape

|Concept|Answers|Example|
|---|---|---|
|**Shape**|*How big in each direction?*|`(2, 3, 4)`|
|**Axis**|*Which direction?*|`axis=1` → the `3`|

```text
  shape  =  the sizes            (2, 3, 4)
  axis   =  which slot you mean       ↑
                                   axis 1
```

> **Mental shift:** in part 1 there was one direction and in part 2 there were two, so "rows" and "columns" were enough. Beyond rank 2 the names run out and the axis *number* becomes the vocabulary. Getting fluent at reading `axis=k` as "delete slot k from the shape" is what makes the rest of part 3 mechanical.
