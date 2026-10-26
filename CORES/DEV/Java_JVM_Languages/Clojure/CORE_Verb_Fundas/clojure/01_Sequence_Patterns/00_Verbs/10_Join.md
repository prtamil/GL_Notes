# Sequence Processing — Verb 10: Join

## Introduction

Often information is spread across multiple sequences, and we need to **bring them together**.

**Join** is the act of combining two or more sequences into a single sequence or collection.

The mental question is:

> **"How do I bring these sequences together?"**

Unlike **Pair**, which relates elements position by position, **Join** focuses on unifying collections into one.

---

# Join → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Join**|How do I bring these sequences together?|`concat`, `into`, `merge`, `merge-with`, `conj`, `cons`|

> **Note:** `concat` joins sequences. `into` copies values into a target collection. `merge` joins maps. `merge-with` combines map values. `conj` and `cons` add items.

---

# Common Join Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Join sequences|`concat`|`(concat [1 2] [3 4])` → `(1 2 3 4)`|
|Join into a collection|`into`|`(into [1 2] [3 4])` → `[1 2 3 4]`|
|Join maps|`merge`|`(merge {:a 1} {:b 2})` → `{:a 1 :b 2}`|
|Join maps with value function|`merge-with`|`(merge-with + {:a 1} {:a 2})` → `{:a 3}`|
|Add one element|`conj`|`(conj [1 2] 3)` → `[1 2 3]`|

---

# The Clojure-specific catches

**Do not use `concat` repeatedly in a loop.** Each call adds another lazy layer. Many layers can be slow and can overflow the stack. Use `into` for accumulation.

**`into` reverses values when the target is a list.** `conj` adds at the front of a list. It adds at the end of a vector. The target type controls the order.

**Pick the join for the collection type.** `concat` for sequences, `into` for building a concrete collection, `merge` for maps, `clojure.string/join` for strings. `concat` on maps gives you a sequence of pairs, not a map.

**`into` uses transients where it can**, so it is meaningfully faster than `(reduce conj …)` for building vectors, sets and maps.

---

# One Sentence to Remember

> **Join combines multiple sequences or collections into a single collection.**

