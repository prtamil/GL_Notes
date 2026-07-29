# Sequence Processing — Verb 11: Pair

## Introduction

Sometimes two or more sequences are related **element by element**.

**Pair** is the act of aligning corresponding elements from multiple sequences so they can be processed together.

The mental question is:

> **"Which elements correspond to each other?"**

Unlike **Join**, which combines collections end-to-end, **Pair** aligns elements by their position or relationship.

---

# Pair → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Pair**|Which elements correspond to each other?|`zip`, `zip_longest`, `dict(zip(k, v))`, `enumerate`, `itertools.pairwise`, `itertools.product`, `str.join`|

> **Note:** `zip` is the whole verb. `zip(*pairs)` unzips them again, `dict(zip(keys, values))` builds a mapping, `pairwise(xs)` pairs each element with its **neighbour**, and `product(a, b)` pairs **every** element with every other.

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

**`zip` stops at the shortest input, silently.** Zipping a 100-row list with a 99-row one gives 99 rows and no warning. Use `zip(..., strict=True)` (3.10+) to raise on a length mismatch, or `zip_longest` to keep everything.

**`zip` returns a one-shot iterator.** `z = zip(a, b)`, then `list(z)` twice → values, then `[]`.

**`zip(*rows)` transposes** — pairing and transposing are the same operation seen from opposite sides.

---

# One Sentence to Remember

> **Pair aligns corresponding elements from multiple sequences so they can be processed together.**
