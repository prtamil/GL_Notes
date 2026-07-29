# Pattern 17 — Distinct

## Mental Model

Keep **only the first occurrence** of each unique element and discard all later duplicates.

Unlike **Dedupe**, which removes only **consecutive duplicates**, **Distinct** removes duplicates **regardless of where they appear**.

Python's headline idiom is **`dict.fromkeys(xs)`** — because dicts have preserved insertion order since 3.7, that one call is "distinct, order-preserving" with no loop and no helper.

---

## Relationship to Cognitive Verb

```text
Compress
    ↓
Distinct
```

Distinct is a **Compress** pattern because it reduces a sequence by eliminating repeated values.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Distinct Values (ordered)|`1 2 3`|`list(dict.fromkeys(xs))`|
|Distinct Values (unordered)|`{1,2,3}`|`set(xs)`|
|Distinct by Key|unique `id`|`{r["id"]: r for r in xs}` (keeps **last**)|
|Distinct by Key, first wins|unique `id`|`dict.fromkeys` on the key, or a `seen` set|
|Count Unique Values|`3`|`len(set(xs))`|
|Distinct After Transform|ignore case|`dict.fromkeys(s.lower() for s in xs)`|
|Distinct Unhashable Items|dicts, lists|a `seen` list, or key on a frozen form|
|Distinct, Lazily|streams|generator with a `seen` set|

> **Note:** `dict.fromkeys` preserves the **first occurrence and original order**; `set` removes duplicates but makes **no order guarantee**. Both require **hashable** elements.

---

## Common Uses

- Remove duplicate records

- Unique IDs

- Unique tags

- Remove repeated words

- Deduplicate search results

- Unique user list

- Data cleaning

- Preprocessing

---

## Hidden Interview Problems

- Remove duplicates from an array

- Count unique elements

- Find unique words

- Deduplicate records

- Keep first occurrence

- Remove repeated IDs

---

## Recognition Clues

If you hear:

- Unique

- Remove duplicates

- Deduplicate

- First occurrence

- Unique values

- Eliminate repeats

- Remove repeated items

Think:

**→ Distinct**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Compress|
|Pattern|Distinct|
|Removes|All duplicate values|
|Preserves Order|Yes (with `dict.fromkeys`)|
|Keeps|First occurrence|
|Primary Use|Deduplication|
|Requires|Hashable elements|

---

## Python Recipe Book

