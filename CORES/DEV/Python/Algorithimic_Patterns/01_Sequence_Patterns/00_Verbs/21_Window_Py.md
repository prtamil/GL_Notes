# Sequence Processing — Verb 21: Window

## Introduction

Sometimes looking at **one element at a time isn't enough**. The meaning comes from **neighboring elements**.

**Window** is the act of viewing a sequence through small contiguous groups of elements.

The mental question is:

> **"Which neighboring elements should I examine together?"**

Unlike **Slice**, which extracts one portion of a sequence, **Window** repeatedly moves across the sequence, producing many local views.

---

# Window → Python

| Thinking Verb | Mental Question                                       | Common Python                                                                              |
| ------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Window**    | Which neighboring elements should I examine together? | `itertools.pairwise`, `itertools.batched`, `zip(xs, xs[1:])`, slicing + `range`, `deque(maxlen=n)`, `groupby` |

> **Note:** Python has no single `partition(size, step, xs)`. Instead there are two specialized tools — `batched` for **size == step** (chunks) and `pairwise` for **size 2, step 1** — and a slicing comprehension for everything in between.

---

# Common Window Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Chunk (non-overlapping)|`batched(xs, 3)`|`[1..6]` → `[(1,2,3), (4,5,6)]`|
|Sliding window (step 1)|`[xs[i:i+3] for i in range(len(xs)-2)]`|`[1..5]` → `[[1,2,3],[2,3,4],[3,4,5]]`|
|Adjacent pairs|`pairwise(xs)`|`[1,2,3]` → `[(1,2), (2,3)]`|
|Jump window (step 2)|`[xs[i:i+3] for i in range(0, len(xs)-2, 2)]`|`[1..7]` → `[[1,2,3],[3,4,5],[5,6,7]]`|
|Gapped window|`[xs[i:i+2] for i in range(0, len(xs), 4)]`|`[1..8]` → `[[1,2], [5,6]]`|
|Partial final window|`batched(xs, 3)`|`[1..5]` → `[(1,2,3), (4,5)]`|
|Logical window (key changes)|`groupby(xs, key=f)`|`[1,3,2,4,5,7]` by parity → `[[1,3],[2,4],[5,7]]`|
|Rolling window over a stream|`deque(maxlen=n)`|append each item; the deque *is* the window|
|Window aggregate|comprehension|`[sum(w) for w in batched(xs, 3)]`|

> **Note:** An **overlapping window** is simply any window where **step < window size**. A **sliding window** is the special case where **step = 1**, and **chunking** is the case where **step = window size**.

---

# The Python-specific catches

**The sliding-window bound is `len(xs) - n + 1`.** Get it wrong and you either drop the last window or emit a short one. `zip(xs, xs[1:], xs[2:])` avoids the arithmetic entirely for small fixed widths.

**Slicing needs `len()`.** None of the slicing forms work on a generator — for a stream, use `deque(maxlen=n)` and read the window after each `append`, which is O(1) memory and works on infinite input.

**A rolling sum should not re-sum.** Recomputing `sum(window)` each step is O(n·k); add the entering element and subtract the leaving one instead, for O(n).

---

# One Sentence to Remember

> **Window repeatedly views neighboring elements together by moving across a sequence — window size and step are the only two parameters, and every windowing pattern is a choice of those two.**
