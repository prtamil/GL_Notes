# Pattern 22 — Histogram (Frequencies)

## Mental Model

Count **how many times each unique value appears** in a sequence.

Unlike **Group By Key**, which stores the actual elements, a **Histogram** stores only their **counts**.

Python gives this one a dedicated type: **`collections.Counter`**. It is a `dict` subclass, so everything you know about dicts still applies — plus `.most_common()`, and arithmetic between counters.

---

## Relationship to Cognitive Verb

```text
Group
   ↓
Histogram (Frequencies)
```

Histogram is a **Group** pattern that summarizes each group as a **frequency count** instead of keeping all the elements.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Count Frequencies|`{'a': 3}`|`Counter(xs)`|
|Frequency After Transform|ignore case|`Counter(s.lower() for s in xs)`|
|Frequency by Property|count departments|`Counter(e["dept"] for e in xs)`|
|Sort by Frequency|most common first|`c.most_common()`|
|Top N Frequent|top 3|`c.most_common(3)`|
|Mode|single most common|`c.most_common(1)[0][0]`|
|Manual Histogram|custom counting|`defaultdict(int)` + `d[k] += 1`|
|Combine Histograms|merge two counts|`c1 + c2`|
|Difference|what's missing|`c1 - c2`|

> **Note:** Think of `Counter` as **`group_by` followed by `len`** — but without ever building the lists. A missing key returns **`0`**, not a `KeyError`, and that lookup does **not** insert the key (unlike `defaultdict`).

---

## Common Uses

- Word count

- Character frequency

- Vote counting

- Event statistics

- Error frequencies

- Log analysis

- Category counts

- Data summarization

---

## Hidden Interview Problems

- Most frequent element

- Top K frequent elements

- Character count

- Word frequency

- Count duplicate values

- Mode of a dataset

- Anagram check

- First non-repeating character

---

## Recognition Clues

If you hear:

- Count occurrences

- Frequency

- Histogram

- Distribution

- Most common

- Top K frequent

- Count duplicates

- Mode

Think:

**→ Histogram (Frequencies)**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Group|
|Pattern|Histogram (Frequencies)|
|Output|`Counter` — value → count|
|Preserves Original Elements|No|
|Aggregation|Count|
|Missing Key|returns `0`, no insert|
|Element Requirement|hashable|
|Primary Use|Frequency analysis|

---

## Python Recipe Book

