# Sequence Processing — Verb 9: Split

## Introduction

Sometimes a sequence is easier to work with after it has been **divided into meaningful pieces**.

**Split** is the act of dividing one sequence into two or more sequences based on a position, condition, delimiter, or grouping rule.

The mental question is:

> **"How should I divide this sequence?"**

Unlike **Slice**, which extracts one portion, **Split** separates the original sequence into multiple parts.

---

# Split → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Split**|How should I divide this sequence?|`split-at`, `split-with`, `partition`, `partition-all`, `partition-by`|

> **Note:** `split-at` and `split-with` produce two parts, while the `partition` family divides a sequence into many parts.

---

# Common Split Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Split at a position|`split-at`|`(split-at 3 [1 2 3 4 5])` → `[(1 2 3) (4 5)]`|
|Split by condition|`split-with`|`(split-with pos? [3 2 1 0 -1])` → `[(3 2 1) (0 -1)]`|
|Split into equal-sized chunks|`partition`|`(partition 2 [1 2 3 4])` → `((1 2) (3 4))`|
|Split into chunks (allow incomplete last)|`partition-all`|`(partition-all 2 [1 2 3 4 5])` → `((1 2) (3 4) (5))`|
|Split whenever key changes|`partition-by`|`(partition-by odd? [1 3 2 4 5 7])` → `((1 3) (2 4) (5 7))`|

---

# One Sentence to Remember

> **Split divides one sequence into multiple meaningful sequences.**