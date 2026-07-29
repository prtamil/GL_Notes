# 38. Identity and Diagonal

## Mental Model

The last generation pattern, and the one with the most structure to it: tensors defined by **where the indices agree**.

```text
i == j        the diagonal        ->  np.eye, np.diag
i >= j        lower triangle      ->  np.tril
i <  j        strictly upper      ->  np.triu(k=1)
```

Part 2's lesson 28 built the identity matrix as `int(r == c)`, a predicate over coordinates. That's still exactly what these functions are, and lesson 37 just showed you how to write it at any rank:

```python
np.arange(n)[:, None] == np.arange(n)[None, :]      # is np.eye(n)
```

Two things still make the library versions worth using.

**`np.diag` is two functions wearing one name.** Hand it a vector and it *builds* a diagonal matrix. Hand it a matrix and it *extracts* the diagonal. Convenient, and genuinely confusing: `np.diag(np.diag(M))` zeroes everything off the diagonal.

**The diagonal generalises to a batch.** `np.diagonal(t, axis1=-2, axis2=-1)` takes the diagonal of every matrix in a stack. In lesson 34's notation that's `einsum('...ii->...i')`, which is the same "index repeated within one operand" rule stated once.

Triangular masks matter more than they look. The causal mask in a transformer is `np.tril(np.ones((T, T), dtype=bool))`.

---

## Relationship to Cognitive Verb

```text
Structure
    ↓
Identity and Diagonal
```

Related verbs:

- Mark the diagonal
- Build structure
- Mask by index order
- Extract the trace
- Construct a neutral element

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Identity|square|`np.eye(n)`, `np.identity(n)`|
|Rectangular / offset|flexible|`np.eye(n, m, k=1)`|
|Build from a vector|1-D in|`np.diag(v)`|
|Extract to a vector|2-D in|`np.diag(M)` — the **same** function|
|Batched extract|any rank|`np.diagonal(t, axis1=-2, axis2=-1)`|
|...as einsum|one rule|`np.einsum('...ii->...i', t)`|
|Trace|sum of the diagonal|`np.trace(M)`, `einsum('...ii->...')`|
|Lower / upper triangle|masks|`np.tril(M)`, `np.triu(M, k=1)`|
|Causal mask|transformers|`np.tril(np.ones((T,T), dtype=bool))`|
|Write the diagonal|in place|`np.fill_diagonal(M, v)`|
|By predicate|the general form|`np.arange(n)[:,None] == np.arange(n)`|

---

## Common Uses

- The neutral element for matrix products
- Attention causal masks
- Covariance and precision matrices
- Excluding self-pairs in a distance matrix
- Extracting per-sample variances
- Triangular solves and decompositions
- Adjacency matrices with no self-loops
- Scaling matrices

---

## Hidden Interview Problems

- Build an n×n identity matrix
- Extract the diagonal of a matrix
- Compute the trace without a loop
- Build a lower-triangular mask
- Zero the diagonal of a distance matrix
- Extract the diagonal of every matrix in a batch
- Construct a diagonal matrix from a vector

---

## Recognition Clues

If you hear...

- "identity matrix..."
- "the diagonal..."
- "trace..."
- "causal / lower-triangular mask..."
- "exclude self-comparisons..."
- "diagonal covariance..."

...think **Identity and Diagonal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Underlying rule|A predicate on index order: `i == j`, `i >= j`, …|
|`np.eye(n)`|Square identity, `float64`|
|`np.eye(n, m, k)`|Rectangular, offset diagonal|
|`np.diag(1-D)`|**Builds** a matrix|
|`np.diag(2-D)`|**Extracts** a vector|
|`M.diagonal()`|A **read-only view**|
|Batched|`np.diagonal(..., axis1=-2, axis2=-1)`|
|Einsum form|`'...ii->...i'` (values), `'...ii->...'` (trace)|
|`np.tril` / `np.triu`|Zero out one triangle; `k` shifts the boundary|
|In-place write|`np.fill_diagonal`|

---

## Python Recipe Book

