# Pattern 18 — Dedupe

## Mental Model

Remove **consecutive duplicate elements** while keeping duplicates that appear later.

**Distinct** removes **every duplicate**. **Dedupe** only squashes **runs of repeated values**.

The tool for this is **`itertools.groupby`**. Unlike SQL's `GROUP BY`, it only groups **adjacent** equal elements, and that so-called limitation is exactly what turns it into a run detector.

---

## Relationship to Cognitive Verb

```text
Compress
    ↓
Dedupe
```

Dedupe is a **Compress** pattern because it folds repeated **adjacent** values down to one.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Remove Consecutive Duplicates|`1 2 3 2`|`[k for k, _ in groupby(xs)]`|
|Dedupe After Sorting|global dedupe|`groupby(sorted(xs))`|
|Dedupe by Key|adjacent equal keys|`groupby(xs, key=f)`|
|Compress Runs|`AAABBCC → ABC`|`"".join(k for k, _ in groupby(s))`|
|Partition into Runs|`AAA BB`|`[list(g) for _, g in groupby(xs)]`|
|Count Runs|`(3, 2)`|`[len(list(g)) for _, g in groupby(xs)]`|
|Manual Dedupe|streaming|compare each element with the previous|

> **Note:** `groupby` only groups **adjacent** equal elements. If duplicates are separated by other values, each run is reported separately — which is the point. **The group iterator is also consumed as you advance**, so materialize it with `list()` before moving on.

---

## Common Uses

- Compress repeated events

- Remove repeated log entries

- Sensor noise cleanup

- Keyboard repeat filtering

- Consecutive state changes

- Run compression

- Data cleanup

- Stream processing

---

## Hidden Interview Problems

- Remove adjacent duplicates

- Compress repeated characters

- Eliminate repeated log messages

- Simplify state transitions

- Remove duplicate clicks

- Run compression

---

## Recognition Clues

If you hear:

- Consecutive duplicates

- Adjacent duplicates

- Runs

- Collapse repeated values

- Compress repeated characters

- Ignore repeated neighbors

Think:

**→ Dedupe**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Compress|
|Pattern|Dedupe|
|Removes|Adjacent duplicates only|
|Preserves Order|Yes|
|Keeps|First value of each run|
|Primary Use|Run compression|
|Memory|O(1) — no `seen` set needed|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import groupby, pairwise

xs = [1, 1, 2, 2, 2, 3, 2, 2, 4, 4, 5]

# ============================================
# Remove consecutive duplicates

[k for k, _ in groupby(xs)]             # => [1, 2, 3, 2, 4, 5]

# note the second 2 SURVIVES — it is a separate run

# ============================================
# Distinct vs Dedupe — the whole distinction

list(dict.fromkeys(xs))                 # => [1, 2, 3, 4, 5]      Distinct
[k for k, _ in groupby(xs)]             # => [1, 2, 3, 2, 4, 5]   Dedupe

# Distinct needs a `seen` set → O(n) memory, needs hashable elements.
# Dedupe only compares neighbours → O(1) memory, works on a stream.

# ============================================
# Compress repeated characters

"".join(k for k, _ in groupby("aaabbbccccdde"))         # => 'abcde'

# ============================================
# Partition into runs

[list(g) for _, g in groupby(xs)]
# => [[1,1], [2,2,2], [3], [2,2], [4,4], [5]]

# ============================================
# Keep the first element of each run

[k for k, _ in groupby(xs)]             # => [1, 2, 3, 2, 4, 5]

# k IS the first element of the run (or its key) — no need for g[0]

# ============================================
# Count run lengths

[len(list(g)) for _, g in groupby(xs)]  # => [2, 3, 1, 2, 2, 1]

# ============================================
# Run-length encoding (the foundation of pattern 19)

[(k, len(list(g))) for k, g in groupby(xs)]
# => [(1,2), (2,3), (3,1), (2,2), (4,2), (5,1)]

# ============================================
# THE TRAP — the group iterator is consumed as you advance

groups = list(groupby(xs))              # materializing the OUTER level only
[list(g) for _, g in groups]
# => [[], [], [], [], [], []]      ← every single group is empty!

# groupby shares one underlying iterator. Advancing to the next group
# discards whatever you didn't read from the previous one.
# ALWAYS consume each group inside the loop:
[(k, list(g)) for k, g in groupby(xs)]  # correct — list(g) happens in order

# ============================================
# Dedupe after sorting = Distinct (the sort makes duplicates adjacent)

[k for k, _ in groupby(sorted(xs))]     # => [1, 2, 3, 4, 5]
sorted(set(xs))                         # => [1, 2, 3, 4, 5]   simpler

# sorting costs O(n log n) to save the O(n) memory of a set.
# Worth it only when the data is already sorted, or too big for memory.

# ============================================
# Dedupe by key

