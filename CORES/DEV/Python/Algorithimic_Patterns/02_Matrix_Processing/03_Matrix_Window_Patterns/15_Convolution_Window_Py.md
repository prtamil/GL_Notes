# 15. Convolution Window

## Mental Model

The last three lessons all slid a window. This one adds the missing piece: **weights**.

```text
window                kernel              output
[[1, 2, 3],           [[0, -1,  0],
 [5, 6, 7],     ×      [-1, 5, -1],   →   one number
 [9,10,11]]            [0, -1,  0]]

  sum of (cell × weight), all k² of them
```

A **kernel** is a tiny matrix of coefficients. Slide it over the input, and at each position take the **weighted sum** of the window. That single operation — multiply-and-add over a sliding window — is blur, sharpen, edge detection, embossing, gradient, and every convolutional layer in every neural network.

Everything you already know applies:

|From|You get|
|---|---|
|Lesson 12|the sliding positions and the output-shrinks rule|
|Lesson 13|stride — a strided convolution is a tiled one|
|Lesson 14|padding modes, and `im2col`|

Two details are genuinely new and both trip people up:

- **Convolution flips the kernel; correlation does not.** What deep learning calls "convolution" is actually correlation. It only matters for asymmetric kernels — but then it matters completely.
    
- **Normalization.** A blur kernel of nine `1`s makes the image nine times brighter unless you divide by the kernel's sum.
    

---

## Relationship to Cognitive Verb

```text
Weigh
   ↓
Convolution Window
```

Related verbs:

- Weigh and combine
    
- Filter
    
- Apply a stencil
    
- Blend neighbours
    
- Detect a feature
    

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Weighted sum|window × kernel|`sum(x*w for x, w in zip(...))`|
|Kernel loop|the k² terms|nested `range(k)` over `kernel[i][j]`|
|Padding|off-grid reads|`at(m, r, c, mode)` from lesson 14|
|'valid' output|no padding|`(rows - k)//s + 1`|
|'same' output|shape preserved|`pad = k // 2`|
|Normalize|keep brightness|divide by `sum(map(sum, kernel))`|
|Flip the kernel|true convolution|`[row[::-1] for row in kernel[::-1]]`|
|Separable kernel|O(k) not O(k²)|two 1D passes|
|Gradient magnitude|combine two kernels|`(gx*gx + gy*gy) ** 0.5`|
|Matrix-multiply form|how libraries do it|`im2col` then one dot product|

---

## Common Uses

- Blur, sharpen, emboss, denoise
    
- Edge detection (Sobel, Prewitt, Laplacian)
    
- Gaussian smoothing
    
- Unsharp masking
    
- Convolutional neural networks
    
- Feature maps and templates
    
- Audio and signal filtering (the 1D case)
    
- Cellular automata as a filter
    
- Heat diffusion and physical simulation stencils
    

---

## Hidden Interview Problems

- Image smoothing / box blur
    
- Apply a filter to a matrix
    
- Edge detection on a grid
    
- Implement 2D convolution with stride and padding
    
- Compute the output shape of a conv layer
    
- Game of Life expressed as a filter
    
- Weighted moving average over a grid
    
- Separable filter optimisation
    

---

## Recognition Clues

If you hear...

- "apply this kernel / filter / mask..."
    
- "weighted average of neighbours..."
    
- "blur, sharpen, detect edges..."
    
- "stride and padding..."
    
- "3×3 stencil..."
    
- "feature map..."
    

...think **Convolution Window**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Dimension|2D|
|Unit|A k × k window reduced by a k × k kernel|
|Reduction|Weighted sum (multiply-accumulate)|
|Output shape|`(rows + 2p - k)//s + 1` per axis|
|'valid'|`p = 0` — output shrinks by `k-1`|
|'same'|`p = k//2` — output keeps its shape|
|Naive cost|O(rows × cols × k²)|
|Separable cost|O(rows × cols × k)|
|Common Domains|Images, vision, ML, signal processing|

---

## Python Recipe Book

