# 14. Patch Extraction

## Mental Model

Lessons 12 and 13 both **looked through** a window and threw it away, keeping one number per position. Patch extraction keeps the window itself.

```text
sliding window            patch extraction
  window -> sum -> 14       window -> [[1,2],[5,6]]  KEEP IT
  window -> sum -> 18       window -> [[2,3],[6,7]]  KEEP IT
  ...                       ...
  a matrix of numbers       a LIST of little matrices
```

A window is a *view for computing*. A **patch is a value you store**, compare, count, hash, feed to a model, or paste back somewhere else.

That change of intent brings three questions the earlier lessons never had to answer:

- **Layout.** A list of `k×k` grids, or one flat `n × k²` table? The flat form has a name — **im2col** — and it is how every convolution library actually runs.
    
- **Anchoring.** Top-left (like a window) or **centred on a cell** (like a neighborhood)? Centred is what you want when every cell needs its own patch.
    
- **Padding.** Centred patches fall off the edge. Zero, clamp, reflect or wrap — and the choice visibly changes your results.
    

---

## Relationship to Cognitive Verb

```text
Extract
   ↓
Patch Extraction
```

Related verbs:

- Extract
    
- Collect samples
    
- Cut out
    
- Gather patches
    
- Harvest sub-images
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Take a patch|the k × k block|`[row[c:c+k] for row in m[r:r+k]]`|
|All patches|as a flat list|comprehension over both ranges|
|Flatten a patch|one row per patch|`[x for row in p for x in row]`|
|im2col|n × k² table|flatten every patch|
|Output shape|how many patches|`(rows + 2p - k)//s + 1`|
|Centred patch|around a cell|`range(r-R, r+R+1)` + padding|
|Padding|off-grid reads|zero / clamp / reflect / wrap|
|Hashable patch|for a set or Counter|`tuple(...)` — lists are unhashable|
|Count distinct|texture vocabulary|`collections.Counter`|
|Reassemble|patches → matrix|accumulate and divide by overlap count|

---

## Common Uses

- im2col for convolution (matrix-multiply form)
    
- CNN and vision-transformer input patches
    
- Texture analysis and synthesis
    
- PatchMatch, inpainting, super-resolution
    
- Wave Function Collapse (tile rules learned from patches)
    
- Template and feature matching
    
- Dataset augmentation (random crops)
    
- Denoising by patch averaging
    
- Local binary patterns
    

---

## Hidden Interview Problems

- Extract all k × k submatrices
    
- Count distinct submatrices of size k
    
- Most frequent k × k pattern
    
- Find all occurrences of a pattern
    
- Check if two matrices share a common block
    
- Reconstruct an image from overlapping patches
    
- Number of unique rows/blocks
    
- Hash a matrix for fast comparison
    

---

## Recognition Clues

If you hear...

- "extract all submatrices..."
    
- "collect the patches..."
    
- "how many distinct blocks..."
    
- "crop around each pixel..."
    
- "feed each region to..."
    
- "reconstruct from overlapping pieces..."
    

...think **Patch Extraction**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D in, list-of-2D out|
|Unit|A k × k patch, kept as data|
|Stride|Any — 1 for dense, k for disjoint|
|Anchoring|Top-left (window) or centred (per cell)|
|Patch count|`((rows+2p-k)//s + 1) * ((cols+2p-k)//s + 1)`|
|im2col shape|`n_patches × k²`|
|Time Complexity|O(n_patches × k²)|
|Space Complexity|O(n_patches × k²) — patches are *stored*|
|Common Domains|ML, vision, texture, compression|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from collections import Counter

