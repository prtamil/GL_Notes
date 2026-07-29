# Sequence Processing — Verb 16: Scan

## Introduction

Sometimes we don't just want the final answer—we want to see **how the answer evolves at every step**.

**Scan** is the act of producing every intermediate result while traversing a sequence.

The mental question is:

> **"What do I know after each step?"**

Unlike **Accumulate**, which returns only the final result, **Scan** returns the entire history of intermediate states.

---

# Scan → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Scan**|What do I know after each step?|`itertools.accumulate`|

> **Note:** Python's function is *named* `accumulate` but it implements the **Scan** verb — it returns every intermediate value. The **Accumulate** verb is `functools.reduce`, which returns only the last one. The library named them after mechanics; the verbs name them after intent.

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

**The function signature is `f(accumulated, next)` — accumulator first.** For non-commutative operations (subtract, divide, string concat) that order is the entire answer.

**`initial=` makes the output one element longer.** That extra leading value is exactly what makes prefix-sum range queries (`P[j] - P[i]`) work without a special case at index 0.

**Scan and adjacent differences are inverses.** `accumulate` turns per-step values into totals; `[b - a for a, b in pairwise(xs)]` turns totals back into per-step values. Real data arrives in both forms.

---

# One Sentence to Remember

> **Scan produces every intermediate result while processing a sequence — it is `reduce` that shows its work.**
