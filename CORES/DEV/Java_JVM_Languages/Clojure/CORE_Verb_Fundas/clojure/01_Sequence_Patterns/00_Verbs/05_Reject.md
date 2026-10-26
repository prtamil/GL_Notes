# Sequence Processing — Verb 5: Reject

## Introduction

Sometimes it is easier to think about **what should be removed** rather than what should be kept.

**Reject** is the act of creating a new sequence by discarding elements that satisfy a rule or condition.

The mental question is:

> **"What should I discard?"**

**Reject** is the logical opposite of **Select**. Many problems are easier to express as the removal of unwanted data.

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

# The Clojure-specific catches

**The "don't mutate while iterating" bug cannot happen here.** Clojure's collections are persistent, so `remove` returns a new sequence and the original is untouched. The entire class of Python `list.remove()`-inside-a-loop bugs simply does not exist — which is why this verb has no ceremony around it.

**`drop-while` only drops the *leading* run.** Once the predicate fails once, everything after is kept, matches included. That is `remove`'s job, not `drop-while`'s.

**`remove` is lazy.** It removes nothing until a consumer realizes the result. Predicate side effects can occur in chunks of 32.

**Use the correct function for each collection.** Use `remove` for sequences, `disj` for sets, and `dissoc` for maps. Each function returns new data.

---

# One Sentence to Remember

> **Reject creates a new sequence by discarding elements that satisfy a rule.**
