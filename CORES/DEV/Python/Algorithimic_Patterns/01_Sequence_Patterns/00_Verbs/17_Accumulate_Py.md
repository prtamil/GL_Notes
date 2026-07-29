# Sequence Processing — Verb 17: Accumulate

## Introduction

Many sequence-processing tasks require us to **build a result step by step**.

**Accumulate** is the act of combining elements one at a time into a single growing result.

The mental question is:

> **"How do I build the result one element at a time?"**

Unlike **Scan**, which returns every intermediate state, **Accumulate** returns only the final accumulated result.

---

# Accumulate → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Accumulate**|How do I build the result one element at a time?|`sum`, `math.prod`, `"".join`, `functools.reduce`, `list.extend`, `dict.update`, `set.update`, an explicit loop|

> **Note:** Python deliberately de-emphasizes `reduce` — Guido moved it out of the builtins into `functools`. For the common accumulations there is a **named** function (`sum`, `prod`, `join`, `min`, `max`, `any`, `all`), and for everything else an explicit loop is usually clearer than a lambda.

---

# Common Accumulation Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Sum values|`sum`|`sum([1,2,3,4])` → `10`|
|Multiply values|`math.prod`|`prod([2,3,4])` → `24`|
|Concatenate strings|`str.join`|`"".join(["a","b","c"])` → `'abc'`|
|Build a list|comprehension / `extend`|`[f(x) for x in xs]`|
|Build a dict|dict comprehension|`{x: x*x for x in [1,2,3]}` → `{1: 1, 2: 4, 3: 9}`|
|Build a set|`set.update`|`s.update(more)`|
|Merge counts|`Counter`|`Counter(a) + Counter(b)`|
|Arbitrary fold|`functools.reduce`|`reduce(lambda a, b: a*b + 1, xs)`|
|Fold with a starting value|`reduce(f, xs, init)`|`reduce(add, [], 0)` → `0` (no error on empty)|

---

# The Python-specific catches

**Never accumulate strings with `+=` in a loop.** Strings are immutable, so each step copies the whole result: O(n²). `"".join(parts)` is the only correct form. The same reasoning makes `sum(lists, [])` quadratic.

**`sum` refuses strings on purpose** (`TypeError`), precisely to push you to `join`.

**`reduce` on an empty sequence raises `TypeError`** unless you pass the initial value. `sum([])` is `0`; `reduce(add, [])` is an error.

**Accumulating into a mutable default is a classic bug.** `def f(x, acc=[])` shares one list across every call — use `acc=None` and create it inside.

---

# One Sentence to Remember

> **Accumulate builds a single final result by combining elements one at a time — and in Python, prefer the named function over `reduce` whenever one exists.**
