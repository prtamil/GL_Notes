# 16. Squeeze and Expand Dims

## Mental Model

The last structural operation, and the smallest: **add or remove an axis of size 1**.

```text
expand:   (2, 3, 4)  ->  (2, 1, 3, 4)
squeeze:  (2, 1, 3, 4)  ->  (2, 3, 4)
```

A size-1 axis holds no data. The element count doesn't change and neither does the flat order. It's a **slot**, and slots exist for two reasons:

- **Alignment.** Broadcasting matches shapes from the right and stretches every `1`. A size-1 axis is how you tell NumPy which dimensions should line up. Lesson 9 did this with the indexing form, `t[:, None]`.
    
- **Meaning.** A batch of one image is `(1, 3, 32, 32)`, not `(3, 32, 32)`. That `1` records that there *is* a batch axis. Drop it and you've changed what the tensor is, even though the numbers are identical.
    

Which sets up the trap this whole lesson exists for:

> **Bare `squeeze()` drops *every* size-1 axis.**

A perfectly legitimate batch-of-one quietly becomes an unbatched sample, and the failure surfaces somewhere else entirely. Always name the axis: `squeeze(axis=1)`.

The mirror-image trap is a **missing** size-1 axis, which is what a reduction without `keepdims=True` leaves you with. On a non-square tensor that raises. On a square one it broadcasts against the wrong axis and hands you confidently wrong numbers.

---

## Relationship to Cognitive Verb

```text
Adjust
   ↓
Squeeze and Expand Dims
```

Related verbs:

- Adjust the rank
- Insert a slot
- Drop a placeholder
- Pad the shape
- Keep the dimension

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Add an axis|indexing form|`t[:, None]`|
|Add an axis|function form|`np.expand_dims(t, k)`|
|Add several|a tuple|`np.expand_dims(t, (0, 1))`|
|Drop one axis|**named**|`t.squeeze(axis=k)`|
|Drop several|a tuple|`t.squeeze(axis=(0, 2))`|
|Drop all size-1|risky|`t.squeeze()`|
|Keep on reduction|the usual source|`t.sum(axis=k, keepdims=True)`|
|Keep on slicing|a size-1 slice|`t[0:1]` instead of `t[0]`|
|Batch of one|prepend|`t[None]`|
|Reshape form|explicit|`t.reshape(2, 1, 3, 4)`|

---

## Common Uses

- Adding a batch dimension before a model call
- Adding a channel dimension to a grayscale image
- Keeping shapes aligned after a reduction
- Removing a leftover axis after a size-1 slice
- Normalising along an axis
- Matching an API that demands a fixed rank
- Broadcasting a per-sample statistic back over its samples

---

## Hidden Interview Problems

- Add a dimension at a given position
- Remove all singleton dimensions
- Normalise each row of a matrix
- Explain why `x / x.sum(axis=1)` is wrong
- Convert `(H, W)` to `(1, 1, H, W)`
- Explain when `squeeze()` is dangerous
- Broadcast a per-sample mean back over the samples

---

## Recognition Clues

If you hear...

