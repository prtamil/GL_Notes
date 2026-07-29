# 9. Ellipsis and newaxis

## Mental Model

Two small bits of index syntax that exist for the same reason: **so your code doesn't hard-code the rank.**

**Ellipsis (`...`)** stands for "as many `:` as needed":

```text
rank 3:   t[..., 0]   ==  t[:, :, 0]
rank 4:   q[..., 0]   ==  q[:, :, :, 0]
```

One expression, any rank. Write `t[:, :, 0]` and it breaks the day someone adds a batch dimension at the front. Write `t[..., 0]` and it keeps meaning "index the last axis".

**newaxis (`None`)** does the opposite: it **inserts** an axis of size 1.

```text
t[None]        (2,3,4)  ->  (1,2,3,4)     new axis at the front
t[:, None]     (2,3,4)  ->  (2,1,3,4)     new axis in the middle
t[..., None]   (2,3,4)  ->  (2,3,4,1)     new axis at the end
```

A size-1 axis holds no data. It's a **placeholder**, and alignment is its entire purpose. Broadcasting (lesson 17) matches shapes from the right and stretches every `1`, so inserting axes is how you tell NumPy *which* dimensions of two tensors should line up. Nearly every broadcasting bug is a missing `None`.

Both are **basic indexing**, so both return views. Neither copies anything.

---

## Relationship to Cognitive Verb

```text
Align
  ↓
Ellipsis and newaxis
```

Related verbs:

- Align
- Fill in the middle
- Insert a placeholder
- Make rank-agnostic
- Pad the shape

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Last axis, any rank|portable index|`t[..., 0]`|
|First axis, any rank|the other end|`t[0, ...]`|
|Slice the last axis|a range|`t[..., 1:3]`|
|Add a leading axis|batch of one|`t[None]`|
|Add a trailing axis|column vector|`t[..., None]`|
|Add in the middle|align for broadcast|`t[:, None]`|
|Named form|explicit|`np.newaxis` (it *is* `None`)|
|Function form|programmatic axis|`np.expand_dims(t, k)`|
|Remove size-1 axes|the inverse|`t.squeeze()`|
|Keep an axis on reduce|same effect|`keepdims=True`|

---

## Common Uses

- Writing rank-agnostic utilities
- Aligning tensors for broadcasting
- Turning a vector into a row or column
- Adding a batch dimension of 1 before a model call
- Adding a channel dimension to a grayscale image
- Outer products and pairwise distance matrices
- Keeping shapes compatible after a reduction

---

## Hidden Interview Problems

- Compute an outer product without loops
- Build a pairwise distance matrix
- Normalise each row of a matrix
- Add a batch dimension to a single sample
- Write a function that works on any rank
- Explain why `a - b` fails but `a[:, None] - b` works

---

## Recognition Clues

If you hear...

- "whatever the number of dimensions..."
- "the last axis..."
- "add a dimension..."
- "shapes are not aligned..."
- "pairwise / all-pairs / outer..."
- "batch of one..."

...think **Ellipsis and newaxis**.

---

## Pattern Summary

|Property|Value|
|---|---|
|`...`|Expands to the `:` needed to fill the rank|
|How many allowed|**One** per index expression|
|`None` / `np.newaxis`|Inserts an axis of size **1**|
|How many allowed|Any number, anywhere|
|Data|Neither moves any — both are views|
|Rank effect|`...` none; `None` adds 1 per use|
|Inverse of `None`|`squeeze()`|
|Equivalent function|`np.expand_dims(t, axis)`|
|Common Domains|Broadcasting, generic code, ML plumbing|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np

t = np.arange(24).reshape(2, 3, 4)
q = np.arange(16).reshape(2, 2, 2, 2)       # rank 4

# ============================================
# The one idiom to remember (part 1)
#
#   ...  means "all the axes I did not mention"

t[..., 0].shape             # => (2, 3)
t[..., 0]
# => array([[ 0,  4,  8],
#           [12, 16, 20]])

np.array_equal(t[..., 0], t[:, :, 0])       # => True

t[0, ...].shape             # => (3, 4)      same as t[0]
t[..., 1:3].shape           # => (2, 3, 2)   slices work too

# ============================================
# WHY it matters: rank portability

