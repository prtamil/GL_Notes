# Sequence Processing — Verb 10: Join

## Introduction

Information tends to arrive scattered across several sequences, and you need to **pull it into one**.

**Join** merges two or more sequences into a single sequence or collection.

The question you're asking:

> **"How do I bring these sequences together?"**

**Pair** lines elements up position by position. **Join** just makes one collection out of many.

---

# Join → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Join**|How do I bring these sequences together?|`itertools.chain`, `+`, `list.extend`, `list.append`, `\|` (dicts and sets), `dict.update`, `str.join`, `{**a, **b}`, `[*a, *b]`|

> **Note:** `+` builds a new list. `.extend()` changes the list in place and returns `None`. `chain` builds nothing at all and just reads through each source in turn. `chain` is also the only one that takes any iterable, since you can't `+` a generator onto a list.

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

**Build big strings with `"".join(parts)` and nothing else.** Doing `s += piece` in a loop is O(n²), because strings are immutable and every `+=` copies. Same reason `sum(lists, [])` is O(n²) for lists.

**When dict keys collide, the *last* value wins.** `{"a":1} | {"a":2}` is `{'a': 2}`. If you want to combine the values instead of replacing them, use `Counter` arithmetic or write the loop.

**`xs = xs.extend(ys)` sets `xs` to `None`.** Same in-place-returns-`None` rule you get from `.sort()` and `.reverse()`.

---

# One Sentence to Remember

> **Join takes several sequences or collections and gives you back one.**
