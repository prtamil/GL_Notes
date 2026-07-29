# 15. Swap / Move Axis

## Mental Model

`transpose(perm)` can express every rearrangement there is, but it makes you spell out **all** the axes even when you only care about one or two.

```text
rank 5, I just want axis 3 at the front:

  t.transpose(3, 0, 1, 2, 4)      count carefully, get it wrong
  np.moveaxis(t, 3, 0)            say what you mean
```

So there are two convenience operations, and telling them apart is what this lesson is about.

**`swapaxes(i, j)` — trade two axes, leave everything else alone.**

```text
(2, 3, 4)  swapaxes(0, 2)  ->  (4, 3, 2)
 ↑     ↑                        ↑     ↑
 └─────┘  those two trade places; axis 1 never moves
```

**`moveaxis(src, dst)` — pull one axis out and slot it back in, sliding the rest along.**

```text
(2, 3, 4)  moveaxis(0, 2)  ->  (3, 4, 2)
 ↑                              ────  ↑
 └── removed, then reinserted at the end;
     3 and 4 each slid left one place
```

They are **not the same operation**, and the shapes prove it: `swapaxes(0,2)` gives `(4,3,2)` while `moveaxis(0,2)` gives `(3,4,2)`. Both are legal, both are views, and picking the wrong one gives you correctly-shaped, wrongly-ordered data.

Use `swapaxes` when two axes genuinely trade places. Use `moveaxis` when one axis needs to *be somewhere* — which is most of the time, because "put the channel axis last" is the real-world request.

---

## Relationship to Cognitive Verb

```text
Relocate
   ↓
Swap / Move Axis
```

Related verbs:

- Relocate
- Exchange two
- Slide into position
- Bring to the front
- Send to the back

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Exchange two axes|symmetric|`t.swapaxes(i, j)`|
|Relocate one axis|asymmetric|`np.moveaxis(t, src, dst)`|
|To the front|for iteration|`np.moveaxis(t, k, 0)`|
|To the back|channels last|`np.moveaxis(t, k, -1)`|
|Several at once|as lists|`np.moveaxis(t, [0,1], [2,3])`|
|Batch matrix transpose|last two|`t.swapaxes(-1, -2)`|
|Full control|the general form|`t.transpose(perm)`|
|Undo a swap|it's its own inverse|swap again|
|Undo a move|reverse the arguments|`np.moveaxis(t, dst, src)`|

---

## Common Uses

- Iterating along a non-zero axis (lesson 5)
- Channels-first ↔ channels-last conversion
- Batch matrix transpose before a matmul
- Moving a time axis to the front for a sequential loop
- Matching the layout a library or kernel expects
- Bringing the axis you want to reduce into a known position
- Writing rank-agnostic helpers

---

## Hidden Interview Problems

- Swap two axes of an n-D array
- Move an axis to the front or back
- Convert between image layouts
- Batch-transpose a stack of matrices
- Write a function that reduces along an arbitrary axis
- Explain the difference between `swapaxes` and `moveaxis`

---

## Recognition Clues

If you hear...

- "put the channel dimension last..."
- "bring the batch axis to the front..."
- "swap the last two dimensions..."
- "along an arbitrary axis..."
- "channels first / channels last..."

...think **Swap / Move Axis**.

---

## Pattern Summary

|Property|`swapaxes(i, j)`|`moveaxis(src, dst)`|
|---|---|---|
|Effect|Exchange two axes|Remove and reinsert one|
|Other axes|Unmoved|**Slide** to fill the gap|
|Symmetric?|Yes — `swapaxes(i,j) == swapaxes(j,i)`|No|
|Inverse|Itself|`moveaxis(dst, src)`|
|Multiple axes|One pair|Lists accepted|
|Returns|A **view**|A **view**|
|Flat order|Changed|Changed|
|Equivalent to|A `transpose` with two entries swapped|A `transpose` with one entry relocated|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np

t = np.arange(24).reshape(2, 3, 4)

# ============================================
# swapaxes — exchange two, leave the rest

t.swapaxes(0, 1).shape          # => (3, 2, 4)
t.swapaxes(0, 2).shape          # => (4, 3, 2)
#
# axis 1 stayed at size 3 in both. Only the named pair
# moved.

