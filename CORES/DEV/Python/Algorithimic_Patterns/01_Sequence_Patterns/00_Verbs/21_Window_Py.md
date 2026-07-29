# Sequence Processing — Verb 21: Window

## Introduction

Sometimes **one element at a time tells you nothing**. The meaning lives in **what's next to what**.

**Window** looks at a sequence through small runs of neighbouring elements.

The question you're asking:

> **"Which neighboring elements should I examine together?"**

**Slice** takes one piece and stops. **Window** keeps moving along the sequence, handing you one local view after another.

---

# Window → Python

| Thinking Verb | Mental Question                                       | Common Python                                                                              |
| ------------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **Window**    | Which neighboring elements should I examine together? | `itertools.pairwise`, `itertools.batched`, `zip(xs, xs[1:])`, slicing + `range`, `deque(maxlen=n)`, `groupby` |

> **Note:** Python doesn't give you one `partition(size, step, xs)`. You get two specialised tools — `batched` for **size == step** (chunks) and `pairwise` for **size 2, step 1** — plus a slicing comprehension for everything in between.

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

> **Note:** An **overlapping window** is just any window where **step < window size**. A **sliding window** is the case where **step = 1**, and **chunking** is the case where **step = window size**.

---

# The Python-specific catches

**The sliding-window bound is `len(xs) - n + 1`.** Get it wrong and you either lose the last window or emit a short one. For small fixed widths, `zip(xs, xs[1:], xs[2:])` skips the arithmetic altogether.

**Slicing needs `len()`.** None of the slicing forms work on a generator. For a stream, use `deque(maxlen=n)` and read the window after each `append`: O(1) memory, and it happily runs on infinite input.

**Don't re-sum a rolling window.** Calling `sum(window)` at every step is O(n·k). Add the element coming in, subtract the one going out, and you're at O(n).

---

# One Sentence to Remember

> **Window walks across a sequence looking at neighbouring elements together. There are only two knobs — window size and step — and every windowing pattern is just a setting of those two.**
