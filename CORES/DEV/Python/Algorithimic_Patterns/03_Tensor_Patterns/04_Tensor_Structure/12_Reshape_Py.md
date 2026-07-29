# 12. Reshape

## Mental Model

Part 2's lesson 22 described a matrix as **a tape with cuts in it**, and reshape as moving the cuts. That's still exactly right. There are just more cuts now.

```text
shape (2, 3, 4)      the tape:  0 1 2 3 4 5 ... 23
shape (4, 6)         same tape, different cuts
shape (24,)          no cuts
```

Two rules, unchanged from rank 2:

- **The linear order never changes.** `t.reshape(...).ravel() == t.ravel()`, always.
    
- **The element count has to be conserved.** `prod(new_shape) == t.size`, or it raises.
    

And here's the comparison that matters most: part 2's lesson-22 warning, now at rank 3.

```text
t.reshape(3, 2, 4)          t.transpose(1, 0, 2)

both shape (3, 2, 4) — and they are DIFFERENT tensors
```

Reshape **re-cuts** the tape. Transpose **re-orders** it. Getting them confused is a silent data corruption, not a crash.

What is new at rank 3+ is that reshape stops being purely notional. `-1` infers one axis, `reshape` merges and splits axes as a matter of routine — and, per lesson 4, it is **free only when the array is contiguous**. On a transposed view it silently allocates.

---

## Relationship to Cognitive Verb

```text
Regroup
   ↓
Reshape
```

Related verbs:

- Regroup
- Re-cut
- Merge and split axes
- Rewrap
- Change the dimensions

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Reshape|new shape|`t.reshape(4, 6)`|
|Infer one axis|let it compute|`-1` in exactly one slot|
|Flatten|to rank 1|`t.reshape(-1)`|
|Keep the batch|collapse the rest|`t.reshape(N, -1)`|
|Collapse to vectors|keep the last axis|`t.reshape(-1, t.shape[-1])`|
|Merge two axes|multiply the sizes|`t.reshape(a*b, c)`|
|Split one axis|factor it|`t.reshape(a, b//k, k)`|
|Column-major fill|Fortran order|`reshape(..., order='F')`|
|Check for a copy|did it allocate?|`np.shares_memory(t, t.reshape(...))`|
|Force contiguity first|make reshape free|`np.ascontiguousarray(t)`|

---

## Common Uses

- Flattening feature maps before a dense layer
- Batching: `(N, H, W)` ↔ `(N, H*W)`
- Splitting a channel axis into groups (grouped convolution)
- Turning a flat buffer from a file into a volume
- Preparing data for a matrix multiply
- Splitting a sequence into fixed-length windows
- Merging batch and time axes to run a per-step operation once

---

## Hidden Interview Problems

- Reshape an array into given dimensions
- Convert a 1-D buffer into an n-D array
- Merge or split a specific axis
- Explain why reshape and transpose differ
- Explain when reshape copies
- Flatten all but the first dimension
- Reshape with one unknown dimension

---

## Recognition Clues

If you hear...

- "reshape into..."
- "flatten before the classifier..."
- "same elements, different dimensions..."
- "collapse the spatial dimensions..."
- "split the channels into groups..."
- "(N, -1)..."

...think **Reshape**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Constraint|`prod(new_shape) == t.size`|
|Linear order|**Preserved** — the defining property|
|`-1`|Infers one axis; only one allowed|
|Fill order|Row-major (C) by default|
|Returns|A **view** if contiguous, else a **copy**|
|Rank|Any → any|
|Inverse|Reshape back to the original shape|
|Time Complexity|O(1) as a view, O(size) as a copy|
|Common Domains|ML plumbing, I/O, linear algebra|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np

t = np.arange(24).reshape(2, 3, 4)

# ============================================
# The one idiom to remember
#
#   same elements, same order, new grouping

t.reshape(4, 6)
# => array([[ 0,  1,  2,  3,  4,  5],
#           [ 6,  7,  8,  9, 10, 11],
#           [12, 13, 14, 15, 16, 17],
#           [18, 19, 20, 21, 22, 23]])

