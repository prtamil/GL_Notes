# Sequence Processing — Verb 18: Compare

## Introduction

Sometimes the goal is not to transform a sequence, but to **determine how two values or sequences relate to each other**.

**Compare** is the act of evaluating similarities, differences, equality, or ordering between elements or collections.

The mental question is:

> **"How are these values or sequences related?"**

Comparison is fundamental to searching, sorting, validation, and decision-making.

---

# Compare → Clojure

|Thinking Verb|Mental Question|Common Clojure Functions|
|---|---|---|
|**Compare**|How are these values or sequences related?|`=`, `not=`, `compare`, `<`, `>`, `<=`, `>=`, `compare-by` (via comparator functions)|

> **Note:** `=` checks value equality, `compare` establishes ordering, and comparison predicates (`<`, `>`, etc.) are used throughout filtering, sorting, and validation.

---

# Common Comparison Patterns

|Pattern|Clojure|Example Result|
|---|---|---|
|Check equality|`=`|`(= [1 2] [1 2])` → `true`|
|Check inequality|`not=`|`(not= 10 20)` → `true`|
|Compare ordering|`compare`|`(compare 3 5)` → `-1`|
|Less than|`<`|`(< 3 5)` → `true`|
|Greater than|`>`|`(> 8 2)` → `true`|
|Compare while sorting|`sort` / `sort-by`|`(sort > [3 1 4 2])` → `(4 3 2 1)`|

---

# The Clojure-specific catches

**`=` and `==` have different numeric rules.** `(= 1 1.0)` is `false`. `(== 1 1.0)` is `true`. Use `==` for numeric magnitude across types.

**`=` compares sequential collections structurally, across types.** `(= [1 2] '(1 2))` is `true` — a vector equals a list with the same elements. But `(= [1 2] #{1 2})` is `false`, because a set is not sequential.

**`compare` throws on mixed types**, the same `ClassCastException` you get from sorting. It returns a negative, zero or positive number — do not depend on exactly `-1` and `1`.

**`identical?` tests reference equality.** Use `=` for normal value comparisons.

---

# One Sentence to Remember

> **Compare determines the relationship between values or sequences, such as equality, ordering, or difference.**
