# Sequence Processing — Verb 16: Scan

## Introduction

Sometimes the final answer isn't enough. You want to watch **how it got there, step by step**.

**Scan** hands you every intermediate result as it walks the sequence.

The question you're asking:

> **"What do I know after each step?"**

**Accumulate** gives you the final result and nothing else. **Scan** gives you the whole history.

---

# Scan → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Scan**|What do I know after each step?|`itertools.accumulate`|

> **Note:** Python's function is *called* `accumulate`, but it does the **Scan** verb: it returns every intermediate value. The **Accumulate** verb is `functools.reduce`, which returns only the last one. The library named them after how they work; the verbs name them after what you meant.

---

# Common Scan Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Running sum|`accumulate(xs)`|`list(accumulate([1,2,3,4]))` → `[1, 3, 6, 10]`|
|Running product|`accumulate(xs, mul)`|`list(accumulate([2,3,4], mul))` → `[2, 6, 24]`|
|Running maximum|`accumulate(xs, max)`|`list(accumulate([3,1,5,2], max))` → `[3, 3, 5, 5]`|
|Running minimum|`accumulate(xs, min)`|`list(accumulate([3,1,5,2], min))` → `[3, 1, 1, 1]`|
|Running balance|`initial=`|`list(accumulate([20,-10], initial=100))` → `[100, 120, 110]`|
|Prefix sum (query-ready)|`initial=0`|`list(accumulate([2,4,6], initial=0))` → `[0, 2, 6, 12]`|
|Custom carried state|`accumulate(xs, step, initial=s)`|a dict or tuple per step|
|Running union|`accumulate(sets, or_)`|`[{1}, {1,2}, {1,2,3}]`|

---

# The Python-specific catches

**The signature is `f(accumulated, next)`, accumulator first.** For anything non-commutative — subtraction, division, string concatenation — that order decides the whole answer.

**`initial=` makes the output one element longer.** That extra value at the front is exactly what lets prefix-sum range queries (`P[j] - P[i]`) work without a special case at index 0.

**Scan and adjacent differences undo each other.** `accumulate` turns per-step values into totals, and `[b - a for a, b in pairwise(xs)]` turns totals back into per-step values. Real data shows up in both shapes.

---

# One Sentence to Remember

> **Scan gives you every intermediate result as it goes. It's `reduce` showing its work.**
