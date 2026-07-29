# Pattern 21 — Group By Predicate

## Mental Model

Split a sequence into groups based on whether elements **satisfy one or more conditions**.

Unlike **Group By Key**, where the key can be any computed value, **Group By Predicate** groups according to **boolean conditions**.

In Python the two-bucket case has a name of its own: **partition**. It is not in the standard library, but `itertools.tee` + `filter`/`filterfalse` is the documented recipe, and a single loop is usually clearer.

---

## Relationship to Cognitive Verb

```text
Group
   ↓
Group By Predicate
```

Group By Predicate is a **Group** pattern where each predicate defines a category.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|True / False Groups|even / odd|`d[bool(p(x))].append(x)`|
|Two Comprehensions|small inputs|`[x for x in xs if p(x)]` + `if not p(x)`|
|Lazy Partition|streams|`filter` / `filterfalse` over `tee`|
|Pass / Fail|score ≥ 50|`d[s >= 50].append(s)`|
|None / Not-None|missing values|`x is None` as the key|
|Blank / Non-blank|strings|`not s.strip()` as the key|
|Multi-category|small / medium / large|a `classify()` function returning labels|
|Numeric Bucketing|ranges|`bisect.bisect` over cut points|

> **Note:** A predicate normally creates **two groups** (`True` and `False`). For more than two categories, return labels such as `"small"`, `"medium"`, `"large"` instead of booleans — Python's `match` or a chain of `if/elif` is the natural home for that.

---

## Common Uses

- Pass / Fail classification

- Valid / Invalid records

- Active / Inactive users

- Positive / Negative values

- Error / Success logs

- Data validation

- Rule engines

- Filtering pipelines

---

## Hidden Interview Problems

- Partition by condition

- Separate positive and negative numbers

- Split valid and invalid records

- Categorize values by thresholds

- Bucket data into ranges

- Classify events

---

## Recognition Clues

If you hear:

- Pass or fail

- Valid or invalid

- True or false

- Meets condition

- Categorize by rule

- Threshold

- Bucket by condition

Think:

**→ Group By Predicate**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Group|
|Pattern|Group By Predicate|
|Output|dict of category → list, or a 2-tuple|
|Key Source|boolean or label|
|Preserves Group Order|Yes|
|Passes Over Input|1 (loop) or 2 (comprehensions)|
|Primary Use|Rule-based grouping|

---

## Python Recipe Book

