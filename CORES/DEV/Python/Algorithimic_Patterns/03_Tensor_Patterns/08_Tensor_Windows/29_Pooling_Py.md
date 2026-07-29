# 29. Pooling

## Mental Model

Lesson 28's windows **overlap**. Pooling uses windows that **don't**. The tensor gets partitioned into blocks and each block collapses to a single value.

```text
4x4, pooled 2x2:

  0  1 | 2  3           max ->   5   7
  4  5 | 6  7
  -----+-----                   13  15
  8  9 |10 11
 12 13 |14 15
```

That's part 2's lesson 13, tiling, with a reduction stuck on the end. And at rank 3 and up there's a much better way to say it than nested loops:

> **Reshape the axis into `(n_blocks, block_size)`, then reduce the block axes.**

```text
(H, W)  ->  (H//k, k, W//k, k)  --reduce axes 1 and 3-->  (H//k, W//k)
```

Every spatial axis splits into "which block" and "where inside the block", and pooling is just reducing the second of each pair. The whole operation is one `reshape` — free, per lesson 12 — plus one multi-axis reduction (lesson 22).

It extends to batches without changing: `(N, C, H, W)` becomes `(N, C, H//k, k, W//k, k)` and you reduce axes `(3, 5)`. Nothing here is specific to 2-D.

Two things to watch. The axis has to **divide evenly**, or reshape refuses. And `(1,3)` versus `(2,3)` is an easy slip that hands you a valid array holding the wrong statistic.

---

## Relationship to Cognitive Verb

```text
Downsample
     ↓
Pooling
```

Related verbs:

- Downsample
- Summarise blocks
- Coarsen
- Reduce resolution
- Aggregate tiles

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|The block reshape|split each axis|`a.reshape(H//k, k, W//k, k)`|
|Max pool|the reduction|`.max(axis=(1, 3))`|
|Average pool|same shape|`.mean(axis=(1, 3))`|
|Batched (NCHW)|two more axes|`reshape(N,C,H//k,k,W//k,k).max(axis=(3,5))`|
|Non-square window|`kh × kw`|`reshape(H//kh, kh, W//kw, kw)`|
|Overlapping|a real stride|`sliding_window_view` then reduce|
|Global pooling|collapse spatially|`a.mean(axis=(-2, -1))`|
|Uneven size|crop or pad|`a[:H//k*k]` or `np.pad`|
|Keep the shape|for upsampling back|`keepdims=True`, then `repeat`|

---

## Common Uses

- Max / average pooling layers in a CNN
- Downsampling an image or mask
- Coarsening a grid before a cheap computation
- Block statistics of a large array
- Reducing a heatmap's resolution
- Binning time-series data
- Mosaicking / pixelating

---

## Hidden Interview Problems

- Implement 2×2 max pooling without loops
- Downsample an image by averaging blocks
- Pool over a batch of multi-channel images
- Handle a size that is not divisible by the pool
- Implement overlapping pooling
- Explain the difference between pooling and striding

---

## Recognition Clues

If you hear...

- "max pool / average pool..."
- "downsample by 2..."
- "block average..."
- "bin the data..."
- "reduce the resolution..."

...think **Pooling**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Windows|**Non-overlapping** — a partition|
|Core trick|`reshape` each axis into `(n_blocks, k)`|
|Reduction|The block-size axes|
|Output shape|`H//k, W//k` per pooled axis|
|Reshape cost|**Free** — contiguous, order preserved|
|Divisibility|Required — crop or pad otherwise|
|Overlapping variant|`sliding_window_view` + slice|
|Global pooling|Reduce the spatial axes entirely|
|Common Domains|CNNs, image processing, binning|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember
#
#   split each axis into (n_blocks, k), reduce the k axes

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

img = np.arange(16).reshape(4, 4)
img
# => array([[ 0,  1,  2,  3],
#           [ 4,  5,  6,  7],
#           [ 8,  9, 10, 11],
#           [12, 13, 14, 15]])

blocks = img.reshape(2, 2, 2, 2)
blocks.shape                # => (2, 2, 2, 2)
#
#   (H//k, k, W//k, k)  =  (2, 2, 2, 2)
#    ↑     ↑  ↑     ↑
#    |     |  |     └── position within the block, horizontally
#    |     |  └──────── which block, horizontally
#    |     └─────────── position within the block, vertically
#    └───────────────── which block, vertically

blocks.max(axis=(1, 3))
# => array([[ 5,  7],
#           [13, 15]])

blocks.mean(axis=(1, 3))
# => array([[ 2.5,  4.5],
#           [10.5, 12.5]])

blocks.sum(axis=(1, 3))
# => array([[10, 18],
#           [42, 50]])
#
# axes 1 and 3 are the two "inside the block" axes. Reduce
# them and only the block indices survive.

