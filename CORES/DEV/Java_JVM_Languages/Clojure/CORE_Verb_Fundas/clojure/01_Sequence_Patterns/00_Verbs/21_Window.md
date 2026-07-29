# Sequence Processing — Verb 21: Window

## Introduction

Sometimes looking at **one element at a time isn't enough**. The meaning comes from **neighboring elements**.

**Window** is the act of viewing a sequence through small contiguous groups of elements.

The mental question is:

> **"Which neighboring elements should I examine together?"**

Unlike **Slice**, which extracts one portion of a sequence, **Window** repeatedly moves across the sequence, producing many local views.

---

# Window → Clojure

| Thinking Verb | Mental Question                                       | Common Clojure Functions                     |
| ------------- | ----------------------------------------------------- | -------------------------------------------- |
| **Window**    | Which neighboring elements should I examine together? | `partition`, `partition-all`, `partition-by` |

> **Note:** `partition` is the primary windowing function. By changing the window size and step, you can express chunking, sliding windows, jumping windows, overlapping windows, and gapped windows.

---

# Common Window Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Chunk (non-overlapping)|`(partition 3 xs)`|`[1 2 3 4 5 6]` → `((1 2 3) (4 5 6))`|
|Sliding window|`(partition 3 1 xs)`|`[1 2 3 4 5]` → `((1 2 3) (2 3 4) (3 4 5))`|
|Jump window|`(partition 3 2 xs)`|`[1 2 3 4 5 6 7]` → `((1 2 3) (3 4 5) (5 6 7))`|
|Gapped window|`(partition 2 4 xs)`|`[1 2 3 4 5 6 7 8]` → `((1 2) (5 6))`|
|Partial window|`(partition-all 3 xs)`|`[1 2 3 4 5]` → `((1 2 3) (4 5))`|
|Logical window|`(partition-by odd? xs)`|`[1 3 2 4 5 7]` → `((1 3) (2 4) (5 7))`|

> **Note:** An **overlapping window** is simply any window where **step < window size** (for example, `(partition 5 2 xs)`). A **sliding window** is the special case where **step = 1**.

---

# One Sentence to Remember

> **Window repeatedly views neighboring elements together by moving across a sequence.**