t.reshape(6, 4).shape           # => (6, 4)
t.reshape(24).shape             # => (24,)
t.reshape(2, 2, 3, 2).shape     # => (2, 2, 3, 2)

# the invariant that defines the operation:
np.array_equal(t.reshape(4, 6).ravel(), t.ravel())          # => True

# ============================================
# -1 infers one axis

t.reshape(-1, 4).shape          # => (6, 4)
t.reshape(2, -1).shape          # => (2, 12)
t.reshape(2, -1, 4).shape       # => (2, 3, 4)

try:
    t.reshape(-1, -1)
except ValueError as e:
    print(e)                    # can only specify one unknown dimension

try:
    t.reshape(-1, 5)
except ValueError as e:
    print(e)                    # cannot reshape array of size 24 into shape (5)
#
# 24 is not divisible by 5, so there is no integer to
# infer. `-1` does division, not magic.

try:
    t.reshape(5, 5)
except ValueError as e:
    print(e)                    # cannot reshape array of size 24 into shape (5,5)

# ============================================
# RESHAPE IS NOT TRANSPOSE
#
# Same output shape. Different tensors. This is part 2's
# lesson 22 warning, one rank up.

t.reshape(3, 2, 4).shape        # => (3, 2, 4)
t.transpose(1, 0, 2).shape      # => (3, 2, 4)

np.array_equal(t.reshape(3, 2, 4), t.transpose(1, 0, 2))    # => False

t.reshape(3, 2, 4)[0]
# => array([[0, 1, 2, 3],
#           [4, 5, 6, 7]])          consecutive on the tape

t.transpose(1, 0, 2)[0]
# => array([[ 0,  1,  2,  3],
#           [12, 13, 14, 15]])      row 0 of each block

# stated precisely, in flat order:
t.reshape(3, 2, 4).ravel()[:8]      # => [0, 1, 2, 3, 4, 5, 6, 7]
t.transpose(1, 0, 2).ravel()[:8]    # => [0, 1, 2, 3, 12, 13, 14, 15]
#
#   reshape   preserves the tape, moves the cuts
#   transpose reorders the tape
#
# Neither raises. If you pick the wrong one your data is
# scrambled and everything downstream still runs.

# ============================================
# VIEW OR COPY? It depends on contiguity

np.shares_memory(t, t.reshape(4, 6))        # => True    free

tr = t.transpose(1, 0, 2)
tr.flags['C_CONTIGUOUS']                    # => False
np.shares_memory(tr, tr.reshape(24))        # => False   ALLOCATED
#
# lesson 4's point, in its most common disguise:
#
#   x.transpose(...).reshape(...)
#
# looks like two O(1) operations and is really one free
# operation plus a full copy. Usually fine — but it is
# the line to look at when a "cheap" pipeline is slow.

np.ascontiguousarray(tr).flags['C_CONTIGUOUS']          # => True
#
# make the copy explicit if you are going to reshape
# repeatedly.

# ============================================
# The four reshape patterns you will actually write

b = np.arange(2*3*4*4).reshape(2, 3, 4, 4)      # N, C, H, W
b.shape                         # => (2, 3, 4, 4)

# 1. collapse the spatial axes, keep N and C
b.reshape(2, 3, -1).shape       # => (2, 3, 16)

# 2. flatten everything but the batch  <- the classic
b.reshape(2, -1).shape          # => (2, 48)
b.reshape(b.shape[0], -1).shape # => (2, 48)   same, rank-agnostic
#
# this is the line before a dense layer in every CNN.

# 3. collapse to a list of vectors along the last axis
b.reshape(-1, b.shape[-1]).shape        # => (24, 4)
#
# "treat every position as an independent sample",
# whatever the leading shape. (Lesson 5 used this too.)

# 4. split an axis into factors
np.arange(12).reshape(3, 4).reshape(3, 2, 2).shape      # => (3, 2, 2)
#
# splitting a 4-wide axis into 2x2. Grouped convolution
# and multi-head attention are both this move.

# and merging is just multiplication:
t.reshape(2*3, 4).shape                                 # => (6, 4)
np.array_equal(t.reshape(6, 4), t.reshape(2*3, 4))      # => True

