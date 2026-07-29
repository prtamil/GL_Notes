# Pattern 23 — Sort

## Mental Model

Rearrange a sequence into a **defined order** based on natural ordering or a custom key.

**Group** splits data into buckets. **Sort** gives you back **one ordered sequence**.

You get exactly two entry points. **`sorted(xs)`** takes any iterable and returns a new list. **`xs.sort()`** rearranges a list in place and returns `None`. Both run **Timsort**: stable, O(n log n), and close to linear when the input is already partly ordered.

---

## Relationship to Cognitive Verb

```text
Order
   ↓
Sort
```

Sort is the core **Order** pattern. It puts the elements into a consistent order.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Ascending Sort|`1 2 3`|`sorted(xs)`|
|Descending Sort|`3 2 1`|`sorted(xs, reverse=True)`|
|Sort by Property|age, name|`sorted(xs, key=itemgetter("age"))`|
|Sort by Multiple Keys|dept then age|`key=itemgetter("dept", "age")`|
|Mixed Directions|dept ↑, age ↓|`key=lambda p: (p["dept"], -p["age"])`|
|In-place Sort|mutate a list|`xs.sort()`|
|Top K|largest 3|`heapq.nlargest(3, xs)`|
|Custom Comparator|domain order|`key=cmp_to_key(cmp)`|
|Keep Sorted|streaming inserts|`bisect.insort`|

> **Note:** `sorted` takes a **key function**, not a comparator. The key is called **once per element** (Schwartzian transform, built in) — so `key=len` is cheap even when the comparison isn't.

---

## Common Uses

- Leaderboards

- Ranking

- Alphabetical ordering

- Date ordering

- Sorting records

- Report generation

- Preparing binary search

- Data presentation

---

## Hidden Interview Problems

- Sort an array

- Sort intervals

- Merge overlapping intervals

- Top K elements

- Sort by frequency

- Custom object sorting

- Sort a nearly-sorted array

---

## Recognition Clues

If you hear:

- Sort

- Order

- Rank

- Ascending

- Descending

- Alphabetical

- Smallest first

- Largest first

Think:

**→ Sort**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Order|
|Pattern|Sort|
|Algorithm|Timsort — stable, O(n log n)|
|Rearranges Elements|Yes|
|Preserves All Elements|Yes|
|`sorted()` Returns|a new `list`, always|
|`.sort()` Returns|`None` (mutates in place)|
|Primary Use|Ordering|

---

## Python Recipe Book

