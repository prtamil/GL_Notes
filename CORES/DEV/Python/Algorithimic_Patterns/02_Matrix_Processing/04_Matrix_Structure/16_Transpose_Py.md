# 16. Transpose

## Mental Model

Every pattern so far *read* a matrix. This section **rearranges** it — the cells are unchanged, only their positions move.

Transpose is the first and most important rearrangement: **swap the two coordinates.**

```text
(r, c)  ->  (c, r)

[[1, 2, 3],          [[1, 4],
 [4, 5, 6]]     ->    [2, 5],
                      [3, 6]]
   2 x 3                3 x 2
```

Rows become columns and columns become rows. The main diagonal is the mirror axis — cells on it never move.

Two things make transpose worth a whole lesson rather than a footnote:

- **It is one expression in Python.** `zip(*m)` — unpack the rows as arguments to `zip`, which walks them in lockstep. This is the single most useful structural idiom in the language, and it is why "loop over columns" is almost never the right code.
    
- **It generates everything else.** Every rotation in this section is a transpose followed by a flip. Learn transpose properly and lessons 17, 19 and 21 are one line each.
    

---

## Relationship to Cognitive Verb

```text
Swap Axes
    ↓
Transpose
```

Related verbs:

- Swap rows and columns
    
- Pivot
    
- Mirror across the diagonal
    
- Reorient
    
- Flip the axes
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Transpose|the whole thing|`list(zip(*m))`|
|As lists, not tuples|usable result|`[list(r) for r in zip(*m)]`|
|By comprehension|explicit indices|`[[m[r][c] for r in range(rows)] for c in range(cols)]`|
|One column|column `c`|`[row[c] for row in m]` or `list(zip(*m))[c]`|
|In place|square only|swap `m[r][c]` and `m[c][r]` for `c > r`|
|Anti-transpose|the other diagonal|`zip(*[row[::-1] for row in m[::-1]])`|
|Dict grid|coordinate swap|`{(c, r): v for (r, c), v in g.items()}`|
|Unzip|inverse of zip|`zip(*pairs)` — same function|
|Rows of unequal length|ragged input|`itertools.zip_longest`|

---

## Common Uses

- Column-wise operations, done as row-wise operations
    
