# 37. Meshgrid

## Mental Model

Part 2's lesson 29 said every generated matrix is a **function of its coordinates**:

```python
[[f(r, c) for c in range(cols)] for r in range(rows)]
```

At rank `n` you can't write that loop nest at all (lesson 6). So instead you **materialise the coordinates as tensors** and let the expression vectorise:

```text
i, j = coordinate grids of shape (3, 4)

f = i + j          ->  the whole grid, no loop
```

That's what `meshgrid`, `indices`, `mgrid` and `ogrid` all produce: one tensor per axis, each holding that axis's index.

```text
np.indices((3,4))[0]        np.indices((3,4))[1]

  0 0 0 0                     0 1 2 3
  1 1 1 1                     0 1 2 3
  2 2 2 2                     0 1 2 3
     ↑ the row index             ↑ the column index
```

Lesson 19 already did this with two vectors and broadcasting — `np.arange(3)[:, None]` and `np.arange(4)[None, :]` — using a fraction of the memory. So what this lesson is really about is **which form to reach for**:

|Form|Shapes|Memory|
|---|---|---|
|`meshgrid(..., sparse=True)`, `ogrid`|`(3,1)`, `(1,4)`|**small**|
|`meshgrid`, `indices`, `mgrid`|`(3,4)`, `(3,4)`|full|

The sparse form *is* the broadcasting form with a name on it. Prefer it and let broadcasting do the expanding.

And here's the trap that costs everyone an afternoon exactly once: **`meshgrid` defaults to `indexing='xy'`, which transposes.**

---

## Relationship to Cognitive Verb

```text
Coordinate
    ↓
Meshgrid
```

Related verbs:

- Lay out coordinates
- Index the space
- Parameterise by position
- Sample a field
- Build a grid

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Coordinate grids|from vectors|`np.meshgrid(xs, ys, indexing='ij')`|
|...without the copy|broadcast shapes|`..., sparse=True`|
|Integer indices|from a shape|`np.indices(shape)`|
|...sparse|same|`np.indices(shape, sparse=True)`|
|Slice syntax, dense|concise|`np.mgrid[0:3, 0:4]`|
|Slice syntax, sparse|**preferred**|`np.ogrid[0:3, 0:4]`|
|By hand|the underlying idea|`a[:, None]`, `b[None, :]`|
|Real-valued grids|not just indices|`np.meshgrid(np.linspace(...), ...)`|
|A field|the payoff|any expression in the coordinate tensors|

---

## Common Uses

- Evaluating a function over a grid
- Distance and radial fields
- Coordinate transforms and warping
- Plotting surfaces and contours
- Positional encodings
- Procedural textures and masks
- Sampling parameter space

---

## Hidden Interview Problems

- Evaluate f(x, y) over a grid without loops
- Build a distance-from-centre field
- Generate all index tuples of an n-D array
- Create a circular or ring mask
- Build a coordinate tensor at arbitrary rank
- Explain the difference between `'ij'` and `'xy'` indexing

---

## Recognition Clues

If you hear...

- "evaluate over a grid..."
- "meshgrid..."
- "distance from the centre..."
- "for every (x, y) pair..."
- "a coordinate field..."

...think **Meshgrid**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Output|One tensor per axis, holding that axis's index|
|`indexing='ij'`|Matrix convention — **use this**|
|`indexing='xy'`|**The default** — transposes the first two axes|
|`sparse=True`|Returns broadcast shapes, not full grids|
|`np.indices(shape)`|Stacked: shape `(ndim, *shape)`|
|`np.mgrid` / `np.ogrid`|Slice syntax; dense / sparse|
|Memory (dense)|`ndim × prod(shape) × itemsize`|
|Memory (sparse)|`sum(shape) × itemsize`|
|Rank|Works at any rank|
|Common Domains|Scientific computing, graphics, ML|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember
#
#   one index tensor per axis

import numpy as np

xs = np.arange(3)
ys = np.arange(4)

X, Y = np.meshgrid(xs, ys, indexing='ij')

X.shape, Y.shape            # => ((3, 4), (3, 4))

X
# => array([[0, 0, 0, 0],
#           [1, 1, 1, 1],
#           [2, 2, 2, 2]])      the ROW index everywhere
Y
# => array([[0, 1, 2, 3],
#           [0, 1, 2, 3],
#           [0, 1, 2, 3]])      the COLUMN index everywhere
#
# now any expression in X and Y is a whole field:
(X + Y).shape               # => (3, 4)

# ============================================
# THE TRAP: the default is 'xy', which transposes

np.meshgrid(xs, ys)[0].shape                # => (4, 3)
np.meshgrid(xs, ys, indexing='ij')[0].shape # => (3, 4)

