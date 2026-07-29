# Sequence Processing — Verb 2: Observe

## Introduction

Once a sequence exists, the first thing we naturally do is **look at it**.

Before changing, filtering, sorting, or grouping data, we usually ask questions about it.

**Observe** is the act of extracting information from a sequence **without changing the sequence itself**.

The mental question is:

> **"What is true about this sequence?"**

Unlike most other verbs, **Observe** is a **read-only** operation. It does not create a new sequence or modify the existing one. It simply reveals information.

---

# Observe → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Observe**|What is true about the sequence?|`len`, `xs[0]`, `xs[-1]`, `not xs`, `any`, `all`, `in`, `min`, `max`, `sum`, `collections.Counter`, `statistics`|

> **Note:** Observation is where **laziness bites**. `len()`, indexing, and `xs[-1]` all require a real sequence — a generator has none of them, and `any`/`all`/`min`/`max` **consume** it, so a second question about the same generator gets an empty answer.

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

**`any`/`all` short-circuit; `min`/`max`/`sum` do not.** Existence questions stop early, aggregate questions must see everything.

**`all([])` is `True`** — vacuously, since no element fails. `any([])` is `False`. Both surprise people exactly once.

**`min`/`max` raise `ValueError` on empty input** unless you pass `default=`.

**`in` is O(1) on a `set` or `dict`, O(n) on a `list`.** Same syntax, completely different cost.

---

# One Sentence to Remember

> **Observe answers questions about a sequence without changing the sequence itself — but on a lazy iterator, asking is itself a consumption.**
