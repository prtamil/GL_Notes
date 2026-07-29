# Sequence Processing — Verb 17: Accumulate

## Introduction

A lot of sequence work comes down to **building a result piece by piece**.

**Accumulate** folds elements in one at a time until you have a single answer.

The question you're asking:

> **"How do I build the result one element at a time?"**

**Scan** shows you every state along the way. **Accumulate** just hands you the finished result.

---

# Accumulate → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Accumulate**|How do I build the result one element at a time?|`sum`, `math.prod`, `"".join`, `functools.reduce`, `list.extend`, `dict.update`, `set.update`, an explicit loop|

> **Note:** Python plays down `reduce` on purpose. Guido moved it out of the builtins and into `functools`. Common accumulations already have a **named** function — `sum`, `prod`, `join`, `min`, `max`, `any`, `all` — and for anything else a plain loop usually reads better than a lambda.

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

**Don't build strings with `+=` in a loop.** Strings are immutable, so every step copies the whole result and you end up at O(n²). `"".join(parts)` is the right form. The same logic is what makes `sum(lists, [])` quadratic.

**`sum` refuses strings deliberately** and raises `TypeError`, precisely to push you toward `join`.

**`reduce` on an empty sequence raises `TypeError`** unless you give it an initial value. `sum([])` is `0`; `reduce(add, [])` blows up.

**Accumulating into a mutable default is a classic trap.** `def f(x, acc=[])` shares one list across every single call. Use `acc=None` and build it inside the function.

---

# One Sentence to Remember

> **Accumulate combines elements one at a time into one final result. In Python, take the named function over `reduce` whenever there is one.**
