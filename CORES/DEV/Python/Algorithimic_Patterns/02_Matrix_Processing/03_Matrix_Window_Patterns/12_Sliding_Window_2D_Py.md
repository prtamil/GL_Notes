# 12. Sliding Window (2D)

## Mental Model

A neighborhood is centred on a cell. A **window** is a fixed rectangle that **slides** — you stop at every position and reduce whatever is inside to an answer.

```text
  ┌───┐              ┌───┐
  │1 2│3 4    1 2 3 4   │3 4│
  │5 6│7 8 →  5 6│7 8│→ ... →  9 10│11 12│
   9 10 11 12    ...           13 14│15 16│
  position (0,0)  (0,1)          (2,2)
```

Three numbers define it, and they are the whole pattern:

- **size** `k` (or `h × w`) — how big the window is.
    
- **stride** — how far it jumps. Stride 1 here; stride `k` is the next lesson.
    
- **the reduction** — sum, max, count, a test.
    

A `k×k` window at stride 1 has exactly `(rows-k+1) × (cols-k+1)` positions, and **consecutive positions overlap by `k-1` columns**. That overlap is both the cost (you re-read the same cells) and the opportunity (you can reuse the previous answer instead of recomputing it).

The whole craft of this pattern is: **do not recompute the overlap.** Naively every window costs O(k²); with an integral image every window costs O(1).

---

## Relationship to Cognitive Verb

```text
Scan
  ↓
Sliding Window (2D)
```

Related verbs:

- Scan across
    
- Sweep a frame
    
- Slide and check
    
- Look through a viewport
    
- Search every placement
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Window positions|top-left corners|`range(rows-k+1)`, `range(cols-k+1)`|
|Take a window|the k×k view|`[row[c:c+k] for row in m[r:r+k]]`|
|Reduce a window|its total|`sum(map(sum, win))`|
|Non-square|h × w window|`[row[c:c+w] for row in m[r:r+h]]`|
|Stride|jump by s|`range(0, rows-k+1, s)`|
|Fast window sums|O(1) each|integral image (prefix sums)|
|Fast window max|O(1) amortized|`deque`, two 1D passes|
|Best window|argmax over positions|`max(positions, key=...)`|
|Test a window|"all ones?"|`window_sum == k*k`|
|Pair windows|compare placements|`itertools.pairwise` over positions|

---

## Common Uses

- Maximum-sum submatrix of fixed size
    
- Template matching in images
    
- Local contrast, local threshold (adaptive binarization)
    
- Moving average over a raster
    
- Detecting solid regions (all-ones squares)
    
- Object detection sweeps
    
- Terrain: finding the flattest buildable plot
    
- Minesweeper-style area scans
    
- Heatmap hotspots
    

---

## Hidden Interview Problems

- Max sum submatrix of size k × k
    
- Maximal square of all ones
    
- Count submatrices with all ones
    
- Number of submatrices that sum to target
    
- Find a given pattern inside a matrix
    
- Largest rectangle of a fixed aspect ratio
    
- Sliding window maximum, in 2D
    
- Smallest window containing all values
    

---

## Recognition Clues

If you hear...

- "every k × k submatrix..."
    
- "any placement of a k × k square..."
    
- "the best sub-square..."
    
- "slide a frame across..."
    
- "find this pattern anywhere in the grid..."
    
- "local average / local maximum..."
    

...think **Sliding Window (2D)**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Unit|A fixed k × k (or h × w) rectangle|
|Stride|1 — consecutive windows overlap|
|Position count|`(rows-k+1) * (cols-k+1)`|
|Overlap|`k-1` columns between neighbours|
|Naive cost|O(rows × cols × k²)|
|With integral image|O(rows × cols) total|
|Space Complexity|O(rows × cols) for the prefix table|
|Common Domains|Images, vision, terrain, pattern search|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

from collections import deque

