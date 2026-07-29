# Part 3 — Tensor Patterns

A tensor is an **n-dimensional array**. Part 1 handled `n = 1`, part 2 handled `n = 2`. Everything here is the same set of questions asked with the rank left open.

```text
rank 0   scalar      5
rank 1   vector      [1, 2, 3]                    Part 1
rank 2   matrix      [[1, 2], [3, 4]]             Part 2
rank 3   cube        [[[...]]]                    Part 3
rank n   tensor      shape = (d0, d1, ..., dn-1)
```

The one idea that carries all of it: **an axis is a position in the shape tuple.** Say "axis 1" and you mean the second number in `shape`. Every operation below is "do the 1D or 2D thing you already know, along a chosen axis."

---

## The pattern families

- **Foundations:** shape, rank, axes, indexing, strides
- **Traversal:** iterate an axis, nested, flat
- **Slicing:** per-axis slice, ellipsis, fancy indexing, boolean mask
- **Structure:** reshape, flatten, permute axes, move axis, squeeze / expand
- **Broadcasting:** the rules, axis alignment, outer operations
- **Reduction:** reduce along an axis, keepdims, multi-axis, argmin / argmax
- **Combination:** concatenate, stack, split, tile / repeat
- **Windows:** patch extraction, pooling, convolution
- **Contraction:** dot, matmul, batch matmul, tensordot, einsum
- **Generation:** zeros / ones / full, arange / linspace, meshgrid, identity / diagonal

---

## Roadmap

| # | Section | Lessons |
|---|---|---|
| 01 | **Tensor Foundations** | 1 Shape and Rank · 2 Axes · 3 Indexing · 4 Strides and Memory Layout |
| 02 | **Tensor Traversal** | 5 Axis Iteration · 6 Nested Traversal · 7 Flat Traversal |
| 03 | **Tensor Slicing** | 8 Basic Slicing · 9 Ellipsis and newaxis · 10 Fancy Indexing · 11 Boolean Masking |
| 04 | **Tensor Structure** | 12 Reshape · 13 Flatten / Ravel · 14 Permute Axes · 15 Swap / Move Axis · 16 Squeeze and Expand Dims |
| 05 | **Tensor Broadcasting** | 17 Broadcasting Rules · 18 Axis Alignment · 19 Outer Operations |
| 06 | **Tensor Reduction** | 20 Reduce Along an Axis · 21 Keepdims · 22 Multi-Axis Reduction · 23 Argmin / Argmax |
| 07 | **Tensor Combination** | 24 Concatenate · 25 Stack · 26 Split · 27 Tile and Repeat |
| 08 | **Tensor Windows** | 28 Patch Extraction · 29 Pooling · 30 Convolution |
| 09 | **Tensor Contraction** | 31 Dot and Matmul · 32 Batch Matmul · 33 Tensordot · 34 Einsum |
| 10 | **Tensor Generation** | 35 Zeros / Ones / Full · 36 Arange and Linspace · 37 Meshgrid · 38 Identity and Diagonal |

---

## The Python tool for each pattern

|Family|Pattern|Reach for|
|---|---|---|
|**Foundations**|rank|`t.ndim`|
||shape|`t.shape` — a tuple, one entry per axis|
||element count|`t.size`|
||memory step per axis|`t.strides`|
|**Traversal**|along axis 0|`for sub in t`|
||along axis k|`for sub in np.moveaxis(t, k, 0)`|
||every index|`np.ndindex(*t.shape)`|
||every value, flat|`t.ravel()` / `t.flat`|
|**Slicing**|per axis|`t[a:b, c:d, e:f]`|
||"all remaining axes"|`t[..., 0]`|
||pick specific positions|`t[[0, 2], :, 1]`|
||filter by condition|`t[t > 5]`|
|**Structure**|reshape|`t.reshape(...)` — `-1` infers one axis|
||flatten|`t.ravel()` (view) / `t.flatten()` (copy)|
||permute axes|`t.transpose(2, 0, 1)`|
||move one axis|`np.moveaxis(t, src, dst)`|
||drop / add a size-1 axis|`t.squeeze()` / `t[:, None]`|
|**Broadcasting**|align shapes|right-align, stretch every `1`|
||add an axis to align|`t[:, None, :]`|
||outer operation|`a[:, None] * b[None, :]`|
|**Reduction**|along an axis|`t.sum(axis=1)`|
||keep the rank|`t.sum(axis=1, keepdims=True)`|
||several axes|`t.sum(axis=(0, 2))`|
||position of the best|`t.argmax(axis=1)`|
|**Combination**|join on an existing axis|`np.concatenate([a, b], axis=0)`|
||join on a NEW axis|`np.stack([a, b], axis=0)`|
||split|`np.split(t, n, axis=0)`|
||repeat|`np.tile` / `np.repeat`|
|**Windows**|patches|`sliding_window_view(t, size, axis)`|
||pooling|reshape into blocks, reduce|
||convolution|`einsum` or `scipy.signal`|
|**Contraction**|matrix product|`a @ b`|
||batched product|`a @ b` with leading batch axes|
||arbitrary axes|`np.tensordot(a, b, axes=...)`|
||anything|`np.einsum('ijk,ikl->ijl', a, b)`|
|**Generation**|constants|`np.zeros`, `np.ones`, `np.full`|
||sequences|`np.arange`, `np.linspace`|
||coordinate tensors|`np.meshgrid`, `np.indices`|
||identity / diagonal|`np.eye`, `np.diag`|

---

## The imports that cover almost everything

```python
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
```

Compare that with parts 1 and 2, which needed a dozen `itertools` names. At rank 3 and above, the library *is* the vocabulary — but the essays in this part always show the nested-list version first, so you can see what the one-liner is doing.

---

## Three rules that cut across all of it

1. **Name the axis, not the loop.** `for i in range(len(t))` throws away which dimension you meant. `axis=1` keeps it, and every reduction, stack, split and reshape takes it.

2. **A reduction removes an axis; `keepdims=True` keeps it as size 1.** That single flag is the difference between a broadcast that works and one that raises. Most axis bugs are shape bugs, and printing `.shape` after every step finds them faster than reading the code.

3. **Views share memory; copies do not.** `reshape`, `transpose` and basic slicing return **views** — writing through one changes the original. Fancy indexing and boolean masking return **copies**. `np.shares_memory(a, b)` settles it.

---

## Reading the code blocks in this part

Every **Python Recipe Book** in part 3 shows a pattern twice:

```python
# what is actually happening — nested lists, no library
[[sum(t[i][j][k] for j in range(J)) for k in range(K)] for i in range(I)]

# the one idiom to remember
t.sum(axis=1)
```

The nested version is there so the NumPy call stops being magic. In real code, write the second one.

---

# The series

```txt
Part 1
1D Sequence Patterns          ✔ complete
        ↓
Part 2
Matrix Patterns               ✔ complete
        ↓
Part 3
Tensor Patterns               ← you are here
        ↓
Part 4
Tree Traversal Patterns
        ↓
Part 5
Graph Traversal Patterns
```
