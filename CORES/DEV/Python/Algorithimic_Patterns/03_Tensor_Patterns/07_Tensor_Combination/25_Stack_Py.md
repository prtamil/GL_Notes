# 25. Stack

## Mental Model

Concatenate grew an axis. **Stack creates one.**

```text
a  (2, 3)
b  (2, 3)

stack([a, b], axis=0)  ->  (2, 2, 3)      a NEW leading axis of length 2
stack([a, b], axis=2)  ->  (2, 3, 2)      a NEW trailing axis
```

The rank goes up by one, and the new axis is as long as the **number of arrays** you handed over. That forces a stricter requirement than concatenate:

> **All inputs must have *exactly* the same shape.**

There's no "except the join axis" clause here, because the join axis didn't exist yet.

This is the operation that turns **a list of samples into a batch**:

```python
np.stack([img0, img1, img2])        # (3, H, W) from three (H, W) images
```

and `axis=` decides where the new dimension lands: `axis=0` for a batch dimension, `axis=-1` for a channel dimension. Same call, different meaning entirely.

The relationship to lesson 24 is exact. Stacking is concatenating after inserting a size-1 axis into every input.

```python
np.stack([a, b], axis=1)  ==  np.concatenate([a[:, None], b[:, None]], axis=1)
```

---

## Relationship to Cognitive Verb

```text
Layer
  ↓
Stack
```

Related verbs:

- Layer
- Pile up
- Batch together
- Add a dimension
- Assemble

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|New axis at the front|a batch|`np.stack(items)` — `axis=0` is the default|
|New axis at the back|channels|`np.stack(items, axis=-1)`|
|Anywhere|explicit|`np.stack(items, axis=k)`|
|Equivalent form|expand then join|`np.concatenate([x[:,None] ...], axis=1)`|
|Undo it|back to a list|`list(batch)` — iterating gives views|
|Undo along another axis|move first|`list(np.moveaxis(t, k, 0))`|
|1-D as rows|shortcut|`np.vstack` ≡ `np.stack(..., axis=0)`|
|1-D as columns|shortcut|`np.column_stack` ≡ `np.stack(..., axis=1)`|
|From a generator|needs a sequence|`np.stack(list(gen))`|

---

## Common Uses

- Building a batch from a list of samples
- Assembling RGB channels into an image
- Collecting per-epoch metrics into an array
- Stacking model predictions for an ensemble
- Turning a list of coordinate arrays into a point cloud
- Combining time steps into a sequence tensor
- Gathering results from a loop

---

## Hidden Interview Problems

- Combine a list of matrices into a 3-D array
- Stack RGB channels into an image
- Explain the difference between `stack` and `concatenate`
- Convert a list of vectors into a matrix, as rows or as columns
- Split a batch back into a list of samples
- Add a batch dimension to a single sample

---

## Recognition Clues

If you hear...

- "build a batch..."
- "stack the channels..."
- "collect the results into an array..."
- "a list of images / samples / predictions..."
- "add a new dimension for..."

...think **Stack**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Rank|**+1**|
|New axis length|The **number of arrays**|
|Input shapes|Must be **identical** — no exceptions|
|`axis`|Where the new axis goes; `0` is the default|
|Equivalent to|`concatenate` after inserting a size-1 axis|
|Returns|A **copy**|
|Inverse|`list(t)` for `axis=0`; `moveaxis` first otherwise|
|Empty list|Raises|
|Common Domains|Batching, ML pipelines, image channels|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember

import numpy as np

a = np.arange(6).reshape(2, 3)
b = np.arange(6, 12).reshape(2, 3)

np.stack([a, b], axis=0).shape      # => (2, 2, 3)
np.stack([a, b], axis=1).shape      # => (2, 2, 3)
np.stack([a, b], axis=2).shape      # => (2, 3, 2)
np.stack([a, b], axis=-1).shape     # => (2, 3, 2)

a.ndim, np.stack([a, b]).ndim       # => (2, 3)      rank +1

# the new axis length is the COUNT of arrays:
c = np.arange(100, 106).reshape(2, 3)
np.stack([a, b, c], axis=0).shape   # => (3, 2, 3)

