# Sequence Processing — Verb 11: Pair

## Introduction

Sometimes two sequences line up **element by element**.

**Pair** matches up those corresponding elements so you can work with them together.

The question you're asking:

> **"Which elements correspond to each other?"**

**Join** sticks collections end to end. **Pair** lines them up side by side, by position or by relationship.

---

# Pair → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Pair**|Which elements correspond to each other?|`zip`, `zip_longest`, `dict(zip(k, v))`, `enumerate`, `itertools.pairwise`, `itertools.product`, `str.join`|

> **Note:** `zip` basically *is* this verb. `zip(*pairs)` unzips them again. `dict(zip(keys, values))` builds a mapping. `pairwise(xs)` pairs each element with its **neighbour**. `product(a, b)` pairs **everything** with everything.

---

# Common Pair Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Pair two sequences|`zip`|`list(zip("ab", [1,2]))` → `[('a', 1), ('b', 2)]`|
|Process two sequences together|comprehension|`[a + b for a, b in zip([1,2,3], [10,20,30])]` → `[11, 22, 33]`|
|Pair keys with values|`dict(zip(...))`|`dict(zip("ab", [1,2]))` → `{'a': 1, 'b': 2}`|
|Pair with the index|`enumerate`|`list(enumerate("abc"))` → `[(0,'a'), (1,'b'), (2,'c')]`|
|Pair adjacent elements|`pairwise`|`list(pairwise([1,2,3]))` → `[(1,2), (2,3)]`|
|Every combination|`product`|`list(product([1,2], "ab"))` → `[(1,'a'), (1,'b'), (2,'a'), (2,'b')]`|
|Unzip|`zip(*pairs)`|`a, b = zip(*[(1,'a'), (2,'b')])` → `(1,2), ('a','b')`|
|Keep uneven tails|`zip_longest`|`list(zip_longest([1,2,3], "ab", fillvalue=None))` → `[(1,'a'), (2,'b'), (3,None)]`|
|Insert separators|`str.join`|`",".join(["A","B","C"])` → `'A,B,C'`|

---

# The Python-specific catches

**`zip` stops at the shortest input and says nothing.** Zip a 100-row list against a 99-row one and you get 99 rows, no warning. Pass `strict=True` (3.10+) if you want it to raise on a length mismatch, or use `zip_longest` to keep everything.

**`zip` hands back a one-shot iterator.** Do `z = zip(a, b)` and call `list(z)` twice: values first, then `[]`.

**`zip(*rows)` transposes.** Pairing and transposing turn out to be the same move viewed from two sides.

---

# One Sentence to Remember

> **Pair lines up matching elements from several sequences so you can work on them together.**
