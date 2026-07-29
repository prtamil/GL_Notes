# Sequence Processing — Verb 12: Expand

## Introduction

Sometimes a single element needs to turn into **several**.

**Expand** swaps each element for zero, one, or many outputs, so the sequence usually comes out bigger.

The question you're asking:

> **"How can one element become many?"**

**Transform** takes one element and gives back one. **Expand** takes one and gives back as many as it likes.

---

# Expand → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Expand**|How can one element become many?|`[y for x in xs for y in f(x)]`, `itertools.chain.from_iterable`, `itertools.product`, `repeat`, `cycle`, `yield from`|

> **Note:** There's no `mapcat` in Python. The nested comprehension **is** flatMap. Read the `for` clauses **outer first**, exactly the way you'd have written the nested loops by hand.

---

# Common Expansion Patterns

|Pattern|Python|Example Result|
|---|---|---|
|One element to many|nested comprehension|`[y for x in [1,2,3] for y in (x, x)]` → `[1,1,2,2,3,3]`|
|Map then flatten|`chain.from_iterable`|`list(chain.from_iterable(map(f, xs)))`|
|Expand into sub-elements|nested comprehension|`[c for w in ["ab","cd"] for c in w]` → `['a','b','c','d']`|
|Split every line into words|nested comprehension|`[w for l in lines for w in l.split()]`|
|Generate combinations|`product`|`list(product([1,2], "ab"))` → `[(1,'a'), (1,'b'), (2,'a'), (2,'b')]`|
|Repeat a value|`repeat` / `*`|`list(repeat("x", 3))` → `['x','x','x']`; `[0]*3` → `[0,0,0]`|
|Repeat a pattern|`cycle`|`list(islice(cycle("RG"), 6))` → `['R','G','R','G','R','G']`|
|Expand recursively|`yield from`|a generator that yields its children's yields|
|Expand to zero or many|comprehension|`[y for x in xs for y in (f(x) if p(x) else [])]`|

---

# The Python-specific catches

**The `for` clauses run outer to inner.** `[y for x in xs for y in x]` walks `xs` first, then each `x`. Swap them around and you get the classic comprehension mistake, usually announced by a baffling `NameError`.

**Expand can do Select's job too.** Yield an empty list for an element and that element disappears, which is why `[y for x in xs for y in f(x)]` can shrink a sequence as easily as grow it.

**`[[0]*3]*2` shares one inner list across both rows.** Repetition copies *references*, not objects. Write `[[0]*3 for _ in range(2)]` instead.

---

# One Sentence to Remember

> **Expand lets every input element produce as many outputs as it needs, so the sequence grows.**
