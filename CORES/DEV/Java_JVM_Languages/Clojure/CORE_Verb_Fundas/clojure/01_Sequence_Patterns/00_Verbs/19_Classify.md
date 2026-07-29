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

# One Sentence to Remember

> **Classify assigns each element to a category based on a rule.**