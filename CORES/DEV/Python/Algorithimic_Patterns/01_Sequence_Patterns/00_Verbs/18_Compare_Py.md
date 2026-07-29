# Sequence Processing — Verb 18: Compare

## Introduction

Sometimes you don't want to change a sequence at all. You want to know **how two things stack up against each other**.

**Compare** works out equality, ordering, overlap and difference between elements or collections.

The question you're asking:

> **"How are these values or sequences related?"**

Comparison sits underneath searching, sorting, validation, and pretty much every decision your code makes.

---

# Compare → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Compare**|How are these values or sequences related?|`==`, `!=`, `<`, `>`, `<=`, `>=`, `is`, `set` operations (`-`, `&`, `\|`, `<=`), `difflib`, `math.isclose`|

> **Note:** Python compares sequences **lexicographically**: element by element, left to right, and the first difference decides it. That's why `[1, 2, 3] < [1, 3]` is `True`, and it's the same rule that makes tuple keys work for multi-field sorting.

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

**`==` compares values, `is` compares identity.** `is` is only correct for `None`, `True`/`False`, and sentinels. On numbers or strings it looks like it works, thanks to interning, and then falls over on real data.

**`0.1 + 0.2 != 0.3`.** Don't compare floats with `==`. Use `math.isclose`, or work in integers or `Decimal`.

**Mixed types won't order.** `1 < "two"` raises `TypeError`, and a stray `None` in your data is usually the culprit. Sort with `key=lambda x: (x is None, x)`.

**Lists compare by value, not identity**, so `[1,2] == [1,2]` is `True` even though those are two separate objects.

---

# One Sentence to Remember

> **Compare works out how values or sequences relate. Element by element for ordering, set operations for membership, and never `==` for floats.**
