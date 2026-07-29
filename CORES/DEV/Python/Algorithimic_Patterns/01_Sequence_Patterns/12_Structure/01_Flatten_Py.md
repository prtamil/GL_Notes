# Pattern 34 — Flatten

## Mental Model

Convert a **nested sequence** into a **single linear sequence**.

**FlatMap** transforms and then flattens one level. **Flatten** goes after the nesting itself.

Python flattens **one level** with `chain.from_iterable(xs)` and **all levels** with an explicit recursive generator. There's no built-in deep flatten, and that gap is on purpose: how deep to go and what counts as a leaf are calls only you can make.

---

## Relationship to Cognitive Verb

```text
Structure
     ↓
Flatten
```

Flatten is a **Structure** pattern: it rearranges how the data is organised without touching the values.

---

## Python Functions & Common Idioms

|Variation|Example|Common Python|
|---|---|---|
|Flatten One Level|`[[1,2],[3]] → 1 2 3`|`chain.from_iterable(xs)`|
|One Level, Eagerly|small input|`[x for row in xs for x in row]`|
|Deep Flatten|arbitrary nesting|a recursive generator|
|Map then Flatten|transform + flatten|`chain.from_iterable(map(f, xs))`|
|Concatenate|join known lists|`chain(a, b, c)` or `a + b + c`|
|Sum of Lists|small, quick|`sum(xs, [])` — O(n²), avoid|
|Flatten Dict Values|`{a:1},{b:2}`|`chain.from_iterable(d.values() …)`|
|Tree to List|nested nodes|recursive `yield from`|
|Numeric Arrays|homogeneous data|`numpy.ravel` / `.flatten()`|

> **Note:** **Strings are iterables**, so any generic deep-flatten will happily explode `"abc"` into `'a','b','c'` unless you treat `str`/`bytes` as leaves. Every real flatten function needs that guard.

---

## Common Uses

- Parse nested JSON

- Flatten XML trees

- Tree traversal

- File system traversal

- Matrix processing

- Graph traversal

- Token streams

- AST processing

---

## Hidden Interview Problems

- Flatten a nested list

- Flatten a binary tree

- Flatten JSON

- Flatten a menu hierarchy

- Nested iterator (flatten lazily)

- Directory walk

---

## Recognition Clues

If you hear:

- Nested lists

- Nested arrays

- Tree to list

- One sequence

- Collapse nesting

- Recursive traversal

- Linearize

Think:

**→ Flatten**

---

## Pattern Summary

|Property|Value|
|---|---|
|Cognitive Verb|Structure|
|Pattern|Flatten|
|Input|nested sequence|
|Output|linear sequence|
|Built-in Depth|one level (`chain.from_iterable`)|
|Deep Flatten|write it yourself|
|Laziness|lazy with `chain` / `yield from`|
|Preserves Values|Yes|
|Primary Use|Remove nesting|

---

## Python Recipe Book

