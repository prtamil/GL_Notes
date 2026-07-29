# 34. Einsum

## Mental Model

Every operation in this section pinned *something* down. `@` pinned which axes contract. `tensordot` freed the axes but gave up batches. `einsum` pins nothing: **you name every axis, and the notation says what happens to it.**

```python
np.einsum('ij,jk->ik', A, B)        # matrix product
```

Read it as: *"`A` has axes `i,j`; `B` has axes `j,k`; the output has axes `i,k`."* Everything follows from three rules:

```text
1.  an index in the OUTPUT              ->  KEPT
2.  an index shared by operands but
    NOT in the output                   ->  SUMMED (contracted)
3.  an index repeated WITHIN one operand ->  DIAGONAL
```

Rule 2 is contraction. Rule 1 is broadcast-and-keep. Rule 3 hands you traces and diagonals for free.

Those three rules cover this whole section, and most of the previous ones too:

```text
'ij->ji'            transpose               (lesson 14)
'ij->j'             sum over axis 0         (lesson 20)
'ii->'              trace
'i,j->ij'           outer product           (lesson 19)
'ij,jk->ik'         matmul                  (lesson 31)
'bij,bjk->bik'      batch matmul            (lesson 32)
'ijkl,kl->ij'       convolution             (lesson 30)
```

The payoff is not brevity. It is that the *intent* is written down: which axes are batch, which are contracted, which survive. A shape mismatch in `@` gives you "core dimension mismatch"; in einsum you can read off what you meant.

---

## Relationship to Cognitive Verb

```text
Specify
   ↓
Einsum
```

Related verbs:

- Specify the contraction
- Name the axes
- Declare the result
- Index notation

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Matrix product|the classic|`np.einsum('ij,jk->ik', A, B)`|
|Batch matmul|one more index|`np.einsum('bij,bjk->bik', A, B)`|
|Any leading axes|ellipsis|`np.einsum('...ij,...jk->...ik', A, B)`|
|Transpose|no second operand|`np.einsum('ij->ji', A)`|
|Reduce|drop an index|`np.einsum('ij->i', A)`|
|Trace / diagonal|repeat within one operand|`'ii->'` / `'ii->i'`|
|Outer product|no shared index|`np.einsum('i,j->ij', u, v)`|
|Elementwise then sum|shared **and** dropped|`np.einsum('ij,ij->', A, B)`|
|Three operands|a chain|`np.einsum('ij,jk,kl->il', X, Y, Z)`|
|Choose a good order|for chains|`optimize=True`|
|Inspect the plan|debugging cost|`np.einsum_path(...)`|

---

## Common Uses

- Attention and transformer internals
- Any contraction where the axes are not in matmul position
- Batched bilinear forms
- Weighted sums over several tensors at once
- Convolution as a contraction
- Tensor network / decomposition code
- Replacing an unreadable chain of transposes and reshapes

---

## Hidden Interview Problems

- Implement matrix multiply with einsum
- Compute a batched bilinear form `xᵀWy`
- Compute the trace and diagonal
- Contract two tensors along named axes
- Explain when einsum is faster than a chain of matmuls
- Express convolution as a contraction

---

## Recognition Clues

If you hear...

- "contract these axes..."
- "einsum..."
- "the shapes need three transposes first..."
- "batched bilinear..."
- "index notation..."

...think **Einsum**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Notation|`'in1,in2->out'`, one letter per axis|
|Index in the output|**Kept**|
|Index shared, not in output|**Summed** (contracted)|
|Index repeated in one operand|**Diagonal**|
|Ellipsis `...`|Stands for any leading axes|
|No `->`|Output is the sorted free indices|
|Operands|Any number|
|`optimize=True`|Chooses a contraction order|
|Batch|Just an index you keep|
|Common Domains|Deep learning, tensor algebra, physics|

---

## Python Recipe Book

