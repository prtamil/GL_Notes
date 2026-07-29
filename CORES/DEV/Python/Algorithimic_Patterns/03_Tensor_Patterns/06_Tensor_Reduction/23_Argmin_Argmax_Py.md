# 23. Argmin / Argmax

## Mental Model

Every reduction so far answered **what**. This family answers **where**.

```text
m.max(axis=1)       ->  the largest VALUE in each row
m.argmax(axis=1)    ->  its POSITION in each row
```

The shape rule is identical: `argmax(axis=k)` deletes entry `k`, exactly like `max(axis=k)`. What changes is what the numbers *mean*. They're indices **into the reduced axis**, not values.

That distinction causes the one bug this lesson exists to head off:

```text
idx = m.argmax(axis=1)          # indices into the COLUMNS
m[idx]                          # ...but this indexes the ROWS
```

`m[idx]` is fancy indexing on axis 0 (lesson 10). Either it raises, when an index runs past the row count, or — worse — it quietly hands back a rearranged set of rows. To turn positions back into values, pair each index with its row:

```python
m[np.arange(len(m)), idx]                       # explicit pairing
np.take_along_axis(m, idx[:, None], axis=1)     # the general form
```

Two more facts worth knowing before you trust the result: **ties go to the first occurrence**, and `axis=None` (the default) gives you a **flat** index that needs `np.unravel_index` before it means coordinates.

---

## Relationship to Cognitive Verb

```text
Locate the Best
      ↓
Argmin / Argmax
```

Related verbs:

- Where is the maximum
- Which one won
- Find the position
- Rank
- Select the best index

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Position of the max|per axis|`t.argmax(axis=k)`|
|Position of the min|per axis|`t.argmin(axis=k)`|
|Flat position|whole tensor|`t.argmax()` — the **default**|
|Flat → coordinates|convert|`np.unravel_index(t.argmax(), t.shape)`|
|Index → value|pair with the other axes|`np.take_along_axis(t, idx, axis=k)`|
|Keep the slot|for take_along_axis|`argmax(axis=k, keepdims=True)`|
|Full ranking|every position|`t.argsort(axis=k)`|
|Top-k, unordered|cheaper|`t.argpartition(-k, axis=...)`|
|Ignoring NaN|the safe version|`np.nanargmax`|
|All matching positions|not the same thing|`np.argwhere(cond)`|

---

## Common Uses

- Predicted class from a probability vector
- Nearest neighbour from a distance matrix
- Best hyperparameter from a score grid
- Peak detection in a signal
- Locating the brightest pixel
- Top-k retrieval
- Selecting the best model per fold

---

## Hidden Interview Problems

- Find the index of the maximum in each row
- Find the coordinates of the maximum in a 2-D array
- Get the top-k elements and their positions
- Find the nearest point from a distance matrix
- Convert model logits to predicted labels
- Explain why `a[a.argmax(axis=1)]` is wrong
- Handle NaNs when finding a maximum

---

## Recognition Clues

If you hear...

- "which index / which position..."
- "the predicted class..."
- "the nearest one..."
- "where is the peak..."
- "top-k..."
- "argmax..."

...think **Argmin / Argmax**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Returns|**Indices**, not values|
|Index space|Positions along the reduced axis|
|Shape rule|Same as any reduction — deletes entry `k`|
|Default `axis`|`None` → a **flat** index|
|Ties|The **first** occurrence wins|
|Multi-axis|**Not supported** — reshape first|
|NaN|Propagates: `argmax` returns the NaN's index|
|Empty|**Raises**|
|Recover values|`np.take_along_axis`|
|Common Domains|Classification, search, optimisation|

---

## Python Recipe Book

