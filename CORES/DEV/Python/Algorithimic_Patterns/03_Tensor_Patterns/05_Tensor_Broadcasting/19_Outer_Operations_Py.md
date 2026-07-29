# 19. Outer Operations

## Mental Model

This is the payoff for the last two lessons. Give two vectors **perpendicular** shapes and broadcasting hands you **every combination**:

```text
a[:, None]      (3, 1)
b[None, :]         (1, 4)
                ---------
                (3, 4)      all 3 x 4 pairs
```

And not just products. *Any* elementwise operation:

```text
a[:, None] * b[None, :]     outer product
a[:, None] + b[None, :]     outer sum
a[:, None] > b[None, :]     comparison matrix
a[:, None] - b[None, :]     pairwise differences
```

This is the vectorised replacement for a nested loop. Part 2's lesson 29 built coordinate grids with `[[f(r, c) for c in ...] for r in ...]`. Those same grids are now a single broadcast, at any size, with no Python loop at all.

The pattern extends to "all pairs of *rows*" by pushing the new axis one place further in:

```text
x[:, None, :] - x[None, :, :]       (n, n, d)   every pairwise difference
```

which is how you write a distance matrix, an attention score matrix, or a similarity search, all in one line.

One caveat worth stating up front: the **inputs** stay small but the **result** is `n × m`. Two 1000-element vectors cost 16 KB and their outer product costs 8 MB. Broadcasting makes the intermediate free; it does not make the output free.

---

## Relationship to Cognitive Verb

```text
Combine All
    ↓
Outer Operations
```

Related verbs:

- Every pair
- Cross-combine
- All against all
- Tabulate
- Build a grid

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Any outer op|the general form|`a[:, None] OP b[None, :]`|
|Outer product|the classic|`np.outer(a, b)`|
|Named ufunc form|any operation|`np.add.outer`, `np.multiply.outer`|
|All pairs of rows|rank 3 result|`x[:, None, :] - x[None, :, :]`|
|Pairwise distances|reduce the last axis|`np.sqrt((d**2).sum(-1))`|
|Coordinate grids|explicit|`np.meshgrid(..., indexing='ij')`|
|...without the copy|sparse|`np.meshgrid(..., sparse=True)`|
|Index grids|all coordinates|`np.indices(shape)`|
|One-hot|compare against `arange`|`labels[:, None] == np.arange(K)`|
|Memory-free reduction|don't materialise|reduce algebraically if you can|

---

## Common Uses

- Pairwise distance and similarity matrices
- Attention scores (`Q @ K.T` is the matmul form of this)
- One-hot encoding
- Coordinate grids and distance fields
- Multiplication tables and lookup grids
- Comparing every prediction against every label
- Building masks from index comparisons
- Gaussian kernels over a grid

---

## Hidden Interview Problems

- Compute a pairwise distance matrix without loops
- One-hot encode a label vector
- Build a multiplication table
- Generate a coordinate grid
- Find the closest pair of points
- Create an upper-triangular mask
- Compute all pairwise differences in an array

---

## Recognition Clues

If you hear...

- "all pairs..."
- "every combination..."
- "distance matrix / similarity matrix..."
- "one-hot..."
- "for each i, for each j..."
- "meshgrid..."

...think **Outer Operations**.

---

## Pattern Summary

|Property|Value|
|---|---|
|The move|Give operands perpendicular size-1 axes|
|Shapes|`(n, 1)` against `(1, m)` → `(n, m)`|
|Works for|**Every** elementwise operation, not just `*`|
|Swap the order|Transposes the result|
|All pairs of rows|`x[:, None, :]` against `x[None, :, :]`|
|Intermediate cost|**Free** — stride-0 views|
|Output cost|`n × m` — this is real|
|Common Domains|ML, geometry, statistics, procedural generation|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember

import numpy as np

u = np.array([1, 2, 3])
w = np.array([10, 20, 30, 40])