np.array_equal(t.swapaxes(0, 1), t.transpose(1, 0, 2))      # => True
np.array_equal(t.swapaxes(0, 2), t.transpose(2, 1, 0))      # => True

# it is its own inverse:
np.array_equal(t.swapaxes(0, 2).swapaxes(0, 2), t)          # => True

# and symmetric:
np.array_equal(t.swapaxes(0, 2), t.swapaxes(2, 0))          # => True

# ============================================
# moveaxis — relocate one, slide the others

np.moveaxis(t, 0, 2).shape      # => (3, 4, 2)
np.moveaxis(t, 2, 0).shape      # => (4, 2, 3)
np.moveaxis(t, 0, -1).shape     # => (3, 4, 2)      -1 means "last"

np.array_equal(np.moveaxis(t, 0, 2), t.transpose(1, 2, 0))  # => True

# ============================================
# THE POINT: they are DIFFERENT operations

t.swapaxes(0, 2).shape          # => (4, 3, 2)
np.moveaxis(t, 0, 2).shape      # => (3, 4, 2)

np.array_equal(np.moveaxis(t, 0, 2), t.swapaxes(0, 2))      # => False
#
#   swapaxes(0,2)   (2,3,4) -> (4,3,2)    2 and 4 trade
#   moveaxis(0,2)   (2,3,4) -> (3,4,2)    2 is pulled out
#                                          and pushed to the end;
#                                          3 and 4 slide left
#
# On rank 2 they coincide (there is nothing to slide),
# which is exactly why the difference surprises people
# the first time they hit rank 3.
#
# and note moveaxis is NOT symmetric:
np.array_equal(np.moveaxis(t, 0, 2), np.moveaxis(t, 2, 0))  # => False
np.array_equal(np.moveaxis(np.moveaxis(t, 0, 2), 2, 0), t)  # => True
#   to undo a move, reverse the arguments.

# ============================================
# Both are views

np.shares_memory(t, np.moveaxis(t, 2, 0))       # => True
np.shares_memory(t, t.swapaxes(0, 2))           # => True
#
# same as lesson 14 — they permute strides. Everything
# in this section except an explicit copy is free.

# ============================================
# WHY THEY EXIST: readability at higher rank

r5 = np.zeros((2, 3, 4, 5, 6))

np.moveaxis(r5, 3, 0).shape             # => (5, 2, 3, 4, 6)
r5.transpose(3, 0, 1, 2, 4).shape       # => (5, 2, 3, 4, 6)
#
# identical result. The first says what you mean; the
# second requires you to write four axes you do not care
# about, in the right order, and get none of them wrong.
#
# Rule of thumb: if you care about ONE axis, use
# moveaxis. If you care about ALL of them, use transpose.

# ============================================
# Application 1: iterate a non-zero axis (lesson 5)

[sub.shape for sub in np.moveaxis(t, 1, 0)]     # => [(2,4), (2,4), (2,4)]
#
# `for sub in t` always walks axis 0, so moving the axis
# you want to the front is the whole technique — and it
# costs nothing because it is a view.

# ============================================
# Application 2: image layout conversion

img = np.zeros((8, 3, 32, 32))          # N, C, H, W

np.moveaxis(img, 1, -1).shape           # => (8, 32, 32, 3)   NHWC
np.array_equal(np.moveaxis(img, 1, -1), img.transpose(0, 2, 3, 1))
# => True
#
# "move the channel axis to the end" reads exactly like
# the intent. `transpose(0,2,3,1)` requires decoding.

# and back:
np.moveaxis(np.zeros((8, 32, 32, 3)), -1, 1).shape          # => (8, 3, 32, 32)

# ============================================
# Application 3: batch matrix transpose
#
# The correct spelling of "transpose each matrix in a
# stack", at any rank.

A = np.arange(24).reshape(2, 3, 4)      # 2 matrices, 3x4 each

A.swapaxes(-1, -2).shape                # => (2, 4, 3)
(A @ A.swapaxes(-1, -2)).shape          # => (2, 3, 3)
#
# negative axes make it rank-agnostic: the same line
# works on (3,4), (2,3,4) and (5,2,3,4).
#
# compare with the mistake from lesson 14:
A.T.shape                               # => (4, 3, 2)   reverses EVERYTHING
# (A @ A.T) raises — the batch dimensions don't line up.

# ============================================
# Moving several axes at once