q.ndim                                      # => 4
q[..., 0].shape                             # => (2, 2, 2)
q[:, :, :, 0].shape                         # => (2, 2, 2)
np.array_equal(q[..., 0], q[:, :, :, 0])    # => True
#
# `t[..., 0]` is the SAME source line for rank 3 and
# rank 4. `t[:, :, 0]` would raise IndexError on rank 4
# — too many indices — or worse, silently index the
# wrong axis if the rank shrank.
#
# same argument as `axis=-1` in lesson 2: name the axis
# from the END and adding a batch dimension is harmless.

# ============================================
# Only one ellipsis

try:
    t[..., ..., 0]
except IndexError as e:
    print(e)
# an index can only have a single ellipsis ('...')
#
# and the reason is obvious once stated: two of them
# would be ambiguous about where the missing axes go.

np.shares_memory(t, t[..., 0])              # => True   still a view

# ============================================
# The one idiom to remember (part 2)
#
#   None  inserts an axis of size 1

t[None].shape               # => (1, 2, 3, 4)
t[:, None].shape            # => (2, 1, 3, 4)
t[..., None].shape          # => (2, 3, 4, 1)
t[:, :, :, None].shape      # => (2, 3, 4, 1)   same as above

np.newaxis is None          # => True
#
# `np.newaxis` is literally the constant None, exported
# under a readable name. Both spellings are correct;
# `None` is shorter, `np.newaxis` is clearer in a long
# index expression.

np.shares_memory(t, t[:, None])             # => True   free

# the function form, for when the axis is a variable:
np.expand_dims(t, 1).shape                  # => (2, 1, 3, 4)
np.array_equal(np.expand_dims(t, 1), t[:, None])        # => True

# ============================================
# The inverse: squeeze

z = np.zeros((1, 3, 1, 4))
z.shape                     # => (1, 3, 1, 4)

z.squeeze().shape           # => (3, 4)     ALL size-1 axes dropped
z.squeeze(axis=0).shape     # => (3, 1, 4)  just that one
z.squeeze(axis=2).shape     # => (1, 3, 4)

try:
    z.squeeze(axis=1)
except ValueError as e:
    print(e)
# cannot select an axis to squeeze out which has size not equal to one
#
# prefer `squeeze(axis=k)` over bare `squeeze()`. The
# bare form silently drops EVERY size-1 axis, so a batch
# of one becomes an unbatched sample and the bug appears
# two functions later.

# ============================================
# WHERE newaxis EARNS ITS KEEP: broadcasting
#
# Broadcasting aligns shapes from the RIGHT and stretches
# every 1. Inserting axes controls that alignment.

v1 = np.array([1, 2, 3])            # (3,)
v2 = np.array([10, 20, 30, 40])     # (4,)

# v1 + v2 -> ValueError, (3,) and (4,) do not align.

v1[:, None].shape           # => (3, 1)
v2[None, :].shape           # => (1, 4)

(v1[:, None] + v2[None, :]).shape       # => (3, 4)

v1[:, None] + v2[None, :]
# => array([[11, 21, 31, 41],
#           [12, 22, 32, 42],
#           [13, 23, 33, 43]])
#
#   (3, 1)
#   (1, 4)
#   ------
#   (3, 4)      every combination, no loop
#
# this is the outer-product pattern, and it is the
# single most useful thing newaxis does. Part 2's
# lesson 29 built coordinate grids with comprehensions;
# this is the same idea, vectorised.

# the trailing None can be omitted — broadcasting pads
# missing LEADING axes automatically:
np.array_equal(v1[:, None] + v2, v1[:, None] + v2[None, :])     # => True
#
# but write it when it aids clarity. Explicit alignment
# is cheaper to read than remembering the padding rule.

# ============================================
# Pairwise distances — the canonical application

pts = np.array([[0, 0], [3, 4], [6, 8]])        # 3 points in 2-D
pts.shape                   # => (3, 2)

diff = pts[:, None, :] - pts[None, :, :]
diff.shape                  # => (3, 3, 2)
#
#   (3, 1, 2)
#   (1, 3, 2)
#   ---------
#   (3, 3, 2)      every pair's coordinate difference

dist = np.sqrt((diff ** 2).sum(axis=-1))
dist.shape                  # => (3, 3)
dist
# => array([[ 0.,  5., 10.],
#           [ 5.,  0.,  5.],
#           [10.,  5.,  0.]])
#
# an all-pairs distance matrix, no loop. `pts[:, None]`
# versus `pts[None, :]` is what makes "every pair"
# happen — swap them and you get the transpose.

# ============================================
# keepdims does the same job on reductions