u[:, None].shape            # => (3, 1)
w[None, :].shape            # => (1, 4)

u[:, None] + w[None, :]
# => array([[11, 21, 31, 41],
#           [12, 22, 32, 42],
#           [13, 23, 33, 43]])
(u[:, None] + w[None, :]).shape         # => (3, 4)
#
#   (3, 1)
#   (1, 4)
#   ------
#   (3, 4)      every pair, no loop

# the operation is a parameter — it does not have to be +
u[:, None] * w[None, :]
# => array([[ 10,  20,  30,  40],
#           [ 20,  40,  60,  80],
#           [ 30,  60,  90, 120]])

u[:, None] > np.array([1, 2, 3])[None, :]
# => array([[False, False, False],
#           [ True, False, False],
#           [ True,  True, False]])
#
# a comparison matrix — and that is a strictly-lower
# triangular mask, built by comparing indices.

# ============================================
# The named forms

np.array_equal(np.outer(u, w), u[:, None] * w[None, :])     # => True

np.add.outer(u, w)
# => array([[11, 21, 31, 41],
#           [12, 22, 32, 42],
#           [13, 23, 33, 43]])

np.multiply.outer(u, w)     # => same as np.outer
#
# EVERY ufunc has an `.outer` method: np.subtract.outer,
# np.maximum.outer, np.greater.outer. `np.outer` is just
# `np.multiply.outer` with a flatten.
#
# the explicit [:, None] form is more general (it extends
# to rank 3+ and mixed ranks), so prefer it unless the
# named version reads better.

# ============================================
# Order matters — it transposes

np.array_equal(w[:, None] + u[None, :],
               (u[:, None] + w[None, :]).T)                 # => True
#
# whichever operand gets the COLUMN shape becomes the
# row index of the result.

# ============================================
# All pairs of ROWS — the rank-3 version
#
# Insert the new axis one place further in.

pts = np.array([[0., 0.],
                [3., 4.],
                [6., 8.],
                [0., 1.]])
pts.shape                   # => (4, 2)      4 points in 2-D

d = pts[:, None, :] - pts[None, :, :]
d.shape                     # => (4, 4, 2)
#
#   (4, 1, 2)
#   (1, 4, 2)
#   ---------
#   (4, 4, 2)     d[i, j] is point i minus point j

dist = np.sqrt((d ** 2).sum(axis=-1))
dist.shape                  # => (4, 4)
np.round(dist, 3)
# => array([[ 0.   ,  5.   , 10.   ,  1.   ],
#           [ 5.   ,  0.   ,  5.   ,  4.243],
#           [10.   ,  5.   ,  0.   ,  9.22 ],
#           [ 1.   ,  4.243,  9.22 ,  0.   ]])

np.allclose(dist, dist.T)           # => True    symmetric, as it must be
np.allclose(np.diag(dist), 0)       # => True    zero on the diagonal
#
# those two checks are worth running whenever you write
# a distance matrix — they catch a swapped [:, None].

# the closest pair (ignoring the diagonal):
np.fill_diagonal(dist, np.inf)
np.unravel_index(dist.argmin(), dist.shape)         # => (0, 3)
#
# points 0 and 3 are closest — distance 1.

# ============================================
# One-hot encoding — a comparison against arange

labels = np.array([0, 2, 1, 2])
K = 3

oh = (labels[:, None] == np.arange(K)[None, :]).astype(int)
oh
# => array([[1, 0, 0],
#           [0, 0, 1],
#           [0, 1, 0],
#           [0, 0, 1]])
oh.shape                    # => (4, 3)
oh.sum(axis=1)              # => [1, 1, 1, 1]     exactly one hot per row
#
#   (4, 1) == (1, 3)  ->  (4, 3)
#
# no loop, no lookup table. The same shape trick as
# lesson 10's embedding, run in the other direction.

# ============================================
# Coordinate grids — part 2's lesson 29, vectorised

