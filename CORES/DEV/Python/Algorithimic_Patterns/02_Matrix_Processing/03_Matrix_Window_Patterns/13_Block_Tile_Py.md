# 13. Block / Tile

## Mental Model

Take the sliding window of lesson 12 and change **one number**: set the stride equal to the window size.

```text
stride 1                    stride k
overlapping windows         non-overlapping tiles

┌───┐                       ┌───┬───┐
│1 2│3 4                    │1 2│3 4│
│5 6│7 8                    │5 6│7 8│
 9 10 11 12                 ├───┼───┤
 13 14 15 16                │9 10│11 12│
                            │13 14│15 16│
 9 positions, they overlap  └───┴───┘
                            4 tiles, they partition
```

That single change turns a *scan* into a **partition**. Every cell now belongs to exactly one tile — no overlap, no double-counting, and the tiles can be processed **independently and in any order**.

That independence is the whole point. It is why tiling shows up wherever work is divided: JPEG's 8×8 blocks, Sudoku's 3×3 boxes, CNN pooling layers, cache-blocked matrix multiply, parallel chunking, screen tiles in a renderer.

The one wrinkle Python makes you handle: **the matrix may not divide evenly.** Then the last row and column of tiles are short, and you must decide — accept ragged tiles, or pad the matrix first.

---

## Relationship to Cognitive Verb

```text
Partition
    ↓
Block / Tile
```

Related verbs:

- Partition
    
- Divide into blocks
    
- Chunk
    
- Tile
    
- Split evenly
    
- Downsample / pool
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Tile boundaries|block starts|`range(0, rows, h)`|
|Take a tile|the h × w block|`[row[c:c+w] for row in m[r:r+h]]`|
|All tiles|grid of blocks|nested comprehension over the two ranges|
|Flatten a tile|cells of one block|`[x for row in tile for x in row]`|
|Pool|one value per tile|`max`, `min`, `sum`, mean|
|Tile count|even or ragged|`-(-rows//h) * -(-cols//w)`|
|Reassemble|blocks → matrix|`zip` / concatenation per tile row|
|Rearrange tiles|block transpose|`zip(*tile_grid)`|
|Same value per tile|pixelate|write the pooled value back|
|Row chunking (1D)|group a flat list|`zip(*[iter(xs)]*n)`|

---

## Common Uses

- JPEG / DCT 8×8 blocks
    
- Sudoku 3×3 box validation
    
- Max-pooling and average-pooling in CNNs
    
- Image downsampling and pixelation
    
- Sprite sheets and tile maps
    
- Chess / board game quadrants
    
- Cache-blocked (tiled) matrix multiplication
    
- Splitting work across threads or machines
    
- Block matrices in linear algebra
    
- Mosaic and thumbnail generation
    

---

## Hidden Interview Problems

- Valid Sudoku (the box rule)
    
- Pixelate / blur an image by blocks
    
- Max pooling over a matrix
    
- Check if a matrix is block-diagonal
    
- Rearrange a matrix by swapping quadrants
    
- Count distinct blocks
    
- Split a matrix into k parts of equal sum
    
- Rotate an image in tiles
    

---

## Recognition Clues

If you hear...

- "divide the matrix into blocks..."
    
- "each 3×3 box..."
    
- "non-overlapping..."
    
- "downsample by 2..."
    
- "chunks / tiles / quadrants..."
    
- "process each region independently..."
    

...think **Block / Tile**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Unit|An h × w block|
|Stride|Equal to the block size|
|Overlap|None — the tiles partition the matrix|
|Tile count|`ceil(rows/h) * ceil(cols/w)`|
|Ragged edges|Yes, unless the sizes divide evenly|
|Time Complexity|O(rows × cols) — every cell read once|
|Space Complexity|O(rows × cols) if materialised, O(1) streaming|
|Common Domains|Images, compression, ML pooling, parallelism|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

