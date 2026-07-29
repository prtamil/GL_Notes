# 6. Nested Traversal

## Mental Model

Lesson 5 peeled one axis. Nested traversal peels **all of them** — you reach individual cells, and you know **where each one is**.

```text
for i in range(2):
    for j in range(3):
        for k in range(4):
            t[i, j, k]          24 cells, with coordinates
```

Part 2 wrote this as two nested loops and that was fine, because the rank was known. At rank `n` the same code is impossible to write by hand — you cannot type a loop nest whose depth is a variable.

So the pattern changes shape. Instead of nesting loops, you **generate the index tuples**:

```python
for idx in np.ndindex(*t.shape):        # (0,0,0), (0,0,1), ...
    t[idx]

for idx, v in np.ndenumerate(t):        # index AND value
    ...
```

`np.ndindex` is the rank-agnostic replacement for a loop nest, and `np.ndenumerate` is its `enumerate`. Both walk in **row-major order** — last index fastest — which is the same order as `t.ravel()` and part 2's flatten.

The pure-Python counterpart is **recursion**: descend the nesting, accumulating a prefix of indices. That version is worth writing once, because it is what makes the rank-independence concrete — the same eight lines handle rank 3 and rank 4 without modification.

And the same caveat as lesson 5 applies, harder: a Python loop over every cell of a real tensor is the slowest thing in this course. Use this pattern when you need **coordinates**, not when you need arithmetic.

---

## Relationship to Cognitive Verb

```text
Enumerate
    ↓
Nested Traversal
```

Related verbs:

- Enumerate
- Visit every cell
- Walk all positions
- Descend
- Address every element

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|All index tuples|rank-agnostic|`np.ndindex(*t.shape)`|
|Index and value|the `enumerate` form|`np.ndenumerate(t)`|
|Pure Python|no NumPy|`itertools.product(*map(range, shape))`|
|Fixed rank|when you know it|explicit nested `for`|
|Any rank, lists|recursion|`yield from` with an index prefix|
|Structure-preserving map|rebuild as you go|recursive `[f(e) for e in x]`|
|Find with position|first match|`next((i for i, v in ndenumerate(t) if p(v)), None)`|
|Best cell|argmax with coords|`np.unravel_index(t.argmax(), t.shape)`|
|Count matches|no positions needed|`int((t > 5).sum())` — vectorised|

---

## Common Uses

