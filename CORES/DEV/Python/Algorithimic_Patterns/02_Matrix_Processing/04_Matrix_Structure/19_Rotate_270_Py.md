# 19. Rotate 270°

## Mental Model

Three quarter turns clockwise, which is the same as one quarter turn **counter-clockwise**. The **top row becomes the left column, reversed**.

```text
[[1, 2, 3],          [[3, 6, 9],
 [4, 5, 6],     ->    [2, 5, 8],
 [7, 8, 9]]           [1, 4, 7]]
```

The coordinate rule:

```text
(r, c)  ->  (cols-1-c, r)
```

Put it next to lesson 17 and the symmetry jumps out:

```text
rotate  90° CW :  (r, c) -> (c, rows-1-r)     reverse the SECOND
rotate 270° CW :  (r, c) -> (cols-1-c, r)     reverse the FIRST
```

Same swap, opposite reversal. And so the idiom mirrors too:

```text
rotate  90° CW  =  transpose  +  reverse each row
rotate 270° CW  =  transpose  +  reverse the row order
```

The real content of this lesson is not a new algorithm — it is a **naming hazard**. "Rotate 270° clockwise", "rotate 90° counter-clockwise", "rotate left", and "rotate −90°" are four names for this one operation, and half the bugs in rotation code come from an API meaning one while the caller meant the other.

The other useful fact: **this is the inverse of lesson 17.** When you need to undo a 90° rotation, you need this.

---

## Relationship to Cognitive Verb

```text
Turn Back
    ↓
Rotate 270°
```

Related verbs:

- Turn counter-clockwise
- Rotate left
- Undo a quarter turn
- Three-quarter turn
- Anti-clockwise

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Rotate 270° CW|the whole thing|`[list(r) for r in zip(*m)][::-1]`|
|Same, other spelling|flip then transpose|`[list(r) for r in zip(*[row[::-1] for row in m])]`|
|As three 90s|explicit|`rot90(rot90(rot90(m)))`|
|As an inverse|undo a 90|`rot270(rot90(m)) == m`|
|By coordinate|explicit rule|`out[cols-1-c][r] = m[r][c]`|
|In place|square only|transpose in place, then reverse the row order|
|Normalise a turn count|any k|`k % 4`, where `3 == -1`|
|Negative angles|left turns|`rotate(m, -1) == rot270(m)`|

---

## Common Uses

- Undoing a 90° rotation
- Counter-clockwise image rotation
- Rotating UI or print layouts left
- Reverse of a device-orientation transform
- Restoring the original after a display rotation
- Counter-clockwise sprite and piece rotation
- Coordinate frame conversions

---

## Hidden Interview Problems

- Rotate an image counter-clockwise
- Rotate by k × 90° with negative k
- Undo a sequence of rotations
- Check if two matrices differ by a rotation
- Rotate matrix layers counter-clockwise
- Normalise an orientation to a canonical form

---

## Recognition Clues

If you hear...

- "counter-clockwise..." / "anti-clockwise..."
- "rotate left..."
- "rotate 270..."
- "rotate by −90..."
- "undo the rotation..."
- "the top row becomes the left column..."

...think **Rotate 270°**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Coordinate rule|`(r, c) → (cols-1-c, r)`|
|Shape|`rows × cols → cols × rows`|
|Aliases|90° CCW, rotate left, −90°|
|Fixed points|The centre cell, if odd-sized and square|
|Involution|No — order 4|
|Inverse|Rotate 90° (lesson 17)|
|In place|Only for square matrices|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(rows × cols), or O(1) in place (square)|
|Common Domains|Images, UI, games, coordinate frames|

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

def transpose(m): return [list(r) for r in zip(*m)]
def flip_h(m):    return [row[::-1] for row in m]
def flip_v(m):    return m[::-1]
def rot90(m):     return [list(r) for r in zip(*m[::-1])]