```python
# ============================================
# Input

from itertools import chain
from collections.abc import Iterable

nested = [[1, 2], [3, 4], [5]]

# ============================================
# Flatten one level — the idiom

list(chain.from_iterable(nested))       # => [1, 2, 3, 4, 5]

# the comprehension form — same result, reads left-to-right like
# the nested for-loops it replaces:
[x for row in nested for x in row]      # => [1, 2, 3, 4, 5]

# ORDER OF THE FORS: outer loop first, exactly as if you'd written
#   for row in nested:
#       for x in row:
# Reversing them is the classic comprehension error.

# ============================================
# chain vs chain.from_iterable

list(chain([1, 2], [3, 4], [5]))        # => [1,2,3,4,5]   separate ARGS
list(chain.from_iterable(nested))       # => [1,2,3,4,5]   ONE iterable
list(chain(*nested))                    # => same, but eagerly unpacks

# from_iterable is lazy in both directions — it never materializes
# the outer list. chain(*nested) fails on an infinite outer sequence.

# ============================================
# NOT sum(xs, [])

sum(nested, [])                         # => [1,2,3,4,5]   works, but
# it builds a new list on EVERY step: O(n²). On 10k rows it's seconds.
# Python 3.12 explicitly blocks sum() on strings for the same reason.

# ============================================
# Deep flatten — you have to write it

def flatten(x):
    """Recursively flatten, treating str/bytes as leaves."""
    for item in x:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            yield from flatten(item)
        else:
            yield item

list(flatten([1, [2, [3, [4]], 5], [6]]))           # => [1,2,3,4,5,6]

# `yield from` IS the recursion — it delegates to the inner generator
# without a manual loop, and keeps the whole thing lazy.

# ============================================
# THE STRING TRAP — why that guard exists

list(flatten([["a", "b"], ["c", ["d", "e"]]]))      # => ['a','b','c','d','e']

# without the isinstance(str) check, "ab" would flatten to 'a','b'
# and then 'a' is a string of length 1 that contains itself —
# infinite recursion, RecursionError.

# ============================================
# One level vs all levels — the distinction that matters

deep = [[1, [2]], [3]]
list(chain.from_iterable(deep))         # => [1, [2], 3]     ONE level
list(flatten(deep))                     # => [1, 2, 3]       ALL levels

# choose deliberately. "Flatten" in a spec almost always means one
# level; deep flatten usually means the data model is wrong.

# ============================================
# Flatten to a specific depth

def flatten_depth(x, depth=1):
    for item in x:
        if depth > 0 and isinstance(item, Iterable) \
           and not isinstance(item, (str, bytes)):
            yield from flatten_depth(item, depth - 1)
        else:
            yield item

list(flatten_depth([1, [2, [3, [4]]]], depth=2))    # => [1, 2, 3, [4]]

# ============================================
# Iterative deep flatten — no recursion limit

def flatten_iter(x):
    stack = [iter(x)]
    while stack:
        it = stack[-1]
        for item in it:
            if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
                stack.append(iter(item))
                break
            yield item
        else:
            stack.pop()

list(flatten_iter([1, [2, [3, [4]], 5], [6]]))      # => [1,2,3,4,5,6]

# Python's recursion limit is ~1000. A 2000-deep JSON structure
# crashes the recursive version; this one doesn't.

# ============================================
# Map then flatten — flatMap by another name

list(chain.from_iterable(map(lambda n: [n, n * 10], [1, 2, 3])))
# => [1, 10, 2, 20, 3, 30]

[y for n in [1, 2, 3] for y in (n, n * 10)]         # => same, clearer

# split every sentence into words:
lines = ["the cat", "sat down"]
[w for line in lines for w in line.split()]         # => ['the','cat','sat','down']

# ============================================
# Concatenate known collections

a, b, c = [1, 2], [3, 4], [5]
a + b + c                               # => [1,2,3,4,5]   lists only
list(chain(a, b, c))                    # => same, works on ANY iterables

# chain accepts generators, sets, dict views, files — `+` does not.
# and chain doesn't copy: it just reads each in turn.

# ============================================
# Flatten dict values

records = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
list(chain.from_iterable(d.values() for d in records))       # => [1,2,3,4]

# all keys across all dicts:
list(chain.from_iterable(records))      # => ['a','b','a','b']
# iterating a dict yields its KEYS — surprising in a flatten context

# ============================================
# Flatten a tree of nodes

tree = {"name": "root", "children": [
    {"name": "a", "children": [{"name": "c", "children": []}]},
    {"name": "b", "children": []},
]}

def walk(node):
    yield node["name"]
    for child in node["children"]:
        yield from walk(child)

list(walk(tree))                        # => ['root', 'a', 'c', 'b']

# depth-first, pre-order, in four lines. Move the yield after the
# loop for post-order; use a deque for breadth-first.

# ============================================
# Flatten nested JSON into dotted keys

def flatten_json(obj, prefix=""):
    for k, v in obj.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            yield from flatten_json(v, key)
        else:
            yield key, v

dict(flatten_json({"a": {"b": 1, "c": {"d": 2}}, "e": 3}))
# => {'a.b': 1, 'a.c.d': 2, 'e': 3}

# this is the flatten people actually need at work — config files,
# API responses, and anything destined for a CSV column

# ============================================
# Undo a flatten — see 12_Structure/03_Reshape

from itertools import batched                       # 3.12+
flat = [1, 2, 3, 4, 5, 6]
[list(b) for b in batched(flat, 2)]     # => [[1,2],[3,4],[5,6]]

# flatten and reshape are inverses ONLY when every row had the same
# length. Flattening ragged rows loses the shape permanently.

# ============================================
# Laziness — flatten a stream without materializing it

big = ([i] * 3 for i in range(1_000_000))
first5 = list(chain.from_iterable(big))[:5]         # builds 3M items first!

from itertools import islice
big = ([i] * 3 for i in range(1_000_000))
list(islice(chain.from_iterable(big), 5))           # => [0,0,0,1,1]  lazy

# chain.from_iterable stays lazy; slicing AFTER list() does not.
# Put the bound inside the pipeline, not after it.

# ============================================
# Numeric data — numpy does it properly

# import numpy as np
# a = np.array([[1, 2], [3, 4]])
# a.ravel()      # => array([1, 2, 3, 4])   a VIEW, no copy
# a.flatten()    # => array([1, 2, 3, 4])   a copy

# for rectangular numeric data, numpy is both faster and clearer.
# Pure-Python flatten is for ragged and heterogeneous structures.

# ============================================
# Compare

chain.from_iterable(xs)         # one level, lazy       → Flatten
[x for r in xs for x in r]      # one level, eager      → Flatten
flatten(xs)                     # all levels, recursive → Flatten
chain.from_iterable(map(f, xs)) # transform + flatten   → FlatMap
batched(flat, n)                # linear → nested       → Reshape
zip(*rows)                      # rows → columns        → Transpose
```

---

### Memory Hooks

|You want|You reach for|
|---|---|
|one level, lazily|`chain.from_iterable(xs)`|
|one level, eagerly|`[x for row in xs for x in row]`|
|to join known lists|`chain(a, b, c)`|
|all levels|a recursive generator with `yield from`|
|a depth limit|pass `depth` down the recursion|
|no recursion limit|the explicit-stack version|
|map then flatten|`[y for x in xs for y in f(x)]`|
|to walk a tree|`yield` the node, `yield from` the children|
|dotted JSON keys|recursive `flatten_json`|
|to un-flatten|`batched(flat, n)`|
|fast numeric flattening|`numpy.ravel`|

---

### Key Insight

**Python gives you one-level flattening and deliberately stops there.** `chain.from_iterable` covers the case that's genuinely well-defined: a list of lists becomes a list. Deep flattening needs two decisions no library can make for you — how deep to go, and what counts as a leaf. A dict, a string, a namedtuple and a numpy array are all iterable, and whether any of them should dissolve is a question about your domain.

**Strings are the trap that turns a clever one-liner into a `RecursionError`.** `"a"` is an iterable containing `"a"`, so a naive deep flatten recurses forever on any single character. Every serious flatten function carries `not isinstance(item, (str, bytes))`. Write one without it and the bug won't show up on your test list of ints — it'll show up on real data.

The habit worth forming is **being suspicious of the deep flatten in the first place**. `[x for row in rows for x in row]` on a matrix is honest work. Recursively dissolving arbitrary nesting usually means the structure meant something — the depth *was* the parent-child relationship — and you just threw it away. The tree walk is the same recursion with the structure kept, and it's almost always what the problem actually wanted.