```python
# ============================================
# Input

from collections import Counter
from itertools import groupby, islice, count

xs = [1, 2, 1, 3, 2, 4, 1, 5]

# ============================================
# Distinct values, order preserved — THE idiom

list(dict.fromkeys(xs))                 # => [1, 2, 3, 4, 5]

# dict.fromkeys builds {1:None, 2:None, ...}; dicts keep insertion
# order (guaranteed since 3.7), so the keys come back first-seen-first.

# ============================================
# Distinct values, order NOT preserved

set(xs)                                 # => {1, 2, 3, 4, 5}
sorted(set(xs))                         # => [1, 2, 3, 4, 5]  if you want order

# set() looks ordered for small ints — that's a coincidence of hashing.
# Never rely on it.
list(set(["banana", "apple", "cherry"]))    # order is arbitrary

# ============================================
# Count unique values

len(set(xs))                            # => 5

# ============================================
# Distinct after a transformation

list(dict.fromkeys(s.lower() for s in ["Apple", "APPLE", "Banana", "banana"]))
# => ['apple', 'banana']

# ============================================
# Remove duplicate characters

"".join(dict.fromkeys("banana"))        # => 'ban'

# ============================================
# Distinct BY a key — keeping the LAST occurrence

users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 1, "name": "Alice Updated"},
]

list({u["id"]: u for u in users}.values())
# => [{'id': 1, 'name': 'Alice Updated'}, {'id': 2, 'name': 'Bob'}]

# a later key OVERWRITES the value but KEEPS the original position.
# Alice stays first, with the updated content.

# ============================================
# Distinct BY a key — keeping the FIRST occurrence

# There is no one-liner for this. The dict comprehension ALWAYS keeps the
# last value, and reversing the input to fix that also reverses the output
# order — you'd have to un-reverse it, and then the positions no longer
# follow first occurrence. Just write the loop:

def distinct_by(xs, key):
    seen = set()
    out = []
    for x in xs:
        k = key(x)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out

distinct_by(users, lambda u: u["id"])
# => [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]

# first-vs-last is a real product decision — say which one you meant.

# ============================================
# The lazy version — for streams and early exit

def distinct(it, key=lambda x: x):
    seen = set()
    for x in it:
        k = key(x)
        if k not in seen:
            seen.add(k)
            yield x

list(distinct(xs))                      # => [1, 2, 3, 4, 5]

list(islice(distinct(x % 7 for x in count()), 7))   # => [0,1,2,3,4,5,6]
# works on an infinite source; dict.fromkeys never would.

# ============================================
# Distinct on UNHASHABLE elements

rows = [{"a": 1}, {"a": 1}, {"a": 2}]
# set(rows)                             # TypeError: unhashable type: 'dict'

# key on a hashable projection of the item
list(distinct(rows, key=lambda d: tuple(sorted(d.items()))))
# => [{'a': 1}, {'a': 2}]

# for lists of lists, tuple() is enough
pts = [[0, 0], [1, 1], [0, 0]]
[list(t) for t in dict.fromkeys(map(tuple, pts))]
# => [[0, 0], [1, 1]]

# ============================================
# Distinct vs set — order is the whole difference

list(dict.fromkeys([3, 1, 2, 3, 2, 1]))     # => [3, 1, 2]     first-seen order
sorted(set([3, 1, 2, 3, 2, 1]))             # => [1, 2, 3]     sorted order

# ============================================
# Unique words

list(dict.fromkeys(["the", "cat", "the", "sat", "cat"]))
# => ['the', 'cat', 'sat']

# ============================================
# The values that appear MORE than once

c = Counter(xs)
[v for v, n in c.items() if n > 1]      # => [1, 2]
[v for v, n in c.items() if n == 1]     # => [3, 4, 5]   truly unique

# "unique" is ambiguous in English: distinct (one of each) vs
# unique (appeared exactly once). Counter answers the second.

# ============================================
# Set algebra — distinct across sequences

a, b = [1, 2, 3], [2, 3, 4]
set(a) | set(b)                         # => {1,2,3,4}   union
set(a) & set(b)                         # => {2,3}       intersection
set(a) - set(b)                         # => {1}         difference
set(a) ^ set(b)                         # => {1,4}       symmetric difference

# order-preserving intersection
bset = set(b)
[x for x in dict.fromkeys(a) if x in bset]      # => [2, 3]

# ============================================
# Does it contain duplicates at all?

len(xs) != len(set(xs))                 # => True

# ============================================
# Compare

list(dict.fromkeys(xs))         # ALL duplicates removed   → Distinct
set(xs)                         # same, order lost         → Distinct
[k for k, _ in groupby(xs)]     # only ADJACENT duplicates → Dedupe
Counter(xs)                     # keep the counts instead  → Summarize
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|unique, keep order|`list(dict.fromkeys(xs))`|
|unique, order irrelevant|`set(xs)`|
|how many unique|`len(set(xs))`|
|unique by a field, last wins|`{key(x): x for x in xs}.values()`|
|unique by a field, first wins|a `seen` set in a loop|
|unique, lazily / infinite|generator + `seen` set|
|unique dicts or lists|key on `tuple(...)`|
|appeared exactly once|`Counter` + `n == 1`|
|"are there duplicates?"|`len(xs) != len(set(xs))`|

---

### Key Insight

**`dict.fromkeys` is Python's `distinct`.** It exists because the language already needed ordered hash maps, so order-preserving deduplication came free — no import, no helper function, one pass, O(n).

Two things it can't do, and both have the same cause: it needs **hashable** elements, and it needs a **finite** sequence. When either fails, fall back to the explicit `seen` set in a generator — which is also the version you want when deduplicating *by a key*, because that's where you have to choose whether the **first or the last** occurrence wins. `{k: v for ...}` silently keeps the last; a `seen` set keeps the first. That difference is invisible in test data where the duplicates are identical, and very visible in production where they aren't.
