# 33. Tensordot

## Mental Model

`@` always contracts the same axes: the last of the left operand against the second-to-last of the right. `np.tensordot` lets you **choose**.

```python
np.tensordot(a, b, axes=([1], [1]))     # contract a's axis 1 with b's axis 1
```

The rule for the output shape is simple and has no exceptions:

> **The contracted axes vanish. Every remaining axis of `a`, followed by every remaining axis of `b`, becomes an output axis.**

```text
a  (2, 3, 4)
b  (4, 3, 2)

axes=([2],[0])   contract 4 with 4   ->  (2, 3) + (3, 2)  ->  (2, 3, 3, 2)
axes=([1],[1])   contract 3 with 3   ->  (2, 4) + (4, 2)  ->  (2, 4, 4, 2)
axes=0           contract nothing    ->  (2,3,4) + (4,3,2) -> (2,3,4,4,3,2)
```

That last case is worth noticing. `axes=0` contracts nothing and gives you the **outer product**, so tensordot covers the whole range from "no contraction" to "full contraction" through one parameter.

And here's the limitation that tells you when *not* to reach for it:

> **Tensordot has no concept of a batch.**

Every non-contracted axis becomes an output axis, so a batch axis sitting in both operands turns up **twice**. `(2,3,4)` and `(2,4,5)` give you `(2,3,2,5)`, the same wrong answer `np.dot` produces, for the same reason. Batches need `@` (lesson 32) or `einsum` (lesson 34).

---

## Relationship to Cognitive Verb

```text
Contract Chosen Axes
         ↓
Tensordot
```

Related verbs:

- Contract by position
- Pair specific axes
- Sum over chosen dimensions
- Generalise the dot product

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Last of a, first of b|the default|`np.tensordot(a, b, axes=1)`|
|Last k with first k|a count|`np.tensordot(a, b, axes=k)`|
|Named axes|explicit pairs|`np.tensordot(a, b, axes=([i],[j]))`|
|Several axes at once|lists|`axes=([1,2],[0,3])`|
|No contraction|outer product|`axes=0`|
|Full contraction|scalar|`axes=([0,1],[0,1])`|
|Equivalent to matmul|rank 2|`axes=1`|
|**Not** batched|use something else|`@` or `einsum`|
|The named alternative|clearer|`np.einsum(...)`|

---

## Common Uses

- Contracting a specific axis of a multi-way array
- Applying a transform along one mode of a tensor
- Tensor decompositions (Tucker, CP)
- Physics and chemistry tensor algebra
- Contracting feature axes that are not last
- Multi-linear maps

---

## Hidden Interview Problems

- Contract two tensors along given axes
- Compute the Frobenius inner product of two matrices
- Apply a matrix along one mode of a 3-way tensor
- Compute an outer product of two tensors
- Explain why `tensordot` cannot do batched matmul

---

## Recognition Clues

If you hear...

- "contract along axis..."
- "sum over the shared dimension..."
- "mode-n product..."
- "tensor contraction..."
- "the axes are not in matmul position..."

...think **Tensordot**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Contracted axes|**Chosen** — by count or by name|
|Output shape|`a`'s free axes, then `b`'s free axes|
|`axes=0`|Outer product — nothing contracted|
|`axes=1`|Last of `a` with first of `b`|
|`axes=k`|Last `k` of `a` with first `k` of `b`, **in order**|
|`axes=([i],[j])`|Explicit pairs|
|Sizes|Paired axes must match, or `ValueError`|
|Batch axes|**No such concept** — they duplicate|
|Common Domains|Tensor algebra, decompositions, physics|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember
#
#   contracted axes vanish; free axes concatenate

import numpy as np

a = np.arange(24).reshape(2, 3, 4)
b = np.arange(24).reshape(4, 3, 2)

np.tensordot(a, b, axes=1).shape        # => (2, 3, 3, 2)
#
#   axes=1  contracts a's LAST axis (4) with b's FIRST (4)
#
#   a free: (2, 3)      b free: (3, 2)
#   output: (2, 3) + (3, 2)  =  (2, 3, 3, 2)
#
# that concatenation IS the rule. Nothing is broadcast,
# nothing is matched up — the free axes simply line up
# left to right.

# ============================================
# Naming the axes explicitly

