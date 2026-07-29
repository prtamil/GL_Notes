# Sequence Processing — Verb 2: Observe

## Introduction

Once you have a sequence, the first thing you do is **look at it**.

Before you change, filter, sort or group anything, you ask a few questions about what you're holding.

**Observe** is pulling information out of a sequence **without touching the sequence**.

The question you're asking:

> **"What is true about this sequence?"**

Observe is the read-only verb. It doesn't build a new sequence and it doesn't modify the old one. It just tells you something.

---

# Observe → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Observe**|What is true about the sequence?|`len`, `xs[0]`, `xs[-1]`, `not xs`, `any`, `all`, `in`, `min`, `max`, `sum`, `collections.Counter`, `statistics`|

> **Note:** This is where **laziness bites you**. `len()`, indexing and `xs[-1]` all need a real sequence, and a generator gives you none of them. Worse, `any`/`all`/`min`/`max` **consume** the generator, so if you ask a second question about it you get an answer based on nothing.

---

# Common Observation Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Count elements|`len`|`len([10, 20, 30])` → `3`|
|First element|`xs[0]`|`[10, 20, 30][0]` → `10`|
|Last element|`xs[-1]`|`[10, 20, 30][-1]` → `30`|
|Is empty?|`not xs`|`not []` → `True`|
|Any match?|`any`|`any(x % 2 == 0 for x in [1, 3, 4])` → `True`|
|All match?|`all`|`all(x % 2 == 0 for x in [2, 4, 6])` → `True`|
|None match?|`not any`|`not any(x < 0 for x in [1, 2, 3])` → `True`|
|Contains a value|`in`|`3 in [1, 2, 3]` → `True`|
|Count occurrences|`Counter`|`Counter("aba")` → `Counter({'a': 2, 'b': 1})`|
|Smallest value|`min`|`min([8, 3, 5])` → `3`|
|Largest value|`max`|`max([8, 3, 5])` → `8`|
|Average|`statistics.mean`|`mean([1, 2, 3])` → `2`|

---

# The Python-specific catches

**`any`/`all` short-circuit. `min`/`max`/`sum` don't.** A question about existence can stop the moment it knows. A question about a total has to see everything.

**`all([])` is `True`.** Nothing failed, so it passes. `any([])` is `False`. Everyone gets caught by this once.

**`min`/`max` raise `ValueError` on empty input** unless you give them `default=`.

**`in` is O(1) on a `set` or `dict` and O(n) on a `list`.** Same syntax, wildly different cost.

---

# One Sentence to Remember

> **Observe answers questions about a sequence without changing it. Just remember that on a lazy iterator, asking the question is what consumes it.**
