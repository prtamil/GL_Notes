# Pattern 20 — Group By Key

## Mental Model

Partition a sequence into **groups based on a key or property**.

Everything with the same key ends up in the same group.

There's no single `group_by` function in Python. The idiom is **`defaultdict(list)` plus a one-line loop**, and it stays a loop for a reason: `itertools.groupby` only groups **adjacent** elements, which is a different pattern entirely (see 06_Compress/Dedupe).

---

## Relationship to Cognitive Verb

```text
Group
   ↓
Group By Key
```

Group By Key is the core **Group** pattern. It groups by a **computed key** rather than by position.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Group by Property|age, department|`defaultdict(list)` + loop|
|Group by Function|even/odd|`d[f(x)].append(x)`|
|Group by First Letter|`"apple"` → `'a'`|`d[s[0]].append(s)`|
|Group by Type|str, int|`d[type(x)].append(x)`|
|Group by Boolean|pass / fail|two-bucket `defaultdict`|
|Group then Transform|groups → counts|dict comprehension over `d.items()`|
|Sorted Groups|keys in order|`groupby(sorted(xs, key=f), key=f)`|
|Count Only|no elements kept|`Counter(f(x) for x in xs)`|

> **Note:** `itertools.groupby` is **not** SQL `GROUP BY`. It starts a new group every time the key *changes*, so it only produces correct global groups if the input is already **sorted by the same key**. When in doubt, use `defaultdict(list)`.

---

## Common Uses

- Group employees by department

- Group students by grade

- Group orders by customer

- Group files by extension

- Group words by length

- Group numbers by parity

- SQL `GROUP BY`

- MapReduce

---

## Hidden Interview Problems

- Group anagrams

- Group words by length

- Group numbers by parity

- Group objects by property

- Bucket records

- Categorize events

---

## Recognition Clues

If you hear:

- Group by

- Bucket

- Categorize

- Classify

- Partition by property

- Collect by key

- Organize by field

Think:

**→ Group By Key**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Group|
|Pattern|Group By Key|
|Output|dict of key → list|
|Key Source|property or function|
|Preserves Group Order|Yes (insertion order since 3.7)|
|Key Requirement|must be hashable|
|Primary Use|Categorization|

---

## Python Recipe Book

