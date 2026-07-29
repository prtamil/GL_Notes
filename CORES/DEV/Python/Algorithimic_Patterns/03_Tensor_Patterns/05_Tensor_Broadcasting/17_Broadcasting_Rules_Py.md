# 17. Broadcasting Rules

## Mental Model

Every operation so far needed two tensors of the **same shape**. Broadcasting is the rule that lets shapes disagree — and it is not a convenience feature, it is *how tensor arithmetic works*.

The algorithm is three lines:

```text
1. Right-align the two shapes.
2. Pad the shorter one with leading 1s.
3. For each axis: sizes must be EQUAL, or one must be 1.
   The output takes the larger.
```

```text
    a  (3, 4)          a  (2, 3, 4)          a  (3, 1)
    b     (4,)         b     (3, 1)          b     (1, 4)
    ----------         -------------         ------------
       (3, 4)             (2, 3, 4)             (3, 4)
```

The word doing the work is **right-align**. Shapes are matched from the *last* axis backwards, which is why `(3,4)` and `(4,)` combine and `(3,4)` and `(3,)` do not — the `3` lands under the `4`.

And the mechanical fact that makes it free:

> **A broadcast axis is a view with stride 0.**

Stretching a length-4 vector across 3 rows does not copy it three times. It sets that axis's stride to **0**, so every step along it reads the *same* memory. No allocation, at any size.

```text
b.strides                       (8,)
np.broadcast_to(b, (3,4)).strides   (0, 8)
                                     ↑ step nowhere
```

That is lesson 4's stride machinery doing one more job. Broadcasting is not a special case bolted on — it is the same view mechanism with a zero in it.

---

## Relationship to Cognitive Verb

```text
Stretch
   ↓
Broadcasting Rules
```

Related verbs:

- Stretch
- Match shapes
- Replicate without copying
- Combine unequal
- Align and apply

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Any elementwise op|it just happens|`a + b`, `a * b`, `a > b`|
|Predict the result|no execution|`np.broadcast_shapes(s1, s2)`|
|Materialise a view|stride-0 expansion|`np.broadcast_to(a, shape)`|
|Both operands expanded|see them|`np.broadcast_arrays(a, b)`|
|Scalar|rank 0|any Python number|
|Add an axis to align|control it|`a[:, None]` (lesson 9)|
|Keep an axis after reducing|the usual fix|`keepdims=True` (lesson 16)|
|In place|destination fixed|`a += b` — `b` broadcasts, `a` cannot|
|Explicit copy|when you must write|`np.tile` / `.copy()`|

---

## Common Uses

- Adding a bias vector to every row
- Scaling each channel of an image by a different factor
- Centring and normalising data
- Comparing a tensor against a threshold
- Building coordinate grids and distance fields
- Applying per-sample weights to a batch
- Any arithmetic between a tensor and a scalar

---

## Hidden Interview Problems

- Add a vector to each row of a matrix without loops
- Normalise the columns of a matrix
- Explain why `(3,4) + (3,)` fails but `(3,4) + (4,)` works
- Scale each image in a batch by a different factor
- Compute a pairwise difference matrix
- Predict the output shape of an operation
- Explain how broadcasting avoids copying

---

## Recognition Clues

If you hear...

- "add a bias to every row..."
- "per-channel scaling..."
- "without an explicit loop..."
- "operands could not be broadcast together..."
- "shapes are incompatible..."
- "apply to each..."

...think **Broadcasting**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Alignment|From the **right** (trailing axes first)|
|Missing leading axes|Treated as size 1|
|Compatible|Sizes equal, **or** one of them is 1|
|Output size per axis|The maximum of the two|
|Cost|**Free** — the stretched axis gets stride 0|
|Memory|Nothing is copied|
|Result|A new array; the *inputs* were never expanded|
|In place|Only the source may broadcast, never the destination|
|Predict it|`np.broadcast_shapes(...)`|
|Common Domains|Everything|

---

## Python Recipe Book

