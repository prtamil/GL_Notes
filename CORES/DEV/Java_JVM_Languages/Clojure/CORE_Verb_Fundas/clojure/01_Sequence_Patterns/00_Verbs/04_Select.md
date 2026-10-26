# Sequence Processing — Verb 4: Select

## Introduction

After searching, we often want to **keep** only the elements that matter.

**Select** is the act of creating a new sequence by retaining elements that satisfy a rule or condition.

The mental question is:

> **"What should I keep?"**

Unlike **Search**, which locates elements, **Select** produces a **new sequence** containing only the desired elements.

---

# Select → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Select**|What should I keep?|`filter`, `keep`, `take`, `take-while`|

> **Note:** `filter` keeps elements that satisfy a predicate. `keep` both transforms and discards `nil` values. `take` and `take-while` select elements based on position or condition.

---

# Common Selection Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Keep matching elements|`filter`|`(filter even? [1 2 3 4])` → `(2 4)`|
|Keep transformed non-`nil` values|`keep`|`(keep #(when (even? %) (* % 10)) [1 2 3 4])` → `(20 40)`|
|Keep first _N_ elements|`take`|`(take 3 [1 2 3 4 5])` → `(1 2 3)`|
|Keep while condition holds|`take-while`|`(take-while pos? [3 2 1 0 -1])` → `(3 2 1)`|

---

# The Clojure-specific catches

**Lazy sequences are cached.** If you realize the same lazy sequence twice, its function runs once. You can traverse the cached sequence again.

**`(filter identity xs)` drops only `nil` and `false`.** In Clojure, `0` and `""` are true values. Python also removes `0`, `""`, and `[]`.

**Use `remove`, not `(filter (complement pred))`.** The name states the intent directly.

**`keep` is filter and map in one step**, dropping `nil` results. If you find yourself filtering and then mapping the same predicate's work, `keep` is the function you wanted.

**`take-while` stops at the first false result. `filter` checks every value.** The two functions can return different results.

---

# One Sentence to Remember

> **Select creates a new sequence by keeping only the elements that satisfy a rule.**
