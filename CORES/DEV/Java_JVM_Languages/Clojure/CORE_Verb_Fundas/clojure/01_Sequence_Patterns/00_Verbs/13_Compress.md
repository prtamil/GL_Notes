# Sequence Processing — Verb 13: Compress

## Introduction

Sometimes a sequence contains **redundant, repeated, or unnecessary information**.

**Compress** is the act of reducing the size or complexity of a sequence while preserving the information that matters.

The mental question is:

> **"How can I make this sequence smaller?"**

Unlike **Reject**, which removes elements based on a rule, **Compress** removes redundancy or simplifies the representation of the sequence.

---

# Compress → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Compress**|How can I make this sequence smaller?|`distinct`, `dedupe`, `partition-by`, `filter`|

> **Note:** `distinct` removes duplicate values, `dedupe` removes only consecutive duplicates, and `partition-by` compresses runs of similar elements into groups.

---

# Common Compression Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Remove duplicate values|`distinct`|`(distinct [1 2 1 3 2])` → `(1 2 3)`|
|Remove consecutive duplicates|`dedupe`|`(dedupe [1 1 2 2 2 3 1])` → `(1 2 3 1)`|
|Compress into runs|`partition-by`|`(partition-by odd? [1 3 2 4 5 7])` → `((1 3) (2 4) (5 7))`|
|Keep only unique matches|`filter` + `distinct`|`(distinct (filter even? [2 4 2 6]))` → `(2 4 6)`|

---

# One Sentence to Remember

> **Compress reduces redundancy in a sequence while preserving its essential information.**