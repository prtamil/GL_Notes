# 30. Checkerboard

## Mental Model

The last generated matrix, and the one with the most hidden depth. The rule is **parity of the coordinate sum**:

```text
f(r, c) = (r + c) % 2

[[0, 1, 0, 1],          . # . #
 [1, 0, 1, 0],          # . # .
 [0, 1, 0, 1],   ->     . # . #
 [1, 0, 1, 0]]          # . # .
```

Adding `r` and `c` and taking the remainder produces alternation in **both** directions at once — moving one step right or one step down always flips the value, because you changed the sum by exactly 1.

That last sentence is not a description of a pattern; it is a **theorem about grids**, and it is why this lesson matters more than "how do I draw a chess board":

> Under 4-connectivity, **every neighbour of a cell has the opposite parity.**

So the checkerboard is a **2-colouring** of the grid graph from lesson 9, which proves that graph is *bipartite*. That single fact settles a family of problems that look like they need search — domino tilings, the mutilated chessboard, knight's-move colour arguments, alternating-turn games — with counting instead.

And the same expression generalises in three directions: `r % 2` and `c % 2` give stripes, `(r//k + c//k) % 2` gives blocks of size `k` (lesson 13's tiling), and `(r + c) % n` gives `n` colours.

---

## Relationship to Cognitive Verb

```text
Alternate
    ↓
Checkerboard
```

Related verbs:

- Alternate
- Tile in two colours
- Interleave
- Two-colour
- Stripe

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Checkerboard|the whole thing|`(r + c) % 2`|
|Inverted|start on the other colour|`(r + c + 1) % 2` or `1 - v`|
|Row stripes|horizontal bands|`r % 2`|
|Column stripes|vertical bands|`c % 2`|
|Block checkerboard|`k × k` squares|`(r//k + c//k) % 2`|
|`n` colours|repeat every `n`|`(r + c) % n`|
|2×2 colour classes|four groups|`(r % 2) * 2 + (c % 2)`|
|Render|as text|`"".join(chars[v] for v in row)`|
|Class counts|how many of each|`collections.Counter`|
|Parity test|same colour?|`(r1 + c1) % 2 == (r2 + c2) % 2`|

---

## Common Uses

- Chess, draughts and other board games
- Transparency backgrounds in image editors
- Test patterns for displays and printers
- Dithering and halftone patterns
- Alternating table row shading
- Tile maps and floor textures
- Bipartite decomposition of a grid graph
- Red-black ordering in numerical solvers (Gauss–Seidel)
- Parity arguments in combinatorics

---

## Hidden Interview Problems

- Generate a checkerboard / chess board pattern
- Check if a binary matrix is a valid chessboard
- Transform a matrix into a chessboard with minimum swaps
- Domino tiling feasibility
- The mutilated chessboard problem
- Knight's tour colour arguments
- Two-colour a grid graph
- Flip game / alternating-turn parity problems

---

## Recognition Clues

If you hear...

- "alternating pattern..."
- "chess board..."
- "no two adjacent cells the same..."
- "cover the board with dominoes..."
- "colour the grid with two colours..."
- "every move goes to a different colour..."

...think **Checkerboard**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Rule|`f(r, c) = (r + c) % 2`|
|Shape|`rows × cols`, any dimensions|
|Period|2 in both directions|
|4-neighbours|**Always** the opposite colour|
|8-neighbours|Diagonals are the **same** colour|
|Class sizes|Equal, unless both dimensions are odd|
|Graph property|Proves the 4-connected grid is **bipartite**|
|Time Complexity|O(rows × cols)|
|Common Domains|Games, graphics, combinatorics, numerics|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember

from collections import Counter

def checker(rows, cols):
    return [[(r + c) % 2 for c in range(cols)] for r in range(rows)]

checker(4, 4)
# =>
# [[0, 1, 0, 1],
#  [1, 0, 1, 0],
#  [0, 1, 0, 1],
#  [1, 0, 1, 0]]

checker(3, 5)                       # works for any shape
# =>
# [[0, 1, 0, 1, 0],
#  [1, 0, 1, 0, 1],
#  [0, 1, 0, 1, 0]]

# ============================================
# Rendering it

def render(m, chars=".#"):
    return "\n".join("".join(chars[v] for v in row) for row in m)

print(render(checker(8, 8)))
# .#.#.#.#
# #.#.#.#.
# .#.#.#.#
# #.#.#.#.
# .#.#.#.#
# #.#.#.#.
# .#.#.#.#
# #.#.#.#.
#
# indexing a STRING by the cell value is the neat trick:
# chars[0] is '.', chars[1] is '#'. Works for any small
# integer palette.

# ============================================
# Starting on the other colour

[[(r + c + 1) % 2 for c in range(4)] for r in range(4)]
# =>
# [[1, 0, 1, 0],
#  [0, 1, 0, 1],
#  [1, 0, 1, 0],
#  [0, 1, 0, 1]]

# same as inverting:
[[1 - v for v in row] for row in checker(4, 4)]     # => identical
#
# there are exactly TWO checkerboards of a given size,
# and they are each other's inverse.

# ============================================
# Stripes — drop one of the two coordinates

[[r % 2 for c in range(4)] for r in range(4)]       # horizontal bands
# =>
# [[0, 0, 0, 0],
#  [1, 1, 1, 1],
#  [0, 0, 0, 0],
#  [1, 1, 1, 1]]

[[c % 2 for c in range(4)] for r in range(4)]       # vertical bands
# =>
# [[0, 1, 0, 1],
#  [0, 1, 0, 1],
#  [0, 1, 0, 1],
#  [0, 1, 0, 1]]
#
# r%2 alternates DOWN, c%2 alternates ACROSS,
# (r+c)%2 alternates BOTH. The sum is what couples them.

# ============================================
# Block checkerboard — lesson 13's tiling, as a rule
#
# Integer-divide first: r//k is "which tile row am I in".
# Then the ordinary parity rule applies to tiles.

def block_checker(rows, cols, k):
    return [[(r//k + c//k) % 2 for c in range(cols)] for r in range(rows)]

print(render(block_checker(8, 8, 2)))
# ..##..##
# ..##..##
# ##..##..
# ##..##..
# ..##..##
# ..##..##
# ##..##..
# ##..##..

block_checker(6, 6, 1) == checker(6, 6)             # => True   k=1 is the base case
#
# this is the standard "transparency" background in
# image editors, and the same // that cut tiles in
# lesson 13.

# ============================================
# More than two colours

[[(r + c) % 3 for c in range(6)] for r in range(6)]
# =>
# [[0, 1, 2, 0, 1, 2],
#  [1, 2, 0, 1, 2, 0],
#  [2, 0, 1, 2, 0, 1],
#  [0, 1, 2, 0, 1, 2],
#  [1, 2, 0, 1, 2, 0],
#  [2, 0, 1, 2, 0, 1]]      diagonal stripes

[[(r % 2) * 2 + (c % 2) for c in range(4)] for r in range(4)]
# =>
# [[0, 1, 0, 1],
#  [2, 3, 2, 3],
#  [0, 1, 0, 1],
#  [2, 3, 2, 3]]           the four 2x2 phase classes
#
# (r+c)%n gives DIAGONAL bands; combining r%2 and c%2
# independently gives a 2x2 grid of classes. Different
# structures — pick by what you need to separate.

# ============================================
# Class sizes
#
# Equal, unless BOTH dimensions are odd — then the
# starting colour gets one extra.

Counter(v for row in checker(4, 4) for v in row)    # => Counter({0: 8, 1: 8})
Counter(v for row in checker(3, 5) for v in row)    # => Counter({0: 8, 1: 7})

def counts(rows, cols):
    c = Counter(v for row in checker(rows, cols) for v in row)
    return c[0], c[1]

counts(8, 8)                        # => (32, 32)
counts(2, 3)                        # => (3, 3)
counts(3, 3)                        # => (5, 4)
counts(5, 5)                        # => (13, 12)
#
# rows*cols even -> equal; both odd -> differ by exactly 1

# ============================================
# THE THEOREM: 4-neighbours always differ
#
# One step changes r or c by 1, so it changes r+c by 1,
# so it flips the parity. Always. No exceptions.

N4 = ((-1, 0), (1, 0), (0, -1), (0, 1))
N8 = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
           if (dr, dc) != (0, 0))

def nbrs(r, c, rows, cols, dirs):
    return [(r+dr, c+dc) for dr, dc in dirs
            if 0 <= r+dr < rows and 0 <= c+dc < cols]

ch = checker(4, 4)

all(ch[r][c] != ch[nr][nc]
    for r in range(4) for c in range(4)
    for nr, nc in nbrs(r, c, 4, 4, N4))             # => True

all(ch[r][c] != ch[nr][nc]
    for r in range(4) for c in range(4)
    for nr, nc in nbrs(r, c, 4, 4, N8))             # => False

ch[0][0], ch[1][1]                                  # => (0, 0)   same colour!
#
# a DIAGONAL step changes r+c by 0 or 2 — parity is
# preserved. So the 8-connected grid is NOT bipartite,
# and every parity argument below is about N4 only.

# ============================================
# What that buys you: the mutilated chessboard
#
# Remove two OPPOSITE corners of an 8x8 board. Can the
# remaining 62 squares be tiled with 31 dominoes?
#
# Each domino covers two ADJACENT squares, which by the
# theorem above is always one of each colour. So any
# tiling needs equal counts. Now count.

b8 = checker(8, 8)

Counter(v for row in b8 for v in row)               # => Counter({0: 32, 1: 32})

b8[0][0], b8[7][7]                                  # => (0, 0)   BOTH the same

Counter(b8[r][c] for r in range(8) for c in range(8)
        if (r, c) not in {(0, 0), (7, 7)})
# => Counter({1: 32, 0: 30})
#
# 30 vs 32. Every domino needs one of each. Impossible.
#
# No search, no backtracking — a colouring and a count.
# This is the pattern's real payoff: parity turns an
# exponential search into arithmetic.

# ============================================
# Knight moves always change colour
#
# A knight moves (1,2) or (2,1), so r+c changes by 1 or
# 3 — odd either way. Parity flips every single move.

KNIGHT = [(1,2), (2,1), (-1,2), (-2,1), (1,-2), (2,-1), (-1,-2), (-2,-1)]

all(b8[r][c] != b8[r+dr][c+dc]
    for r in range(8) for c in range(8)
    for dr, dc in KNIGHT
    if 0 <= r+dr < 8 and 0 <= c+dc < 8)             # => True

b8[0][0], b8[1][2], b8[2][1]                        # => (0, 1, 1)
#
# consequence: a closed knight's tour must have an even
# number of moves, and no knight's tour exists on a
# board with unequal colour counts.

# ============================================
# Validating a board someone else built

def is_checkerboard(m):
    return all(m[r][c] == (m[0][0] + r + c) % 2
               for r in range(len(m)) for c in range(len(m[0])))

is_checkerboard(checker(5, 5))                      # => True
is_checkerboard([[1 - v for v in row] for row in checker(5, 5)])    # => True
is_checkerboard([[0, 1], [0, 1]])                   # => False
#
# anchoring to m[0][0] accepts BOTH phases without
# needing two separate checks

# ============================================
# Chess board convention
#
# In algebraic notation a1 is DARK and is the
# bottom-left. With row 0 at the top, a1 is (7, 0).

checker(8, 8)[7][0]                 # => 1
checker(8, 8)[7][7]                 # => 0
#
# so with chars=".#", '#' is dark. Whether your row 0 is
# the top or the bottom is lesson 21's flip_v question,
# and it decides which colour lands in which corner.

# ============================================
# Compare — the section, complete

n = 4
[[int(r == c)       for c in range(n)] for r in range(n)]   # 28 identity
[[(r, c)            for c in range(n)] for r in range(n)]   # 29 coordinates
[[(r + c) % 2       for c in range(n)] for r in range(n)]   # 30 checkerboard
[[(r//2 + c//2) % 2 for c in range(n)] for r in range(n)]   # 30 blocks
[[(r + c) % 3       for c in range(n)] for r in range(n)]   # 30 n-colour
#
# one comprehension, five rules.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a checkerboard|`(r + c) % 2`|
|the other phase|`(r + c + 1) % 2`|
|horizontal stripes|`r % 2`|
|vertical stripes|`c % 2`|
|`k × k` blocks|`(r//k + c//k) % 2`|
|`n` colours|`(r + c) % n`|
|to render it|`chars[v]` with `chars = ".#"`|
|"are these the same colour?"|`(r1+c1) % 2 == (r2+c2) % 2`|
|a parity argument|4-neighbours always differ; **diagonals do not**|

---

## Key Insight

**`(r + c) % 2` is not a drawing trick — it is a proof that the 4-connected grid is bipartite.**

One orthogonal step changes `r` or `c` by exactly 1, so it changes `r + c` by 1, so it flips the parity. Every time, everywhere, on any grid size. That gives you a free 2-colouring in which **no two adjacent cells share a colour**, and a whole class of problems collapses:

- **Dominoes** cover one cell of each colour, so any tiling needs equal counts. Remove two opposite corners of a chess board — both the same colour — and you have 30 versus 32. No tiling exists, and you proved it by counting rather than searching.
    
- **Knight moves** change `r + c` by 1 or 3, always odd, so a knight alternates colour every move. Closed tours must therefore have even length.
    
- **Alternating-turn games** on grids are parity arguments wearing a costume.
    

The essential caveat: **this holds for 4-connectivity only.** A diagonal step changes `r + c` by 0 or 2 and preserves parity, so the 8-connected grid is *not* bipartite — `ch[0][0]` and `ch[1][1]` are the same colour. Every argument above quietly depends on which neighborhood from lessons 9–10 you mean.

Practically, the rule generalises by changing what you feed the modulo:

```text
(r + c) % 2        alternating cells
r % 2, c % 2       stripes, one axis at a time
(r//k + c//k) % 2  k x k blocks   (lesson 13's tiling)
(r + c) % n        n diagonal colour bands
```

---

## The Course in One Table

|Section|Lessons|The question|
|---|---|---|
|Traversal|1–8|In what **order** do I visit cells?|
|Neighborhood|9–11|Which cells are **near** this one?|
|Windows|12–15|What is inside this **rectangle**, as I slide it?|
|Structure|16–23|Where does each cell **go**?|
|Search|24–26|**Where** is it, and what **connects** to what?|
|Scan|27|How do I answer rectangle queries in **O(1)**?|
|Generation|28–30|What **is** each cell, given its coordinates?|

```text
  1-27 :  matrix  ──►  answer        (consume)
  28-30:  f(r,c)  ──►  matrix        (produce)
```

And the threads that ran through all of it:

- **`zip(*m)`** — transpose, columns, matrix multiply, and every rotation.
    
- **The neighborhood function** — turns a grid into a graph, and BFS solves the rest (9, 25, 26).
    
- **`(r, c)` as the unit of thought** — an order in 1–8, a shape in 9–15, a destination in 16–23, and finally an *input* in 28–30.
    
- **Two slices** — `m[r:r+h]` and `row[c:c+w]` — which are, verbatim, all of lessons 12–15.
    

> **Mental shift:** the course began by asking how to *read* a matrix and ends by asking how to *write* one. The checkerboard is the right place to stop, because it shows that a generated pattern can be a mathematical object: two lines of Python that also happen to prove something about every grid you will ever traverse.
