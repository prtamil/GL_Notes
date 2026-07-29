# Pattern 9 — Prefix

## Mental Model

Take the **beginning portion** of a sequence.

In Python the choice comes down to one thing: **`xs[:n]`** for indexable data (eager, needs `len`), or **`islice` / `takewhile`** for iterators and streams (lazy, one pass).

---

## Relationship to Cognitive Verb

```text
Slice
   ↓
Prefix
```

Prefix is a **Slice** pattern that takes elements **from the start** of a sequence.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|First N Elements|`1 2 3`|`xs[:n]`, `islice(it, n)`|
|First Element|`1`|`xs[0]`, `next(it)`|
|First Element, Safe|`None` if empty|`next(iter(xs), None)`|
|First While Condition|`1 2 3`|`itertools.takewhile(pred, xs)`|
|First Matching Element|first even|`next(x for x in xs if pred(x))`|
|All Prefixes|`[] [1] [1,2] [1,2,3]`|`accumulate(xs, lambda a, x: a + [x], initial=[])`|
|Prefix Until Predicate|until match|`takewhile`|
|Test For a Prefix|"starts with"|`str.startswith`, `xs[:n] == p`|
|N Largest / Smallest|top-k|`heapq.nlargest(n, xs)`|

---

## Common Uses

- Preview data

- Pagination (first page)

- File headers

- String prefixes

- Autocomplete

- Initial samples

- Bootstrapping algorithms

- Reading protocol headers

---

## Hidden Interview Problems

- Return first K elements

- Longest common prefix

- Check string starts with prefix

- Read file header

- Process first page of results

- Extract startup records

---

## Recognition Clues

If you hear:

- First N

- Beginning

- Starts with

- Leading elements

- Initial segment

- Header

- Front of sequence

- Prefix

Think:

**→ Prefix**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Slice|
|Pattern|Prefix|
|Direction|Front|
|Size|Fixed or Predicate-based|
|Preserves Order|Yes|
|Includes Entire Sequence|Possible|
|Cost|O(n) copy for `xs[:n]`, O(n) lazy for `islice`|

---

## Python Recipe Book