m = [[1,  2,  3,  4],
     [5,  6,  7,  8],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

# ============================================
# The one idiom to remember
#
# Same two slices as lesson 12. The ONLY difference is
# the step in range() — h and w instead of 1.

def tiles(m, h, w):
    return [[[row[c:c+w] for row in m[r:r+h]]
             for c in range(0, len(m[0]), w)]
            for r in range(0, len(m), h)]

t = tiles(m, 2, 2)

t[0][0]                 # => [[1, 2], [5, 6]]
t[0][1]                 # => [[3, 4], [7, 8]]
t[1][0]                 # => [[9, 10], [13, 14]]
t[1][1]                 # => [[11, 12], [15, 16]]

len(t), len(t[0])       # => (2, 2)   a 2x2 grid OF 2x2 tiles

# note the result is a grid of grids — four dimensions.
# Keeping the tile GRID (not a flat list) is what makes
# reassembly and block transpose easy later.

# ============================================
# Note the range step — that is the entire lesson
#
# range(0, rows, 1)  -> sliding window, overlapping
# range(0, rows, h)  -> tiles, partitioning

list(range(0, 4, 1))    # => [0, 1, 2, 3]     4 positions, overlap
list(range(0, 4, 2))    # => [0, 2]           2 positions, disjoint

# ============================================
# Pooling — one number per tile

def pool(m, h, w, f):
    return [[f([x for row in tile for x in row]) for tile in trow]
            for trow in tiles(m, h, w)]

pool(m, 2, 2, max)                          # => [[6, 8], [14, 16]]
pool(m, 2, 2, min)                          # => [[1, 3], [9, 11]]
pool(m, 2, 2, sum)                          # => [[14, 22], [46, 54]]
pool(m, 2, 2, lambda xs: sum(xs)/len(xs))   # => [[3.5, 5.5], [11.5, 13.5]]

# a 4x4 becomes a 2x2 — pooling is downsampling by (h, w)

# ============================================
# Tiles are a SUBSET of the sliding window
#
# lesson 12 gave every 2x2 window sum:
#   [[14, 18, 22],
#    [30, 34, 38],
#    [46, 50, 54]]
#
# the tiles are the four corners of that grid — positions
# (0,0), (0,2), (2,0), (2,2). Same windows, sampled at
# stride 2 instead of 1.

pool(m, 2, 2, sum)                          # => [[14, 22], [46, 54]]

# ============================================
# Ragged tiles — the real-world case
#
# 5 does not divide by 2. range(0, 5, 2) still yields
# 0, 2, 4, and the last slice simply comes up short.
# Python slicing NEVER raises for this: row[4:6] on a
# 5-wide row returns one element, not an error.

m5 = [[1,  2,  3,  4,  5 ],
      [6,  7,  8,  9,  10],
      [11, 12, 13, 14, 15],
      [16, 17, 18, 19, 20],
      [21, 22, 23, 24, 25]]

t5 = tiles(m5, 2, 2)

len(t5), len(t5[0])                 # => (3, 3)   not (2, 2)
t5[-1][-1]                          # => [[25]]   a 1x1 tile
[len(tile[0]) for tile in t5[0]]    # => [2, 2, 1]  widths shrink

pool(m5, 2, 2, max)
# =>
# [[7,  9,  10],
#  [17, 19, 20],
#  [22, 24, 25]]
#
# the edge tiles pooled over 2 or 1 cells, not 4.
# Silent, and usually wrong for image work — pad first
# if every tile must be the same size.

# ============================================
# How many tiles? Ceiling division

def tile_count(rows, cols, h, w):
    return -(-rows // h) * -(-cols // w)     # -(-a//b) is ceil(a/b)

tile_count(4, 4, 2, 2)              # => 4    even
tile_count(5, 5, 2, 2)              # => 9    ragged

# ============================================
# Reassemble — tiles back into a matrix
#
# For each tile-row, concatenate the i-th row of every
# tile in it. Works with ragged tiles unchanged.

def untile(t):
    return [[x for tile in trow for x in tile[i]]
            for trow in t
            for i in range(len(trow[0]))]

untile(tiles(m, 2, 2)) == m         # => True
untile(tiles(m5, 2, 2)) == m5       # => True   ragged survives

# ============================================
# Sudoku boxes — tiling IS the box rule

sud = [[(r*3 + r//3 + c) % 9 + 1 for c in range(9)] for r in range(9)]

sud[0]                              # => [1, 2, 3, 4, 5, 6, 7, 8, 9]

boxes = [[x for row in tile for x in row]
         for trow in tiles(sud, 3, 3) for tile in trow]

len(boxes)                          # => 9
boxes[0]                            # => [1, 2, 3, 4, 5, 6, 7, 8, 9]
all(len(set(b)) == 9 for b in boxes)    # => True

# rows and columns are lessons 1 and 2; the box rule is
# the ONLY part of Sudoku that needs tiling

# ============================================
# Pixelate — pool, then write the value back
#
# Pooling shrinks; pixelating keeps the shape and
# flattens each block to one value.

def pixelate(m, k):
    out = [row[:] for row in m]
    rows, cols = len(m), len(m[0])
    for r in range(0, rows, k):
        for c in range(0, cols, k):
            block = [m[i][j] for i in range(r, min(r+k, rows))
                             for j in range(c, min(c+k, cols))]
            avg = sum(block) // len(block)
            for i in range(r, min(r+k, rows)):
                for j in range(c, min(c+k, cols)):
                    out[i][j] = avg
    return out

pixelate(m, 2)
# =>
# [[3,  3,  5,  5 ],
#  [3,  3,  5,  5 ],
#  [11, 11, 13, 13],
#  [11, 11, 13, 13]]
#
# min(r+k, rows) is the ragged guard — without it the
# write-back loop runs past the end

# ============================================
# Rearranging tiles — the payoff of keeping the GRID
#
# Transpose the grid of tiles, leave each tile alone.

def tile_transpose(m, k):
    return untile([list(r) for r in zip(*tiles(m, k, k))])

tile_transpose(m, 2)
# =>
# [[1, 2, 9,  10],
#  [5, 6, 13, 14],
#  [3, 4, 11, 12],
#  [7, 8, 15, 16]]
#
# the 2x2 blocks moved; their contents did not.
# Compare with a real transpose (lesson 16), which
# moves the cells too.

# ============================================
# The 1D version — grouping a flat sequence
#
# The classic grouper. Worth knowing because tiling a
# matrix is this idea applied twice.

xs = [1, 2, 3, 4, 5, 6]

[xs[i:i+2] for i in range(0, len(xs), 2)]   # => [[1,2],[3,4],[5,6]]

list(zip(*[iter(xs)] * 2))                  # => [(1,2),(3,4),(5,6)]
#
# zip(*[iter(xs)]*2) DROPS a ragged remainder;
# the slice version KEEPS it. Pick deliberately.

# ============================================
# Streaming — never materialise the tiles
#
# For big matrices, yield tiles instead of building a
# 4-deep nested list.

def itertiles(m, h, w):
    for r in range(0, len(m), h):
        for c in range(0, len(m[0]), w):
            yield (r, c), [row[c:c+w] for row in m[r:r+h]]

[(pos, sum(map(sum, tile))) for pos, tile in itertiles(m, 2, 2)]
# => [((0,0), 14), ((0,2), 22), ((2,0), 46), ((2,2), 54)]
#
# each tile is independent — this loop parallelises as-is

# ============================================
# Compare

# stride 1  -> overlapping windows (lesson 12)
[(r, c) for r in range(0, rows-k+1, 1) for c in range(0, cols-k+1, 1)]

# stride k  -> tiles, this lesson
[(r, c) for r in range(0, rows, k) for c in range(0, cols, k)]

# note the ranges differ too: windows stop at rows-k+1
# (never hang off the edge), tiles run to rows (and the
# last one is allowed to be short)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|tiles instead of windows|step by `h`/`w` in `range`|
|a tile|`[row[c:c+w] for row in m[r:r+h]]`|
|the tile grid|nested comprehension, keep it 2D|
|one value per tile|`pool(m, h, w, max)`|
|how many tiles|`-(-rows//h) * -(-cols//w)`|
|the matrix back|`untile` — concat row `i` of each tile|
|blocks moved, cells kept|`zip(*tiles(...))`|
|ragged safety|`min(r+k, rows)` when writing back|
|the 1D version|`zip(*[iter(xs)]*n)` (drops the remainder)|

---

## Key Insight

**Block/tile is the sliding window with stride = size.** One number changes; the meaning changes completely:

```text
stride < size   ->  overlap     ->  a SCAN     (lesson 12)
stride = size   ->  partition   ->  a SPLIT    (this lesson)
stride > size   ->  gaps        ->  sampling
```

Partitioning buys you the property that scanning cannot: **every cell belongs to exactly one tile**, so tiles are independent. Sum the tiles and you get the matrix total; process them out of order, in parallel, on different machines — the answer is the same. That is why this pattern is the backbone of compression, pooling and parallel decomposition rather than just another way to loop.

Two Python specifics do the real work:

- `range(0, rows, h)` versus `range(0, rows-h+1)` — tiles run to the end and let the last one be short; windows stop early so they never hang off the edge.
    
- Slicing past the end **returns a short list rather than raising**, which is why ragged tiling silently works and silently misleads. `pool(m5, 2, 2, max)` averaged some tiles over 1 cell and 4 cells alike. If uniformity matters, pad the matrix first.
    

---

## Window vs Tile

|Pattern|Stride|Overlap|Output|Cells read|
|---|---|---|---|---|
|**Sliding Window**|1|`k-1`|`(rows-k+1) × (cols-k+1)`|`k²` times each|
|**Block / Tile**|`k`|none|`ceil(rows/k) × ceil(cols/k)`|once each|

```text
Sliding Window          Block / Tile
  scan, compare           split, distribute
  answers overlap         answers are independent
  "best placement?"       "process each region"
```

> **Mental shift:** a window **searches** — you compare placements and pick one. A tile **divides** — you keep them all, and their results reassemble into the whole. Ask yourself which you want, and the stride follows automatically.
