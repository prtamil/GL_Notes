# Pattern 2 — Sliding Window

## Mental Model

Slide a **fixed-size window** along a sequence **one element at a time**. Each window **overlaps** heavily with the one before it.

Python has no single `partition` builtin for this, so you choose: **slicing** (needs an indexable input, eager), **`itertools`** (lazy), or **`deque(maxlen=n)`** (streaming, O(1) per step).

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Sliding Window
```

Sliding Window is a **Window** pattern where the window moves forward **one position** at a time.

---

## Python Functions & Common Variations

|Variation|Example|Common Python|
|---|---|---|
|Sliding Window (size 2)|`(1 2) (2 3) (3 4)`|`itertools.pairwise(xs)`|
|Sliding Window (size 3)|`(1 2 3) (2 3 4)`|`zip(xs, xs[1:], xs[2:])`|
|Sliding Window (size N)|Overlapping windows|`[xs[i:i+n] for i in range(len(xs)-n+1)]`|
|Sliding Window (lazy / stream)|infinite input|`deque(maxlen=n)` loop|
|Sliding Window (keep partial end)|`(1 2 3) (2 3) (3)`|`[xs[i:i+n] for i in range(len(xs))]`|
|Rolling aggregate|moving sum/avg|running total, not re-summing|

---

## Common Uses

- Moving average

- Time-series analysis

- Signal processing

- Image filters (convolution)

- Video frame analysis

- Text n-grams

- DNA sequence analysis

- Network traffic monitoring

- Sensor data streams

---

## Hidden Interview Problems

- Maximum sum subarray of size K

- Longest substring without duplicates

- Minimum window substring

- Sliding window maximum

- Moving average

- Consecutive pattern detection

- Fraud detection over recent transactions

---

## Recognition Clues

If you hear:

- Moving

- Rolling

- Recent **N**

- Last **K**

- Consecutive elements

- Running window

- Window slides

- Neighboring values

Think:

**→ Sliding Window**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Window|
|Pattern|Sliding Window|
|Overlap|Yes|
|Window Size|Fixed|
|Step Size|1|
|Preserves Order|Yes|
|Covers All Elements|Yes (except incomplete tail unless you ask for it)|

---

## Python Recipe Book

```python
# ============================================
# Setup

from collections import deque
from itertools import pairwise, islice, tee, batched   # batched: 3.12+

xs = [1, 2, 3, 4, 5]

# ============================================
# Window of 2 — pairwise (3.10+), the one you use most

list(pairwise(xs))
# => [(1, 2), (2, 3), (3, 4), (4, 5)]

# ============================================
# Window of 3 — zip of offset slices

list(zip(xs, xs[1:], xs[2:]))
# => [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

# reads exactly like the picture: column i of the zip is offset i

# ============================================
# Window of N — slicing (indexable input)

n = 3
[xs[i:i + n] for i in range(len(xs) - n + 1)]
# => [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

# len(xs) - n + 1 is the window count. Off-by-one lives here — memorize it.

# ============================================
# Window of N — lazy, works on generators and infinite streams

def sliding(it, n):
    it = iter(it)
    win = deque(islice(it, n), maxlen=n)
    if len(win) == n:
        yield tuple(win)
    for x in it:
        win.append(x)          # maxlen makes the oldest fall off, O(1)
        yield tuple(win)

list(sliding(xs, 3))
# => [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

# ============================================
# Window of N — generic zip trick (itertools.tee)

def sliding_zip(it, n):
    iters = tee(it, n)
    for i, t in enumerate(iters):
        next(islice(t, i, i), None)   # advance the i-th copy by i
    return zip(*iters)

list(sliding_zip(xs, 3))     # => [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

# ============================================
# Keep the shrinking tail

[xs[i:i + 3] for i in range(len(xs))]
# => [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5], [5]]

# ============================================
# Moving average

[sum(w) / 3 for w in sliding(xs, 3)]        # => [2.0, 3.0, 4.0]

# ============================================
# Rolling sum in O(n) — add the new, drop the old

def rolling_sum(xs, n):
    total = sum(xs[:n])
    yield total
    for i in range(n, len(xs)):
        total += xs[i] - xs[i - n]          # never re-sum the window
        yield total

list(rolling_sum(xs, 3))                    # => [6, 9, 12]

# This is THE sliding-window optimization: recompute the delta, not the window.

# ============================================
# Maximum sum subarray of size K

max(rolling_sum(xs, 3))                     # => 12

# ============================================
# Sliding window maximum — monotonic deque, O(n)

def window_max(xs, n):
    dq, out = deque(), []                   # dq holds indices, values decreasing
    for i, x in enumerate(xs):
        while dq and xs[dq[-1]] <= x:
            dq.pop()                        # x beats everything smaller behind it
        dq.append(i)
        if dq[0] <= i - n:
            dq.popleft()                    # front slid out of the window
        if i >= n - 1:
            out.append(xs[dq[0]])
    return out

window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)   # => [3, 3, 5, 5, 6, 7]

# ============================================
# Variable-size window — longest substring without repeats

def longest_unique(s):
    seen, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1             # shrink from the left
        seen[ch] = right
        best = max(best, right - left + 1)
    return best

longest_unique("abcabcbb")                  # => 3

# Two pointers = a window whose size is decided by the data, not by n.

# ============================================
# Text n-grams

words = "the quick brown fox jumps".split()
[" ".join(w) for w in sliding(words, 2)]
# => ['the quick', 'quick brown', 'brown fox', 'fox jumps']

# ============================================
# Compare

list(pairwise(xs))                          # step 1, size 2
list(sliding(xs, 3))                        # step 1, size 3  → overlap
list(batched(xs, 3))                        # step 3, size 3  → chunk, no overlap
xs[::3]                                     # every 3rd element, no window at all
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|neighbours, size 2|`pairwise(xs)`|
|size 3, indexable|`zip(xs, xs[1:], xs[2:])`|
|size n, indexable|`[xs[i:i+n] for i in range(len(xs)-n+1)]`|
|size n, streaming|`deque(maxlen=n)`|
|rolling sum in O(n)|`total += new - old`|
|window max in O(n)|monotonic `deque` of indices|
|window size set by data|two pointers (`left`, `right`)|

---

### Key Insight

**A sliding window drops an O(n·k) problem to O(n)**, but only if you update the window's *summary* as you go instead of rebuilding it. Put `sum(window)` inside the loop and you've thrown the whole benefit away.

The other thing worth noticing: **the window doesn't have to be a fixed size.** Let a condition decide the size instead of a constant and you've got the two-pointer technique, which is what most of the "hard" sliding-window interview problems really are.