# ============================================
# SHAPE ALONE DOES NOT TELL YOU WHICH AXIS
#
# axis=0 and axis=1 both gave (2,2,3) above — because
# a is (2,3) and there are 2 arrays. The CONTENT differs.

np.stack([a, b], axis=0)
# => array([[[ 0,  1,  2],
#            [ 3,  4,  5]],
#
#           [[ 6,  7,  8],
#            [ 9, 10, 11]]])
#    [0] is all of a, [1] is all of b

np.stack([a, b], axis=1)
# => array([[[ 0,  1,  2],
#            [ 6,  7,  8]],
#
#           [[ 3,  4,  5],
#            [ 9, 10, 11]]])
#    [0] is row 0 of a beside row 0 of b
#
# same shape, interleaved differently. Never verify a
# stack by its shape alone when the sizes coincide.

np.stack([a, b], axis=2)
# => array([[[ 0,  6],
#            [ 1,  7],
#            [ 2,  8]],
#
#           [[ 3,  9],
#            [ 4, 10],
#            [ 5, 11]]])
#    each element of a paired with its counterpart in b

# ============================================
# ALL SHAPES MUST MATCH — no exceptions

d = np.arange(8).reshape(2, 4)

try:
    np.stack([a, d])
except ValueError as e:
    print(e)
# all input arrays must have the same shape
#
# compare with lesson 24, where `concatenate([a, d],
# axis=1)` was fine. Concatenate allows one axis to
# differ; stack allows none.

# ============================================
# Stack IS concatenate plus a size-1 axis

np.array_equal(np.stack([a, b], axis=0),
               np.concatenate([a[None], b[None]], axis=0))          # => True

np.array_equal(np.stack([a, b], axis=1),
               np.concatenate([a[:, None], b[:, None]], axis=1))    # => True
#
# insert the new axis in every input (lesson 9), then
# concatenate along it. `stack` is that, spelled once.

# ============================================
# THE APPLICATION: a list of samples -> a batch

frames = [np.full((2, 2), i) for i in range(3)]
[f.shape for f in frames]           # => [(2,2), (2,2), (2,2)]

batch = np.stack(frames)
batch.shape                         # => (3, 2, 2)     N, H, W
batch
# => array([[[0, 0],
#            [0, 0]],
#
#           [[1, 1],
#            [1, 1]],
#
#           [[2, 2],
#            [2, 2]]])

# the same three arrays as CHANNELS instead of a batch:
np.stack(frames, axis=-1).shape     # => (2, 2, 3)     H, W, C
#
# one argument decides whether you built a batch of 3
# grayscale images or one 3-channel image. Nothing
# raises either way — lesson 2's warning again.

# ============================================
# The inverse: unstack

list(batch)                         # a list of 3 (2,2) arrays
[f.shape for f in list(batch)]      # => [(2,2), (2,2), (2,2)]
np.array_equal(np.stack(list(batch)), batch)            # => True
#
# iterating walks axis 0 (lesson 5), so `list(t)` undoes
# `stack(..., axis=0)`. And it is FREE — the pieces are
# views:
np.shares_memory(batch, list(batch)[0])                 # => True

# for another axis, move it to the front first:
[f.shape for f in np.moveaxis(np.stack(frames, axis=-1), -1, 0)]
# => [(2,2), (2,2), (2,2)]
#
# note the asymmetry: STACKING copies, UNSTACKING does not.
np.shares_memory(a, np.stack([a, b]))                   # => False

# ============================================
# 1-D inputs: stack replaces the shortcuts cleanly

x1 = np.array([1, 2, 3])
x2 = np.array([4, 5, 6])

np.stack([x1, x2], axis=0)
# => array([[1, 2, 3],
#           [4, 5, 6]])          as ROWS

np.stack([x1, x2], axis=1)
# => array([[1, 4],
#           [2, 5],
#           [3, 6]])             as COLUMNS

np.array_equal(np.stack([x1, x2]), np.vstack([x1, x2]))             # => True
np.array_equal(np.stack([x1, x2], axis=1), np.column_stack([x1, x2]))   # => True
#
# lesson 24 noted that vstack promotes 1-D input and
# hstack does not. `stack` has no such special case —
# it ALWAYS adds an axis, at any rank. That consistency
# is why it is the better default.

# ============================================
# Practical: assembling RGB

