# Sequence Processing — Verb 13: Compress

## Introduction

Sometimes a sequence contains **redundant, repeated, or unnecessary information**.

**Compress** is the act of reducing the size or complexity of a sequence while preserving the information that matters.

The mental question is:

> **"How can I make this sequence smaller?"**

Unlike **Reject**, which removes elements based on a rule, **Compress** removes redundancy or simplifies the representation of the sequence.

---

# Compress → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Compress**|How can I make this sequence smaller?|`dict.fromkeys`, `set`, `itertools.groupby`, `collections.Counter`, `deque(maxlen=n)`|

> **Note:** `set(xs)` removes all duplicates but **loses order**; `list(dict.fromkeys(xs))` removes all duplicates and **keeps first-seen order**. `groupby` removes only **adjacent** duplicates and needs no memory at all.

---

# Common Compression Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Remove duplicate values (ordered)|`dict.fromkeys`|`list(dict.fromkeys([1,2,1,3,2]))` → `[1, 2, 3]`|
|Remove duplicate values (unordered)|`set`|`set([1,2,1,3,2])` → `{1, 2, 3}`|
|Remove consecutive duplicates|`groupby`|`[k for k,_ in groupby([1,1,2,2,2,3,1])]` → `[1, 2, 3, 1]`|
|Compress into runs|`groupby`|`[list(g) for _,g in groupby([1,3,2,4,5], key=lambda n: n%2)]` → `[[1,3],[2,4],[5]]`|
|Run-length encode|`groupby`|`[(k, len(list(g))) for k,g in groupby("aab")]` → `[('a',2), ('b',1)]`|
|Replace values with counts|`Counter`|`Counter([1,2,1])` → `Counter({1: 2, 2: 1})`|
|Keep only the last _N_|`deque(maxlen=n)`|`deque([1,2,3,4], maxlen=2)` → `deque([3, 4])`|
|Unique matches only|set comprehension|`{x for x in [2,4,2,6] if x % 2 == 0}` → `{2, 4, 6}`|

---

# The Python-specific catches

**`set` and `dict.fromkeys` need hashable elements** — a list of lists won't dedupe this way. `groupby` compares with `==` and works on anything.

**Distinct is O(n) memory; dedupe is O(1).** `dict.fromkeys` holds every value seen; `groupby` only compares each element to its predecessor, so it runs on an infinite stream.

**Sorting turns dedupe into distinct.** `[k for k,_ in groupby(sorted(xs))]` and `sorted(set(xs))` give the same answer by opposite trade-offs — one spends time, the other memory.

---

# One Sentence to Remember

> **Compress reduces redundancy in a sequence while preserving its essential information.**