people = [
    {"id": 1, "name": "Alice"},
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Carol"},
]

[next(g) for _, g in groupby(people, key=lambda p: p["id"])]
# => [{'id':1,'name':'Alice'}, {'id':2,'name':'Bob'}, {'id':3,'name':'Carol'}]

# with a key function, k is the KEY and next(g) is the first full record

from operator import itemgetter
[next(g) for _, g in groupby(people, key=itemgetter("id"))]      # same

# ============================================
# The manual version — O(1) memory, works on any stream

def dedupe(it):
    prev = object()                     # a sentinel that equals nothing
    for x in it:
        if x != prev:
            yield x
            prev = x

list(dedupe(xs))                        # => [1, 2, 3, 2, 4, 5]

# this is what groupby is doing; write it out when you need a
# custom "same as previous" test (tolerance, case-insensitive, ...)

def dedupe_near(it, tol):
    prev = None
    for x in it:
        if prev is None or abs(x - prev) > tol:
            yield x
            prev = x

list(dedupe_near([1.0, 1.01, 1.02, 5.0, 5.01], tol=0.1))    # => [1.0, 5.0]

# ============================================
# Sensor noise / keyboard repeat filtering

readings = ["off", "off", "on", "on", "on", "off", "off"]
[k for k, _ in groupby(readings)]       # => ['off', 'on', 'off']

# 7 readings → 3 state CHANGES. That's the actual signal.

# ============================================
# State transitions — dedupe then pair

states = ["idle", "idle", "run", "run", "stop"]
transitions = list(pairwise(k for k, _ in groupby(states)))
# => [('idle', 'run'), ('run', 'stop')]

# dedupe first, then pairwise — a transition to yourself isn't a transition

# ============================================
# Longest run

max(((k, len(list(g))) for k, g in groupby(xs)), key=lambda kv: kv[1])
# => (2, 3)      the value 2 had the longest run, of length 3

# longest run of consecutive True (a very common interview shape)
flags = [1, 1, 0, 1, 1, 1, 0]
max((len(list(g)) for k, g in groupby(flags) if k), default=0)      # => 3

# ============================================
# Remove repeated log lines

log = ["conn ok", "conn ok", "conn ok", "timeout", "conn ok"]
[(line, n) for line, n in ((k, len(list(g))) for k, g in groupby(log))]
# => [('conn ok', 3), ('timeout', 1), ('conn ok', 1)]

# "last message repeated 3 times" — that's this pattern, verbatim

# ============================================
# groupby is NOT SQL GROUP BY

data = ["a", "b", "a"]
[(k, list(g)) for k, g in groupby(data)]
# => [('a', ['a']), ('b', ['b']), ('a', ['a'])]     THREE groups

# for a real GROUP BY you must sort first, or use a defaultdict:
[(k, list(g)) for k, g in groupby(sorted(data))]
# => [('a', ['a', 'a']), ('b', ['b'])]              two groups

# see 07_Group for the defaultdict/Counter approach

# ============================================
# Compare

[k for k, _ in groupby(xs)]         # adjacent dupes gone  → Dedupe
list(dict.fromkeys(xs))             # all dupes gone       → Distinct
[(k, len(list(g))) for k,g in groupby(xs)]   # runs + counts → RLE
[list(g) for _, g in groupby(xs)]   # the runs themselves  → Group (adjacent)
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|collapse adjacent repeats|`[k for k, _ in groupby(xs)]`|
|the runs themselves|`[list(g) for _, g in groupby(xs)]`|
|run lengths|`[len(list(g)) for _, g in groupby(xs)]`|
|runs by a field|`groupby(xs, key=itemgetter("id"))`|
|the first record of each run|`[next(g) for _, g in groupby(xs, key=…)]`|
|a custom "same" test|write the `prev` loop|
|global dedupe instead|`dict.fromkeys` or `sorted(set(...))`|
|longest run|`max(len(list(g)) for _, g in groupby(xs))`|

---

### Key Insight

**Dedupe is Distinct's streaming sibling.** It only ever compares an element to the one right before it, so it runs in **O(1) memory on an infinite stream** and handles unhashable elements. `set` and `dict.fromkeys` can do neither. When your data arrives as a feed instead of a list, this is usually the only deduplication you can afford.

Burn this `groupby` trap in: **the group iterators are views onto a single shared cursor.** `list(groupby(xs))` hands you groups that are already empty, because materialising the outer level walked straight past all of them. Consume each group *inside* the loop, or you'll get a column of empty lists and no error explaining why.

And here's the sentence that ties this whole family together: **sorting turns Dedupe into Distinct.** Once equal values sit next to each other, removing adjacent duplicates removes all of them. That's why `groupby(sorted(xs))` and `set(xs)` land on the same answer by opposite routes, one trading time for memory and the other memory for time.
