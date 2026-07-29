# Sequence Processing — Verb 9: Split

## Introduction

A sequence is often much easier to handle once you've **broken it into pieces that mean something**.

**Split** cuts one sequence into two or more, using a position, a condition, a delimiter, or a grouping rule.

The question you're asking:

> **"How should I divide this sequence?"**

**Slice** takes one piece out. **Split** breaks the whole thing into parts.

---

# Split → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Split**|How should I divide this sequence?|`xs[:n], xs[n:]`, `itertools.batched`, `itertools.groupby`, `str.split`, `str.partition`, `re.split`, a two-bucket loop|

> **Note:** There's no `split-with` in Python. If you want "the leading run, then everything else", use `takewhile` plus `dropwhile` (two passes) or write one explicit loop. If you want "all the trues here, all the falses there" — a **partition** — index a 2-tuple with `bool(pred(x))`.

---

# Common Split Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Split at a position|two slices|`xs[:3], xs[3:]` → `([1,2,3], [4,5])`|
|Split into two buckets by predicate|loop|`partition(lambda x: x > 0, xs)` → `([-1, 0], [3, 2, 1])`|
|Split at the first failure|`takewhile`/`dropwhile`|`[3,2,1]` and `[0,-1]`|
|Split into equal-sized chunks|`batched`|`list(batched([1,2,3,4], 2))` → `[(1,2), (3,4)]`|
|Chunks, allow a short last one|`batched`|`list(batched([1,2,3,4,5], 2))` → `[(1,2), (3,4), (5,)]`|
|Chunks, drop the short last one|`zip(*[iter(xs)]*n)`|`list(zip(*[iter([1,2,3,4,5])]*2))` → `[(1,2), (3,4)]`|
|Split whenever a key changes|`groupby`|`[list(g) for _, g in groupby([1,3,2,4,5], key=lambda n: n%2)]` → `[[1,3], [2,4], [5]]`|
|Split a string|`str.split`|`"a,b,c".split(",")` → `['a', 'b', 'c']`|
|Split once, keep the separator|`str.partition`|`"k=v".partition("=")` → `('k', '=', 'v')`|
|Split on a pattern|`re.split`|`re.split(r"\s+", "a  b")` → `['a', 'b']`|
|Split into head and tail|starred unpack|`first, *rest = xs`|

---

# The Python-specific catches

**`itertools.groupby` splits wherever the key changes between *adjacent* items**, just like Clojure's `partition-by`. It is not SQL's `GROUP BY`. Also, all its group iterators share a single cursor, so consume each group **inside** the loop or you'll find them empty later.

**`"a,,b".split(",")` keeps the empty field** and gives you `['a', '', 'b']`. But `" a  b ".split()` with no argument collapses runs of whitespace and trims the ends. Same name, two different functions underneath.

**`batched` keeps the short tail. The `zip(*[iter(xs)]*n)` grouper throws it away.** Pick on purpose, because a tail that vanishes silently is the classic chunking bug.

---

# One Sentence to Remember

> **Split turns one sequence into several that each mean something on their own.**
