# Pattern 1 — Chunk (Fixed-Size Blocks)

## Mental Model

Cut a sequence into **fixed-size, non-overlapping blocks**. Each element belongs to **exactly one** chunk.

Chunking is the degenerate case of a window where **step size == window size**: the window never revisits an element.

---

## Relationship to Cognitive Verb

```text
Window
   ↓
Chunk
```

Chunk is a **Window** pattern where the window advances by **its own width**, so consecutive windows never share elements.

---

## Python Functions & Common Variations

|Variation|Example|Common Python|
|---|---|---|
|Chunk of 3 (drop partial tail)|`(1 2 3) (4 5 6)`|`zip(*[iter(xs)] * 3)`|
|Chunk of 3 (keep partial tail)|`(1 2 3) (4 5)`|`itertools.batched(xs, 3)` (3.12+)|
|Chunk by slicing|indexable input|`[xs[i:i+n] for i in range(0, len(xs), n)]`|
|Pad the last chunk|`(4 5 _)`|`itertools.zip_longest(*[iter(xs)] * n, fillvalue=0)`|
|Chunk a lazy stream|generators, files|`itertools.islice` in a loop|
|Chunk a string|`"abcdef"` → `"abc" "def"`|slicing, `textwrap.wrap`|

---

## Common Uses

- Batching API / DB writes

- Pagination

- Fixed-width record parsing

- Memory-bounded stream processing

- Splitting work across workers

- Building grid rows from a flat list

- Byte-block / packet framing

- Mini-batches in ML training

---

## Hidden Interview Problems

- Split an array into groups of K

- Reshape a flat list into a matrix

- Batch requests with a size limit

- Chunk a string every N characters

- Average of every K elements

- Reverse each group of K in a linked list

- Distribute items round-robin across N buckets

---

## Recognition Clues

If you hear:

- Groups of **K**

- Batches of **N**

- Pages of size **N**

- Blocks

- Non-overlapping

- Split evenly

- Every N items at a time

Think:

**→ Chunk**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Window|
|Pattern|Chunk|
|Overlap|No|
|Window Size|Fixed (`n`)|
|Step Size|`n` (same as window)|
|Preserves Order|Yes|
|Covers All Elements|Yes with `batched` / slicing, No with `zip(*[iter()]*n)`|

---

## Python Recipe Book

```python
# ============================================
# Setup

from itertools import batched, islice, zip_longest   # batched: 3.12+

xs = [1, 2, 3, 4, 5, 6, 7, 8]

# ============================================
# Chunk, keeping the partial tail — the modern default

list(batched(xs, 3))
# => [(1, 2, 3), (4, 5, 6), (7, 8)]

# ============================================
# Chunk by slicing — works on any list/string, keeps the tail

[xs[i:i + 3] for i in range(0, len(xs), 3)]
# => [[1, 2, 3], [4, 5, 6], [7, 8]]

# needs len(), so it does NOT work on a generator

# ============================================
# The grouper idiom — drops the partial tail

list(zip(*[iter(xs)] * 3))
# => [(1, 2, 3), (4, 5, 6)]      # 7, 8 are silently dropped

# Why it works: [iter(xs)] * 3 is the SAME iterator three times,
# so zip pulls 1,2,3 then 4,5,6 from one shared cursor.

# ============================================
# Pad the last chunk instead of dropping it

list(zip_longest(*[iter(xs)] * 3, fillvalue=0))
# => [(1, 2, 3), (4, 5, 6), (7, 8, 0)]

# ============================================
# Chunk a lazy stream (no len(), possibly infinite)

def chunks(it, n):
    it = iter(it)
    while chunk := list(islice(it, n)):
        yield chunk

list(chunks(iter(xs), 3))
# => [[1, 2, 3], [4, 5, 6], [7, 8]]

# ============================================
# Aggregate per chunk

[sum(c) for c in batched(xs, 3)]        # => [6, 15, 15]
[max(c) for c in batched(xs, 3)]        # => [3, 6, 8]

# average of every K elements
[sum(c) / len(c) for c in batched(xs, 3)]   # => [2.0, 5.0, 7.5]

# ============================================
# Reshape a flat list into a matrix

flat = [1, 2, 3, 4, 5, 6]
[list(r) for r in batched(flat, 3)]
# => [[1, 2, 3], [4, 5, 6]]

# ============================================
# Chunk a string

s = "abcdefgh"
["".join(c) for c in batched(s, 3)]     # => ['abc', 'def', 'gh']
[s[i:i + 3] for i in range(0, len(s), 3)]   # same, simpler for strings

# ============================================
# Batch side effects (the real-world use)

for batch in batched(range(1000), 100):
    ...  # write_to_db(batch) — 10 calls instead of 1000

# ============================================
# Chunk vs Sliding Window — the one-line difference

list(batched(xs, 3))                                  # step 3 → no overlap
[tuple(xs[i:i + 3]) for i in range(len(xs) - 2)]      # step 1 → overlap

# ============================================
# Round-robin distribution (chunk's cousin)

buckets = [xs[i::3] for i in range(3)]
# => [[1, 4, 7], [2, 5, 8], [3, 6]]
# note: [i::n] takes every nth, [i:i+n] takes n in a row
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|blocks of n, keep tail|`batched(xs, n)`|
|blocks of n, drop tail|`zip(*[iter(xs)] * n)`|
|blocks of n, pad tail|`zip_longest(*[iter(xs)] * n, fillvalue=…)`|
|blocks from a list|`[xs[i:i+n] for i in range(0, len(xs), n)]`|
|blocks from a stream|`islice` in a `while` loop|
|one number per block|`[sum(c) for c in batched(xs, n)]`|
|every nth item (not a block)|`xs[::n]`|

---

### Key Insight

**Chunk and Sliding Window are the same operation with a different step.** Window size `n` with step `n` gives you disjoint chunks; step `1` gives you overlapping windows. Everything between them is a Jump Window.

The only real decision in Python is **what happens to the leftover tail** — `batched` keeps it, the `zip(*[iter()]*n)` grouper drops it, and `zip_longest` pads it. Pick deliberately; a silently dropped tail is the classic chunking bug.