# ============================================
# The one idiom to remember
#
# Transpose, then reverse the ROW ORDER.
# Lesson 17 reversed each row; this reverses the list
# of rows. The [::-1] moved outside.

def rot270(m):
    return [list(r) for r in zip(*m)][::-1]

rot270(s)
# =>
# [[3, 6, 9],
#  [2, 5, 8],
#  [1, 4, 7]]

rot270(m)
# =>
# [[3, 6],
#  [2, 5],
#  [1, 4]]

len(m), len(m[0])                       # => (2, 3)
len(rot270(m)), len(rot270(m)[0])       # => (3, 2)   shape swaps

# ============================================
# Where the [::-1] goes IS the direction
#
#   zip(*m[::-1])          ->  90  CW   flip inside, on rows
#   [ ... zip(*m)][::-1]   ->  270 CW   flip outside, on the result
#
# One character of placement separates the two
# directions. Write both down once and never guess.

rot90(s)
# => [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
rot270(s)
# => [[3, 6, 9], [2, 5, 8], [1, 4, 7]]

rot90(s) == rot270(s)                   # => False   (obviously — but
                                        #  on a symmetric test matrix
                                        #  it would be True. Always
                                        #  test with asymmetric data.)

# ============================================
# Every equivalent spelling

rot270(s) == rot90(rot90(rot90(s)))     # => True   three quarter turns
rot270(s) == flip_v(transpose(s))       # => True   transpose, flip rows
rot270(s) == transpose(flip_h(s))       # => True   flip cols, transpose

# ============================================
# It is the INVERSE of lesson 17

rot270(rot90(m)) == m                   # => True
rot90(rot270(m)) == m                   # => True
#
# this is the practical reason the lesson exists:
# when something rotated your data 90 degrees, this
# is what puts it back.

# ============================================
# Turn counting — negative k is the natural spelling

def rotate(m, k):
    k %= 4                              # -1 % 4 == 3 in Python
    for _ in range(k):
        m = rot90(m)
    return m

rotate(s, 3) == rot270(s)               # => True
rotate(s, -1) == rot270(s)              # => True   left turn
rotate(s, -5) == rot270(s)              # => True
rotate(s, 0) == s                       # => True

(-1) % 4                                # => 3
#
# Python's modulo returns a NON-NEGATIVE result for a
# positive divisor, so k % 4 handles left turns for
# free. In C or Java, -1 % 4 is -1 and range() would
# do nothing — a real cross-language gotcha.

# ============================================
# The coordinate rule

def rot270_coords(m):
    rows, cols = len(m), len(m[0])
    out = [[None] * rows for _ in range(cols)]
    for r in range(rows):
        for c in range(cols):
            out[cols - 1 - c][r] = m[r][c]
    return out

rot270_coords(s) == rot270(s)           # => True
rot270_coords(m) == rot270(m)           # => True

# for bare points:
def turn_left(r, c, cols):
    return (cols - 1 - c, r)

turn_left(0, 0, 3)                      # => (2, 0)   top-left -> bottom-left
turn_left(2, 0, 3)                      # => (2, 2)   bottom-left -> bottom-right
turn_left(2, 2, 3)                      # => (0, 2)   bottom-right -> top-right
turn_left(0, 2, 3)                      # => (0, 0)   top-right -> top-left
#
# the corners cycle the OTHER way round from lesson 17

# ============================================
# In place — square only

def rot270_inplace(m):
    n = len(m)
    for r in range(n):
        for c in range(r + 1, n):       # upper triangle
            m[r][c], m[c][r] = m[c][r], m[r][c]
    m.reverse()                         # row ORDER, not each row
    return m

rot270_inplace([row[:] for row in s])
# =>
# [[3, 6, 9],
#  [2, 5, 8],
#  [1, 4, 7]]
#
# lesson 17 did `for row in m: row.reverse()`.
# This does `m.reverse()`. One word apart, opposite turns.

