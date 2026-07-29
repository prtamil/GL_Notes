# Pattern 4 — Overlapping Window

## Mental Model

Process **windows that intentionally share elements**. The amount of overlap can vary depending on the application.

> **Sliding Window is the most common type of Overlapping Window.**

In Python you rarely say "overlap" directly — you say **step**, and overlap falls out of it: `overlap = n - step`.

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Overlapping Window
```

Overlapping Window is a general pattern where consecutive windows reuse some of the previous elements.

---

## Python Functions & Common Variations

|Variation|Example|Common Python|
|---|---|---|
|1-element overlap|`(1 2 3) (3 4 5)`|`[xs[i:i+3] for i in range(0, len(xs)-2, 2)]`|
|2-element overlap (Sliding)|`(1 2 3) (2 3 4)`|`zip(xs, xs[1:], xs[2:])`|
|Large overlap|`(1 2 3 4) (2 3 4 5)`|`[xs[i:i+4] for i in range(len(xs)-3)]`|
|Configurable overlap|window `n`, step `n - overlap`|`range(0, len(xs)-n+1, n-overlap)`|
|Keep Partial End|include incomplete final window|`range(0, len(xs), step)`|
|Streaming overlap|audio / sensor frames|`deque(maxlen=n)` + emit every `step`|
|Overlap-add reconstruction|windowed signal → signal|accumulate into a zeroed buffer|

---

## Common Uses

- Audio signal processing

- Image convolution

- Video frame analysis

- Speech recognition

- Time-series forecasting

- DNA sequence analysis

- Text n-grams

- Streaming analytics

---

## Hidden Interview Problems

- Moving averages

- Rolling statistics

- Consecutive pattern detection

- Window-based anomaly detection

- Sequence matching

- Time-series feature extraction

---

## Recognition Clues

If you hear:

- Overlapping data

- Shared neighbors

- Rolling window

- Reuse previous values

- Sliding analysis

- Context preservation

- Neighboring elements

Think:

**→ Overlapping Window**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Window|
|Pattern|Overlapping Window|
|Overlap|Yes (configurable)|
|Window Size|Fixed|
|Step Size|Less than Window Size|
|Preserves Order|Yes|
|Covers All Elements|Usually Yes|

---

## Python Recipe Book

```python
# ============================================
# Setup

from collections import deque
from itertools import islice

xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# ============================================
# Say it in terms of overlap, not step

def windows(xs, n, overlap):
    """Windows of size n where consecutive windows share `overlap` elements."""
    assert 0 <= overlap < n, "overlap must be smaller than the window"
    step = n - overlap
    return [xs[i:i + n] for i in range(0, len(xs) - n + 1, step)]

# ============================================
# 1-element overlap  (n=3, step=2)

windows(xs, 3, overlap=1)
# => [[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8, 9]]
#            ^^^^^^ 3 appears in two windows

# ============================================
# 2-element overlap = Sliding Window  (n=3, step=1)

windows(xs, 3, overlap=2)[:3]
# => [[1, 2, 3], [2, 3, 4], [3, 4, 5]]

# the fast idiom for a fixed small n:
list(zip(xs, xs[1:], xs[2:]))[:3]
# => [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

# ============================================
# Large overlap  (n=4, step=1) — 75% shared

windows(xs, 4, overlap=3)[:3]
# => [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]

# ============================================
# No overlap → you have left the pattern; this is Chunk

windows(xs, 3, overlap=0)
# => [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# ============================================
# 50% overlap — the audio/DSP default ("hop size = n/2")

n, hop = 4, 2
frames = [xs[i:i + n] for i in range(0, len(xs) - n + 1, hop)]
# => [[1,2,3,4], [3,4,5,6], [5,6,7,8], [7,8,9,10]]

# ============================================
# Streaming overlap — emit a window every `step` arrivals

