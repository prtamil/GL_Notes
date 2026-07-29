# 28. Patch Extraction

## Mental Model

Part 2's lesson 14 extracted patches by copying them. Every `k×k` window became a new little array, and `im2col` duplicated each cell up to `k²` times. That's a real memory cost, paid for convenience.

NumPy doesn't have to pay it.

```python
from numpy.lib.stride_tricks import sliding_window_view as swv

swv(x, 3)       # every length-3 window of x — as a VIEW
```

A sliding window is **regularly spaced**, so strides can describe it. And lesson 4 established that anything strides can describe is free.

```text
x        = [0 1 2 3 4 5 6 7]        strides (8,)

swv(x,3) = [[0 1 2],                strides (8, 8)
            [1 2 3],                          ↑  ↑
            [2 3 4],            step to the next window
            ...]                       step within the window
```

Both strides are 8 bytes. Moving one window forward and moving one element forward are *the same step*, which is exactly what "overlapping by `k-1`" means once you write it as arithmetic.

What you get back is a tensor of shape `(n_windows..., window_shape...)`, and it costs **nothing**:

```text
m           (4, 5)
swv(m,(2,2))  ->  (3, 4, 2, 2)      12 windows, each 2x2
```

The catch, and it is a real one: the *logical* size can be enormous. A million-element array windowed at 100 presents as 800 MB while occupying 8 MB. Read from it freely; the moment you `reshape` or `copy`, you materialise the whole thing.

---

## Relationship to Cognitive Verb

```text
Frame
  ↓
Patch Extraction
```

Related verbs:

- Frame
- Slide a window
- Take every neighbourhood
- Unfold
- Enumerate positions

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|All windows|the whole thing|`sliding_window_view(t, size)`|
|One axis only|1-D windows|`sliding_window_view(t, k, axis=0)`|
|Chosen axes|spatial only|`sliding_window_view(t, (kh,kw), axis=(-2,-1))`|
|Stride / step|skip positions|slice the result: `[::s]`|
|Window count|per axis|`n - k + 1`|
|im2col|flatten each window|`.reshape(-1, k*k)` — **copies**|
|Reduce per window|no copy|`.mean(axis=(-2,-1))`|
|Writeable copy|when you must write|`.copy()`|
|Check it's free|confirm|`np.shares_memory(t, w)`|

---

## Common Uses

- Sliding-window statistics (moving average, rolling max)
- Convolution and correlation
- Pooling with overlap
- Template matching
- Local feature extraction
- n-gram windows over a sequence
- Patch-based image models (ViT, PatchMatch)

---

## Hidden Interview Problems

- Extract all k×k submatrices
- Compute a rolling mean without a loop
- Find every window matching a pattern
- Build an im2col matrix
- Compute the maximum in every sliding window
- Explain how a windowed view can be larger than its source

---

## Recognition Clues

If you hear...

- "every window / patch / neighbourhood..."
- "rolling / moving / sliding..."
- "all k×k submatrices..."
- "n-grams..."
- "local statistics..."

...think **Patch Extraction**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Result shape|`(n_windows..., window_shape...)`|
|Window count|`n - k + 1` per windowed axis|
|Window axes|Appended at the **end**|
|Returns|A **view** — stride 0 is not needed; the strides repeat|
|Writeable|**No** — read-only by default|
|Logical size|Up to `k^d ×` the source|
|Actual memory|Unchanged|
|Materialising|`reshape` / `copy` allocates the full logical size|
|Time Complexity|O(1) to create|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

x = np.arange(8)

swv(x, 3)
# => array([[0, 1, 2],
#           [1, 2, 3],
#           [2, 3, 4],
#           [3, 4, 5],
#           [4, 5, 6],
#           [5, 6, 7]])
swv(x, 3).shape             # => (6, 3)      8 - 3 + 1 = 6 windows

# ============================================
# AND IT IS FREE

np.shares_memory(x, swv(x, 3))          # => True

x.strides                   # => (8,)
swv(x, 3).strides           # => (8, 8)
#
# the SAME stride, twice. Advancing one window and
# advancing one element inside a window are the same
# 8-byte step — which is precisely what "windows overlap
# by k-1" means, written as memory arithmetic.
#
# part 2 lesson 14 built these by copying. Lesson 4's
# stride machinery makes the copy unnecessary.

