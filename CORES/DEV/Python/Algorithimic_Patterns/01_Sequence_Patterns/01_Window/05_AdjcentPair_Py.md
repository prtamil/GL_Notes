# Pattern 5 — Adjacent Pair

## Mental Model

Take **neighbouring elements** together so you can compare them, transform them, or spot where something changed.

Python gives this one its own builtin: **`itertools.pairwise`** (3.10+). It's the most reusable single line in this whole family of patterns.

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Adjacent Pair
```

Adjacent Pair is just a **Sliding Window** with the **window size pinned at 2**.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Forward Pair (Current → Next)|`(1 2) (2 3) (3 4)`|`pairwise(xs)`|
|Forward Pair (keep partial tail)|`(1 2) (2 3) (3,)`|`zip_longest(xs, xs[1:])`|
|Current + Next|`(curr, nxt)`|`zip(xs, xs[1:])`|
|Previous + Current|`(prev, curr)`|`zip(xs, xs[1:])` _(viewed from the right element)_|
|Previous + Current + Next|`(prev, curr, nxt)`|`zip(xs, xs[1:], xs[2:])`|
|Compare Adjacent Values|`curr < nxt`|`all(a < b for a, b in pairwise(xs))`|
|Difference Between Adjacent|`nxt - curr`|`[b - a for a, b in pairwise(xs)]`|
|Adjacent with Index|`(i, curr, nxt)`|`enumerate(pairwise(xs))`|
|Wrap-around pair (cyclic)|`… (last, first)`|`zip(xs, xs[1:] + xs[:1])`|

> **Note:** `Current + Next` and `Previous + Current` are the **same Python idiom**: `pairwise(xs)` produces `(10, 20) (20, 30) (30, 40)`. The difference is **how you read each pair**. Standing on the **first** element it means **(current, next)** — "I'm at 10, next is 20." Standing on the **second** it means **(previous, current)** — "I'm at 20, previous was 10." The code is identical; only the mental perspective changes. Name the loop variables accordingly (`for prev, curr in ...` vs `for curr, nxt in ...`) and the intent documents itself.

---

## Common Uses

- Compare neighboring values

- Consecutive differences (delta)

- Trend detection

- Transition detection

- Sortedness checking

- Duplicate detection

- Velocity from positions

- Line / edge construction

- Change-point detection

---

## Hidden Interview Problems

- Check if an array is sorted

- Find adjacent duplicates

- Compute differences between consecutive values

- Count increasing/decreasing pairs

- Detect peaks and valleys

- Find transition points

- Compare neighboring timestamps

---

## Recognition Clues

If you hear:

- Previous element

- Next element

- Neighbor

- Adjacent

- Consecutive

- Delta

- Transition

- Compare with previous

- Compare with next

- Pairwise

Think:

**→ Adjacent Pair**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Window|
|Pattern|Adjacent Pair|
|Overlap|Yes|
|Window Size|2 (or 3 for both neighbors)|
|Step Size|1|
|Preserves Order|Yes|
|Covers All Elements|Yes (except boundaries unless handled explicitly)|

---

## Python Recipe Book

```python
# ============================================
# Setup

from itertools import pairwise, zip_longest, groupby   # pairwise: 3.10+

xs = [10, 20, 30, 40]

# ============================================
# The pattern itself

list(pairwise(xs))
# => [(10, 20), (20, 30), (30, 40)]

list(zip(xs, xs[1:]))          # pre-3.10 equivalent, identical result
# => [(10, 20), (20, 30), (30, 40)]

# n pairs from n+1 elements — there is always one fewer pair than element.

# ============================================
# Naming makes the perspective explicit

for curr, nxt in pairwise(xs):
    ...     # "I am curr, looking forward"

for prev, curr in pairwise(xs):
    ...     # same tuples, "I am curr, looking back"

# ============================================
# Deltas — the classic use

[b - a for a, b in pairwise(xs)]              # => [10, 10, 10]

# velocity from positions + timestamps
ts  = [0, 1, 3, 6]
pos = [0, 5, 15, 45]
[(p2 - p1) / (t2 - t1)
 for (t1, t2), (p1, p2) in zip(pairwise(ts), pairwise(pos))]
# => [5.0, 5.0, 10.0]

# ============================================
# Sortedness — one line, short-circuits

