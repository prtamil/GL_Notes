# 30. Convolution

## Mental Model

Lesson 28 handed you every window for free. Lesson 29 reduced non-overlapping windows with `max` or `mean`. Convolution reduces **overlapping** windows using **weights**:

```text
windows  x  kernel  ──sum over the window axes──►  one value per position
```

In NumPy that's two lines, and the second is an `einsum`:

```python
w = sliding_window_view(img, (3, 3))        # (H-2, W-2, 3, 3)   free
out = np.einsum('ijkl,kl->ij', w, kernel)   # contract the window axes
```

Part 2's lesson 15 wrote this as a nested loop over positions with a guarded accumulator. Here the *extraction* is a stride trick and the *arithmetic* is one contraction, with nothing materialised in between.

Everything else in the lesson is a parameter:

|Parameter|How|
|---|---|
|**stride**|slice the position axes: `w[::2, ::2]`|
|**padding**|`np.pad` the input first|
|**kernel flip**|`kernel[::-1, ::-1]` — see below|
|**batch / channels**|more `einsum` subscripts|

Same warning as part 2, except now you can demonstrate it with a library function: **`np.convolve` flips the kernel, `np.correlate` doesn't.** What machine learning calls "convolution" is correlation.

---

## Relationship to Cognitive Verb

```text
Weigh
  ↓
Convolution
```

Related verbs:

- Weigh and combine
- Filter
- Apply a stencil
- Correlate
- Slide and dot

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|The pattern|windows × kernel|`swv(t, k)` then `einsum`|
|1-D correlation|no flip|`np.correlate(a, v, mode=...)`|
|1-D convolution|flips|`np.convolve(a, v, mode=...)`|
|'valid'|no padding|output shrinks by `k-1`|
|'same'|shape preserved|`np.pad(t, k//2)` first|
|Stride|skip positions|`w[::s, ::s]`|
|Flip the kernel|true convolution|`kernel[::-1, ::-1]`|
|Separable|two 1-D passes|`swv(..., axis=1)` then `axis=0`|
|Batched, multi-channel|full conv layer|`einsum('nchwij,ocij->nohw', ...)`|
|Sanity check|blur of a constant|equals the constant|

---

## Common Uses

- Blurring, sharpening and edge detection
- Convolutional neural network layers
- Moving averages and smoothing filters
- Gradient and Laplacian operators
- Template correlation
- Feature detection
- Signal filtering

---

## Hidden Interview Problems

- Implement 2-D convolution without loops
- Apply a Sobel filter
- Implement 'same' padding
- Implement strided convolution
- Optimise a separable kernel
- Explain the difference between convolution and correlation
- Compute the output shape of a conv layer

---

## Recognition Clues

If you hear...

- "apply this kernel / filter..."
- "blur / sharpen / edge detect..."
- "convolution layer..."
- "stride and padding..."
- "weighted moving average..."

...think **Convolution**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Operation|Weighted sum over each window|
|Extraction|`sliding_window_view` — a **view**|
|Contraction|`einsum` over the window axes|
|Output shape|`(n + 2p - k)//s + 1` per axis|
|'valid'|`p = 0` — shrinks by `k-1`|
|'same'|`p = k//2`|
|Kernel flip|`convolve` yes, `correlate` no, ML no|
|Separable|Two 1-D passes: O(k) not O(k²)|
|Memory|Nothing materialised|
|Common Domains|Images, CNNs, signal processing|

---

## Python Recipe Book

