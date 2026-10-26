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

# The Clojure-specific catches

**`reduce` on an empty collection with no init calls the function with zero arguments.** `(reduce + [])` is `0` because `(+)` is `0`. But `(reduce max [])` throws an `ArityException`, because `max` has no zero-arity. Supply an init whenever the collection might be empty.

**Use `reduced` to stop early.** Returning `(reduced acc)` from the step function short-circuits the whole traversal — the idiomatic way to bail out of a fold.

**Prefer `into` over `(reduce conj …)`.** `into` uses transients internally and is meaningfully faster for building vectors, sets and maps.

**`reduce` is eager and cannot be lazy** — it must consume everything to produce its one answer. If you want the intermediate values, that is `reductions`.

---

# One Sentence to Remember

> **Accumulate builds a single final result by combining elements one at a time.**