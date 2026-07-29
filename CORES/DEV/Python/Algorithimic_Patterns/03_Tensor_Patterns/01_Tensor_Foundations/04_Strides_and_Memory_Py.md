# 4. Strides and Memory Layout

## Mental Model

A tensor looks nested. In memory it's **flat**: one contiguous run of numbers, plus a recipe for reading it.

```text
shape   (2, 3, 4)
memory  0 1 2 3 4 5 6 7 8 ... 23        one line of 24 values
```

That recipe is the **strides**: how far to step through memory to move each index forward by one.

```text
axis 2  (innermost)  step 1      the next number along
axis 1               step 4      skip a whole row of 4
axis 0  (outermost)  step 12     skip a whole block of 3x4
```

which turns any index into a position by a dot product:

```text
flat = i*12 + j*4 + k*1
```

Lesson 23 in part 2 had exactly this at rank 2: `i = r*cols + c`. Strides are that same formula generalised, with NumPy storing the multipliers instead of recomputing them each time.

The payoff is the thing to actually take away:

> **Reshape and transpose do not move data. They rewrite `shape` and `strides`.**

`t.reshape(4, 6)` keeps the same memory and changes the multipliers. `t.transpose(2,1,0)` keeps the same memory and *permutes* the multipliers. Both are **views** — free, and sharing storage with the original, so writing through one changes the other.

That is also why some operations are suddenly not free: once the strides are out of order, the array is no longer **contiguous**, and anything that needs a flat run of memory has to copy.

---

## Relationship to Cognitive Verb

```text
Locate
   ↓
Strides and Memory Layout
```

Related verbs:

- Locate in memory
- Step through
- Lay out
- Address arithmetic
- Interpret the buffer

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Strides, in bytes|memory step per axis|`t.strides`|
|Strides, in elements|divide out|`s // t.itemsize`|
|Bytes per element|dtype size|`t.itemsize`|
|Flat index|multi → flat|`i*s0 + j*s1 + k*s2`|
|Both directions|convert|`np.ravel_multi_index`, `np.unravel_index`|
|Flat view|no copy|`t.ravel()`|
|Flat copy|independent|`t.flatten()`|
|Is it contiguous?|check|`t.flags['C_CONTIGUOUS']`|
|Does it share memory?|check|`np.shares_memory(a, b)`|
|Is it a view?|check|`t.base is not None`|
|Force contiguity|copy if needed|`np.ascontiguousarray(t)`|
|Column-major|Fortran order|`order='F'`|

---

## Common Uses

- Understanding why some operations are free and others copy
- Debugging "I changed a copy and the original changed too"
- Performance: keeping loops on the innermost (stride-1) axis
- Interfacing with C, GPU or file formats that need contiguous data
- Zero-copy sliding windows (`sliding_window_view`)
- Choosing NCHW vs NHWC for cache behaviour
- Reading memory-mapped or binary data

---

## Hidden Interview Problems

- Convert a multi-dimensional index to a flat index and back
- Explain why transpose is O(1)
- Explain the difference between `ravel` and `flatten`
- Detect whether two arrays share memory
- Implement an n-dimensional array on top of a flat list
- Explain why row-major traversal is faster than column-major

---

## Recognition Clues

If you hear...

- "without copying..."
- "in place / zero-copy..."
- "contiguous..."
- "why did the original change..."
- "row-major / column-major / C order / Fortran order..."
- "cache-friendly..."

...think **Strides**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Storage|One flat buffer, whatever the rank|
|Strides|Bytes to step per axis, as a tuple|
|C order|Last axis has stride 1 (row-major) — NumPy's default|
|Flat index|`sum(index[k] * stride_in_elements[k])`|
|Reshape|A **view** — rewrites shape and strides|
|Transpose|A **view** — permutes the strides|
|Basic slice|A **view**|
|Fancy / boolean index|A **copy**|
|Contiguity|Lost when strides go out of order|
|Time Complexity|O(1) for a view, O(size) for a copy|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np

t = np.arange(24).reshape(2, 3, 4)

t.shape                     # => (2, 3, 4)
t.dtype                     # => dtype('int64')
t.itemsize                  # => 8       bytes per element

# ============================================
# The one idiom to remember
#
#   strides = how far to step per axis

t.strides                   # => (96, 32, 8)      BYTES

