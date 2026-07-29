# Sequence Processing — Verb 15: Order

## Introduction

Some problems depend not only on **which elements** exist, but also on **the sequence in which they are processed**.

**Order** is the act of establishing or preserving a meaningful processing order for a sequence.

The mental question is:

> **"In what sequence should these elements be processed?"**

Unlike **Arrange**, which physically reorders a collection, **Order** is about the logical sequence of processing or traversal.

---

# Order → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Order**|In what sequence should these elements be processed?|`sort`, `sort-by`, `reverse`, `rseq`, `seq`|

> **Note:** In practice, **Order** often uses the same functions as **Arrange**. The distinction is conceptual: **Arrange** changes the layout of data, while **Order** emphasizes the sequence in which data is traversed or processed.

---

# Common Ordering Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Process in ascending order|`sort`|`(sort [4 1 3 2])` → `(1 2 3 4)`|
|Process by custom key|`sort-by`|`(sort-by :age people)` → ordered by `:age`|
|Process in reverse order|`reverse`|`(reverse [1 2 3])` → `(3 2 1)`|
|Reverse traversal of vector|`rseq`|`(rseq [1 2 3])` → `(3 2 1)`|
|Obtain a sequence for traversal|`seq`|`(seq [1 2 3])` → `(1 2 3)`|

---

# One Sentence to Remember

> **Order determines the logical sequence in which elements are processed.**