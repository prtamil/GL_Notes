# Sequence Processing — Verb 20: Summarize

## Introduction

You've generated, transformed, grouped and processed. Now you usually want **one thing out of it all**.

**Summarize** pulls something meaningful out of the whole sequence.

The question you're asking:

> **"What does this sequence tell me?"**

**Accumulate** is about the process of building a result. **Summarize** is about the number or fact you end up with.

---

# Summarize → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Summarize**|What does this sequence tell me?|`len`, `sum`, `min`, `max`, `any`, `all`, `math.prod`, `statistics`, `Counter.most_common`, `heapq.nlargest`|

> **Note:** A lot of Python's builtins are just specialised summaries. `reduce` could compute nearly all of them, but `len`, `sum`, `min`, `max` and `Counter` say the common ones directly and far more clearly.

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

**Empty input is the edge case that keeps coming back.** `sum([])` is `0` and `len([])` is `0`, but `min([])` and `max([])` raise `ValueError`, `mean([])` raises `StatisticsError`, and `most_common(1)[0]` raises `IndexError`. Pass `default=` or guard for empty.

**`all([])` is `True`.** Nothing failed, so it passes. That's the correct definition, and it still catches people out.

**Summarize a generator instead of building a list.** `sum(1 for x in xs if p(x))` counts without allocating anything. `len([x for x in xs if p(x)])` builds a whole list just to measure it and throw it away.

**Floats drift.** `sum([0.1]*10)` comes out as `0.9999999999999999`. Use `math.fsum` when the total matters, or integers and `Decimal` when it's money.

---

# One Sentence to Remember

> **Summarize pulls the final number or fact out of a sequence. Reach for the named builtin, and decide up front what an empty sequence should mean.**