all(a <= b for a, b in pairwise(xs))          # => True   (non-decreasing)
all(a <  b for a, b in pairwise(xs))          # => True   (strictly increasing)
any(a >  b for a, b in pairwise(xs))          # => False  (any inversion?)

# ============================================
# Adjacent duplicates

[a for a, b in pairwise([1, 2, 2, 3, 3, 3]) if a == b]     # => [2, 3, 3]

any(a == b for a, b in pairwise([1, 2, 2, 3]))             # => True

# ============================================
# Count increasing / decreasing steps

steps = [b - a for a, b in pairwise([3, 1, 4, 1, 5])]      # => [-2, 3, -3, 4]
sum(d > 0 for d in steps)                                  # => 2 rises
sum(d < 0 for d in steps)                                  # => 2 falls

# ============================================
# Transition points — where the value changes

seq = ["a", "a", "b", "b", "c"]
[i + 1 for i, (a, b) in enumerate(pairwise(seq)) if a != b]
# => [2, 4]   (indices where a new run begins)

# ============================================
# Peaks and valleys — needs THREE neighbours, not two

ys = [1, 3, 2, 5, 4]
peaks   = [i + 1 for i, (a, b, c) in enumerate(zip(ys, ys[1:], ys[2:])) if a < b > c]
valleys = [i + 1 for i, (a, b, c) in enumerate(zip(ys, ys[1:], ys[2:])) if a > b < c]
# peaks   => [1, 3]
# valleys => [2]

# ============================================
# Both neighbours with the edges handled

def with_neighbours(xs, pad=None):
    return zip([pad] + list(xs), xs, list(xs[1:]) + [pad])

[(p, c, n) for p, c, n in with_neighbours([1, 2, 3])]
# => [(None, 1, 2), (1, 2, 3), (2, 3, None)]

# Boundaries are where adjacent-pair bugs live — pad them on purpose.

# ============================================
# Cyclic pairs — last element wraps to the first

cyc = list(zip(xs, xs[1:] + xs[:1]))
# => [(10, 20), (20, 30), (30, 40), (40, 10)]

# polygon edges, round-robin schedules, ring buffers

# ============================================
# Gap detection in timestamps

times = [0, 1, 2, 10, 11]
[(a, b) for a, b in pairwise(times) if b - a > 5]         # => [(2, 10)]

# ============================================
# Trend direction as a string

def trend(xs):
    return "".join("+" if b > a else "-" if b < a else "="
                   for a, b in pairwise(xs))

trend([1, 3, 3, 2])           # => '+=-'

# then reach for groupby to find the runs
[(k, len(list(g))) for k, g in groupby(trend([1, 2, 3, 2, 1]))]
# => [('+', 2), ('-', 2)]

# ============================================
# Keep the ragged tail (rare, but asked for sometimes)

list(zip_longest(xs, xs[1:]))
# => [(10, 20), (20, 30), (30, 40), (40, None)]

# ============================================
# Compare

list(pairwise(xs))                  # size 2, step 1  ← this pattern
list(zip(xs, xs[1:], xs[2:]))       # size 3, step 1  ← both neighbours
list(zip(xs[::2], xs[1::2]))        # size 2, step 2  ← disjoint pairs (Chunk)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|each item with its next|`pairwise(xs)`|
|each item with its previous|`pairwise(xs)`, read right-to-left|
|both neighbours|`zip(xs, xs[1:], xs[2:])`|
|differences|`[b - a for a, b in pairwise(xs)]`|
|"is it sorted?"|`all(a <= b for a, b in pairwise(xs))`|
|"where does it change?"|`enumerate(pairwise(xs))` + `a != b`|
|wrap-around|`zip(xs, xs[1:] + xs[:1])`|
|disjoint pairs instead|`zip(xs[::2], xs[1::2])`|

---

### Key Insight

**`pairwise` turns a sequence of *values* into a sequence of *changes*.** That's the whole pattern. `[10, 20, 30]` is three states; it becomes `[10, 10]`, two transitions. Most questions you ask about a sequence — is it sorted? is it monotonic? where did it jump? how fast? — are really questions about the deltas, and they collapse into one-liners once you make that switch.

Two things to watch out for. The result is **one element shorter**, and **the endpoints have no neighbour**. Every off-by-one in this pattern traces back to one of those two.
