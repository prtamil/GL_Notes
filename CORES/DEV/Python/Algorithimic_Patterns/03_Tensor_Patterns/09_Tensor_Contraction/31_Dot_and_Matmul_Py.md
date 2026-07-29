# 31. Dot and Matmul

## Mental Model

**Contraction** is the operation this whole section is about: multiply two tensors elementwise along a **shared** axis, then **sum that axis away**.

```text
A  (2, 3)
B     (3, 4)
       ↑ shared — it disappears
   -> (2, 4)
```

`A @ B` pairs the last axis of `A` with the first axis of `B`, multiplies, and sums. The shared dimension has to match, and it doesn't show up in the output. That's what "contracted" means.

Set it beside the two operations you already know:

```text
A * B      elementwise  — shapes align, nothing is summed
A.sum(1)   reduction    — an axis is summed, no second operand
A @ B      contraction  — an axis is summed BETWEEN two operands
```

Contraction is the missing third one: a reduction that eats an axis from each of two tensors.

One thing to settle right now, because it causes real bugs: **`np.dot` and `@` agree at rank ≤ 2 and diverge above it.**

```text
(2,3,4) @ (2,4,3)        ->  (2, 3, 3)        batched matmul
np.dot((2,3,4),(2,4,3))  ->  (2, 3, 2, 3)     something else entirely
```

Use `@` / `np.matmul`. `np.dot` at rank 3+ takes an outer product over the non-contracted axes, which is almost never what you want.

---

## Relationship to Cognitive Verb

```text
Contract
   ↓
Dot and Matmul
```

Related verbs:

- Contract
- Multiply and sum
- Combine along a shared axis
- Project
- Compose

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Matrix product|the operator|`A @ B`|
|Same, function form|explicit|`np.matmul(A, B)`|
|Inner product|1-D · 1-D|`u @ v` — a scalar|
|Matrix–vector|1-D on the right|`A @ v`|
|Vector–matrix|1-D on the left|`v @ A`|
|Outer product|no contraction|`np.outer(u, v)` (lesson 19)|
|Elementwise|**not** contraction|`A * B`|
|Transpose to align|fix a mismatch|`A @ B.T`|
|**Avoid**|different at rank 3+|`np.dot`|
|Cost control|association order|`(X@Y)@Z` vs `X@(Y@Z)`|

---

## Common Uses

- A linear layer: `x @ W`
- Projecting data onto a basis
- Change of coordinates
- Covariance: `X.T @ X`
- Composing transformations
- Weighted sums of feature vectors
- Similarity scores between embeddings

---

## Hidden Interview Problems

- Multiply two matrices without loops
- Compute a covariance matrix
- Apply a linear transformation to a batch of vectors
- Explain the difference between `*` and `@`
- Explain why `np.dot` differs from `matmul` on 3-D input
- Choose the cheaper association order for a chain of products

---

## Recognition Clues

If you hear...

- "matrix multiply..."
- "linear layer / projection..."
- "dot product..."
- "inner product / similarity..."
- "shapes not aligned for matmul..."

...think **Dot and Matmul**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Operation|Multiply along a shared axis, then sum it|
|Rule|`(n, k) @ (k, m) → (n, m)`|
|The shared axis|**Disappears**|
|1-D on the right|Treated as a column, then squeezed|
|1-D on the left|Treated as a row, then squeezed|
|1-D · 1-D|A scalar|
|`np.dot` at rank 3+|**Different** — outer over the free axes|
|Scalars|`@` rejects them; `np.dot` accepts|
|Associativity|Same result, **very** different cost|
|Common Domains|Linear algebra, ML, geometry|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember

import numpy as np

A = np.arange(6).reshape(2, 3)
B = np.arange(12).reshape(3, 4)

A @ B
# => array([[20, 23, 26, 29],
#           [56, 68, 80, 92]])
(A @ B).shape               # => (2, 4)
#
#   (2, 3) @ (3, 4)  ->  (2, 4)
#       ↑     ↑
#       the 3s must match, and the 3 is GONE
#
# element [i][j] = sum over k of A[i,k] * B[k,j]

try:
    B @ A
except ValueError as e:
    print(str(e)[:55])
# matmul: Input operand 1 has a mismatch in its core dim
#
# (3,4) @ (2,3) — the 4 and the 2 do not match. Matmul is
# NOT commutative, and usually not even legal both ways.

