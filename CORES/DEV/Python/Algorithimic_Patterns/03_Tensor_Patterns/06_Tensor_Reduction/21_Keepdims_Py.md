# 21. Keepdims

## Mental Model

A reduction deletes an axis. `keepdims=True` leaves a **size-1 axis** in its place.

```text
t.sum(axis=1)                   (2, 3, 4) -> (2, 4)
t.sum(axis=1, keepdims=True)    (2, 3, 4) -> (2, 1, 4)
```

Same numbers, same element count. The only difference is a `1` where the `3` used to be.

That `1` exists for exactly one reason:

> **So the result broadcasts back against the tensor it came from.**

Because almost every reduction in real code is the first half of a two-step pattern:

```text
reduce  ──►  broadcast back
```

Centre the data: subtract the mean. Normalise: divide by the sum. Softmax: subtract the max, then divide by the sum. In each case the reduced statistic must line up with the *original* axes — and lesson 18 showed that only the last axis aligns for free. `keepdims=True` guarantees the alignment for every other axis, without you having to count `None`s.

It is not a formatting preference. Without it, the reduction either raises or — when the sizes happen to coincide — silently aligns against the wrong axis.

---

## Relationship to Cognitive Verb

```text
Preserve
   ↓
Keepdims
```

Related verbs:

- Keep the slot
- Preserve the rank
- Hold the place
- Stay aligned
- Reduce without collapsing

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Any reduction|the flag|`t.sum(axis=k, keepdims=True)`|
|Manual equivalent|explicit|`t.sum(axis=k)[:, None, :]`|
|Function form|same|`np.expand_dims(t.sum(axis=k), k)`|
|Multi-axis|several 1s|`t.sum(axis=(1,2), keepdims=True)`|
|Everything|all-ones shape|`t.sum(keepdims=True)`|
|Centre|subtract the mean|`t - t.mean(axis=k, keepdims=True)`|
|Normalise|divide by the sum|`t / t.sum(axis=k, keepdims=True)`|
|Standardise|z-score|`(t - mu) / sd`, both with keepdims|
|Stable softmax|subtract the max first|`max` and `sum`, both with keepdims|
|Drop it later|if you need the rank back|`.squeeze(axis=k)`|

---

## Common Uses

- Centring and standardising data
- Softmax and log-softmax
- Layer normalisation and batch normalisation
- Dividing by a row or column total
- Per-sample scaling
- Attention weight normalisation
- Any "subtract / divide by the statistic of this axis"

---

## Hidden Interview Problems

- Normalise each row of a matrix to sum to 1
- Implement a numerically stable softmax
- Standardise features to zero mean and unit variance
- Subtract the per-channel mean from an image batch
- Explain why `x / x.sum(axis=1)` fails
- Explain when it silently succeeds and is wrong

---

## Recognition Clues

If you hear...

- "normalise along..."
- "subtract the mean of each..."
- "softmax..."
- "layer norm / batch norm..."
- "operands could not be broadcast together..."
- "divide by the row total..."

...think **Keepdims**.

---

## Pattern Summary

|Property|Value|
|---|---|
|Effect|Reduced axis becomes size 1 instead of disappearing|
|Rank|**Preserved**|
|Element count|Same as without it|
|Equivalent to|`np.expand_dims(reduced, axis)`|
|Purpose|Broadcast the result back against the input|
|Multi-axis|Every reduced axis becomes a 1|
|Cost|Free — it is a shape, not data|
|Without it|Raises, **or** silently misaligns|
|Undo|`.squeeze(axis=k)`|

---

## Python Recipe Book

