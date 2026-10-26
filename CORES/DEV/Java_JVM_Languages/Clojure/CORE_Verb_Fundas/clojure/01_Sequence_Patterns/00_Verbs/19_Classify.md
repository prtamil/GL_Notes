# Sequence Processing — Verb 19: Classify

## Introduction

Sometimes we don't just want to group elements—we first want to **assign each element to a category**.

**Classify** is the act of assigning every element in a sequence to a class, label, or category based on a rule.

The mental question is:

> **"Which category does this element belong to?"**

Unlike **Group**, which collects elements into buckets, **Classify** focuses on determining the category for each individual element.

---

# Classify → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Classify**|Which category does this element belong to?|`group-by`, `case`, `cond`, `condp`, `map`|

> **Note:** In practice, classification is often implemented by using `map` to assign labels or `group-by` to both classify and collect elements into categories.

---

# Common Classification Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Classify by predicate|`map`|`(map #(if (odd? %) :odd :even) [1 2 3])` → `(:odd :even :odd)`|
|Classify by multiple rules|`cond` + `map`|`(map #(cond (< % 18) :child (< % 65) :adult :else :senior) [10 30 70])` → `(:child :adult :senior)`|
|Classify and group|`group-by`|`(group-by odd? [1 2 3 4])` → `{true [1 3], false [2 4]}`|
|Classify by computed key|`group-by`|`(group-by count ["cat" "apple" "dog"])` → `{3 ["cat" "dog"], 5 ["apple"]}`|

---

# The Clojure-specific catches

**`case` needs compile-time literals.** It does not evaluate its test constants, so `(case x some-var …)` compares against the *symbol*, not its value. Use `condp` or `cond` when the branches are computed.

**`case` throws when nothing matches** unless you supply a trailing default expression. `cond` returns `nil` instead — a silent classification hole.

**`group-by` is eager.** It realizes the complete sequence. `keep` and `filter` stay lazy.

**Keywords make the best labels.** They are interned, fast to compare, and self-documenting as map keys — prefer `:high` over `"high"` or `2`.

---

# One Sentence to Remember

> **Classify assigns each element to a category based on a rule.**
