# 27. Prefix Sum (Integral Image)

## Mental Model

Every pattern so far answered a question by **reading the cells it needed**. This one answers by reading four numbers, however big the question is.

The trick is to precompute, once, the sum of every **top-left rectangle**:

```text
S[r][c]  =  sum of everything above and to the left of (r, c)
```

Then any rectangle's sum is inclusion–exclusion on four corners:

```text
   ┌────────┬──────┐
   │   A    │  B   │        wanted = D - B - C + A
   ├────────┼──────┤
   │   C    │ want │        (A is subtracted twice, so add it back)
   └────────┴──────┘
                D = the whole top-left block ending at the far corner
```

Two properties follow from that, and between them they're the entire reason this pattern exists:

- **Build once, query forever.** O(rows × cols) to build, then **O(1) per query**, for a rectangle of *any* size at *any* position.
    
- **It only works for operations you can invert.** Sum can be inverted with subtraction. So can count and XOR. **Max and min can't**, which is why lesson 12 needed a deque for sliding-window maxima but could use this for sums.
    

Computer vision calls the same table an **integral image**, and it's what made real-time face detection possible back in 2001. Haar features are just sums of rectangles, and this drops each one to four array lookups.

---

## Relationship to Cognitive Verb

```text
Accumulate
    ↓
Prefix Sum
```

Related verbs:

- Accumulate
- Running total
- Precompute
- Summarise cumulatively
- Scan

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|1D prefix|running totals|`itertools.accumulate(xs, initial=0)`|
|2D build|the table|`S[r+1][c+1] = m[r][c] + S[r][c+1] + S[r+1][c] - S[r][c]`|
|Padding|no edge cases|one extra row and column of zeros|
|Rectangle sum|4 lookups|`S[r+h][c+w] - S[r][c+w] - S[r+h][c] + S[r][c]`|
|Corner form|inclusive bounds|`S[r2+1][c2+1] - S[r1][c2+1] - S[r2+1][c1] + S[r1][c1]`|
|Counting|binary matrix|the same table; the sum *is* the count|
|Mean|average of a region|rectangle sum ÷ cell count|
|Row-only prefix|partial|`[accumulate(row, initial=0) for row in m]`|
|XOR version|works too|swap `+`/`-` for `^`|
|Range **update**|the mirror image|difference array, then prefix-sum it|

---

## Common Uses

- 2D range-sum queries on static data
- Integral images (Viola–Jones face detection, Haar features)
- Box blur at any radius in constant time per pixel
- Maximum-sum submatrix
- Counting points or events inside a rectangle
- Adaptive thresholding in image processing
- Heatmap and density queries
- Local mean and variance in O(1)
- Range-update problems, via the difference array

---

## Hidden Interview Problems

- Range Sum Query 2D — Immutable (LeetCode 304)
- Maximum Sum Submatrix of size k × k
- Max Sum of Rectangle No Larger Than K (LeetCode 363)
- Count Submatrices With All Ones
- Number of Submatrices That Sum to Target (LeetCode 1074)
- Matrix Block Sum (LeetCode 1314)
- Increment Submatrices by One (LeetCode 2536)
- Count Square Submatrices with All Ones

---

## Recognition Clues

If you hear...

- "sum of a submatrix..."
- "many queries on the same grid..."
- "the grid does not change..."
- "count the ones in this rectangle..."
- "average over a k × k region, for every cell..."
- "add v to every cell in this rectangle, many times..."

...think **Prefix Sum**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Precomputed|Sum of every top-left rectangle|
|Table size|`(rows+1) × (cols+1)` — the extra row/col is padding|
|Build|O(rows × cols)|
|Query|**O(1)** — four lookups, any size, any position|
|Requirement|The operation needs an **inverse** (sum ✓, max ✗)|
|Data|**Static** — one update invalidates the table|
|Space Complexity|O(rows × cols)|
|Common Domains|Vision, image processing, competitive programming|

---

## Python Recipe Book

