# Sequence Processing — Verb 7: Arrange

## Introduction

Sometimes the elements are correct, but their **order** is not.

**Arrange** is the act of reorganizing the elements of a sequence without changing the elements themselves.

The mental question is:

> **"How should these elements be arranged?"**

Unlike **Transform**, which changes the values, **Arrange** changes only their position or ordering.

---

# Arrange → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Arrange**|How should these elements be arranged?|`sorted`, `list.sort`, `reversed`, `xs[::-1]`, `random.shuffle`, `random.sample`, `xs[n:] + xs[:n]`|

> **Note:** Python separates **copy** from **mutate** for every arrangement: `sorted(xs)` / `xs.sort()`, `reversed(xs)` / `xs.reverse()`, `random.sample(xs, k)` / `random.shuffle(xs)`. The mutating forms all return **`None`**.

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

**`xs = xs.sort()` sets `xs` to `None`.** The single most common arrangement bug in Python. `sorted()` when you want a value; `.sort()` when you want a side effect.

**Sorting is stable (Timsort).** Equal elements keep their original order — which is what makes multi-pass sorting work: sort by the least significant key first, and the last sort is the primary key.

**`sorted(xs, reverse=True)` ≠ `sorted(xs)[::-1]`.** They agree on values and disagree on ties. Prefer `reverse=True`.

---

# One Sentence to Remember

> **Arrange creates a new view of a sequence by changing the order of its elements without changing the elements themselves.**
