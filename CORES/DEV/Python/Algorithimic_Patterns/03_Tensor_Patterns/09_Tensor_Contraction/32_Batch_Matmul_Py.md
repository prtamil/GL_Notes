# 32. Batch Matmul

## Mental Model

`@` on rank 3+ does exactly one thing, and the rule is worth memorising verbatim:

> **The last two axes are the matrix. Every leading axis is a batch, and batches broadcast.**

```text
(2, 3, 4) @ (2, 4, 5)  ->  (2, 3, 5)
 ↑  └───┘    ↑  └───┘       ↑  └───┘
 batch  matrix              batch, matrix
```

`out[b] == A[b] @ B[b]` — two independent matrix products, computed in one call.

And because the batch axes *broadcast* (lesson 17), a single matrix applies to a whole batch with no tiling:

```text
(2, 3, 4) @ (4, 5)  ->  (2, 3, 5)      the same (4,5) used twice
```

That is a linear layer applied to a batch, and it costs nothing extra — the weight matrix is not copied.

Two traps follow directly from "the last two axes are the matrix":

- **`.T` is wrong.** On rank 3 it reverses *all* axes (lesson 14), giving `(4,3,2)` where you wanted `(2,4,3)`. The correct batch transpose is `swapaxes(-1, -2)`.
    
- **`np.dot` is wrong.** It has no batch concept and takes an outer product over the free axes: `(2,3,4)` with `(2,4,5)` gives `(2,3,2,5)` instead of `(2,3,5)`.
    

---

## Relationship to Cognitive Verb

```text
Contract Per Batch
        ↓
Batch Matmul
```

Related verbs:

- Apply to each
- Contract per sample
- Multiply matrix-wise
- Project a batch
- Compose in parallel

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Batched product|the operator|`A @ B`|
|Same weights for all|broadcasting|`batch @ W`|
|Batch transpose|**not** `.T`|`A.swapaxes(-1, -2)`|
|Batched matrix–vector|1-D promotion|`A @ v`|
|...keeping the axis|explicit column|`A @ v[..., None]`|
|Broadcasting batches|different leading shapes|`(1,3,…) @ (2,1,…)`|
|Attention scores|Q·Kᵀ|`Q @ K.swapaxes(-1,-2)`|
|Named version|explicit|`np.einsum('bij,bjk->bik', A, B)`|
|**Avoid**|no batch semantics|`np.dot`, `np.tensordot`|

---

## Common Uses

- Applying a linear layer to a batch
- Scaled dot-product attention
- Per-sample coordinate transforms
- Batched least squares
- Multi-head attention (batch = `(N, heads)`)
- Rotating a batch of point clouds
- Applying per-sample matrices in a physics simulation

---

## Hidden Interview Problems

- Multiply a batch of matrices pairwise
- Apply one weight matrix to a batch of inputs
- Implement scaled dot-product attention
- Transpose the last two axes of a rank-4 tensor
- Explain why `A @ A.T` fails on a batch
- Explain why `np.dot` gives the wrong shape

---

## Recognition Clues

If you hear...

- "for each sample in the batch, multiply..."
- "batched matmul / bmm..."
- "attention scores..."
- "apply the weights to the batch..."
- "per-head..."

...think **Batch Matmul**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Matrix axes|The **last two**|
|Leading axes|Batch — **broadcast**|
|Rule|`(…, n, k) @ (…, k, m) → (…, n, m)`|
|One matrix, many samples|`(b, n, k) @ (k, m)` works|
|Batch transpose|`swapaxes(-1, -2)` — **not** `.T`|
|`np.dot`|Wrong — no batch concept|
|`np.tensordot`|Wrong — no batch concept (lesson 33)|
|1-D operand|Promoted then squeezed|
|Common Domains|Deep learning, geometry, simulation|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember
#
#   last two axes = the matrix; the rest is batch

import numpy as np

Ab = np.arange(2*3*4).reshape(2, 3, 4)
Bb = np.arange(2*4*5).reshape(2, 4, 5)

(Ab @ Bb).shape             # => (2, 3, 5)
#
#   (2, 3, 4) @ (2, 4, 5)  ->  (2, 3, 5)
#    ↑  └──┘      ↑  └──┘       ↑  └──┘
#   batch matrix  batch matrix  batch result

# it really is one matmul per batch element:
np.allclose((Ab @ Bb)[0], Ab[0] @ Bb[0])    # => True
np.allclose((Ab @ Bb)[1], Ab[1] @ Bb[1])    # => True

# ============================================
# THE BATCH AXES BROADCAST