np.tensordot(a, b, axes=([2], [0])).shape       # => (2, 3, 3, 2)
np.array_equal(np.tensordot(a, b, axes=([2], [0])),
               np.tensordot(a, b, axes=1))      # => True
#   axes=1 IS ([last of a], [first of b])

np.tensordot(a, b, axes=([1], [1])).shape       # => (2, 4, 4, 2)
#   contract a's axis 1 (size 3) with b's axis 1 (size 3)
#   a free: (2, 4)      b free: (4, 2)
#
# this is what `@` cannot express: the contracted axes
# are in the MIDDLE of both operands.

# sizes must match:
try:
    np.tensordot(a, b, axes=2)
except ValueError as e:
    print(e)
# shape-mismatch for sum
#
#   axes=2 means "a's last two with b's first two,
#   in order": (3,4) against (4,3). 3≠4. It refuses.
#
# the count form pairs them positionally — easy to get
# backwards. The explicit form says what you mean.

# ============================================
# The two extremes

np.tensordot(a, b, axes=0).shape        # => (2, 3, 4, 4, 3, 2)
np.array_equal(np.tensordot(a, b, axes=0), np.multiply.outer(a, b))
# => True
#   axes=0 contracts NOTHING — the outer product
#   (lesson 19), with every axis kept.

A = np.arange(6).reshape(2, 3)
np.tensordot(A, A, axes=([0, 1], [0, 1]))       # => 55
(A * A).sum()                                   # => 55
#   contract EVERYTHING — a scalar. This is the
#   Frobenius inner product of two matrices.
#
# so `axes` spans the full range:
#
#   0            no contraction   -> outer product
#   1            one axis         -> matmul-like
#   all of them  full contraction -> scalar

# ============================================
# It generalises matmul

B = np.arange(12).reshape(3, 4)
np.array_equal(np.tensordot(A, B, axes=1), A @ B)       # => True
#
# at rank 2, `axes=1` IS matmul. Everything `@` does at
# rank 2, tensordot does — plus the cases where the
# shared axis is not in matmul position.

# ============================================
# THE LIMITATION: no batch semantics

Ab = np.arange(2*3*4).reshape(2, 3, 4)
Bb = np.arange(2*4*5).reshape(2, 4, 5)

(Ab @ Bb).shape                                 # => (2, 3, 5)
np.tensordot(Ab, Bb, axes=([2], [1])).shape     # => (2, 3, 2, 5)
#
# the batch axis appears TWICE — once from `a`'s free
# axes and once from `b`'s. Tensordot has no way to say
# "these two axes are the same batch"; it only knows
# "contract" and "keep".
#
# that is the same failure as `np.dot` in lesson 32, and
# it is structural rather than a bug: the output rule is
# "concatenate the free axes", and a batch would need
# them ALIGNED instead.
#
# For batches, use `@` or einsum:
np.array_equal(np.einsum('bij,bjk->bik', Ab, Bb), Ab @ Bb)      # => True

# ============================================
# WHERE IT IS THE RIGHT TOOL: a mode-n product
#
# Apply a matrix along ONE axis of a multi-way array,
# leaving the others alone.

T = np.arange(2*3*4).reshape(2, 3, 4)
M = np.ones((5, 3))                 # maps the size-3 axis to size 5

mode1 = np.tensordot(M, T, axes=([1], [1]))
mode1.shape                         # => (5, 2, 4)
#
#   contract M's axis 1 (3) with T's axis 1 (3)
#   M free: (5,)       T free: (2, 4)
#   output: (5, 2, 4)
#
# the new axis lands FIRST, because M was the first
# operand and free axes concatenate in operand order.
# To put it back where the old one was:
np.moveaxis(mode1, 0, 1).shape      # => (2, 5, 4)
#
# this is the "mode-n product" of tensor decompositions,
# and it is genuinely awkward with `@` — you would have
# to moveaxis, reshape, matmul and reshape back.

# ============================================
# Contracting several axes at once

x = np.ones((2, 3, 4, 5))
y = np.ones((3, 5, 7))

np.tensordot(x, y, axes=([1, 3], [0, 1])).shape         # => (2, 4, 7)
#
#   pair x's axis 1 (3) with y's axis 0 (3)
#   pair x's axis 3 (5) with y's axis 1 (5)
#   x free: (2, 4)     y free: (7,)
#
# the lists are matched ELEMENTWISE — first with first,
# second with second. Order inside the lists matters.