```python
# ============================================
# The one idiom to remember

import numpy as np

t = np.arange(24).reshape(2, 3, 4)

t.sum(axis=1).shape                     # => (2, 4)      axis gone
t.sum(axis=1, keepdims=True).shape      # => (2, 1, 4)   axis kept as 1

# same data, same count:
t.sum(axis=1).size, t.sum(axis=1, keepdims=True).size    # => (8, 8)

# and it is exactly expand_dims:
np.array_equal(t.sum(axis=1, keepdims=True),
               np.expand_dims(t.sum(axis=1), 1))         # => True

# every axis behaves the same way:
t.sum(axis=0, keepdims=True).shape      # => (1, 3, 4)
t.sum(axis=2, keepdims=True).shape      # => (2, 3, 1)
t.sum(axis=(1, 2), keepdims=True).shape # => (2, 1, 1)
t.sum(keepdims=True).shape              # => (1, 1, 1)
#
# every reduced axis becomes a 1. The rank never changes.

# ============================================
# WHY: reduce, then broadcast back

centred = t - t.mean(axis=1, keepdims=True)
centred.shape                           # => (2, 3, 4)
np.round(centred.mean(axis=1), 10)
# => array([[0., 0., 0., 0.],
#           [0., 0., 0., 0.]])          every column now zero-mean
#
#   t                       (2, 3, 4)
#   mean(axis=1, keepdims)  (2, 1, 4)   -> stretches over axis 1
#   ----------------------------------
#                           (2, 3, 4)

try:
    t - t.mean(axis=1)
except ValueError as e:
    print(str(e)[:60])
# operands could not be broadcast together with shapes (2,3,4) (2,4)
#
# without keepdims the statistic is (2,4), which
# right-aligns 4 against 4 and then 2 against 3. Fails.

# normalising works the same way:
img = np.arange(2*3*4, dtype=float).reshape(2, 3, 4) + 1
np.round((img / img.sum(axis=-1, keepdims=True)).sum(axis=-1), 10)
# => array([[1., 1., 1.],
#           [1., 1., 1.]])

# ============================================
# THE PAYOFF: a numerically stable softmax
#
# softmax(x)_i = exp(x_i) / sum_j exp(x_j)
# ...which overflows the moment x gets large.

x = np.array([[   1.,    2.,    3.],
              [1000., 1001., 1002.]])

naive = np.exp(x) / np.exp(x).sum(axis=1, keepdims=True)
naive
# => array([[0.09003057, 0.24472847, 0.66524096],
#           [       nan,        nan,        nan]])
bool(np.isnan(naive).any())             # => True
#
# exp(1000) is inf; inf/inf is nan. The first row is
# fine and the second is destroyed — a data-dependent
# failure, the worst kind.

# the fix: subtract the row max first. Mathematically a
# no-op (it cancels), numerically it caps the exponent
# at exp(0) == 1.
stable = np.exp(x - x.max(axis=1, keepdims=True))
stable = stable / stable.sum(axis=1, keepdims=True)
np.round(stable, 6)
# => array([[0.090031, 0.244728, 0.665241],
#           [0.090031, 0.244728, 0.665241]])

stable.sum(axis=1)                      # => array([1., 1.])
np.allclose(stable[0], stable[1])       # => True
#
# both rows give the same answer, as they must —
# softmax is shift-invariant.
#
# NOTE THE TWO keepdims. The max must broadcast back
# over the row, and so must the sum. Drop either one and
# this raises (or, on a square input, quietly misaligns).
# This is the canonical example of the pattern.

# ============================================
# Standardising — two statistics, both kept

f = np.arange(12, dtype=float).reshape(3, 4)    # 3 samples, 4 features

mu = f.mean(axis=0, keepdims=True)      # (1, 4)   per FEATURE
sd = f.std(axis=0, keepdims=True)       # (1, 4)
z = (f - mu) / sd

z.shape                                 # => (3, 4)
np.allclose(z.mean(axis=0), 0)          # => True
np.allclose(z.std(axis=0), 1)           # => True
#
# here `axis=0` gives (4,), which WOULD have aligned
# without keepdims — the last axis is free (lesson 18).
# Write keepdims anyway: it makes the intent explicit
# and it keeps working if someone adds a batch axis.

# ============================================
# Chaining reductions

t.sum(axis=2, keepdims=True).sum(axis=1, keepdims=True).shape   # => (2, 1, 1)
t.sum(axis=2).sum(axis=1).shape                                 # => (2,)
#
# with keepdims the axis NUMBERS stay valid through the
# chain. Without it they renumber after each step, which
# is lesson 22's trap. Keeping the dims is the simplest
# way to avoid having to think about it.

# ============================================
# keepdims vs a manual None

np.array_equal(t.sum(axis=1, keepdims=True),
               t.sum(axis=1)[:, None, :])       # => True
#
# identical. Prefer keepdims:
#
#   keepdims=True     cannot put the 1 in the wrong place
#   [:, None, :]      you have to count, and it is
#                     wrong the moment the axis changes
#
# and with a variable axis the manual form needs
# np.expand_dims(reduced, axis) — at which point
# keepdims was always the shorter path.

# ============================================
# Dropping it again, when you need the rank back

t.sum(axis=1, keepdims=True).squeeze(axis=1).shape          # => (2, 4)
np.array_equal(t.sum(axis=1, keepdims=True).squeeze(axis=1),
               t.sum(axis=1))                               # => True
#
# name the axis in squeeze (lesson 16). Bare squeeze()
# would also drop any OTHER size-1 axis, including a
# batch of one.

# ============================================
# When you do NOT need it
#
# If the reduced result is the final answer, keepdims is
# just noise.

float(t.mean())                         # a number to print
t.sum(axis=(1, 2)).tolist()             # => [66, 210]   per-sample totals
#
# rule of thumb: does the result meet the ORIGINAL
# tensor again? If yes, keepdims. If it is going to a
# log line, a metric or a return value, don't bother.

# ============================================
# Compare

t.mean(axis=1)                          # (2, 4)      the statistic
t.mean(axis=1, keepdims=True)           # (2, 1, 4)   ...ready to broadcast
t - t.mean(axis=1, keepdims=True)       # (2, 3, 4)   centred
t / t.sum(axis=1, keepdims=True)        # (2, 3, 4)   normalised

# the pattern in one line, at any rank and any axis:
def centre(a, axis):
    return a - a.mean(axis=axis, keepdims=True)

[centre(t, k).shape for k in (0, 1, 2)]     # => [(2,3,4)] * 3
[np.allclose(centre(t, k).mean(axis=k), 0) for k in (0, 1, 2)]   # => [True]*3
#
# no per-axis special case. That is what keepdims buys.
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the reduced axis kept|`keepdims=True`|
|to centre|`t - t.mean(axis=k, keepdims=True)`|
|to normalise|`t / t.sum(axis=k, keepdims=True)`|
|a stable softmax|subtract `max(keepdims)`, divide by `sum(keepdims)`|
|to know when you need it|does the result meet the original again?|
|the manual form|`np.expand_dims(reduced, axis)` — but just use keepdims|
|the rank back|`.squeeze(axis=k)`, named|
|**not** to be caught|square shapes hide the missing flag|

---

## Key Insight

**`keepdims=True` exists because reductions are usually half of a round trip.** You reduce to get a statistic, then you use that statistic against the tensor it came from — and the size-1 axis is what makes the second step line up.

```text
reduce  ──►  broadcast back
```

Without the flag, the reduced axis vanishes and the statistic right-aligns against whatever axis happens to be last. Lesson 18 established the two failure modes: it **raises** when the sizes disagree and **silently misaligns** when they coincide. `keepdims=True` removes the question entirely — there is no counting, no `None` placement, and it works unchanged for any axis and any rank.

The stable softmax is the pattern at its most concentrated:

```python
e = np.exp(x - x.max(axis=1, keepdims=True))
softmax = e / e.sum(axis=1, keepdims=True)
```

Two reductions, two round trips, two `keepdims`. Drop either and it breaks — and the naive version without the max subtraction produces `nan` for large inputs while looking perfectly correct on small test data.

Two secondary benefits worth knowing:

- **Chained reductions keep their axis numbers.** `t.sum(axis=2, keepdims=True).sum(axis=1, keepdims=True)` refers to the original axes throughout; without keepdims the axes renumber after every step (lesson 22).
    
- **It removes the per-axis special case.** `a - a.mean(axis=axis, keepdims=True)` works for every `axis` with no branching — which is how you write a function that takes `axis` as a parameter.
    

And when the reduction *is* the answer — a metric, a log line, a return value — skip it. The test is simply: does this result meet the original tensor again?

---

## Keepdims vs Not

|Form|Shape|Use when|
|---|---|---|
|`t.sum(axis=1)`|`(2, 4)`|the statistic is the answer|
|`t.sum(axis=1, keepdims=True)`|`(2, 1, 4)`|the statistic goes back against `t`|

```text
   (2, 3, 4)  --sum(axis=1)-------------->  (2, 4)      done
   (2, 3, 4)  --sum(axis=1, keepdims)---->  (2, 1, 4)  --broadcast-->  (2, 3, 4)
```

> **Mental shift:** in part 1 a reduction ended the computation — `sum(xs)` was the result. In part 3 it usually starts one. The statistic is a means, not an end, and `keepdims=True` is the small piece of bookkeeping that keeps it usable. Making it your default costs nothing and removes an entire class of silent bugs.