Bs = np.arange(4*5).reshape(4, 5)           # ONE matrix, no batch

(Ab @ Bs).shape             # => (2, 3, 5)
np.allclose((Ab @ Bs)[1], Ab[1] @ Bs)       # => True
#
#   (2, 3, 4) @    (4, 5)  ->  (2, 3, 5)
#
# the same (4,5) matrix is used for every batch element,
# and it is NOT tiled — broadcasting (lesson 17) handles
# it with stride 0. This is a linear layer applied to a
# batch, and it is the most common matmul in ML.

# batch axes broadcast against each other too:
A4 = np.ones((1, 3, 4, 5))
B4 = np.ones((2, 1, 5, 6))
(A4 @ B4).shape             # => (2, 3, 4, 6)
#
#   batch (1,3) and (2,1)  ->  (2,3)     ordinary broadcasting
#   matrix (4,5) @ (5,6)   ->  (4,6)     ordinary matmul
#
# the two rules are applied independently: broadcasting
# to the leading axes, matmul to the last two.

# ============================================
# TRAP 1: .T is not the batch transpose

Ab.T.shape                  # => (4, 3, 2)      reverses ALL axes

try:
    Ab @ Ab.T
except ValueError as e:
    print(str(e)[:55])
# matmul: Input operand 1 has a mismatch in its core dim
#
# (2,3,4) @ (4,3,2): the batch axes 2 and 4 disagree, and
# so do the inner dimensions. Lesson 14 warned about this;
# here is the concrete failure.

(Ab @ Ab.swapaxes(-1, -2)).shape            # => (2, 3, 3)
np.array_equal(Ab.swapaxes(-1, -2), Ab.transpose(0, 2, 1))      # => True
#
# `swapaxes(-1, -2)` is rank-agnostic: it works on (n,k),
# (b,n,k) and (b,h,n,k) alike. `.T` only means "matrix
# transpose" at rank 2.

# ============================================
# TRAP 2: np.dot has no batch concept

np.matmul(Ab, Bb).shape     # => (2, 3, 5)      correct
np.dot(Ab, Bb).shape        # => (2, 3, 2, 5)   every batch PAIR
#
# `np.dot` contracts the last axis of `a` with the
# second-to-last of `b` and takes an outer product over
# everything else — so batch 0 of A is combined with
# batch 1 of B as well. Quadratic in the batch size, and
# silent.
#
# `np.tensordot` behaves the same way (lesson 33).
# For batches: `@`, `np.matmul`, or `einsum`.

# ============================================
# 1-D operands are promoted, then squeezed

Mb = np.arange(2*3*4).reshape(2, 3, 4)
vb = np.arange(4)

(Mb @ vb).shape             # => (2, 3)
#   the (4,) becomes a column (4,1), giving (2,3,1),
#   and the added axis is removed again.

(Mb @ vb[..., None]).shape  # => (2, 3, 1)
#   keep the axis by writing the column explicitly —
#   necessary when the result feeds another matmul.

# ============================================
# THE APPLICATION: scaled dot-product attention
#
# Two batch matmuls with a softmax between them.

rng = np.random.default_rng(0)
N, T, d = 2, 3, 4                   # batch, sequence length, dim

Q = rng.normal(size=(N, T, d))
K = rng.normal(size=(N, T, d))
V = rng.normal(size=(N, T, d))

scores = Q @ K.swapaxes(-1, -2) / np.sqrt(d)
scores.shape                # => (2, 3, 3)
#
#   (N,T,d) @ (N,d,T) -> (N,T,T)
#   the FEATURE axis d is contracted; every query is
#   scored against every key. That is lesson 19's
#   all-pairs, done as a contraction.

e = np.exp(scores - scores.max(axis=-1, keepdims=True))
attn = e / e.sum(axis=-1, keepdims=True)            # lesson 21
attn.shape                  # => (2, 3, 3)
np.allclose(attn.sum(axis=-1), 1)                   # => True

out = attn @ V
out.shape                   # => (2, 3, 4)
#
#   (N,T,T) @ (N,T,d) -> (N,T,d)
#   now the KEY axis is contracted — a weighted sum of
#   value vectors.
#
# the whole mechanism is: contract the feature axis to
# get scores, normalise, contract the key axis to get
# outputs. Two lines, both batch matmuls.

# multi-head is the same code with one more batch axis:
#   Q: (N, H, T, d_head)   ->  scores: (N, H, T, T)
# nothing in the expressions changes, because everything
# before the last two axes is batch.

# ============================================
# Practical: a linear layer over a sequence

