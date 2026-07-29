# 18. Axis Alignment

## Mental Model

Lesson 17 gave the rule. This lesson is about the consequence nobody expects:

> **Broadcasting aligns from the right, so which axis a vector lands on is decided by the shape, not by your intent.**

The cleanest demonstration is a matrix and its two sums:

```text
m.shape          (3, 4)
m.sum(axis=0)       (4,)     column sums
m.sum(axis=1)    (3,)        row sums
```

Divide by each:

```text
m / m.sum(axis=0)      (3,4) vs (4,)   ->  works
m / m.sum(axis=1)      (3,4) vs (3,)   ->  RAISES
```

**Normalising columns works without any help. Normalising rows does not.** Not because one is harder, but because right-alignment puts the `4` under the `4` in one case and the `3` under the `4` in the other.

So the skill is putting the size-1 axes where you need them:

```python
m / m.sum(axis=1, keepdims=True)        # (3,4) vs (3,1)   -> works
m + v[:, None]                          # align v with rows
t + v[:, None, None]                    # align v with axis 0 of a rank-3
```

And the reason this matters more than it should: **when the sizes happen to coincide, the wrong alignment does not raise.** A square matrix will silently normalise across the wrong axis. That is the failure mode this lesson exists to prevent.

---

## Relationship to Cognitive Verb

```text
Align
  ↓
Axis Alignment
```

Related verbs:

- Line up
- Aim at an axis
- Position the placeholder
- Match deliberately
- Target a dimension

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Align with the last axis|automatic|shape `(C,)` — nothing to do|
|Align with any axis|add trailing 1s|`v[:, None]`, `v[:, None, None]`|
|Keep an axis after reducing|the usual fix|`keepdims=True`|
|Programmatic axis|when it's a variable|`v.reshape([-1 if i==ax else 1 ...])`|
|Function form|same|`np.expand_dims(v, axes)`|
|Check before trusting|predict|`np.broadcast_shapes(a.shape, b.shape)`|
|Inspect what happened|debug|`np.broadcast_arrays(a, b)`|
|Rank-agnostic|from the end|`...` and negative axes|
|Per-channel on NCHW|`(C,1,1)`|`ch[:, None, None]`|

---

## Common Uses

- Normalising rows vs columns
- Per-channel mean subtraction on images
- Per-sample scaling in a batch
- Centring data before PCA
- Softmax over a chosen axis
- Applying per-timestep weights to a sequence
- Any "divide by the sum along axis k" operation

---

## Hidden Interview Problems

- Normalise each row of a matrix so it sums to 1
- Subtract the per-channel mean from an image batch
- Explain why row normalisation needs `keepdims`
- Scale each sample in a batch by its own factor
- Standardise features (subtract mean, divide by std)
- Write a function that normalises along an arbitrary axis

---

## Recognition Clues

If you hear...

- "per row / per column / per channel / per sample..."
- "operands could not be broadcast together..."
- "divide by the sum along..."
- "subtract the mean of each..."
- "normalise along axis k..."

...think **Axis Alignment**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Alignment direction|From the **right**|
|Last axis|Aligns automatically — no work needed|
|Any other axis|Needs trailing size-1 axes|
|After a reduction|`keepdims=True` puts the slot back|
|Rule of thumb|`k` trailing `None`s targets the `k`-th-from-last axis|
|Failure mode 1|Raises — sizes disagree (good)|
|Failure mode 2|**Silent** — sizes coincide (bad)|
|Cost|Free — all of this is stride-0 views|
|Common Domains|Normalisation, statistics, ML preprocessing|

---

## Python Recipe Book

