# Pattern 29 — Running Sum (Prefix Sum)

## Mental Model

Compute the **cumulative total** at every step of a sequence.

Instead of returning only the final sum, **Running Sum** keeps every intermediate result.

Python's tool is **`itertools.accumulate`** — `reduce` with the intermediate values kept. It is lazy, takes any binary function, and takes an optional `initial=` value.

---

## Relationship to Cognitive Verb

```text
Scan
   ↓
Running Sum (Prefix Sum)
```

Running Sum is a **Scan** pattern because it scans the sequence while carrying forward an accumulated state.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Running Sum|`1 3 6 10`|`accumulate(xs)`|
|Running Product|`1 2 6 24`|`accumulate(xs, mul)`|
|Running Maximum|`3 3 5 5 8`|`accumulate(xs, max)`|
|Running Minimum|`5 5 3 3 2`|`accumulate(xs, min)`|
|Running String|`"a" "ab" "abc"`|`accumulate(xs, add)`|
|Running Balance|starts at 100|`accumulate(xs, initial=100)`|
|Running Average|mean so far|`accumulate` + `enumerate`|
|Custom State|a dict per step|`accumulate(xs, step_fn, initial=state)`|
|Final Value Only|the total|`sum(xs)` / `reduce(f, xs)`|

> **Note:** `accumulate` is **lazy** — wrap it in `list()` to see it. With `initial=`, the output is **one longer** than the input, and that extra leading element is exactly what makes range queries clean.

---

## Common Uses

- Prefix sums

- Running balance

- Progress tracking

- Cumulative statistics

- Financial ledgers

- Time series

- Dynamic programming

- Streaming analytics

---

## Hidden Interview Problems

- Prefix sum array

- Range sum queries

- Running average

- Running maximum

- Cumulative balance

- Maximum profit (buy/sell once)

- Water level / running minimum problems

---

## Recognition Clues

If you hear:

- Running

- Cumulative

- Prefix

- So far

- Up to this point

- Accumulate while traversing

- Rolling total

Think:

**→ Running Sum (Prefix Sum)**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Scan|
|Pattern|Running Sum|
|Output Size|same as input (+1 with `initial=`)|
|Keeps Intermediate Results|Yes|
|Builds State|Yes|
|Laziness|lazy iterator|
|Cost|O(n), one pass|
|Primary Use|Cumulative computation|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import accumulate, pairwise
from functools import reduce
from operator import mul, add, sub, or_
import statistics

xs = [1, 2, 3, 4, 5]

# ============================================
# Running sum — the default, no function needed

list(accumulate(xs))                    # => [1, 3, 6, 10, 15]

# accumulate defaults to operator.add. It's LAZY:
accumulate(xs)                          # => <itertools.accumulate object>

# ============================================
# reduce vs accumulate — the whole distinction

reduce(add, xs)                         # => 15                the total
sum(xs)                                 # => 15                same, faster
list(accumulate(xs))                    # => [1, 3, 6, 10, 15] every step

# reduce collapses to one value; accumulate keeps the trail.
# Last element of accumulate == the reduce result:
list(accumulate(xs))[-1] == sum(xs)     # => True

# ============================================
# Running product

list(accumulate(xs, mul))               # => [1, 2, 6, 24, 120]

# factorials for free:
list(accumulate(range(1, 6), mul))      # => [1, 2, 6, 24, 120]

# ============================================
# Running maximum / minimum

list(accumulate([3, 1, 5, 2, 8, 4], max))           # => [3, 3, 5, 5, 8, 8]
list(accumulate([5, 7, 3, 8, 2, 6], min))           # => [5, 5, 3, 3, 2, 2]

# "the best seen so far" — monotonic by construction, and the
# backbone of a dozen DP problems

# ============================================
# Running string

list(accumulate(["a", "b", "c", "d"], add))
# => ['a', 'ab', 'abc', 'abcd']

# works because str supports +. O(n²) total characters though —
# fine for display, wrong for building a large document.

# ============================================
# Growing collection

list(accumulate([["a"], ["b"], ["c"]], add))
# => [['a'], ['a', 'b'], ['a', 'b', 'c']]

# each step is a NEW list (add copies), so the snapshots are
# independent. Appending in place would give you n references to
# one list — every "snapshot" identical and fully grown.

# ============================================
# Running balance — initial= is the opening value

list(accumulate([20, -10, 50, -30], initial=100))
# => [100, 120, 110, 160, 130]

# note the output is 5 long for 4 transactions: the opening balance
# is included. That's usually what a ledger wants.

# without initial, you lose the starting point:
list(accumulate([20, -10, 50, -30]))    # => [20, 10, 60, 30]

# ============================================
# Running average

[s / i for i, s in enumerate(accumulate(xs), start=1)]
# => [1.0, 1.5, 2.0, 2.5, 3.0]

# enumerate(..., start=1) gives the COUNT so far alongside the sum.
# for a stream where you want the mean at each point:
def running_mean(it):
    total = n = 0
    for x in it:
        total += x
        n += 1
        yield total / n