- Matrix multiplication (`A @ B` needs `B`'s columns)
    
- Pivoting tables and spreadsheets
    
- Converting row-records to column-arrays
    
- Image axis swap
    
- Coordinate system changes
    
- Building rotations
    
- Reading CSV columns
    

---

## Hidden Interview Problems

- Transpose a matrix (in place, for square)
    
- Rotate an image by 90°
    
- Check if a matrix is symmetric
    
- Column sums / column maxima
    
- Validate Sudoku columns
    
- Matrix multiplication
    
- Find the diagonal of a matrix
    
- Convert row-major data to column-major
    

---

## Recognition Clues

If you hear...

- "swap rows and columns..."
    
- "process each column..."
    
- "pivot the table..."
    
- "mirror along the diagonal..."
    
- "is the matrix symmetric..."
    
- "reorient the grid..."
    

...think **Transpose**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Coordinate rule|`(r, c) → (c, r)`|
|Shape|`rows × cols → cols × rows`|
|Fixed points|The main diagonal|
|Involution|Yes — `T(T(m)) == m`|
|In place|Only for square matrices|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(rows × cols), or O(1) in place (square)|
|Common Domains|Linear algebra, data pivoting, images|

---

## Python Recipe Book

```python
# ============================================
# Two matrices — one non-square, to keep shape honest

m = [[1, 2, 3],
     [4, 5, 6]]                 # 2 x 3

s = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]                 # 3 x 3

# ============================================
# The one idiom to remember
#
#   zip(*m)
#
# The * unpacks the rows into separate arguments, so
# zip walks them in lockstep and yields the columns.

list(zip(*m))
# => [(1, 4), (2, 5), (3, 6)]
#
# note: TUPLES, and a lazy iterator before list().
# Almost always you want lists back:

def transpose(m):
    return [list(r) for r in zip(*m)]

transpose(m)
# =>
# [[1, 4],
#  [2, 5],
#  [3, 6]]

len(m), len(m[0])                       # => (2, 3)
len(transpose(m)), len(transpose(m)[0]) # => (3, 2)   shape swaps

# ============================================
# The explicit version — what zip is doing

[[m[r][c] for r in range(len(m))] for c in range(len(m[0]))]
# =>
# [[1, 4],
#  [2, 5],
#  [3, 6]]
#
# note the loops are INVERTED: c outside, r inside.
# That inversion IS the transpose.

# ============================================
# Transpose is its own inverse

transpose(transpose(m)) == m            # => True

# ============================================
# The diagonal never moves

transpose(s)
# =>
# [[1, 4, 7],
#  [2, 5, 8],
#  [3, 6, 9]]

[transpose(s)[i][i] for i in range(3)]  # => [1, 5, 9]
[s[i][i] for i in range(3)]             # => [1, 5, 9]   unchanged

# ============================================
# Why this matters: columns become free
#
# Lesson 2 walked columns the hard way. Transpose and
# every row idiom from lesson 1 works on columns.

transpose(m)[1]                     # => [2, 5]   column 1

[sum(col) for col in zip(*m)]       # => [5, 7, 9]     column sums
[max(col) for col in zip(*m)]       # => [4, 5, 6]     column maxima

# no new technique — column ops ARE row ops after zip(*m)

# ============================================
# Symmetry test — one line

def symmetric(m):
    return m == transpose(m)

symmetric(s)                                # => False
symmetric([[1, 7], [7, 4]])                 # => True

# ============================================
# In place — square matrices only
#
# Non-square cannot be done in place: the shape changes,
# so there is nowhere to put the extra cells.
#
# Walk the UPPER triangle only (c > r). Walking the full
# grid swaps every pair twice and gives you back the
# original — a classic bug.

def transpose_inplace(m):
    n = len(m)
    for r in range(n):
        for c in range(r + 1, n):           # c > r, upper triangle
            m[r][c], m[c][r] = m[c][r], m[r][c]
    return m

transpose_inplace([row[:] for row in s])
# =>
# [[1, 4, 7],
#  [2, 5, 8],
#  [3, 6, 9]]

# ============================================
# The OTHER diagonal — anti-transpose
#
# Mirror across the anti-diagonal instead:
#   (r, c) -> (n-1-c, n-1-r)

def anti_transpose(m):
    return [list(r) for r in zip(*[row[::-1] for row in m[::-1]])]

anti_transpose(s)
# =>
# [[9, 6, 3],
#  [8, 5, 2],
#  [7, 4, 1]]

# it is the ordinary transpose sandwiched in 180s
anti_transpose(s) == [row[::-1] for row in transpose(s)[::-1]]   # => True

anti_transpose(anti_transpose(s)) == s      # => True, also an involution

# ============================================
# zip is also UNZIP — same function both ways

pairs = [(1, 'a'), (2, 'b'), (3, 'c')]
list(zip(*pairs))               # => [(1, 2, 3), ('a', 'b', 'c')]

# transposing a list of records gives you its columns.
# This is the whole trick behind "pivot the table".

# ============================================
# Ragged rows — zip TRUNCATES silently
#
# The most common transpose bug in Python.

ragged = [[1, 2, 3],
          [4, 5]]

list(zip(*ragged))              # => [(1, 4), (2, 5)]
#                                    the 3 vanished

from itertools import zip_longest
list(zip_longest(*ragged, fillvalue=None))
# => [(1, 4), (2, 5), (3, None)]
#
# zip stops at the SHORTEST row. If your rows might
# differ in length, say so explicitly.

# ============================================
# Dict grids transpose by rewriting the key

g = {(r, c): v for r, row in enumerate(m) for c, v in enumerate(row)}

{(c, r): v for (r, c), v in g.items()}
# => {(0,0): 1, (1,0): 2, (2,0): 3, (0,1): 4, (1,1): 5, (2,1): 6}
#
# with coordinates as keys, a transpose is a rename

# ============================================
# What transpose generates
#
# Every rotation in this section is transpose + a flip.

[row[::-1] for row in transpose(s)]     # => rotate  90 CW  (lesson 17)
transpose(s)[::-1]                      # => rotate 270 CW  (lesson 19)

# ============================================
# Compare

# same cells, new positions   -> this section
transpose(m)

# same positions, new values  -> convolution (lesson 15)
# same cells, new ORDER only  -> flatten/reshape (lessons 22-23)

transpose(m)                            # shape 2x3 -> 3x2
[x for row in transpose(m) for x in row]    # => [1, 4, 2, 5, 3, 6]
[x for row in m for x in row]               # => [1, 2, 3, 4, 5, 6]
#
# transpose CHANGES the linear order. Reshape does not.
# That is the dividing line in this section.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the transpose|`[list(r) for r in zip(*m)]`|
|one column|`[row[c] for row in m]`|
|all column sums|`[sum(col) for col in zip(*m)]`|
|is it symmetric|`m == transpose(m)`|
|in place (square)|swap `m[r][c]`/`m[c][r]` for **`c > r`**|
|the other diagonal|`zip(*[row[::-1] for row in m[::-1]])`|
|ragged rows kept|`itertools.zip_longest`|
|to unzip pairs|`zip(*pairs)` — the same call|
|a rotation|transpose, then flip|

---

## Key Insight

**Transpose is the coordinate swap `(r, c) → (c, r)`, and in Python it is `zip(*m)`.**

Three consequences worth internalising:

1. **Columns stop being special.** Lesson 2 needed its own techniques for column traversal; after `zip(*m)` every row idiom from lesson 1 applies unchanged. When you catch yourself writing `for c in range(cols)`, ask whether transposing first would let you write `for col in zip(*m)` instead.
    
2. **It is the generator of the rotation family.** `transpose` + `reverse each row` = rotate 90°. `transpose` + `reverse the row order` = rotate 270°. You do not need to memorise four rotations, only transpose and which flip follows it.
    
3. **In place works only for squares**, and only over the **upper triangle**. Looping the full grid swaps each pair twice, leaving the matrix untouched — a bug that looks like the code did nothing, because it did.
    

And the trap that costs real time: **`zip` truncates to the shortest row.** On ragged input it silently drops data rather than raising. Use `zip_longest` when rows may differ.

---

## The Structure Section

|Lesson|Operation|Shape|Linear order|
|---|---|---|---|
|16 Transpose|`(r,c) → (c,r)`|swaps|changes|
|17-19 Rotations|turn by 90/180/270|swaps (90, 270)|changes|
|20-21 Flips|mirror|preserved|changes|
|22 Reshape|regroup|changes|**preserved**|
|23 Flatten|to 1D|`R×C → R*C`|**preserved**|

```text
same cells, new POSITIONS   ->  16-21  (symmetry)
same cells, new GROUPING    ->  22-23  (layout)
```

> **Mental shift:** traversal, neighborhood and windows all asked *"which cells do I read?"*. Structure asks *"where does each cell go?"* — every operation here is a function from `(r, c)` to a new `(r, c)`, and writing that function down is usually easier than reasoning about the picture.
