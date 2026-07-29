# Sequence Processing — Verb 3: Search

## Introduction

You have a sequence and you've had a look at it. Next you want to **find something in it**.

**Search** means locating the element or elements that match some condition.

The question you're asking:

> **"Where is what I'm looking for?"**

**Observe** tells you about the sequence as a whole. **Search** zooms in on particular elements or positions inside it.

---

# Search → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Search**|Where is what I'm looking for?|`next((x for x in xs if p(x)), None)`, `list.index`, `enumerate`, `in`, `dict.get`, `str.find`, `re.search`, `bisect`|

> **Note:** There's no one generic "find" in Python. What you reach for depends on what you want back — the **element**, its **index**, a **yes/no**, or a **value for a key** — and on whether the data is already sorted.

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

**`next()` with no default raises `StopIteration`**, and inside a generator function that turns into a baffling `RuntimeError`. Always pass the second argument.

**`.index()` raises `ValueError`, `.find()` returns `-1`, `.get()` returns `None`.** Three different ways of saying "not found", all in the same standard library.

**Watch for the nested-search trap.** One `next()` scan is O(n) and perfectly fine. Put that same scan inside a loop over n keys and it's O(n²), and it never looks wrong on the page. Build a `dict` index once instead.

---

# One Sentence to Remember

> **Search finds the elements or positions in a sequence that match a condition. If you're searching the same collection over and over, stop searching and build an index.**
