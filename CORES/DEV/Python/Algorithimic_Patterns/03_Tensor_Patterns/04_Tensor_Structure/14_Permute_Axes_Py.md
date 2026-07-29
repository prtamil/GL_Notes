# 14. Permute Axes

## Mental Model

Part 2's lesson 16 had **one** interesting rearrangement: transpose, `(r,c) → (c,r)`. At rank 2 that is the only non-trivial permutation there is.

At rank `n` there are `n!` of them.

```text
rank 2:   2 permutations       identity, transpose
rank 3:   6
rank 4:  24
```

So the operation stops being "transpose" and becomes "**state the new axis order**":

```python
t.transpose(2, 0, 1)
```

Read that as: *the new axis 0 is the old axis 2; the new axis 1 is the old axis 0; the new axis 2 is the old axis 1.* Which gives the rule for predicting the shape without thinking:

```text
out.shape[i] == t.shape[perm[i]]

t.shape = (2, 3, 4)
perm    = (2, 0, 1)
out     = (4, 2, 3)
```

And the elements follow the same relabelling: `t[i,j,k] == out[k,i,j]`.

Like every structural operation since lesson 4, this is a **view** — permuting axes permutes the *strides* and touches no data. But unlike reshape, it **changes the flat order**, which is the dividing line of this whole section and the reason a later `reshape` may suddenly copy.

---

## Relationship to Cognitive Verb

```text
Reorder
   ↓
Permute Axes
```

Related verbs:

- Reorder the axes
- Relabel dimensions
- Transpose (generalised)
- Rearrange
- Change the layout

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Arbitrary order|state the permutation|`t.transpose(2, 0, 1)`|
|Function form|same thing|`np.transpose(t, (2, 0, 1))`|
|Reverse all axes|the shorthand|`t.T`|
|Last two only|matrix transpose per batch|`t.transpose(0, 2, 1)`|
|Predict the shape|no execution needed|`tuple(t.shape[i] for i in perm)`|
|Undo|inverse permutation|`np.argsort(perm)`|
|Compose|two permutations|apply the second to the first|
|Layout conversion|NCHW ↔ NHWC|`t.transpose(0, 2, 3, 1)`|
|Check the cost|did it copy?|`np.shares_memory(t, t.transpose(...))`|
|Restore contiguity|before reshaping|`np.ascontiguousarray(t)`|

---

## Common Uses

- Converting between NCHW and NHWC image layouts
- Preparing tensors for batched matrix multiply
- Moving the feature axis to the end for a linear layer
- Aligning axes before broadcasting
- Reordering `(T, N, C)` ↔ `(N, T, C)` for sequence models
- Matching the layout a library expects
- Transposing the last two axes of a batch of matrices

---

## Hidden Interview Problems

- Transpose a 3-D array along given axes
- Convert an image batch between layouts
- Reverse the axis order of a tensor
- Compute the inverse of an axis permutation
- Explain why `.T` on a rank-3 array is not a matrix transpose
- Batch-transpose a stack of matrices
- Explain why transpose then reshape copies

---

## Recognition Clues

If you hear...

- "swap the axes so that..."
- "channels last / channels first..."
- "NCHW / NHWC..."
- "the layout the library expects..."
- "transpose the last two dimensions..."
- "permute..."

...think **Permute Axes**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Argument|A permutation of `range(ndim)`|
|Shape rule|`out.shape[i] == t.shape[perm[i]]`|
|Element rule|`t[idx] == out[tuple(idx[p] for p in perm)]`|
|Count|`n!` permutations at rank `n`|
|Returns|A **view** — strides are permuted|
|Flat order|**Changed**|
|Contiguity|Usually lost|
|`.T`|Reverses **all** axes, not just the last two|
|Inverse|`np.argsort(perm)`|
|Time Complexity|O(1)|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np
import math

t = np.arange(24).reshape(2, 3, 4)

# ============================================
# The one idiom to remember
#
#   transpose(perm) means "new axis i is old axis perm[i]"

t.transpose(2, 0, 1).shape          # => (4, 2, 3)

# predict it without running anything:
tuple(t.shape[i] for i in (2, 0, 1))                # => (4, 2, 3)
#
#   new axis 0 <- old axis 2  (size 4)
#   new axis 1 <- old axis 0  (size 2)
#   new axis 2 <- old axis 1  (size 3)

