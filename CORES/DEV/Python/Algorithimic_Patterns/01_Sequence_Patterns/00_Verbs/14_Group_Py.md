# Sequence Processing — Verb 14: Group

## Introduction

Often the clearest way to make sense of a sequence is to **put similar things next to each other**.

**Group** carves a sequence into collections based on some shared property or key.

The question you're asking:

> **"Which elements belong together?"**

**Split** cuts by position or boundary. **Group** sorts elements by what they're *like*.

---

# Group → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Group**|Which elements belong together?|`collections.defaultdict(list)`, `collections.Counter`, `itertools.groupby(sorted(...))`, `dict.setdefault`|

> **Note:** There's no `group-by` function in Python. The idiom is a three-line loop: `d = defaultdict(list)`, then `d[f(x)].append(x)`. One pass, O(n), and it works even on data you can't sort.

---

# Common Grouping Patterns

|Pattern|Python|Example Result|
|---|---|---|
|Group by key|`defaultdict(list)`|`d[n % 2 == 0].append(n)` over `[1,2,3,4,5]` → `{False: [1,3,5], True: [2,4]}`|
|Group by a field|`itemgetter`|`d[e["dept"]].append(e)`|
|Count groups|`Counter`|`Counter("aba")` → `Counter({'a': 2, 'b': 1})`|
|Group consecutive elements|`groupby`|`[list(g) for _,g in groupby([1,3,2,4,5,7], key=lambda n: n%2)]` → `[[1,3],[2,4],[5,7]]`|
|Group by a computed value|`defaultdict(list)`|`d[len(w)].append(w)` over `["cat","dog","apple"]` → `{3: ['cat','dog'], 5: ['apple']}`|
|Group with sorted keys|`groupby(sorted(...))`|`{k: list(g) for k,g in groupby(sorted(xs, key=f), key=f)}`|
|Group into unique sets|`defaultdict(set)`|`d[k].add(v)`|
|Two-level grouping|nested defaultdict|`defaultdict(lambda: defaultdict(list))`|

---

# The Python-specific catches

**`itertools.groupby` is not SQL's `GROUP BY`.** It opens a new group every time the key *changes*, so unsorted input gives you the same key several times over, and building a dict from that quietly keeps only the last one. Sort first, or reach for `defaultdict`.

**Group keys have to be hashable.** A list key raises `TypeError`. Convert it to a tuple.

**If all you need is counts, don't build the lists at all.** `Counter(f(x) for x in xs)` keeps one integer per key instead of a whole list.

---

# One Sentence to Remember

> **Group sorts a sequence into buckets of things that share a key. The grouping is never the interesting part; the key function is.**
