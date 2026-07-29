# 20. Reduce Along an Axis

## Mental Model

A reduction takes many values and gives back one. With a tensor the question is always **along which axis**, and the answer sets the output shape by a single rule:

> **Reducing along axis `k` deletes entry `k` from the shape.**

```text
t.shape = (2, 3, 4)

t.sum(axis=0)  ->  (3, 4)      the 2 collapsed
t.sum(axis=1)  ->  (2, 4)      the 3 collapsed
t.sum(axis=2)  ->  (2, 3)      the 4 collapsed
t.sum()        ->  ()          everything collapsed
```

Lesson 2 stated that rule. This is where it becomes your everyday tool. Part 1 reduced sequences with `sum`, `max` and `Counter`. Part 2 reduced rows and columns. Here it's the same set of operations with one extra argument, and that argument carries the whole design:

```python
t.sum(axis=1)       # per (block, column)
t.mean(axis=0)      # per (row, column), averaged over blocks
t.max(axis=-1)      # per (block, row)
```

Two practical points that only show up at rank 3 and above:

- **`axis=None` is the default and it collapses *everything***. `t.mean()` is one number, not a per-row mean. Don't lean on the default. Write the axis.
    
- **Empty reductions return the operation's identity**, not an error: `sum` of nothing is `0`, `prod` of nothing is `1`, `all` of nothing is `True`. But `max` of nothing *raises*, because there is no identity for maximum.
    

---

## Relationship to Cognitive Verb

```text
Collapse
   ↓
Reduce Along an Axis
```

Related verbs:

- Collapse
- Aggregate
- Summarise
- Fold
- Total

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Sum|the default reduction|`t.sum(axis=k)`|
|Mean / std / var|statistics|`t.mean(axis=k)`, `t.std(axis=k)`|
|Extremes|value, not position|`t.max(axis=k)`, `t.min(axis=k)`|
|Boolean|does any / do all|`mask.any(axis=k)`, `mask.all(axis=k)`|
|Count|how many pass|`mask.sum(axis=k)`|
|Product|multiply through|`t.prod(axis=k)`|
|Range|max − min|`np.ptp(t, axis=k)`|
|Median / quantile|order statistics|`np.median(t, axis=k)`|
|Conditional|reduce a subset|`t.sum(axis=k, where=mask)`|
|Running total|**not** a reduction|`t.cumsum(axis=k)` — shape preserved|

---

## Common Uses

- Per-sample loss from a per-element loss
- Channel statistics of an image batch
- Summing over a time axis
- Counting matches per row
- Global pooling in a CNN
- Aggregating scores across an ensemble
- Any "total / average / best per group" computation

---

## Hidden Interview Problems

- Sum a 3-D array along each axis
- Compute per-row and per-column statistics
- Count how many elements pass a test, per group
- Find the maximum of each slice
- Compute the mean ignoring missing values
- Explain why `t.mean()` is not a per-row mean
- Explain what an empty sum returns

---

## Recognition Clues

If you hear...

- "total per..."
- "average across..."
- "the maximum of each..."
- "collapse the time dimension..."
- "how many per row..."
- "aggregate over..."

...think **Reduce Along an Axis**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Shape rule|Deletes entry `k` from the shape|
|Rank|Drops by 1 (or by `len(axis)` for a tuple)|
|`axis=None`|The **default** — collapses everything to a scalar|
|Negative axes|`axis=-1` is the innermost, at any rank|
|Empty input|Returns the identity: `sum`→0, `prod`→1, `all`→True|
|Empty `max`|**Raises** — no identity exists|
|dtype|Widened for small ints; `mean` always returns float|
|`cumsum`/`cumprod`|**Not** reductions — shape is preserved|
|Time Complexity|O(size)|
|Common Domains|Statistics, ML losses, pooling|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember
#
#   reducing along axis k deletes entry k

import numpy as np

t = np.arange(24).reshape(2, 3, 4)

t.sum(axis=0).shape         # => (3, 4)
t.sum(axis=1).shape         # => (2, 4)
t.sum(axis=2).shape         # => (2, 3)
t.sum().shape               # => ()

t.sum(axis=1)
# => array([[12, 15, 18, 21],
#           [48, 51, 54, 57]])
#
# element [i][k] = t[i][0][k] + t[i][1][k] + t[i][2][k]

np.array_equal(t.sum(axis=-1), t.sum(axis=2))       # => True
#
# use axis=-1 for "the innermost" — it survives someone
# prepending a batch dimension (lesson 2).