t.transpose(1, 0, 2).shape          # => (3, 2, 4)   swap the first two
np.transpose(t, (2, 0, 1)).shape    # => (4, 2, 3)   function form

# ============================================
# The elements follow the same relabelling

int(t[1, 2, 3])                     # => 23
int(t.transpose(2, 0, 1)[3, 1, 2])  # => 23
#
# the index (i,j,k) moves to (k,i,j) — the SAME
# permutation applied to the index tuple.

all(t[i, j, k] == t.transpose(2, 0, 1)[k, i, j]
    for i, j, k in np.ndindex(*t.shape))            # => True

# ============================================
# How many are there

math.factorial(2)           # => 2      rank 2: identity, transpose
math.factorial(3)           # => 6
math.factorial(4)           # => 24
#
# part 2 had one interesting rearrangement and could
# name it "transpose". At rank 4 there are 24 and they
# need to be spelled out.

# ============================================
# .T reverses ALL axes — a common surprise

t.T.shape                   # => (4, 3, 2)
t.shape[::-1]               # => (4, 3, 2)
np.array_equal(t.T, t.transpose(2, 1, 0))           # => True
#
# on a rank-2 array .T is the matrix transpose you
# expect. On rank 3+ it is NOT "transpose the last two
# axes" — it reverses everything.
#
# for a batch of matrices you almost always want:
t.transpose(0, 2, 1).shape  # => (2, 4, 3)      keep axis 0, swap 1 and 2

# which is what makes batched matmul work:
A = np.arange(24).reshape(2, 3, 4)      # 2 matrices, each 3x4
(A @ A.transpose(0, 2, 1)).shape        # => (2, 3, 3)
#
# `A @ A.T` would try (2,3,4) @ (4,3,2) and fail. This
# is the single most common .T bug in tensor code.

# ============================================
# IT IS A VIEW — the strides are permuted

np.shares_memory(t, t.transpose(2, 0, 1))           # => True

t.strides                           # => (96, 32, 8)
t.transpose(2, 0, 1).strides        # => (8, 96, 32)
#
# the SAME three numbers, permuted by (2,0,1). That is
# the entire implementation. Nothing is copied — part 2
# built a whole new list of lists to transpose a matrix.

# ============================================
# BUT the flat order changes

t.ravel()[:8]                       # => [0, 1, 2, 3, 4, 5, 6, 7]
t.transpose(1, 0, 2).ravel()[:8]    # => [0, 1, 2, 3, 12, 13, 14, 15]

np.array_equal(t.transpose(1, 0, 2).ravel(), t.ravel())     # => False
#
# compare lesson 12:
np.array_equal(t.reshape(3, 2, 4).ravel(), t.ravel())       # => True
#
#   reshape   keeps the tape order, moves the cuts
#   transpose reorders the tape
#
# and because the tape order changed, the array is no
# longer contiguous, so a following reshape must copy:
tr = t.transpose(1, 0, 2)
tr.flags['C_CONTIGUOUS']                            # => False
np.shares_memory(tr, tr.reshape(24))                # => False

# ============================================
# Undoing a permutation — argsort

perm = (2, 0, 1)
inv = tuple(np.argsort(perm))
inv                                 # => (1, 2, 0)

np.array_equal(t.transpose(perm).transpose(inv), t)         # => True

# applying the SAME permutation twice does NOT undo it:
np.array_equal(t.transpose(perm).transpose(perm), t)        # => False
#
# (that only works for permutations that are their own
# inverse — swaps, and .T.)
#
# argsort(perm) is the inverse because argsort answers
# "where did each position come from?", which is exactly
# the reverse relabelling.

# ============================================
# Composing permutations

np.array_equal(t.transpose(2, 0, 1).transpose(2, 0, 1),
               t.transpose(1, 2, 0))                # => True
#
# applying (2,0,1) twice equals applying (1,2,0) once.
# Permutations form a group — the rank-n generalisation
# of part 2's D4 table in lesson 21.

# ============================================
# THE application: image layout conversion

img = np.zeros((8, 3, 32, 32))      # N, C, H, W   (PyTorch default)
img.shape                           # => (8, 3, 32, 32)

img.transpose(0, 2, 3, 1).shape     # => (8, 32, 32, 3)   NHWC (TensorFlow)
#
#   new 0 <- old 0   (N)
#   new 1 <- old 2   (H)
#   new 2 <- old 3   (W)
#   new 3 <- old 1   (C)

