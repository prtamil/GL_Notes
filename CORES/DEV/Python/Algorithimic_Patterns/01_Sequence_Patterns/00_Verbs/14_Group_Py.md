# Sequence Processing — Verb 14: Group

## Introduction

Sometimes the most natural way to understand a sequence is to **organize similar elements together**.

**Group** is the act of partitioning a sequence into collections based on a shared property or key.

The mental question is:

> **"Which elements belong together?"**

Unlike **Split**, which divides a sequence by position or boundaries, **Group** organizes elements by their characteristics.

---

# Group → Python

|Thinking Verb|Mental Question|Common Python|
|---|---|---|
|**Group**|Which elements belong together?|`collections.defaultdict(list)`, `collections.Counter`, `itertools.groupby(sorted(...))`, `dict.setdefault`|

> **Note:** Python has no `group-by` function. The idiom is a three-line loop: `d = defaultdict(list)` then `d[f(x)].append(x)`. It is one pass, O(n), and works on unsortable data.

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

**`itertools.groupby` is not SQL `GROUP BY`.** It starts a new group each time the key *changes*, so on unsorted input it produces duplicate keys — and building a dict from that silently keeps only the last one. Sort first, or use `defaultdict`.

**Group keys must be hashable.** A list key raises `TypeError`; convert it to a tuple.

**If you only need counts, never build the lists.** `Counter(f(x) for x in xs)` holds one integer per key instead of one list.

---

# One Sentence to Remember

> **Group organizes a sequence into collections whose elements share a common property or key — and the interesting part is never the grouping, it's the key function.**
