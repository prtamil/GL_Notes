# 18. Rotate 180°

## Mental Model

Turn the matrix upside down. Every cell moves to the position diagonally opposite through the **centre**.

```text
[[1, 2, 3],          [[9, 8, 7],
 [4, 5, 6],     ->    [6, 5, 4],
 [7, 8, 9]]           [3, 2, 1]]
```

The coordinate rule:

```text
(r, c)  ->  (rows-1-r, cols-1-c)
```

**Both** indices reverse. That symmetry is what makes this the easiest operation in the section — and the one with the most alternative spellings:

```text
rotate 180  =  reverse the rows, and reverse each row
            =  flip vertical  then  flip horizontal
            =  flip horizontal then flip vertical
            =  rotate 90  twice
            =  reverse the FLATTENED matrix
```

That last one is the interesting one. Because both axes reverse, rotating 180° in row-major order is simply reading every cell backwards. No other operation in this section has that property.

Two things that set it apart from lessons 17 and 19:

- **The shape is preserved**, even for non-square matrices. A `2×3` stays a `2×3`. So in-place works for *any* matrix, not just squares.
    
- **It is its own inverse.** Do it twice and you are back where you started.
    

---

## Relationship to Cognitive Verb

```text
Invert
   ↓
Rotate 180°
```

Related verbs:

- Turn upside down
- Reverse both ways
- Point-reflect
- Half turn
- Flip end over end

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Rotate 180°|the whole thing|`[row[::-1] for row in m[::-1]]`|
|As two flips|explicit|`flip_h(flip_v(m))`|
|As two rotations|explicit|`rot90(rot90(m))`|
|Via flatten|the linear view|reverse the flat list, then reshape|
|By coordinate|explicit rule|`out[rows-1-r][cols-1-c] = m[r][c]`|
|In place|any shape|reverse the outer list, reverse each row|
|Half-way swap|one pass|swap cell `i` with cell `n-1-i` in the flat order|
|Test invariance|180°-symmetric?|`m == rot180(m)`|

---

## Common Uses

- Displaying an image upside down
- Reversing a printed page or receipt
- Rotating a game board for the second player
- Undoing an accidental 180° scan
- Point symmetry checks
- Playing card / domino orientation
- Reversing a path or route grid

---

## Hidden Interview Problems

- Rotate a matrix by 180°
- Check if a matrix is symmetric under a half turn
- Rotate by k × 90° (the `k == 2` case)
- Reverse a matrix in place
- Detect a centrally symmetric pattern
- Strobogrammatic grids (readable upside down)

---

## Recognition Clues

If you hear...

- "upside down..."
- "rotate 180..."
- "half turn..."
- "reverse both directions..."
- "the same viewed from the other side of the table..."

...think **Rotate 180°**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Coordinate rule|`(r, c) → (rows-1-r, cols-1-c)`|
|Shape|**Preserved** — `rows × cols → rows × cols`|
|Fixed points|The centre cell, if both dimensions are odd|
|Involution|**Yes** — its own inverse|
|In place|Yes, for **any** shape|
|Linear order|Exactly the reverse of the flattened matrix|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) in place|
|Common Domains|Images, games, display, symmetry|

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
# Reverse the rows, and reverse each row.
# Two [::-1]s, one on each axis.

def rot180(m):
    return [row[::-1] for row in m[::-1]]

rot180(s)
# =>
# [[9, 8, 7],
#  [6, 5, 4],
#  [3, 2, 1]]

rot180(m)
# =>
# [[6, 5, 4],
#  [3, 2, 1]]

# ============================================
# Shape is PRESERVED — unlike 90 and 270

len(m), len(m[0])                       # => (2, 3)
len(rot180(m)), len(rot180(m)[0])       # => (2, 3)   unchanged
#
# both axes reverse, neither swaps. That is why this
# one works in place on any matrix.

# ============================================
# Its own inverse

rot180(rot180(m)) == m                  # => True

# ============================================
# Every equivalent spelling

def transpose(m): return [list(r) for r in zip(*m)]
def flip_h(m):    return [row[::-1] for row in m]
def flip_v(m):    return m[::-1]
def rot90(m):     return [list(r) for r in zip(*m[::-1])]

rot180(s) == rot90(rot90(s))            # => True   two quarter turns
rot180(m) == flip_h(flip_v(m))          # => True   both mirrors
rot180(m) == flip_v(flip_h(m))          # => True   ...in either order
#
# note flip_h and flip_v COMMUTE. Most pairs in this
# section do not — flip_h then transpose is a different
# matrix from transpose then flip_h.

# ============================================
# The property no other operation has
#
# Because both axes reverse, a 180 rotation is just the
# flattened matrix, backwards.

flat = lambda m: [x for row in m for x in row]

flat(m)                                 # => [1, 2, 3, 4, 5, 6]
flat(rot180(m))                         # => [6, 5, 4, 3, 2, 1]

