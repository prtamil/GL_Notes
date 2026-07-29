# 20. Flip Horizontal

## Mental Model

Hold a mirror along the **vertical centre line** and look at the reflection. Left and right swap; top and bottom stay put.

```text
[[1, 2, 3],          [[3, 2, 1],
 [4, 5, 6],     ->    [6, 5, 4],
 [7, 8, 9]]           [9, 8, 7]]

   each ROW is reversed; the row ORDER is untouched
```

The coordinate rule:

```text
(r, c)  ->  (r, cols-1-c)
```

Only the column index changes. In Python that is exactly one slice, applied per row:

```python
[row[::-1] for row in m]
```

The reason this deserves its own lesson, rather than being filed as "half of a 180° rotation", is that **a reflection is not a rotation.** No sequence of turns will ever produce a mirror image. Rotations preserve *handedness*; reflections reverse it. A left glove stays a left glove however you turn it — mirror it and it becomes a right glove.

That distinction is why `is_rotation(m, flip_h(m))` returns `False` in lesson 17, why the eight symmetries of a square split into four rotations and four reflections, and why "flip" and "rotate" are separate buttons in every image editor.

**Naming warning.** "Horizontal flip" means *mirrored horizontally* — the axis is vertical. Some libraries call this `fliplr` (flip left-right) or `mirror`. Others use "horizontal" to mean the axis, giving the opposite operation. Always check which one you have.

---

## Relationship to Cognitive Verb

```text
Mirror
   ↓
Flip Horizontal
```

Related verbs:

- Mirror left-right
- Reflect across the vertical axis
- Reverse each row
- Face the other way

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Flip horizontal|the whole thing|`[row[::-1] for row in m]`|
|In place|no copy|`for row in m: row.reverse()`|
|By coordinate|explicit rule|`out[r][cols-1-c] = m[r][c]`|
|One row|a single line|`row[::-1]`|
|Reversed iterator|lazy, no copy|`reversed(row)`|
|Palindrome test|already mirrored?|`m == flip_h(m)`|
|Compose with transpose|becomes a rotation|`flip_h(transpose(m))` is `rot90`|
|Flip a column index|coordinate only|`cols - 1 - c`|
|Strings / rows of text|same idiom|`line[::-1]`|

---

## Common Uses

- Mirroring an image
- Sprite facing direction in games
- Right-to-left language layout
- Selfie / front-camera correction
- Symmetry detection
- Reflecting a maze or level
- Chirality checks in shape matching
- Mirror-image data augmentation for training

---

## Hidden Interview Problems

- Flip an image horizontally (LeetCode 832, then invert)
- Check if a matrix is a mirror image of another
- Check for vertical-axis symmetry
- Reverse each row in place
- Flip and invert an image
- Determine if two shapes are congruent vs mirror-congruent
- Palindromic rows

---

## Recognition Clues

If you hear...

- "mirror image..."
- "flip left to right..."
- "reverse each row..."
- "facing the other direction..."
- "reflect across the vertical axis..."
- "is it symmetric left-to-right..."

...think **Flip Horizontal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Coordinate rule|`(r, c) → (r, cols-1-c)`|
|Shape|**Preserved**|
|Axis|The vertical centre line|
|Fixed points|The centre column, if `cols` is odd|
|Involution|**Yes** — its own inverse|
|Orientation|**Reversed** — this is a reflection, not a rotation|
|In place|Yes, for any shape|
|Time Complexity|O(rows × cols)|
|Space Complexity|O(1) in place|
|Common Domains|Images, games, symmetry, text layout|

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
def rot90(m):     return [list(r) for r in zip(*m[::-1])]
def rot180(m):    return [row[::-1] for row in m[::-1]]
def rot270(m):    return [list(r) for r in zip(*m)][::-1]
def flip_v(m):    return m[::-1]

# ============================================
# The one idiom to remember
#
# Reverse every row. Nothing else.

def flip_h(m):
    return [row[::-1] for row in m]

flip_h(s)
# =>
# [[3, 2, 1],
#  [6, 5, 4],
#  [9, 8, 7]]

flip_h(m)
# =>
# [[3, 2, 1],
#  [6, 5, 4]]

len(m), len(m[0])                       # => (2, 3)
len(flip_h(m)), len(flip_h(m)[0])       # => (2, 3)   shape preserved

# ============================================
# Its own inverse

flip_h(flip_h(m)) == m                  # => True

# ============================================
# In place — any shape, O(1) extra space

def flip_h_inplace(m):
    for row in m:
        row.reverse()                   # list.reverse() mutates
    return m

flip_h_inplace([row[:] for row in s])
# =>
# [[3, 2, 1],
#  [6, 5, 4],
#  [9, 8, 7]]

# note the three ways to reverse a row, and what each returns:
row = [1, 2, 3]
row[::-1]                               # => [3, 2, 1]   new list
list(reversed(row))                     # => [3, 2, 1]   new list, lazy until list()
row.reverse()                           # => None        MUTATES, returns nothing
row                                     # => [3, 2, 1]
#
# `m = [row.reverse() for row in m]` gives you a list of
# Nones. That is the classic slip here.

# ============================================
# It is NOT a rotation
#
# Reflections reverse handedness; rotations do not.
# No number of turns produces a mirror image.

def rotate(m, k):
    k %= 4
    for _ in range(k):
        m = rot90(m)
    return m