# ============================================
# As a function

def pool(a, k, f=np.max):
    H, W = a.shape
    return f(a.reshape(H//k, k, W//k, k), axis=(1, 3))

pool(img, 2)                # => [[5, 7], [13, 15]]
pool(img, 2, np.mean)       # => [[2.5, 4.5], [10.5, 12.5]]
pool(img, 4)                # => [[15]]        one block, the whole image
#
# any reduction works — max, mean, sum, min, median.
# The reduction is a parameter, exactly as in part 2's
# lesson 13.

# ============================================
# WATCH THE AXES
#
# (1, 3) is right. (2, 3) is a different, valid answer.

blocks.max(axis=(1, 3))     # => [[ 5,  7], [13, 15]]     correct
blocks.max(axis=(2, 3))     # => [[ 3,  7], [11, 15]]     NOT pooling
#
# axes 2 and 3 are "which block horizontally" and
# "position inside horizontally" — reducing both
# collapses the entire width instead of pooling it.
# Nothing raises. Count the axes from the reshape.

# ============================================
# THE RESHAPE IS FREE

np.shares_memory(img, img.reshape(2, 2, 2, 2))      # => True
#
# it is a plain reshape on contiguous data (lesson 12),
# so the partition costs nothing. Only the reduction
# does work — and it reads every element exactly once.
#
# compare with lesson 28's overlapping windows, which
# read every element k^2 times.

# ============================================
# DIVISIBILITY IS REQUIRED

img5 = np.arange(25).reshape(5, 5)

try:
    pool(img5, 2)
except ValueError as e:
    print(str(e)[:55])
# cannot reshape array of size 25 into shape (2,2,2,2)
#
# 5 // 2 == 2, so the reshape asks for 16 elements out
# of 25. Two standard fixes:

# 1. CROP — discard the remainder
pool(img5[:4, :4], 2)
# => array([[ 6,  8],
#           [16, 18]])

# 2. PAD — extend to a multiple
padded = np.pad(img5, ((0, 1), (0, 1)), mode='edge')
padded.shape                # => (6, 6)
pool(padded, 2)
# => array([[ 6,  8,  9],
#           [16, 18, 19],
#           [21, 23, 24]])
#
# cropping loses the edge; padding invents it. Frameworks
# call these `ceil_mode=False` and `ceil_mode=True`.
# Neither is more correct — decide deliberately.

# a general crop:
def pool_crop(a, k, f=np.max):
    H, W = a.shape
    a = a[:H//k*k, :W//k*k]                 # trim to a multiple
    return f(a.reshape(H//k, k, W//k, k), axis=(1, 3))

pool_crop(img5, 2)          # => [[6, 8], [16, 18]]

# ============================================
# BATCHED: the pattern is rank-agnostic

batch = np.arange(2*3*4*4).reshape(2, 3, 4, 4)      # N, C, H, W

def pool_nchw(a, k, f=np.max):
    N, C, H, W = a.shape
    return f(a.reshape(N, C, H//k, k, W//k, k), axis=(3, 5))

pool_nchw(batch, 2).shape   # => (2, 3, 2, 2)
pool_nchw(batch, 2)[0, 0]
# => array([[ 5,  7],
#           [13, 15]])
#
# the batch and channel axes are untouched; only H and W
# split. Axes (3, 5) instead of (1, 3) — two more leading
# axes shifted everything by two.
#
# this is one of the few places where counting axes by
# hand is unavoidable. Write the reshape shape out and
# read the positions off it.

# ============================================
# OVERLAPPING POOLING — use lesson 28's windows

swv(img, (2, 2)).max(axis=(2, 3))
# => array([[ 5,  6,  7],
#           [ 9, 10, 11],
#           [13, 14, 15]])
swv(img, (2, 2)).max(axis=(2, 3)).shape             # => (3, 3)
#
# every position, stride 1 — 3x3 outputs from a 4x4.

# and a stride-2 slice of that IS the non-overlapping version:
np.array_equal(swv(img, (2, 2))[::2, ::2].max(axis=(2, 3)), pool(img, 2))
# => True
#
#   reshape trick   : reads each element once
#   swv + [::2,::2] : reads each element once too (the
#                     view skips), but goes through a
#                     bigger intermediate shape
#
# use the reshape when stride == window (the common case),
# and sliding_window_view when they differ.

# ============================================
# GLOBAL POOLING — collapse the spatial axes entirely

batch.mean(axis=(2, 3)).shape           # => (2, 3)      one value per channel
batch.max(axis=(2, 3)).shape            # => (2, 3)
#
# this is just lesson 22's multi-axis reduction; no
# reshape needed, because there is only one block.
# `GlobalAveragePooling2D` is one line.

batch.mean(axis=(2, 3), keepdims=True).shape        # => (2, 3, 1, 1)
#
# keepdims when the result is going to be broadcast back
# (lesson 21) — as in squeeze-and-excitation blocks.

# ============================================
# Non-square windows

r = np.arange(24).reshape(4, 6)
def pool_hw(a, kh, kw, f=np.max):
    H, W = a.shape
    return f(a.reshape(H//kh, kh, W//kw, kw), axis=(1, 3))

pool_hw(r, 2, 3).shape      # => (2, 2)
pool_hw(r, 2, 3)
# => array([[ 8, 11],
#           [20, 23]])
#
# the two block sizes are independent — nothing in the
# pattern assumed they were equal.

# ============================================
# Unpooling — the inverse, approximately

small = pool(img, 2)
small
# => array([[ 5,  7],
#           [13, 15]])

np.repeat(np.repeat(small, 2, axis=0), 2, axis=1)
# => array([[ 5,  5,  7,  7],
#           [ 5,  5,  7,  7],
#           [13, 13, 15, 15],
#           [13, 13, 15, 15]])
#
# lesson 27's `repeat` — nearest-neighbour upsampling.
# Pooling is lossy, so this is not a true inverse; it is
# what a decoder does.

# ============================================
# Compare

img.reshape(2,2,2,2).max(axis=(1,3))    # non-overlapping   -> (2,2)
swv(img,(2,2)).max(axis=(2,3))          # overlapping       -> (3,3)
swv(img,(2,2))[::2,::2].max(axis=(2,3)) # == the first one
batch.mean(axis=(2,3))                  # global            -> (N, C)
np.repeat(np.repeat(small,2,0),2,1)     # unpool            -> (4,4)

[img.reshape(2,2,2,2).max(axis=(1,3)).shape,
 swv(img,(2,2)).max(axis=(2,3)).shape,
 batch.mean(axis=(2,3)).shape]
# => [(2, 2), (3, 3), (2, 3)]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the pooling trick|`reshape(H//k, k, W//k, k)`, reduce `(1, 3)`|
|batched (NCHW)|`reshape(N, C, H//k, k, W//k, k)`, reduce `(3, 5)`|
|the reduction|any — `max`, `mean`, `sum`|
|non-divisible sizes|crop `a[:H//k*k]` or `np.pad`|
|overlapping|`sliding_window_view`, then reduce|
|global pooling|`a.mean(axis=(-2, -1))` — no reshape|
|to upsample back|`np.repeat` on both axes|
|**not** to slip|write the reshape out and read the axis numbers off it|

---

## Key Insight

**Pooling is a reshape plus a reduction.** Split each spatial axis into "which block" and "where inside the block", then reduce the second of each pair:

```text
(H, W)  --reshape-->  (H//k, k, W//k, k)  --reduce (1,3)-->  (H//k, W//k)
```

The reshape is **free** — the data is contiguous and the flat order is preserved (lesson 12) — so the only real work is the reduction, which reads each element exactly once. Contrast that with lesson 28's overlapping windows, which read each element `k²` times.

Three practical points:

1. **The axis numbers are the whole difficulty.** `(1, 3)` pools; `(2, 3)` collapses the width. Both run. When the leading axes change — `(N, C, H, W)` needs `(3, 5)` — write the reshape shape out and read the positions off it rather than guessing.
    
2. **Divisibility is not optional.** `reshape` refuses a size that does not split evenly, which is a feature: you must decide between cropping (lose the edge) and padding (invent it). Frameworks expose the same choice as `ceil_mode`.
    
3. **Choose the tool by stride.** When stride equals the window — the usual case — the reshape trick is the cleanest. When they differ, `sliding_window_view` plus a slice handles it, and the non-overlapping case falls out as `[::k, ::k]`.
    

And global pooling needs none of this: it is lesson 22's `a.mean(axis=(-2, -1))`, because there is only one block.

---

## Pooling vs Sliding Windows

|Aspect|Pooling (29)|Sliding windows (28)|
|---|---|---|
|Windows|non-overlapping|overlapping|
|Mechanism|`reshape`|`sliding_window_view`|
|Element reads|once|`k²` times|
|Output size|`n // k`|`n - k + 1`|
|Constraint|must divide evenly|none|

```text
   pool:   [0 1][2 3][4 5]        a partition
   swv:    [0 1]
             [1 2]
               [2 3] ...          every position
```

> **Mental shift:** part 2's lesson 13 tiled a matrix and reduced each tile, and the tiling was the interesting bit. Here the tiling *is a reshape*: free, and one line at any rank. All that's left to think about is which axes you reduce, which makes pooling a special case of lesson 22 rather than a technique in its own right.
