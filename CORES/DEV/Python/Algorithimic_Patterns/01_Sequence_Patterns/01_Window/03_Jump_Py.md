# Pattern 3 — Jump Window (Strided Window)

## Mental Model

Move a **fixed-size window** through a sequence by **jumping multiple elements** each time. Windows may overlap, touch, or have gaps depending on the jump size.

Python has no `partition n step` builtin, so the stride lives in **`range(0, len(xs), step)`** — the third argument of `range` (or of a slice) *is* the jump.

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Jump Window
```

Jump Window is a **Window** pattern where the window advances by a **fixed stride greater than one**.

---

## Python Functions & Common Variations

|Variation|Example|Common Python|
|---|---|---|
|Jump 2, Window 3|`(1 2 3) (3 4 5) (5 6 7)`|`[xs[i:i+3] for i in range(0, len(xs)-2, 2)]`|
|Jump 3, Window 4|`(1 2 3 4) (4 5 6 7)`|`[xs[i:i+4] for i in range(0, len(xs)-3, 3)]`|
|Jump = Window (Chunk)|`(1 2 3) (4 5 6)`|`itertools.batched(xs, 3)`|
|Jump > Window (Gapped)|`(1 2) (5 6) (9 10)`|`[xs[i:i+2] for i in range(0, len(xs), 4)]`|
|Keep Partial End|include incomplete final window|`range(0, len(xs), step)` (no `-n+1` trim)|
|Every Nth element (window 1)|`1 4 7`|`xs[::3]`|
|Lazy / streaming stride|generators|`itertools.islice(it, 0, None, step)`|

---

## Common Uses

- Downsampling signals

- Video frame sampling

- Processing every Nth record

- Sparse feature extraction

- Time-series sampling

- Data compression

- Game AI tick processing

- Large dataset sampling

---

## Hidden Interview Problems

- Process every Kth element

- Analyze every Nth frame

- Sample logs periodically

- Downsample sensor readings

- Feature extraction from streams

- Efficient large-scale scanning

---

## Recognition Clues

If you hear:

- Every **K** elements

- Skip **N**

- Sample periodically

- Jump ahead

- Stride

- Downsample

- Every third frame

- Every fifth record

Think:

**→ Jump Window**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Window|
|Pattern|Jump Window|
|Overlap|Depends on stride|
|Window Size|Fixed|
|Step Size|Any positive integer|
|Preserves Order|Yes|
|Covers All Elements|Not necessarily|

---

## Python Recipe Book

```python
# ============================================
# Setup

from itertools import islice, batched      # batched: 3.12+

xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# ============================================
# The one function that covers every case

def jump(xs, n, step, partial=False):
    """Windows of size n, advancing by `step`.

    partial=False → only full windows
    partial=True  → include the ragged final window
    """
    stop = len(xs) if partial else len(xs) - n + 1
    return [xs[i:i + n] for i in range(0, stop, step)]

# Everything below is this one function with different numbers.

# ============================================
# Jump 2, Window 3 — overlapping by 1

jump(xs, 3, 2)
# => [[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8, 9]]

# ============================================
# Jump 3, Window 4 — overlapping by 1

jump(xs, 4, 3)
# => [[1, 2, 3, 4], [4, 5, 6, 7], [7, 8, 9, 10]]

# ============================================
# Jump == Window → this is just Chunk

jump(xs, 3, 3)                    # => [[1,2,3], [4,5,6], [7,8,9]]
list(batched(xs, 3))              # same idea, keeps the tail (10,)

# ============================================
# Jump > Window → gaps, elements are skipped entirely

jump(xs, 2, 4)
# => [[1, 2], [5, 6], [9, 10]]
#      ^^^^         3,4 and 7,8 are never seen

# ============================================
# Keep the partial final window

jump(xs, 3, 4, partial=True)
# => [[1, 2, 3], [5, 6, 7], [9, 10]]

# ============================================
# Window of 1 → plain sampling, use a slice step

xs[::3]                           # => [1, 4, 7, 10]
xs[1::3]                          # => [2, 5, 8]     (phase offset 1)

# The slice's third argument IS the jump. No loop needed.

# ============================================
# Lazy stride over a stream (no len(), possibly infinite)

def jump_lazy(it, n, step):
    it = iter(it)
    win = list(islice(it, n))
    while len(win) == n:
        yield win
        if step < n:
            win = win[step:] + list(islice(it, step))   # overlap: reuse the tail
        else:
            list(islice(it, step - n))                  # burn the gap
            win = list(islice(it, n))                   # then a fresh window

list(jump_lazy(iter(xs), 3, 2))
# => [[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8, 9]]

# lazy sampling, window of 1
list(islice(iter(xs), 0, None, 3))               # => [1, 4, 7, 10]

# ============================================
# Downsample: one value per window

[sum(w) / len(w) for w in jump(xs, 3, 3)]        # => [2.0, 5.0, 8.0]
[max(w) for w in jump(xs, 4, 2)]                 # peak-preserving downsample

# ============================================
# Process every Nth record

for i, rec in enumerate(xs):
    if i % 3 == 0:
        ...            # equivalent to xs[::3], but you keep the index

# ============================================
# Sampling from a stream of unknown length

frames = range(1_000_000)
sampled = islice(frames, 0, None, 250)           # every 250th frame, lazily
sum(1 for _ in sampled)                          # => 4000

# ============================================
# Compare — the whole Window family in four lines

jump(xs, 3, 1)          # step < size  → Sliding / Overlapping
jump(xs, 3, 3)          # step == size → Chunk
jump(xs, 3, 5)          # step > size  → Gapped, skips data
xs[::3]                 # size 1       → Sample / Stride
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|windows of n every k|`[xs[i:i+n] for i in range(0, len(xs)-n+1, k)]`|
|include the ragged tail|drop the `-n+1` from the `range` stop|
|every kth element|`xs[::k]`|
|every kth, offset by j|`xs[j::k]`|
|every kth, lazily|`islice(it, 0, None, k)`|
|no overlap at all|`step >= n`|
|nothing skipped|`step <= n`|

---

### Key Insight

**Stride is a single number that decides the entire Window family.** Fix the window size `n` and vary the step: `1` gives Sliding, `n` gives Chunk, `> n` gives Gapped sampling. There is no separate algorithm to learn — only a different third argument to `range`.

The practical warning: when `step > n`, data is **silently discarded**. That is the point when downsampling, and a bug everywhere else — so make the stride an explicit named variable, never a magic number buried in a slice.
