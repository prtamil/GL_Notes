# Sequence Processing — Verb 5: Reject

## Introduction

Sometimes it is easier to think about **what should be removed** rather than what should be kept.

**Reject** is the act of creating a new sequence by discarding elements that satisfy a rule or condition.

The mental question is:

> **"What should I discard?"**

Although **Reject** is the logical opposite of **Select**, it is an equally important way of thinking because many real-world problems are naturally expressed as removing unwanted data.

---

# Reject → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Reject**|What should I discard?|`remove`, `drop`, `drop-while`|

> **Note:** `remove` discards elements matching a predicate. `drop` removes a fixed number of elements, while `drop-while` removes elements until a condition becomes false.

---

# Common Rejection Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Remove matching elements|`remove`|`(remove even? [1 2 3 4])` → `(1 3)`|
|Drop first _N_ elements|`drop`|`(drop 2 [1 2 3 4 5])` → `(3 4 5)`|
|Drop while condition holds|`drop-while`|`(drop-while pos? [3 2 1 0 -1])` → `(0 -1)`|

---

# One Sentence to Remember

> **Reject creates a new sequence by discarding elements that satisfy a rule.**