h, w = 2, 2
red   = np.full((h, w), 255)
green = np.full((h, w), 128)
blue  = np.full((h, w), 0)

hwc = np.stack([red, green, blue], axis=-1)
hwc.shape                           # => (2, 2, 3)     H, W, C
hwc[0, 0]                           # => array([255, 128,   0])

chw = np.stack([red, green, blue], axis=0)
chw.shape                           # => (3, 2, 2)     C, H, W
#
# the two standard image layouts, from the same three
# channel arrays. `axis` is the only difference.

# ============================================
# Practical: collecting loop results

results = []
for i in range(4):
    results.append(np.arange(3) * i)        # cheap: list append

out = np.stack(results)
out.shape                           # => (4, 3)
out
# => array([[0, 0, 0],
#           [0, 1, 2],
#           [0, 2, 4],
#           [0, 3, 6]])
#    row i is [0, 1, 2] * i
#
# collect into a list, stack ONCE — the same advice as
# lesson 24's "never concatenate in a loop", for the
# same reason.

# ============================================
# Compare

np.concatenate([a, b], axis=0)      # (4, 3)      grows axis 0
np.stack([a, b], axis=0)            # (2, 2, 3)   creates axis 0
np.stack([a, b], axis=-1)           # (2, 3, 2)   creates a trailing axis
list(np.stack([a, b]))              # back to [a, b]   — views
a[None]                             # (1, 2, 3)   "stack" of one (lesson 9)

[np.concatenate([a, b], axis=0).shape,
 np.stack([a, b], axis=0).shape]
# => [(4, 3), (2, 2, 3)]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a batch from a list|`np.stack(items)`|
|channels from a list|`np.stack(items, axis=-1)`|
|the rule|**all** shapes identical; rank **+1**|
|the new axis length|the number of arrays|
|the equivalence|`stack` = insert `None`, then `concatenate`|
|to undo it|`list(t)` — and it's **free**|
|to undo another axis|`np.moveaxis(t, k, 0)` first|
|1-D as rows / columns|`axis=0` / `axis=1` — no shortcut needed|
|to build in a loop|append to a **list**, stack once|

---

## Key Insight

**Stack creates an axis; concatenate grows one.** Everything else follows:

```text
concatenate  (2,3) + (2,3)  ->  (4,3)      an axis got longer
stack        (2,3) + (2,3)  ->  (2,2,3)    an axis appeared
```

Because the new axis did not exist in the inputs, there is no "all but one" exemption — **every input shape must match exactly**. And the new axis's length is simply how many arrays you passed, which is what makes `np.stack(list_of_samples)` the canonical way to build a batch.

Three things worth carrying:

1. **The shape can lie about which axis you used.** Stacking two `(2,3)` arrays gives `(2,2,3)` for *both* `axis=0` and `axis=1` — different content, identical shape. When the sizes coincide, check a value, not just `.shape`.
    
2. **`axis` decides the semantics.** `np.stack(frames)` is a batch of three images; `np.stack(frames, axis=-1)` is one three-channel image. Same inputs, both valid, neither raises.
    
3. **Stacking copies; unstacking does not.** `np.stack([a, b])` allocates, but `list(batch)` returns views into it — iterating axis 0 is just indexing (lesson 5). That asymmetry is worth knowing when you loop over a batch and modify a slice.
    

Prefer `np.stack` to `vstack`/`column_stack`: it behaves identically at every rank, whereas the shortcuts special-case 1-D input (lesson 24).

---

## Stack vs Concatenate

|Question|Concatenate|Stack|
|---|---|---|
|Axis|must exist|is created|
|Rank|unchanged|**+1**|
|Input shapes|match except the join axis|**identical**|
|Result size on that axis|sum of the inputs|count of the inputs|
|Typical use|append more data|build a batch|

```text
   [a, b]  --concatenate(axis=0)-->  a
                                     b        (4, 3)

   [a, b]  --stack(axis=0)-------->  [a]
                                     [b]      (2, 2, 3)
```

> **Mental shift:** ask yourself "do I have more *data* along an existing dimension, or a new *dimension* of grouping?" The answer is obvious the moment you ask, and it's the only decision this pair needs. More samples for a dataset you already have: concatenate. A collection of things that used to be separate: stack.
