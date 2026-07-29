# 36. Arange and Linspace

## Mental Model

Two ways to generate a sequence, and they differ in **what you specify**:

```text
np.arange(start, stop, STEP)     you choose the spacing;  count follows
np.linspace(start, stop, NUM)    you choose the count;    spacing follows
```

```text
np.arange(0, 1, 0.25)      ->  [0.  , 0.25, 0.5 , 0.75      ]   stop EXCLUSIVE
np.linspace(0, 1, 5)       ->  [0.  , 0.25, 0.5 , 0.75, 1.  ]   stop INCLUSIVE
```

Watch the endpoints. `arange` excludes `stop`, like Python's `range`. `linspace` includes it. That difference alone usually decides which one you want.

There's also a real hazard in `arange` that `linspace` doesn't have:

> **`np.arange` with a float step has an unpredictable element count.**

```text
np.arange(1, 1.3, 0.1)   ->  [1. , 1.1, 1.2, 1.3]      FOUR elements
```

`1.3` should have been excluded. The count comes from `ceil((stop-start)/step)` in floating point, and `0.1` isn't exactly representable, so the arithmetic tips just over the boundary. **Use `arange` for integers and `linspace` for floats** and this never bites you.

Paired with `reshape`, `arange` is also the workhorse of this whole course. `np.arange(24).reshape(2, 3, 4)` has built the example tensor in every lesson since lesson 1.

---

## Relationship to Cognitive Verb

```text
Enumerate
    ↓
Arange and Linspace
```

Related verbs:

- Enumerate
- Step through a range
- Sample an interval
- Lay out evenly
- Count

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Integer sequence|the common case|`np.arange(n)`|
|With a step|explicit|`np.arange(start, stop, step)`|
|Backwards|negative step|`np.arange(10, 0, -2)`|
|Fixed count|**for floats**|`np.linspace(a, b, num)`|
|Exclude the end|like arange|`np.linspace(a, b, n, endpoint=False)`|
|Get the spacing too|useful|`np.linspace(..., retstep=True)`|
|Log-spaced|orders of magnitude|`np.logspace(0, 3, 4)`|
|Geometric|by endpoints|`np.geomspace(1, 1000, 4)`|
|Build a test tensor|the workhorse|`np.arange(n).reshape(...)`|
|Several ranges at once|vectorised|`np.linspace([0,10], [1,20], 3)`|

---

## Common Uses

- Building index arrays
- Sampling a function over an interval
- Time or frequency axes
- Learning-rate and hyperparameter sweeps
- Plot axes
- Generating test data with known values
- Positional encodings

---

## Hidden Interview Problems

- Generate n evenly spaced points between a and b
- Create an index array and reshape it
- Explain why `arange` with a float step is unreliable
- Generate a log-spaced sweep
- Produce a descending sequence
- Sample an interval inclusively

---

## Recognition Clues

If you hear...

- "n evenly spaced values..."
- "from a to b in steps of..."
- "an index array..."
- "sample the interval..."
- "log scale sweep..."

...think **Arange and Linspace**.

---

## Pattern Summary

|Property|`np.arange`|`np.linspace`|
|---|---|---|
|You specify|the **step**|the **count**|
|`stop`|**excluded**|**included** (by default)|
|Count|`ceil((stop-start)/step)`|exactly `num`|
|dtype|inferred from the arguments|**always float**|
|Float steps|**unreliable**|exact count guaranteed|
|Backwards|negative step|`a > b` works|
|Best for|integers, indices|floats, sampling|

---

## Python Recipe Book