# ============================================
# Canonical orientation — normalise before comparing
#
# When orientation shouldn't matter (puzzle pieces,
# tile matching), reduce to the smallest rotation.

def canonical(m):
    return min(tuple(map(tuple, rotate(m, k))) for k in range(4))

canonical(s) == canonical(rot90(s))     # => True
canonical(s) == canonical(rot270(s))    # => True
canonical(s) == canonical(rotate(s, 2)) # => True

canonical(s)                            # => ((1, 2, 3), (4, 5, 6), (7, 8, 9))
#
# all four rotations of a piece now hash to one key —
# the standard trick for de-duplicating rotated shapes

# ============================================
# Compare

# quarter turn right   -> lesson 17
[list(r) for r in zip(*m[::-1])]

# half turn            -> lesson 18
[row[::-1] for row in m[::-1]]

# quarter turn left    -> this lesson
[list(r) for r in zip(*m)][::-1]

# no turn, just mirror -> lessons 20, 21
[row[::-1] for row in m]                # flip horizontal
m[::-1]                                 # flip vertical

# all four rotations, side by side:
#   rot0    = m
#   rot90   = zip(*m[::-1])
#   rot180  = [row[::-1] for row in m[::-1]]
#   rot270  = [*zip(*m)][::-1]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|rotate 270° CW (= 90° CCW)|`[list(r) for r in zip(*m)][::-1]`|
|to remember the difference|**90°: flip inside** `zip(*m[::-1])`; **270°: flip outside** `[...][::-1]`|
|the rule|`(r, c) → (cols-1-c, r)`|
|to undo a 90° rotation|apply this one|
|a left turn by count|`rotate(m, -1)` — `k % 4` handles it|
|in place (square)|transpose in place, then `m.reverse()`|
|the 90° in-place contrast|`row.reverse()` for each row, not `m.reverse()`|
|orientation-free comparison|`min` over all four rotations|

---

## Key Insight

**Rotate 270° is rotate 90° with the flip on the other side of the transpose.**

```text
rot90   =  transpose  then  reverse each row      ->  [row[::-1] for row in T]
rot270  =  transpose  then  reverse the row list  ->  T[::-1]
```

Everything else follows: same swap of axes, so the shape swaps identically; opposite reversal, so the direction inverts; and applying one after the other returns the original, which is the whole practical point — **this is the undo button for lesson 17.**

Two things actually worth guarding against:

1. **The naming.** 270° CW, 90° CCW, rotate left and −90° are the same operation. When you write or call a rotation API, state the convention in the name or the docstring. And **test with an asymmetric matrix** — `[[1,2,3],[4,5,6]]`, not a symmetric one — because a direction bug is completely invisible on symmetric data.
    
2. **The one-word difference in place.** Both in-place rotations start with the same triangle transpose. Then 90° does `row.reverse()` for every row; 270° does `m.reverse()` once. Swap those and you get the other rotation, silently.
    

Python gives you one small gift here: `-1 % 4 == 3`, so `k % 4` normalises left turns without a special case. That is not true in C, Java or JavaScript, where `-1 % 4` is `-1`.

---

## The Four Rotations

|Turn|Idiom|Shape|Inverse|
|---|---|---|---|
|**0°**|`m`|—|itself|
|**90° CW**|`zip(*m[::-1])`|swaps|270°|
|**180°**|`[row[::-1] for row in m[::-1]]`|preserved|itself|
|**270° CW**|`[*zip(*m)][::-1]`|swaps|90°|

```text
           R90
    I  ─────────►  R90
    ▲                │
    │ R90            │ R90
    │                ▼
  R270  ◄─────────  R180
           R90

  going clockwise round this cycle is rot90;
  going counter-clockwise is rot270
```

> **Mental shift:** you don't have four rotation algorithms to learn. You have `zip(*m)` and one decision about where the `[::-1]` goes. Inside, on the rows, turns right. Outside, on the result, turns left. One on each axis with no transpose gives you the half turn.
