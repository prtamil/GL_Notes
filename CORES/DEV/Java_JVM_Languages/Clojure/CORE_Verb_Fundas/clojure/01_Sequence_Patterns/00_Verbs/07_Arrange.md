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

> **Note:** `sort` orders values naturally, `sort-by` orders using a key function, `reverse` flips the order, `shuffle` randomizes the order, and `rseq` efficiently traverses reversible collections in reverse.

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

# One Sentence to Remember

> **Arrange creates a new view of a sequence by changing the order of its elements without changing the elements themselves.**