# ============================================
# What it is doing underneath
#
# Tensordot is transpose + reshape + matmul + reshape.

def tensordot_manual(a, b, ax_a, ax_b):
    free_a = [i for i in range(a.ndim) if i not in ax_a]
    free_b = [i for i in range(b.ndim) if i not in ax_b]
    A2 = a.transpose(free_a + list(ax_a)).reshape(
        int(np.prod([a.shape[i] for i in free_a])), -1)
    B2 = b.transpose(list(ax_b) + free_b).reshape(
        -1, int(np.prod([b.shape[i] for i in free_b])))
    out = A2 @ B2
    return out.reshape([a.shape[i] for i in free_a] + [b.shape[i] for i in free_b])

np.array_equal(tensordot_manual(a, b, [1], [1]),
               np.tensordot(a, b, axes=([1], [1])))     # => True
#
# move the contracted axes together, flatten to 2-D, one
# matmul, unflatten. That is why the output rule is
# "free axes of a then free axes of b" — it is literally
# a reshape of a matrix product.
#
# and it is why there is no batch: the reshape has
# already merged everything into two big matrices.

# ============================================
# Compare

A @ B                                   # fixed axes, batched
np.tensordot(A, B, axes=1)              # == A @ B at rank 2
np.tensordot(a, b, axes=([1],[1]))      # any axes, NOT batched
np.tensordot(a, b, axes=0)              # outer product
np.einsum('ij,jk->ik', A, B)            # any axes, batched, named

[np.tensordot(a, b, axes=1).shape,
 np.tensordot(a, b, axes=([1],[1])).shape,
 np.tensordot(a, b, axes=0).shape]
# => [(2, 3, 3, 2), (2, 4, 4, 2), (2, 3, 4, 4, 3, 2)]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the output rule|contracted axes vanish; free axes **concatenate**|
|specific axes|`axes=([i], [j])` — say it explicitly|
|an outer product|`axes=0`|
|a full contraction|`axes=([0,1], [0,1])` — a scalar|
|matmul|`axes=1` at rank 2|
|a mode-n product|`tensordot(M, T, axes=([1],[n]))`, then `moveaxis`|
|**not** a batch|it duplicates the batch axis — use `@`|
|to know why|it's transpose + reshape + matmul underneath|

---

## Key Insight

**Tensordot's output rule is "concatenate the free axes"** — every axis of `a` that was not contracted, followed by every axis of `b` that was not contracted. That one sentence predicts every shape it produces, and it also explains its limitation.

```text
a (2,3,4), b (4,3,2), contract a2 with b0

   a free (2,3)  +  b free (3,2)   ->   (2,3,3,2)
```

Because free axes are *concatenated* rather than *aligned*, a batch axis shared by both operands appears **twice**. `(2,3,4)` with `(2,4,5)` gives `(2,3,2,5)` — structurally the same failure as `np.dot` (lesson 32), and for the same reason. Tensordot knows only two verbs, "contract" and "keep"; a batch needs a third, "match".

The reason the rule looks the way it does becomes obvious once you see the implementation: **transpose the contracted axes together, reshape to 2-D, do one matmul, reshape back.** The output is literally a reshaped matrix product, which is also why there is nowhere for batch semantics to live.

Where it genuinely earns its place is the **mode-n product** — applying a matrix along one axis of a multi-way array while leaving the others alone. With `@` that needs a moveaxis, a reshape, a matmul and a reshape back; with `tensordot` it is one call.

Two smaller cautions: the integer form `axes=k` pairs "last `k` of `a`" with "first `k` of `b`" **in order**, which is easy to get backwards (`(3,4)` against `(4,3)` fails); and `axes=0` is a legitimate outer product, not a no-op.

---

## The Three Contraction Tools So Far

|Tool|Contracts|Batch|Says which axes|
|---|---|---|---|
|`@`|last / second-to-last|**yes**|no — fixed|
|`np.tensordot`|**any**, by position|no|by position|
|`np.einsum`|**any**, by name|**yes**|by name|

```text
   @          fixed axes, batched          the common case
   tensordot  chosen axes, not batched     mode-n products
   einsum     everything                   lesson 34
```

> **Mental shift:** matmul fixed the axes and got batches in return. Tensordot freed the axes and gave up batches. Neither gives you both, which is precisely the gap `einsum` fills, and why the next lesson is where this section really lands.