```python
# ============================================
# Input

from operator import itemgetter, attrgetter
from functools import cmp_to_key
from collections import Counter
import heapq, bisect, locale

xs = [5, 3, 1, 4, 2]

# ============================================
# Ascending sort

sorted(xs)                              # => [1, 2, 3, 4, 5]     new list
xs.sort()                               # => None                mutates xs!

# THE classic bug: `xs = xs.sort()` sets xs to None.
# sorted() when you want a value; .sort() when you want a side effect.

# sorted() takes ANY iterable and always gives back a list:
sorted({3, 1, 2})                       # => [1, 2, 3]
sorted({"b": 2, "a": 1})                # => ['a', 'b']    keys only
sorted("cba")                           # => ['a', 'b', 'c']   a LIST of chars
"".join(sorted("cba"))                  # => 'abc'             back to a string

# ============================================
# Descending sort

sorted(xs, reverse=True)                # => [5, 4, 3, 2, 1]
sorted(xs)[::-1]                        # same result, but loses stability

# reverse=True keeps ties in ORIGINAL order; [::-1] flips them.
# Always prefer reverse=True.

# ============================================
# Sort strings

sorted(["pear", "apple", "banana"])     # => ['apple', 'banana', 'pear']

# it's a CODEPOINT sort, so uppercase wins:
sorted(["banana", "Apple"])             # => ['Apple', 'banana']
sorted(["banana", "Apple"], key=str.lower)      # => ['Apple', 'banana']

# for real human ordering use locale.strxfrm or PyICU
sorted(["ä", "z", "a"], key=locale.strxfrm)     # locale-aware

# ============================================
# Sort by length

sorted(["pear", "kiwi", "banana", "fig"], key=len)
# => ['fig', 'pear', 'kiwi', 'banana']

# 'pear' before 'kiwi' — both length 4, and the sort is STABLE
# so their input order survives

# ============================================
# Sort dicts by a field

employees = [
    {"name": "Bob",   "age": 30},
    {"name": "Alice", "age": 25},
    {"name": "Carol", "age": 35},
]

sorted(employees, key=itemgetter("age"))
# => [{'name':'Alice','age':25}, {'name':'Bob','age':30}, {'name':'Carol','age':35}]

sorted(employees, key=lambda e: e["age"])       # same, one more character

# for objects: key=attrgetter("age")

# ============================================
# Sort by multiple keys — a TUPLE key

people = [
    {"dept": "IT", "age": 30},
    {"dept": "HR", "age": 25},
    {"dept": "IT", "age": 22},
    {"dept": "HR", "age": 35},
]

sorted(people, key=itemgetter("dept", "age"))
# => [{'dept':'HR','age':25}, {'dept':'HR','age':35},
#     {'dept':'IT','age':22}, {'dept':'IT','age':30}]

# tuples compare left to right — that IS multi-key sorting

# ============================================
# Mixed directions — the two ways

# numeric secondary key: negate it
sorted(people, key=lambda p: (p["dept"], -p["age"]))
# => HR 35, HR 25, IT 30, IT 22

# non-numeric: sort twice, LEAST significant key FIRST (stability does the rest)
tmp = sorted(employees, key=itemgetter("name"), reverse=True)
sorted(tmp, key=itemgetter("age"))
# age ascending, name descending within equal ages

# this only works because Timsort is stable — memorize the order:
# last sort = primary key

# ============================================
# Sort by frequency

c = Counter([1, 2, 1, 3, 2, 1, 4])
sorted(c.items(), key=itemgetter(1), reverse=True)
# => [(1, 3), (2, 2), (3, 1), (4, 1)]

c.most_common()                         # => same thing, already written

# most frequent first, then alphabetically on ties:
sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))
# => [(1, 3), (2, 2), (3, 1), (4, 1)]

# ============================================
# Sort a dict by value

scores = {"alice": 90, "bob": 75, "carol": 85}
dict(sorted(scores.items(), key=itemgetter(1), reverse=True))
# => {'alice': 90, 'carol': 85, 'bob': 75}

# dicts keep insertion order, so a sorted dict STAYS sorted (until you add)

# ============================================
# Custom comparator — the escape hatch

def by_len_desc(a, b):
    return len(b) - len(a)              # negative → a first

sorted(["a", "apple", "cat", "banana"], key=cmp_to_key(by_len_desc))
# => ['banana', 'apple', 'cat', 'a']

# only when the order can't be expressed as a key — e.g. a partial order,
# or "compare a to b" logic that isn't a per-element value.
# cmp_to_key is SLOW: O(n log n) comparator calls vs n key calls.

# ============================================
# Top K without a full sort

heapq.nlargest(3, xs)                   # => [5, 4, 3]
heapq.nsmallest(3, xs)                  # => [1, 2, 3]

heapq.nlargest(2, employees, key=itemgetter("age"))
# => [{'name':'Carol','age':35}, {'name':'Bob','age':30}]

# O(n log k) instead of O(n log n). For k == 1 just use max()/min();
# for k close to n just sort.

max(employees, key=itemgetter("age"))   # => {'name': 'Carol', 'age': 35}

# ============================================
# Sort intervals — the setup for half of all interval problems

intervals = [(3, 5), (1, 4), (6, 8), (2, 3)]
sorted(intervals)                       # => [(1,4), (2,3), (3,5), (6,8)]

# tuples already sort by start then end — no key needed.
# merging overlaps, after sorting, is one pass:
merged = []
for lo, hi in sorted(intervals):
    if merged and lo <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
    else:
        merged.append((lo, hi))
# merged => [(1, 5), (6, 8)]

# ============================================
# THE TRAP — mixed types don't compare

sorted([1, "two", 3])
# TypeError: '<' not supported between instances of 'str' and 'int'

# None is the usual culprit in real data:
rows = [{"age": 30}, {"age": None}, {"age": 25}]
sorted(rows, key=lambda r: (r["age"] is None, r["age"] or 0))
# => Nones last, everything else ascending

# the bool in the tuple is a "sort group" — False(0) before True(1)

# ============================================
# Sorting is a precondition, not just a presentation step

sorted_xs = sorted(xs)
bisect.bisect_left(sorted_xs, 3)        # => 2      binary search needs sort
[k for k, _ in groupby(sorted(data))]   # groupby needs sort
sorted(data)[len(data) // 2]            # median needs sort

# keep a list sorted as it grows (O(n) insert, but no re-sort):
bisect.insort(sorted_xs, 3.5)           # => [1, 2, 3, 3.5, 4, 5]

# ============================================
# Sorting reverses cheaply — reversed() on a sorted list

s = sorted(xs)
list(reversed(s))                       # => [5, 4, 3, 2, 1]     no re-sort

# ============================================
# Compare

sorted(xs)                       # full order, O(n log n)      → Sort
heapq.nlargest(k, xs)            # partial order, O(n log k)   → Top K
max(xs)                          # one element, O(n)           → Search
sorted(set(xs))                  # order + dedupe              → Distinct + Sort
xs.sort()                        # in place, returns None      → mutation
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|a sorted copy|`sorted(xs)`|
|to sort in place|`xs.sort()` (returns `None`!)|
|descending|`sorted(xs, reverse=True)`|
|by a field|`key=itemgetter("age")`|
|by an attribute|`key=attrgetter("age")`|
|by two keys|`key=itemgetter("dept", "age")`|
|one key up, one down|negate the number, or sort twice|
|case-insensitive|`key=str.lower`|
|top k only|`heapq.nlargest(k, xs)`|
|Nones last|`key=lambda x: (x is None, x)`|
|true comparator logic|`key=cmp_to_key(f)`|
|to stay sorted while inserting|`bisect.insort`|

---

### Key Insight

**Python sorts by key, not by comparator, and the key becomes a tuple when you need more than one field.** That one fact covers just about every custom comparison function you'd otherwise write: `(dept, age)` for two ascending keys, `(dept, -age)` for one of each, `(x is None, x)` to shove missing values to the end. The key function runs exactly once per element, so it can be as expensive as you like.

**Stability is what makes multi-pass sorting work.** Timsort never reorders elements that compare equal, so sorting by name and *then* by age gives you age-major, name-minor order. Whatever you sort by last becomes the primary key. It's the only clean way to mix ascending and descending on non-numeric fields, and it's why `reverse=True` isn't the same as `[::-1]`.

One habit worth building: **ask whether you need the full order at all.** `max()` is O(n), `nlargest(k)` is O(n log k), a full sort is O(n log n). Sorting a list to find one element is the most common bit of casual waste in Python. That said, when sorting is the *precondition* for something else — binary search, `groupby`, median, interval merging — it stops being presentation and becomes the algorithm.
