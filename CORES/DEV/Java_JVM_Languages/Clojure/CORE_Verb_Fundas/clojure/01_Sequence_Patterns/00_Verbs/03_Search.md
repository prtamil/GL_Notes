# Sequence Processing — Verb 3: Search

## Introduction

Once a sequence exists and we have observed it, the next natural action is to **find something**.

**Search** is the act of locating one or more elements in a sequence that satisfy a condition.

The mental question is:

> **"Where is what I'm looking for?"**

Unlike **Observe**, which describes the sequence as a whole, **Search** focuses on finding specific elements or positions within the sequence.

---

# Search → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Search**|Where is what I'm looking for?|`some`, `filter`, `keep`, `keep-indexed`, `first`, `ffirst`, `find` (maps), `contains?` (maps/sets/indexed collections)|

> **Note:** Clojure has no single generic "find in a sequence" function. The appropriate function depends on whether you're searching for a value, matching a predicate, finding an index, or looking up a key in a map.

---

# Common Search Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Find first matching element|`(some pred coll)`|`(some even? [1 3 4 5])` → `true` (truthy)|
|Find all matching elements|`filter`|`(filter even? [1 2 3 4])` → `(2 4)`|
|Find first transformed match|`keep`|`(keep #(when (even? %) (* % 10)) [1 2 3 4])` → `(20 40)`|
|Find matching indices|`keep-indexed`|`(keep-indexed #(when (even? %2) %1) [1 2 3 4])` → `(1 3)`|
|Find by key (map)|`find`|`(find {:a 1 :b 2} :b)` → `[:b 2]`|
|Check key/index exists|`contains?`|`(contains? #{1 2 3} 2)` → `true`|

---

# One Sentence to Remember

> **Search locates specific elements or positions in a sequence that satisfy a condition.**