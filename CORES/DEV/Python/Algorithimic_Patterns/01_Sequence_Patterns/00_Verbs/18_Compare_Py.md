# Sequence Processing — Verb 18: Compare

## Introduction

Sometimes the goal is not to transform a sequence, but to **determine how two values or sequences relate to each other**.

**Compare** is the act of evaluating similarities, differences, equality, or ordering between elements or collections.

The mental question is:

> **"How are these values or sequences related?"**

Comparison is fundamental to searching, sorting, validation, and decision-making.

---

# Compare → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Compare**|How are these values or sequences related?|`==`, `!=`, `<`, `>`, `<=`, `>=`, `is`, `set` operations (`-`, `&`, `\|`, `<=`), `difflib`, `math.isclose`|

> **Note:** Python compares sequences **lexicographically** — element by element, left to right, first difference wins. `[1, 2, 3] < [1, 3]` is `True`, and that same rule is what makes tuple keys work for multi-field sorting.

---

# Common Comparison Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Check equality|`==`|`[1,2] == [1,2]` → `True`|
|Check inequality|`!=`|`10 != 20` → `True`|
|Compare ordering|`<` `>`|`[1,2,3] < [1,3]` → `True` (lexicographic)|
|Chained comparison|`a < b < c`|`1 < 2 < 3` → `True`|
|Same object?|`is`|`a is b` — identity, not value|
|What's in a but not b|`set` difference|`{1,2,3} - {2}` → `{1, 3}`|
|What's in both|`set` intersection|`{1,2} & {2,3}` → `{2}`|
|Is a subset?|`<=`|`{1,2} <= {1,2,3}` → `True`|
|Same elements, any order|`sorted` / `Counter`|`Counter("listen") == Counter("silent")` → `True`|
|Float comparison|`math.isclose`|`isclose(0.1+0.2, 0.3)` → `True`|
|Text similarity|`difflib`|`SequenceMatcher(None, a, b).ratio()` → `0.88`|
|Line-by-line diff|`difflib.unified_diff`|a diff of two files|

---

# The Python-specific catches

**`==` compares values; `is` compares identity.** `is` is correct only for `None`, `True`/`False`, and sentinels. Using it on numbers or strings appears to work because of interning, then fails on real data.

**`0.1 + 0.2 != 0.3`.** Never compare floats with `==`; use `math.isclose` or compare integers/`Decimal`.

**Mixed types don't order.** `1 < "two"` raises `TypeError`, and `None` in your data is the usual cause — sort with `key=lambda x: (x is None, x)`.

**Lists compare by value, not identity**, so `[1,2] == [1,2]` is `True` even though they are different objects.

---

# One Sentence to Remember

> **Compare determines the relationship between values or sequences — element-by-element for order, set operations for membership, and never `==` for floats.**