np.meshgrid(xs, ys)[0]
# => array([[0, 1, 2],
#           [0, 1, 2],
#           [0, 1, 2],
#           [0, 1, 2]])
#
# 'xy' is the CARTESIAN convention: x horizontal, y
# vertical — which swaps the first two axes relative to
# array indexing. It is the default because meshgrid
# came from plotting.
#
# For array work ALWAYS pass indexing='ij'. Forgetting
# gives you a transposed field that still runs — and on
# a square grid it does not even change the shape.

# ============================================
# sparse=True — the form you actually want

Xs, Ys = np.meshgrid(xs, ys, indexing='ij', sparse=True)
Xs.shape, Ys.shape          # => ((3, 1), (1, 4))

# ...which is exactly lesson 19's broadcasting setup:
xs[:, None].shape, ys[None, :].shape        # => ((3, 1), (1, 4))

(Xs + Ys).shape             # => (3, 4)
np.array_equal(X + Y, Xs + Ys)              # => True
#
# same answer, because broadcasting expands them for
# free (lesson 17). And the memory:

X.nbytes + Y.nbytes         # => 192      dense
Xs.nbytes + Ys.nbytes       # => 56       sparse
#
# on a 1000x1000 grid that is 16 MB versus 16 KB. The
# dense grids are almost never necessary — every
# elementwise expression broadcasts them anyway.

# ============================================
# np.indices — the same thing, from a shape

np.indices((3, 4)).shape    # => (2, 3, 4)
#
#   (ndim, *shape) — the coordinate tensors STACKED
#   along a new leading axis.

np.indices((3, 4))[0]
# => array([[0, 0, 0, 0],
#           [1, 1, 1, 1],
#           [2, 2, 2, 2]])

np.array_equal(np.indices((3, 4)),
               np.array(np.meshgrid(xs, ys, indexing='ij')))    # => True
#
# `indices` takes a SHAPE, `meshgrid` takes VECTORS.
# Use indices when you want plain 0..n-1 coordinates;
# use meshgrid when the axes have real values
# (linspace, log scales, physical units).

[a.shape for a in np.indices((3, 4), sparse=True)]      # => [(3,1), (1,4)]

# because it is stacked, you can reduce over the axes:
np.indices((3, 4)).sum(axis=0)
# => array([[0, 1, 2, 3],
#           [1, 2, 3, 4],
#           [2, 3, 4, 5]])          i + j, in one call

# ============================================
# mgrid and ogrid — slice syntax

np.mgrid[0:3, 0:4].shape                    # => (2, 3, 4)
np.array_equal(np.mgrid[0:3, 0:4], np.indices((3, 4)))          # => True

[a.shape for a in np.ogrid[0:3, 0:4]]       # => [(3,1), (1,4)]
#
#   mgrid  = Meshgrid, dense
#   ogrid  = Open grid, sparse
#
# they accept slice syntax including steps and complex
# "number of points" notation:
#   np.mgrid[0:1:5j]  ->  5 points from 0 to 1, like linspace
#
# ogrid is the most concise way to get broadcast-ready
# coordinates.

# ============================================
# AT ANY RANK — this is why the section exists

i, j, k = np.ogrid[0:2, 0:3, 0:4]
i.shape, j.shape, k.shape   # => ((2,1,1), (1,3,1), (1,1,4))
#
# each coordinate is a size-1 tensor in every axis but
# its own — the alignment rule of lesson 18, done for you.

(i + j + k).shape           # => (2, 3, 4)
(i + j + k)[0]
# => array([[0, 1, 2, 3],
#           [1, 2, 3, 4],
#           [2, 3, 4, 5]])

np.array_equal(i + j + k, np.indices((2, 3, 4)).sum(axis=0))    # => True
#
# `f(i, j, k)` for a rank-3 tensor, with no loop and no
# rank-specific code. Part 2's lesson 29 could only do
# this for rank 2, because the comprehension had to be
# written out.

# ============================================
# THE PAYOFF: fields are one expression

r = np.arange(5)[:, None]
c = np.arange(5)[None, :]

# checkerboard (part 2, lesson 30)
(r + c) % 2
# => array([[0, 1, 0, 1, 0],
#           [1, 0, 1, 0, 1],
#           [0, 1, 0, 1, 0],
#           [1, 0, 1, 0, 1],
#           [0, 1, 0, 1, 0]])

# radial distance from the centre (part 2, lesson 29)
np.round(np.sqrt((r - 2)**2 + (c - 2)**2), 1)
# => array([[2.8, 2.2, 2. , 2.2, 2.8],
#           [2.2, 1.4, 1. , 1.4, 2.2],
#           [2. , 1. , 0. , 1. , 2. ],
#           [2.2, 1.4, 1. , 1.4, 2.2],
#           [2.8, 2.2, 2. , 2.2, 2.8]])

