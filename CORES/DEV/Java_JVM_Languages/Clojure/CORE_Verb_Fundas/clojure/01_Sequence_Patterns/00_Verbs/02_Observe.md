# Sequence Processing — Verb 2: Observe

## Introduction

Once a sequence exists, the first thing we naturally do is **look at it**.

Before changing, filtering, sorting, or grouping data, we usually ask questions about it.

**Observe** is the act of extracting information from a sequence **without changing the sequence itself**.

The mental question is:

> **"What is true about this sequence?"**

Unlike most other verbs, **Observe** is a **read-only** operation. It does not create a new sequence or modify the existing one. It simply reveals information.

---

# Observe → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Observe**|What is true about the sequence?|`count`, `first`, `last`, `empty?`, `some`, `every?`, `not-any?`, `find`, `contains?`, `frequencies`, `min`, `max`, `apply`|

> **Note:** Some functions (like `contains?`) are intended for maps and indexed collections rather than checking whether a sequence contains a value. Later we'll discuss the right tool for each collection type.

---

# Common Observation Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Count elements|`count`|`(count [10 20 30])` → `3`|
|First element|`first`|`(first [10 20 30])` → `10`|
|Last element|`last`|`(last [10 20 30])` → `30`|
|Is empty?|`empty?`|`(empty? [])` → `true`|
|Any match?|`some`|`(some even? [1 3 4])` → `true` (truthy)|
|All match?|`every?`|`(every? even? [2 4 6])` → `true`|
|None match?|`not-any?`|`(not-any? neg? [1 2 3])` → `true`|
|Count occurrences|`frequencies`|`(frequencies [:a :b :a])` → `{:a 2 :b 1}`|
|Smallest value|`apply min`|`(apply min [8 3 5])` → `3`|
|Largest value|`apply max`|`(apply max [8 3 5])` → `8`|

---

# One Sentence to Remember

> **Observe answers questions about a sequence without changing the sequence itself.**