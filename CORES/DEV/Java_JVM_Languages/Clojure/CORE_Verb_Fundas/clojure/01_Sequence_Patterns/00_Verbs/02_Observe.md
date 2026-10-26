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

# The Clojure-specific catches

**`contains?` asks about keys, not values.** `(contains? [10 20 30] 10)` is `false` — a three-element vector has no index 10. `(contains? [10 20 30] 1)` is `true`. For "is this value present?" on a sequence use `(some #{v} coll)`, and remember sets are their own lookup function.

**`some` returns the predicate's value, not the element.** `(some even? [1 3 4])` gives `true`, not `4`. Write `(some #(when (even? %) %) coll)` when you want the element back.

**Only `nil` and `false` are falsey.** `0` and `""` are truthy, so the empty-value guards you carry over from Python quietly stop working.

**Empty collections use identity results.** `(every? pred [])` and `(not-any? pred [])` return `true`. `(some pred [])` returns `nil`. `(apply min [])` throws.

**`count` realizes all of a lazy sequence.** It is O(1) for vectors, maps, and sets. It does not return for an infinite sequence.

---

# One Sentence to Remember

> **Observe answers questions about a sequence without changing the sequence itself.**
