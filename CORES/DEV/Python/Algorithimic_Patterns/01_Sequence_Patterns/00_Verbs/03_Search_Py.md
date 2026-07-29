# Sequence Processing — Verb 3: Search

## Introduction

Once a sequence exists and we have observed it, the next natural action is to **find something**.

**Search** is the act of locating one or more elements in a sequence that satisfy a condition.

The mental question is:

> **"Where is what I'm looking for?"**

Unlike **Observe**, which describes the sequence as a whole, **Search** focuses on finding specific elements or positions within the sequence.

---

# Search → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Search**|Where is what I'm looking for?|`next((x for x in xs if p(x)), None)`, `list.index`, `enumerate`, `in`, `dict.get`, `str.find`, `re.search`, `bisect`|

> **Note:** Python has no single generic "find" function. The right tool depends on whether you want the **element**, its **index**, a **boolean**, or a **lookup by key** — and on whether the data is sorted.

---

# Common Search Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Find first matching element|`next((x for x in xs if p(x)), None)`|`next((x for x in [1,3,4,5] if x % 2 == 0), None)` → `4`|
|Find all matching elements|comprehension|`[x for x in [1,2,3,4] if x % 2 == 0]` → `[2, 4]`|
|Find first transformed match|generator + `next`|`next((x*10 for x in [1,2,3] if x % 2 == 0), None)` → `20`|
|Find matching indices|`enumerate`|`[i for i, x in enumerate([1,2,3,4]) if x % 2 == 0]` → `[1, 3]`|
|Find the index of a value|`list.index`|`[10, 20, 30].index(20)` → `1` (raises if absent)|
|Look up by key|`dict.get`|`{"a": 1}.get("b")` → `None`|
|Check membership|`in`|`2 in {1, 2, 3}` → `True`|
|Find a substring|`str.find`|`"error: x".find("x")` → `7` (`-1` if absent)|
|Search sorted data|`bisect_left`|`bisect_left([10,20,30], 20)` → `1`|

---

# The Python-specific catches

**`next()` without a default raises `StopIteration`** — and inside a generator function that becomes a confusing `RuntimeError`. Always pass the second argument.

**`.index()` raises `ValueError`; `.find()` returns `-1`; `.get()` returns `None`.** Three different "not found" conventions in the same standard library.

**The nested-search trap:** one `next()` scan is O(n) and fine. The same scan inside a loop over n keys is O(n²) and never looks like a mistake. Build a `dict` index once instead.

---

# One Sentence to Remember

> **Search locates specific elements or positions in a sequence that satisfy a condition — and if you're searching the same collection repeatedly, stop searching and build an index.**