# ============================================
# `*` IS NOT `@`

C = np.arange(6).reshape(2, 3)

A * C                       # elementwise, needs the SAME shape
# => array([[ 0,  1,  4],
#           [ 9, 16, 25]])
(A * C).shape               # => (2, 3)

# A @ C would raise: (2,3) @ (2,3) has 3 against 2.
#
#   *   aligns shapes, sums NOTHING          (lesson 17)
#   @   pairs one axis, sums IT AWAY
#
# this is the single most common beginner confusion, and
# it usually raises — except when the shapes happen to
# be square, where both run and give different answers.

# ============================================
# The 1-D cases

u = np.array([1, 2, 3])
v = np.array([4, 5, 6])

u @ v                       # => 32          a SCALAR
np.shape(u @ v)             # => ()
#   1*4 + 2*5 + 3*6 — the inner product. Both axes
#   contracted, nothing left.

np.dot(u, v)                # => 32          same for 1-D
np.inner(u, v)              # => 32

A @ u                       # => array([ 8, 26])
(A @ u).shape               # => (2,)
#   the 1-D operand on the RIGHT is treated as a column
#   (3,1), giving (2,1), then the added axis is removed.

w = np.array([1, 1])
w @ A                       # => array([3, 5, 7])
(w @ A).shape               # => (3,)
#   on the LEFT it becomes a row (1,2), giving (1,3),
#   then squeezed.
#
# so `A @ u` and `u @ A` contract DIFFERENT axes. The
# promotion is convenient and silent; when in doubt,
# write the axis explicitly with `u[:, None]`.

np.array_equal(u @ A.T, A @ u)              # => True

# and the operation that does NOT contract:
np.outer(u, v).shape        # => (3, 3)      lesson 19
#
#   inner: sum over the shared axis   -> scalar
#   outer: keep both axes             -> matrix

# ============================================
# THE TRAP: np.dot at rank 3+

T1 = np.arange(24).reshape(2, 3, 4)
T2 = np.arange(24).reshape(2, 4, 3)

(T1 @ T2).shape             # => (2, 3, 3)      batched matmul
np.matmul(T1, T2).shape     # => (2, 3, 3)      same
np.dot(T1, T2).shape        # => (2, 3, 2, 3)   DIFFERENT
#
#   matmul : the last two axes are a matrix, leading
#            axes are a BATCH (lesson 32)
#   dot    : contracts the last axis of a with the
#            SECOND-TO-LAST of b, and takes an OUTER
#            product over everything else
#
# `np.dot` on a batch of matrices computes every
# combination of batch elements — 2x the memory here,
# and quadratic in the batch size. It does not raise.
#
# RULE: use `@` or `np.matmul`. Reserve `np.dot` for
# 1-D inner products, where it is unambiguous.

# one more difference:
np.dot(A, 3).shape          # => (2, 3)      scalar allowed
try:
    np.matmul(A, 3)
except ValueError as e:
    print(str(e)[:50])
# matmul: Input operand 1 does not have enough dimensions
#
# matmul refuses scalars — use `A * 3`.

# ============================================
# The identity

I = np.eye(3)
np.allclose(A @ I, A)       # => True
#
# lesson 28 of part 2 made this the point of the identity
# matrix; here it is the neutral element of contraction.

# ============================================
# ASSOCIATIVITY IS FREE; COST IS NOT

X = np.ones((100, 2))
Y = np.ones((2, 100))
Z = np.ones((100, 2))

((X @ Y) @ Z).shape         # => (100, 2)
(X @ (Y @ Z)).shape         # => (100, 2)
np.allclose((X @ Y) @ Z, X @ (Y @ Z))       # => True

# same answer — but look at the intermediates:
(X @ Y).shape               # => (100, 100)     10,000 elements
(Y @ Z).shape               # => (2, 2)         4 elements
#
# `(X@Y)@Z` builds a 100x100 intermediate.
# `X@(Y@Z)` builds a 2x2 one.
#
# Both are correct. On real sizes this is the difference
# between fitting in cache and not — and with three or
# more operands, choosing the order is a real
# optimisation (lesson 34's `optimize=True` does it for
# you).

# ============================================
# Practical: a linear layer

