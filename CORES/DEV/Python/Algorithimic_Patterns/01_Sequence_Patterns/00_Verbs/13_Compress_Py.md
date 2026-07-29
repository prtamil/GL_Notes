# Sequence Processing — Verb 13: Compress

## Introduction

Plenty of sequences carry **repeated or redundant junk** you don't need.

**Compress** shrinks a sequence, or simplifies it, without losing the information that matters.

The question you're asking:

> **"How can I make this sequence smaller?"**

**Reject** drops elements that fail a rule. **Compress** goes after redundancy instead, or finds a tighter way to say the same thing.

---

# Compress → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Compress**|How can I make this sequence smaller?|`dict.fromkeys`, `set`, `itertools.groupby`, `collections.Counter`, `deque(maxlen=n)`|

> **Note:** `set(xs)` kills every duplicate but **throws away the order**. `list(dict.fromkeys(xs))` kills every duplicate and **keeps first-seen order**. `groupby` only collapses **adjacent** duplicates, and it needs no memory at all to do it.

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

**`set` and `dict.fromkeys` need hashable elements.** A list of lists won't dedupe this way. `groupby` just compares with `==`, so it works on anything.

**Distinct costs O(n) memory. Dedupe costs O(1).** `dict.fromkeys` remembers every value it has seen. `groupby` only ever compares an element to the one before it, which is why it can run on an infinite stream.

**Sort first and dedupe becomes distinct.** `[k for k,_ in groupby(sorted(xs))]` and `sorted(set(xs))` land on the same answer through opposite trade-offs: one spends time, the other spends memory.

---

# One Sentence to Remember

> **Compress strips the redundancy out of a sequence and keeps what actually matters.**
