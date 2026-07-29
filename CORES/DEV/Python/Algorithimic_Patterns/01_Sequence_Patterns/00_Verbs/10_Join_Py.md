# Sequence Processing — Verb 10: Join

## Introduction

Often information is spread across multiple sequences, and we need to **bring them together**.

**Join** is the act of combining two or more sequences into a single sequence or collection.

The mental question is:

> **"How do I bring these sequences together?"**

Unlike **Pair**, which relates elements position by position, **Join** focuses on unifying collections into one.

---

# Join → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Join**|How do I bring these sequences together?|`itertools.chain`, `+`, `list.extend`, `list.append`, `\|` (dicts and sets), `dict.update`, `str.join`, `{**a, **b}`, `[*a, *b]`|

> **Note:** `+` builds a new list; `.extend()` mutates in place and returns `None`; `chain` builds nothing at all and just reads each source in turn. Only `chain` works on arbitrary iterables — you cannot `+` a generator onto a list.

---

# Common Join Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Join sequences|`+`|`[1,2] + [3,4]` → `[1, 2, 3, 4]`|
|Join lazily / any iterables|`chain`|`list(chain([1,2], (3,4)))` → `[1, 2, 3, 4]`|
|Join a list of lists|`chain.from_iterable`|`list(chain.from_iterable([[1,2],[3]]))` → `[1, 2, 3]`|
|Unpack into a new list|`[*a, *b]`|`[*[1,2], *[3,4]]` → `[1, 2, 3, 4]`|
|Extend in place|`list.extend`|`xs.extend([3,4])` → `None`, `xs` grew|
|Add one element|`list.append`|`xs.append(3)`|
|Join dicts|`\|` (3.9+)|`{"a":1} \| {"b":2}` → `{'a': 1, 'b': 2}`|
|Join dicts, combining values|`Counter` / loop|`Counter({"a":1}) + Counter({"a":2})` → `Counter({'a': 3})`|
|Join sets|`\|`|`{1,2} \| {2,3}` → `{1, 2, 3}`|
|Join strings|`str.join`|`",".join(["a","b"])` → `'a,b'`|

---

# The Python-specific catches

**`"".join(parts)` is the only correct way to build a large string.** Repeated `s += piece` is O(n²) because strings are immutable — the same reason `sum(lists, [])` is O(n²) for lists.

**Joining dicts keeps the *last* value on a key collision.** `{"a":1} | {"a":2}` is `{'a': 2}`. To combine values instead of replacing, use `Counter` arithmetic or an explicit loop.

**`xs = xs.extend(ys)` sets `xs` to `None`** — the same in-place-returns-`None` rule as `.sort()` and `.reverse()`.

---

# One Sentence to Remember

> **Join combines multiple sequences or collections into a single collection.**