# a disc mask
((r - 2)**2 + (c - 2)**2 <= 4).astype(int)
# => array([[0, 0, 1, 0, 0],
#           [0, 1, 1, 1, 0],
#           [1, 1, 1, 1, 1],
#           [0, 1, 1, 1, 0],
#           [0, 0, 1, 0, 0]])
#
# lesson 11's masking (`int(condition)`) plus lesson 19's
# broadcasting — the geometry is the expression.

# ============================================
# Real-valued axes: meshgrid, not indices

x = np.linspace(-1, 1, 5)
y = np.linspace(-1, 1, 5)
Xr, Yr = np.meshgrid(x, y, indexing='ij', sparse=True)

Z = np.exp(-(Xr**2 + Yr**2))
Z.shape                     # => (5, 5)
np.round(Z, 3)[2]           # => [0.368, 0.779, 1.   , 0.779, 0.368]
#
# a 2-D gaussian, sampled on a grid. `indices` cannot do
# this — the axes are not 0..n-1. That is the division
# of labour between the two functions.

# ============================================
# Practical: a positional encoding

T, d = 4, 6
pos = np.arange(T)[:, None]                 # (T, 1)
dim = np.arange(d // 2)[None, :]            # (1, d/2)

angle = pos / (10000 ** (2 * dim / d))
angle.shape                                 # => (4, 3)
pe = np.concatenate([np.sin(angle), np.cos(angle)], axis=-1)
pe.shape                                    # => (4, 6)
#
# two coordinate vectors, one broadcast expression, one
# concatenate (lesson 24). No loop over positions.

# ============================================
# Compare

np.meshgrid(a, b, indexing='ij')            # dense grids, real values
np.meshgrid(a, b, indexing='ij', sparse=True)   # broadcast shapes
np.indices(shape)                           # dense, integer, stacked
np.ogrid[0:3, 0:4]                          # sparse, concise
a[:, None], b[None, :]                      # by hand — the same thing

[np.indices((3,4)).shape,
 [a.shape for a in np.ogrid[0:3, 0:4]],
 [np.arange(3)[:,None].shape, np.arange(4)[None,:].shape]]
# => [(2, 3, 4), [(3, 1), (1, 4)], [(3, 1), (1, 4)]]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|coordinate tensors|`np.meshgrid(..., indexing='ij')`|
|**always**|`indexing='ij'` — the default transposes|
|the cheap form|`sparse=True`, or `np.ogrid`|
|integer coordinates from a shape|`np.indices(shape)`|
|real-valued axes|`meshgrid` over `linspace`|
|arbitrary rank|`np.ogrid[0:a, 0:b, 0:c]`|
|`i + j` in one call|`np.indices(shape).sum(axis=0)`|
|by hand|`a[:, None]`, `b[None, :]`|

---

## Key Insight

**Coordinate tensors are how `f(i, j, k)` becomes an expression instead of a loop.**

Part 2 wrote `[[f(r,c) for c in ...] for r in ...]` and could only do rank 2, because the loop nest had to be typed out. Materialise one index tensor per axis and the same function is a single vectorised expression — at any rank:

```python
i, j, k = np.ogrid[0:2, 0:3, 0:4]
field = i + j + k                       # shape (2, 3, 4), no loop
```

Two decisions matter more than which function you call:

1. **`indexing='ij'`, always.** `np.meshgrid` defaults to `'xy'`, which transposes the first two axes — a plotting convention that produces a transposed field in array code. It still runs, and on a square grid the shape does not even change.
    
2. **Use the sparse form.** `sparse=True` / `np.ogrid` return `(3,1)` and `(1,4)` instead of two full `(3,4)` grids — which is exactly lesson 19's `a[:, None]` and `b[None, :]`. Broadcasting expands them for free (lesson 17), so the dense grids are wasted memory: 16 MB versus 16 KB on a 1000×1000 field.
    

The division of labour between the two families is simple: **`np.indices` takes a shape and gives integer coordinates; `np.meshgrid` takes vectors and gives whatever values they hold** — `linspace` samples, log scales, physical units.

---

## Coordinates Across the Course

|Where|Coordinates came from|
|---|---|
|Part 2, lesson 29|`for r in range(R): for c in range(C)`|
|Part 3, lesson 6|`np.ndindex(*shape)` — one tuple at a time|
|**Part 3, lesson 37**|**index tensors** — all at once, vectorised|

```text
   loop      ->  one cell at a time,  rank-specific
   ndindex   ->  one cell at a time,  rank-agnostic
   ogrid     ->  ALL cells at once,   rank-agnostic
```

> **Mental shift:** part 2 treated `(r, c)` as an address you looped over. Here the coordinates are *data*: tensors you do arithmetic on. Once position is a value rather than a loop variable, a checkerboard, a distance field and a positional encoding are all just expressions, and the rank stops mattering.
