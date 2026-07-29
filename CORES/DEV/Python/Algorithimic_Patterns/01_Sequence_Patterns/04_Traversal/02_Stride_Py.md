# Pattern 13 — Stride Traversal

## Mental Model

Traverse a sequence by **skipping a fixed number of elements** between visits.

Instead of visiting every element, you visit **every Nth element**.

Python builds this into slice syntax: **`xs[start:stop:step]`**. The third number *is* the stride, and it is the reason Python needs no `take-nth`.

---

## Relationship to Cognitive Verb

```text
Traversal
      ↓
Stride Traversal
```

Stride Traversal is a **Traversal** pattern where the traversal advances by a fixed **stride** instead of one element at a time.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Every 2nd Element|`1 3 5`|`xs[::2]`|
|Every 3rd Element|`1 4 7`|`xs[::3]`|
|Drop then Stride|`2 4 6`|`xs[1::2]`|
|Stride a Range|`0 3 6 9`|`range(0, 10, 3)`|
|Stride an Iterator|lazy / infinite|`itertools.islice(it, 0, None, n)`|
|Indexed Stride|keep `i % n == 0`|`[x for i, x in enumerate(xs) if i % n == 0]`|
|Reverse Stride|`10 8 6`|`xs[::-2]`|
|Stride Windows|window ≠ step|`[xs[i:i+n] for i in range(0, len(xs), step)]`|

> **Note:** Unlike **Jump Window**, which returns **windows**, Stride Traversal returns **individual elements**.

---

## Common Uses

- Downsampling

- Periodic sampling

- Sparse traversal

- Data inspection

- Signal processing

- Image processing

- Frame skipping

- Performance optimization

---

## Hidden Interview Problems

- Print every Kth element

- Sample large datasets

- Skip alternate elements

- Read every Nth record

- Downsample a signal

- Sparse matrix traversal

---

## Recognition Clues

If you hear:

- Every Nth element

- Skip elements

- Every other

- Every third

- Downsample

- Sample periodically

- Sparse traversal

- Stride

Think:

**→ Stride Traversal**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Traversal|
|Pattern|Stride Traversal|
|Direction|Forward (negative step for backward)|
|Visits Every Element|No|
|Step Size|Fixed|
|Primary Use|Sparse traversal|
|Cost|`xs[::n]` copies; `islice` doesn't|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import islice, compress, cycle

xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# ============================================
# Every 2nd element

xs[::2]                                 # => [1, 3, 5, 7, 9]

# ============================================
# Every 3rd element

xs[::3]                                 # => [1, 4, 7, 10]

# ============================================
# Skip the first, then every 2nd

xs[1::2]                                # => [2, 4, 6, 8, 10]

# ============================================
# Drop 3, then every 2nd

xs[3::2]                                # => [4, 6, 8, 10]

# read xs[a:b:c] as "from a, up to b, every c"

# ============================================
# Bounded stride — stop early too

xs[0:6:2]                               # => [1, 3, 5]

# ============================================
# Even- and odd-indexed elements

xs[0::2]                                # => [1, 3, 5, 7, 9]     even indices
xs[1::2]                                # => [2, 4, 6, 8, 10]    odd indices

# the same thing, spelled with indices
[x for i, x in enumerate(xs) if i % 2 == 0]     # => [1, 3, 5, 7, 9]

# use the comprehension when you need i for something else;
# otherwise the slice says it more clearly.

# ============================================
# Enumerate every 3rd element

list(enumerate(xs[::3]))
# => [(0, 1), (1, 4), (2, 7), (3, 10)]

# note the index is the position IN THE SAMPLE, not the original.
# for original positions:
[(i, xs[i]) for i in range(0, len(xs), 3)]
# => [(0, 1), (3, 4), (6, 7), (9, 10)]

# ============================================
# Reverse stride — negative step

xs[::-1]                                # => [10, 9, ..., 1]    every element
xs[::-2]                                # => [10, 8, 6, 4, 2]   every 2nd, backwards
xs[8::-2]                               # => [9, 7, 5, 3, 1]    from index 8 backwards

