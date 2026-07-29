# Sequence Processing — Verb 9: Split

## Introduction

Sometimes a sequence is easier to work with after it has been **divided into meaningful pieces**.

**Split** is the act of dividing one sequence into two or more sequences based on a position, condition, delimiter, or grouping rule.

The mental question is:

> **"How should I divide this sequence?"**

Unlike **Slice**, which extracts one portion, **Split** separates the original sequence into multiple parts.

---

# Split → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Split**|How should I divide this sequence?|`xs[:n], xs[n:]`, `itertools.batched`, `itertools.groupby`, `str.split`, `str.partition`, `re.split`, a two-bucket loop|

> **Note:** Python has no `split-with`. For "leading run, then the rest" use `takewhile` + `dropwhile` (two passes) or one explicit loop. For "everything true, everything false" — a **partition** — index a 2-tuple with `bool(pred(x))`.

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

**`itertools.groupby` splits on *adjacent* key changes**, exactly like Clojure's `partition-by` — it is not SQL `GROUP BY`. And its group iterators share one cursor: consume each group **inside** the loop or they come back empty.

**`"a,,b".split(",")` keeps the empty field** (`['a', '', 'b']`), but `" a  b ".split()` with no argument collapses whitespace runs and strips the ends. Two different functions wearing one name.

**`batched` keeps the short tail; the `zip(*[iter(xs)]*n)` grouper drops it.** Choose deliberately — a silently dropped tail is the classic chunking bug.

---

# One Sentence to Remember

> **Split divides one sequence into multiple meaningful sequences.**