```python
# ============================================
# The identity

import numpy as np

np.eye(3)
# => array([[1., 0., 0.],
#           [0., 1., 0.],
#           [0., 0., 1.]])

np.eye(3).dtype             # => float64      note: NOT int
np.eye(3, dtype=int)
# => array([[1, 0, 0],
#           [0, 1, 0],
#           [0, 0, 1]])

np.array_equal(np.identity(3), np.eye(3))       # => True
#   `identity` is `eye` without the extra parameters.

# eye is more flexible than identity:
np.eye(3, 4)
# => array([[1., 0., 0., 0.],
#           [0., 1., 0., 0.],
#           [0., 0., 1., 0.]])      rectangular

np.eye(3, k=1)
# => array([[0., 1., 0.],
#           [0., 0., 1.],
#           [0., 0., 0.]])          the SUPERdiagonal

np.eye(3, k=-1)
# => array([[0., 0., 0.],
#           [1., 0., 0.],
#           [0., 1., 0.]])          the SUBdiagonal
#
# k>0 shifts up-right, k<0 down-left. `eye(n, k=1)` is
# the "shift by one" operator — it moves a vector's
# elements when you multiply by it.

# ============================================
# np.diag DOES TWO DIFFERENT THINGS

v = np.array([1, 2, 3])
M = np.arange(9).reshape(3, 3)

np.diag(v)                  # 1-D in -> 2-D out: BUILD
# => array([[1, 0, 0],
#           [0, 2, 0],
#           [0, 0, 3]])

np.diag(M)                  # 2-D in -> 1-D out: EXTRACT
# => array([0, 4, 8])
#
# the SAME function. Which behaviour you get depends on
# the rank of the input, which is unusual in NumPy and
# worth being explicit about in your own code.

np.diag(np.diag(M))
# => array([[0, 0, 0],
#           [0, 4, 0],
#           [0, 0, 8]])
#   extract, then rebuild — this zeroes the off-diagonal.
#   A neat idiom, and a confusing one if unintentional.

np.diag(M, k=1)             # => array([1, 5])       superdiagonal
np.diag(M, k=-1)            # => array([3, 7])       subdiagonal

np.diag(v, k=1).shape       # => (4, 4)
#   building with an offset grows the matrix to fit.

np.diagflat([[1, 2], [3, 4]])
# => array([[1, 0, 0, 0],
#           [0, 2, 0, 0],
#           [0, 0, 3, 0],
#           [0, 0, 0, 4]])
#   flattens first, then builds — unambiguous, unlike diag.

# ============================================
# .diagonal() — a READ-ONLY view

M.diagonal()                            # => array([0, 4, 8])
np.shares_memory(M, M.diagonal())       # => True     a view!
M.diagonal().flags['WRITEABLE']         # => False
#
# a diagonal IS regularly strided (step = cols + 1), so
# it can be a view — lesson 4 again. But NumPy marks it
# read-only. To WRITE the diagonal:
f = np.zeros((3, 3))
np.fill_diagonal(f, 5)
f
# => array([[5., 0., 0.],
#           [0., 5., 0.],
#           [0., 0., 5.]])

# ============================================
# BATCHED — the diagonal of every matrix in a stack

T3 = np.arange(2*3*3).reshape(2, 3, 3)
T3.shape                    # => (2, 3, 3)

np.diagonal(T3, axis1=-2, axis2=-1)
# => array([[ 0,  4,  8],
#           [ 9, 13, 17]])
np.diagonal(T3, axis1=-2, axis2=-1).shape       # => (2, 3)

np.einsum('...ii->...i', T3)
# => array([[ 0,  4,  8],
#           [ 9, 13, 17]])
np.array_equal(np.diagonal(T3, axis1=-2, axis2=-1),
               np.einsum('...ii->...i', T3))                # => True
#
# lesson 34's rule 3 — "an index repeated within one
# operand gives the diagonal" — covers the batched case
# for free. The `...` handles any leading axes.

# ============================================
# Trace

np.trace(M)                 # => 12
int(np.diag(M).sum())       # => 12          the same thing

np.trace(T3, axis1=-2, axis2=-1)            # => array([12, 39])
np.einsum('...ii->...', T3)                 # => array([12, 39])
#
# drop the `i` from the output and it is summed instead
# of kept — one character between "the diagonal" and
# "the trace".

# ============================================
# TRIANGULAR MASKS

np.tril(M)
# => array([[0, 0, 0],
#           [3, 4, 0],
#           [6, 7, 8]])      keep i >= j

np.triu(M)
# => array([[0, 1, 2],
#           [0, 4, 5],
#           [0, 0, 8]])      keep i <= j

np.triu(M, k=1)
# => array([[0, 1, 2],
#           [0, 0, 5],
#           [0, 0, 0]])      STRICTLY upper — excludes the diagonal

np.tri(3)
# => array([[1., 0., 0.],
#           [1., 1., 0.],
#           [1., 1., 1.]])   the mask itself, not applied to anything

# index form, for assignment:
np.tril_indices(3)
# => (array([0, 1, 1, 2, 2, 2]), array([0, 0, 1, 0, 1, 2]))

mm = M.copy()
mm[np.triu_indices(3, k=1)] = 0
mm
# => array([[0, 0, 0],
#           [3, 4, 0],
#           [6, 7, 8]])      == np.tril(M)

# ============================================
# THE APPLICATION: a causal mask

T = 4
mask = np.tril(np.ones((T, T), dtype=bool))
mask
# => array([[ True, False, False, False],
#           [ True,  True, False, False],
#           [ True,  True,  True, False],
#           [ True,  True,  True,  True]])
#
# position i may attend to positions j <= i. That is the
# whole of causal masking.

scores = np.zeros((3, 3))
np.where(np.tril(np.ones((3, 3), dtype=bool)), scores, -np.inf)
# => array([[  0., -inf, -inf],
#           [  0.,   0., -inf],
#           [  0.,   0.,   0.]])
#
# `-inf` before the softmax makes those positions
# exactly zero afterwards (lesson 21). Combine with
# lesson 32's attention and the mechanism is complete.

# ============================================
# Excluding self-pairs

pts = np.array([[0., 0.], [3., 4.], [6., 8.]])
d = np.sqrt(((pts[:, None, :] - pts[None, :, :]) ** 2).sum(-1))
np.fill_diagonal(d, np.inf)
d.argmin(axis=1)            # => array([1, 0, 1])
#
# without `fill_diagonal` every point is its own nearest
# neighbour at distance 0 (lesson 23). The diagonal of a
# pairwise matrix is almost always the self-comparison,
# and almost always needs removing.

# ============================================
# ...AND THE PREDICATE FORM UNDERNEATH IT ALL

n = 4
i = np.arange(n)[:, None]
j = np.arange(n)[None, :]

(i == j).astype(int)
# => array([[1, 0, 0, 0],
#           [0, 1, 0, 0],
#           [0, 0, 1, 0],
#           [0, 0, 0, 1]])
np.array_equal((i == j).astype(int), np.eye(n, dtype=int))      # => True

(i >= j).astype(int)
# => array([[1, 0, 0, 0],
#           [1, 1, 0, 0],
#           [1, 1, 1, 0],
#           [1, 1, 1, 1]])
np.array_equal((i >= j).astype(int), np.tri(n, dtype=int))      # => True
#
# every function in this lesson is a comparison between
# coordinate tensors (lesson 37). The library names are
# convenient; the predicate is the definition — and it
# extends to cases with no library function, like
# `abs(i - j) <= 2` for a banded mask.

np.array_equal((abs(i - j) <= 1).astype(int),
               np.eye(n, k=-1, dtype=int) + np.eye(n, dtype=int)
               + np.eye(n, k=1, dtype=int))                     # => True

# ============================================
# Compare — the four generation patterns

np.zeros((3, 3))                        # a constant        lesson 35
np.arange(9).reshape(3, 3)              # a sequence        lesson 36
np.indices((3, 3)).sum(axis=0)          # a coordinate f    lesson 37
np.eye(3)                               # structure         this lesson

# ...and the last three are all lesson 37 underneath:
np.array_equal(np.eye(3, dtype=int),
               (np.indices((3, 3))[0] == np.indices((3, 3))[1]).astype(int))
# => True
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the identity|`np.eye(n)` — it's `float64`|
|an offset diagonal|`np.eye(n, k=1)`|
|to **build** from a vector|`np.diag(v)`|
|to **extract** to a vector|`np.diag(M)` — same function!|
|unambiguous building|`np.diagflat(v)`|
|a batched diagonal|`np.einsum('...ii->...i', t)`|
|a trace|`np.einsum('...ii->...', t)` — drop the `i`|
|a causal mask|`np.tril(np.ones((T,T), dtype=bool))`|
|to write the diagonal|`np.fill_diagonal` — `.diagonal()` is read-only|
|anything else|the predicate: `i == j`, `i >= j`, `abs(i-j) <= k`|

---

## Key Insight

**These are all predicates on index order, and the library functions are names for the common ones.**

```text
i == j        np.eye
i >= j        np.tri / np.tril
i <  j        np.triu(k=1)
abs(i-j) <= k no function — write the predicate
```

Part 2 built the identity as `int(r == c)`; lesson 37 made coordinate tensors available at any rank; this lesson is where that pays off. When there is a named function, use it. When there is not — a banded mask, a checkerboard-and-diagonal combination — the comparison between coordinate tensors always works.

Three specifics worth remembering:

1. **`np.diag` is overloaded on rank.** 1-D in builds a matrix; 2-D in extracts a vector. `np.diag(np.diag(M))` therefore zeroes the off-diagonal — useful when deliberate, baffling otherwise. `np.diagflat` builds unambiguously.
    
2. **`.diagonal()` is a read-only view.** A diagonal is regularly strided (step `cols + 1`), so it *can* be a view — lesson 4's machinery again — but NumPy forbids writing through it. Use `np.fill_diagonal`.
    
3. **The batched forms are einsum one-liners.** `'...ii->...i'` for the diagonals, `'...ii->...'` for the traces. One character — whether `i` survives into the output — separates them, which is lesson 34's rule set doing exactly what it promised.
    

And the two applications that come up constantly: a **causal mask** is `np.tril(np.ones((T,T), dtype=bool))`, and any **pairwise matrix** needs its diagonal removed before an argmin, because self-comparison always wins.

---

## The Generation Section, Complete

|Lesson|Built from|Underlying form|
|---|---|---|
|35 Zeros / Ones / Full|a shape and a constant|`f(i,j,…) = c`|
|36 Arange / Linspace|a range|`f(i) = start + i·step`|
|37 Meshgrid|coordinates|`f(i,j,k) = …`|
|**38 Identity / Diagonal**|index predicates|`f(i,j) = (i == j)`|

```text
   every generated tensor is  f(coordinates)
   35  ignores them
   36  uses one
   37  supplies them all
   38  compares them