# With a negative step, `start` is on the RIGHT and defaults to the end.
# This is where slice intuition breaks; test it rather than reasoning about it.

# ============================================
# Striding a range — no list is ever built

list(range(0, 10, 3))                   # => [0, 3, 6, 9]
list(range(10, 0, -3))                  # => [10, 7, 4, 1]

# range IS a strided traversal object. len() and `in` work on it in O(1).

# ============================================
# Striding an ITERATOR — islice, lazy, no copy

list(islice(iter(xs), 0, None, 3))      # => [1, 4, 7, 10]

# islice cannot take a negative step. Backwards + lazy don't mix.

# sample an infinite / huge stream
from itertools import count
list(islice(count(), 0, 20, 5))         # => [0, 5, 10, 15]

# sample every 1000th line of a file, holding one line in memory:
# with open("huge.log") as f:
#     for line in islice(f, 0, None, 1000):
#         ...

# ============================================
# The cost difference that matters

# xs[::1000]                → builds a copy of the SELECTED elements,
#                             but must have the whole list in memory first
# islice(stream, 0, None, 1000) → never holds more than one element

# ============================================
# Stride by a mask instead of a number (irregular sampling)

mask = cycle([1, 0, 0])                 # keep 1 of every 3
list(compress(xs, mask))                # => [1, 4, 7, 10]

# compress generalizes stride: any boolean pattern, not just periodic.

# ============================================
# Downsample a signal

signal = [0, 1, 4, 9, 16, 25, 36, 49]
signal[::2]                             # => [0, 4, 16, 36]      pick one
[max(signal[i:i+2]) for i in range(0, len(signal), 2)]
# => [1, 9, 25, 49]                     peak-preserving

# Plain striding DISCARDS the skipped values. If a spike can live in a
# discarded slot, aggregate the block instead of sampling it.

# ============================================
# Stride with windows — the Jump Window pattern, for contrast

[xs[i:i+3] for i in range(0, len(xs) - 3 + 1, 2)]
# => [[1,2,3], [3,4,5], [5,6,7], [7,8,9]]

# Stride traversal gives ELEMENTS; jump window gives GROUPS.

# ============================================
# Deinterleave — k strides with k phase offsets

woven = ['r','g','b','r','g','b']
[woven[i::3] for i in range(3)]
# => [['r', 'r'], ['g', 'g'], ['b', 'b']]

# ============================================
# Strided assignment — slices work on the left too

ys = [0] * 10
ys[::2] = [1, 1, 1, 1, 1]
ys                                      # => [1,0,1,0,1,0,1,0,1,0]

# the right side must match the slice length EXACTLY for an extended slice
# (unlike xs[2:5] = [...], which can resize the list)

# ============================================
# Compare

xs[::3]                                 # every 3rd ELEMENT   → Stride
list(islice(it, 0, None, 3))            # same, lazily        → Stride
[xs[i:i+3] for i in range(0,len(xs),3)] # groups of 3         → Chunk
[xs[i:i+3] for i in range(0,len(xs),2)] # groups, step 2      → Jump Window
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|every nth|`xs[::n]`|
|every nth, offset j|`xs[j::n]`|
|every nth, backwards|`xs[::-n]`|
|every nth, lazily|`islice(it, 0, None, n)`|
|every nth number|`range(0, stop, n)`|
|original indices too|`range(0, len(xs), n)`|
|an irregular pattern|`compress(xs, cycle(mask))`|
|groups, not elements|see Jump Window|

---

### Key Insight

**Stride is the third slice argument — that's the whole pattern.** `xs[::n]` needs no import, no helper, no loop, and reads as "every n-th". The only reason to write anything longer is when you need the *original index* (use `range(0, len(xs), n)`) or when the source is a stream (use `islice`).

The thing to stay honest about: **striding throws data away by design.** Downsampling a signal with `xs[::4]` doesn't average four samples, it keeps one and discards three — so a spike that lands in a discarded slot vanishes silently. When the skipped values could matter, you don't want stride traversal at all; you want a chunk plus an aggregate.