```python
# ============================================
# Input

from collections import Counter, defaultdict

xs = [1, 2, 1, 3, 2, 1, 4, 3, 1]

# ============================================
# Count frequencies

Counter(xs)
# => Counter({1: 4, 2: 2, 3: 2, 4: 1})

# it IS a dict — c[1], c.items(), c.keys() all work as usual
Counter(xs)[1]                          # => 4
Counter(xs)[99]                         # => 0     no KeyError, no insert

# ============================================
# Character frequency

Counter("banana")
# => Counter({'a': 3, 'n': 2, 'b': 1})

# ============================================
# Word frequency

Counter(["the", "cat", "the", "sat", "cat", "the"])
# => Counter({'the': 3, 'cat': 2, 'sat': 1})

# from raw text, the one-liner everyone writes:
text = "the cat the sat the"
Counter(text.lower().split())           # => Counter({'the': 3, 'cat': 1, 'sat': 1})

# ============================================
# Frequency after transformation

Counter(s.lower() for s in ["Apple", "APPLE", "Banana", "banana"])
# => Counter({'apple': 2, 'banana': 2})

# normalize INSIDE the generator — never count then merge afterwards

# ============================================
# Frequency by property

employees = [
    {"name": "Alice", "dept": "IT"},
    {"name": "Bob",   "dept": "HR"},
    {"name": "Carol", "dept": "IT"},
    {"name": "Dave",  "dept": "Sales"},
    {"name": "Eve",   "dept": "IT"},
]

Counter(e["dept"] for e in employees)
# => Counter({'IT': 3, 'HR': 1, 'Sales': 1})

# ============================================
# Sort by frequency

Counter(xs).most_common()
# => [(1, 4), (2, 2), (3, 2), (4, 1)]

# already sorted descending — no key= needed.
# ties keep FIRST-SEEN order (2 before 3), not sorted order

# ============================================
# Top N most frequent

Counter(xs).most_common(2)              # => [(1, 4), (2, 2)]

# most_common(n) uses a heap: O(n log k), not a full sort

# ============================================
# The mode

Counter(xs).most_common(1)[0][0]        # => 1

# raises IndexError on empty input — guard it:
c = Counter(xs)
mode = c.most_common(1)[0][0] if c else None

# ============================================
# Least common — most_common has no reverse flag

Counter(xs).most_common()[-1]           # => (4, 1)
min(Counter(xs).items(), key=lambda kv: kv[1])      # => (4, 1)

# ============================================
# Manual histogram — the pre-Counter idiom, still worth knowing

d = defaultdict(int)
for x in xs:
    d[x] += 1
dict(d)                                 # => {1: 4, 2: 2, 3: 2, 4: 1}

# plain dict version:
d = {}
for x in xs:
    d[x] = d.get(x, 0) + 1

# use these when the "count" isn't 1 — e.g. summing weights

# ============================================
# Counting weights, not occurrences — Counter can't do this

sales = [("apple", 3), ("banana", 2), ("apple", 5)]
d = defaultdict(int)
for item, qty in sales:
    d[item] += qty
dict(d)                                 # => {'apple': 8, 'banana': 2}

# Counter counts EVENTS. Weighted sums need the loop —
# though Counter(dict(...)).update() can also accept counts:
c = Counter()
for item, qty in sales:
    c[item] += qty                      # => Counter({'apple': 8, 'banana': 2})

# ============================================
# Counter arithmetic — the feature nobody remembers

a = Counter("aabbc")
b = Counter("abbbd")

a + b               # => Counter({'b': 5, 'a': 3, 'c': 1, 'd': 1})   sum
a - b               # => Counter({'a': 1, 'c': 1})    subtract, drops ≤ 0
a & b               # => Counter({'b': 2, 'a': 1})    min — the intersection
a | b               # => Counter({'b': 3, 'a': 2, 'c': 1, 'd': 1})   max

# `-` silently DROPS zero and negative counts. For signed differences
# use c.subtract(other), which mutates in place and keeps negatives.

# ============================================
# Group-by vs histogram

{k: [x for x in xs if x == k] for k in set(xs)}
# => {1: [1,1,1,1], 2: [2,2], 3: [3,3], 4: [4]}     keeps elements

Counter(xs)
# => Counter({1: 4, 2: 2, 3: 2, 4: 1})              keeps counts only

# if the elements are identical anyway, the list is pure waste

# ============================================
# Anagram check — histogram equality

Counter("listen") == Counter("silent")  # => True

# ============================================
# First non-repeating character — two passes, O(n)

def first_unique(s):
    c = Counter(s)
    return next((ch for ch in s if c[ch] == 1), None)

first_unique("swiss")                   # => 'w'

# pass 1 counts, pass 2 scans in ORDER. Counter preserves insertion
# order too, so `next(ch for ch, n in c.items() if n == 1)` also works.

# ============================================
# Duplicates and uniques

c = Counter(xs)
[k for k, n in c.items() if n > 1]      # => [1, 2, 3]     appeared twice+
[k for k, n in c.items() if n == 1]     # => [4]           appeared once
sum(c.values())                         # => 9             back to len(xs)
len(c)                                  # => 4             distinct count

# ============================================
# Expand a histogram back into elements

list(Counter(xs).elements())
# => [1, 1, 1, 1, 2, 2, 3, 3, 4]        sorted by first appearance

# the inverse of Counter() — RLE decode, essentially

# ============================================
# Bucketed histogram — count ranges, not values

scores = [3, 47, 52, 88, 91, 95]
Counter(s // 10 * 10 for s in scores)
# => Counter({90: 2, 0: 1, 40: 1, 50: 1, 80: 1})

# integer division is the cheapest bucketing there is

# ============================================
# A quick ASCII bar chart

for k, n in Counter(xs).most_common():
    print(f"{k:>3} | {'█' * n} {n}")
#   1 | ████ 4
#   2 | ██ 2
#   3 | ██ 2
#   4 | █ 1

# ============================================
# Compare

Counter(xs)                     # value → count            → Histogram
group_by(f, xs)                 # key → elements           → Group By Key
set(xs)                         # which values exist       → Distinct
[(k, len(list(g))) for k, g in groupby(xs)]   # RUN lengths → RLE
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|counts of each value|`Counter(xs)`|
|counts of a field|`Counter(e["k"] for e in xs)`|
|most frequent first|`c.most_common()`|
|top k|`c.most_common(k)`|
|the mode|`c.most_common(1)[0][0]`|
|distinct count|`len(c)`|
|total count back|`sum(c.values())`|
|weighted sums|`defaultdict(int)` + `d[k] += w`|
|merge two histograms|`c1 + c2`|
|what's in a but not b|`c1 - c2`|
|elements back out|`c.elements()`|

---

### Key Insight

**A histogram is a group that threw away its members.** That is the whole economy of it: `group_by` allocates a list per key and holds every element; `Counter` holds one integer per key. When all you will ever call on the group is `len()`, building the list is pure overhead — and on a large stream it is the difference between fitting in memory and not.

`Counter` earns its place in the standard library through the parts people forget: **`most_common(k)` is a heap, not a sort**, so top-K is O(n log k); **a missing key reads as 0 without inserting it**, so you can probe freely inside a comprehension; and **counters do arithmetic** — `a & b` is the multiset intersection that solves "which characters can I build from this bag of letters" in one character.

The limit is worth naming too: **`Counter` counts occurrences, not quantities.** The moment your data says `("apple", 5)` rather than five apples, you are back to `defaultdict(int)` and `d[k] += qty`. Recognizing which of the two you have is the actual skill; the syntax is the easy half.
