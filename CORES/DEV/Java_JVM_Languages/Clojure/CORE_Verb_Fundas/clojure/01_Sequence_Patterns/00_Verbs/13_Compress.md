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

# The Clojure-specific catches

**`distinct` and `dedupe` are different operations.** `distinct` removes every repeat anywhere — `(distinct [1 1 2 1])` is `(1 2)`. `dedupe` collapses only *consecutive* runs — `(dedupe [1 1 2 1])` is `(1 2 1)`. Reaching for the wrong one on unsorted data is the classic bug.

**`distinct` retains every value that it sees.** Its memory use grows with the number of different values. It cannot complete for infinite unique input.

**`set` does not preserve order. `distinct` preserves first appearance order.** Select the function from the required result.

**`dedupe` and `distinct` have transducer arities.** Use them when compression is one step in a data pipeline.

---

# One Sentence to Remember

> **Compress reduces redundancy in a sequence while preserving its essential information.**
