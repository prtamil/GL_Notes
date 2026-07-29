# Sequence Processing — Verb 8: Slice

## Introduction

Sometimes we don't need the entire sequence—we only need **a portion of it**.

**Slice** is the act of extracting a contiguous part of a sequence based on position or a stopping condition.

The mental question is:

> **"Which part of the sequence do I need?"**

Unlike **Select**, which keeps elements based on a predicate regardless of position, **Slice** focuses on taking or removing **contiguous regions** of a sequence.

---

# Slice → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Slice**|Which part of the sequence do I need?|`xs[a:b:step]`, `itertools.islice`, `takewhile`, `dropwhile`, `collections.deque(maxlen=n)`|

> **Note:** Slicing is **the** Python idiom, and it never raises: out-of-range bounds are clamped silently. `islice` is the slicing you use on an iterator — but it cannot take negative indices, because a stream has no known end.

---

# Common Slice Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Take first _N_ elements|`xs[:n]`|`[1,2,3,4,5][:3]` → `[1, 2, 3]`|
|Drop first _N_ elements|`xs[n:]`|`[1,2,3,4,5][3:]` → `[4, 5]`|
|Take last _N_ elements|`xs[-n:]`|`[1,2,3,4,5][-2:]` → `[4, 5]`|
|Drop last _N_ elements|`xs[:-n]`|`[1,2,3,4,5][:-2]` → `[1, 2, 3]`|
|Every _N_th element|`xs[::n]`|`[1,2,3,4,5][::2]` → `[1, 3, 5]`|
|Reverse|`xs[::-1]`|`[1,2,3][::-1]` → `[3, 2, 1]`|
|Take while a condition holds|`takewhile`|`list(takewhile(lambda x: x > 0, [3,2,1,0,-1]))` → `[3, 2, 1]`|
|Drop while a condition holds|`dropwhile`|`list(dropwhile(lambda x: x > 0, [3,2,1,0,-1]))` → `[0, -1]`|
|Split at a position|two slices|`xs[:3], xs[3:]` → `([1,2,3], [4,5])`|
|Slice a lazy iterator|`islice`|`list(islice(count(), 2, 6))` → `[2, 3, 4, 5]`|
|Keep only the last _N_ of a stream|`deque(maxlen=n)`|`deque(stream, maxlen=10)`|

---

# The Python-specific catches

**Slices are half-open**: `xs[a:b]` includes `a`, excludes `b`, and has `b - a` elements. `xs[:n] + xs[n:] == xs` for any `n`, always.

**Slicing never raises.** `[1,2,3][10:20]` is `[]`, not an error. Convenient, and the reason an off-by-one can pass silently.

**`xs[:]` copies a list** (shallowly) — the classic idiom for "iterate over a snapshot while mutating the original".

**Slicing a list is O(k) and copies**; slicing a `range` returns another lazy `range`; `islice` copies nothing but must consume from the start.

---

# One Sentence to Remember

> **Slice extracts a contiguous portion of a sequence based on position or a boundary condition.**
