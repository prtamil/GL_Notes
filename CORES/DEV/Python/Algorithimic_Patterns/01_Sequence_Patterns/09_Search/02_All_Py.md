# Pattern 27 — Search All Matches

## Mental Model

Search the entire sequence and **return every element that satisfies a condition**.

**First Match** stops at the first result. **Search All** walks the entire sequence.

The default spelling is the **comprehension with an `if`**: `[x for x in xs if p(x)]`. `filter()` does the same job lazily, but the comprehension reads better the moment a transform is involved.

---

## Relationship to Cognitive Verb

```text
Search
   ↓
Search All
```

Search All is a **Search** pattern that pulls out **every matching element** in the sequence.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|All Matching Elements|all evens|`[x for x in xs if p(x)]`|
|Lazily|big / infinite input|`filter(p, xs)`|
|Remove Matches|keep non-matches|`[x for x in xs if not p(x)]` / `filterfalse`|
|Matching Indices|positions|`[i for i, x in enumerate(xs) if p(x)]`|
|Match then Transform|project|`[f(x) for x in xs if p(x)]`|
|Transform then Match|filter on the result|`[y for x in xs if (y := f(x)) is not None]`|
|Count Matches|how many|`sum(1 for x in xs if p(x))`|
|Multiple Conditions|`and` / `or`|`if p(x) and q(x)`|
|Membership Filter|in a set of values|`if x in allowed`|
|All Regex Matches|every occurrence|`re.findall` / `re.finditer`|

> **Note:** `filter(p, xs)` returns an **iterator**, not a list — printing it shows `<filter object>`, and it is empty after one pass. `filter(None, xs)` is the special form that keeps every **truthy** element.

---

## Common Uses

- Find all errors

- Search logs

- Query records

- Data filtering

- Find all users

- Validation reports

- Event filtering

- Database-style queries

---

## Hidden Interview Problems

- Find all duplicates

- Find all primes

- Find all intervals overlapping a range

- Return matching records

- Search text

- Filter a dataset

- All indices of a target

---

## Recognition Clues

If you hear:

- All matches

- Every occurrence

- Find all

- Search entire sequence

- Matching records

- Filter results

- Collect matches

Think:

**→ Search All**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Search|
|Pattern|Search All|
|Stops Early|No|
|Returns|all matching values|
|Cost|O(n) always|
|Comprehension Returns|a `list`|
|`filter()` Returns|a one-shot iterator|
|Preserves Order|Yes|
|Primary Use|Complete search|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import filterfalse, compress
import re

xs = [3, 7, 10, 12, 15, 20]

# ============================================
# All even numbers — the default spelling

[x for x in xs if x % 2 == 0]           # => [10, 12, 20]

# lazily, when the input is huge or infinite:
list(filter(lambda x: x % 2 == 0, xs))  # => [10, 12, 20]

# the comprehension is faster here (no per-element lambda call) and
# reads better. Use filter() when you already HAVE a named function:
list(filter(str.isdigit, ["1", "a", "2"]))          # => ['1', '2']

# ============================================
# All numbers greater than 10

[x for x in xs if x > 10]               # => [12, 15, 20]

# ============================================
# Remove matches — the complement

[x for x in xs if x % 2]                # => [3, 7, 15]     odds
list(filterfalse(lambda x: x % 2 == 0, xs))         # => [3, 7, 15]

# `not p(x)` in a comprehension, or filterfalse with filter's signature.
# Keeping BOTH halves? That's partition — see 07_Group.

# ============================================
# Matching indices instead of values

[i for i, x in enumerate(xs) if x % 2 == 0]         # => [2, 3, 5]

# every index of a specific value:
data = [1, 2, 1, 3, 1]
[i for i, x in enumerate(data) if x == 1]           # => [0, 2, 4]

# list.index only ever gives you the first one — this is the "all" form

# ============================================
# Filter records

users = [
    {"id": 1, "active": True},
    {"id": 2, "active": False},
    {"id": 3, "active": True},
]

[u for u in users if u["active"]]
# => [{'id': 1, 'active': True}, {'id': 3, 'active': True}]

# use .get() when the key may be missing — [u for u in users if u.get("active")]
# otherwise one malformed record raises KeyError and kills the whole query

# ============================================
# Search then transform — one pass, one comprehension

[x * 10 for x in xs if x % 2 == 0]      # => [100, 120, 200]

# the `if` runs FIRST, then the expression. Reading order is:
#   for → if → expression
# which is why the transform only ever sees matching elements.

# don't chain map over filter:
list(map(lambda x: x * 10, filter(lambda x: x % 2 == 0, xs)))    # same, worse

# ============================================
# Transform then filter on the RESULT — the walrus idiom

lines = ["a=1", "junk", "b=2"]

[m.groups() for line in lines if (m := re.match(r"(\w+)=(\d+)", line))]
# => [('a', '1'), ('b', '2')]

# without the walrus you'd have to run the regex twice, or write a loop.
# `:=` binds inside the `if` and the value is reusable in the expression.

# ============================================
# Count matches without building the list

sum(1 for x in xs if x % 2 == 0)        # => 3
sum(x % 2 == 0 for x in xs)             # => 3     bools sum as 1/0

# len([x for x in xs if p(x)]) builds a list just to measure it

# ============================================
# Multiple conditions

[x for x in xs if x > 5 and x % 2 == 0]             # => [10, 12, 20]