t.sum(axis=1).shape                     # => (2, 4)     axis gone
t.sum(axis=1, keepdims=True).shape      # => (2, 1, 4)  axis kept as 1

np.array_equal(t.sum(axis=1, keepdims=True), t.sum(axis=1)[:, None, :])
# => True
#
# `keepdims=True` is exactly "reduce, then put a None
# back where the axis was". It exists because the
# result is almost always about to be broadcast against
# the original — normalising, centring, softmax.
# (Lesson 21.)

# normalise each row of a matrix:
m = np.arange(12, dtype=float).reshape(3, 4)
(m / m.sum(axis=1, keepdims=True)).sum(axis=1)          # => [1., 1., 1.]
#
# without keepdims, m.sum(axis=1) is (3,) and would
# broadcast against the COLUMNS — wrong answer, no error.

# ============================================
# Adding a batch or channel dimension

sample = np.zeros((3, 224, 224))            # C, H, W
sample[None].shape                          # => (1, 3, 224, 224)   N=1

gray = np.zeros((224, 224))                 # H, W
gray[..., None].shape                       # => (224, 224, 1)      HWC
gray[None, ...].shape                       # => (1, 224, 224)      CHW
#
# which end you add to is the difference between a
# channel dimension and a batch dimension. Same syntax,
# entirely different meaning — lesson 2's warning again.

# ============================================
# Compare

t[..., 0]           # ellipsis  -> rank 2, view, portable
t[:, :, 0]          # explicit  -> rank 2, view, rank-locked
t[None]             # newaxis   -> rank 4, view
t[:, None]          # newaxis   -> rank 4, view
np.expand_dims(t,1) # function  -> same as t[:, None]
t.squeeze()         # inverse   -> drops all size-1 axes
t.sum(axis=1, keepdims=True)    # reduce, keep the slot

# all views:
[np.shares_memory(t, x) for x in (t[..., 0], t[None], t[:, None])]
# => [True, True, True]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the last axis, any rank|`t[..., 0]`|
|the first axis, any rank|`t[0, ...]`|
|to add a leading axis|`t[None]`|
|to add a trailing axis|`t[..., None]`|
|to align for broadcasting|`a[:, None]` against `b[None, :]`|
|a programmatic axis|`np.expand_dims(t, k)`|
|to drop size-1 axes|`squeeze(axis=k)` — **name the axis**|
|to keep an axis after reducing|`keepdims=True`|
|an outer product|`a[:, None] * b[None, :]`|
|all-pairs anything|`x[:, None] - x[None, :]`|

---

## Key Insight

**Both of these exist so the rank stays out of your source code.**

`...` fills in however many `:` the rank requires, so `t[..., 0]` means "the last axis" at rank 3, rank 4 or rank 7. `None` inserts a size-1 placeholder, so two tensors can be aligned deliberately instead of accidentally.

The second one is the load-bearing idea. Broadcasting matches shapes **from the right** and stretches every `1`, which means the shape of your result is decided by *where you put the `None`s*:

```text
a[:, None]  (3, 1)
b[None, :]  (1, 4)
            ------
            (3, 4)      every pair
```

That single move produces outer products, pairwise distance matrices, coordinate grids and every "all combinations" computation — with no loop. Almost every broadcasting error is a missing `None`, and almost every *silent* broadcasting error is a missing `keepdims=True`, which is the same insertion applied after a reduction.

Two things to be careful about:

1. **Only one `...` per expression**, because two would be ambiguous.
    
2. **Prefer `squeeze(axis=k)` to bare `squeeze()`.** The bare form drops *every* size-1 axis — so a legitimate batch of one silently becomes an unbatched sample, and the failure surfaces far from the cause.
    

Both are basic indexing, so both are **free views**. Adding and removing axes costs nothing but a new shape tuple.

---

## Ellipsis vs newaxis

|Syntax|Effect on rank|Purpose|
|---|---|---|
|`...`|unchanged|read at any rank|
|`None`|**+1** per use|align for broadcasting|
|`squeeze()`|**−1** per size-1 axis|remove placeholders|

```text
   t[..., 0]      "whatever the rank, the last axis"
   t[:, None]     "make room here so shapes line up"
```

> **Mental shift:** at rank 2 you always knew where you were. Rows and columns, both named. From rank 3 up, rank itself becomes a variable your code shouldn't depend on. `...` lets you index without counting axes, and `None` lets you create the axes that make two shapes agree. Between them, that's how tensor code stays short and stays correct when the rank changes underneath it.