```python
# ============================================
# Basic matrix

m = [[1,  2,  3,  4],
     [5,  6,  7,  8],
     [9,  10, 11, 12],
     [13, 14, 15, 16]]

# ============================================
# Padding — the same helper as lesson 14
#
# Convolution reads outside the matrix by construction,
# so this is not optional.

MODES = {
    "clamp":   lambda i, n: min(max(i, 0), n - 1),
    "reflect": lambda i, n: abs(i) if i < 0 else (2*n - 2 - i if i >= n else i),
    "wrap":    lambda i, n: i % n,
}

def at(m, r, c, mode="zero", fill=0):
    rows, cols = len(m), len(m[0])
    if mode == "zero":
        return m[r][c] if 0 <= r < rows and 0 <= c < cols else fill
    f = MODES[mode]
    return m[f(r, rows)][f(c, cols)]

# ============================================
# The one function to remember
#
# Slide, multiply, add. Everything else is a parameter.

def convolve(m, kernel, stride=1, pad=0, mode="zero", flip=False):
    k = len(kernel)
    if flip:                                    # true convolution
        kernel = [row[::-1] for row in kernel[::-1]]
    rows, cols = len(m), len(m[0])
    oh = (rows + 2*pad - k)//stride + 1
    ow = (cols + 2*pad - k)//stride + 1
    def cell(r, c):
        return sum(at(m, r+i-pad, c+j-pad, mode) * kernel[i][j]
                   for i in range(k) for j in range(k))
    return [[cell(r*stride, c*stride) for c in range(ow)] for r in range(oh)]

# ============================================
# The kernel zoo

IDENTITY = [[0,  0,  0],
            [0,  1,  0],
            [0,  0,  0]]

BOX      = [[1,  1,  1],
            [1,  1,  1],
            [1,  1,  1]]      # divide by 9

SHARPEN  = [[0, -1,  0],
            [-1, 5, -1],
            [0, -1,  0]]

LAPLACE  = [[0,  1,  0],
            [1, -4,  1],
            [0,  1,  0]]

SOBEL_X  = [[-1, 0,  1],
            [-2, 0,  2],
            [-1, 0,  1]]

SOBEL_Y  = [[-1, -2, -1],
            [0,   0,  0],
            [1,   2,  1]]

MOORE    = [[1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]]        # the 8-neighborhood, as a kernel

# read a kernel by its SIGNS:
#   all positive          -> averaging / blur
#   sums to zero          -> a difference / edge detector
#   big centre, negative ring -> sharpen
#   opposite signs across an axis -> a directional gradient

# ============================================
# 'valid' vs 'same' — the shape decision
#
# valid: no padding, output shrinks by k-1
# same : pad = k//2, output keeps its shape

convolve(m, IDENTITY, pad=1) == m       # => True   identity is a no-op

convolve(m, BOX)                        # 'valid', 4x4 -> 2x2
# =>
# [[54, 63],
#  [90, 99]]

# ...which is exactly lesson 12's window_sums(m, 3).
# A box kernel IS the sliding window sum.

# ============================================
# Normalize, or everything gets 9x brighter

[[x // 9 for x in row] for row in convolve(m, BOX)]
# =>
# [[6,  7 ],
#  [10, 11]]      the real 3x3 means

# in general: divide by sum(map(sum, kernel)),
# and skip it when that sum is 0 (edge kernels)

def norm(kernel):
    s = sum(map(sum, kernel))
    return s if s else 1

# ============================================
# Padding mode is VISIBLE in the output

[[x // 9 for x in row] for row in convolve(m, BOX, pad=1, mode="zero")]
# =>
# [[1,  2,  3,  2],
#  [3,  6,  7,  5],
#  [6,  10, 11, 7],
#  [5,  8,  8,  6]]
#      ^ the border collapsed toward 0 — a dark frame

[[x // 9 for x in row] for row in convolve(m, BOX, pad=1, mode="clamp")]
# =>
# [[2,  3,  4,  5 ],
#  [5,  6,  7,  7 ],
#  [9,  10, 11, 11],
#  [12, 12, 13, 14]]
#      no dark frame — the edge extended itself
#
# same kernel, same image, different border story.
# Zero padding is the default in ML and the wrong
# default for image processing.

# ============================================
# Sharpen and Laplacian

convolve(m, SHARPEN, pad=1, mode="clamp")
# =>
# [[-4, -2, -1, 1 ],
#  [4,  6,  7,  9 ],
#  [8,  10, 11, 13],
#  [16, 18, 19, 21]]
#
# note the values escaped 1..16 — real image code has to
# clip back to the valid range afterwards

convolve(m, LAPLACE, pad=1, mode="clamp")
# =>
# [[5,  4,  4,  3 ],
#  [1,  0,  0,  -1],
#  [1,  0,  0,  -1],
#  [-3, -4, -4, -5]]
#
# zero in the interior: a linear ramp has no curvature.
# The Laplacian sums to 0, so flat AND sloped regions
# vanish, leaving only bends. That is what "edge kernel"
# means mechanically.

# ============================================
# Edge detection — a vertical edge, found

img = [[0, 0, 0, 9, 9, 9],
       [0, 0, 0, 9, 9, 9],
       [0, 0, 0, 9, 9, 9],
       [0, 0, 0, 9, 9, 9]]

gx = convolve(img, SOBEL_X)
# =>
# [[0, 36, 36, 0],
#  [0, 36, 36, 0]]      the vertical edge lights up

gy = convolve(img, SOBEL_Y)
# =>
# [[0, 0, 0, 0],
#  [0, 0, 0, 0]]        no horizontal edge exists

# gradient magnitude — direction-free edge strength
[[round((a*a + b*b) ** 0.5, 1) for a, b in zip(rx, ry)]
 for rx, ry in zip(gx, gy)]
# =>
# [[0.0, 36.0, 36.0, 0.0],
#  [0.0, 36.0, 36.0, 0.0]]

# ============================================
# Correlation vs convolution — the flip
#
# Probe with an impulse: a single 1 surrounded by 0s.
# Whatever comes out IS the kernel, flipped or not.

asym = [[1, 2],
        [3, 4]]

impulse = [[0, 0, 0],
           [0, 1, 0],
           [0, 0, 0]]

convolve(impulse, asym)                 # correlation (no flip)
# =>
# [[4, 3],
#  [2, 1]]      the kernel comes out REVERSED

convolve(impulse, asym, flip=True)      # true convolution
# =>
# [[1, 2],
#  [3, 4]]      the kernel comes out as written
#
# true convolution is associative and commutative;
# correlation is not. For symmetric kernels (box,
# gaussian, laplace) the two are identical — which is
# why nobody notices until they use an asymmetric one.

# ============================================
# Separable kernels — O(k) instead of O(k²)
#
# If kernel == outer(col, row), then one 2D pass equals
# two 1D passes. Box, Gaussian and Sobel all separate.

def conv1d_rows(m, k1):
    n = len(k1)
    return [[sum(row[c+i] * k1[i] for i in range(n))
             for c in range(len(row) - n + 1)]
            for row in m]

def conv1d_cols(m, k1):
    n = len(k1)
    return [[sum(m[r+i][c] * k1[i] for i in range(n))
             for c in range(len(m[0]))]
            for r in range(len(m) - n + 1)]

conv1d_cols(conv1d_rows(m, [1, 1, 1]), [1, 1, 1]) == convolve(m, BOX)
# => True
# because BOX == [1,1,1] outer [1,1,1]

conv1d_cols(conv1d_rows(img, [-1, 0, 1]), [1, 2, 1]) == convolve(img, SOBEL_X)
# => True
# because SOBEL_X == [1,2,1]^T outer [-1,0,1]

# a 9x9 Gaussian: 81 multiplies per pixel, or 18.
# Same trick as lesson 12's max2d — separability is
# the recurring escape from O(k²).

# ============================================
# Game of Life is a convolution
#
# The Moore kernel counts live neighbours; the rule is
# a threshold on that count. Lesson 10 wrote this as a
# neighbour loop — same computation, different clothes.

blinker = [[0, 0, 0],
           [1, 1, 1],
           [0, 0, 0]]

counts = convolve(blinker, MOORE, pad=1)
# =>
# [[2, 3, 2],
#  [1, 2, 1],
#  [2, 3, 2]]

[[int(n == 3 or (blinker[r][c] and n == 2)) for c, n in enumerate(row)]
 for r, row in enumerate(counts)]
# =>
# [[0, 1, 0],
#  [0, 1, 0],
#  [0, 1, 0]]      the blinker turned, exactly as in lesson 10

# ============================================
# Output shapes — the formula, again
#
#   out = (in + 2*pad - k) // stride + 1

def out_shape(rows, cols, k, stride=1, pad=0):
    return ((rows + 2*pad - k)//stride + 1,
            (cols + 2*pad - k)//stride + 1)

out_shape(4, 4, 3, 1, 0)        # => (2, 2)   'valid'
out_shape(4, 4, 3, 1, 1)        # => (4, 4)   'same'
out_shape(4, 4, 2, 2, 0)        # => (2, 2)   stride 2 == tiling

len(convolve(m, BOX))           # => 2
len(convolve(m, BOX, pad=1))    # => 4

# ============================================
# Why im2col exists
#
# Flatten every patch to a row (lesson 14), flatten the
# kernel to a column, and the whole convolution is ONE
# dot product per row. That is how real libraries run it.

def patches(m, k, stride=1):
    rows, cols = len(m), len(m[0])
    return [[row[c:c+k] for row in m[r:r+k]]
            for r in range(0, rows-k+1, stride)
            for c in range(0, cols-k+1, stride)]

def conv_im2col(m, kernel, stride=1):
    k = len(kernel)
    w = [x for row in kernel for x in row]
    cols_ = [[x for row in p for x in row] for p in patches(m, k, stride)]
    out = [sum(a*b for a, b in zip(col, w)) for col in cols_]
    _, ow = out_shape(len(m), len(m[0]), k, stride)
    return [out[i:i+ow] for i in range(0, len(out), ow)]

conv_im2col(m, BOX) == convolve(m, BOX)         # => True
conv_im2col(m, SOBEL_X) == convolve(m, SOBEL_X) # => True

# ============================================
# Compare

# window -> sum                    -> lesson 12
sum(map(sum, window))

# window -> sum, stride k          -> lesson 13
pool(m, k, k, sum)

# window -> kept                   -> lesson 14
patches(m, k, stride)

# window -> WEIGHTED sum           -> this lesson
sum(x * w for x, w in zip(flat_window, flat_kernel))

# and the box kernel closes the loop:
convolve(m, BOX) == window_sums(m, 3)   # True — window_sums from lesson 12.
                                        # A blur IS a sliding window sum.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the operation|slide → multiply → add|
|shape preserved|`pad = k // 2` ('same')|
|shape shrinks|`pad = 0` ('valid'), loses `k-1`|
|the output size|`(in + 2*pad - k)//stride + 1`|
|brightness kept|divide by `sum(map(sum, kernel))`|
|true convolution|`[row[::-1] for row in kernel[::-1]]`|
|an edge detector|a kernel whose weights sum to **0**|
|a blur|a kernel of all-positive weights|
|O(k) not O(k²)|separate into two 1D passes|
|no dark border|`mode="clamp"` or `"reflect"`, not zero|

