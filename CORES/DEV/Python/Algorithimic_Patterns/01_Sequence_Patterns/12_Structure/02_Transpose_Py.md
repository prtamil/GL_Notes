# Pattern 35 — Transpose

## Mental Model

Swap **rows and columns** of a 2D sequence.

A transpose changes the **orientation** of the data and leaves the values alone.

Python's answer is one of its best tricks: **`zip(*rows)`**. Unpacking the rows as arguments turns "take one from each row" into "build a column", which means transpose and unzip are literally the same call.

---

## Relationship to Cognitive Verb

```text
Structure
     ↓
Transpose
```

Transpose is a **Structure** pattern that flips the layout from **row-major** to **column-major**, or back again.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Matrix Transpose|rows ↔ columns|`list(zip(*m))`|
|As Lists Not Tuples|`[[1,4],[2,5]]`|`[list(c) for c in zip(*m)]`|
|Ragged Rows|uneven lengths|`zip_longest(*m, fillvalue=None)`|
|Unzip|inverse of zip|`a, b = zip(*pairs)`|
|Column Stats|sums, maxes|`[sum(c) for c in zip(*m)]`|
|Transpose Strings|`"CAT","DOG"`|`["".join(c) for c in zip(*words)]`|
|Rotate 90°|clockwise|`zip(*m[::-1])`|
|CSV Columns|pivot a file|`zip(*rows)`|
|Numeric Arrays|large matrices|`numpy.array(m).T`|

> **Note:** `zip` stops at the **shortest** row, so a ragged matrix loses data **silently**. Use `zip_longest` when rows may differ in length — and note that transposing twice only round-trips for rectangular input.

---

## Common Uses

- Matrix operations

- CSV processing

- Pivot tables

- Column-wise statistics

- Graphics transformations

- Machine learning datasets

- DataFrame operations

- Image processing

---

## Hidden Interview Problems

- Matrix transpose

- Rotate an image 90°

- Zip / unzip arrays

- Pivot table

- Column sums

- Spreadsheet transformations

- Valid Sudoku (check columns)

---

## Recognition Clues

If you hear:

- Rows to columns

- Columns to rows

- Pivot

- Matrix transpose

- Flip across the diagonal

- Column-wise processing

- Unzip

Think:

**→ Transpose**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Structure|
|Pattern|Transpose|
|Input|2D sequence|
|Output|rows become columns|
|Shape|`(r, c)` → `(c, r)`|
|Returns|tuples, not lists|
|Ragged Input|silently truncated|
|Preserves Values|Yes|
|Primary Use|Matrix reorganization|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import zip_longest

m = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]

# ============================================
# The transpose

list(zip(*m))
# => [(1, 4, 7), (2, 5, 8), (3, 6, 9)]

# WHY it works:
#   zip(*m) is zip([1,2,3], [4,5,6], [7,8,9])
#   zip takes one item from each argument → (1, 4, 7)
#   "one from each row" IS a column.

# as lists rather than tuples:
[list(c) for c in zip(*m)]
# => [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

# ============================================
# Non-square works fine — the shape flips

r = [[1, 2, 3],
     [4, 5, 6]]
list(zip(*r))                           # => [(1,4), (2,5), (3,6)]

# (2 rows × 3 cols) → (3 rows × 2 cols)

# ============================================
# Transpose is its own inverse

list(zip(*zip(*m))) == [tuple(row) for row in m]    # => True

# only for RECTANGULAR input — see the ragged trap below

# ============================================
# THE RAGGED TRAP — zip truncates silently

ragged = [[1, 2, 3],
          [4, 5],
          [6, 7, 8]]
list(zip(*ragged))                      # => [(1,4,6), (2,5,7)]

# the 3 and the 8 are GONE. No error, no warning.

list(zip_longest(*ragged, fillvalue=None))
# => [(1,4,6), (2,5,7), (3,None,8)]     nothing lost

# always ask whether rows can differ in length. In CSV parsing and
# scraped data they usually can.

# ============================================
# Unzip — the same call, read the other way

pairs = [(1, "a"), (2, "b"), (3, "c")]
nums, letters = zip(*pairs)
# nums    => (1, 2, 3)
# letters => ('a', 'b', 'c')

# zip builds pairs; zip(*) takes them apart. One function, both
# directions. This is THE way to split a list of records into
# parallel lists.

# empty input breaks it — zip(*[]) yields nothing, so the unpack fails:
# a, b = zip(*[])       ValueError: not enough values to unpack
a, b = zip(*pairs) if pairs else ((), ())

# ============================================
# Column-wise statistics — the real reason to transpose

[sum(c) for c in zip(*m)]               # => [12, 15, 18]   column sums
[max(c) for c in zip(*m)]               # => [7, 8, 9]      column maxes
[sum(c) / len(c) for c in zip(*m)]      # => [4.0, 5.0, 6.0] column means

# row-wise needs no transpose at all:
[sum(row) for row in m]                 # => [6, 15, 24]

# transpose is how you turn a row-major structure into a
# column-major question. That's its entire job.

# ============================================
# Column-wise on records