# and back:
img.transpose(0, 2, 3, 1).transpose(0, 3, 1, 2).shape       # => (8, 3, 32, 32)
#
# (0,3,1,2) is argsort((0,2,3,1)). Feeding the wrong
# layout to a model does not raise — the shapes are all
# valid — it just trains badly. Lesson 2's warning, with
# a concrete cost.

# ============================================
# The nested-list version, for contrast

nested = t.tolist()

def transpose_nested_201(n):
    I, J, K = len(n), len(n[0]), len(n[0][0])
    return [[[n[i][j][k] for j in range(J)]         # new axes k, i, j
             for i in range(I)]
            for k in range(K)]

np.array_equal(transpose_nested_201(nested), t.transpose(2, 0, 1))      # => True
#
# 24 elements copied into a brand-new nested structure,
# and the loop order has to be worked out by hand for
# every permutation. NumPy permutes a 3-tuple of strides.

# ============================================
# Compare

t.reshape(3, 2, 4)          # regroup   -> flat order KEPT
t.transpose(1, 0, 2)        # reorder   -> flat order CHANGED
t.T                         # reverse ALL axes
t.transpose(0, 2, 1)        # batch matrix transpose
t.swapaxes(0, 1)            # one swap  -> lesson 15
np.moveaxis(t, 0, 2)        # one move  -> lesson 15

# same shape, different data:
t.reshape(3, 2, 4).shape == t.transpose(1, 0, 2).shape          # => True
np.array_equal(t.reshape(3, 2, 4), t.transpose(1, 0, 2))        # => False
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|any axis order|`t.transpose(perm)`|
|to read it|"new axis `i` is old axis `perm[i]`"|
|the output shape|`tuple(t.shape[i] for i in perm)`|
|**not** `.T` on rank 3+|it reverses **all** axes|
|a batch matrix transpose|`t.transpose(0, 2, 1)`|
|to undo a permutation|`np.argsort(perm)`|
|NCHW → NHWC|`transpose(0, 2, 3, 1)`|
|to know it's free|it is — strides are permuted|
|to know the next reshape isn't|contiguity is gone|

---

## Key Insight

**`transpose(perm)` means "the new axis `i` is the old axis `perm[i]`."** Everything else falls out of that one reading:

```text
shape:    out.shape[i] == t.shape[perm[i]]
elements: t[i,j,k]     == out[k,i,j]        for perm = (2,0,1)
strides:  permuted, not recomputed          -> it is a view
inverse:  np.argsort(perm)
```

The two things that actually cause bugs:

1. **`.T` reverses every axis.** On rank 2 it is the familiar matrix transpose; on rank 3+ it turns `(2,3,4)` into `(4,3,2)`, which is almost never what you want. For a batch of matrices, `transpose(0, 2, 1)` — and `A @ A.T` failing where `A @ A.transpose(0,2,1)` works is the canonical symptom.
    
2. **It changes the flat order, so contiguity is lost.** This is the difference from reshape, and it is why `x.transpose(...).reshape(...)` silently allocates. If you are going to reshape after permuting and do it often, `np.ascontiguousarray` once and make the copy explicit.
    

The rest is arithmetic you can do in your head: predict `out.shape` with `tuple(t.shape[i] for i in perm)` before running anything, and `np.argsort(perm)` to get back. Permutations compose, which makes them a group — the rank-n generalisation of part 2's eight square symmetries.

---

## Permute vs Reshape

|Operation|Cells|Flat order|Shape|Cost|
|---|---|---|---|---|
|**Reshape**|same|**preserved**|any compatible|free if contiguous|
|**Permute**|same|**changed**|a permutation|always free (view)|

```text
   the tape:  0 1 2 3 4 5 ... 23

   reshape    ->  same tape, new cuts
   transpose  ->  new tape order
```

They can produce **the same shape** from the same input and different data — `t.reshape(3,2,4)` and `t.transpose(1,0,2)` are both `(3,2,4)`. Neither raises. That is the one thing from this lesson worth being paranoid about.

> **Mental shift:** at rank 2 "transpose" was a word. At rank n it is a *permutation you have to write down*, and the useful skill is reading `(2,0,1)` as a relabelling rather than picturing the rotation. Predict the shape from the tuple, use `argsort` to invert, and never let `.T` near a rank-3 tensor.