```python
# ============================================
# Input

from collections import defaultdict
from itertools import filterfalse, tee
from bisect import bisect

xs = [-3, -2, -1, 0, 1, 2, 3, 4]

# ============================================
# The partition idiom — one pass, returns (falses, trues)

def partition(pred, it):
    out = ([], [])
    for x in it:
        out[bool(pred(x))].append(x)        # False → 0, True → 1
    return out

# bool indexes the tuple. That is the whole trick.

no, yes = partition(lambda n: n % 2 == 0, xs)
# no  => [-3, -1, 1, 3]
# yes => [-2, 0, 2, 4]

# ============================================
# Group even / odd as a dict

d = defaultdict(list)
for n in xs:
    d[n % 2 == 0].append(n)
dict(d)
# => {False: [-3, -1, 1, 3], True: [-2, 0, 2, 4]}

# ============================================
# Two comprehensions — clearest for small, in-memory input

evens = [n for n in xs if n % 2 == 0]
odds  = [n for n in xs if n % 2]
# two passes and the predicate written twice — fine for 8 items,
# wrong for a generator (it would be exhausted after the first pass)

# ============================================
# Group positive / non-positive

partition(lambda n: n > 0, xs)
# => ([-3, -2, -1, 0], [1, 2, 3, 4])

# ============================================
# Group None / not-None

partition(lambda x: x is None, [1, None, 2, None, 3])
# => ([1, 2, 3], [None, None])

# `is None`, never `== None`, and never a bare truthiness test —
# 0 and "" are falsy but not missing

# ============================================
# Group strings by blank

partition(lambda s: not s.strip(), ["hello", "", " ", "world"])
# => (['hello', 'world'], ['', ' '])

# "" is falsy but " " is TRUTHY — .strip() is what makes them agree

# ============================================
# Pass / fail

scores = [85, 42, 90, 61, 35, 78]
fail, passed = partition(lambda s: s >= 50, scores)
# fail   => [42, 35]
# passed => [85, 90, 61, 78]

# ============================================
# Multi-category classification — name the function, don't inline it

def size(n):
    if n < 10:
        return "small"
    if n < 20:
        return "medium"
    return "large"

d = defaultdict(list)
for n in [3, 8, 12, 17, 21, 30]:
    d[size(n)].append(n)
dict(d)
# => {'small': [3, 8], 'medium': [12, 17], 'large': [21, 30]}

# same shape with match (3.10+):
def size2(n):
    match n:
        case n if n < 10: return "small"
        case n if n < 20: return "medium"
        case _:           return "large"

# ============================================
# Valid / invalid records

users = [
    {"id": 1, "email": "a@test.com"},
    {"id": 2, "email": None},
    {"id": 3, "email": "b@test.com"},
]

invalid, valid = partition(lambda u: u["email"] is not None, users)
# invalid => [{'id': 2, 'email': None}]
# valid   => [{'id': 1, ...}, {'id': 3, ...}]

# the return order is (False, True) — name the variables, don't count

# ============================================
# Group by sign — three buckets, so booleans won't do

def sign(n):
    return "negative" if n < 0 else "zero" if n == 0 else "positive"

d = defaultdict(list)
for n in xs:
    d[sign(n)].append(n)
dict(d)
# => {'negative': [-3, -2, -1], 'zero': [0], 'positive': [1, 2, 3, 4]}

# ============================================
# Numeric bucketing — bisect beats a chain of ifs

cuts   = [0, 10, 20, 50]
labels = ["neg", "0-9", "10-19", "20-49", "50+"]

def bucket(n):
    return labels[bisect(cuts, n)]

[bucket(n) for n in [-5, 0, 7, 15, 30, 99]]
# => ['neg', '0-9', '0-9', '10-19', '20-49', '50+']

# O(log k) instead of O(k), and the cut points stay editable data

# ============================================
# Lazy partition — no list built, input consumed once

def lazy_partition(pred, it):
    a, b = tee(it)                      # tee lets both filters read the stream
    return filterfalse(pred, a), filter(pred, b)

odd_it, even_it = lazy_partition(lambda n: n % 2 == 0, iter(xs))
list(even_it)                           # => [-2, 0, 2, 4]

# WARNING: tee buffers. If you drain one side fully before touching
# the other, tee holds the entire sequence in memory anyway.
# For a big stream, prefer the single loop.

# ============================================
# Just the counts, not the elements

sum(1 for n in xs if n > 0)             # => 4      how many passed
sum(n > 0 for n in xs)                  # => 4      bools sum as 1/0

# all() / any() when you only need the verdict, not the split
all(n > -10 for n in xs)                # => True
any(n == 0  for n in xs)                # => True

# ============================================
# Multiple independent predicates — an element can land in many buckets

rules = {
    "even":     lambda n: n % 2 == 0,
    "positive": lambda n: n > 0,
    "big":      lambda n: abs(n) > 2,
}
d = defaultdict(list)
for n in xs:
    for name, p in rules.items():
        if p(n):
            d[name].append(n)
dict(d)
# => {'even': [-2, 0, 2, 4], 'positive': [1, 2, 3, 4], 'big': [-3, 3, 4]}

# note this is NOT a partition — the buckets overlap and 
# an element matching nothing simply disappears

# ============================================
# Compare

partition(p, xs)                  # 2 buckets, both kept     → Predicate
[x for x in xs if p(x)]           # 1 bucket, rest discarded → Select
group_by(f, xs)                   # n buckets by value       → Group By Key
Counter(p(x) for x in xs)         # counts only              → Histogram
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|two buckets, one pass|`out[bool(pred(x))].append(x)`|
|two buckets, quick and small|two comprehensions|
|two buckets, lazily|`filterfalse`/`filter` over `tee`|
|three or more categories|a named `classify()` returning labels|
|numeric ranges|`bisect(cuts, n)` into a labels list|
|only the count that passed|`sum(p(x) for x in xs)`|
|only a yes/no verdict|`any()` / `all()`|
|overlapping categories|loop the rules, append to each match|

---

### Key Insight

**`bool` is an integer, and that is the entire partition idiom.** `out[bool(pred(x))]` puts falses at index 0 and trues at index 1 with no branch, no dict, and one pass over the data. The same fact makes `sum(p(x) for x in xs)` a counter of passing elements.

The real decision here is **two buckets or many**. A predicate answers yes/no, so it can only ever produce two groups — the moment you need "small/medium/large" you are no longer writing a predicate, you are writing a **classifier**, and it belongs in a named function rather than inlined in the loop. That rename is not cosmetic: a named `size(n)` is testable, reusable, and the place where the next category gets added.

And keep the failure mode in view: **two comprehensions read beautifully and silently break on generators.** The second pass sees an exhausted iterator and returns an empty list — no error, just a missing half. If the input isn't a list, partition with the loop.
