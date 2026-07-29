# Sequence Processing — Verb 16: Scan

## Introduction

Sometimes we don't just want the final answer—we want to see **how the answer evolves at every step**.

**Scan** is the act of producing every intermediate result while traversing a sequence.

The mental question is:

> **"What do I know after each step?"**

Unlike **Accumulate**, which returns only the final result, **Scan** returns the entire history of intermediate states.

---

# Scan → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Scan**|What do I know after each step?|`reductions`|

> **Note:** `reductions` is to `reduce` what a journey is to the destination—it returns every intermediate accumulation instead of only the final one.

---

# Common Scan Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Running sum|`(reductions + [1 2 3 4])`|`(1 3 6 10)`|
|Running product|`(reductions * [2 3 4])`|`(2 6 24)`|
|Running maximum|`(reductions max [3 1 5 2])`|`(3 3 5 5)`|
|Running minimum|`(reductions min [3 1 5 2])`|`(3 1 1 1)`|

---

# One Sentence to Remember

> **Scan produces every intermediate result while processing a sequence.**