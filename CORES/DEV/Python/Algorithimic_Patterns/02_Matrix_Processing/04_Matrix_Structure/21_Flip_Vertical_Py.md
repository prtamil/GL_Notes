# 21. Flip Vertical

## Mental Model

Hold a mirror along the **horizontal centre line**. Top and bottom swap. Left and right stay where they are.

```text
[[1, 2, 3],          [[7, 8, 9],
 [4, 5, 6],     ->    [4, 5, 6],
 [7, 8, 9]]           [1, 2, 3]]

   the row ORDER is reversed; each row is untouched
```

The coordinate rule:

```text
(r, c)  ->  (rows-1-r, c)
```

Only the row index changes, which makes this the **cheapest operation in the whole section**:

```python
m[::-1]
```

One slice on the outer list. Lesson 20 had to reverse every row; this reverses the list *of* rows. No inner loop at all.

That cheapness comes with the sharpest trap in these eight lessons: **`m[::-1]` copies the outer list but shares the row objects.** The flipped matrix and the original point at the *same* rows. Mutate a row through one and you have mutated the other.

The other reason this operation matters far more often than its simplicity suggests: **screen coordinates run top-down, mathematical coordinates run bottom-up.** Almost every image format, plotting library and graphics API disagrees with some other one about which way `y` points, and a vertical flip is the fix.

---

## Relationship to Cognitive Verb

```text
Mirror
   ↓
Flip Vertical
```

Related verbs:

- Mirror top-bottom
- Reflect across the horizontal axis
- Reverse the row order
- Turn it over
- Invert the y-axis

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Flip vertical|the whole thing|`m[::-1]`|
|Safe copy|no shared rows|`[row[:] for row in m[::-1]]`|
|In place|no copy|`m.reverse()`|
|By coordinate|explicit rule|`out[rows-1-r][c] = m[r][c]`|
|Lazy|no new list|`reversed(m)`|
|Symmetry test|already mirrored?|`m == m[::-1]`|
|Compose with transpose|becomes a rotation|`transpose(m)[::-1]` is `rot270`|
|y-axis conversion|screen ↔ maths|`rows - 1 - r`|
|Bottom-up iteration|walk upward|`for row in reversed(m)`|

---

## Common Uses

- Screen-space vs world-space coordinate conversion
- BMP and other bottom-up image formats
- Plotting a matrix as a chart (origin at the bottom)
- Flipping a game board for the opposing player
- Vertical mirroring of sprites
- Reversing a stack of layers
- Heightmap and terrain orientation
- Reading a grid from the bottom up

---

## Hidden Interview Problems

- Reverse the rows of a matrix
- Check for horizontal-axis symmetry
- Convert between coordinate systems
- Rotate a matrix (as one half of the job)
- Print a matrix bottom-up
- Detect a matrix that reads the same upside down
- Flip a binary image vertically

---

## Recognition Clues

If you hear...

- "flip top to bottom..."
- "reverse the rows..."
- "origin at the bottom-left..."
- "y-axis points the other way..."
- "upside down, but not mirrored..."
- "the board from the other player's side..."

...think **Flip Vertical**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Coordinate rule|`(r, c) → (rows-1-r, c)`|
|Shape|**Preserved**|
|Axis|The horizontal centre line|
|Fixed points|The centre row, if `rows` is odd|
|Involution|**Yes** — its own inverse|
|Orientation|**Reversed** — a reflection, not a rotation|
|In place|Yes, for any shape|
|Time Complexity|O(rows) — the rows themselves are not touched|
|Space Complexity|O(rows) for the new outer list, O(1) in place|
|Common Domains|Graphics, plotting, games, image formats|

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
def rot90(m):     return [list(r) for r in zip(*m[::-1])]
def rot180(m):    return [row[::-1] for row in m[::-1]]
def rot270(m):    return [list(r) for r in zip(*m)][::-1]

# ============================================
# The one idiom to remember
#
# One slice. The cheapest operation in the section.

def flip_v(m):
    return m[::-1]

flip_v(s)
# =>
# [[7, 8, 9],
#  [4, 5, 6],
#  [1, 2, 3]]

flip_v(m)
# =>
# [[4, 5, 6],
#  [1, 2, 3]]

