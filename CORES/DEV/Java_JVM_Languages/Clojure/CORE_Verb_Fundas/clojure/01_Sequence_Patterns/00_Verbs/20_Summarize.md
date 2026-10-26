# Sequence Processing — Verb 20: Summarize

## Introduction

After generating, transforming, grouping, and processing a sequence, we often want **one final insight**.

**Summarize** is the act of extracting meaningful information from an entire sequence.

The mental question is:

> **"What does this sequence tell me?"**

Unlike **Accumulate**, which describes the process of building a result, **Summarize** focuses on the final information or statistic produced from the sequence.

---

# Summarize → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Summarize**|What does this sequence tell me?|`count`, `reduce`, `apply`, `frequencies`, `min`, `max`, `min-key`, `max-key`|

> **Note:** Many Clojure functions are specialized summaries. While `reduce` can compute almost any summary, functions like `count`, `min`, `max`, and `frequencies` express common summaries directly and more clearly.

---

# Common Summary Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Count elements|`count`|`(count [1 2 3 4])` → `4`|
|Sum values|`(reduce + xs)`|`(reduce + [1 2 3 4])` → `10`|
|Find minimum|`apply min`|`(apply min [8 3 5])` → `3`|
|Find maximum|`apply max`|`(apply max [8 3 5])` → `8`|
|Count occurrences|`frequencies`|`(frequencies [:a :b :a])` → `{:a 2 :b 1}`|
|Find min/max by key|`min-key` / `max-key`|`(max-key count "cat" "elephant" "dog")` → `"elephant"`|

---

# The Clojure-specific catches

**Division yields exact ratios, not floats.** `(/ (reduce + [1 2]) 2)` is `3/2`, not `1.5`. That is more correct and will surprise anything downstream expecting a double — call `double` at the boundary.

**Prefer `reduce` to `apply` for large aggregates.** `reduce` does not build a list of function arguments.

**Maximum operations fail for empty input.** `(apply max [])` and `(reduce max [])` throw an `ArityException`. Supply an initial value or test for empty input.

**A summary operation must read the complete input.** It cannot complete for an infinite sequence. It fully realizes a lazy sequence.

---

# One Sentence to Remember

> **Summarize extracts the final insight or statistic from a sequence.**
