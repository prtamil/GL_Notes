# Sequence Processing — Verb 6: Transform

## Introduction

Once we have the right elements, we often need to **change** them.

**Transform** is the act of converting each element of a sequence into another value while preserving the overall structure of the sequence.

The mental question is:

> **"How should each element change?"**

Unlike **Select** and **Reject**, which decide _which_ elements remain, **Transform** changes _what_ each element becomes.

---

# Transform → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Transform**|How should each element change?|`[f(x) for x in xs]`, `map`, `enumerate`, `starmap`, dict/set comprehensions, `str.translate`|

> **Note:** `map(f, xs)` and `[f(x) for x in xs]` do the same thing. The comprehension wins whenever the transform is an expression rather than an existing function; `map` wins for `map(str.strip, lines)` and friends.

---

# Common Transformation Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Transform every element|comprehension|`[x + 1 for x in [1,2,3]]` → `[2, 3, 4]`|
|Transform with a named function|`map`|`list(map(str.upper, ["a","b"]))` → `['A', 'B']`|
|Transform using the index|`enumerate`|`list(enumerate("abc"))` → `[(0,'a'), (1,'b'), (2,'c')]`|
|Transform two sequences together|`map` / `zip`|`list(map(add, [1,2], [10,20]))` → `[11, 22]`|
|Unpack tuples into a function|`starmap`|`list(starmap(pow, [(2,3), (3,2)]))` → `[8, 9]`|
|Replace specific values|dict lookup|`[m.get(x, x) for x in [1,2,3]]` with `m = {2: "two"}` → `[1, 'two', 3]`|
|Transform dict values|dict comprehension|`{k: v*2 for k, v in d.items()}`|
|Transform a set|set comprehension|`{len(w) for w in words}`|
|Transform characters|`str.translate`|`s.translate(str.maketrans("abc", "xyz"))`|

---

# The Python-specific catches

**`map` is lazy and one-shot.** `m = map(f, xs)` then `list(m)` twice gives you the values once and `[]` the second time.

**`map` with multiple iterables stops at the shortest**, exactly like `zip`.

**Transform preserves length; it never filters.** If your transform returns `None` for some inputs, you have a Select hiding inside a Transform — write the `if` explicitly.

---

# One Sentence to Remember

> **Transform creates a new sequence by changing each element according to a rule while preserving the sequence structure.**