# ============================================
# Fill order

np.arange(6).reshape(2, 3)
# => array([[0, 1, 2],
#           [3, 4, 5]])          C order: fills rows first

np.arange(6).reshape(2, 3, order='F')
# => array([[0, 2, 4],
#           [1, 3, 5]])          F order: fills columns first
#
# same as part 2 lesson 22. Python, C and image formats
# are C order; Fortran, MATLAB and R are F order. Data
# crossing that boundary needs the flag or it scrambles.

# ============================================
# reshape returns a NEW object

t.reshape(4, 6) is t            # => False
#
# it never modifies in place. (Assigning to `.shape`
# used to be the in-place form; it is deprecated as of
# NumPy 2.5 — use reshape.)

# ============================================
# Round trip

np.array_equal(t.reshape(-1).reshape(2, 3, 4), t)       # => True
#
# reshape is invertible as long as you remember the
# original shape. The shape is the information that
# flattening throws away (lesson 13).

# ============================================
# Compare

t.reshape(3, 2, 4)      # re-cut the tape       -> flat order KEPT
t.transpose(1, 0, 2)    # re-order the tape     -> flat order CHANGED
t.ravel()               # remove all cuts       -> lesson 13
t[:, None]              # add an empty cut      -> lesson 16

np.array_equal(t.reshape(3,2,4).ravel(), t.ravel())         # => True
np.array_equal(t.transpose(1,0,2).ravel(), t.ravel())       # => False
#
# THAT is the dividing line of this whole section.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a new shape|`t.reshape(...)`|
|one axis computed|`-1` — exactly one|
|flatten but keep the batch|`t.reshape(t.shape[0], -1)`|
|a list of last-axis vectors|`t.reshape(-1, t.shape[-1])`|
|to merge axes|multiply their sizes|
|to split an axis|factor its size|
|to know if it copied|`np.shares_memory(...)`|
|reshape to stay free|keep the array contiguous|
|**not** to confuse it|reshape ≠ transpose, even at the same shape|

---

## Key Insight

**Reshape moves the cuts; it never moves the cells.** The test is one line and it is the definition:

```python
t.reshape(anything).ravel() == t.ravel()        # always True
t.transpose(anything).ravel() == t.ravel()      # generally False
```

That distinction is the dividing line of the whole structure section, and at rank 3+ it is easy to trip over because **reshape and transpose can produce the same shape from the same input**. `t.reshape(3,2,4)` and `t.transpose(1,0,2)` are both `(3,2,4)` and hold different numbers. Nothing raises. If you reach for the wrong one, your data is quietly transposed and every later step still runs.

Three practical points:

1. **`-1` divides, it does not guess.** `t.reshape(-1, 5)` on 24 elements raises, because 24/5 is not an integer. Only one `-1` per call.
    
2. **Reshape is free only on contiguous data.** `x.transpose(...).reshape(...)` is one free operation followed by a full copy — the most common hidden allocation in tensor code.
    
3. **The patterns are few.** `reshape(N, -1)` before a dense layer, `reshape(-1, C)` to treat every position as a sample, factoring an axis for groups or heads, and merging adjacent axes. Almost all real reshapes are one of those four.
    

---

## The Structure Section

|Lesson|Operation|Shape|Flat order|
|---|---|---|---|
|**12 Reshape**|regroup|changed|**preserved**|
|13 Flatten / Ravel|collapse|`→ (size,)`|**preserved**|
|14 Permute Axes|reorder axes|permuted|**changed**|
|15 Swap / Move Axis|reorder axes|permuted|**changed**|
|16 Squeeze / Expand|add or drop size-1|±1 rank|**preserved**|

```text
                  ┌── keep the tape order  ──►  12, 13, 16
  same cells  ────┤
                  └── reorder the tape     ──►  14, 15
```

> **Mental shift:** part 2 could treat reshape as a curiosity, because a `2×3` matrix doesn't have many interesting regroupings. At rank 3 and up, reshape is *plumbing you write constantly*: merging batch and time, flattening before a dense layer, splitting channels into heads. The rules didn't change. The frequency did.