len(m), len(m[0])                       # => (2, 3)
len(flip_v(m)), len(flip_v(m)[0])       # => (2, 3)   shape preserved

flip_v(flip_v(m)) == m                  # => True     its own inverse

# ============================================
# THE TRAP: m[::-1] shares the row objects
#
# The outer list is new. The rows inside it are the
# SAME list objects as in the original.

orig = [[1, 2],
        [3, 4]]

flipped = orig[::-1]                    # => [[3, 4], [1, 2]]

flipped[0][0] = 99                      # write through the flipped view

orig
# =>
# [[1, 2],
#  [99, 4]]      <-- the ORIGINAL changed

orig[1] is flipped[0]                   # => True   same object

# compare with lesson 20, where [row[::-1] for row in m]
# builds brand-new rows and has no such problem.

# ============================================
# The fix: copy the rows too

def flip_v_copy(m):
    return [row[:] for row in m[::-1]]

deep = flip_v_copy(orig)
deep[0] is orig[1]                      # => False   independent

# rule of thumb for this whole section:
#   m[::-1]                       shallow — shares rows
#   [row[::-1] for row in m]      deep    — new rows
#   [row[:] for row in m[::-1]]   deep    — new rows, explicitly

# ============================================
# In place

def flip_v_inplace(m):
    m.reverse()                         # mutates, returns None
    return m

flip_v_inplace([row[:] for row in s])
# =>
# [[7, 8, 9],
#  [4, 5, 6],
#  [1, 2, 3]]

# and the lazy form, when you only want to iterate
for row in reversed(s):
    pass                                # no list built at all

# ============================================
# Contrast with lesson 20 — one bracket apart

flip_v(s)                               # m[::-1]                    rows
# => [[7, 8, 9], [4, 5, 6], [1, 2, 3]]

flip_h(s)                               # [row[::-1] for row in m]   cells
# => [[3, 2, 1], [6, 5, 4], [9, 8, 7]]
#
# vertical  flip: reverse the LIST OF rows
# horizontal flip: reverse EACH row
#
# and both together is the half turn:
flip_v(flip_h(s)) == rot180(s)          # => True

# ============================================
# Composed with transpose, it is a rotation

flip_v(transpose(s)) == rot270(s)       # => True
transpose(flip_v(s)) == rot90(s)        # => True
#
# opposite order, opposite turn — they do not commute

flip_v(transpose(s)) == transpose(flip_v(s))    # => False

# ============================================
# The reason you will actually use this
#
# Screen coordinates count rows DOWNWARD from the top.
# Maths, plots and many image formats count UPWARD from
# the bottom. Converting between them is a vertical flip.

def to_screen(r, rows):
    return rows - 1 - r

heights = [[0, 0, 0],
           [0, 1, 0],
           [1, 1, 1]]                   # a hill, drawn screen-style

flip_v(heights)                         # the same hill, maths-style
# =>
# [[1, 1, 1],
#  [0, 1, 0],
#  [0, 0, 0]]
#
# if a plot comes out upside down, this is the fix —
# and it is a flip, NOT a rotation. Rotating would
# also mirror it left-to-right.

# ============================================
# Symmetry test

def flip_v_symmetric(m):
    return m == flip_v(m)

flip_v_symmetric(s)                             # => False
flip_v_symmetric([[1, 2], [3, 4], [1, 2]])      # => True
#
# the row list is a palindrome  <=>  symmetric about
# the horizontal axis

# ============================================
# Compare — the section's whole vocabulary

transpose(m)                # (r,c) -> (c,r)                diagonal mirror
flip_h(m)                   # (r,c) -> (r, cols-1-c)        vertical mirror
flip_v(m)                   # (r,c) -> (rows-1-r, c)        horizontal mirror
rot90(m)                    # (r,c) -> (c, rows-1-r)
rot180(m)                   # (r,c) -> (rows-1-r, cols-1-c)
rot270(m)                   # (r,c) -> (cols-1-c, r)
#
# six of the eight symmetries of a square. The other two
# are the identity and the anti-transpose (lesson 16).
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|flip vertical|`m[::-1]`|
|**safely**|`[row[:] for row in m[::-1]]` — shares rows otherwise|
|in place|`m.reverse()`|
|the rule|`(r, c) → (rows-1-r, c)`|
|to iterate bottom-up|`for row in reversed(m)`|
|screen ↔ maths y|`rows - 1 - r`|
|is it top-bottom symmetric|`m == m[::-1]`|
|the contrast with lesson 20|`m[::-1]` vs `[row[::-1] for row in m]`|