---

## Key Insight

**Convolution is the sliding window with a weighted reduction.** The loop is identical to lesson 12; `sum(window)` became `sum(window × kernel)`. Everything expressive lives in the kernel, not the code:

```text
weights all positive     ->  blur      (an average)
weights summing to zero  ->  edges     (a difference)
big centre, negative ring ->  sharpen  (original + edges)
signs split across an axis -> gradient (a directional derivative)
```

That is why one twelve-line function covers blur, sharpen, Sobel, Laplacian and a CNN layer — you are not writing new algorithms, you are writing new numbers.

Four things to actually remember:

1. **The shape formula** `(in + 2p - k)//s + 1` is the same one from lesson 14 and governs every conv layer you will ever configure.
    
2. **Normalize or don't, deliberately.** Divide by the kernel sum for averaging kernels; leave edge kernels alone, since their sum is zero.
    
3. **Padding mode is a visible choice.** Zero padding puts a dark frame on a blurred image; clamp and reflect do not.
    
4. **Separability is the optimisation** — the same trick that made `max2d` cheap in lesson 12.
    

And the one that catches everybody: **"convolution" in machine learning is correlation.** The kernel is not flipped. It makes no difference for symmetric kernels and complete nonsense for asymmetric ones.

---

## The Window Section in One Table

|Lesson|Stride|What happens to the window|Output|
|---|---|---|---|
|12 Sliding Window|1|reduced to a number|smaller matrix|
|13 Block / Tile|`k`|reduced to a number|much smaller matrix|
|14 Patch Extraction|any|**kept**|list of matrices|
|15 Convolution|any|reduced **with weights**|feature map|

```text
                 ┌── reduce ─────────► 12 (stride 1)
                 │                     13 (stride k)
window (size, stride)
                 ├── keep ───────────► 14
                 └── reduce × weights ► 15
```

Everything in this section is the same two slices — `m[r:r+k]` and `row[c:c+w]` — under four different intentions.

> **Mental shift:** traversal chose an *order*, neighborhood chose a *shape*, and windows choose a *shape plus a stride plus what you do with it*. Once those three are parameters rather than assumptions, blur, pooling, Sudoku boxes, im2col and a CNN layer are all the same loop.