# ============================================
# THE DEFAULT IS axis=None — always write the axis

t.mean()                    # => 11.5        ONE number
t.mean(axis=1).shape        # => (2, 4)      what you probably wanted
#
# `t.mean()` looks like "the mean" and is the mean of
# EVERYTHING. On a batch that is almost never the
# statistic you want, and it does not raise.

# ============================================
# The reduction zoo — same axis argument throughout

t.sum()                     # => 276
t.mean()                    # => 11.5
t.max(), t.min()            # => (23, 0)
round(float(t.std()), 4)    # => 6.9222
round(float(t.var()), 4)    # => 47.9167
np.ptp(t)                   # => 23          peak-to-peak: max - min
float(np.median(t))         # => 11.5
np.arange(1, 5).prod()      # => 24

# boolean reductions
bool((t > 20).any())        # => True
bool((t >= 0).all())        # => True
int((t > 20).sum())         # => 3
#
# summing a bool array COUNTS it — the vectorised
# replacement for every `sum(1 for x in ... if ...)`
# loop from parts 1 and 2.

# and they take axes like everything else:
(t > 10).sum(axis=(1, 2))   # => array([ 1, 12])
(t > 10).any(axis=2)
# => array([[False, False,  True],
#           [ True,  True,  True]])

# ============================================
# cumsum is NOT a reduction — the shape survives

t.cumsum(axis=1).shape      # => (2, 3, 4)   unchanged!

t.cumsum(axis=1)[0]
# => array([[ 0,  1,  2,  3],
#           [ 4,  6,  8, 10],
#           [12, 15, 18, 21]])
#
# each row is the running total down axis 1. The LAST
# entry equals the full reduction:
np.array_equal(t.cumsum(axis=1)[:, -1, :], t.sum(axis=1))       # => True
#
# part 1 called this "scan" and part 2 used it for
# prefix sums (lesson 27). A scan keeps every partial
# result; a reduction keeps only the final one.

# ============================================
# EMPTY REDUCTIONS return the identity

np.array([]).sum()                      # => 0.0
np.array([]).prod()                     # => 1.0
bool(np.array([], dtype=bool).all())    # => True     "all of none"
bool(np.array([], dtype=bool).any())    # => False    "any of none"
#
# these are the identity elements: adding 0 changes
# nothing, multiplying by 1 changes nothing. `all([])`
# being True surprises people but is the only consistent
# answer.

try:
    np.array([]).max()
except ValueError as e:
    print(str(e)[:50])
# zero-size array to reduction operation maximum which
#
# max has NO identity — there is no value that loses
# to everything — so it raises. Guard with `.size`
# before reducing something that might be empty.

# a zero-size AXIS is fine, and gives you zeros:
z = np.zeros((2, 0, 4))
z.shape                     # => (2, 0, 4)
z.sum(axis=1).shape         # => (2, 4)
z.sum(axis=1)
# => array([[0., 0., 0., 0.],
#           [0., 0., 0., 0.]])

# ============================================
# dtype: accumulators are widened, mean is always float

str((t > 10).sum().dtype)               # => 'int64'    bool -> int
str(t.mean().dtype)                     # => 'float64'  int -> float

small = np.array([100, 100], dtype=np.int8)
small.sum()                             # => 200
str(small.sum().dtype)                  # => 'int64'
#
# 200 does not fit in an int8 (max 127), but the SUM
# does not overflow — NumPy accumulates in a wider type.
# ELEMENTWISE arithmetic does not get that protection:
small[0] + small[1]                     # => 200, promoted too
#
# but if you force the output dtype you can lose data:
#   small.sum(dtype=np.int8)  -> overflows
# pass dtype= explicitly only when you know it fits.

# ============================================
# Conditional reduction — `where=`

t.sum(axis=2, where=t % 2 == 0)
# => array([[ 2, 10, 18],
#           [26, 34, 42]])
#
# sum only the even elements along the last axis.
# Row 0 of block 0 is [0,1,2,3]; the evens are 0 and 2.

np.mean(t, axis=2, where=t > 10)
# => array([[ nan,  nan, 11. ],
#           [13.5, 17.5, 21.5]])
#
# careful: where nothing passes, `mean` divides by zero
# and returns nan (with a RuntimeWarning). `sum` returns
# 0 there instead, because 0 is its identity.
#
# `where=` avoids building a masked copy — compare with
# t[t % 2 == 0].sum(), which flattens and loses the axes
# entirely (lesson 11).