---

## Key Insight

**Flip vertical is `m[::-1]` — and that is both why it is the cheapest operation here and why it is the most dangerous.**

It touches only the outer list. The rows are never read, never copied, never rebuilt; the new list holds **the same row objects**. `flipped[0][0] = 99` writes straight through into the original. Lesson 20's `[row[::-1] for row in m]` constructs new rows and has no such hazard, which makes the asymmetry easy to forget: *the horizontal flip is safe by accident, the vertical flip is unsafe by default.* When the result must be independent, say so: `[row[:] for row in m[::-1]]`.

Beyond that it is the mirror twin of lesson 20 in every respect — shape preserved, its own inverse, in place for any shape, orientation-reversing — and it slots into the same compositions:

```text
flip_v ∘ flip_h    == rot180        (perpendicular mirrors commute)
flip_v ∘ transpose == rot270        (order matters)
transpose ∘ flip_v == rot90         (…the other order, the other turn)
```

And the practical payoff: **row 0 is the top of the screen and the bottom of a graph.** Whenever a rendered matrix comes out upside down, the fix is a vertical flip — not a rotation, which would mirror it sideways as well.

---

## The Eight Symmetries of a Square (D4)

Every operation in lessons 16–21, plus the identity, forms a closed group of exactly eight. Nothing else is reachable.

|Name|Idiom|Kind|Own inverse?|
|---|---|---|---|
|`I` identity|`m`|—|yes|
|`R90`|`[*zip(*m[::-1])]`|rotation|no (→ `R270`)|
|`R180`|`[row[::-1] for row in m[::-1]]`|rotation|**yes**|
|`R270`|`[*zip(*m)][::-1]`|rotation|no (→ `R90`)|
|`FH`|`[row[::-1] for row in m]`|reflection|**yes**|
|`FV`|`m[::-1]`|reflection|**yes**|
|`T` transpose|`[*zip(*m)]`|reflection|**yes**|
|`AT` anti-transpose|`[*zip(*[r[::-1] for r in m[::-1]])]`|reflection|**yes**|

Applied to `[[1,2,3],[4,5,6],[7,8,9]]`, all eight give different results:

```text
I     1 2 3 4 5 6 7 8 9         FH    3 2 1 6 5 4 9 8 7
R90   7 4 1 8 5 2 9 6 3         FV    7 8 9 4 5 6 1 2 3
R180  9 8 7 6 5 4 3 2 1         T     1 4 7 2 5 8 3 6 9
R270  3 6 9 2 5 8 1 4 7         AT    9 6 3 8 5 2 7 4 1
```

Composition table — **apply the row's operation first, then the column's**:

```text
          I   R90  R180  R270    FH    FV     T    AT
  I       I   R90  R180  R270    FH    FV     T    AT
  R90   R90  R180  R270     I     T    AT    FV    FH
  R180  R180  R270    I    R90    FV    FH    AT     T
  R270  R270    I   R90   R180    AT     T    FH    FV
  FH     FH    AT    FV      T     I  R180  R270   R90
  FV     FV     T    FH     AT  R180     I   R90  R270
  T       T    FH    AT     FV   R90  R270     I  R180
  AT     AT    FV     T     FH  R270   R90  R180     I
```

Three things to read off it:

- **Reflection ∘ reflection = rotation.** The bottom-right quadrant is entirely rotations.
    
- **Rotation ∘ reflection = reflection.** Handedness flips exactly once, so the result is still a mirror image.
    
- **The table isn't symmetric.** `T ∘ R90` and `R90 ∘ T` land in different cells. Order of composition matters, and that's where most rotate/flip bugs come from.
    

> **Mental shift:** lessons 16–21 aren't six unrelated tricks. They're six of the eight elements of one small closed group, built from just two operations: `zip(*m)` and a `[::-1]`. Learn where the `[::-1]` goes and you've got all eight.