```python
# ============================================
# The three rules, demonstrated

import numpy as np

A = np.arange(6).reshape(2, 3)
B = np.arange(12).reshape(3, 4)

# RULE 1 + 2: j is shared and absent from the output -> summed
np.array_equal(np.einsum('ij,jk->ik', A, B), A @ B)     # => True
#
#   i  in output  -> kept
#   k  in output  -> kept
#   j  shared, not in output -> SUMMED
#
# that is a matrix product, written as a sentence.

# RULE 1 alone: keep everything, sum nothing
np.array_equal(np.einsum('i,j->ij', np.array([1,2,3]), np.array([4,5,6])),
               np.outer(np.array([1,2,3]), np.array([4,5,6])))     # => True
#   no shared index -> nothing contracted -> outer product

# RULE 3: an index repeated WITHIN one operand -> diagonal
S = np.arange(9).reshape(3, 3)
np.einsum('ii->i', S)       # => array([0, 4, 8])       the diagonal
np.einsum('ii->', S)        # => 12                     the trace
np.trace(S)                 # => 12
np.array_equal(np.einsum('ii->i', S), np.diag(S))       # => True

# ============================================
# The whole course, in one notation

np.einsum('ij->ji', A)                  # transpose        (lesson 14)
np.array_equal(np.einsum('ij->ji', A), A.T)             # => True

np.einsum('ij->', A)                    # => 15   sum everything  (lesson 20)
np.einsum('ij->j', A)                   # => [3, 5, 7]    sum axis 0
np.einsum('ij->i', A)                   # => [3, 12]      sum axis 1
#
# dropping an index from the output sums it. `'ij->i'`
# says "keep i, lose j" — which IS `A.sum(axis=1)`.

np.einsum('i,i->', np.array([1,2,3]), np.array([4,5,6]))    # => 32   inner
np.einsum('ij,ij->ij', A, A)            # elementwise product
np.einsum('ij,ij->', A, A)              # => 55   elementwise then sum
#
# note the last two differ only in the output: keeping
# `ij` gives `A*A`, dropping it sums the result. One
# character.

# ============================================
# Batch is just an index you keep

Ab = np.arange(2*3*4).reshape(2, 3, 4)
Bb = np.arange(2*4*5).reshape(2, 4, 5)

np.array_equal(np.einsum('bij,bjk->bik', Ab, Bb), Ab @ Bb)      # => True
#
#   b appears in both operands AND in the output -> KEPT
#   j appears in both and NOT in the output      -> SUMMED
#
# that single distinction is what `tensordot` could not
# express (lesson 33) and what makes einsum strictly
# more general than both `@` and `tensordot`.

Mb = np.arange(2*3*4).reshape(2, 3, 4)
vb = np.arange(4)
np.array_equal(np.einsum('bij,j->bi', Mb, vb), Mb @ vb)         # => True
#   `j` is shared and dropped; `b` and `i` survive.

# ============================================
# Ellipsis — "whatever the leading axes are"

np.einsum('...ij->...ji', Ab).shape             # => (2, 4, 3)
np.array_equal(np.einsum('...ij->...ji', Ab), Ab.swapaxes(-1, -2))  # => True

np.einsum('...ij,...jk->...ik', Ab, Bb).shape   # => (2, 3, 5)
np.array_equal(np.einsum('...ij,...jk->...ik', Ab, Bb), Ab @ Bb)    # => True
#
# THAT expression is matmul's rule, written out: "the
# last two axes are a matrix, everything before is
# broadcast". If you ever forget what `@` does at rank 4,
# this is the definition.
#
# the ellipsis also keeps code rank-agnostic — the same
# subscripts work for (n,k), (b,n,k) and (b,h,n,k).

# ============================================
# Implicit output — usually write the arrow

np.einsum('ij,jk', A, B).shape          # => (2, 4)
np.array_equal(np.einsum('ij,jk', A, B), np.einsum('ij,jk->ik', A, B))  # => True

np.einsum('ij', A).shape                # => (2, 3)     a no-op
#
# without `->`, the output is the free indices in
# ALPHABETICAL order. It happens to give matmul for
# 'ij,jk' and it will surprise you elsewhere. Write the
# arrow; it is also the documentation.

# ============================================
# THREE OPERANDS — and why order matters

X = np.ones((100, 2))
Y = np.ones((2, 100))
Z = np.ones((100, 2))

np.einsum('ij,jk,kl->il', X, Y, Z).shape            # => (100, 2)

np.einsum_path('ij,jk,kl->il', X, Y, Z)[0]
# => ['einsum_path', (1, 2), (0, 1)]
#
# read it as: contract operands 1 and 2 first (Y and Z,
# giving a 2x2), THEN contract with operand 0. That
# avoids the 100x100 intermediate that left-to-right
# would build — lesson 31's associativity point, decided
# automatically.

np.allclose(np.einsum('ij,jk,kl->il', X, Y, Z),
            np.einsum('ij,jk,kl->il', X, Y, Z, optimize=True))      # => True
#
# `optimize=True` uses that path. For two operands it
# makes no difference; for three or more it can be the
# difference between milliseconds and minutes.
#
# (NumPy's default is optimize=False, so pass it
# explicitly on any chain.)

# ============================================
# Practical: a bilinear form

u = np.array([1, 2, 3])
W = np.arange(12).reshape(3, 4)
y = np.arange(4)

np.einsum('i,ij,j->', u, W, y)          # => 276
u @ W @ y                               # => 276
#
# same answer. The einsum version says "contract i with
# W's rows and j with W's columns, keep nothing" — and
# it batches trivially:
#
#   'bi,ij,bj->b'    a bilinear score per sample
#
# which as a chain of matmuls needs an explicit
# elementwise-multiply-and-sum step.

# ============================================
# Practical: convolution, from lesson 30

from numpy.lib.stride_tricks import sliding_window_view as swv

img = np.arange(25).reshape(5, 5)
box = np.ones((3, 3)) / 9

np.round(np.einsum('ijkl,kl->ij', swv(img, (3, 3)), box), 2)
# => array([[ 6.,  7.,  8.],
#           [11., 12., 13.],
#           [16., 17., 18.]])
#
#   i, j  window POSITION  -> kept
#   k, l  window CONTENTS  -> contracted with the kernel
#
# and a full conv layer:
#
#   'nchwij,ocij->nohw'
#
#   n  batch          kept
#   c  input channel  CONTRACTED
#   h,w position      kept
#   i,j kernel        CONTRACTED
#   o  output channel kept
#
# every design decision of a convolution is visible in
# that string.

# ============================================
# Practical: attention, spelled out

rng = np.random.default_rng(0)
N, H, T, d = 2, 2, 3, 4
Q = rng.normal(size=(N, H, T, d))
K = rng.normal(size=(N, H, T, d))
V = rng.normal(size=(N, H, T, d))

scores = np.einsum('nhqd,nhkd->nhqk', Q, K) / np.sqrt(d)
scores.shape                            # => (2, 2, 3, 3)
#
#   n, h  batch and head  -> kept
#   q, k  the two positions -> kept (this is the all-pairs part)
#   d     feature          -> CONTRACTED
#
# compare with `Q @ K.swapaxes(-1,-2)` from lesson 32 —
# same computation, but here you can SEE that d is the
# contracted axis and q,k are the pair axes.

e = np.exp(scores - scores.max(axis=-1, keepdims=True))
attn = e / e.sum(axis=-1, keepdims=True)

out = np.einsum('nhqk,nhkd->nhqd', attn, V)
out.shape                               # => (2, 2, 3, 4)
#   now k is contracted — a weighted sum of value vectors.

# ============================================
# When NOT to use einsum
#
# It is not always faster. `A @ B` dispatches straight to
# BLAS; einsum may not, especially without optimize=True.
# For a plain matrix product, `@` is clearer AND faster.
#
# reach for einsum when:
#   - the axes are not in matmul position
#   - there are three or more operands
#   - batch and contracted axes are interleaved
#   - the alternative is transpose + reshape + matmul + reshape

# ============================================
# Compare — every contraction in this section

np.einsum('i,i->', u, u)                # inner          (lesson 31)
np.einsum('i,j->ij', u, u)              # outer          (lesson 19)
np.einsum('ij,jk->ik', A, B)            # matmul         (lesson 31)
np.einsum('bij,bjk->bik', Ab, Bb)       # batch matmul   (lesson 32)
np.einsum('ijk,jl->ikl', Ab, np.ones((3, 5)))   # a MIDDLE axis  (lesson 33)
np.einsum('ii->', S)                    # trace
np.einsum('ij->ji', A)                  # transpose      (lesson 14)
np.einsum('ij->i', A)                   # reduction      (lesson 20)

# all one function, distinguished only by the string.

# that middle-axis one is tensordot's use case:
np.einsum('ijk,jl->ikl', Ab, np.ones((3, 5))).shape                 # => (2, 4, 5)
np.tensordot(Ab, np.ones((3, 5)), axes=([1], [0])).shape            # => (2, 4, 5)
#
# einsum contracts j (Ab's MIDDLE axis) — something `@`
# cannot express without a moveaxis first.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the three rules|output → keep; shared & dropped → **sum**; repeated in one → **diagonal**|
|a matrix product|`'ij,jk->ik'`|
|a batch|add a letter that appears everywhere: `'bij,bjk->bik'`|
|any leading axes|`'...ij,...jk->...ik'`|
|a transpose|`'ij->ji'`|
|a reduction|drop the index: `'ij->i'`|
|a trace|`'ii->'`|
|three or more operands|`optimize=True` — always|
|to see the plan|`np.einsum_path(...)`|
|**not** einsum|a plain `A @ B` — clearer and faster|

---

## Key Insight

**Einsum makes the axes explicit, and then the three rules do everything.**

```text
in the output              ->  kept
shared, not in the output  ->  summed
repeated in one operand    ->  diagonal
```

Rule 2 is contraction, so `@`, `tensordot`, `dot`, `inner`, `outer`, `trace`, `transpose` and every axis reduction are the same function with different strings. What einsum adds over the others is not power in the abstract — it is that **the intent is written down**. In `'bij,bjk->bik'` you can see that `b` is a batch and `j` is contracted; in `A @ B` at rank 4 you have to remember the convention.

That is why the notation is worth learning even when `@` would do: the string is the documentation, and it is checkable by eye.

Three practical points:

1. **Write the `->`.** Without it, the output is the free indices in *alphabetical* order. It happens to be right for `'ij,jk'` and it will not be right for something else.
    
2. **Pass `optimize=True` for three or more operands.** NumPy defaults to left-to-right, and `np.einsum_path('ij,jk,kl->il', X, Y, Z)` returns `[(1,2), (0,1)]` — contract `Y·Z` first and avoid a 100×100 intermediate. This is lesson 31's associativity argument, automated.
    
3. **Do not use it for a plain matrix product.** `A @ B` dispatches to BLAS directly and reads better. Einsum earns its place when the axes are not in matmul position, when there are several operands, or when the alternative is a chain of transposes and reshapes.
    

---

## The Contraction Section, Complete

|Lesson|Contracts|Batch|Axes chosen by|
|---|---|---|---|
|31 Dot and Matmul|last / second-to-last|—|fixed|
|32 Batch Matmul|last two|**broadcast**|fixed|
|33 Tensordot|**any**|**no**|position|
|**34 Einsum**|**any**|**yes**|**name**|

```text
   @           fixed axes, batched          -> the common case
   tensordot   any axes, no batch           -> mode-n products
   einsum      any axes, any batch, named   -> everything else
```

Each earlier tool is a special case of the next:

```python
A @ B                    ==  np.einsum('...ij,...jk->...ik', A, B)
np.tensordot(a,b,axes=1) ==  np.einsum('ijk,klm->ijlm', a, b)
u @ v                    ==  np.einsum('i,i->', u, v)
A.T                      ==  np.einsum('ij->ji', A)
A.sum(axis=1)            ==  np.einsum('ij->i', A)
```

> **Mental shift:** part 1 wrote `sum(a*b for a,b in zip(u,v))` and part 2 wrote a triple loop for matrix multiply. Both spelled out *how*. Einsum spells out *what*: which axes pair up, which survive, which get summed away. Once the axes have names, the difference between a dot product, a matmul, an attention score and a convolution is a different string, and the loop is somebody else's problem.