```python
# ============================================
# Start in 1D — the 2D case is this idea, twice

from itertools import accumulate

xs = [3, 1, 4, 1, 5, 9, 2, 6]

def prefix1d(xs):
    p = [0]                             # the leading 0 is the whole trick
    for x in xs:
        p.append(p[-1] + x)
    return p

prefix1d(xs)                # => [0, 3, 4, 8, 9, 14, 23, 25, 31]

# the standard library does it directly:
list(accumulate(xs, initial=0))         # => same list

# and any range is one subtraction:
p = prefix1d(xs)
p[5] - p[2]                 # => 10
sum(xs[2:5])                # => 10     the slow way

# the leading 0 means p[i] == "sum of the first i items",
# so p[j] - p[i] is xs[i:j] with NO special case for i == 0.

# ============================================
# 2D — the same idea with inclusion-exclusion

m = [[1,  2,  3,  4 ],
     [5,  6,  7,  8 ],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

def integral(m):
    rows, cols = len(m), len(m[0])
    S = [[0] * (cols + 1) for _ in range(rows + 1)]     # padded with zeros
    for r in range(rows):
        for c in range(cols):
            S[r+1][c+1] = (m[r][c]
                           + S[r][c+1]                  # the block above
                           + S[r+1][c]                  # the block to the left
                           - S[r][c])                   # counted twice — remove
    return S

S = integral(m)
S
# =>
# [[0, 0,  0,  0,  0 ],
#  [0, 1,  3,  6,  10],
#  [0, 6,  14, 24, 36],
#  [0, 15, 33, 54, 78],
#  [0, 28, 60, 96, 136]]
#
# S[r][c] is the sum of the r x c block at the top-left.
# S[4][4] == 136 == sum(1..16). The row and column of
# zeros mean no `if r == 0` anywhere.

# ============================================
# The one idiom to remember
#
#   D - B - C + A
#
# Four lookups. The rectangle's size is irrelevant.

def rect(S, r, c, h, w):                # top-left + height/width
    return S[r+h][c+w] - S[r][c+w] - S[r+h][c] + S[r][c]

rect(S, 1, 1, 2, 2)         # => 34     the [[6,7],[10,11]] block
rect(S, 0, 0, 4, 4)         # => 136    everything
rect(S, 0, 0, 1, 1)         # => 1      a single cell
rect(S, 3, 3, 1, 1)         # => 16
rect(S, 0, 1, 3, 2)         # => 39     a 3x2 block

# the other common spelling, with INCLUSIVE corners:
def rect_corners(S, r1, c1, r2, c2):
    return S[r2+1][c2+1] - S[r1][c2+1] - S[r2+1][c1] + S[r1][c1]

rect_corners(S, 1, 1, 2, 2) # => 34     same block, +1s moved inside
#
# pick ONE convention and stay with it. Mixing the
# inclusive and exclusive forms is the bug in this
# pattern, and it produces plausible wrong numbers.

# ============================================
# Verified against brute force

def brute(m, r, c, h, w):
    return sum(m[i][j] for i in range(r, r+h) for j in range(c, c+w))

all(rect(S, r, c, h, w) == brute(m, r, c, h, w)
    for r in range(4) for c in range(4)
    for h in range(1, 4-r+1) for w in range(1, 4-c+1))
# => True    (all 100 rectangles of this 4x4)

# ============================================
# Building it with accumulate
#
# A row-prefix, then add the row above. Same table.

def integral_acc(m):
    S = [[0] * (len(m[0]) + 1)]
    for row in m:
        prev = S[-1]
        cur = list(accumulate(row, initial=0))
        S.append([a + b for a, b in zip(cur, prev)])
    return S

integral_acc(m) == S                    # => True

# row prefixes alone are sometimes all you need:
[list(accumulate(row, initial=0)) for row in m]
# =>
# [[0, 1,  3,  6,  10],
#  [0, 5,  11, 18, 26],
#  [0, 9,  19, 30, 42],
#  [0, 13, 27, 42, 58]]
#
# O(1) for any single-row range, O(rows) for a rectangle.
# Cheaper to build, and enough for the Kadane algorithm
# further down.

# ============================================
# Counting — an integral image over a binary matrix
#
# With 0/1 data the "sum" IS the count of ones. This is
# the original computer-vision use.

b = [[1, 0, 1, 1],
     [0, 1, 1, 1],
     [1, 1, 1, 1],
     [0, 0, 1, 1]]

SB = integral(b)

rect(SB, 0, 0, 4, 4)        # => 12     ones in total
rect(SB, 0, 0, 2, 2)        # => 2      ones in the top-left 2x2
rect(SB, 1, 1, 2, 2)        # => 4      ones in a 2x2 at (1,1)

# "is this k x k block ALL ones?" becomes arithmetic:
[(r, c) for r in range(3) for c in range(3) if rect(SB, r, c, 2, 2) == 4]
# => [(0, 2), (1, 1), (1, 2), (2, 2)]

[(r, c) for r in range(2) for c in range(2) if rect(SB, r, c, 3, 3) == 9]
# => []      no solid 3x3 exists

# density, for free:
rect(SB, 1, 1, 2, 2) / 4    # => 1.0

# ============================================
# O(1) box blur — ANY radius, same cost
#
# Lesson 15's blur cost O(k^2) per pixel. With an
# integral image the radius is free.

def box_mean(m, S, r, c, rad):
    rows, cols = len(m), len(m[0])
    r1, c1 = max(0, r - rad), max(0, c - rad)
    r2, c2 = min(rows - 1, r + rad), min(cols - 1, c + rad)
    n = (r2 - r1 + 1) * (c2 - c1 + 1)           # clipped area
    return rect_corners(S, r1, c1, r2, c2) / n

[[round(box_mean(m, S, r, c, 1), 2) for c in range(4)] for r in range(4)]
# =>
# [[3.5,  4.0,  5.0,  5.5 ],
#  [5.5,  6.0,  7.0,  7.5 ],
#  [9.5,  10.0, 11.0, 11.5],
#  [11.5, 12.0, 13.0, 13.5]]

[[round(box_mean(m, S, r, c, 2), 2) for c in range(4)] for r in range(4)]
# =>
# [[6.0,  6.5,  6.5,  7.0 ],
#  [8.0,  8.5,  8.5,  9.0 ],
#  [8.0,  8.5,  8.5,  9.0 ],
#  [10.0, 10.5, 10.5, 11.0]]
#
# a radius-25 blur costs exactly the same as radius-1.
# That is what "O(1) regardless of size" buys you, and
# it is why adaptive thresholding is practical.

# ============================================
# Max-sum submatrix of FIXED size — lesson 12, finished

def max_fixed(m, k):
    S = integral(m)
    rows, cols = len(m), len(m[0])
    return max(rect(S, r, c, k, k)
               for r in range(rows - k + 1) for c in range(cols - k + 1))

max_fixed(m, 2)             # => 54
max_fixed(m, 3)             # => 99
#
# O(rows*cols), not O(rows*cols*k^2)

# ============================================
# Max-sum submatrix of ANY size — Kadane on column pairs
#
# Fix a top and bottom row, collapse the band into a 1D
# array of column sums, and run Kadane. O(rows^2 * cols).

mm = [[1,  -2, -1, 4 ],
      [-8,  3,  4, 2 ],
      [3,   8, 10, -8],
      [-4, -1,  1, 7 ]]

def kadane(a):
    best = cur = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

kadane([1, -2, -1, 4])      # => 4

def max_submatrix(m):
    rows, cols = len(m), len(m[0])
    best = None
    for top in range(rows):
        colsum = [0] * cols
        for bot in range(top, rows):
            for c in range(cols):
                colsum[c] += m[bot][c]      # extend the band downward
            v = kadane(colsum)
            if best is None or v > best:
                best = v
    return best

max_submatrix(mm)           # => 27
#
# brute force over all rectangles agrees: 27, at
# (r=0, c=1, h=4, w=3) — the middle three columns,
# full height.

# ============================================
# WHY MAX CANNOT USE THIS TABLE
#
# Inclusion-exclusion needs to SUBTRACT the overlap.
# Max has no subtraction. Here is the proof: two
# matrices with IDENTICAL prefix-max tables and
# different answers for the same sub-rectangle.

A = [[9, 1],
     [1, 5]]

B = [[9, 1],
     [1, 2]]

def prefix_max(m):
    rows, cols = len(m), len(m[0])
    S = [[float('-inf')] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            S[r+1][c+1] = max(m[r][c], S[r][c+1], S[r+1][c])
    return S

prefix_max(A) == prefix_max(B)          # => True   both tables are all 9s
A[1][1], B[1][1]                        # => (5, 2)
#
# the tables are the same, the answers differ — so NO
# formula over the table can recover the sub-rectangle
# max. That is what "no inverse" means, concretely.
#
# for max you need a sparse table, a segment tree, or
# lesson 12's sliding deque.

# ============================================
# XOR, on the other hand, works fine
#
# XOR is its own inverse, so the same four-corner
# formula applies with ^ in place of + and -.

def integral_xor(m):
    rows, cols = len(m), len(m[0])
    S = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            S[r+1][c+1] = m[r][c] ^ S[r][c+1] ^ S[r+1][c] ^ S[r][c]
    return S

def rect_xor(S, r, c, h, w):
    return S[r+h][c+w] ^ S[r][c+w] ^ S[r+h][c] ^ S[r][c]

SX = integral_xor(m)
rect_xor(SX, 0, 0, 4, 4)    # => 16     (1^2^...^16)
#
# verified against brute force on all 100 rectangles.
# The test for "can I prefix this?" is exactly:
# does the operation have an inverse?

# ============================================
# THE MIRROR IMAGE: the difference array
#
# Prefix sum: O(1) range QUERY on static data.
# Difference array: O(1) range UPDATE, read at the end.
#
# Mark the corners of each update, then prefix-sum the
# marks to materialise the result.

def range_add_1d(n, ops):
    d = [0] * (n + 1)
    for l, r, v in ops:
        d[l] += v
        d[r+1] -= v                     # switch the increment off
    return list(accumulate(d))[:n]

range_add_1d(6, [(0, 2, 3), (2, 4, 1), (5, 5, 10)])
# => [3, 3, 4, 1, 1, 10]

# 2D: four corner marks instead of two
def range_add_2d(rows, cols, ops):
    d = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r1, c1, r2, c2, v in ops:
        d[r1][c1]   += v
        d[r1][c2+1] -= v
        d[r2+1][c1] -= v
        d[r2+1][c2+1] += v              # added back — the same corners
    out = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            cur = d[r][c]
            if r:        cur += out[r-1][c]
            if c:        cur += out[r][c-1]
            if r and c:  cur -= out[r-1][c-1]
            out[r][c] = cur
    return out

range_add_2d(4, 4, [(0, 0, 1, 1, 5),
                    (1, 1, 3, 3, 2),
                    (2, 0, 2, 3, 1)])
# =>
# [[5, 5, 0, 0],
#  [5, 7, 2, 2],
#  [1, 3, 3, 3],
#  [0, 2, 2, 2]]
#
# verified against applying every update cell by cell.
# 1000 updates on a 1000x1000 grid: 4000 writes plus one
# final sweep, instead of a billion writes.

range_add_2d(3, 3, [(1, 1, 2, 2, 1), (0, 0, 1, 1, 1)])
# =>
# [[1, 1, 0],
#  [1, 2, 1],
#  [0, 1, 1]]      LeetCode 2536

# ============================================
# THE CAVEAT: the data must be STATIC
#
# One change to m[r][c] invalidates every table entry
# below and to the right of it — O(rows*cols) to repair.
#
#   many queries, no updates   -> prefix sum
#   many updates, no queries   -> difference array
#   BOTH interleaved           -> Fenwick tree (BIT) or
#                                 segment tree, O(log n) each

# ============================================
# Floats: catastrophic cancellation is real
#
# The table holds sums of the whole top-left block. If
# the background is large and the query is small, you
# subtract two nearly equal huge numbers.

huge = [[1e16] * 4 for _ in range(4)]
huge[2][2] = 1.0

rect(integral(huge), 2, 2, 1, 1)        # => 0.0    should be 1.0
#
# the 1.0 was lost inside 1e16 during the build.
# Integers in Python are exact and arbitrary precision,
# so this NEVER happens with int data:
rect(integral([[10**9, 1], [1, 10**9]]), 0, 0, 2, 2) == 2*10**9 + 2   # => True
#
# with floats, keep values in a similar range or use
# math.fsum / Decimal for the build.

# ============================================
# Compare

# read every cell in the rectangle    -> O(area)
sum(m[i][j] for i in range(r, r+h) for j in range(c, c+w))

# read four table entries             -> O(1), this lesson
rect(S, r, c, h, w)

# slide a window and re-sum           -> lesson 12, naive
# slide a window with this table      -> lesson 12, fast
# blur with a k x k kernel            -> lesson 15, O(k^2)
# blur with this table                -> O(1) per pixel
#
# prefix sum is not a new pattern so much as the
# ACCELERATOR for the window patterns of lessons 12-15.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|1D prefix|`accumulate(xs, initial=0)`|
|the 2D table|`m[r][c] + S[r][c+1] + S[r+1][c] - S[r][c]`|
|no edge cases|pad with a zero row **and** a zero column|
|any rectangle|`D - B - C + A` — four lookups|
|to count, not sum|the same table on a 0/1 matrix|
|"is this block all ones?"|`rect(...) == k*k`|
|a blur of any radius|`rect(...) / area`|
|max instead of sum|**you can't** — no inverse; use a deque or segment tree|
|O(1) range **updates**|difference array, then prefix-sum it|
|updates *and* queries|Fenwick tree, not this|

---

## Key Insight

**Prefix sum buys O(1) queries by precomputing every prefix once — and it works only for operations that can be undone.**

The formula is inclusion–exclusion, nothing more:

```text
wanted = whole - top - left + top-left
```

The `+ A` at the end is there because the top-left corner block was removed twice. That single line is the pattern, in 1D, 2D, and n dimensions.

What actually matters when applying it:

1. **The inverse requirement is a hard boundary, not a preference.** Sum, count and XOR have inverses; max and min do not. The proof is concrete: two matrices can have *identical* prefix-max tables and different sub-rectangle maxima, so no formula over the table could possibly work. This is exactly why lesson 12 needed a monotonic deque for window maxima but could use four lookups for window sums.
    
2. **Pad the table.** An extra row and column of zeros removes every `if r == 0` from both the build and the query. It is the same trick as the sentinel border in lesson 9.
    
3. **Pick one index convention.** The exclusive form `rect(S, r, c, h, w)` and the inclusive form `rect_corners(S, r1, c1, r2, c2)` are both correct and differ by scattered `+1`s. Mixing them yields plausible wrong answers rather than crashes.
    
4. **The data must be static.** One cell change invalidates the whole lower-right quadrant of the table. If updates and queries interleave, you want a Fenwick tree instead.
    
5. **Difference arrays are the mirror image.** Prefix sum makes *reads* O(1) on static data; a difference array makes *writes* O(1) and pays once at the end. Four corner marks per rectangle update, one sweep to materialise.
    

---

## Prefix Sum vs the Window Patterns

|Pattern|Cost of one region|Precompute|Works for|
|---|---|---|---|
|**Lesson 12** naive window|O(k²)|none|anything|
|**Lesson 12** window max|O(1) amortised|deque, per k|max, min|
|**Lesson 15** convolution|O(k²)|none|any weights|
|**Prefix sum**|**O(1)**|O(rows × cols), once|sum, count, XOR|

```text
  windows ask:  "what is in this rectangle?"
  prefix sum answers:  "here, in four lookups"

  the catch: only for operations you can subtract back out
```

> **Mental shift:** every earlier pattern scaled with the *size of the region*. This one doesn't. A 3×3 query and a 300×300 query both cost the same four array reads. That's why prefix sum is less a pattern in its own right and more the **accelerator** that makes the sliding-window and convolution patterns from lessons 12–15 practical at scale.