swv(x, 3).flags['WRITEABLE']            # => False
#
# read-only, for the same reason `broadcast_to` is
# (lesson 17): a single element appears in several
# windows, so writing to one would change the others.
# `.copy()` if you need to write.

# ============================================
# THE MEMORY ILLUSION

swv(x, 3).nbytes            # => 144     what it presents as
x.nbytes                    # => 64      what it costs

big = np.arange(1_000_000)
w = swv(big, 100)
w.shape                     # => (999901, 100)
w.nbytes                    # => 799920800     ~800 MB, logically
big.nbytes                  # => 8000000       8 MB, actually
w.nbytes // big.nbytes      # => 99
#
# a hundredfold illusion. Reducing over it is fine —
# `w.mean(axis=-1)` streams through the same 8 MB. But
# `w.copy()` or `w.reshape(...)` allocates all 800 MB.
#
# THAT is the rule for this whole section: read from the
# view, never materialise it.

# ============================================
# 2-D: windows over both axes

m = np.arange(20).reshape(4, 5)
m
# => array([[ 0,  1,  2,  3,  4],
#           [ 5,  6,  7,  8,  9],
#           [10, 11, 12, 13, 14],
#           [15, 16, 17, 18, 19]])

swv(m, (2, 2)).shape        # => (3, 4, 2, 2)
#
#   (4-2+1, 5-2+1, 2, 2)  =  12 windows, each 2x2
#
# the WINDOW axes are appended at the END. The leading
# axes index the position; the trailing axes are the
# window itself.

swv(m, (2, 2))[0, 0]
# => array([[0, 1],
#           [5, 6]])        the top-left window

swv(m, (2, 2))[1, 2]
# => array([[ 7,  8],
#           [12, 13]])      the window at row 1, col 2

np.shares_memory(m, swv(m, (2, 2)))     # => True

m.strides                   # => (40, 8)
swv(m, (2, 2)).strides      # => (40, 8, 40, 8)
#
# the source strides, REPEATED. Position strides then
# window strides — the entire implementation.

# ============================================
# Windowing only some axes

swv(m, 3, axis=0).shape     # => (2, 5, 3)   windows down the rows
swv(m, 3, axis=1).shape     # => (4, 3, 3)   windows across the columns

swv(m, 3, axis=0)[0]
# => array([[ 0,  5, 10],
#           [ 1,  6, 11],
#           [ 2,  7, 12],
#           [ 3,  8, 13],
#           [ 4,  9, 14]])
#    each row is a column of m, windowed vertically

# on a batched tensor, window only the spatial axes:
t = np.arange(24).reshape(2, 3, 4)
swv(t, 2, axis=-1).shape            # => (2, 3, 3, 2)
swv(t, (2, 2), axis=(1, 2)).shape   # => (2, 2, 3, 2, 2)
#
# the batch axis is left alone — the standard shape for
# batched convolution (lesson 30).

# ============================================
# STRIDE (step) — just slice the result

swv(x, 3)[::2]
# => array([[0, 1, 2],
#           [2, 3, 4],
#           [4, 5, 6]])
swv(x, 3)[::2].shape                # => (3, 3)

swv(m, (2, 2))[::2, ::2].shape      # => (2, 2, 2, 2)
np.shares_memory(m, swv(m, (2, 2))[::2, ::2])       # => True
#
# there is no `step=` parameter, and none is needed:
# slicing the position axes IS the stride, and it stays
# a view (lesson 8).

# ============================================
# im2col — the version that DOES copy

col = swv(m, (2, 2)).reshape(-1, 4)
col.shape                   # => (12, 4)      12 windows, flattened
np.shares_memory(m, col)    # => False        MATERIALISED

col[:3]
# => array([[0, 1, 5, 6],
#           [1, 2, 6, 7],
#           [2, 3, 7, 8]])
#
# reshape cannot describe this layout with strides
# (the windows overlap), so it allocates. This is part 2
# lesson 14's im2col exactly — and now you can see the
# cost was never mandatory, only the reshape was.
#
# prefer einsum over the VIEW (lesson 30) to keep it free.

# ============================================
# Reducing per window — the common case, no copy

swv(x, 3).mean(axis=-1)     # => [1., 2., 3., 4., 5., 6.]   rolling mean
swv(x, 3).max(axis=-1)      # => [2, 3, 4, 5, 6, 7]         rolling max
swv(x, 3).sum(axis=-1)      # => [ 3,  6,  9, 12, 15, 18]