```python
# ============================================
# arange — you choose the STEP

import numpy as np

np.arange(5)                # => array([0, 1, 2, 3, 4])
np.arange(2, 8)             # => array([2, 3, 4, 5, 6, 7])
np.arange(0, 10, 3)         # => array([0, 3, 6, 9])
np.arange(10, 0, -2)        # => array([10,  8,  6,  4,  2])
np.arange(5, 5)             # => array([], dtype=int64)     empty is fine
#
# `stop` is EXCLUSIVE — exactly like Python's `range`,
# and for the same reason: `arange(n)` gives n elements.

np.arange(5).dtype          # => int64
np.arange(5.0).dtype        # => float64     one float argument is enough

# ============================================
# linspace — you choose the COUNT

np.linspace(0, 1, 5)        # => array([0.  , 0.25, 0.5 , 0.75, 1.  ])
np.linspace(0, 10, 3)       # => array([ 0.,  5., 10.])
#
# `stop` is INCLUDED. That is usually what you want when
# sampling an interval, and it is the opposite of arange.

np.linspace(0, 1, 5, endpoint=False)    # => array([0. , 0.2, 0.4, 0.6, 0.8])
np.allclose(np.linspace(0, 1, 5, endpoint=False), np.arange(0, 1, 0.2))
# => True
#   endpoint=False makes linspace behave like arange —
#   but with a guaranteed count.
#
# note the display is rounded. The VALUES still carry
# ordinary float error:
np.linspace(0, 1, 5, endpoint=False).tolist()
# => [0.0, 0.2, 0.4, 0.6000000000000001, 0.8]
#
# linspace guarantees the COUNT, not exact decimals —
# nothing can guarantee those in binary floating point.
# Compare with np.allclose, never with ==.

np.linspace(0, 1, 5, retstep=True)[1]   # => 0.25      the spacing
np.linspace(0, 1, 1)                    # => array([0.])   num=1 is legal

np.linspace(0, 1, 5).dtype  # => float64    ALWAYS float, even for int inputs

# ============================================
# THE FLOAT TRAP

np.arange(0, 0.3, 0.1)      # => array([0. , 0.1, 0.2])
len(np.arange(0, 0.3, 0.1)) # => 3         as expected

np.arange(1, 1.3, 0.1)      # => array([1. , 1.1, 1.2, 1.3])
len(np.arange(1, 1.3, 0.1)) # => 4         ONE MORE THAN EXPECTED
#
# `1.3` should be excluded. The count is
# ceil((stop - start) / step) computed in floating
# point, and (1.3 - 1) / 0.1 evaluates to slightly
# more than 3 — so it rounds up to 4.
#
# the same call with start=0 gives the right answer.
# It is DATA-DEPENDENT, which is the worst kind of bug.

np.arange(0, 1, 0.1).shape  # => (10,)     this one is fine
#
# you cannot predict which cases break by inspection.

# THE FIX — say how many you want:
np.linspace(1, 1.3, 4)      # => array([1. , 1.1, 1.2, 1.3])
np.linspace(1, 1.3, 3, endpoint=False)      # => array([1. , 1.1, 1.2])
#
# RULE: arange for INTEGERS, linspace for FLOATS.

# ============================================
# Log and geometric spacing

np.logspace(0, 3, 4)        # => array([   1.,   10.,  100., 1000.])
#   evenly spaced in the EXPONENT: 10^0 .. 10^3

np.geomspace(1, 1000, 4)    # => array([   1.,   10.,  100., 1000.])
#   same result, specified by ENDPOINTS rather than
#   exponents — usually the more natural interface.
#
# for a learning-rate sweep you want one of these, not
# linspace: 1e-5 to 1e-1 linearly is nine samples that
# are all effectively 1e-1.

# ============================================
# THE WORKHORSE: arange + reshape

np.arange(24).reshape(2, 3, 4).shape        # => (2, 3, 4)
#
# this single expression has produced the example tensor
# in nearly every lesson of part 3. Sequential values
# make every operation checkable by eye — after a
# transpose or a reduction you can see immediately
# whether the numbers went where you expected.
#
# it is the best habit in this course: debug shape logic
# on `np.arange(n).reshape(...)`, never on random data.

np.arange(6, dtype=np.float32).dtype        # => float32
#   set the dtype at creation rather than casting after.

# ============================================
# Vectorised endpoints

np.linspace([0, 10], [1, 20], 3)
# => array([[ 0. , 10. ],
#           [ 0.5, 15. ],
#           [ 1. , 20. ]])
np.linspace([0, 10], [1, 20], 3).shape      # => (3, 2)
#
# two independent ranges in one call — the sample axis
# comes first. Handy for per-channel scales.

# ============================================
# Practical: a time axis

fs = 100                            # samples per second
dur = 0.05                          # seconds
t = np.arange(0, dur, 1/fs)
t.shape                             # => (5,)
#
# ...but that is a float step. Safer:
n = int(dur * fs)
t = np.arange(n) / fs               # => [0., 0.01, 0.02, 0.03, 0.04]
t.shape                             # => (5,)
#
# generate INTEGER indices, then scale. The count is now
# exact by construction, and this is the standard fix
# whenever a float step is tempting.

# ============================================
# Practical: sampling a function

x = np.linspace(0, 2*np.pi, 5)
np.round(np.sin(x), 3)      # => array([ 0.,  1.,  0., -1., -0.])
#
# linspace includes both endpoints, so 0 and 2*pi are
# both present — usually what you want for a plot, and
# usually NOT what you want for a periodic signal
# (the endpoint duplicates the start). Use
# endpoint=False there.

# ============================================
# Practical: index arrays

n = 5
idx = np.arange(n)
idx[::-1]                   # => array([4, 3, 2, 1, 0])      reversed
idx[idx % 2 == 0]           # => array([0, 2, 4])            filtered
#
# `np.arange(len(x))` is how you get positions to pass to
# fancy indexing (lesson 10) — for shuffling, batching,
# or pairing with argmax results (lesson 23).

# ============================================
# Compare

np.arange(5)                        # step 1, int, stop excluded
np.arange(0, 1, 0.25)               # float step — count NOT guaranteed
np.linspace(0, 1, 5)                # count guaranteed, stop included
np.linspace(0, 1, 5, endpoint=False)    # count guaranteed, stop excluded
np.geomspace(1, 1000, 4)            # multiplicative spacing

[np.arange(0, 1, 0.25).shape, np.linspace(0, 1, 5).shape,
 np.linspace(0, 1, 5, endpoint=False).shape]
# => [(4,), (5,), (5,)]
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|integer indices|`np.arange(n)`|
|n evenly spaced floats|`np.linspace(a, b, n)`|
|the rule|**arange for ints, linspace for floats**|
|`stop` included|linspace (default)|
|`stop` excluded|arange, or `endpoint=False`|
|the spacing back|`retstep=True`|
|a log sweep|`np.geomspace(lo, hi, n)`|
|a safe float step|`np.arange(n) / rate`|
|a test tensor|`np.arange(n).reshape(...)`|

---

## Key Insight

**`arange` fixes the step and derives the count; `linspace` fixes the count and derives the step.** That is the whole distinction, and it decides which one is safe:

```text
np.arange(1, 1.3, 0.1)  ->  4 elements, including 1.3
```

The count comes from `ceil((stop - start) / step)` evaluated in floating point, and `0.1` is not exactly representable — so the boundary case goes the wrong way. Worse, it is **data-dependent**: `np.arange(0, 0.3, 0.1)` gives the expected 3 elements while `np.arange(1, 1.3, 0.1)` gives 4. You cannot tell by looking.

`linspace` cannot have this problem, because you told it the count. So:

> **arange for integers, linspace for floats.**

And when a float step is genuinely what you mean — a time axis at 100 Hz — generate integer indices and scale: `np.arange(n) / fs`. The count is then exact by construction.

Two smaller points: `linspace` **always returns float**, even for integer endpoints; and for anything spanning orders of magnitude (learning rates, frequencies) you want `geomspace`, because linear spacing between `1e-5` and `1e-1` produces samples that are all effectively `1e-1`.

Finally, the idiom this course has leaned on throughout: **`np.arange(n).reshape(...)`**. Sequential values make every shape operation checkable by eye — after a transpose or a reduction you can see whether the numbers landed where you expected. Debug shape logic on `arange`, never on random data.

---

## Arange vs Linspace vs Range

|Tool|Type|`stop`|Count|
|---|---|---|---|
|`range(n)`|Python, lazy|excluded|exact (ints only)|
|`np.arange`|array|excluded|**derived** — unreliable for floats|
|`np.linspace`|array|**included**|**exact**|

```text
   arange:   |----|----|----|         you set the gap
   linspace: |---|---|---|---|        you set the number of points
```

> **Mental shift:** part 1's `range` only ever dealt in integers, so step versus count never came up. The moment you're sampling a continuous interval it becomes the whole question. `linspace` exists because "give me n points" is almost always what you actually mean, while "step by 0.1" is a fragile way of saying it.