r = np.arange(5)[:, None]           # (5, 1)
c = np.arange(5)[None, :]           # (1, 5)

# checkerboard (part 2, lesson 30)
(r + c) % 2
# => array([[0, 1, 0, 1, 0],
#           [1, 0, 1, 0, 1],
#           [0, 1, 0, 1, 0],
#           [1, 0, 1, 0, 1],
#           [0, 1, 0, 1, 0]])

# identity (part 2, lesson 28)
(r == c).astype(int)
# => array([[1, 0, 0, 0, 0],
#           [0, 1, 0, 0, 0],
#           [0, 0, 1, 0, 0],
#           [0, 0, 0, 1, 0],
#           [0, 0, 0, 0, 1]])

# a radial distance field (part 2, lesson 29)
np.round(np.sqrt((r - 2)**2 + (c - 2)**2), 1)
# => array([[2.8, 2.2, 2. , 2.2, 2.8],
#           [2.2, 1.4, 1. , 1.4, 2.2],
#           [2. , 1. , 0. , 1. , 2. ],
#           [2.2, 1.4, 1. , 1.4, 2.2],
#           [2.8, 2.2, 2. , 2.2, 2.8]])
#
# part 2 wrote `[[f(r,c) for c in range(C)] for r in range(R)]`.
# This is the same function of coordinates with the loops
# replaced by two perpendicular vectors. `f(r, c)` is now
# literally an expression in `r` and `c`.

# ============================================
# meshgrid — the explicit version, and its trap

X, Y = np.meshgrid(np.arange(3), np.arange(4), indexing='ij')
X.shape                     # => (3, 4)
X
# => array([[0, 0, 0, 0],
#           [1, 1, 1, 1],
#           [2, 2, 2, 2]])
Y
# => array([[0, 1, 2, 3],
#           [0, 1, 2, 3],
#           [0, 1, 2, 3]])

# the DEFAULT is indexing='xy', which TRANSPOSES:
np.meshgrid(np.arange(3), np.arange(4))[0].shape        # => (4, 3)
#
# 'xy' is Cartesian convention (x horizontal); 'ij' is
# matrix convention (first index = row). Getting this
# wrong gives you a transposed grid that still runs.
# Always pass indexing='ij' for array work.

# meshgrid materialises full arrays. sparse=True gives
# the broadcast form instead:
[a.shape for a in np.meshgrid(np.arange(3), np.arange(4),
                              indexing='ij', sparse=True)]
# => [(3, 1), (1, 4)]
#
# which is exactly `np.arange(3)[:, None]` and
# `np.arange(4)[None, :]`. meshgrid(sparse=True) IS the
# outer-operation setup, with a name.

# and np.indices gives every coordinate at once:
np.indices((3, 4)).shape                # => (2, 3, 4)
np.indices((3, 4))[0]
# => array([[0, 0, 0, 0],
#           [1, 1, 1, 1],
#           [2, 2, 2, 2]])

# ============================================
# THE COST: inputs stay small, the output does not

big_u = np.arange(1000)
big_w = np.arange(1000)

(big_u.nbytes + big_w.nbytes)                   # => 16000     16 KB in
(big_u[:, None] * big_w[None, :]).nbytes        # => 8000000   8 MB out
#
# broadcasting made the INTERMEDIATE free — nothing was
# tiled. But the result is a genuine n x m array and it
# is allocated in full.
#
# At n = 100,000 an outer product is 80 GB. "Vectorised"
# does not mean "free" — it means "no Python loop".

# sometimes you can avoid materialising it entirely:
int((big_u[:, None] * big_w[None, :]).sum())    # => 249500250000   8 MB
int(big_u.sum()) * int(big_w.sum())             # => 249500250000   no array
#
# sum(a_i * b_j) == (sum a)(sum b). When the outer
# product is immediately reduced, check whether algebra
# collapses it first. This is the same idea that makes
# `einsum` and matmul efficient (lesson 34).

# ============================================
# Compare