```python
# ============================================
# Setup

from itertools import islice, takewhile, accumulate, count
import heapq

xs = [1, 2, 3, 4, 5, 6]

# ============================================
# First N elements

xs[:3]                          # => [1, 2, 3]
xs[:100]                        # => [1,2,3,4,5,6]   no IndexError, just clamps

# Slicing NEVER raises for out-of-range bounds. Indexing does.
# xs[100]  → IndexError        xs[100:]  → []

# ============================================
# First N from an iterator / stream

it = iter(xs)
list(islice(it, 3))             # => [1, 2, 3]
list(it)                        # => [4, 5, 6]   islice CONSUMED the first three

# first N of an infinite sequence — where slicing can't help you at all
list(islice(count(), 5))        # => [0, 1, 2, 3, 4]

# ============================================
# First element

xs[0]                           # => 1          raises IndexError if empty
next(iter(xs), None)            # => 1          returns None if empty
next(iter([]), "empty")         # => 'empty'    default form

# the safe idiom for "head or nothing"
head = xs[0] if xs else None

# ============================================
# First element MATCHING a condition — stops at the first hit

next(x for x in xs if x % 2 == 0)               # => 2
next((x for x in xs if x > 99), None)           # => None   (default)

# don't write [x for x in xs if pred][0] — it scans the whole list first

# ============================================
# First while a condition holds — takewhile

list(takewhile(lambda x: x < 4, xs))            # => [1, 2, 3]

# THE distinction that matters:
list(takewhile(lambda x: x < 4, [1, 2, 9, 3]))  # => [1, 2]      stops at 9
[x for x in [1, 2, 9, 3] if x < 4]              # => [1, 2, 3]   keeps scanning

# takewhile = "the leading run".  filter = "every match anywhere".

# ============================================
# All prefixes — accumulate with a growing list

list(accumulate([1, 2, 3, 4], lambda acc, x: acc + [x], initial=[]))
# => [[], [1], [1,2], [1,2,3], [1,2,3,4]]

# the O(n²) copying above is fine for display; for real work just slice:
[xs[:i] for i in range(len(xs) + 1)][:4]
# => [[], [1], [1, 2], [1, 2, 3]]

# ============================================
# Prefix sums — the useful kind of "all prefixes"

list(accumulate([1, 2, 3, 4]))                  # => [1, 3, 6, 10]
list(accumulate([1, 2, 3, 4], initial=0))       # => [0, 1, 3, 6, 10]

# ============================================
# Does it start with a prefix?

"hello.txt".startswith("hello")                 # => True
"a.py".startswith((".py", "a."))                # => True   tuple = any of

xs[:3] == [1, 2, 3]                             # => True   lists

# ============================================
# Longest common prefix — the classic interview question

def lcp(strs):
    if not strs:
        return ""
    for i, group in enumerate(zip(*strs)):      # zip stops at the shortest
        if len(set(group)) > 1:
            return strs[0][:i]
    return min(strs, key=len)

lcp(["flower", "flow", "flight"])               # => 'fl'
lcp(["interspecies", "interstellar"])           # => 'inters'

# zip(*strs) walks the strings column-wise — the prefix ends at the first
# column that isn't unanimous.

# there is also a stdlib shortcut for paths:
import os
os.path.commonprefix(["flower", "flow"])        # => 'flow'

# ============================================
# Pagination — first page

PAGE = 2
xs[:PAGE]                                       # page 1  => [1, 2]
xs[PAGE:PAGE * 2]                               # page 2  => [3, 4]
[xs[i:i + PAGE] for i in range(0, len(xs), PAGE)]   # all pages

# ============================================
# File header — read N lines without loading the file

# with open("data.csv") as f:
#     header = list(islice(f, 5))     # 5 lines, file stays open and lazy

# islice on a file object is why "read the first 5 lines of a 10GB file"
# is a one-liner and not a problem.

# ============================================
# Top-K — a prefix of the SORTED sequence

heapq.nlargest(3, [5, 1, 9, 3, 7])              # => [9, 7, 5]
heapq.nsmallest(3, [5, 1, 9, 3, 7])             # => [1, 3, 5]

sorted([5, 1, 9, 3, 7], reverse=True)[:3]       # same, but sorts everything
# nlargest is O(n log k); the sort is O(n log n). For small k, use heapq.

# ============================================
# Drop the prefix instead of taking it

xs[3:]                                          # => [4, 5, 6]
list(islice(iter(xs), 3, None))                 # => [4, 5, 6]   lazy version

# ============================================
# Compare

xs[:3]                              # first 3, by COUNT     → Prefix
list(takewhile(lambda x: x < 4, xs))# leading run, by VALUE  → Prefix
xs[-3:]                             # last 3                → Suffix
xs[0], xs[1:]                       # one + the rest        → Head & Tail
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|first n|`xs[:n]`|
|first n, lazily|`islice(it, n)`|
|first element|`xs[0]`|
|first element, safely|`next(iter(xs), default)`|
|first match|`next(x for x in xs if pred(x))`|
|the leading run|`takewhile(pred, xs)`|
|every match|`filter(pred, xs)` — not the same thing|
|first n lines of a file|`islice(f, n)`|
|top k|`heapq.nlargest(k, xs)`|

---

### Key Insight

**"First N" and "first while" are two different patterns sharing a word.** `islice` and `[:n]` cut by **count**. `takewhile` cuts by **condition** and stops the instant the condition fails. Mixing up `takewhile` and `filter` — one stops, the other keeps scanning — is the most common bug in this pattern by a mile.

The other thing worth burning in: **slicing copies, `islice` doesn't.** On a list of six that makes no difference. On a 10 GB log file or an infinite generator it's the difference between a one-liner and something you simply can't do. When your source is a stream, prefix is the *only* slice pattern still available, which is why `islice(f, n)` turns up everywhere in real Python.
