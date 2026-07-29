# Sequence Processing — Verb 12: Expand

## Introduction

Sometimes one element needs to become **multiple elements**.

**Expand** is the act of replacing each element with zero, one, or many output elements, producing a larger sequence.

The mental question is:

> **"How can one element become many?"**

Unlike **Transform**, which maps one element to one element, **Expand** maps one element to many elements.

---

# Expand → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Expand**|How can one element become many?|`[y for x in xs for y in f(x)]`, `itertools.chain.from_iterable`, `itertools.product`, `repeat`, `cycle`, `yield from`|

> **Note:** Python has no `mapcat`. The nested comprehension **is** flatMap — and the `for` clauses read **outer first**, exactly as if you had written the nested loops.

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

**The order of `for` clauses is outer-to-inner.** `[y for x in xs for y in x]` iterates `xs` first, then each `x`. Reversing them is the classic comprehension error, and it usually raises a confusing `NameError`.

**Expand subsumes Select.** Yielding an empty list for an element drops it — which is why `[y for x in xs for y in f(x)]` can shrink a sequence as well as grow one.

**`[[0]*3]*2` shares the inner list.** Repetition copies *references*, not objects. Use `[[0]*3 for _ in range(2)]`.

---

# One Sentence to Remember

> **Expand produces a larger sequence by allowing each input element to generate multiple output elements.**