tuple(s // t.itemsize for s in t.strides)
# => (12, 4, 1)             ELEMENTS — the readable form
#
#   axis 2: step 1   -> the next number
#   axis 1: step 4   -> skip one row of 4
#   axis 0: step 12  -> skip one block of 3*4
#
# strides are reported in BYTES, so they depend on dtype.
# An int32 array of the same shape would show (48,16,4).
# Divide by itemsize before reasoning about them.

# ============================================
# The flat index — part 2's formula, generalised
#
# rank 2 (lesson 23):   flat = r*cols + c
# rank n:               flat = sum(index[k] * stride[k])

def c_strides(shape):
    """Element strides for C (row-major) order."""
    s = [1]
    for d in reversed(shape[1:]):
        s.append(s[-1] * d)
    return tuple(reversed(s))

c_strides((2, 3, 4))        # => (12, 4, 1)
c_strides((2, 3, 4)) == tuple(s // t.itemsize for s in t.strides)   # => True

def flat_index(idx, strides):
    return sum(i * s for i, s in zip(idx, strides))

flat_index((1, 2, 3), c_strides(t.shape))       # => 23
t.ravel()[23]                                   # => 23

# it holds for every index:
all(t.ravel()[flat_index(idx, c_strides(t.shape))] == t[idx]
    for idx in np.ndindex(*t.shape))            # => True

# the same thing with Horner's rule, no stride table:
def flat_index2(idx, shape):
    f = 0
    for i, d in zip(idx, shape):
        f = f * d + i
    return f

flat_index2((1, 2, 3), (2, 3, 4))               # => 23

# and the library versions, both directions:
np.ravel_multi_index((1, 2, 3), (2, 3, 4))      # => 23
np.unravel_index(23, (2, 3, 4))                 # => (1, 2, 3)

# ============================================
# WHY RESHAPE IS FREE
#
# The buffer is untouched; only shape and strides change.

r = t.reshape(4, 6)

r.shape                     # => (4, 6)
r.strides                   # => (48, 8)     new multipliers
np.shares_memory(t, r)      # => True        SAME memory
r.base is not None          # => True        it's a view

# writing through the view changes the original:
t2 = np.arange(24).reshape(2, 3, 4)
v = t2.reshape(4, 6)
v[0, 0] = 99
t2[0, 0, 0]                 # => 99
#
# this is part 2 lesson 21's aliasing trap, promoted to
# a design principle: NumPy returns views by default and
# expects you to know it.

# ============================================
# WHY TRANSPOSE IS FREE
#
# Permuting axes permutes the strides. Nothing moves.

tr = t.transpose(2, 1, 0)

tr.shape                    # => (4, 3, 2)       reversed
tr.strides                  # => (8, 32, 96)     also reversed
np.shares_memory(t, tr)     # => True
#
# compare with t.strides == (96, 32, 8). The transpose
# is literally the same tuple, backwards. Part 2's
# lesson 16 built a whole new list of lists; NumPy just
# relabels the stepping rule.

# ============================================
# CONTIGUITY — what you lose in exchange

t.flags['C_CONTIGUOUS']     # => True   strides decrease, last is 1
tr.flags['C_CONTIGUOUS']    # => False  strides now INCREASE
tr.flags['F_CONTIGUOUS']    # => True   it is column-major now
#
# "C contiguous" means: walking the buffer front to back
# visits elements in the array's own index order. After
# a transpose that is no longer true.

# so a reshape that needs a flat run has to COPY:
np.shares_memory(tr, tr.reshape(24))            # => False
#
# reshape is free ONLY on contiguous data. On a
# transposed array it silently allocates. That is the
# hidden cost behind `x.transpose(...).reshape(...)`
# in model code.

np.ascontiguousarray(tr).flags['C_CONTIGUOUS']  # => True    explicit copy

# ============================================
# ravel vs flatten — the same values, different sharing

t3 = np.arange(6).reshape(2, 3)

rv = t3.ravel()             # view when possible
fl = t3.flatten()           # ALWAYS a copy

np.shares_memory(t3, rv)    # => True
np.shares_memory(t3, fl)    # => False

rv[0] = 77
t3[0, 0]                    # => 77      ravel wrote through
#
# choose deliberately:
#   ravel()    fast, may alias
#   flatten()  safe, always allocates
#
# (lesson 13 covers this properly)

# ============================================
# C order vs Fortran order

np.arange(6).reshape(2, 3)
# => array([[0, 1, 2],
#           [3, 4, 5]])

np.arange(6).reshape(2, 3).ravel(order='C')     # => [0, 1, 2, 3, 4, 5]
np.arange(6).reshape(2, 3).ravel(order='F')     # => [0, 3, 1, 4, 2, 5]
#
# C order: LAST index varies fastest  (Python, C, images)
# F order: FIRST index varies fastest (Fortran, MATLAB, R)
#
# same buffer, two reading orders. This is part 2's
# lesson 22 row-major/column-major distinction, and it
# is still the thing that scrambles data crossing a
# language boundary.

# ============================================
# Why stride-1 loops are fast
#
# The innermost axis has stride 1, so consecutive reads
# hit the same cache line. The outermost has stride 12
# and jumps.

t.strides[0] // t.itemsize      # => 12    axis 0 leaps
t.strides[2] // t.itemsize      # => 1     axis 2 walks
#
# practical consequence: put the axis you iterate most
# LAST. It is why NHWC can beat NCHW for some kernels
# and why part 2's lesson 1 said row traversal is
# cache-friendly — the same fact, one rank up.

# ============================================
# A tiny tensor on top of a flat list
#
# The whole abstraction, in ten lines. This is what
# NumPy is doing.

class Tensor:
    def __init__(self, data, shape):
        self.data = list(data)
        self.shape = tuple(shape)
        self.strides = c_strides(shape)
    def __getitem__(self, idx):
        return self.data[sum(i * s for i, s in zip(idx, self.strides))]
    def reshape(self, *shape):              # free — no data touched
        return Tensor(self.data, shape)

x = Tensor(range(24), (2, 3, 4))
x[1, 2, 3]                  # => 23
x.strides                   # => (12, 4, 1)
x.reshape(4, 6)[3, 5]       # => 23     same buffer, new strides
#
# nested lists cannot do this: their sublists are
# separate objects at scattered addresses, which is
# exactly why NumPy exists.

# ============================================
# Compare

t.reshape(4, 6)             # view — rewrites strides
t.transpose(2, 1, 0)        # view — permutes strides
t[0]                        # view — offsets into the buffer
t[0:1]                      # view
t.ravel()                   # view when contiguous
t.flatten()                 # COPY, always
t[[0, 1]]                   # COPY — fancy indexing
t[t > 5]                    # COPY — boolean mask
np.ascontiguousarray(tr)    # COPY when not contiguous

# when in doubt, ask:
np.shares_memory(t, t.reshape(4, 6))            # => True
np.shares_memory(t, t.flatten())                # => False
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the memory step per axis|`t.strides` — in **bytes**|
|the readable version|`s // t.itemsize`|
|the flat position|`sum(idx[k] * stride[k])`|
|both conversions|`np.ravel_multi_index` / `np.unravel_index`|
|to know why reshape is free|it rewrites strides, not data|
|to know why transpose is free|it permutes strides|
|to know if you have an alias|`np.shares_memory(a, b)`|
|a guaranteed copy|`.flatten()`, `.copy()`|
|contiguous data for C / GPU|`np.ascontiguousarray(t)`|
|speed|iterate the **last** axis — stride 1|

---

## Key Insight

**A tensor is a flat buffer plus a stepping rule.** `shape` says how many steps along each axis; `strides` says how big each step is. The element at `(i, j, k)` lives at

```text
i*stride0 + j*stride1 + k*stride2
```

which is part 2's `r*cols + c` with one more term — nothing new, just more axes.

Everything expensive or surprising in NumPy follows from this:

1. **Reshape and transpose are O(1)** because they only rewrite `shape` and `strides`. Part 2 built new lists to transpose a matrix; NumPy reverses a 3-tuple.
    
2. **Views share memory.** `v = t.reshape(4,6); v[0,0] = 99` changes `t`. This is the aliasing trap from part 2's lesson 21 elevated to the default behaviour — `np.shares_memory(a, b)` is how you check, and `.copy()` is how you opt out.
    
3. **Contiguity is the currency.** A transpose leaves strides out of order, so the array is no longer C-contiguous, and the next `reshape` has to allocate. `x.transpose(...).reshape(...)` looks like two free operations and is really one free one and one full copy.
    
4. **Stride 1 is cache speed.** The innermost axis walks adjacent memory; the outermost leaps. Loop over the last axis when you have the choice — the same reason part 2 called row traversal cache-friendly.
    

The one detail people misread: **strides are in bytes, not elements.** `(96, 32, 8)` for `int64` becomes `(48, 16, 4)` for `int32` on identical data. Divide by `itemsize` before comparing anything.

---

## The Foundations Section, Complete

|Lesson|Question|The answer|
|---|---|---|
|1 Shape and Rank|*How big?*|`t.shape`, a tuple|
|2 Axes|*Which direction?*|a position in that tuple|
|3 Indexing|*How do I reach it?*|integers consume axes, slices keep them|
|**4 Strides**|*Where is it really?*|`sum(idx[k] * stride[k])` in a flat buffer|

```text
  shape    (2, 3, 4)      what you asked for
  strides  (12, 4, 1)     how it is delivered
  buffer   0 1 2 ... 23   what actually exists
```

> **Mental shift:** the nesting is a fiction. There's one flat array and a tuple of multipliers, and every "free" operation in part 3 — reshape, transpose, slice, moveaxis, sliding windows — changes those multipliers rather than the data. Knowing which operations touch the buffer and which only touch the metadata is what separates tensor code that runs from tensor code that runs fast.
