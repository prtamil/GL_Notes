# Sequence Processing — Verb 4: Select

## Introduction

Once you've found things, you usually want to **keep** only the ones that matter.

**Select** builds a new sequence out of the elements that pass some rule.

The question you're asking:

> **"What should I keep?"**

**Search** points at elements. **Select** hands you a **new sequence** made of the ones you wanted.

---

# Select → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Select**|What should I keep?|`[x for x in xs if p(x)]`, `filter`, `itertools.takewhile`, `islice`, slicing, `itertools.compress`|

> **Note:** Default to the comprehension. `filter(p, xs)` is lazy and reads nicely when `p` already has a name. `filter(None, xs)` is the special case that keeps every **truthy** element.

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

**`filter` gives you a one-shot iterator, not a list.** No `len`, no indexing, and it's empty after one pass.

**`filter(None, xs)` throws away `0`, `""`, `[]` and `False` too**, not just `None`. If you really mean "not None", write `if x is not None`.

**`takewhile` quits at the first failure. `filter` checks everything.** `takewhile(p, [1, -1, 2])` gives you `[1]`; `filter` gives you `[1, 2]`.

---

# One Sentence to Remember

> **Select builds a new sequence out of just the elements that pass your rule.**