flat(rot180(m)) == flat(m)[::-1]        # => True

# so you can rotate by flatten, reverse, reshape:
def rot180_via_flat(m):
    cols = len(m[0])
    xs = flat(m)[::-1]
    return [xs[i:i+cols] for i in range(0, len(xs), cols)]

rot180_via_flat(m) == rot180(m)         # => True
#
# lessons 22 and 23 make this the natural way to say it.
# Try the same trick for rotate 90 and it fails — 90
# does NOT preserve a simple linear relationship.

# ============================================
# In place — works for any shape
#
# Reverse the outer list, then reverse each row.
# O(1) extra space, no square requirement.

def rot180_inplace(m):
    m.reverse()                         # row order
    for row in m:
        row.reverse()                   # each row
    return m

rot180_inplace([row[:] for row in m])
# =>
# [[6, 5, 4],
#  [3, 2, 1]]

# ============================================
# One-pass version — swap opposite cells
#
# Walk only the first HALF of the cells. Walking all of
# them swaps every pair twice and undoes the work — the
# same trap as the in-place transpose in lesson 16.

def rot180_swap(m):
    m = [row[:] for row in m]
    rows, cols = len(m), len(m[0])
    n = rows * cols
    for i in range(n // 2):
        r1, c1 = divmod(i, cols)
        r2, c2 = divmod(n - 1 - i, cols)
        m[r1][c1], m[r2][c2] = m[r2][c2], m[r1][c1]
    return m

rot180_swap(s) == rot180(s)             # => True
rot180_swap(m) == rot180(m)             # => True
#
# divmod(i, cols) is the flat-index-to-(r,c) conversion
# from lesson 23, arriving early

# ============================================
# The centre never moves

rot180(s)[1][1]                         # => 5
s[1][1]                                 # => 5
#
# a matrix with odd rows AND odd cols has exactly one
# fixed point: the centre. Even dimensions have none.

# ============================================
# 180-degree symmetry test

def centrally_symmetric(m):
    return m == rot180(m)

centrally_symmetric(s)                          # => False
centrally_symmetric([[1, 2], [2, 1]])           # => True
centrally_symmetric([[1, 2, 1], [3, 9, 3]])     # => False

# ============================================
# Compare

# one quarter turn      -> lesson 17    shape swaps
rot90(m)

# TWO quarter turns     -> this lesson  shape preserved
rot180(m)

# three quarter turns   -> lesson 19    shape swaps
rot90(rot90(rot90(m)))

# one mirror only       -> lessons 20, 21
flip_h(m)
flip_v(m)

# and the identity that ties them:
rot180(m) == flip_h(flip_v(m))          # => True
#
# 180 is the one rotation that is also a pair of flips
# with NO transpose involved. That is why it preserves
# shape and the others do not.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|rotate 180°|`[row[::-1] for row in m[::-1]]`|
|the rule|`(r, c) → (rows-1-r, cols-1-c)`|
|the shape|unchanged — this is the safe rotation|
|in place, any shape|`m.reverse()` then `row.reverse()` each|
|via the flat list|reverse it, then reshape|
|as two flips|`flip_h(flip_v(m))` — they commute|
|to undo it|do it again|
|the fixed point|the centre, when both dims are odd|

---

## Key Insight

**Rotate 180° is the only rotation that reverses both axes without swapping them** — and that single fact explains everything else about it:

- **Shape is preserved**, so it works in place on any matrix, square or not.
    
- **It is an involution**, so it is its own undo.
    
- **It is exactly the reversed flat list**, because reversing both axes in row-major order *is* reading backwards. `flat(rot180(m)) == flat(m)[::-1]` — no other operation in this section has such a clean linear form.
    
- **It is two flips with no transpose**, `flip_h ∘ flip_v`, and those two commute. Rotations by 90° and 270° need a transpose, which is precisely why *their* shape swaps.
    

The trap, shared with the in-place transpose of lesson 16: when swapping opposite cells, walk only **half** the cells. Swapping every pair twice returns the original, and the bug reads as "my function did nothing."

---

## The Rotation Family So Far

|Turn|Rule|Shape|Own inverse?|
|---|---|---|---|
|**90° CW**|`(r,c) → (c, rows-1-r)`|swaps|no — undone by 270°|
|**180°**|`(r,c) → (rows-1-r, cols-1-c)`|**preserved**|**yes**|
|**270° CW**|`(r,c) → (cols-1-c, r)`|swaps|no — undone by 90°|

```text
       R90        R90        R90        R90
  I  ──────► R90 ──────► R180 ──────► R270 ──────► I
                          ▲
                   the only self-inverse
                   the only shape-preserving
```

> **Mental shift:** 90° and 270° are *turns* — they tip the matrix onto its side and the dimensions trade places. 180° is a *point reflection* — nothing tips, every cell just walks through the centre to the far side. That is why it behaves more like the flips of lessons 20 and 21 than like its fellow rotations.