```python
# ============================================
# 1-D first — and the flip

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

sig = np.array([1, 2, 3, 4, 5])
ker = np.array([1, 0, -1])

swv(sig, 3)
# => array([[1, 2, 3],
#           [2, 3, 4],
#           [3, 4, 5]])

(swv(sig, 3) * ker).sum(axis=-1)        # => array([-2, -2, -2])
np.correlate(sig, ker, mode='valid')    # => array([-2, -2, -2])
#
# windows times kernel, summed. That is correlation, and
# it is what the hand-written version computes.

np.convolve(sig, ker, mode='valid')     # => array([2, 2, 2])
#
# OPPOSITE SIGN. `convolve` reverses the kernel first:
np.array_equal(np.convolve(sig, ker, mode='valid'),
               np.correlate(sig, ker[::-1], mode='valid'))       # => True
#
# true convolution flips; correlation does not. For a
# SYMMETRIC kernel (box, gaussian, laplacian) they agree
# and nobody notices. For an asymmetric one — every
# gradient filter — the sign is wrong.
#
# every deep-learning "convolution" is correlation.

# the three modes:
np.convolve(sig, ker, mode='valid')     # => [2, 2, 2]                len 3
np.convolve(sig, ker, mode='same')      # => [2, 2, 2, 2, -4]         len 5
np.convolve(sig, ker, mode='full')      # => [1, 2, 2, 2, 2, -4, -5]  len 7
#
#   valid  n - k + 1     only fully-overlapping positions
#   same   n             zero-padded to preserve length
#   full   n + k - 1     every position with any overlap

# ============================================
# The one idiom to remember — 2-D

img = np.arange(25).reshape(5, 5)
box = np.ones((3, 3)) / 9

w = swv(img, (3, 3))
w.shape                     # => (3, 3, 3, 3)   (out_i, out_j, ki, kj)

out = np.einsum('ijkl,kl->ij', w, box)
np.round(out, 2)
# => array([[ 6.,  7.,  8.],
#           [11., 12., 13.],
#           [16., 17., 18.]])
#
# read the subscripts: 'ijkl,kl->ij' means "multiply the
# window axes k,l against the kernel and sum them out,
# keeping the position axes i,j". The kernel axes appear
# on both sides of the comma and NOT after the arrow —
# that is what "contract" means (lesson 33).

# it is a weighted mean, so it agrees with the plain one:
np.allclose(out, w.mean(axis=(-2, -1)))                 # => True

# and the elementwise form, if einsum is unfamiliar:
np.array_equal(np.einsum('ijkl,kl->ij', w, box),
               (w * box).sum(axis=(-2, -1)))            # => True
#
# `(w * box).sum(...)` broadcasts the (3,3) kernel against
# the (3,3,3,3) windows, then reduces. Same answer;
# einsum avoids the intermediate.

# ============================================
# Edge detection — the part 2 result, reproduced

sob = np.array([[-1, 0, 1],
                [-2, 0, 2],
                [-1, 0, 1]])

edge = np.zeros((5, 6))
edge[:, 3:] = 9
edge
# => array([[0., 0., 0., 9., 9., 9.],
#           ... 5 identical rows ...

np.einsum('ijkl,kl->ij', swv(edge, (3, 3)), sob)
# => array([[ 0., 36., 36.,  0.],
#           [ 0., 36., 36.,  0.],
#           [ 0., 36., 36.,  0.]])
#
# the vertical edge lights up at 36 — exactly the number
# part 2's lesson 15 produced with a nested loop. Same
# computation, no loop, no copy.

# ============================================
# PADDING: 'valid' vs 'same'

np.einsum('ijkl,kl->ij', swv(img, (3, 3)), box).shape           # => (3, 3)
#   'valid' — a 5x5 shrinks to 3x3

pad = np.pad(img, 1, mode='constant')
pad.shape                                                       # => (7, 7)
np.einsum('ijkl,kl->ij', swv(pad, (3, 3)), box).shape           # => (5, 5)
#   'same' — pad by k//2 first, shape preserved

np.pad(img, 1, mode='edge').shape                               # => (7, 7)
#
# `mode=` picks what is outside: 'constant' (zeros),
# 'edge' (clamp), 'reflect', 'wrap' — the same four
# choices as part 2's lesson 14, and the same warning:
# zero padding darkens the border of a blurred image.

# ============================================
# STRIDE: slice the position axes

np.einsum('ijkl,kl->ij', swv(img, (3, 3))[::2, ::2], box).shape # => (2, 2)
#
# no `stride=` parameter needed — the position axes are
# just axes, and slicing them stays a view (lesson 28).

# the general output shape, from lesson 14:
def out_shape(n, k, s=1, p=0):
    return (n + 2*p - k)//s + 1

out_shape(5, 3)             # => 3      valid
out_shape(5, 3, p=1)        # => 5      same
out_shape(5, 3, s=2)        # => 2      strided

# ============================================
# SEPARABLE KERNELS — O(k) instead of O(k²)
#
# A box blur is the outer product of two 1-D means, so
# it can be done as two 1-D passes.

k1 = np.ones(3) / 3

tmp = np.einsum('ijk,k->ij', swv(img, 3, axis=1), k1)   # blur across
tmp.shape                                               # => (5, 3)

sep = np.einsum('ijk,k->ij', swv(tmp, 3, axis=0), k1)   # then down
sep.shape                                               # => (3, 3)

np.allclose(sep, np.einsum('ijkl,kl->ij', swv(img, (3, 3)), box))   # => True
#
# note sliding_window_view APPENDS the window axis, so
# after `swv(tmp, 3, axis=0)` the shape is
# (n_row_windows, cols, window) — the window is already
# last, and einsum sums over it directly. No moveaxis.
#
# 2k multiplies per output instead of k^2. For a 9x9
# gaussian that is 18 versus 81 — the same separability
# argument as part 2's lesson 15 and lesson 12's max2d.

# ============================================
# A FULL CONV LAYER — batched and multi-channel
#
# This is where einsum stops being optional.

bimg = np.arange(2*1*5*5, dtype=float).reshape(2, 1, 5, 5)   # N, C, H, W
kers = np.arange(3*1*3*3, dtype=float).reshape(3, 1, 3, 3)   # O, C, kh, kw

win = swv(bimg, (3, 3), axis=(2, 3))
win.shape                   # => (2, 1, 3, 3, 3, 3)
#                                 n  c  h  w  i  j

conv = np.einsum('nchwij,ocij->nohw', win, kers)
conv.shape                  # => (2, 3, 3, 3)
#                                 N  O  H  W
#
# read the subscripts:
#   n  batch          kept
#   c  input channel  CONTRACTED (summed over)
#   h,w position      kept
#   i,j kernel        CONTRACTED
#   o  output channel kept, from the kernel
#
# summing over `c` is what "a conv layer combines all
# input channels" means, and it is one letter.

conv[0, 0]
# => array([[312., 348., 384.],
#           [492., 528., 564.],
#           [672., 708., 744.]])

# verified against the definition:
manual = np.zeros((2, 3, 3, 3))
for n in range(2):
    for o in range(3):
        for h in range(3):
            for x in range(3):
                manual[n, o, h, x] = (bimg[n, :, h:h+3, x:x+3] * kers[o]).sum()

np.allclose(conv, manual)   # => True
#
# four nested Python loops, or one einsum. And the
# einsum never materialises the windows.

# ============================================
# Sanity checks worth running

# a blur of a constant image is that constant
flat = np.full((5, 5), 7.0)
np.allclose(np.einsum('ijkl,kl->ij', swv(flat, (3, 3)), box), 7.0)  # => True

# an identity kernel is a no-op
ident = np.zeros((3, 3)); ident[1, 1] = 1
np.array_equal(np.einsum('ijkl,kl->ij', swv(img, (3, 3)), ident),
               img[1:-1, 1:-1])                                     # => True
#
# kernels that sum to 1 preserve brightness; kernels that
# sum to 0 (every edge detector) return 0 on flat input.
# Both are one-line tests of a filter you just wrote.

# ============================================
# Compare

np.correlate(a, v)                      # 1-D, no flip
np.convolve(a, v)                       # 1-D, flips
(swv(t, k) * ker).sum(axis=(-2,-1))     # explicit, an intermediate
np.einsum('ijkl,kl->ij', swv(t,k), ker) # contracted, no intermediate
swv(t, k)[::s, ::s]                     # strided
np.pad(t, k//2)                         # 'same'
swv(t,(k,k)).mean(axis=(-2,-1))         # unweighted == box blur

# the whole family is: windows, times weights, summed.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the pattern|`swv(t, k)` then `einsum('ijkl,kl->ij', w, ker)`|
|1-D, no flip|`np.correlate`|
|1-D, flipped|`np.convolve`|
|'same' output|`np.pad(t, k//2)` first|
|a stride|slice the position axes `[::s]`|
|the output size|`(n + 2p - k)//s + 1`|
|O(k) not O(k²)|two 1-D passes for a separable kernel|
|a full conv layer|`einsum('nchwij,ocij->nohw', win, kers)`|
|to check a filter|blur a constant; it should not change|

---

## Key Insight

**Convolution is a windowed contraction: extract every window (free), multiply by weights, sum the window axes.**

```python
np.einsum('ijkl,kl->ij', sliding_window_view(img, (3,3)), kernel)
```

Both halves came from earlier lessons — the windows are lesson 28's stride trick, and the contraction is lesson 22's multi-axis reduction with weights. Nothing is materialised: the `k²` copies part 2 had to make never exist.

Everything a framework exposes as a parameter is a small edit here:

|Framework option|Here|
|---|---|
|`stride=s`|`w[::s, ::s]`|
|`padding='same'`|`np.pad(t, k//2)`|
|`groups`, `dilation`|more slicing / more subscripts|
|multi-channel|one more contracted index|

That last row is the one worth internalising. A complete convolutional layer — batch, input channels, output channels, spatial positions — is:

```python
np.einsum('nchwij,ocij->nohw', windows, kernels)
```

The letters appearing on **both** sides of the comma but **not** after the arrow (`c`, `i`, `j`) are summed away. "Combine all input channels" is the single letter `c`.

Two things to keep straight:

1. **`np.convolve` flips the kernel; `np.correlate` does not** — verified above, `[2,2,2]` versus `[-2,-2,-2]`. Symmetric kernels hide the difference; every gradient filter reveals it as a sign error. ML "convolution" is correlation.
    
2. **Separability still pays.** Two 1-D passes cost `2k` multiplies per output against `k²` — 18 versus 81 for a 9×9. The extraction being free does not make the arithmetic free.
    

---

## The Windows Section, Complete

|Lesson|Windows|Reduction|Cost of extraction|
|---|---|---|---|
|28 Patch Extraction|overlapping|none — you keep them|**free** (a view)|
|29 Pooling|non-overlapping|`max` / `mean`|**free** (a reshape)|
|**30 Convolution**|overlapping|**weighted** sum|**free** (a view)|

```text
   windows  ─┬── keep            ──►  28
             ├── reduce          ──►  29  (partition)
             └── reduce × weights ──►  30  (every position)
```

Compare that with part 2's window section: four lessons largely *about avoiding the cost of windowing*, between integral images, separable passes and block sums. With strides, extraction is free and only the arithmetic is left.

> **Mental shift:** part 2 taught windows as a copying problem you had to optimise around. Part 3 makes the copy vanish, and what remains is a contraction. That's why the next section is about contraction in general. Convolution turns out to be one `einsum` among many, and `einsum` is the vocabulary the rest of tensor computation is written in.