# ============================================
# What the library is doing — nested lists

nested = t.tolist()

def sum_axis1(n):
    I, J, K = len(n), len(n[0]), len(n[0][0])
    return [[sum(n[i][j][k] for j in range(J))      # j is consumed
             for k in range(K)] for i in range(I)]  # i, k survive

sum_axis1(nested) == t.sum(axis=1).tolist()         # => True
#
# the reduced index moves inside sum(); the surviving
# indices become the loops. Writing this by hand for
# each axis is exactly what `axis=` replaces.

# ============================================
# Functional and method forms are the same

np.array_equal(np.sum(t, axis=1), t.sum(axis=1))    # => True

# but watch the names:
#   np.max      REDUCES one array
#   np.maximum  is ELEMENTWISE between two arrays
np.max(np.array([1, 5, 3]))                         # => 5
np.maximum(np.array([1, 5, 3]), np.array([4, 2, 6]))    # => [4, 5, 6]
#
# same for min/minimum and sum/add. Reaching for
# `np.maximum` when you wanted `np.max` gives a wrong
# shape rather than an error.

# ============================================
# Compare

t.sum(axis=1)                   # rank 3 -> rank 2
t.sum(axis=1, keepdims=True)    # rank 3 -> rank 3    (lesson 21)
t.sum(axis=(1, 2))              # rank 3 -> rank 1    (lesson 22)
t.argmax(axis=1)                # the POSITION         (lesson 23)
t.cumsum(axis=1)                # shape preserved — a scan, not a reduction

[t.sum(axis=1).shape,
 t.sum(axis=1, keepdims=True).shape,
 t.sum(axis=(1, 2)).shape,
 t.cumsum(axis=1).shape]
# => [(2, 4), (2, 1, 4), (2,), (2, 3, 4)]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the shape rule|reducing axis `k` deletes entry `k`|
|the innermost axis|`axis=-1`|
|**not** to be surprised|always write `axis=` — the default is *everything*|
|a count|`mask.sum(axis=k)`|
|a range|`np.ptp(t, axis=k)`|
|a conditional reduction|`where=mask`|
|a running total|`cumsum` — that's a scan, not a reduction|
|to know what empty gives|the identity: 0, 1, True — but `max` raises|
|elementwise, not reducing|`np.maximum`, not `np.max`|

---

## Key Insight

**A reduction deletes one entry from the shape tuple, and `axis=` says which.** Once you can predict the output shape from the input shape and the axis, every reduction in NumPy behaves identically — `sum`, `mean`, `std`, `max`, `any`, `all` and `prod` differ only in the arithmetic, not the shape logic.

The three things that actually cause problems:

1. **The default is `axis=None`.** `t.mean()` collapses *everything* to one number. On a batch that is almost never the statistic you meant, and it produces a valid scalar rather than an error. Write the axis every time.
    
2. **Empty reductions return identities, except `max`.** `sum([])` is `0`, `prod([])` is `1`, `all([])` is `True` — all consistent. But `max([])` raises, because no value loses to everything. Check `.size` before reducing data that might be empty.
    
3. **`cumsum` is not a reduction.** It preserves the shape and keeps every partial result; the reduction is just its last element. That is the scan/reduce distinction from part 1, and it is why prefix sums (part 2, lesson 27) live in a different family.
    

Two smaller gotchas worth carrying: `np.max` reduces while `np.maximum` is elementwise (same for `min`/`minimum`), and `where=` lets you reduce a subset **without** flattening — unlike boolean masking, which discards the axes entirely.

---

## The Reduction Section

|Lesson|Question|
|---|---|
|**20 Reduce Along an Axis**|*Which axis collapses, and to what?*|
|21 Keepdims|*How do I keep the slot so the result broadcasts back?*|
|22 Multi-Axis Reduction|*How do I collapse several at once?*|
|23 Argmin / Argmax|*Where was it, rather than what was it?*|

```text
   (2, 3, 4)  --sum(axis=1)-->  (2, 4)          20
              --keepdims---->   (2, 1, 4)       21
              --axis=(1,2)-->   (2,)            22
              --argmax------>   indices         23
```

> **Mental shift:** part 1 reduced a sequence to a number and that was the end of the story. In part 3 a reduction is rarely the end. The result is usually about to meet the original tensor again in a subtraction or a division. That's why the next lesson is about *not* losing the axis you just collapsed.