swv(m, (2, 2)).sum(axis=(-2, -1))
# => array([[12, 16, 20, 24],
#           [32, 36, 40, 44],
#           [52, 56, 60, 64]])
#
# part 2's lesson 12 computed these with an integral
# image because the naive version was O(k^2) per window.
# Here the O(k^2) work is real but the MEMORY is free —
# and for small k that is the better trade.

# ============================================
# The copying version, for comparison

def patches_copy(m, k):
    R, C = m.shape
    return np.array([[m[r:r+k, c:c+k] for c in range(C-k+1)]
                     for r in range(R-k+1)])

np.array_equal(patches_copy(m, 2), swv(m, (2, 2)))  # => True
np.shares_memory(m, patches_copy(m, 2))             # => False
#
# identical values. One allocates 12 arrays and a
# Python loop; the other adjusts a strides tuple.

# ============================================
# Practical: template matching

img = np.arange(20).reshape(4, 5)
tmpl = np.array([[7, 8],
                 [12, 13]])

hits = (swv(img, (2, 2)) == tmpl).all(axis=(-2, -1))
np.argwhere(hits).tolist()          # => [[1, 2]]
#
# compare every window against the template in one
# expression — part 2 lesson 12's `find`, vectorised.

# ============================================
# Practical: n-grams over a sequence

seq = np.array(list("abcde"))
swv(seq, 2)
# => array([['a', 'b'],
#           ['b', 'c'],
#           ['c', 'd'],
#           ['d', 'e']], dtype='<U1')
#
# part 1's `pairwise`, at any window size and any rank.

# ============================================
# Compare

swv(t, k)                       # every window        -> VIEW
swv(t, k)[::s]                  # every s-th window   -> VIEW
swv(t, k).reshape(-1, k)        # im2col              -> COPY
swv(t, k).mean(axis=-1)         # reduce per window   -> new small array
t.reshape(n//k, k, ...)         # NON-overlapping     -> lesson 29

[np.shares_memory(m, y) for y in
 (swv(m, (2,2)), swv(m, (2,2))[::2], swv(m, (2,2)).reshape(-1, 4))]
# => [True, True, False]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|every window|`sliding_window_view(t, size)`|
|one axis|`..., axis=k`|
|spatial axes only|`..., axis=(-2, -1)`|
|a stride|slice the position axes: `[::s]`|
|the window count|`n - k + 1`|
|a per-window statistic|reduce the **trailing** axes|
|to know it's free|`np.shares_memory(t, w)`|
|**not** to blow up memory|never `reshape` or `copy` the view|
|to write to it|`.copy()` — it is read-only|

---

## Key Insight

**A sliding window is regularly spaced, so it is describable by strides — and therefore free.**

```text
x.strides        (8,)
swv(x,3).strides (8, 8)
```

The same step serves both "next window" and "next element within the window", which is what overlap *is*. Part 2 built patches by copying because Python lists have no other option; NumPy adjusts a tuple.

Three things follow:

1. **The view is read-only.** One element belongs to several windows, so writing through it would have non-local effects — the same reasoning that makes `broadcast_to` read-only (lesson 17).
    
2. **Logical size ≠ real size.** A million-element array windowed at 100 reports 800 MB and occupies 8 MB — a 99× illusion. Reductions over the view stream through the original memory; `reshape` and `copy` materialise the whole thing. **Read from it, never materialise it.**
    
3. **im2col was optional.** Part 2 framed the `n × k²` table as the price of vectorised convolution. It is only the price of *reshaping*; keeping the view and contracting with `einsum` (lesson 30) costs nothing extra.
    

There is no `step=` parameter because none is needed — slicing the position axes gives you strided windows and stays a view.

---

## The Windows Section

|Lesson|Windows|Overlap|Tool|
|---|---|---|---|
|**28 Patch Extraction**|every position|yes|`sliding_window_view`|
|29 Pooling|non-overlapping|no|`reshape` into blocks|
|30 Convolution|every position, **weighted**|yes|windows + `einsum`|

```text
   part 2, lesson 12   sliding window   ->  copied
   part 3, lesson 28   sliding window   ->  a view

   the operation is identical; only the cost changed
```

> **Mental shift:** part 2's window section was built around *dodging* the cost of windows — integral images, separable passes, all of it to avoid the O(k²) copy. At rank 3 with strides, the extraction is free and the only cost left is the arithmetic you actually wanted. That reframes the whole family: stop optimising the windowing and put the effort into the reduction.