```python
# ============================================
# Input

from collections import defaultdict, Counter
from itertools import groupby
from operator import itemgetter, attrgetter

xs = [1, 2, 3, 4, 5, 6, 7, 8]

# ============================================
# The core idiom — memorize this shape

def group_by(f, it):
    d = defaultdict(list)
    for x in it:
        d[f(x)].append(x)
    return dict(d)

# three lines, works on any iterable, one pass, no sorting

# ============================================
# Group even / odd

group_by(lambda n: n % 2 == 0, xs)
# => {False: [1, 3, 5, 7], True: [2, 4, 6, 8]}

# inline, when you only need it once:
d = defaultdict(list)
for n in xs:
    d[n % 2 == 0].append(n)

# ============================================
# Group by remainder

group_by(lambda n: n % 3, xs)
# => {1: [1, 4, 7], 2: [2, 5, 8], 0: [3, 6]}

# keys appear in FIRST-SEEN order, not sorted order

# ============================================
# Group strings by first letter

group_by(lambda s: s[0], ["apple", "ape", "bat", "ball"])
# => {'a': ['apple', 'ape'], 'b': ['bat', 'ball']}

# ============================================
# Group strings by length

group_by(len, ["a", "to", "cat", "dog", "tree"])
# => {1: ['a'], 2: ['to'], 3: ['cat', 'dog'], 4: ['tree']}

# ============================================
# Group dicts by a field

employees = [
    {"name": "Alice", "dept": "IT"},
    {"name": "Bob",   "dept": "HR"},
    {"name": "Carol", "dept": "IT"},
    {"name": "Dave",  "dept": "Sales"},
]

group_by(itemgetter("dept"), employees)
# => {'IT':    [{'name':'Alice',...}, {'name':'Carol',...}],
#     'HR':    [{'name':'Bob',...}],
#     'Sales': [{'name':'Dave',...}]}

# for objects instead of dicts: attrgetter("dept")

# ============================================
# Count elements in each group

{k: len(v) for k, v in group_by(lambda n: n % 2 == 0, xs).items()}
# => {False: 4, True: 4}

# but if you ONLY want counts, never build the lists:
Counter(n % 2 == 0 for n in xs)         # => Counter({False: 4, True: 4})

# ============================================
# Group then extract one field

{k: [e["name"] for e in v]
 for k, v in group_by(itemgetter("dept"), employees).items()}
# => {'IT': ['Alice', 'Carol'], 'HR': ['Bob'], 'Sales': ['Dave']}

# or map while grouping — never materialize the full records:
d = defaultdict(list)
for e in employees:
    d[e["dept"]].append(e["name"])

# ============================================
# Group characters

group_by(lambda c: c, "banana")
# => {'b': ['b'], 'a': ['a', 'a', 'a'], 'n': ['n', 'n']}

Counter("banana")                       # => Counter({'a': 3, 'n': 2, 'b': 1})

# ============================================
# Group by type

group_by(type, [1, "hello", 2.5, True, 7])
# => {<class 'int'>: [1, 7], <class 'str'>: ['hello'],
#     <class 'float'>: [2.5], <class 'bool'>: [True]}

# careful: bool is a SUBCLASS of int, but type() distinguishes them.
# isinstance(True, int) is True — group_by(type, ...) does not care.

# ============================================
# THE TRAP — itertools.groupby is not SQL GROUP BY

words = ["apple", "bat", "ape"]
{k: list(g) for k, g in groupby(words, key=lambda s: s[0])}
# => {'a': ['ape'], 'b': ['bat']}      WRONG — 'apple' was overwritten

# groupby saw a, b, a → THREE groups; the dict comp kept the last 'a'.
# It only works if you sort by the same key first:
{k: list(g) for k, g in groupby(sorted(words, key=lambda s: s[0]),
                                key=lambda s: s[0])}
# => {'a': ['apple', 'ape'], 'b': ['bat']}     correct, but O(n log n)

# defaultdict is O(n) and cannot be wrong. Prefer it.

# ============================================
# When groupby IS the right call — you want sorted keys anyway

key = itemgetter("dept")
{k: [e["name"] for e in g]
 for k, g in groupby(sorted(employees, key=key), key=key)}
# => {'HR': ['Bob'], 'IT': ['Alice', 'Carol'], 'Sales': ['Dave']}

# the sort gives you alphabetical departments for free

# ============================================
# Group anagrams — the classic interview problem

def group_anagrams(words):
    d = defaultdict(list)
    for w in words:
        d["".join(sorted(w))].append(w)     # canonical form as the key
    return list(d.values())

group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
# => [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]

# the whole trick is "what is the key?" — a sorted string is the fingerprint

# ============================================
# Group files by extension

files = ["a.py", "b.txt", "c.py", "d.md"]
group_by(lambda f: f.rsplit(".", 1)[-1], files)
# => {'py': ['a.py', 'c.py'], 'txt': ['b.txt'], 'md': ['d.md']}

# ============================================
# Grouping into a set instead of a list (dedupes as it groups)

d = defaultdict(set)
for e in employees:
    d[e["dept"]].add(e["name"])

# defaultdict(int) → counts, defaultdict(list) → all, defaultdict(set) → unique

# ============================================
# Nested / two-level grouping

d = defaultdict(lambda: defaultdict(list))
for n in xs:
    d[n % 2 == 0][n % 3].append(n)

# a defaultdict of defaultdicts — the lambda is required, since
# defaultdict(defaultdict(list)) would share ONE inner dict

# ============================================
# Compare

group_by(f, xs)                       # all elements, per key   → Group By Key
Counter(f(x) for x in xs)             # counts only             → Histogram
[list(g) for _, g in groupby(xs)]     # ADJACENT runs only      → Dedupe/RLE
{f(x) for x in xs}                    # just the distinct keys  → Distinct
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|group by a computed key|`defaultdict(list)` + `d[f(x)].append(x)`|
|group by a dict field|`itemgetter("dept")` as the key fn|
|group by an object attribute|`attrgetter("dept")`|
|counts per group|`Counter(f(x) for x in xs)`|
|unique members per group|`defaultdict(set)`|
|groups with sorted keys|`groupby(sorted(xs, key=f), key=f)`|
|adjacent runs, not real groups|plain `groupby(xs)`|
|two-level grouping|`defaultdict(lambda: defaultdict(list))`|

---

### Key Insight

**In Python, grouping is a loop rather than a function, and that's fine.** `d[f(x)].append(x)` is one line, one pass, O(n), and it handles input that can't be sorted, can't be ordered, and arrives as a stream. Every "elegant" alternative is worse: `groupby` needs a sort first, and a dict comprehension can't accumulate.

The thing genuinely worth memorising is **how `itertools.groupby` fails**, because it fails *quietly*. Give it `a b a` and it emits three groups. Build a dict from that and you keep only the last one, so your answer has the right shape, the right type, and silently missing rows. It's a **run detector with a grouping name**. If your input isn't sorted by the key, it's the wrong tool.

One last thing: **the interesting part of grouping is never the grouping, it's the key function.** Grouping anagrams is `sorted(word)`. Grouping files is the extension. Grouping by hour is a truncated timestamp. Once you can name the key, everything left is three lines of boilerplate.