```python
# ============================================
# The rule, demonstrated

import numpy as np

np.broadcast_shapes((3, 4), (4,))           # => (3, 4)
np.broadcast_shapes((2, 3, 4), (3, 1))      # => (2, 3, 4)
np.broadcast_shapes((3, 1), (1, 4))         # => (3, 4)
np.broadcast_shapes((2, 1, 3), (4, 3))      # => (2, 4, 3)
np.broadcast_shapes((1,), (2, 3, 4))        # => (2, 3, 4)
#
# work each one right-to-left:
#
#   (2, 1, 3)          (4, 3) padded to (1, 4, 3)
#      ↓  ↓  ↓
#   3 vs 3   equal        -> 3
#   1 vs 4   one is 1     -> 4
#   2 vs 1   one is 1     -> 2
#   ---------------------------
#   (2, 4, 3)

# and the failures:
for s1, s2 in [((3,), (4,)), ((2, 3), (3, 2)), ((2, 3, 4), (2, 4))]:
    try:
        np.broadcast_shapes(s1, s2)
    except ValueError as e:
        print(s1, s2, '->', str(e)[:45])
# (3,) (4,)        -> shape mismatch: objects cannot be broadcast
# (2,3) (3,2)      -> shape mismatch: ...
# (2,3,4) (2,4)    -> shape mismatch: ...
#
# note the third: (2,3,4) and (2,4) look "compatible"
# because both start with 2 — but alignment is from the
# RIGHT, so it compares 4 vs 4, then 3 vs 2. Fails.

# ============================================
# The one idiom to remember
#
#   right-align, stretch every 1

a = np.arange(12).reshape(3, 4)
b = np.array([10, 20, 30, 40])          # (4,)

a + b
# => array([[10, 21, 32, 43],
#           [14, 25, 36, 47],
#           [18, 29, 40, 51]])
#
#   (3, 4)
#      (4,)  ->  (1, 4)  ->  stretched down the rows
#   ------
#   (3, 4)
#
# b was added to EVERY row. This is "add a bias vector",
# and it is the single most common broadcast in practice.

c = np.array([[100], [200], [300]])     # (3, 1)

a + c
# => array([[100, 101, 102, 103],
#           [204, 205, 206, 207],
#           [308, 309, 310, 311]])
#
#   (3, 1) stretched ACROSS the columns — a per-row offset.

# and two vectors of different orientation give a grid:
b + c
# => array([[110, 120, 130, 140],
#           [210, 220, 230, 240],
#           [310, 320, 330, 340]])
(b + c).shape                           # => (3, 4)
#
#   (3, 1) and (1, 4)  ->  (3, 4)
#
# that is lesson 19's outer operation, arriving early.

# ============================================
# Scalars are just rank 0

t = np.arange(24).reshape(2, 3, 4)

np.shape(10)                # => ()      a scalar has no axes
(t + 10).shape              # => (2, 3, 4)
(t * 2)[0, 0]               # => array([0, 2, 4, 6])
#
# `t + 10` is broadcasting with an empty shape — every
# axis is "missing", so every axis is padded to 1 and
# stretched. Scalar arithmetic was broadcasting all along.

# ============================================
# WHY IT IS FREE: stride 0

bt = np.broadcast_to(b, (3, 4))
bt
# => array([[10, 20, 30, 40],
#           [10, 20, 30, 40],
#           [10, 20, 30, 40]])

b.strides                   # => (8,)
bt.strides                  # => (0, 8)
#                                 ↑
#              stepping along axis 0 moves ZERO bytes:
#              all three "rows" are the same memory.

np.shares_memory(b, bt)     # => True
#
# there are four numbers in memory, presented as twelve.
# This is lesson 4's stride machinery with a 0 in it —
# not a new mechanism.

# the memory saving is not marginal:
big = np.broadcast_to(np.array([1.0]), (1000, 1000))
big.base.nbytes                             # => 8       ONE float
np.tile(np.array([1.0]), (1000, 1000)).nbytes   # => 8000000
#
# a million-element view over eight bytes.

# ============================================
# ...and why broadcast_to is READ-ONLY

bt.flags['WRITEABLE']       # => False

try:
    bt[0, 0] = 1
except ValueError as e:
    print(e)                # assignment destination is read-only
#
# with stride 0, `bt[0,0]`, `bt[1,0]` and `bt[2,0]` are
# the SAME byte. Writing one would silently write all
# three, so NumPy forbids it. If you need to write,
# make a real copy: `np.broadcast_to(b, (3,4)).copy()`.

# ============================================
# Seeing both operands expanded

x, y = np.broadcast_arrays(np.arange(3)[:, None], np.arange(4)[None, :])
x.shape, y.shape            # => ((3, 4), (3, 4))

x
# => array([[0, 0, 0, 0],
#           [1, 1, 1, 1],
#           [2, 2, 2, 2]])
y
# => array([[0, 1, 2, 3],
#           [0, 1, 2, 3],
#           [0, 1, 2, 3]])
#
# the best debugging tool in this section: when a
# broadcast does something you did not expect, print
# these and look at what actually got stretched.

# ============================================
# It applies to EVERY elementwise operation

np.maximum(a, b).shape      # => (3, 4)
(a > b).shape               # => (3, 4)      comparisons too
(a / (b + 1)).shape         # => (3, 4)
#
# these are all "ufuncs" — universal functions — and
# broadcasting is part of their definition, not an
# extra step.

isinstance(np.add, np.ufunc)                # => True

# ============================================
# IN PLACE: only the SOURCE may broadcast

z = np.zeros((3, 4))
z += b                      # (4,) broadcasts up to (3,4)
z
# => array([[10., 20., 30., 40.],
#           [10., 20., 30., 40.],
#           [10., 20., 30., 40.]])

w = np.zeros((4,))
try:
    w += a                  # (3,4) cannot fit into (4,)
except ValueError as e:
    print(str(e)[:60])
# non-broadcastable output operand with shape (4,) doesn't match
#
# `+=` writes into an existing buffer, so the DESTINATION
# shape is fixed. Broadcasting can grow an operand, never
# the target. `w = w + a` works — it allocates a new (3,4).

# ============================================
# The nested-list version, for contrast

nested = a.tolist()
[[x + y for x, y in zip(row, b.tolist())] for row in nested][0]
# => [10, 21, 32, 43]
#
# correct, and it hard-codes the alignment: you chose to
# zip the LAST axis. Broadcasting makes that choice a
# rule instead of a decision, and applies it at any rank.

# ============================================
# Compare

t + 10                      # scalar    -> () padded to (1,1,1)
t + np.arange(4)            # (4,)      -> aligns with the LAST axis
t + np.arange(3)[:, None]   # (3,1)     -> aligns with axis 1
t + np.arange(2)[:, None, None]         # -> aligns with axis 0

# all of these produce (2,3,4) and none of them copies:
[(t + x).shape for x in (10, np.arange(4),
                         np.arange(3)[:, None],
                         np.arange(2)[:, None, None])]
# => [(2,3,4), (2,3,4), (2,3,4), (2,3,4)]
#
# WHERE you put the size-1 axes decides which dimension
# the vector lines up with — that is lesson 18.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the rule|right-align; equal, or one is 1|
|the output shape|`np.broadcast_shapes(s1, s2)`|
|to see what got stretched|`np.broadcast_arrays(a, b)`|
|to know why it's free|the stretched axis has **stride 0**|
|to write to a broadcast|you can't — `.copy()` first|
|a bias per row|shape `(cols,)` — aligns automatically|
|a bias per column|shape `(rows, 1)` — needs the explicit 1|
|in-place|`a += b` grows `b`, never `a`|
|to know it failed|it raises — mismatches are loud (usually)|

---

## Key Insight

**Broadcasting is right-alignment plus stride 0.**

Right-alignment explains every compatibility question: shapes are matched from the *last* axis backwards, missing leading axes count as 1, and each pair must be equal or contain a 1. `(2,3,4)` and `(2,4)` fail — not because they look different, but because alignment puts `4` under `4` and then `3` under `2`.

Stride 0 explains every cost question. A stretched axis is a view whose step size is zero, so all "copies" of the data are the *same memory*:

```text
b.strides                          (8,)
np.broadcast_to(b, (3,4)).strides  (0, 8)
```

A million-element broadcast over a single float has an 8-byte base. Nothing is duplicated — which is also why `broadcast_to` returns a **read-only** array: writing to one logical element would write to all of them.

Three practical consequences:

1. **Scalar arithmetic was always broadcasting.** `t + 10` is shape `()` padded to all-ones and stretched. There is no separate scalar code path.
    
2. **`+=` cannot grow the destination.** The source broadcasts up to the target's shape; the target never changes. `w += a` raises where `w = w + a` succeeds.
    
3. **`np.broadcast_arrays` is the debugger.** When a broadcast produces the wrong answer rather than an error, print both expanded operands and look at what actually got stretched.
    

---

## The Broadcasting Section

|Lesson|Question|
|---|---|
|**17 Broadcasting Rules**|*When do two shapes combine, and what does it cost?*|
|18 Axis Alignment|*How do I make them combine the way I meant?*|
|19 Outer Operations|*What can I build once alignment is deliberate?*|

```text
  17   the rule        right-align, stretch every 1
  18   the control     where you put the 1s decides everything
  19   the payoff      all-pairs, grids, distances — no loops
```

> **Mental shift:** parts 1 and 2 wrote a loop whenever two things of different shapes had to combine. Part 3 states the shapes and lets the alignment rule do it — at no memory cost, at any rank. The skill being built is not "remember the rule" but *predicting the output shape before running the code*, because a broadcast that succeeds when you expected an error is the quietest bug in this course.
