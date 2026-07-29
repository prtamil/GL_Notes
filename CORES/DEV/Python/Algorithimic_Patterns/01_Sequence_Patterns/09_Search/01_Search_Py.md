# Pattern 26 — First Match

## Mental Model

Traverse a sequence until the **first element satisfying a condition** is found, then **stop immediately**.

Unlike **Filter**, which returns **all matching elements**, **First Match** returns only the first one.

Python's spelling is **`next(x for x in xs if p(x), default)`** — a generator expression that is never fully consumed, so the scan stops on the first hit. The `default` is not optional in practice: without it, "not found" is a `StopIteration`.

---

## Relationship to Cognitive Verb

```text
Search
   ↓
First Match
```

First Match is a **Search** pattern because it searches until a match is found, then terminates.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|First Matching Element|first even|`next((x for x in xs if p(x)), None)`|
|Does Any Match?|boolean only|`any(p(x) for x in xs)`|
|First Truthy Value|first non-`None`|`next(filter(None, xs), None)`|
|Find Position|index of first match|`next((i for i, x in enumerate(xs) if p(x)), -1)`|
|Index of a Known Value|`xs.index(3)`|`list.index` (raises `ValueError`)|
|First Matching Record|find by id|`next((u for u in us if u["id"] == 2), None)`|
|Search Then Transform|return a computed value|`next((f(x) for x in xs if p(x)), None)`|
|First N Matches|first 3 hits|`islice((x for x in xs if p(x)), 3)`|
|Substring Search|position in text|`s.find(t)` → `-1`, or `s.index(t)` → raises|

> **Note:** `next()` with a **second argument** returns that default instead of raising `StopIteration`. Always supply it unless a missing match is genuinely a bug — and remember `None` is a poor sentinel if `None` could itself be a valid element.

---

## Common Uses

- Find a user

- Find first error

- Lookup configuration

- Find first available slot

- Search logs

- Validation

- Rule matching

- Event detection

---

## Hidden Interview Problems

- Find first duplicate

- First non-repeating character

- First missing positive

- Search a sorted array

- First valid record

- Find target element

- First index where a condition flips

---

## Recognition Clues

If you hear:

- First match

- Find first

- Stop when found

- Exists

- Search until

- First valid

- First occurrence satisfying

Think:

**→ First Match**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Search|
|Pattern|First Match|
|Stops Early|Yes|
|Returns|first matching value|
|Not Found|the `default`, or `StopIteration`|
|Cost|O(k) where k is the hit position|
|Preserves Order|Yes|
|Primary Use|Early search|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import islice, dropwhile
from collections import Counter
import bisect, re

xs = [3, 7, 10, 12, 15, 20]

# ============================================
# The idiom — memorize the parentheses

next((x for x in xs if x % 2 == 0), None)       # => 10

# the inner parens are REQUIRED: next() takes two arguments, so the
# genexp must be wrapped or Python reads it as next(genexp_arg, None_arg)
# with a syntax error.

# it stops at 10 — 12, 15, 20 are never even generated.

# ============================================
# Without a default — a missing match is an exception

next(x for x in xs if x > 100)
# StopIteration

# use this ONLY when "not found" means the program is wrong.
# in a generator function, a leaking StopIteration becomes a
# RuntimeError (PEP 479) — a genuinely confusing failure.

# ============================================
# First number greater than 10

next((x for x in xs if x > 10), None)           # => 12

# ============================================
# Does anything match? — don't fetch what you won't use

any(x % 2 == 0 for x in xs)                     # => True
all(x > 0 for x in xs)                          # => True

# any/all also short-circuit. They are the boolean form of this pattern.

# empty input: any([]) is False, all([]) is True. The second one
# surprises people — "all zero elements pass" is vacuously true.

# ============================================
# First truthy value

next(filter(None, [None, False, "", "hello", 0]), None)     # => 'hello'

# filter(None, xs) drops every falsy element — 0 and "" go too.
# if you mean "first not-None", say so:
next((x for x in [None, False, 0] if x is not None), None)  # => False

# ============================================
# Find the first matching record

users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Carol"},
]

next((u for u in users if u["id"] == 2), None)
# => {'id': 2, 'name': 'Bob'}

# if you do this in a loop over many ids, build an index ONCE instead:
by_id = {u["id"]: u for u in users}
by_id.get(2)                            # => O(1) forever after

# n lookups × O(n) scan = O(n²). The dict is the fix, not a faster scan.

# ============================================
# Find the INDEX of the first match

next((i for i, x in enumerate(xs) if x % 2 == 0), -1)       # => 2

# for a known value, the list method is shorter but RAISES:
xs.index(12)                            # => 3
# xs.index(99)                          # ValueError: 99 is not in list

# .index takes a start offset — the "find the next one after i" idiom:
xs.index(12, 2)                         # => 3

# ============================================
# Return a computed value, not the element

next((x * 10 for x in xs if x % 2 == 0), None)              # => 100

# transform INSIDE the genexp — the transform runs once, on the hit only

