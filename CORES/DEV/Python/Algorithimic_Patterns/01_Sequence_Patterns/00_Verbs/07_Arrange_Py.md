# Sequence Processing — Verb 7: Arrange

## Introduction

Sometimes you have exactly the right elements sitting in exactly the wrong **order**.

**Arrange** moves elements around without touching the elements themselves.

The question you're asking:

> **"How should these elements be arranged?"**

**Transform** changes the values. **Arrange** only changes where they sit.

---

# Arrange → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Arrange**|How should these elements be arranged?|`sorted`, `list.sort`, `reversed`, `xs[::-1]`, `random.shuffle`, `random.sample`, `xs[n:] + xs[:n]`|

> **Note:** For every arrangement Python gives you a **copy** version and a **mutate** version: `sorted(xs)` / `xs.sort()`, `reversed(xs)` / `xs.reverse()`, `random.sample(xs, k)` / `random.shuffle(xs)`. Every mutating one returns **`None`**.

---

# Common Arrangement Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Sort ascending|`sorted`|`sorted([4,1,3,2])` → `[1, 2, 3, 4]`|
|Sort descending|`sorted(..., reverse=True)`|`sorted([4,1,3,2], reverse=True)` → `[4, 3, 2, 1]`|
|Sort by a key|`key=`|`sorted(["cat","elephant","dog"], key=len)` → `['cat', 'dog', 'elephant']`|
|Sort by two keys|tuple key|`sorted(ps, key=itemgetter("dept", "age"))`|
|Sort in place|`list.sort`|`xs.sort()` → `None`, `xs` is now sorted|
|Reverse order|`xs[::-1]`|`[1,2,3][::-1]` → `[3, 2, 1]`|
|Reverse lazily|`reversed`|`list(reversed([1,2,3]))` → `[3, 2, 1]`|
|Randomize (in place)|`random.shuffle`|`shuffle(xs)` → `None`, `xs` reordered|
|Randomize (copy)|`random.sample`|`sample([1,2,3,4], 4)` → e.g. `[3, 1, 4, 2]`|
|Rotate|slicing|`xs[2:] + xs[:2]`|

---

# The Python-specific catches

**`xs = xs.sort()` sets `xs` to `None`.** This is the classic arrangement bug in Python. Use `sorted()` when you want a value back, `.sort()` when you want the side effect.

**Sorting is stable, thanks to Timsort.** Equal elements stay in their original order, and that's what makes multi-pass sorting work: sort by the least important key first, and whatever you sort by last becomes the primary key.

**`sorted(xs, reverse=True)` is not the same as `sorted(xs)[::-1]`.** The values match, but ties come out in different orders. Stick with `reverse=True`.

---

# One Sentence to Remember

> **Arrange gives you the same elements in a different order, and never changes the elements themselves.**