m = [[1,  2,  3,  4],
     [5,  6,  7,  8],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

rows, cols = len(m), len(m[0])

# ============================================
# The one idiom to remember
#
# Same two slices as lessons 12 and 13. What changed is
# that the result is COLLECTED, not reduced — and the
# loops are flattened into one list, not a grid.

def patches(m, k, stride=1):
    rows, cols = len(m), len(m[0])
    return [[row[c:c+k] for row in m[r:r+k]]
            for r in range(0, rows - k + 1, stride)
            for c in range(0, cols - k + 1, stride)]

p = patches(m, 2)

len(p)                  # => 9
p[0]                    # => [[1, 2], [5, 6]]
p[4]                    # => [[6, 7], [10, 11]]

# ============================================
# The stride knob spans the two previous lessons

len(patches(m, 2, stride=1))    # => 9   dense, overlapping  (lesson 12)
len(patches(m, 2, stride=2))    # => 4   disjoint            (lesson 13)

patches(m, 2, stride=2)
# => [[[1, 2], [5, 6]],
#     [[3, 4], [7, 8]],
#     [[9, 10], [13, 14]],
#     [[11, 12], [15, 16]]]
#
# identical to the tiles of lesson 13, flattened.
# Patch extraction is the DATA form of both patterns.

# ============================================
# How many patches? The formula worth memorising
#
#   out = (in + 2*pad - k) // stride + 1
#
# It is the same formula for patches, pooling and
# convolution. Learn it once.

def out_shape(rows, cols, k, stride=1, pad=0):
    return ((rows + 2*pad - k)//stride + 1,
            (cols + 2*pad - k)//stride + 1)

out_shape(4, 4, 2, 1, 0)        # => (3, 3)    9 patches
out_shape(4, 4, 2, 2, 0)        # => (2, 2)    4 patches
out_shape(4, 4, 3, 1, 1)        # => (4, 4)    'same' — shape preserved

len(patches(m, 2)) == 3 * 3     # => True

# ============================================
# im2col — flatten every patch into a row
#
# This is THE representation. Once patches are rows, a
# convolution is a matrix multiply, a patch comparison
# is a row comparison, and a patch is hashable.

def im2col(m, k, stride=1):
    return [[x for row in p for x in row] for p in patches(m, k, stride)]

col = im2col(m, 2)

len(col), len(col[0])   # => (9, 4)     n_patches x k*k

col
# => [[1,  2,  5,  6 ],
#     [2,  3,  6,  7 ],
#     [3,  4,  7,  8 ],
#     [5,  6,  9,  10],
#     [6,  7,  10, 11],
#     [7,  8,  11, 12],
#     [9,  10, 13, 14],
#     [10, 11, 14, 15],
#     [11, 12, 15, 16]]
#
# every cell appears up to k*k times — im2col trades
# memory for the ability to use one matrix multiply

# ============================================
# Padding: four ways to answer "what is off the grid?"
#
# Needed the moment patches are CENTRED rather than
# anchored top-left.

MODES = {
    "zero":    None,                                    # handled below
    "clamp":   lambda i, n: min(max(i, 0), n - 1),      # repeat the edge
    "reflect": lambda i, n: abs(i) if i < 0 else (2*n - 2 - i if i >= n else i),
    "wrap":    lambda i, n: i % n,                      # torus
}

def at(m, r, c, mode="zero", fill=0):
    rows, cols = len(m), len(m[0])
    if mode == "zero":
        return m[r][c] if 0 <= r < rows and 0 <= c < cols else fill
    f = MODES[mode]
    return m[f(r, rows)][f(c, cols)]

def pad_matrix(m, p, mode="zero"):
    rows, cols = len(m), len(m[0])
    return [[at(m, r, c, mode) for c in range(-p, cols + p)]
            for r in range(-p, rows + p)]

pad_matrix(m, 1, "zero")
# =>
# [[0, 0,  0,  0,  0,  0],
#  [0, 1,  2,  3,  4,  0],
#  [0, 5,  6,  7,  8,  0],
#  [0, 9,  10, 11, 12, 0],
#  [0, 13, 14, 15, 16, 0],
#  [0, 0,  0,  0,  0,  0]]

pad_matrix(m, 1, "clamp")
# =>
# [[1,  1,  2,  3,  4,  4 ],
#  [1,  1,  2,  3,  4,  4 ],
#  [5,  5,  6,  7,  8,  8 ],
#  [9,  9,  10, 11, 12, 12],
#  [13, 13, 14, 15, 16, 16],
#  [13, 13, 14, 15, 16, 16]]

pad_matrix(m, 1, "reflect")
# =>
# [[6,  5,  6,  7,  8,  7 ],
#  [2,  1,  2,  3,  4,  3 ],
#  [6,  5,  6,  7,  8,  7 ],
#  [10, 9,  10, 11, 12, 11],
#  [14, 13, 14, 15, 16, 15],
#  [10, 9,  10, 11, 12, 11]]

pad_matrix(m, 1, "wrap")
# =>
# [[16, 13, 14, 15, 16, 13],
#  [4,  1,  2,  3,  4,  1 ],
#  [8,  5,  6,  7,  8,  5 ],
#  [12, 9,  10, 11, 12, 9 ],
#  [16, 13, 14, 15, 16, 13],
#  [4,  1,  2,  3,  4,  1 ]]
#
# zero    invents a dark border    -> visible edge artifacts
# clamp   repeats the edge         -> the usual safe default
# reflect mirrors inward           -> best for smooth images
# wrap    joins opposite edges     -> tiling textures, toruses

# ============================================
# Centred patches — one per CELL, not one per position
#
# This is the neighborhood anchoring from lessons 9-11,
# with the patch kept instead of reduced.

def centered_patch(m, r, c, R, mode="zero"):
    return [[at(m, i, j, mode) for j in range(c-R, c+R+1)]
            for i in range(r-R, r+R+1)]

centered_patch(m, 1, 1, 1)
# =>
# [[1,  2,  3],
#  [5,  6,  7],
#  [9,  10, 11]]

centered_patch(m, 0, 0, 1)                  # corner, zero-padded
# =>
# [[0, 0, 0],
#  [0, 1, 2],
#  [0, 5, 6]]

centered_patch(m, 0, 0, 1, "clamp")         # corner, edge-clamped
# =>
# [[1, 1, 2],
#  [1, 1, 2],
#  [5, 5, 6]]
#
# a centred patch of radius R is exactly the Chebyshev
# ball of lesson 11, plus the centre, kept as a grid.
# Padding is what lesson 11 avoided by filtering; here
# you cannot filter, because the patch must stay k x k.

# ============================================
# Patches must be TUPLES to be counted
#
# Lists are unhashable — no set, no Counter, no dict key.
# Flatten and tuple() is the standard move.

tex = [[1, 0, 1, 0],
       [0, 1, 0, 1],
       [1, 0, 1, 0],
       [0, 1, 0, 1]]

keys = [tuple(x for row in p for x in row) for p in patches(tex, 2)]

keys
# => [(1,0,0,1), (0,1,1,0), (1,0,0,1),
#     (0,1,1,0), (1,0,0,1), (0,1,1,0),
#     (1,0,0,1), (0,1,1,0), (1,0,0,1)]

len(set(keys))                  # => 2

Counter(keys).most_common()
# => [((1, 0, 0, 1), 5), ((0, 1, 1, 0), 4)]
#
# a perfect checkerboard has a two-patch vocabulary.
# This count IS a texture descriptor — and it is the
# input Wave Function Collapse learns its rules from.

# ============================================
# Index the patches once, answer many queries
#
# This is what the patch representation buys you.
# Lesson 12's find() rescans the matrix per query;
# a dict of patch -> positions is built once.

def flat(p):
    return tuple(x for row in p for x in row)

def coords(m, k, stride=1):
    return [(r, c) for r in range(0, len(m) - k + 1, stride)
                   for c in range(0, len(m[0]) - k + 1, stride)]

def index_patches(m, k):
    idx = {}
    for (r, c), p in zip(coords(m, k), patches(m, k)):
        idx.setdefault(flat(p), []).append((r, c))
    return idx

idx = index_patches(m, 2)

len(idx)                            # => 9   all distinct here
idx[flat([[6, 7], [10, 11]])]       # => [(1, 1)]
idx.get(flat([[0, 0], [0, 0]]), []) # => []

# on the checkerboard the index collapses to 2 keys,
# each holding several positions
index_patches(tex, 2)[(1, 0, 0, 1)]
# => [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)]

# ============================================
# Reassembly (fold / col2im)
#
# Overlapping patches write to the same cells, so
# accumulate the values AND the write counts, then divide.

def fold(ps, rows, cols, k, stride=1):
    acc = [[0]*cols for _ in range(rows)]
    cnt = [[0]*cols for _ in range(rows)]
    it = iter(ps)
    for r in range(0, rows - k + 1, stride):
        for c in range(0, cols - k + 1, stride):
            patch = next(it)
            for i in range(k):
                for j in range(k):
                    acc[r+i][c+j] += patch[i][j]
                    cnt[r+i][c+j] += 1
    return [[acc[r][c] // cnt[r][c] for c in range(cols)] for r in range(rows)]

fold(patches(m, 2), 4, 4, 2) == m       # => True

# the count grid shows the overlap — corners are written
# once, the interior four times
# [[1, 2, 2, 1],
#  [2, 4, 4, 2],
#  [2, 4, 4, 2],
#  [1, 2, 2, 1]]
#
# forgetting to divide by cnt is THE reconstruction bug:
# the interior comes out ~4x too bright

# ============================================
# Streaming — patches are big, don't materialise them

def ipatches(m, k, stride=1):
    rows, cols = len(m), len(m[0])
    for r in range(0, rows - k + 1, stride):
        for c in range(0, cols - k + 1, stride):
            yield (r, c), [row[c:c+k] for row in m[r:r+k]]

[pos for pos, _ in ipatches(m, 3)]      # => [(0,0), (0,1), (1,0), (1,1)]

# im2col on a 1000x1000 image with k=3 is 9 million
# numbers. Generate, consume, discard.

# ============================================
# Compare

# reduce the window to a number      -> lesson 12
sum(map(sum, window))

# reduce it, stride = k              -> lesson 13
pool(m, k, k, max)

# KEEP the window                    -> this lesson
patches(m, k, stride)

# reduce it with WEIGHTS             -> lesson 15
sum(w * x for w, x in zip(kernel_flat, patch_flat))
#
# and note: convolution == im2col followed by one
# matrix multiply. That is not an analogy; it is how
# it is implemented.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|all patches|`[[row[c:c+k] for row in m[r:r+k]] for r ... for c ...]`|
|how many|`(in + 2*pad - k)//stride + 1`, per axis|
|one row per patch|flatten → im2col, `n × k²`|
|patches disjoint|`stride=k` (that's lesson 13)|
|a patch per cell|centre it: `range(r-R, r+R+1)` + padding|
|off-grid values|`clamp` by default, `reflect` for images|
|to count patches|`tuple(...)` then `Counter`|
|the matrix back|accumulate, then **divide by the write count**|
|to not blow up memory|`yield` patches instead of listing them|

---

## Key Insight

**A patch is a window you decided to keep.** The extraction code is the same two slices as the last two lessons; everything new comes from storing the result:

```text
window  ->  reduce  ->  a number      (lessons 12, 13)
window  ->  keep    ->  a value       (this lesson)
```

Storing it forces three decisions that reducing never did:

1. **Layout.** Flattening patches into rows gives `im2col`, an `n × k²` table. Every cell is duplicated up to `k²` times — a real memory cost, paid because it turns convolution into a single matrix multiply and patch comparison into row comparison.
    
2. **Anchoring.** Top-left anchoring gives you one patch per *position* (`rows-k+1` of them). Centred anchoring gives you one patch per *cell* — and re-introduces the boundary problem from the neighborhood lessons.
    
3. **Padding.** You cannot filter out-of-bounds cells, because a patch must stay `k×k`. So you invent values: zero, clamp, reflect, or wrap. The choice is visible in the output — zero padding darkens edges, which is exactly why image code defaults to clamp or reflect.
    

And one Python specific that bites every time: **lists are unhashable.** No `set`, no `Counter`, no dict key until you flatten to a `tuple`. Counting distinct patches is a two-line job only after that conversion.

---

## The Three Window Patterns So Far

|Lesson|Stride|Result per position|Output|
|---|---|---|---|
|12 Sliding Window|1|one number|a smaller matrix|
|13 Block / Tile|`k`|one number|a much smaller matrix|
|14 Patch Extraction|any|**the window itself**|a list of matrices|

```text
              reduce  ──►  12 (stride 1) / 13 (stride k)
window  ──┤
              keep    ──►  14
              weight  ──►  15
```

> **Mental shift:** windows 12 and 13 answer a question and discard the evidence. Patch extraction *is* the evidence — which is why it is the interface to everything statistical: counting, matching, learning, reconstructing.