```python
# ============================================
# The running example

import numpy as np

m = np.array([[3, 7, 1, 9],
              [8, 2, 6, 4],
              [5, 5, 5, 5]])

t = np.arange(24).reshape(2, 3, 4)

# ============================================
# The one idiom to remember
#
#   argmax gives POSITIONS, max gives VALUES

m.max(axis=1)               # => array([9, 8, 5])       values
m.argmax(axis=1)            # => array([3, 0, 0])       positions

m.argmax(axis=0)            # => array([1, 0, 1, 0])    per column
m.argmin(axis=1)            # => array([2, 1, 0])

m.argmax(axis=1).shape      # => (3,)
#
# same shape rule as every reduction: axis 1 deleted.
# The values are indices INTO axis 1, so they range
# 0..3 regardless of what the numbers in m are.

# ============================================
# Ties go to the FIRST occurrence

m[2]                        # => array([5, 5, 5, 5])
m.argmax(axis=1)[2]         # => 0
#
# every element ties; index 0 wins. Deterministic, but
# it means "the argmax" is not well-defined on tied data
# — if that matters, break ties yourself.

# ============================================
# THE BUG: indices are not values

idx = m.argmax(axis=1)
idx                         # => array([3, 0, 0])

try:
    m[idx]
except IndexError as e:
    print(str(e)[:50])
# index 3 is out of bounds for axis 0 with size 3
#
# `m[idx]` is fancy indexing on axis 0 — it asked for
# rows 3, 0 and 0. Here it raises because there are only
# 3 rows. On a taller matrix it would NOT raise:

wide = np.array([[3, 7, 1, 9],
                 [8, 2, 6, 4],
                 [5, 1, 9, 0],
                 [0, 0, 0, 1]])
wi = wide.argmax(axis=1)
wi                          # => array([3, 0, 2, 3])

wide[wi]                    # SILENTLY WRONG
# => array([[0, 0, 0, 1],
#           [3, 7, 1, 9],
#           [5, 1, 9, 0],
#           [0, 0, 0, 1]])
#
# a (4,4) array of rearranged ROWS, when you wanted the
# four maximum values. No error.

wide[np.arange(len(wide)), wi]      # => array([9, 8, 9, 1])   correct

# ============================================
# Recovering the values — two correct spellings

# 1. explicit pairing (rank 2 only)
m[np.arange(len(m)), idx]                       # => array([9, 8, 5])

# 2. take_along_axis — the general form
np.take_along_axis(m, idx[:, None], axis=1)
# => array([[9],
#           [8],
#           [5]])
np.take_along_axis(m, idx[:, None], axis=1).squeeze(axis=1)
# => array([9, 8, 5])

np.array_equal(np.take_along_axis(m, idx[:, None], axis=1).squeeze(1),
               m.max(axis=1))                   # => True
#
# the [:, None] restores the axis argmax removed, so the
# index array has the same rank as m. `keepdims` does it
# for you:

m.argmax(axis=1, keepdims=True).shape           # => (3, 1)
np.take_along_axis(m, m.argmax(axis=1, keepdims=True), axis=1)
# => array([[9],
#           [8],
#           [5]])
#
# THAT is the idiomatic pair: argmax with keepdims,
# straight into take_along_axis. It works at any rank
# and for any axis.

# ============================================
# When you want the value, just use max()
#
# argmax -> take_along_axis is for when you need to look
# up a DIFFERENT array at the winning positions.

scores = np.array([[0.1, 0.7, 0.2],
                   [0.8, 0.1, 0.1]])
names = np.array([['cat', 'dog', 'fox'],
                  ['cat', 'dog', 'fox']])

best = scores.argmax(axis=1, keepdims=True)
np.take_along_axis(names, best, axis=1).squeeze(axis=1)
# => array(['dog', 'cat'], dtype='<U3')
#
# the position came from `scores`, the value from
# `names`. This is the case max() cannot cover.

# ============================================
# The DEFAULT is a FLAT index

int(m.argmax())             # => 3
int(m.ravel()[m.argmax()])  # => 9
np.unravel_index(m.argmax(), m.shape)           # => (0, 3)
#
# with no axis you get one number: the position in
# row-major order (lesson 4). `unravel_index` turns it
# into coordinates.

int(t.argmax())                                 # => 23
np.unravel_index(t.argmax(), t.shape)           # => (1, 2, 3)
#
# this is the standard "where is the global maximum"
# recipe, at any rank.

# ============================================
# There is no multi-axis argmax

try:
    t.argmax(axis=(1, 2))
except TypeError as e:
    print(str(e)[:50])
# 'tuple' object cannot be interpreted as an integer
#
# unlike sum/mean/max, argmax takes ONE axis. The reason
# is that a position along several axes is not a single
# number — you would need a tuple per element.
#
# the workaround: merge the axes, then unravel.
flat = t.reshape(2, -1).argmax(axis=1)          # per-sample flat index
np.unravel_index(flat[0], (3, 4))               # => (2, 3)
#
# merge (lesson 13), argmax, unravel (lesson 4).

# on a rank-3 tensor with an axis, the result keeps the
# other axes as usual:
t.argmax(axis=1).shape                          # => (2, 4)
t.argmax(axis=1)
# => array([[2, 2, 2, 2],
#           [2, 2, 2, 2]])
#   the last row of each block always wins, since t
#   increases along axis 1.

# ============================================
# Full and partial ranking

v = np.array([30, 10, 20, 50, 40])

v.argsort()                 # => array([1, 2, 0, 4, 3])
v[v.argsort()]              # => array([10, 20, 30, 40, 50])
#
# argsort returns the indices that WOULD sort the array —
# "where does each rank come from". Part 2's lesson 19
# used argsort to invert a permutation; same function.

# top 3, descending:
top3 = v.argsort()[-3:][::-1]
top3                        # => array([3, 4, 0])
v[top3]                     # => array([50, 40, 30])

# top 2 when the ORDER does not matter — argpartition is
# O(n) instead of O(n log n):
part = v.argpartition(-2)[-2:]
part                        # => array([4, 3])
np.sort(v[part])            # => array([40, 50])
#
# argpartition guarantees the last 2 positions hold the
# 2 largest values — in no particular order.

# ============================================
# NaN propagates — use the nan* variants

nv = np.array([1., np.nan, 3.])

int(nv.argmax())            # => 1        the NaN's index!
float(nv.max())             # => nan

int(np.nanargmax(nv))       # => 2        correct
float(np.nanmax(nv))        # => 3.0
#
# NaN compares False with everything, so the ordinary
# argmax reports it as the winner. On real data with
# missing values this silently corrupts every downstream
# lookup. Reach for nanargmax / nanargmin whenever NaN
# is possible.

# ============================================
# Empty raises

try:
    np.array([]).argmax()
except ValueError as e:
    print(str(e)[:45])
# attempt to get argmax of an empty sequence
#
# same reason `max` raises on empty input (lesson 20) —
# there is no identity. Check `.size` first.

# ============================================
# argmax vs argwhere — different questions

m.argmax(axis=1)            # => array([3, 0, 0])       ONE per row
np.argwhere(m > 7).tolist() # => [[0, 3], [1, 0]]       ALL matches
#
#   argmax    the best, one per group
#   argwhere  every position satisfying a condition (lesson 11)
#
# they are not variants of each other.

# ============================================
# Practical: predicted class, and nearest neighbour

logits = np.array([[2.0, 1.0, 0.1],
                   [0.5, 3.0, 0.2]])
logits.argmax(axis=1)                           # => array([0, 1])
#
# the predicted label per sample. No softmax needed —
# argmax is invariant under monotonic transforms.

pts = np.array([[0., 0.], [3., 4.], [6., 8.], [0., 1.]])
d = np.sqrt(((pts[:, None, :] - pts[None, :, :]) ** 2).sum(-1))
np.fill_diagonal(d, np.inf)                     # exclude self
d.argmin(axis=1)                                # => array([3, 3, 1, 0])
#
# each point's nearest neighbour. The `fill_diagonal` is
# essential — otherwise every point is its own nearest,
# at distance 0.
#
# note point 1 is equidistant from points 0 and 2 (both
# 5.0) but closest to point 3 (4.243) — worth checking
# the numbers rather than trusting the picture:
np.round(d[1], 3)                   # => array([5., inf, 5., 4.243])

# ============================================
# Compare

m.max(axis=1)                       # the VALUE
m.argmax(axis=1)                    # the POSITION
m.argmax()                          # a FLAT position
np.unravel_index(m.argmax(), m.shape)           # coordinates
np.take_along_axis(m, m.argmax(axis=1, keepdims=True), axis=1)   # value again
m.argsort(axis=1)                   # every position, ranked
np.argwhere(m > 7)                  # all positions matching a test
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the winning value|`t.max(axis=k)`|
|the winning position|`t.argmax(axis=k)`|
|the global position|`np.unravel_index(t.argmax(), t.shape)`|
|the value back|`take_along_axis(t, argmax(axis=k, keepdims=True), axis=k)`|
|**not** this|`t[t.argmax(axis=1)]` — that indexes axis 0|
|several axes|merge them first, then `unravel_index`|
|a ranking|`argsort`|
|top-k, order irrelevant|`argpartition` — O(n)|
|NaN safety|`np.nanargmax`|
|all matches, not the best|`np.argwhere`|

---

## Key Insight

**`argmax` obeys the same shape rule as `max` but returns indices into the reduced axis** — and mixing up the two index spaces is the bug this lesson exists to prevent.

```python
idx = m.argmax(axis=1)      # positions along axis 1
m[idx]                      # ...indexes axis 0
```

That expression raises when an index happens to exceed the length of axis 0, and **silently returns rearranged rows** when it does not. The correct recovery is to pair each index with the axes `argmax` did not reduce:

```python
np.take_along_axis(m, m.argmax(axis=1, keepdims=True), axis=1)
```

`keepdims=True` here is not decoration — `take_along_axis` requires the index array to have the same rank as the source, and `keepdims` supplies exactly that. It is lesson 21's flag doing a second job.

Three more things to hold on to:

1. **The default `axis=None` gives a flat index.** `np.unravel_index(t.argmax(), t.shape)` is the standard "where is the global maximum" recipe, and it is lesson 4's flat-index arithmetic reappearing.
    
2. **There is no multi-axis argmax**, because a position along several axes is not one number. Merge the axes (lesson 13), take the argmax, then `unravel_index` back.
    
3. **NaN wins.** `np.array([1., np.nan, 3.]).argmax()` returns `1` — the NaN's index — because NaN compares `False` with everything. On data that can contain missing values, use `nanargmax`, or you will look up the wrong element with no warning.
    

And ties always go to the **first** occurrence, which makes the result deterministic but means "the argmax" is not well-defined on tied data.

---

## The Reduction Section, Complete

|Lesson|Returns|Shape effect|
|---|---|---|
|20 Reduce Along an Axis|the **value**|deletes entry `k`|
|21 Keepdims|the value, aligned|entry `k` becomes **1**|
|22 Multi-Axis Reduction|the value|deletes **every** listed entry|
|**23 Argmin / Argmax**|the **position**|deletes entry `k`|

```text
   (2, 3, 4)  --max(axis=1)-------->  (2, 4)      what
              --max(axis=1,keep)--->  (2, 1, 4)   what, ready to broadcast
              --max(axis=(1,2))--->   (2,)        what, over two axes
              --argmax(axis=1)---->   (2, 4)      WHERE
```

All four share the same shape rule. They differ in whether you get the value or the index, whether the slot survives, and how many axes go at once.

> **Mental shift:** parts 1 and 2 gave you `max(xs)` and `max(m, key=sum)`, and when you wanted the position you wrote `xs.index(max(xs))` — a second pass. In part 3 the position is a first-class reduction with the same axis semantics as the value, so you can ask "which one won, per sample" as easily as "what was the best score". The only new skill is remembering that the answer lives in a different index space.
