# Sequence Processing — Verb 6: Transform

## Introduction

Once you've got the right elements, you usually need to **change** them.

**Transform** turns each element into some other value and leaves the shape of the sequence alone.

The question you're asking:

> **"How should each element change?"**

**Select** and **Reject** decide _which_ elements survive. **Transform** decides _what each one turns into_.

---

# Transform → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Transform**|How should each element change?|`[f(x) for x in xs]`, `map`, `enumerate`, `starmap`, dict/set comprehensions, `str.translate`|

> **Note:** `map(f, xs)` and `[f(x) for x in xs]` do the same job. Go with the comprehension when the transform is an expression you're writing on the spot. Go with `map` when you already have the function, as in `map(str.strip, lines)`.

---

# Common Transformation Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Transform every element|comprehension|`[x + 1 for x in [1,2,3]]` → `[2, 3, 4]`|
|Transform with a named function|`map`|`list(map(str.upper, ["a","b"]))` → `['A', 'B']`|
|Transform using the index|`enumerate`|`list(enumerate("abc"))` → `[(0,'a'), (1,'b'), (2,'c')]`|
|Transform two sequences together|`map` / `zip`|`list(map(add, [1,2], [10,20]))` → `[11, 22]`|
|Unpack tuples into a function|`starmap`|`list(starmap(pow, [(2,3), (3,2)]))` → `[8, 9]`|
|Replace specific values|dict lookup|`[m.get(x, x) for x in [1,2,3]]` with `m = {2: "two"}` → `[1, 'two', 3]`|
|Transform dict values|dict comprehension|`{k: v*2 for k, v in d.items()}`|
|Transform a set|set comprehension|`{len(w) for w in words}`|
|Transform characters|`str.translate`|`s.translate(str.maketrans("abc", "xyz"))`|

---

# The Python-specific catches

**`map` is lazy and one-shot.** Say `m = map(f, xs)` and call `list(m)` twice: you get the values the first time and `[]` the second.

**`map` over several iterables stops at the shortest one**, same as `zip`.

**Transform keeps the length. It never filters.** If your transform returns `None` for some inputs, there's a Select hiding inside it. Pull the `if` out and write it properly.

---

# One Sentence to Remember

> **Transform runs a rule over every element and gives you a new sequence of the same shape.**