```python
# ============================================
# The asymmetry that starts everything

import numpy as np

m = np.arange(12, dtype=float).reshape(3, 4)
m.shape                     # => (3, 4)

m.sum(axis=0).shape         # => (4,)    one per column
m.sum(axis=1).shape         # => (3,)    one per row

# columns: works with no help at all
(m / m.sum(axis=0)).shape   # => (3, 4)
(m / m.sum(axis=0, keepdims=True)).sum(axis=0)      # => [1., 1., 1., 1.]

# rows: raises
try:
    m / m.sum(axis=1)
except ValueError as e:
    print(str(e)[:55])
# operands could not be broadcast together with shapes (3,4) (3,)
#
#   (3, 4)              (3, 4)
#      (4,)   works        (3,)   fails
#   ------              ------
#   4 vs 4 equal        4 vs 3 mismatch
#
# The LAST axis is the one that aligns for free. Every
# other axis needs a placeholder.

# ============================================
# The one idiom to remember
#
#   keepdims=True keeps the slot the reduction removed

(m / m.sum(axis=1, keepdims=True)).sum(axis=1)      # => [1., 1., 1.]
#
#   m               (3, 4)
#   sum keepdims    (3, 1)   <- the 1 marks "this axis was here"
#   ---------------------
#                   (3, 4)   stretched across columns. Correct.

m.sum(axis=1, keepdims=True).shape                  # => (3, 1)
m.sum(axis=1).shape                                 # => (3,)

# ============================================
# THE SILENT CASE — square shapes hide the bug

sq = np.arange(16, dtype=float).reshape(4, 4)

(sq / sq.sum(axis=1)).sum(axis=1)
# => array([0.15364168, 1.18146376, 2.20928584, 3.23710792])
#    should be [1., 1., 1., 1.]

(sq / sq.sum(axis=1, keepdims=True)).sum(axis=1)
# => array([1., 1., 1., 1.])
#
# On a (3,4) matrix the missing keepdims RAISES.
# On a (4,4) matrix it runs and divides each COLUMN by
# the row sums. Same bug, and only one of them tells you.
#
# Square shapes are everywhere — batch == sequence length,
# 32x32 images, attention matrices. Do not rely on the
# error to catch this.

# ============================================
# Aligning a vector with a chosen axis
#
# The rule: k trailing Nones target the k-th-from-last axis.

v3 = np.array([1., 2., 3.])
v3.shape                    # => (3,)
v3[:, None].shape           # => (3, 1)

(m + v3[:, None])
# => array([[ 1.,  2.,  3.,  4.],
#           [ 6.,  7.,  8.,  9.],
#           [11., 12., 13., 14.]])
#
# one value added per ROW. Without the None it would
# have tried to align 3 against 4 and raised.

# on a rank-3 tensor, each axis needs a different number:
t = np.arange(24).reshape(2, 3, 4)

(t + np.array([1, 2, 3, 4])).shape                  # => (2,3,4)  axis 2
(t + np.array([1, 2, 3])[:, None]).shape            # => (2,3,4)  axis 1
(t + np.array([1, 2])[:, None, None]).shape         # => (2,3,4)  axis 0
#
#   axis -1  ->  (4,)        0 extra Nones
#   axis -2  ->  (3, 1)      1 extra None
#   axis -3  ->  (2, 1, 1)   2 extra Nones
#
# count from the END. That is why negative axes and `...`
# keep coming up: they are stated relative to the side
# alignment starts from.

# check it does what you think:
(t + np.array([100, 200])[:, None, None])[0, 0]     # => [100, 101, 102, 103]
(t + np.array([100, 200])[:, None, None])[1, 0]     # => [212, 213, 214, 215]
#
# block 0 got +100, block 1 got +200. Correct.

# ============================================
# When the axis is a VARIABLE

def align(v, axis, ndim):
    """Shape v so it broadcasts against `axis` of an ndim tensor."""
    shape = [1] * ndim
    shape[axis] = -1
    return v.reshape(shape)

align(np.array([1, 2]), 0, 3).shape         # => (2, 1, 1)
align(np.array([1, 2, 3]), 1, 3).shape      # => (1, 3, 1)
align(np.array([1, 2, 3, 4]), 2, 3).shape   # => (1, 1, 4)

np.array_equal(t + align(np.array([100, 200]), 0, 3),
               t + np.array([100, 200])[:, None, None])         # => True
#
# all-1s with a -1 in one slot. This is how you write a
# function that takes `axis=` — the companion to lesson
# 15's move-to-(-1) trick.

# the library form:
np.array_equal(np.expand_dims(np.array([1, 2]), (1, 2)),
               np.array([1, 2])[:, None, None])                 # => True

# ============================================
# Practical: centring an image batch

img = np.arange(2*3*4*4, dtype=float).reshape(2, 3, 4, 4)       # N, C, H, W

# per-image-per-channel mean over the spatial axes
mean = img.mean(axis=(2, 3), keepdims=True)
mean.shape                          # => (2, 3, 1, 1)

centred = img - mean
centred.shape                       # => (2, 3, 4, 4)
centred.mean(axis=(2, 3))
# => array([[0., 0., 0.],
#           [0., 0., 0.]])          every channel now zero-mean

# without keepdims:
img.mean(axis=(2, 3)).shape         # => (2, 3)
try:
    img - img.mean(axis=(2, 3))
except ValueError as e:
    print(str(e)[:60])
# operands could not be broadcast together with shapes (2,3,4,4) (2,3)
#
# (2,3) right-aligns against (4,4) — nonsense, and it
# says so. Here the error is a gift; on a (2,3,2,3)
# tensor it would have silently "worked".

# ============================================
# Practical: a per-channel constant

ch = np.array([1., 2., 3.])         # one value per channel
ch.shape                            # => (3,)

# NCHW: the channel axis is axis 1, i.e. 2 from the end
ch[:, None, None].shape             # => (3, 1, 1)
(img - ch[:, None, None]).shape     # => (2, 3, 4, 4)
#
#   img              (2, 3, 4, 4)
#   ch[:,None,None]     (3, 1, 1)
#   -------------------------------
#                    (2, 3, 4, 4)
#
# in NHWC layout the same vector needs NO Nones, because
# the channel axis is already last. The alignment code
# depends on the layout — one more reason to write the
# layout down (lesson 2).

# ============================================
# Standardising features — the full pattern

x = np.arange(12, dtype=float).reshape(3, 4)        # 3 samples, 4 features

mu = x.mean(axis=0, keepdims=True)      # (1, 4)  per FEATURE
sd = x.std(axis=0, keepdims=True)       # (1, 4)
zs = (x - mu) / sd
zs.shape                                # => (3, 4)
np.allclose(zs.mean(axis=0), 0)         # => True
np.allclose(zs.std(axis=0), 1)          # => True
#
# axis=0 reduces OVER the samples, giving one statistic
# per feature — the (1,4) then stretches down the rows.
# `axis=0` and `axis=1` here are different statistics and
# both run; only the shapes tell you which you got.

# ============================================
# Debugging an alignment

a = np.arange(6).reshape(3, 2)
b = np.arange(2)

np.broadcast_shapes(a.shape, b.shape)               # => (3, 2)   predict first

x, y = np.broadcast_arrays(a, b)
y
# => array([[0, 1],
#           [0, 1],
#           [0, 1]])
#
# `broadcast_arrays` shows you exactly what got stretched.
# When a broadcast runs but gives the wrong answer, this
# is the two-line diagnosis.

# ============================================
# Compare

m / m.sum(axis=0)                   # last axis  -> free
m / m.sum(axis=1)                   # other axis -> RAISES
m / m.sum(axis=1, keepdims=True)    # other axis -> correct
m / m.sum(axis=1)[:, None]          # same thing, written manually

np.array_equal(m / m.sum(axis=1, keepdims=True),
               m / m.sum(axis=1)[:, None])          # => True
#
# keepdims=True and [:, None] are the same operation.
# Prefer keepdims — it cannot get the position wrong.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|to align with the last axis|nothing — it's automatic|
|to align with axis −2|one trailing `None`|
|to align with axis −3|two trailing `None`s|
|to reduce and broadcast back|`keepdims=True`, always|
|a variable axis|all-1s shape with `-1` in one slot|
|per-channel on NCHW|`ch[:, None, None]`|
|to predict|`np.broadcast_shapes(a.shape, b.shape)`|
|to diagnose|`np.broadcast_arrays(a, b)`|
|**not** to trust silence|square shapes hide misalignment|

---

## Key Insight

**The last axis aligns for free; every other axis needs a placeholder.**

That single asymmetry produces the whole lesson. Column statistics on a `(3,4)` matrix have shape `(4,)` and broadcast back automatically. Row statistics have shape `(3,)` and do not — the `3` lands under the `4`. It is not that rows are harder; it is that alignment starts from the right.

The counting rule is worth memorising because it removes all guesswork:

```text
to target axis -1  ->  (C,)          no extra Nones
to target axis -2  ->  (C, 1)        one
to target axis -3  ->  (C, 1, 1)     two
```

And `keepdims=True` is simply "put back the slot I just removed", which is why it should be your default on any reduction whose result will meet the original again.

The reason to be disciplined rather than reactive: **broadcasting has two failure modes, and only one of them is loud.**

|Sizes|Result|
|---|---|
|disagree|`ValueError` — you find out immediately|
|coincide|**runs, wrong answer** — you find out much later|

A `(3,4)` matrix protects you; a `(4,4)` matrix does not. Square shapes are common — attention matrices, 32×32 images, batch size equal to sequence length — so "it didn't raise" is not evidence that the alignment was right. Predict the shape with `np.broadcast_shapes` before you run it, and use `np.broadcast_arrays` when the answer looks odd.

---

## Alignment vs the Rules

|Lesson|Answers|
|---|---|
|17 Broadcasting Rules|*Will these two shapes combine, and what does it cost?*|
|**18 Axis Alignment**|*Will they combine the way I meant?*|

```text
   17:  (3,4) and (3,)   ->  incompatible          a fact
   18:  I wanted rows    ->  use keepdims          a decision
```

> **Mental shift:** the rule in lesson 17 is mechanical and you will internalise it quickly. This lesson is about intent, which the rule cannot see. NumPy will happily align a per-row statistic with your columns if the numbers permit — so the discipline is to state the alignment explicitly (`keepdims`, an explicit `None`) rather than letting it fall out of whatever shapes happen to exist.
