# 35. Zeros / Ones / Full

## Mental Model

Every lesson so far consumed a tensor. This section **produces** one, out of a description rather than out of data.

The simplest description is a shape and a constant:

```python
np.zeros((2, 3, 4))         # every element 0
np.ones((2, 3, 4))          # every element 1
np.full((2, 3, 4), 7)       # every element 7
```

Three things lift this above trivia.

**The shape is a tuple.** `np.zeros(3)` works because a bare int is accepted at rank 1, but `np.zeros(3, 3)` does *not* mean a 3×3. The second positional argument is `dtype`, so you get a baffling error. Always write the tuple.

**The dtype is a decision.** `np.zeros` defaults to `float64` and `np.full` infers from the fill value. An integer array quietly truncates anything you assign into it, and that dtype costs 8× the memory of a boolean one.

**`np.empty` doesn't initialise.** It hands you whatever bytes happened to be in that memory. It exists for when you're about to overwrite everything anyway, and it's a genuine source of bugs when you aren't.

This is also where part 2's lesson-28 warning finally goes away. There's no `[[0]*n]*n` aliasing trap here, because NumPy allocates a real block of memory instead of repeating a reference.

---

## Relationship to Cognitive Verb

```text
Allocate
   ↓
Zeros / Ones / Full
```

Related verbs:

- Allocate
- Initialise
- Fill
- Reserve
- Create blank

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|All zeros|the default|`np.zeros(shape)`|
|All ones|for products/masks|`np.ones(shape)`|
|Any constant|explicit|`np.full(shape, value)`|
|Uninitialised|fastest, dangerous|`np.empty(shape)`|
|Match another tensor|shape **and** dtype|`np.zeros_like(t)`|
|Choose the type|explicit|`dtype=int`, `dtype=np.float32`|
|Missing-value init|for masks|`np.full(shape, np.nan)`|
|Accumulator init|for min/max|`np.full(shape, np.inf)`|
|Boolean grid|1 byte per cell|`np.zeros(shape, dtype=bool)`|

---

## Common Uses

- Allocating an output buffer before a loop
- Initialising weights, counters or accumulators
- Building masks
- Padding
- Placeholder values before filling from data
- Preallocating so you do not concatenate in a loop (lesson 24)

---

## Hidden Interview Problems

- Create an n-dimensional array of a given constant
- Preallocate a result array
- Explain the difference between `zeros` and `empty`
- Create an array matching another's shape and dtype
- Explain why `np.zeros(3, 3)` fails
- Choose a dtype to halve memory usage

---

## Recognition Clues

If you hear...

- "initialise an array of..."
- "preallocate..."
- "fill with zeros / ones / NaN..."
- "same shape as..."
- "an empty buffer..."

...think **Zeros / Ones / Full**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Shape argument|A **tuple** (an int works only for rank 1)|
|Second positional arg|`dtype` — **not** another dimension|
|`zeros` / `ones` default|`float64`|
|`full` dtype|Inferred from the fill value|
|`empty`|**Uninitialised** — arbitrary contents|
|`*_like`|Copies shape **and** dtype|
|Memory|`prod(shape) × itemsize`|
|Aliasing|None — unlike part 2's `[[0]*n]*n`|
|Common Domains|Everywhere|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember
#
#   a SHAPE TUPLE and a dtype

import numpy as np

np.zeros((2, 3))
# => array([[0., 0., 0.],
#           [0., 0., 0.]])

np.zeros((2, 3, 4)).shape       # => (2, 3, 4)
np.ones((2, 3))
# => array([[1., 1., 1.],
#           [1., 1., 1.]])

np.full((2, 3), 7)
# => array([[7, 7, 7],
#           [7, 7, 7]])

# ============================================
# THE SHAPE IS A TUPLE

np.zeros(3).shape           # => (3,)      an int is fine for rank 1
np.zeros((3,)).shape        # => (3,)      the explicit form

try:
    np.zeros(3, 3)