rows = [
    {"name": "Alice", "age": 30, "city": "NY"},
    {"name": "Bob",   "age": 25, "city": "LA"},
]
{k: [r[k] for r in rows] for k in rows[0]}
# => {'name': ['Alice','Bob'], 'age': [30,25], 'city': ['NY','LA']}

# row-major (list of dicts) → column-major (dict of lists).
# That IS a transpose, and it's the shape a DataFrame stores.

# ============================================
# Transpose strings

words = ["CAT", "DOG", "PIG"]
["".join(c) for c in zip(*words)]       # => ['CDP', 'AOI', 'TGG']

# strings are sequences of characters, so they transpose directly.
# reading a grid of letters column-wise is one line.

# ============================================
# Rotate a matrix 90° — transpose plus a reverse

[list(c) for c in zip(*m[::-1])]
# => [[7,4,1], [8,5,2], [9,6,3]]        CLOCKWISE

[list(c) for c in zip(*m)][::-1]
# => [[3,6,9], [2,5,8], [1,4,7]]        COUNTER-clockwise

# clockwise  = reverse the rows, then transpose
# counter-cw = transpose, then reverse the rows
# 180°       = [row[::-1] for row in m[::-1]]

# the order of the two operations is the whole difference.
# "Rotate Image" is this one line plus an in-place requirement.

# ============================================
# Pair each row with its column

list(zip(m, zip(*m)))
# => [([1,2,3], (1,4,7)), ([4,5,6], (2,5,8)), ([7,8,9], (3,6,9))]

# row i alongside column i — the diagonal-adjacent view

# ============================================
# The main diagonal — indexing, not transposing

[m[i][i] for i in range(len(m))]        # => [1, 5, 9]
[m[i][len(m) - 1 - i] for i in range(len(m))]       # => [3, 5, 7]

# a transpose leaves the main diagonal fixed — that's what
# "flip across the diagonal" means geometrically

# ============================================
# CSV pivot

# import csv
# with open("data.csv") as fh:
#     rows = list(csv.reader(fh))
# columns = list(zip(*rows))
# header, *values = columns[0]           # first column as a series

# reading column-wise from a row-wise file is exactly this

# ============================================
# Valid Sudoku — check columns by transposing

def rows_ok(grid):
    return all(len(set(r)) == len(r) for r in grid)

def valid(grid):
    return rows_ok(grid) and rows_ok(zip(*grid))    # cols = transposed rows

# write the check once, apply it to the transpose. That's the
# payoff of a cheap orientation flip.

# ============================================
# Laziness and cost

z = zip(*m)                             # lazy iterator
next(z)                                 # => (1, 4, 7)     first column only
list(z)                                 # => [(2,5,8), (3,6,9)]  the rest

# BUT zip(*m) unpacks the outer list eagerly — every row must exist
# in memory and be a real sequence. It cannot transpose a stream of
# rows lazily, because column 0 needs the first element of the LAST
# row before it's complete.

# ============================================
# numpy — for anything large or numeric

# import numpy as np
# a = np.array(m)
# a.T            # => a VIEW, O(1), no data copied at all
# a.T.sum(axis=0)

# numpy's .T just relabels the strides — genuinely free. zip(*m)
# builds r×c new tuples. For big matrices the difference is total.

# ============================================
# Compare

zip(*m)                         # rows ↔ columns          → Transpose
zip(*m[::-1])                   # rotate 90° clockwise    → Transpose
a, b = zip(*pairs)              # unzip                   → Transpose
zip(a, b)                       # zip                     → Pair
chain.from_iterable(m)          # 2D → 1D                 → Flatten
batched(flat, n)                # 1D → 2D                 → Reshape
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|to transpose|`list(zip(*m))`|
|lists not tuples|`[list(c) for c in zip(*m)]`|
|ragged rows kept|`zip_longest(*m, fillvalue=None)`|
|to unzip pairs|`a, b = zip(*pairs)`|
|column sums|`[sum(c) for c in zip(*m)]`|
|to rotate clockwise|`zip(*m[::-1])`|
|to rotate counter-cw|`list(zip(*m))[::-1]`|
|list-of-dicts → dict-of-lists|`{k: [r[k] for r in rows] for k in rows[0]}`|
|column-wise strings|`["".join(c) for c in zip(*words)]`|
|a free transpose|`numpy_array.T`|

---

### Key Insight

**`zip(*m)` is the whole pattern, and the `*` is what does the work.** Unpacking turns a list of rows into separate arguments, and zip's "one item from each argument" rule then produces columns by definition. The same expression unzips a list of pairs, and that's no accident: zipping and transposing are one operation seen from two sides, which is why `zip(*zip(*m))` puts you back where you started.

**`zip` truncates at the shortest input, so a ragged matrix loses data without a word.** This is the failure that reaches production. It works perfectly on your clean test matrix and quietly drops the tail of every long row in real data. If rows can vary in length — CSV, scraped tables, user input — use `zip_longest` and decide what the filler means.

Transposing matters because **it turns a column-wise question into a row-wise one**, and row-wise is the only direction Python iterates naturally. Column sums, per-field statistics, checking Sudoku columns, unzipping records into parallel series: each of these is a loop you already know how to write, pointed at `zip(*m)` instead of `m`. Write the check once, transpose, run it again. For large numeric data reach for `numpy.T`, where the same flip is free because only the strides change.