x = np.arange(12, dtype=float).reshape(4, 3)    # 4 samples, 3 features
W = np.ones((3, 5))                             # 3 in, 5 out
b = np.arange(5, dtype=float)                   # bias

out = x @ W + b
out.shape                   # => (4, 5)
#
#   (4,3) @ (3,5) -> (4,5), then the (5,) bias
#   broadcasts across the rows (lesson 18).
#
# the feature axis is contracted; the sample axis is not.
# That asymmetry is what makes a layer "apply the same
# weights to every sample".

# ============================================
# Practical: covariance / Gram matrix

Xc = x - x.mean(axis=0, keepdims=True)          # centre (lesson 21)
cov = Xc.T @ Xc / (len(Xc) - 1)
cov.shape                   # => (3, 3)         feature x feature
np.allclose(cov, cov.T)     # => True           symmetric, as it must be

gram = x @ x.T
gram.shape                  # => (4, 4)         sample x sample
#
# `X.T @ X` contracts the SAMPLE axis -> a feature-space
# matrix. `X @ X.T` contracts the FEATURE axis -> a
# sample-space matrix. Which axis you contract decides
# what the result means.

# ============================================
# Compare

A * B                       # elementwise    — nothing summed
A.sum(axis=1)               # reduction      — one operand
A @ B                       # contraction    — one shared axis summed
np.outer(u, v)              # outer          — nothing summed, ranks added
np.einsum('ij,jk->ik', A, B)    # the same contraction, named (lesson 34)

np.array_equal(A @ B, np.einsum('ij,jk->ik', A, B))     # => True
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a matrix product|`A @ B`|
|the rule|`(n,k) @ (k,m) → (n,m)`; the `k` disappears|
|elementwise instead|`A * B`|
|an inner product|`u @ v` — a scalar|
|**not** `np.dot`|it differs from `@` at rank 3+|
|scalars|`A * 3`, not `matmul`|
|a covariance|`X.T @ X` — contracts the sample axis|
|a Gram matrix|`X @ X.T` — contracts the feature axis|
|a cheaper chain|reassociate; check the intermediate shapes|

---

## Key Insight

**Contraction is a reduction shared between two operands.** Elementwise operations align shapes and sum nothing; reductions sum an axis of one tensor; contraction sums an axis that *both* tensors have.

```text
(n, k) @ (k, m)  ->  (n, m)
```

The `k` must match and it vanishes. Everything else in this section generalises that one sentence — batch axes in lesson 32, arbitrary axes in 33, arbitrary *names* in 34.

Three things worth fixing in memory:

1. **Use `@`, not `np.dot`.** They agree for rank ≤ 2 and diverge above it: `(2,3,4)` with `(2,4,3)` gives `(2,3,3)` under `matmul` and `(2,3,2,3)` under `dot`, because `dot` takes an outer product over the free axes. It does not raise — it silently computes every batch-pair combination.
    
2. **`*` and `@` are different operations**, and on square inputs both run. `A * B` aligns and multiplies; `A @ B` pairs one axis and sums it away.
    
3. **Which axis you contract decides the meaning.** `X.T @ X` is a feature×feature covariance; `X @ X.T` is a sample×sample Gram matrix. Same data, same operator, different question — the shapes are the only clue.
    

And a performance note that matters more than it looks: matrix products are **associative in value, not in cost**. `(X@Y)@Z` built a 100×100 intermediate where `X@(Y@Z)` built a 2×2. Lesson 34's `optimize=True` chooses for you.

---

## The Contraction Section

|Lesson|Contracts|Batch axes|Spelled by|
|---|---|---|---|
|**31 Dot and Matmul**|the last/first axis|—|`@`|
|32 Batch Matmul|the last two axes|**broadcast**|`@`|
|33 Tensordot|**any** axes|none|position|
|34 Einsum|any axes|any|**names**|

```text
   31   A @ B                     one shared axis
   32   A @ B, with a batch       leading axes broadcast
   33   tensordot(A, B, axes=…)   choose the axes
   34   einsum('ij,jk->ik', …)    name every axis
```

> **Mental shift:** parts 1 and 2 gave you `sum(a*b for a,b in zip(u,v))` and a triple loop for matrix multiply. The loop hasn't gone anywhere; it moved into BLAS. What you write instead is *which axis is shared*. Once contraction is your primitive, linear layers, covariance, attention and convolution are all the same operation with different axes picked out.