except TypeError as e:
    print(e)
# Cannot interpret '3' as a data type
#
# the SECOND positional argument is `dtype`, not another
# dimension. `np.zeros(3, 3)` asks for a 1-D array of
# dtype "3". Always parenthesise: np.zeros((3, 3)).

# ============================================
# dtype is a decision, not a detail

np.zeros(3).dtype           # => float64       the default
np.zeros(3, dtype=int)      # => array([0, 0, 0])
np.full((2, 2), 7).dtype    # => int64         inferred from the 7
np.full((2, 2), 7.0).dtype  # => float64       inferred from the 7.0

# an int array truncates on assignment, silently:
z = np.zeros(3, dtype=int)
z[0] = 0.9
z                           # => array([0, 0, 0])
#
# 0.9 became 0. No warning. If a buffer will hold
# fractions, say `dtype=float` when you create it.

# and the memory difference is not marginal:
np.zeros((1000, 1000)).nbytes                   # => 8000000    float64
np.zeros((1000, 1000), dtype=np.float32).nbytes # => 4000000
np.zeros((1000, 1000), dtype=bool).nbytes       # => 1000000    8x smaller
#
# for masks, `dtype=bool` is the right choice and saves
# a factor of eight.

# ============================================
# `full` broadcasts its fill value

np.full((2, 3), [1, 2, 3])
# => array([[1, 2, 3],
#           [1, 2, 3]])
#
# the fill can be any broadcastable array (lesson 17),
# not just a scalar — a compact way to build a repeated
# row without `tile`.

# ============================================
# THE TRAP: np.empty is UNINITIALISED

e = np.empty((2, 3))
e.shape                     # => (2, 3)
e.dtype                     # => float64
#
# the CONTENTS are whatever was in that memory. They may
# look like zeros — that is the dangerous part, because
# it works in testing and fails in production.
#
# use `empty` only when the very next statement fills
# every element:
out = np.empty((2, 3))
out[:] = 5                  # every element written
#
# otherwise use `zeros`. The speed difference is
# irrelevant unless you are allocating in a hot loop.

# ============================================
# The *_like family — shape AND dtype

t = np.arange(24).reshape(2, 3, 4)

np.zeros_like(t).shape      # => (2, 3, 4)
np.zeros_like(t).dtype      # => int64        matches t, not float64!
np.ones_like(t).shape       # => (2, 3, 4)
np.full_like(t, 9)[0, 0]    # => array([9, 9, 9, 9])

np.array_equal(np.zeros(t.shape, dtype=t.dtype), np.zeros_like(t))  # => True
#
# note `zeros_like(t)` is an INT array here, while
# `zeros(t.shape)` would be float. That difference bites
# when you then assign fractions into it.
#
# to keep the shape but change the type:
np.zeros_like(t, dtype=float).dtype             # => float64

# ============================================
# No aliasing trap — unlike part 2

grid = np.zeros((3, 3), dtype=int)
grid[0, 0] = 9
grid
# => array([[9, 0, 0],
#           [0, 0, 0],
#           [0, 0, 0]])
#
# compare part 2's lesson 28:
bad = [[0] * 3] * 3
bad[0][0] = 9
bad                         # => [[9,0,0], [9,0,0], [9,0,0]]
#
# `*` on a list repeats the REFERENCE; np.zeros allocates
# a real block. The trap that lesson existed to warn
# about simply does not arise here.

# ============================================
# Sentinel initialisations

np.full((2, 3), np.nan)
# => array([[nan, nan, nan],
#           [nan, nan, nan]])
#   "not yet computed" for float data — and `np.isnan`
#   finds them (lesson 11).

np.full(3, -np.inf)         # => array([-inf, -inf, -inf])
#   the identity for `max`: anything beats it. This is
#   the fix for lesson 20's "max of an empty array
#   raises" — seed the accumulator instead.

np.full(3, np.inf)          # for a running minimum