```

---

## Part 3 Complete

Thirty-eight lessons, ten sections, one recurring question: **which axis?**

|Section|The question|
|---|---|
|01 Foundations|How big, which direction, where in memory?|
|02 Traversal|At what granularity do I walk it?|
|03 Slicing|Which cells, and do I get a view or a copy?|
|04 Structure|Does the flat order change?|
|05 Broadcasting|Which axes line up?|
|06 Reduction|Which axis collapses — and do I keep the slot?|
|07 Combination|Grow an axis, or create one?|
|08 Windows|Overlapping or partitioned?|
|09 Contraction|Which axis is shared?|
|10 Generation|What is each cell, given its coordinates?|

Four ideas carried the whole part:

- **The shape tuple is the type.** Predict it before running the code, and most bugs never happen.
    
- **Strides make things free.** Reshape, transpose, slicing, broadcasting and sliding windows are all metadata edits. Knowing which operations touch the buffer is what separates code that runs from code that runs fast.
    
- **`keepdims` and `None` are the same idea** — a size-1 axis is a *free* placeholder, and putting it in the right place is how you control alignment.
    
- **Name the axis, not the loop.** `axis=k`, `swapaxes(-1,-2)`, `'bij,bjk->bik'` — every one of them survives a change of rank, where a hand-written loop does not.
    

```txt
Part 1   1D Sequence Patterns     ✔
Part 2   Matrix Patterns          ✔
Part 3   Tensor Patterns          ✔  ← complete
Part 4   Tree Traversal Patterns
Part 5   Graph Traversal Patterns
```

> **Mental shift:** part 1 taught you to think in sequences and part 2 in grids, and both were about *writing the loop well*. Part 3 is about not writing it at all: describe the shape of the computation and let the library find the loop. The skill that took its place is shape prediction. If you can say what `t.shape` will be before you hit enter, you've understood the operation.
