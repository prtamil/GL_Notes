# Sequence Processing — Verb 14: Group

## Introduction

Sometimes the most natural way to understand a sequence is to **organize similar elements together**.

**Group** is the act of partitioning a sequence into collections based on a shared property or key.

The mental question is:

> **"Which elements belong together?"**

Unlike **Split**, which divides a sequence by position or boundaries, **Group** organizes elements by their characteristics.

---

# Group → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Group**|Which elements belong together?|`group-by`, `frequencies`, `partition-by`|

> **Note:** `group-by` is the primary grouping function. `frequencies` is a specialized form of grouping that counts occurrences, while `partition-by` groups only consecutive elements with the same key.

---

# Common Grouping Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Group by key|`group-by`|`(group-by odd? [1 2 3 4 5])` → `{true [1 3 5], false [2 4]}`|
|Count groups|`frequencies`|`(frequencies [:a :b :a :c])` → `{:a 2 :b 1 :c 1}`|
|Group consecutive elements|`partition-by`|`(partition-by odd? [1 3 2 4 5 7])` → `((1 3) (2 4) (5 7))`|
|Group by computed value|`group-by`|`(group-by count ["cat" "dog" "apple"])` → `{3 ["cat" "dog"], 5 ["apple"]}`|

---

# One Sentence to Remember

> **Group organizes a sequence into collections whose elements share a common property or key.**