m = [[1,  2,  3,  4],
     [5,  6,  7,  8],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

rows, cols = len(m), len(m[0])

# ============================================
# Where can the window sit?
#
# The last legal top-left corner is rows-k, so the
# range stops at rows-k+1. Off-by-one lives here.

def positions(rows, cols, k, stride=1):
    return [(r, c) for r in range(0, rows - k + 1, stride)
                   for c in range(0, cols - k + 1, stride)]

len(positions(4, 4, 2))         # => 9    (4-2+1)^2
positions(4, 4, 3)              # => [(0,0), (0,1), (1,0), (1,1)]

# a window bigger than the matrix gives NO positions,
# not an error — range(4-5+1) is empty
positions(4, 4, 5)              # => []

# ============================================
# The one idiom to remember
#
# Two slices. The outer picks rows, the inner picks
# columns. This is the whole pattern.

def window(m, r, c, k):
    return [row[c:c+k] for row in m[r:r+k]]

window(m, 1, 1, 2)
# =>
# [[6,  7],
#  [10, 11]]

window(m, 0, 0, 3)
# =>
# [[1,  2,  3],
#  [5,  6,  7],
#  [9,  10, 11]]

# ============================================
# Slicing is SAFE here, unlike in the neighborhood lessons
#
# r and c are non-negative by construction, so no
# max(0, ...) clamp is needed. Windows are anchored at
# the top-left, not centred — that's why.

# ============================================
# Reduce every window

def window_sums(m, k):
    rows, cols = len(m), len(m[0])
    return [[sum(map(sum, window(m, r, c, k))) for c in range(cols-k+1)]
            for r in range(rows-k+1)]

window_sums(m, 2)
# =>
# [[14, 18, 22],
#  [30, 34, 38],
#  [46, 50, 54]]

window_sums(m, 3)
# =>
# [[54, 63],
#  [90, 99]]
#
# note the result is SMALLER than the input — 3x3 for k=2,
# 2x2 for k=3. That shrinkage is the signature of stride 1.

# ============================================
# Best window

max(max(row) for row in window_sums(m, 2))          # => 54

max(positions(rows, cols, 2),
    key=lambda p: sum(map(sum, window(m, *p, 2))))  # => (2, 2)

# ============================================
# Non-square windows — h and w are independent

def window_hw(m, r, c, h, w):
    return [row[c:c+w] for row in m[r:r+h]]

window_hw(m, 0, 1, 3, 2)
# =>
# [[2,  3],
#  [6,  7],
#  [10, 11]]

# ============================================
# THE optimisation: the integral image
#
# S[r][c] = sum of everything above-and-left of (r, c).
# One extra row and column of zeros removes every
# boundary special case.

def integral(m):
    rows, cols = len(m), len(m[0])
    S = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            S[r+1][c+1] = m[r][c] + S[r][c+1] + S[r+1][c] - S[r][c]
    return S

S = integral(m)
S
# =>
# [[0, 0,  0,  0,  0 ],
#  [0, 1,  3,  6,  10],
#  [0, 6,  14, 24, 36],
#  [0, 15, 33, 54, 78],
#  [0, 28, 60, 96, 136]]

# ============================================
# Any rectangle's sum in FOUR lookups
#
#   whole - top - left + top-left-counted-twice

def rect_sum(S, r, c, h, w):
    return S[r+h][c+w] - S[r][c+w] - S[r+h][c] + S[r][c]

rect_sum(S, 1, 1, 2, 2)         # => 34    the [[6,7],[10,11]] window
rect_sum(S, 0, 0, 4, 4)         # => 136   the whole matrix

# every window sum, now O(1) each
[[rect_sum(S, r, c, 2, 2) for c in range(3)] for r in range(3)]
# =>
# [[14, 18, 22],
#  [30, 34, 38],
#  [46, 50, 54]]      identical to the naive version

# and the window size is now free — no rebuild needed
[[rect_sum(S, r, c, 2, 3) for c in range(2)] for r in range(3)]
# =>
# [[24, 30],
#  [48, 54],
#  [72, 78]]

# O(rows*cols) to build, O(1) per query, ANY size.
# This is lesson 27 arriving early because the sliding
# window is what makes it worth having.

# ============================================
# Testing a window instead of summing it
#
# "Is this k x k block all ones?" is a sum test —
# don't write a nested all().

b = [[1, 0, 1, 0],
     [1, 0, 1, 1],
     [1, 1, 1, 1],
     [1, 0, 0, 1]]

window_sums(b, 2)
# =>
# [[2, 2, 3],
#  [3, 3, 4],
#  [3, 2, 3]]

[(r, c) for r, row in enumerate(window_sums(b, 2))
        for c, s in enumerate(row) if s == 2*2]     # => [(1, 2)]

sum(s == 4 for row in window_sums(b, 2) for s in row)   # => 1

# ============================================
# Sliding window MAXIMUM — sum's harder cousin
#
# Max has no inverse, so integral images don't work.
# The trick: a 2D max window is two 1D max windows.
# Slide horizontally, then slide the result vertically.

def max1d(xs, k):
    out, dq = [], deque()
    for i, x in enumerate(xs):
        while dq and xs[dq[-1]] <= x:
            dq.pop()                    # x dominates them; drop
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()                # left the window
        if i >= k - 1:
            out.append(xs[dq[0]])
    return out

max1d([1, 3, 2, 5, 4], 2)       # => [3, 3, 5, 5]

def max2d(m, k):
    horiz = [max1d(row, k) for row in m]             # rows first
    vert = [max1d(list(col), k) for col in zip(*horiz)]   # then columns
    return [list(r) for r in zip(*vert)]

max2d(m, 2)
# =>
# [[6,  7,  8 ],
#  [10, 11, 12],
#  [14, 15, 16]]

max2d(m, 3)
# =>
# [[11, 12],
#  [15, 16]]
#
# O(rows*cols) total, independent of k. Same trick works
# for min — and this separability is exactly the idea
# lesson 15 reuses for separable kernels.

# ============================================
# Template matching — the window IS the query

def find(m, pattern):
    ph, pw = len(pattern), len(pattern[0])
    return [(r, c)
            for r in range(len(m) - ph + 1)
            for c in range(len(m[0]) - pw + 1)
            if window_hw(m, r, c, ph, pw) == pattern]

find(m, [[6, 7], [10, 11]])     # => [(1, 1)]
find(m, [[99]])                 # => []

# ============================================
# Compare

# every cell               -> traversal (lessons 1-8)
# cells around one cell    -> neighborhood (lessons 9-11)

# every k x k placement, overlapping   -> this lesson
positions(rows, cols, k, stride=1)

# ...stride k instead of 1 -> non-overlapping tiles (lesson 13)
positions(rows, cols, k, stride=k)

# ...keep the window instead of reducing it -> patches (lesson 14)
# ...reduce it with WEIGHTS -> convolution (lesson 15)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the legal positions|`range(rows-k+1)`, `range(cols-k+1)`|
|the window|`[row[c:c+k] for row in m[r:r+k]]`|
|how many positions|`(rows-k+1) * (cols-k+1)`|
|every window's sum, fast|integral image + 4 lookups|
|any rectangle's sum|`S[r+h][c+w] - S[r][c+w] - S[r+h][c] + S[r][c]`|
|"all ones?"|`window_sum == k*k`|
|every window's max|`deque`, rows pass then columns pass|
|the best placement|`max(positions, key=...)`|

---

## Key Insight

**A sliding window is a neighborhood that stopped being centred and started moving.** Anchor it top-left instead of on a cell, and slicing becomes safe — no clamping, no negative-index trap, just `m[r:r+k]` and `row[c:c+k]`.

The pattern is three parameters:

```text
size  x  stride  x  reduction
```

and the rest of this section is those parameters taking different values. Stride 1 (here) means **overlap**, and overlap is the thing to exploit:

- **Sum** has an inverse, so precompute an integral image once and every window — any size, any position — costs 4 lookups.
    
- **Max** has no inverse, so instead use **separability**: a 2D window max is a horizontal pass followed by a vertical pass, O(rows × cols) regardless of `k`.
    

Those two tricks — *prefix* and *separable* — are the only reasons anyone writes this pattern by hand instead of a double loop, and both come back in lesson 15.

---

## Sliding Window vs Neighborhood

|Pattern|Anchored|Overlap|Result size|
|---|---|---|---|
|**Neighborhood** (9-11)|on a cell, centred|yes|same as input|
|**Sliding Window**|top-left corner|yes|`(rows-k+1) × (cols-k+1)`|

```text
Neighborhood            Sliding Window
  centred on (r,c)        anchored at (r,c)
  needs padding           shrinks the output
  output: same shape      output: smaller
```

> **Mental shift:** a neighborhood asks *"what surrounds this cell?"* and gives you one answer per cell. A window asks *"what is the best placement?"* and gives you one answer per **position** — and there are fewer positions than cells, which is why the output shrinks.
