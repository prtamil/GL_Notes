# Pattern 36 — Reshape

## Mental Model

Change the **shape** of data without changing the values.

**Flatten** strips structure away. **Reshape** takes a flat sequence and gives it a different layout.

The building block is **`itertools.batched(xs, n)`** (3.12+), or the slice comprehension `[xs[i:i+n] for i in range(0, len(xs), n)]`. There's no general N-dimensional reshape outside NumPy, and for anything numeric and rectangular NumPy is the right answer anyway.

---

## Relationship to Cognitive Verb

```text
Structure
     ↓
Reshape
```

Reshape is a **Structure** pattern: it changes **how the data is arranged**, never the data itself.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|1D → 2D|`[1,2,3,4] → [[1,2],[3,4]]`|`batched(xs, 2)`|
|1D → 2D (any version)|slicing|`[xs[i:i+n] for i in range(0, len(xs), n)]`|
|Drop the Partial Row|exact rows only|`zip(*[iter(xs)] * n)`|
|Pad the Partial Row|fill the tail|`zip_longest(*[iter(xs)] * n, fillvalue=0)`|
|2D → 1D|matrix → vector|`chain.from_iterable(m)`|
|Reshape by Columns|column-major fill|`zip(*batched(xs, rows))`|
|Rows ↔ Columns|`(r,c)` → `(c,r)`|`zip(*m)`|
|Batch a Stream|no `len()`|`islice` in a loop, or `batched`|
|N-dimensional|tensors|`numpy.reshape`|

> **Note:** `batched` keeps a **short final batch**; the `zip(*[iter(xs)] * n)` grouper **drops** it. A reshape is only lossless when `len(xs)` is divisible by the row width — decide explicitly what happens to the remainder.

---

## Common Uses

- Matrix construction

- Image pixels

- CSV parsing

- Batch processing

- Neural network tensors

- Packet parsing

- Data chunking

- Grid generation

---

## Hidden Interview Problems

- Convert an array to a matrix

- Spiral matrix traversal

- Chunk data into batches

- Reshape image pixels

- Grid generation

- Fixed-width record parsing

---

## Recognition Clues

If you hear:

- Reshape

- Matrix

- Rows and columns

- Chunk into groups

- Convert to grid

- Batch size

- Change dimensions

Think:

**→ Reshape**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Structure|
|Pattern|Reshape|
|Input|linear or nested sequence|
|Output|a different layout|
|Preserves Values|Yes|
|Preserves Order|Yes (row-major by default)|
|Total Count|unchanged, if nothing is dropped|
|Requires|`len(xs) % width == 0` to be exact|
|Primary Use|Change organization|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import accumulate, batched, chain, islice, zip_longest  # batched: 3.12+

xs = list(range(1, 13))                 # 1..12

# ============================================
# 1D → 2D

[list(b) for b in batched(xs, 3)]
# => [[1,2,3], [4,5,6], [7,8,9], [10,11,12]]

# pre-3.12, or when you want real lists from a real list:
[xs[i:i + 3] for i in range(0, len(xs), 3)]         # => same

# range(0, len, n) generates the row starts. That's the whole idea.

# ============================================
# The partial final row — three deliberate choices

ys = list(range(1, 13))
[list(b) for b in batched(ys, 5)]
# => [[1..5], [6..10], [11,12]]         KEEPS the short tail

list(zip(*[iter(ys)] * 5))
# => [(1..5), (6..10)]                  DROPS 11 and 12

list(zip_longest(*[iter(ys)] * 5, fillvalue=0))
# => [(1..5), (6..10), (11,12,0,0,0)]   PADS the tail

# the grouper idiom: [iter(ys)] * 5 is the SAME iterator five times,
# so zip pulls five consecutive items from one shared cursor.

# a silently dropped tail is the classic reshaping bug — pick on purpose

# ============================================
# 2D → 1D

m = [[1, 2, 3], [4, 5, 6]]
list(chain.from_iterable(m))            # => [1,2,3,4,5,6]
[x for row in m for x in row]           # => same

# ============================================
# Round trip — only exact when the shape divides evenly

