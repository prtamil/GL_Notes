# Sequence Processing — Verb 11: Pair

## Introduction

Sometimes two or more sequences are related **element by element**.

**Pair** is the act of aligning corresponding elements from multiple sequences so they can be processed together.

The mental question is:

> **"Which elements correspond to each other?"**

Unlike **Join**, which combines collections end-to-end, **Pair** aligns elements by their position or relationship.

---

# Pair → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Pair**|Which elements correspond to each other?|`map`, `mapv`, `zipmap`, `interleave`, `interpose`|

> **Note:** `map` can process parallel sequences. `zipmap` pairs keys and values. `interleave` alternates values. `interpose` inserts separators.

---

# Common Pair Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Pair two sequences|`(map vector)`|`(map vector [:a :b] [1 2])` → `([:a 1] [:b 2])`|
|Process two sequences together|`map`|`(map + [1 2 3] [10 20 30])` → `(11 22 33)`|
|Pair keys with values|`zipmap`|`(zipmap [:a :b] [1 2])` → `{:a 1 :b 2}`|
|Alternate elements|`interleave`|`(interleave [1 2 3] [:a :b :c])` → `(1 :a 2 :b 3 :c)`|
|Insert separators|`interpose`|`(interpose "," ["A" "B" "C"])` → `("A" "," "B" "," "C")`|

---

# The Clojure-specific catches

**There is no `zip` — `map` is one.** Give `map` two collections and it walks them in step. The function you pass decides the result: `vector` keeps pairs, `+` adds, `=` compares.

**Pairing stops at the shortest input without a warning.** Check the counts when parallel sequences must have equal lengths.

**`zipmap` keeps the last value for a duplicate key.** Its result is a map. Do not use the map to preserve pairing order.

**`interleave` also stops at the shortest**, and unlike pairing it gives you no way to see what was dropped.

**Unzipping is the same call.** `(apply map vector pairs)` transposes, which is why pairing, unzipping and matrix transposition are one idiom.

---

# One Sentence to Remember

> **Pair aligns corresponding elements from multiple sequences so they can be processed together.**