- "add a batch dimension..."
- "keepdims..."
- "shapes could not be broadcast..."
- "the extra dimension of size one..."
- "unsqueeze..." (PyTorch's name for `expand_dims`)
- "singleton dimension..."

...think **Squeeze and Expand Dims**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Effect|Insert or delete an axis of size **1**|
|Element count|Unchanged|
|Flat order|**Unchanged**|
|Returns|A **view**|
|`expand_dims(t, k)`|Rank + 1; identical to `t[..., None, ...]`|
|`squeeze(axis=k)`|Rank − 1; **raises** if that axis isn't 1|
|`squeeze()`|Drops **all** size-1 axes — dangerous|
|Main source of slots|`keepdims=True`, size-1 slices|
|Main purpose|Broadcast alignment|
|Time Complexity|O(1)|

---

## Python Recipe Book

```python
# ============================================
# The running examples

import numpy as np

t = np.arange(24).reshape(2, 3, 4)
z = np.zeros((1, 3, 1, 4))

# ============================================
# Expanding — three spellings, one operation

np.expand_dims(t, 0).shape      # => (1, 2, 3, 4)
np.expand_dims(t, 1).shape      # => (2, 1, 3, 4)
np.expand_dims(t, -1).shape     # => (2, 3, 4, 1)
np.expand_dims(t, 3).shape      # => (2, 3, 4, 1)   same as -1 here

np.array_equal(np.expand_dims(t, 0), t[None])       # => True
np.array_equal(np.expand_dims(t, 1), t[:, None])    # => True
t.reshape(2, 1, 3, 4).shape                         # => (2, 1, 3, 4)
#
#   t[:, None]              terse, best inside an expression
#   np.expand_dims(t, k)    when k is a VARIABLE
#   t.reshape(...)          when you are already reshaping

np.expand_dims(t, (0, 1)).shape                     # => (1, 1, 2, 3, 4)

np.shares_memory(t, np.expand_dims(t, 1))           # => True    free

# ============================================
# Squeezing — and why you must name the axis

z.shape                         # => (1, 3, 1, 4)

z.squeeze(axis=0).shape         # => (3, 1, 4)
z.squeeze(axis=2).shape         # => (1, 3, 4)
z.squeeze(axis=(0, 2)).shape    # => (3, 4)
z.squeeze().shape               # => (3, 4)      ALL of them

try:
    z.squeeze(axis=1)
except ValueError as e:
    print(e)
# cannot select an axis to squeeze out which has size not equal to one
#
# the named form CHECKS. That is the point of it — if
# your assumption about the shape is wrong, you find out
# here rather than three functions later.

z.size, z.squeeze().size        # => (12, 12)    no data moved
np.shares_memory(z, z.squeeze())                    # => True

# ============================================
# THE TRAP: bare squeeze() eats real dimensions

np.zeros((1, 5)).squeeze().shape                    # => (5,)
np.zeros((1, 1, 5)).squeeze().shape                 # => (5,)
#
# a batch of 1 sample with 1 channel became a bare
# vector. Both axes were meaningful; both are gone.

np.zeros((1, 1, 5)).squeeze(axis=1).shape           # => (1, 5)
#
# named: only the channel axis dropped, the batch axis
# survived. This is the version to write.
#
# The failure mode is nasty because it is DATA-DEPENDENT:
# `squeeze()` on a batch of 32 is harmless, and the same
# line silently breaks on the last batch of 1.

# ============================================
# Where size-1 axes come from

t.sum(axis=1, keepdims=True).shape      # => (2, 1, 4)   a reduction
t[0:1].shape                            # => (1, 3, 4)   a size-1 slice
t[None].shape                           # => (1, 2, 3, 4) explicit
np.take(t, [0], axis=0).shape           # => (1, 3, 4)   a length-1 index
#
# note the contrast with the rank-dropping forms:
t.sum(axis=1).shape                     # => (2, 4)
t[0].shape                              # => (3, 4)
#
# in each pair, one spelling keeps the slot and one
# removes it. Choosing deliberately is most of what
# this lesson is about.

# keepdims and expand_dims are the same thing:
np.array_equal(t.sum(axis=1, keepdims=True),
               np.expand_dims(t.sum(axis=1), 1))            # => True

t.sum(axis=1, keepdims=True).squeeze(axis=1).shape          # => (2, 4)
np.array_equal(t.sum(axis=1, keepdims=True).squeeze(axis=1),
               t.sum(axis=1))                               # => True

# ============================================
# WHY keepdims EXISTS — the silent-failure demo
#
# Normalise each row so it sums to 1.

m = np.arange(12, dtype=float).reshape(3, 4)

# correct:
(m / m.sum(axis=1, keepdims=True)).sum(axis=1)
# => array([1., 1., 1.])
#
#   m               (3, 4)
#   sum keepdims    (3, 1)   -> broadcasts across columns
#   ------------------------
#                   (3, 4)   correct

# without keepdims, on a NON-square matrix it raises:
try:
    m / m.sum(axis=1)
except ValueError as e:
    print(e)
# operands could not be broadcast together with shapes (3,4) (3,)
#
# lucky. The shapes disagree, so you find out.

# ...but on a SQUARE matrix it runs, and is WRONG:
sq = np.arange(16, dtype=float).reshape(4, 4)

(sq / sq.sum(axis=1)).sum(axis=1)
# => array([0.15364168, 1.18146376, 2.20928584, 3.23710792])
#
#   should be [1., 1., 1., 1.]
#
#   sq              (4, 4)
#   sum no keepdims (4,)   -> right-aligned to (1,4)
#   ------------------------
#                   (4, 4)   broadcast across ROWS, not columns
#
# it divided each COLUMN by the row sums. No error, no
# warning, plausible-looking numbers.

(sq / sq.sum(axis=1, keepdims=True)).sum(axis=1)
# => array([1., 1., 1., 1.])
#
# THIS is why `keepdims=True` is not optional styling.
# Reduce, then broadcast back — always keep the slot.

# (aside: that display is rounded. The last entry is
# really 0.9999999999999999 — ordinary float error, not
# a broadcasting bug. Compare with np.allclose, never ==)
(sq / sq.sum(axis=1, keepdims=True)).sum(axis=1).tolist()
# => [1.0, 1.0, 1.0, 0.9999999999999999]
np.allclose((sq / sq.sum(axis=1, keepdims=True)).sum(axis=1), 1.0)      # => True

# ============================================
# Adding a batch or channel dimension

sample = np.zeros((3, 224, 224))        # C, H, W — one image
sample[None].shape                      # => (1, 3, 224, 224)   N=1

gray = np.zeros((224, 224))             # H, W
gray[None].shape                        # => (1, 224, 224)      C first
gray[..., None].shape                   # => (224, 224, 1)      C last
#
# which end you add to decides whether it is a batch
# axis or a channel axis. Same call, different meaning —
# lesson 2's warning, one last time.

# and the round trip after a model call:
batched = sample[None]                  # (1, 3, 224, 224)
batched.squeeze(axis=0).shape           # => (3, 224, 224)
#
# named, so a genuine batch of 1 in some other position
# is never touched.

# ============================================
# Per-sample statistics, broadcast back

x = np.arange(24, dtype=float).reshape(2, 3, 4)

mean = x.mean(axis=(1, 2), keepdims=True)
mean.shape                              # => (2, 1, 1)
centred = x - mean
centred.shape                           # => (2, 3, 4)
centred.mean(axis=(1, 2))               # => array([0., 0.])
#
# (2,1,1) broadcasts back over (2,3,4) automatically.
# Without keepdims the mean would be (2,) and would
# right-align to the LAST axis — wrong, and on a tensor
# with a trailing 2 it would not even raise.

# ============================================
# Compare

t[:, None]                      # add a slot     -> rank +1, view
np.expand_dims(t, 1)            # same, variable axis
t.squeeze(axis=1)               # drop a slot    -> rank -1, view, CHECKED
t.squeeze()                     # drop all slots -> risky
t.sum(axis=1)                   # reduce, drop the axis
t.sum(axis=1, keepdims=True)    # reduce, keep the slot
t[0]                            # index, drop the axis
t[0:1]                          # slice, keep the slot

# every one of these is a view and preserves the flat order:
np.array_equal(t[:, None].ravel(), t.ravel())               # => True
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|an axis added|`t[:, None]` or `np.expand_dims(t, k)`|
|a batch of one|`t[None]`|
|a channel last|`t[..., None]`|
|an axis dropped|`t.squeeze(axis=k)` — **name it**|
|**not** to lose a batch axis|never bare `squeeze()`|
|to reduce and broadcast back|`keepdims=True`|
|to keep an axis while indexing|`t[0:1]`, not `t[0]`|
|to know if you needed keepdims|did the result get broadcast? then yes|

---

## Key Insight

**A size-1 axis carries no data but carries meaning, and both adding and dropping one are free views.** The whole lesson is about doing it *deliberately*, because both directions have a silent-failure mode:

**Dropping too much.** Bare `squeeze()` removes *every* size-1 axis. A batch of one becomes an unbatched sample, and — worst of all — the bug is data-dependent: the line works for 999 batches and breaks on the last one. `squeeze(axis=k)` checks the axis really is 1 and raises if not, which is exactly the feedback you want.

**Not adding enough.** A reduction without `keepdims=True` deletes the axis, and the result then right-aligns against the wrong dimension. The demonstration is worth remembering:

```python
sq = np.arange(16.).reshape(4, 4)

(sq / sq.sum(axis=1)).sum(axis=1)
# => [0.154, 1.181, 2.209, 3.237]      wrong, and silent

(sq / sq.sum(axis=1, keepdims=True)).sum(axis=1)
# => [1., 1., 1., 1.]                  correct
```

On a **non-square** matrix the first form raises and you are safe. On a **square** one it broadcasts across rows instead of columns and returns plausible numbers. Square tensors are common — batch size equal to sequence length, a 32×32 image — so this is a real bug, not a curiosity.

The habit that prevents both: **whenever you reduce and then use the result against the original, pass `keepdims=True`; whenever you squeeze, name the axis.**

---

## The Structure Section, Complete

|Lesson|Operation|Shape|Flat order|View?|
|---|---|---|---|---|
|12 Reshape|regroup|any compatible|**preserved**|if contiguous|
|13 Flatten / Ravel|merge adjacent axes|`→ (size,)`|**preserved**|if contiguous|
|14 Permute Axes|reorder all axes|permuted|**changed**|always|
|15 Swap / Move Axis|reorder one or two|permuted|**changed**|always|
|**16 Squeeze / Expand**|add or drop size-1|±1 rank|**preserved**|always|

```text
                  ┌── keep the tape order  ──►  12, 13, 16   (regroup)
  same cells  ────┤
                  └── reorder the tape     ──►  14, 15       (permute)
```

That dividing line, **does the flat order change?**, is exactly where part 2's structure section ended, and it's still the question that tells you which operation you want. `flat(reshape(t)) == flat(t)`. `flat(transpose(t))` generally doesn't.

> **Mental shift:** part 2's structure lessons were about *pictures*, rotating and flipping a grid you could see. Part 3's are about *contracts*: which axis means what, which ones line up, and whether the operation you just wrote kept the tape order or reordered it. The tensor is too big to picture, so the shape tuple becomes the thing you reason about, and `keepdims` plus a named `squeeze` are how you keep it honest.