# stacked ifs mean AND, and read better when the conditions are unrelated:
[x for x in xs
   if x > 5
   if x % 2 == 0]                       # => [10, 12, 20]

# OR needs one condition:
[x for x in xs if x < 5 or x > 15]      # => [3, 20]

# ============================================
# Membership filtering — set, not list

levels = ["info", "error", "debug", "fatal", "warn"]
bad = {"error", "fatal"}                # a SET: O(1) membership

[lv for lv in levels if lv in bad]      # => ['error', 'fatal']

# with a list on the right this is O(n*m). With a set it's O(n).
# free speedup, one character of syntax.

# ============================================
# Non-empty / truthy

[s for s in ["", "hello", "", "world"] if s]        # => ['hello', 'world']
list(filter(None, ["", "hello", None, "world"]))    # => ['hello', 'world']

# filter(None, ...) drops falsy: "", 0, None, [], False.
# if you only mean "not None", say `if s is not None` — 0 is data.

# ============================================
# Filter by a parallel mask

flags = [1, 0, 1, 1, 0, 1]
list(compress(xs, flags))               # => [3, 10, 12, 20]

# compress pairs values with a selector iterable — useful when the
# decision was computed elsewhere (a numpy mask, a DB result, ...)

# ============================================
# Find all duplicates

from collections import Counter
c = Counter([1, 2, 1, 3, 2, 1])
[k for k, n in c.items() if n > 1]      # => [1, 2]

# all values appearing exactly once:
[k for k, n in c.items() if n == 1]     # => [3]

# ============================================
# All primes below n — filter with a computed predicate

def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))

[n for n in range(30) if is_prime(n)]
# => [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

# note all() inside a comprehension — First Match nested in Search All

# ============================================
# All intervals overlapping a range

intervals = [(1, 4), (6, 8), (3, 5), (9, 12)]
lo, hi = 3, 7
[iv for iv in intervals if iv[0] < hi and iv[1] > lo]
# => [(1, 4), (6, 8), (3, 5)]

# the overlap test is "starts before mine ends AND ends after mine starts" —
# easier to get right than enumerating the four overlap cases

# ============================================
# All regex matches in text

text = "a=1, b=22, c=333"
re.findall(r"\d+", text)                # => ['1', '22', '333']
re.findall(r"(\w)=(\d+)", text)         # => [('a','1'), ('b','22'), ('c','333')]

# findall returns STRINGS (or tuples if there are groups).
# for match objects with positions, use finditer:
[(m.group(), m.start()) for m in re.finditer(r"\d+", text)]
# => [('1', 2), ('22', 7), ('333', 13)]

# findall builds a list; finditer is lazy. Same rule as always.

# ============================================
# THE TRAP — filter() is a one-shot iterator

f = filter(lambda x: x % 2 == 0, xs)
list(f)                                 # => [10, 12, 20]
list(f)                                 # => []            already exhausted!

len(f)                                  # TypeError: no len() on a filter
f[0]                                    # TypeError: not subscriptable

# if you need it twice, or need len/indexing, materialize it: list(filter(...))

# ============================================
# Filtering a dict

scores = {"alice": 90, "bob": 45, "carol": 85}
{k: v for k, v in scores.items() if v >= 50}
# => {'alice': 90, 'carol': 85}

# same pattern, dict comprehension. Sets too: {x for x in xs if p(x)}

# ============================================
# Compare

[x for x in xs if p(x)]         # every hit, eager        → Search All
filter(p, xs)                   # every hit, lazy         → Search All
next((x for x in xs if p(x)), None)     # first hit only  → First Match
sum(1 for x in xs if p(x))      # how many               → Search All + count
min(xs, key=f)                  # the single best        → Nearest
partition(p, xs)                # BOTH halves            → Group By Predicate
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|all matches|`[x for x in xs if p(x)]`|
|all matches, lazily|`filter(p, xs)`|
|all non-matches|`[x for x in xs if not p(x)]`|
|matching positions|`[i for i, x in enumerate(xs) if p(x)]`|
|match and transform|`[f(x) for x in xs if p(x)]`|
|filter on a computed value|`if (y := f(x))` walrus|
|just the count|`sum(1 for x in xs if p(x))`|
|all truthy|`filter(None, xs)`|
|filter by a mask|`compress(xs, flags)`|
|matching dict entries|`{k: v for k, v in d.items() if p(v)}`|
|every regex hit|`re.findall` / `re.finditer`|

---

### Key Insight

**Search All is the comprehension, and the comprehension runs out of order.** `[f(x) for x in xs if p(x)]` executes as *for → if → f*, even though `f` is written first. Read it that way and the "filter and map in one pass" shape stops looking clever. The transform is simply the last step, and it only ever sees the survivors.

**What separates this from First Match is cost, not syntax.** Search All is always O(n). It can't short-circuit, because it doesn't know it's finished until the input runs out. That makes it wrong for existence checks (`any` short-circuits), wrong for a single lookup (`next` short-circuits), and wrong for infinite input (a comprehension over `count()` never returns). The list you build is O(k) memory you may not need either — if you're only going to count, sum a generator instead.

There's a subtler recurring bug too: **`filter()` gives you a one-shot iterator with no length and no indexing**, and once exhausted it returns an empty list rather than an error. A pipeline that "worked yesterday" and now returns nothing has usually grown a second consumer of the same iterator. Comprehensions don't have this failure mode, which is a big part of why they're the default.