x = np.ones((8, 20, 64))            # batch 8, 20 steps, 64 features
W = np.ones((64, 128))

(x @ W).shape               # => (8, 20, 128)
#
# no reshape needed. Compare with lesson 13's
# merge-operate-split — that was necessary when the
# operation was NOT a matmul. Matmul broadcasts the
# batch axes itself.

# ============================================
# Practical: per-sample transforms

pts = np.ones((5, 100, 3))          # 5 clouds of 100 points in 3-D
R = np.stack([np.eye(3) for _ in range(5)])     # a rotation per cloud
R.shape                     # => (5, 3, 3)

(pts @ R.swapaxes(-1, -2)).shape    # => (5, 100, 3)
#
# each cloud gets its OWN matrix — the batch axes match
# rather than broadcasting. Note the transpose: points
# are rows, so `p @ Rᵀ` applies R to each row vector.

# ============================================
# Compare

Ab @ Bb                             # (2,3,4)@(2,4,5) -> (2,3,5)   batched
Ab @ Bs                             # (2,3,4)@(4,5)   -> (2,3,5)   broadcast
np.dot(Ab, Bb)                      # (2,3,2,5)                    WRONG
Ab.T                                # (4,3,2)                      WRONG
Ab.swapaxes(-1, -2)                 # (2,4,3)                      right
np.einsum('bij,bjk->bik', Ab, Bb)   # the same thing, named

np.array_equal(np.einsum('bij,bjk->bik', Ab, Bb), Ab @ Bb)      # => True
np.array_equal(np.einsum('...ij,...jk->...ik', Ab, Bb), Ab @ Bb)    # => True
#
# the `...` form is exactly matmul's rule, written out:
# "whatever the leading axes, contract j".
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the rule|last two axes are the matrix; the rest broadcasts|
|a batched product|`A @ B`|
|one matrix for all samples|`batch @ W` — free, no tiling|
|a batch transpose|`swapaxes(-1, -2)`|
|**not** a batch transpose|`.T` — it reverses everything|
|**not** batched at all|`np.dot`, `np.tensordot`|
|attention scores|`Q @ K.swapaxes(-1,-2)`|
|a kept vector axis|`v[..., None]`|
|the rule spelled out|`einsum('...ij,...jk->...ik', A, B)`|

---

## Key Insight

**`@` splits the shape in two: the last two axes are a matrix, everything before them is a batch.** Then it applies matmul to the first part and *broadcasting* to the second — two rules you already know, composed.

```text
(1,3, 4,5) @ (2,1, 5,6)  ->  (2,3, 4,6)
 └───┘        └───┘           └───┘        broadcasting
       └─┘          └─┘             └─┘    matmul
```

The consequence that matters most: **one weight matrix applies to an entire batch for free.** `batch @ W` broadcasts `W` across the batch with stride 0 — no tiling, no reshape, no loop. That is why a linear layer over a `(N, T, C)` sequence needs no `merge-operate-split` (lesson 13); matmul already handles the leading axes.

Two errors are worth guarding against explicitly, because both are silent or confusingly worded:

1. **`.T` is not the batch transpose.** At rank 3 it reverses *all* axes. Use `swapaxes(-1, -2)`, which is rank-agnostic and reads as "transpose the matrix part".
    
2. **`np.dot` has no batch concept.** `(2,3,4)` with `(2,4,5)` gives `(2,3,2,5)` — every combination of batch elements, quadratic in the batch size, no error. Lesson 33 shows `tensordot` shares the problem. For anything batched, use `@` or `einsum`.
    

Attention is the pattern's showcase: contract the *feature* axis to score every query against every key, normalise, then contract the *key* axis to produce outputs. Two batch matmuls, and multi-head requires no code change at all — one more leading axis is just more batch.

---

## Matmul vs Dot vs Tensordot

|Input|`@` / `matmul`|`np.dot`|
|---|---|---|
|`(n,k)`, `(k,m)`|`(n,m)`|`(n,m)` — same|
|`(b,n,k)`, `(b,k,m)`|**`(b,n,m)`**|`(b,n,b,m)`|
|`(b,n,k)`, `(k,m)`|**`(b,n,m)`**|`(b,n,m)` — same here|
|scalar|**raises**|allowed|

```text
   matmul:  batch is a BATCH
   dot:     batch is just another free axis -> outer product
```

> **Mental shift:** lesson 31's matmul was a single linear-algebra operation. Adding leading axes turns it into "do this to every item", which is the shape of nearly all deep-learning code — and the reason `@` is written with the *matrix* axes last. Put the axes you want contracted at the end, and the batch takes care of itself.