list(running_mean(xs))                  # => [1.0, 1.5, 2.0, 2.5, 3.0]

# ============================================
# Custom running state — the general form

def step(state, x):
    return {"sum": state["sum"] + x, "count": state["count"] + 1}

list(accumulate(xs, step, initial={"sum": 0, "count": 0}))
# => [{'sum':0,'count':0}, {'sum':1,'count':1}, {'sum':3,'count':2}, ...]

# the function signature is f(accumulated, next) — accumulator FIRST.
# return a NEW state; mutating and returning the same dict gives you
# n references to one object, all showing the final value.

# ============================================
# THE ARGUMENT ORDER TRAP

list(accumulate(xs, sub))               # => [1, -1, -4, -8, -13]

# f(acc, x), not f(x, acc). For non-commutative functions (subtract,
# divide, string concat) the order is the whole answer.
# 1, 1-2=-1, -1-3=-4, ...

# ============================================
# Undo an accumulation — differences

sums = list(accumulate(xs))             # => [1, 3, 6, 10, 15]
[b - a for a, b in pairwise([0] + sums)]            # => [1, 2, 3, 4, 5]

# accumulate and "adjacent differences" are inverses. Given a
# cumulative series (odometer, counter, total-so-far), differencing
# recovers the per-step values — that's how you turn a monotonic
# metrics counter into a rate.

# ============================================
# Maximum profit — running minimum in disguise

prices = [7, 1, 5, 3, 6, 4]
max(p - lo for p, lo in zip(prices, accumulate(prices, min)))       # => 5

# "best price to have bought at, so far" is a running min; the answer
# is the largest gap between today and that. One pass, O(1) extra state.

# ============================================
# Streaming — accumulate never materializes the input

from itertools import count, islice
list(islice(accumulate(count(1)), 5))   # => [1, 3, 6, 10, 15]

# works on an infinite source. sum() on count() would hang forever.

# ============================================
# Progress tracking

sizes = [120, 340, 90, 450]
total = sum(sizes)
[f"{done / total:.0%}" for done in accumulate(sizes)]
# => ['12%', '46%', '55%', '100%']

# ============================================
# Cumulative distribution from a histogram

from collections import Counter
c = Counter("mississippi")
labels = sorted(c)
list(zip(labels, accumulate(c[k] for k in labels)))
# => [('i', 4), ('m', 5), ('p', 7), ('s', 11)]

# ============================================
# Running set-union — accumulate works on any associative op

list(accumulate([{1, 2}, {2, 3}, {4}], or_))
# => [{1, 2}, {1, 2, 3}, {1, 2, 3, 4}]

# "everything seen up to now" for tags, visitors, feature flags

# ============================================
# Float drift — the one numeric caveat

vals = [0.1] * 10
list(accumulate(vals))[-1]              # => 0.9999999999999999
sum(vals)                               # => 0.9999999999999999
statistics.fsum(vals)                   # => 1.0     exact

# error accumulates step by step. For money use Decimal or integer
# cents; for scientific sums use math.fsum / statistics.fsum.
# fsum has no running form — you'd re-fsum each prefix, O(n²).

# ============================================
# Compare

list(accumulate(xs))            # every prefix total      → Running Sum
sum(xs)                         # final total only        → Reduce
[b - a for a, b in pairwise(xs)]        # per-step deltas → the inverse
list(accumulate(xs, max))       # best so far             → Running Max
accumulate(xs, initial=0)       # +1 element, query-ready → Prefix Sum
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|running total|`accumulate(xs)`|
|running product|`accumulate(xs, mul)`|
|best/worst so far|`accumulate(xs, max)` / `min`|
|a starting value|`accumulate(xs, initial=v)`|
|running mean|`enumerate(accumulate(xs), 1)` then divide|
|arbitrary carried state|`accumulate(xs, step, initial=state)`|
|only the final value|`sum(xs)` or `reduce(f, xs)`|
|to undo a running sum|adjacent differences via `pairwise`|
|exact float sums|`math.fsum` (no running form)|
|running union|`accumulate(sets, or_)`|

---

### Key Insight

**`accumulate` is `reduce` that shows its work.** Same one-pass traversal, same `f(acc, x)` signature — it just yields each intermediate instead of only the last. Any time you catch yourself writing a loop with a `total` variable and an `append`, that loop is already `accumulate`; the only question is what the binary function is.

**The function argument order is `f(accumulated, next)`, and for anything non-commutative that order is the entire answer.** `accumulate(xs, sub)` computes `((1-2)-3)-4`, not the reverse. `max` and `min` don't care, `add` doesn't care, subtraction and string concatenation care very much. When a running computation gives a plausible but wrong series, check this first.

The habit worth building is noticing the **inverse relationship with adjacent differences**. `accumulate` turns per-step values into cumulative ones; `pairwise` differencing turns cumulative values back into per-step ones. Real data arrives in both forms — a bank statement lists transactions, an odometer lists totals, a Prometheus counter lists totals — and knowing which form you have, plus these two one-liners, is most of what time-series preprocessing amounts to.