flat = list(chain.from_iterable(m))
[list(b) for b in batched(flat, 3)] == m            # => True

# ragged input never round-trips:
ragged = [[1, 2], [3], [4, 5, 6]]
flat = list(chain.from_iterable(ragged))            # => [1,2,3,4,5,6]
# the shape (2,1,3) is gone forever. Flattening is lossy.

# ============================================
# Reshape to a target shape — validate first

def reshape(xs, rows, cols):
    if len(xs) != rows * cols:
        raise ValueError(f"cannot reshape {len(xs)} items into {rows}x{cols}")
    return [list(xs[r * cols:(r + 1) * cols]) for r in range(rows)]

reshape(xs, 3, 4)
# => [[1,2,3,4], [5,6,7,8], [9,10,11,12]]
reshape(xs, 4, 3)
# => [[1,2,3], [4,5,6], [7,8,9], [10,11,12]]
# reshape(xs, 5, 3)     ValueError — 12 != 15

# numpy raises on a mismatched reshape; hand-rolled code usually
# truncates instead. Check the product, or you get quiet data loss.

# ============================================
# Infer the missing dimension — numpy's -1

def reshape_auto(xs, cols):
    rows, rem = divmod(len(xs), cols)
    if rem:
        raise ValueError(f"{len(xs)} items don't divide into rows of {cols}")
    return reshape(xs, rows, cols)

reshape_auto(xs, 4)                     # => 3 rows of 4

# divmod gives you the row count and the leftover in one call —
# the leftover IS the validity check

# ============================================
# Column-major fill — the other reading order

# row-major (C order): fill each row left to right
[list(b) for b in batched(xs, 4)]
# => [[1,2,3,4], [5,6,7,8], [9,10,11,12]]

# column-major (Fortran order): fill each column top to bottom
[list(c) for c in zip(*batched(xs, 3))]
# => [[1,4,7,10], [2,5,8,11], [3,6,9,12]]

# same 12 values, same 3x4 shape, completely different matrix.
# When reshaping pixel or sensor data, the fill order is the spec —
# get it wrong and the image comes out sheared.

# ============================================
# Reshape a string / fixed-width records

s = "abcdefghijkl"
["".join(b) for b in batched(s, 4)]     # => ['abcd', 'efgh', 'ijkl']
[s[i:i + 4] for i in range(0, len(s), 4)]           # => same, simpler

# fixed-width parsing with NAMED widths, which is the real use:
record = "JOHN      SMITH     42"
widths = [10, 10, 2]
bounds = list(accumulate(widths, initial=0))        # => [0, 10, 20, 22]
[record[a:b].strip() for a, b in zip(bounds, bounds[1:])]
# => ['JOHN', 'SMITH', '42']

# accumulate turns widths into cut points; pairwise cut points into slices

# ============================================
# Batch processing — the everyday reshape

for batch in batched(range(1000), 100):
    ...                                 # 10 calls instead of 1000

# on a STREAM, where len() doesn't exist:
def chunks(it, n):
    it = iter(it)
    while chunk := list(islice(it, n)):
        yield chunk

list(chunks(iter(xs), 5))
# => [[1..5], [6..10], [11,12]]

# the walrus makes the "read n, stop when empty" loop one line.
# batched() does this natively in 3.12+, on any iterable.

# ============================================
# Grid generation and indexing

rows, cols = 3, 4
grid = [list(b) for b in batched(xs, cols)]

# flat index ↔ (row, col) — the conversion behind every reshape
def to_rc(i, cols):
    return divmod(i, cols)              # (row, col)

def to_flat(r, c, cols):
    return r * cols + c

to_rc(6, 4)                             # => (1, 2)
grid[1][2]                              # => 7
xs[to_flat(1, 2, 4)]                    # => 7      same element

# divmod IS the reshape, for a single index. A 2D array is just a
# 1D array with an index-arithmetic convention on top.

# ============================================
# Neighbours in a reshaped grid

