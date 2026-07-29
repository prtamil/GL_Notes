# Sequence Processing — Verb 6: Transform

## Introduction

Once we have the right elements, we often need to **change** them.

**Transform** is the act of converting each element of a sequence into another value while preserving the overall structure of the sequence.

The mental question is:

> **"How should each element change?"**

Unlike **Select** and **Reject**, which decide _which_ elements remain, **Transform** changes _what_ each element becomes.

---

# Transform → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Transform**|How should each element change?|`map`, `map-indexed`, `replace`, `update`, `update-in`|

> **Note:** `map` is the primary transformation function. `map-indexed` includes the element's position, while `replace`, `update`, and `update-in` are useful for targeted value transformations.

---

# Common Transformation Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Transform every element|`map`|`(map inc [1 2 3])` → `(2 3 4)`|
|Transform using index|`map-indexed`|`(map-indexed vector [:a :b :c])` → `([0 :a] [1 :b] [2 :c])`|
|Replace specific values|`replace`|`(replace {2 :two 4 :four} [1 2 3 4])` → `(1 :two 3 :four)`|
|Update a map value|`update`|`(update {:x 10} :x inc)` → `{:x 11}`|
|Update a nested value|`update-in`|`(update-in {:a {:b 2}} [:a :b] inc)` → `{:a {:b 3}}`|

---

# One Sentence to Remember

> **Transform creates a new sequence by changing each element according to a rule while preserving the sequence structure.**