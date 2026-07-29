# Sequence Processing — Verb 17: Accumulate

## Introduction

Many sequence-processing tasks require us to **build a result step by step**.

**Accumulate** is the act of combining elements one at a time into a single growing result.

The mental question is:

> **"How do I build the result one element at a time?"**

Unlike **Scan**, which returns every intermediate state, **Accumulate** returns only the final accumulated result.

---

# Accumulate → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Accumulate**|How do I build the result one element at a time?|`reduce`, `into`, `transduce`|

> **Note:** `reduce` is the fundamental accumulation function. `into` accumulates elements into a collection, while `transduce` performs efficient accumulation by combining transformations with reduction.

---

# Common Accumulation Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Sum values|`reduce`|`(reduce + [1 2 3 4])` → `10`|
|Multiply values|`reduce`|`(reduce * [2 3 4])` → `24`|
|Build a vector|`into`|`(into [] '(1 2 3))` → `[1 2 3]`|
|Build a map|`reduce`|`(reduce (fn [m x] (assoc m x (* x x))) {} [1 2 3])` → `{1 1, 2 4, 3 9}`|

---

# One Sentence to Remember

> **Accumulate builds a single final result by combining elements one at a time.**