# Sequence Processing — Verb 8: Slice

## Introduction

Often you don't want the whole sequence. You want **a stretch of it**.

**Slice** pulls out a contiguous run, chosen by position or by where some condition stops holding.

The question you're asking:

> **"Which part of the sequence do I need?"**

**Select** picks elements by a test, wherever they happen to sit. **Slice** works on **contiguous regions** instead.

---

# Slice → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Slice**|Which part of the sequence do I need?|`xs[a:b:step]`, `itertools.islice`, `takewhile`, `dropwhile`, `collections.deque(maxlen=n)`|

> **Note:** Slicing is **the** Python idiom, and it never raises. Bounds past the end get clamped without a word. For iterators you use `islice` instead, and it won't take negative indices, because a stream doesn't know where it ends.

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

**Slices are half-open.** `xs[a:b]` takes `a`, stops before `b`, and gives you `b - a` elements. `xs[:n] + xs[n:] == xs` for every `n`, no exceptions.

**Slicing never raises.** `[1,2,3][10:20]` is `[]`, not an error. Handy, and also why an off-by-one can slip through unnoticed.

**`xs[:]` makes a shallow copy of a list.** It's the usual trick for looping over a snapshot while you mutate the original.

**Slicing a list is O(k) and copies.** Slicing a `range` hands back another lazy `range`. `islice` copies nothing, but it has to consume from the start to get anywhere.

---

# One Sentence to Remember

> **Slice pulls out a contiguous chunk of a sequence, picked by position or by where a condition stops holding.**
