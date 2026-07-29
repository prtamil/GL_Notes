# 17. Rotate 90°

## Mental Model

Turn the matrix a quarter turn clockwise. The **top row becomes the right column**.

```text
[[1, 2, 3],          [[7, 4, 1],
 [4, 5, 6],     ->    [8, 5, 2],
 [7, 8, 9]]           [9, 6, 3]]

first row 1 2 3  ->  last column 1 2 3, reading down
```

The coordinate rule, for an `rows × cols` matrix:

```text
(r, c)  ->  (c, rows-1-r)
```

Read it as *"the new row is the old column; the new column counts backwards from the old row."* The `rows-1-r` is the reversal — and that reversal is the only thing separating this from a plain transpose.

Which gives the idiom that matters:

```text
rotate 90° CW  =  transpose  +  reverse each row
```

Two practical consequences:

- **The shape swaps.** A `2×3` becomes a `3×2`. So a non-square matrix cannot be rotated in place — there is nowhere to put the cells.
    
- **"90°" is ambiguous** until you say clockwise or counter-clockwise. This lesson is clockwise; counter-clockwise is lesson 19 wearing a different name.
    

---

## Relationship to Cognitive Verb

```text
Turn
  ↓
Rotate 90°
```

Related verbs:

- Turn a quarter
- Spin clockwise
- Reorient
- Tip on its side
- Rotate right

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Rotate 90° CW|the whole thing|`[list(r) for r in zip(*m[::-1])]`|
|Same, spelled out|transpose then flip|`[row[::-1] for row in zip(*m)]`|
|Rotate 90° CCW|the other way|`[list(r) for r in zip(*m)][::-1]`|
|By coordinate|explicit rule|`out[c][rows-1-r] = m[r][c]`|
|In place|square only|transpose in place, then `row.reverse()`|
|In place, one pass|4-way cycle|rotate each ring's four cells|
|k turns|any multiple|`k % 4`, then apply|
|Shape after|new dimensions|`cols × rows`|
|Rotate coordinates|not the values|apply the rule to `(r, c)` pairs|

---

## Common Uses

- Image rotation
- Tetris and puzzle piece rotation
- Board game orientation
- Screen / device rotation
- Rotating a maze or level layout
- Matrix layout in printing
- Sprite transforms
- Rotating a heatmap for display

---

## Hidden Interview Problems

- Rotate Image (LeetCode 48, in place)
- Rotate a matrix by k × 90°
- Check if one matrix is a rotation of another
- Rotate a non-square matrix
- Rotate matrix layers / rings
- Determine the orientation of a shape
- Rotate a Tetris piece and test placement

---

## Recognition Clues

If you hear...

- "rotate 90 degrees..."
- "turn clockwise..."
- "the top row becomes the right column..."
- "rotate the image / board / piece..."
- "in place, no extra matrix..."

...think **Rotate 90°**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Coordinate rule|`(r, c) → (c, rows-1-r)`|
|Shape|`rows × cols → cols × rows`|
|Fixed points|The centre cell, if the matrix is odd-sized and square|
|Involution|No — order 4 (`R90` applied 4 times is the identity)|
|Inverse|Rotate 270° (lesson 19)|
|In place|Only for square matrices|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(rows × cols), or O(1) in place (square)|
|Common Domains|Images, games, UI, puzzles|

---

## Python Recipe Book