any(rotate(s, k) == flip_h(s) for k in range(4))     # => False
#
# this is the mathematical content of the lesson.
# Rotations and reflections are genuinely different
# kinds of transformation, and a "rotate by k" API can
# never express a flip.

# ============================================
# But a reflection PLUS a transpose is a rotation

flip_h(transpose(s)) == rot90(s)        # => True
transpose(flip_h(s)) == rot270(s)       # => True
#
# read carefully: same two operations, opposite order,
# opposite rotation. These do NOT commute.

flip_h(transpose(s)) == transpose(flip_h(s))    # => False

# ============================================
# And two reflections make a rotation

flip_h(flip_v(m)) == rot180(m)          # => True
flip_v(flip_h(m)) == rot180(m)          # => True
#
# THESE do commute — reflections in perpendicular axes
# always compose to a half turn, in either order.

# ============================================
# Symmetry tests

def mirror_symmetric(m):
    return m == flip_h(m)

mirror_symmetric(s)                             # => False
mirror_symmetric([[1, 2, 1], [3, 4, 3]])        # => True
#
# every row is a palindrome  <=>  the matrix is
# symmetric about its vertical axis

all(row == row[::-1] for row in [[1, 2, 1], [3, 4, 3]])     # => True

# ============================================
# Are two matrices mirror images?

def is_mirror(a, b):
    return flip_h(a) == b

is_mirror(s, flip_h(s))                 # => True
is_mirror(s, rot180(s))                 # => False

# ============================================
# The coordinate rule, for things that are not matrices
#
# Flipping a sprite means flipping its hitbox, its
# spawn points and its collision cells too.

def mirror_x(r, c, cols):
    return (r, cols - 1 - c)

[mirror_x(r, c, 3) for r, c in [(0, 0), (0, 1), (0, 2)]]
# => [(0, 2), (0, 1), (0, 0)]
#
# the centre column (c == 1 when cols == 3) is fixed.
# With an even width, nothing is fixed.

# ============================================
# Flip and invert — the classic two-liner
#
# LeetCode 832: reverse each row, then flip every bit.

def flip_and_invert(m):
    return [[1 - x for x in row[::-1]] for row in m]

flip_and_invert([[1, 1, 0],
                 [1, 0, 1],
                 [0, 0, 0]])
# =>
# [[1, 0, 0],
#  [0, 1, 0],
#  [1, 1, 1]]

# ============================================
# Compare

# mirror across the VERTICAL axis    -> this lesson
[row[::-1] for row in m]

# mirror across the HORIZONTAL axis  -> lesson 21
m[::-1]

# mirror across the DIAGONAL         -> transpose (lesson 16)
[list(r) for r in zip(*m)]

# both perpendicular mirrors         -> rotate 180 (lesson 18)
[row[::-1] for row in m[::-1]]
#
# four reflections, four axes. Compose any two and you
# get a rotation — that is the shape of the whole family.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|flip horizontal|`[row[::-1] for row in m]`|
|in place|`for row in m: row.reverse()`|
|the rule|`(r, c) → (r, cols-1-c)`|
|the shape|unchanged|
|to undo it|do it again|
|is it left-right symmetric|`all(row == row[::-1] for row in m)`|
|a rotation from it|compose with `transpose`|
|to remember `reverse()`|it returns **`None`** and mutates|
|the axis|"horizontal flip" ⇒ **vertical** mirror line|

---

## Key Insight

**A flip is a reflection, and reflections are not rotations.** This is the one genuinely new idea in the lesson, and it has a concrete consequence: an API that only offers `rotate(m, k)` cannot mirror your data, no matter what `k` you pass. `any(rotate(s, k) == flip_h(s) for k in range(4))` is `False`.

The mechanics are trivial by comparison — `[row[::-1] for row in m]`, shape preserved, its own inverse, in place for any shape. What is worth carrying:

- **Two perpendicular reflections compose to a half turn**, in either order: `flip_h ∘ flip_v == flip_v ∘ flip_h == rot180`. Perpendicular mirrors commute.
    
- **A reflection composed with the transpose is a quarter turn** — but the order matters: `flip_h ∘ transpose` is `rot90`, while `transpose ∘ flip_h` is `rot270`. These do *not* commute, and that asymmetry is exactly what lessons 17 and 19 exploit.
    
- **`list.reverse()` returns `None`.** `[row.reverse() for row in m]` builds a list of `None`s while quietly mutating the original. Use `row[::-1]` to build, `row.reverse()` to mutate — never mix them.
    

---

## The Four Mirrors

|Reflection|Axis|Idiom|Shape|
|---|---|---|---|
|**Flip horizontal**|vertical line|`[row[::-1] for row in m]`|preserved|
|**Flip vertical**|horizontal line|`m[::-1]`|preserved|
|**Transpose**|main diagonal|`[*zip(*m)]`|swaps|
|**Anti-transpose**|anti-diagonal|`[*zip(*[r[::-1] for r in m[::-1]])]`|swaps|

```text
        \   |   /
         \  |  /          the four mirror axes of a square
   ───────  ·  ───────
         /  |  \
        /   |   \

  vertical, horizontal, and the two diagonals
```

> **Mental shift:** rotations move the matrix *through* itself and come back after four turns. Reflections fold it *onto* itself and come back after two. Compose two folds and you get a turn — which is why every rotation in this section can be written as a transpose plus a flip.