u[:, None] * w[None, :]         # outer product      (3,4)
u[:, None] + w[None, :]         # outer sum          (3,4)
u[:, None] > w[None, :]         # comparison matrix  (3,4)
x[:, None, :] - x[None, :, :]   # all pairs of rows  (n,n,d)
labels[:, None] == np.arange(K) # one-hot            (n,K)
np.meshgrid(a, b, indexing='ij')            # explicit grids
np.meshgrid(a, b, indexing='ij', sparse=True)   # ...the broadcast form

# the trailing [None, :] is optional — broadcasting pads
# leading axes automatically:
np.array_equal(u[:, None] * w, u[:, None] * w[None, :])     # => True
#
# write it when it makes the intent clearer, omit it when
# the code is dense. The [:, None] is the one that matters.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|every pair|`a[:, None] OP b[None, :]`|
|an outer product|`np.outer(a, b)` or the `[:, None]` form|
|any other outer op|`np.add.outer`, `np.maximum.outer`, …|
|all pairs of rows|`x[:, None, :]` vs `x[None, :, :]`|
|a distance matrix|that, then `sqrt((d**2).sum(-1))`|
|to sanity-check it|symmetric, and zero on the diagonal|
|one-hot|`labels[:, None] == np.arange(K)`|
|a coordinate grid|two perpendicular `arange`s|
|`meshgrid`|**always** `indexing='ij'`|
|to not blow up memory|remember the output is `n × m`|

---

## Key Insight

**Perpendicular size-1 axes produce every combination.** That is the whole pattern:

```text
(n, 1)  OP  (1, m)   ->   (n, m)
```

and the operation is a parameter. Multiply and you get an outer product; subtract and you get pairwise differences; compare and you get a mask. Insert the axis one position deeper and "every pair of scalars" becomes "every pair of **rows**", which is one line away from a distance matrix, a similarity matrix or an attention score matrix.

This is also where part 2's generation section reappears. `[[f(r, c) for c in ...] for r in ...]` becomes `f(r[:, None], c[None, :])` — the checkerboard, the identity matrix and the radial distance field are all one expression now, at any size.

Three things to carry:

1. **`meshgrid` defaults to `indexing='xy'`, which transposes.** Always pass `indexing='ij'` for array work. And `sparse=True` returns `(n,1)` and `(1,m)` — meshgrid's sparse mode *is* the outer-operation setup.
    
2. **Check your distance matrices.** Symmetric, and zero on the diagonal. Both hold automatically if the `[:, None]` is on the right operand, and both break if it is not — so they are a free correctness test.
    
3. **The intermediate is free; the output is not.** Broadcasting means nothing is tiled, but an `n × m` result is genuinely allocated. Two 1000-vectors give 8 MB; at 100,000 it is 80 GB. When the outer product is immediately reduced, look for the algebraic shortcut first — `sum(aᵢbⱼ) == (Σa)(Σb)` — which is the same insight that makes matmul and `einsum` fast.
    

---

## The Broadcasting Section, Complete

|Lesson|Contribution|
|---|---|
|17 Broadcasting Rules|right-align, stretch every 1 — and stride 0 makes it free|
|18 Axis Alignment|**where** you put the 1s decides which axis lines up|
|**19 Outer Operations**|put them **perpendicular** and you get every pair|

```text
   a  (n,)        a[:, None]  (n, 1)
   b  (m,)   ──►  b[None, :]     (1, m)
                              ---------
                               (n, m)     all pairs
```

Three lessons, one mechanism. A size-1 axis is a *free* axis, and deciding where the free axes go is the whole vocabulary.

> **Mental shift:** parts 1 and 2 answered "combine every a with every b" with a nested loop, and the loop *was* the program. Part 3 answers it with two shapes. The loop hasn't vanished — it moved into C, where it belongs — and what you write instead is the *alignment*. That's why the last two lessons were about placing `None`s: in tensor code, shape manipulation **is** the control flow.