np.moveaxis(np.zeros((2, 3, 4, 5)), [0, 1], [2, 3]).shape
# => (4, 5, 2, 3)
#   axes 0 and 1 go to positions 2 and 3; 4 and 5 slide left

np.moveaxis(np.zeros((2, 3, 4, 5)), [0, 3], [3, 0]).shape
# => (5, 3, 4, 2)
#   axes 0 and 3 exchange — the same as swapaxes(0, 3)

# ============================================
# Writing a rank-agnostic helper
#
# The standard trick: move the axis of interest to a
# known position, do the work, move it back.

def normalise_along(t, axis):
    x = np.moveaxis(t, axis, -1)                # bring it to the end
    x = x / x.sum(axis=-1, keepdims=True)       # operate on a known axis
    return np.moveaxis(x, -1, axis)             # put it back

f = np.arange(24, dtype=float).reshape(2, 3, 4) + 1
out = normalise_along(f, 1)
out.shape                                       # => (2, 3, 4)
out.sum(axis=1)                                 # => all 1.0
#
# this is how library functions accept an `axis=`
# argument without writing a separate code path per axis.

# ============================================
# Compare

t.transpose(2, 0, 1)        # full control, all axes named
t.swapaxes(0, 2)            # exchange two, rest fixed
np.moveaxis(t, 0, 2)        # relocate one, rest slide
t.T                         # reverse all (rank 3+: rarely what you want)
t.swapaxes(-1, -2)          # batch matrix transpose (rank-agnostic)

# all views, all changing the flat order:
[np.shares_memory(t, x) for x in
 (t.transpose(2,0,1), t.swapaxes(0,2), np.moveaxis(t,0,2))]     # => [True]*3
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|two axes to trade|`t.swapaxes(i, j)`|
|one axis relocated|`np.moveaxis(t, src, dst)`|
|to remember the difference|**swap** = exchange; **move** = pull out and reinsert|
|an axis at the front|`np.moveaxis(t, k, 0)`|
|an axis at the back|`np.moveaxis(t, k, -1)`|
|a batch matrix transpose|`t.swapaxes(-1, -2)` — **not** `.T`|
|to undo a swap|swap again|
|to undo a move|`np.moveaxis(t, dst, src)`|
|an `axis=` parameter in your own function|move to `-1`, work, move back|

---

## Key Insight

**`swapaxes` exchanges; `moveaxis` relocates — and on rank 3+ those are different results.**

```text
(2,3,4)  swapaxes(0,2)  ->  (4,3,2)     the pair trades, axis 1 stays
(2,3,4)  moveaxis(0,2)  ->  (3,4,2)     axis 0 is extracted and appended
```

They coincide at rank 2, which is precisely why the difference catches people out later. Both are views, both change the flat order, and both are just `transpose` with a particular permutation — but naming the intent is worth something. At rank 5, `np.moveaxis(t, 3, 0)` is unambiguous where `t.transpose(3, 0, 1, 2, 4)` is four opportunities to make a typo that does not raise.

Two idioms worth taking away whole:

1. **`t.swapaxes(-1, -2)` is the batch matrix transpose.** Negative axes make it work at any rank, and it is the correct replacement for `.T`, which reverses everything and breaks batched matmul.
    
2. **Move-to-`-1`, operate, move-back** is how you write a function that accepts an `axis=` argument. Bring the axis of interest to a known position, use the ordinary code path, then restore. It costs nothing because both moves are views — and it is how NumPy's own `axis=` parameters are implemented.
    

---

## The Three Reordering Tools

|Tool|Names|Best for|
|---|---|---|
|`transpose(perm)`|**all** axes|a full known layout change|
|`swapaxes(i, j)`|**two** axes|an exchange, batch matrix transpose|
|`moveaxis(src, dst)`|**one** axis|"put this axis there"|

```text
   care about every axis   ──►  transpose
   care about two          ──►  swapaxes
   care about one          ──►  moveaxis
```

> **Mental shift:** part 2 had one rearrangement and one name for it. Part 3 has `n!` of them, so the useful question stops being "which rearrangement?" and becomes "how much of the layout do I actually need to spell out?" These three functions are the same operation at three levels of verbosity. Pick the one that states your intent and the reader — you, in three months — won't have to decode a permutation tuple.