# ============================================
# filter vs next — the whole distinction

[x for x in xs if x % 2 == 0]           # => [10, 12, 20]   scans everything
next((x for x in xs if x % 2 == 0), None)       # => 10     stops at index 2

# on a 10-million-element list where the hit is early, that's the
# difference between milliseconds and seconds. On an infinite
# generator, it's the difference between an answer and a hang.

# ============================================
# First non-empty string

next((s for s in ["", "", "hello", "world"] if s), None)    # => 'hello'

# ============================================
# First element in a set of interesting values

levels = ["info", "debug", "warn", "error", "fatal"]
bad = {"error", "fatal"}
next((lv for lv in levels if lv in bad), None)              # => 'error'

# `in` against a SET is O(1); against a list it's O(n) per element

# ============================================
# First duplicate — the classic

def first_duplicate(it):
    seen = set()
    for x in it:
        if x in seen:
            return x
        seen.add(x)
    return None

first_duplicate([2, 5, 3, 5, 2])        # => 5     (5 repeats before 2 does)

# note it returns on the second SIGHTING, not the first — read the
# question carefully, these differ

# first non-repeating character (two passes, still O(n)):
def first_unique(s):
    c = Counter(s)
    return next((ch for ch in s if c[ch] == 1), None)

first_unique("swiss")                   # => 'w'

# ============================================
# First N matches — not all of them

list(islice((x for x in xs if x % 2 == 0), 2))              # => [10, 12]

# islice over a genexp: still lazy, still stops early

# ============================================
# Skip until, then take — dropwhile is "first match" that keeps the tail

list(dropwhile(lambda x: x < 12, xs))   # => [12, 15, 20]

# next() gives you the element; dropwhile gives you everything from
# there on. Useful for "find the header line, then read the body".

# ============================================
# Sorted input? Don't scan — binary search

s = [10, 15, 22, 30, 42, 55]
i = bisect.bisect_left(s, 22)           # => 2       first index >= 22
s[i] if i < len(s) and s[i] == 22 else None                 # => 22

# "first element >= target" is bisect_left; "first element > target"
# is bisect_right. O(log n) instead of O(n) — but only if sorted.

# ============================================
# Text search — three tools, three failure modes

text = "error: disk full"
text.find("disk")                       # => 7      -1 if absent
text.index("disk")                      # => 7      ValueError if absent
"disk" in text                          # => True   just the boolean

m = re.search(r"\w+:", text)            # => match object, or None
m.group() if m else None                # => 'error:'

# re.search finds the first match anywhere; re.match only at the start.
# ALWAYS check for None before .group() — that's the usual crash.

# ============================================
# Guarding the not-found case — pick a real sentinel

MISSING = object()                      # unmistakable, unlike None
found = next((x for x in xs if x > 100), MISSING)
if found is MISSING:
    ...                                 # genuinely absent

# use this when None, 0, or "" are legitimate values in your data

# ============================================
# Compare

next((x for x in xs if p(x)), None)     # first hit, stops    → First Match
[x for x in xs if p(x)]                 # every hit           → Search All
any(p(x) for x in xs)                   # yes/no, stops       → First Match
min(xs, key=f)                          # BEST hit, scans all → Nearest
bisect_left(sorted_xs, t)               # O(log n) position   → First Match
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|the first match|`next((x for x in xs if p(x)), None)`|
|just yes or no|`any(p(x) for x in xs)`|
|the first index|`next((i for i, x in enumerate(xs) if p(x)), -1)`|
|the index of a known value|`xs.index(v)` (raises!)|
|the first truthy|`next(filter(None, xs), None)`|
|a transformed first hit|`next((f(x) for x in xs if p(x)), None)`|
|the first n hits|`islice(genexp, n)`|
|everything from the hit onward|`dropwhile(...)`|
|a fast lookup, repeatedly|build a `dict` index once|
|a fast lookup, sorted data|`bisect_left`|
|first substring position|`s.find(t)` → `-1`|
|an unambiguous "absent"|`MISSING = object()`|

---

### Key Insight

**The parentheses are the pattern.** `next((x for x in xs if p(x)), None)` reads as noise until you see what each piece buys: the generator expression makes the scan lazy so it stops at the first hit, and the second argument to `next` converts "not found" from an exception into a value. Drop the default and a routine miss becomes a `StopIteration` — which inside a generator function turns into a `RuntimeError` with a stack trace that points nowhere useful.

**Early termination is the entire point, and it is invisible in the output.** `next(...)` and `[... ][0]` return the same element on the same data; they differ only in how much work happened. On a large list that's a constant factor, on an infinite generator it's correctness. Any time you write `[x for x in xs if p(x)][0]` you have built the whole list to throw away all but one element.

The trap worth internalizing is the **repeated** first match. One `next()` scan is O(n) and fine. The same scan inside a loop over n keys is O(n²), and it never looks like a mistake because each individual line is idiomatic. The moment you search the same collection more than a couple of times, stop searching it — **build a `dict` once and look up forever**, or sort it and `bisect`.