def neighbours(r, c, rows, cols):
    for dr, dc in ((-1,0), (1,0), (0,-1), (0,1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            yield nr, nc

list(neighbours(0, 0, 3, 4))            # => [(1,0), (0,1)]

# the bounds check is the entire difference between a grid and a
# flat list — without it, index arithmetic wraps to the wrong row

# ============================================
# Spiral traversal — repeated peel-and-transpose

def spiral(m):
    out = []
    m = [list(r) for r in m]
    while m:
        out += m.pop(0)                 # take the top row
        m = [list(r) for r in zip(*m)][::-1]         # rotate counter-cw
    return out

spiral([[1,2,3], [4,5,6], [7,8,9]])     # => [1,2,3,6,9,8,7,4,5]

# "take a row, rotate, repeat" — the spiral problem collapses into
# reshape plus rotate, with no index bookkeeping at all

# ============================================
# Reshape records — list-of-dicts ↔ dict-of-lists

rows = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
{k: [r[k] for r in rows] for k in rows[0]}          # => {'a':[1,3], 'b':[2,4]}

cols = {"a": [1, 3], "b": [2, 4]}
[dict(zip(cols, vals)) for vals in zip(*cols.values())]
# => [{'a':1,'b':2}, {'a':3,'b':4}]

# row-major ↔ column-major for records. This is exactly what
# pandas does between a list of records and a DataFrame.

# ============================================
# numpy — real N-dimensional reshaping

# import numpy as np
# a = np.arange(12)
# a.reshape(3, 4)        # 2D
# a.reshape(2, 2, 3)     # 3D
# a.reshape(-1, 4)       # -1 = "infer this dimension"
# a.reshape(3, 4, order="F")     # column-major fill
# a.reshape(5, 3)        # ValueError — numpy REFUSES to lose data

# reshape in numpy is O(1): it changes the strides, not the buffer.
# Pure Python must build new lists. Anything numeric and large
# belongs in numpy — this pattern is for ragged/heterogeneous data.

# ============================================
# Compare

batched(xs, n)                  # 1D → 2D                → Reshape
chain.from_iterable(m)          # 2D → 1D                → Flatten
zip(*m)                         # (r,c) → (c,r)          → Transpose
xs[i:i+n] for i in range(0,…)   # 1D → 2D, any version   → Reshape
zip(*[iter(xs)] * n)            # 1D → 2D, tail dropped  → Reshape
divmod(i, cols)                 # flat index → (r, c)    → Reshape
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|rows of n, keep the tail|`batched(xs, n)`|
|rows of n, any Python|`[xs[i:i+n] for i in range(0, len(xs), n)]`|
|rows of n, drop the tail|`zip(*[iter(xs)] * n)`|
|rows of n, pad the tail|`zip_longest(*[iter(xs)] * n, fillvalue=…)`|
|to flatten back|`chain.from_iterable(m)`|
|column-major fill|`zip(*batched(xs, rows))`|
|to check a shape is valid|`divmod(len(xs), cols)`|
|flat index → row, col|`divmod(i, cols)`|
|row, col → flat index|`r * cols + c`|
|to batch a stream|`islice` in a `while` loop|
|true N-D reshaping|`numpy.reshape`|

---

### Key Insight

**A 2-D structure is a 1-D structure plus an index convention, and `divmod` is the whole conversion.** `divmod(i, cols)` turns a flat position into `(row, col)`, and `r * cols + c` turns it back. Reshaping a list into rows just makes that convention concrete, which is why `batched` and slice-stepping give you the same thing, and why NumPy can reshape in O(1) by changing strides and never touching the data.

**The remainder is a decision the API quietly makes for you, so make it yourself.** `batched` keeps a short final row, the `zip(*[iter(xs)] * n)` grouper drops it, and `zip_longest` pads it. Each of those is right for some problem and disastrous for another. A dropped tail in a batch-upload loop means records that were never written, with no error anywhere. Check `divmod(len(xs), width)` and decide on purpose.

The second decision is **fill order**. Row-major and column-major give you the same values in the same shape and a completely different matrix. For pixel buffers, sensor frames and anything arriving off the wire, fill order is part of the format spec. `[list(c) for c in zip(*batched(xs, rows))]` is the column-major form, and most people only go looking for it after the output "looks sheared".
