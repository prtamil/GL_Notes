# Sequence Processing — Verb 4: Select

## Introduction

After searching, we often want to **keep** only the elements that matter.

**Select** is the act of creating a new sequence by retaining elements that satisfy a rule or condition.

The mental question is:

> **"What should I keep?"**

Unlike **Search**, which locates elements, **Select** produces a **new sequence** containing only the desired elements.

---

# Select → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Select**|What should I keep?|`[x for x in xs if p(x)]`, `filter`, `itertools.takewhile`, `islice`, slicing, `itertools.compress`|

> **Note:** The comprehension is the default. `filter(p, xs)` is lazy and reads well when `p` is already a named function; `filter(None, xs)` is the special form that keeps every **truthy** element.

---

# Common Selection Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Keep matching elements|comprehension|`[x for x in [1,2,3,4] if x % 2 == 0]` → `[2, 4]`|
|Keep matching, lazily|`filter`|`list(filter(str.isdigit, ["1","a","2"]))` → `['1', '2']`|
|Keep and transform|comprehension|`[x*10 for x in [1,2,3,4] if x % 2 == 0]` → `[20, 40]`|
|Keep first _N_ elements|slicing / `islice`|`[1,2,3,4,5][:3]` → `[1, 2, 3]`|
|Keep while a condition holds|`takewhile`|`list(takewhile(lambda x: x > 0, [3,2,1,0,-1]))` → `[3, 2, 1]`|
|Keep only truthy values|`filter(None, xs)`|`list(filter(None, ["", "a", None, "b"]))` → `['a', 'b']`|
|Keep by a parallel mask|`compress`|`list(compress("abcd", [1,0,1,0]))` → `['a', 'c']`|

---

# The Python-specific catches

**`filter` returns a one-shot iterator**, not a list — no `len`, no indexing, and empty after one pass.

**`filter(None, xs)` drops `0`, `""`, `[]`, and `False`**, not just `None`. If you mean "not None", write `if x is not None`.

**`takewhile` stops at the first failure; `filter` checks every element.** `takewhile(p, [1, -1, 2])` gives `[1]`, `filter` gives `[1, 2]`.

---

# One Sentence to Remember

> **Select creates a new sequence by keeping only the elements that satisfy a rule.**
