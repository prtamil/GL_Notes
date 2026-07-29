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

> **Note:** `map` can process multiple sequences in parallel, `zipmap` pairs keys with values to create a map, `interleave` alternates elements from multiple sequences, and `interpose` inserts a separator between adjacent elements.

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

# One Sentence to Remember

> **Pair aligns corresponding elements from multiple sequences so they can be processed together.**