# ============================================
# Practical: preallocate instead of concatenating

# BAD — O(n^2), see lesson 24
#   out = np.zeros((0, 3))
#   for i in range(n):
#       out = np.concatenate([out, row])

# GOOD — allocate once, fill in place
n = 4
out = np.zeros((n, 3))
for i in range(n):
    out[i] = i
out
# => array([[0., 0., 0.],
#           [1., 1., 1.],
#           [2., 2., 2.],
#           [3., 3., 3.]])
#
# when you know the final shape, allocate it. When you
# do not, collect into a list and `np.stack` once
# (lesson 25).

# ============================================
# Practical: a mask you fill in

mask = np.zeros((4, 4), dtype=bool)
mask[1:3, 1:3] = True
mask
# => array([[False, False, False, False],
#           [False,  True,  True, False],
#           [False,  True,  True, False],
#           [False, False, False, False]])
int(mask.sum())             # => 4
#
# bool dtype, slice assignment (lesson 8), count with
# `.sum()` (lesson 11).

# ============================================
# Compare

np.zeros((2, 3))            # a constant             this lesson
np.arange(6).reshape(2, 3)  # a sequence             lesson 36
np.indices((2, 3))          # coordinates            lesson 37
np.eye(3)                   # structure              lesson 38

[np.zeros((2,3)).shape, np.arange(6).reshape(2,3).shape,
 np.indices((2,3)).shape, np.eye(3).shape]
# => [(2, 3), (2, 3), (2, 2, 3), (3, 3)]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a constant array|`np.zeros/ones/full(shape, ...)`|
|the shape|a **tuple** — the 2nd positional arg is `dtype`|
|a matching array|`np.zeros_like(t)` — copies the dtype too|
|less memory|`dtype=bool` for masks, `float32` for data|
|a "not computed" marker|`np.full(shape, np.nan)`|
|a max accumulator|`np.full(shape, -np.inf)`|
|**not** `np.empty`|unless the next line fills everything|
|to avoid O(n²)|preallocate, or list + `np.stack`|

---

## Key Insight

**Generation starts with a shape and a value — and both are decisions.**

The shape must be a **tuple**: `np.zeros(3, 3)` is not a 3×3 array, it is a rank-1 array with dtype `3`, and the error message says so obscurely. The dtype defaults to `float64` for `zeros`/`ones` but is *inferred* for `full` and *copied* for `zeros_like` — so `np.zeros(t.shape)` and `np.zeros_like(t)` can differ, and an int array will silently truncate every fraction you assign into it.

Two things worth being deliberate about:

1. **`np.empty` is uninitialised memory.** It often looks like zeros, which is exactly what makes it dangerous — the bug appears when the memory happens to be dirty. Use it only when the next statement writes every element.
    
2. **Preallocate rather than grow.** Lesson 24 showed that concatenating in a loop is O(n²). If you know the final shape, `np.zeros` it and fill by index; if you do not, collect into a Python list and `np.stack` once.
    

And a pleasant absence: part 2's lesson 28 was largely a warning about `[[0]*n]*n` creating `n` references to one row. NumPy allocates a real block, so that trap is simply gone.

---

## The Generation Section

|Lesson|Built from|Example|
|---|---|---|
|**35 Zeros / Ones / Full**|a shape and a **constant**|`np.zeros((2,3))`|
|36 Arange / Linspace|a **range**|`np.arange(6)`|
|37 Meshgrid|**coordinates**|`np.indices((2,3))`|
|38 Identity / Diagonal|**structure**|`np.eye(3)`|

```text
   constant   ──►  35
   sequence   ──►  36
   f(i,j,k)   ──►  37   (coordinates make the function possible)
   structure  ──►  38
```

> **Mental shift:** every other section in part 3 answered "what do I do with this tensor?". Generation answers "where did the tensor come from?", and the answer is almost never a literal. It's a shape plus a rule, which is why the next three lessons are about supplying richer rules.