```python
# ============================================
# Two matrices

m = [[1, 2, 3],
     [4, 5, 6]]                 # 2 x 3

s = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]                 # 3 x 3

# ============================================
# The one idiom to remember
#
#   zip(*m[::-1])
#
# Reverse the ROW ORDER first, then transpose.
# The [::-1] is the whole difference from lesson 16.

def rot90(m):
    return [list(r) for r in zip(*m[::-1])]

rot90(s)
# =>
# [[7, 4, 1],
#  [8, 5, 2],
#  [9, 6, 3]]

rot90(m)
# =>
# [[4, 1],
#  [5, 2],
#  [6, 3]]

len(m), len(m[0])                   # => (2, 3)
len(rot90(m)), len(rot90(m)[0])     # => (3, 2)   shape swapped

# ============================================
# The same thing, in the other order
#
# transpose first, then reverse each row.
# Both spellings are correct; pick one and keep it.

def rot90_alt(m):
    return [list(r)[::-1] for r in zip(*m)]

rot90_alt(s) == rot90(s)            # => True

# reverse-then-transpose  ==  transpose-then-reverse-rows
# the flip just moves to the other side of the transpose

# ============================================
# Reading the two spellings
#
#   zip(*m[::-1])          flip vertical, then transpose
#   [r[::-1] for r in zip(*m)]  transpose, then flip horizontal

def transpose(m):  return [list(r) for r in zip(*m)]
def flip_h(m):     return [row[::-1] for row in m]
def flip_v(m):     return m[::-1]

rot90(s) == flip_h(transpose(s))    # => True
rot90(s) == transpose(flip_v(s))    # => True
#
# a rotation is ALWAYS a transpose plus one flip.
# Which flip, and on which side, picks the direction.

# ============================================
# Order 4 — four turns bring you home

rot90(rot90(rot90(rot90(s)))) == s  # => True

def rotate(m, k):
    k %= 4                          # 5 turns == 1 turn
    for _ in range(k):
        m = rot90(m)
    return m

rotate(s, 0) == s                   # => True
rotate(s, 4) == s                   # => True
rotate(s, 5) == rot90(s)            # => True
#
# ALWAYS take k % 4 first. Rotating 1000 times should
# cost four rotations at most, not a thousand.

# ============================================
# The coordinate rule, written out
#
# Useful when you must rotate something that is NOT a
# matrix — a list of points, a sprite's hitbox, a path.

def rot90_coords(m):
    rows, cols = len(m), len(m[0])
    out = [[None] * rows for _ in range(cols)]
    for r in range(rows):
        for c in range(cols):
            out[c][rows - 1 - r] = m[r][c]
    return out

rot90_coords(s) == rot90(s)         # => True

# and for bare points:
def turn(r, c, rows):
    return (c, rows - 1 - r)

turn(0, 0, 3)                       # => (0, 2)   top-left -> top-right
turn(0, 2, 3)                       # => (2, 2)   top-right -> bottom-right
turn(2, 2, 3)                       # => (2, 0)   bottom-right -> bottom-left
turn(2, 0, 3)                       # => (0, 0)   bottom-left -> top-left
#
# the four corners cycle — that IS the rotation

# ============================================
# In place — square only (LeetCode 48)
#
# Transpose in place, then reverse every row.
# Two O(1)-space passes.

def rot90_inplace(m):
    n = len(m)
    for r in range(n):
        for c in range(r + 1, n):           # upper triangle only
            m[r][c], m[c][r] = m[c][r], m[r][c]
    for row in m:
        row.reverse()
    return m

rot90_inplace([row[:] for row in s])
# =>
# [[7, 4, 1],
#  [8, 5, 2],
#  [9, 6, 3]]

# a non-square matrix CANNOT do this — the result has a
# different shape, so it needs a different-shaped list

# ============================================
# In place, one pass — the four-way ring cycle
#
# Each ring rotates as a unit: four cells swap in a cycle,
# and you walk the ring's top edge to drive them.

def rot90_layers(m):
    m = [row[:] for row in m]
    n = len(m)
    for lay in range(n // 2):
        last = n - 1 - lay
        for i in range(lay, last):
            off = i - lay
            top                = m[lay][i]
            m[lay][i]          = m[last - off][lay]     # left  -> top
            m[last - off][lay] = m[last][last - off]    # bottom-> left
            m[last][last - off] = m[i][last]            # right -> bottom
            m[i][last]         = top                    # top   -> right
    return m

rot90_layers(s) == rot90(s)         # => True

big = [[1,  2,  3,  4 ],
       [5,  6,  7,  8 ],
       [9,  10, 11, 12],
       [13, 14, 15, 16]]

rot90_layers(big)
# =>
# [[13, 9,  5, 1],
#  [14, 10, 6, 2],
#  [15, 11, 7, 3],
#  [16, 12, 8, 4]]

rot90_layers(big) == rot90(big)     # => True
#
# this is the version interviewers want to see; the
# transpose+reverse version is the one to write at work

# ============================================
# Is B a rotation of A?

def is_rotation(a, b):
    return any(rotate(a, k) == b for k in range(4))

is_rotation(s, rot90(s))            # => True
is_rotation(s, flip_h(s))           # => False
#
# a FLIP is not a rotation — see lesson 20. No amount of
# turning a shape produces its mirror image.

# ============================================
# Compare

# swap the axes                -> transpose (lesson 16)
transpose(m)

# swap the axes, then flip     -> this lesson
[list(r) for r in zip(*m[::-1])]

# two quarter turns            -> lesson 18
# three quarter turns          -> lesson 19
# just the flip, no transpose  -> lessons 20, 21
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|rotate 90° CW|`[list(r) for r in zip(*m[::-1])]`|
|the other spelling|`[list(r)[::-1] for r in zip(*m)]`|
|rotate 90° CCW|`[list(r) for r in zip(*m)][::-1]`|
|the rule|`(r, c) → (c, rows-1-r)`|
|the new shape|`cols × rows`|
|k rotations|`k % 4` first, always|
|in place (square)|transpose in place, then `row.reverse()`|
|the interview answer|four-way ring cycle, layer by layer|
|to undo it|rotate 270° (lesson 19)|

---

## Key Insight

**A rotation is a transpose plus a flip.** That is the whole lesson:

```text
rot90 CW  =  transpose  then  reverse each row
          =  reverse the row order  then  transpose
```

Both spellings produce the same matrix, because moving the flip to the other side of the transpose changes which axis it acts on. Once you see that, you do not memorise four rotation formulas — you memorise `zip(*m)` and decide where the `[::-1]` goes.

Three things to keep straight:

1. **Direction must be stated.** "Rotate 90°" is under-specified. `zip(*m[::-1])` is clockwise; `zip(*m)[::-1]` is counter-clockwise. Getting this backwards is the most common bug in this lesson, and it is invisible on a symmetric test matrix — always test with something asymmetric like `[[1,2,3],[4,5,6]]`.
    
2. **Shape swaps, so in place needs a square.** `rows × cols` becomes `cols × rows`. The elegant transpose-then-reverse trick only exists for square matrices; a non-square rotation must allocate.
    
3. **Rotations have order 4.** Take `k % 4` before doing any work. And rotations alone never produce a mirror image — reflection is a genuinely different operation (lesson 20).
    

---

## Rotate 90° vs Transpose

|Operation|Rule|Top row becomes|
|---|---|---|
|**Transpose**|`(r,c) → (c,r)`|the left column, **in order**|
|**Rotate 90° CW**|`(r,c) → (c, rows-1-r)`|the right column, **in order**|

```text
   original      transpose      rotate 90 CW
   1 2 3          1 4 7           7 4 1
   4 5 6          2 5 8           8 5 2
   7 8 9          3 6 9           9 6 3
```

> **Mental shift:** transpose is a **reflection** — hold the diagonal fixed and fold. Rotation is a **turn** — nothing is held fixed except the centre. They differ by exactly one flip, which is why the code differs by exactly one `[::-1]`.
