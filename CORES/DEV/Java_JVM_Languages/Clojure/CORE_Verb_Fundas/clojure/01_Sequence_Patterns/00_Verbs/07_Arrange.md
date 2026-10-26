# Sequence Processing — Verb 7: Arrange

## Introduction

Sometimes the elements are correct, but their **order** is not.

**Arrange** is the act of reorganizing the elements of a sequence without changing the elements themselves.

The mental question is:

> **"How should these elements be arranged?"**

Unlike **Transform**, which changes the values, **Arrange** changes only their position or ordering.

---

# Arrange → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Arrange**|How should these elements be arranged?|`sort`, `sort-by`, `reverse`, `shuffle`, `rseq`|

> **Note:** `sort` uses natural order. `sort-by` uses a key. `reverse` flips the order. `shuffle` randomizes it. `rseq` traverses reversible collections backward.

---

# Common Arrangement Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Sort ascending|`sort`|`(sort [4 1 3 2])` → `(1 2 3 4)`|
|Sort by property|`sort-by`|`(sort-by count ["cat" "elephant" "dog"])` → `("cat" "dog" "elephant")`|
|Reverse order|`reverse`|`(reverse [1 2 3])` → `(3 2 1)`|
|Randomize order|`shuffle`|`(shuffle [1 2 3 4])` → e.g. `(3 1 4 2)`|
|Reverse traversal (vector)|`rseq`|`(rseq [1 2 3])` → `(3 2 1)`|

---

# The Clojure-specific catches

**`sort` and `sort-by` are eager.** They realize the complete collection. Do not use them with an infinite sequence.

**`sort-by` calls the key function during every comparison**, not once per element, so an expensive key is computed O(n log n) times. Precompute it — `(map second (sort-by first (map (juxt keyfn identity) xs)))` — when the key costs real work.

**Sorting mixed types throws.** `(sort [1 "a"])` causes a `ClassCastException`. The default comparator does not order different types.

**Both are stable**, so equal elements keep their original relative order and you can sort by successive keys to get a compound ordering.

**`reverse` is eager and O(n). `rseq` is O(1).** Use `rseq` only with vectors and sorted collections.

---

# One Sentence to Remember

> **Arrange creates a new view of a sequence by changing the order of its elements without changing the elements themselves.**
