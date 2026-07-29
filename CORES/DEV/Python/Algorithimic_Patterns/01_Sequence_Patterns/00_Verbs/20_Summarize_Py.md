# Sequence Processing — Verb 20: Summarize

## Introduction

After generating, transforming, grouping, and processing a sequence, we often want **one final insight**.

**Summarize** is the act of extracting meaningful information from an entire sequence.

The mental question is:

> **"What does this sequence tell me?"**

Unlike **Accumulate**, which describes the process of building a result, **Summarize** focuses on the final information or statistic produced from the sequence.

---

# Summarize → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Summarize**|What does this sequence tell me?|`len`, `sum`, `min`, `max`, `any`, `all`, `math.prod`, `statistics`, `Counter.most_common`, `heapq.nlargest`|

> **Note:** Many Python builtins are specialized summaries. While `reduce` can compute almost any summary, `len`, `sum`, `min`, `max`, and `Counter` express the common ones directly and much more clearly.

---

# Common Summary Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Count elements|`len`|`len([1,2,3,4])` → `4`|
|Count matching elements|`sum` of a genexp|`sum(1 for x in xs if p(x))`|
|Sum values|`sum`|`sum([1,2,3,4])` → `10`|
|Multiply values|`math.prod`|`prod([2,3,4])` → `24`|
|Find the minimum|`min`|`min([8,3,5])` → `3`|
|Find the maximum|`max`|`max([8,3,5])` → `8`|
|Find min/max by a key|`key=`|`max(["cat","elephant"], key=len)` → `'elephant'`|
|Count occurrences|`Counter`|`Counter("aba")` → `Counter({'a': 2, 'b': 1})`|
|Most common value|`most_common(1)`|`Counter(xs).most_common(1)[0][0]`|
|Top k values|`heapq.nlargest`|`nlargest(3, xs)` — O(n log k)|
|Average / median|`statistics`|`mean([1,2,3])` → `2`, `median(xs)`|
|Spread|`statistics.stdev`|`stdev(xs)`|
|Does any / do all match|`any` / `all`|`any(x < 0 for x in xs)` → `False`|

---

# The Python-specific catches

**Empty input is the recurring edge case.** `sum([])` is `0` and `len([])` is `0`, but `min([])` and `max([])` raise `ValueError`, `mean([])` raises `StatisticsError`, and `most_common(1)[0]` raises `IndexError`. Pass `default=` or guard the empty case.

**`all([])` is `True`** — vacuously. This is the correct definition and it still surprises people.

**Summarize a generator, don't build a list.** `sum(1 for x in xs if p(x))` counts without allocating; `len([x for x in xs if p(x)])` builds a whole list just to measure it.

**Floats drift.** `sum([0.1]*10)` is `0.9999999999999999`; use `math.fsum` when the total matters, or integers/`Decimal` for money.

---

# One Sentence to Remember

> **Summarize extracts the final insight or statistic from a sequence — reach for the named builtin, and decide up front what an empty sequence means.**