def overlapping_stream(it, n, step):
    win = deque(maxlen=n)
    countdown = n
    for x in it:
        win.append(x)
        countdown -= 1
        if len(win) == n and countdown <= 0:
            yield tuple(win)
            countdown = step

list(overlapping_stream(iter(xs), 4, 2))
# => [(1,2,3,4), (3,4,5,6), (5,6,7,8), (7,8,9,10)]

# deque(maxlen=n) is the whole trick: old elements fall off the left for free.

# ============================================
# Rolling statistics over overlapping windows

ws = windows(xs, 4, overlap=3)
[sum(w) / len(w) for w in ws][:3]            # rolling mean  => [2.5, 3.5, 4.5]
[max(w) - min(w) for w in ws][:3]            # rolling range => [3, 3, 3]

# ============================================
# Rolling standard deviation

import statistics
[round(statistics.pstdev(w), 3) for w in windows(xs, 4, 3)][:3]
# => [1.118, 1.118, 1.118]

# ============================================
# Anomaly detection — compare a point to its NEIGHBOURS

def anomalies(xs, n=5, k=3.0):
    mid = n // 2
    for i, w in enumerate(windows(xs, n, overlap=n - 1)):
        ctx = w[:mid] + w[mid + 1:]          # the window minus the point itself
        mu, sd = statistics.mean(ctx), statistics.pstdev(ctx) or 1e-9
        if abs(w[mid] - mu) > k * sd:
            yield i + mid, w[mid]

list(anomalies([1, 1, 1, 1, 9, 1, 1, 1, 1]))   # => [(4, 9)]

# Excluding the centre matters: a spike large enough to matter also drags
# the mean and stdev of its own window, and can hide itself from the test.
# Caveat: a perfectly flat context gives sd == 0, so the 1e-9 guard makes
# ANY deviation an anomaly. On real data use a floor you chose on purpose.

# ============================================
# Character n-grams (overlap = n-1) — fuzzy matching, plagiarism

def ngrams(s, n):
    return {s[i:i + n] for i in range(len(s) - n + 1)}

a, b = ngrams("clojure", 3), ngrams("closure", 3)
len(a & b) / len(a | b)                       # Jaccard similarity => 0.25

# ============================================
# Overlap-add — reconstruct a signal from windowed frames

def overlap_add(frames, hop):
    n = len(frames[0])
    out = [0] * (hop * (len(frames) - 1) + n)
    for f, frame in enumerate(frames):
        for i, v in enumerate(frame):
            out[f * hop + i] += v             # overlapping regions accumulate
    return out

overlap_add([[1, 1], [1, 1], [1, 1]], hop=1)  # => [1, 2, 2, 1]
# the 2s are exactly where the windows overlapped

# ============================================
# Compare — overlap is derived, not primitive

# overlap = n - step
windows(xs, 3, overlap=2)     # step 1  → Sliding
windows(xs, 3, overlap=1)     # step 2  → Jump, still overlapping
windows(xs, 3, overlap=0)     # step 3  → Chunk, no sharing
# step > n                    → Gapped, data skipped (see 03_Jump)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|overlap of k|`step = n - k`|
|maximum overlap|`step = 1` → Sliding Window|
|50% overlap (DSP hop)|`step = n // 2`|
|no overlap|`step = n` → Chunk|
|streaming overlap|`deque(maxlen=n)` + a countdown|
|rolling stat|`[f(w) for w in windows(...)]`|
|put the pieces back|overlap-add into a zeroed buffer|

---

### Key Insight

**Overlap is not an operation — it is a number you compute: `overlap = n - step`.** Every "overlapping window" API in the wild (DSP hop size, tokenizer stride, chunked-embedding overlap) is this one subtraction wearing a different name.

The reason to overlap at all: **windows destroy context at their edges.** An event straddling a chunk boundary is invisible to both chunks. Overlap buys back that context at a cost of `n / step` × the work — which is why the tuning question is always "how much context do I need?", never "how big should the window be?".