- Building an index → value mapping
- Sparse extraction: keeping only non-zero positions with their coordinates
- Writing a generic n-dimensional utility
- Debugging: printing every cell with its address
- Coordinate-dependent generation (part 2's lesson 29, at rank n)
- Neighbour lookups in an n-dimensional grid
- Serialising a tensor with explicit positions

---

## Hidden Interview Problems

- Iterate all elements of an arbitrarily nested list
- Find the coordinates of a value in an n-D array
- Flatten a nested list of unknown depth (part 2, lesson 23)
- Apply a function to every element, preserving structure
- Locate the maximum and return its multi-index
- Convert a dense tensor to a sparse coordinate list
- Count elements matching a predicate

---

## Recognition Clues

If you hear...

- "for every element..."
- "with its index / position / coordinates..."
- "arbitrary number of dimensions..."
- "n-dimensional, not just 2D..."
- "return the position of..."

...think **Nested Traversal**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Each step yields|One cell, plus its index tuple|
|Step count|`t.size`|
|Order|Row-major — **last index varies fastest**|
|Rank-agnostic tool|`np.ndindex` / `np.ndenumerate`|
|Pure-Python tool|`itertools.product`, or recursion|
|Matches|`t.ravel()` order exactly|
|Time Complexity|O(size), with per-element Python overhead|
|Prefer instead|Boolean masks and reductions, when you don't need coordinates|
|Common Domains|Generic utilities, sparse data, debugging|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np
from itertools import product

t = np.arange(24).reshape(2, 3, 4)
nested = t.tolist()

# ============================================
# The problem with explicit nesting
#
# This is correct, and it only works for rank 3.

vals = []
for i in range(2):
    for j in range(3):
        for k in range(4):
            vals.append(t[i, j, k])

vals == t.ravel().tolist()          # => True
#
# now write the same thing for rank n. You cannot —
# the loop depth is a variable. That is the whole
# reason this lesson exists.

# ============================================
# The one idiom to remember
#
#   np.ndindex(*shape)   generates the index tuples
#
# One loop, any rank.

list(np.ndindex(*t.shape))[:6]
# => [(0,0,0), (0,0,1), (0,0,2), (0,0,3), (0,1,0), (0,1,1)]

len(list(np.ndindex(*t.shape)))     # => 24     == t.size

for idx in np.ndindex(*t.shape):
    t[idx]                          # idx is a tuple — t[(0,0,1)] works
#
# note the ORDER: the last index moves fastest. Same as
# row-major flatten (lesson 7), same as part 2's
# `for r: for c:`.

# ============================================
# With the value too — ndenumerate

list(np.ndenumerate(t))[:4]
# => [((0,0,0), 0), ((0,0,1), 1), ((0,0,2), 2), ((0,0,3), 3)]

list(np.ndenumerate(t))[-1]
# => ((1, 2, 3), 23)
#
# ndenumerate : ndindex  ::  enumerate : range
# Use it whenever you would otherwise write t[idx].

# ============================================
# Pure Python — itertools.product
#
# Exactly the same sequence, no NumPy required.

list(product(*map(range, t.shape))) == list(np.ndindex(*t.shape))   # => True

list(product(range(2), range(3), range(4)))[:4]
# => [(0,0,0), (0,0,1), (0,0,2), (0,0,3)]
#
# product's rightmost argument varies fastest, which is
# why it matches. `*map(range, shape)` is what makes it
# rank-agnostic.

# ============================================
# The recursive version — for nested lists
#
# Descend the structure, carrying the index prefix.
# Eight lines, any rank, no library.

def walk(x, prefix=()):
    if not isinstance(x, list):
        yield prefix, x
    else:
        for i, e in enumerate(x):
            yield from walk(e, prefix + (i,))

list(walk(nested))[:4]
# => [((0,0,0), 0), ((0,0,1), 1), ((0,0,2), 2), ((0,0,3), 3)]

len(list(walk(nested)))             # => 24

[(i, v) for i, v in walk(nested)] == [(i, int(v)) for i, v in np.ndenumerate(t)]
# => True    identical to ndenumerate

# and it genuinely does not care about the rank:
q = np.arange(16).reshape(2, 2, 2, 2).tolist()      # rank 4
len(list(walk(q)))                  # => 16
list(walk(q))[:3]
# => [((0,0,0,0), 0), ((0,0,0,1), 1), ((0,0,1,0), 2)]
#
# `yield from` is what keeps this readable — it is the
# same shape as part 2's deep_flatten (lesson 23), with
# the index prefix added.

# ============================================
# Structure-preserving map
#
# Same recursion, but rebuild instead of yielding.

def map_nested(x, f):
    if not isinstance(x, list):
        return f(x)
    return [map_nested(e, f) for e in x]

np.array(map_nested(nested, lambda v: v * 2)).shape     # => (2, 3, 4)
map_nested(nested, lambda v: v * 2) == (t * 2).tolist() # => True
#
# ...and `t * 2` is the version to write. This is here to
# show what the elementwise operator is doing, not as a
# recommendation.

# ============================================
# WHERE THIS PATTERN EARNS ITS KEEP: coordinates

# find the position of a value
next((idx for idx, v in np.ndenumerate(t) if v == 17), None)     # => (1, 1, 1)

# every position matching a predicate
[idx for idx, v in np.ndenumerate(t) if v % 7 == 0]
# => [(0, 0, 0), (0, 1, 3), (1, 0, 2), (1, 2, 1)]

# sparse form: keep only the interesting cells
sparse = [(idx, int(v)) for idx, v in np.ndenumerate(t) if v > 20]
sparse
# => [((1, 2, 1), 21), ((1, 2, 2), 22), ((1, 2, 3), 23)]

# ============================================
# ...but check for a vectorised version first

# counting does NOT need coordinates:
sum(1 for idx, v in np.ndenumerate(t) if v % 2 == 0)        # => 12   slow
int((t % 2 == 0).sum())                                     # => 12   fast

# and neither does finding the maximum:
max(np.ndenumerate(t), key=lambda p: p[1])                  # => ((1,2,3), 23)

int(t.argmax())                                             # => 23   flat index
np.unravel_index(t.argmax(), t.shape)                       # => (1, 2, 3)
#
# argmax gives a FLAT index; unravel_index turns it into
# coordinates (lesson 4). Two vectorised calls beat a
# full Python traversal every time.

# even "all positions matching" has a vectorised form:
np.argwhere(t % 7 == 0).tolist()
# => [[0, 0, 0], [0, 1, 3], [1, 0, 2], [1, 2, 1]]
#
# same answer as the comprehension above, as an array.

# ============================================
# When you DO want the loop
#
# Coordinate-dependent generation at arbitrary rank —
# part 2's lesson 29, one rank up.

shape = (2, 3, 4)
out = np.empty(shape, dtype=int)
for idx in np.ndindex(*shape):
    out[idx] = sum(idx)             # f(i, j, k) = i + j + k

out[0]
# => array([[0, 1, 2, 3],
#           [1, 2, 3, 4],
#           [2, 3, 4, 5]])

# the vectorised equivalent, for reference (lesson 37):
np.add.reduce(np.indices(shape))[0]
# => same array

# ============================================
# Compare

for sub in t: pass                          # lesson 5 — sub-tensors
for idx in np.ndindex(*t.shape): pass       # this lesson — coordinates
for idx, v in np.ndenumerate(t): pass       # this lesson — coords + values
for v in t.flat: pass                       # lesson 7 — values only
t.sum(axis=0)                               # lesson 20 — no loop at all

# they all visit 24 cells in the same order:
[t[idx] for idx in np.ndindex(*t.shape)] == t.ravel().tolist()      # => True
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|all index tuples|`np.ndindex(*t.shape)`|
|indices **and** values|`np.ndenumerate(t)`|
|no NumPy|`product(*map(range, shape))`|
|nested lists, any depth|recursion with an index prefix + `yield from`|
|to keep the structure|recursive rebuild, not a generator|
|the position of the max|`np.unravel_index(t.argmax(), t.shape)`|
|all matching positions|`np.argwhere(cond)`|
|just a **count**|`int(cond.sum())` — no traversal|
|the visit order|row-major: last index fastest|

---

## Key Insight

**You cannot write a loop nest whose depth is a variable — so generate the index tuples instead.**

```python
for idx in np.ndindex(*t.shape):    # replaces `for i: for j: for k:`
```

That substitution is what makes code rank-agnostic, and it is the single structural difference between part 2's traversal lessons and this one. `np.ndenumerate` adds the value; `itertools.product(*map(range, shape))` is the dependency-free equivalent; recursion with a `yield from` and an index prefix is the version for nested lists, and the same eight lines handle rank 3 and rank 4 unchanged.

All three walk in **row-major order**, matching `t.ravel()` — verified, and worth relying on when you convert between flat and multi-dimensional indexing.

The discipline that matters more than the syntax: **only reach for this when you need coordinates.**

|Question|Traversal|Vectorised|
|---|---|---|
|"how many are even?"|loop + count|`int((t % 2 == 0).sum())`|
|"where is the max?"|loop + `max`|`np.unravel_index(t.argmax(), t.shape)`|
|"which positions match?"|comprehension|`np.argwhere(cond)`|
|"double everything"|recursive map|`t * 2`|

Each right-hand column is shorter and roughly two orders of magnitude faster (lesson 5 measured ~280×). Nested traversal is for generic utilities, sparse extraction, coordinate-dependent generation, and debugging — not for arithmetic.

---

## Nested vs Axis Traversal

|Pattern|Peels|Yields|Rank-agnostic?|
|---|---|---|---|
|**Axis Iteration** (5)|one axis|sub-tensors|yes, via `moveaxis`|
|**Nested Traversal** (6)|**all** axes|cells + coordinates|yes, via `ndindex`|

```text
   05:  t  ──►  ▢ ▢          two (3,4) slices
   06:  t  ──►  (0,0,0)→0  (0,0,1)→1  ...  24 cells
```

> **Mental shift:** part 2 could hard-code `for r: for c:` because the rank was fixed at 2. The moment rank is a parameter, the loop nest has to become data — a stream of index tuples. Once you make that move, the same function works at every rank, which is the whole promise of "tensor" over "matrix".
